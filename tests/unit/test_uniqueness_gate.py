"""
Unit Tests for Content Uniqueness Gate
Path: E:/projects/cloud-stack-generator/tests/unit/test_uniqueness_gate.py

Description:
Tests for UniquenessGate (Issue #38): identical pages score ~1.0 and block,
genuinely varied pages pass, warn vs block thresholds, HTML tag-stripping,
and the gate's wiring into PageGenerator/WebsiteOrchestrator as a
pre-publish check.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-08-08

Last Modified Date:
2026-08-08

Comments:
* v1.00 - Initial tests for issue #38 (core engine only)
"""

import sys
import os

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.quality.uniqueness_gate import (
    UniquenessGate,
    UniquenessGateError,
    strip_html,
    extract_shingles,
    MinHasher,
    estimated_jaccard,
)


CITY_TEMPLATE = """
<section class="hero">
<h2>{industry} Services in {city}</h2>
<p>Professional {industry_lower} services serving {city} and surrounding areas. Our team
has decades of combined experience delivering reliable, high quality work throughout the
region, and we take pride in treating every job, large or small, with the same level of
craftsmanship and attention to detail.</p>
</section>
<section class="content">
<h3>Local {industry} Experts</h3>
<p>Acme is proud to serve this area with professional {industry_lower} services. Our local
expertise and commitment to excellence make us the preferred choice for residents and
businesses. We understand the unique challenges that come with the local climate, building
codes, and architectural styles common throughout the area, and we tailor our approach
accordingly rather than applying a one size fits all solution to every project.</p>
<p>Whether you need emergency repairs, routine maintenance, or a full replacement, our
licensed and insured technicians arrive on time, communicate clearly, and stand behind
their work with a comprehensive warranty. We source premium materials from trusted
manufacturers and never cut corners, because we know that the quality of our work directly
reflects on our reputation in the community we live and work in every single day.</p>
<h3>Why Choose Us</h3>
<ul>
<li>Decades of combined industry experience and thousands of completed projects</li>
<li>Fully licensed, bonded, and insured for your complete peace of mind</li>
<li>Transparent, upfront pricing with no hidden fees or surprise charges</li>
<li>Responsive customer service and flexible scheduling options available</li>
</ul>
<p>Contact our {city} team today to schedule a free, no obligation consultation and discover
why so many homeowners and business owners throughout the region continue to trust us with
their most important projects year after year.</p>
</section>
"""


def render_city_page(city: str, industry: str = "Roofing") -> str:
    return CITY_TEMPLATE.format(city=city, industry=industry, industry_lower=industry.lower())


GENUINELY_DIFFERENT_PAGES = {
    "about": """
        <section class="about">
            <h2>Our Company History</h2>
            <p>Founded in 1998 by two brothers who noticed a gap in the local hardware
            market, our company has grown from a single storefront into a regional
            distributor. We pride ourselves on curated inventory, same-day pickup,
            and staff who actually know what a torque wrench is for.</p>
        </section>
    """,
    "faq": """
        <section class="faq">
            <h2>Frequently Asked Questions</h2>
            <details><summary>Do you ship internationally?</summary>
            <p>No, we currently only ship within the continental United States due to
            hazardous materials restrictions on several product lines.</p></details>
            <details><summary>What is your return policy?</summary>
            <p>Unopened items may be returned within 30 days with a receipt. Opened
            electrical components are final sale for safety reasons.</p></details>
        </section>
    """,
    "careers": """
        <section class="careers">
            <h2>Join Our Team</h2>
            <p>We are hiring warehouse associates and delivery drivers for our
            growing distribution center. Benefits include health insurance after 90
            days, a 401k match, and a genuinely good break room with a foosball
            table nobody ever wins on.</p>
        </section>
    """,
}


class TestTextExtraction:
    def test_strip_html_removes_tags(self):
        html = "<section><h2>Hello</h2><p>World</p></section>"
        assert strip_html(html) == "Hello World"

    def test_strip_html_removes_script_and_style_content(self):
        html = "<p>Visible</p><script>var x = 'hidden';</script><style>.x{color:red}</style>"
        result = strip_html(html)
        assert "hidden" not in result
        assert "color" not in result
        assert "Visible" in result

    def test_extract_shingles_basic(self):
        shingles = extract_shingles("the quick brown fox jumps over the lazy dog", shingle_size=5)
        assert "the quick brown fox jumps" in shingles
        assert "quick brown fox jumps over" in shingles

    def test_extract_shingles_empty_text(self):
        assert extract_shingles("") == set()

    def test_extract_shingles_short_text_falls_back_to_whole_string(self):
        shingles = extract_shingles("only three words", shingle_size=5)
        assert shingles == {"only three words"}


