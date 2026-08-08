"""
Unit Tests for Anchor Text Selector
Path: E:/projects/cloud-stack-generator/tests/unit/test_anchor_selector.py

Description:
Tests for AnchorSelector (Issue #37): distribution converges toward target
over many selections, selection is deterministic under a fixed seed, no
anchor repeats within a single page, and empty/misconfigured pools fall
back safely. Also covers the safety ceiling on exact-match share and the
build_anchor_selector() wiring for backlink_site vs resource site identity.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-08-07

Last Modified Date:
2026-08-07

Comments:
* v1.00 - Initial tests for issue #37 (core engine only)
"""

import sys
import os
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.generators.content.anchor_selector import (
    AnchorSelector,
    AnchorSelectionError,
    build_anchor_selector,
    DEFAULT_DISTRIBUTION,
)


POOLS = {
    "branded": ["Acme Garage Doors", "Acme", "Acme Garage Doors of Richmond"],
    "naked_url": ["acmegaragedoors.com"],
    "generic": ["visit their website", "learn more", "see full details", "their main site"],
    "partial_match": ["garage door repair specialists", "commercial door installers", "residential door pros"],
    "exact_match": ["garage door repair richmond va"],
}


class TestAnchorSelectorValidation:
    def test_distribution_must_sum_to_100(self):
        with pytest.raises(AnchorSelectionError, match="must sum to 100"):
            AnchorSelector(distribution={"branded": 50, "generic": 40})

    def test_exact_match_over_ceiling_hard_fails(self):
        with pytest.raises(AnchorSelectionError, match="exceeds the safety ceiling"):
            AnchorSelector(
                distribution={
                    "branded": 30, "naked_url": 15, "generic": 20,
                    "partial_match": 20, "exact_match": 15,
                },
                exact_match_ceiling=10,
            )

    def test_exact_match_at_ceiling_is_allowed(self):
        selector = AnchorSelector(
            distribution={
                "branded": 35, "naked_url": 15, "generic": 20,
                "partial_match": 20, "exact_match": 10,
            },
            exact_match_ceiling=10,
        )
        assert selector is not None


class TestDistributionConvergence:
    def test_realized_distribution_converges_toward_target_over_many_pages(self):
        selector = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=42)

        for i in range(100):
            selector.select(slot="generic", page_id=f"page-{i}")

        realized = selector.realized_distribution()
        for category, target_pct in DEFAULT_DISTRIBUTION.items():
            assert abs(realized[category] - target_pct) <= 8, (
                f"{category}: realized {realized[category]}% vs target {target_pct}%"
            )


class TestDeterminism:
    def test_same_seed_produces_identical_sequence(self):
        selector_a = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=123)
        selector_b = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=123)

        sequence_a = [selector_a.select(slot="generic", page_id=f"page-{i}") for i in range(30)]
        sequence_b = [selector_b.select(slot="generic", page_id=f"page-{i}") for i in range(30)]

        assert sequence_a == sequence_b

    def test_different_seeds_diverge(self):
        selector_a = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=1)
        selector_b = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=2)

        sequence_a = [selector_a.select(slot="generic", page_id=f"page-{i}") for i in range(30)]
        sequence_b = [selector_b.select(slot="generic", page_id=f"page-{i}") for i in range(30)]

        assert sequence_a != sequence_b


class TestNoIntraPageRepeats:
    def test_no_repeated_anchor_within_one_page(self):
        selector = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=7)

        # 5 slots on one page - well under the ~13 total distinct anchors
        # across all pools, so no repeat is required
        anchors = [selector.select(slot="generic", page_id="richmond-va") for _ in range(5)]

        assert len(anchors) == len(set(anchors))

    def test_repeats_are_allowed_across_different_pages(self):
        selector = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=7)

        for _ in range(3):
            selector.select(slot="generic", page_id="page-a")
        page_two = [selector.select(slot="generic", page_id="page-b") for _ in range(3)]

        # Not a correctness assertion on repeats existing, just that the
        # per-page tracking is independent (page-b isn't blocked by page-a's picks)
        assert len(page_two) == 3


class TestEmptyPoolFallback:
    def test_empty_category_pool_falls_back_to_branded(self):
        pools = dict(POOLS)
        pools["exact_match"] = []

        selector = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=pools, seed=1)

        # Drive many selections on distinct pages - whenever drift correction
        # would pick exact_match, its empty pool must redirect to branded
        # instead of crashing, and exact_match's realized count must stay 0
        for i in range(50):
            anchor = selector.select(slot="generic", page_id=f"page-{i}")
            assert anchor != ""

        assert selector.realized_counts()["exact_match"] == 0

    def test_all_pools_exhausted_on_one_page_still_returns_something(self):
        selector = AnchorSelector(
            distribution=DEFAULT_DISTRIBUTION,
            pools={"branded": ["OnlyOne"], "naked_url": [], "generic": [], "partial_match": [], "exact_match": []},
            seed=1,
        )

        # More selects than total pool size (1) on a single page - must not raise
        anchors = [selector.select(slot="generic", page_id="tiny-page") for _ in range(3)]
        assert all(a == "OnlyOne" for a in anchors)


