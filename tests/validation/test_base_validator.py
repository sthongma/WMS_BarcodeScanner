"""
Tests for BaseValidator class

This module tests the base validator functionality including:
- ValidationResult class
- All static helper methods
- Common validation operations
"""
import pytest
from datetime import datetime
from src.validation.base_validator import BaseValidator, ValidationResult
from src import constants


class ConcreteValidator(BaseValidator):
    """Concrete implementation of BaseValidator for testing"""

    def validate(self, data):
        """Simple validation for testing"""
        if not data:
            return self.create_error_result("Data cannot be empty")
        return self.create_success_result("Validation passed")


@pytest.fixture
def validator():
    """Create a concrete validator instance for testing"""
    return ConcreteValidator()


@pytest.mark.unit
@pytest.mark.validation
class TestValidationResult:
    """Test ValidationResult class"""

    def test_init_success(self):
        """Test ValidationResult initialization with success"""
        result = ValidationResult(is_valid=True, message="Success")
        assert result.is_valid is True
        assert result.message == "Success"
        assert result.errors == []

    def test_init_failure(self):
        """Test ValidationResult initialization with failure"""
        errors = ["Error 1", "Error 2"]
        result = ValidationResult(is_valid=False, message="Failed", errors=errors)
        assert result.is_valid is False
        assert result.message == "Failed"
        assert result.errors == errors

    def test_init_default_errors(self):
        """Test ValidationResult with default empty errors list"""
        result = ValidationResult(is_valid=True, message="Test")
        assert result.errors == []

    def test_to_dict_success(self):
        """Test to_dict conversion for success result"""
        result = ValidationResult(is_valid=True, message="Success")
        result_dict = result.to_dict()

        assert result_dict["success"] is True
        assert result_dict["message"] == "Success"
        assert result_dict["errors"] == []

    def test_to_dict_failure(self):
        """Test to_dict conversion for failure result"""
        errors = ["Error 1", "Error 2"]
        result = ValidationResult(is_valid=False, message="Failed", errors=errors)
        result_dict = result.to_dict()

        assert result_dict["success"] is False
        assert result_dict["message"] == "Failed"
        assert result_dict["errors"] == errors

    def test_bool_true(self):
        """Test boolean evaluation returns True for valid result"""
        result = ValidationResult(is_valid=True, message="Success")
        assert bool(result) is True
        assert result  # Direct boolean check

    def test_bool_false(self):
        """Test boolean evaluation returns False for invalid result"""
        result = ValidationResult(is_valid=False, message="Failed")
        assert bool(result) is False
        assert not result  # Direct boolean check

    def test_boolean_in_conditional(self):
        """Test using ValidationResult in if statements"""
        valid_result = ValidationResult(is_valid=True)
        invalid_result = ValidationResult(is_valid=False)

        if valid_result:
            valid_check = True
        else:
            valid_check = False

        if invalid_result:
            invalid_check = True
        else:
            invalid_check = False

        assert valid_check is True
        assert invalid_check is False