class TestMinHashEstimation:
    def test_identical_shingle_sets_have_similarity_1(self):
        hasher = MinHasher(num_hashes=64, seed=1)
        shingles = extract_shingles(render_city_page("Richmond"))
        sig_a = hasher.signature(shingles)
        sig_b = hasher.signature(shingles)
        assert estimated_jaccard(sig_a, sig_b) == 1.0

    def test_disjoint_shingle_sets_have_low_similarity(self):
        hasher = MinHasher(num_hashes=64, seed=1)
        sig_a = hasher.signature(extract_shingles(GENUINELY_DIFFERENT_PAGES["about"]))
        sig_b = hasher.signature(extract_shingles(GENUINELY_DIFFERENT_PAGES["careers"]))
        assert estimated_jaccard(sig_a, sig_b) < 0.2

    def test_empty_shingle_set_does_not_crash(self):
        hasher = MinHasher(num_hashes=16, seed=1)
        sig = hasher.signature(set())
        assert len(sig) == 16


class TestUniquenessGateValidation:
    def test_invalid_warn_threshold_raises(self):
        with pytest.raises(ValueError, match="warn_threshold"):
            UniquenessGate(warn_threshold=1.5)

    def test_invalid_block_threshold_raises(self):
        with pytest.raises(ValueError, match="block_threshold"):
            UniquenessGate(block_threshold=-0.1)

    def test_block_below_warn_raises(self):
        with pytest.raises(ValueError, match="must be >="):
            UniquenessGate(warn_threshold=0.9, block_threshold=0.5)


class TestIdenticalPagesBlock:
    def test_identical_pages_score_near_1_and_block(self):
        gate = UniquenessGate(warn_threshold=0.75, block_threshold=0.85)
        page_text = render_city_page("Richmond")

        # Same content, different city name only - the exact scaled-abuse pattern
        gate.add_page("richmond.html", page_text)
        gate.add_page("norfolk.html", page_text.replace("Richmond", "Norfolk"))

        with pytest.raises(UniquenessGateError, match="too similar"):
            gate.check()

    def test_report_reflects_high_similarity_before_raising(self):
        gate = UniquenessGate(warn_threshold=0.75, block_threshold=0.85)
        page_text = render_city_page("Richmond")
        gate.add_page("richmond.html", page_text)
        gate.add_page("norfolk.html", page_text.replace("Richmond", "Norfolk"))

        report = gate.score()
        assert report.max_similarity["richmond.html"] > 0.85
        assert report.max_similarity["norfolk.html"] > 0.85
        assert report.blocked_pages(0.85) == {"richmond.html", "norfolk.html"}


class TestVariedPagesPass:
    def test_genuinely_different_pages_do_not_block(self):
        gate = UniquenessGate(warn_threshold=0.75, block_threshold=0.85)
        for page_id, html in GENUINELY_DIFFERENT_PAGES.items():
            gate.add_page(f"{page_id}.html", html)

        report = gate.check()  # must not raise

        assert report.blocked_pages(0.85) == set()
        assert report.warned_pages(0.75) == set()

    def test_single_page_never_blocks(self):
        gate = UniquenessGate()
        gate.add_page("only.html", render_city_page("Richmond"))

        report = gate.check()  # must not raise - nothing to compare against

        assert report.max_similarity["only.html"] == 0.0


class TestWarnVsBlock:
    def test_warn_threshold_logs_without_raising_below_block(self, caplog):
        import logging

        # A page with high but not-quite-identical overlap: same structural
        # template with light rewrites, likely landing between warn and block
        gate = UniquenessGate(warn_threshold=0.3, block_threshold=0.99)
        gate.add_page("a.html", render_city_page("Richmond"))
        gate.add_page("b.html", render_city_page("Norfolk"))

        with caplog.at_level(logging.WARNING):
            report = gate.check()  # must not raise - below the (very high) block threshold

        assert report.blocked_pages(0.99) == set()
        assert len(report.warned_pages(0.3)) > 0


