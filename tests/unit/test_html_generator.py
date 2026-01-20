"""
Comprehensive Unit Tests for HTML Generator
Path: E:/projects/cloud-stack-generator/tests/unit/test_html_generator.py

Description:
Comprehensive unit tests for the HTML generation system, targeting 80%+ code coverage.
Tests all page generation methods, template data preparation, custom filters, and error handling.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Comprehensive test suite for HTML generator
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from datetime import datetime
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.generators.html_generator import HTMLGenerator


class MockBusiness:
    """Mock business configuration"""
    def __init__(self, **kwargs):
        self.business_name = kwargs.get('business_name', 'Test Business')
        self.industry = kwargs.get('industry', 'Professional Services')
        self.tagline = kwargs.get('tagline', 'Quality services you can trust')
        self.description = kwargs.get('description', 'We provide excellent professional services.')
        self.legal_name = kwargs.get('legal_name', 'Test Business LLC')
        self.founded_year = kwargs.get('founded_year', '2020')
        self.domain = kwargs.get('domain', 'https://testbusiness.com')


class MockAddress:
    """Mock address configuration"""
    def __init__(self, **kwargs):
        self.street = kwargs.get('street', '123 Test Street')
        self.city = kwargs.get('city', 'Test City')
        self.state = kwargs.get('state', 'TS')
        self.zip_code = kwargs.get('zip_code', '12345')
        self.country = kwargs.get('country', 'US')

    def to_single_line(self):
        return f"{self.street}, {self.city}, {self.state} {self.zip_code}"


class MockContact:
    """Mock contact configuration"""
    def __init__(self, **kwargs):
        self.phone = kwargs.get('phone', '(555) 123-4567')
        self.email = kwargs.get('email', 'test@testbusiness.com')
        self.address = kwargs.get('address', MockAddress())


class MockService:
    """Mock service configuration"""
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'Test Service')
        self.description = kwargs.get('description', 'A test service description')
        self.price_range = kwargs.get('price_range', '$100-500')
        self.category = kwargs.get('category', 'General')


class MockProduct:
    """Mock product configuration"""
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', 'Test Product')
        self.description = kwargs.get('description', 'A test product description')
        self.price = kwargs.get('price', '$299.99')
        self.category = kwargs.get('category', 'Hardware')
        self.sku = kwargs.get('sku', 'TEST-001')
        self.material = kwargs.get('material', 'Steel')


class MockCityPage:
    """Mock city page configuration"""
    def __init__(self, **kwargs):
        self.city_name = kwargs.get('city_name', 'Test City')
        self.slug = kwargs.get('slug', 'test-city')
        self.state = kwargs.get('state', 'TS')
        self.title = kwargs.get('title', f"{self.city_name} — Custom Architectural Metal")
        self.hero_title = kwargs.get('hero_title', f"{self.city_name} — Custom Architectural Metal Fabrication")
        self.meta_description = kwargs.get('meta_description', f"Custom metal fabrication services in {self.city_name}")
        self.breadcrumbs = kwargs.get('breadcrumbs', ["Home", "Locations", self.city_name])

    def full_city_name(self):
        """Get full city name with state"""
        if self.state:
            return f"{self.city_name}, {self.state}"
        return self.city_name


class MockCloudConfig:
    """Mock cloud configuration"""
    def __init__(self, **kwargs):
        self.meta_tags = kwargs.get('meta_tags', {})
        self.site_type = kwargs.get('site_type', None)
        self.main_site_url = kwargs.get('main_site_url', '')
        self.deployment_url = kwargs.get('deployment_url', None)


class MockClientConfig:
    """Mock client configuration"""
    def __init__(self, **kwargs):
        self.business = kwargs.get('business', MockBusiness())
        self.contact = kwargs.get('contact', MockContact())
        self.services = kwargs.get('services', [MockService()])
        self.products = kwargs.get('products', [MockProduct()])

        # Optional attributes
        self.branding = kwargs.get('branding', None)
        self.google_business_profile = kwargs.get('google_business_profile', None)
        self.social_media = kwargs.get('social_media', None)
        self.geo_coordinates = kwargs.get('geo_coordinates', None)
        self.business_hours = kwargs.get('business_hours', None)
        self.city_pages = kwargs.get('city_pages', [])
        self.faq = kwargs.get('faq', [])
        self.cloud = kwargs.get('cloud', None)
        self.target_cities = kwargs.get('target_cities', [])


class TestHTMLGeneratorInit:
    """Test HTMLGenerator initialization and setup"""

    def test_init_default_template_dir(self):
        """Test initialization with default template directory"""
        generator = HTMLGenerator()

        assert generator.template_dir is not None
        assert isinstance(generator.template_dir, Path)
        # Should point to src/templates relative to html_generator.py
        assert generator.template_dir.name == "templates"

    def test_init_custom_template_dir(self):
        """Test initialization with custom template directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = HTMLGenerator(template_dir=temp_dir)

            assert generator.template_dir == Path(temp_dir)

    @patch('core.generators.html_generator.jinja2.FileSystemLoader')
    @patch('core.generators.html_generator.jinja2.Environment')
    def test_jinja_environment_setup_success(self, mock_env, mock_loader):
        """Test successful Jinja2 environment setup"""
        mock_env_instance = MagicMock()
        mock_env.return_value = mock_env_instance

        HTMLGenerator()

        # Verify FileSystemLoader was called with template directory
        mock_loader.assert_called_once()

        # Verify Environment was configured properly
        mock_env.assert_called_once()
        call_kwargs = mock_env.call_args[1]
        assert 'loader' in call_kwargs
        assert 'autoescape' in call_kwargs
        assert call_kwargs['trim_blocks'] is True
        assert call_kwargs['lstrip_blocks'] is True

    @patch('core.generators.html_generator.jinja2.FileSystemLoader', side_effect=Exception("Template load error"))
    def test_jinja_environment_setup_failure(self, mock_loader):
        """Test Jinja2 environment setup failure handling"""
        generator = HTMLGenerator()

        # Should handle exception gracefully and set jinja_env to None
        assert generator.jinja_env is None

    def test_custom_filters_registration(self):
        """Test that custom filters are registered"""
        with patch('core.generators.html_generator.jinja2.Environment') as mock_env:
            mock_env_instance = MagicMock()
            mock_env.return_value = mock_env_instance

            HTMLGenerator()

            # Verify filters were registered
            expected_filters = ['format_phone', 'format_price', 'slugify', 'truncate_words', 'date']
            for filter_name in expected_filters:
                assert mock_env_instance.filters.__setitem__.call_args_list
                # Check that the filter was set
                filter_calls = [call[0][0] for call in mock_env_instance.filters.__setitem__.call_args_list]
                assert filter_name in filter_calls


