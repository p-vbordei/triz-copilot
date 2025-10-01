"""
Async Utility Functions (TASK-011)
Bridge between async MCP handlers and sync TRIZ core functions
"""

import asyncio
from typing import Any, Callable, TypeVar
from functools import wraps

T = TypeVar('T')


async def run_sync(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """
    Run a synchronous function in a thread pool to avoid blocking the event loop

    Args:
        func: Synchronous function to run
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Result from the function
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


def async_wrap(func: Callable[..., T]) -> Callable[..., asyncio.Future[T]]:
    """
    Decorator to wrap a synchronous function for async execution

    Usage:
        @async_wrap
        def sync_function():
            return "result"

        result = await sync_function()
    """
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> T:
        return await run_sync(func, *args, **kwargs)
    return wrapper


class AsyncCache:
    """Simple async-safe cache for expensive operations"""

    def __init__(self):
        self._cache: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any:
        """Get cached value"""
        async with self._lock:
            return self._cache.get(key)

    async def set(self, key: str, value: Any) -> None:
        """Set cached value"""
        async with self._lock:
            self._cache[key] = value

    async def clear(self) -> None:
        """Clear all cached values"""
        async with self._lock:
            self._cache.clear()
