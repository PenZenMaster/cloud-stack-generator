"""
Unit tests for schema generation methods
Tests breadcrumb schema generation added in schema enhancements
"""

import pytest
from unittest.mock import Mock

from src.core.generators.html_generator import HTMLGenerator
from src.core.generators.enhanced_city_page_generator import EnhancedCityPageGenerator
from src.core.config.models import (
    ClientConfig, BusinessConfig, ContactConfig, AddressConfig,
    BrandingConfig, CloudConfig
)


@pytest.mark.unit
class TestBreadcrumbSchemaGeneration:
    """Test breadcrumb schema generation in HTML generator"""

    def setup_method(self):
        """Set up test fixtures"""
        self.generator = HTMLGenerator()
        self.base_url = "https://example.com"

    def test_breadcrumb_homepage(self):
        """Test breadcrumb schema for homepage (Home only)"""
        schema = self.generator._generate_breadcrumb_schema(
            "homepage",
            self.base_url
        )

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "BreadcrumbList"
        assert "itemListElement" in schema

        items = schema["itemListElement"]
        assert len(items) == 1
        assert items[0]["@type"] == "ListItem"
        assert items[0]["position"] == 1
        assert items[0]["name"] == "Home"
        assert items[0]["item"] == self.base_url

    def test_breadcrumb_about(self):
        """Test breadcrumb schema for about page"""
        schema = self.generator._generate_breadcrumb_schema(
            "about",
            self.base_url
        )

        items = schema["itemListElement"]
        assert len(items) == 2

        # Home
        assert items[0]["name"] == "Home"
        assert items[0]["position"] == 1

        # About
        assert items[1]["name"] == "About Us"
        assert items[1]["position"] == 2
        assert items[1]["item"] == f"{self.base_url}/about.html"

    def test_breadcrumb_contact(self):
        """Test breadcrumb schema for contact page"""
        schema = self.generator._generate_breadcrumb_schema(
            "contact",
            self.base_url
        )

        items = schema["itemListElement"]
        assert len(items) == 2
        assert items[1]["name"] == "Contact"
        assert items[1]["item"] == f"{self.base_url}/contact.html"

    def test_breadcrumb_services(self):
        """Test breadcrumb schema for services overview page"""
        schema = self.generator._generate_breadcrumb_schema(
            "services",
            self.base_url
        )

        items = schema["itemListElement"]
        assert len(items) == 2
        assert items[1]["name"] == "Services"
        assert items[1]["item"] == f"{self.base_url}/services.html"

    def test_breadcrumb_service_detail(self):
        """Test breadcrumb schema for individual service page"""
        schema = self.generator._generate_breadcrumb_schema(
            "service-detail",
            self.base_url,
            page_title="Portable Restrooms",
            page_url=f"{self.base_url}/services/portable-restrooms.html"
        )

        items = schema["itemListElement"]
        assert len(items) == 3

        # Home
        assert items[0]["name"] == "Home"
        assert items[0]["position"] == 1

        # Services
        assert items[1]["name"] == "Services"
        assert items[1]["position"] == 2
        assert items[1]["item"] == f"{self.base_url}/services.html"

        # Service Detail
        assert items[2]["name"] == "Portable Restrooms"
        assert items[2]["position"] == 3
        assert items[2]["item"] == f"{self.base_url}/services/portable-restrooms.html"

    def test_breadcrumb_products(self):
        """Test breadcrumb schema for products overview page"""
        schema = self.generator._generate_breadcrumb_schema(
            "products",
            self.base_url
        )

        items = schema["itemListElement"]
        assert len(items) == 2
        assert items[1]["name"] == "Products"
        assert items[1]["item"] == f"{self.base_url}/products.html"

    def test_breadcrumb_product_detail(self):
        """Test breadcrumb schema for individual product page"""
        schema = self.generator._generate_breadcrumb_schema(
            "product-detail",
            self.base_url,
            page_title="Luxury Restroom Trailer",
            page_url=f"{self.base_url}/products/luxury-restroom-trailer.html"
        )

        items = schema["itemListElement"]
        assert len(items) == 3

        # Products
        assert items[1]["name"] == "Products"
        assert items[1]["position"] == 2

        # Product Detail
        assert items[2]["name"] == "Luxury Restroom Trailer"
        assert items[2]["position"] == 3

    def test_breadcrumb_faq(self):
        """Test breadcrumb schema for FAQ page"""
        schema = self.generator._generate_breadcrumb_schema(
            "faq",
            self.base_url
        )

        items = schema["itemListElement"]
        assert len(items) == 2
        assert items[1]["name"] == "FAQ"
        assert items[1]["item"] == f"{self.base_url}/faq.html"

    def test_breadcrumb_privacy(self):
        """Test breadcrumb schema for privacy policy page"""
        schema = self.generator._generate_breadcrumb_schema(
            "privacy",
            self.base_url
        )

        items = schema["itemListElement"]
        assert len(items) == 2
        assert items[1]["name"] == "Privacy Policy"
        assert items[1]["item"] == f"{self.base_url}/privacy-policy.html"

    def test_breadcrumb_city_page(self):
        """Test breadcrumb schema for city pages"""
        schema = self.generator._generate_breadcrumb_schema(
            "city-page",
            self.base_url,
            page_title="Orlando",
            page_url=f"{self.base_url}/locations/orlando.html"
        )

        items = schema["itemListElement"]
        assert len(items) == 3

        # Home
        assert items[0]["name"] == "Home"
        assert items[0]["position"] == 1

        # Locations
        assert items[1]["name"] == "Locations"
        assert items[1]["position"] == 2
        assert items[1]["item"] == f"{self.base_url}/#locations"

        # City
        assert items[2]["name"] == "Orlando"
        assert items[2]["position"] == 3
        assert items[2]["item"] == f"{self.base_url}/locations/orlando.html"

    def test_breadcrumb_service_detail_auto_url(self):
        """Test breadcrumb schema auto-generates URL when not provided"""
        schema = self.generator._generate_breadcrumb_schema(
            "service-detail",
            self.base_url,
            page_title="Emergency Services"
            # Note: no page_url provided
        )

        items = schema["itemListElement"]
        assert len(items) == 3
        # Should auto-generate URL from title
        assert "emergency-services" in items[2]["item"].lower()


