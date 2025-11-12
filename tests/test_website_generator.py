"""
Test suite for website_generator.py (Facade)
Tests backward compatibility of WebsiteGenerator facade

Version: 2.0.0
Date: 2025-11-11
Author: Cloud Stack Generator Team
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.core.website_generator import WebsiteGenerator, GenerationError, GenerationResult
    from src.core.config.models import (
        ClientConfig,
        BusinessConfig,
        ContactConfig,
        BrandingConfig,
        AddressConfig
    )
except ImportError as e:
    # Skip tests if modules not implemented yet
    pytest.skip(f"Website generator dependencies not available: {e}", allow_module_level=True)


@pytest.fixture
def sample_config():
    """Fixture for sample client configuration"""
    return ClientConfig(
        business=BusinessConfig(
            business_name="Acme Professional Services",
            industry="Technology",
            tagline="Excellence in Service"
        ),
        contact=ContactConfig(
            phone="+1-555-123-4567",
            email="contact@acme.com",
            address=AddressConfig(
                street="123 Tech Street",
                city="TestCity",
                state="CA",
                zip_code="12345"
            )
        ),
        branding=BrandingConfig(
            primary_color="#0066cc",
            logo_url="logo.png"
        ),
        target_cities=["TestCity"]
    )


class TestWebsiteGeneratorFacade:
    """Test suite for WebsiteGenerator facade backward compatibility"""

    def test_website_generator_exists(self):
        """Test that WebsiteGenerator class exists"""
        generator = WebsiteGenerator()
        assert generator is not None

    def test_facade_has_correct_attributes(self):
        """Test that facade exposes expected attributes for backward compatibility"""
        generator = WebsiteGenerator(use_ai=False)

        # Check legacy attributes
        assert hasattr(generator, 'output_dir')
        assert hasattr(generator, 'config')
        assert hasattr(generator, 'use_ai')
        assert hasattr(generator, 'ai_service')
        assert hasattr(generator, 'content_cache')

    def test_generate_delegates_to_orchestrator(self, sample_config, tmp_path):
        """Test that generate() method successfully delegates to orchestrator"""
        generator = WebsiteGenerator(use_ai=False)
        result = generator.generate(sample_config, output_dir=str(tmp_path))

        # Check result
        assert isinstance(result, GenerationResult)
        assert result.success is True
        assert len(result.generated_files) > 0

    def test_generate_creates_index_page(self, sample_config, tmp_path):
        """Test that generation creates index.html"""
        generator = WebsiteGenerator(use_ai=False)
        result = generator.generate(sample_config, output_dir=str(tmp_path))

        # Check that index.html was created
        index_file = tmp_path / "index.html"
        assert index_file.exists()

        # Check basic HTML structure
        content = index_file.read_text()
        assert "<!DOCTYPE html>" in content

    def test_generate_sets_legacy_attributes(self, sample_config, tmp_path):
        """Test that generate() sets legacy instance variables"""
        generator = WebsiteGenerator(use_ai=False)
        result = generator.generate(sample_config, output_dir=str(tmp_path))

        # Check that legacy attributes were set
        assert generator.output_dir == str(tmp_path)
        assert generator.config == sample_config

    def test_error_handling_propagates(self, sample_config):
        """Test that errors from orchestrator are properly propagated"""
        generator = WebsiteGenerator(use_ai=False)

        # Use invalid path that should cause issues
        result = generator.generate(sample_config, output_dir="/invalid\x00path")

        # Should return error result instead of raising
        assert result.success is False
        assert result.errors is not None


class TestGenerationResult:
    """Test the GenerationResult data structure"""

    def test_generation_result_success(self):
        """Test GenerationResult for successful generation"""
        result = GenerationResult(
            success=True,
            generated_files=["index.html", "about.html"],
            errors=None
        )

        assert result.success is True
        assert len(result.generated_files) == 2
        assert result.errors is None

    def test_generation_result_with_errors(self):
        """Test GenerationResult with errors"""
        result = GenerationResult(
            success=False,
            generated_files=[],
            errors="Template not found"
        )

        assert result.success is False
        assert result.errors == "Template not found"


class TestBackwardCompatibilityImports:
    """Test that legacy imports still work"""

    def test_can_import_website_generator(self):
        """Test importing WebsiteGenerator from core.website_generator"""
        from src.core.website_generator import WebsiteGenerator
        assert WebsiteGenerator is not None

    def test_can_import_generation_error(self):
        """Test importing GenerationError"""
        from src.core.website_generator import GenerationError
        assert GenerationError is not None

    def test_can_import_generation_result(self):
        """Test importing GenerationResult"""
        from src.core.website_generator import GenerationResult
        assert GenerationResult is not None

    def test_generation_error_is_exception(self):
        """Test that GenerationError is an Exception"""
        from src.core.website_generator import GenerationError
        assert issubclass(GenerationError, Exception)

    def test_can_instantiate_and_use_generator(self, sample_config, tmp_path):
        """Test full workflow using only legacy imports"""
        from src.core.website_generator import WebsiteGenerator

        generator = WebsiteGenerator(use_ai=False)
        result = generator.generate(sample_config, str(tmp_path))

        assert result.success is True
