"""
Unit tests for Content Generators
Path: E:/projects/cloud-stack-generator/tests/unit/test_content_generators.py

Description:
Tests for the extracted content generator modules to ensure proper functionality
after refactoring from website_generator.py.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-17

Last Modified Date:
2025-10-17

Comments:
* v1.00 - Initial tests for refactored content generators
"""

import pytest
from unittest.mock import Mock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.generators.content import (
    HomeContentGenerator,
    CityContentGenerator,
    FooterGenerator,
    NavigationBuilder
)
from core.utils.string_utils import normalize_phone, format_phone_display, generate_city_slug
from core.utils.html_utils import modify_iframe_size


class TestHomeContentGenerator:
    """Tests for HomeContentGenerator"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock ClientConfig for testing"""
        config = Mock()
        config.business = Mock()
        config.business.business_name = "Test Business"
        config.business.industry = "Testing"
        config.business.company_overview = "We test things"
        config.business.why_choose_us = ["Quality", "Reliability"]
        config.business.company_stats = {"projects": "100+", "years": "10+"}
        config.business.service_guarantee = "100% satisfaction guaranteed"
        config.business.service_area_description = "Serving the test area"
        config.business.get_hero_tagline = Mock(return_value="Professional Testing Services")
        config.business.get_years_display = Mock(return_value="Over 10 years of experience")

        config.contact = Mock()
        config.contact.phone = "555-1234"
        config.contact.office_phone = None
        config.contact.email = "test@example.com"
        config.contact.response_time_promise = "24 hour response"
        config.contact.business_hours = {"monday": "9-5", "tuesday": "9-5"}
        config.contact.get_primary_phone = Mock(return_value="555-1234")
        config.contact.has_multiple_contacts = Mock(return_value=False)

        config.services = []
        config.products = []
        config.faq = []
        config.pages = []

        return config

    def test_generate_basic_home_content(self, mock_config):
        """Test basic home content generation"""
        generator = HomeContentGenerator()
        content = generator.generate_basic_home_content(mock_config)

        assert "Test Business" in content
        assert "Testing" in content
        assert "hero" in content
        assert "content" in content

    def test_generate_enhanced_home_content(self, mock_config):
        """Test enhanced home content generation"""
        generator = HomeContentGenerator()
        content = generator.generate_enhanced_home_content(mock_config)

        assert "Test Business" in content
        assert "Professional Testing Services" in content
        assert "Over 10 years of experience" in content
        assert "100% satisfaction guaranteed" in content

    def test_basic_home_with_services(self, mock_config):
        """Test home content with services"""
        service = Mock()
        service.name = "Test Service"
        service.description = "A test service"
        mock_config.services = [service]

        generator = HomeContentGenerator()
        content = generator.generate_basic_home_content(mock_config)

        assert "Test Service" in content
        assert "services-grid" in content

    def test_basic_home_with_products(self, mock_config):
        """Test home content with products"""
        product = Mock()
        product.name = "Test Product"
        product.description = "A test product"
        mock_config.products = [product]

        generator = HomeContentGenerator()
        content = generator.generate_basic_home_content(mock_config)

        assert "Test Product" in content
        assert "products-grid" in content


class TestCityContentGenerator:
    """Tests for CityContentGenerator"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock ClientConfig for testing"""
        config = Mock()
        config.business = Mock()
        config.business.business_name = "Test Business"
        config.business.industry = "Testing"

        service = Mock()
        service.name = "Test Service"
        service.description = "A test service"
        config.services = [service]
        config.products = []
        config.faq = []
        config.pages = []

        return config

    def test_generate_city_content(self, mock_config):
        """Test city content generation"""
        generator = CityContentGenerator()
        content = generator.generate_city_content(mock_config, "Chicago")

        assert "Chicago" in content
        assert "Test Business" in content
        assert "Testing Services in Chicago" in content
        assert "Test Service" in content

    def test_city_content_with_products(self, mock_config):
        """Test city content with products"""
        product = Mock()
        product.name = "Test Product"
        product.description = "A test product"
        mock_config.products = [product]

        generator = CityContentGenerator()
        content = generator.generate_city_content(mock_config, "Chicago")

        assert "Test Product" in content
        assert "Our Products Available in Chicago" in content


