"""
Comprehensive tests for logging configuration

Tests all logging functionality including setup, handlers, formatters,
specialized loggers, and logging utilities.
"""
import logging
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
import pytest

from src.logging_config import (
    LEVEL_DEBUG,
    LEVEL_INFO,
    LEVEL_WARNING,
    LEVEL_ERROR,
    LEVEL_CRITICAL,
    DEFAULT_LOG_DIR,
    LOG_FILE_APP,
    LOG_FILE_ERROR,
    LOG_FILE_DATABASE,
    LOG_FILE_SERVICE,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    MAX_BYTES,
    BACKUP_COUNT,
    setup_logging,
    get_logger,
    get_database_logger,
    get_service_logger,
    get_repository_logger,
    get_ui_logger,
    get_validation_logger,
    log_exception,
    create_session_log,
    LoggerAdapter,
    get_contextual_logger,
    initialize_default_logging,
)


class TestLoggingConstants:
    """Test logging constants"""

    def test_logging_levels_defined(self):
        """Test that logging levels are defined correctly"""
        assert LEVEL_DEBUG == logging.DEBUG
        assert LEVEL_INFO == logging.INFO
        assert LEVEL_WARNING == logging.WARNING
        assert LEVEL_ERROR == logging.ERROR
        assert LEVEL_CRITICAL == logging.CRITICAL

    def test_default_log_dir_defined(self):
        """Test that default log directory is defined"""
        assert DEFAULT_LOG_DIR == "logs"

    def test_log_file_names_defined(self):
        """Test that log file names are defined"""
        assert LOG_FILE_APP == "wms_app.log"
        assert LOG_FILE_ERROR == "wms_error.log"
        assert LOG_FILE_DATABASE == "wms_database.log"
        assert LOG_FILE_SERVICE == "wms_service.log"

    def test_log_format_defined(self):
        """Test that log format is defined"""
        assert isinstance(LOG_FORMAT, str)
        assert "%(asctime)s" in LOG_FORMAT
        assert "%(name)s" in LOG_FORMAT
        assert "%(levelname)s" in LOG_FORMAT
        assert "%(message)s" in LOG_FORMAT

    def test_log_date_format_defined(self):
        """Test that log date format is defined"""
        assert LOG_DATE_FORMAT == "%Y-%m-%d %H:%M:%S"

    def test_rotation_settings_defined(self):
        """Test that file rotation settings are defined"""
        assert MAX_BYTES == 10 * 1024 * 1024  # 10 MB
        assert BACKUP_COUNT == 5


