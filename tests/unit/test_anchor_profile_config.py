"""
Unit tests for AnchorProfileConfig - complete pipeline testing

Tests the full anchor_profile data flow (Issue #37):
1. AnchorProfileConfig model defaults and construction
2. CloudConfig carries an anchor_profile field
3. ConfigParser saves anchor_profile to YAML only when explicitly configured
4. ConfigParser loads anchor_profile back from YAML
5. Full save/load round trip preserves distribution, pools, seed

Author: Cloud Stack Generator Team
Created: 2026-08-07
Version: 1.0.0
"""

import pytest

from src.core.config.models import (
    AnchorProfileConfig,
    CloudConfig,
    ClientConfig,
    BusinessConfig,
    ContactConfig,
    BrandingConfig,
    AddressConfig,
)
from src.core.config.parser import ConfigParser


class TestAnchorProfileConfigModel:
    """Test AnchorProfileConfig model defaults"""

    def test_default_distribution_sums_to_100(self):
        profile = AnchorProfileConfig()
        assert sum(profile.distribution.values()) == 100

    def test_default_pools_are_empty(self):
        profile = AnchorProfileConfig()
        assert profile.pools == {}
        assert profile.is_configured() is False

    def test_configured_when_pools_present(self):
        profile = AnchorProfileConfig(pools={"branded": ["Acme"]})
        assert profile.is_configured() is True

    def test_default_exact_match_ceiling(self):
        profile = AnchorProfileConfig()
        assert profile.exact_match_ceiling == 10

    def test_cloud_config_has_anchor_profile(self):
        cloud = CloudConfig()
        assert isinstance(cloud.anchor_profile, AnchorProfileConfig)


class TestAnchorProfileConfigSaveLoad:
    """Test ConfigParser save/load cycle with anchor_profile"""

    @pytest.fixture
    def sample_config_with_anchor_profile(self):
        return ClientConfig(
            business=BusinessConfig(
                business_name="Acme Roofing",
                domain="https://acmeroofing.com",
                industry="Roofing",
            ),
            contact=ContactConfig(
                phone="555-1234",
                address=AddressConfig(
                    street="123 Test St", city="Test City", state="TS", zip_code="12345"
                ),
            ),
            branding=BrandingConfig(),
            cloud=CloudConfig(
                site_type="backlink_site",
                main_site_url="https://acmeroofing.com",
                anchor_profile=AnchorProfileConfig(
                    distribution={
                        "branded": 35, "naked_url": 15, "generic": 25,
                        "partial_match": 20, "exact_match": 5,
                    },
                    pools={
                        "branded": ["Acme Roofing", "Acme"],
                        "generic": ["visit their website", "learn more"],
                    },
                    seed=20260807,
                    exact_match_ceiling=8,
                ),
            ),
        )

    def test_unconfigured_profile_is_not_written_to_yaml(self):
        """Default (unconfigured) anchor_profile shouldn't clutter every config file"""
        config = ClientConfig(
            business=BusinessConfig(business_name="X", domain="https://x.com", industry="Y"),
            contact=ContactConfig(address=AddressConfig()),
            branding=BrandingConfig(),
            cloud=CloudConfig(),
        )
        parser = ConfigParser()
        yaml_dict = parser.generate_yaml_dict(config)

        assert "anchor_profile" not in yaml_dict.get("cloud", {})

    def test_configured_profile_is_written_to_yaml(self, sample_config_with_anchor_profile):
        parser = ConfigParser()
        yaml_dict = parser.generate_yaml_dict(sample_config_with_anchor_profile)

        assert "anchor_profile" in yaml_dict["cloud"]
        assert yaml_dict["cloud"]["anchor_profile"]["seed"] == 20260807
        assert yaml_dict["cloud"]["anchor_profile"]["distribution"]["branded"] == 35
        assert yaml_dict["cloud"]["anchor_profile"]["pools"]["branded"] == ["Acme Roofing", "Acme"]

    def test_save_load_roundtrip_preserves_anchor_profile(self, sample_config_with_anchor_profile):
        """
        Round-trips through generate_yaml_dict() -> parse_yaml_dict() rather
        than a full save-to-disk-and-reload cycle: ClientConfig.google_business_profile
        has a pre-existing, unrelated bug where generate_yaml_dict() writes the raw
        dataclass object instead of a plain dict, which yaml.safe_load() then can't
        parse back (see test_meta_tags_feature.py's test_save_load_roundtrip_preserves_meta_tags,
        which hits the same pre-existing failure). Not an anchor_profile issue -
        this test isolates anchor_profile's own round-trip from that bug.
        """
        parser = ConfigParser()
        yaml_dict = parser.generate_yaml_dict(sample_config_with_anchor_profile)

        loaded = parser.parse_yaml_dict(yaml_dict)

        original = sample_config_with_anchor_profile.cloud.anchor_profile
        restored = loaded.cloud.anchor_profile

        assert restored.distribution == original.distribution
        assert restored.pools == original.pools
        assert restored.seed == original.seed
        assert restored.exact_match_ceiling == original.exact_match_ceiling

    def test_load_config_without_anchor_profile_section_uses_defaults(self, tmp_path):
        """A config file with no anchor_profile section at all must not error"""
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
        config_file = tmp_path / "no_anchor_profile.yaml"
        config_file.write_text(yaml_content)

        parser = ConfigParser()
        loaded = parser.parse_yaml_file(str(config_file))

        assert isinstance(loaded.cloud.anchor_profile, AnchorProfileConfig)
        assert loaded.cloud.anchor_profile.is_configured() is False
        assert sum(loaded.cloud.anchor_profile.distribution.values()) == 100