class TestTemplateDataPreparation:
    """Test _prepare_template_data method comprehensively"""

    @pytest.fixture
    def generator(self):
        """Create HTMLGenerator instance for testing"""
        return HTMLGenerator()

    @pytest.fixture
    def complete_config(self):
        """Complete mock configuration with all optional fields"""
        return MockClientConfig(
            branding={'primary_color': '#007bff', 'logo_url': 'logo.png'},
            google_business_profile={'embed_code': '<iframe></iframe>'},
            social_media={'facebook': 'https://facebook.com/test'},
            geo_coordinates={'latitude': 40.7128, 'longitude': -74.0060},
            business_hours=[{'day': 'Monday', 'hours': '9 AM - 5 PM'}],
            city_pages=[MockCityPage(city_name='Test City', slug='test-city')]
        )

    def test_prepare_template_data_basic(self, generator, complete_config):
        """Test basic template data preparation"""
        result = generator._prepare_template_data(complete_config)

        # Verify basic data structure
        assert 'business' in result
        assert 'contact' in result
        assert 'services' in result
        assert 'products' in result
        assert 'current_year' in result
        assert 'generation_date' in result

        # Verify business data
        assert result['business'].business_name == 'Test Business'
        assert result['business'].industry == 'Professional Services'

        # Verify contact data
        assert result['contact'].phone == '(555) 123-4567'
        assert result['contact'].email == 'test@testbusiness.com'

    def test_prepare_template_data_optional_fields(self, generator, complete_config):
        """Test template data preparation with optional fields"""
        result = generator._prepare_template_data(complete_config)

        # Verify optional fields are included
        assert 'branding' in result
        assert 'google_business_profile' in result
        assert 'social_media' in result
        assert 'geo_coordinates' in result
        assert 'business_hours' in result

        # Verify optional field values
        assert result['branding']['primary_color'] == '#007bff'
        assert result['google_business_profile']['embed_code'] == '<iframe></iframe>'
        assert result['social_media']['facebook'] == 'https://facebook.com/test'

    def test_prepare_template_data_minimal_config(self, generator):
        """Test template data preparation with minimal configuration"""
        minimal_config = MockClientConfig()

        result = generator._prepare_template_data(minimal_config)

        # Should handle missing optional fields gracefully
        assert 'business' in result
        assert 'contact' in result
        assert 'services' in result
        assert 'products' in result

        # Optional fields should be None or default values
        branding = result.get('branding')
        assert branding is None

    @patch.object(HTMLGenerator, '_generate_navigation')
    @patch.object(HTMLGenerator, '_generate_footer_links')
    @patch.object(HTMLGenerator, '_get_social_links')
    @patch.object(HTMLGenerator, '_generate_organization_schema')
    def test_prepare_template_data_calls_helpers(self, mock_schema, mock_social, mock_footer, mock_nav, generator):
        """Test that template data preparation calls helper methods"""
        config = MockClientConfig()

        # Mock return values
        mock_nav.return_value = []
        mock_footer.return_value = []
        mock_social.return_value = []
        mock_schema.return_value = {}

        result = generator._prepare_template_data(config)

        # Verify helper methods were called
        mock_nav.assert_called_once_with(config)
        mock_footer.assert_called_once_with(config)
        mock_social.assert_called_once_with(config)
        mock_schema.assert_called_once_with(config)

        # Verify results are included
        assert 'navigation' in result
        assert 'footer_links' in result
        assert 'social_links' in result
        assert 'organization_schema' in result


