"""
Unit tests for Template Validator
Path: E:/projects/cloud-stack-generator/tests/unit/test_template_validator.py

Description:
Comprehensive unit tests for the template validation system,
covering syntax, HTML structure, SEO, accessibility, performance, and security validation.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Initial test suite for template validator
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.templates.template_validator import (
    TemplateValidator,
    ValidationResult,
    ValidationIssue,
    ValidationCategory,
    ValidationLevel
)


class TestValidationIssue:
    """Tests for ValidationIssue dataclass"""

    def test_validation_issue_creation(self):
        """Test creating a ValidationIssue"""
        issue = ValidationIssue(
            category=ValidationCategory.SYNTAX,
            level=ValidationLevel.ERROR,
            message="Test error message",
            line_number=5,
            column_number=10,
            suggestion="Fix this error"
        )

        assert issue.category == ValidationCategory.SYNTAX
        assert issue.level == ValidationLevel.ERROR
        assert issue.message == "Test error message"
        assert issue.line_number == 5
        assert issue.column_number == 10
        assert issue.suggestion == "Fix this error"

    def test_validation_issue_repr(self):
        """Test string representation of ValidationIssue"""
        issue = ValidationIssue(
            type=ValidationCategory.SEO,
            severity=ValidationLevel.WARNING,
            message="Missing meta description"
        )

        repr_str = repr(issue)
        assert "SEO" in repr_str
        assert "WARNING" in repr_str
        assert "Missing meta description" in repr_str


class TestValidationResult:
    """Tests for ValidationResult dataclass"""

    def test_validation_result_creation(self):
        """Test creating a ValidationResult"""
        issues = [
            ValidationIssue(ValidationCategory.SYNTAX, ValidationLevel.ERROR, "Syntax error"),
            ValidationIssue(ValidationCategory.SEO, ValidationLevel.WARNING, "SEO warning")
        ]

        result = ValidationResult(
            is_valid=False,
            issues=issues,
            warnings_count=1,
            errors_count=1,
            validation_time=0.5
        )

        assert result.is_valid is False
        assert len(result.issues) == 2
        assert result.warnings_count == 1
        assert result.errors_count == 1
        assert result.validation_time == 0.5

    def test_validation_result_success(self):
        """Test creating a successful validation result"""
        result = ValidationResult(
            is_valid=True,
            issues=[],
            warnings_count=0,
            errors_count=0,
            validation_time=0.1
        )

        assert result.is_valid is True
        assert len(result.issues) == 0


class TestTemplateValidator:
    """Tests for TemplateValidator class"""

    @pytest.fixture
    def validator(self):
        """Create TemplateValidator instance"""
        return TemplateValidator()

    @pytest.fixture
    def temp_components_dir(self):
        """Create temporary components directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir) / "templates"
            components_dir = templates_dir / "components"
            components_dir.mkdir(parents=True)

            # Create sample header component
            header_file = components_dir / "header.html"
            header_file.write_text("""
<header>
    <h1>{{ business_name }}</h1>
    <nav>Navigation</nav>
</header>
            """)

            # Create sample footer component
            footer_file = components_dir / "footer.html"
            footer_file.write_text("""
<footer>
    <p>&copy; {{ current_year }} {{ business_name }}</p>
</footer>
            """)

            yield components_dir.parent

    def test_validator_initialization(self, validator):
        """Test TemplateValidator initialization"""
        assert validator is not None
        # Test that Jinja2 environment is set up if available
        if hasattr(validator, 'jinja_env') and validator.jinja_env:
            assert validator.jinja_env is not None

    def test_validate_template_valid_html(self, validator):
        """Test validating a valid HTML template"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <meta name="description" content="{{ meta_description }}">
</head>
<body>
    <h1>{{ heading }}</h1>
    <p>{{ content }}</p>
</body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        assert isinstance(result, ValidationResult)
        # Should have minimal issues for a well-formed template
        errors = [issue for issue in result.issues if issue.level == ValidationLevel.ERROR]
        assert len(errors) == 0

    def test_validate_template_syntax_error(self, validator):
        """Test validating template with Jinja2 syntax errors"""
        template_content = """
