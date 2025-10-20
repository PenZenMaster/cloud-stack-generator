"""
Core utilities package for Cloud Stack Generator
Path: E:/projects/cloud-stack-generator/src/core/utils/__init__.py

Description:
Utility modules for API access, bulk processing, string manipulation, and HTML processing.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Last Modified Date:
2025-10-17

Comments:
* v1.01 - Added string_utils and html_utils modules
"""

from .google_maps_api import GoogleMapsAPI, build_google_map_embed, build_google_directions_embed
from .wikipedia_api import WikipediaAPI, build_wikipedia_image_embed, get_city_wikipedia_info
from .csv_bulk_processor import CSVBulkProcessor, CityProcessingResult, BulkProcessingResult, process_cities_bulk
from .string_utils import (
    create_slug,
    generate_city_slug,
    normalize_phone,
    format_phone_display,
)
from .html_utils import (
    format_content_body,
    modify_iframe_size,
)

__all__ = [
    # API utilities
    "GoogleMapsAPI",
    "build_google_map_embed",
    "build_google_directions_embed",
    "WikipediaAPI",
    "build_wikipedia_image_embed",
    "get_city_wikipedia_info",
    # Bulk processing
    "CSVBulkProcessor",
    "CityProcessingResult",
    "BulkProcessingResult",
    "process_cities_bulk",
    # String utilities
    "create_slug",
    "generate_city_slug",
    "normalize_phone",
    "format_phone_display",
    # HTML utilities
    "format_content_body",
    "modify_iframe_size",
]
