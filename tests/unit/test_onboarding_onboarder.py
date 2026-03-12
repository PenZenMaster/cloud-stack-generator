"""
Tests for src/core/onboarding/onboarder.py

Covers: full pipeline success, partial failures, output path generation.
"""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.onboarding.gbp_client import GBPData
from src.core.onboarding.llm_extractor import ExtractedData
from src.core.onboarding.onboarder import OnboardResult, Onboarder


def _make_onboarder(**kwargs):
    defaults = dict(
        url="https://acme.com",
        gbp_link="https://maps.app.goo.gl/abc",
        industry="plumbing",
        claude_api_key="test-claude-key",
        google_api_key="test-google-key",
        model="balanced",
    )
    defaults.update(kwargs)
    return Onboarder(**defaults)


def _mock_pages():
    from src.core.onboarding.web_fetcher import PageContent
    return [PageContent(
        url="https://acme.com",
        text="ACME Plumbing",
        css_snippets=[],
        meta_title="ACME Plumbing",
        meta_description="",
        images=[],
    )]


def _mock_llm_data():
    return ExtractedData(
        business_name="ACME Plumbing Co.",
        description="Best plumbing.",
        tagline="Call us now!",
        services=[{"name": "Drain Cleaning", "description": "We clean."}],
        products=[],
        branding={"primary_color": "#003366"},
    )


def _mock_gbp_data():
    return GBPData(
        business_name="ACME Plumbing",
        phone="(555) 123-4567",
        street="123 Main St",
        city="Chicago",
        state="IL",
        zip_code="60601",
    )


class TestOnboarderFullPipeline:
    def test_returns_successful_result(self, tmp_path):
        output = str(tmp_path / "test_config.yaml")
        onboarder = _make_onboarder()

        with patch("src.core.onboarding.onboarder.WebFetcher") as MockFetcher, \
             patch("src.core.onboarding.onboarder.LLMExtractor") as MockExtractor, \
             patch("src.core.onboarding.onboarder.GBPClient") as MockGBP:

            MockFetcher.return_value.run.return_value = _mock_pages()
            MockExtractor.return_value.extract_business_data.return_value = _mock_llm_data()
            MockGBP.return_value.fetch.return_value = _mock_gbp_data()

            result = onboarder.run(output_path=output)

        assert result.success is True
        assert Path(result.output_path).exists()
        assert result.business_name != ""

    def test_services_count_in_result(self, tmp_path):
        output = str(tmp_path / "test_config.yaml")
        onboarder = _make_onboarder()

        with patch("src.core.onboarding.onboarder.WebFetcher") as MockFetcher, \
             patch("src.core.onboarding.onboarder.LLMExtractor") as MockExtractor, \
             patch("src.core.onboarding.onboarder.GBPClient") as MockGBP:

            MockFetcher.return_value.run.return_value = _mock_pages()
            llm = _mock_llm_data()
            llm.services = [
                {"name": "A", "description": ""},
                {"name": "B", "description": ""},
                {"name": "C", "description": ""},
            ]
            MockExtractor.return_value.extract_business_data.return_value = llm
            MockGBP.return_value.fetch.return_value = None

            result = onboarder.run(output_path=output)

        assert result.services_found == 3


class TestOnboarderWithoutGBP:
    def test_skips_gbp_when_no_link_provided(self, tmp_path):
        output = str(tmp_path / "test_config.yaml")
        onboarder = _make_onboarder(gbp_link="")

        with patch("src.core.onboarding.onboarder.WebFetcher") as MockFetcher, \
             patch("src.core.onboarding.onboarder.LLMExtractor") as MockExtractor, \
             patch("src.core.onboarding.onboarder.GBPClient") as MockGBP:

            MockFetcher.return_value.run.return_value = _mock_pages()
            MockExtractor.return_value.extract_business_data.return_value = _mock_llm_data()

            result = onboarder.run(output_path=output)

        # GBPClient.fetch should not be called when no gbp_link
        MockGBP.return_value.fetch.assert_not_called()
        assert result.success is True


class TestOnboarderPartialFailures:
    def test_website_fetch_failure_continues(self, tmp_path):
        output = str(tmp_path / "test_config.yaml")
        onboarder = _make_onboarder()

        with patch("src.core.onboarding.onboarder.WebFetcher") as MockFetcher, \
             patch("src.core.onboarding.onboarder.LLMExtractor") as MockExtractor, \
             patch("src.core.onboarding.onboarder.GBPClient") as MockGBP:

            MockFetcher.return_value.run.side_effect = Exception("Connection refused")
            MockExtractor.return_value.extract_business_data.return_value = _mock_llm_data()
            MockGBP.return_value.fetch.return_value = _mock_gbp_data()

            result = onboarder.run(output_path=output)

        # Should still succeed using GBP data alone
        assert result.success is True
        assert len(result.warnings) > 0

    def test_llm_failure_continues_with_gbp_data(self, tmp_path):
        output = str(tmp_path / "test_config.yaml")
        onboarder = _make_onboarder()

        with patch("src.core.onboarding.onboarder.WebFetcher") as MockFetcher, \
             patch("src.core.onboarding.onboarder.LLMExtractor") as MockExtractor, \
             patch("src.core.onboarding.onboarder.GBPClient") as MockGBP:

            MockFetcher.return_value.run.return_value = _mock_pages()
            MockExtractor.return_value.extract_business_data.side_effect = Exception("API error")
            MockGBP.return_value.fetch.return_value = _mock_gbp_data()

            result = onboarder.run(output_path=output)

        assert result.success is True
        assert len(result.errors) > 0

    def test_gbp_failure_continues_with_llm_data(self, tmp_path):
        output = str(tmp_path / "test_config.yaml")
        onboarder = _make_onboarder()

        with patch("src.core.onboarding.onboarder.WebFetcher") as MockFetcher, \
             patch("src.core.onboarding.onboarder.LLMExtractor") as MockExtractor, \
             patch("src.core.onboarding.onboarder.GBPClient") as MockGBP:

            MockFetcher.return_value.run.return_value = _mock_pages()
            MockExtractor.return_value.extract_business_data.return_value = _mock_llm_data()
            MockGBP.return_value.fetch.side_effect = Exception("Places API down")

            result = onboarder.run(output_path=output)

        assert result.success is True
        assert len(result.warnings) > 0


class TestProgressCallback:
    def test_progress_callback_is_called(self, tmp_path):
        output = str(tmp_path / "test_config.yaml")
        onboarder = _make_onboarder()
        messages = []

        with patch("src.core.onboarding.onboarder.WebFetcher") as MockFetcher, \
             patch("src.core.onboarding.onboarder.LLMExtractor") as MockExtractor, \
             patch("src.core.onboarding.onboarder.GBPClient") as MockGBP:

            MockFetcher.return_value.run.return_value = _mock_pages()
            MockExtractor.return_value.extract_business_data.return_value = _mock_llm_data()
            MockGBP.return_value.fetch.return_value = None

            onboarder.run(output_path=output, progress_callback=messages.append)

        assert any("[1/4]" in m for m in messages)
        assert any("[2/4]" in m for m in messages)
        assert any("[3/4]" in m for m in messages)
        assert any("[4/4]" in m for m in messages)