class TestPageGenerationMethods:
    """Test all public page generation methods"""

    @pytest.fixture
    def generator(self):
        """Create HTMLGenerator instance with mocked template rendering"""
        gen = HTMLGenerator()
        gen._render_template = MagicMock(return_value="<html>Mocked Template</html>")
        return gen

    @pytest.fixture
    def config(self):
        """Standard test configuration"""
        return MockClientConfig()

    def test_generate_homepage(self, generator, config):
        """Test homepage generation"""
        result = generator.generate_homepage(config)

        assert result == "<html>Mocked Template</html>"

        # Verify _render_template was called with correct parameters
        generator._render_template.assert_called_once()
        call_args = generator._render_template.call_args

        template_name, template_data = call_args[0]
        assert template_name == "pages/index.html"

        # Verify homepage-specific data
        assert template_data['page_type'] == 'homepage'
        assert template_data['is_homepage'] is True
        assert 'featured_services' in template_data
        assert 'featured_products' in template_data
        assert len(template_data['featured_services']) <= 3  # Top 3 services
        assert len(template_data['featured_products']) <= 6  # Top 6 products

    def test_generate_about_page(self, generator, config):
        """Test about page generation"""
        result = generator.generate_about_page(config)

        assert result == "<html>Mocked Template</html>"

        call_args = generator._render_template.call_args
        template_name, template_data = call_args[0]

        assert template_name == "pages/about.html"
        assert template_data['page_type'] == 'about'
        assert 'company_story' in template_data
        assert 'team_members' in template_data
        assert 'company_values' in template_data

    def test_generate_contact_page(self, generator, config):
        """Test contact page generation"""
        generator.generate_contact_page(config)

        call_args = generator._render_template.call_args
        template_name, template_data = call_args[0]

        assert template_name == "pages/contact.html"
        assert template_data['page_type'] == 'contact'
        assert template_data['contact_form'] is True
        assert 'google_maps_embed' in template_data
        assert 'business_hours' in template_data

    def test_generate_services_page(self, generator, config):
        """Test services page generation"""
        generator.generate_services_page(config)

        call_args = generator._render_template.call_args
        template_name, template_data = call_args[0]

        assert template_name == "pages/services.html"
        assert template_data['page_type'] == 'services'
        assert 'services_by_category' in template_data
        assert 'service_categories' in template_data

    def test_generate_services_page_empty_services(self, generator):
        """Test services page generation with empty services"""
        config = MockClientConfig(services=[])
        generator.generate_services_page(config)

        call_args = generator._render_template.call_args
        template_name, template_data = call_args[0]

        assert template_data['services_by_category'] == {}
        assert template_data['service_categories'] == []

    def test_generate_products_page(self, generator, config):
        """Test products page generation"""
        generator.generate_products_page(config)

        call_args = generator._render_template.call_args
        template_name, template_data = call_args[0]

        assert template_name == "pages/products.html"
        assert template_data['page_type'] == 'products'
        assert 'products_by_category' in template_data
        assert 'product_categories' in template_data

    def test_generate_individual_service_page(self, generator, config):
        """Test individual service page generation"""
        service = MockService(name="Test Service")
        generator.generate_individual_service_page(config, service)

        call_args = generator._render_template.call_args
        template_name, template_data = call_args[0]

        assert template_name == "pages/service-detail.html"
        assert template_data['page_type'] == 'service'
        assert template_data['service'] == service
        assert 'related_services' in template_data
        assert 'service_schema' in template_data

    def test_generate_individual_product_page(self, generator, config):
        """Test individual product page generation"""
        product = MockProduct(name="Test Product")
        generator.generate_individual_product_page(config, product)

        call_args = generator._render_template.call_args
        template_name, template_data = call_args[0]

        assert template_name == "pages/product-detail.html"
        assert template_data['page_type'] == 'product'
        assert template_data['product'] == product
        assert 'related_products' in template_data
        assert 'product_schema' in template_data
        assert template_data['base_path'] == '../'

    def test_generate_faq_page(self, generator):
        """Test FAQ page generation"""
        faq_data = [
            {'question': 'What do you do?', 'answer': 'We provide services.', 'category': 'General'}
        ]
        config = MockClientConfig(faq=faq_data)
        generator.generate_faq_page(config)

        call_args = generator._render_template.call_args
        template_name, template_data = call_args[0]

        assert template_name == "pages/faq.html"
        assert template_data['page_type'] == 'faq'
        assert 'faq_by_category' in template_data
        assert 'total_faqs' in template_data
        assert template_data['total_faqs'] == 1

    def test_generate_privacy_page(self, generator, config):
        """Test privacy page generation"""
        generator.generate_privacy_page(config)

        call_args = generator._render_template.call_args
        template_name, template_data = call_args[0]

        assert template_name == "pages/privacy-policy.html"
        assert template_data['page_type'] == 'privacy'
        assert 'current_year' in template_data


