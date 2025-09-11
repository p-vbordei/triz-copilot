#!/usr/bin/env python3
"""
Singleton Pattern Utility

Centralized singleton pattern implementation to reduce code duplication
across services that use singleton pattern.
"""

from typing import TypeVar, Type, Dict, Any, Optional
from threading import Lock

T = TypeVar('T')

class SingletonMeta(type):
    """
    Thread-safe singleton metaclass.
    """
    _instances: Dict[Type, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Thread-safe singleton instance creation.
        """
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
    
    @classmethod
    def reset_instance(mcs, cls: Type[T]) -> None:
        """
        Reset singleton instance for testing or reinitialization.
        """
        with mcs._lock:
            if cls in mcs._instances:
                del mcs._instances[cls]
    
    @classmethod
    def get_instance(mcs, cls: Type[T]) -> Optional[T]:
        """
        Get existing instance without creating new one.
        """
        return mcs._instances.get(cls)


def singleton_factory(cls: Type[T], reset: bool = False, **kwargs) -> T:
    """
    Factory function for singleton instances with reset capability.
    
    Args:
        cls: Class to instantiate
        reset: Whether to reset existing instance
        **kwargs: Arguments to pass to class constructor
    
    Returns:
        Singleton instance of the class
    """
    if reset:
        SingletonMeta.reset_instance(cls)
    
    # For classes not using SingletonMeta, implement manual singleton
    if not hasattr(cls, '_instances'):
        cls._instances = {}
        cls._lock = Lock()
    
    with cls._lock:
        if cls not in cls._instances or reset:
            cls._instances[cls] = cls(**kwargs)
    
    return cls._instances[cls]


class SingletonBase(metaclass=SingletonMeta):
    """
    Base class for singleton implementations.
    """
    pass


# Decorator for singleton factory functions
def singleton_getter(cls: Type[T]):
    """
    Decorator to create getter functions for singleton instances.
    
    Usage:
        @singleton_getter(MyClass)
        def get_my_instance(reset=False, **kwargs):
            pass
    """
    def decorator(func):
        def wrapper(reset: bool = False, **kwargs):
            return singleton_factory(cls, reset=reset, **kwargs)
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper
    return decorator