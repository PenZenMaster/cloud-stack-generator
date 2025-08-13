"""
Filename: contact_tab.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\components\\contact_tab.py
Description: Contact information configuration tab with auto-formatting and validation
Handles business contact details including phone, email, and address with smart input assistance

Version: 1.0.0
Date: 2025-08-11
Author: Cloud Stack Generator Team
"""

import re
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFrame,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtGui import QFont, QPalette
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


class ContactTab(BaseTab):
    """Tab for contact information configuration"""

    # Signals
    config_changed = pyqtSignal()
    validation_requested = pyqtSignal()
    data_loaded = pyqtSignal()

    def __init__(self, parent=None):
        self.contact_inputs = {}
        self.social_media_inputs = {}
        self.google_business_inputs = {}
        self.error_labels = {}
        self.has_changes = False
        super().__init__(parent)

    def setup_ui(self):
        """Setup contact information UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Create main sections
        self._create_contact_section(main_layout)
        self._create_address_section(main_layout)
        self._create_social_media_section(main_layout)
        self._create_google_business_section(main_layout)
        self._create_validation_section(main_layout)

        # Add stretch to push content to top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def _create_contact_section(self, parent_layout: QVBoxLayout):
        """Create contact details section"""
        # Section header
        header_label = self._create_section_header("Contact Information")
        parent_layout.addWidget(header_label)

        # Contact form
        contact_group = QGroupBox()
        contact_layout = QGridLayout()
        contact_layout.setSpacing(10)

        # Contact fields with validation
        fields = [
            ("* Contact Name", "name", "Enter primary contact name"),
            ("* Phone Number", "phone", "Enter phone number (will auto-format)"),
            ("* Email Address", "email", "Enter business email address"),
        ]

        row = 0
        for label_text, field_key, placeholder in fields:
            # Label
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

            # Input widget
            widget = QLineEdit()
            widget.setFont(QFont("Arial", 10))
            widget.setPlaceholderText(placeholder)
            widget.setMinimumHeight(30)

            # Special handling for phone formatting
            if field_key == "phone":
                widget.textChanged.connect(self._format_phone_number)

            # Error label
            error_label = self._create_error_label(field_key)

            # Layout
            contact_layout.addWidget(label, row, 0)
            contact_layout.addWidget(widget, row, 1)
            contact_layout.addWidget(error_label, row + 1, 1)

            self.contact_inputs[field_key] = widget
            row += 2

        contact_group.setLayout(contact_layout)
        parent_layout.addWidget(contact_group)

    def _create_address_section(self, parent_layout: QVBoxLayout):
        """Create address section"""
        # Section header
        header_label = self._create_section_header("Business Address")
        parent_layout.addWidget(header_label)

        # Address form
        address_group = QGroupBox()
        address_layout = QVBoxLayout()
        address_layout.setSpacing(10)

        # Address field
        address_label = QLabel("* Full Business Address")
        address_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        address_widget = QTextEdit()
        address_widget.setFont(QFont("Arial", 10))
        address_widget.setPlaceholderText(
            "Enter complete business address\n(Street, City, State, ZIP)"
        )
        address_widget.setMaximumHeight(80)

        # Error label for address
        address_error = self._create_error_label("address")

        address_layout.addWidget(address_label)
        address_layout.addWidget(address_widget)
        address_layout.addWidget(address_error)

        self.contact_inputs["address"] = address_widget

        # Google Maps placeholder
        maps_label = QLabel("Google Maps Integration")
        maps_label.setFont(QFont("Arial", 9))
        maps_label.setStyleSheet("color: #666; font-style: italic;")
        address_layout.addWidget(maps_label)

        address_group.setLayout(address_layout)
        parent_layout.addWidget(address_group)

    def _create_social_media_section(self, parent_layout: QVBoxLayout):
        """Create social media links section (optional)"""
        # Section header
        header_label = self._create_section_header("Social Media Links (Optional)")
        parent_layout.addWidget(header_label)

        # Social media form
        social_group = QGroupBox()
        social_layout = QGridLayout()
        social_layout.setSpacing(10)

        # Social media platforms (up to 5)
        platforms = [
            ("Facebook", "facebook", "https://facebook.com/yourbusiness"),
            ("Twitter/X", "twitter", "https://twitter.com/yourbusiness"),
            ("LinkedIn", "linkedin", "https://linkedin.com/company/yourbusiness"),
            ("Instagram", "instagram", "https://instagram.com/yourbusiness"),
            ("YouTube", "youtube", "https://youtube.com/@yourbusiness"),
        ]

        row = 0
        for label_text, field_key, placeholder in platforms:
            # Label
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 10))

            # Input widget
            widget = QLineEdit()
            widget.setFont(QFont("Arial", 10))
            widget.setPlaceholderText(placeholder)
            widget.setMinimumHeight(30)
            widget.textChanged.connect(self._emit_config_changed)

            # Layout
            social_layout.addWidget(label, row, 0)
            social_layout.addWidget(widget, row, 1)

            self.social_media_inputs[field_key] = widget
            row += 1

        # Help text
        help_label = QLabel("💡 Add your social media URLs to enhance your online presence. All fields are optional.")
        help_label.setFont(QFont("Arial", 9))
        help_label.setStyleSheet("color: #666; padding: 5px; font-style: italic;")
        help_label.setWordWrap(True)
        social_layout.addWidget(help_label, row, 0, 1, 2)

        social_group.setLayout(social_layout)
        parent_layout.addWidget(social_group)

    def _create_google_business_section(self, parent_layout: QVBoxLayout):
        """Create Google Business Profile section (optional)"""
        # Section header
        header_label = self._create_section_header("Google Business Profile (Optional)")
        parent_layout.addWidget(header_label)

        # Google Business form
        gbp_group = QGroupBox()
        gbp_layout = QVBoxLayout()
        gbp_layout.setSpacing(10)

        # Embed code field
        embed_label = QLabel("Google Business Profile Embed Code")
        embed_label.setFont(QFont("Arial", 10))

        embed_widget = QTextEdit()
        embed_widget.setFont(QFont("Arial", 9))
        embed_widget.setPlaceholderText(
            "Paste your Google Business Profile embed code here...\n"
            "Example: <iframe src=\"https://www.google.com/maps/embed?pb=...\" ...></iframe>"
        )
        embed_widget.setMaximumHeight(100)
        embed_widget.textChanged.connect(self._emit_config_changed)

        self.google_business_inputs["embed_code"] = embed_widget

        # Help text
        help_label = QLabel(
            "💡 Get your embed code from Google Maps by searching for your business, "
            "clicking 'Share' → 'Embed a map', then copying the iframe code. "
            "This will display your business location and reviews on your website."
        )
        help_label.setFont(QFont("Arial", 9))
        help_label.setStyleSheet("color: #666; padding: 5px; font-style: italic;")
        help_label.setWordWrap(True)

        gbp_layout.addWidget(embed_label)
        gbp_layout.addWidget(embed_widget)
        gbp_layout.addWidget(help_label)

        gbp_group.setLayout(gbp_layout)
        parent_layout.addWidget(gbp_group)

    def _create_validation_section(self, parent_layout: QVBoxLayout):
        """Create validation controls section"""
        # Separator
        separator = self._create_separator()
        parent_layout.addWidget(separator)

        # Validation controls
        validation_layout = QHBoxLayout()

        self.validate_btn = QPushButton("Validate Contact Info")
        self.validate_btn.setFont(QFont("Arial", 9))
        self.validate_btn.clicked.connect(self.validate_and_show_results)

        self.format_btn = QPushButton("Auto-Format Fields")
        self.format_btn.setFont(QFont("Arial", 9))
        self.format_btn.clicked.connect(self.auto_format_fields)

        validation_layout.addWidget(self.validate_btn)
        validation_layout.addWidget(self.format_btn)
        validation_layout.addStretch()

        parent_layout.addLayout(validation_layout)

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

    def _format_phone_number(self):
        """Auto-format phone number as user types"""
        phone_widget = self.contact_inputs["phone"]
        text = phone_widget.text()

        # Remove all non-digits
        digits_only = re.sub(r"\D", "", text)

        # Format based on length
        if len(digits_only) == 0:
            formatted = ""
        elif len(digits_only) <= 3:
            formatted = f"({digits_only}"
        elif len(digits_only) <= 6:
            formatted = f"({digits_only[:3]}) {digits_only[3:]}"
        elif len(digits_only) <= 10:
            formatted = f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
        else:
            # For numbers longer than 10 digits, add country code
            formatted = (
                f"+1-({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:11]}"
            )

        # Update widget without triggering signal recursion
        phone_widget.blockSignals(True)
        phone_widget.setText(formatted)
        phone_widget.blockSignals(False)

        self._emit_config_changed()

    def auto_format_fields(self):
        """Auto-format all contact fields"""
        # Format phone number (already done in real-time)
        self._format_phone_number()

        # Format email (lowercase, trim)
        email_widget = self.contact_inputs["email"]
        email_text = email_widget.text().strip().lower()
        email_widget.setText(email_text)

        # Format name (title case)
        name_widget = self.contact_inputs["name"]
        name_text = name_widget.text().strip().title()
        name_widget.setText(name_text)

        # Format address (basic cleanup)
        address_widget = self.contact_inputs["address"]
        address_text = address_widget.toPlainText().strip()
        address_widget.setPlainText(address_text)

        self._emit_config_changed()

    def connect_signals(self):
        """Connect UI signals to emit config_changed"""
        # Connect text change signals
        for field_name, widget in self.contact_inputs.items():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self._emit_config_changed)
            elif isinstance(widget, QTextEdit):
                widget.textChanged.connect(self._emit_config_changed)

    def get_required_fields(self) -> List[str]:
        """Get list of required field names"""
        return ["name", "phone", "email", "address"]

    def validate_data(self) -> ValidationResult:
        """Validate contact data with detailed field-specific errors"""
        result = ValidationResult()

        # Clear existing errors
        for field_name in self.error_labels:
            self._hide_field_error(field_name)

        # Required fields validation
        required_fields = {
            "name": "Contact name is required",
            "phone": "Phone number is required",
            "email": "Email address is required",
            "address": "Business address is required",
        }

        for field_name, error_message in required_fields.items():
            widget = self.contact_inputs[field_name]

            if isinstance(widget, QLineEdit):
                value = widget.text().strip()
            else:  # QTextEdit
                value = widget.toPlainText().strip()

            if not value:
                result.add_error(error_message)
                self._show_field_error(field_name, error_message)

        # Email format validation
        email_text = self.contact_inputs["email"].text().strip()
        if email_text:
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email_text):
                error_msg = "Invalid email format"
                result.add_error(error_msg)
                self._show_field_error("email", error_msg)

        # Phone number validation
        phone_text = self.contact_inputs["phone"].text().strip()
        if phone_text:
            digits_only = re.sub(r"\D", "", phone_text)
            if len(digits_only) < 10:
                error_msg = "Phone number must be at least 10 digits"
                result.add_error(error_msg)
                self._show_field_error("phone", error_msg)

        # Address validation (basic length check)
        address_text = self.contact_inputs["address"].toPlainText().strip()
        if address_text and len(address_text) < 10:
            error_msg = "Address seems too short"
            result.add_warning(error_msg)

        return result

    def validate_and_show_results(self):
        """Validate data and show results to user"""
        result = self.validate_data()

        if result.is_valid:
            # Show success (could use a status bar or temporary message)
            print("✅ Contact information validation passed!")
        else:
            # Errors are already shown in field-specific error labels
            print(f"❌ Validation failed: {len(result.errors)} errors")

    def get_config_data(self) -> Dict[str, Any]:
        """Get contact configuration data"""
        # Basic contact data
        contact_data = {
            "name": self.contact_inputs["name"].text().strip(),
            "phone": self.contact_inputs["phone"].text().strip(),
            "email": self.contact_inputs["email"].text().strip(),
            "address": self.contact_inputs["address"].toPlainText().strip(),
        }
        
        # Social media data
        social_media_data = {}
        for platform, widget in self.social_media_inputs.items():
            url = widget.text().strip()
            if url:  # Only include non-empty URLs
                social_media_data[platform] = url
        
        # Google Business Profile data
        google_business_data = {}
        embed_code = self.google_business_inputs["embed_code"].toPlainText().strip()
        if embed_code:  # Only include if embed code is provided
            google_business_data["embed_code"] = embed_code
        
        # Combine all data
        all_data = contact_data.copy()
        all_data["social_media"] = social_media_data
        all_data["google_business_profile"] = google_business_data
        
        return all_data

    def set_config_data(self, data: Dict[str, Any]):
        """Set contact configuration data"""
        # Set basic contact data
        self.contact_inputs["name"].setText(data.get("name", ""))
        self.contact_inputs["phone"].setText(data.get("phone", ""))
        self.contact_inputs["email"].setText(data.get("email", ""))
        self.contact_inputs["address"].setPlainText(data.get("address", ""))
        
        # Set social media data
        social_media_data = data.get("social_media", {})
        for platform, widget in self.social_media_inputs.items():
            widget.setText(social_media_data.get(platform, ""))
        
        # Set Google Business Profile data
        google_business_data = data.get("google_business_profile", {})
        embed_code = google_business_data.get("embed_code", "")
        self.google_business_inputs["embed_code"].setPlainText(embed_code)

        # Clear any existing errors
        for field_name in self.error_labels:
            self._hide_field_error(field_name)

        # Emit data loaded signal
        self.data_loaded.emit()

    def clear_data(self):
        """Clear all contact data"""
        # Clear basic contact data
        for field_name, widget in self.contact_inputs.items():
            if isinstance(widget, QLineEdit):
                widget.clear()
            else:  # QTextEdit
                widget.clear()
        
        # Clear social media data
        for platform, widget in self.social_media_inputs.items():
            widget.clear()
        
        # Clear Google Business Profile data
        for field_name, widget in self.google_business_inputs.items():
            widget.clear()

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