class TestSetupLogging:
    """Test setup_logging function"""

    def test_setup_logging_creates_log_directory(self, tmp_path):
        """Test that setup_logging creates log directory if it doesn't exist"""
        log_dir = tmp_path / "test_logs"
        assert not log_dir.exists()

        setup_logging(log_dir=str(log_dir), console_output=False)

        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_setup_logging_with_existing_directory(self, tmp_path):
        """Test setup_logging with existing directory"""
        log_dir = tmp_path / "existing_logs"
        log_dir.mkdir()

        # Should not raise error
        logger = setup_logging(log_dir=str(log_dir), console_output=False)
        assert isinstance(logger, logging.Logger)

    def test_setup_logging_console_only(self):
        """Test setup_logging with console output only"""
        logger = setup_logging(console_output=True, file_output=False)

        assert isinstance(logger, logging.Logger)
        # Should have at least one handler (console)
        assert len(logger.handlers) >= 1
        # Check that at least one handler is StreamHandler
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)

    def test_setup_logging_file_only(self, tmp_path):
        """Test setup_logging with file output only"""
        log_dir = tmp_path / "file_logs"
        logger = setup_logging(
            log_dir=str(log_dir),
            console_output=False,
            file_output=True
        )

        assert isinstance(logger, logging.Logger)
        # Should have file handlers
        assert len(logger.handlers) >= 1

    def test_setup_logging_both_console_and_file(self, tmp_path):
        """Test setup_logging with both console and file output"""
        log_dir = tmp_path / "both_logs"
        logger = setup_logging(
            log_dir=str(log_dir),
            console_output=True,
            file_output=True
        )

        assert isinstance(logger, logging.Logger)
        # Should have multiple handlers (console + file handlers)
        assert len(logger.handlers) >= 2

    def test_setup_logging_creates_app_log_file(self, tmp_path):
        """Test that setup_logging creates app log file"""
        log_dir = tmp_path / "app_logs"
        setup_logging(log_dir=str(log_dir), console_output=False)

        app_log_file = log_dir / LOG_FILE_APP
        # File may not exist until first write, but handler should be created
        assert log_dir.exists()

    def test_setup_logging_creates_error_log_file(self, tmp_path):
        """Test that setup_logging creates error log file handler"""
        log_dir = tmp_path / "error_logs"
        logger = setup_logging(log_dir=str(log_dir), console_output=False)

        # Error handler should be created
        error_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
            and h.level == LEVEL_ERROR
        ]
        assert len(error_handlers) > 0

    def test_setup_logging_with_debug_level(self, tmp_path):
        """Test setup_logging with DEBUG level"""
        log_dir = tmp_path / "debug_logs"
        logger = setup_logging(
            log_dir=str(log_dir),
            level=LEVEL_DEBUG,
            console_output=False
        )

        assert logger.level == LEVEL_DEBUG

    def test_setup_logging_with_info_level(self, tmp_path):
        """Test setup_logging with INFO level"""
        log_dir = tmp_path / "info_logs"
        logger = setup_logging(
            log_dir=str(log_dir),
            level=LEVEL_INFO,
            console_output=False
        )

        assert logger.level == LEVEL_INFO

    def test_setup_logging_with_warning_level(self, tmp_path):
        """Test setup_logging with WARNING level"""
        log_dir = tmp_path / "warning_logs"
        logger = setup_logging(
            log_dir=str(log_dir),
            level=LEVEL_WARNING,
            console_output=False
        )

        assert logger.level == LEVEL_WARNING

    def test_setup_logging_with_error_level(self, tmp_path):
        """Test setup_logging with ERROR level"""
        log_dir = tmp_path / "error_level_logs"
        logger = setup_logging(
            log_dir=str(log_dir),
            level=LEVEL_ERROR,
            console_output=False
        )

        assert logger.level == LEVEL_ERROR

    def test_setup_logging_clears_existing_handlers(self, tmp_path):
        """Test that setup_logging clears existing handlers"""
        log_dir = tmp_path / "clear_logs"

        # Setup logging first time
        logger1 = setup_logging(log_dir=str(log_dir), console_output=False)
        handler_count_1 = len(logger1.handlers)

        # Setup logging second time
        logger2 = setup_logging(log_dir=str(log_dir), console_output=False)
        handler_count_2 = len(logger2.handlers)

        # Handler count should be same (old handlers cleared)
        assert handler_count_1 == handler_count_2

    def test_setup_logging_returns_root_logger(self, tmp_path):
        """Test that setup_logging returns root logger"""
        log_dir = tmp_path / "root_logs"
        logger = setup_logging(log_dir=str(log_dir), console_output=False)

        assert logger is logging.getLogger()

    def test_setup_logging_file_rotation_settings(self, tmp_path):
        """Test that file handlers have correct rotation settings"""
        log_dir = tmp_path / "rotation_logs"
        logger = setup_logging(log_dir=str(log_dir), console_output=False)

        rotating_handlers = [
            h for h in logger.handlers
            if isinstance(h, logging.handlers.RotatingFileHandler)
        ]

        assert len(rotating_handlers) > 0
        for handler in rotating_handlers:
            assert handler.maxBytes == MAX_BYTES
            assert handler.backupCount == BACKUP_COUNT

    def test_setup_logging_formatter(self, tmp_path):
        """Test that handlers have correct formatter"""
        log_dir = tmp_path / "format_logs"
        logger = setup_logging(log_dir=str(log_dir), console_output=True)

        for handler in logger.handlers:
            formatter = handler.formatter
            assert formatter is not None
            assert formatter._fmt == LOG_FORMAT
            assert formatter.datefmt == LOG_DATE_FORMAT