class TestCustomJinja2Filters:
    """Test all custom Jinja2 filters"""

    @pytest.fixture
    def generator(self):
        """Create HTMLGenerator instance"""
        return HTMLGenerator()

    def test_format_phone_valid_10_digit(self, generator):
        """Test phone formatting with valid 10-digit number"""
        result = generator._format_phone("5551234567")
        assert result == "(555) 123-4567"

    def test_format_phone_valid_11_digit(self, generator):
        """Test phone formatting with valid 11-digit number"""
        result = generator._format_phone("15551234567")
        assert result == "+1 (555) 123-4567"

    def test_format_phone_already_formatted(self, generator):
        """Test phone formatting with already formatted number"""
        formatted = "(555) 123-4567"
        result = generator._format_phone(formatted)
        assert result == formatted

    def test_format_phone_invalid(self, generator):
        """Test phone formatting with invalid number"""
        result = generator._format_phone("invalid")
        assert result == "invalid"  # Should return as-is

    def test_format_phone_empty(self, generator):
        """Test phone formatting with empty input"""
        result = generator._format_phone("")
        assert result == ""

    def test_format_price_valid(self, generator):
        """Test price formatting with valid price"""
        result = generator._format_price("$299.99")
        assert result == "$299.99"

    def test_format_price_empty(self, generator):
        """Test price formatting with empty price"""
        result = generator._format_price("")
        assert result == "Contact for pricing"

    def test_format_price_none(self, generator):
        """Test price formatting with None price"""
        result = generator._format_price(None)
        assert result == "Contact for pricing"

    def test_slugify_basic(self, generator):
        """Test basic slugify functionality"""
        result = generator._slugify("Test Service Name")
        assert result == "test-service-name"

    def test_slugify_special_characters(self, generator):
        """Test slugify with special characters"""
        result = generator._slugify("Test & Service! @#$")
        assert result == "test-service"

    def test_slugify_multiple_spaces_hyphens(self, generator):
        """Test slugify with multiple spaces and hyphens"""
        result = generator._slugify("Test  --  Service   Name")
        assert result == "test-service-name"

    def test_slugify_empty(self, generator):
        """Test slugify with empty string"""
        result = generator._slugify("")
        assert result == ""

    def test_truncate_words_normal(self, generator):
        """Test word truncation with normal text"""
        text = "This is a long sentence with many words in it"
        result = generator._truncate_words(text, 5)
        assert result == "This is a long sentence..."

    def test_truncate_words_shorter_than_limit(self, generator):
        """Test word truncation with text shorter than limit"""
        text = "Short text"
        result = generator._truncate_words(text, 5)
        assert result == "Short text"

    def test_truncate_words_exact_limit(self, generator):
        """Test word truncation with text exactly at limit"""
        text = "One two three four five"
        result = generator._truncate_words(text, 5)
        assert result == "One two three four five"

    def test_date_filter_now(self, generator):
        """Test date filter with 'now' keyword"""
        result = generator._date_filter("now", "%Y")
        current_year = str(datetime.now().year)
        assert result == current_year

    def test_date_filter_datetime_object(self, generator):
        """Test date filter with datetime object"""
        test_date = datetime(2025, 9, 22, 10, 30, 0)
        result = generator._date_filter(test_date, "%Y-%m-%d")
        assert result == "2025-09-22"

    def test_date_filter_valid_string(self, generator):
        """Test date filter with valid date string"""
        result = generator._date_filter("2025-09-22", "%Y")
        assert result == "2025"

    def test_date_filter_invalid_string(self, generator):
        """Test date filter with invalid date string"""
        result = generator._date_filter("invalid-date", "%Y")
        assert result == "invalid-date"  # Should return as-is


