"""
Module/Script Name: LLM Extractor
Path: src/core/onboarding/llm_extractor.py

Description:
Uses the Anthropic Claude API to extract structured business data from
fetched website page content during client auto-onboarding. Returns
business name, description, services, products, contact info, social
media URLs, and branding color suggestions.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-11

Last Modified Date:
2026-03-11

Comments:
* v1.00 - Initial implementation
"""

import json
import re
from dataclasses import dataclass, field
from typing import Dict, List

from ..utils.logger import get_logger
from .web_fetcher import PageContent

logger = get_logger(__name__)

try:
    from anthropic import Anthropic, AnthropicError

    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning(
        "anthropic library not installed. Install with: pip install anthropic"
    )

# Model presets - mirrors ClaudeProvider.MODELS
MODEL_PRESETS: Dict[str, str] = {
    "fast": "claude-haiku-4-5-20251001",
    "balanced": "claude-sonnet-4-5-20250929",
    "thorough": "claude-opus-4-6",
}

MAX_TOTAL_CHARS = 50_000
MAX_CSS_CHARS = 5_000


@dataclass
class ExtractedData:
    """Structured business data extracted from website content by the LLM."""

    business_name: str = ""
    description: str = ""
    tagline: str = ""
    contact_name: str = ""
    phone: str = ""
    email: str = ""
    logo_url: str = ""
    services: List[Dict[str, str]] = field(default_factory=list)
    products: List[Dict[str, str]] = field(default_factory=list)
    social_media: Dict[str, str] = field(default_factory=dict)
    branding: Dict[str, str] = field(default_factory=dict)


