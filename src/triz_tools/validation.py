"""
Input Validation and Error Handling (T051)
Provides comprehensive validation for TRIZ tool inputs.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validation check"""
    is_valid: bool
    message: str
    sanitized_value: Optional[Any] = None
    errors: Optional[List[str]] = None
    
    def __bool__(self) -> bool:
        """Allow using result as boolean"""
        return self.is_valid


class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, errors: Optional[List[str]] = None):
        super().__init__(message)
        self.errors = errors or []


class InputValidator:
    """Validates and sanitizes input for TRIZ tools"""
    
    # Valid ranges
    PRINCIPLE_RANGE = (1, 40)
    PARAMETER_RANGE = (1, 39)
    MAX_TEXT_LENGTH = 5000
    MAX_LIST_LENGTH = 100
    
    # Patterns
    SESSION_ID_PATTERN = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$')
    SAFE_TEXT_PATTERN = re.compile(r'^[\w\s.,;:!?()\[\]{}"\'-]+$')
    
    @classmethod
    def validate_principle_id(cls, principle_id: Any) -> ValidationResult:
        """
        Validate TRIZ principle ID.
        
        Args:
            principle_id: Input to validate
        
        Returns:
            Validation result
        """
        try:
            # Convert to int
            if isinstance(principle_id, str):
                principle_id = int(principle_id)
            elif not isinstance(principle_id, int):
                return ValidationResult(
                    is_valid=False,
                    message=f"Principle ID must be an integer, got {type(principle_id).__name__}"
                )
            
            # Check range
            if principle_id < cls.PRINCIPLE_RANGE[0] or principle_id > cls.PRINCIPLE_RANGE[1]:
                return ValidationResult(
                    is_valid=False,
                    message=f"Principle ID must be between {cls.PRINCIPLE_RANGE[0]} and {cls.PRINCIPLE_RANGE[1]}"
                )
            
            return ValidationResult(
                is_valid=True,
                message="Valid principle ID",
                sanitized_value=principle_id
            )
            
        except (ValueError, TypeError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid principle ID: {str(e)}"
            )
    
    @classmethod
    def validate_parameter_id(cls, parameter_id: Any) -> ValidationResult:
        """
        Validate engineering parameter ID.
        
        Args:
            parameter_id: Input to validate
        
        Returns:
            Validation result
        """
        try:
            # Convert to int
            if isinstance(parameter_id, str):
                parameter_id = int(parameter_id)
            elif not isinstance(parameter_id, int):
                return ValidationResult(
                    is_valid=False,
                    message=f"Parameter ID must be an integer, got {type(parameter_id).__name__}"
                )
            
            # Check range
            if parameter_id < cls.PARAMETER_RANGE[0] or parameter_id > cls.PARAMETER_RANGE[1]:
                return ValidationResult(
                    is_valid=False,
                    message=f"Parameter ID must be between {cls.PARAMETER_RANGE[0]} and {cls.PARAMETER_RANGE[1]}"
                )
            
            return ValidationResult(
                is_valid=True,
                message="Valid parameter ID",
                sanitized_value=parameter_id
            )
            
        except (ValueError, TypeError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid parameter ID: {str(e)}"
            )
    
    @classmethod
    def validate_contradiction(
        cls,
        improving: Any,
        worsening: Any
    ) -> ValidationResult:
        """
        Validate contradiction parameters.
        
        Args:
            improving: Improving parameter
            worsening: Worsening parameter
        
        Returns:
            Validation result
        """
        errors = []
        
        # Validate improving parameter
        imp_result = cls.validate_parameter_id(improving)
        if not imp_result.is_valid:
            errors.append(f"Improving parameter: {imp_result.message}")
        else:
            improving = imp_result.sanitized_value
        
        # Validate worsening parameter
        wor_result = cls.validate_parameter_id(worsening)
        if not wor_result.is_valid:
            errors.append(f"Worsening parameter: {wor_result.message}")
        else:
            worsening = wor_result.sanitized_value
        
        # Check if same
        if errors == [] and improving == worsening:
            errors.append("Improving and worsening parameters cannot be the same")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                message="Invalid contradiction parameters",
                errors=errors
            )
        
        return ValidationResult(
            is_valid=True,
            message="Valid contradiction",
            sanitized_value=(improving, worsening)
        )
    
    @classmethod
    def validate_text_input(
        cls,
        text: Any,
        max_length: Optional[int] = None,
        allow_empty: bool = False
    ) -> ValidationResult:
        """
        Validate text input.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            allow_empty: Whether empty text is valid
        
        Returns:
            Validation result
        """
        if max_length is None:
            max_length = cls.MAX_TEXT_LENGTH
        
        # Check type
        if not isinstance(text, str):
            return ValidationResult(
                is_valid=False,
                message=f"Text must be a string, got {type(text).__name__}"
            )
        
        # Sanitize
        text = text.strip()
        
        # Check empty
        if not text and not allow_empty:
            return ValidationResult(
                is_valid=False,
                message="Text cannot be empty"
            )
        
        # Check length
        if len(text) > max_length:
            return ValidationResult(
                is_valid=False,
                message=f"Text exceeds maximum length of {max_length} characters"
            )
        
        # Remove potentially harmful characters
        sanitized = cls._sanitize_text(text)
        
        return ValidationResult(
            is_valid=True,
            message="Valid text input",
            sanitized_value=sanitized
        )
    
    @classmethod
    def validate_session_id(cls, session_id: Any) -> ValidationResult:
        """
        Validate session ID format.
        
        Args:
            session_id: Session ID to validate
        
        Returns:
            Validation result
        """
        if not isinstance(session_id, str):
            return ValidationResult(
                is_valid=False,
                message="Session ID must be a string"
            )
        
        if not cls.SESSION_ID_PATTERN.match(session_id):
            return ValidationResult(
                is_valid=False,
                message="Invalid session ID format (expected UUID)"
            )
        
        return ValidationResult(
            is_valid=True,
            message="Valid session ID",
            sanitized_value=session_id
        )
    
    @classmethod
    def validate_list_input(
        cls,
        items: Any,
        item_type: type = None,
        max_length: Optional[int] = None,
        allow_empty: bool = False
    ) -> ValidationResult:
        """
        Validate list input.
        
        Args:
            items: Input list
            item_type: Expected type of items
            max_length: Maximum list length
            allow_empty: Whether empty list is valid
        
        Returns:
            Validation result
        """
        if max_length is None:
            max_length = cls.MAX_LIST_LENGTH
        
        # Check type
        if not isinstance(items, (list, tuple)):
            return ValidationResult(
                is_valid=False,
                message=f"Expected list or tuple, got {type(items).__name__}"
            )
        
        # Check empty
        if len(items) == 0 and not allow_empty:
            return ValidationResult(
                is_valid=False,
                message="List cannot be empty"
            )
        
        # Check length
        if len(items) > max_length:
            return ValidationResult(
                is_valid=False,
                message=f"List exceeds maximum length of {max_length}"
            )
        
        # Check item types
        if item_type is not None:
            invalid_items = []
            for i, item in enumerate(items):
                if not isinstance(item, item_type):
                    invalid_items.append(f"Item {i}: expected {item_type.__name__}, got {type(item).__name__}")
            
            if invalid_items:
                return ValidationResult(
                    is_valid=False,
                    message="Invalid item types in list",
                    errors=invalid_items
                )
        
        return ValidationResult(
            is_valid=True,
            message="Valid list input",
            sanitized_value=list(items)
        )
    
    @classmethod
    def validate_dict_input(
        cls,
        data: Any,
        required_keys: Optional[List[str]] = None,
        optional_keys: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate dictionary input.
        
        Args:
            data: Input dictionary
            required_keys: Keys that must be present
            optional_keys: Keys that are allowed but not required
        
        Returns:
            Validation result
        """
        # Check type
        if not isinstance(data, dict):
            return ValidationResult(
                is_valid=False,
                message=f"Expected dictionary, got {type(data).__name__}"
            )
        
        errors = []
        
        # Check required keys
        if required_keys:
            missing = [key for key in required_keys if key not in data]
            if missing:
                errors.append(f"Missing required keys: {', '.join(missing)}")
        
        # Check for unexpected keys
        if required_keys is not None or optional_keys is not None:
            allowed_keys = set(required_keys or []) | set(optional_keys or [])
            unexpected = [key for key in data.keys() if key not in allowed_keys]
            if unexpected:
                errors.append(f"Unexpected keys: {', '.join(unexpected)}")
        
        if errors:
            return ValidationResult(
                is_valid=False,
                message="Invalid dictionary structure",
                errors=errors
            )
        
        return ValidationResult(
            is_valid=True,
            message="Valid dictionary input",
            sanitized_value=data
        )
    
    @classmethod
    def validate_file_path(
        cls,
        path: Any,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
        extensions: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate file path.
        
        Args:
            path: File path to validate
            must_exist: Whether path must exist
            must_be_file: Whether path must be a file
            must_be_dir: Whether path must be a directory
            extensions: Allowed file extensions
        
        Returns:
            Validation result
        """
        # Convert to Path
        try:
            if isinstance(path, str):
                path = Path(path)
            elif not isinstance(path, Path):
                return ValidationResult(
                    is_valid=False,
                    message=f"Expected path string or Path object, got {type(path).__name__}"
                )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid path: {str(e)}"
            )
        
        # Check existence
        if must_exist and not path.exists():
            return ValidationResult(
                is_valid=False,
                message=f"Path does not exist: {path}"
            )
        
        # Check type
        if must_be_file and path.exists() and not path.is_file():
            return ValidationResult(
                is_valid=False,
                message=f"Path is not a file: {path}"
            )
        
        if must_be_dir and path.exists() and not path.is_dir():
            return ValidationResult(
                is_valid=False,
                message=f"Path is not a directory: {path}"
            )
        
        # Check extension
        if extensions and path.is_file():
            if path.suffix.lower() not in [ext.lower() for ext in extensions]:
                return ValidationResult(
                    is_valid=False,
                    message=f"Invalid file extension. Allowed: {', '.join(extensions)}"
                )
        
        return ValidationResult(
            is_valid=True,
            message="Valid file path",
            sanitized_value=path
        )
    
    @classmethod
    def validate_numeric_range(
        cls,
        value: Any,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
        allow_negative: bool = True
    ) -> ValidationResult:
        """
        Validate numeric value within range.
        
        Args:
            value: Value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            allow_negative: Whether negative values are allowed
        
        Returns:
            Validation result
        """
        try:
            # Convert to float
            if isinstance(value, str):
                value = float(value)
            elif not isinstance(value, (int, float)):
                return ValidationResult(
                    is_valid=False,
                    message=f"Expected numeric value, got {type(value).__name__}"
                )
            
            # Check negative
            if not allow_negative and value < 0:
                return ValidationResult(
                    is_valid=False,
                    message="Negative values not allowed"
                )
            
            # Check range
            if min_value is not None and value < min_value:
                return ValidationResult(
                    is_valid=False,
                    message=f"Value must be at least {min_value}"
                )
            
            if max_value is not None and value > max_value:
                return ValidationResult(
                    is_valid=False,
                    message=f"Value must be at most {max_value}"
                )
            
            return ValidationResult(
                is_valid=True,
                message="Valid numeric value",
                sanitized_value=value
            )
            
        except (ValueError, TypeError) as e:
            return ValidationResult(
                is_valid=False,
                message=f"Invalid numeric value: {str(e)}"
            )
    
    @staticmethod
    def _sanitize_text(text: str) -> str:
        """
        Sanitize text input.
        
        Args:
            text: Text to sanitize
        
        Returns:
            Sanitized text
        """
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char == '\n')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text


