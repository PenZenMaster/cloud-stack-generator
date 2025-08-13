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

__all__ = [
    "ErrorLogger",
    "get_error_logger", 
    "log_error_dialog",
    "log_validation_error",
    "log_file_operation_error"
]