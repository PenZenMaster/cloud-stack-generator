"""
Unit tests for ContentQualityConfig - YAML round-trip (Issue #38)

Tests the content_quality config section:
1. ContentQualityConfig model defaults
2. CloudConfig carries a content_quality field
3. ConfigParser saves content_quality to YAML only when explicitly configured
4. ConfigParser loads content_quality back from YAML

Author: Cloud Stack Generator Team
Created: 2026-08-08
Version: 1.0.0
"""

import pytest

from src.core.config.models import (
    ContentQualityConfig,
    CloudConfig,
    ClientConfig,
    BusinessConfig,
    ContactConfig,
    BrandingConfig,
    AddressConfig,
)
from src.core.config.parser import ConfigParser


class TestContentQualityConfigModel:
    def test_defaults(self):
        quality = ContentQualityConfig()
        assert quality.warn_threshold == 0.75
        assert quality.block_threshold == 0.85
        assert quality.enable_embeddings is False
        assert quality.max_regeneration_attempts == 2

    def test_not_configured_by_default(self):
        assert ContentQualityConfig().is_configured() is False

    def test_configured_when_customized(self):
        assert ContentQualityConfig(block_threshold=0.9).is_configured() is True

    def test_cloud_config_has_content_quality(self):
        cloud = CloudConfig()
        assert isinstance(cloud.content_quality, ContentQualityConfig)


class TestContentQualityConfigSaveLoad:
    @pytest.fixture
    def sample_config_with_content_quality(self):
        return ClientConfig(
            business=BusinessConfig(
                business_name="Acme Roofing", domain="https://acmeroofing.com", industry="Roofing"
            ),
            contact=ContactConfig(
                phone="555-1234",
                address=AddressConfig(
                    street="123 Test St", city="Test City", state="TS", zip_code="12345"
                ),
            ),
            branding=BrandingConfig(),
            cloud=CloudConfig(
                content_quality=ContentQualityConfig(
                    warn_threshold=0.6,
                    block_threshold=0.8,
                    enable_embeddings=True,
                    max_regeneration_attempts=3,
                ),
            ),
        )

    def test_unconfigured_profile_not_written_to_yaml(self):
        config = ClientConfig(
            business=BusinessConfig(business_name="X", domain="https://x.com", industry="Y"),
            contact=ContactConfig(address=AddressConfig()),
            branding=BrandingConfig(),
            cloud=CloudConfig(),
        )
        parser = ConfigParser()
        yaml_dict = parser.generate_yaml_dict(config)

        assert "content_quality" not in yaml_dict.get("cloud", {})

    def test_configured_profile_written_to_yaml(self, sample_config_with_content_quality):
        parser = ConfigParser()
        yaml_dict = parser.generate_yaml_dict(sample_config_with_content_quality)

        assert "content_quality" in yaml_dict["cloud"]
        assert yaml_dict["cloud"]["content_quality"]["warn_threshold"] == 0.6
        assert yaml_dict["cloud"]["content_quality"]["block_threshold"] == 0.8
        assert yaml_dict["cloud"]["content_quality"]["enable_embeddings"] is True
        assert yaml_dict["cloud"]["content_quality"]["max_regeneration_attempts"] == 3

    def test_roundtrip_preserves_content_quality(self, sample_config_with_content_quality):
        """Round-trips through generate_yaml_dict() -> parse_yaml_dict() -
        see test_anchor_profile_config.py for why this avoids the disk cycle."""
        parser = ConfigParser()
        yaml_dict = parser.generate_yaml_dict(sample_config_with_content_quality)

        loaded = parser.parse_yaml_dict(yaml_dict)

        original = sample_config_with_content_quality.cloud.content_quality
        restored = loaded.cloud.content_quality

        assert restored.warn_threshold == original.warn_threshold
        assert restored.block_threshold == original.block_threshold
        assert restored.enable_embeddings == original.enable_embeddings
        assert restored.max_regeneration_attempts == original.max_regeneration_attempts

    def test_load_without_content_quality_section_uses_defaults(self, tmp_path):
        yaml_content = """
client:
  business_name: Test Business
  domain: https://testbusiness.com
  industry: Testing
  contact:
    phone: "555-1234"
    address:
      street: "123 Test St"
      city: Test City
      state: TS
      zip_code: "12345"

cloud:
  site_type: backlink_site
  main_site_url: https://testbusiness.com
"""
        config_file = tmp_path / "no_content_quality.yaml"
        config_file.write_text(yaml_content)

        parser = ConfigParser()
        loaded = parser.parse_yaml_file(str(config_file))

        assert isinstance(loaded.cloud.content_quality, ContentQualityConfig)
        assert loaded.cloud.content_quality.is_configured() is False
        assert loaded.cloud.content_quality.warn_threshold == 0.75
