"""
Default Theme Configuration
Path: src/ui/themes/default_theme.py

Comprehensive UI theme system with standardized colors, typography, spacing, and button styles.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-23

Last Modified Date:
2025-11-23

Comments:
* v1.00 - Initial theme system for v3.5.0
* Standardizes all UI button styles, colors, and typography
"""

from typing import Dict


class ColorPalette:
    """
    Centralized color palette for the application.
    All colors follow Material Design and Bootstrap conventions.
    """

    # Primary Action Colors
    AI_BLUE = "#007bff"           # AI-powered features
    AI_BLUE_HOVER = "#0056b3"
    AI_BLUE_PRESSED = "#004085"

    SUCCESS_GREEN = "#28a745"     # Primary actions, generation
    SUCCESS_GREEN_HOVER = "#218838"
    SUCCESS_GREEN_PRESSED = "#1e7e34"

    VALIDATION_PURPLE = "#9b59b6"  # Data validation
    VALIDATION_PURPLE_HOVER = "#8e44ad"
    VALIDATION_PURPLE_PRESSED = "#732d91"

    IMPORT_GREEN = "#27ae60"      # Import actions
    IMPORT_GREEN_HOVER = "#219a52"
    IMPORT_GREEN_PRESSED = "#1d8743"

    EXPORT_BLUE = "#3498db"       # Export actions
    EXPORT_BLUE_HOVER = "#2980b9"
    EXPORT_BLUE_PRESSED = "#216696"

    DANGER_RED = "#e74c3c"        # Destructive actions
    DANGER_RED_HOVER = "#c0392b"
    DANGER_RED_PRESSED = "#962d20"

    DISABLED_GRAY = "#95a5a6"     # Inactive state

    # UI Element Colors
    WHITE = "#ffffff"
    BLACK = "#000000"

    # Background Colors
    BG_PRIMARY = "#f8f9fa"
    BG_SECONDARY = "#e9ecef"
    BG_DARK = "#343a40"

    # Text Colors
    TEXT_PRIMARY = "#212529"
    TEXT_SECONDARY = "#6c757d"
    TEXT_LIGHT = "#ffffff"

    # Border Colors
    BORDER_LIGHT = "#dee2e6"
    BORDER_DARK = "#495057"


class Typography:
    """Typography configuration for consistent font usage across the application."""

    FONT_FAMILY = "Arial"

    # Font Sizes
    SIZE_SMALL = 10
    SIZE_NORMAL = 12
    SIZE_LARGE = 14
    SIZE_XLARGE = 16

    # Font Weights
    WEIGHT_NORMAL = "normal"
    WEIGHT_BOLD = "bold"


class Spacing:
    """Spacing and sizing constants for consistent layout."""

    # Padding
    PADDING_SMALL = "6px 12px"
    PADDING_NORMAL = "8px 16px"
    PADDING_LARGE = "10px 20px"

    # Border Radius
    RADIUS_SMALL = 4
    RADIUS_NORMAL = 6
    RADIUS_LARGE = 8

    # Margins
    MARGIN_SMALL = 8
    MARGIN_NORMAL = 12
    MARGIN_LARGE = 16


# Base button template (module-level for use in class definitions)
_BUTTON_TEMPLATE = """
    QPushButton {{
        background-color: {color};
        color: {text_color};
        font-family: {font_family};
        font-size: {font_size}pt;
        font-weight: {font_weight};
        padding: {padding};
        border: none;
        border-radius: {radius}px;
    }}
    QPushButton:hover {{
        background-color: {hover_color};
    }}
    QPushButton:pressed {{
        background-color: {pressed_color};
    }}
    QPushButton:disabled {{
        background-color: {disabled_color};
        color: {disabled_text_color};
    }}
"""


def _generate_button_style(
    color: str,
    hover_color: str,
    pressed_color: str,
    text_color: str = ColorPalette.WHITE,
    font_family: str = Typography.FONT_FAMILY,
    font_size: int = Typography.SIZE_NORMAL,
    font_weight: str = Typography.WEIGHT_BOLD,
    padding: str = Spacing.PADDING_NORMAL,
    radius: int = Spacing.RADIUS_NORMAL,
    disabled_color: str = ColorPalette.DISABLED_GRAY,
    disabled_text_color: str = ColorPalette.WHITE
) -> str:
    """Generate button stylesheet with given parameters."""
    return _BUTTON_TEMPLATE.format(
        color=color,
        hover_color=hover_color,
        pressed_color=pressed_color,
        text_color=text_color,
        font_family=font_family,
        font_size=font_size,
        font_weight=font_weight,
        padding=padding,
        radius=radius,
        disabled_color=disabled_color,
        disabled_text_color=disabled_text_color
    )


