#!/usr/bin/env python3
"""
Error Handling Utilities

Centralized error handling patterns and decorators.
"""

import functools
import logging
from typing import Any, Callable, Dict, Optional, Type, Union
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


class TRIZBaseException(Exception):
    """Base exception for all TRIZ-related errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        self.timestamp = datetime.now()


class ValidationError(TRIZBaseException):
    """Validation-related errors."""
    pass


class ServiceError(TRIZBaseException):
    """Service operation errors."""
    pass


class DataError(TRIZBaseException):
    """Data access/persistence errors."""
    pass


class ConfigurationError(TRIZBaseException):
    """Configuration-related errors."""
    pass


@dataclass
class ErrorResult:
    """Standardized error result structure."""
    success: bool = False
    error: str = ""
    message: str = ""
    details: Dict[str, Any] = None
    timestamp: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "error": self.error,
            "message": self.message,
            "details": self.details or {},
            "timestamp": self.timestamp
        }


def error_handler(
    default_return: Any = None,
    exceptions: tuple = (Exception,),
    log_errors: bool = True,
    return_error_dict: bool = False
):
    """
    Decorator for consistent error handling across services.
    
    Args:
        default_return: Default value to return on error
        exceptions: Tuple of exceptions to catch
        log_errors: Whether to log caught exceptions
        return_error_dict: Whether to return standardized error dict
        
    Returns:
        Decorated function with error handling
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
                
                if return_error_dict:
                    return ErrorResult(
                        success=False,
                        error=type(e).__name__,
                        message=str(e),
                        details=getattr(e, 'details', {}),
                        timestamp=datetime.now().isoformat()
                    ).to_dict()
                
                return default_return
        return wrapper
    return decorator


def safe_execute(
    func: Callable,
    *args,
    default: Any = None,
    exceptions: tuple = (Exception,),
    log_errors: bool = True,
    **kwargs
) -> Any:
    """
    Safely execute a function with error handling.
    
    Args:
        func: Function to execute
        *args: Positional arguments for function
        default: Default return value on error
        exceptions: Exceptions to catch
        log_errors: Whether to log errors
        **kwargs: Keyword arguments for function
        
    Returns:
        Function result or default value
    """
    try:
        return func(*args, **kwargs)
    except exceptions as e:
        if log_errors:
            logger.error(f"Error executing {func.__name__}: {str(e)}", exc_info=True)
        return default


def handle_service_errors(func: Callable) -> Callable:
    """
    Decorator specifically for service method error handling.
    Returns standardized service response format.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            
            # If result is already a dict with success field, return as-is
            if isinstance(result, dict) and 'success' in result:
                return result
            
            # Otherwise wrap successful result
            return {
                "success": True,
                "data": result,
                "message": "Operation completed successfully"
            }
            
        except TRIZBaseException as e:
            return {
                "success": False,
                "error": e.error_code,
                "message": e.message,
                "details": e.details,
                "timestamp": e.timestamp.isoformat()
            }
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": "UnexpectedError",
                "message": f"An unexpected error occurred: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    return wrapper


def validate_parameters(**validators):
    """
    Decorator for parameter validation.
    
    Args:
        **validators: Dict of parameter_name -> validation_function
        
    Example:
        @validate_parameters(
            principle_id=lambda x: 1 <= x <= 40,
            text=lambda x: len(x.strip()) > 0
        )
        def some_function(principle_id, text):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature to map args to parameter names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate parameters
            for param_name, validator in validators.items():
                if param_name in bound_args.arguments:
                    value = bound_args.arguments[param_name]
                    try:
                        if not validator(value):
                            raise ValidationError(
                                f"Invalid value for parameter '{param_name}': {value}",
                                error_code="ParameterValidationError",
                                details={"parameter": param_name, "value": value}
                            )
                    except Exception as e:
                        if isinstance(e, ValidationError):
                            raise
                        raise ValidationError(
                            f"Validation error for parameter '{param_name}': {str(e)}",
                            error_code="ParameterValidationError",
                            details={"parameter": param_name, "value": value, "validation_error": str(e)}
                        )
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


class ErrorContext:
    """
    Context manager for error handling with cleanup.
    """
    
    def __init__(
        self,
        operation_name: str,
        cleanup_func: Optional[Callable] = None,
        log_errors: bool = True
    ):
        self.operation_name = operation_name
        self.cleanup_func = cleanup_func
        self.log_errors = log_errors
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if self.log_errors:
                logger.error(f"Error in {self.operation_name}: {str(exc_val)}", exc_info=True)
            
            if self.cleanup_func:
                try:
                    self.cleanup_func()
                except Exception as cleanup_error:
                    logger.error(f"Cleanup error after {self.operation_name}: {str(cleanup_error)}")
        
        # Don't suppress the exception
        return False


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator for retrying function calls on failure.
    
    Args:
        max_attempts: Maximum number of attempts
        delay: Initial delay between attempts (seconds)
        backoff_factor: Multiplier for delay on each retry
        exceptions: Exceptions that should trigger retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            import time
            
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:  # Don't sleep on last attempt
                        logger.warning(
                            f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}. "
                            f"Retrying in {current_delay} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(f"All {max_attempts} attempts failed for {func.__name__}")
            
            # Re-raise the last exception if all attempts failed
            raise last_exception
        return wrapper
    return decorator


# Common validation functions
def is_positive_integer(value: Any) -> bool:
    """Check if value is a positive integer."""
    try:
        return isinstance(value, int) and value > 0
    except:
        return False


def is_non_empty_string(value: Any) -> bool:
    """Check if value is a non-empty string."""
    try:
        return isinstance(value, str) and len(value.strip()) > 0
    except:
        return False


def is_valid_principle_id(value: Any) -> bool:
    """Check if value is a valid TRIZ principle ID (1-40)."""
    try:
        return isinstance(value, int) and 1 <= value <= 40
    except:
        return False


def is_valid_parameter_id(value: Any) -> bool:
    """Check if value is a valid engineering parameter ID (1-39)."""
    try:
        return isinstance(value, int) and 1 <= value <= 39
    except:
        return False