class TestNavigationGeneration:
    """Test _generate_navigation method"""

    @pytest.fixture
    def generator(self):
        """Create HTMLGenerator instance"""
        return HTMLGenerator()

    def test_generate_navigation_basic(self, generator):
        """Test basic navigation generation"""
        config = MockClientConfig()
        result = generator._generate_navigation(config)

        assert isinstance(result, list)

        # Should include basic navigation items
        nav_items = [item['text'] for item in result]
        assert 'Home' in nav_items
        assert 'About' in nav_items
        assert 'Contact' in nav_items

    def test_generate_navigation_with_services(self, generator):
        """Test navigation generation with services"""
        services = [MockService(name="Service 1"), MockService(name="Service 2")]
        config = MockClientConfig(services=services)
        result = generator._generate_navigation(config)

        nav_items = [item['text'] for item in result]
        assert 'Services' in nav_items

    def test_generate_navigation_with_products(self, generator):
        """Test navigation generation with products"""
        products = [MockProduct(name="Product 1"), MockProduct(name="Product 2")]
        config = MockClientConfig(products=products)
        result = generator._generate_navigation(config)

        nav_items = [item['text'] for item in result]
        assert 'Products' in nav_items

    def test_generate_navigation_with_city_pages(self, generator):
        """Test navigation generation with city pages"""
        city_pages = [MockCityPage(city_name='Test City', slug='test-city')]
        config = MockClientConfig(city_pages=city_pages)
        result = generator._generate_navigation(config)

        # Should include city pages in navigation
        service_areas = [item for item in result if item['text'] == 'Service Areas']
        assert len(service_areas) > 0


