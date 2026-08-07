"""
Unit Tests for Content Quality Gate
Path: E:/projects/cloud-stack-generator/tests/unit/test_content_quality_gate.py

Description:
Tests for the content quality gate that prevents scaled near-duplicate city
page content (Issue #35). Covers the gate class directly and its wiring into
CityPageGenerator.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-08-07

Last Modified Date:
2026-08-07

Comments:
* v1.00 - Initial tests for issue #35
"""

import sys
import os
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.generators.content.content_quality_gate import (
    ContentQualityGate,
    ContentQualityGateError,
    city_page_uses_template_fallback,
)
from core.generators.city_page_generator import CityPageGenerator


class MockCityPage:
    """Mock city page configuration"""
    def __init__(self, **kwargs):
        self.city_name = kwargs.get('city_name', 'Test City')
        self.slug = kwargs.get('slug', 'test-city')
        self.about_city = kwargs.get('about_city', '')
        self.seo_content_body = kwargs.get('seo_content_body', '')


class MockClientConfig:
    """Mock client configuration"""
    def __init__(self, **kwargs):
        self.city_pages = kwargs.get('city_pages', [])
        self.business = MagicMock()
        self.business.business_name = 'Test Business'
        self.business.industry = 'Professional Services'
        self.business.domain = 'https://testbusiness.com'
        self.contact = MagicMock()
        self.contact.phone = '(555) 123-4567'
        self.branding = MagicMock()
        self.branding.city_page_image_pool = []


def make_city_pages(total, with_content):
    """Build a list of city pages: the first `with_content` have real content,
    the rest are empty and will trigger template fallback."""
    pages = []
    for i in range(total):
        if i < with_content:
            pages.append(MockCityPage(
                city_name=f"City{i}",
                about_city=f"Real unique history of City{i}.",
                seo_content_body=f"Real unique SEO content for City{i}.",
            ))
        else:
            pages.append(MockCityPage(city_name=f"City{i}"))
    return pages


class TestCityPageUsesTemplateFallback:
    """Test the per-page fallback detection helper"""

    def test_empty_fields_use_fallback(self):
        page = MockCityPage(city_name="Springfield")
        uses_fallback, reason = city_page_uses_template_fallback(page)

        assert uses_fallback is True
        assert "about_city" in reason
        assert "seo_content_body" in reason

    def test_populated_fields_do_not_use_fallback(self):
        page = MockCityPage(
            city_name="Springfield",
            about_city="Springfield has a rich history.",
            seo_content_body="Detailed SEO content for Springfield.",
        )
        uses_fallback, reason = city_page_uses_template_fallback(page)

        assert uses_fallback is False
        assert reason == ""

    def test_partially_populated_still_uses_fallback(self):
        page = MockCityPage(city_name="Springfield", about_city="Some history.")
        uses_fallback, reason = city_page_uses_template_fallback(page)

        assert uses_fallback is True
        assert "seo_content_body" in reason
        assert "about_city" not in reason


class TestContentQualityGate:
    """Test ContentQualityGate.check_batch against the acceptance criteria"""

    def test_fallback_under_limit_succeeds_with_warning(self):
        gate = ContentQualityGate(template_fallback_page_limit=10)
        # 5 pages fall back, well under the limit of 10
        pages = make_city_pages(total=8, with_content=3)

        gate.check_batch(pages)  # must not raise

        assert gate.fallback_count == 5
        assert "5 city page(s)" in gate.summary()

    def test_fallback_over_limit_raises(self):
        gate = ContentQualityGate(template_fallback_page_limit=10)
        # 15 pages fall back, over the limit of 10
        pages = make_city_pages(total=20, with_content=5)

        with pytest.raises(ContentQualityGateError) as exc_info:
            gate.check_batch(pages)

        assert "15 of 20" in str(exc_info.value)
        assert "template_fallback_page_limit of 10" in str(exc_info.value)

    def test_allow_template_fallback_bypasses_the_limit(self):
        gate = ContentQualityGate(
            template_fallback_page_limit=10, allow_template_fallback=True
        )
        pages = make_city_pages(total=20, with_content=0)

        gate.check_batch(pages)  # must not raise despite exceeding the limit

        assert gate.fallback_count == 20

    def test_no_fallback_pages_is_a_no_op(self):
        gate = ContentQualityGate(template_fallback_page_limit=10)
        pages = make_city_pages(total=20, with_content=20)

        gate.check_batch(pages)  # must not raise - nothing falls back

        assert gate.fallback_count == 0
        assert gate.summary() == ""

    def test_exactly_at_limit_does_not_raise(self):
        gate = ContentQualityGate(template_fallback_page_limit=10)
        pages = make_city_pages(total=10, with_content=0)

        gate.check_batch(pages)  # 10 fallbacks == limit, not over it

        assert gate.fallback_count == 10


class TestCityPageGeneratorContentQualityWiring:
    """Test that CityPageGenerator wires the gate in correctly"""

    def test_check_content_quality_raises_when_over_limit(self):
        config = MockClientConfig(city_pages=make_city_pages(total=20, with_content=0))
        generator = CityPageGenerator(config, template_fallback_page_limit=10)

        with pytest.raises(ContentQualityGateError):
            generator.check_content_quality()

    def test_check_content_quality_passes_when_allowed(self):
        config = MockClientConfig(city_pages=make_city_pages(total=20, with_content=0))
        generator = CityPageGenerator(
            config, allow_template_fallback=True, template_fallback_page_limit=10
        )

        generator.check_content_quality()  # must not raise

        assert generator.content_quality_gate.fallback_count == 20

    def test_check_content_quality_passes_when_under_limit(self):
        config = MockClientConfig(city_pages=make_city_pages(total=5, with_content=0))
        generator = CityPageGenerator(config, template_fallback_page_limit=10)

        generator.check_content_quality()  # must not raise

        assert generator.content_quality_gate.fallback_count == 5
