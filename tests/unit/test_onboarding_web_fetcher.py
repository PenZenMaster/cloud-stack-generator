"""
Tests for src/core/onboarding/web_fetcher.py

Covers: homepage fetch, page discovery, content extraction, error handling.
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from src.core.onboarding.web_fetcher import (
    MAX_PAGES,
    FetchedPage,
    PageContent,
    WebFetcher,
)


class TestWebFetcherInit:
    def test_normalizes_url_without_scheme(self):
        with patch("src.core.onboarding.web_fetcher.requests"):
            fetcher = WebFetcher("example.com")
        assert fetcher.base_url == "https://example.com"

    def test_strips_trailing_slash(self):
        with patch("src.core.onboarding.web_fetcher.requests"):
            fetcher = WebFetcher("https://example.com/")
        assert fetcher.base_url == "https://example.com"

    def test_sets_base_domain(self):
        with patch("src.core.onboarding.web_fetcher.requests"):
            fetcher = WebFetcher("https://acme.com")
        assert fetcher.base_domain == "acme.com"


class TestFetchHomepage:
    def _make_fetcher(self, url="https://example.com"):
        with patch("src.core.onboarding.web_fetcher.requests"):
            fetcher = WebFetcher(url)
        return fetcher

    def test_returns_fetched_page_on_success(self):
        fetcher = self._make_fetcher()
        mock_resp = Mock()
        mock_resp.url = "https://example.com"
        mock_resp.text = "<html><body>Hello</body></html>"
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "text/html"}

        fetcher._session = Mock()
        fetcher._session.get.return_value = mock_resp

        page = fetcher.fetch_homepage()
        assert page is not None
        assert page.status_code == 200
        assert "Hello" in page.html

    def test_returns_none_on_timeout(self):
        import requests as req_lib
        fetcher = self._make_fetcher()
        fetcher._session = Mock()
        fetcher._session.get.side_effect = req_lib.exceptions.Timeout()

        page = fetcher.fetch_homepage()
        assert page is None

    def test_returns_none_for_non_html_response(self):
        fetcher = self._make_fetcher()
        mock_resp = Mock()
        mock_resp.url = "https://example.com/file.pdf"
        mock_resp.text = "%PDF"
        mock_resp.status_code = 200
        mock_resp.headers = {"Content-Type": "application/pdf"}

        fetcher._session = Mock()
        fetcher._session.get.return_value = mock_resp

        page = fetcher.fetch_homepage()
        assert page is None


class TestDiscoverPages:
    HOMEPAGE_HTML = """
    <html>
    <body>
      <nav>
        <a href="/about">About Us</a>
        <a href="/services">Our Services</a>
        <a href="/contact">Contact</a>
        <a href="https://external.com/page">External</a>
        <a href="/products">Products</a>
      </nav>
    </body>
    </html>
    """

    def _make_fetcher(self, url="https://example.com"):
        with patch("src.core.onboarding.web_fetcher.requests"):
            return WebFetcher(url)

    def test_discovers_relevant_internal_links(self):
        fetcher = self._make_fetcher()
        urls = fetcher.discover_pages(self.HOMEPAGE_HTML)
        assert any("about" in u for u in urls)
        assert any("services" in u for u in urls)
        assert any("contact" in u for u in urls)

    def test_ignores_external_links(self):
        fetcher = self._make_fetcher()
        urls = fetcher.discover_pages(self.HOMEPAGE_HTML)
        assert not any("external.com" in u for u in urls)

    def test_respects_max_pages_cap(self):
        many_links = "".join(
            f'<a href="/services-{i}">Services {i}</a>' for i in range(50)
        )
        html = f"<html><body><nav>{many_links}</nav></body></html>"
        fetcher = self._make_fetcher()
        urls = fetcher.discover_pages(html)
        assert len(urls) <= MAX_PAGES

    def test_deduplicates_links(self):
        html = """
        <html><body>
          <a href="/services">Services</a>
          <a href="/services">Services Again</a>
          <a href="/services/">Services Trailing Slash</a>
        </body></html>
        """
        fetcher = self._make_fetcher()
        urls = fetcher.discover_pages(html)
        service_urls = [u for u in urls if "services" in u]
        assert len(service_urls) == 1


class TestExtractContent:
    def _make_fetcher(self, url="https://example.com"):
        with patch("src.core.onboarding.web_fetcher.requests"):
            return WebFetcher(url)

    def test_extracts_meta_title(self):
        html = "<html><head><title>ACME Plumbing</title></head><body>Text</body></html>"
        page = FetchedPage(url="https://example.com", html=html, status_code=200)
        fetcher = self._make_fetcher()
        content = fetcher.extract_content(page)
        assert content.meta_title == "ACME Plumbing"

    def test_extracts_meta_description(self):
        html = (
            '<html><head>'
            '<meta name="description" content="Best plumber in town">'
            '</head><body>Text</body></html>'
        )
        page = FetchedPage(url="https://example.com", html=html, status_code=200)
        fetcher = self._make_fetcher()
        content = fetcher.extract_content(page)
        assert content.meta_description == "Best plumber in town"

    def test_strips_script_tags(self):
        html = (
            "<html><body>"
            "<script>var x = 1;</script>"
            "<p>Visible content</p>"
            "</body></html>"
        )
        page = FetchedPage(url="https://example.com", html=html, status_code=200)
        fetcher = self._make_fetcher()
        content = fetcher.extract_content(page)
        assert "var x" not in content.text
        assert "Visible content" in content.text

    def test_extracts_css_snippets(self):
        html = (
            "<html><head>"
            "<style>header { background-color: #003366; }</style>"
            "</head><body>Text</body></html>"
        )
        page = FetchedPage(url="https://example.com", html=html, status_code=200)
        fetcher = self._make_fetcher()
        content = fetcher.extract_content(page)
        assert any("#003366" in css for css in content.css_snippets)

    def test_extracts_images(self):
        html = (
            '<html><body>'
            '<img src="/logo.png" alt="Company Logo">'
            '</body></html>'
        )
        page = FetchedPage(url="https://example.com", html=html, status_code=200)
        fetcher = self._make_fetcher()
        content = fetcher.extract_content(page)
        assert len(content.images) == 1
        assert "logo.png" in content.images[0]["src"]
        assert content.images[0]["alt"] == "Company Logo"

    def test_returns_page_content_dataclass(self):
        html = "<html><body>Simple content</body></html>"
        page = FetchedPage(url="https://example.com", html=html, status_code=200)
        fetcher = self._make_fetcher()
        content = fetcher.extract_content(page)
        assert isinstance(content, PageContent)
        assert content.url == "https://example.com"
