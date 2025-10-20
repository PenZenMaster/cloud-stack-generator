"""
Error Classification System - Clear Error vs Warning Criteria
Path: E:/projects/cloud-stack-generator/src/utils/error_classification.py

Description:
Provides clear, consistent criteria for classifying issues as errors vs warnings
and standardizes their presentation across the UI.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-23

Last Modified Date:
2025-09-23

Comments:
* v1.00 - Initial error classification system
"""

from enum import Enum
from typing import Dict, Any, Tuple
from dataclasses import dataclass
from PyQt6.QtWidgets import QMessageBox


class IssueLevel(Enum):
    """Classification levels for issues"""
    ERROR = "error"      # Blocks functionality, must be resolved
    WARNING = "warning"  # Doesn't block functionality, should be addressed
    INFO = "info"        # Informational, no action required
    CRITICAL = "critical" # System-level failure, application may be unstable


class IssueCategory(Enum):
    """Categories of issues for better classification"""
    TEMPLATE_PARSING = "template_parsing"
    FILE_OPERATION = "file_operation"
    VALIDATION = "validation"
    UI_INTERACTION = "ui_interaction"
    NETWORK = "network"
    PERMISSION = "permission"
    CONFIGURATION = "configuration"
    DATA_INTEGRITY = "data_integrity"


@dataclass
class IssueClassification:
    """Represents a classified issue"""
    level: IssueLevel
    category: IssueCategory
    title: str
    message: str
    technical_details: str
    user_action_suggestion: str
    log_to_file: bool
    show_dialog: bool
    dialog_icon: QMessageBox.Icon


