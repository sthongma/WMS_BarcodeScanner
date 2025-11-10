"""
Comprehensive tests for custom exception classes

Tests all custom exception classes and their behavior, including
exception hierarchy, details handling, and status code mapping.
"""
import pytest
from src.exceptions import (
    WMSBaseException,
    DatabaseException,
    ConnectionException,
    QueryException,
    RepositoryException,
    RecordNotFoundException,
    DuplicateRecordException,
    ServiceException,
    ValidationException,
    BusinessRuleException,
    DependencyException,
    ConfigurationException,
    ImportException,
    ExportException,
    AuthenticationException,
    AuthorizationException,
    FileException,
    EXCEPTION_STATUS_CODES,
    get_exception_status_code,
)


class TestWMSBaseException:
    """Test the base WMS exception class"""

    def test_base_exception_with_message_only(self):
        """Test creating base exception with just a message"""
        exc = WMSBaseException("Something went wrong")
        assert exc.message == "Something went wrong"
        assert exc.details == {}
        assert str(exc) == "Something went wrong"

    def test_base_exception_with_details(self):
        """Test creating base exception with details"""
        details = {"key1": "value1", "key2": "value2"}
        exc = WMSBaseException("Error occurred", details=details)
        assert exc.message == "Error occurred"
        assert exc.details == details
        assert "key1=value1" in str(exc)
        assert "key2=value2" in str(exc)

    def test_base_exception_string_representation(self):
        """Test string representation of exception"""
        exc = WMSBaseException("Test error", details={"code": 123})
        result = str(exc)
        assert "Test error" in result
        assert "code=123" in result

    def test_base_exception_can_be_raised(self):
        """Test that exception can be raised and caught"""
        with pytest.raises(WMSBaseException) as exc_info:
            raise WMSBaseException("Test exception")
        assert str(exc_info.value) == "Test exception"

    def test_base_exception_inherits_from_exception(self):
        """Test that WMSBaseException inherits from Exception"""
        exc = WMSBaseException("Test")
        assert isinstance(exc, Exception)

    def test_base_exception_with_empty_details(self):
        """Test exception with explicitly empty details dict"""
        exc = WMSBaseException("Error", details={})
        assert exc.details == {}
        assert str(exc) == "Error"


class TestDatabaseException:
    """Test database-related exceptions"""

    def test_database_exception_basic(self):
        """Test basic database exception"""
        exc = DatabaseException("Database error")
        assert exc.message == "Database error"
        assert isinstance(exc, WMSBaseException)

    def test_database_exception_with_details(self):
        """Test database exception with details"""
        exc = DatabaseException("Query failed", details={"table": "users"})
        assert exc.details["table"] == "users"

    def test_connection_exception_default_message(self):
        """Test ConnectionException with default message"""
        exc = ConnectionException()
        assert exc.message == "Failed to connect to database"
        assert isinstance(exc, DatabaseException)

    def test_connection_exception_custom_message(self):
        """Test ConnectionException with custom message"""
        exc = ConnectionException("Cannot reach server")
        assert exc.message == "Cannot reach server"

    def test_connection_exception_with_details(self):
        """Test ConnectionException with details"""
        exc = ConnectionException(details={"server": "localhost", "port": 1433})
        assert exc.details["server"] == "localhost"
        assert exc.details["port"] == 1433

    def test_query_exception_default_message(self):
        """Test QueryException with default message"""
        exc = QueryException()
        assert exc.message == "Database query failed"

    def test_query_exception_with_query(self):
        """Test QueryException with query string"""
        exc = QueryException(query="SELECT * FROM users")
        assert exc.details["query"] == "SELECT * FROM users"

    def test_query_exception_with_query_and_details(self):
        """Test QueryException with both query and details"""
        exc = QueryException(
            message="Invalid query",
            query="SELECT * FROM unknown",
            details={"error_code": 1234}
        )
        assert exc.message == "Invalid query"
        assert exc.details["query"] == "SELECT * FROM unknown"
        assert exc.details["error_code"] == 1234


