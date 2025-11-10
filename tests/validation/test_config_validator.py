"""
Tests for ConfigValidator class

This module tests the config validator functionality including:
- Connection config validation
- Auth type validation
- Credentials validation
- Server and database name validation
"""
import pytest
from src.validation.config_validator import ConfigValidator
from src.validation.base_validator import ValidationResult
from src import constants


@pytest.fixture
def config_validator():
    """Create ConfigValidator instance for testing"""
    return ConfigValidator()


@pytest.mark.unit
@pytest.mark.validation
class TestConfigValidatorInitialization:
    """Test ConfigValidator initialization"""

    def test_init(self, config_validator):
        """Test ConfigValidator initializes correctly"""
        assert config_validator is not None
        assert isinstance(config_validator, ConfigValidator)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateServerName:
    """Test server name validation"""

    def test_validate_server_name_valid(self, config_validator):
        """Test validation passes with valid server name"""
        result = config_validator.validate_server_name("localhost\\SQLEXPRESS")

        assert result.is_valid is True

    def test_validate_server_name_simple(self, config_validator):
        """Test validation passes with simple server name"""
        result = config_validator.validate_server_name("localhost")

        assert result.is_valid is True

    def test_validate_server_name_empty_string(self, config_validator):
        """Test validation fails with empty string"""
        result = config_validator.validate_server_name("")

        assert result.is_valid is False
        assert "empty" in result.message.lower()

    def test_validate_server_name_whitespace(self, config_validator):
        """Test validation fails with whitespace only"""
        result = config_validator.validate_server_name("   ")

        assert result.is_valid is False

    def test_validate_server_name_none(self, config_validator):
        """Test validation fails with None"""
        result = config_validator.validate_server_name(None)

        assert result.is_valid is False


@pytest.mark.unit
@pytest.mark.validation
class TestValidateDatabaseName:
    """Test database name validation"""

    def test_validate_database_name_valid(self, config_validator):
        """Test validation passes with valid database name"""
        result = config_validator.validate_database_name("WMS_EP")

        assert result.is_valid is True

    def test_validate_database_name_empty_string(self, config_validator):
        """Test validation fails with empty string"""
        result = config_validator.validate_database_name("")

        assert result.is_valid is False
        assert "empty" in result.message.lower()

    def test_validate_database_name_whitespace(self, config_validator):
        """Test validation fails with whitespace only"""
        result = config_validator.validate_database_name("   ")

        assert result.is_valid is False

    def test_validate_database_name_none(self, config_validator):
        """Test validation fails with None"""
        result = config_validator.validate_database_name(None)

        assert result.is_valid is False


@pytest.mark.unit
@pytest.mark.validation
class TestValidateAuthType:
    """Test authentication type validation"""

    def test_validate_auth_type_sql(self, config_validator):
        """Test validation passes with SQL auth type"""
        result = config_validator.validate_auth_type(constants.AUTH_TYPE_SQL)

        assert result.is_valid is True

    def test_validate_auth_type_windows(self, config_validator):
        """Test validation passes with Windows auth type"""
        result = config_validator.validate_auth_type(constants.AUTH_TYPE_WINDOWS)

        assert result.is_valid is True

    def test_validate_auth_type_empty_string(self, config_validator):
        """Test validation fails with empty string"""
        result = config_validator.validate_auth_type("")

        assert result.is_valid is False
        assert "empty" in result.message.lower()

    def test_validate_auth_type_invalid(self, config_validator):
        """Test validation fails with invalid auth type"""
        result = config_validator.validate_auth_type("InvalidAuth")

        assert result.is_valid is False
        assert "InvalidAuth" in result.message

    def test_validate_auth_type_none(self, config_validator):
        """Test validation fails with None"""
        result = config_validator.validate_auth_type(None)

        assert result.is_valid is False

    def test_validate_auth_type_case_sensitive(self, config_validator):
        """Test validation is case sensitive"""
        result = config_validator.validate_auth_type("sql")  # lowercase

        assert result.is_valid is False


@pytest.mark.unit
@pytest.mark.validation
class TestValidateSqlCredentials:
    """Test SQL credentials validation"""

    def test_validate_sql_credentials_valid(self, config_validator):
        """Test validation passes with valid credentials"""
        result = config_validator.validate_sql_credentials("username", "password")

        assert result.is_valid is True

    def test_validate_sql_credentials_empty_username(self, config_validator):
        """Test validation fails with empty username"""
        result = config_validator.validate_sql_credentials("", "password")

        assert result.is_valid is False
        assert any("username" in err.lower() for err in result.errors)

    def test_validate_sql_credentials_empty_password(self, config_validator):
        """Test validation fails with empty password"""
        result = config_validator.validate_sql_credentials("username", "")

        assert result.is_valid is False
        assert any("password" in err.lower() for err in result.errors)

    def test_validate_sql_credentials_both_empty(self, config_validator):
        """Test validation fails with both credentials empty"""
        result = config_validator.validate_sql_credentials("", "")

        assert result.is_valid is False
        assert len(result.errors) == 2

    def test_validate_sql_credentials_none_username(self, config_validator):
        """Test validation fails with None username"""
        result = config_validator.validate_sql_credentials(None, "password")

        assert result.is_valid is False

    def test_validate_sql_credentials_none_password(self, config_validator):
        """Test validation fails with None password"""
        result = config_validator.validate_sql_credentials("username", None)

        assert result.is_valid is False

    def test_validate_sql_credentials_whitespace(self, config_validator):
        """Test validation fails with whitespace credentials"""
        result = config_validator.validate_sql_credentials("   ", "   ")

        assert result.is_valid is False


