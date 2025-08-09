"""
Test suite for website_generator.py
Following TDD approach - these tests define the expected website generation behavior

Version: 1.0.1
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.core.website_generator import WebsiteGenerator, GenerationError
    from src.core.config_parser import ConfigParser
except ImportError:
    # Skip tests if modules not implemented yet
    pytest.skip("Website generator not implemented yet", allow_module_level=True)


class TestWebsiteGenerator:
    """Test suite for website generation functionality"""

    def test_website_generator_exists(self):
        """Test that WebsiteGenerator class exists"""
        generator = WebsiteGenerator()
        assert generator is not None

    def test_generate_single_page(self, sample_config_dict, temp_dir):
        """Test generating a single HTML page"""
        # Parse config
        parser = ConfigParser()
        config = parser.parse(sample_config_dict)

        # Generate website
        generator = WebsiteGenerator()
        result = generator.generate(config, output_dir=str(temp_dir))

        # Check that files were created
        assert result.success is True
        assert len(result.generated_files) > 0

        # Check that index.html exists
        index_file = temp_dir / "index.html"
        assert index_file.exists()

        # Check basic HTML structure
        content = index_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Acme Professional Services" in content
        assert "+1-555-123-4567" in content

    def test_generate_multiple_pages(self, sample_config_dict, temp_dir):
        """Test generating multiple pages from config"""
        parser = ConfigParser()
        config = parser.parse(sample_config_dict)

        generator = WebsiteGenerator()
        result = generator.generate(config, output_dir=str(temp_dir))

        # Should generate one file per page
        expected_files = ["index.html", "about.html"]
        for filename in expected_files:
            file_path = temp_dir / filename
            assert file_path.exists(), f"Missing file: {filename}"

        assert len(result.generated_files) >= len(expected_files)

    def test_error_handling_invalid_output_dir(self, sample_config_dict):
        """Test error handling for invalid output directory"""
        parser = ConfigParser()
        config = parser.parse(sample_config_dict)

        generator = WebsiteGenerator()

        with pytest.raises(GenerationError):
            generator.generate(config, output_dir="/invalid/readonly/path")

    def test_template_rendering(self, sample_config_dict):
        """Test that Jinja2 templates are properly rendered"""
        parser = ConfigParser()
        config = parser.parse(sample_config_dict)

        generator = WebsiteGenerator()

        # Test template rendering with sample data
        template_content = "Hello {{ client.business_name }}!"
        rendered = generator.render_template(template_content, config=config)

        assert rendered == "Hello Acme Professional Services!"


class TestGenerationResult:
    """Test the GenerationResult data structure"""

    def test_generation_result_success(self):
        """Test GenerationResult for successful generation"""
        from src.core.website_generator import GenerationResult

        result = GenerationResult(
            success=True,
            generated_files=["index.html", "about.html"],
            output_dir="/path/to/output",
        )

        assert result.success is True
        assert len(result.generated_files) == 2
        assert result.errors == []

    def test_generation_result_with_errors(self):
        """Test GenerationResult with errors"""
        from src.core.website_generator import GenerationResult

        result = GenerationResult(
            success=False,
            generated_files=[],
            output_dir="/path/to/output",
            errors=["Template not found", "Permission denied"],
        )

        assert result.success is False
        assert len(result.errors) == 2
