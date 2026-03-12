"""
Tests for src/core/onboarding/config_builder.py

Covers: config building, merge priority, YAML output, round-trip compatibility.
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest
import yaml

from src.core.onboarding.config_builder import BRANDING_DEFAULTS, ConfigBuilder
from src.core.onboarding.gbp_client import GBPData
from src.core.onboarding.llm_extractor import ExtractedData


def _make_llm_data(**kwargs) -> ExtractedData:
    defaults = dict(
        business_name="ACME Plumbing Co.",
        description="Best plumbing in Chicago.",
        tagline="Reliable. Fast. Affordable.",
        contact_name="John Smith",
        phone="555-100-2000",
        email="info@acme.com",
        logo_url="https://acme.com/logo.png",
        services=[{"name": "Drain Cleaning", "description": "We clean drains."}],
        products=[{"sku": "PROD-001", "name": "Wrench", "description": "Pipe wrench.", "image_url": ""}],
        social_media={"facebook": "https://fb.com/acme", "instagram": ""},
        branding={
            "primary_color": "#003366",
            "secondary_color": "#ff6600",
            "body_background_color": "#ffffff",
            "body_text_color": "#333333",
            "footer_background_color": "#003366",
            "footer_text_color": "#ffffff",
            "h1_text_color": "#003366",
            "h2_text_color": "#003366",
            "h3_text_color": "#555555",
            "main_menu_text_color": "#ffffff",
        },
    )
    defaults.update(kwargs)
    return ExtractedData(**defaults)


def _make_gbp_data(**kwargs) -> GBPData:
    defaults = dict(
        business_name="ACME Plumbing",
        phone="(555) 123-4567",
        website="https://acme.com",
        street="123 Main Street",
        city="Chicago",
        state="IL",
        zip_code="60601",
        country="United States",
        latitude=41.8781,
        longitude=-87.6298,
        rating="4.7",
        review_count="238",
        place_id="ChIJabc123",
        profile_url="https://maps.google.com/?cid=12345",
        business_hours={
            "monday": "8:00 AM - 5:00 PM",
            "tuesday": "8:00 AM - 5:00 PM",
            "wednesday": "8:00 AM - 5:00 PM",
            "thursday": "8:00 AM - 5:00 PM",
            "friday": "8:00 AM - 5:00 PM",
            "saturday": "9:00 AM - 2:00 PM",
            "sunday": "Closed",
        },
    )
    defaults.update(kwargs)
    return GBPData(**defaults)


class TestConfigBuilderBuild:
    def test_returns_dict_with_client_key(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(llm_data=_make_llm_data(), gbp_data=_make_gbp_data())
        assert "client" in result

    def test_industry_from_user_input_not_llm(self):
        # Even if LLM extracted a different industry, user's input is authoritative
        builder = ConfigBuilder(industry="roofing", website_url="https://acme.com")
        result = builder.build(llm_data=_make_llm_data(), gbp_data=None)
        assert result["client"]["industry"] == "roofing"

    def test_gbp_business_name_takes_priority(self):
        llm = _make_llm_data(business_name="LLM Name")
        gbp = _make_gbp_data(business_name="GBP Name")
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(llm, gbp)
        assert result["client"]["business_name"] == "GBP Name"

    def test_llm_name_used_when_no_gbp(self):
        llm = _make_llm_data(business_name="LLM Name")
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(llm, None)
        assert result["client"]["business_name"] == "LLM Name"

    def test_gbp_phone_takes_priority(self):
        llm = _make_llm_data(phone="555-LLM-PHON")
        gbp = _make_gbp_data(phone="(555) GBP-PHON")
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(llm, gbp)
        assert result["client"]["contact"]["phone"] == "(555) GBP-PHON"

    def test_gbp_address_included_in_contact(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(_make_llm_data(), _make_gbp_data())
        contact = result["client"]["contact"]
        address = contact["address"]
        assert address["city"] == "Chicago"
        assert address["state"] == "IL"

    def test_no_address_in_contact_when_no_gbp(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(_make_llm_data(), None)
        contact = result["client"]["contact"]
        assert "address" not in contact

    def test_branding_colors_from_llm(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(_make_llm_data(), None)
        branding = result["client"]["branding"]
        assert branding["primary_color"] == "#003366"

    def test_branding_defaults_fill_missing_colors(self):
        llm = _make_llm_data(branding={"primary_color": "#003366"})  # only one color
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(llm, None)
        branding = result["client"]["branding"]
        # Missing colors should use defaults
        assert branding["secondary_color"] == BRANDING_DEFAULTS["secondary_color"]
        assert branding["body_text_color"] == BRANDING_DEFAULTS["body_text_color"]

    def test_services_get_type_service(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(_make_llm_data(), None)
        offerings = result["client"]["offerings"]
        services = [o for o in offerings if o.get("type") == "service"]
        assert len(services) == 1
        assert services[0]["name"] == "Drain Cleaning"

    def test_products_get_type_product(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(_make_llm_data(), None)
        offerings = result["client"]["offerings"]
        products = [o for o in offerings if o.get("type") == "product"]
        assert len(products) == 1
        assert products[0]["sku"] == "PROD-001"

    def test_gbp_section_populated(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(_make_llm_data(), _make_gbp_data())
        gbp = result["client"]["google_business_profile"]
        assert gbp["place_id"] == "ChIJabc123"

    def test_default_pages_generated(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        result = builder.build(_make_llm_data(), None)
        pages = result["client"]["pages"]
        slugs = [p["slug"] for p in pages]
        assert "index" in slugs
        assert "about" in slugs
        assert "services" in slugs
        assert "contact" in slugs


class TestSaveYaml:
    def test_writes_yaml_file(self, tmp_path):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        config = builder.build(_make_llm_data(), None)
        output = str(tmp_path / "test_config.yaml")
        path = builder.save_yaml(config, output)
        assert Path(path).exists()

    def test_yaml_is_parseable(self, tmp_path):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        config = builder.build(_make_llm_data(), None)
        output = str(tmp_path / "test_config.yaml")
        path = builder.save_yaml(config, output)

        with open(path, "r", encoding="utf-8") as fh:
            loaded = yaml.safe_load(fh)

        assert "client" in loaded
        assert loaded["client"]["industry"] == "plumbing"

    def test_creates_parent_directories(self, tmp_path):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        config = builder.build(_make_llm_data(), None)
        output = str(tmp_path / "nested" / "deep" / "config.yaml")
        path = builder.save_yaml(config, output)
        assert Path(path).exists()


class TestGenerateOutputPath:
    def test_slugifies_business_name(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        path = builder.generate_output_path("ACME Plumbing Co.")
        assert "acme-plumbing-co" in path

    def test_uses_default_dir(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        path = builder.generate_output_path("Test Co")
        assert path.startswith("config/clients/")

    def test_handles_empty_name(self):
        builder = ConfigBuilder(industry="plumbing", website_url="https://acme.com")
        path = builder.generate_output_path("")
        assert "new-client" in path
