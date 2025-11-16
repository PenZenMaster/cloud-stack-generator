"""
Unit tests for Template Preview Generator
Path: E:/projects/cloud-stack-generator/tests/unit/test_template_preview.py

Description:
Comprehensive unit tests for the template preview generation system,
covering HTML preview generation, thumbnails, and comparison views.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Initial test suite for template preview generator
"""

import pytest
import tempfile
import json
import base64
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.templates.template_preview import TemplatePreviewGenerator
from core.templates.template_manager import TemplateManager, TemplateMetadata, TemplateType, TemplateVariant


class TestTemplatePreviewGenerator:
    """Tests for TemplatePreviewGenerator class"""

    @pytest.fixture
    def temp_templates_dir(self):
        """Create temporary directory structure for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir) / "templates"
            pages_dir = templates_dir / "pages"
            components_dir = templates_dir / "components"

            pages_dir.mkdir(parents=True)
            components_dir.mkdir(parents=True)

            # Create sample template
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

            template_file = pages_dir / "test_template.html"
            template_file.write_text(template_content)

            # Create template metadata
            metadata = {
                'id': 'test_template',
                'name': 'Test Template',
                'description': 'A test template for preview generation',
                'type': 'city_page',
                'variant': 'basic',
                'version': '1.0.0',
                'author': 'Test Author',
                'created_date': '2025-09-22',
                'last_modified': '2025-09-22',
                'preview_image': 'previews/test_template.png',
                'template_file': 'test_template.html',
                'required_data': ['page_title', 'heading'],
                'optional_data': ['meta_description', 'content'],
                'features': ['Responsive design', 'SEO optimized'],
                'compatibility': {'min_version': '1.0.0'}
            }

            metadata_file = pages_dir / "test_template.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))

            # Create header component
            header_content = """
<header>
    <div class="header-content">
        <h1>{{ business_name }}</h1>
        <nav>Navigation here</nav>
    </div>
</header>
            """.strip()

            header_file = components_dir / "header.html"
            header_file.write_text(header_content)

            # Create footer component
            footer_content = """
<footer>
    <div class="footer-content">
        <p>&copy; {{ current_year }} {{ business_name }}</p>
    </div>
