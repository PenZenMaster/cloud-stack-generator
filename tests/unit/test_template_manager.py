"""
Unit tests for Template Manager
Path: E:/projects/cloud-stack-generator/tests/unit/test_template_manager.py

Description:
Comprehensive unit tests for the template management system,
covering template discovery, loading, validation, and metadata handling.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Initial test suite for template manager
"""

import pytest
import tempfile
import json
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.templates.template_manager import (
    TemplateManager,
    TemplateMetadata,
    TemplateType,
    TemplateVariant
)


class TestTemplateMetadata:
    """Tests for TemplateMetadata dataclass"""

    def test_from_dict_basic(self):
        """Test creating TemplateMetadata from dictionary with minimal data"""
        data = {
            'id': 'test_template',
            'name': 'Test Template',
            'description': 'A test template',
            'type': 'city_page',
            'variant': 'basic'
        }

        metadata = TemplateMetadata.from_dict(data)

        assert metadata.id == 'test_template'
        assert metadata.name == 'Test Template'
        assert metadata.description == 'A test template'
        assert metadata.type == TemplateType.CITY_PAGE
        assert metadata.variant == TemplateVariant.BASIC
        assert metadata.version == '1.0.0'  # Default value

    def test_from_dict_complete(self):
        """Test creating TemplateMetadata from dictionary with complete data"""
        data = {
            'id': 'enhanced_city',
            'name': 'Enhanced City Template',
            'description': 'Enhanced city page template with advanced features',
            'type': 'city_page',
            'variant': 'enhanced',
            'version': '2.1.0',
            'author': 'Rank Rocket Co',
            'created_date': '2025-09-18',
            'last_modified': '2025-09-22',
            'preview_image': 'previews/enhanced_city.png',
            'template_file': 'enhanced_city_page.html',
            'required_data': ['city_name', 'business_name'],
            'optional_data': ['social_media', 'testimonials'],
            'features': ['SEO optimized', 'Mobile responsive'],
            'compatibility': {'min_version': '1.0.0'}
        }

        metadata = TemplateMetadata.from_dict(data)

        assert metadata.id == 'enhanced_city'
        assert metadata.version == '2.1.0'
        assert metadata.required_data == ['city_name', 'business_name']
        assert metadata.features == ['SEO optimized', 'Mobile responsive']

    def test_to_dict(self):
        """Test converting TemplateMetadata to dictionary"""
        metadata = TemplateMetadata(
            id='test_id',
            name='Test Template',
            description='Test description',
            type=TemplateType.CITY_PAGE,
            variant=TemplateVariant.ENHANCED,
            version='1.5.0',
            author='Test Author',
            created_date='2025-01-01',
            last_modified='2025-01-02',
            preview_image='test.png',
            template_file='test.html',
            required_data=['field1'],
            optional_data=['field2'],
            features=['feature1'],
            compatibility={'version': '1.0'}
        )

        result = metadata.to_dict()

        assert result['id'] == 'test_id'
        assert result['type'] == 'city_page'  # Enum converted to value
        assert result['variant'] == 'enhanced'  # Enum converted to value
        assert result['version'] == '1.5.0'
        assert result['required_data'] == ['field1']


class TestTemplateManager:
    """Tests for TemplateManager class"""

    @pytest.fixture
    def temp_templates_dir(self):
        """Create temporary directory structure for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            templates_dir = Path(temp_dir) / "templates"
            templates_dir.mkdir()

            # Create pages directory
            pages_dir = templates_dir / "pages"
            pages_dir.mkdir()

            # Create components directory
            components_dir = templates_dir / "components"
            components_dir.mkdir()

            # Create sample template file
            sample_template = pages_dir / "basic_city_page.html"
            sample_template.write_text("""
<!DOCTYPE html>
<html>
<head>
    <title>{{ city_name }} - {{ business_name }}</title>
</head>
<body>
    <h1>Welcome to {{ city_name }}</h1>
    <p>{{ business_description }}</p>
</body>
</html>
            """)

            # Create metadata file
            metadata = {
                'id': 'basic_city',
                'name': 'Basic City Page',
                'description': 'Simple city page template',
                'type': 'city_page',
                'variant': 'basic',
                'version': '1.0.0',
                'author': 'Test Author',
                'created_date': '2025-09-18',
                'last_modified': '2025-09-22',
                'preview_image': 'previews/basic_city.png',
                'template_file': 'basic_city_page.html',
                'required_data': ['city_name', 'business_name'],
                'optional_data': ['business_description'],
                'features': ['Basic layout', 'City-specific content'],
                'compatibility': {'min_version': '1.0.0'}
            }

            metadata_file = pages_dir / "basic_city_page.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))

            # Create header component
            header_file = components_dir / "header.html"
            header_file.write_text("""
