"""
API Keys Tab - Secure management of API keys and integrations
Stores sensitive keys outside of main configuration files
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QTextEdit,
    QMessageBox,
    QFrame,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from typing import Dict, Any
import json
from pathlib import Path

from .base_tab import BaseTab, ValidationResult
from ..layouts import ScalableLayout, ResponsiveSection, StandardFormLayout


class APIKeysTab(BaseTab):
    """Tab for managing API keys and external integrations"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the API Keys tab UI"""
        # Check if layout already exists to avoid conflicts
        if self.layout() is not None:
            return
            
        # Use simple QVBoxLayout to avoid conflicts
        layout = QVBoxLayout()
        
        # Title section with description
        title_label = QLabel("API Keys & Integrations")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        
        description_label = QLabel(
            "Manage API keys for external services. Keys are stored securely "
            "and excluded from version control."
        )
        description_label.setStyleSheet("color: #666; font-style: italic; margin-bottom: 20px;")
        description_label.setWordWrap(True)
        
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        
        # Google Maps section
        maps_section = self.create_maps_section()
        layout.addWidget(maps_section)
        
        # Future integrations placeholder
        future_section = self.create_future_integrations_section()
        layout.addWidget(future_section)
        
        # Actions section
        actions_section = self.create_actions_section()
        layout.addWidget(actions_section)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def create_maps_section(self) -> QGroupBox:
        """Create Google Maps API section"""
        group = QGroupBox("Google Maps Integration")
        layout = QVBoxLayout()
        
        # API Key field with show/hide button
        api_key_layout = QHBoxLayout()
        
        # API Key input
        self.maps_api_key = QLineEdit()
        self.maps_api_key.setPlaceholderText("Enter your Google Maps API key")
        self.maps_api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.maps_api_key.textChanged.connect(self.on_api_key_changed)
        
        # Show/Hide button
        self.toggle_visibility_btn = QPushButton("👁️")
        self.toggle_visibility_btn.clicked.connect(self.toggle_api_key_visibility)
        self.toggle_visibility_btn.setMaximumWidth(30)
        self.toggle_visibility_btn.setToolTip("Show/Hide API Key")
        
        api_key_layout.addWidget(QLabel("API Key:"))
        api_key_layout.addWidget(self.maps_api_key)
        api_key_layout.addWidget(self.toggle_visibility_btn)
        
        layout.addLayout(api_key_layout)
        
        # Instructions
        instructions_label = QLabel(
            "Get your API key from Google Cloud Console > APIs & Services > Credentials. "
            "Enable the Maps JavaScript API and Places API for full functionality."
        )
        instructions_label.setWordWrap(True)
        instructions_label.setStyleSheet("color: #666; font-style: italic; margin-top: 10px;")
        layout.addWidget(instructions_label)
        
        group.setLayout(layout)
        return group
        
    def create_future_integrations_section(self) -> QGroupBox:
        """Create section for future API integrations"""
        group = QGroupBox("Future Integrations")
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "Additional API integrations will be added here:\n"
            "• Google Analytics\n"
            "• Social Media APIs\n"
            "• Email Marketing Services\n"
            "• SEO Tools"
        )
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)
        
        group.setLayout(layout)
        return group
        
    def create_actions_section(self) -> QFrame:
        """Create actions section"""
        frame = QFrame()
        layout = QHBoxLayout()
        
        self.save_btn = QPushButton("Save API Keys")
        self.save_btn.clicked.connect(self.save_api_keys)
        
        self.test_btn = QPushButton("Test Google Maps API")
        self.test_btn.clicked.connect(self.test_maps_api)
        
        layout.addWidget(self.save_btn)
        layout.addWidget(self.test_btn)
        layout.addStretch()
        
        frame.setLayout(layout)
        return frame
        
    def toggle_api_key_visibility(self):
        """Toggle API key visibility"""
        if self.maps_api_key.echoMode() == QLineEdit.EchoMode.Password:
            self.maps_api_key.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_visibility_btn.setText("🙈")
        else:
            self.maps_api_key.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_visibility_btn.setText("👁️")
            
    def on_api_key_changed(self):
        """Handle API key text changes"""
        # This makes the field more responsive and ensures text is properly tracked
        pass
            
    def save_api_keys(self):
        """Save API keys using main window's app-wide functionality"""
        try:
            api_key_value = self.maps_api_key.text().strip()
            
            # Validate API key before saving
            if not api_key_value:
                QMessageBox.warning(
                    self,
                    "No API Key",
                    "Please enter a Google Maps API key before saving."
                )
                return
            
            # Get reference to main window and save via app-wide method
            main_window = self.window()
            if hasattr(main_window, 'save_app_api_keys'):
                api_keys = {"google_maps_api_key": api_key_value}
                main_window.save_app_api_keys(api_keys)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"API key saved successfully!\n\nKey length: {len(api_key_value)} characters"
                )
                
                # Do NOT emit config_changed signal - API keys are app-wide, not client config
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    "Could not access main window for saving API keys"
                )
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save API keys: {str(e)}"
            )
            
    def test_maps_api(self):
        """Test Google Maps API key"""
        api_key = self.maps_api_key.text().strip()
        
        if not api_key:
            QMessageBox.warning(
                self,
                "No API Key Found",
                "No Google Maps API key found.\n\n"
                "Please:\n"
                "1. Enter your API key in the field above\n"
                "2. Click 'Save API Keys'\n"
                "3. Then test the API key"
            )
            return
            
        # Basic validation
        if len(api_key) < 20:
            QMessageBox.warning(
                self,
                "Invalid API Key",
                f"The API key appears to be too short ({len(api_key)} characters).\n\n"
                "Google Maps API keys are typically 39 characters long."
            )
            return
            
        # TODO: Implement actual API test
        QMessageBox.information(
            self,
            "API Key Test Result",
            f"✅ API key format looks valid!\n\n"
            f"Key length: {len(api_key)} characters\n"
            f"Key preview: {api_key[:8]}...{api_key[-4:]}\n\n"
            "Note: Full API connectivity testing will be implemented in a future update."
        )
        
    def get_config_data(self) -> Dict[str, Any]:
        """Get current API keys configuration"""
        return {
            'google_maps_api_key': self.maps_api_key.text().strip()
        }
        
    def set_config_data(self, data: Dict[str, Any]):
        """Set API keys configuration"""
        api_key = data.get('google_maps_api_key', '')
        self.maps_api_key.setText(api_key)
        
    def get_required_fields(self) -> list:
        """Return list of required fields (none for API keys)"""
        return []
        
    def validate_data(self) -> ValidationResult:
        """Validate API keys data"""
        result = super().validate_data()
        
        # API keys are optional, so just validate format if provided
        api_key = self.maps_api_key.text().strip()
        if api_key and len(api_key) < 10:
            result.add_error(
                "Google Maps API key appears to be too short",
                "api_key"
            )
            
        return result