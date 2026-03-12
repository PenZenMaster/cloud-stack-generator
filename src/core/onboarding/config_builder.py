"""
Module/Script Name: Config Builder
Path: src/core/onboarding/config_builder.py

Description:
Merges LLM-extracted website data and Google Business Profile data into
a YAML client config dict compatible with the AWG ConfigParser. Writes
the result to a file using the standard YAML serialization format.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-11

Last Modified Date:
2026-03-11

Comments:
* v1.00 - Initial implementation
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from ..utils.logger import get_logger
from .gbp_client import GBPData
from .llm_extractor import ExtractedData

logger = get_logger(__name__)

# BrandingConfig defaults - used when LLM cannot extract a color
BRANDING_DEFAULTS: Dict[str, str] = {
    "primary_color": "#007bff",
    "secondary_color": "#6c757d",
    "body_background_color": "#ffffff",
    "body_text_color": "#333333",
    "footer_background_color": "#2c3e50",
    "footer_text_color": "#ffffff",
    "h1_text_color": "#2c3e50",
    "h2_text_color": "#34495e",
    "h3_text_color": "#34495e",
    "main_menu_text_color": "#ffffff",
}


class ConfigBuilder:
    """
    Merges extracted data into an AWG-compatible YAML client config dict.

    Merge priority:
      - GBP wins for: business_name (if present), phone, address, lat/lng, hours
      - LLM wins for: description, tagline, services, products, branding, email, social media
      - User input is authoritative for: industry, website URL

    Args:
        industry: User-provided industry string.
        website_url: User-provided website URL.
    """

    def __init__(self, industry: str, website_url: str) -> None:
        self.industry = industry
        self.website_url = website_url

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def build(
        self,
        llm_data: ExtractedData,
        gbp_data: Optional[GBPData] = None,
    ) -> Dict[str, Any]:
        """
        Merge LLM and GBP data into a YAML config dict.

        Args:
            llm_data: Data extracted by LLMExtractor.
            gbp_data: Data fetched from Google Business Profile (may be None).

        Returns:
            A dict with a top-level 'client' key that ConfigParser can parse.
        """
        return {
            "client": {
                **self._build_business_section(llm_data, gbp_data),
                "contact": self._build_contact_section(llm_data, gbp_data),
                "branding": self._build_branding_section(llm_data),
                "social_media": self._build_social_media(llm_data),
                "google_business_profile": self._build_gbp_section(gbp_data),
                "offerings": self._build_offerings(llm_data),
                "pages": self._build_default_pages(llm_data, gbp_data),
            }
        }

    def save_yaml(self, yaml_dict: Dict[str, Any], output_path: str) -> str:
        """
        Write the config dict to a YAML file.

        Args:
            yaml_dict: The config dict (with 'client' top-level key).
            output_path: Destination file path.

        Returns:
            Absolute path to the written file.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding="utf-8") as fh:
            yaml.dump(
                yaml_dict,
                fh,
                default_flow_style=False,
                sort_keys=False,
                indent=2,
                allow_unicode=True,
            )

        logger.info(f"Config written to: {path.resolve()}")
        return str(path.resolve())

    def generate_output_path(
        self, business_name: str, base_dir: str = "config/clients"
    ) -> str:
        """
        Generate a file path for the config based on the business name.

        Args:
            business_name: The extracted or GBP business name.
            base_dir: Base directory for client configs.

        Returns:
            Relative file path string.
        """
        slug = self._slugify(business_name) if business_name else "new-client"
        return f"{base_dir}/{slug}/{slug}_config.yaml"

    # ------------------------------------------------------------------
    # Private section builders
    # ------------------------------------------------------------------

    def _build_business_section(
        self, llm: ExtractedData, gbp: Optional[GBPData]
    ) -> Dict[str, Any]:
        """Populate top-level business fields."""
        # GBP business name takes priority if present
        business_name = (
            (gbp.business_name if gbp and gbp.business_name else None)
            or llm.business_name
            or ""
        )
        domain = self.website_url or (gbp.website if gbp else "") or ""

        return {
            "business_name": business_name,
            "domain": domain,
            "industry": self.industry,
            "description": llm.description or "",
            "tagline": llm.tagline or "",
        }

    def _build_contact_section(
        self, llm: ExtractedData, gbp: Optional[GBPData]
    ) -> Dict[str, Any]:
        """Populate contact section. GBP wins for phone/address/hours."""
        # Phone: GBP > LLM
        phone = (gbp.phone if gbp and gbp.phone else None) or llm.phone or ""
        email = llm.email or ""
        contact_name = llm.contact_name or ""

        # Address: from GBP only (structured and reliable)
        address: Dict[str, Any] = {}
        latitude = 0.0
        longitude = 0.0
        if gbp and gbp.street:
            address = {
                "street": gbp.street,
                "city": gbp.city,
                "state": gbp.state,
                "zip_code": gbp.zip_code,
                "country": gbp.country,
            }
            latitude = gbp.latitude
            longitude = gbp.longitude

        # Business hours: GBP > default empty
        hours = gbp.business_hours if gbp and gbp.business_hours else {}

        section: Dict[str, Any] = {
            "name": contact_name,
            "phone": phone,
            "email": email,
        }
        if address:
            section["address"] = address
            if latitude or longitude:
                section["latitude"] = latitude
                section["longitude"] = longitude
        if hours:
            section["business_hours"] = hours

        return section

    def _build_branding_section(self, llm: ExtractedData) -> Dict[str, Any]:
        """Populate branding colors. LLM extraction takes priority; defaults fill gaps."""
        branding: Dict[str, Any] = {}
        for key, default_val in BRANDING_DEFAULTS.items():
            branding[key] = llm.branding.get(key) or default_val

        if llm.logo_url:
            branding["logo_url"] = llm.logo_url

        return branding

    def _build_social_media(self, llm: ExtractedData) -> Dict[str, str]:
        """Populate social media URLs from LLM extraction."""
        platforms = ["facebook", "twitter", "linkedin", "instagram", "youtube"]
        return {p: llm.social_media.get(p, "") for p in platforms}

    def _build_gbp_section(self, gbp: Optional[GBPData]) -> Dict[str, Any]:
        """Populate the google_business_profile section."""
        if not gbp:
            return {}
        section: Dict[str, Any] = {}
        if gbp.place_id:
            section["place_id"] = gbp.place_id
        if gbp.profile_url:
            section["profile_url"] = gbp.profile_url
        if gbp.rating:
            section["rating"] = gbp.rating
        if gbp.review_count:
            section["review_count"] = gbp.review_count
        return section

    def _build_offerings(self, llm: ExtractedData) -> List[Dict[str, Any]]:
        """
        Combine services and products into the 'offerings' list.

        Services get type='service'; products get type='product'.
        """
        offerings: List[Dict[str, Any]] = []

        for svc in llm.services:
            offerings.append(
                {
                    "name": svc.get("name", ""),
                    "description": svc.get("description", ""),
                    "category": "",
                    "type": "service",
                }
            )

        for prod in llm.products:
            offerings.append(
                {
                    "sku": prod.get("sku", ""),
                    "name": prod.get("name", ""),
                    "description": prod.get("description", ""),
                    "image_url": prod.get("image_url", ""),
                    "category": "",
                    "type": "product",
                }
            )

        return offerings

    def _build_default_pages(
        self, llm: ExtractedData, gbp: Optional[GBPData]
    ) -> List[Dict[str, Any]]:
        """Create a minimal set of standard pages for the config."""
        industry_lower = self.industry.lower()
        business_name = (
            (gbp.business_name if gbp and gbp.business_name else None)
            or llm.business_name
            or ""
        )

        return [
            {
                "title": "Home",
                "slug": "index",
                "primary_keyword": f"{industry_lower} services",
                "secondary_keywords": [industry_lower, business_name],
                "hero_image": "",
            },
            {
                "title": "About Us",
                "slug": "about",
                "primary_keyword": f"about {business_name}".strip(),
                "secondary_keywords": [industry_lower],
                "hero_image": "",
            },
            {
                "title": "Services",
                "slug": "services",
                "primary_keyword": f"{industry_lower} services",
                "secondary_keywords": [],
                "hero_image": "",
            },
            {
                "title": "Contact Us",
                "slug": "contact",
                "primary_keyword": f"contact {business_name}".strip(),
                "secondary_keywords": [],
                "hero_image": "",
            },
        ]

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def _slugify(self, text: str) -> str:
        """Convert a business name to a URL-safe slug."""
        slug = text.lower().strip()
        slug = re.sub(r"[^a-z0-9\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug)
        slug = slug.strip("-")
        return slug or "client"
