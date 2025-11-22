"""
Enhanced Error Handler - Uniform Error Logging and Management System
Path: E:/projects/cloud-stack-generator/src/utils/enhanced_error_handler.py

Description:
Provides a comprehensive, uniform error handling and logging system for the entire application.
Ensures all errors are properly logged, tracked, and handled consistently across all components.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-23

Last Modified Date:
2025-09-23

Comments:
* v1.00 - Comprehensive uniform error handling system
"""

import functools
import inspect
import logging
import traceback
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Callable
from contextlib import contextmanager
from .error_logger import ErrorLogger


class ErrorHandlerConfig:
    """Configuration for error handling behavior"""

    def __init__(self):
        self.log_to_file = True
        self.log_to_console = False
        self.raise_in_debug = False
        self.show_user_dialogs = True
        self.capture_stack_trace = True
        self.log_directory = Path.cwd() / "logs"


class UniformErrorHandler:
    """
    Uniform error handler that provides consistent error logging and management
    across the entire application.
    """

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.config = ErrorHandlerConfig()
            self.error_logger = ErrorLogger(str(self.config.log_directory))
            self.error_counts = {"errors": 0, "warnings": 0, "criticals": 0}
            self._setup_logging()
            UniformErrorHandler._initialized = True

    def _setup_logging(self):
        """Setup enhanced logging configuration"""
        # Create a logger for this handler
        self.logger = logging.getLogger('UniformErrorHandler')
        self.logger.setLevel(logging.DEBUG)

        # Prevent duplicate logs
        self.logger.propagate = False

        if not self.logger.handlers:
            # File handler
            if self.config.log_to_file:
                file_handler = logging.FileHandler(
                    self.config.log_directory / "system_errors.log",
                    encoding='utf-8'
                )
                file_formatter = logging.Formatter(
                    '%(asctime)s | %(name)s | %(levelname)s | %(funcName)s:%(lineno)d | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(file_formatter)
                self.logger.addHandler(file_handler)

            # Console handler
            if self.config.log_to_console:
                console_handler = logging.StreamHandler(sys.stdout)
                console_formatter = logging.Formatter(
                    '%(levelname)s | %(name)s | %(message)s'
                )
                console_handler.setFormatter(console_formatter)
                self.logger.addHandler(console_handler)

    def log_error(self,
                  error: Exception,
                  context: str = None,
                  component: str = None,
                  user_action: str = None,
                  severity: str = "error",
                  show_dialog: bool = None) -> None:
        """
        Log an error with comprehensive context information

        Args:
            error: The exception that occurred
            context: Additional context about when/where error occurred
            component: Component/module where error occurred
            user_action: What the user was trying to do
            severity: error, warning, or critical
            show_dialog: Whether to show user dialog (None = use config)
        """

        # Get caller information
        frame = inspect.currentframe()
        try:
            caller_frame = frame.f_back
            caller_info = inspect.getframeinfo(caller_frame)
            if not component:
                component = f"{Path(caller_info.filename).name}:{caller_info.function}"
        except Exception:
            component = component or "Unknown"
        finally:
            del frame

        # Generate error details
        error_type = type(error).__name__
        error_message = str(error)
        timestamp = datetime.now().isoformat()

        # Create comprehensive error context
        error_context = {
            "timestamp": timestamp,
            "error_type": error_type,
            "error_message": error_message,
            "component": component,
            "context": context,
            "user_action": user_action,
            "severity": severity.upper()
        }

        # Add stack trace if enabled
        if self.config.capture_stack_trace:
            error_context["stack_trace"] = traceback.format_exc()

        # Log to system logger
        log_message = f"[{severity.upper()}] {component}: {error_message}"
        if context:
            log_message += f" | Context: {context}"

        if severity.lower() == "critical":
            self.logger.critical(log_message, exc_info=error)
            self.error_counts["criticals"] += 1
        elif severity.lower() == "warning":
            self.logger.warning(log_message, exc_info=error)
            self.error_counts["warnings"] += 1
        else:
            self.logger.error(log_message, exc_info=error)
            self.error_counts["errors"] += 1

        # Log to human-readable error log
        self.error_logger.log_error_dialog(
            title=f"{severity.title()}: {error_type}",
            message=error_message,
            context=context,
            component=component,
            exception=error,
            user_action=user_action
        )

        # Show user dialog if configured
        show_dialog = show_dialog if show_dialog is not None else self.config.show_user_dialogs
        if show_dialog and severity.lower() in ["error", "critical"]:
            self._show_user_error_dialog(error_context)

    def _show_user_error_dialog(self, error_context: Dict[str, Any]):
        """Show user-friendly error dialog"""
        try:
            from PyQt6.QtWidgets import QMessageBox, QApplication

            # Only show if we have an active QApplication
            if QApplication.instance() is not None:
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Icon.Critical)
                msg_box.setWindowTitle(f"Application Error - {error_context['component']}")

                # Create user-friendly message
                user_message = f"An error occurred: {error_context['error_message']}"
                if error_context.get('user_action'):
                    user_message += f"\n\nWhile: {error_context['user_action']}"

                user_message += "\n\nThis error has been logged for debugging. Please contact support if the problem persists."

                msg_box.setText(user_message)
                msg_box.setDetailedText(error_context.get('stack_trace', ''))
                msg_box.exec()
        except Exception as dialog_error:
            # If we can't show dialog, just log it
            self.logger.error(f"Failed to show error dialog: {dialog_error}")

    def log_warning(self, message: str, context: str = None, component: str = None):
        """Log a warning message"""
        self.logger.warning(f"{component or 'Unknown'}: {message}")
        if context:
            self.logger.warning(f"Context: {context}")
        self.error_counts["warnings"] += 1

    def log_info(self, message: str, component: str = None):
        """Log an info message"""
        self.logger.info(f"{component or 'Unknown'}: {message}")

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics"""
        return {
            "session_errors": self.error_counts["errors"],
            "session_warnings": self.error_counts["warnings"],
            "session_criticals": self.error_counts["criticals"],
            "total_issues": sum(self.error_counts.values()),
            "log_directory": str(self.config.log_directory)
        }

    @contextmanager
    def error_context(self, context: str, component: str = None, user_action: str = None):
        """
        Context manager for automatic error handling

        Usage:
            with error_handler.error_context("Loading template", "TemplateManager", "Opening template"):
                # risky operation
                pass
        """
        try:
            yield
        except Exception as e:
            self.log_error(
                error=e,
                context=context,
                component=component,
                user_action=user_action
            )
            raise


# Global error handler instance
_global_error_handler = None


def get_error_handler() -> UniformErrorHandler:
    """Get the global error handler instance"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = UniformErrorHandler()
    return _global_error_handler


