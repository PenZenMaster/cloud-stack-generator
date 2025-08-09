"""
Refactored City Embed Dialog for SEO Authority Website Generator
Enhanced with validation and better user experience

Version: 2.0.0
Date: 2025-08-09
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
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
import re


class CityEmbedDialog(QDialog):
    """Dialog for adding cities with Google Maps embed codes"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add City with Google Maps Embed")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout()

        # City information group
        city_group = QGroupBox("City Information")
        city_layout = QVBoxLayout()

        # City name
        city_layout.addWidget(QLabel("City Name:"))
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("e.g., Detroit")
        self.city_input.setFont(QFont("Arial", 10))
        city_layout.addWidget(self.city_input)

        # State
        city_layout.addWidget(QLabel("State (2-letter abbreviation):"))
        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText("e.g., MI")
        self.state_input.setFont(QFont("Arial", 10))
        self.state_input.setMaxLength(2)
        city_layout.addWidget(self.state_input)

        city_group.setLayout(city_layout)
        layout.addWidget(city_group)

        # Google Maps embed group
        maps_group = QGroupBox("Google Maps Embed")
        maps_layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "1. Go to Google Maps\n"
            "2. Search for your business location\n"
            "3. Click 'Share' → 'Embed a map'\n"
            "4. Copy the entire <iframe> code and paste below:"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic;")
        maps_layout.addWidget(instructions)

        # Embed code input
        maps_layout.addWidget(QLabel("Google Maps Embed Code:"))
        self.embed_input = QTextEdit()
        self.embed_input.setPlaceholderText(
            '<iframe src="https://www.google.com/maps/embed?pb=..." '
            'width="600" height="450" style="border:0;" allowfullscreen="" '
            'loading="lazy" referrerpolicy="no-referrer-when-downgrade">'
            "</iframe>"
        )
        self.embed_input.setFont(QFont("Consolas", 9))
        self.embed_input.setFixedHeight(120)
        maps_layout.addWidget(self.embed_input)

        # Auto-validate checkbox
        self.auto_validate_check = QCheckBox("Auto-validate embed code")
        self.auto_validate_check.setChecked(True)
        maps_layout.addWidget(self.auto_validate_check)

        maps_group.setLayout(maps_layout)
        layout.addWidget(maps_group)

        # Validation status
        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.validate_button = QPushButton("Validate Embed Code")
        self.validate_button.clicked.connect(self.validate_embed_code)
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

        # Connect validation on text change
        self.embed_input.textChanged.connect(self.on_embed_text_changed)
        self.city_input.textChanged.connect(self.update_validation_status)
        self.state_input.textChanged.connect(self.update_validation_status)

    def on_embed_text_changed(self):
        """Handle embed code text changes"""
        if self.auto_validate_check.isChecked():
            self.validate_embed_code(show_message=False)

    def validate_embed_code(self, show_message=True):
        """Validate the Google Maps embed code"""
        embed_code = self.embed_input.toPlainText().strip()

        if not embed_code:
            self.set_status("⚠️ No embed code provided", "orange")
            return False

        # Check for iframe tag
        if not embed_code.startswith("<iframe") or not embed_code.endswith("</iframe>"):
            self.set_status(
                "❌ Invalid format: Must be complete <iframe>...</iframe> tag", "red"
            )
            if show_message:
                QMessageBox.warning(
                    self,
                    "Invalid Format",
                    "Please paste the complete <iframe> embed code from Google Maps.",
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
                    "Cannot find the source URL in the embed code.",
                )
            return False

        url = url_match.group(1)

        # Check for required Google Maps parameters
        if "pb=" not in url and "q=" not in url:
            self.set_status("⚠️ Embed code may not contain location data", "orange")
            if show_message:
                QMessageBox.information(
                    self,
                    "Warning",
                    "The embed code may not contain specific location data. "
                    "Please ensure you've searched for a specific location in Google Maps.",
                )
            return True

        self.set_status
