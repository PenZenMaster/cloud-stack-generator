"""
Filename: contact_tab_fixed.py
Path: E:/projects/cloud-stack-generator/src/ui/components/contact_tab_fixed.py
Description: Contact information configuration tab with fixed layout issues
Simple, working layout that displays correctly in all screen modes

Version: 2.1.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

import re
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFrame,
    QGroupBox,
    QScrollArea,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from .base_tab import BaseTab, ValidationResult
from typing import Dict, Any


class ContactTab(BaseTab):
    """Contact information configuration tab with fixed layout"""

    # Signals
    config_changed = pyqtSignal()
    validation_requested = pyqtSignal()
    data_loaded = pyqtSignal()

    def __init__(self, parent=None):
        self.contact_inputs = {}
        self.enhanced_contact_inputs = {}
        self.business_hours_inputs = {}
        self.social_media_inputs = {}
        self.google_business_inputs = {}
        self.error_labels = {}
        self.has_changes = False
        super().__init__(parent)

    def setup_ui(self):
        """Setup contact information UI with working layout"""
        # Create main scroll area for the entire content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_widget = QVBoxLayout()
        content_widget.setSpacing(20)
        content_widget.setContentsMargins(10, 10, 10, 10)
        
        # Create sections
        self._create_contact_section(content_widget)
        self._create_address_section(content_widget)  
        self._create_enhanced_contact_section(content_widget)
        self._create_business_hours_section(content_widget)
        self._create_social_media_section(content_widget)
        self._create_google_business_section(content_widget)
        
        # Add validation button
        validation_button = QPushButton("Validate Contact Information")
        validation_button.clicked.connect(self.validate_data)
        validation_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        validation_button.setMaximumWidth(300)
        content_widget.addWidget(validation_button)

        # Add stretch to push content to top
        content_widget.addStretch()

        # Create container widget and set layout
        container = QFrame()
        container.setLayout(content_widget)
        
        # Set up scroll area
        scroll_area.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)

    def _create_contact_section(self, parent_layout: QVBoxLayout):
        """Create contact details section"""
        # Section header
        header = QLabel("Contact Information")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Contact form in a group box
        contact_group = QGroupBox()
        contact_group.setMaximumHeight(150)
        contact_layout = QGridLayout()
        contact_layout.setSpacing(10)
        
        # Contact fields
        fields = [
            ("* Contact Name", "name", "Enter primary contact name"),
            ("* Phone Number", "phone", "Enter phone number (will auto-format)"),
            ("* Email Address", "email", "Enter business email address"),
        ]

        for row, (label_text, field_key, placeholder) in enumerate(fields):
            # Label
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 10))
            contact_layout.addWidget(label, row, 0)

            # Input
            input_field = QLineEdit()
            input_field.setFont(QFont("Arial", 10))
            input_field.setPlaceholderText(placeholder)
            input_field.setMinimumHeight(30)
            input_field.textChanged.connect(self._emit_config_changed)
            contact_layout.addWidget(input_field, row, 1)

            # Error label
            error_label = self._create_error_label(field_key)
            contact_layout.addWidget(error_label, row, 2)

            self.contact_inputs[field_key] = input_field

        contact_group.setLayout(contact_layout)
        parent_layout.addWidget(contact_group)

    def _create_address_section(self, parent_layout: QVBoxLayout):
        """Create address section"""
        # Section header
        header = QLabel("Business Address")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Address form in a group box
        address_group = QGroupBox()
        address_group.setMaximumHeight(260)
        address_layout = QGridLayout()
        address_layout.setSpacing(10)

        # Address fields
        fields = [
            ("* Street Address", "street", "Enter street address"),
            ("* City", "city", "Enter city"),
            ("* State/Province", "state", "Enter state or province"),
            ("* ZIP/Postal Code", "zip_code", "Enter ZIP or postal code"),
            ("Country", "country", "Enter country (default: United States)"),
            ("Latitude (optional)", "latitude", "41.760615"),
            ("Longitude (optional)", "longitude", "-88.344462"),
        ]

        for row, (label_text, field_key, placeholder) in enumerate(fields):
            # Label
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 10))
            address_layout.addWidget(label, row, 0)

            # Input
            input_field = QLineEdit()
            input_field.setFont(QFont("Arial", 10))
            input_field.setPlaceholderText(placeholder)
            input_field.setMinimumHeight(30)
            input_field.textChanged.connect(self._emit_config_changed)
            address_layout.addWidget(input_field, row, 1)

            self.contact_inputs[field_key] = input_field

        address_group.setLayout(address_layout)
        parent_layout.addWidget(address_group)

    def _create_social_media_section(self, parent_layout: QVBoxLayout):
        """Create social media links section"""
        # Section header
        header = QLabel("Social Media Links (Optional)")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Social media form in a group box
        social_group = QGroupBox()
        social_group.setMaximumHeight(200)
        social_layout = QGridLayout()
        social_layout.setSpacing(10)

        # Social media platforms
        platforms = [
            ("Facebook", "facebook", "https://facebook.com/yourbusiness"),
            ("Twitter/X", "twitter", "https://twitter.com/yourbusiness"),
            ("LinkedIn", "linkedin", "https://linkedin.com/company/yourbusiness"),
            ("Instagram", "instagram", "https://instagram.com/yourbusiness"),
            ("YouTube", "youtube", "https://youtube.com/@yourbusiness"),
        ]

        for row, (label_text, field_key, placeholder) in enumerate(platforms):
            # Label
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 10))
            social_layout.addWidget(label, row, 0)

            # Input
            input_field = QLineEdit()
            input_field.setFont(QFont("Arial", 10))
            input_field.setPlaceholderText(placeholder)
            input_field.setMinimumHeight(30)
            input_field.textChanged.connect(self._emit_config_changed)
            social_layout.addWidget(input_field, row, 1)

            self.social_media_inputs[field_key] = input_field

        social_group.setLayout(social_layout)
        parent_layout.addWidget(social_group)

    def _create_google_business_section(self, parent_layout: QVBoxLayout):
        """Create Google Business Profile section"""
        # Section header
        header = QLabel("Google Business Profile (Optional)")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Google Business form in a group box
        gbp_group = QGroupBox()
        gbp_group.setMaximumHeight(150)
        gbp_layout = QVBoxLayout()
        gbp_layout.setSpacing(10)

        # Embed code field
        embed_label = QLabel("Google Business Profile Embed Code")
        embed_label.setFont(QFont("Arial", 10))
        gbp_layout.addWidget(embed_label)

        embed_widget = QTextEdit()
        embed_widget.setFont(QFont("Arial", 9))
        embed_widget.setPlaceholderText(
            "Paste your Google Business Profile embed code here...\n"
            "Example: <iframe src=\"https://www.google.com/maps/embed?pb=...\" ...></iframe>"
        )
        embed_widget.setMaximumHeight(80)
        embed_widget.setMinimumHeight(80)
        embed_widget.textChanged.connect(self._emit_config_changed)
        gbp_layout.addWidget(embed_widget)

        self.google_business_inputs["embed_code"] = embed_widget

        gbp_group.setLayout(gbp_layout)
        parent_layout.addWidget(gbp_group)

    def _create_enhanced_contact_section(self, parent_layout: QVBoxLayout):
        """Create enhanced contact information section"""
        # Section header
        header = QLabel("Additional Contact Methods (Optional)")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Enhanced contact form in a group box
        enhanced_group = QGroupBox()
        enhanced_group.setMaximumHeight(200)
        enhanced_layout = QGridLayout()
        enhanced_layout.setSpacing(10)
        
        # Enhanced contact fields
        fields = [
            ("Office Phone", "office_phone", "Main office line"),
            ("Mobile Phone", "mobile_phone", "Mobile contact number"),
            ("Emergency Phone", "emergency_phone", "After-hours contact"),
            ("Fax Number", "fax_number", "Fax number if applicable"),
            ("Response Time Promise", "response_time_promise", "We respond within 24 hours"),
            ("Contact Preference", "contact_preference", "Phone, Email, or Online Form"),
        ]

        for row, (label_text, field_key, placeholder) in enumerate(fields):
            # Label
            label = QLabel(label_text)
            label.setFont(QFont("Arial", 10))
            enhanced_layout.addWidget(label, row, 0)

            # Input
            input_field = QLineEdit()
            input_field.setFont(QFont("Arial", 10))
            input_field.setPlaceholderText(placeholder)
            input_field.setMinimumHeight(30)
            input_field.textChanged.connect(self._emit_config_changed)
            enhanced_layout.addWidget(input_field, row, 1)

            self.enhanced_contact_inputs[field_key] = input_field

        enhanced_group.setLayout(enhanced_layout)
        parent_layout.addWidget(enhanced_group)

    def _create_business_hours_section(self, parent_layout: QVBoxLayout):
        """Create business hours section"""
        # Section header
        header = QLabel("Business Hours (Optional)")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Business hours form in a group box
        hours_group = QGroupBox()
        hours_group.setMaximumHeight(250)
        hours_layout = QGridLayout()
        hours_layout.setSpacing(10)
        
        # Days of the week
        days = [
            ("Monday", "monday"),
            ("Tuesday", "tuesday"),
            ("Wednesday", "wednesday"),
            ("Thursday", "thursday"),
            ("Friday", "friday"),
            ("Saturday", "saturday"),
            ("Sunday", "sunday"),
        ]

        for row, (day_label, day_key) in enumerate(days):
            # Day label
            label = QLabel(day_label)
            label.setFont(QFont("Arial", 10))
            hours_layout.addWidget(label, row, 0)

            # Hours input
            input_field = QLineEdit()
            input_field.setFont(QFont("Arial", 10))
            if day_key in ["saturday"]:
                input_field.setPlaceholderText("9:00 AM - 4:00 PM")
            elif day_key in ["sunday"]:
                input_field.setPlaceholderText("Closed")
            else:
                input_field.setPlaceholderText("8:00 AM - 6:00 PM")
            input_field.setMinimumHeight(30)
            input_field.textChanged.connect(self._emit_config_changed)
            hours_layout.addWidget(input_field, row, 1)

            self.business_hours_inputs[day_key] = input_field

        hours_group.setLayout(hours_layout)
        parent_layout.addWidget(hours_group)

    def _create_error_label(self, field_name: str) -> QLabel:
        """Create error label for field validation"""
        error_label = QLabel()
        error_label.setStyleSheet("color: red; font-size: 10px;")
        error_label.setWordWrap(True)
        error_label.hide()
        self.error_labels[field_name] = error_label
        return error_label

    def get_config_data(self) -> Dict[str, Any]:
        """Get configuration data from all forms"""
        # Separate contact info from address info
        contact_fields = ["name", "phone", "email"]
        address_fields = ["street", "city", "state", "zip_code", "country"]
        geo_fields = ["latitude", "longitude"]
        
        contact_data = {key: self.contact_inputs[key].text() for key in contact_fields if key in self.contact_inputs}
        address_data = {key: self.contact_inputs[key].text() for key in address_fields if key in self.contact_inputs}
        geo_data = {key: self.contact_inputs[key].text() for key in geo_fields if key in self.contact_inputs}
        social_data = {key: widget.text() for key, widget in self.social_media_inputs.items()}
        google_data = {}
        
        # Handle QTextEdit for Google Business embed
        if "embed_code" in self.google_business_inputs:
            google_data["embed_code"] = self.google_business_inputs["embed_code"].toPlainText()
            
        # Get enhanced contact data
        enhanced_contact_data = {key: widget.text() for key, widget in self.enhanced_contact_inputs.items()}
        
        # Get business hours data
        business_hours_data = {key: widget.text() for key, widget in self.business_hours_inputs.items()}
        
        # Merge enhanced data into contact
        contact_data.update(enhanced_contact_data)
        contact_data["business_hours"] = business_hours_data
        
        return {
            "contact": contact_data,
            "address": address_data,
            "geo_coordinates": geo_data,
            "social_media": social_data,
            "google_business_profile": google_data
        }

    def set_config_data(self, data: Dict[str, Any]):
        """Set configuration data to all forms"""
        self._start_loading()
        
        try:
            # Set contact data
            if "contact" in data:
                for field_name, value in data["contact"].items():
                    if field_name in self.contact_inputs:
                        self.contact_inputs[field_name].setText(str(value))
                    elif field_name in self.enhanced_contact_inputs:
                        self.enhanced_contact_inputs[field_name].setText(str(value))
                    elif field_name == "business_hours" and isinstance(value, dict):
                        # Set business hours
                        for day, hours in value.items():
                            if day in self.business_hours_inputs:
                                self.business_hours_inputs[day].setText(str(hours))
            
            # Set address data  
            if "address" in data:
                for field_name, value in data["address"].items():
                    if field_name in self.contact_inputs:
                        self.contact_inputs[field_name].setText(str(value))
            
            # Set geo coordinates data
            if "geo_coordinates" in data:
                for field_name, value in data["geo_coordinates"].items():
                    if field_name in self.contact_inputs:
                        self.contact_inputs[field_name].setText(str(value))
            
            # Set social media data
            if "social_media" in data:
                for field_name, value in data["social_media"].items():
                    if field_name in self.social_media_inputs:
                        self.social_media_inputs[field_name].setText(str(value))
            
            # Set Google Business data
            if "google_business_profile" in data:
                embed_code = data["google_business_profile"].get("embed_code", "")
                if "embed_code" in self.google_business_inputs:
                    self.google_business_inputs["embed_code"].setPlainText(str(embed_code))
        
        finally:
            self._finish_loading()

    def validate_data(self) -> ValidationResult:
        """Validate contact information"""
        result = ValidationResult()
        
        # Get all field values
        config_data = self.get_config_data()
        contact = config_data.get("contact", {})
        address = config_data.get("address", {})
        
        # Validate required contact fields
        if not contact.get("name", "").strip():
            result.add_error("Contact name is required", "name")
        
        if not contact.get("phone", "").strip():
            result.add_error("Phone number is required", "phone") 
        else:
            # Validate phone format
            phone = contact.get("phone", "")
            # Accept both normalized format (+1-XXX-XXX-XXXX) and common formats
            valid_patterns = [
                r'^\+1-\d{3}-\d{3}-\d{4}$',  # Normalized format: +1-866-713-3396
                r'^\(\d{3}\)\s\d{3}-\d{4}$',  # Common format: (866) 713-3396
                r'^\d{3}-\d{3}-\d{4}$',       # Simple format: 866-713-3396
                r'^\d{3}\.\d{3}\.\d{4}$',     # Dot format: 866.713.3396
                r'^\d{10}$',                  # Raw digits: 8667133396
            ]
            
            is_valid = any(re.match(pattern, phone) for pattern in valid_patterns)
            if not is_valid:
                result.add_error("Phone number format is invalid", "phone")
        
        if not contact.get("email", "").strip():
            result.add_error("Email address is required", "email")
        else:
            # Validate email format
            email = contact.get("email", "")
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                result.add_error("Email address format is invalid", "email")
        
        # Validate required address fields
        required_address_fields = ["street", "city", "state", "zip_code"]
        for field in required_address_fields:
            if not address.get(field, "").strip():
                result.add_error(f"{field.replace('_', ' ').title()} is required", field)
        
        return result
    
    def get_tab_name(self) -> str:
        """Get tab name for title display"""
        return "Contact Details"

    def connect_signals(self):
        """Connect UI signals"""
        pass