@pytest.mark.unit
@pytest.mark.validation
class TestValidateWindowsAuth:
    """Test Windows authentication validation"""

    def test_validate_windows_auth(self, config_validator):
        """Test Windows auth validation always passes"""
        result = config_validator.validate_windows_auth()

        assert result.is_valid is True


@pytest.mark.unit
@pytest.mark.validation
class TestValidateDatabaseConfig:
    """Test database configuration validation"""

    def test_validate_database_config_sql_auth_valid(self, config_validator):
        """Test validation passes with valid SQL auth config"""
        config = {
            "server": "localhost\\SQLEXPRESS",
            "database": "WMS_EP",
            "auth_type": constants.AUTH_TYPE_SQL,
            "username": "user",
            "password": "pass"
        }

        result = config_validator.validate_database_config(config)

        assert result.is_valid is True

    def test_validate_database_config_windows_auth_valid(self, config_validator):
        """Test validation passes with valid Windows auth config"""
        config = {
            "server": "localhost\\SQLEXPRESS",
            "database": "WMS_EP",
            "auth_type": constants.AUTH_TYPE_WINDOWS
        }

        result = config_validator.validate_database_config(config)

        assert result.is_valid is True

    def test_validate_database_config_missing_server(self, config_validator):
        """Test validation fails with missing server"""
        config = {
            "database": "WMS_EP",
            "auth_type": constants.AUTH_TYPE_SQL,
            "username": "user",
            "password": "pass"
        }

        result = config_validator.validate_database_config(config)

        assert result.is_valid is False
        assert "server" in result.message.lower()

    def test_validate_database_config_missing_database(self, config_validator):
        """Test validation fails with missing database"""
        config = {
            "server": "localhost",
            "auth_type": constants.AUTH_TYPE_SQL,
            "username": "user",
            "password": "pass"
        }

        result = config_validator.validate_database_config(config)

        assert result.is_valid is False
        assert "database" in result.message.lower()

    def test_validate_database_config_missing_auth_type(self, config_validator):
        """Test validation fails with missing auth type"""
        config = {
            "server": "localhost",
            "database": "WMS_EP",
            "username": "user",
            "password": "pass"
        }

        result = config_validator.validate_database_config(config)

        assert result.is_valid is False
        assert "auth_type" in result.message.lower()

    def test_validate_database_config_sql_missing_credentials(self, config_validator):
        """Test validation fails with SQL auth but missing credentials"""
        config = {
            "server": "localhost",
            "database": "WMS_EP",
            "auth_type": constants.AUTH_TYPE_SQL
        }

        result = config_validator.validate_database_config(config)

        assert result.is_valid is False

    def test_validate_database_config_empty_server(self, config_validator):
        """Test validation fails with empty server name"""
        config = {
            "server": "",
            "database": "WMS_EP",
            "auth_type": constants.AUTH_TYPE_WINDOWS
        }

        result = config_validator.validate_database_config(config)

        assert result.is_valid is False

    def test_validate_database_config_invalid_auth_type(self, config_validator):
        """Test validation fails with invalid auth type"""
        config = {
            "server": "localhost",
            "database": "WMS_EP",
            "auth_type": "InvalidAuth"
        }

        result = config_validator.validate_database_config(config)

        assert result.is_valid is False


@pytest.mark.unit
@pytest.mark.validation
class TestValidateConnectionString:
    """Test connection string validation"""

    def test_validate_connection_string_valid(self, config_validator):
        """Test validation passes with valid connection string"""
        conn_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=localhost;"
            "DATABASE=WMS_EP;"
        )

        result = config_validator.validate_connection_string(conn_str)

        assert result.is_valid is True

    def test_validate_connection_string_empty(self, config_validator):
        """Test validation fails with empty connection string"""
        result = config_validator.validate_connection_string("")

        assert result.is_valid is False

    def test_validate_connection_string_missing_driver(self, config_validator):
        """Test validation fails with missing DRIVER component"""
        conn_str = "SERVER=localhost;DATABASE=WMS_EP;"

        result = config_validator.validate_connection_string(conn_str)

        assert result.is_valid is False
        assert "DRIVER" in result.message

    def test_validate_connection_string_missing_server(self, config_validator):
        """Test validation fails with missing SERVER component"""
        conn_str = "DRIVER={ODBC Driver 17};DATABASE=WMS_EP;"

        result = config_validator.validate_connection_string(conn_str)

        assert result.is_valid is False
        assert "SERVER" in result.message

    def test_validate_connection_string_missing_database(self, config_validator):
        """Test validation fails with missing DATABASE component"""
        conn_str = "DRIVER={ODBC Driver 17};SERVER=localhost;"

        result = config_validator.validate_connection_string(conn_str)

        assert result.is_valid is False
        assert "DATABASE" in result.message


