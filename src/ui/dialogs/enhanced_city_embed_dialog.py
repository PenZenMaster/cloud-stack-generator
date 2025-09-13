"""
Filename: enhanced_city_embed_dialog.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\dialogs\\enhanced_city_embed_dialog.py
Description: Enhanced City Embed Dialog with Google Maps API Integration
Supports both manual embed codes and automatic API-based generation

Version: 1.0.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

from PyQt6.QtWidgets import (
    QDialog,
    QLabel,
    QLineEdit,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QMessageBox,
    QGroupBox,
    QCheckBox,
    QTabWidget,
    QWidget,
    QComboBox,
    QSpinBox,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import pyqtSignal
import re
from typing import Optional, Dict, Any

try:
    from ...core.utils.google_maps_api import GoogleMapsAPI
except ImportError:
    GoogleMapsAPI = None


class EnhancedCityEmbedDialog(QDialog):
    """Enhanced dialog for adding cities with Google Maps integration"""
    
    # Signal emitted when API key is needed
    api_key_required = pyqtSignal(str)  # Signal with message

    def __init__(self, parent=None, api_key: Optional[str] = None):
        super().__init__(parent)
        self.api_key = api_key
        self.google_maps_api = None
        
        if self.api_key and GoogleMapsAPI:
            try:
                self.google_maps_api = GoogleMapsAPI(self.api_key)
            except ValueError:
                self.google_maps_api = None
        
        self.setWindowTitle("Add City with Google Maps")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface with tabs for different input methods"""
        layout = QVBoxLayout()

        # City information (common to both tabs)
        city_group = QGroupBox("City Information")
        city_layout = QVBoxLayout()

        city_layout.addWidget(QLabel("Location Name:"))
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("e.g., Chicago, Detroit, Evanston Illinois")
        self.city_input.setFont(QFont("Arial", 10))
        city_layout.addWidget(self.city_input)

        city_group.setLayout(city_layout)
        layout.addWidget(city_group)

        # Tab widget for different input methods
        self.tab_widget = QTabWidget()
        
        # API Generation tab
        if self.google_maps_api and GoogleMapsAPI:
            self.api_tab = self._create_api_tab()
            self.tab_widget.addTab(self.api_tab, "🚀 API Generation")
            
        # Manual Embed tab
        self.manual_tab = self._create_manual_tab()
        self.tab_widget.addTab(self.manual_tab, "✏️ Manual Embed")
        
        layout.addWidget(self.tab_widget)

        # Status display
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()

        if self.google_maps_api:
            self.generate_button = QPushButton("🚀 Generate with API")
            self.generate_button.clicked.connect(self.generate_api_embed)
            button_layout.addWidget(self.generate_button)

        self.validate_button = QPushButton("✅ Validate Embed")
        self.validate_button.clicked.connect(self.validate_current_embed)
        button_layout.addWidget(self.validate_button)

        button_layout.addStretch()

        self.ok_button = QPushButton("Add City")
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.ok_button.setDefault(True)
        button_layout.addWidget(self.ok_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # Connect validation
        self.city_input.textChanged.connect(self.update_validation_status)

    def _create_api_tab(self) -> QWidget:
        """Create the API generation tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # API Status
        api_status = QLabel("✅ Google Maps API Connected" if self.google_maps_api else "❌ Google Maps API Not Available")
        api_status.setStyleSheet(f"color: {'green' if self.google_maps_api else 'red'}; font-weight: bold;")
        layout.addWidget(api_status)

        # API Options
        options_group = QGroupBox("Map Options")
        options_layout = QVBoxLayout()

        # Map type
        options_layout.addWidget(QLabel("Map Type:"))
        self.map_type_combo = QComboBox()
        self.map_type_combo.addItems(["roadmap", "satellite", "hybrid", "terrain"])
        options_layout.addWidget(self.map_type_combo)

        # Zoom level
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom Level:"))
        self.zoom_spin = QSpinBox()
        self.zoom_spin.setRange(1, 21)
        self.zoom_spin.setValue(15)
        zoom_layout.addWidget(self.zoom_spin)
        zoom_layout.addStretch()
        options_layout.addLayout(zoom_layout)

        # Embed dimensions
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Width:"))
        self.width_input = QLineEdit("100%")
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(QLabel("Height:"))
        self.height_input = QLineEdit("400")
        size_layout.addWidget(self.height_input)
        options_layout.addLayout(size_layout)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        # Generated embed preview
        preview_group = QGroupBox("Generated Embed Code")
        preview_layout = QVBoxLayout()

        self.api_embed_preview = QTextEdit()
        self.api_embed_preview.setFont(QFont("Consolas", 9))
        self.api_embed_preview.setFixedHeight(120)
        self.api_embed_preview.setReadOnly(True)
        self.api_embed_preview.setPlaceholderText("Generated embed code will appear here...")
        preview_layout.addWidget(self.api_embed_preview)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        layout.addStretch()
        tab.setLayout(layout)
        return tab

    def _create_manual_tab(self) -> QWidget:
        """Create the manual embed tab"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "1. Go to Google Maps\n"
            "2. Search for your location\n" 
            "3. Click 'Share' → 'Embed a map'\n"
            "4. Copy the entire <iframe> code and paste below:"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(instructions)

        # Manual embed input
        manual_group = QGroupBox("Manual Embed Code")
        manual_layout = QVBoxLayout()

        self.manual_embed_input = QTextEdit()
        self.manual_embed_input.setPlaceholderText(
            '<iframe src="https://www.google.com/maps/embed?pb=..." '
            'width="600" height="450" style="border:0;" allowfullscreen="" '
            'loading="lazy" referrerpolicy="no-referrer-when-downgrade">'
            "</iframe>"
        )
        self.manual_embed_input.setFont(QFont("Consolas", 9))
        self.manual_embed_input.setFixedHeight(120)
        manual_layout.addWidget(self.manual_embed_input)

        # Auto-validate checkbox
        self.auto_validate_check = QCheckBox("Auto-validate embed code")
        self.auto_validate_check.setChecked(True)
        manual_layout.addWidget(self.auto_validate_check)

        manual_group.setLayout(manual_layout)
        layout.addWidget(manual_group)

        layout.addStretch()
        tab.setLayout(layout)

        # Connect manual embed validation
        self.manual_embed_input.textChanged.connect(self.on_manual_embed_changed)
        
        return tab

    def on_manual_embed_changed(self):
        """Handle manual embed code changes"""
        if self.auto_validate_check.isChecked():
            self.validate_manual_embed(show_message=False)

    def generate_api_embed(self):
        """Generate embed code using Google Maps API"""
        if not self.google_maps_api:
            self.set_status("❌ Google Maps API not available", "red")
            self.api_key_required.emit("Google Maps API key required for automatic generation")
            return

        location = self.city_input.text().strip()
        if not location:
            self.set_status("⚠️ Please enter a location name first", "orange")
            self.city_input.setFocus()
            return

        try:
            # Get options
            map_type = self.map_type_combo.currentText()
            zoom = self.zoom_spin.value()
            width = self.width_input.text().strip() or "100%"
            height = self.height_input.text().strip() or "400"

            # Generate embed
            embed_data = self.google_maps_api.create_place_embed(
                location=location,
                width=width,
                height=height,
                maptype=map_type,
                zoom=zoom
            )

            # Update preview
            self.api_embed_preview.setPlainText(embed_data["iframe"])
            self.set_status(f"✅ Generated embed for {location}", "green")

        except Exception as e:
            self.set_status(f"❌ Generation failed: {str(e)}", "red")

    def validate_current_embed(self):
        """Validate the currently active embed code"""
        if self.tab_widget.currentIndex() == 0 and self.google_maps_api:
            # API tab
            embed_code = self.api_embed_preview.toPlainText().strip()
            if not embed_code:
                self.set_status("⚠️ No generated embed code", "orange")
                return False
            return self.validate_embed_code(embed_code, show_message=True)
        else:
            # Manual tab
            return self.validate_manual_embed(show_message=True)

    def validate_manual_embed(self, show_message=True) -> bool:
        """Validate manual embed code"""
        embed_code = self.manual_embed_input.toPlainText().strip()
        return self.validate_embed_code(embed_code, show_message)

    def validate_embed_code(self, embed_code: str, show_message=True) -> bool:
        """Validate Google Maps embed code"""
        if not embed_code:
            self.set_status("⚠️ No embed code provided", "orange")
            return False

        # Check for iframe tag
        if not embed_code.startswith("<iframe") or not embed_code.endswith("</iframe>"):
            self.set_status("❌ Invalid format: Must be complete <iframe>...</iframe> tag", "red")
            if show_message:
                QMessageBox.warning(
                    self,
                    "Invalid Format", 
                    "Please paste the complete <iframe> embed code."
                )
            return False

        # Check for Google Maps URL
        if "maps.google.com" not in embed_code and "google.com/maps" not in embed_code:
            self.set_status("❌ Invalid source: Must be from Google Maps", "red")
            if show_message:
                QMessageBox.warning(
                    self, "Invalid Source", "The embed code must be from Google Maps."
                )
            return False

        # Extract and validate URL
        url_match = re.search(r'src=["\']([^"\']*)["\']', embed_code)
        if not url_match:
            self.set_status("❌ Cannot find src URL in embed code", "red")
            if show_message:
                QMessageBox.warning(
                    self,
                    "Invalid Code",
                    "Cannot find the source URL in the embed code."
                )
            return False

        self.set_status("✅ Valid Google Maps embed code", "green")
        return True

    def set_status(self, message: str, color: str):
        """Set the status message with color"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def update_validation_status(self):
        """Update validation status based on all inputs"""
        location = self.city_input.text().strip()
        if not location:
            self.set_status("⚠️ Location name required", "orange")
            return False

        # Don't auto-validate embed unless we have a location
        return True

    def validate_and_accept(self):
        """Validate all inputs before accepting"""
        location = self.city_input.text().strip()

        # Validate location
        if not location:
            QMessageBox.warning(
                self, "Missing Information", "Please enter a location name."
            )
            self.city_input.setFocus()
            return

        # Get embed code based on active tab
        embed_code = ""
        if self.tab_widget.currentIndex() == 0 and self.google_maps_api:
            # API tab
            embed_code = self.api_embed_preview.toPlainText().strip()
            if not embed_code:
                QMessageBox.warning(
                    self,
                    "No Generated Embed",
                    "Please generate an embed code using the API or switch to manual entry."
                )
                return
        else:
            # Manual tab
            embed_code = self.manual_embed_input.toPlainText().strip()

        # Validate embed code
        if not embed_code:
            QMessageBox.warning(
                self,
                "Missing Embed Code",
                "Please provide a Google Maps embed code."
            )
            return

        if not self.validate_embed_code(embed_code, show_message=True):
            return

        # All validation passed
        self.accept()

    def get_data(self) -> Dict[str, Any]:
        """Get the entered data"""
        # Determine which embed code to use
        embed_code = ""
        generation_method = "manual"
        
        if self.tab_widget.currentIndex() == 0 and self.google_maps_api:
            # API tab
            embed_code = self.api_embed_preview.toPlainText().strip()
            generation_method = "api"
        else:
            # Manual tab 
            embed_code = self.manual_embed_input.toPlainText().strip()
            generation_method = "manual"

        return {
            "location": self.city_input.text().strip(),
            "embed_code": embed_code,
            "generation_method": generation_method,
            "api_options": {
                "map_type": self.map_type_combo.currentText() if self.google_maps_api else None,
                "zoom": self.zoom_spin.value() if self.google_maps_api else None,
                "width": self.width_input.text().strip() if self.google_maps_api else None,
                "height": self.height_input.text().strip() if self.google_maps_api else None,
            } if self.google_maps_api else None
        }

    def set_data(self, data: Dict[str, Any]):
        """Set the dialog data (for editing existing entries)"""
        # Support both old format and new format
        location = data.get("location", "") or data.get("city", "")
        self.city_input.setText(location)
        
        embed_code = data.get("embed_code", "")
        generation_method = data.get("generation_method", "manual")
        
        # Set embed code in appropriate tab
        if generation_method == "api" and self.google_maps_api:
            self.tab_widget.setCurrentIndex(0)  # API tab
            self.api_embed_preview.setPlainText(embed_code)
            
            # Set API options if available
            api_options = data.get("api_options", {})
            if api_options:
                if api_options.get("map_type"):
                    index = self.map_type_combo.findText(api_options["map_type"])
                    if index >= 0:
                        self.map_type_combo.setCurrentIndex(index)
                if api_options.get("zoom"):
                    self.zoom_spin.setValue(int(api_options["zoom"]))
                if api_options.get("width"):
                    self.width_input.setText(api_options["width"])
                if api_options.get("height"):
                    self.height_input.setText(api_options["height"])
        else:
            # Default to manual tab
            manual_tab_index = 1 if self.google_maps_api else 0
            self.tab_widget.setCurrentIndex(manual_tab_index)
            self.manual_embed_input.setPlainText(embed_code)

    def clear_inputs(self):
        """Clear all input fields"""
        self.city_input.clear()
        self.manual_embed_input.clear()
        if self.google_maps_api:
            self.api_embed_preview.clear()
        self.status_label.clear()

    def set_api_key(self, api_key: str):
        """Set Google Maps API key and reinitialize"""
        self.api_key = api_key
        if GoogleMapsAPI:
            try:
                self.google_maps_api = GoogleMapsAPI(api_key)
                # Refresh UI if needed
                if hasattr(self, 'tab_widget'):
                    # Add API tab if it doesn't exist
                    if self.tab_widget.count() == 1:  # Only manual tab
                        self.api_tab = self._create_api_tab()
                        self.tab_widget.insertTab(0, self.api_tab, "🚀 API Generation")
            except ValueError:
                self.google_maps_api = None