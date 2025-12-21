"""
Module/Script Name: Google Search Console Verification Dialog
Path: src/ui/dialogs/gsc_verification_dialog.py

Description:
UI dialog for Google Search Console verification workflow including
OAuth authentication, token retrieval, and site verification.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-12-20

Last Modified Date:
2025-12-20

Comments:
* v1.00 - Initial implementation with OAuth flow and token management
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTextEdit, QGroupBox, QMessageBox,
    QApplication, QCheckBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.integrations.google_search_console import GoogleSearchConsoleClient


class GSCVerificationDialog(QDialog):
    """
    Dialog for Google Search Console verification workflow

    Signals:
        meta_tag_generated: Emitted when meta tag is generated (name, content)
        verification_completed: Emitted when verification completes (site_url, success)
    """

    meta_tag_generated = pyqtSignal(str, str)  # (name, content)
    verification_completed = pyqtSignal(str, bool)  # (site_url, success)

    def __init__(self, initial_url: str = "", parent=None):
        """
        Initialize GSC verification dialog

        Args:
            initial_url: Initial site URL to pre-populate
            parent: Parent widget
        """
        super().__init__(parent)
        self.gsc_client = GoogleSearchConsoleClient()
        self.current_token = ""
        self.current_meta_tag = ""

        self.setWindowTitle("Google Search Console Verification")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)

        self.init_ui(initial_url)
        self.check_authentication_status()

    def init_ui(self, initial_url: str):
        """Initialize UI components"""
        layout = QVBoxLayout(self)

        # Site URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Site URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com/")
        if initial_url:
            self.url_input.setText(initial_url)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Verification method
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Verification Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["META", "FILE", "DNS_TXT"])
        self.method_combo.setCurrentText("META")
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch()
        layout.addLayout(method_layout)

        # Status panel
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()

        self.auth_status = QCheckBox("Authenticated with Google")
        self.auth_status.setEnabled(False)
        status_layout.addWidget(self.auth_status)

        self.token_status = QCheckBox("Verification token requested")
        self.token_status.setEnabled(False)
        status_layout.addWidget(self.token_status)

        self.added_status = QCheckBox("Token added to deployment")
        self.added_status.setEnabled(False)
        status_layout.addWidget(self.added_status)

        self.verified_status = QCheckBox("Site verified")
        self.verified_status.setEnabled(False)
        status_layout.addWidget(self.verified_status)

        status_group.setLayout(status_layout)
        layout.addWidget(status_group)

        # Generated meta tag display
        layout.addWidget(QLabel("Generated Meta Tag:"))
        self.meta_tag_display = QTextEdit()
        self.meta_tag_display.setReadOnly(True)
        self.meta_tag_display.setMaximumHeight(80)
        font = QFont("Consolas", 9)
        self.meta_tag_display.setFont(font)
        layout.addWidget(self.meta_tag_display)

        # Copy button
        copy_layout = QHBoxLayout()
        self.copy_button = QPushButton("Copy to Clipboard")
        self.copy_button.clicked.connect(self.copy_to_clipboard)
        self.copy_button.setEnabled(False)
        copy_layout.addWidget(self.copy_button)
        copy_layout.addStretch()
        layout.addLayout(copy_layout)

        # Verification code display
        code_layout = QHBoxLayout()
        code_layout.addWidget(QLabel("Verification Code:"))
        self.code_display = QLineEdit()
        self.code_display.setReadOnly(True)
        code_layout.addWidget(self.code_display)
        layout.addLayout(code_layout)

        # Warning panel (initially hidden)
        self.warning_panel = QGroupBox("Warning")
        warning_layout = QVBoxLayout()
        self.warning_text = QLabel()
        self.warning_text.setWordWrap(True)
        self.warning_text.setStyleSheet("color: #d97706;")
        warning_layout.addWidget(self.warning_text)
        self.warning_panel.setLayout(warning_layout)
        self.warning_panel.setVisible(False)
        layout.addWidget(self.warning_panel)

        # Action buttons (top row)
        action_layout = QHBoxLayout()
        self.auth_button = QPushButton("Authenticate")
        self.auth_button.clicked.connect(self.authenticate)
        action_layout.addWidget(self.auth_button)

        self.get_token_button = QPushButton("Get Token")
        self.get_token_button.clicked.connect(self.get_token)
        self.get_token_button.setEnabled(False)
        action_layout.addWidget(self.get_token_button)

        self.verify_button = QPushButton("Verify Site")
        self.verify_button.clicked.connect(self.verify_site)
        self.verify_button.setEnabled(False)
        action_layout.addWidget(self.verify_button)

        action_layout.addStretch()
        layout.addLayout(action_layout)

        # Dialog buttons (bottom row)
        dialog_layout = QHBoxLayout()
        dialog_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        dialog_layout.addWidget(self.cancel_button)

        self.add_button = QPushButton("Add to Deployment")
        self.add_button.clicked.connect(self.add_to_deployment)
        self.add_button.setEnabled(False)
        dialog_layout.addWidget(self.add_button)

        layout.addLayout(dialog_layout)

    def check_authentication_status(self):
        """Check if already authenticated"""
        if self.gsc_client.is_authenticated():
            self.auth_status.setChecked(True)
            self.auth_button.setText("Re-authenticate")
            self.get_token_button.setEnabled(True)
        else:
            # Check for existing token file
            if self.gsc_client.token_file.exists():
                success, error = self.gsc_client.authenticate()
                if success:
                    self.auth_status.setChecked(True)
                    self.auth_button.setText("Re-authenticate")
                    self.get_token_button.setEnabled(True)

    def authenticate(self):
        """Run OAuth authentication flow"""
        # Check for credentials file
        if not os.path.exists(self.gsc_client.credentials_file):
            QMessageBox.warning(
                self,
                "Credentials Not Found",
                f"Google OAuth credentials file not found: {self.gsc_client.credentials_file}\n\n"
                "To get credentials:\n"
                "1. Go to console.cloud.google.com\n"
                "2. Create or select a project\n"
                "3. Enable 'Site Verification API'\n"
                "4. Create OAuth 2.0 Client ID (Desktop app)\n"
                "5. Download credentials.json\n"
                "6. Place in project root directory"
            )
            return

        # Show progress message
        QMessageBox.information(
            self,
            "Authentication",
            "Your browser will open for Google authentication.\n\n"
            "Please sign in and grant permissions."
        )

        # Run authentication
        success, error = self.gsc_client.authenticate()

        if success:
            self.auth_status.setChecked(True)
            self.auth_button.setText("Re-authenticate")
            self.get_token_button.setEnabled(True)
            QMessageBox.information(
                self,
                "Success",
                "Successfully authenticated with Google!"
            )
        else:
            QMessageBox.critical(
                self,
                "Authentication Failed",
                f"Failed to authenticate:\n{error}"
            )

    def get_token(self):
        """Request verification token from Google"""
        site_url = self.url_input.text().strip()

        if not site_url:
            QMessageBox.warning(
                self,
                "Missing URL",
                "Please enter a site URL"
            )
            return

        # Get verification method
        method = self.method_combo.currentText()

        # Request token
        token, meta_tag, error = self.gsc_client.get_verification_token(
            site_url, method
        )

        if error:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to get verification token:\n{error}"
            )
            return

        # Store token and meta tag
        self.current_token = token
        self.current_meta_tag = meta_tag if meta_tag else token

        # Update UI
        if method == "META":
            self.meta_tag_display.setPlainText(meta_tag)
            self.code_display.setText(token)
        else:
            self.meta_tag_display.setPlainText(token)
            self.code_display.setText(token)

        self.token_status.setChecked(True)
        self.copy_button.setEnabled(True)
        self.add_button.setEnabled(True)
        self.verify_button.setEnabled(True)

        # Check for token reuse
        is_duplicate, duplicates = self.gsc_client.check_token_reuse(token)

        if is_duplicate:
            warning_msg = "This Google verification code is already used in:\n"
            for dup in duplicates:
                warning_msg += f"\n+ {dup}"
            warning_msg += "\n\nUsing the same verification code for multiple sites may "
            warning_msg += "cause verification issues with Google Search Console."

            self.warning_text.setText(warning_msg)
            self.warning_panel.setVisible(True)
        else:
            self.warning_panel.setVisible(False)

    def verify_site(self):
        """Attempt to verify site ownership"""
        site_url = self.url_input.text().strip()

        if not site_url:
            QMessageBox.warning(
                self,
                "Missing URL",
                "Please enter a site URL"
            )
            return

        method = self.method_combo.currentText()

        # Confirm verification
        reply = QMessageBox.question(
            self,
            "Verify Site",
            f"Attempt to verify {site_url}?\n\n"
            "Make sure the verification token is correctly placed on your site.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Attempt verification
        success, error = self.gsc_client.verify_site(site_url, method)

        if success:
            self.verified_status.setChecked(True)
            self.verification_completed.emit(site_url, True)
            QMessageBox.information(
                self,
                "Success",
                f"Successfully verified {site_url}!"
            )
        else:
            QMessageBox.warning(
                self,
                "Verification Failed",
                f"Failed to verify site:\n{error}\n\n"
                "Make sure the verification token is correctly placed on your site."
            )
            self.verification_completed.emit(site_url, False)

    def copy_to_clipboard(self):
        """Copy meta tag to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.current_meta_tag)

        QMessageBox.information(
            self,
            "Copied",
            "Meta tag copied to clipboard!"
        )

    def add_to_deployment(self):
        """Emit signal to add meta tag to deployment"""
        if not self.current_token:
            QMessageBox.warning(
                self,
                "No Token",
                "Please get a verification token first"
            )
            return

        # Emit signal with name and content
        self.meta_tag_generated.emit("google-site-verification", self.current_token)
        self.added_status.setChecked(True)

        QMessageBox.information(
            self,
            "Added",
            "Meta tag has been added to the deployment meta tags table."
        )

        # Close dialog
        self.accept()