class TestPageGeneratorWiring:
    """Test the gate's wiring into PageGenerator.generate_complete_website()
    (the GUI production path) as a pre-publish check."""

    def test_check_content_uniqueness_records_error_on_duplicate_pages(self, tmp_path):
        from core.generators.page_generator import PageGenerator, GenerationResult
        from unittest.mock import MagicMock

        richmond = tmp_path / "richmond.html"
        norfolk = tmp_path / "norfolk.html"
        richmond.write_text(render_city_page("Richmond"), encoding="utf-8")
        norfolk.write_text(render_city_page("Norfolk"), encoding="utf-8")

        result = GenerationResult()
        result.generated_files = [str(richmond), str(norfolk)]

        config = MagicMock()
        config.cloud.content_quality.warn_threshold = 0.75
        config.cloud.content_quality.block_threshold = 0.85

        generator = PageGenerator(output_base_dir=str(tmp_path / "out"))
        generator._check_content_uniqueness(config, result)

        assert len(result.errors) == 1
        assert "too similar" in result.errors[0]

    def test_check_content_uniqueness_passes_on_distinct_pages(self, tmp_path):
        from core.generators.page_generator import PageGenerator, GenerationResult
        from unittest.mock import MagicMock

        files = []
        for page_id, html in GENUINELY_DIFFERENT_PAGES.items():
            path = tmp_path / f"{page_id}.html"
            path.write_text(html, encoding="utf-8")
            files.append(str(path))

        result = GenerationResult()
        result.generated_files = files

        config = MagicMock()
        config.cloud.content_quality.warn_threshold = 0.75
        config.cloud.content_quality.block_threshold = 0.85

        generator = PageGenerator(output_base_dir=str(tmp_path / "out"))
        generator._check_content_uniqueness(config, result)

        assert result.errors == []


class TestWebsiteOrchestratorWiring:
    """Test the gate's wiring into WebsiteOrchestrator.generate() (the CLI
    production path via build_pipeline.py) as a pre-publish check."""

    def test_check_content_uniqueness_raises_on_duplicate_pages(self, tmp_path):
        from core.orchestration.website_orchestrator import WebsiteOrchestrator
        from core.quality.uniqueness_gate import UniquenessGateError
        from unittest.mock import MagicMock

        richmond = tmp_path / "richmond.html"
        norfolk = tmp_path / "norfolk.html"
        richmond.write_text(render_city_page("Richmond"), encoding="utf-8")
        norfolk.write_text(render_city_page("Norfolk"), encoding="utf-8")

        config = MagicMock()
        config.cloud.content_quality.warn_threshold = 0.75
        config.cloud.content_quality.block_threshold = 0.85

        orchestrator = WebsiteOrchestrator(use_ai=False)

        with pytest.raises(UniquenessGateError):
            orchestrator._check_content_uniqueness(config, [str(richmond), str(norfolk)])

    def test_check_content_uniqueness_passes_on_distinct_pages(self, tmp_path):
        from core.orchestration.website_orchestrator import WebsiteOrchestrator
        from unittest.mock import MagicMock

        files = []
        for page_id, html in GENUINELY_DIFFERENT_PAGES.items():
            path = tmp_path / f"{page_id}.html"
            path.write_text(html, encoding="utf-8")
            files.append(str(path))

        config = MagicMock()
        config.cloud.content_quality.warn_threshold = 0.75
        config.cloud.content_quality.block_threshold = 0.85

        orchestrator = WebsiteOrchestrator(use_ai=False)
        orchestrator._check_content_uniqueness(config, files)  # must not raise


class TestReportShape:
    def test_worst_pairs_sorted_descending(self):
        gate = UniquenessGate(warn_threshold=0.1, block_threshold=0.99)
        page_text = render_city_page("Richmond")
        gate.add_page("a.html", page_text)
        gate.add_page("b.html", page_text.replace("Richmond", "Norfolk"))
        for page_id, html in GENUINELY_DIFFERENT_PAGES.items():
            gate.add_page(page_id, html)

        report = gate.score()

        scores = [p.similarity for p in report.worst_pairs]
        assert scores == sorted(scores, reverse=True)

    def test_mean_pairwise_similarity_is_between_0_and_1(self):
        gate = UniquenessGate()
        for page_id, html in GENUINELY_DIFFERENT_PAGES.items():
            gate.add_page(page_id, html)

        report = gate.score()
        assert 0.0 <= report.mean_pairwise_similarity <= 1.0
