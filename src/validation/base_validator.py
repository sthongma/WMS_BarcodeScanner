"""
Base Validator - Abstract base class for all validators
Provides common validation methods and result structure
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from src import constants


class ValidationResult:
    """Result of a validation operation"""

    def __init__(self, is_valid: bool, message: str = "", errors: Optional[List[str]] = None):
        self.is_valid = is_valid
        self.message = message
        self.errors = errors or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "success": self.is_valid,
            "message": self.message,
            "errors": self.errors,
        }

    def __bool__(self) -> bool:
        """Allow boolean evaluation: if validation_result: ..."""
        return self.is_valid


class BaseValidator(ABC):
    """
    Abstract base validator class
    All validators should inherit from this class
    """

    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """
        Validate the given data
        Must be implemented by subclasses

        Args:
            data: Data to validate

        Returns:
            ValidationResult: Result of validation
        """
        pass

    @staticmethod
    def is_not_empty(value: Optional[str]) -> bool:
        """Check if string value is not empty"""
        return value is not None and str(value).strip() != ""

    @staticmethod
    def is_positive_integer(value: Any) -> bool:
        """Check if value is a positive integer"""
        try:
            int_value = int(value)
            return int_value > 0
        except (ValueError, TypeError):
            return False

    @staticmethod
    def is_valid_date_format(date_string: str, format_string: str = constants.DATE_FORMAT) -> bool:
        """
        Check if date string matches the given format

        Args:
            date_string: Date string to validate
            format_string: Expected date format (default: YYYY-MM-DD)

        Returns:
            bool: True if valid, False otherwise
        """
        if not date_string:
            return False
        try:
            datetime.strptime(date_string, format_string)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_within_range(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
        """
        Check if numeric value is within range

        Args:
            value: Value to check
            min_val: Minimum value (inclusive), None for no minimum
            max_val: Maximum value (inclusive), None for no maximum

        Returns:
            bool: True if within range, False otherwise
        """
        try:
            num_value = float(value)
            if min_val is not None and num_value < min_val:
                return False
            if max_val is not None and num_value > max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def has_required_keys(data: Dict, required_keys: List[str]) -> tuple[bool, List[str]]:
        """
        Check if dictionary has all required keys

        Args:
            data: Dictionary to check
            required_keys: List of required key names

        Returns:
            tuple: (all_present, missing_keys)
        """
        if not isinstance(data, dict):
            return False, required_keys

        missing = [key for key in required_keys if key not in data]
        return len(missing) == 0, missing

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Basic email validation

        Args:
            email: Email address to validate

        Returns:
            bool: True if valid email format, False otherwise
        """
        if not email or "@" not in email:
            return False
        parts = email.split("@")
        return len(parts) == 2 and all(part.strip() for part in parts)

    @staticmethod
    def create_success_result(message: str = "") -> ValidationResult:
        """Create a successful validation result"""
        return ValidationResult(is_valid=True, message=message)

    @staticmethod
    def create_error_result(message: str, errors: Optional[List[str]] = None) -> ValidationResult:
        """Create a failed validation result"""
        return ValidationResult(is_valid=False, message=message, errors=errors)
