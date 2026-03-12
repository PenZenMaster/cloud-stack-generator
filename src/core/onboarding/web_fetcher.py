"""
Module/Script Name: Web Fetcher
Path: src/core/onboarding/web_fetcher.py

Description:
Fetches client website pages and extracts visible text, CSS snippets, meta tags,
and image references for use by the LLM extraction step of auto-onboarding.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-11

Last Modified Date:
2026-03-11

Comments:
* v1.00 - Initial implementation
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from urllib.parse import urlparse, urljoin

from ..utils.logger import get_logger

logger = get_logger(__name__)

try:
    import requests
    from bs4 import BeautifulSoup

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests and/or beautifulsoup4 not installed.")

# Keywords used to identify relevant internal pages
PAGE_KEYWORDS = {
    "about",
    "service",
    "services",
    "product",
    "products",
    "contact",
    "team",
    "staff",
    "what-we-do",
    "offerings",
    "solutions",
    "portfolio",
    "work",
    "capabilities",
}

MAX_PAGES = 10
REQUEST_TIMEOUT = 15
FETCH_DELAY = 0.5  # seconds between page fetches
MAX_CONTENT_CHARS = 50_000  # total chars sent to LLM


@dataclass
class FetchedPage:
    """Raw HTTP response from a fetched page."""

    url: str
    html: str
    status_code: int


@dataclass
class PageContent:
    """Extracted content from a parsed HTML page."""

    url: str
    text: str
    css_snippets: List[str] = field(default_factory=list)
    meta_title: str = ""
    meta_description: str = ""
    images: List[Dict[str, str]] = field(default_factory=list)


class WebFetcher:
    """
    Fetches the client website homepage and relevant linked pages,
    then extracts text and CSS for downstream LLM extraction.

    Args:
        base_url: The client website URL (homepage).
        timeout: HTTP request timeout in seconds.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    def __init__(self, base_url: str, timeout: int = REQUEST_TIMEOUT) -> None:
        if not REQUESTS_AVAILABLE:
            raise ImportError(
                "requests and beautifulsoup4 are required. "
                "Install with: pip install requests beautifulsoup4"
            )
        self.base_url = self._normalize_url(base_url)
        self.base_domain = urlparse(self.base_url).netloc
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({"User-Agent": self.USER_AGENT})

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch_homepage(self) -> Optional[FetchedPage]:
        """Fetch the homepage. Returns None if the request fails."""
        return self._get(self.base_url)

    def discover_pages(self, homepage_html: str) -> List[str]:
        """
        Parse the homepage HTML and return a list of relevant internal page URLs.

        Only includes same-domain links whose href or link text matches PAGE_KEYWORDS.
        Capped at MAX_PAGES total URLs.

        Args:
            homepage_html: Raw HTML of the homepage.

        Returns:
            List of absolute URLs to fetch next.
        """
        soup = BeautifulSoup(homepage_html, "html.parser")
        seen: set = set()
        discovered: List[str] = []

        for tag in soup.find_all("a", href=True):
            href = tag["href"].strip()
            text = tag.get_text(strip=True).lower()
            abs_url = urljoin(self.base_url, href)
            parsed = urlparse(abs_url)

            # Same-domain check
            if parsed.netloc != self.base_domain:
                continue

            # Skip anchors, mailto, tel, query-only links
            if (
                not parsed.path
                or parsed.path == "/"
                or parsed.scheme not in ("http", "https")
            ):
                continue

            # Keyword match in href path or link text
            path_lower = parsed.path.lower()
            if not self._is_relevant_page(path_lower, text):
                continue

            # Deduplicate
            canonical = abs_url.split("?")[0].split("#")[0].rstrip("/")
            if canonical in seen or canonical == self.base_url.rstrip("/"):
                continue

            seen.add(canonical)
            discovered.append(canonical)

            if len(discovered) >= MAX_PAGES:
                break

        return discovered

    def fetch_pages(self, urls: List[str]) -> List[FetchedPage]:
        """
        Fetch each URL in the list, skipping failures.

        Applies a short delay between requests to be polite.

        Args:
            urls: List of absolute URLs to fetch.

        Returns:
            List of successfully fetched FetchedPage objects.
        """
        pages: List[FetchedPage] = []
        for url in urls:
            time.sleep(FETCH_DELAY)
            page = self._get(url)
            if page:
                pages.append(page)
        return pages

    def extract_content(self, page: FetchedPage) -> PageContent:
        """
        Parse a FetchedPage into structured PageContent.

        Strips scripts, styles, navigation, and other boilerplate. Retains
        visible text, inline CSS, meta tags, and image src/alt pairs.

        Args:
            page: A successfully fetched page.

        Returns:
            PageContent with text, css_snippets, meta tags, and images.
        """
        soup = BeautifulSoup(page.html, "html.parser")

        # Extract meta tags before stripping
        meta_title = ""
        title_tag = soup.find("title")
        if title_tag:
            meta_title = title_tag.get_text(strip=True)

        meta_description = ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag and desc_tag.get("content"):
            meta_description = desc_tag["content"].strip()

        # Collect CSS snippets from inline <style> blocks and relevant style attrs
        css_snippets: List[str] = []
        for style_tag in soup.find_all("style"):
            snippet = style_tag.get_text()
            if snippet.strip():
                css_snippets.append(snippet[:2000])  # cap per snippet

        # Collect style attributes from structural elements
        for selector in ["header", "nav", "footer", "body", "main", "section"]:
            for elem in soup.find_all(selector, style=True):
                css_snippets.append(f"{selector} {{ {elem['style']} }}")

        # Extract images (src + alt)
        images: List[Dict[str, str]] = []
        for img in soup.find_all("img", src=True)[:20]:
            src = img.get("src", "").strip()
            alt = img.get("alt", "").strip()
            if src:
                abs_src = urljoin(page.url, src)
                images.append({"src": abs_src, "alt": alt})

        # Remove non-content tags
        for tag in soup.find_all(
            ["script", "style", "noscript", "svg", "iframe", "head"]
        ):
            tag.decompose()

        visible_text = soup.get_text(separator=" ", strip=True)
        # Collapse excessive whitespace
        import re

        visible_text = re.sub(r"\s{3,}", "  ", visible_text)

        return PageContent(
            url=page.url,
            text=visible_text[:10_000],  # per-page cap
            css_snippets=css_snippets[:5],  # limit snippets per page
            meta_title=meta_title,
            meta_description=meta_description,
            images=images,
        )

    def run(self) -> List[PageContent]:
        """
        Convenience method: fetch homepage + discovered pages, return all PageContent.

        Returns:
            List of PageContent objects (homepage first, then discovered pages).
        """
        homepage = self.fetch_homepage()
        if not homepage:
            logger.warning(f"Could not fetch homepage: {self.base_url}")
            return []

        content_list: List[PageContent] = [self.extract_content(homepage)]

        discovered_urls = self.discover_pages(homepage.html)
        logger.info(f"Discovered {len(discovered_urls)} additional pages")

        additional_pages = self.fetch_pages(discovered_urls)
        for page in additional_pages:
            content_list.append(self.extract_content(page))

        return content_list

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _normalize_url(self, url: str) -> str:
        """Ensure the URL has a scheme."""
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            url = f"https://{url}"
        return url.rstrip("/")

    def _is_relevant_page(self, path: str, link_text: str) -> bool:
        """Return True if the page path or link text matches a keyword."""
        for keyword in PAGE_KEYWORDS:
            if keyword in path or keyword in link_text:
                return True
        return False

    def _get(self, url: str) -> Optional[FetchedPage]:
        """Perform an HTTP GET. Returns None on failure."""
        try:
            resp = self._session.get(url, timeout=self.timeout, allow_redirects=True)
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type:
                logger.debug(f"Skipping non-HTML response: {url} ({content_type})")
                return None
            return FetchedPage(
                url=resp.url, html=resp.text, status_code=resp.status_code
            )
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout fetching {url}")
            return None
        except requests.exceptions.RequestException as exc:
            logger.warning(f"Failed to fetch {url}: {exc}")
            return None