@pytest.mark.unit
@pytest.mark.validation
class TestValidatePort:
    """Test port validation"""

    def test_validate_port_valid(self, config_validator):
        """Test validation passes with valid port"""
        result = config_validator.validate_port(1433)

        assert result.is_valid is True

    def test_validate_port_none(self, config_validator):
        """Test validation passes with None (optional field)"""
        result = config_validator.validate_port(None)

        assert result.is_valid is True

    def test_validate_port_empty_string(self, config_validator):
        """Test validation passes with empty string (optional field)"""
        result = config_validator.validate_port("")

        assert result.is_valid is True

    def test_validate_port_zero(self, config_validator):
        """Test validation fails with zero"""
        result = config_validator.validate_port(0)

        assert result.is_valid is False

    def test_validate_port_negative(self, config_validator):
        """Test validation fails with negative port"""
        result = config_validator.validate_port(-1)

        assert result.is_valid is False

    def test_validate_port_too_large(self, config_validator):
        """Test validation fails with port > 65535"""
        result = config_validator.validate_port(70000)

        assert result.is_valid is False

    def test_validate_port_string(self, config_validator):
        """Test validation passes with string port number"""
        result = config_validator.validate_port("1433")

        assert result.is_valid is True


@pytest.mark.unit
@pytest.mark.validation
class TestValidateTimeout:
    """Test timeout validation"""

    def test_validate_timeout_valid(self, config_validator):
        """Test validation passes with valid timeout"""
        result = config_validator.validate_timeout(30)

        assert result.is_valid is True

    def test_validate_timeout_none(self, config_validator):
        """Test validation passes with None (optional field)"""
        result = config_validator.validate_timeout(None)

        assert result.is_valid is True

    def test_validate_timeout_empty_string(self, config_validator):
        """Test validation passes with empty string (optional field)"""
        result = config_validator.validate_timeout("")

        assert result.is_valid is True

    def test_validate_timeout_zero(self, config_validator):
        """Test validation fails with zero"""
        result = config_validator.validate_timeout(0)

        assert result.is_valid is False

    def test_validate_timeout_negative(self, config_validator):
        """Test validation fails with negative timeout"""
        result = config_validator.validate_timeout(-1)

        assert result.is_valid is False

    def test_validate_timeout_too_large(self, config_validator):
        """Test validation fails with timeout > 300"""
        result = config_validator.validate_timeout(500)

        assert result.is_valid is False


@pytest.mark.unit
@pytest.mark.validation
class TestFullValidation:
    """Test full configuration validation"""

    def test_validate_valid_config(self, config_validator):
        """Test validation passes with valid config"""
        config = {
            "server": "localhost\\SQLEXPRESS",
            "database": "WMS_EP",
            "auth_type": constants.AUTH_TYPE_SQL,
            "username": "user",
            "password": "pass"
        }

        result = config_validator.validate(config)

        assert result.is_valid is True

    def test_validate_not_dict(self, config_validator):
        """Test validation fails when config is not a dictionary"""
        result = config_validator.validate("not a dict")

        assert result.is_valid is False
        assert "dictionary" in result.message.lower()

    def test_validate_invalid_config(self, config_validator):
        """Test validation fails with invalid config"""
        config = {
            "server": "",
            "database": "",
            "auth_type": "Invalid"
        }

        result = config_validator.validate(config)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_returns_validation_result(self, config_validator):
        """Test validate returns ValidationResult instance"""
        config = {
            "server": "localhost",
            "database": "WMS_EP",
            "auth_type": constants.AUTH_TYPE_WINDOWS
        }

        result = config_validator.validate(config)

        assert isinstance(result, ValidationResult)


@pytest.mark.unit
@pytest.mark.validation
class TestValidateConfigFilePath:
    """Test config file path validation"""

    def test_validate_config_file_path_valid(self, config_validator):
        """Test validation passes with valid file path"""
        result = config_validator.validate_config_file_path("config/sql_config.json")

        assert result.is_valid is True

    def test_validate_config_file_path_empty(self, config_validator):
        """Test validation fails with empty path"""
        result = config_validator.validate_config_file_path("")

        assert result.is_valid is False

    def test_validate_config_file_path_none(self, config_validator):
        """Test validation fails with None"""
        result = config_validator.validate_config_file_path(None)

        assert result.is_valid is False
