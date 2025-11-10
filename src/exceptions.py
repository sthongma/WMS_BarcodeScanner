"""
Custom Exception Classes for WMS Barcode Scanner
Provides a hierarchy of exceptions for different error types
"""


class WMSBaseException(Exception):
    """Base exception for all WMS Barcode Scanner exceptions"""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            details_str = ", ".join([f"{k}={v}" for k, v in self.details.items()])
            return f"{self.message} ({details_str})"
        return self.message


class DatabaseException(WMSBaseException):
    """Exception raised for database-related errors"""

    pass


class ConnectionException(DatabaseException):
    """Exception raised when database connection fails"""

    def __init__(self, message: str = "Failed to connect to database", details: dict = None):
        super().__init__(message, details)


class QueryException(DatabaseException):
    """Exception raised when a database query fails"""

    def __init__(self, message: str = "Database query failed", query: str = None, details: dict = None):
        details = details or {}
        if query:
            details["query"] = query
        super().__init__(message, details)


class RepositoryException(WMSBaseException):
    """Exception raised for repository layer errors"""

    pass


class RecordNotFoundException(RepositoryException):
    """Exception raised when a requested record is not found"""

    def __init__(self, entity: str, identifier: any, details: dict = None):
        message = f"{entity} not found"
        details = details or {}
        details["identifier"] = identifier
        super().__init__(message, details)


class DuplicateRecordException(RepositoryException):
    """Exception raised when attempting to create a duplicate record"""

    def __init__(self, entity: str, identifier: any, details: dict = None):
        message = f"Duplicate {entity} found"
        details = details or {}
        details["identifier"] = identifier
        super().__init__(message, details)


class ServiceException(WMSBaseException):
    """Exception raised for service layer errors"""

    pass


class ValidationException(ServiceException):
    """Exception raised when validation fails"""

    def __init__(self, message: str = "Validation failed", errors: list = None, details: dict = None):
        details = details or {}
        if errors:
            details["errors"] = errors
        super().__init__(message, details)


class BusinessRuleException(ServiceException):
    """Exception raised when a business rule is violated"""

    pass


class DependencyException(BusinessRuleException):
    """Exception raised when dependencies are not met"""

    def __init__(self, message: str = "Dependencies not met", missing_dependencies: list = None, details: dict = None):
        details = details or {}
        if missing_dependencies:
            details["missing_dependencies"] = missing_dependencies
        super().__init__(message, details)


class ConfigurationException(WMSBaseException):
    """Exception raised for configuration errors"""

    def __init__(self, message: str = "Configuration error", config_key: str = None, details: dict = None):
        details = details or {}
        if config_key:
            details["config_key"] = config_key
        super().__init__(message, details)


class ImportException(WMSBaseException):
    """Exception raised during data import operations"""

    def __init__(self, message: str = "Import failed", row_number: int = None, details: dict = None):
        details = details or {}
        if row_number is not None:
            details["row_number"] = row_number
        super().__init__(message, details)


class ExportException(WMSBaseException):
    """Exception raised during data export operations"""

    pass


class AuthenticationException(WMSBaseException):
    """Exception raised for authentication failures"""

    pass


class AuthorizationException(WMSBaseException):
    """Exception raised for authorization failures"""

    def __init__(self, message: str = "Access denied", required_permission: str = None, details: dict = None):
        details = details or {}
        if required_permission:
            details["required_permission"] = required_permission
        super().__init__(message, details)


class FileException(WMSBaseException):
    """Exception raised for file operation errors"""

    def __init__(self, message: str = "File operation failed", file_path: str = None, details: dict = None):
        details = details or {}
        if file_path:
            details["file_path"] = file_path
        super().__init__(message, details)


# Exception mapping for HTTP status codes (useful for web app)
EXCEPTION_STATUS_CODES = {
    WMSBaseException: 500,
    DatabaseException: 500,
    ConnectionException: 503,
    QueryException: 500,
    RepositoryException: 500,
    RecordNotFoundException: 404,
    DuplicateRecordException: 409,
    ServiceException: 500,
    ValidationException: 400,
    BusinessRuleException: 422,
    DependencyException: 422,
    ConfigurationException: 500,
    ImportException: 400,
    ExportException: 500,
    AuthenticationException: 401,
    AuthorizationException: 403,
    FileException: 500,
}


def get_exception_status_code(exception: Exception) -> int:
    """
    Get HTTP status code for an exception

    Args:
        exception: Exception instance

    Returns:
        int: HTTP status code
    """
    exception_type = type(exception)
    return EXCEPTION_STATUS_CODES.get(exception_type, 500)