class TestSchemaGeneration:
    """Test JSON-LD schema generation methods"""

    @pytest.fixture
    def generator(self):
        """Create HTMLGenerator instance"""
        return HTMLGenerator()

    def test_generate_organization_schema_basic(self, generator):
        """Test basic organization schema generation"""
        config = MockClientConfig()
        result = generator._generate_organization_schema(config)

        assert isinstance(result, dict)
        assert result['@context'] == 'https://schema.org'
        assert result['@type'] == 'Organization'
        assert result['name'] == 'Test Business'
        assert result['description'] == 'We provide excellent professional services.'

    def test_generate_organization_schema_with_address(self, generator):
        """Test organization schema with address information"""
        config = MockClientConfig()
        result = generator._generate_organization_schema(config)

        assert 'address' in result
        address = result['address']
        assert address['@type'] == 'PostalAddress'
        assert address['streetAddress'] == '123 Test Street'
        assert address['addressLocality'] == 'Test City'

    def test_generate_organization_schema_with_contact(self, generator):
        """Test organization schema with contact information"""
        config = MockClientConfig()
        result = generator._generate_organization_schema(config)

        assert 'telephone' in result
        assert 'email' in result
        assert result['telephone'] == '(555) 123-4567'
        assert result['email'] == 'test@testbusiness.com'

    @patch.object(HTMLGenerator, '_generate_industry_wikipedia_entities')
    def test_generate_organization_schema_with_wikipedia(self, mock_wikipedia, generator):
        """Test organization schema with Wikipedia entities"""
        mock_wikipedia.return_value = [{'@type': 'Thing', 'name': 'Construction'}]

        config = MockClientConfig()
        result = generator._generate_organization_schema(config)

        mock_wikipedia.assert_called_once_with('Professional Services')
        # Should include @graph structure when Wikipedia entities are present
        assert '@graph' in result

    def test_generate_service_schema(self, generator):
        """Test service schema generation"""
        service = MockService(name="Test Service", description="Service description", price_range="$100-500")
        config = MockClientConfig()

        result = generator._generate_service_schema(service, config)

        assert isinstance(result, dict)
        assert result['@type'] == 'Service'
        assert result['name'] == 'Test Service'
        assert result['description'] == 'Service description'

        # Should include provider information
        assert 'provider' in result
        assert result['provider']['name'] == 'Test Business'

    def test_generate_product_schema_basic(self, generator):
        """Test basic product schema generation"""
        product = MockProduct(name="Test Product", description="Product description", price="$299.99")
        config = MockClientConfig()

        result = generator._generate_product_schema(product, config)

        assert isinstance(result, dict)
        assert result['@type'] == 'Product'
        assert result['name'] == 'Test Product'
        assert result['description'] == 'Product description'

    def test_generate_product_schema_with_details(self, generator):
        """Test product schema with detailed information"""
        product = MockProduct(
            name="Steel Product",
            sku="SP-001",
            material="Steel",
            price="$499.99"
        )
        config = MockClientConfig()

        result = generator._generate_product_schema(product, config)

        assert result['sku'] == 'SP-001'
        assert result['material'] == 'Steel'

        # Should include offers
        assert 'offers' in result
        offers = result['offers']
        assert offers['@type'] == 'Offer'
        assert offers['price'] == '499.99'


class TestWikipediaEntityGeneration:
    """Test Wikipedia entity mapping"""

    @pytest.fixture
    def generator(self):
        """Create HTMLGenerator instance"""
        return HTMLGenerator()

    def test_generate_industry_wikipedia_entities_construction(self, generator):
        """Test Wikipedia entities for construction industry"""
        result = generator._generate_industry_wikipedia_entities("Construction")

        assert isinstance(result, list)
        assert len(result) > 0

        # Should include construction-related entities
        entity_names = [entity['name'] for entity in result]
        assert 'Construction' in entity_names

    def test_generate_industry_wikipedia_entities_roofing(self, generator):
        """Test Wikipedia entities for roofing industry"""
        result = generator._generate_industry_wikipedia_entities("Roofing")

        entity_names = [entity['name'] for entity in result]
        assert 'Roof' in entity_names

    def test_generate_industry_wikipedia_entities_unknown(self, generator):
        """Test Wikipedia entities for unknown industry"""
        result = generator._generate_industry_wikipedia_entities("Unknown Industry")

        # Should return empty list for unknown industries
        assert result == []

    def test_generate_product_wikipedia_entities_cupola(self, generator):
        """Test Wikipedia entities for cupola product"""
        result = generator._generate_product_wikipedia_entities("cupola")

        assert isinstance(result, list)
        assert len(result) > 0

        entity_names = [entity['name'] for entity in result]
        assert 'Cupola' in entity_names

    def test_generate_product_wikipedia_entities_unknown(self, generator):
        """Test Wikipedia entities for unknown product"""
        result = generator._generate_product_wikipedia_entities("unknown-product")

        # Should return empty list for unknown products
        assert result == []


