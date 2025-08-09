"""
Refactored YAML Builder Widget for SEO Authority Website Generator
Integrates with new nested config structure and ConfigParser

Version: 2.0.0
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

import sys
from pathlib import Path
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
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
import yaml

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.core.config_parser import ConfigParser, ConfigValidationError
from src.ui.dialogs.city_embed_dialog import CityEmbedDialog


class YAMLBuilderWidget(QWidget):
    """
    Refactored YAML builder that creates nested config structure
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
        layout.addWidget(self.service_inputs["faq"])

        group.setLayout(layout)
        return group

    def create_cities_section(self) -> QGroupBox:
        """Create cities with Google Maps embeds section"""
        group = QGroupBox("Cities with Google Maps")
        layout = QVBoxLayout()

        # City list display
        layout.addWidget(QLabel("Added Cities:"))
        self.city_list = QListWidget()
        self.city_list.setFont(QFont("Arial", self.font_size))
        self.city_list.setFixedHeight(150)
        layout.addWidget(self.city_list)

        # Manage cities button
        self.manage_cities_button = QPushButton("Manage Cities & Google Maps")
        self.manage_cities_button.setFont(QFont("Arial", self.font_size))
        self.manage_cities_button.clicked.connect(self.open_city_dialog)
        layout.addWidget(self.manage_cities_button)

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

    def open_city_dialog(self):
        """Open dialog to manage cities and Google Maps embeds"""
        dialog = CityEmbedDialog(self)
        if dialog.exec():
            city_data = dialog.get_data()
            key = f"{city_data['city']}, {city_data['state']}"
            self.city_data[key] = {"embed_code": city_data["embed_code"]}
            self.refresh_city_list()
            self.config_changed.emit()

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
                # Google Maps
                "google_maps": self.build_google_maps(),
                # Pages
                "pages": self.build_pages(),
                # Services/Offerings
                "offerings": self.build_offerings(),
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

    def build_social_media(self) -> dict:
        """Build social media dict from inputs"""
        social = {}
        for platform, widget in self.social_inputs.items():
            if url := widget.text().strip():
                social[platform] = url
        return social if social else None

    def build_branding(self) -> dict:
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

    def build_google_maps(self) -> dict:
        """Build Google Maps config from city data"""
        if not self.city_data:
            return None

        # Use the first city's embed as the main one
        for city_data in self.city_data.values():
            if embed_code := city_data.get("embed_code"):
                # Extract URL from iframe if present
                import re

                match = re.search(r'src=["\']([^"\']*)["\']', embed_code)
                if match:
                    return {"embed_url": match.group(1)}

        return None

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

    def load_yaml(self):
        """Load YAML configuration from file"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open YAML File", "", "YAML Files (*.yaml *.yml)"
        )
        if not file_name:
            return

        try:
            with open(file_name, "r", encoding="utf-8") as file:
                data = yaml.safe_load(file)

            self.populate_from_config(data)
            QMessageBox.information(self, "Loaded", "✅ YAML loaded successfully.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Failed to load YAML file:\n{e}")

    def populate_from_config(self, config: dict):
        """Populate UI fields from config dictionary"""
        client = config.get("client", {})

        # Business info
        self.business_inputs["business_name"].setText(client.get("business_name", ""))
        self.business_inputs["domain"].setText(client.get("domain", ""))
        self.business_inputs["industry"].setText(client.get("industry", ""))

        # Contact info
        contact = client.get("contact", {})
        self.contact_inputs["name"].setText(contact.get("name", ""))
        self.contact_inputs["phone"].setText(contact.get("phone", ""))

        # Parse address back to components if needed
        if address := contact.get("address"):
            # This is simplified - you might want more sophisticated address parsing
            parts = address.split(", ")
            if len(parts) >= 1:
                self.contact_inputs.get("street_address", QLineEdit()).setText(parts[0])
            if len(parts) >= 2:
                self.contact_inputs.get("city", QLineEdit()).setText(parts[1])

        # Social media
        social = client.get("social_media", {})
        for platform, widget in self.social_inputs.items():
            widget.setText(social.get(platform, ""))

        # Branding
        branding = client.get("branding", {})
        for key, widget in self.branding_inputs.items():
            widget.setText(branding.get(key, ""))

        # TODO: Populate other sections (pages, cities, etc.)
        # This would require more complex reverse-mapping logic

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
            from src.core.website_generator import WebsiteGenerator

            generator = WebsiteGenerator()

            # Generate to temporary directory
            import tempfile

            with tempfile.TemporaryDirectory() as temp_dir:
                result = generator.generate(config, temp_dir)

                if result.success:
                    # Open the generated index.html in browser
                    import webbrowser

                    index_path = Path(temp_dir) / "index.html"
                    webbrowser.open(f"file://{index_path}")
                else:
                    QMessageBox.warning(
                        self,
                        "Preview Error",
                        f"❌ Failed to generate preview:\n{result.errors}",
                    )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"❌ Preview failed:\n{e}")
