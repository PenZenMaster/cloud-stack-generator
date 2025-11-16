"""
Unit tests for meta tags feature - complete pipeline testing

Tests the full meta tags data flow:
1. CloudConfig model stores meta_tags
2. ConfigParser saves cloud section to YAML
3. ConfigParser loads cloud section from YAML
4. HTMLGenerator passes cloud to template context
5. Generated HTML includes meta tags in <head>

Author: Cloud Stack Generator Team
Created: 2025-11-15
Version: 1.0.0
"""

import pytest
import tempfile
from pathlib import Path
from typing import Dict, Any

from src.core.config.models import CloudConfig, ClientConfig, BusinessConfig, ContactConfig, BrandingConfig, AddressConfig
from src.core.config.parser import ConfigParser
from src.core.generators.html_generator import HTMLGenerator


class TestMetaTagsConfigModel:
    """Test CloudConfig model with meta_tags"""

    def test_cloud_config_default_meta_tags(self):
        """Test CloudConfig initializes with empty meta_tags dict"""
        cloud = CloudConfig()
        assert hasattr(cloud, 'meta_tags')
        assert cloud.meta_tags == {}

    def test_cloud_config_with_meta_tags(self):
        """Test CloudConfig accepts meta_tags dictionary"""
        meta_tags = {
            "google-site-verification": "test123",
            "facebook-domain-verification": "test456"
        }
        cloud = CloudConfig(meta_tags=meta_tags)
        assert cloud.meta_tags == meta_tags
        assert cloud.meta_tags["google-site-verification"] == "test123"

    def test_cloud_config_meta_tags_multiple_entries(self):
        """Test CloudConfig can store multiple meta tags"""
        meta_tags = {
            "google-site-verification": "xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU",
            "facebook-domain-verification": "abcd1234efgh5678",
            "msvalidate.01": "1234567890ABCDEF",
            "p:domain_verify": "pinterest123"
        }
        cloud = CloudConfig(meta_tags=meta_tags)
        assert len(cloud.meta_tags) == 4
        assert all(key in cloud.meta_tags for key in meta_tags.keys())


class TestMetaTagsConfigSaveLoad:
    """Test ConfigParser save/load cycle with meta_tags"""

    @pytest.fixture
    def sample_config_with_meta_tags(self):
        """Create a minimal ClientConfig with meta_tags"""
        return ClientConfig(
            business=BusinessConfig(
                business_name="Test Business",
                domain="testbusiness.com",
                industry="Testing"
            ),
            contact=ContactConfig(
                phone="555-1234",
                address=AddressConfig(
                    street="123 Test St",
                    city="Test City",
                    state="TS",
                    zip_code="12345"
                )
            ),
            branding=BrandingConfig(),
            cloud=CloudConfig(
                aws_profile="test-profile",
                bucket_name="test-bucket",
                distribution_id="E3VQJQK8Z5Z5Z5",
                auto_invalidate_cache=True,
                meta_tags={
                    "google-site-verification": "xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU",
                    "facebook-domain-verification": "abcd1234"
                }
            )
        )

    def test_save_config_includes_cloud_section(self, sample_config_with_meta_tags):
        """Test that saving config includes cloud section in YAML"""
        parser = ConfigParser()
        yaml_dict = parser.generate_yaml_dict(sample_config_with_meta_tags)

        assert "cloud" in yaml_dict
        assert "meta_tags" in yaml_dict["cloud"]

    def test_save_config_preserves_meta_tags(self, sample_config_with_meta_tags):
        """Test that meta_tags are correctly saved to YAML"""
        parser = ConfigParser()
        yaml_dict = parser.generate_yaml_dict(sample_config_with_meta_tags)

        meta_tags = yaml_dict["cloud"]["meta_tags"]
        assert meta_tags["google-site-verification"] == "xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU"
        assert meta_tags["facebook-domain-verification"] == "abcd1234"

    def test_save_load_roundtrip_preserves_meta_tags(self, sample_config_with_meta_tags, tmp_path):
        """Test complete save/load cycle preserves meta_tags"""
        parser = ConfigParser()

        # Save to temporary file
        config_file = tmp_path / "test_config.yaml"
        success = parser.save_yaml_file(sample_config_with_meta_tags, str(config_file))
        assert success

        # Load back from file
        loaded_config = parser.parse_yaml_file(str(config_file))

        # Verify meta_tags survived the round trip
        assert loaded_config.cloud.meta_tags == sample_config_with_meta_tags.cloud.meta_tags
        assert loaded_config.cloud.meta_tags["google-site-verification"] == "xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU"

    def test_load_config_parses_cloud_section(self, tmp_path):
        """Test that loading config correctly parses cloud section from YAML"""
        # Create YAML file with cloud section
        yaml_content = """
client:
  business_name: Test Business
  domain: testbusiness.com
  industry: Testing
  contact:
    phone: 555-1234
    address:
      street: 123 Test St
      city: Test City
      state: TS
      zip_code: "12345"
  branding:
    primary_color: "#007bff"

cloud:
  aws_profile: test-profile
  aws_region: us-east-1
  bucket_name: test-bucket
  distribution_id: E3VQJQK8Z5Z5Z5
  auto_invalidate_cache: true
  meta_tags:
    google-site-verification: xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU
    facebook-domain-verification: abcd1234
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(yaml_content)

        # Load and verify
        parser = ConfigParser()
        loaded_config = parser.parse_yaml_file(str(config_file))

        assert loaded_config.cloud is not None
        assert loaded_config.cloud.meta_tags is not None
        assert len(loaded_config.cloud.meta_tags) == 2
        assert loaded_config.cloud.meta_tags["google-site-verification"] == "xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU"

    def test_load_config_without_cloud_section_creates_default(self, tmp_path):
        """Test that loading config without cloud section creates default CloudConfig"""
        yaml_content = """