class TestRepositoryException:
    """Test repository-related exceptions"""

    def test_repository_exception_basic(self):
        """Test basic repository exception"""
        exc = RepositoryException("Repository error")
        assert exc.message == "Repository error"
        assert isinstance(exc, WMSBaseException)

    def test_record_not_found_exception(self):
        """Test RecordNotFoundException"""
        exc = RecordNotFoundException(entity="User", identifier=123)
        assert exc.message == "User not found"
        assert exc.details["identifier"] == 123
        assert isinstance(exc, RepositoryException)

    def test_record_not_found_with_string_identifier(self):
        """Test RecordNotFoundException with string identifier"""
        exc = RecordNotFoundException(entity="Product", identifier="ABC123")
        assert exc.message == "Product not found"
        assert exc.details["identifier"] == "ABC123"

    def test_record_not_found_with_additional_details(self):
        """Test RecordNotFoundException with additional details"""
        exc = RecordNotFoundException(
            entity="Order",
            identifier=456,
            details={"status": "searching"}
        )
        assert exc.message == "Order not found"
        assert exc.details["identifier"] == 456
        assert exc.details["status"] == "searching"

    def test_duplicate_record_exception(self):
        """Test DuplicateRecordException"""
        exc = DuplicateRecordException(entity="User", identifier="john@example.com")
        assert exc.message == "Duplicate User found"
        assert exc.details["identifier"] == "john@example.com"
        assert isinstance(exc, RepositoryException)

    def test_duplicate_record_with_details(self):
        """Test DuplicateRecordException with additional details"""
        exc = DuplicateRecordException(
            entity="Product",
            identifier="SKU123",
            details={"warehouse": "WH01"}
        )
        assert exc.details["identifier"] == "SKU123"
        assert exc.details["warehouse"] == "WH01"


class TestServiceException:
    """Test service-related exceptions"""

    def test_service_exception_basic(self):
        """Test basic service exception"""
        exc = ServiceException("Service error")
        assert exc.message == "Service error"
        assert isinstance(exc, WMSBaseException)

    def test_validation_exception_default(self):
        """Test ValidationException with default message"""
        exc = ValidationException()
        assert exc.message == "Validation failed"

    def test_validation_exception_with_errors_list(self):
        """Test ValidationException with errors list"""
        errors = ["Field1 is required", "Field2 is invalid"]
        exc = ValidationException(errors=errors)
        assert exc.details["errors"] == errors

    def test_validation_exception_with_custom_message_and_errors(self):
        """Test ValidationException with custom message and errors"""
        errors = ["Email format invalid", "Password too short"]
        exc = ValidationException(message="Form validation failed", errors=errors)
        assert exc.message == "Form validation failed"
        assert exc.details["errors"] == errors

    def test_validation_exception_with_details(self):
        """Test ValidationException with additional details"""
        exc = ValidationException(
            message="Validation error",
            errors=["Error1"],
            details={"field": "email"}
        )
        assert exc.details["errors"] == ["Error1"]
        assert exc.details["field"] == "email"

    def test_business_rule_exception(self):
        """Test BusinessRuleException"""
        exc = BusinessRuleException("Business rule violated")
        assert exc.message == "Business rule violated"
        assert isinstance(exc, ServiceException)

    def test_dependency_exception_default(self):
        """Test DependencyException with default message"""
        exc = DependencyException()
        assert exc.message == "Dependencies not met"
        assert isinstance(exc, BusinessRuleException)

    def test_dependency_exception_with_missing_dependencies(self):
        """Test DependencyException with missing dependencies list"""
        missing = ["lib1", "lib2", "lib3"]
        exc = DependencyException(missing_dependencies=missing)
        assert exc.details["missing_dependencies"] == missing

    def test_dependency_exception_complete(self):
        """Test DependencyException with all parameters"""
        missing = ["dependency1", "dependency2"]
        exc = DependencyException(
            message="Cannot proceed without dependencies",
            missing_dependencies=missing,
            details={"context": "initialization"}
        )
        assert exc.message == "Cannot proceed without dependencies"
        assert exc.details["missing_dependencies"] == missing
        assert exc.details["context"] == "initialization"


class TestConfigurationException:
    """Test configuration-related exceptions"""

    def test_configuration_exception_default(self):
        """Test ConfigurationException with default message"""
        exc = ConfigurationException()
        assert exc.message == "Configuration error"

    def test_configuration_exception_with_config_key(self):
        """Test ConfigurationException with config_key"""
        exc = ConfigurationException(config_key="database.host")
        assert exc.details["config_key"] == "database.host"

    def test_configuration_exception_complete(self):
        """Test ConfigurationException with all parameters"""
        exc = ConfigurationException(
            message="Missing required configuration",
            config_key="api.secret_key",
            details={"section": "api"}
        )
        assert exc.message == "Missing required configuration"
        assert exc.details["config_key"] == "api.secret_key"
        assert exc.details["section"] == "api"


