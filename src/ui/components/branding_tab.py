"""
Filename: branding_tab.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\components\\branding_tab.py
Description: Branding configuration tab with color pickers, font selection, and logo management
Handles visual branding elements with live preview and validation

Version: 1.0.0
Date: 2025-08-11
Author: Cloud Stack Generator Team
"""

import re
import os
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFrame,
    QGroupBox,
    QColorDialog,
    QSpacerItem,
    QSizePolicy,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtGui import QFont, QColor, QPalette
from PyQt6.QtCore import Qt, pyqtSignal
from .base_tab import BaseTab
from typing import Dict, Any, List, Tuple


class ValidationResult:
    """Validation result container"""

    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, message: str):
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        self.warnings.append(message)


class BrandingTab(BaseTab):
    """Tab for branding configuration with color and font management"""

    # Signals
    config_changed = pyqtSignal()
    validation_requested = pyqtSignal()
    data_loaded = pyqtSignal()

    # Default colors
    DEFAULT_PRIMARY = "#007bff"
    DEFAULT_SECONDARY = "#6c757d"

    # Web-safe fonts
    WEB_FONTS = [
        "Arial, sans-serif",
        "Helvetica, sans-serif",
        "Times New Roman, serif",
        "Georgia, serif",
        "Verdana, sans-serif",
        "Calibri, sans-serif",
        "Trebuchet MS, sans-serif",
        "Courier New, monospace",
        "Lucida Console, monospace",
        "Impact, sans-serif",
    ]

    def __init__(self, parent=None):
        self.branding_inputs = {}
        self.color_buttons = {}
        self.preview_labels = {}
        self.error_labels = {}
        self.current_colors = {
            "primary": self.DEFAULT_PRIMARY,
            "secondary": self.DEFAULT_SECONDARY,
        }
        self.has_changes = False
        super().__init__(parent)

    def setup_ui(self):
        """Setup branding configuration UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Create main sections
        self._create_color_section(main_layout)
        self._create_font_section(main_layout)
        self._create_logo_section(main_layout)
        self._create_preview_section(main_layout)

        # Add stretch to push content to top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def _create_color_section(self, parent_layout: QVBoxLayout):
        """Create color selection section"""
        # Section header
        header_label = self._create_section_header("Brand Colors")
        parent_layout.addWidget(header_label)

        # Color form
        color_group = QGroupBox()
        color_layout = QGridLayout()
        color_layout.setSpacing(15)

        # Color fields
        colors = [
            ("Primary Color", "primary", "Main brand color for headers and highlights"),
            (
                "Secondary Color",
                "secondary",
                "Supporting color for accents and backgrounds",
            ),
        ]

        row = 0
        for label_text, color_key, description in colors:
            # Label
            label = QLabel(f"* {label_text}")
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

            # Color input and button container
            color_container = QHBoxLayout()

            # Hex input
            hex_input = QLineEdit()
            hex_input.setFont(QFont("Arial", 10))
            hex_input.setPlaceholderText("#FFFFFF")
            hex_input.setMaximumWidth(100)
            # Enhanced input styling for better scaling
            hex_input.setStyleSheet("""
                QLineEdit {
                    min-height: 25px;
                    padding: 5px;
                    font-size: inherit;
                    border: 1px solid #ccc;
                    border-radius: 3px;
                }
                QLineEdit:focus {
                    border: 2px solid #007bff;
                }
            """)
            hex_input.textChanged.connect(lambda text, key=color_key: self._on_hex_input_changed(key, text))

            # Color picker button
            color_button = QPushButton()
            color_button.setMaximumWidth(50)
            color_button.setMinimumHeight(30)
            color_button.clicked.connect(
                lambda checked, key=color_key: self._open_color_picker(key)
            )

            # Preview label
            preview_label = QLabel("Sample")
            preview_label.setFont(QFont("Arial", 9, QFont.Weight.Bold))
            preview_label.setMinimumHeight(30)
            preview_label.setStyleSheet(
                "border: 1px solid #ccc; padding: 5px; border-radius: 3px;"
            )

            color_container.addWidget(hex_input)
            color_container.addWidget(color_button)
            color_container.addWidget(preview_label)
            color_container.addStretch()

            # Description
            desc_label = QLabel(description)
            desc_label.setFont(QFont("Arial", 8))
            desc_label.setStyleSheet("color: #666; font-style: italic;")

            # Error label
            error_label = self._create_error_label(f"{color_key}_color")

            # Layout
            color_layout.addWidget(label, row, 0)
            color_layout.addLayout(color_container, row, 1)
            color_layout.addWidget(desc_label, row + 1, 1)
            color_layout.addWidget(error_label, row + 2, 1)

            # Store references
            self.branding_inputs[f"{color_key}_color"] = hex_input
            self.color_buttons[color_key] = color_button
            self.preview_labels[color_key] = preview_label

            # Set default colors
            default_color = (
                self.DEFAULT_PRIMARY
                if color_key == "primary"
                else self.DEFAULT_SECONDARY
            )
            hex_input.setText(default_color)
            self._update_color_display(color_key, default_color)

            row += 3

        color_group.setLayout(color_layout)
        parent_layout.addWidget(color_group)

    def _create_font_section(self, parent_layout: QVBoxLayout):
        """Create font selection section"""
        # Section header
        header_label = self._create_section_header("Typography")
        parent_layout.addWidget(header_label)

        # Font form
        font_group = QGroupBox()
        font_layout = QGridLayout()
        font_layout.setSpacing(10)

        # Font family selection
        font_label = QLabel("* Font Family")
        font_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        font_combo = QComboBox()
        font_combo.setFont(QFont("Arial", 10))
        # Enhanced font scaling support
        font_combo.setStyleSheet("""
            QComboBox {
                min-height: 25px;
                padding: 5px;
                font-size: inherit;
            }
            QComboBox::drop-down {
                width: 20px;
            }
        """)
        font_combo.addItems(self.WEB_FONTS)
        font_combo.setCurrentText("Arial, sans-serif")
        font_combo.currentTextChanged.connect(self._on_font_changed)

        # Font preview
        font_preview = QLabel("The quick brown fox jumps over the lazy dog")
        font_preview.setFont(QFont("Arial", 12))
        font_preview.setStyleSheet(
            "border: 1px solid #ccc; padding: 10px; background: #f8f9fa; border-radius: 3px;"
        )

        # Description
        font_desc = QLabel("Select web-safe font family for website text")
        font_desc.setFont(QFont("Arial", 8))
        font_desc.setStyleSheet("color: #666; font-style: italic;")

        # Error label
        font_error = self._create_error_label("font_family")

        font_layout.addWidget(font_label, 0, 0)
        font_layout.addWidget(font_combo, 0, 1)
        font_layout.addWidget(font_desc, 1, 1)
        font_layout.addWidget(QLabel("Preview:"), 2, 0)
        font_layout.addWidget(font_preview, 2, 1)
        font_layout.addWidget(font_error, 3, 1)

        # Store references
        self.branding_inputs["font_family"] = font_combo
        self.preview_labels["font"] = font_preview

        # Connect font change to preview update
        font_combo.currentTextChanged.connect(
            lambda font: self._update_font_preview(font)
        )

        font_group.setLayout(font_layout)
        parent_layout.addWidget(font_group)

    def _create_logo_section(self, parent_layout: QVBoxLayout):
        """Create logo URL section"""
        # Section header
        header_label = self._create_section_header("Logo & Assets")
        parent_layout.addWidget(header_label)

        # Logo form
        logo_group = QGroupBox()
        logo_layout = QGridLayout()
        logo_layout.setSpacing(10)

        # Logo URL input
        logo_label = QLabel("Logo URL")
        logo_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        logo_input = QLineEdit()
        logo_input.setFont(QFont("Arial", 10))
        logo_input.setPlaceholderText("https://yoursite.com/logo.png")
        logo_input.textChanged.connect(self._emit_config_changed)

        # Browse button (for future file upload)
        browse_btn = QPushButton("Browse...")
        browse_btn.setMaximumWidth(80)
        browse_btn.clicked.connect(self._browse_logo_file)

        # URL container
        url_container = QHBoxLayout()
        url_container.addWidget(logo_input)
        url_container.addWidget(browse_btn)

        # Description
        logo_desc = QLabel("URL to your logo image (PNG, JPG, SVG recommended)")
        logo_desc.setFont(QFont("Arial", 8))
        logo_desc.setStyleSheet("color: #666; font-style: italic;")

        # Error label
        logo_error = self._create_error_label("logo_url")

        logo_layout.addWidget(logo_label, 0, 0)
        logo_layout.addLayout(url_container, 0, 1)
        logo_layout.addWidget(logo_desc, 1, 1)
        logo_layout.addWidget(logo_error, 2, 1)

        # Store reference
        self.branding_inputs["logo_url"] = logo_input

        logo_group.setLayout(logo_layout)
        parent_layout.addWidget(logo_group)

    def _create_preview_section(self, parent_layout: QVBoxLayout):
        """Create live preview section"""
        # Separator
        separator = self._create_separator()
        parent_layout.addWidget(separator)

        # Section header
        header_label = self._create_section_header("Live Preview")
        parent_layout.addWidget(header_label)

        # Preview container
        preview_group = QGroupBox()
        preview_layout = QVBoxLayout()

        # Color scheme preview
        scheme_preview = QLabel("Color Scheme Preview")
        scheme_preview.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        scheme_preview.setMinimumHeight(60)
        scheme_preview.setStyleSheet(
            f"""
            background: {self.current_colors['primary']};
            color: white;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        """
        )

        # Validation button
        validate_btn = QPushButton("🎨 Validate Branding")
        validate_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        validate_btn.clicked.connect(self.validate_and_show_results)

        preview_layout.addWidget(scheme_preview)
        preview_layout.addWidget(validate_btn)

        # Store reference
        self.preview_labels["scheme"] = scheme_preview

        preview_group.setLayout(preview_layout)
        parent_layout.addWidget(preview_group)

    def _create_section_header(self, text: str) -> QLabel:
        """Create a styled section header"""
        label = QLabel(text)
        label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; padding: 5px 0px;")
        return label

    def _create_separator(self) -> QFrame:
        """Create a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #bdc3c7;")
        return line

    def _create_error_label(self, field_name: str) -> QLabel:
        """Create an error label for a field"""
        error_label = QLabel()
        error_label.setFont(QFont("Arial", 8))
        error_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        error_label.setWordWrap(True)
        error_label.hide()
        self.error_labels[field_name] = error_label
        return error_label

    def _show_field_error(self, field_name: str, message: str):
        """Show error message for a specific field"""
        if field_name in self.error_labels:
            self.error_labels[field_name].setText(f"⚠ {message}")
            self.error_labels[field_name].show()

    def _hide_field_error(self, field_name: str):
        """Hide error message for a specific field"""
        if field_name in self.error_labels:
            self.error_labels[field_name].hide()

    def _open_color_picker(self, color_key: str):
        """Open color picker dialog"""
        current_color = QColor(self.current_colors[color_key])
        color = QColorDialog.getColor(
            current_color, self, f"Select {color_key.title()} Color"
        )

        if color.isValid():
            hex_color = color.name()
            self.current_colors[color_key] = hex_color
            self.branding_inputs[f"{color_key}_color"].setText(hex_color)
            self._update_color_display(color_key, hex_color)
            self._update_live_preview()
            self._emit_config_changed()

    def _on_hex_input_changed(self, color_key: str, text: str = None):
        """Handle hex input changes with live updates"""
        if text is None:
            # Fallback for cases where text is not provided
            hex_input = self.branding_inputs[f"{color_key}_color"]
            hex_value = hex_input.text().strip()
        else:
            hex_value = text.strip()
        
        # Clean the input - add # if missing and convert to uppercase
        if hex_value and not hex_value.startswith("#"):
            hex_value = "#" + hex_value
        
        # Always update the input field to show the cleaned value
        hex_input = self.branding_inputs[f"{color_key}_color"]
        if hex_input.text() != hex_value and hex_value != "#":
            hex_input.blockSignals(True)  # Prevent recursive calls
            hex_input.setText(hex_value)
            hex_input.blockSignals(False)

        if self._is_valid_hex_color(hex_value):
            self.current_colors[color_key] = hex_value
            self._update_color_display(color_key, hex_value)
            self._update_live_preview()
            self._hide_field_error(f"{color_key}_color")
        else:
            # Show error for invalid colors but don't reset immediately
            if hex_value and len(hex_value) > 1:  # Don't show error for partial input
                self._show_field_error(f"{color_key}_color", "Invalid hex color format")

        self._emit_config_changed()

    def _update_color_display(self, color_key: str, hex_color: str):
        """Update color button and preview display"""
        # Update color button
        color_button = self.color_buttons[color_key]
        color_button.setStyleSheet(
            f"""
            background-color: {hex_color};
            border: 2px solid #333;
            border-radius: 3px;
        """
        )

        # Update preview label
        preview_label = self.preview_labels[color_key]
        text_color = "#ffffff" if self._is_dark_color(hex_color) else "#000000"
        preview_label.setStyleSheet(
            f"""
            background-color: {hex_color};
            color: {text_color};
            border: 1px solid #ccc;
            padding: 5px;
            border-radius: 3px;
        """
        )

    def _on_font_changed(self, font_family: str):
        """Handle font family changes with live preview updates"""
        try:
            # Update the font preview
            self._update_font_preview(font_family)
            # Update the live preview section
            self._update_live_preview()
            # Emit config changed signal
            self._emit_config_changed()
        except Exception as e:
            print(f"DEBUG: Error in font change handler: {e}")

    def _update_font_preview(self, font_family: str):
        """Update font preview display"""
        font_preview = self.preview_labels["font"]
        base_font = font_family.split(",")[0].strip().strip('"').strip("'")
        font_preview.setStyleSheet(
            f"""
            font-family: {font_family};
            border: 1px solid #ccc;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 3px;
        """
        )

    def _update_live_preview(self):
        """Update the live color scheme preview with enhanced display"""
        try:
            if "scheme" in self.preview_labels:
                scheme_preview = self.preview_labels["scheme"]
                primary = self.current_colors["primary"]
                secondary = self.current_colors["secondary"]
                text_color = "#ffffff" if self._is_dark_color(primary) else "#000000"
                
                # Get current font family
                font_family = "Arial, sans-serif"
                if hasattr(self, 'branding_inputs') and 'font_family' in self.branding_inputs:
                    font_family = self.branding_inputs['font_family'].currentText()
                
                # Extract base font name for CSS
                base_font = font_family.split(",")[0].strip().strip('"').strip("'")

                scheme_preview.setStyleSheet(
                    f"""
                    QLabel {{
                        background: linear-gradient(45deg, {primary} 0%, {secondary} 100%);
                        color: {text_color};
                        padding: 15px;
                        border-radius: 8px;
                        text-align: center;
                        font-family: '{base_font}';
                        font-size: 14px;
                        font-weight: bold;
                        border: 2px solid {self._darken_color(primary, 0.2)};
                    }}
                """
                )
                
                # Update the text to show both colors
                scheme_preview.setText(
                    f"Website Preview\nPrimary: {primary}\nSecondary: {secondary}\nFont: {base_font}"
                )
        except Exception as e:
            print(f"DEBUG: Error updating live preview: {e}")
            # Fallback to simple display
            if "scheme" in self.preview_labels:
                scheme_preview = self.preview_labels["scheme"]
                scheme_preview.setStyleSheet("background: #f8f9fa; padding: 15px; border-radius: 5px;")
                scheme_preview.setText("Preview unavailable")

    def _is_valid_hex_color(self, hex_color: str) -> bool:
        """Validate hex color format"""
        pattern = r"^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
        return bool(re.match(pattern, hex_color))

    def _is_dark_color(self, hex_color: str) -> bool:
        """Determine if color is dark (for text contrast)"""
        try:
            hex_color = hex_color.lstrip("#")
            rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            # Calculate perceived brightness
            brightness = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000
            return brightness < 128
        except:
            return True  # Default to dark if can't determine

    def _darken_color(self, hex_color: str, factor: float = 0.2) -> str:
        """Darken a hex color by the given factor"""
        try:
            hex_color = hex_color.lstrip("#")
            rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
            # Darken each component
            darkened_rgb = tuple(int(c * (1 - factor)) for c in rgb)
            # Convert back to hex
            return f"#{darkened_rgb[0]:02x}{darkened_rgb[1]:02x}{darkened_rgb[2]:02x}"
        except:
            return hex_color  # Return original if conversion fails

    def _browse_logo_file(self):
        """Browse for logo file (placeholder for future implementation)"""
        QMessageBox.information(
            self,
            "Browse Logo",
            "File browsing will be implemented in future version.\nFor now, please enter the logo URL directly.",
        )

    def connect_signals(self):
        """Connect UI signals to emit config_changed"""
        # Color inputs already connected in _create_color_section
        # Font combo already connected in _create_font_section
        # Logo input already connected in _create_logo_section
        pass

    def get_required_fields(self) -> List[str]:
        """Get list of required field names"""
        return ["primary_color", "secondary_color", "font_family"]

    def validate_data(self) -> ValidationResult:
        """Validate branding data with detailed field-specific errors"""
        result = ValidationResult()

        # Clear existing errors
        for field_name in self.error_labels:
            self._hide_field_error(field_name)

        # Validate primary color
        primary_hex = self.branding_inputs["primary_color"].text().strip()
        if not primary_hex:
            error_msg = "Primary color is required"
            result.add_error(error_msg)
            self._show_field_error("primary_color", error_msg)
        elif not self._is_valid_hex_color(primary_hex):
            error_msg = "Invalid hex color format (use #FFFFFF)"
            result.add_error(error_msg)
            self._show_field_error("primary_color", error_msg)

        # Validate secondary color
        secondary_hex = self.branding_inputs["secondary_color"].text().strip()
        if not secondary_hex:
            error_msg = "Secondary color is required"
            result.add_error(error_msg)
            self._show_field_error("secondary_color", error_msg)
        elif not self._is_valid_hex_color(secondary_hex):
            error_msg = "Invalid hex color format (use #FFFFFF)"
            result.add_error(error_msg)
            self._show_field_error("secondary_color", error_msg)

        # Validate font family
        font_family = self.branding_inputs["font_family"].currentText()
        if not font_family:
            error_msg = "Font family is required"
            result.add_error(error_msg)
            self._show_field_error("font_family", error_msg)

        # Validate logo URL (optional but check format if provided)
        logo_url = self.branding_inputs["logo_url"].text().strip()
        if logo_url:
            url_pattern = r"^https?://.+"
            if not re.match(url_pattern, logo_url):
                error_msg = "Logo URL should start with http:// or https://"
                result.add_warning(error_msg)

        # Color contrast warning
        if (
            primary_hex
            and secondary_hex
            and self._is_valid_hex_color(primary_hex)
            and self._is_valid_hex_color(secondary_hex)
        ):
            if primary_hex.lower() == secondary_hex.lower():
                result.add_warning("Primary and secondary colors are identical")

        return result

    def validate_and_show_results(self):
        """Validate data and show results to user"""
        result = self.validate_data()

        if result.is_valid:
            print("✅ Branding validation passed!")
            if result.warnings:
                print("⚠️ Warnings:", result.warnings)
        else:
            print(f"❌ Validation failed: {len(result.errors)} errors")

    def get_config_data(self) -> Dict[str, Any]:
        """Get branding configuration data"""
        return {
            "branding": {
                "primary_color": self.branding_inputs["primary_color"].text().strip(),
                "secondary_color": self.branding_inputs["secondary_color"]
                .text()
                .strip(),
                "font_family": self.branding_inputs["font_family"].currentText(),
                "logo_url": self.branding_inputs["logo_url"].text().strip(),
            }
        }

    def set_config_data(self, data: Dict[str, Any]):
        """Set branding configuration data"""
        branding_data = data.get("branding", {})

        # Set colors
        primary_color = branding_data.get("primary_color", self.DEFAULT_PRIMARY)
        secondary_color = branding_data.get("secondary_color", self.DEFAULT_SECONDARY)

        self.branding_inputs["primary_color"].setText(primary_color)
        self.branding_inputs["secondary_color"].setText(secondary_color)

        # Update color displays
        self.current_colors["primary"] = primary_color
        self.current_colors["secondary"] = secondary_color
        self._update_color_display("primary", primary_color)
        self._update_color_display("secondary", secondary_color)

        # Set font
        font_family = branding_data.get("font_family", "Arial, sans-serif")
        font_combo = self.branding_inputs["font_family"]
        if font_family in self.WEB_FONTS:
            font_combo.setCurrentText(font_family)

        # Set logo URL
        self.branding_inputs["logo_url"].setText(branding_data.get("logo_url", ""))

        # Update previews
        self._update_font_preview(font_family)
        self._update_live_preview()

        # Clear any existing errors
        for field_name in self.error_labels:
            self._hide_field_error(field_name)

        # Emit data loaded signal
        self.data_loaded.emit()

    def clear_data(self):
        """Clear all branding data"""
        # Reset to defaults
        self.branding_inputs["primary_color"].setText(self.DEFAULT_PRIMARY)
        self.branding_inputs["secondary_color"].setText(self.DEFAULT_SECONDARY)
        self.branding_inputs["font_family"].setCurrentText("Arial, sans-serif")
        self.branding_inputs["logo_url"].clear()

        # Reset color tracking
        self.current_colors["primary"] = self.DEFAULT_PRIMARY
        self.current_colors["secondary"] = self.DEFAULT_SECONDARY

        # Update displays
        self._update_color_display("primary", self.DEFAULT_PRIMARY)
        self._update_color_display("secondary", self.DEFAULT_SECONDARY)
        self._update_font_preview("Arial, sans-serif")
        self._update_live_preview()

        # Clear errors
        for field_name in self.error_labels:
            self._hide_field_error(field_name)

        self.has_changes = False

    def _emit_config_changed(self):
        """Helper method to emit config changed signal"""
        self.has_changes = True
        self.config_changed.emit()

        # Update window title to show unsaved changes (*) - if method exists
        parent_window = self.window()
        if parent_window and hasattr(parent_window, "update_title_with_changes"):
            try:
                getattr(parent_window, "update_title_with_changes")()
            except Exception:
                pass  # Silently ignore if method call fails
