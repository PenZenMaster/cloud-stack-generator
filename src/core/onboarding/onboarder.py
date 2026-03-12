"""
Module/Script Name: Onboarder
Path: src/core/onboarding/onboarder.py

Description:
Orchestrates the auto-onboarding pipeline: website fetch -> LLM extraction ->
GBP lookup -> config build -> YAML output. Handles partial failures gracefully
and always produces a config file even when some steps fail.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-11

Last Modified Date:
2026-03-11

Comments:
* v1.00 - Initial implementation
"""

from dataclasses import dataclass, field
from typing import Callable, List, Optional

from ..utils.logger import get_logger
from .config_builder import ConfigBuilder
from .gbp_client import GBPClient, GBPData
from .llm_extractor import ExtractedData, LLMExtractor
from .web_fetcher import PageContent, WebFetcher

logger = get_logger(__name__)


@dataclass
class OnboardResult:
    """Result of a completed auto-onboarding run."""

    success: bool
    output_path: str = ""
    business_name: str = ""
    services_found: int = 0
    products_found: int = 0
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class Onboarder:
    """
    Orchestrates the full auto-onboarding pipeline.

    Given a website URL, GBP share link, and industry, this class fetches
    the website, extracts business data via Claude, fetches GBP details,
    merges the data, and writes an AWG-compatible YAML config file.

    Args:
        url: Client website URL.
        gbp_link: Google Business Profile share link (empty string to skip).
        industry: Business industry string.
        claude_api_key: Anthropic API key for LLM extraction.
        google_api_key: Google Maps / Places API key for GBP lookup.
        model: Claude model preset ('fast', 'balanced', 'thorough').
    """

    def __init__(
        self,
        url: str,
        gbp_link: str,
        industry: str,
        claude_api_key: str,
        google_api_key: Optional[str] = None,
        model: str = "balanced",
    ) -> None:
        self.url = url
        self.gbp_link = gbp_link.strip() if gbp_link else ""
        self.industry = industry
        self.claude_api_key = claude_api_key
        self.google_api_key = google_api_key or ""
        self.model = model

    def run(
        self,
        output_path: Optional[str] = None,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> OnboardResult:
        """
        Execute the full onboarding pipeline.

        Args:
            output_path: Destination YAML file path. Auto-generated if None.
            progress_callback: Optional callable called with step messages for progress display.

        Returns:
            OnboardResult with status, output path, and extraction summary.
        """
        result = OnboardResult(success=False)

        def progress(msg: str) -> None:
            logger.info(msg)
            if progress_callback:
                progress_callback(msg)

        # ------------------------------------------------------------------
        # Step 1: Fetch website pages
        # ------------------------------------------------------------------
        progress("[1/4] Fetching website pages...")
        pages: List[PageContent] = []
        try:
            fetcher = WebFetcher(base_url=self.url)
            pages = fetcher.run()
            progress(f"  Found {len(pages)} page(s)")
        except Exception as exc:
            msg = f"Website fetch failed: {exc}"
            logger.error(msg)
            result.warnings.append(msg)
            progress(f"  WARNING: {msg}")

        # ------------------------------------------------------------------
        # Step 2: Extract business data via LLM
        # ------------------------------------------------------------------
        progress("[2/4] Extracting business data via LLM...")
        llm_data = ExtractedData()
        try:
            extractor = LLMExtractor(
                api_key=self.claude_api_key, model_preset=self.model
            )
            llm_data = extractor.extract_business_data(pages, self.industry)
            progress(f"  Business: {llm_data.business_name or '(not found)'}")
            progress(f"  Services: {len(llm_data.services)}")
            progress(f"  Products: {len(llm_data.products)}")
        except Exception as exc:
            msg = f"LLM extraction failed: {exc}"
            logger.error(msg)
            result.errors.append(msg)
            progress(f"  ERROR: {msg}")

        # ------------------------------------------------------------------
        # Step 3: Fetch Google Business Profile data
        # ------------------------------------------------------------------
        progress("[3/4] Fetching Google Business Profile...")
        gbp_data: Optional[GBPData] = None
        if self.gbp_link:
            try:
                gbp_client = GBPClient(api_key=self.google_api_key or None)
                gbp_data = gbp_client.fetch(self.gbp_link)
                if gbp_data:
                    progress(f"  Business: {gbp_data.business_name}")
                    if gbp_data.street:
                        progress(
                            f"  Address: {gbp_data.street}, "
                            f"{gbp_data.city}, {gbp_data.state} {gbp_data.zip_code}"
                        )
                    if gbp_data.business_hours:
                        progress(
                            f"  Hours: {len(gbp_data.business_hours)} days configured"
                        )
                else:
                    msg = "GBP lookup returned no data"
                    result.warnings.append(msg)
                    progress(f"  WARNING: {msg}")
            except Exception as exc:
                msg = f"GBP lookup failed: {exc}"
                logger.error(msg)
                result.warnings.append(msg)
                progress(f"  WARNING: {msg}")
        else:
            progress("  Skipped (no GBP link provided)")

        # ------------------------------------------------------------------
        # Step 4: Build and write config
        # ------------------------------------------------------------------
        progress("[4/4] Building configuration...")
        try:
            builder = ConfigBuilder(industry=self.industry, website_url=self.url)
            config_dict = builder.build(llm_data=llm_data, gbp_data=gbp_data)

            # Determine business name for output path
            business_name = (
                (
                    gbp_data.business_name
                    if gbp_data and gbp_data.business_name
                    else None
                )
                or llm_data.business_name
                or "new-client"
            )

            if not output_path:
                output_path = builder.generate_output_path(business_name)

            final_path = builder.save_yaml(config_dict, output_path)

            result.success = True
            result.output_path = final_path
            result.business_name = business_name
            result.services_found = len(llm_data.services)
            result.products_found = len(llm_data.products)

        except Exception as exc:
            msg = f"Config build/write failed: {exc}"
            logger.error(msg)
            result.errors.append(msg)
            progress(f"  ERROR: {msg}")

        return result