class TestImportExportException:
    """Test import/export related exceptions"""

    def test_import_exception_default(self):
        """Test ImportException with default message"""
        exc = ImportException()
        assert exc.message == "Import failed"

    def test_import_exception_with_row_number(self):
        """Test ImportException with row_number"""
        exc = ImportException(row_number=42)
        assert exc.details["row_number"] == 42

    def test_import_exception_with_row_zero(self):
        """Test ImportException with row_number 0 (should be included)"""
        exc = ImportException(row_number=0)
        assert exc.details["row_number"] == 0

    def test_import_exception_complete(self):
        """Test ImportException with all parameters"""
        exc = ImportException(
            message="Invalid data format",
            row_number=15,
            details={"column": "price", "value": "invalid"}
        )
        assert exc.message == "Invalid data format"
        assert exc.details["row_number"] == 15
        assert exc.details["column"] == "price"

    def test_export_exception(self):
        """Test ExportException"""
        exc = ExportException("Export failed")
        assert exc.message == "Export failed"
        assert isinstance(exc, WMSBaseException)


class TestAuthenticationAuthorization:
    """Test authentication and authorization exceptions"""

    def test_authentication_exception(self):
        """Test AuthenticationException"""
        exc = AuthenticationException("Invalid credentials")
        assert exc.message == "Invalid credentials"
        assert isinstance(exc, WMSBaseException)

    def test_authorization_exception_default(self):
        """Test AuthorizationException with default message"""
        exc = AuthorizationException()
        assert exc.message == "Access denied"

    def test_authorization_exception_with_permission(self):
        """Test AuthorizationException with required_permission"""
        exc = AuthorizationException(required_permission="admin:write")
        assert exc.details["required_permission"] == "admin:write"

    def test_authorization_exception_complete(self):
        """Test AuthorizationException with all parameters"""
        exc = AuthorizationException(
            message="Insufficient permissions",
            required_permission="users:delete",
            details={"user_id": "user123"}
        )
        assert exc.message == "Insufficient permissions"
        assert exc.details["required_permission"] == "users:delete"
        assert exc.details["user_id"] == "user123"


class TestFileException:
    """Test file operation exceptions"""

    def test_file_exception_default(self):
        """Test FileException with default message"""
        exc = FileException()
        assert exc.message == "File operation failed"

    def test_file_exception_with_file_path(self):
        """Test FileException with file_path"""
        exc = FileException(file_path="/path/to/file.txt")
        assert exc.details["file_path"] == "/path/to/file.txt"

    def test_file_exception_complete(self):
        """Test FileException with all parameters"""
        exc = FileException(
            message="File not found",
            file_path="/data/import.csv",
            details={"operation": "read"}
        )
        assert exc.message == "File not found"
        assert exc.details["file_path"] == "/data/import.csv"
        assert exc.details["operation"] == "read"


class TestExceptionStatusCodes:
    """Test exception status code mapping"""

    def test_exception_status_codes_mapping_exists(self):
        """Test that EXCEPTION_STATUS_CODES dictionary exists"""
        assert isinstance(EXCEPTION_STATUS_CODES, dict)
        assert len(EXCEPTION_STATUS_CODES) > 0

    def test_base_exception_status_code(self):
        """Test status code for WMSBaseException"""
        assert EXCEPTION_STATUS_CODES[WMSBaseException] == 500

    def test_database_exception_status_codes(self):
        """Test status codes for database exceptions"""
        assert EXCEPTION_STATUS_CODES[DatabaseException] == 500
        assert EXCEPTION_STATUS_CODES[ConnectionException] == 503
        assert EXCEPTION_STATUS_CODES[QueryException] == 500

    def test_repository_exception_status_codes(self):
        """Test status codes for repository exceptions"""
        assert EXCEPTION_STATUS_CODES[RepositoryException] == 500
        assert EXCEPTION_STATUS_CODES[RecordNotFoundException] == 404
        assert EXCEPTION_STATUS_CODES[DuplicateRecordException] == 409

    def test_service_exception_status_codes(self):
        """Test status codes for service exceptions"""
        assert EXCEPTION_STATUS_CODES[ServiceException] == 500
        assert EXCEPTION_STATUS_CODES[ValidationException] == 400
        assert EXCEPTION_STATUS_CODES[BusinessRuleException] == 422
        assert EXCEPTION_STATUS_CODES[DependencyException] == 422

    def test_auth_exception_status_codes(self):
        """Test status codes for authentication/authorization exceptions"""
        assert EXCEPTION_STATUS_CODES[AuthenticationException] == 401
        assert EXCEPTION_STATUS_CODES[AuthorizationException] == 403

    def test_other_exception_status_codes(self):
        """Test status codes for other exceptions"""
        assert EXCEPTION_STATUS_CODES[ConfigurationException] == 500
        assert EXCEPTION_STATUS_CODES[ImportException] == 400
        assert EXCEPTION_STATUS_CODES[ExportException] == 500
        assert EXCEPTION_STATUS_CODES[FileException] == 500

    def test_get_exception_status_code_for_known_exception(self):
        """Test get_exception_status_code for known exception types"""
        exc = RecordNotFoundException("User", 123)
        status_code = get_exception_status_code(exc)
        assert status_code == 404

    def test_get_exception_status_code_for_validation_exception(self):
        """Test get_exception_status_code for ValidationException"""
        exc = ValidationException("Invalid input")
        status_code = get_exception_status_code(exc)
        assert status_code == 400

    def test_get_exception_status_code_for_unknown_exception(self):
        """Test get_exception_status_code for unknown exception type"""
        exc = ValueError("Some error")
        status_code = get_exception_status_code(exc)
        assert status_code == 500  # Default status code

    def test_get_exception_status_code_for_standard_exception(self):
        """Test get_exception_status_code for standard Python exception"""
        exc = RuntimeError("Runtime error")
        status_code = get_exception_status_code(exc)
        assert status_code == 500


