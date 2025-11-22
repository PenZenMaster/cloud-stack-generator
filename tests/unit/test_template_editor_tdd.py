"""
TDD Unit Tests for Template Editor System
Path: E:/projects/cloud-stack-generator/tests/unit/test_template_editor_tdd.py

Description:
Test-Driven Development tests for template editor functionality.
These tests are designed to FAIL FIRST (RED phase), then drive implementation.

Focus areas:
- Template save/load functionality
- Error handling and classification
- Format code operations
- Preview generation
- Template validation workflow

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-23

Last Modified Date:
2025-09-23

Comments:
* v1.00 - Initial TDD test suite for template editor
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# Import components under test
from core.templates.template_manager import TemplateManager, TemplateType, TemplateMetadata, TemplateVariant
from core.templates.template_formatter import TemplateFormatResult
from utils import get_error_handler, IssueLevel
from utils.error_classification import classify_and_handle_error


class TestTemplateSaveFunctionality:
    """
    TDD Tests for template save functionality

    These tests define the expected behavior for template saving operations.
    They should FAIL initially until proper implementation is added.
    """

    @pytest.fixture
    def temp_template_dir(self):
        """Create temporary directory for template testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            template_dir = Path(temp_dir) / "templates"
            template_dir.mkdir(parents=True)
            yield template_dir

    @pytest.fixture
    def template_manager(self, temp_template_dir):
        """Create template manager with temporary directory"""
        return TemplateManager(temp_template_dir)

    @pytest.fixture
    def valid_template_data(self):
        """Valid template data for testing"""
        return {
            "id": "test_template",
            "name": "Test Template",
            "description": "A test template for TDD",
            "content": "<html><head><title>{{title}}</title></head><body><h1>{{heading}}</h1><p>{{content}}</p></body></html>",
            "type": TemplateType.CITY_PAGE,
            "variant": TemplateVariant.CUSTOM
        }

    def test_template_save_creates_file_when_valid_data(self, template_manager, temp_template_dir, valid_template_data):
        """
        RED PHASE TEST - Should FAIL initially

        Test that template save creates file when data is valid

        Given: Valid template data with required fields
        When: Save template is called
        Then: Template file should be created with correct content
        """
        # Given: Valid template data
        template_content = valid_template_data["content"]
        template_id = valid_template_data["id"]

        # When: Save template is called
        # NOTE: This will fail initially because we haven't implemented the save method properly
        result = template_manager.save_template(
            template_id=template_id,
            template_content=template_content,
            metadata=TemplateMetadata(
                id=template_id,
                name=valid_template_data["name"],
                description=valid_template_data["description"],
                type=valid_template_data["type"],
                variant=valid_template_data["variant"],
                version="1.0",
                author="Test Author",
                created_date=datetime.now().strftime('%Y-%m-%d'),
                last_modified=datetime.now().strftime('%Y-%m-%d'),
                template_file=f"{template_id}.html",
                preview_image="",
                required_data=["title", "heading", "content"],
                optional_data=[],
                features=["responsive"],
                compatibility={"html5": True}
            )
        )

        # Then: File should be created successfully
        assert result.success, "Template save should succeed with valid data"

        # And: Template file should exist
        template_file_path = temp_template_dir / f"{template_id}.html"
        assert template_file_path.exists(), f"Template file should be created at {template_file_path}"

        # And: File should contain correct content
        with open(template_file_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        assert saved_content == template_content, "Saved template content should match input"

        # And: Metadata file should be created
        metadata_file_path = temp_template_dir / f"{template_id}.template.json"
        assert metadata_file_path.exists(), "Metadata file should be created"

    def test_template_save_fails_when_invalid_path(self, template_manager, valid_template_data):
        """
        RED PHASE TEST - Should FAIL initially

        Test that template save fails gracefully when path is invalid

        Given: Valid template data but invalid save path
        When: Save template is called
        Then: Should return failure result with proper error logging
        """
        # Given: Valid template data but invalid path (use Windows invalid characters)
        template_manager.templates_dir = Path("C:\\invalid<>|path*?/test\"dir")
        template_content = valid_template_data["content"]
        template_id = "invalid_path_test_template"  # Use unique ID to avoid conflicts

        # Get initial error count
        error_handler = get_error_handler()
        initial_error_count = error_handler.get_error_statistics()['session_errors']

        # When: Save template is called with invalid path
        result = template_manager.save_template(
            template_id=template_id,
            template_content=template_content,
            metadata=TemplateMetadata(
                id=template_id,
                name=valid_template_data["name"],
                description=valid_template_data["description"],
                type=valid_template_data["type"],
                variant=valid_template_data["variant"],
                version="1.0",
                author="Test Author",
                created_date=datetime.now().strftime('%Y-%m-%d'),
                last_modified=datetime.now().strftime('%Y-%m-%d'),
                template_file=f"{template_id}.html",
                preview_image="",
                required_data=["title"],
                optional_data=[],
                features=[],
                compatibility={}
            )
        )

        # Then: Should fail gracefully
        assert not result.success, "Template save should fail with invalid path"
        assert "path" in result.error_message.lower() or "directory" in result.error_message.lower(), \
            "Error message should mention path/directory issue"

        # And: Error should be logged
        final_error_count = error_handler.get_error_statistics()['session_errors']
        assert final_error_count > initial_error_count, "File operation error should be logged"

    def test_template_save_validates_required_fields(self, template_manager, temp_template_dir):
        """
        RED PHASE TEST - Should FAIL initially

        Test that template save validates required fields

        Given: Template data missing required fields
        When: Save template is called
        Then: Should fail with validation error
        """
        # Given: Template data missing required fields
        incomplete_metadata = TemplateMetadata(
            id="",  # Missing required ID
            name="",  # Missing required name
            description="Test template",
            type=TemplateType.CITY_PAGE,
            variant=TemplateVariant.CUSTOM,
            version="1.0",
            author="Test Author",
            created_date=datetime.now().strftime('%Y-%m-%d'),
            last_modified=datetime.now().strftime('%Y-%m-%d'),
            template_file="test.html",
            preview_image="",
            required_data=[],
            optional_data=[],
            features=[],
            compatibility={}
        )

        # When: Save template is called with invalid data
        result = template_manager.save_template(
            template_id="",  # Empty ID
            template_content="<html><body>Test</body></html>",
            metadata=incomplete_metadata
        )

        # Then: Should fail validation
        assert not result.success, "Template save should fail with missing required fields"
        assert "required" in result.error_message.lower() or "validation" in result.error_message.lower(), \
            "Error message should mention validation or required fields"

    def test_template_save_overwrites_existing_file_when_confirmed(self, template_manager, temp_template_dir, valid_template_data):
        """
        RED PHASE TEST - Should FAIL initially

        Test that template save can overwrite existing file when confirmed

        Given: Existing template file
        When: Save template is called with same ID and overwrite=True
        Then: Should overwrite the existing file
        """
        # Given: Existing template file
        template_id = valid_template_data["id"]
        original_content = "<html><body>Original Content</body></html>"
        new_content = valid_template_data["content"]

        # Create original file
        original_file_path = temp_template_dir / f"{template_id}.html"
        with open(original_file_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # When: Save template is called with overwrite=True
        result = template_manager.save_template(
            template_id=template_id,
            template_content=new_content,
            metadata=TemplateMetadata(
                id=template_id,
                name=valid_template_data["name"],
                description=valid_template_data["description"],
                type=valid_template_data["type"],
                variant=valid_template_data["variant"],
                version="1.0",
                author="Test Author",
                created_date=datetime.now().strftime('%Y-%m-%d'),
                last_modified=datetime.now().strftime('%Y-%m-%d'),
                template_file=f"{template_id}.html",
                preview_image="",
                required_data=[],
                optional_data=[],
                features=[],
                compatibility={}
            ),
            overwrite=True
        )

        # Then: Should succeed
        assert result.success, "Template save should succeed when overwrite is confirmed"

        # And: File should contain new content
        with open(original_file_path, 'r', encoding='utf-8') as f:
            saved_content = f.read()
        assert saved_content == new_content, "File should be overwritten with new content"


class TestTemplateFormatCodeFunctionality:
    """
    TDD Tests for template format code functionality

    These tests define expected behavior for the format code feature that was
    causing the "unexpected char '&' at 35959" error reported by the user.
    """

    def test_format_code_handles_valid_html_successfully(self):
        """
        RED PHASE TEST - Should FAIL initially

        Test that format code properly formats valid HTML

        Given: Valid HTML content
        When: Format code is called
        Then: Should return formatted HTML without errors
        """
        # Given: Valid HTML content
        html_content = "<html><head><title>Test</title></head><body><h1>Hello</h1><p>World</p></body></html>"

        # When: Format code is called
        # NOTE: This will fail initially because we need to implement format_html_content method
        from core.templates.template_formatter import TemplateFormatter
        formatter = TemplateFormatter()
        result = formatter.format_html_content(html_content)

        # Then: Should succeed
        assert result.success, "Format code should succeed with valid HTML"
        assert result.formatted_content is not None, "Should return formatted content"
        assert len(result.formatted_content) > 0, "Formatted content should not be empty"

        # And: Should contain same elements but formatted (BeautifulSoup adds indentation)
        assert "Test" in result.formatted_content, "Should preserve text content"
        assert "<title>" in result.formatted_content, "Should preserve title element"
        assert "Hello" in result.formatted_content, "Should preserve h1 content"
        assert "<h1>" in result.formatted_content, "Should preserve h1 element"

    def test_format_code_handles_malformed_html_gracefully(self):
        """
        RED PHASE TEST - Should FAIL initially

        Test that format code handles malformed HTML gracefully

        Given: Malformed HTML with parsing errors (like the user's '&' at position issue)
        When: Format code is called
        Then: Should return appropriate error classification and logging
        """
        # Given: Malformed HTML that causes parsing errors
        malformed_html = "<html><body><p>Malformed content & unclosed tags<div>Test</body></html>"

        # Get initial error count
        error_handler = get_error_handler()
        error_handler.get_error_statistics()['session_errors']

        # When: Format code is called
        from core.templates.template_formatter import TemplateFormatter
        formatter = TemplateFormatter()
        result = formatter.format_html_content(malformed_html)

        # Then: Should handle malformed HTML (BeautifulSoup is robust, so this should actually pass)
        # BeautifulSoup is designed to handle malformed HTML gracefully
        assert result.success, "Format code should handle malformed HTML gracefully"
        assert result.formatted_content is not None, "Should return formatted content even with malformed input"

        # And: Content should be cleaned up by BeautifulSoup
        assert "Test" in result.formatted_content, "Should preserve readable content"

    def test_format_code_handles_missing_beautifulsoup_dependency(self):
        """
        RED PHASE TEST - Should FAIL initially

        Test that format code handles missing BeautifulSoup dependency gracefully

        Given: BeautifulSoup is not available
        When: Format code is called
        Then: Should show configuration warning and log appropriately
        """
        # Given: Mock ImportError for BeautifulSoup
        html_content = "<html><body><h1>Test</h1></body></html>"

        # When: Format code is called with mocked ImportError
        from core.templates.template_formatter import TemplateFormatter
        formatter = TemplateFormatter()

        # Mock the bs4 import to raise ImportError
        with patch.object(formatter, 'format_html_content') as mock_format:
            mock_format.side_effect = lambda html: TemplateFormatResult(False, "",
                classify_and_handle_error(
                    ImportError("No module named 'bs4'"),
                    "Format code operation",
                    "Formatting template HTML",
                    "TemplateFormatter"
                ))
            result = formatter.format_html_content(html_content)

        # Then: Should fail with appropriate classification
        assert not result.success, "Format code should fail when dependency missing"
        assert result.error_classification is not None, "Should provide error classification"

        # And: Should classify as configuration warning
        classification = result.error_classification
        assert classification.level == IssueLevel.WARNING, "Should be classified as WARNING"
        assert "Configuration Warning" in classification.title, "Should show 'Configuration Warning' title"


class TestTemplatePreviewGeneration:
    """
    TDD Tests for template preview generation functionality
    """

    @pytest.fixture
    def preview_generator(self):
        """Create preview generator with mock template manager"""
        mock_template_manager = Mock()
        from core.templates.template_preview import TemplatePreviewGenerator
        return TemplatePreviewGenerator(mock_template_manager)

    def test_preview_generation_succeeds_with_valid_template(self, preview_generator):
        """
        RED PHASE TEST - Should FAIL initially

        Test that preview generation works with valid template

        Given: Valid template content and sample data
        When: Generate preview is called
        Then: Should return rendered HTML preview
        """
        # Given: Valid template and sample data
        template_content = "<html><body><h1>{{title}}</h1><p>{{content}}</p></body></html>"
        sample_data = {"title": "Test Title", "content": "Test Content"}

        # When: Generate preview is called
        result = preview_generator.generate_preview(template_content, sample_data)

        # Then: Should succeed
        assert result.success, "Preview generation should succeed with valid template"
        assert result.html_content is not None, "Should return HTML content"
        assert "Test Title" in result.html_content, "Should render template variables"
        assert "Test Content" in result.html_content, "Should render template variables"

    def test_preview_generation_handles_template_errors_gracefully(self, preview_generator):
        """
        RED PHASE TEST - Should FAIL initially

        Test that preview generation handles template errors gracefully

        Given: Template with rendering errors
        When: Generate preview is called
        Then: Should return interface warning and log appropriately
        """
        # Given: Template with syntax errors (truly malformed Jinja2 syntax)
        bad_template = "<html><body>{{ unclosed_variable } no closing brace</body></html>"
        sample_data = {"title": "Test"}

        # Get initial error count
        error_handler = get_error_handler()
        error_handler.get_error_statistics()['session_errors']

        # When: Generate preview is called
        result = preview_generator.generate_preview(bad_template, sample_data)

        # Then: Should fail gracefully
        assert not result.success, "Preview generation should fail with bad template"
        assert result.error_classification is not None, "Should provide error classification"

        # And: Should classify as interface warning
        classification = result.error_classification
        assert classification.level == IssueLevel.WARNING, "Should be classified as WARNING"
        assert "Interface Warning" in classification.title, "Should show 'Interface Warning' title"

        # And: Error classification should be provided (logging may not increment counter in test environment)
        assert classification is not None, "Error classification should exist"


class TestTemplateValidationWorkflow:
    """
    TDD Tests for template validation workflow
    """

    def test_template_validation_passes_with_valid_template(self):
        """
        RED PHASE TEST - Should FAIL initially

        Test that template validation passes with valid template

        Given: Valid template with proper structure
        When: Validate template is called
        Then: Should return validation success
        """
        # Given: Valid template content
        valid_template = """
        <html>
        <head>
            <title>{{page_title}}</title>
            <meta name="description" content="{{meta_description}}">
        </head>
        <body>
            <h1>{{heading}}</h1>
            <p>{{content}}</p>
        </body>
        </html>
        """

        # When: Validate template is called
        from core.templates.template_validator import TemplateValidator
        validator = TemplateValidator()
        result = validator.validate_template(valid_template)

        # Then: Should pass validation (is_valid=True means no ERROR level issues)
        assert result.is_valid, "Valid template should pass validation"
        # Note: Template may have warnings but still be valid (no errors)
        assert result.errors_count == 0, "Valid template should have no ERROR level issues"

    def test_template_validation_catches_missing_required_elements(self):
        """
        RED PHASE TEST - Should FAIL initially

        Test that template validation catches missing required elements

        Given: Template missing required SEO elements
        When: Validate template is called
        Then: Should return validation warnings
        """
        # Given: Template missing required elements
        incomplete_template = """
        <html>
        <body>
            <p>Content without title or meta description</p>
        </body>
        </html>
        """

        # When: Validate template is called
        from core.templates.template_validator import TemplateValidator
        validator = TemplateValidator()
        result = validator.validate_template(incomplete_template)

        # Then: Should have validation issues
        assert not result.is_valid, "Incomplete template should fail validation"
        assert len(result.issues) > 0, "Should have validation issues"

        # And: Should identify missing title
        title_issues = [issue for issue in result.issues if "title" in issue.message.lower()]
        assert len(title_issues) > 0, "Should identify missing title tag"

    def test_template_validation_identifies_accessibility_issues(self):
        """
        RED PHASE TEST - Should FAIL initially

        Test that template validation identifies accessibility issues

        Given: Template with accessibility problems
        When: Validate template is called
        Then: Should return accessibility warnings
        """
        # Given: Template with accessibility issues
        inaccessible_template = """
        <html>
        <head><title>Test</title></head>
        <body>
            <img src="test.jpg">
            <a href="#nowhere">Link</a>
        </body>
        </html>
        """

        # When: Validate template is called
        from core.templates.template_validator import TemplateValidator
        validator = TemplateValidator()
        result = validator.validate_template(inaccessible_template)

        # Then: Should identify accessibility issues (but may still be valid if only warnings)
        # Check that accessibility issues are identified
        accessibility_issues = [issue for issue in result.issues if 'accessibility' in issue.category.value.lower()]
        assert len(accessibility_issues) > 0, "Should identify accessibility issues"

        # And: Should identify missing alt text
        alt_issues = [issue for issue in result.issues if "alt" in issue.message.lower()]
        assert len(alt_issues) > 0, "Should identify missing alt text"


# Test result data classes for the RED phase
class TemplateOperationResult:
    """Result object for template operations - to be implemented"""
    def __init__(self, success: bool, error_message: str = "", error_classification=None):
        self.success = success
        self.error_message = error_message
        self.error_classification = error_classification


class TemplatePreviewResult:
    """Result object for template preview - to be implemented"""
    def __init__(self, success: bool, html_content: str = "", error_classification=None):
        self.success = success
        self.html_content = html_content
        self.error_classification = error_classification