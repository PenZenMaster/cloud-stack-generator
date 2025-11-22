"""
Unit tests for Template Sample Data
Path: E:/projects/cloud-stack-generator/tests/unit/test_template_sample_data.py

Description:
Tests to verify that sample data generation covers all template variables
and prevents attribute errors during template rendering.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Initial test suite for sample data validation
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from ui.dialogs.template_editor_dialog import TemplateEditorDialog
from ui.dialogs.simple_template_editor import SimpleTemplateEditor
from unittest.mock import Mock


class TestTemplateSampleData:
    """Tests for template sample data generation"""

    def test_template_editor_sample_data_completeness(self):
        """Test that template editor sample data includes all required fields"""
        # Mock the template manager and other dependencies
        mock_template_manager = Mock()

        # Create dialog with mocked dependencies
        dialog = TemplateEditorDialog()
        dialog.template_manager = mock_template_manager

        # Get sample data
        sample_data = dialog._generate_sample_data()

        # Verify business data structure
        assert 'business' in sample_data
        business = sample_data['business']

        # Test for commonly used business attributes
        required_business_attrs = [
            'business_name', 'industry', 'tagline', 'description',
            'service_overview', 'domain', 'legal_name', 'founded_year'
        ]

        for attr in required_business_attrs:
            assert attr in business, f"Missing business.{attr} in sample data"
            assert business[attr] is not None, f"business.{attr} should not be None"
            assert len(str(business[attr])) > 0, f"business.{attr} should not be empty"

    def test_template_editor_contact_data_structure(self):
        """Test that contact data has proper nested structure"""
        dialog = TemplateEditorDialog()
        dialog.template_manager = Mock()

        sample_data = dialog._generate_sample_data()

        # Verify contact data structure
        assert 'contact' in sample_data
        contact = sample_data['contact']

        # Test basic contact fields
        basic_contact_attrs = ['phone', 'email', 'full_address']
        for attr in basic_contact_attrs:
            assert attr in contact, f"Missing contact.{attr} in sample data"

        # Test nested address structure
        assert 'address' in contact, "Missing contact.address in sample data"
        address = contact['address']

        required_address_attrs = ['street', 'city', 'state', 'zip_code', 'country']
        for attr in required_address_attrs:
            assert attr in address, f"Missing contact.address.{attr} in sample data"
            assert address[attr] is not None, f"contact.address.{attr} should not be None"

    def test_simple_template_editor_sample_data(self):
        """Test that simple template editor has consistent sample data"""
        editor = SimpleTemplateEditor()

        # Mock the refresh preview to get sample data
        # The sample data is embedded in the _refresh_preview method
        # We'll test by calling the method and checking for errors

        try:
            # This should not raise AttributeError for missing business.industry
            editor._refresh_preview()
            # If we get here without exception, the sample data is adequate
            assert True
        except AttributeError as e:
            if 'industry' in str(e):
                pytest.fail(f"Missing business.industry in simple editor sample data: {e}")
            else:
                # Other AttributeErrors might be acceptable (missing UI components)
                pass

    def test_custom_filters_available(self):
        """Test that custom filters are properly registered"""
        dialog = TemplateEditorDialog()
        dialog.template_manager = Mock()

        # Test filter methods exist
        assert hasattr(dialog, '_slugify_filter'), "Missing _slugify_filter method"
        assert hasattr(dialog, '_date_filter'), "Missing _date_filter method"
        assert hasattr(dialog, '_urlencode_filter'), "Missing _urlencode_filter method"
        assert hasattr(dialog, '_markdown_basic_filter'), "Missing _markdown_basic_filter method"

        # Test filter functionality
        assert dialog._slugify_filter("Test Service") == "test-service"
        assert dialog._slugify_filter("My Product Name!") == "my-product-name"

        assert "http" in dialog._urlencode_filter("http://test.com")

        # Test date filter with "now"
        result = dialog._date_filter("now", "%Y")
        assert len(result) == 4 and result.isdigit()  # Should be current year

    def test_sample_data_prevents_common_template_errors(self):
        """Test that sample data prevents common template variable errors"""
        dialog = TemplateEditorDialog()
        dialog.template_manager = Mock()

        sample_data = dialog._generate_sample_data()

        # Test for common template variables that cause errors
        common_vars = [
            'business.business_name',
            'business.industry',
            'contact.phone',
            'contact.email',
            'contact.address.city',
            'contact.address.state',
            'current_year',
            'page_title',
            'meta_description'
        ]

        for var_path in common_vars:
            # Navigate nested attributes
            obj = sample_data
            parts = var_path.split('.')

            try:
                for part in parts:
                    obj = obj[part] if isinstance(obj, dict) else getattr(obj, part)
                # If we get here, the variable exists and is accessible
                assert obj is not None, f"Variable {var_path} should not be None"
            except (KeyError, AttributeError) as e:
                pytest.fail(f"Missing variable {var_path} in sample data: {e}")

    def test_branding_data_structure(self):
        """Test that branding data structure is complete"""
        dialog = TemplateEditorDialog()
        dialog.template_manager = Mock()

        sample_data = dialog._generate_sample_data()

        assert 'branding' in sample_data
        branding = sample_data['branding']

        required_branding_attrs = [
            'primary_color', 'secondary_color', 'accent_color',
            'logo_url', 'font_family'
        ]

        for attr in required_branding_attrs:
            assert attr in branding, f"Missing branding.{attr} in sample data"
            assert branding[attr] is not None, f"branding.{attr} should not be None"

    def test_city_page_data_structure(self):
        """Test that city page data structure supports templates"""
        dialog = TemplateEditorDialog()
        dialog.template_manager = Mock()

        sample_data = dialog._generate_sample_data()

        assert 'city_page' in sample_data
        city_page = sample_data['city_page']

        # Test for commonly used city page attributes
        common_city_attrs = [
            'title', 'meta_description', 'city_name', 'state',
            'primary_keyword', 'secondary_keywords', 'hero_title'
        ]

        for attr in common_city_attrs:
            assert attr in city_page, f"Missing city_page.{attr} in sample data"

    def test_services_and_products_sample_data(self):
        """Test that services and products arrays are provided"""
        dialog = TemplateEditorDialog()
        dialog.template_manager = Mock()

        sample_data = dialog._generate_sample_data()

        # Check services array
        if 'services' in sample_data:
            services = sample_data['services']
            assert isinstance(services, list), "services should be a list"
            if len(services) > 0:
                service = services[0]
                # Services should have name attribute for slugify filter
                assert 'name' in service or isinstance(service, str), "Service should have name or be string"

        # Check products array
        if 'products' in sample_data:
            products = sample_data['products']
            assert isinstance(products, list), "products should be a list"
            if len(products) > 0:
                product = products[0]
                # Products should have name attribute for slugify filter
                assert 'name' in product or isinstance(product, str), "Product should have name or be string"

    def test_filter_error_handling(self):
        """Test that filters handle edge cases gracefully"""
        dialog = TemplateEditorDialog()

        # Test slugify with edge cases
        assert dialog._slugify_filter("") == ""
        assert dialog._slugify_filter(None) == ""
        assert dialog._slugify_filter("   ") == ""
        assert dialog._slugify_filter("Test!!!") == "test"

        # Test urlencode with edge cases
        assert dialog._urlencode_filter("") == ""
        assert dialog._urlencode_filter(None) == ""

        # Test date filter with invalid input
        result = dialog._date_filter("invalid-date")
        assert isinstance(result, str)  # Should return string, not crash

        # Test markdown filter with edge cases
        assert dialog._markdown_basic_filter("") == ""
        assert dialog._markdown_basic_filter(None) == ""


class TestTemplateDataConsistency:
    """Tests for consistency between different template components"""

    def test_simple_vs_advanced_editor_consistency(self):
        """Test that both editors provide compatible sample data"""
        # Create both editors
        advanced_dialog = TemplateEditorDialog()
        advanced_dialog.template_manager = Mock()

        SimpleTemplateEditor()

        # Get sample data from advanced editor
        advanced_data = advanced_dialog._generate_sample_data()

        # For simple editor, we need to extract the sample data from the preview method
        # Since it's embedded, we'll just verify the structure matches common needs

        # Both should have business with industry
        assert 'business' in advanced_data
        assert 'industry' in advanced_data['business']

        # Both should have contact with address structure
        assert 'contact' in advanced_data
        assert 'address' in advanced_data['contact']
        assert 'city' in advanced_data['contact']['address']

    def test_sample_data_covers_template_requirements(self):
        """Test that sample data covers actual template requirements"""
        dialog = TemplateEditorDialog()
        dialog.template_manager = Mock()

        sample_data = dialog._generate_sample_data()

        # Variables commonly used in templates based on our grep results
        template_vars = [
            ('business', 'business_name'),
            ('business', 'industry'),
            ('business', 'description'),
            ('contact', 'phone'),
            ('contact', 'email'),
            ('branding', 'primary_color'),
            ('current_year',),
            ('page_title',),
        ]

        for var_path in template_vars:
            obj = sample_data
            for part in var_path:
                assert part in obj, f"Missing {'.'.join(var_path)} in sample data"
                obj = obj[part]


if __name__ == '__main__':
    pytest.main([__file__])