def handle_errors(component: str = None,
                 user_action: str = None,
                 severity: str = "error",
                 reraise: bool = True,
                 return_on_error: Any = None):
    """
    Decorator for automatic error handling

    Args:
        component: Component name (auto-detected if None)
        user_action: Description of user action
        severity: error, warning, or critical
        reraise: Whether to re-raise the exception
        return_on_error: Value to return if error occurs and reraise=False
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            error_handler = get_error_handler()

            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Auto-detect component if not provided
                func_component = component or f"{func.__module__}.{func.__name__}"

                error_handler.log_error(
                    error=e,
                    context=f"Function: {func.__name__}",
                    component=func_component,
                    user_action=user_action,
                    severity=severity
                )

                if reraise:
                    raise
                else:
                    return return_on_error

        return wrapper
    return decorator


def safe_operation(operation_name: str,
                  component: str = None,
                  user_action: str = None,
                  default_return: Any = None):
    """
    Context manager for safe operations that don't crash the application

    Usage:
        with safe_operation("Save template", "TemplateEditor", "Saving template") as safe:
            if safe:
                # risky operation
                template.save()
    """
    return SafeOperationContext(operation_name, component, user_action, default_return)


class SafeOperationContext:
    """Context manager for safe operations"""

    def __init__(self, operation_name: str, component: str = None,
                 user_action: str = None, default_return: Any = None):
        self.operation_name = operation_name
        self.component = component
        self.user_action = user_action
        self.default_return = default_return
        self.error_handler = get_error_handler()
        self.success = True
        self.error = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.success = False
            self.error = exc_val

            self.error_handler.log_error(
                error=exc_val,
                context=self.operation_name,
                component=self.component,
                user_action=self.user_action
            )

            # Suppress the exception
            return True
        return False

    def __bool__(self):
        """Allow using 'if safe:' syntax"""
        return self.success


# Convenience functions for common error types
def log_import_error(module_name: str, component: str = None, fallback_action: str = None):
    """Log import errors consistently"""
    error_handler = get_error_handler()
    error_handler.log_warning(
        message=f"Failed to import {module_name}. {fallback_action or 'Functionality may be limited.'}",
        component=component or "Import Handler"
    )


def log_file_operation_error(operation: str, file_path: str, error: Exception, component: str = None):
    """Log file operation errors consistently"""
    error_handler = get_error_handler()
    error_handler.log_error(
        error=error,
        context=f"File operation: {operation} on {file_path}",
        component=component or "File Handler",
        user_action=f"Attempting to {operation} file"
    )


def log_validation_error(field_name: str, value: Any, error: Exception, component: str = None):
    """Log validation errors consistently"""
    error_handler = get_error_handler()
    error_handler.log_error(
        error=error,
        context=f"Validation failed for field '{field_name}' with value: {value}",
        component=component or "Validator",
        user_action="Validating user input"
    )


def log_ui_error(widget_name: str, action: str, error: Exception, user_action: str = None):
    """Log UI errors consistently"""
    error_handler = get_error_handler()
    error_handler.log_error(
        error=error,
        context=f"UI Error in {widget_name} during {action}",
        component="UI System",
        user_action=user_action or f"Interacting with {widget_name}"
    )