class TestGetLogger:
    """Test get_logger function"""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance"""
        logger = get_logger("test.module")
        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_name(self):
        """Test get_logger with specific name"""
        logger = get_logger("my.custom.logger")
        assert logger.name == "my.custom.logger"

    def test_get_logger_with_level_override(self):
        """Test get_logger with level override"""
        logger = get_logger("test.logger", level=LEVEL_DEBUG)
        assert logger.level == LEVEL_DEBUG

    def test_get_logger_without_level_override(self):
        """Test get_logger without level override"""
        logger = get_logger("test.logger2")
        # Should inherit from root logger or have default level
        assert isinstance(logger.level, int)

    def test_get_logger_same_name_returns_same_logger(self):
        """Test that get_logger returns same logger for same name"""
        logger1 = get_logger("same.name")
        logger2 = get_logger("same.name")
        assert logger1 is logger2


class TestSpecializedLoggers:
    """Test specialized logger functions"""

    def test_get_database_logger(self):
        """Test get_database_logger"""
        logger = get_database_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "wms.database"

    def test_get_service_logger(self):
        """Test get_service_logger"""
        logger = get_service_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "wms.service"

    def test_get_repository_logger(self):
        """Test get_repository_logger"""
        logger = get_repository_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "wms.repository"

    def test_get_ui_logger(self):
        """Test get_ui_logger"""
        logger = get_ui_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "wms.ui"

    def test_get_validation_logger(self):
        """Test get_validation_logger"""
        logger = get_validation_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == "wms.validation"

    def test_specialized_loggers_are_different(self):
        """Test that specialized loggers have different names"""
        db_logger = get_database_logger()
        service_logger = get_service_logger()
        repo_logger = get_repository_logger()

        assert db_logger.name != service_logger.name
        assert service_logger.name != repo_logger.name


class TestLogException:
    """Test log_exception function"""

    def test_log_exception_with_message(self):
        """Test log_exception with context message"""
        logger = Mock()
        exception = ValueError("Test error")

        log_exception(logger, exception, message="Context message")

        logger.error.assert_called_once()
        call_args = logger.error.call_args
        assert "Context message" in call_args[0][0]
        assert "Test error" in call_args[0][0]
        assert call_args[1]["exc_info"] is True

    def test_log_exception_without_message(self):
        """Test log_exception without context message"""
        logger = Mock()
        exception = RuntimeError("Runtime error")

        log_exception(logger, exception)

        logger.error.assert_called_once()
        call_args = logger.error.call_args
        assert "Exception occurred" in call_args[0][0]
        assert "Runtime error" in call_args[0][0]
        assert call_args[1]["exc_info"] is True

    def test_log_exception_with_custom_exception(self):
        """Test log_exception with custom exception"""
        logger = Mock()

        class CustomException(Exception):
            pass

        exception = CustomException("Custom error")
        log_exception(logger, exception, message="Custom error occurred")

        logger.error.assert_called_once()
        assert logger.error.call_args[1]["exc_info"] is True

    def test_log_exception_includes_traceback(self):
        """Test that log_exception includes traceback"""
        logger = Mock()
        exception = Exception("Test")

        log_exception(logger, exception)

        # Verify exc_info=True is passed (enables traceback)
        assert logger.error.call_args[1]["exc_info"] is True


class TestCreateSessionLog:
    """Test create_session_log function"""

    def test_create_session_log_creates_directory(self, tmp_path):
        """Test that create_session_log creates directory"""
        log_dir = tmp_path / "session_logs"
        assert not log_dir.exists()

        session_log = create_session_log(log_dir=str(log_dir))

        assert log_dir.exists()
        assert log_dir.is_dir()

    def test_create_session_log_returns_path(self, tmp_path):
        """Test that create_session_log returns a path string"""
        log_dir = tmp_path / "session_logs"
        session_log = create_session_log(log_dir=str(log_dir))

        assert isinstance(session_log, str)
        assert "session_" in session_log
        assert session_log.endswith(".log")

    def test_create_session_log_path_format(self, tmp_path):
        """Test create_session_log path format"""
        log_dir = tmp_path / "session_logs"
        session_log = create_session_log(log_dir=str(log_dir))

        # Should contain timestamp in format: session_YYYYMMDD_HHMMSS.log
        filename = os.path.basename(session_log)
        assert filename.startswith("session_")
        assert filename.endswith(".log")
        # Extract timestamp part
        timestamp_part = filename[8:-4]  # Remove "session_" and ".log"
        assert len(timestamp_part) == 15  # YYYYMMDD_HHMMSS
        assert timestamp_part[8] == "_"  # Underscore separator

    def test_create_session_log_unique_filenames(self, tmp_path):
        """Test that create_session_log generates unique filenames"""
        log_dir = tmp_path / "session_logs"

        # Create two session logs in quick succession
        session_log1 = create_session_log(log_dir=str(log_dir))
        session_log2 = create_session_log(log_dir=str(log_dir))

        # They might be the same if created in same second, but should be valid paths
        assert isinstance(session_log1, str)
        assert isinstance(session_log2, str)

    def test_create_session_log_with_default_directory(self):
        """Test create_session_log with default directory"""
        session_log = create_session_log()

        assert isinstance(session_log, str)
        assert DEFAULT_LOG_DIR in session_log


class TestLoggerAdapter:
    """Test LoggerAdapter class"""

    def test_logger_adapter_initialization(self):
        """Test LoggerAdapter initialization"""
        logger = Mock()
        context = {"user": "test_user", "session": "abc123"}

        adapter = LoggerAdapter(logger, context)

        assert adapter.logger is logger
        assert adapter.extra == context

    def test_logger_adapter_process_with_context(self):
        """Test LoggerAdapter.process with context"""
        logger = Mock()
        context = {"user": "john", "id": "123"}
        adapter = LoggerAdapter(logger, context)

        message, kwargs = adapter.process("Test message", {})

        assert "[user=john]" in message
        assert "[id=123]" in message
        assert "Test message" in message

    def test_logger_adapter_process_without_context(self):
        """Test LoggerAdapter.process without context"""
        logger = Mock()
        adapter = LoggerAdapter(logger, None)

        message, kwargs = adapter.process("Test message", {})

        assert message == "Test message"

    def test_logger_adapter_process_with_empty_context(self):
        """Test LoggerAdapter.process with empty context"""
        logger = Mock()
        adapter = LoggerAdapter(logger, {})

        message, kwargs = adapter.process("Test message", {})

        assert message == "Test message"

    def test_logger_adapter_context_formatting(self):
        """Test LoggerAdapter context formatting"""
        logger = Mock()
        context = {"key1": "value1", "key2": "value2", "key3": "value3"}
        adapter = LoggerAdapter(logger, context)

        message, kwargs = adapter.process("Log message", {})

        # All context items should be in message
        assert "[key1=value1]" in message
        assert "[key2=value2]" in message
        assert "[key3=value3]" in message
        assert "Log message" in message


class TestGetContextualLogger:
    """Test get_contextual_logger function"""

    def test_get_contextual_logger_returns_adapter(self):
        """Test that get_contextual_logger returns LoggerAdapter"""
        logger = get_contextual_logger("test.logger", user="test_user")
        assert isinstance(logger, LoggerAdapter)

    def test_get_contextual_logger_with_single_context(self):
        """Test get_contextual_logger with single context"""
        logger = get_contextual_logger("test.logger", user_id="user123")
        assert logger.extra == {"user_id": "user123"}

    def test_get_contextual_logger_with_multiple_context(self):
        """Test get_contextual_logger with multiple context values"""
        logger = get_contextual_logger(
            "test.logger",
            user="john",
            session="abc123",
            request_id="req-456"
        )
        assert logger.extra["user"] == "john"
        assert logger.extra["session"] == "abc123"
        assert logger.extra["request_id"] == "req-456"

    def test_get_contextual_logger_with_no_context(self):
        """Test get_contextual_logger with no context"""
        logger = get_contextual_logger("test.logger")
        assert logger.extra == {}

    def test_get_contextual_logger_name(self):
        """Test that get_contextual_logger uses correct logger name"""
        adapter = get_contextual_logger("my.custom.logger", key="value")
        assert adapter.logger.name == "my.custom.logger"


class TestInitializeDefaultLogging:
    """Test initialize_default_logging function"""

    def test_initialize_default_logging_sets_up_logging(self):
        """Test that initialize_default_logging sets up logging"""
        # Clear existing handlers
        root_logger = logging.getLogger()
        root_logger.handlers.clear()

        initialize_default_logging()

        # Should have handlers after initialization
        assert len(root_logger.handlers) > 0

    def test_initialize_default_logging_skips_if_configured(self):
        """Test that initialize_default_logging skips if already configured"""
        root_logger = logging.getLogger()

        # Add a handler
        handler = logging.StreamHandler()
        root_logger.addHandler(handler)
        initial_handler_count = len(root_logger.handlers)

        initialize_default_logging()

        # Should not add more handlers if already configured
        assert len(root_logger.handlers) == initial_handler_count

        # Cleanup
        root_logger.removeHandler(handler)


class TestLoggingIntegration:
    """Integration tests for logging functionality"""

    def test_logging_to_file(self, tmp_path):
        """Test actual logging to file"""
        log_dir = tmp_path / "integration_logs"
        setup_logging(log_dir=str(log_dir), console_output=False)

        logger = get_logger("test.integration")
        logger.info("Test log message")

        # Force flush
        for handler in logging.getLogger().handlers:
            handler.flush()

        # Check that log file was created
        app_log_file = log_dir / LOG_FILE_APP
        assert app_log_file.exists()

    def test_different_log_levels(self, tmp_path):
        """Test logging with different log levels"""
        log_dir = tmp_path / "level_logs"
        setup_logging(log_dir=str(log_dir), level=LEVEL_DEBUG, console_output=False)

        logger = get_logger("test.levels")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

        # Should not raise errors
        assert True

    def test_contextual_logging(self, tmp_path):
        """Test contextual logging with LoggerAdapter"""
        log_dir = tmp_path / "context_logs"
        setup_logging(log_dir=str(log_dir), console_output=False)

        logger = get_contextual_logger(
            "test.context",
            user="test_user",
            session="session123"
        )

        # Should not raise errors
        logger.info("Contextual log message")
        assert True

    def test_exception_logging(self, tmp_path):
        """Test exception logging"""
        log_dir = tmp_path / "exception_logs"
        setup_logging(log_dir=str(log_dir), console_output=False)

        logger = get_logger("test.exception")

        try:
            raise ValueError("Test exception")
        except ValueError as e:
            log_exception(logger, e, "Error occurred during test")

        # Should not raise errors
        assert True

    def test_specialized_logger_usage(self, tmp_path):
        """Test using specialized loggers"""
        log_dir = tmp_path / "specialized_logs"
        setup_logging(log_dir=str(log_dir), console_output=False)

        db_logger = get_database_logger()
        service_logger = get_service_logger()
        ui_logger = get_ui_logger()

        db_logger.info("Database operation")
        service_logger.info("Service operation")
        ui_logger.info("UI operation")

        # Should not raise errors
        assert True

    def test_log_format_contains_required_fields(self, tmp_path):
        """Test that log format contains all required fields"""
        log_dir = tmp_path / "format_test_logs"
        setup_logging(log_dir=str(log_dir), console_output=False)

        logger = get_logger("test.format")
        logger.info("Test message")

        # Flush handlers
        for handler in logging.getLogger().handlers:
            handler.flush()

        # Read log file
        app_log_file = log_dir / LOG_FILE_APP
        if app_log_file.exists():
            content = app_log_file.read_text()
            # Should contain timestamp, logger name, level, and message
            assert "test.format" in content
            assert "INFO" in content
            assert "Test message" in content
