"""
Filename: cities_tab.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\components\\cities_tab.py
Description: Cities management tab with Google Maps integration and SEO content fields
Handles city locations, local SEO content, and CloudStack SOP compliance for authority stack generation

Version: 1.0.0
Date: 2025-08-14
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
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from .base_tab import BaseTab, ValidationResult
from ..dialogs.city_embed_dialog import CityEmbedDialog

# Import error logging
from ...utils import log_validation_error


class CitiesTab(BaseTab):
    """Tab for cities and locations management with SEO content"""

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
        super().__init__(parent)

    def setup_ui(self):
        """Setup cities management UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)

        # Create main sections
        self._create_target_cities_section(main_layout)
        self._create_city_maps_section(main_layout)
        self._create_seo_content_section(main_layout)
        self._create_validation_section(main_layout)

        # Add stretch to push content to top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def _create_target_cities_section(self, parent_layout: QVBoxLayout):
        """Create target cities input section"""
        # Section header
        header_label = self._create_section_header("🎯 Target Cities")
        parent_layout.addWidget(header_label)

        # Cities input group
        cities_group = QGroupBox()
        cities_layout = QVBoxLayout()
        cities_layout.setSpacing(10)

        # Instructions
        instructions = QLabel(
            "Enter your target cities (one per line). These cities will have dedicated landing pages "
            "generated with local SEO optimization and strategic interlinking."
        )
        instructions.setFont(QFont("Arial", 12))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        cities_layout.addWidget(instructions)

        # Target cities input
        cities_label = QLabel("* Target Cities:")
        cities_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        cities_layout.addWidget(cities_label)

        self.city_inputs["target_cities"] = QTextEdit()
        self.city_inputs["target_cities"].setFont(QFont("Arial", 14))
        self.city_inputs["target_cities"].setMinimumHeight(140)
        # Remove maximum height to allow proper scrolling and remove size restrictions
        self.city_inputs["target_cities"].setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.city_inputs["target_cities"].setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.city_inputs["target_cities"].setPlaceholderText(
            "Detroit\nGrand Rapids\nAnn Arbor\nKalamazoo\nLansing"
        )
        self.city_inputs["target_cities"].textChanged.connect(self._on_target_cities_changed)
        cities_layout.addWidget(self.city_inputs["target_cities"])

        # Error label for target cities
        target_cities_error = self._create_error_label("target_cities")
        cities_layout.addWidget(target_cities_error)

        cities_group.setLayout(cities_layout)
        parent_layout.addWidget(cities_group)

    def _create_city_maps_section(self, parent_layout: QVBoxLayout):
        """Create Google Maps integration section"""
        # Section header
        header_label = self._create_section_header("🗺️ Google Maps Integration")
        parent_layout.addWidget(header_label)

        # Maps group
        maps_group = QGroupBox()
        maps_layout = QVBoxLayout()
        maps_layout.setSpacing(15)

        # Instructions
        instructions = QLabel(
            "Select cities from your Target Cities list to add Google Maps embeds. "
            "Maps will appear in the footer of each city page for local credibility."
        )
        instructions.setFont(QFont("Arial", 12))
        instructions.setWordWrap(True)
        instructions.setMinimumHeight(40)
        instructions.setStyleSheet("color: #666; font-style: italic; margin-bottom: 15px; padding: 5px 0px; line-height: 1.4;")
        maps_layout.addWidget(instructions)

        # City selector and add button
        selector_layout = QHBoxLayout()
        
        selector_label = QLabel("Select City:")
        selector_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        selector_layout.addWidget(selector_label)

        self.city_selector = QComboBox()
        self.city_selector.setFont(QFont("Arial", 14))
        self.city_selector.setMinimumHeight(40)
        self.city_selector.addItem("Select a city...")
        selector_layout.addWidget(self.city_selector)

        self.add_city_map_btn = QPushButton("🗺️ Add Google Map")
        self.add_city_map_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.add_city_map_btn.setMinimumHeight(45)
        self.add_city_map_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                font-size: 14px;
                padding: 12px 20px;
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
        list_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        maps_layout.addWidget(list_label)

        self.city_list = QListWidget()
        self.city_list.setFont(QFont("Arial", 14))
        self.city_list.setMinimumHeight(150)
        maps_layout.addWidget(self.city_list)

        # Connect signals
        self.city_selector.currentTextChanged.connect(self._on_city_selector_changed)

        maps_group.setLayout(maps_layout)
        parent_layout.addWidget(maps_group)

    def _create_seo_content_section(self, parent_layout: QVBoxLayout):
        """Create SEO content fields for CloudStack SOP compliance"""
        # Section header
        header_label = self._create_section_header("📝 SEO Content for City Pages")
        parent_layout.addWidget(header_label)

        # SEO content group
        seo_group = QGroupBox()
        seo_layout = QVBoxLayout()
        seo_layout.setSpacing(15)

        # Instructions
        instructions = QLabel(
            "Add rich SEO content that will be used to generate 800-1,200 word city pages "
            "following CloudStack SOP standards for search engine optimization."
        )
        instructions.setFont(QFont("Arial", 12))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic; margin-bottom: 15px;")
        seo_layout.addWidget(instructions)

        # SEO content fields
        seo_fields = [
            ("neighborhoods", "City Neighborhoods & Landmarks", "Downtown Detroit, Corktown, Midtown, Belle Isle Park"),
            ("pain_points", "Local Pain Points & Seasonal Factors", "Winter weather challenges, road construction impacts, supply chain considerations"),
            ("case_studies", "Micro Case Studies & Examples", "Completed project: Historic downtown renovation (Before/After)"),
            ("testimonial", "Local Client Testimonial", "Customer name, project details, and their positive experience"),
            ("directions", "Service Area & Process Description", "We serve the greater Detroit metro area with 24/7 emergency response"),
        ]

        for field_key, label_text, placeholder in seo_fields:
            # Label
            label = QLabel(label_text + ":")
            label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
            label.setWordWrap(True)  # Allow label text to wrap properly
            seo_layout.addWidget(label)

            # Input field
            widget = QTextEdit()
            if field_key in ["case_studies", "testimonial", "directions"]:
                widget.setMinimumHeight(100)
                # Remove maximum height for better scaling in full-screen mode
            else:
                widget.setMinimumHeight(80)
                # Remove maximum height for better scaling in non-critical fields too
            
            widget.setFont(QFont("Arial", 14))
            widget.setPlaceholderText(placeholder)
            widget.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            widget.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            widget.textChanged.connect(self._emit_config_changed)
            
            self.seo_inputs[field_key] = widget
            seo_layout.addWidget(widget)

        # City-specific FAQ section
        faq_label = QLabel("City-Specific FAQ (4-6 Questions):")
        faq_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        faq_label.setWordWrap(True)  # Allow label text to wrap properly
        seo_layout.addWidget(faq_label)

        self.seo_inputs["local_faq"] = QTextEdit()
        self.seo_inputs["local_faq"].setFont(QFont("Arial", 14))
        self.seo_inputs["local_faq"].setMinimumHeight(120)
        # Remove maximum height for better scaling in full-screen mode
        self.seo_inputs["local_faq"].setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.seo_inputs["local_faq"].setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.seo_inputs["local_faq"].setPlaceholderText(
            "Do you serve Detroit's downtown area?\n"
            "What are your typical response times in Detroit?\n"
            "Do you handle winter weather emergencies?\n"
            "What Detroit landmarks have you worked on?"
        )
        self.seo_inputs["local_faq"].textChanged.connect(self._emit_config_changed)
        seo_layout.addWidget(self.seo_inputs["local_faq"])

        seo_group.setLayout(seo_layout)
        parent_layout.addWidget(seo_group)

    def _create_validation_section(self, parent_layout: QVBoxLayout):
        """Create validation controls section"""
        # Separator
        separator = self._create_separator()
        parent_layout.addWidget(separator)

        # Validation controls
        validation_layout = QHBoxLayout()

        self.validate_btn = QPushButton("🔍 Validate Cities")
        self.validate_btn.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.validate_btn.setMinimumHeight(45)
        self.validate_btn.clicked.connect(self.validate_and_show_results)

        validation_layout.addWidget(self.validate_btn)
        validation_layout.addStretch()

        parent_layout.addLayout(validation_layout)

    def _create_section_header(self, text: str) -> QLabel:
        """Create a styled section header"""
        label = QLabel(text)
        label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; padding: 10px 0px;")
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
        error_label.setFont(QFont("Arial", 12))
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

        # Clear and repopulate selector
        self.city_selector.clear()
        self.city_selector.addItem("Select a city...")

        for city in cities:
            # Check if this city already has a map (using exact location key match)
            if city not in self.city_data.keys():
                self.city_selector.addItem(city)

    def _on_city_selector_changed(self, city_name: str):
        """Handle city selector change"""
        self.add_city_map_btn.setEnabled(
            city_name != "Select a city..." and city_name != ""
        )

    def _add_city_map(self):
        """Add Google Map for selected city"""
        selected_city = self.city_selector.currentText()
        if selected_city and selected_city != "Select a city...":
            dialog = CityEmbedDialog(self)
            dialog.city_input.setText(selected_city)

            if dialog.exec():
                city_data = dialog.get_data()
                location_key = city_data["location"]
                self.city_data[location_key] = {"embed_code": city_data["embed_code"]}
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

    def connect_signals(self):
        """Connect UI signals to emit config_changed"""
        # Signals already connected in individual widgets
        pass

    def get_required_fields(self) -> List[str]:
        """Get list of required field names"""
        return ["target_cities"]

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
            result.add_warning(f"Only {seo_fields_filled}/{total_seo_fields} SEO fields completed - consider adding more content for better SEO impact")

        # Check Google Maps coverage
        cities_with_maps = len(self.city_data)
        total_cities = len([c.strip() for c in cities_text.split("\n") if c.strip()]) if cities_text else 0
        
        if total_cities > 0 and cities_with_maps == 0:
            result.add_warning("No Google Maps added - consider adding maps for local credibility")
        elif cities_with_maps < total_cities:
            result.add_warning(f"Google Maps added for {cities_with_maps}/{total_cities} cities")

        return result

    def validate_and_show_results(self):
        """Validate data and show results to user"""
        result = self.validate_data()

        if result.is_valid:
            msg = "✅ Cities configuration is valid!\n\n"
            cities_count = len([c.strip() for c in self.city_inputs["target_cities"].toPlainText().split("\n") if c.strip()])
            maps_count = len(self.city_data)
            seo_fields_count = sum(1 for widget in self.seo_inputs.values() if widget.toPlainText().strip())
            
            msg += f"• Target cities: {cities_count}\n"
            msg += f"• Cities with maps: {maps_count}\n"
            msg += f"• SEO fields completed: {seo_fields_count}/{len(self.seo_inputs)}\n"

            if result.warnings:
                msg += f"• Warnings: {len(result.warnings)}\n"
                detailed_msg = msg + "\n" + "\n".join([f"⚠️ {w}" for w in result.warnings])
                msgbox = QMessageBox(self)
                msgbox.setWindowTitle("Cities Validation Results")
                msgbox.setText(msg)
                msgbox.setDetailedText(detailed_msg)
                # Resize for better visibility in full-screen mode
                msgbox.resize(600, 400)
                msgbox.exec()
            else:
                msgbox = QMessageBox(self)
                msgbox.setWindowTitle("Cities Validation Success")
                msgbox.setText(msg)
                msgbox.setIcon(QMessageBox.Icon.Information)
                # Resize for better visibility in full-screen mode
                msgbox.resize(500, 300)
                msgbox.exec()
        else:
            msg = f"❌ Cities validation failed!\n\n"
            msg += f"• Errors: {len(result.errors)}\n"

            if result.warnings:
                msg += f"• Warnings: {len(result.warnings)}\n"

            # Show detailed errors and warnings
            details = []
            details.extend([f"❌ {e}" for e in result.errors])
            details.extend([f"⚠️ {w}" for w in result.warnings])

            detailed_msg = msg + "\n" + "\n".join(details)
            msgbox = QMessageBox(self)
            msgbox.setWindowTitle("Cities Validation Results")
            msgbox.setText(msg)
            msgbox.setDetailedText(detailed_msg)
            msgbox.setIcon(QMessageBox.Icon.Critical)
            # Resize for better visibility in full-screen mode
            msgbox.resize(600, 400)
            msgbox.exec()

    def get_config_data(self) -> Dict[str, Any]:
        """Get cities configuration data"""
        # Target cities
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

        return {
            "target_cities": target_cities,
            "seo_content": seo_content,
            "google_maps": google_maps,
        }

    def set_config_data(self, data: Dict[str, Any]):
        """Set cities configuration data"""
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

        # Clear any existing errors
        for field_name in self.error_labels:
            self._hide_field_error(field_name)

        # Emit data loaded signal
        self.data_loaded.emit()

    def clear_data(self):
        """Clear all cities data"""
        # Clear target cities
        self.city_inputs["target_cities"].clear()

        # Clear SEO content
        for widget in self.seo_inputs.values():
            widget.clear()

        # Clear Google Maps data
        self.city_data.clear()
        self._refresh_city_list()
        self._update_city_selector()

        # Clear errors
        for field_name in self.error_labels:
            self._hide_field_error(field_name)

        self.has_changes = False

    def _emit_config_changed(self):
        """Helper method to emit config changed signal"""
        self.has_changes = True
        # Call parent's implementation for proper signal handling
        # Auto-save is disabled at the main window level for Cities tab
        super()._emit_config_changed()