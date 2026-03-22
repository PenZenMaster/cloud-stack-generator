"""
Module/Script Name: theme_presets.py
Path: src/core/config/theme_presets.py

Description:
Named color palette presets for the generated website. Each preset defines
a complete set of BrandingConfig color and font values so users can apply
a professional look with one click from the Branding tab.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-22

Last Modified Date:
2026-03-22

Comments:
* v1.00 - Initial implementation for Sprint 5 theme preset feature
"""

from typing import Dict, Any

# Each preset maps BrandingConfig field names -> values.
# All color fields must be valid hex strings (validated by BrandingConfig.__post_init__).

THEME_PRESETS: Dict[str, Dict[str, Any]] = {
    "Default": {
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
        "font_family": "Arial, sans-serif",
    },
    "Midnight Pro": {
        # Dark navy - professional services, consulting, finance
        "primary_color": "#1a1a2e",
        "secondary_color": "#16213e",
        "body_background_color": "#f8f9fa",
        "body_text_color": "#212529",
        "footer_background_color": "#0f3460",
        "footer_text_color": "#e0e0e0",
        "h1_text_color": "#1a1a2e",
        "h2_text_color": "#16213e",
        "h3_text_color": "#0f3460",
        "main_menu_text_color": "#ffffff",
        "font_family": "Trebuchet MS, sans-serif",
    },
    "Forest Service": {
        # Deep greens - landscaping, outdoor, environmental, agriculture
        "primary_color": "#2d6a4f",
        "secondary_color": "#40916c",
        "body_background_color": "#ffffff",
        "body_text_color": "#1b4332",
        "footer_background_color": "#1b4332",
        "footer_text_color": "#d8f3dc",
        "h1_text_color": "#1b4332",
        "h2_text_color": "#2d6a4f",
        "h3_text_color": "#40916c",
        "main_menu_text_color": "#d8f3dc",
        "font_family": "Georgia, serif",
    },
    "Crimson Trades": {
        # Bold red - plumbing, electrical, HVAC, roofing, trades
        "primary_color": "#c0392b",
        "secondary_color": "#922b21",
        "body_background_color": "#ffffff",
        "body_text_color": "#2c2c2c",
        "footer_background_color": "#7b241c",
        "footer_text_color": "#fdfefe",
        "h1_text_color": "#922b21",
        "h2_text_color": "#c0392b",
        "h3_text_color": "#922b21",
        "main_menu_text_color": "#ffffff",
        "font_family": "Arial, sans-serif",
    },
    "Slate Corporate": {
        # Neutral slate - B2B, commercial, industrial, logistics
        "primary_color": "#2c3e50",
        "secondary_color": "#34495e",
        "body_background_color": "#f5f6fa",
        "body_text_color": "#2d3436",
        "footer_background_color": "#1a252f",
        "footer_text_color": "#ecf0f1",
        "h1_text_color": "#2c3e50",
        "h2_text_color": "#34495e",
        "h3_text_color": "#4d6278",
        "main_menu_text_color": "#ecf0f1",
        "font_family": "Calibri, sans-serif",
    },
    "Amber Warmth": {
        # Warm amber/orange - home services, HVAC, restoration, cleaning
        "primary_color": "#e67e22",
        "secondary_color": "#d35400",
        "body_background_color": "#fefefe",
        "body_text_color": "#34302d",
        "footer_background_color": "#7e5109",
        "footer_text_color": "#fdebd0",
        "h1_text_color": "#7e5109",
        "h2_text_color": "#a04000",
        "h3_text_color": "#d35400",
        "main_menu_text_color": "#ffffff",
        "font_family": "Verdana, sans-serif",
    },
    "Ocean Coastal": {
        # Deep ocean blue - marine, coastal, water services, pool/spa
        "primary_color": "#0077b6",
        "secondary_color": "#023e8a",
        "body_background_color": "#f0f8ff",
        "body_text_color": "#03045e",
        "footer_background_color": "#03045e",
        "footer_text_color": "#caf0f8",
        "h1_text_color": "#023e8a",
        "h2_text_color": "#0077b6",
        "h3_text_color": "#0096c7",
        "main_menu_text_color": "#caf0f8",
        "font_family": "Helvetica, sans-serif",
    },
}

# Ordered list for display in UI dropdowns
PRESET_NAMES = list(THEME_PRESETS.keys())


def get_preset(name: str) -> Dict[str, Any]:
    """Return a copy of the named preset dict, or the Default preset if not found."""
    return dict(THEME_PRESETS.get(name, THEME_PRESETS["Default"]))