@pytest.mark.unit
class TestCityPageBreadcrumbGeneration:
    """Test breadcrumb schema in city page generator"""

    def setup_method(self):
        """Set up test fixtures with mock config"""
        # Create minimal mock config
        self.config = Mock(spec=ClientConfig)
        self.config.business = Mock(spec=BusinessConfig)
        self.config.business.business_name = "Test Business"
        self.config.business.industry = "Testing"
        self.config.business.domain = "https://test.com"

        self.config.contact = Mock(spec=ContactConfig)
        self.config.contact.phone = "555-1234"
        self.config.contact.email = "test@test.com"
        self.config.contact.address = Mock(spec=AddressConfig)
        self.config.contact.address.street = "123 Test St"
        self.config.contact.address.city = "Test City"
        self.config.contact.address.state = "TS"
        self.config.contact.address.zip_code = "12345"
        self.config.contact.address.country = "US"

        self.config.branding = Mock(spec=BrandingConfig)
        self.config.branding.primary_color = "#000000"
        self.config.branding.secondary_color = "#ffffff"
        self.config.branding.accent_color = "#ff0000"
        self.config.branding.logo_url = "https://test.com/logo.png"
        self.config.branding.font_family = "Arial"

        self.config.cloud = Mock(spec=CloudConfig)
        self.config.cloud.deployment_url = "https://test.com"
        self.config.cloud.site_type = "main_site"

        self.config.services = []
        self.config.products = []

        self.generator = EnhancedCityPageGenerator(self.config)

    def test_city_breadcrumb_generation(self):
        """Test breadcrumb schema generation for city pages"""
        schema = self.generator._generate_breadcrumb_schema(
            "Orlando",
            "orlando"
        )

        assert schema["@context"] == "https://schema.org"
        assert schema["@type"] == "BreadcrumbList"

        items = schema["itemListElement"]
        assert len(items) == 3

        # Verify structure
        assert items[0]["name"] == "Home"
        assert items[1]["name"] == "Locations"
        assert items[2]["name"] == "Orlando"

        # Verify positions
        assert items[0]["position"] == 1
        assert items[1]["position"] == 2
        assert items[2]["position"] == 3

        # Verify URLs
        assert items[0]["item"] == "https://test.com"
        assert items[1]["item"] == "https://test.com/#locations"
        assert items[2]["item"] == "https://test.com/locations/orlando.html"

    def test_city_breadcrumb_with_deployment_url(self):
        """Test breadcrumb uses correct deployment URL"""
        # Set a different deployment URL
        self.config.cloud.deployment_url = "https://cdn.example.com"

        generator = EnhancedCityPageGenerator(self.config)
        schema = generator._generate_breadcrumb_schema(
            "Miami",
            "miami"
        )

        items = schema["itemListElement"]

        # Should use deployment URL, not business domain
        assert items[0]["item"] == "https://cdn.example.com"
        assert items[2]["item"] == "https://cdn.example.com/locations/miami.html"

    def test_city_breadcrumb_backlink_site(self):
        """Test breadcrumb for backlink site configuration"""
        # Configure as backlink site
        self.config.cloud.site_type = "backlink_site"
        self.config.cloud.deployment_url = "https://backlink.example.com"

        generator = EnhancedCityPageGenerator(self.config)
        schema = generator._generate_breadcrumb_schema(
            "Tampa",
            "tampa"
        )

        items = schema["itemListElement"]

        # Should use backlink site deployment URL
        assert "backlink.example.com" in items[0]["item"]
        assert "backlink.example.com" in items[2]["item"]


