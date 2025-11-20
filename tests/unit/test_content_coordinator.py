"""
Module: test_content_coordinator
Path: tests/unit/test_content_coordinator.py

Description:
Unit tests for ContentCoordinator class. Tests content generation
coordination logic, AI service integration, and delegation to specialized generators.

Author: Cloud Stack Generator Team
Created: 2025-11-11
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.core.orchestration.content_coordinator import ContentCoordinator
from src.core.config.models import (
    ClientConfig,
    BusinessConfig,
    ContactConfig,
    BrandingConfig,
    CityPageConfig,
    PlaceOfInterest,
    CityFAQItem
)


@pytest.fixture
def mock_ai_service():
    """Fixture for mock AI service"""
    service = Mock()
    service.generate_content = Mock(return_value="AI generated content")
    return service


@pytest.fixture
def mock_content_cache():
    """Fixture for mock content cache"""
    cache = Mock()
    cache.get = Mock(return_value=None)
    cache.set = Mock()
    return cache


@pytest.fixture
def sample_config():
    """Fixture for sample client configuration"""
    return ClientConfig(
        business=BusinessConfig(
            business_name="Test Business",
            industry="Technology",
            tagline="Testing Excellence"
        ),
        contact=ContactConfig(
            phone="555-0100",
            email="test@example.com",
            address="123 Test St"
        ),
        branding=BrandingConfig(
            primary_color="#0066cc",
            logo_url="logo.png"
        ),
        target_cities=["TestCity", "SampleTown"]
    )


@pytest.fixture
def sample_city_page():
    """Fixture for sample city page configuration"""
    return CityPageConfig(
        city_name="TestCity",
        slug="testcity",
        title="TestCity Services - Test Business",
        meta_description="Professional services in TestCity",
        hero_title="Welcome to TestCity",
        about_city="TestCity is a great place for business.",
        seo_content_title="Our TestCity Services",
        seo_content_body="We provide excellent services in TestCity.\n\nOur team is dedicated to quality.",
        service_area_note="Proudly serving TestCity and surrounding areas",
        places_of_interest=[
            PlaceOfInterest(
                name="City Hall",
                embed_url="https://example.com/map/cityhall"
            )
        ],
        city_faq=[
            CityFAQItem(
                question="What services do you offer?",
                answer="We offer comprehensive technology services."
            )
        ]
    )


class TestContentCoordinatorInitialization:
    """Test ContentCoordinator initialization"""

    def test_coordinator_initialization_with_services(self, mock_ai_service, mock_content_cache):
        """Test coordinator initializes with AI service and cache"""
        coordinator = ContentCoordinator(
            ai_service=mock_ai_service,
            content_cache=mock_content_cache
        )

        assert coordinator.ai_service == mock_ai_service
        assert coordinator.content_cache == mock_content_cache

    def test_coordinator_initialization_without_services(self):
        """Test coordinator initializes without AI service and cache"""
        coordinator = ContentCoordinator()

        assert coordinator.ai_service is None
        assert coordinator.content_cache is None

    def test_coordinator_initialization_with_only_ai_service(self, mock_ai_service):
        """Test coordinator initializes with only AI service"""
        coordinator = ContentCoordinator(ai_service=mock_ai_service)

        assert coordinator.ai_service == mock_ai_service
        assert coordinator.content_cache is None


class TestHomePageGeneration:
    """Test home page generation coordination"""

    @patch('src.core.orchestration.content_coordinator.HTMLGenerator')
    def test_generate_home_page_delegates_to_html_generator(
        self,
        mock_html_generator_class,
        sample_config,
        mock_ai_service,
        mock_content_cache
    ):
        """Test generate_home_page delegates to HTMLGenerator"""
        # Setup mock
        mock_html_generator = Mock()
        mock_html_generator.generate_homepage = Mock(return_value="<html>Home Page</html>")
        mock_html_generator_class.return_value = mock_html_generator

        # Create coordinator and generate
        coordinator = ContentCoordinator(
            ai_service=mock_ai_service,
            content_cache=mock_content_cache
        )
        result = coordinator.generate_home_page(sample_config, use_ai=True)

        # Verify HTMLGenerator was created with correct params
        mock_html_generator_class.assert_called_once_with(
            ai_service=mock_ai_service,
            cache=mock_content_cache
        )

        # Verify generate_homepage was called
        mock_html_generator.generate_homepage.assert_called_once_with(
            sample_config,
            use_ai=True
        )

        # Verify result
        assert result == "<html>Home Page</html>"

    @patch('src.core.orchestration.content_coordinator.HTMLGenerator')
    def test_generate_home_page_without_ai(
        self,
        mock_html_generator_class,
        sample_config
    ):
        """Test generate_home_page with use_ai=False"""
        # Setup mock
        mock_html_generator = Mock()
        mock_html_generator.generate_homepage = Mock(return_value="<html>Basic Home</html>")
        mock_html_generator_class.return_value = mock_html_generator

        # Create coordinator and generate
        coordinator = ContentCoordinator()
        result = coordinator.generate_home_page(sample_config, use_ai=False)

        # Verify generate_homepage was called with use_ai=False
        mock_html_generator.generate_homepage.assert_called_once_with(
            sample_config,
            use_ai=False
        )

        assert result == "<html>Basic Home</html>"


class TestCityPagesGeneration:
    """Test city pages generation coordination"""

    @patch('src.core.orchestration.content_coordinator.CityPageGenerator')
    def test_generate_city_pages_delegates_to_city_generator(
        self,
        mock_city_generator_class,
        sample_config,
        mock_ai_service,
        mock_content_cache,
        tmp_path
    ):
        """Test generate_city_pages delegates to CityPageGenerator"""
        # Setup mock
        mock_city_generator = Mock()
        mock_city_generator.generate_all_city_pages = Mock(
            return_value=["city1.html", "city2.html"]
        )
        mock_city_generator_class.return_value = mock_city_generator

        # Create coordinator and generate
        coordinator = ContentCoordinator(
            ai_service=mock_ai_service,
            content_cache=mock_content_cache
        )
        result = coordinator.generate_city_pages(
            sample_config,
            str(tmp_path),
            use_ai=True
        )

        # Verify CityPageGenerator was created with correct params
        mock_city_generator_class.assert_called_once_with(
            sample_config,
            ai_service=mock_ai_service,
            cache=mock_content_cache
        )

        # Verify generate_all_city_pages was called
        mock_city_generator.generate_all_city_pages.assert_called_once_with(
            str(tmp_path),
            use_ai=True
        )

        # Verify result
        assert result == ["city1.html", "city2.html"]

    @patch('src.core.orchestration.content_coordinator.CityPageGenerator')
    def test_generate_city_pages_without_ai(
        self,
        mock_city_generator_class,
        sample_config,
        tmp_path
    ):
        """Test generate_city_pages with use_ai=False"""
        # Setup mock
        mock_city_generator = Mock()
        mock_city_generator.generate_all_city_pages = Mock(
            return_value=["city1.html"]
        )
        mock_city_generator_class.return_value = mock_city_generator

        # Create coordinator and generate
        coordinator = ContentCoordinator()
        result = coordinator.generate_city_pages(
            sample_config,
            str(tmp_path),
            use_ai=False
        )

        # Verify generate_all_city_pages was called with use_ai=False
        mock_city_generator.generate_all_city_pages.assert_called_once_with(
            str(tmp_path),
            use_ai=False
        )

        assert result == ["city1.html"]


class TestSingleCityPageGeneration:
    """Test single city page generation"""

    def test_generate_single_city_page_creates_html_file(
        self,
        sample_config,
        sample_city_page,
        tmp_path
    ):
        """Test generate_single_city_page creates HTML file"""
        coordinator = ContentCoordinator()

        # Generate city page
        result = coordinator.generate_single_city_page(
            sample_config,
            sample_city_page,
            str(tmp_path)
        )

        # Verify file was created
        expected_path = tmp_path / "testcity.html"
        assert Path(result) == expected_path
        assert expected_path.exists()

        # Verify content
        content = expected_path.read_text(encoding="utf-8")
        assert "TestCity" in content
        assert "Test Business" in content
        assert sample_city_page.about_city in content

    def test_generate_single_city_page_includes_places_of_interest(
        self,
        sample_config,
        sample_city_page,
        tmp_path
    ):
        """Test city page includes places of interest"""
        coordinator = ContentCoordinator()

        result = coordinator.generate_single_city_page(
            sample_config,
            sample_city_page,
            str(tmp_path)
        )

        content = Path(result).read_text(encoding="utf-8")
        assert "Places of Interest" in content
        assert "City Hall" in content
        assert sample_city_page.places_of_interest[0].embed_url in content

    def test_generate_single_city_page_includes_faq(
        self,
        sample_config,
        sample_city_page,
        tmp_path
    ):
        """Test city page includes FAQ section"""
        coordinator = ContentCoordinator()

        result = coordinator.generate_single_city_page(
            sample_config,
            sample_city_page,
            str(tmp_path)
        )

        content = Path(result).read_text(encoding="utf-8")
        assert "Frequently Asked Questions" in content
        assert sample_city_page.city_faq[0].question in content
        assert sample_city_page.city_faq[0].answer in content

    def test_generate_single_city_page_includes_contact_info(
        self,
        sample_config,
        sample_city_page,
        tmp_path
    ):
        """Test city page includes contact information"""
        coordinator = ContentCoordinator()

        result = coordinator.generate_single_city_page(
            sample_config,
            sample_city_page,
            str(tmp_path)
        )

        content = Path(result).read_text(encoding="utf-8")
        assert sample_config.contact.phone in content
        assert sample_config.contact.email in content

    def test_generate_single_city_page_without_optional_sections(
        self,
        sample_config,
        tmp_path
    ):
        """Test city page generation without optional sections"""
        # Create minimal city page
        minimal_city_page = CityPageConfig(
            city_name="MinimalCity",
            slug="minimal",
            about_city="Minimal city description",
            seo_content_body="Basic content"
        )

        coordinator = ContentCoordinator()
        result = coordinator.generate_single_city_page(
            sample_config,
            minimal_city_page,
            str(tmp_path)
        )

        content = Path(result).read_text(encoding="utf-8")
        assert "MinimalCity" in content
        assert "Minimal city description" in content
        # Optional sections should not be present
        assert "Places of Interest" not in content
        assert "Frequently Asked Questions" not in content


class TestContentFormatting:
    """Test content formatting helper methods"""

    def test_format_content_body_with_paragraphs(self):
        """Test _format_content_body splits and formats paragraphs"""
        coordinator = ContentCoordinator()

        content = "First paragraph.\n\nSecond paragraph.\n\nThird paragraph."
        result = coordinator._format_content_body(content)

        assert "<p>First paragraph.</p>" in result
        assert "<p>Second paragraph.</p>" in result
        assert "<p>Third paragraph.</p>" in result

    def test_format_content_body_with_empty_content(self):
        """Test _format_content_body handles empty content"""
        coordinator = ContentCoordinator()

        result = coordinator._format_content_body("")

        assert result == ""

    def test_format_content_body_with_whitespace(self):
        """Test _format_content_body handles whitespace"""
        coordinator = ContentCoordinator()

        content = "   \n\n   Paragraph with whitespace   \n\n   "
        result = coordinator._format_content_body(content)

        assert "<p>Paragraph with whitespace</p>" in result
        assert result.count("<p>") == 1  # Only one non-empty paragraph


class TestSlugGeneration:
    """Test slug generation from city names"""

    def test_create_slug_basic(self):
        """Test _create_slug with basic city name"""
        coordinator = ContentCoordinator()

        assert coordinator._create_slug("New York") == "new-york"
        assert coordinator._create_slug("Los Angeles") == "los-angeles"
        assert coordinator._create_slug("Chicago") == "chicago"

    def test_create_slug_with_special_characters(self):
        """Test _create_slug removes special characters"""
        coordinator = ContentCoordinator()

        assert coordinator._create_slug("St. Louis") == "st-louis"
        assert coordinator._create_slug("O'Fallon") == "ofallon"
        assert coordinator._create_slug("Coeur d'Alene") == "coeur-dalene"

    def test_create_slug_with_multiple_spaces(self):
        """Test _create_slug handles multiple spaces"""
        coordinator = ContentCoordinator()

        assert coordinator._create_slug("Salt   Lake   City") == "salt-lake-city"

    def test_create_slug_with_mixed_case(self):
        """Test _create_slug converts to lowercase"""
        coordinator = ContentCoordinator()

        assert coordinator._create_slug("SAN FRANCISCO") == "san-francisco"
        assert coordinator._create_slug("SeAtTlE") == "seattle"


class TestEnhancedCityHTMLGeneration:
    """Test enhanced city HTML generation"""

    def test_create_enhanced_city_html_structure(self, sample_config, sample_city_page):
        """Test _create_enhanced_city_html creates valid HTML structure"""
        coordinator = ContentCoordinator()

        html = coordinator._create_enhanced_city_html(sample_city_page, sample_config)

        # Check basic HTML structure
        assert "<!DOCTYPE html>" in html
        assert "<html lang=\"en\">" in html
        assert "<head>" in html
        assert "<body>" in html
        assert "</html>" in html

    def test_create_enhanced_city_html_includes_meta_tags(self, sample_config, sample_city_page):
        """Test HTML includes proper meta tags"""
        coordinator = ContentCoordinator()

        html = coordinator._create_enhanced_city_html(sample_city_page, sample_config)

        assert "<meta charset=\"UTF-8\">" in html
        assert "<meta name=\"viewport\"" in html
        assert sample_city_page.meta_description in html

    def test_create_enhanced_city_html_includes_business_name(self, sample_config, sample_city_page):
        """Test HTML includes business name"""
        coordinator = ContentCoordinator()

        html = coordinator._create_enhanced_city_html(sample_city_page, sample_config)

        assert sample_config.business.business_name in html

    def test_create_enhanced_city_html_includes_hero_section(self, sample_config, sample_city_page):
        """Test HTML includes hero section"""
        coordinator = ContentCoordinator()

        html = coordinator._create_enhanced_city_html(sample_city_page, sample_config)

        assert 'class="hero"' in html
        assert sample_city_page.hero_title in html

    def test_create_enhanced_city_html_uses_default_titles(self, sample_config):
        """Test HTML uses default titles when not provided"""
        # Create city page without custom titles
        city_page = CityPageConfig(
            city_name="DefaultCity",
            about_city="City description"
        )

        coordinator = ContentCoordinator()
        html = coordinator._create_enhanced_city_html(city_page, sample_config)

        # Check that city name and business name appear in the HTML
        assert "DefaultCity" in html
        assert sample_config.business.business_name in html
        assert "Professional Services in DefaultCity" in html
