"""
Tests for src/core/onboarding/llm_extractor.py

Covers: JSON parsing, partial/malformed responses, prompt content, model mapping.
"""

import json
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.onboarding.llm_extractor import (
    MODEL_PRESETS,
    ExtractedData,
    LLMExtractor,
)
from src.core.onboarding.web_fetcher import PageContent


FULL_JSON_RESPONSE = json.dumps({
    "business_name": "ACME Plumbing Co.",
    "description": "Full service plumbing company serving Chicago since 1995.",
    "tagline": "Fast, Reliable Plumbing You Can Count On",
    "contact_name": "John Smith",
    "phone": "(555) 123-4567",
    "email": "info@acmeplumbing.com",
    "logo_url": "https://acmeplumbing.com/logo.png",
    "services": [
        {"name": "Emergency Repairs", "description": "24/7 emergency plumbing repairs."},
        {"name": "Drain Cleaning", "description": "Professional drain cleaning service."},
    ],
    "products": [
        {"sku": "PROD-001", "name": "Pipe Wrench", "description": "Heavy duty pipe wrench.", "image_url": ""},
    ],
    "social_media": {
        "facebook": "https://facebook.com/acmeplumbing",
        "twitter": "",
        "linkedin": "",
        "instagram": "https://instagram.com/acmeplumbing",
        "youtube": "",
    },
    "branding": {
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
})


def _make_mock_client_response(text: str):
    """Build a mock Anthropic response object."""
    mock_response = Mock()
    mock_response.content = [Mock(text=text)]
    mock_response.usage = Mock(input_tokens=500, output_tokens=300)
    return mock_response


def _make_extractor():
    """Create an LLMExtractor with a mocked Anthropic client."""
    with patch("src.core.onboarding.llm_extractor.Anthropic") as MockAnthropic:
        extractor = LLMExtractor(api_key="test-key", model_preset="balanced")
        extractor._client = MockAnthropic.return_value
    return extractor


def _make_pages():
    return [
        PageContent(
            url="https://example.com",
            text="ACME Plumbing Co. - Fast and reliable plumbing services.",
            css_snippets=["header { background-color: #003366; }"],
            meta_title="ACME Plumbing",
            meta_description="Professional plumbing in Chicago.",
            images=[{"src": "https://example.com/logo.png", "alt": "Logo"}],
        )
    ]


class TestModelPresetMapping:
    def test_balanced_maps_to_sonnet(self):
        assert "sonnet" in MODEL_PRESETS["balanced"]

    def test_fast_maps_to_haiku(self):
        assert "haiku" in MODEL_PRESETS["fast"]

    def test_thorough_maps_to_opus(self):
        assert "opus" in MODEL_PRESETS["thorough"]

    def test_unknown_preset_falls_back_to_balanced(self):
        with patch("src.core.onboarding.llm_extractor.Anthropic"):
            extractor = LLMExtractor(api_key="key", model_preset="unknown")
        assert extractor._model == MODEL_PRESETS["balanced"]


class TestExtractBusinessData:
    def test_full_response_parses_all_fields(self):
        extractor = _make_extractor()
        extractor._client.messages.create.return_value = _make_mock_client_response(FULL_JSON_RESPONSE)

        result = extractor.extract_business_data(_make_pages(), "plumbing")

        assert result.business_name == "ACME Plumbing Co."
        assert result.description != ""
        assert result.phone == "(555) 123-4567"
        assert result.email == "info@acmeplumbing.com"
        assert len(result.services) == 2
        assert len(result.products) == 1
        assert result.branding.get("primary_color") == "#003366"
        assert result.social_media.get("facebook") != ""

    def test_partial_response_returns_available_fields(self):
        partial = json.dumps({
            "business_name": "Half Baked Co.",
            "description": "",
            "services": [{"name": "Service A", "description": ""}],
            "products": [],
            "social_media": {},
            "branding": {},
        })
        extractor = _make_extractor()
        extractor._client.messages.create.return_value = _make_mock_client_response(partial)

        result = extractor.extract_business_data(_make_pages(), "services")

        assert result.business_name == "Half Baked Co."
        assert len(result.services) == 1
        assert len(result.products) == 0
        assert result.branding == {}

    def test_malformed_json_returns_empty_data(self):
        extractor = _make_extractor()
        extractor._client.messages.create.return_value = _make_mock_client_response(
            "This is not JSON at all!"
        )

        result = extractor.extract_business_data(_make_pages(), "plumbing")

        assert isinstance(result, ExtractedData)
        assert result.business_name == ""
        assert result.services == []

    def test_json_in_markdown_fences_is_parsed(self):
        fenced = f"```json\n{FULL_JSON_RESPONSE}\n```"
        extractor = _make_extractor()
        extractor._client.messages.create.return_value = _make_mock_client_response(fenced)

        result = extractor.extract_business_data(_make_pages(), "plumbing")
        assert result.business_name == "ACME Plumbing Co."

    def test_invalid_hex_colors_are_filtered(self):
        data = json.dumps({
            "business_name": "Test Co",
            "branding": {
                "primary_color": "blue",  # not a hex code
                "secondary_color": "#ff6600",  # valid
            },
            "services": [],
            "products": [],
            "social_media": {},
        })
        extractor = _make_extractor()
        extractor._client.messages.create.return_value = _make_mock_client_response(data)

        result = extractor.extract_business_data(_make_pages(), "retail")

        assert "primary_color" not in result.branding  # filtered out
        assert result.branding.get("secondary_color") == "#ff6600"

    def test_empty_pages_returns_empty_data(self):
        extractor = _make_extractor()
        result = extractor.extract_business_data([], "plumbing")
        assert isinstance(result, ExtractedData)
        assert result.business_name == ""


class TestBuildExtractionPrompt:
    def test_prompt_includes_page_text(self):
        extractor = _make_extractor()
        pages = _make_pages()
        prompt = extractor._build_extraction_prompt(pages, "plumbing")
        assert "ACME Plumbing" in prompt

    def test_prompt_includes_css_for_colors(self):
        extractor = _make_extractor()
        pages = _make_pages()
        prompt = extractor._build_extraction_prompt(pages, "plumbing")
        assert "#003366" in prompt

    def test_prompt_includes_industry(self):
        extractor = _make_extractor()
        pages = _make_pages()
        prompt = extractor._build_extraction_prompt(pages, "roofing")
        assert "roofing" in prompt