client:
  business_name: Test Business
  domain: testbusiness.com
  industry: Testing
  contact:
    phone: 555-1234
    address:
      street: 123 Test St
      city: Test City
      state: TS
      zip_code: "12345"
"""
        config_file = tmp_path / "test_config.yaml"
        config_file.write_text(yaml_content)

        parser = ConfigParser()
        loaded_config = parser.parse_yaml_file(str(config_file))

        # Should have default CloudConfig with empty meta_tags
        assert loaded_config.cloud is not None
        assert loaded_config.cloud.meta_tags == {}


class TestMetaTagsTemplateContext:
    """Test that cloud object is passed to template context"""

    @pytest.fixture
    def html_generator(self):
        """Create HTMLGenerator instance"""
        return HTMLGenerator()

    @pytest.fixture
    def config_with_meta_tags(self):
        """Create ClientConfig with meta_tags for template testing"""
        return ClientConfig(
            business=BusinessConfig(
                business_name="Test Business",
                domain="testbusiness.com",
                industry="Testing",
                description="Test description"
            ),
            contact=ContactConfig(
                phone="555-1234",
                address=AddressConfig(
                    street="123 Test St",
                    city="Test City",
                    state="TS",
                    zip_code="12345"
                )
            ),
            branding=BrandingConfig(),
            cloud=CloudConfig(
                deployment_url="https://testbusiness.com",
                meta_tags={
                    "google-site-verification": "test123",
                    "facebook-domain-verification": "test456"
                }
            )
        )

    def test_prepare_template_data_includes_cloud(self, html_generator, config_with_meta_tags):
        """Test that _prepare_template_data includes cloud object"""
        template_data = html_generator._prepare_template_data(config_with_meta_tags)

        assert "cloud" in template_data
        assert template_data["cloud"] is not None

    def test_prepare_template_data_cloud_has_meta_tags(self, html_generator, config_with_meta_tags):
        """Test that cloud object in template data contains meta_tags"""
        template_data = html_generator._prepare_template_data(config_with_meta_tags)

        assert hasattr(template_data["cloud"], "meta_tags")
        assert template_data["cloud"].meta_tags == config_with_meta_tags.cloud.meta_tags

    def test_homepage_generation_has_cloud_context(self, html_generator, config_with_meta_tags):
        """Test that homepage generation receives cloud in context"""
        # Generate homepage HTML
        html = html_generator.generate_homepage(config_with_meta_tags, use_ai=False)

        # HTML should be generated successfully
        assert html is not None
        assert len(html) > 0


class TestMetaTagsHTMLGeneration:
    """Test that meta tags appear in generated HTML"""

    @pytest.fixture
    def html_generator(self):
        """Create HTMLGenerator instance"""
        return HTMLGenerator()

    @pytest.fixture
    def config_with_google_verification(self):
        """Config with Google Site Verification meta tag"""
        return ClientConfig(
            business=BusinessConfig(
                business_name="Test Business",
                domain="testbusiness.com",
                industry="Testing",
                description="Professional testing services"
            ),
            contact=ContactConfig(
                phone="555-1234",
                address=AddressConfig(
                    street="123 Test St",
                    city="Test City",
                    state="TS",
                    zip_code="12345"
                )
            ),
            branding=BrandingConfig(),
            cloud=CloudConfig(
                deployment_url="https://testbusiness.com",
                meta_tags={
                    "google-site-verification": "xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU"
                }
            )
        )

    def test_generated_html_contains_meta_tags(self, html_generator, config_with_google_verification):
        """Test that generated HTML contains meta tags in <head>"""
        html = html_generator.generate_homepage(config_with_google_verification, use_ai=False)

        # Check for Google verification meta tag
        assert 'name="google-site-verification"' in html
        assert 'content="xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU"' in html

    def test_generated_html_meta_tag_in_head_section(self, html_generator, config_with_google_verification):
        """Test that meta tag appears in <head> section"""
        html = html_generator.generate_homepage(config_with_google_verification, use_ai=False)

        # Extract head section
        head_start = html.find("<head>")
        head_end = html.find("</head>")
        assert head_start >= 0 and head_end > head_start

        head_section = html[head_start:head_end]

        # Meta tag should be in head section
        assert 'name="google-site-verification"' in head_section
        assert 'content="xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU"' in head_section

    def test_generated_html_multiple_meta_tags(self, html_generator):
        """Test that multiple meta tags are all included"""
        config = ClientConfig(
            business=BusinessConfig(
                business_name="Test Business",
                domain="testbusiness.com",
                industry="Testing",
                description="Professional testing services"
            ),
            contact=ContactConfig(
                phone="555-1234",
                address=AddressConfig(
                    street="123 Test St",
                    city="Test City",
                    state="TS",
                    zip_code="12345"
                )
            ),
            branding=BrandingConfig(),
            cloud=CloudConfig(
                deployment_url="https://testbusiness.com",
                meta_tags={
                    "google-site-verification": "google123",
                    "facebook-domain-verification": "facebook456",
                    "msvalidate.01": "microsoft789"
                }
            )
        )

        html = html_generator.generate_homepage(config, use_ai=False)

        # All three meta tags should be present
        assert 'name="google-site-verification"' in html
        assert 'content="google123"' in html
        assert 'name="facebook-domain-verification"' in html
        assert 'content="facebook456"' in html
        assert 'name="msvalidate.01"' in html
        assert 'content="microsoft789"' in html

    def test_generated_html_no_meta_tags_when_empty(self, html_generator):
        """Test that no custom meta tags appear when meta_tags is empty"""
        config = ClientConfig(
            business=BusinessConfig(
                business_name="Test Business",
                domain="testbusiness.com",
                industry="Testing",
                description="Professional testing services"
            ),
            contact=ContactConfig(
                phone="555-1234",
                address=AddressConfig(
                    street="123 Test St",
                    city="Test City",
                    state="TS",
                    zip_code="12345"
                )
            ),
            branding=BrandingConfig(),
            cloud=CloudConfig(
                deployment_url="https://testbusiness.com",
                meta_tags={}  # Empty meta_tags
            )
        )

        html = html_generator.generate_homepage(config, use_ai=False)

        # Should not contain verification meta tags
        assert 'name="google-site-verification"' not in html
        assert 'name="facebook-domain-verification"' not in html


class TestMetaTagsEdgeCases:
    """Test edge cases and error handling for meta tags"""

    def test_meta_tags_with_special_characters(self):
        """Test meta tags with special characters in content"""
        cloud = CloudConfig(
            meta_tags={
                "test-tag": "value with spaces & special chars: <>\"'"
            }
        )
        assert cloud.meta_tags["test-tag"] == "value with spaces & special chars: <>\"'"

    def test_meta_tags_with_unicode(self):
        """Test meta tags can handle unicode characters"""
        cloud = CloudConfig(
            meta_tags={
                "description": "Testing with unicode: café résumé naïve"
            }
        )
        assert "café" in cloud.meta_tags["description"]

    def test_meta_tags_with_very_long_content(self):
        """Test meta tags with very long content values"""
        long_content = "a" * 1000
        cloud = CloudConfig(
            meta_tags={
                "long-tag": long_content
            }
        )
        assert len(cloud.meta_tags["long-tag"]) == 1000

    def test_empty_meta_tag_name(self):
        """Test that empty meta tag names are stored (template should handle)"""
        cloud = CloudConfig(
            meta_tags={
                "": "empty-name-value"
            }
        )
        assert "" in cloud.meta_tags

    def test_empty_meta_tag_content(self):
        """Test that empty meta tag content is stored"""
        cloud = CloudConfig(
            meta_tags={
                "empty-content": ""
            }
        )
        assert cloud.meta_tags["empty-content"] == ""