<html>
<body>
    <h1>{{ unclosed_variable</h1>
    <p>{% if condition %}</p>
    <p>Missing endif</p>
</body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        assert isinstance(result, ValidationResult)
        # Should detect syntax errors
        syntax_errors = [
            issue for issue in result.issues
            if issue.category == ValidationCategory.SYNTAX and issue.level == ValidationLevel.ERROR
        ]
        assert len(syntax_errors) > 0

    def test_validate_html_structure_missing_doctype(self, validator):
        """Test HTML structure validation - missing DOCTYPE"""
        template_content = """
<html>
<head><title>Test</title></head>
<body><h1>Test</h1></body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Should detect missing DOCTYPE
        doctype_issues = [
            issue for issue in result.issues
            if "DOCTYPE" in issue.message
        ]
        assert len(doctype_issues) > 0

    def test_validate_html_structure_missing_lang(self, validator):
        """Test HTML structure validation - missing lang attribute"""
        template_content = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Test</h1></body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Should detect missing lang attribute
        lang_issues = [
            issue for issue in result.issues
            if "lang" in issue.message.lower()
        ]
        assert len(lang_issues) > 0

    def test_validate_seo_missing_title(self, validator):
        """Test SEO validation - missing title tag"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body><h1>Content</h1></body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Should detect missing title
        title_issues = [
            issue for issue in result.issues
            if issue.category == ValidationCategory.SEO and "title" in issue.message.lower()
        ]
        assert len(title_issues) > 0

    def test_validate_seo_missing_meta_description(self, validator):
        """Test SEO validation - missing meta description"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Page</title>
    <meta charset="UTF-8">
</head>
<body><h1>Content</h1></body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Should detect missing meta description
        desc_issues = [
            issue for issue in result.issues
            if issue.category == ValidationCategory.SEO and "description" in issue.message.lower()
        ]
        assert len(desc_issues) > 0

    def test_validate_accessibility_missing_alt_text(self, validator):
        """Test accessibility validation - missing alt text"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head><title>Test</title></head>
<body>
    <img src="test.jpg">
    <img src="test2.jpg" alt="">
</body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Should detect missing alt attributes
        alt_issues = [
            issue for issue in result.issues
            if issue.category == ValidationCategory.ACCESSIBILITY and "alt" in issue.message.lower()
        ]
        assert len(alt_issues) > 0

    def test_validate_accessibility_heading_structure(self, validator):
        """Test accessibility validation - heading hierarchy"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head><title>Test</title></head>
<body>
    <h3>Skipped H1 and H2</h3>
    <h1>Out of order</h1>
</body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Should detect heading hierarchy issues
        heading_issues = [
            issue for issue in result.issues
            if issue.category == ValidationCategory.ACCESSIBILITY and "heading" in issue.message.lower()
        ]
        assert len(heading_issues) > 0

    def test_validate_performance_missing_viewport(self, validator):
        """Test performance validation - missing viewport meta tag"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test</title>
    <meta charset="UTF-8">
</head>
<body><h1>Content</h1></body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Should detect missing viewport
        viewport_issues = [
            issue for issue in result.issues
            if "viewport" in issue.message.lower()
        ]
        assert len(viewport_issues) > 0

    def test_validate_security_inline_scripts(self, validator):
        """Test security validation - inline scripts"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head><title>Test</title></head>
<body>
    <script>alert('inline script');</script>
    <div onclick="malicious()">Click me</div>
</body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Should detect security issues
        security_issues = [
            issue for issue in result.issues
            if issue.category == ValidationCategory.SECURITY
        ]
        assert len(security_issues) > 0

    def test_validate_template_with_components(self, validator, temp_components_dir):
        """Test validating template with component includes"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ page_title }}</title>
    <meta name="description" content="{{ meta_description }}">
</head>
<body>
    {% include 'components/header.html' %}
    <main>
        <h1>{{ heading }}</h1>
        <p>{{ content }}</p>
    </main>
    {% include 'components/footer.html' %}
</body>
</html>
        """.strip()

        # Mock the component loading to use our temp directory
        with patch.object(validator, '_load_component_templates') as mock_load:
            # Load actual components from temp directory
            components = {}
            header_file = temp_components_dir / "components" / "header.html"
            footer_file = temp_components_dir / "components" / "footer.html"

            components['components/header.html'] = header_file.read_text()
            components['components/footer.html'] = footer_file.read_text()
            components['header.html'] = components['components/header.html']
            components['footer.html'] = components['components/footer.html']

            mock_load.return_value = components

            # Recreate validator with mocked components
            validator = TemplateValidator()
            result = validator.validate_template(template_content)

            assert isinstance(result, ValidationResult)
            # Template with includes should validate successfully
            syntax_errors = [
                issue for issue in result.issues
                if issue.category == ValidationCategory.SYNTAX and issue.level == ValidationLevel.ERROR
            ]
            assert len(syntax_errors) == 0

    def test_validate_template_with_metadata(self, validator):
        """Test validating template with metadata context"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ page_title }}</title>
</head>
<body>
    <h1>{{ heading }}</h1>
</body>
</html>
        """.strip()

        metadata = {
            'required_data': ['page_title', 'heading'],
            'optional_data': ['meta_description'],
            'features': ['SEO optimized', 'Mobile responsive']
        }

        result = validator.validate_template(template_content, metadata)

        assert isinstance(result, ValidationResult)
        # Validation should consider the metadata context

    def test_validate_template_empty_content(self, validator):
        """Test validating empty template content"""
        result = validator.validate_template("")

        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        # Should have errors for empty content
        assert result.errors_count > 0

    def test_validate_template_none_content(self, validator):
        """Test validating None template content"""
        result = validator.validate_template(None)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is False

    @patch('core.templates.template_validator.JINJA2_AVAILABLE', False)
    def test_validate_template_no_jinja2(self):
        """Test validation when Jinja2 is not available"""
        validator = TemplateValidator()

        template_content = """
<!DOCTYPE html>
<html>
<body>{{ test }}</body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        assert isinstance(result, ValidationResult)
        # Should still perform basic HTML validation

    def test_performance_timing(self, validator):
        """Test that validation timing is recorded"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head><title>Test</title></head>
<body><h1>Test</h1></body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        assert result.validation_time > 0
        assert isinstance(result.validation_time, float)

    def test_issue_counting(self, validator):
        """Test that issues are counted correctly"""
        template_content = """
<html>
<body>
    <img src="test.jpg">
    <script>alert('test');</script>
</body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Verify counts match actual issues
        error_count = len([i for i in result.issues if i.level == ValidationLevel.ERROR])
        warning_count = len([i for i in result.issues if i.level == ValidationLevel.WARNING])

        assert result.errors_count == error_count
        assert result.warnings_count == warning_count

    def test_load_html_tags(self, validator):
        """Test HTML tags loading functionality"""
        # This tests the internal _load_html_tags method
        html_tags = validator._load_html_tags()

        assert isinstance(html_tags, set)
        assert 'html' in html_tags
        assert 'body' in html_tags
        assert 'div' in html_tags
        assert 'script' in html_tags

    def test_extract_template_variables(self, validator):
        """Test template variable extraction"""
        template_content = """
<html>
<body>
    <h1>{{ page_title }}</h1>
    <p>{{ content | safe }}</p>
    {% for item in items %}
        <span>{{ item.name }}</span>
    {% endfor %}
</body>
</html>
        """.strip()

        # This would test internal variable extraction
        # Implementation depends on whether this method exists
        if hasattr(validator, '_extract_template_variables'):
            variables = validator._extract_template_variables(template_content)
            assert 'page_title' in variables
            assert 'content' in variables
            assert 'items' in variables

    def test_suggest_fixes(self, validator):
        """Test that validation issues include helpful suggestions"""
        template_content = """
<html>
<head></head>
<body>
    <img src="test.jpg">
</body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Check that issues have suggestions
        issues_with_suggestions = [
            issue for issue in result.issues
            if issue.suggestion and len(issue.suggestion.strip()) > 0
        ]
        assert len(issues_with_suggestions) > 0

    def test_validation_categories(self, validator):
        """Test that all validation categories are covered"""
        template_content = """
<html>
<head></head>
<body>
    <h3>Wrong heading order</h3>
    <img src="test.jpg">
    <script>alert('test');</script>
</body>
</html>
        """.strip()

        result = validator.validate_template(template_content)

        # Should have issues from multiple categories
        issue_types = {issue.category for issue in result.issues}

        # Should cover multiple validation areas
        assert len(issue_types) > 1


class TestTemplateValidatorIntegration:
    """Integration tests for TemplateValidator"""

    def test_comprehensive_validation_workflow(self):
        """Test complete validation workflow with realistic template"""
        template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title | default('Default Title') }}</title>
    <meta name="description" content="{{ meta_description | default('Default description') }}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>{{ business_name }}</h1>
        <nav role="navigation">
            <ul>
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </nav>
    </header>

    <main>
        <section>
            <h2>{{ section_title }}</h2>
            <p>{{ section_content }}</p>
            <img src="{{ hero_image }}" alt="{{ hero_alt_text }}" loading="lazy">
        </section>

        {% if services %}
        <section>
            <h2>Our Services</h2>
            <ul>
                {% for service in services %}
                <li>{{ service.name }}: {{ service.description }}</li>
                {% endfor %}
            </ul>
        </section>
        {% endif %}
    </main>

    <footer>
        <p>&copy; {{ current_year }} {{ business_name }}. All rights reserved.</p>
    </footer>
</body>
</html>
        """.strip()

        validator = TemplateValidator()
        result = validator.validate_template(template_content)

        # This should be a well-formed template with minimal issues
        assert isinstance(result, ValidationResult)
        assert result.validation_time > 0

        # Should have few or no errors
        critical_errors = [
            issue for issue in result.issues
            if issue.level == ValidationLevel.ERROR
        ]
        assert len(critical_errors) == 0  # Well-formed template should have no errors


if __name__ == '__main__':
    pytest.main([__file__])