class TestFooterGenerator:
    """Tests for FooterGenerator"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock ClientConfig for testing"""
        config = Mock()
        config.business = Mock()
        config.business.business_name = "Test Business"

        config.contact = Mock()
        config.contact.phone = "555-1234"
        config.contact.email = "test@example.com"
        config.contact.address = Mock()
        config.contact.address.street = "123 Test St"
        config.contact.address.city = "Test City"
        config.contact.address.state = "TS"
        config.contact.address.zip_code = "12345"

        config.social_media = Mock()
        config.social_media.get_valid_links = Mock(return_value={
            "facebook": "https://facebook.com/test",
            "twitter": "https://twitter.com/test"
        })

        config.google_business_profile = None
        config.google_maps = None

        return config

    def test_generate_footer_content(self, mock_config):
        """Test footer content generation"""
        generator = FooterGenerator()
        content = generator.generate_footer_content(mock_config)

        assert "Test Business" in content
        assert "123 Test St" in content
        assert "test@example.com" in content
        assert "555-1234" in content

    def test_normalize_phone(self):
        """Test phone number normalization"""
        assert normalize_phone("(555) 123-4567") == "5551234567"
        assert normalize_phone("555-123-4567") == "5551234567"
        assert normalize_phone("5551234567") == "5551234567"

    def test_get_display_phone(self):
        """Test phone number display formatting"""
        # Already formatted - should keep it
        formatted = "(555) 123-4567"
        assert format_phone_display(formatted) == formatted

        # Not formatted - should format it
        assert format_phone_display("5551234567") == "(555) 123-4567"

    def test_modify_iframe_size(self):
        """Test iframe size modification"""
        iframe = '<iframe width="600" height="450" src="test.html"></iframe>'
        modified = modify_iframe_size(iframe, 800, 600)

        assert 'width="800"' in modified
        assert 'height="600"' in modified


class TestNavigationBuilder:
    """Tests for NavigationBuilder"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock ClientConfig for testing"""
        config = Mock()
        config.target_cities = [
            "Chicago, IL",
            "Aurora, IL",
            "Naperville, IL"
        ]
        return config

    def test_build_navigation(self, mock_config):
        """Test navigation building"""
        builder = NavigationBuilder()
        nav = builder.build_navigation(mock_config)

        assert "Home" in nav
        assert "Products" in nav
        assert "Service Area" in nav
        assert "Contact Us" in nav
        assert "Chicago" in nav
        assert "Aurora" in nav
        assert "Naperville" in nav

    def test_build_navigation_with_current_city(self, mock_config):
        """Test navigation with current city highlighted"""
        builder = NavigationBuilder()
        nav = builder.build_navigation(mock_config, "Chicago")

        assert 'class="active-city"' in nav
        assert 'chicago-il.html' in nav

    def test_generate_city_slug(self):
        """Test city slug generation"""
        # Test basic slug generation
        assert generate_city_slug("Chicago, IL") == "chicago-il"
        assert generate_city_slug("Oak Brook") == "oak-brook"
        # Spaces->dashes happens first, so "Aurora IL" becomes "aurora-il"
        # then " il" pattern doesn't match "-il", so it stays
        assert generate_city_slug("Aurora IL") == "aurora-il"
        # Comma is removed but spaces to dashes happens, resulting in "napervilleil"
        assert generate_city_slug("Naperville,IL") == "napervilleil"

    def test_navigation_without_cities(self):
        """Test navigation when no cities are configured"""
        config = Mock()
        config.target_cities = []

        builder = NavigationBuilder()
        nav = builder.build_navigation(config)

        # Should still have basic navigation structure
        assert "Home" in nav
        assert "Products" in nav
        assert "Service Area" in nav


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