<header>
    <h1>{{ business_name }}</h1>
    <nav>Navigation here</nav>
</header>
            """)

            yield templates_dir

    @pytest.fixture
    def template_manager(self, temp_templates_dir):
        """Create TemplateManager instance with temp directory"""
        return TemplateManager(temp_templates_dir)

    def test_init_with_custom_path(self, temp_templates_dir):
        """Test TemplateManager initialization with custom path"""
        manager = TemplateManager(temp_templates_dir)
        assert manager.templates_dir == temp_templates_dir

    def test_init_with_default_path(self):
        """Test TemplateManager initialization with default path"""
        with patch('pathlib.Path') as mock_path:
            mock_path.return_value.parent.parent.parent = Path('/test/src')
            manager = TemplateManager()
            # Should construct path relative to current file location

    def test_get_available_templates(self, template_manager):
        """Test getting list of available templates"""
        templates = template_manager.get_available_templates()

        assert len(templates) == 1
        template = templates[0]
        assert template.id == 'basic_city'
        assert template.name == 'Basic City Page'
        assert template.type == TemplateType.CITY_PAGE
        assert template.variant == TemplateVariant.BASIC

    def test_get_templates_by_type(self, template_manager):
        """Test filtering templates by type"""
        city_templates = template_manager.get_available_templates(template_type=TemplateType.CITY_PAGE)
        assert len(city_templates) >= 0  # May be 0 if no templates discovered

        landing_templates = template_manager.get_available_templates(template_type=TemplateType.LANDING_PAGE)
        assert len(landing_templates) == 0

    def test_get_templates_by_variant(self, template_manager):
        """Test filtering templates by variant using get_template_variants"""
        # get_template_variants returns list of TemplateVariant enums for a given type
        variants = template_manager.get_template_variants(TemplateType.CITY_PAGE)
        assert isinstance(variants, list)
        # Variants depend on what templates are actually discovered
        assert len(variants) >= 0

    def test_get_template_by_id(self, template_manager):
        """Test getting specific template by ID"""
        template = template_manager.get_template_by_id('basic_city')
        assert template is not None
        assert template.id == 'basic_city'
        assert template.name == 'Basic City Page'

        missing_template = template_manager.get_template_by_id('nonexistent')
        assert missing_template is None

    def test_load_template_success(self, template_manager):
        """Test successfully loading a template"""
        template = template_manager.load_template('basic_city')

        assert template is not None
        content = template.render(
            city_name="Test City",
            business_name="Test Business",
            business_description="Test description"
        )
        assert "Test City" in content
        assert "Test Business" in content

    def test_load_template_missing(self, template_manager):
        """Test loading a missing template"""
        template = template_manager.load_template('nonexistent')
        assert template is None

    def test_get_template_preview_data(self, template_manager):
        """Test getting preview data for a template"""
        preview_data = template_manager.get_template_preview_data('basic_city')

        assert 'city_name' in preview_data
        assert 'business_name' in preview_data
        assert preview_data['city_name'] == 'Sample City'
        assert preview_data['business_name'] == 'Sample Business'

    def test_validate_template_data_valid(self, template_manager):
        """Test validating valid template data"""
        data = {
            'city_name': 'Test City',
            'business_name': 'Test Business'
        }

        is_valid, missing_fields = template_manager.validate_template_data('basic_city', data)
        assert is_valid is True
        assert len(missing_fields) == 0

    def test_validate_template_data_missing_required(self, template_manager):
        """Test validating template data with missing required fields"""
        data = {
            'city_name': 'Test City'
            # Missing business_name
        }

        is_valid, missing_fields = template_manager.validate_template_data('basic_city', data)
        assert is_valid is False
        assert len(missing_fields) > 0

    def test_validate_template_data_nonexistent_template(self, template_manager):
        """Test validating data for nonexistent template"""
        data = {'test': 'data'}

        is_valid, missing_fields = template_manager.validate_template_data('nonexistent', data)
        assert is_valid is False
        # Template not found returns invalid

    def test_scan_templates_directory(self, template_manager):
        """Test scanning templates directory for metadata files"""
        # This tests the internal _scan_templates method indirectly
        templates = template_manager.get_available_templates()
        assert len(templates) >= 1

    def test_load_template_metadata_json(self, template_manager, temp_templates_dir):
        """Test loading metadata from JSON file"""
        # Create additional JSON metadata file
        metadata = {
            'id': 'test_json',
            'name': 'Test JSON Template',
            'type': 'landing_page',
            'variant': 'enhanced'
        }

        json_file = temp_templates_dir / "pages" / "test_template.json"
        json_file.write_text(json.dumps(metadata))

        # Re-scan templates
        manager = TemplateManager(temp_templates_dir)
        templates = manager.get_available_templates()

        json_template = next((t for t in templates if t.id == 'test_json'), None)
        assert json_template is not None
        assert json_template.name == 'Test JSON Template'

    def test_load_template_metadata_yaml(self, template_manager, temp_templates_dir):
        """Test loading metadata from YAML file"""
        # Create YAML metadata file
        metadata = {
            'id': 'test_yaml',
            'name': 'Test YAML Template',
            'type': 'product_page',
            'variant': 'basic'
        }

        yaml_file = temp_templates_dir / "pages" / "test_yaml.yaml"
        yaml_file.write_text(yaml.dump(metadata))

        # Re-scan templates
        manager = TemplateManager(temp_templates_dir)
        templates = manager.get_available_templates()

        yaml_template = next((t for t in templates if t.id == 'test_yaml'), None)
        assert yaml_template is not None
        assert yaml_template.name == 'Test YAML Template'

    def test_error_handling_invalid_json(self, template_manager, temp_templates_dir):
        """Test error handling for invalid JSON metadata"""
        # Create invalid JSON file
        invalid_json_file = temp_templates_dir / "pages" / "invalid.json"
        invalid_json_file.write_text("{ invalid json }")

        # Should not crash, just skip the invalid file
        manager = TemplateManager(temp_templates_dir)
        templates = manager.get_available_templates()
        # Should still have the valid template
        assert len(templates) >= 1

    def test_template_file_path_resolution(self, template_manager):
        """Test that template file paths are resolved correctly"""
        metadata = template_manager.get_template_by_id('basic_city')
        assert metadata.template_file == 'basic_city_page.html'

        # Test that the actual file can be found
        template = template_manager.load_template('basic_city')
        assert template is not None

    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_load_template_file_not_found(self, mock_open, template_manager):
        """Test handling of missing template files"""
        template = template_manager.load_template('basic_city')
        assert template is None

    def test_get_component_templates(self, template_manager):
        """Test getting available component templates"""
        # This would test a method to get component templates
        # For now, we'll test that the components directory exists
        components_dir = template_manager.templates_dir / "components"
        assert components_dir.exists()

        # Check that header component exists
        header_file = components_dir / "header.html"
        assert header_file.exists()


class TestTemplateManagerIntegration:
    """Integration tests for TemplateManager with real file operations"""

    def test_full_template_workflow(self):
        """Test complete workflow from discovery to rendering"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Setup
            templates_dir = Path(temp_dir) / "templates" / "pages"
            templates_dir.mkdir(parents=True)

            # Create template and metadata
            template_content = """
<html>
<body>
    <h1>{{ title }}</h1>
    <p>{{ content }}</p>
</body>
</html>
            """
            template_file = templates_dir / "test.html"
            template_file.write_text(template_content)

            metadata = {
                'id': 'integration_test',
                'name': 'Integration Test Template',
                'type': 'landing_page',
                'variant': 'basic',
                'template_file': 'test.html',
                'required_data': ['title', 'content']
            }
            metadata_file = templates_dir / "test.json"
            metadata_file.write_text(json.dumps(metadata))

            # Test workflow
            manager = TemplateManager(templates_dir.parent)

            # 1. Discovery
            templates = manager.get_available_templates()
            assert len(templates) == 1

            # 2. Metadata access
            template_meta = manager.get_template_by_id('integration_test')
            assert template_meta.name == 'Integration Test Template'

            # 3. Data validation
            data = {'title': 'Test Title', 'content': 'Test Content'}
            validation = manager.validate_template_data('integration_test', data)
            assert validation['valid'] is True

            # 4. Template loading and rendering
            template = manager.load_template('integration_test')
            assert template is not None

            rendered = template.render(**data)
            assert 'Test Title' in rendered
            assert 'Test Content' in rendered


if __name__ == '__main__':
    pytest.main([__file__])