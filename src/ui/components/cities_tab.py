"""
Filename: cities_tab_fixed.py
Path: E:/projects/cloud-stack-generator/src/ui/components/cities_tab_fixed.py
Description: Cities management tab with fixed layout issues
Simple, working layout that displays correctly in all screen modes

Version: 2.1.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

from typing import Dict, Any, List
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QGroupBox,
    QFrame,
    QMessageBox,
    QScrollArea,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from .base_tab import BaseTab, ValidationResult
from ..dialogs.city_embed_dialog import CityEmbedDialog
from ..dialogs.enhanced_city_embed_dialog import EnhancedCityEmbedDialog

# Import error logging
from ...utils import log_validation_error

# Import Wikipedia API
try:
    from ...core.utils.wikipedia_api import WikipediaAPI
except ImportError:
    WikipediaAPI = None

# Import secure API key storage (note: now using app-wide system instead)


class CitiesTab(BaseTab):
    """Tab for cities and locations management with fixed layout"""

    # Signals
    config_changed = pyqtSignal()
    validation_requested = pyqtSignal()
    data_loaded = pyqtSignal()

    def __init__(self, parent=None):
        self.city_data = {}
        self.city_inputs = {}
        self.seo_inputs = {}
        self.error_labels = {}
        self.has_changes = False
        self.app_api_keys = {}  # Store reference to app-wide API keys
        super().__init__(parent)

    def setup_ui(self):
        """Setup cities management UI with working layout"""
        # Create main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Create main sections
        self._create_target_cities_section(content_layout)
        self._create_api_config_section(content_layout)
        self._create_city_maps_section(content_layout)
        self._create_wikipedia_section(content_layout)
        self._create_seo_content_section(content_layout)
        
        # Add validation button
        validation_button = QPushButton("Validate Cities Configuration")
        validation_button.clicked.connect(self.validate_data)
        validation_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        validation_button.setMaximumWidth(300)
        content_layout.addWidget(validation_button)

        # Add stretch to push content to top
        content_layout.addStretch()

        # Create container widget
        container = QFrame()
        container.setLayout(content_layout)
        
        # Set up scroll area
        scroll_area.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)

    def _create_target_cities_section(self, parent_layout: QVBoxLayout):
        """Create target cities input section"""
        # Section header
        header = QLabel("Target Cities")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Cities input group
        cities_group = QGroupBox()
        cities_group.setMaximumHeight(200)
        cities_layout = QVBoxLayout()
        cities_layout.setSpacing(10)

        # Instructions
        instructions = QLabel("Enter your target cities (one per line). These will have dedicated landing pages generated.")
        instructions.setFont(QFont("Arial", 10))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic;")
        cities_layout.addWidget(instructions)

        # Target cities input
        cities_label = QLabel("* Target Cities:")
        cities_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        cities_layout.addWidget(cities_label)

        self.city_inputs["target_cities"] = QTextEdit()
        self.city_inputs["target_cities"].setFont(QFont("Arial", 10))
        self.city_inputs["target_cities"].setMaximumHeight(120)
        self.city_inputs["target_cities"].setMinimumHeight(120)
        self.city_inputs["target_cities"].setPlaceholderText("Detroit\nGrand Rapids\nAnn Arbor\nKalamazoo\nLansing")
        self.city_inputs["target_cities"].textChanged.connect(self._on_target_cities_changed)
        cities_layout.addWidget(self.city_inputs["target_cities"])

        # Error label for target cities
        target_cities_error = self._create_error_label("target_cities")
        cities_layout.addWidget(target_cities_error)

        cities_group.setLayout(cities_layout)
        parent_layout.addWidget(cities_group)

    def _create_api_config_section(self, parent_layout: QVBoxLayout):
        """Create API configuration section"""
        # Section header
        header = QLabel("API Configuration")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)
        
        # API config group
        api_group = QGroupBox()
        api_group.setMaximumHeight(150)
        api_layout = QVBoxLayout()
        api_layout.setSpacing(10)
        
        # Instructions
        instructions = QLabel("Configure your Google Maps API key to enable automatic embed generation.")
        instructions.setFont(QFont("Arial", 10))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic;")
        api_layout.addWidget(instructions)
        
        # API key input
        api_key_layout = QHBoxLayout()
        api_key_label = QLabel("Google Maps API Key:")
        api_key_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        api_key_layout.addWidget(api_key_label)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setFont(QFont("Arial", 10))
        self.api_key_input.setPlaceholderText("Enter your Google Maps API key here...")
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.textChanged.connect(self._on_api_key_changed)
        api_key_layout.addWidget(self.api_key_input)
        
        # Show/hide API key button
        self.show_api_key_btn = QPushButton("👁️")
        self.show_api_key_btn.setMaximumWidth(30)
        self.show_api_key_btn.setToolTip("Show/Hide API Key")
        self.show_api_key_btn.clicked.connect(self._toggle_api_key_visibility)
        api_key_layout.addWidget(self.show_api_key_btn)
        
        api_layout.addLayout(api_key_layout)
        
        # API key status
        self.api_status_label = QLabel("⚠️ No API key configured")
        self.api_status_label.setStyleSheet("color: orange; font-weight: bold;")
        api_layout.addWidget(self.api_status_label)
        
        api_group.setLayout(api_layout)
        parent_layout.addWidget(api_group)

    def _create_city_maps_section(self, parent_layout: QVBoxLayout):
        """Create Google Maps integration section"""
        # Section header
        header = QLabel("Google Maps Integration")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Maps group
        maps_group = QGroupBox()
        maps_group.setMaximumHeight(250)
        maps_layout = QVBoxLayout()
        maps_layout.setSpacing(10)

        # Instructions
        instructions = QLabel("Select cities from your Target Cities list to add Google Maps embeds.")
        instructions.setFont(QFont("Arial", 10))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic;")
        maps_layout.addWidget(instructions)

        # City selector and add button
        selector_layout = QHBoxLayout()
        
        selector_label = QLabel("Select City:")
        selector_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        selector_layout.addWidget(selector_label)

        self.city_selector = QComboBox()
        self.city_selector.setFont(QFont("Arial", 10))
        self.city_selector.setMinimumHeight(30)
        self.city_selector.addItem("Select a city...")
        selector_layout.addWidget(self.city_selector)

        self.add_city_map_btn = QPushButton("Add Google Map")
        self.add_city_map_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.add_city_map_btn.setMinimumHeight(30)
        self.add_city_map_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.add_city_map_btn.clicked.connect(self._add_city_map)
        self.add_city_map_btn.setEnabled(False)
        selector_layout.addWidget(self.add_city_map_btn)

        maps_layout.addLayout(selector_layout)

        # City list display
        list_label = QLabel("Cities with Google Maps:")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        maps_layout.addWidget(list_label)

        self.city_list = QListWidget()
        self.city_list.setFont(QFont("Arial", 10))
        self.city_list.setMaximumHeight(120)
        self.city_list.setMinimumHeight(120)
        maps_layout.addWidget(self.city_list)

        # Connect signals
        self.city_selector.currentTextChanged.connect(self._on_city_selector_changed)

        maps_group.setLayout(maps_layout)
        parent_layout.addWidget(maps_group)

    def _create_wikipedia_section(self, parent_layout: QVBoxLayout):
        """Create Wikipedia image preview section"""
        # Section header
        header = QLabel("Wikipedia Images Preview")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)
        
        # Wikipedia group
        wiki_group = QGroupBox()
        wiki_group.setMaximumHeight(200)
        wiki_layout = QVBoxLayout()
        wiki_layout.setSpacing(10)
        
        # Instructions
        instructions = QLabel("Preview Wikipedia images for your target cities with proper attribution.")
        instructions.setFont(QFont("Arial", 10))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic;")
        wiki_layout.addWidget(instructions)
        
        # Wikipedia status
        wiki_status = QLabel("✅ Wikipedia integration available" if WikipediaAPI else "❌ Wikipedia integration not available")
        wiki_status.setStyleSheet(f"color: {'green' if WikipediaAPI else 'red'}; font-weight: bold;")
        wiki_layout.addWidget(wiki_status)
        
        if WikipediaAPI:
            # City selector for Wikipedia preview
            selector_layout = QHBoxLayout()
            
            city_label = QLabel("Select City for Preview:")
            city_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            selector_layout.addWidget(city_label)
            
            self.wiki_city_selector = QComboBox()
            self.wiki_city_selector.setFont(QFont("Arial", 10))
            self.wiki_city_selector.setMinimumHeight(30)
            self.wiki_city_selector.addItem("Select a city...")
            selector_layout.addWidget(self.wiki_city_selector)
            
            # Preview button
            self.preview_wiki_btn = QPushButton("Preview Wikipedia Info")
            self.preview_wiki_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.preview_wiki_btn.setMinimumHeight(30)
            self.preview_wiki_btn.setStyleSheet("""
                QPushButton {
                    background-color: #17a2b8;
                    color: white;
                    font-weight: bold;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #138496;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """)
            self.preview_wiki_btn.clicked.connect(self._preview_wikipedia_info)
            self.preview_wiki_btn.setEnabled(False)
            selector_layout.addWidget(self.preview_wiki_btn)
            
            wiki_layout.addLayout(selector_layout)
            
            # Preview display area
            self.wiki_preview_area = QTextEdit()
            self.wiki_preview_area.setFont(QFont("Arial", 9))
            self.wiki_preview_area.setMaximumHeight(80)
            self.wiki_preview_area.setMinimumHeight(80)
            self.wiki_preview_area.setReadOnly(True)
            self.wiki_preview_area.setPlaceholderText("Wikipedia information will appear here...")
            wiki_layout.addWidget(self.wiki_preview_area)
            
            # Connect signals
            self.wiki_city_selector.currentTextChanged.connect(self._on_wiki_city_selector_changed)
            
        wiki_group.setLayout(wiki_layout)
        parent_layout.addWidget(wiki_group)

    def _create_seo_content_section(self, parent_layout: QVBoxLayout):
        """Create SEO content fields for CloudStack SOP compliance"""
        # Section header
        header = QLabel("SEO Content for City Pages")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # SEO content group
        seo_group = QGroupBox()
        seo_group.setMaximumHeight(400)
        seo_layout = QVBoxLayout()
        seo_layout.setSpacing(10)

        # Instructions
        instructions = QLabel("Add rich SEO content for 800-1,200 word city pages following CloudStack SOP standards.")
        instructions.setFont(QFont("Arial", 10))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic;")
        seo_layout.addWidget(instructions)

        # SEO content fields
        seo_fields = [
            ("neighborhoods", "City Neighborhoods & Landmarks", "Downtown Detroit, Corktown, Midtown, Belle Isle Park"),
            ("pain_points", "Local Pain Points & Seasonal Factors", "Winter weather challenges, road construction impacts"),
            ("case_studies", "Micro Case Studies & Examples", "Completed project: Historic downtown renovation"),
        ]

        for field_key, label_text, placeholder in seo_fields:
            # Label
            label = QLabel(label_text + ":")
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            label.setWordWrap(True)
            seo_layout.addWidget(label)

            # Input field
            widget = QTextEdit()
            widget.setMaximumHeight(60)
            widget.setMinimumHeight(60)
            widget.setFont(QFont("Arial", 9))
            widget.setPlaceholderText(placeholder)
            widget.textChanged.connect(self._emit_config_changed)
            
            self.seo_inputs[field_key] = widget
            seo_layout.addWidget(widget)

        # City-specific FAQ section
        faq_label = QLabel("City-Specific FAQ (4-6 Questions):")
        faq_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        faq_label.setWordWrap(True)
        seo_layout.addWidget(faq_label)

        self.seo_inputs["local_faq"] = QTextEdit()
        self.seo_inputs["local_faq"].setFont(QFont("Arial", 9))
        self.seo_inputs["local_faq"].setMaximumHeight(80)
        self.seo_inputs["local_faq"].setMinimumHeight(80)
        self.seo_inputs["local_faq"].setPlaceholderText(
            "Do you serve Detroit's downtown area?\n"
            "What are your typical response times in Detroit?\n"
            "Do you handle winter weather emergencies?"
        )
        self.seo_inputs["local_faq"].textChanged.connect(self._emit_config_changed)
        seo_layout.addWidget(self.seo_inputs["local_faq"])

        seo_group.setLayout(seo_layout)
        parent_layout.addWidget(seo_group)

    def _create_error_label(self, field_name: str) -> QLabel:
        """Create an error label for a field"""
        error_label = QLabel()
        error_label.setFont(QFont("Arial", 10))
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

    def _on_target_cities_changed(self):
        """Handle target cities text changes"""
        self._update_city_selector()
        self._emit_config_changed()

    def _update_city_selector(self):
        """Update the city selector dropdown when target cities change"""
        cities_text = self.city_inputs["target_cities"].toPlainText()
        cities = [city.strip() for city in cities_text.split("\n") if city.strip()]

        # Clear and repopulate Maps selector
        self.city_selector.clear()
        self.city_selector.addItem("Select a city...")

        for city in cities:
            # Check if this city already has a map
            if city not in self.city_data.keys():
                self.city_selector.addItem(city)
                
        # Update Wikipedia selector if available
        if WikipediaAPI and hasattr(self, 'wiki_city_selector'):
            self.wiki_city_selector.clear()
            self.wiki_city_selector.addItem("Select a city...")
            
            for city in cities:
                self.wiki_city_selector.addItem(city)

    def _on_city_selector_changed(self, city_name: str):
        """Handle city selector change"""
        self.add_city_map_btn.setEnabled(
            city_name != "Select a city..." and city_name != ""
        )

    def _on_api_key_changed(self):
        """Handle API key input changes"""
        api_key = self.api_key_input.text().strip()
        if api_key:
            # Store API key in app-wide system
            self.app_api_keys['google_maps_api_key'] = api_key
            # Notify parent to save API keys
            if hasattr(self.parent(), 'save_app_api_keys'):
                self.parent().save_app_api_keys(self.app_api_keys)
            self.api_status_label.setText("✅ API key configured and stored securely")
            self.api_status_label.setStyleSheet("color: green; font-weight: bold;")
        else:
            # Remove API key from app-wide system
            if 'google_maps_api_key' in self.app_api_keys:
                del self.app_api_keys['google_maps_api_key']
            # Notify parent to save API keys
            if hasattr(self.parent(), 'save_app_api_keys'):
                self.parent().save_app_api_keys(self.app_api_keys)
            self.api_status_label.setText("⚠️ No API key configured")
            self.api_status_label.setStyleSheet("color: orange; font-weight: bold;")
        self._emit_config_changed()

    def _toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.api_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_api_key_btn.setText("🙈")
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_api_key_btn.setText("👁️")

    def _get_api_key(self) -> str:
        """Get the current API key from app-wide storage"""
        return self.app_api_keys.get("google_maps_api_key", "")

    def _on_wiki_city_selector_changed(self, city_name: str):
        """Handle Wikipedia city selector change"""
        if WikipediaAPI and hasattr(self, 'preview_wiki_btn'):
            self.preview_wiki_btn.setEnabled(
                city_name != "Select a city..." and city_name != ""
            )

    def _preview_wikipedia_info(self):
        """Preview Wikipedia information for selected city"""
        if not WikipediaAPI:
            return
            
        selected_city = self.wiki_city_selector.currentText()
        if selected_city and selected_city != "Select a city...":
            try:
                # Create Wikipedia API instance
                wiki_api = WikipediaAPI()
                
                # Get city information
                city_info = wiki_api.get_city_image_info(selected_city)
                
                # Format the preview text
                preview_text = f"City: {city_info['city_name']}\nWikipedia: {city_info['wikipedia_page'] or 'Not found'}\nImage: {city_info['image_url']}\nDescription: {city_info['description'] or 'No description available'}"
                
                self.wiki_preview_area.setPlainText(preview_text)
                
            except Exception as e:
                self.wiki_preview_area.setPlainText(f"Error retrieving Wikipedia info: {str(e)}")

    def _add_city_map(self):
        """Add Google Map for selected city"""
        selected_city = self.city_selector.currentText()
        if selected_city and selected_city != "Select a city...":
            # Get API key for enhanced dialog
            api_key = self._get_api_key()
            
            # Use enhanced dialog if API key is available, otherwise fall back to basic dialog
            if api_key:
                dialog = EnhancedCityEmbedDialog(self, api_key=api_key)
            else:
                dialog = CityEmbedDialog(self)
            
            dialog.city_input.setText(selected_city)

            if dialog.exec():
                city_data = dialog.get_data()
                location_key = city_data["location"]
                
                # Store additional data for API-generated embeds
                embed_data = {
                    "embed_code": city_data["embed_code"],
                    "generation_method": city_data.get("generation_method", "manual")
                }
                
                # Store API options if available
                if city_data.get("api_options"):
                    embed_data["api_options"] = city_data["api_options"]
                
                self.city_data[location_key] = embed_data
                self._refresh_city_list()
                self._update_city_selector()  # Refresh selector
                self._emit_config_changed()

    def _refresh_city_list(self):
        """Refresh the city list display"""
        self.city_list.clear()
        for location, data in self.city_data.items():
            has_embed = bool(data.get("embed_code"))
            status = "✅" if has_embed else "⚠️"
            item = QListWidgetItem(f"{status} {location}")
            self.city_list.addItem(item)

    def get_config_data(self) -> Dict[str, Any]:
        """Get cities configuration data - UNIFIED FORMAT"""
        # Target cities (legacy format)
        cities_text = self.city_inputs["target_cities"].toPlainText().strip()
        target_cities = [city.strip() for city in cities_text.split("\n") if city.strip()]

        # SEO content
        seo_content = {}
        for field_key, widget in self.seo_inputs.items():
            content = widget.toPlainText().strip()
            if content:
                seo_content[field_key] = content

        # Google Maps data
        google_maps = {"cities": self.city_data} if self.city_data else {}

        # Enhanced city pages (NEW: convert target_cities to city_pages format for compatibility)
        city_pages = []
        for city_name in target_cities:
            # Create basic CityPageConfig from legacy data
            city_page_data = {
                "city_name": city_name,
                "state": "",  # Extract from city name if format is "City, State"
                "slug": self._create_slug(city_name),
                "title": f"{city_name} Services",
                "meta_description": f"Professional services in {city_name}",
                "primary_keyword": f"{city_name} services",
                "secondary_keywords": [],
                "hero_title": f"{city_name} — Professional Services",
                "breadcrumbs": ["Home", "Service Areas", city_name],
                "about_city": seo_content.get("city_description", f"Information about {city_name}"),
                "city_image": {
                    "image_url": "",
                    "alt_text": f"{city_name} skyline",
                    "caption": "",
                    "credit": "",
                    "source": "Wikipedia"
                },
                "seo_content_title": f"Professional Services in {city_name}",
                "seo_content_body": seo_content.get("city_content", f"We provide professional services throughout {city_name} and surrounding areas."),
                "places_of_interest": [],
                "city_faq": [],
                "featured_products": [],
                "city_map_embed": self.city_data.get(city_name, {}).get("embed_code", ""),
                "service_area_note": f"Serving {city_name} and surrounding areas"
            }
            
            # Parse state from city name if format is "City, State"
            if ", " in city_name:
                city_part, state_part = city_name.split(", ", 1)
                city_page_data["city_name"] = city_part
                city_page_data["state"] = state_part
            
            city_pages.append(city_page_data)

        # NOTE: API keys are stored securely and not included in config files

        return {
            "target_cities": target_cities,  # Legacy format for backward compatibility
            "city_pages": city_pages,        # NEW: Enhanced format for Sprint 2.5+
            "seo_content": seo_content,
            "google_maps": google_maps,
        }
        
    def _create_slug(self, city_name: str) -> str:
        """Create URL-friendly slug from city name"""
        import re
        # Remove state suffix if present
        city_part = city_name.split(",")[0].strip()
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', city_part.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        return slug

    def set_config_data(self, data: Dict[str, Any]):
        """Set cities configuration data"""
        self._start_loading()
        
        try:
            # Set target cities
            target_cities = data.get("target_cities", [])
            if isinstance(target_cities, list):
                self.city_inputs["target_cities"].setPlainText("\n".join(target_cities))

            # Set SEO content
            seo_content = data.get("seo_content", {})
            for field_key, widget in self.seo_inputs.items():
                content = seo_content.get(field_key, "")
                widget.setPlainText(str(content))

            # Set Google Maps data
            google_maps = data.get("google_maps", {})
            self.city_data = google_maps.get("cities", {})
            self._refresh_city_list()
            self._update_city_selector()

            # Load API key from app-wide storage
            stored_api_key = self.app_api_keys.get("google_maps_api_key", "")
            self.api_key_input.setText(stored_api_key)
            self._on_api_key_changed()  # Update status

            # Clear any existing errors
            for field_name in self.error_labels:
                self._hide_field_error(field_name)

            # Emit data loaded signal
            self.data_loaded.emit()
        
        finally:
            self._finish_loading()

    def validate_data(self) -> ValidationResult:
        """Validate cities data"""
        result = ValidationResult()

        # Clear existing errors
        for field_name in self.error_labels:
            self._hide_field_error(field_name)

        # Validate target cities
        cities_text = self.city_inputs["target_cities"].toPlainText().strip()
        if not cities_text:
            error_msg = "At least one target city is required"
            result.add_error(error_msg)
            self._show_field_error("target_cities", error_msg)
        else:
            cities = [city.strip() for city in cities_text.split("\n") if city.strip()]
            if len(cities) == 0:
                error_msg = "At least one valid target city is required"
                result.add_error(error_msg)
                self._show_field_error("target_cities", error_msg)
            elif len(cities) > 20:
                result.add_warning(f"Large number of cities ({len(cities)}) may impact site performance")

        # Check for SEO content completeness
        seo_fields_filled = 0
        total_seo_fields = len(self.seo_inputs)
        
        for field_key, widget in self.seo_inputs.items():
            if widget.toPlainText().strip():
                seo_fields_filled += 1

        if seo_fields_filled == 0:
            result.add_warning("No SEO content provided - city pages will have basic content only")
        elif seo_fields_filled < total_seo_fields // 2:
            result.add_warning(f"Only {seo_fields_filled}/{total_seo_fields} SEO fields completed")

        # Check Google Maps coverage
        cities_with_maps = len(self.city_data)
        total_cities = len([c.strip() for c in cities_text.split("\n") if c.strip()]) if cities_text else 0
        
        if total_cities > 0 and cities_with_maps == 0:
            result.add_warning("No Google Maps added - consider adding maps for local credibility")
        elif cities_with_maps < total_cities:
            result.add_warning(f"Google Maps added for {cities_with_maps}/{total_cities} cities")

        return result
    
    def get_tab_name(self) -> str:
        """Get tab name for title display"""
        return "Cities & Locations"

    def set_app_api_keys(self, api_keys: Dict[str, str]):
        """Set the app-wide API keys reference"""
        self.app_api_keys = api_keys.copy()
        # Update the UI with the loaded API key
        stored_api_key = self.app_api_keys.get("google_maps_api_key", "")
        self.api_key_input.setText(stored_api_key)
        self._on_api_key_changed()  # Update status
    
    def connect_signals(self):
        """Connect UI signals to emit config_changed"""
        # Signals already connected in individual widgets
        pass