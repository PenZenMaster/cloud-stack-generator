"""
Module/Script Name: Content Quality Gate
Path: src/core/generators/content/content_quality_gate.py

Description:
Detects and gates scaled near-duplicate city page content before generation.
seo_authority_city_page.html falls back to static boilerplate paragraphs
(only the city name substituted) whenever CityPageConfig.about_city or
seo_content_body is empty. Left unchecked, a large city_pages batch with
unfilled fields silently mass-produces near-identical pages, which maps
onto Google's scaled content abuse policy.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-08-07

Last Modified Date:
2026-08-07

Comments:
* v1.00 - Initial implementation for issue #35
"""

import logging
from dataclasses import dataclass, field
from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from ...config.models import CityPageConfig

logger = logging.getLogger(__name__)

DEFAULT_TEMPLATE_FALLBACK_PAGE_LIMIT = 10


class ContentQualityGateError(Exception):
    """Raised when generating the requested batch would produce scaled template-fallback content."""


def city_page_uses_template_fallback(city_page: "CityPageConfig") -> Tuple[bool, str]:
    """
    Determine whether a city page will render seo_authority_city_page.html's
    static boilerplate fallback instead of real per-city content.

    Mirrors the {% if %}/{% else %} conditions in that template for
    about_city and seo_content_body - the two fields whose absence triggers
    canned paragraphs with only the city name substituted.
    """
    missing = []
    if not getattr(city_page, "about_city", ""):
        missing.append("about_city")
    if not getattr(city_page, "seo_content_body", ""):
        missing.append("seo_content_body")

    if missing:
        return True, f"missing {' and '.join(missing)}"
    return False, ""


@dataclass
class ContentQualityGate:
    """Gates a batch of city pages against scaled template-fallback content."""

    template_fallback_page_limit: int = DEFAULT_TEMPLATE_FALLBACK_PAGE_LIMIT
    allow_template_fallback: bool = False
    _fallback_pages: List[Tuple[str, str]] = field(default_factory=list, init=False)

    def check_batch(self, city_pages: List["CityPageConfig"]) -> None:
        """
        Scan a batch of city pages before generation and raise if too many
        would fall back to static boilerplate content, unless explicitly
        allowed.

        Raises:
            ContentQualityGateError: if the number of pages using template
                fallback exceeds template_fallback_page_limit and
                allow_template_fallback is False.
        """
        self._fallback_pages = []
        for city_page in city_pages:
            uses_fallback, reason = city_page_uses_template_fallback(city_page)
            if uses_fallback:
                self._fallback_pages.append((city_page.city_name, reason))
                logger.warning(
                    f"City page '{city_page.city_name}' will use template fallback content: {reason}"
                )

        if not self._fallback_pages or self.allow_template_fallback:
            return

        if len(self._fallback_pages) > self.template_fallback_page_limit:
            preview = ", ".join(name for name, _ in self._fallback_pages[:10])
            more = f", and {len(self._fallback_pages) - 10} more" if len(self._fallback_pages) > 10 else ""
            raise ContentQualityGateError(
                f"{len(self._fallback_pages)} of {len(city_pages)} city pages have no real "
                f"content configured (about_city / seo_content_body) and would render identical "
                f"boilerplate paragraphs with only the city name substituted, exceeding the "
                f"template_fallback_page_limit of {self.template_fallback_page_limit}. This risks "
                f"a Google scaled content abuse penalty. Populate content for these cities, or "
                f"pass allow_template_fallback=True (--allow-template-fallback on the CLI) to "
                f"proceed deliberately. Affected cities: {preview}{more}"
            )

    @property
    def fallback_count(self) -> int:
        return len(self._fallback_pages)

    @property
    def fallback_cities(self) -> List[str]:
        return [name for name, _ in self._fallback_pages]

    def summary(self) -> str:
        """One-line summary suitable for surfacing as a GenerationResult warning."""
        if not self._fallback_pages:
            return ""

        cities = ", ".join(self.fallback_cities[:10])
        more = f", and {len(self._fallback_pages) - 10} more" if len(self._fallback_pages) > 10 else ""
        return (
            f"{len(self._fallback_pages)} city page(s) used template fallback content "
            f"(missing about_city/seo_content_body): {cities}{more}"
        )
