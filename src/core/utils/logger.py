"""
Centralized Logging System for Cloud Stack Generator
Path: E:\\projects\\cloud-stack-generator\\src\\core\\utils\\logger.py

Description:
Provides structured logging with console and file output, rotating file handlers,
and context-aware logging for debugging and production monitoring.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-18

Last Modified Date:
2025-11-18

Comments:
* v1.00 - Initial logging system implementation
* Replaces print statements with proper logging
* Supports DEBUG, INFO, WARNING, ERROR, CRITICAL levels
* Rotating file handlers (10MB, 5 backups)
* JSON-structured logs for parsing
* Performance timing utilities
"""

import logging
import logging.handlers
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from functools import wraps
import time


# Default log directory
DEFAULT_LOG_DIR = Path.home() / ".cloud-stack-generator" / "logs"


class JsonFormatter(logging.Formatter):
    """
    JSON formatter for structured logging.

    Outputs log records as JSON objects for easy parsing and analysis.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message": record.getMessage(),
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for readable development logs.

    Uses ANSI color codes for different log levels (Windows 10+ compatible).
    """

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors"""
        # Get color for log level
        color = self.COLORS.get(record.levelname, self.COLORS['RESET'])
        reset = self.COLORS['RESET']

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')

        # Build colored message
        formatted = (
            f"{color}[{timestamp}] {record.levelname:8s}{reset} "
            f"{record.name:20s} - {record.getMessage()}"
        )

        # Add exception if present
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


def setup_logger(
    name: str = "cloud_stack_generator",
    level: str = "INFO",
    log_dir: Optional[Path] = None,
    console: bool = True,
    file_logging: bool = True
) -> logging.Logger:
    """
    Set up a logger with console and file handlers.

    Args:
        name: Logger name (typically module name)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (default: ~/.cloud-stack-generator/logs)
        console: Enable console output (default: True)
        file_logging: Enable file logging (default: True)

    Returns:
        Configured logger instance

    Example:
        logger = setup_logger(__name__)
        logger.info("Application started")
        logger.error("An error occurred", extra={"client": "test-client"})
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Console handler (colored, human-readable)
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, level.upper()))
        console_handler.setFormatter(ColoredConsoleFormatter())
        logger.addHandler(console_handler)

    # File handlers (JSON, rotating)
    if file_logging:
        log_dir = log_dir or DEFAULT_LOG_DIR
        log_dir.mkdir(parents=True, exist_ok=True)

        # Main log file (all levels, JSON format)
        main_log = log_dir / "cloud_stack_generator.log"
        main_handler = logging.handlers.RotatingFileHandler(
            main_log,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(JsonFormatter())
        logger.addHandler(main_handler)

        # Error log file (ERROR and above, detailed)
        error_log = log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JsonFormatter())
        logger.addHandler(error_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Get or create a logger instance.

    Args:
        name: Logger name (typically __name__ from calling module)

    Returns:
        Logger instance

    Example:
        from src.core.utils.logger import get_logger
        logger = get_logger(__name__)
        logger.info("Processing started")
    """
    if name is None:
        name = "cloud_stack_generator"

    # Check if logger already exists
    logger = logging.getLogger(name)

    # If no handlers, set it up
    if not logger.handlers:
        logger = setup_logger(name)

    return logger


def log_execution_time(func):
    """
    Decorator to log function execution time.

    Usage:
        @log_execution_time
        def my_function():
            # ... function code ...

    Logs function name and execution time at INFO level.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__)
        start_time = time.time()

        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(
                f"{func.__name__} completed in {elapsed:.2f}s",
                extra={"extra_fields": {
                    "function": func.__name__,
                    "execution_time_seconds": elapsed,
                    "status": "success"
                }}
            )
            return result

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"{func.__name__} failed after {elapsed:.2f}s: {str(e)}",
                exc_info=True,
                extra={"extra_fields": {
                    "function": func.__name__,
                    "execution_time_seconds": elapsed,
                    "status": "failed",
                    "error": str(e)
                }}
            )
            raise

    return wrapper


def log_exception(logger: logging.Logger, context: str = ""):
    """
    Decorator to log exceptions with context.

    Args:
        logger: Logger instance to use
        context: Contextual description of what was being attempted

    Usage:
        logger = get_logger(__name__)

        @log_exception(logger, "uploading file to S3")
        def upload_file(file_path):
            # ... upload logic ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_context = context or f"executing {func.__name__}"
                logger.error(
                    f"Error {error_context}: {str(e)}",
                    exc_info=True,
                    extra={"extra_fields": {
                        "function": func.__name__,
                        "context": error_context,
                        "error_type": type(e).__name__
                    }}
                )
                raise

        return wrapper

    return decorator


class LogContext:
    """
    Context manager for adding context to log messages.

    Usage:
        logger = get_logger(__name__)

        with LogContext(logger, "deploying to S3", client="test-client"):
            # ... deployment code ...
            logger.info("Upload started")  # Will include context fields
    """

    def __init__(self, logger: logging.Logger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.logger.info(
            f"Starting: {self.operation}",
            extra={"extra_fields": {
                "operation": self.operation,
                "phase": "start",
                **self.context
            }}
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time

        if exc_type is None:
            self.logger.info(
                f"Completed: {self.operation} ({elapsed:.2f}s)",
                extra={"extra_fields": {
                    "operation": self.operation,
                    "phase": "complete",
                    "duration_seconds": elapsed,
                    "status": "success",
                    **self.context
                }}
            )
        else:
            self.logger.error(
                f"Failed: {self.operation} ({elapsed:.2f}s) - {exc_val}",
                exc_info=(exc_type, exc_val, exc_tb),
                extra={"extra_fields": {
                    "operation": self.operation,
                    "phase": "failed",
                    "duration_seconds": elapsed,
                    "status": "failed",
                    "error_type": exc_type.__name__ if exc_type else None,
                    **self.context
                }}
            )

        return False  # Don't suppress exceptions


# Initialize default logger
_default_logger = setup_logger()


def info(message: str, **kwargs):
    """Log info message using default logger"""
    _default_logger.info(message, extra={"extra_fields": kwargs} if kwargs else None)


def warning(message: str, **kwargs):
    """Log warning message using default logger"""
    _default_logger.warning(message, extra={"extra_fields": kwargs} if kwargs else None)


def error(message: str, **kwargs):
    """Log error message using default logger"""
    _default_logger.error(message, extra={"extra_fields": kwargs} if kwargs else None)


def debug(message: str, **kwargs):
    """Log debug message using default logger"""
    _default_logger.debug(message, extra={"extra_fields": kwargs} if kwargs else None)


def critical(message: str, **kwargs):
    """Log critical message using default logger"""
    _default_logger.critical(message, extra={"extra_fields": kwargs} if kwargs else None)