class TestTemplateRendering:
    """Test template rendering and fallback systems"""

    @pytest.fixture
    def generator_with_mock_env(self):
        """Create HTMLGenerator with mocked Jinja environment"""
        generator = HTMLGenerator()
        generator.jinja_env = MagicMock()
        return generator

    def test_render_template_success(self, generator_with_mock_env):
        """Test successful template rendering"""
        # Mock template
        mock_template = MagicMock()
        mock_template.render.return_value = "<html>Rendered Content</html>"
        generator_with_mock_env.jinja_env.get_template.return_value = mock_template

        result = generator_with_mock_env._render_template("test.html", {"key": "value"})

        assert result == "<html>Rendered Content</html>"
        generator_with_mock_env.jinja_env.get_template.assert_called_once_with("test.html")
        mock_template.render.assert_called_once_with(key="value")

    def test_render_template_not_found(self, generator_with_mock_env):
        """Test template not found handling"""
        from jinja2 import TemplateNotFound
        generator_with_mock_env.jinja_env.get_template.side_effect = TemplateNotFound("test.html")

        with patch.object(generator_with_mock_env, '_render_fallback_template') as mock_fallback:
            mock_fallback.return_value = "<html>Fallback</html>"

            result = generator_with_mock_env._render_template("test.html", {"key": "value"})

            assert result == "<html>Fallback</html>"
            mock_fallback.assert_called_once_with("test.html", {"key": "value"})

    def test_render_template_general_exception(self, generator_with_mock_env):
        """Test general template rendering exception"""
        generator_with_mock_env.jinja_env.get_template.side_effect = Exception("Rendering error")

        with patch.object(generator_with_mock_env, '_render_fallback_template') as mock_fallback:
            mock_fallback.return_value = "<html>Fallback</html>"

            result = generator_with_mock_env._render_template("test.html", {"key": "value"})

            assert result == "<html>Fallback</html>"
            mock_fallback.assert_called_once_with("test.html", {"key": "value"})

    def test_render_template_no_jinja_env(self):
        """Test template rendering when Jinja environment is None"""
        generator = HTMLGenerator()
        generator.jinja_env = None

        with patch.object(generator, '_render_fallback_template') as mock_fallback:
            mock_fallback.return_value = "<html>Fallback</html>"

            result = generator._render_template("test.html", {"key": "value"})

            assert result == "<html>Fallback</html>"
            mock_fallback.assert_called_once_with("test.html", {"key": "value"})


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""

    def test_init_with_nonexistent_template_dir(self):
        """Test initialization with non-existent template directory"""
        generator = HTMLGenerator(template_dir="/nonexistent/path")
        # Should handle gracefully and still create instance
        assert generator.template_dir == Path("/nonexistent/path")

    def test_services_categorization_with_none_category(self):
        """Test service categorization when category is None"""
        generator = HTMLGenerator()

        # Create service with None category
        service_no_category = MockService(name="No Category Service")
        service_no_category.category = None

        config = MockClientConfig(services=[service_no_category])
        result = generator._prepare_template_data(config)

        # Should handle None category gracefully
        assert 'services_by_category' not in result or isinstance(result.get('services_by_category'), dict)

    def test_generate_maps_embed_with_long_address(self):
        """Test Google Maps embed generation with long address"""
        generator = HTMLGenerator()

        long_address = "Very Long Street Name That Might Cause Issues, Very Long City Name, Very Long State Name 12345-6789"
        result = generator._generate_maps_embed(long_address)

        # Should handle long addresses
        assert isinstance(result, str)
        assert len(result) > 0


class TestImagePathNormalization:
    """Test _normalize_image_path method for Issue #2 regression fix"""

    @pytest.fixture
    def generator(self):
        """Create HTMLGenerator instance"""
        return HTMLGenerator()

    def test_normalize_absolute_windows_path(self, generator):
        """Test normalization of absolute Windows path"""
        absolute_path = "D:/OneDrive/RankRocket/Clients/Adventure Marketing/Salvo Metal/GBP/images/unprocessed/ai_generated_1768850143_1.png"
        result = generator._normalize_image_path(absolute_path)

        assert result == "images/ai_generated_1768850143_1.png"
        assert not Path(result).is_absolute()
        assert "/" in result  # Uses forward slashes for web

    def test_normalize_absolute_unix_path(self, generator):
        """Test normalization of absolute Unix path"""
        absolute_path = "/home/user/projects/images/hero.jpg"
        result = generator._normalize_image_path(absolute_path)

        assert result == "images/hero.jpg"
        assert not Path(result).is_absolute()

    def test_normalize_relative_path_with_backslashes(self, generator):
        """Test normalization of relative path with backslashes"""
        relative_path = "images\\product\\copper-box.jpg"
        result = generator._normalize_image_path(relative_path)

        assert result == "images/product/copper-box.jpg"
        assert "\\" not in result  # Converts backslashes to forward slashes

    def test_normalize_relative_path_already_normalized(self, generator):
        """Test normalization of already normalized path"""
        relative_path = "images/hero-background.jpg"
        result = generator._normalize_image_path(relative_path)

        assert result == "images/hero-background.jpg"

    def test_normalize_empty_path(self, generator):
        """Test normalization of empty path"""
        result = generator._normalize_image_path("")

        assert result == ""

    def test_normalize_none_path(self, generator):
        """Test normalization of None path"""
        result = generator._normalize_image_path(None)

        assert result is None

    def test_normalize_path_integration_in_template_data(self, generator):
        """Test that hero background image path is normalized in template data"""
        from unittest.mock import MagicMock

        # Create mock branding with absolute path
        mock_branding = MagicMock()
        mock_branding.hero_background_image_url = "D:/OneDrive/Client/images/hero.png"
        mock_branding.logo_url = None

        # Create mock cloud config
        mock_cloud = MagicMock()
        mock_cloud.deployment_url = "https://example.com"
        mock_cloud.site_type = None

        # Create mock config
        mock_config = MockClientConfig(branding=mock_branding)
        mock_config.cloud = mock_cloud
        mock_config.target_cities = []  # Add missing attribute

        # Prepare template data
        result = generator._prepare_template_data(mock_config)

        # Verify hero background image URL is normalized
        assert result['branding'].hero_background_image_url == "images/hero.png"