@pytest.mark.unit
class TestSchemaStructure:
    """Test schema structure compliance"""

    def setup_method(self):
        """Set up test fixtures"""
        self.generator = HTMLGenerator()

    def test_breadcrumb_schema_required_fields(self):
        """Test all breadcrumbs have required schema.org fields"""
        page_types = [
            "homepage", "about", "contact", "services", "products", "faq", "privacy"
        ]

        for page_type in page_types:
            schema = self.generator._generate_breadcrumb_schema(
                page_type,
                "https://example.com"
            )

            # Verify required fields
            assert "@context" in schema, f"Missing @context in {page_type}"
            assert "@type" in schema, f"Missing @type in {page_type}"
            assert "itemListElement" in schema, f"Missing itemListElement in {page_type}"

            # Verify type
            assert schema["@type"] == "BreadcrumbList", f"Wrong type in {page_type}"

            # Verify items structure
            for item in schema["itemListElement"]:
                assert "@type" in item, f"Missing @type in item for {page_type}"
                assert item["@type"] == "ListItem", f"Wrong item type in {page_type}"
                assert "position" in item, f"Missing position in {page_type}"
                assert "name" in item, f"Missing name in {page_type}"
                assert "item" in item, f"Missing item URL in {page_type}"

    def test_breadcrumb_positions_sequential(self):
        """Test breadcrumb positions are sequential starting from 1"""
        schema = self.generator._generate_breadcrumb_schema(
            "service-detail",
            "https://example.com",
            page_title="Test Service",
            page_url="https://example.com/services/test.html"
        )

        items = schema["itemListElement"]

        # Verify positions are sequential
        for i, item in enumerate(items, start=1):
            assert item["position"] == i, f"Position {i} incorrect"

    def test_breadcrumb_urls_valid(self):
        """Test all breadcrumb URLs are properly formatted"""
        schema = self.generator._generate_breadcrumb_schema(
            "product-detail",
            "https://example.com",
            page_title="Test Product",
            page_url="https://example.com/products/test.html"
        )

        items = schema["itemListElement"]

        # Verify all URLs start with base URL
        for item in items:
            assert item["item"].startswith("https://example.com"), \
                f"Invalid URL: {item['item']}"