class ButtonStyles:
    """
    Comprehensive button style definitions.

    Usage:
        button = QPushButton("Generate")
        button.setStyleSheet(ButtonStyles.AI_GENERATION)
    """

    # Pre-defined Button Styles
    AI_GENERATION = _generate_button_style(
        color=ColorPalette.AI_BLUE,
        hover_color=ColorPalette.AI_BLUE_HOVER,
        pressed_color=ColorPalette.AI_BLUE_PRESSED
    )

    SUCCESS = _generate_button_style(
        color=ColorPalette.SUCCESS_GREEN,
        hover_color=ColorPalette.SUCCESS_GREEN_HOVER,
        pressed_color=ColorPalette.SUCCESS_GREEN_PRESSED
    )

    VALIDATION = _generate_button_style(
        color=ColorPalette.VALIDATION_PURPLE,
        hover_color=ColorPalette.VALIDATION_PURPLE_HOVER,
        pressed_color=ColorPalette.VALIDATION_PURPLE_PRESSED
    )

    IMPORT = _generate_button_style(
        color=ColorPalette.IMPORT_GREEN,
        hover_color=ColorPalette.IMPORT_GREEN_HOVER,
        pressed_color=ColorPalette.IMPORT_GREEN_PRESSED
    )

    EXPORT = _generate_button_style(
        color=ColorPalette.EXPORT_BLUE,
        hover_color=ColorPalette.EXPORT_BLUE_HOVER,
        pressed_color=ColorPalette.EXPORT_BLUE_PRESSED
    )

    DANGER = _generate_button_style(
        color=ColorPalette.DANGER_RED,
        hover_color=ColorPalette.DANGER_RED_HOVER,
        pressed_color=ColorPalette.DANGER_RED_PRESSED
    )

    DISABLED = _generate_button_style(
        color=ColorPalette.DISABLED_GRAY,
        hover_color=ColorPalette.DISABLED_GRAY,
        pressed_color=ColorPalette.DISABLED_GRAY
    )


class ThemeManager:
    """
    Central theme management class.
    Provides convenient methods to apply styles to UI elements.

    Usage:
        # Apply button style
        ThemeManager.apply_button_style(my_button, "ai_generation")

        # Get custom button style
        custom_style = ThemeManager.get_button_style(
            color="#ff5722",
            hover_color="#e64a19",
            pressed_color="#d84315"
        )
    """

    # Button style mappings
    BUTTON_STYLES: Dict[str, str] = {
        "ai_generation": ButtonStyles.AI_GENERATION,
        "ai": ButtonStyles.AI_GENERATION,
        "success": ButtonStyles.SUCCESS,
        "generate": ButtonStyles.SUCCESS,
        "validation": ButtonStyles.VALIDATION,
        "validate": ButtonStyles.VALIDATION,
        "import": ButtonStyles.IMPORT,
        "export": ButtonStyles.EXPORT,
        "danger": ButtonStyles.DANGER,
        "delete": ButtonStyles.DANGER,
        "disabled": ButtonStyles.DISABLED,
    }

    @staticmethod
    def apply_button_style(button, style_name: str):
        """
        Apply a pre-defined button style to a QPushButton.

        Args:
            button: QPushButton instance
            style_name: Name of the style (ai_generation, success, validation, etc.)

        Example:
            btn = QPushButton("Generate")
            ThemeManager.apply_button_style(btn, "success")
        """
        style_name = style_name.lower()
        if style_name in ThemeManager.BUTTON_STYLES:
            button.setStyleSheet(ThemeManager.BUTTON_STYLES[style_name])
        else:
            raise ValueError(
                f"Unknown button style: {style_name}. "
                f"Available styles: {', '.join(ThemeManager.BUTTON_STYLES.keys())}"
            )

    @staticmethod
    def get_button_style(
        color: str,
        hover_color: str,
        pressed_color: str,
        **kwargs
    ) -> str:
        """
        Generate a custom button style with specified colors.

        Args:
            color: Base button color
            hover_color: Hover state color
            pressed_color: Pressed state color
            **kwargs: Additional style parameters (text_color, font_size, etc.)

        Returns:
            CSS stylesheet string

        Example:
            custom_style = ThemeManager.get_button_style(
                color="#ff5722",
                hover_color="#e64a19",
                pressed_color="#d84315",
                font_size=14
            )
            button.setStyleSheet(custom_style)
        """
        return _generate_button_style(
            color=color,
            hover_color=hover_color,
            pressed_color=pressed_color,
            **kwargs
        )

    @staticmethod
    def get_available_styles() -> list:
        """Get list of available pre-defined button styles."""
        return list(ThemeManager.BUTTON_STYLES.keys())


# Convenience aliases for backward compatibility
BUTTON_AI = ButtonStyles.AI_GENERATION
BUTTON_SUCCESS = ButtonStyles.SUCCESS
BUTTON_VALIDATION = ButtonStyles.VALIDATION
BUTTON_IMPORT = ButtonStyles.IMPORT
BUTTON_EXPORT = ButtonStyles.EXPORT
BUTTON_DANGER = ButtonStyles.DANGER
BUTTON_DISABLED = ButtonStyles.DISABLED