class TestSlotWeighting:
    """Compare a slot's realized mix against an unweighted baseline run with
    the same seed and iteration count - robust to the exact convergence
    dynamics of the drift-correction algorithm."""

    def test_footer_slot_skews_branded_and_generic_vs_unweighted_baseline(self):
        unweighted = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=42)
        footer = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=42)

        for i in range(300):
            unweighted.select(slot="unweighted_probe", page_id=f"page-{i}")
            footer.select(slot="footer", page_id=f"page-{i}")

        unweighted_bg = unweighted.realized_distribution()
        footer_bg = footer.realized_distribution()

        assert (footer_bg["branded"] + footer_bg["generic"]) > (
            unweighted_bg["branded"] + unweighted_bg["generic"]
        )

    def test_body_contextual_slot_skews_partial_match_vs_unweighted_baseline(self):
        unweighted = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=42)
        body = AnchorSelector(distribution=DEFAULT_DISTRIBUTION, pools=POOLS, seed=42)

        for i in range(300):
            unweighted.select(slot="unweighted_probe", page_id=f"page-{i}")
            body.select(slot="body_contextual", page_id=f"page-{i}")

        assert body.realized_distribution()["partial_match"] > (
            unweighted.realized_distribution()["partial_match"]
        )


class TestAutoGeneratedDefaultPools:
    def test_unconfigured_pools_are_auto_generated_from_identity(self):
        selector = AnchorSelector(
            distribution=DEFAULT_DISTRIBUTION,
            pools={},
            seed=1,
            business_name="Acme Roofing",
            industry="Roofing",
            domain="https://acmeroofing.com",
            cities=["Richmond", "Norfolk"],
        )

        assert "Acme Roofing" in selector.pools["branded"]
        assert "acmeroofing.com" in selector.pools["naked_url"]
        assert selector.pools["generic"]
        assert selector.pools["partial_match"]
        assert selector.pools["exact_match"]


class TestBuildAnchorSelector:
    def _make_config(self, site_type, resource_site_configured=False):
        config = MagicMock()
        config.cloud.site_type = site_type
        config.cloud.main_site_url = "https://mainsite.example.com"
        config.cloud.anchor_profile.distribution = DEFAULT_DISTRIBUTION
        config.cloud.anchor_profile.pools = {}
        config.cloud.anchor_profile.seed = 5
        config.cloud.anchor_profile.exact_match_ceiling = 10
        config.business.business_name = "Resource Site Editorial Brand"
        config.business.industry = "Garage Doors"
        config.business.domain = "https://resourcesite.example.com"
        config.city_pages = []
        config.target_cities = ["Richmond"]

        if resource_site_configured:
            config.resource_site.is_configured.return_value = True
            config.resource_site.money_site_name = "Acme Garage Doors"
            config.resource_site.money_site_url = "https://acmegaragedoors.com"
        else:
            config.resource_site.is_configured.return_value = False

        return config

    def test_backlink_site_uses_business_identity(self):
        config = self._make_config("backlink_site")
        selector = build_anchor_selector(config)

        assert "Resource Site Editorial Brand" in selector.pools["branded"]

    def test_resource_site_uses_money_site_identity_not_own_business(self):
        config = self._make_config("resource", resource_site_configured=True)
        selector = build_anchor_selector(config)

        assert "Acme Garage Doors" in selector.pools["branded"]
        assert "Resource Site Editorial Brand" not in selector.pools["branded"]

    def test_unconfigured_resource_site_falls_back_to_business_identity(self):
        config = self._make_config("resource", resource_site_configured=False)
        selector = build_anchor_selector(config)

        assert "Resource Site Editorial Brand" in selector.pools["branded"]


class TestSeoAuthorityCityPageAnchorRender:
    """End-to-end: render the live city page template for a backlink_site
    config and confirm the anchor() global actually populates real,
    non-empty anchor text - and that the backlink CTA section renders at
    all now that is_backlink_site/main_site_url are wired into the context."""

    def test_backlink_site_city_page_renders_varied_anchor_text(self, tmp_path):
        from core.generators.city_page_generator import CityPageGenerator
        from core.config.models import CityPageConfig

        config = MagicMock()
        config.cloud.site_type = "backlink_site"
        config.cloud.main_site_url = "https://mainsite.example.com"
        config.cloud.deployment_url = "https://d123.cloudfront.net"
        config.cloud.meta_tags = {}
        config.cloud.anchor_profile.distribution = DEFAULT_DISTRIBUTION
        config.cloud.anchor_profile.pools = {}
        config.cloud.anchor_profile.seed = 99
        config.cloud.anchor_profile.exact_match_ceiling = 10
        config.resource_site.is_configured.return_value = False
        config.business.business_name = "Acme Roofing"
        config.business.industry = "Roofing"
        config.business.domain = "https://acmeroofing.com"
        config.business.hours = "Mo-Fr 08:00-17:00"
        config.contact.phone = "555-0100"
        config.contact.email = "contact@acmeroofing.com"
        config.branding.city_page_image_pool = []
        config.branding.logo_url = ""
        config.city_pages = []
        config.services = []
        config.products = []
        config.faq = []
        config.target_cities = []

        generator = CityPageGenerator(config)
        city_page = CityPageConfig(city_name="Richmond", state="VA", slug="richmond-va")

        output_dir = str(tmp_path)
        file_path = generator.generate_city_page(city_page, output_dir, use_ai=False)
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()

        # The backlink CTA section must actually render now that
        # is_backlink_site/main_site_url are populated in the context
        assert "https://mainsite.example.com" in html
        # And the anchor text must be real, resolved anchor pool content -
        # not left as an unrendered Jinja expression or empty
        assert "{{ anchor(" not in html
        assert "Acme Roofing" in html or "acmeroofing.com" in html