class ErrorHandler:
    """Centralized error handling for TRIZ tools"""
    
    @staticmethod
    def handle_validation_error(
        error: ValidationError,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle validation error.
        
        Args:
            error: Validation error
            context: Error context
        
        Returns:
            Error response
        """
        logger.error(f"Validation error{f' in {context}' if context else ''}: {str(error)}")
        
        return {
            "success": False,
            "error": "Validation Error",
            "message": str(error),
            "details": error.errors if error.errors else None,
            "context": context
        }
    
    @staticmethod
    def handle_general_error(
        error: Exception,
        context: Optional[str] = None,
        fallback_message: str = "An unexpected error occurred"
    ) -> Dict[str, Any]:
        """
        Handle general exception.
        
        Args:
            error: Exception
            context: Error context
            fallback_message: Fallback error message
        
        Returns:
            Error response
        """
        logger.error(
            f"Error{f' in {context}' if context else ''}: {str(error)}",
            exc_info=True
        )
        
        return {
            "success": False,
            "error": type(error).__name__,
            "message": str(error) if str(error) else fallback_message,
            "context": context
        }
    
    @staticmethod
    def safe_execute(
        func,
        *args,
        context: Optional[str] = None,
        default_return: Any = None,
        **kwargs
    ) -> Tuple[bool, Any]:
        """
        Safely execute a function with error handling.
        
        Args:
            func: Function to execute
            *args: Function arguments
            context: Execution context
            default_return: Default return value on error
            **kwargs: Function keyword arguments
        
        Returns:
            Tuple of (success, result)
        """
        try:
            result = func(*args, **kwargs)
            return True, result
        except ValidationError as e:
            error_response = ErrorHandler.handle_validation_error(e, context)
            return False, error_response
        except Exception as e:
            error_response = ErrorHandler.handle_general_error(e, context)
            return False, default_return if default_return is not None else error_response


# Decorator for input validation
def validate_inputs(**validators):
    """
    Decorator to validate function inputs.
    
    Usage:
        @validate_inputs(
            principle_id=InputValidator.validate_principle_id,
            text=lambda x: InputValidator.validate_text_input(x, max_length=1000)
        )
        def my_function(principle_id, text):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function argument names
            import inspect
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Validate each argument
            errors = []
            sanitized_args = dict(bound_args.arguments)
            
            for arg_name, validator in validators.items():
                if arg_name in sanitized_args:
                    value = sanitized_args[arg_name]
                    result = validator(value)
                    
                    if not result.is_valid:
                        errors.append(f"{arg_name}: {result.message}")
                    elif result.sanitized_value is not None:
                        sanitized_args[arg_name] = result.sanitized_value
            
            if errors:
                raise ValidationError(
                    f"Invalid inputs for {func.__name__}",
                    errors=errors
                )
            
            # Call function with sanitized arguments
            return func(**sanitized_args)
        
        return wrapper
    return decorator