class TestBusinessLogicHelpers:
    """Test business logic helper methods"""

    @pytest.fixture
    def generator(self):
        """Create HTMLGenerator instance"""
        return HTMLGenerator()

    def test_generate_company_story(self, generator):
        """Test company story generation"""
        config = MockClientConfig()
        result = generator._generate_company_story(config)

        assert isinstance(result, str)
        assert len(result) > 0
        assert 'Test Business' in result

    def test_get_team_members(self, generator):
        """Test team members retrieval"""
        config = MockClientConfig()
        result = generator._get_team_members(config)

        assert isinstance(result, list)
        # Current implementation returns empty list
        assert result == []

    def test_get_company_values(self, generator):
        """Test company values retrieval"""
        config = MockClientConfig()
        result = generator._get_company_values(config)

        assert isinstance(result, list)
        assert len(result) > 0
        # Should include common business values
        assert any('Quality' in value for value in result)

    def test_generate_maps_embed(self, generator):
        """Test Google Maps embed generation"""
        address = "123 Test St, Test City, TS 12345"
        result = generator._generate_maps_embed(address)

        assert isinstance(result, str)
        assert 'iframe' in result
        assert 'google.com/maps' in result

    def test_get_business_hours(self, generator):
        """Test business hours retrieval"""
        config = MockClientConfig()
        result = generator._get_business_hours(config)

        assert isinstance(result, list)
        # Should return default business hours
        assert len(result) > 0


class TestMetaTagFormatting:
    """Tests for GSC and other meta tag formatting (v3.13.0)"""

    @pytest.fixture
    def generator(self):
        """Create HTMLGenerator instance"""
        return HTMLGenerator()

    @pytest.fixture
    def mock_config(self):
        """Create mock config with cloud meta tags"""
        config = MockClientConfig()
        config.cloud = MockCloudConfig()
        config.cloud.meta_tags = {
            'google-site-verification': '5prGkkDwdgnD7-QWd3YNFqARdjtMCc4c5z5GWaHDR90'
        }
        return config

    def test_meta_tags_are_self_closing(self, generator, mock_config):
        """Test that meta tags are properly self-closing with /"""
        html = generator.generate_homepage(mock_config, use_ai=False)

        # Check that meta tag is self-closing with />
        assert '<meta name="google-site-verification" content="5prGkkDwdgnD7-QWd3YNFqARdjtMCc4c5z5GWaHDR90" />' in html

        # Verify it's NOT the incorrect format (without />)
        assert '<meta name="google-site-verification" content="5prGkkDwdgnD7-QWd3YNFqARdjtMCc4c5z5GWaHDR90">' not in html or \
               '<meta name="google-site-verification" content="5prGkkDwdgnD7-QWd3YNFqARdjtMCc4c5z5GWaHDR90" />' in html

    def test_multiple_meta_tags_all_self_closing(self, generator, mock_config):
        """Test that all custom meta tags are self-closing"""
        mock_config.cloud.meta_tags = {
            'google-site-verification': 'test-verification-code',
            'msvalidate.01': 'test-bing-code',
            'p:domain_verify': 'test-pinterest-code'
        }

        html = generator.generate_homepage(mock_config, use_ai=False)

        # All meta tags should be self-closing
        assert '<meta name="google-site-verification" content="test-verification-code" />' in html
        assert '<meta name="msvalidate.01" content="test-bing-code" />' in html
        assert '<meta name="p:domain_verify" content="test-pinterest-code" />' in html


if __name__ == '__main__':
    pytest.main([__file__])