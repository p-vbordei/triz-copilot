#!/usr/bin/env python3
"""
TRIZ Tools Utilities

Common utilities and helper functions for the TRIZ tools system.
"""

from .singleton import SingletonMeta, SingletonBase, singleton_factory, singleton_getter
from .error_handling import error_handler, TRIZBaseException, safe_execute
from .data_validation import validate_and_convert, ValidationMixin
from .file_operations import ensure_directory, safe_file_operation, atomic_write

__all__ = [
    # Singleton utilities
    'SingletonMeta',
    'SingletonBase', 
    'singleton_factory',
    'singleton_getter',
    
    # Error handling
    'error_handler',
    'TRIZBaseException',
    'safe_execute',
    
    # Data validation
    'validate_and_convert',
    'ValidationMixin',
    
    # File operations
    'ensure_directory',
    'safe_file_operation',
    'atomic_write'
]