class ErrorClassifier:
    """Classifies errors and warnings according to defined criteria"""

    def __init__(self):
        self._classification_rules = self._setup_classification_rules()

    def _setup_classification_rules(self) -> Dict[str, Any]:
        """Setup the rules for classifying different types of issues"""
        return {
            # Template parsing issues
            "template_parse_error": {
                "keywords": ["unexpected char", "parsing error", "malformed", "invalid syntax"],
                "default_level": IssueLevel.ERROR,
                "category": IssueCategory.TEMPLATE_PARSING,
                "log_required": True,
                "user_facing": True
            },

            # Template validation issues
            "template_validation": {
                "keywords": ["validation", "missing required", "invalid value"],
                "default_level": IssueLevel.WARNING,
                "category": IssueCategory.VALIDATION,
                "log_required": True,
                "user_facing": True
            },

            # File operation issues
            "file_not_found": {
                "keywords": ["no such file", "file not found", "does not exist"],
                "default_level": IssueLevel.ERROR,
                "category": IssueCategory.FILE_OPERATION,
                "log_required": True,
                "user_facing": True
            },

            "permission_denied": {
                "keywords": ["permission denied", "access denied", "not authorized"],
                "default_level": IssueLevel.ERROR,
                "category": IssueCategory.PERMISSION,
                "log_required": True,
                "user_facing": True
            },

            # Preview generation issues
            "preview_generation": {
                "keywords": ["preview", "rendering", "display"],
                "default_level": IssueLevel.WARNING,  # Previews are convenience features
                "category": IssueCategory.UI_INTERACTION,
                "log_required": True,
                "user_facing": True
            },

            # Import/dependency issues
            "missing_dependency": {
                "keywords": ["importerror", "no module named", "not installed"],
                "default_level": IssueLevel.WARNING,  # App should work with fallbacks
                "category": IssueCategory.CONFIGURATION,
                "log_required": True,
                "user_facing": False  # User can't fix this immediately
            }
        }

    def classify_issue(self,
                      exception: Exception,
                      context: str = "",
                      user_action: str = "",
                      component: str = "") -> IssueClassification:
        """
        Classify an issue based on exception details and context

        Args:
            exception: The exception that occurred
            context: What was happening when the error occurred
            user_action: What the user was trying to do
            component: Which component generated the error

        Returns:
            IssueClassification with appropriate level and presentation details
        """

        # Get exception details
        exception_type = type(exception).__name__
        exception_message = str(exception).lower()
        context_lower = context.lower()

        # Determine issue level and category
        level, category = self._determine_level_and_category(
            exception_type, exception_message, context_lower
        )

        # Create user-friendly title and message
        title, message, suggestion = self._create_user_friendly_messages(
            level, category, exception, context, user_action
        )

        # Determine dialog icon based on level
        dialog_icon = self._get_dialog_icon(level)

        return IssueClassification(
            level=level,
            category=category,
            title=title,
            message=message,
            technical_details=f"{exception_type}: {str(exception)}",
            user_action_suggestion=suggestion,
            log_to_file=True,  # Always log for debugging
            show_dialog=level in [IssueLevel.ERROR, IssueLevel.CRITICAL],
            dialog_icon=dialog_icon
        )

    def _determine_level_and_category(self,
                                    exception_type: str,
                                    exception_message: str,
                                    context: str) -> Tuple[IssueLevel, IssueCategory]:
        """Determine the appropriate level and category for an issue"""

        # Check for specific classification rules
        for rule_name, rule_config in self._classification_rules.items():
            keywords = rule_config["keywords"]
            if any(keyword in exception_message or keyword in context
                   for keyword in keywords):
                return rule_config["default_level"], rule_config["category"]

        # Special cases based on exception type
        if exception_type.lower() in ["filenotfounderror", "permissionerror"]:
            return IssueLevel.ERROR, IssueCategory.FILE_OPERATION

        if exception_type.lower() in ["importerror", "modulenotfounderror"]:
            return IssueLevel.WARNING, IssueCategory.CONFIGURATION

        if exception_type.lower() in ["validationerror", "valueerror"]:
            return IssueLevel.WARNING, IssueCategory.VALIDATION

        # Context-based classification
        if "preview" in context or "format" in context:
            return IssueLevel.WARNING, IssueCategory.UI_INTERACTION

        if "save" in context or "load" in context:
            return IssueLevel.ERROR, IssueCategory.FILE_OPERATION

        # Default fallback
        return IssueLevel.ERROR, IssueCategory.UI_INTERACTION

    def _create_user_friendly_messages(self,
                                     level: IssueLevel,
                                     category: IssueCategory,
                                     exception: Exception,
                                     context: str,
                                     user_action: str) -> Tuple[str, str, str]:
        """Create user-friendly title, message, and suggestion"""

        # Create appropriate title based on level
        level_word = "Error" if level == IssueLevel.ERROR else "Warning" if level == IssueLevel.WARNING else "Information"

        if category == IssueCategory.TEMPLATE_PARSING:
            title = f"Template {level_word}"
            message = self._create_template_parsing_message(exception, context)
            suggestion = "Please check your template syntax and fix any HTML errors."

        elif category == IssueCategory.VALIDATION:
            title = f"Validation {level_word}"
            message = f"Template validation issue: {str(exception)}"
            suggestion = "Please review and correct the highlighted issues."

        elif category == IssueCategory.FILE_OPERATION:
            title = f"File Operation {level_word}"
            message = f"Unable to {context}: {str(exception)}"
            suggestion = "Please check file permissions and try again."

        elif category == IssueCategory.UI_INTERACTION:
            title = f"Interface {level_word}"
            message = self._create_ui_interaction_message(exception, context, user_action)
            suggestion = "This is a non-critical issue. You can continue working."

        elif category == IssueCategory.CONFIGURATION:
            title = f"Configuration {level_word}"
            message = f"Missing dependency or configuration: {str(exception)}"
            suggestion = "Some features may be limited. Contact support if needed."

        else:
            title = f"Application {level_word}"
            message = f"An unexpected issue occurred: {str(exception)}"
            suggestion = "Please try the operation again or contact support."

        return title, message, suggestion

    def _create_template_parsing_message(self, exception: Exception, context: str) -> str:
        """Create specific message for template parsing errors"""
        error_str = str(exception)

        # Extract position information if available
        if "at" in error_str and any(char.isdigit() for char in error_str):
            return f"Template contains invalid HTML syntax: {error_str}"
        else:
            return f"Template parsing failed: {error_str}"

    def _create_ui_interaction_message(self, exception: Exception, context: str, user_action: str) -> str:
        """Create specific message for UI interaction issues"""
        if "preview" in context.lower():
            return f"Unable to generate template preview: {str(exception)}"
        elif "format" in context.lower():
            return f"Unable to format template code: {str(exception)}"
        else:
            return f"Interface operation failed while {user_action}: {str(exception)}"

    def _get_dialog_icon(self, level: IssueLevel) -> QMessageBox.Icon:
        """Get appropriate dialog icon for the issue level"""
        icon_map = {
            IssueLevel.ERROR: QMessageBox.Icon.Critical,      # Red X
            IssueLevel.CRITICAL: QMessageBox.Icon.Critical,  # Red X
            IssueLevel.WARNING: QMessageBox.Icon.Warning,    # Yellow Triangle
            IssueLevel.INFO: QMessageBox.Icon.Information    # Blue i
        }
        return icon_map.get(level, QMessageBox.Icon.Warning)

    def should_log_to_file(self, level: IssueLevel, category: IssueCategory) -> bool:
        """Determine if this issue should be logged to file"""
        # Always log errors and criticals
        if level in [IssueLevel.ERROR, IssueLevel.CRITICAL]:
            return True

        # Log warnings for certain categories
        if level == IssueLevel.WARNING and category in [
            IssueCategory.TEMPLATE_PARSING,
            IssueCategory.VALIDATION,
            IssueCategory.FILE_OPERATION
        ]:
            return True

        return False

    def should_show_dialog(self, level: IssueLevel, category: IssueCategory) -> bool:
        """Determine if this issue should show a user dialog"""
        # Always show dialogs for errors and criticals
        if level in [IssueLevel.ERROR, IssueLevel.CRITICAL]:
            return True

        # Show warnings for user-facing operations
        if level == IssueLevel.WARNING and category in [
            IssueCategory.TEMPLATE_PARSING,
            IssueCategory.VALIDATION,
            IssueCategory.UI_INTERACTION
        ]:
            return True

        return False


# Global classifier instance
_global_classifier = None


def get_error_classifier() -> ErrorClassifier:
    """Get the global error classifier instance"""
    global _global_classifier
    if _global_classifier is None:
        _global_classifier = ErrorClassifier()
    return _global_classifier


def classify_and_handle_error(exception: Exception,
                            context: str = "",
                            user_action: str = "",
                            component: str = "") -> IssueClassification:
    """
    Convenience function to classify and handle an error

    Args:
        exception: The exception that occurred
        context: What was happening when the error occurred
        user_action: What the user was trying to do
        component: Which component generated the error

    Returns:
        IssueClassification with handling recommendations
    """
    classifier = get_error_classifier()
    return classifier.classify_issue(exception, context, user_action, component)