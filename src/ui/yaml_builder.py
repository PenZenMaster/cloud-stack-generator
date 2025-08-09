"""
Filename: src/ui/yaml_builder.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\yaml_builder.py
Description: Enhanced YAML Builder Widget with GBP integration and city selection

Version: 2.1.0
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QGridLayout,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QScrollArea,
    QTabWidget,
    QComboBox,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
import yaml
import tempfile
import webbrowser

# Import our modules - fixed import paths
from core.config_parser import ConfigParser, ConfigValidationError
from ui.dialogs.city_embed_dialog import CityEmbedDialog


class YAMLBuilderWidget(QWidget):
    """
    Enhanced YAML builder with GBP integration and city selection
    Compatible with ConfigParser and WebsiteGenerator
    """

    config_changed = pyqtSignal()  # Signal when config is modified

    def __init__(self):
        super().__init__()
        self.font_size = 10
        self.city_data = {}
        self.config_parser = ConfigParser()

        # Input widgets organized by section
        self.business_inputs = {}
        self.contact_inputs = {}
        self.social_inputs = {}
        self.branding_inputs = {}
        self.page_inputs = {}
        self.service_inputs = {}
        self.gbp_inputs = {}

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()

        # Create scroll area for the form
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        # Add form sections
        scroll_layout.addWidget(self.create_business_section())
        scroll_layout.addWidget(self.create_contact_section())
        scroll_layout.addWidget(self.create_gbp_section())  # New GBP section
        scroll_layout.addWidget(self.create_social_section())
        scroll_layout.addWidget(self.create_branding_section())
        scroll_layout.addWidget(self.create_pages_section())
        scroll_layout.addWidget(self.create_services_section())
        scroll_layout.addWidget(self.create_cities_section())

        scroll_widget.setLayout(scroll_layout)
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)

        # Add action buttons
        layout.addWidget(self.create_action_buttons())

        self.setLayout(layout)

    def create_business_section(self) -> QGroupBox:
        """Create business information section"""
        group = QGroupBox("Business Information")
        layout = QGridLayout()

        # Business fields mapping to new structure
        fields = {
            "* Business Name": "business_name",
            "* Website": "domain",
            "* Business Category": "industry",
        }

        row = 0
        for label_text, field_key in fields.items():
            label = QLabel(label_text)
            label.setFont(QFont("Arial", self.font_size))

            widget = QLineEdit()
            widget.setFont(QFont("Arial", self.font_size))

            layout.addWidget(label, row, 0)
            layout.addWidget(widget, row, 1)

            self.business_inputs[field_key] = widget
            row += 1

        group.setLayout(layout)
        return group

    def create_contact_section(self) -> QGroupBox:
        """Create contact information section (NAP)"""
        group = QGroupBox("Contact Information (NAP)")
        layout = QGridLayout()

        # Contact fields
        fields = {
            "Contact Name": "name",
            "* Phone": "phone",
            "Street Address": "street_address",
            "City": "city",
            "State": "state",
            "ZIP": "zip",
            "Country": "country",
            "Email": "email",
        }

        row = 0
        for label_text, field_key in fields.items():
            label = QLabel(label_text)
            label.setFont(QFont("Arial", self.font_size))

            widget = QLineEdit()
            widget.setFont(QFont("Arial", self.font_size))

            if "Phone" in label_text:
                widget.setInputMask("(000) 000-0000;_")

            layout.addWidget(label, row, 0)
            layout.addWidget(widget, row, 1)

            self.contact_inputs[field_key] = widget
            row += 1

        group.setLayout(layout)
        return group

    def create_gbp_section(self) -> QGroupBox:
        """Create Google Business Profile section"""
        group = QGroupBox("Google Business Profile (GBP)")
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Add your Google Business Profile map embed for the main location. "
            "This will appear in the footer of your homepage as a 480x480 map."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(
            "color: #666; font-style: italic; margin-bottom: 10px;"
        )
        layout.addWidget(instructions)

        # GBP embed code
        layout.addWidget(QLabel("Google Business Profile Map Embed:"))
        self.gbp_inputs["embed_code"] = QTextEdit()
        self.gbp_inputs["embed_code"].setFixedHeight(100)
        self.gbp_inputs["embed_code"].setPlaceholderText(
            "Paste your Google Business Profile <iframe> embed code here..."
        )
        layout.addWidget(self.gbp_inputs["embed_code"])

        # Validate GBP button
        validate_gbp_btn = QPushButton("Validate GBP Embed")
        validate_gbp_btn.clicked.connect(self.validate_gbp_embed)
        layout.addWidget(validate_gbp_btn)

        group.setLayout(layout)
        return group

    def create_social_section(self) -> QGroupBox:
        """Create social media section"""
        group = QGroupBox("Social Media")
        layout = QGridLayout()

        # Social media platforms
        platforms = ["facebook", "twitter", "linkedin", "instagram"]

        for i, platform in enumerate(platforms):
            label = QLabel(f"{platform.title()} URL:")
            label.setFont(QFont("Arial", self.font_size))

            widget = QLineEdit()
            widget.setFont(QFont("Arial", self.font_size))
            widget.setPlaceholderText(f"https://{platform}.com/yourpage")

            layout.addWidget(label, i, 0)
            layout.addWidget(widget, i, 1)

            self.social_inputs[platform] = widget

        group.setLayout(layout)
        return group

    def create_branding_section(self) -> QGroupBox:
        """Create branding customization section"""
        group = QGroupBox("Branding & Appearance")
        layout = QGridLayout()

        # Branding fields
        fields = {
            "Primary Color": "primary_color",
            "Secondary Color": "secondary_color",
            "Logo URL": "logo_url",
            "Font Family": "font_family",
        }

        row = 0
        for label_text, field_key in fields.items():
            label = QLabel(label_text)
            label.setFont(QFont("Arial", self.font_size))

            widget = QLineEdit()
            widget.setFont(QFont("Arial", self.font_size))

            if "Color" in label_text:
                widget.setPlaceholderText("#FF5722")
            elif "Font" in label_text:
                widget.setPlaceholderText("Arial, sans-serif")

            layout.addWidget(label, row, 0)
            layout.addWidget(widget, row, 1)

            self.branding_inputs[field_key] = widget
            row += 1

        group.setLayout(layout)
        return group

    def create_pages_section(self) -> QGroupBox:
        """Create pages configuration section"""
        group = QGroupBox("Website Pages")
        layout = QVBoxLayout()

        # Hero image URL
        hero_layout = QHBoxLayout()
        hero_layout.addWidget(QLabel("Hero Image URL:"))
        self.page_inputs["hero_image"] = QLineEdit()
        self.page_inputs["hero_image"].setPlaceholderText(
            "https://example.com/hero.jpg"
        )
        hero_layout.addWidget(self.page_inputs["hero_image"])
        layout.addLayout(hero_layout)

        # Target cities (creates individual pages)
        layout.addWidget(QLabel("* Target Cities (one per line):"))
        self.page_inputs["target_cities"] = QTextEdit()
        self.page_inputs["target_cities"].setFixedHeight(100)
        self.page_inputs["target_cities"].setPlaceholderText(
            "Detroit\nGrand Rapids\nAnn Arbor"
        )
        self.page_inputs["target_cities"].textChanged.connect(self.update_city_selector)
        layout.addWidget(self.page_inputs["target_cities"])

        group.setLayout(layout)
        return group

    def create_services_section(self) -> QGroupBox:
        """Create services/offerings section"""
        group = QGroupBox("Services & Offerings")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("* Services (one per line):"))
        self.service_inputs["services"] = QTextEdit()
        self.service_inputs["services"].setFixedHeight(100)
        self.service_inputs["services"].setPlaceholderText(
            "Business Consulting\nStrategic Planning\nManagement Advice"
        )
        layout.addWidget(self.service_inputs["services"])

        layout.addWidget(QLabel("FAQ Questions (one per line):"))
        self.service_inputs["faq"] = QTextEdit()
        self.service_inputs["faq"].setFixedHeight(80)
        self.service_inputs["faq"].setPlaceholderText(
            "What services do you offer?\nHow long have you been in business?\nWhat areas do you serve?"
        )
        layout.addWidget(self.service_inputs["faq"])

        group.setLayout(layout)
        return group

    def create_cities_section(self) -> QGroupBox:
        """Create cities with Google Maps embeds section"""
        group = QGroupBox("Cities with Google Maps")
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Select cities from your Target Cities list to add Google Maps embeds. "
            "Maps will appear in the footer of each city page."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet(
            "color: #666; font-style: italic; margin-bottom: 10px;"
        )
        layout.addWidget(instructions)

        # City selector dropdown
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Select City:"))
        self.city_selector = QComboBox()
        self.city_selector.addItem("Select a city...")
        selector_layout.addWidget(self.city_selector)

        self.add_city_map_btn = QPushButton("Add Google Map")
        self.add_city_map_btn.clicked.connect(self.add_city_map)
        self.add_city_map_btn.setEnabled(False)
        selector_layout.addWidget(self.add_city_map_btn)

        layout.addLayout(selector_layout)

        # City list display
        layout.addWidget(QLabel("Cities with Maps:"))
        self.city_list = QListWidget()
        self.city_list.setFont(QFont("Arial", self.font_size))
        self.city_list.setFixedHeight(150)
        layout.addWidget(self.city_list)

        # Connect city selector change
        self.city_selector.currentTextChanged.connect(self.on_city_selector_changed)

        group.setLayout(layout)
        return group

    def create_action_buttons(self) -> QWidget:
        """Create action buttons for load/save/validate"""
        widget = QWidget()
        layout = QHBoxLayout()

        # Load button
        load_btn = QPushButton("Load YAML")
        load_btn.clicked.connect(self.load_yaml)
        layout.addWidget(load_btn)

        # Validate button
        validate_btn = QPushButton("Validate Config")
        validate_btn.clicked.connect(self.validate_config)
        layout.addWidget(validate_btn)

        # Save button
        save_btn = QPushButton("Save YAML")
        save_btn.clicked.connect(self.save_yaml)
        layout.addWidget(save_btn)

        # Preview button
        preview_btn = QPushButton("Preview Website")
        preview_btn.clicked.connect(self.preview_website)
        layout.addWidget(preview_btn)

        widget.setLayout(layout)
        return widget

    def update_city_selector(self):
        """Update the city selector dropdown when target cities change"""
        cities_text = self.page_inputs.get("target_cities", QTextEdit()).toPlainText()
        cities = [city.strip() for city in cities_text.split("\n") if city.strip()]

        # Clear and repopulate selector
        self.city_selector.clear()
        self.city_selector.addItem("Select a city...")

        for city in cities:
            if city not in [key.split(",")[0] for key in self.city_data.keys()]:
                self.city_selector.addItem(city)

    def on_city_selector_changed(self, city_name):
        """Handle city selector change"""
        self.add_city_map_btn.setEnabled(
            city_name != "Select a city..." and city_name != ""
        )

    def add_city_map(self):
        """Add Google Map for selected city"""
        selected_city = self.city_selector.currentText()
        if selected_city and selected_city != "Select a city...":
            dialog = CityEmbedDialog(self)
            dialog.city_input.setText(selected_city)

            if dialog.exec():
                city_data = dialog.get_data()
                key = f"{city_data['city']}, {city_data['state']}"
                self.city_data[key] = {"embed_code": city_data["embed_code"]}
                self.refresh_city_list()
                self.update_city_selector()  # Refresh selector
                self.config_changed.emit()

    def validate_gbp_embed(self):
        """Validate Google Business Profile embed code"""
        embed_code = self.gbp_inputs["embed_code"].toPlainText().strip()

        if not embed_code:
            QMessageBox.warning(
                self, "No Embed Code", "Please paste your GBP embed code."
            )
            return

        if not embed_code.startswith("<iframe") or not embed_code.endswith("</iframe>"):
            QMessageBox.warning(
                self, "Invalid Format", "Please paste the complete <iframe> embed code."
            )
            return

        if "maps.google.com" not in embed_code:
            QMessageBox.warning(
                self, "Invalid Source", "The embed code must be from Google Maps."
            )
            return

        QMessageBox.information(
            self, "Valid Embed", "✅ Valid Google Business Profile embed code!"
        )

    def refresh_city_list(self):
        """Refresh the city list display"""
        self.city_list.clear()
        for city, data in self.city_data.items():
            has_embed = bool(data.get("embed_code"))
            status = "✅" if has_embed else "⚠️"
            self.city_list.addItem(QListWidgetItem(f"{status} {city}"))

    def validate_config(self):
        """Validate the current configuration using ConfigParser"""
        try:
            config_dict = self.build_config_dict()
            self.config_parser.parse(config_dict)
            QMessageBox.information(self, "Validation", "✅ Configuration is valid!")
        except ConfigValidationError as e:
            QMessageBox.warning(
                self, "Validation Error", f"❌ Configuration error:\n{str(e)}"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Unexpected error:\n{str(e)}")

    def build_config_dict(self) -> dict:
        """Build the nested configuration dictionary from UI inputs"""
        config = {
            "client": {
                # Business info
                "business_name": self.business_inputs["business_name"].text(),
                "domain": self.business_inputs["domain"].text(),
                "industry": self.business_inputs["industry"].text(),
                # Contact info
                "contact": {
                    "name": self.contact_inputs["name"].text()
                    or self.business_inputs["business_name"].text(),
                    "address": self.build_address(),
                    "phone": self.normalize_phone(self.contact_inputs["phone"].text()),
                },
                # Social media
                "social_media": self.build_social_media(),
                # Branding
                "branding": self.build_branding(),
                # Google Business Profile
                "google_business_profile": self.build_gbp(),
                # Google Maps for cities
                "google_maps": self.build_google_maps(),
                # Pages
                "pages": self.build_pages(),
                # Services/Offerings
                "offerings": self.build_offerings(),
                # FAQ
                "faq": self.build_faq(),
            }
        }

        return config

    def build_address(self) -> str:
        """Build full address from separate fields"""
        parts = []
        if street := self.contact_inputs.get("street_address", QLineEdit()).text():
            parts.append(street)
        if city := self.contact_inputs.get("city", QLineEdit()).text():
            parts.append(city)
        if state := self.contact_inputs.get("state", QLineEdit()).text():
            parts.append(state)
        if zip_code := self.contact_inputs.get("zip", QLineEdit()).text():
            parts.append(zip_code)

        return ", ".join(filter(None, parts))

    def normalize_phone(self, phone: str) -> str:
        """Convert phone to normalized format"""
        if not phone:
            return ""

        # Remove all non-digits
        digits = "".join(filter(str.isdigit, phone))

        # Format as +1-XXX-XXX-XXXX
        if len(digits) == 10:
            return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits.startswith("1"):
            return f"+1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"

        return phone  # Return original if can't parse

    def load_yaml(self):
        """Load YAML configuration from a file and populate the UI fields"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open YAML File", "", "YAML Files (*.yaml *.yml)"
        )
        if not file_path:
            return
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            self.populate_fields_from_config(config)
            QMessageBox.information(
                self, "Load YAML", "✅ YAML configuration loaded successfully!"
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to load YAML:\n{str(e)}")

    def populate_fields_from_config(self, config: dict):
        """Populate UI fields from loaded config dictionary - with error handling"""
        try:
            # Ensure we have the right structure
            if not isinstance(config, dict):
                raise ValueError("Config must be a dictionary")

            client = config.get("client", {})
            if not isinstance(client, dict):
                raise ValueError("Client section must be a dictionary")

            # Business info - with safe defaults
            self.business_inputs["business_name"].setText(
                str(client.get("business_name", ""))
            )
            self.business_inputs["domain"].setText(str(client.get("domain", "")))
            self.business_inputs["industry"].setText(str(client.get("industry", "")))

            # Contact info - with safe handling
            contact = client.get("contact", {})
            if isinstance(contact, dict):
                self.contact_inputs["name"].setText(str(contact.get("name", "")))
                self.contact_inputs["phone"].setText(str(contact.get("phone", "")))

                # Handle address parsing safely
                address = contact.get("address", "")
                if isinstance(address, str) and address:
                    address_parts = address.split(",")
                    self.contact_inputs["street_address"].setText(
                        address_parts[0].strip() if len(address_parts) > 0 else ""
                    )
                    self.contact_inputs["city"].setText(
                        address_parts[1].strip() if len(address_parts) > 1 else ""
                    )
                    self.contact_inputs["state"].setText(
                        address_parts[2].strip() if len(address_parts) > 2 else ""
                    )
                    self.contact_inputs["zip"].setText(
                        address_parts[3].strip() if len(address_parts) > 3 else ""
                    )

            # Social media - with safe handling
            social = client.get("social_media", {})
            if isinstance(social, dict):
                for platform in self.social_inputs:
                    self.social_inputs[platform].setText(str(social.get(platform, "")))

            # Branding - with safe handling
            branding = client.get("branding", {})
            if isinstance(branding, dict):
                for key in self.branding_inputs:
                    self.branding_inputs[key].setText(str(branding.get(key, "")))

            # GBP - with safe handling
            gbp = client.get("google_business_profile", {})
            if isinstance(gbp, dict):
                self.gbp_inputs["embed_code"].setPlainText(
                    str(gbp.get("embed_code", ""))
                )

            # Google Maps for cities - with safe handling
            google_maps = client.get("google_maps", {})
            self.city_data = {}
            if isinstance(google_maps, dict):
                cities = google_maps.get("cities", {})
                if isinstance(cities, dict):
                    for city_key, city_info in cities.items():
                        if isinstance(city_info, dict):
                            self.city_data[city_key] = {
                                "embed_code": city_info.get("embed_code", "")
                            }

            self.refresh_city_list()
            self.update_city_selector()

            # Pages - with safe handling
            pages = client.get("pages", [])
            if isinstance(pages, list) and pages:
                # Extract hero image from first page
                first_page = pages[0] if isinstance(pages[0], dict) else {}
                self.page_inputs["hero_image"].setText(
                    str(first_page.get("hero_image", ""))
                )

                # Extract cities from pages (skip home page)
                target_cities = []
                for page in pages:
                    if isinstance(page, dict) and page.get("slug") != "index":
                        city = page.get("city", "")
                        if city and city not in target_cities:
                            target_cities.append(city)

                self.page_inputs["target_cities"].setPlainText("\n".join(target_cities))

            # Services/Offerings - with safe handling
            offerings = client.get("offerings", [])
            if isinstance(offerings, list):
                service_names = []
                for offering in offerings:
                    if isinstance(offering, dict):
                        service_names.append(str(offering.get("name", "")))
                    else:
                        service_names.append(str(offering))
                self.service_inputs["services"].setPlainText(
                    "\n".join(filter(None, service_names))
                )

            # FAQ - with safe handling
            faq = client.get("faq", [])
            if isinstance(faq, list):
                faq_questions = []
                for item in faq:
                    if isinstance(item, dict):
                        question = item.get("question", "")
                        if question:
                            faq_questions.append(str(question))
                    else:
                        faq_questions.append(str(item))
                self.service_inputs["faq"].setPlainText(
                    "\n".join(filter(None, faq_questions))
                )

        except Exception as e:
            # Show detailed error for debugging
            QMessageBox.critical(
                self,
                "YAML Load Error",
                f"Error loading YAML configuration:\n\n{str(e)}\n\n"
                f"This usually means the YAML file structure doesn't match what's expected.\n"
                f"You may need to create a new configuration.",
            )
            print(f"DEBUG - Config structure: {config}")  # For debugging

    def build_social_media(self) -> Optional[Dict[str, str]]:
        """Build social media dict from inputs"""
        social = {}
        for platform, widget in self.social_inputs.items():
            if url := widget.text().strip():
                social[platform] = url
        return social if social else None

    def build_branding(self) -> Dict[str, str]:
        """Build branding dict from inputs"""
        branding = {}
        for key, widget in self.branding_inputs.items():
            if value := widget.text().strip():
                branding[key] = value

        # Set defaults if nothing specified
        if not branding:
            branding = {
                "primary_color": "#007bff",
                "secondary_color": "#6c757d",
                "font_family": "Arial, sans-serif",
            }
        return branding

    def build_gbp(self) -> Optional[Dict[str, str]]:
        """Build Google Business Profile config"""
        embed_code = (
            self.gbp_inputs.get("embed_code", QTextEdit()).toPlainText().strip()
        )
        if embed_code:
            return {"embed_code": embed_code}
        return None

    def build_google_maps(self) -> Optional[Dict[str, Any]]:
        """Build Google Maps config from city data"""
        if not self.city_data:
            return None
        return {"cities": self.city_data}

    def build_pages(self) -> list:
        """Build pages list from target cities and business info"""
        pages = []
        business_name = self.business_inputs["business_name"].text()
        industry = self.business_inputs["industry"].text() or "services"
        hero_image = self.page_inputs.get("hero_image", QLineEdit()).text()

        # Home page
        pages.append(
            {
                "title": "Home",
                "slug": "index",
                "primary_keyword": industry.lower(),
                "secondary_keywords": [business_name.lower(), "local business"],
                "hero_image": hero_image,
            }
        )

        # City pages
        cities_text = self.page_inputs.get("target_cities", QTextEdit()).toPlainText()
        if cities_text:
            for city in cities_text.split("\n"):
                city = city.strip()
                if city:
                    pages.append(
                        {
                            "title": f"{industry} in {city}",
                            "slug": city.lower().replace(" ", "-").replace(",", ""),
                            "primary_keyword": f"{industry.lower()} {city.lower()}",
                            "secondary_keywords": [
                                f"{city.lower()} {industry.lower()}",
                                f"local {industry.lower()}",
                            ],
                            "hero_image": hero_image,
                            "city": city,
                        }
                    )
        return pages

    def build_offerings(self) -> list:
        """Build offerings list from services"""
        offerings = []
        services_text = self.service_inputs.get("services", QTextEdit()).toPlainText()
        industry = self.business_inputs["industry"].text() or "Professional Service"

        if services_text:
            for service in services_text.split("\n"):
                service = service.strip()
                if service:
                    offerings.append(
                        {
                            "name": service,
                            "description": f"Professional {service.lower()} services",
                            "category": industry,
                        }
                    )
        return offerings

    def build_faq(self) -> list:
        """Build FAQ list from input"""
        faq_list = []
        faq_text = self.service_inputs.get("faq", QTextEdit()).toPlainText()

        if faq_text:
            for question in faq_text.split("\n"):
                question = question.strip()
                if question:
                    faq_list.append(
                        {
                            "question": question,
                            "answer": f"We provide comprehensive answers about {question.lower()}. Contact us for more details.",
                        }
                    )
        return faq_list

    def save_yaml(self):
        """Save current configuration to YAML file"""
        try:
            config_dict = self.build_config_dict()
            # Validate before saving
            self.config_parser.parse(config_dict)

            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save YAML File", "", "YAML Files (*.yaml *.yml)"
            )
            if file_name:
                with open(file_name, "w", encoding="utf-8") as f:
                    yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)
                QMessageBox.information(self, "Saved", "✅ YAML saved successfully!")

        except ConfigValidationError as e:
            QMessageBox.warning(
                self,
                "Validation Error",
                f"❌ Please fix these issues before saving:\n{str(e)}",
            )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to save YAML:\n{e}")

    def preview_website(self):
        """Preview the generated website"""
        try:
            config_dict = self.build_config_dict()
            config = self.config_parser.parse(config_dict)

            # Import and use WebsiteGenerator
            from core.website_generator import WebsiteGenerator

            generator = WebsiteGenerator()

            # Generate to temporary directory
            temp_dir = tempfile.mkdtemp()
            result = generator.generate(config, temp_dir)

            if result.success:
                # Open the generated index.html in browser
                index_path = Path(temp_dir) / "index.html"
                file_url = index_path.as_uri()
                webbrowser.open(file_url)

                QMessageBox.information(
                    self,
                    "Preview Opened",
                    f"✅ Website preview opened in your browser!\n\nTemporary files: {temp_dir}",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Preview Error",
                    f"❌ Failed to generate preview:\n{result.errors}",
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Preview failed:\n{e}")
