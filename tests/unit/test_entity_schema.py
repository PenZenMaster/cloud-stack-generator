"""
Unit Tests for Entity Schema Resolver
Path: E:/projects/cloud-stack-generator/tests/unit/test_entity_schema.py

Description:
Tests for resolve_entity_schema (Issue #36): LocalBusiness + NAP data must be
restricted to main_site properties. Buffer (backlink_site) and resource
properties must not assert the client's real-world entity. Covers the
resolver directly, its wiring into CityPageGenerator's template context, and
an end-to-end render of seo_authority_city_page.html to confirm the emitted
JSON-LD actually reflects the restriction.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-08-07

Last Modified Date:
2026-08-07

Comments:
* v1.00 - Initial tests for issue #36
"""

import sys
import os
import re
import json
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.generators.content.entity_schema import resolve_entity_schema
from core.generators.city_page_generator import CityPageGenerator


class MockAddress:
    def __init__(self, **kwargs):
        self.street = kwargs.get('street', '123 Main St')
        self.city = kwargs.get('city', 'Springfield')
        self.state = kwargs.get('state', 'IL')
        self.zip_code = kwargs.get('zip_code', '62701')
        self.country = kwargs.get('country', 'US')
        self.publish_on_website = kwargs.get('publish_on_website', True)


class MockContact:
    def __init__(self, **kwargs):
        self.phone = kwargs.get('phone', '555-0100')
        self.email = kwargs.get('email', 'contact@example.com')
        self.address = kwargs.get('address', MockAddress())


class MockGBP:
    def __init__(self, **kwargs):
        self.expose_address = kwargs.get('expose_address', False)


class MockCloud:
    def __init__(self, **kwargs):
        self.site_type = kwargs.get('site_type', 'main_site')
        self.deployment_url = kwargs.get('deployment_url', 'https://example.cloudfront.net')
        self.meta_tags = kwargs.get('meta_tags', {})
        self.main_site_url = kwargs.get('main_site_url', '')
        self.allow_indexing = kwargs.get('allow_indexing', True)


class MockConfig:
    """Minimal config object exposing only what resolve_entity_schema reads"""
    def __init__(self, **kwargs):
        self.cloud = kwargs.get('cloud', MockCloud())
        self.contact = kwargs.get('contact', MockContact())
        self.google_business_profile = kwargs.get('google_business_profile', MockGBP())


class TestResolveEntitySchema:
    """Unit tests for the resolver itself"""

    def test_main_site_with_public_address_gets_local_business(self):
        config = MockConfig(
            cloud=MockCloud(site_type='main_site'),
            contact=MockContact(address=MockAddress(publish_on_website=True)),
        )
        result = resolve_entity_schema(config)

        assert result['entity_additional_type'] == 'LocalBusiness'
        assert result['include_nap_schema'] is True

    def test_main_site_with_hidden_address_gets_organization(self):
        config = MockConfig(
            cloud=MockCloud(site_type='main_site'),
            contact=MockContact(address=MockAddress(publish_on_website=False)),
            google_business_profile=MockGBP(expose_address=False),
        )
        result = resolve_entity_schema(config)

        assert result['entity_additional_type'] == 'Organization'
        assert result['include_nap_schema'] is False

    def test_main_site_gbp_expose_overrides_hidden_address(self):
        config = MockConfig(
            cloud=MockCloud(site_type='main_site'),
            contact=MockContact(address=MockAddress(publish_on_website=False)),
            google_business_profile=MockGBP(expose_address=True),
        )
        result = resolve_entity_schema(config)

        assert result['entity_additional_type'] == 'LocalBusiness'
        assert result['include_nap_schema'] is True

    def test_backlink_site_never_gets_local_business_even_with_public_address(self):
        config = MockConfig(
            cloud=MockCloud(site_type='backlink_site'),
            contact=MockContact(address=MockAddress(publish_on_website=True)),
            google_business_profile=MockGBP(expose_address=True),
        )
        result = resolve_entity_schema(config)

        assert result['entity_additional_type'] == 'Organization'
        assert result['include_nap_schema'] is False

    def test_resource_site_gets_webpage_alone_no_nap(self):
        config = MockConfig(
            cloud=MockCloud(site_type='resource'),
            contact=MockContact(address=MockAddress(publish_on_website=True)),
            google_business_profile=MockGBP(expose_address=True),
        )
        result = resolve_entity_schema(config)

        assert result['entity_additional_type'] is None
        assert result['include_nap_schema'] is False