</footer>
            """.strip()

            footer_file = components_dir / "footer.html"
            footer_file.write_text(footer_content)

            yield templates_dir

    @pytest.fixture
    def template_manager(self, temp_templates_dir):
        """Create TemplateManager instance"""
        return TemplateManager(temp_templates_dir)

    @pytest.fixture
    def preview_generator(self, template_manager):
        """Create TemplatePreviewGenerator instance"""
        return TemplatePreviewGenerator(template_manager)

    def test_init(self, template_manager):
        """Test TemplatePreviewGenerator initialization"""
        generator = TemplatePreviewGenerator(template_manager)

        assert generator.template_manager == template_manager

    def test_generate_preview_html_success(self, preview_generator):
        """Test successfully generating preview HTML"""
        preview_html = preview_generator.generate_preview_html('test_template')

        assert preview_html is not None
        assert isinstance(preview_html, str)
        assert len(preview_html) > 0

        # Should contain preview enhancements
        assert 'template-preview-overlay' in preview_html
        assert 'Template Preview' in preview_html
        assert 'Test Template' in preview_html

    def test_generate_preview_html_with_custom_data(self, preview_generator):
        """Test generating preview with custom data"""
        custom_data = {
            'page_title': 'Custom Title',
            'heading': 'Custom Heading',
            'content': 'Custom content for testing',
            'business_name': 'Custom Business'
        }

        preview_html = preview_generator.generate_preview_html('test_template', custom_data)

        assert preview_html is not None
        assert 'Custom Title' in preview_html
        assert 'Custom Heading' in preview_html
        assert 'Custom content for testing' in preview_html
        assert 'Custom Business' in preview_html

    def test_generate_preview_html_nonexistent_template(self, preview_generator):
        """Test generating preview for nonexistent template"""
        preview_html = preview_generator.generate_preview_html('nonexistent_template')

        assert preview_html is None

    def test_generate_preview_html_includes_components(self, preview_generator):
        """Test that preview includes component templates"""
        preview_html = preview_generator.generate_preview_html('test_template')

        assert preview_html is not None
        # Should include header content
        assert 'header-content' in preview_html or 'Navigation here' in preview_html
        # Should include footer content
        assert 'footer-content' in preview_html or '&copy;' in preview_html

    def test_get_preview_enhancements(self, preview_generator):
        """Test preview enhancement data"""
        enhancements = preview_generator._get_preview_enhancements()

        assert isinstance(enhancements, dict)
        assert 'preview_mode' in enhancements
        assert enhancements['preview_mode'] is True
        assert 'page_url' in enhancements
        assert 'current_year' in enhancements
        assert 'timestamp' in enhancements

    def test_enhance_preview_html(self, preview_generator):
        """Test HTML enhancement for preview"""
        base_html = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<body><h1>Content</h1></body>
</html>
        """.strip()

        enhanced_html = preview_generator._enhance_preview_html(base_html, 'test_template')

        assert enhanced_html != base_html
        assert 'template-preview-overlay' in enhanced_html
        assert 'Template Preview' in enhanced_html
        assert 'Test Template' in enhanced_html

    def test_enhance_preview_html_no_head_tag(self, preview_generator):
        """Test HTML enhancement when no head tag exists"""
        base_html = """
<html>
<body><h1>Content</h1></body>
</html>
        """.strip()

        enhanced_html = preview_generator._enhance_preview_html(base_html, 'test_template')

        assert enhanced_html != base_html
        assert 'template-preview-overlay' in enhanced_html
        # CSS should still be injected

    def test_enhance_preview_html_no_body_tag(self, preview_generator):
        """Test HTML enhancement when no body tag exists"""
        base_html = """
<!DOCTYPE html>
<html>
<head><title>Test</title></head>
<h1>Content without body tag</h1>
        """.strip()

        enhanced_html = preview_generator._enhance_preview_html(base_html, 'test_template')

        assert enhanced_html != base_html
        assert 'template-preview-overlay' in enhanced_html
        # Overlay should still be added

    def test_generate_preview_thumbnail_success(self, preview_generator):
        """Test generating preview thumbnail"""
        thumbnail_data = preview_generator.generate_preview_thumbnail('test_template')

        assert thumbnail_data is not None
        assert isinstance(thumbnail_data, str)
        assert thumbnail_data.startswith('data:image/svg+xml;base64,')

        # Decode and verify it's valid base64
        try:
            base64_data = thumbnail_data.split(',')[1]
            decoded = base64.b64decode(base64_data)
            svg_content = decoded.decode('utf-8')
            assert '<svg' in svg_content
            assert 'Test Template' in svg_content
        except Exception as e:
            pytest.fail(f"Failed to decode thumbnail: {e}")

    def test_generate_preview_thumbnail_custom_size(self, preview_generator):
        """Test generating thumbnail with custom dimensions"""
        thumbnail_data = preview_generator.generate_preview_thumbnail(
            'test_template',
            width=800,
            height=600
        )

        assert thumbnail_data is not None

        # Decode and check dimensions
        base64_data = thumbnail_data.split(',')[1]
        decoded = base64.b64decode(base64_data)
        svg_content = decoded.decode('utf-8')

        assert 'width="800"' in svg_content
        assert 'height="600"' in svg_content

    def test_generate_preview_thumbnail_nonexistent_template(self, preview_generator):
        """Test generating thumbnail for nonexistent template"""
        thumbnail_data = preview_generator.generate_preview_thumbnail('nonexistent_template')

        assert thumbnail_data is None

    def test_create_thumbnail_html(self, preview_generator):
        """Test creating HTML for thumbnail generation"""
        thumbnail_html = preview_generator._create_thumbnail_html('test_template', 400, 300)

        assert isinstance(thumbnail_html, str)
        assert len(thumbnail_html) > 0
        assert 'Test Template' in thumbnail_html
        assert 'width: 400px' in thumbnail_html
        assert 'height: 300px' in thumbnail_html

    def test_create_placeholder_thumbnail(self, preview_generator):
        """Test creating placeholder thumbnail"""
        placeholder_data = preview_generator._create_placeholder_thumbnail('test_template', 400, 300)

        assert isinstance(placeholder_data, str)
        assert placeholder_data.startswith('data:image/svg+xml;base64,')

        # Decode and verify content
        base64_data = placeholder_data.split(',')[1]
        decoded = base64.b64decode(base64_data)
        svg_content = decoded.decode('utf-8')

        assert '<svg' in svg_content
        assert 'width="400"' in svg_content
        assert 'height="300"' in svg_content
        assert 'Test Template' in svg_content

    def test_save_preview_to_file_success(self, preview_generator, temp_templates_dir):
        """Test saving preview HTML to file"""
        output_path = temp_templates_dir / "output" / "preview.html"

        success = preview_generator.save_preview_to_file('test_template', output_path)

        assert success is True
        assert output_path.exists()

        # Verify content
        content = output_path.read_text(encoding='utf-8')
        assert len(content) > 0
        assert 'template-preview-overlay' in content

    def test_save_preview_to_file_with_custom_data(self, preview_generator, temp_templates_dir):
        """Test saving preview with custom data"""
        custom_data = {
            'page_title': 'Saved Preview Title',
            'heading': 'Saved Preview Heading'
        }

        output_path = temp_templates_dir / "output" / "custom_preview.html"

        success = preview_generator.save_preview_to_file(
            'test_template',
            output_path,
            custom_data
        )

        assert success is True
        assert output_path.exists()

        content = output_path.read_text(encoding='utf-8')
        assert 'Saved Preview Title' in content
        assert 'Saved Preview Heading' in content

    def test_save_preview_to_file_nonexistent_template(self, preview_generator, temp_templates_dir):
        """Test saving preview for nonexistent template"""
        output_path = temp_templates_dir / "output" / "fail_preview.html"

        success = preview_generator.save_preview_to_file('nonexistent_template', output_path)

        assert success is False
        assert not output_path.exists()

    def test_save_preview_to_file_creates_directory(self, preview_generator, temp_templates_dir):
        """Test that save_preview creates output directory if it doesn't exist"""
        output_path = temp_templates_dir / "new_dir" / "nested" / "preview.html"

        success = preview_generator.save_preview_to_file('test_template', output_path)

        assert success is True
        assert output_path.exists()
        assert output_path.parent.exists()

    @patch('builtins.open', side_effect=PermissionError("Access denied"))
    def test_save_preview_to_file_permission_error(self, mock_open, preview_generator, temp_templates_dir):
        """Test handling permission errors when saving preview"""
        output_path = temp_templates_dir / "output" / "permission_test.html"

        success = preview_generator.save_preview_to_file('test_template', output_path)

        assert success is False

    def test_get_template_comparison_html_success(self, preview_generator):
        """Test generating template comparison HTML"""
        template_ids = ['test_template']

        comparison_html = preview_generator.get_template_comparison_html(template_ids)

        assert comparison_html is not None
        assert isinstance(comparison_html, str)
        assert 'Template Comparison' in comparison_html
        assert 'Test Template' in comparison_html
        assert 'comparison-container' in comparison_html

    def test_get_template_comparison_html_multiple_templates(self, preview_generator, temp_templates_dir):
        """Test comparison with multiple templates"""
        # Create second template
        template2_content = """
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body><h1>Second Template</h1></body>
</html>
        """.strip()

        template2_file = temp_templates_dir / "pages" / "test_template2.html"
        template2_file.write_text(template2_content)

        metadata2 = {
            'id': 'test_template2',
            'name': 'Second Test Template',
            'type': 'landing_page',
            'variant': 'enhanced'
        }

        metadata2_file = temp_templates_dir / "pages" / "test_template2.json"
        metadata2_file.write_text(json.dumps(metadata2))

        # Recreate template manager to pick up new template
        template_manager = TemplateManager(temp_templates_dir)
        preview_generator = TemplatePreviewGenerator(template_manager)

        template_ids = ['test_template', 'test_template2']

        comparison_html = preview_generator.get_template_comparison_html(template_ids)

        assert comparison_html is not None
        assert 'Test Template' in comparison_html
        assert 'Second Test Template' in comparison_html
        assert comparison_html.count('template-preview-frame') >= 2

    def test_get_template_comparison_html_empty_list(self, preview_generator):
        """Test comparison with empty template list"""
        comparison_html = preview_generator.get_template_comparison_html([])

        assert comparison_html is None

    def test_get_template_comparison_html_nonexistent_template(self, preview_generator):
        """Test comparison including nonexistent template"""
        template_ids = ['test_template', 'nonexistent_template']

        comparison_html = preview_generator.get_template_comparison_html(template_ids)

        assert comparison_html is not None
        # Should include the valid template and skip the invalid one
        assert 'Test Template' in comparison_html

    def test_comparison_html_iframe_embedding(self, preview_generator):
        """Test that comparison HTML properly embeds templates in iframes"""
        template_ids = ['test_template']

        comparison_html = preview_generator.get_template_comparison_html(template_ids)

        assert comparison_html is not None
        assert 'iframe' in comparison_html
        assert 'data:text/html;base64,' in comparison_html

        # Verify base64 encoded content
        import re
        iframe_pattern = r'src="data:text/html;base64,([^"]+)"'
        matches = re.findall(iframe_pattern, comparison_html)

        assert len(matches) >= 1

        # Decode first match
        encoded_content = matches[0]
        try:
            decoded_content = base64.b64decode(encoded_content).decode('utf-8')
            assert len(decoded_content) > 0
            # Should be the template preview HTML
            assert 'template-preview-overlay' in decoded_content
        except Exception as e:
            pytest.fail(f"Failed to decode iframe content: {e}")

    @patch('core.templates.template_preview.tempfile.NamedTemporaryFile')
    def test_preview_temp_file_handling(self, mock_tempfile, preview_generator):
        """Test temporary file handling in preview generation"""
        # Mock temporary file
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_preview.html"
        mock_tempfile.return_value.__enter__.return_value = mock_file

        preview_html = preview_generator.generate_preview_html('test_template')

        # Should still generate preview HTML even if temp file creation is mocked
        assert preview_html is not None

    def test_preview_error_handling(self, preview_generator):
        """Test error handling in preview generation"""
        # Test with template that has rendering errors
        with patch.object(preview_generator.template_manager, 'load_template') as mock_load:
            # Mock template that raises an exception during rendering
            mock_template = MagicMock()
            mock_template.render.side_effect = Exception("Template rendering error")
            mock_load.return_value = mock_template

            preview_html = preview_generator.generate_preview_html('test_template')

            assert preview_html is None

    def test_preview_with_missing_components(self, preview_generator, temp_templates_dir):
        """Test preview generation when component files are missing"""
        # Remove component files
        header_file = temp_templates_dir / "components" / "header.html"
        footer_file = temp_templates_dir / "components" / "footer.html"

        if header_file.exists():
            header_file.unlink()
        if footer_file.exists():
            footer_file.unlink()

        # Should still generate preview, possibly with include errors
        preview_html = preview_generator.generate_preview_html('test_template')

        # Depending on implementation, might return None or partial HTML
        # The important thing is it doesn't crash
        assert preview_html is None or isinstance(preview_html, str)

    def test_preview_data_sanitization(self, preview_generator):
        """Test that preview data is properly sanitized"""
        custom_data = {
            'page_title': '<script>alert("xss")</script>Test Title',
            'heading': 'Safe Heading',
            'content': '<img src="x" onerror="alert(\'xss\')">'
        }

        preview_html = preview_generator.generate_preview_html('test_template', custom_data)

        assert preview_html is not None
        # Jinja2 should escape HTML by default
        assert '<script>' not in preview_html
        assert 'onerror=' not in preview_html

    def test_preview_performance_timing(self, preview_generator):
        """Test preview generation performance"""
        import time

        start_time = time.time()
        preview_html = preview_generator.generate_preview_html('test_template')
        end_time = time.time()

        generation_time = end_time - start_time

        assert preview_html is not None
        # Should complete reasonably quickly (adjust threshold as needed)
        assert generation_time < 5.0  # 5 seconds max

    def test_memory_usage_large_templates(self, preview_generator, temp_templates_dir):
        """Test memory handling with large template content"""
        # Create a template with substantial content
        large_content = """
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body>
        """ + "<!-- Large content block -->\n" * 1000 + """
<h1>{{ heading }}</h1>
</body>
</html>
        """

        large_template_file = temp_templates_dir / "pages" / "large_template.html"
        large_template_file.write_text(large_content)

        metadata = {
            'id': 'large_template',
            'name': 'Large Template',
            'type': 'city_page',
            'variant': 'basic',
            'template_file': 'large_template.html'
        }

        metadata_file = temp_templates_dir / "pages" / "large_template.json"
        metadata_file.write_text(json.dumps(metadata))

        # Recreate components to include large template
        template_manager = TemplateManager(temp_templates_dir)
        preview_generator = TemplatePreviewGenerator(template_manager)

        # Should handle large content without issues
        preview_html = preview_generator.generate_preview_html('large_template')

        assert preview_html is not None
        assert len(preview_html) > len(large_content)  # Should be larger due to enhancements


