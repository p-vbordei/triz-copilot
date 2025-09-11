#!/usr/bin/env python3
"""
Data Validation Utilities

Common data validation and conversion patterns.
"""

from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Callable
from dataclasses import dataclass, fields
import json
from datetime import datetime
from pathlib import Path

T = TypeVar('T')


@dataclass
class ValidationResult:
    """Result of validation operation."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    converted_value: Any = None
    
    def add_error(self, message: str):
        """Add an error message."""
        self.errors.append(message)
        self.is_valid = False
    
    def add_warning(self, message: str):
        """Add a warning message."""
        self.warnings.append(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "converted_value": self.converted_value
        }


class ValidationMixin:
    """Mixin class providing validation capabilities to data classes."""
    
    def validate(self) -> ValidationResult:
        """Validate the instance."""
        result = ValidationResult(is_valid=True, errors=[], warnings=[])
        
        # Check required fields
        for field in fields(self):
            value = getattr(self, field.name)
            
            # Check for None values in non-optional fields
            if value is None and not self._is_optional_field(field):
                result.add_error(f"Required field '{field.name}' is None")
            
            # Custom validation if method exists
            validator_name = f"validate_{field.name}"
            if hasattr(self, validator_name):
                validator = getattr(self, validator_name)
                try:
                    validator(value, result)
                except Exception as e:
                    result.add_error(f"Validation error for '{field.name}': {str(e)}")
        
        return result
    
    def _is_optional_field(self, field) -> bool:
        """Check if field is optional (Union with None or has default)."""
        return (
            hasattr(field, 'default') and field.default is not None or
            hasattr(field, 'default_factory') or
            (hasattr(field.type, '__origin__') and 
             type(None) in getattr(field.type, '__args__', []))
        )


def validate_and_convert(
    value: Any,
    target_type: Type[T],
    validators: Optional[List[Callable[[Any], bool]]] = None,
    converters: Optional[List[Callable[[Any], Any]]] = None
) -> ValidationResult:
    """
    Validate and convert a value to target type.
    
    Args:
        value: Value to validate/convert
        target_type: Target type to convert to
        validators: List of validation functions
        converters: List of conversion functions
        
    Returns:
        ValidationResult with conversion result
    """
    result = ValidationResult(is_valid=True, errors=[], warnings=[])
    converted_value = value
    
    try:
        # Apply converters first
        if converters:
            for converter in converters:
                try:
                    converted_value = converter(converted_value)
                except Exception as e:
                    result.add_error(f"Conversion error: {str(e)}")
                    return result
        
        # Type conversion
        if not isinstance(converted_value, target_type):
            try:
                if target_type == str:
                    converted_value = str(converted_value)
                elif target_type == int:
                    converted_value = int(float(converted_value))  # Handle string floats
                elif target_type == float:
                    converted_value = float(converted_value)
                elif target_type == bool:
                    if isinstance(converted_value, str):
                        converted_value = converted_value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        converted_value = bool(converted_value)
                elif target_type == list and isinstance(converted_value, str):
                    # Try to parse JSON list or comma-separated
                    try:
                        converted_value = json.loads(converted_value)
                        if not isinstance(converted_value, list):
                            converted_value = [converted_value]
                    except:
                        converted_value = [x.strip() for x in converted_value.split(',')]
                elif target_type == dict and isinstance(converted_value, str):
                    converted_value = json.loads(converted_value)
                else:
                    # Try direct type conversion
                    converted_value = target_type(converted_value)
            except Exception as e:
                result.add_error(f"Type conversion to {target_type.__name__} failed: {str(e)}")
                return result
        
        # Apply validators
        if validators:
            for validator in validators:
                try:
                    if not validator(converted_value):
                        result.add_error(f"Validation failed for value: {converted_value}")
                except Exception as e:
                    result.add_error(f"Validator error: {str(e)}")
        
        result.converted_value = converted_value
        
    except Exception as e:
        result.add_error(f"Unexpected validation error: {str(e)}")
    
    return result


def validate_principle_id(value: Any) -> ValidationResult:
    """Validate TRIZ principle ID (1-40)."""
    return validate_and_convert(
        value,
        int,
        validators=[lambda x: 1 <= x <= 40]
    )


def validate_parameter_id(value: Any) -> ValidationResult:
    """Validate engineering parameter ID (1-39)."""
    return validate_and_convert(
        value,
        int,
        validators=[lambda x: 1 <= x <= 39]
    )


def validate_session_id(value: Any) -> ValidationResult:
    """Validate session ID format."""
    result = validate_and_convert(value, str)
    if result.is_valid:
        # Check UUID-like format
        if len(result.converted_value) < 8:
            result.add_error("Session ID too short")
        elif not all(c.isalnum() or c == '-' for c in result.converted_value):
            result.add_error("Session ID contains invalid characters")
    return result


def validate_text_input(value: Any, min_length: int = 1, max_length: int = 10000) -> ValidationResult:
    """Validate text input."""
    result = validate_and_convert(
        value,
        str,
        converters=[lambda x: x.strip() if isinstance(x, str) else str(x)]
    )
    
    if result.is_valid:
        text = result.converted_value
        if len(text) < min_length:
            result.add_error(f"Text too short (minimum {min_length} characters)")
        elif len(text) > max_length:
            result.add_error(f"Text too long (maximum {max_length} characters)")
    
    return result


def validate_file_path(value: Any, must_exist: bool = False, create_parent: bool = False) -> ValidationResult:
    """Validate file path."""
    result = validate_and_convert(value, str)
    
    if result.is_valid:
        try:
            path = Path(result.converted_value)
            
            if must_exist and not path.exists():
                result.add_error(f"File does not exist: {path}")
            
            if create_parent and not path.parent.exists():
                try:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    result.add_warning(f"Created parent directory: {path.parent}")
                except Exception as e:
                    result.add_error(f"Could not create parent directory: {str(e)}")
            
            result.converted_value = path
            
        except Exception as e:
            result.add_error(f"Invalid file path: {str(e)}")
    
    return result


def validate_json_data(value: Any, schema: Optional[Dict] = None) -> ValidationResult:
    """Validate JSON data."""
    result = ValidationResult(is_valid=True, errors=[], warnings=[])
    
    try:
        # Convert to JSON-serializable format
        if isinstance(value, str):
            data = json.loads(value)
        else:
            # Test JSON serialization
            json.dumps(value)
            data = value
        
        # Basic schema validation if provided
        if schema:
            result = _validate_against_schema(data, schema)
        
        result.converted_value = data
        
    except json.JSONDecodeError as e:
        result.add_error(f"Invalid JSON: {str(e)}")
    except Exception as e:
        result.add_error(f"JSON validation error: {str(e)}")
    
    return result


def _validate_against_schema(data: Any, schema: Dict) -> ValidationResult:
    """Basic schema validation."""
    result = ValidationResult(is_valid=True, errors=[], warnings=[])
    
    if not isinstance(schema, dict):
        return result
    
    # Check required fields
    if isinstance(data, dict):
        required = schema.get('required', [])
        for field in required:
            if field not in data:
                result.add_error(f"Required field missing: {field}")
        
        # Check field types
        properties = schema.get('properties', {})
        for field, field_schema in properties.items():
            if field in data:
                expected_type = field_schema.get('type')
                if expected_type:
                    value = data[field]
                    if expected_type == 'string' and not isinstance(value, str):
                        result.add_error(f"Field '{field}' should be string, got {type(value).__name__}")
                    elif expected_type == 'number' and not isinstance(value, (int, float)):
                        result.add_error(f"Field '{field}' should be number, got {type(value).__name__}")
                    elif expected_type == 'array' and not isinstance(value, list):
                        result.add_error(f"Field '{field}' should be array, got {type(value).__name__}")
                    elif expected_type == 'object' and not isinstance(value, dict):
                        result.add_error(f"Field '{field}' should be object, got {type(value).__name__}")
    
    return result


def sanitize_input(value: str, remove_html: bool = True, max_length: int = 10000) -> str:
    """Sanitize text input."""
    if not isinstance(value, str):
        value = str(value)
    
    # Remove HTML tags if requested
    if remove_html:
        import re
        value = re.sub(r'<[^>]+>', '', value)
    
    # Trim whitespace
    value = value.strip()
    
    # Limit length
    if len(value) > max_length:
        value = value[:max_length]
    
    return value


def normalize_text(text: str) -> str:
    """Normalize text for processing."""
    if not isinstance(text, str):
        text = str(text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Replace multiple whitespace with single space
    import re
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters except basic punctuation
    text = re.sub(r'[^\w\s\-.,;:!?()]', '', text)
    
    return text.strip()


class DataConverter:
    """Utility class for common data conversions."""
    
    @staticmethod
    def to_bool(value: Any) -> bool:
        """Convert various types to boolean."""
        if isinstance(value, bool):
            return value
        elif isinstance(value, str):
            return value.lower() in ('true', '1', 'yes', 'on', 'enabled')
        elif isinstance(value, (int, float)):
            return value != 0
        else:
            return bool(value)
    
    @staticmethod
    def to_list(value: Any, separator: str = ',') -> List[Any]:
        """Convert various types to list."""
        if isinstance(value, list):
            return value
        elif isinstance(value, str):
            if value.strip().startswith('['):
                try:
                    return json.loads(value)
                except:
                    pass
            return [x.strip() for x in value.split(separator) if x.strip()]
        elif value is None:
            return []
        else:
            return [value]
    
    @staticmethod
    def to_dict(value: Any) -> Dict[str, Any]:
        """Convert various types to dictionary."""
        if isinstance(value, dict):
            return value
        elif isinstance(value, str):
            try:
                return json.loads(value)
            except:
                return {"value": value}
        elif hasattr(value, 'to_dict'):
            return value.to_dict()
        elif hasattr(value, '__dict__'):
            return value.__dict__
        else:
            return {"value": value}