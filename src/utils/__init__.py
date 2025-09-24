"""
Filename: __init__.py
Path: E:\\projects\\cloud-stack-generator\\src\\utils\\__init__.py
Description: Utility modules for SEO Authority Website Generator
Provides common utility functions including error logging

Version: 1.0.0
Date: 2025-08-13
Author: Cloud Stack Generator Team
"""

from .error_logger import (
    ErrorLogger,
    get_error_logger,
    log_error_dialog,
    log_validation_error,
    log_file_operation_error
)

from .enhanced_error_handler import (
    UniformErrorHandler,
    get_error_handler,
    handle_errors,
    safe_operation,
    log_import_error,
    log_file_operation_error as enhanced_log_file_operation_error,
    log_validation_error as enhanced_log_validation_error,
    log_ui_error
)

from .error_classification import (
    ErrorClassifier,
    IssueLevel,
    IssueCategory,
    IssueClassification,
    get_error_classifier,
    classify_and_handle_error
)

__all__ = [
    # Original error logger (for backward compatibility)
    "ErrorLogger",
    "get_error_logger",
    "log_error_dialog",
    "log_validation_error",
    "log_file_operation_error",

    # Enhanced uniform error handler
    "UniformErrorHandler",
    "get_error_handler",
    "handle_errors",
    "safe_operation",
    "log_import_error",
    "enhanced_log_file_operation_error",
    "enhanced_log_validation_error",
    "log_ui_error",

    # Error classification system
    "ErrorClassifier",
    "IssueLevel",
    "IssueCategory",
    "IssueClassification",
    "get_error_classifier",
    "classify_and_handle_error"
]