class TestExceptionHierarchy:
    """Test exception inheritance hierarchy"""

    def test_database_exception_hierarchy(self):
        """Test DatabaseException is a WMSBaseException"""
        exc = DatabaseException("Test")
        assert isinstance(exc, WMSBaseException)
        assert isinstance(exc, Exception)

    def test_connection_exception_hierarchy(self):
        """Test ConnectionException hierarchy"""
        exc = ConnectionException()
        assert isinstance(exc, DatabaseException)
        assert isinstance(exc, WMSBaseException)

    def test_query_exception_hierarchy(self):
        """Test QueryException hierarchy"""
        exc = QueryException()
        assert isinstance(exc, DatabaseException)
        assert isinstance(exc, WMSBaseException)

    def test_repository_exception_hierarchy(self):
        """Test RepositoryException hierarchy"""
        exc = RepositoryException("Test")
        assert isinstance(exc, WMSBaseException)

    def test_record_not_found_hierarchy(self):
        """Test RecordNotFoundException hierarchy"""
        exc = RecordNotFoundException("User", 1)
        assert isinstance(exc, RepositoryException)
        assert isinstance(exc, WMSBaseException)

    def test_service_exception_hierarchy(self):
        """Test ServiceException hierarchy"""
        exc = ServiceException("Test")
        assert isinstance(exc, WMSBaseException)

    def test_validation_exception_hierarchy(self):
        """Test ValidationException hierarchy"""
        exc = ValidationException()
        assert isinstance(exc, ServiceException)
        assert isinstance(exc, WMSBaseException)

    def test_business_rule_exception_hierarchy(self):
        """Test BusinessRuleException hierarchy"""
        exc = BusinessRuleException("Test")
        assert isinstance(exc, ServiceException)
        assert isinstance(exc, WMSBaseException)

    def test_dependency_exception_hierarchy(self):
        """Test DependencyException hierarchy"""
        exc = DependencyException()
        assert isinstance(exc, BusinessRuleException)
        assert isinstance(exc, ServiceException)
        assert isinstance(exc, WMSBaseException)


class TestExceptionCatchPatterns:
    """Test exception catching patterns"""

    def test_catch_specific_exception(self):
        """Test catching specific exception type"""
        with pytest.raises(RecordNotFoundException):
            raise RecordNotFoundException("User", 123)

    def test_catch_parent_exception(self):
        """Test catching exception by parent type"""
        with pytest.raises(RepositoryException):
            raise RecordNotFoundException("User", 123)

    def test_catch_base_exception(self):
        """Test catching any WMS exception"""
        with pytest.raises(WMSBaseException):
            raise ValidationException("Invalid data")

    def test_catch_and_inspect_exception(self):
        """Test catching and inspecting exception details"""
        try:
            raise ValidationException(
                message="Invalid input",
                errors=["Field1 required", "Field2 invalid"]
            )
        except ValidationException as exc:
            assert exc.message == "Invalid input"
            assert len(exc.details["errors"]) == 2
            assert "Field1 required" in exc.details["errors"]
