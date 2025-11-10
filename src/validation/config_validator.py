"""
Config Validator - Validates configuration settings
"""

from typing import Any, Dict, List, Optional
from src.validation.base_validator import BaseValidator, ValidationResult
from src import constants


class ConfigValidator(BaseValidator):
    """Validator for configuration settings"""

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """
        Validate configuration dictionary

        Args:
            data: Configuration dictionary

        Returns:
            ValidationResult: Validation result
        """
        if not isinstance(data, dict):
            return self.create_error_result("Configuration must be a dictionary")

        errors = []

        # Validate database connection config
        db_result = self.validate_database_config(data)
        if not db_result:
            errors.extend(db_result.errors)

        if errors:
            return self.create_error_result(
                "Configuration validation failed",
                errors
            )

        return self.create_success_result("Configuration is valid")

    def validate_database_config(self, config: Dict[str, Any]) -> ValidationResult:
        """
        Validate database connection configuration

        Args:
            config: Configuration dictionary containing database settings

        Returns:
            ValidationResult: Validation result
        """
        errors = []

        # Check required keys
        required_keys = ['server', 'database', 'auth_type']
        all_present, missing = self.has_required_keys(config, required_keys)

        if not all_present:
            return self.create_error_result(
                f"Missing required configuration keys: {', '.join(missing)}",
                [f"Missing: {key}" for key in missing]
            )

        # Validate server name
        server_result = self.validate_server_name(config.get('server'))
        if not server_result:
            errors.append(server_result.message)

        # Validate database name
        db_result = self.validate_database_name(config.get('database'))
        if not db_result:
            errors.append(db_result.message)

        # Validate auth type
        auth_result = self.validate_auth_type(config.get('auth_type'))
        if not auth_result:
            errors.append(auth_result.message)

        # Validate credentials for SQL auth
        if config.get('auth_type') == constants.AUTH_TYPE_SQL:
            creds_result = self.validate_sql_credentials(
                config.get('username'),
                config.get('password')
            )
            if not creds_result:
                errors.extend(creds_result.errors)

        if errors:
            return self.create_error_result(
                "Database configuration validation failed",
                errors
            )

        return self.create_success_result()

    def validate_server_name(self, server: Any) -> ValidationResult:
        """
        Validate server name is not empty

        Args:
            server: Server name value

        Returns:
            ValidationResult: Validation result
        """
        if not self.is_not_empty(server):
            return self.create_error_result("Server name cannot be empty")

        # Additional server name format validation can be added here
        # For example: check for invalid characters, length limits, etc.

        return self.create_success_result()

    def validate_database_name(self, database: Any) -> ValidationResult:
        """
        Validate database name is not empty

        Args:
            database: Database name value

        Returns:
            ValidationResult: Validation result
        """
        if not self.is_not_empty(database):
            return self.create_error_result("Database name cannot be empty")

        # Additional database name format validation can be added here
        # For example: check for invalid characters, length limits, etc.

        return self.create_success_result()

    def validate_auth_type(self, auth_type: Any) -> ValidationResult:
        """
        Validate authentication type (SQL or Windows)

        Args:
            auth_type: Authentication type value

        Returns:
            ValidationResult: Validation result
        """
        if not self.is_not_empty(auth_type):
            return self.create_error_result("Authentication type cannot be empty")

        valid_auth_types = [constants.AUTH_TYPE_SQL, constants.AUTH_TYPE_WINDOWS]

        if auth_type not in valid_auth_types:
            return self.create_error_result(
                f"Authentication type must be one of: {', '.join(valid_auth_types)}. Got: {auth_type}"
            )

        return self.create_success_result()

    def validate_sql_credentials(
        self,
        username: Optional[str],
        password: Optional[str]
    ) -> ValidationResult:
        """
        Validate SQL authentication credentials

        Args:
            username: SQL username
            password: SQL password

        Returns:
            ValidationResult: Validation result
        """
        errors = []

        if not self.is_not_empty(username):
            errors.append("Username is required for SQL authentication")

        if not self.is_not_empty(password):
            errors.append("Password is required for SQL authentication")

        if errors:
            return self.create_error_result(
                "SQL credentials validation failed",
                errors
            )

        return self.create_success_result()

    def validate_windows_auth(self) -> ValidationResult:
        """
        Validate Windows authentication configuration

        Args:
            None - Windows auth doesn't require additional credentials

        Returns:
            ValidationResult: Validation result
        """
        # Windows authentication doesn't require additional validation
        # as it uses the current Windows user's credentials
        return self.create_success_result()

    def validate_connection_string(self, connection_string: str) -> ValidationResult:
        """
        Validate connection string format

        Args:
            connection_string: Database connection string

        Returns:
            ValidationResult: Validation result
        """
        if not self.is_not_empty(connection_string):
            return self.create_error_result("Connection string cannot be empty")

        # Check for required components in connection string
        required_components = ['DRIVER', 'SERVER', 'DATABASE']
        missing = []

        for component in required_components:
            if component not in connection_string.upper():
                missing.append(component)

        if missing:
            return self.create_error_result(
                f"Connection string missing required components: {', '.join(missing)}",
                [f"Missing: {comp}" for comp in missing]
            )

        return self.create_success_result()

    def validate_port(self, port: Any) -> ValidationResult:
        """
        Validate port number (optional field)

        Args:
            port: Port number value

        Returns:
            ValidationResult: Validation result
        """
        # Port is optional, so None/empty is valid
        if port is None or str(port).strip() == "":
            return self.create_success_result()

        # If port is provided, validate it
        if not self.is_positive_integer(port):
            return self.create_error_result("Port must be a positive integer")

        # Check port is within valid range (1-65535)
        if not self.is_within_range(port, 1, 65535):
            return self.create_error_result("Port must be between 1 and 65535")

        return self.create_success_result()

    def validate_timeout(self, timeout: Any) -> ValidationResult:
        """
        Validate connection timeout value (optional field)

        Args:
            timeout: Timeout value in seconds

        Returns:
            ValidationResult: Validation result
        """
        # Timeout is optional
        if timeout is None or str(timeout).strip() == "":
            return self.create_success_result()

        # If timeout is provided, validate it
        if not self.is_positive_integer(timeout):
            return self.create_error_result("Timeout must be a positive integer")

        # Reasonable timeout range: 1-300 seconds
        if not self.is_within_range(timeout, 1, 300):
            return self.create_error_result("Timeout must be between 1 and 300 seconds")

        return self.create_success_result()

    def validate_config_file_path(self, file_path: str) -> ValidationResult:
        """
        Validate configuration file path

        Args:
            file_path: Path to configuration file

        Returns:
            ValidationResult: Validation result
        """
        if not self.is_not_empty(file_path):
            return self.create_error_result("Configuration file path cannot be empty")

        # Additional path validation can be added here
        # For example: check for valid path format, file extension, etc.

        return self.create_success_result()