class TestTemplatePreviewIntegration:
    """Integration tests for TemplatePreviewGenerator"""

    def test_full_preview_workflow(self):
        """Test complete preview generation workflow"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup complete template structure
            templates_dir = Path(temp_dir) / "templates"
            pages_dir = templates_dir / "pages"
            components_dir = templates_dir / "components"

            pages_dir.mkdir(parents=True)
            components_dir.mkdir(parents=True)

            # Create realistic template
            template_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }}</title>
    <meta name="description" content="{{ meta_description }}">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        header { background: #333; color: white; padding: 20px; }
        main { padding: 20px 0; }
        footer { background: #f5f5f5; padding: 20px; text-align: center; }
    </style>
</head>
<body>
    {% include 'components/header.html' %}
    <div class="container">
        <main>
            <h1>{{ heading }}</h1>
            <p>{{ content }}</p>
            {% if services %}
            <section>
                <h2>Services</h2>
                <ul>
                    {% for service in services %}
                    <li>{{ service }}</li>
                    {% endfor %}
                </ul>
            </section>
            {% endif %}
        </main>
    </div>
    {% include 'components/footer.html' %}
</body>
</html>
            """.strip()

            template_file = pages_dir / "integration_template.html"
            template_file.write_text(template_content)

            # Create metadata
            metadata = {
                'id': 'integration_template',
                'name': 'Integration Test Template',
                'description': 'Full workflow integration test',
                'type': 'city_page',
                'variant': 'enhanced',
                'version': '1.0.0',
                'template_file': 'integration_template.html',
                'required_data': ['page_title', 'heading'],
                'optional_data': ['meta_description', 'content', 'services'],
                'features': ['Responsive', 'SEO', 'Components']
            }

            metadata_file = pages_dir / "integration_template.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))

            # Create components
            header_content = """
<header>
    <div class="container">
        <h1>{{ business_name | default('Sample Business') }}</h1>
        <nav>
            <a href="#home">Home</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
        </nav>
    </div>
</header>
            """.strip()

            footer_content = """
<footer>
    <div class="container">
        <p>&copy; {{ current_year | default('2025') }} {{ business_name | default('Sample Business') }}. All rights reserved.</p>
    </div>
</footer>
            """.strip()

            header_file = components_dir / "header.html"
            header_file.write_text(header_content)

            footer_file = components_dir / "footer.html"
            footer_file.write_text(footer_content)

            # Test workflow
            template_manager = TemplateManager(templates_dir)
            preview_generator = TemplatePreviewGenerator(template_manager)

            # 1. Generate preview with default data
            preview_html = preview_generator.generate_preview_html('integration_template')
            assert preview_html is not None
            assert 'Integration Test Template' in preview_html
            assert 'template-preview-overlay' in preview_html

            # 2. Generate preview with custom data
            custom_data = {
                'page_title': 'Custom Integration Test',
                'heading': 'Welcome to Integration Testing',
                'content': 'This is a comprehensive integration test.',
                'services': ['Web Design', 'SEO', 'Marketing'],
                'business_name': 'Test Business Inc'
            }

            custom_preview = preview_generator.generate_preview_html('integration_template', custom_data)
            assert custom_preview is not None
            assert 'Custom Integration Test' in custom_preview
            assert 'Welcome to Integration Testing' in custom_preview
            assert 'Web Design' in custom_preview
            assert 'Test Business Inc' in custom_preview

            # 3. Generate thumbnail
            thumbnail = preview_generator.generate_preview_thumbnail('integration_template')
            assert thumbnail is not None
            assert thumbnail.startswith('data:image/svg+xml;base64,')

            # 4. Save preview to file
            output_path = Path(temp_dir) / "integration_preview.html"
            save_success = preview_generator.save_preview_to_file('integration_template', output_path)
            assert save_success is True
            assert output_path.exists()

            saved_content = output_path.read_text(encoding='utf-8')
            assert len(saved_content) > 0
            assert 'Integration Test Template' in saved_content

            # 5. Generate comparison view
            comparison_html = preview_generator.get_template_comparison_html(['integration_template'])
            assert comparison_html is not None
            assert 'Template Comparison' in comparison_html
            assert 'Integration Test Template' in comparison_html


if __name__ == '__main__':
    pytest.main([__file__])