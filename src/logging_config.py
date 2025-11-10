"""
Logging Configuration for WMS Barcode Scanner
Provides centralized logging setup with file rotation and formatted output
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime


# Logging levels
LEVEL_DEBUG = logging.DEBUG
LEVEL_INFO = logging.INFO
LEVEL_WARNING = logging.WARNING
LEVEL_ERROR = logging.ERROR
LEVEL_CRITICAL = logging.CRITICAL

# Default log directory
DEFAULT_LOG_DIR = "logs"

# Default log file names
LOG_FILE_APP = "wms_app.log"
LOG_FILE_ERROR = "wms_error.log"
LOG_FILE_DATABASE = "wms_database.log"
LOG_FILE_SERVICE = "wms_service.log"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# File rotation settings
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Keep 5 backup files


def setup_logging(
    log_dir: str = DEFAULT_LOG_DIR,
    level: int = LEVEL_INFO,
    console_output: bool = True,
    file_output: bool = True,
) -> logging.Logger:
    """
    Setup centralized logging configuration

    Args:
        log_dir: Directory to store log files
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        console_output: Whether to output logs to console
        file_output: Whether to output logs to files

    Returns:
        logging.Logger: Configured root logger
    """
    # Create log directory if it doesn't exist
    if file_output:
        Path(log_dir).mkdir(parents=True, exist_ok=True)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # File handlers with rotation
    if file_output:
        # Main application log
        app_log_path = os.path.join(log_dir, LOG_FILE_APP)
        app_handler = logging.handlers.RotatingFileHandler(
            app_log_path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
        )
        app_handler.setLevel(level)
        app_handler.setFormatter(formatter)
        root_logger.addHandler(app_handler)

        # Error log (only errors and critical)
        error_log_path = os.path.join(log_dir, LOG_FILE_ERROR)
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_path, maxBytes=MAX_BYTES, backupCount=BACKUP_COUNT, encoding="utf-8"
        )
        error_handler.setLevel(LEVEL_ERROR)
        error_handler.setFormatter(formatter)
        root_logger.addHandler(error_handler)

    return root_logger


def get_logger(name: str, level: int = None) -> logging.Logger:
    """
    Get a logger with the specified name

    Args:
        name: Logger name (usually __name__)
        level: Optional logging level override

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger


def get_database_logger() -> logging.Logger:
    """Get logger for database operations"""
    return get_logger("wms.database")


def get_service_logger() -> logging.Logger:
    """Get logger for service layer"""
    return get_logger("wms.service")


def get_repository_logger() -> logging.Logger:
    """Get logger for repository layer"""
    return get_logger("wms.repository")


def get_ui_logger() -> logging.Logger:
    """Get logger for UI layer"""
    return get_logger("wms.ui")


def get_validation_logger() -> logging.Logger:
    """Get logger for validation"""
    return get_logger("wms.validation")


def log_exception(logger: logging.Logger, exception: Exception, message: str = None):
    """
    Log an exception with full traceback

    Args:
        logger: Logger instance
        exception: Exception to log
        message: Optional context message
    """
    if message:
        logger.error(f"{message}: {str(exception)}", exc_info=True)
    else:
        logger.error(f"Exception occurred: {str(exception)}", exc_info=True)


def create_session_log(log_dir: str = DEFAULT_LOG_DIR) -> str:
    """
    Create a session-specific log file

    Args:
        log_dir: Directory to store log files

    Returns:
        str: Path to session log file
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_log = os.path.join(log_dir, f"session_{timestamp}.log")
    return session_log


class LoggerAdapter(logging.LoggerAdapter):
    """
    Custom logger adapter that adds context information to all log messages
    """

    def process(self, msg, kwargs):
        """Add context information to log message"""
        if self.extra:
            context = " ".join([f"[{k}={v}]" for k, v in self.extra.items()])
            return f"{context} {msg}", kwargs
        return msg, kwargs


def get_contextual_logger(name: str, **context) -> LoggerAdapter:
    """
    Get a logger with context information

    Args:
        name: Logger name
        **context: Context key-value pairs to include in all log messages

    Returns:
        LoggerAdapter: Logger with context

    Example:
        logger = get_contextual_logger('wms.scan', user_id='user123', session='abc')
        logger.info('Scan completed')  # Output: [user_id=user123] [session=abc] Scan completed
    """
    logger = get_logger(name)
    return LoggerAdapter(logger, context)


# Initialize default logging on module import
def initialize_default_logging():
    """Initialize default logging configuration"""
    # Only setup if not already configured
    if not logging.getLogger().handlers:
        setup_logging(level=LEVEL_INFO, console_output=True, file_output=True)


# Auto-initialize when module is imported (can be disabled if needed)
# initialize_default_logging()