class TestCityPageGeneratorEntitySchemaWiring:
    """Test that CityPageGenerator's template context carries the resolved values"""

    def _make_config(self, site_type):
        config = MagicMock()
        config.cloud = MockCloud(site_type=site_type)
        config.contact = MockContact()
        config.google_business_profile = MockGBP(expose_address=False)
        config.business.business_name = 'Test Business'
        config.business.industry = 'Professional Services'
        config.business.domain = 'https://testbusiness.com'
        config.branding.city_page_image_pool = []
        config.city_pages = []
        config.services = []
        config.products = []
        return config

    def test_main_site_context_includes_local_business(self):
        from core.config.models import CityPageConfig

        config = self._make_config('main_site')
        generator = CityPageGenerator(config)
        city_page = CityPageConfig(city_name="Springfield")

        context = generator._build_template_context(city_page)

        assert context['entity_additional_type'] == 'LocalBusiness'
        assert context['include_nap_schema'] is True

    def test_backlink_site_context_excludes_local_business_and_nap(self):
        from core.config.models import CityPageConfig

        config = self._make_config('backlink_site')
        generator = CityPageGenerator(config)
        city_page = CityPageConfig(city_name="Springfield")

        context = generator._build_template_context(city_page)

        assert context['entity_additional_type'] == 'Organization'
        assert context['include_nap_schema'] is False

    def test_resource_site_context_excludes_local_business_and_nap(self):
        from core.config.models import CityPageConfig

        config = self._make_config('resource')
        generator = CityPageGenerator(config)
        city_page = CityPageConfig(city_name="Springfield")

        context = generator._build_template_context(city_page)

        assert context['entity_additional_type'] is None
        assert context['include_nap_schema'] is False


def _extract_json_ld_blocks(html: str):
    """Extract and parse all application/ld+json script blocks from rendered HTML"""
    blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
    )
    return [json.loads(b) for b in blocks]


class TestSeoAuthorityCityPageRender:
    """End-to-end render of the live template to confirm actual output"""

    def _generate(self, tmp_path, site_type):
        from core.config.models import CityPageConfig

        config = MagicMock()
        config.cloud = MockCloud(site_type=site_type)
        config.contact = MockContact()
        config.google_business_profile = MockGBP(expose_address=False)
        config.business.business_name = 'Test Business'
        config.business.industry = 'Professional Services'
        config.business.domain = 'https://testbusiness.com'
        config.business.hours = 'Mo-Fr 08:00-17:00'
        config.branding.city_page_image_pool = []
        config.branding.logo_url = ''
        config.city_pages = []
        config.services = []
        config.products = []
        config.faq = []

        generator = CityPageGenerator(config)
        city_page = CityPageConfig(city_name="Springfield", state="IL", slug="springfield-il")

        output_dir = str(tmp_path)
        file_path = generator.generate_city_page(city_page, output_dir, use_ai=False)
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    def test_main_site_renders_local_business_and_nap(self, tmp_path):
        html = self._generate(tmp_path, 'main_site')
        blocks = _extract_json_ld_blocks(html)
        entity = blocks[0]

        assert entity['@type'] == ['WebPage', 'LocalBusiness']
        assert 'address' in entity
        assert entity['telephone'] == '555-0100'

    def test_backlink_site_renders_no_local_business_or_nap(self, tmp_path):
        html = self._generate(tmp_path, 'backlink_site')
        blocks = _extract_json_ld_blocks(html)
        entity = blocks[0]

        assert entity['@type'] == ['WebPage', 'Organization']
        assert 'address' not in entity
        assert 'telephone' not in entity
        assert 'email' not in entity

    def test_resource_site_renders_webpage_alone_no_nap(self, tmp_path):
        html = self._generate(tmp_path, 'resource')
        blocks = _extract_json_ld_blocks(html)
        entity = blocks[0]

        assert entity['@type'] == 'WebPage'
        assert 'address' not in entity
        assert 'telephone' not in entity
        assert 'email' not in entity