@pytest.mark.unit
@pytest.mark.validation
class TestBaseValidatorHelpers:
    """Test static helper methods in BaseValidator"""

    def test_is_not_empty_valid_string(self, validator):
        """Test is_not_empty with valid non-empty string"""
        assert validator.is_not_empty("test") is True
        assert validator.is_not_empty("Hello World") is True
        assert validator.is_not_empty("123") is True

    def test_is_not_empty_with_spaces(self, validator):
        """Test is_not_empty strips whitespace"""
        assert validator.is_not_empty("  test  ") is True

    def test_is_not_empty_empty_string(self, validator):
        """Test is_not_empty with empty string"""
        assert validator.is_not_empty("") is False
        assert validator.is_not_empty("   ") is False

    def test_is_not_empty_none(self, validator):
        """Test is_not_empty with None"""
        assert validator.is_not_empty(None) is False

    def test_is_positive_integer_valid(self, validator):
        """Test is_positive_integer with valid positive integers"""
        assert validator.is_positive_integer(1) is True
        assert validator.is_positive_integer(100) is True
        assert validator.is_positive_integer("5") is True
        assert validator.is_positive_integer("999") is True

    def test_is_positive_integer_zero(self, validator):
        """Test is_positive_integer with zero (should be False)"""
        assert validator.is_positive_integer(0) is False
        assert validator.is_positive_integer("0") is False

    def test_is_positive_integer_negative(self, validator):
        """Test is_positive_integer with negative numbers"""
        assert validator.is_positive_integer(-1) is False
        assert validator.is_positive_integer(-100) is False
        assert validator.is_positive_integer("-5") is False

    def test_is_positive_integer_invalid(self, validator):
        """Test is_positive_integer with invalid values"""
        assert validator.is_positive_integer("abc") is False
        assert validator.is_positive_integer("12.5") is False
        assert validator.is_positive_integer(None) is False
        assert validator.is_positive_integer("") is False

    def test_is_valid_date_format_valid(self, validator):
        """Test is_valid_date_format with valid dates"""
        assert validator.is_valid_date_format("2024-01-01") is True
        assert validator.is_valid_date_format("2024-12-31") is True
        assert validator.is_valid_date_format("2023-06-15") is True

    def test_is_valid_date_format_invalid(self, validator):
        """Test is_valid_date_format with invalid dates"""
        assert validator.is_valid_date_format("2024-13-01") is False  # Invalid month
        assert validator.is_valid_date_format("2024-01-32") is False  # Invalid day
        assert validator.is_valid_date_format("01-01-2024") is False  # Wrong format
        assert validator.is_valid_date_format("2024/01/01") is False  # Wrong delimiter
        assert validator.is_valid_date_format("not-a-date") is False

    def test_is_valid_date_format_empty(self, validator):
        """Test is_valid_date_format with empty string"""
        assert validator.is_valid_date_format("") is False
        assert validator.is_valid_date_format(None) is False

    def test_is_valid_date_format_custom_format(self, validator):
        """Test is_valid_date_format with custom format"""
        assert validator.is_valid_date_format("01/01/2024", "%m/%d/%Y") is True
        assert validator.is_valid_date_format("2024-01-01", "%m/%d/%Y") is False

    def test_is_within_range_valid(self, validator):
        """Test is_within_range with values in range"""
        assert validator.is_within_range(5, 1, 10) is True
        assert validator.is_within_range(1, 1, 10) is True  # Min boundary
        assert validator.is_within_range(10, 1, 10) is True  # Max boundary
        assert validator.is_within_range(5.5, 1, 10) is True

    def test_is_within_range_out_of_range(self, validator):
        """Test is_within_range with values out of range"""
        assert validator.is_within_range(0, 1, 10) is False
        assert validator.is_within_range(11, 1, 10) is False
        assert validator.is_within_range(-5, 1, 10) is False

    def test_is_within_range_no_min(self, validator):
        """Test is_within_range with no minimum"""
        assert validator.is_within_range(-100, None, 10) is True
        assert validator.is_within_range(5, None, 10) is True
        assert validator.is_within_range(11, None, 10) is False

    def test_is_within_range_no_max(self, validator):
        """Test is_within_range with no maximum"""
        assert validator.is_within_range(1000, 1, None) is True
        assert validator.is_within_range(5, 1, None) is True
        assert validator.is_within_range(0, 1, None) is False

    def test_is_within_range_no_bounds(self, validator):
        """Test is_within_range with no boundaries"""
        assert validator.is_within_range(-1000, None, None) is True
        assert validator.is_within_range(1000, None, None) is True
        assert validator.is_within_range(0, None, None) is True

    def test_is_within_range_invalid_value(self, validator):
        """Test is_within_range with invalid values"""
        assert validator.is_within_range("abc", 1, 10) is False
        assert validator.is_within_range(None, 1, 10) is False

    def test_has_required_keys_all_present(self, validator):
        """Test has_required_keys when all keys present"""
        data = {"name": "test", "age": 25, "city": "Bangkok"}
        all_present, missing = validator.has_required_keys(data, ["name", "age"])

        assert all_present is True
        assert missing == []

    def test_has_required_keys_some_missing(self, validator):
        """Test has_required_keys when some keys missing"""
        data = {"name": "test", "age": 25}
        all_present, missing = validator.has_required_keys(data, ["name", "age", "city"])

        assert all_present is False
        assert "city" in missing
        assert len(missing) == 1

    def test_has_required_keys_all_missing(self, validator):
        """Test has_required_keys when all keys missing"""
        data = {"other": "value"}
        all_present, missing = validator.has_required_keys(data, ["name", "age", "city"])

        assert all_present is False
        assert len(missing) == 3
        assert "name" in missing
        assert "age" in missing
        assert "city" in missing

    def test_has_required_keys_empty_dict(self, validator):
        """Test has_required_keys with empty dictionary"""
        data = {}
        all_present, missing = validator.has_required_keys(data, ["name", "age"])

        assert all_present is False
        assert len(missing) == 2

    def test_has_required_keys_not_dict(self, validator):
        """Test has_required_keys with non-dictionary"""
        all_present, missing = validator.has_required_keys("not a dict", ["name", "age"])

        assert all_present is False
        assert len(missing) == 2

    def test_is_valid_email_valid(self, validator):
        """Test is_valid_email with valid email addresses"""
        assert validator.is_valid_email("test@example.com") is True
        assert validator.is_valid_email("user.name@domain.co.th") is True
        assert validator.is_valid_email("test123@test-domain.com") is True

    def test_is_valid_email_invalid(self, validator):
        """Test is_valid_email with invalid email addresses"""
        assert validator.is_valid_email("notemail") is False
        assert validator.is_valid_email("@example.com") is False
        assert validator.is_valid_email("test@") is False
        assert validator.is_valid_email("") is False
        assert validator.is_valid_email("test@@example.com") is False

    def test_is_valid_email_none(self, validator):
        """Test is_valid_email with None"""
        assert validator.is_valid_email(None) is False


