"""
Template Formatter - HTML Template Formatting Utilities
Path: E:/projects/cloud-stack-generator/src/core/templates/template_formatter.py

Description:
Provides HTML formatting capabilities for template content with error handling
and classification integration.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-23

Last Modified Date:
2025-09-23

Comments:
* v1.00 - Initial template formatter with error classification
"""

from typing import Optional
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from utils.error_classification import classify_and_handle_error


class TemplateFormatter:
    """Formats HTML template content with proper error handling"""

    def __init__(self):
        pass

    def format_html_content(self, html_content: str) -> 'TemplateFormatResult':
        """
        Format HTML content using BeautifulSoup

        Args:
            html_content: Raw HTML content to format

        Returns:
            TemplateFormatResult with success status and formatted content or error details
        """
        try:
            from bs4 import BeautifulSoup

            # Parse and format HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            formatted_html = soup.prettify()

            return TemplateFormatResult(True, formatted_html)

        except ImportError as e:
            # Missing dependency - classify as configuration warning
            classification = classify_and_handle_error(
                exception=e,
                context="Format code operation",
                user_action="Formatting template HTML",
                component="TemplateFormatter"
            )

            return TemplateFormatResult(False, "", classification)

        except Exception as e:
            # Template parsing error - classify as template error
            classification = classify_and_handle_error(
                exception=e,
                context="Format code operation",
                user_action="Formatting template HTML",
                component="TemplateFormatter"
            )

            return TemplateFormatResult(False, "", classification)


class TemplateFormatResult:
    """Result object for template formatting operations"""

    def __init__(self, success: bool, formatted_content: str = "", error_classification=None):
        self.success = success
        self.formatted_content = formatted_content
        self.error_classification = error_classification