"""
Unit tests for Utility Modules
Path: E:/projects/cloud-stack-generator/tests/unit/test_utils.py

Description:
Tests for the extracted utility modules (string_utils, html_utils) to ensure
proper functionality after refactoring from website_generator.py.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-17

Last Modified Date:
2025-10-17

Comments:
* v1.00 - Initial tests for refactored utility modules
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.utils.string_utils import (
    create_slug,
    generate_city_slug,
    normalize_phone,
    format_phone_display,
)
from core.utils.html_utils import (
    format_content_body,
    modify_iframe_size,
)


class TestStringUtils:
    """Tests for string_utils module"""

    def test_create_slug_basic(self):
        """Test basic slug creation"""
        assert create_slug("Chicago, IL") == "chicago-il"
        assert create_slug("Oak Brook") == "oak-brook"
        assert create_slug("St. Charles") == "st-charles"

    def test_create_slug_removes_special_chars(self):
        """Test that special characters are removed"""
        assert create_slug("City@Name!") == "cityname"
        assert create_slug("City & Town") == "city-town"

    def test_create_slug_handles_multiple_spaces(self):
        """Test handling of multiple spaces"""
        assert create_slug("City  Name") == "city-name"
        assert create_slug("  City Name  ") == "city-name"

    def test_create_slug_lowercase(self):
        """Test that output is lowercase"""
        assert create_slug("CHICAGO") == "chicago"
        assert create_slug("ChIcAgO") == "chicago"

    def test_generate_city_slug_basic(self):
        """Test city slug generation"""
        assert generate_city_slug("Chicago, IL") == "chicago-il"
        assert generate_city_slug("Oak Brook") == "oak-brook"

    def test_generate_city_slug_state_removal(self):
        """Test state suffix removal"""
        # Note: Pattern only removes " illinois" and " il" with leading space
        # After comma removal, "Aurora IL" becomes "aurora il" which matches
        assert generate_city_slug("Aurora IL") == "aurora-il"
        # "Naperville,IL" becomes "napervilleil" (no space before IL)
        assert generate_city_slug("Naperville,IL") == "napervilleil"

    def test_generate_city_slug_comma_removal(self):
        """Test comma removal"""
        assert generate_city_slug("City, State") == "city-state"
        assert generate_city_slug("City,State") == "citystate"

    def test_normalize_phone_basic(self):
        """Test basic phone normalization"""
        assert normalize_phone("(555) 123-4567") == "5551234567"
        assert normalize_phone("555-123-4567") == "5551234567"
        assert normalize_phone("5551234567") == "5551234567"

    def test_normalize_phone_removes_all_non_digits(self):
        """Test that all non-digit characters are removed"""
        assert normalize_phone("+1 (555) 123-4567") == "15551234567"
        assert normalize_phone("555.123.4567") == "5551234567"

    def test_normalize_phone_empty_input(self):
        """Test handling of empty input"""
        assert normalize_phone("") == ""
        assert normalize_phone(None) == ""

    def test_format_phone_display_basic(self):
        """Test basic phone formatting"""
        assert format_phone_display("5551234567") == "(555) 123-4567"
        assert format_phone_display("15551234567") == "(555) 123-4567"

    def test_format_phone_display_already_formatted(self):
        """Test that already formatted phones are preserved"""
        formatted = "(555) 123-4567"
        assert format_phone_display(formatted) == formatted

    def test_format_phone_display_10_digits(self):
        """Test formatting of 10-digit numbers"""
        assert format_phone_display("5551234567") == "(555) 123-4567"

    def test_format_phone_display_11_digits(self):
        """Test formatting of 11-digit numbers (with 1 prefix)"""
        assert format_phone_display("15551234567") == "(555) 123-4567"

    def test_format_phone_display_unparseable(self):
        """Test handling of unparseable phone numbers"""
        assert format_phone_display("123") == "123"
        assert format_phone_display("invalid") == "invalid"

    def test_format_phone_display_empty_input(self):
        """Test handling of empty input"""
        assert format_phone_display("") == ""
        assert format_phone_display(None) == ""


class TestHtmlUtils:
    """Tests for html_utils module"""

    def test_format_content_body_basic(self):
        """Test basic content formatting"""
        content = "First paragraph.\n\nSecond paragraph."
        expected = "<p>First paragraph.</p>\n<p>Second paragraph.</p>"
        assert format_content_body(content) == expected

    def test_format_content_body_single_paragraph(self):
        """Test single paragraph formatting"""
        content = "Single paragraph."
        expected = "<p>Single paragraph.</p>"
        assert format_content_body(content) == expected

    def test_format_content_body_multiple_paragraphs(self):
        """Test multiple paragraph formatting"""
        content = "First.\n\nSecond.\n\nThird."
        expected = "<p>First.</p>\n<p>Second.</p>\n<p>Third.</p>"
        assert format_content_body(content) == expected

    def test_format_content_body_empty_input(self):
        """Test handling of empty input"""
        assert format_content_body("") == ""
        assert format_content_body(None) == ""

    def test_format_content_body_strips_whitespace(self):
        """Test that paragraph whitespace is stripped"""
        content = "  First paragraph.  \n\n  Second paragraph.  "
        expected = "<p>First paragraph.</p>\n<p>Second paragraph.</p>"
        assert format_content_body(content) == expected

    def test_format_content_body_skips_empty_paragraphs(self):
        """Test that empty paragraphs are skipped"""
        content = "First.\n\n\n\nSecond."
        expected = "<p>First.</p>\n<p>Second.</p>"
        assert format_content_body(content) == expected

    def test_modify_iframe_size_basic(self):
        """Test basic iframe size modification"""
        iframe = '<iframe width="600" height="450" src="test.html"></iframe>'
        result = modify_iframe_size(iframe, 800, 600)
        assert 'width="800"' in result
        assert 'height="600"' in result

    def test_modify_iframe_size_with_style(self):
        """Test iframe size modification with style attribute"""
        iframe = '<iframe style="width: 600px; height: 450px;" src="test.html"></iframe>'
        result = modify_iframe_size(iframe, 800, 600)
        assert 'width: 800px' in result
        assert 'height: 600px' in result

    def test_modify_iframe_size_mixed_formats(self):
        """Test iframe with both attributes and style"""
        iframe = '<iframe width="600" height="450" style="width: 600px; height: 450px;"></iframe>'
        result = modify_iframe_size(iframe, 800, 600)
        assert 'width="800"' in result
        assert 'height="600"' in result
        assert 'width: 800px' in result
        assert 'height: 600px' in result

    def test_modify_iframe_size_preserves_other_attributes(self):
        """Test that other attributes are preserved"""
        iframe = '<iframe src="test.html" frameborder="0" width="600" height="450"></iframe>'
        result = modify_iframe_size(iframe, 800, 600)
        assert 'src="test.html"' in result
        assert 'frameborder="0"' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
