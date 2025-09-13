"""
Filename: error_logger.py
Path: E:\\projects\\cloud-stack-generator\\src\\utils\\error_logger.py
Description: Human-readable error logging utility for tracking error dialogs and debugging
Provides comprehensive error logging with timestamps, context, and stack traces

Version: 1.0.0
Date: 2025-08-13
Author: Cloud Stack Generator Team
"""

import logging
import traceback
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json


class ErrorLogger:
    """
    Enhanced error logging utility for tracking error dialogs and application issues.
    Provides human-readable error logs with context and debugging information.
    """

    def __init__(self, log_directory: Optional[str] = None):
        """Initialize the error logger with configurable log directory"""
        self.log_directory = Path(log_directory) if log_directory else Path.cwd() / "logs"
        self.log_directory.mkdir(exist_ok=True)
        
        # Create log files
        self.error_log_path = self.log_directory / "error_log.txt"
        self.debug_log_path = self.log_directory / "debug_log.json"
        
        # Setup logging configuration
        self._setup_logging()
        
        # Initialize session
        self._log_session_start()

    def _setup_logging(self):
        """Setup Python logging configuration"""
        # Create formatter for human-readable logs
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Setup file handler for error log
        self.file_handler = logging.FileHandler(self.error_log_path, encoding='utf-8')
        self.file_handler.setFormatter(formatter)
        self.file_handler.setLevel(logging.ERROR)
        
        # Setup logger
        self.logger = logging.getLogger('SEOGenerator_ErrorLogger')
        self.logger.setLevel(logging.DEBUG)
        self.logger.addHandler(self.file_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False

    def _log_session_start(self):
        """Log session start information"""
        session_info = f"""
{'='*80}
NEW SESSION STARTED
{'='*80}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Application: SEO Authority Website Generator
Platform: {sys.platform}
Python Version: {sys.version}
Working Directory: {Path.cwd()}
{'='*80}
"""
        
        with open(self.error_log_path, 'a', encoding='utf-8') as f:
            f.write(session_info + '\n')

    def log_error_dialog(self, 
                        title: str, 
                        message: str, 
                        context: Optional[str] = None,
                        component: Optional[str] = None,
                        exception: Optional[Exception] = None,
                        user_action: Optional[str] = None) -> None:
        """
        Log an error dialog with comprehensive context information
        
        Args:
            title: Dialog title/header
            message: Error message displayed to user
            context: Additional context about when error occurred
            component: Component/module where error occurred
            exception: Original exception if available
            user_action: What the user was trying to do when error occurred
        """
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Create human-readable log entry
        log_entry = f"""
{'-'*60}
ERROR DIALOG DISPLAYED
{'-'*60}
Timestamp: {timestamp}
Dialog Title: {title}
Error Message: {message}
"""
        
        if context:
            log_entry += f"Context: {context}\n"
        
        if component:
            log_entry += f"Component: {component}\n"
        
        if user_action:
            log_entry += f"User Action: {user_action}\n"
        
        if exception:
            log_entry += f"Exception Type: {type(exception).__name__}\n"
            log_entry += f"Exception Details: {str(exception)}\n"
            
            # Add stack trace if available
            if hasattr(exception, '__traceback__') and exception.__traceback__:
                log_entry += f"Stack Trace:\n{''.join(traceback.format_tb(exception.__traceback__))}\n"
        
        # Add current stack trace for debugging
        log_entry += f"Call Stack:\n{''.join(traceback.format_stack()[:-1])}\n"
        log_entry += f"{'-'*60}\n"
        
        # Write to human-readable log
        with open(self.error_log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Also log through Python logger
        self.logger.error(f"Dialog: {title} | Message: {message}")
        
        # Write structured data for debugging
        self._write_debug_log({
            'timestamp': timestamp,
            'type': 'error_dialog',
            'title': title,
            'message': message,
            'context': context,
            'component': component,
            'exception': str(exception) if exception else None,
            'exception_type': type(exception).__name__ if exception else None,
            'user_action': user_action,
            'stack_trace': traceback.format_stack() if exception else None
        })

    def log_validation_error(self, 
                            field: str, 
                            error_message: str, 
                            value: Any = None,
                            component: Optional[str] = None) -> None:
        """
        Log validation errors with field and value context
        
        Args:
            field: Field name that failed validation
            error_message: Validation error message
            value: Value that failed validation
            component: Component where validation occurred
        """
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"""
{'-'*60}
VALIDATION ERROR
{'-'*60}
Timestamp: {timestamp}
Field: {field}
Error: {error_message}
Value: {repr(value)}
"""
        
        if component:
            log_entry += f"Component: {component}\n"
        
        log_entry += f"{'-'*60}\n"
        
        # Write to human-readable log
        with open(self.error_log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Write structured data
        self._write_debug_log({
            'timestamp': timestamp,
            'type': 'validation_error',
            'field': field,
            'message': error_message,
            'value': repr(value),
            'component': component
        })

    def log_file_operation_error(self, 
                                operation: str, 
                                file_path: str, 
                                error_message: str,
                                exception: Optional[Exception] = None) -> None:
        """
        Log file operation errors (read, write, import, export)
        
        Args:
            operation: Type of file operation (read, write, import, export)
            file_path: Path to file that caused error
            error_message: Error message
            exception: Original exception if available
        """
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"""
{'-'*60}
FILE OPERATION ERROR
{'-'*60}
Timestamp: {timestamp}
Operation: {operation}
File Path: {file_path}
Error: {error_message}
"""
        
        if exception:
            log_entry += f"Exception: {type(exception).__name__}: {str(exception)}\n"
        
        # Add file information if possible
        try:
            file_path_obj = Path(file_path)
            if file_path_obj.exists():
                stat = file_path_obj.stat()
                log_entry += f"File Size: {stat.st_size} bytes\n"
                log_entry += f"File Modified: {datetime.fromtimestamp(stat.st_mtime)}\n"
            else:
                log_entry += "File Status: Does not exist\n"
        except:
            log_entry += "File Status: Unable to determine\n"
        
        log_entry += f"{'-'*60}\n"
        
        # Write to human-readable log
        with open(self.error_log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def log_application_crash(self, 
                            crash_message: str, 
                            exception: Exception,
                            context: Optional[str] = None) -> None:
        """
        Log critical application crashes
        
        Args:
            crash_message: Description of crash
            exception: Exception that caused crash
            context: Additional context about application state
        """
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        log_entry = f"""
{'#'*80}
CRITICAL APPLICATION CRASH
{'#'*80}
Timestamp: {timestamp}
Crash Message: {crash_message}
Exception: {type(exception).__name__}: {str(exception)}
"""
        
        if context:
            log_entry += f"Context: {context}\n"
        
        # Full stack trace for crashes
        log_entry += f"Full Stack Trace:\n{traceback.format_exc()}\n"
        
        # System information
        log_entry += f"Python Version: {sys.version}\n"
        log_entry += f"Platform: {sys.platform}\n"
        log_entry += f"Working Directory: {Path.cwd()}\n"
        log_entry += f"{'#'*80}\n"
        
        # Write to human-readable log
        with open(self.error_log_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
        
        # Also log as critical
        self.logger.critical(f"APPLICATION CRASH: {crash_message}")

    def _write_debug_log(self, data: Dict[str, Any]) -> None:
        """Write structured debug data to JSON log for automated analysis"""
        try:
            # Read existing data
            debug_data = []
            if self.debug_log_path.exists():
                with open(self.debug_log_path, 'r', encoding='utf-8') as f:
                    debug_data = json.load(f)
            
            # Add new entry
            debug_data.append(data)
            
            # Keep only last 1000 entries to prevent file from growing too large
            if len(debug_data) > 1000:
                debug_data = debug_data[-1000:]
            
            # Write back
            with open(self.debug_log_path, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=2, ensure_ascii=False)
        
        except Exception:
            # If debug logging fails, don't crash the application
            pass

    def get_recent_errors(self, count: int = 10) -> list:
        """Get recent error entries for debugging"""
        try:
            if not self.debug_log_path.exists():
                return []
            
            with open(self.debug_log_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return data[-count:] if data else []
        
        except Exception:
            return []

    def clear_logs(self) -> None:
        """Clear all log files (use with caution)"""
        try:
            if self.error_log_path.exists():
                self.error_log_path.unlink()
            if self.debug_log_path.exists():
                self.debug_log_path.unlink()
            
            # Reinitialize
            self._setup_logging()
            self._log_session_start()
        
        except Exception as e:
            print(f"Error clearing logs: {e}")


# Global error logger instance
_global_error_logger: Optional[ErrorLogger] = None


def get_error_logger() -> ErrorLogger:
    """Get or create global error logger instance"""
    global _global_error_logger
    
    if _global_error_logger is None:
        _global_error_logger = ErrorLogger()
    
    return _global_error_logger


def log_error_dialog(title: str, 
                    message: str, 
                    context: Optional[str] = None,
                    component: Optional[str] = None,
                    exception: Optional[Exception] = None,
                    user_action: Optional[str] = None) -> None:
    """
    Convenience function to log error dialogs globally
    
    Args:
        title: Dialog title/header
        message: Error message displayed to user
        context: Additional context about when error occurred
        component: Component/module where error occurred
        exception: Original exception if available
        user_action: What the user was trying to do when error occurred
    """
    logger = get_error_logger()
    logger.log_error_dialog(title, message, context, component, exception, user_action)


def log_validation_error(field: str, 
                        error_message: str, 
                        value: Any = None,
                        component: Optional[str] = None) -> None:
    """Convenience function to log validation errors globally"""
    logger = get_error_logger()
    logger.log_validation_error(field, error_message, value, component)


def log_file_operation_error(operation: str, 
                            file_path: str, 
                            error_message: str,
                            exception: Optional[Exception] = None) -> None:
    """Convenience function to log file operation errors globally"""
    logger = get_error_logger()
    logger.log_file_operation_error(operation, file_path, error_message, exception)