@pytest.mark.unit
@pytest.mark.validation
class TestBaseValidatorResultCreators:
    """Test result creator methods"""

    def test_create_success_result_no_message(self, validator):
        """Test create_success_result without message"""
        result = validator.create_success_result()

        assert result.is_valid is True
        assert result.message == ""
        assert result.errors == []

    def test_create_success_result_with_message(self, validator):
        """Test create_success_result with message"""
        result = validator.create_success_result("Operation successful")

        assert result.is_valid is True
        assert result.message == "Operation successful"
        assert result.errors == []

    def test_create_error_result_message_only(self, validator):
        """Test create_error_result with message only"""
        result = validator.create_error_result("Operation failed")

        assert result.is_valid is False
        assert result.message == "Operation failed"
        assert result.errors is None or result.errors == []

    def test_create_error_result_with_errors(self, validator):
        """Test create_error_result with error list"""
        errors = ["Error 1", "Error 2", "Error 3"]
        result = validator.create_error_result("Multiple errors", errors)

        assert result.is_valid is False
        assert result.message == "Multiple errors"
        assert result.errors == errors


@pytest.mark.unit
@pytest.mark.validation
class TestConcreteValidatorImplementation:
    """Test concrete validator implementation"""

    def test_validate_success(self, validator):
        """Test validate method with valid data"""
        result = validator.validate("valid data")

        assert result.is_valid is True
        assert result.message == "Validation passed"

    def test_validate_failure(self, validator):
        """Test validate method with invalid data"""
        result = validator.validate("")

        assert result.is_valid is False
        assert result.message == "Data cannot be empty"

    def test_validate_none(self, validator):
        """Test validate method with None"""
        result = validator.validate(None)

        assert result.is_valid is False

    def test_validate_returns_validation_result(self, validator):
        """Test validate returns ValidationResult instance"""
        result = validator.validate("test")

        assert isinstance(result, ValidationResult)