class LLMExtractor:
    """
    Extracts structured business data from website page content using Claude.

    Args:
        api_key: Anthropic API key.
        model_preset: One of 'fast', 'balanced', 'thorough'. Defaults to 'balanced'.
    """

    def __init__(self, api_key: str, model_preset: str = "balanced") -> None:
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic library required. Install with: pip install anthropic"
            )
        self._model = MODEL_PRESETS.get(model_preset.lower(), MODEL_PRESETS["balanced"])
        self._client = Anthropic(api_key=api_key)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def extract_business_data(
        self, pages: List[PageContent], industry: str
    ) -> ExtractedData:
        """
        Send page content to Claude and return structured ExtractedData.

        Truncates combined page text to MAX_TOTAL_CHARS to stay within the
        model's effective context window.

        Args:
            pages: List of PageContent objects from WebFetcher.
            industry: User-provided industry label (e.g. "plumbing").

        Returns:
            ExtractedData with best-effort populated fields.
        """
        if not pages:
            logger.warning("No page content provided to LLM extractor.")
            return ExtractedData()

        prompt = self._build_extraction_prompt(pages, industry)

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            raw_text = response.content[0].text
            logger.info(
                f"LLM extraction used {response.usage.input_tokens} input / "
                f"{response.usage.output_tokens} output tokens (model: {self._model})"
            )
            return self._parse_response(raw_text)

        except AnthropicError as exc:
            logger.error(f"Claude API error during extraction: {exc}")
            return ExtractedData()
        except Exception as exc:
            logger.error(f"Unexpected LLM error: {exc}")
            return ExtractedData()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _build_extraction_prompt(self, pages: List[PageContent], industry: str) -> str:
        """
        Construct the extraction prompt from page content.

        Combines page text up to MAX_TOTAL_CHARS, then appends CSS snippets
        for color analysis.
        """
        # Aggregate page text (homepage first, then additional pages)
        text_parts: List[str] = []
        total_chars = 0
        all_css: List[str] = []
        all_images: List[str] = []

        for page in pages:
            if total_chars >= MAX_TOTAL_CHARS:
                break
            remaining = MAX_TOTAL_CHARS - total_chars
            chunk = f"--- PAGE: {page.url} ---\n"
            if page.meta_title:
                chunk += f"Title: {page.meta_title}\n"
            if page.meta_description:
                chunk += f"Meta Description: {page.meta_description}\n"
            chunk += page.text[:remaining]
            text_parts.append(chunk)
            total_chars += len(chunk)

            all_css.extend(page.css_snippets)
            for img in page.images[:5]:
                if img.get("src"):
                    all_images.append(img["src"])

        combined_text = "\n\n".join(text_parts)
        css_text = "\n".join(all_css)[:MAX_CSS_CHARS]
        images_text = "\n".join(all_images[:20])

        return f"""You are a data extraction assistant. Extract structured business information from the website content below.

Industry: {industry}

WEBSITE CONTENT:
{combined_text}

CSS SNIPPETS (for color extraction):
{css_text}

IMAGE URLS FOUND ON SITE:
{images_text}

TASK: Extract the following information and return it as valid JSON only.
For any field you cannot find, use an empty string "" or empty array [].
For branding colors, identify hex color codes from CSS or infer from the site's visual style.
For products, generate sequential SKUs: PROD-001, PROD-002, etc.
For services, do not generate SKUs.

REQUIRED JSON SCHEMA:
{{
  "business_name": "string",
  "description": "string (2-4 sentence business description)",
  "tagline": "string (catchy value proposition for hero section)",
  "contact_name": "string (contact person name if found)",
  "phone": "string",
  "email": "string",
  "logo_url": "string (absolute URL of the logo image if found)",
  "services": [
    {{"name": "string", "description": "string"}}
  ],
  "products": [
    {{"sku": "string", "name": "string", "description": "string", "image_url": "string"}}
  ],
  "social_media": {{
    "facebook": "string",
    "twitter": "string",
    "linkedin": "string",
    "instagram": "string",
    "youtube": "string"
  }},
  "branding": {{
    "primary_color": "string (hex, e.g. #007bff - header/nav background)",
    "secondary_color": "string (hex - accent/button color)",
    "body_background_color": "string (hex - main page background)",
    "body_text_color": "string (hex - main body text)",
    "footer_background_color": "string (hex - footer background)",
    "footer_text_color": "string (hex - footer text)",
    "h1_text_color": "string (hex - H1 heading color)",
    "h2_text_color": "string (hex - H2 heading color)",
    "h3_text_color": "string (hex - H3 heading color)",
    "main_menu_text_color": "string (hex - navigation link color)"
  }}
}}

IMPORTANT: Return ONLY the JSON object above. No markdown, no explanation, no code fences."""

    def _parse_response(self, raw_text: str) -> ExtractedData:
        """
        Parse Claude's JSON response into ExtractedData.

        Handles:
        - Clean JSON responses
        - JSON wrapped in markdown code fences
        - Partial / malformed JSON (returns empty ExtractedData with warning)
        """
        # Strip markdown code fences if present
        cleaned = raw_text.strip()
        fence_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", cleaned)
        if fence_match:
            cleaned = fence_match.group(1).strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError:
            # Try to extract a JSON object from the text
            json_match = re.search(r"\{[\s\S]+\}", cleaned)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))
                except json.JSONDecodeError:
                    logger.warning(
                        "LLM returned malformed JSON - using empty extraction."
                    )
                    return ExtractedData()
            else:
                logger.warning("LLM returned no JSON object - using empty extraction.")
                return ExtractedData()

        # Validate and coerce colors - strip any without '#' prefix
        branding = data.get("branding", {})
        clean_branding: Dict[str, str] = {}
        for key, value in branding.items():
            if isinstance(value, str) and value.strip():
                val = value.strip()
                if re.match(r"^#[0-9a-fA-F]{3,6}$", val):
                    clean_branding[key] = val
                else:
                    logger.debug(f"Ignoring non-hex branding color for {key}: {val}")

        return ExtractedData(
            business_name=str(data.get("business_name", "")).strip(),
            description=str(data.get("description", "")).strip(),
            tagline=str(data.get("tagline", "")).strip(),
            contact_name=str(data.get("contact_name", "")).strip(),
            phone=str(data.get("phone", "")).strip(),
            email=str(data.get("email", "")).strip(),
            logo_url=str(data.get("logo_url", "")).strip(),
            services=self._coerce_list(
                data.get("services", []), ("name", "description")
            ),
            products=self._coerce_list(
                data.get("products", []), ("sku", "name", "description", "image_url")
            ),
            social_media={
                k: str(v).strip()
                for k, v in data.get("social_media", {}).items()
                if isinstance(v, str) and v.strip()
            },
            branding=clean_branding,
        )

    def _coerce_list(self, raw: list, required_keys: tuple) -> List[Dict[str, str]]:
        """
        Coerce a raw list of dicts, keeping only items that have at least
        one required key with a non-empty string value.
        """
        result: List[Dict[str, str]] = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            coerced = {k: str(item.get(k, "")).strip() for k in required_keys}
            # Keep if at least the first required key is non-empty
            if coerced.get(required_keys[0]):
                result.append(coerced)
        return result
