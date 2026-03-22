"""
Module/Script Name: Cloud Deployment Tab
Path: src/ui/components/cloud_tab.py

Description:
Cloud deployment configuration tab implementing AWS integration with secure
credential management, bucket operations, and deployment modes.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-05

Last Modified Date:
2026-03-21

Version: v1.04

Comments:
* v1.04 - Comprehensive Test Connection: real S3 PUT/GET/DELETE, bucket state, CloudFront OAC check
* v1.03 - Added auto-populate GCS Project ID from service account JSON key file
* v1.02 - Fixed friendly name format (removed '+' separator, use spaces),
  Fixed deployment history persistence (unique timestamp-based deployment IDs)
* v1.01 - Added friendly name feature and deployment tracking
* v1.00 - Initial implementation following existing UI patterns and SOP workflow
"""

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QRadioButton,
    QButtonGroup,
    QTextEdit,
    QProgressBar,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QApplication,
    QCheckBox,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
import subprocess
import platform
from datetime import datetime
from src.core.utils.logger import get_logger

logger = get_logger(__name__)

from .base_tab import BaseTab
from .progress_widget import ProgressWidget
from ...core.aws.credentials import AWSCredentialsManager, AuthMethod
from ...core.aws.s3_manager import S3Manager, UploadProgress, UploadResult
from ...core.config.client_aws_config import ClientAWSConfig, get_client_aws_manager
from ...core.config.models import DeploymentConfig
from ...utils.error_logger import log_error_dialog
from ..dialogs.gsc_verification_dialog import GSCVerificationDialog


class AWSProfileDialog(QDialog):
    """Dialog for AWS profile management"""

    def __init__(self, parent=None, existing_profiles: List[str] = None):
        super().__init__(parent)
        self.existing_profiles = existing_profiles or []
        self.setup_ui()
        self.setWindowTitle("AWS Profile Setup")
        self.resize(400, 300)

    def setup_ui(self):
        """Setup profile dialog UI"""
        layout = QVBoxLayout()

        # Profile name
        profile_group = QGroupBox("Profile Information")
        profile_layout = QGridLayout()

        profile_layout.addWidget(QLabel("Profile Name:"), 0, 0)
        self.profile_name_input = QLineEdit()
        profile_layout.addWidget(self.profile_name_input, 0, 1)

        profile_layout.addWidget(QLabel("Description:"), 1, 0)
        self.description_input = QLineEdit()
        profile_layout.addWidget(self.description_input, 1, 1)

        profile_group.setLayout(profile_layout)
        layout.addWidget(profile_group)

        # Authentication method
        auth_group = QGroupBox("Authentication Method")
        auth_layout = QVBoxLayout()

        self.auth_button_group = QButtonGroup()
        self.sso_radio = QRadioButton("AWS SSO")
        self.access_keys_radio = QRadioButton("Access Keys (Recommended)")
        self.access_keys_radio.setChecked(True)

        self.auth_button_group.addButton(self.sso_radio, 0)
        self.auth_button_group.addButton(self.access_keys_radio, 1)

        auth_layout.addWidget(self.sso_radio)
        auth_layout.addWidget(self.access_keys_radio)

        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)

        # Configuration details
        self.config_group = QGroupBox("Configuration")
        self.config_layout = QGridLayout()

        # SSO fields (default visible)
        self.config_layout.addWidget(QLabel("SSO Start URL:"), 0, 0)
        self.sso_url_input = QLineEdit()
        self.sso_url_input.setPlaceholderText("https://d-xxxxxxxxxx.awsapps.com/start")
        self.config_layout.addWidget(self.sso_url_input, 0, 1)

        # Add help button for SSO URL
        help_button = QPushButton("?")
        help_button.setMaximumWidth(30)
        help_button.setToolTip("Click for SSO configuration help")
        help_button.clicked.connect(self.show_sso_help)
        self.config_layout.addWidget(help_button, 0, 2)

        self.config_layout.addWidget(QLabel("SSO Region:"), 1, 0)
        self.sso_region_combo = QComboBox()
        self.sso_region_combo.addItems(["us-east-1", "us-west-2", "eu-west-1"])
        self.config_layout.addWidget(self.sso_region_combo, 1, 1)

        self.config_layout.addWidget(QLabel("Default Region:"), 2, 0)
        self.region_combo = QComboBox()
        self.region_combo.addItems(
            ["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"]
        )
        self.config_layout.addWidget(self.region_combo, 2, 1)

        # Add Configure SSO button
        self.configure_sso_button = QPushButton("Configure SSO")
        self.configure_sso_button.setToolTip("Open terminal to configure AWS SSO")
        self.configure_sso_button.clicked.connect(self.configure_sso_cli)
        self.config_layout.addWidget(self.configure_sso_button, 3, 0, 1, 2)

        # Access Key fields (initially hidden)
        self.config_layout.addWidget(QLabel("Access Key ID:"), 4, 0)
        self.access_key_input = QLineEdit()
        self.access_key_input.setPlaceholderText("AKIA...")
        self.access_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.config_layout.addWidget(self.access_key_input, 4, 1)

        self.config_layout.addWidget(QLabel("Secret Access Key:"), 5, 0)
        self.secret_key_input = QLineEdit()
        self.secret_key_input.setPlaceholderText("Enter your secret access key")
        self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.config_layout.addWidget(self.secret_key_input, 5, 1)

        # Show/Hide password button for access keys
        self.show_keys_button = QPushButton("👁")
        self.show_keys_button.setMaximumWidth(30)
        self.show_keys_button.setToolTip("Show/Hide Access Keys")
        self.show_keys_button.clicked.connect(self.toggle_key_visibility)
        self.config_layout.addWidget(self.show_keys_button, 4, 2)

        self.config_group.setLayout(self.config_layout)
        layout.addWidget(self.config_group)

        # Connect signals
        self.auth_button_group.buttonClicked.connect(self.on_auth_method_changed)

        # Initialize UI state based on default selection
        self.on_auth_method_changed()

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def on_auth_method_changed(self):
        """Handle authentication method change"""
        is_sso = self.sso_radio.isChecked()

        # Show/hide SSO fields
        self.sso_url_input.setVisible(is_sso)
        self.sso_region_combo.setVisible(is_sso)
        self.configure_sso_button.setVisible(is_sso)

        # Show/hide Access Key fields
        self.access_key_input.setVisible(not is_sso)
        self.secret_key_input.setVisible(not is_sso)
        self.show_keys_button.setVisible(not is_sso)

        # Update labels visibility
        for i in range(self.config_layout.rowCount()):
            item = self.config_layout.itemAtPosition(i, 0)
            if item and item.widget():
                label = item.widget()
                if isinstance(label, QLabel):
                    text = label.text()
                    if "SSO" in text:
                        label.setVisible(is_sso)
                    elif "Access Key" in text or "Secret" in text:
                        label.setVisible(not is_sso)

    def toggle_key_visibility(self):
        """Toggle visibility of access keys"""
        if self.access_key_input.echoMode() == QLineEdit.EchoMode.Password:
            self.access_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_keys_button.setText("🙈")
        else:
            self.access_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.secret_key_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_keys_button.setText("👁")

    def configure_sso_cli(self):
        """Open terminal to configure AWS SSO"""
        profile_name = self.profile_name_input.text().strip()
        if not profile_name:
            QMessageBox.warning(
                self,
                "Profile Name Required",
                "Please enter a profile name before configuring SSO.",
            )
            return

        try:
            # Prepare AWS configure SSO command with profile name
            command = f"aws configure sso --profile {profile_name}"

            # Open terminal based on operating system
            system = platform.system().lower()

            if system == "windows":
                # Use Windows Terminal if available, otherwise use cmd
                try:
                    subprocess.run(["wt", "cmd", "/k", command], check=False)
                except FileNotFoundError:
                    # Fallback to cmd if Windows Terminal not available
                    subprocess.run(["cmd", "/k", command], check=False)
            elif system == "darwin":  # macOS
                # Use Terminal app
                applescript = f"""
                tell application "Terminal"
                    do script "{command}"
                    activate
                end tell
                """
                subprocess.run(["osascript", "-e", applescript], check=False)
            else:  # Linux and other Unix-like systems
                # Try common terminal emulators
                terminals = [
                    "gnome-terminal",
                    "konsole",
                    "xterm",
                    "x-terminal-emulator",
                ]
                for terminal in terminals:
                    try:
                        if terminal == "gnome-terminal":
                            subprocess.run(
                                [terminal, "--", "bash", "-c", f"{command}; exec bash"],
                                check=False,
                            )
                        elif terminal == "konsole":
                            subprocess.run(
                                [terminal, "-e", "bash", "-c", f"{command}; exec bash"],
                                check=False,
                            )
                        else:
                            subprocess.run(
                                [terminal, "-e", f"bash -c '{command}; exec bash'"],
                                check=False,
                            )
                        break
                    except FileNotFoundError:
                        continue
                else:
                    QMessageBox.warning(
                        self,
                        "Terminal Not Found",
                        "Could not find a suitable terminal application.",
                    )
                    return

            QMessageBox.information(
                self,
                "SSO Configuration",
                f"AWS SSO configuration started for profile '{profile_name}'. "
                f"Please complete the configuration in the terminal window that opened.",
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open terminal: {str(e)}")

    def show_sso_help(self):
        """Show detailed SSO configuration instructions"""
        help_text = """
        <h3>AWS SSO Configuration Help</h3>
        
        <p><strong>Before you begin:</strong></p>
        <ul>
            <li>Ensure you have the AWS CLI v2 installed</li>
            <li>Get your SSO start URL from your AWS administrator</li>
            <li>Know which AWS region your SSO is configured in</li>
        </ul>
        
        <p><strong>SSO Start URL Format:</strong></p>
        <p>Your SSO start URL should look like:<br>
        <code>https://d-xxxxxxxxxx.awsapps.com/start</code></p>
        
        <p><strong>Configuration Process:</strong></p>
        <ol>
            <li>Enter a profile name (e.g., "my-company-dev")</li>
            <li>Click "Configure SSO" to open a terminal</li>
            <li>In the terminal, follow the prompts:
                <ul>
                    <li>Enter your SSO start URL</li>
                    <li>Choose your SSO region</li>
                    <li>A browser will open for authentication</li>
                    <li>Complete the login in your browser</li>
                    <li>Select your AWS account and role</li>
                    <li>Choose your default region</li>
                    <li>Set default output format (usually "json")</li>
                </ul>
            </li>
            <li>Return to this dialog and fill in the configuration details</li>
            <li>Click OK to save the profile</li>
        </ol>
        
        <p><strong>Troubleshooting:</strong></p>
        <ul>
            <li>If AWS CLI is not found, install it from: https://aws.amazon.com/cli/</li>
            <li>Make sure you're using AWS CLI v2 (v1 doesn't support SSO)</li>
            <li>Check with your AWS administrator for the correct SSO URL</li>
        </ul>
        """

        msg = QMessageBox(self)
        msg.setWindowTitle("AWS SSO Configuration Help")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.resize(600, 400)
        msg.exec()

    def get_profile_data(self) -> Dict[str, Any]:
        """Get profile configuration data"""
        auth_method = (
            AuthMethod.SSO if self.sso_radio.isChecked() else AuthMethod.ACCESS_KEYS
        )

        data = {
            "name": self.profile_name_input.text().strip(),
            "description": self.description_input.text().strip(),
            "auth_method": auth_method,
            "region": self.region_combo.currentText(),
        }

        # Add method-specific data
        if auth_method == AuthMethod.SSO:
            data.update(
                {
                    "sso_start_url": self.sso_url_input.text().strip(),
                    "sso_region": self.sso_region_combo.currentText(),
                }
            )
        else:  # ACCESS_KEYS
            data.update(
                {
                    "access_key_id": self.access_key_input.text().strip(),
                    "secret_access_key": self.secret_key_input.text().strip(),
                }
            )

        return data


class BucketRefreshWorker(QThread):
    """Background worker for bucket list refresh operations"""

    progress_updated = pyqtSignal(str)
    finished = pyqtSignal(list, str)  # buckets, profile_name
    error_occurred = pyqtSignal(
        str, str, Exception
    )  # error_message, profile_name, exception

    def __init__(self, credentials_manager, s3_manager, profile_name: str):
        super().__init__()
        self.credentials_manager = credentials_manager
        self.s3_manager = s3_manager
        self.profile_name = profile_name

    def run(self):
        """Execute bucket refresh in background"""
        try:
            self.progress_updated.emit("Connecting to AWS...")

            # Get AWS session for the profile
            session = self.credentials_manager._get_session(self.profile_name)
            if not session:
                self.error_occurred.emit(
                    "Could not create AWS session for the selected profile",
                    self.profile_name,
                    None,
                )
                return

            self.progress_updated.emit("Retrieving bucket list...")

            # Set session and get buckets
            self.s3_manager.set_session(session)

            # Get all client buckets with SOP compliance indicators
            buckets = self.credentials_manager.list_client_buckets(
                self.profile_name, show_all=True
            )

            self.progress_updated.emit("Processing bucket list...")

            # Emit success with buckets
            self.finished.emit(buckets, self.profile_name)

        except Exception as e:
            error_message = f"Failed to retrieve bucket list: {str(e)}"
            self.error_occurred.emit(error_message, self.profile_name, e)


class ConnectionResultsDialog(QDialog):
    """Scrollable, color-coded AWS connection test results dialog."""

    _STATUS_COLORS = {
        "PASS": ("#1a7a1a", "#e8f5e9"),
        "FAIL": ("#b71c1c", "#ffebee"),
        "WARN": ("#e65100", "#fff3e0"),
        "SKIP": ("#555555", "#f5f5f5"),
        "INFO": ("#01579b", "#e3f2fd"),
    }

    def __init__(self, identity: dict, checks: list, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AWS Connection Test Results")
        self.setMinimumWidth(780)
        screen_h = (
            parent.screen().availableGeometry().height() if parent else 800
        )
        self.setMaximumHeight(int(screen_h * 0.85))

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        # Identity header
        account = identity.get("account", "Unknown")
        region = identity.get("region", "Unknown")
        profile = identity.get("profile", "Unknown")
        arn = identity.get("arn", "")

        header = QLabel(
            f"Account: {account}   |   Region: {region}   |   Profile: {profile}"
        )
        header_font = QFont()
        header_font.setBold(True)
        header.setFont(header_font)
        header.setStyleSheet("padding: 4px;")
        layout.addWidget(header)

        if arn:
            arn_label = QLabel(f"ARN: {arn}")
            arn_label.setStyleSheet("font-size: 10px; color: #555; padding: 2px;")
            layout.addWidget(arn_label)

        # Summary counts
        passed = sum(1 for c in checks if c["status"] == "PASS")
        failed = sum(1 for c in checks if c["status"] == "FAIL")
        warned = sum(1 for c in checks if c["status"] == "WARN")
        total = len(checks)

        parts = [f"{passed}/{total} checks passed"]
        if failed:
            parts.append(f"{failed} failed")
        if warned:
            parts.append(f"{warned} warning(s)")
        summary_color = "#b71c1c" if failed else "#e65100" if warned else "#1a7a1a"
        summary_label = QLabel("   ".join(parts))
        summary_font = QFont()
        summary_font.setBold(True)
        summary_label.setFont(summary_font)
        summary_label.setStyleSheet(f"color: {summary_color}; padding: 4px;")
        layout.addWidget(summary_label)

        # Results table
        table = QTableWidget(len(checks), 4)
        table.setHorizontalHeaderLabels(["Category", "Check", "Status", "Detail"])
        table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeMode.ResizeToContents
        )
        table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeMode.Stretch
        )
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.setWordWrap(True)

        for row, check in enumerate(checks):
            status = check.get("status", "INFO")
            fg, bg = self._STATUS_COLORS.get(status, ("#000000", "#ffffff"))
            for col, key in enumerate(["category", "check", "status", "detail"]):
                item = QTableWidgetItem(check.get(key, ""))
                item.setForeground(QColor(fg))
                item.setBackground(QColor(bg))
                if key == "status":
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    f = QFont()
                    f.setBold(True)
                    item.setFont(f)
                table.setItem(row, col, item)

        table.resizeRowsToContents()
        layout.addWidget(table)

        btn = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        btn.accepted.connect(self.accept)
        layout.addWidget(btn)


class ConnectionTestWorker(QThread):
    """Background worker for comprehensive AWS connection testing."""

    _TEST_KEY = "awg-connection-test.tmp"

    progress_updated = pyqtSignal(str)
    test_completed = pyqtSignal(bool, str, dict, list)  # success, msg, identity, checks
    error_occurred = pyqtSignal(str, Exception)

    def __init__(
        self,
        credentials_manager,
        profile_name: str,
        bucket_name: str = "",
        distribution_id: str = "",
    ):
        super().__init__()
        self.credentials_manager = credentials_manager
        self.profile_name = profile_name
        self.bucket_name = bucket_name
        self.distribution_id = distribution_id

    def run(self):
        """Execute comprehensive connection test in background."""
        checks: list = []
        identity: dict = {}
        try:
            self.progress_updated.emit("Validating AWS profile credentials...")
            is_valid, message, identity = self.credentials_manager.validate_profile(
                self.profile_name
            )
            identity["profile"] = self.profile_name

            if not is_valid:
                checks.append({
                    "category": "Identity",
                    "check": "STS GetCallerIdentity",
                    "status": "FAIL",
                    "detail": message,
                })
                self.test_completed.emit(False, message, identity, checks)
                return

            checks.append({
                "category": "Identity",
                "check": "STS GetCallerIdentity",
                "status": "PASS",
                "detail": (
                    f"Account {identity.get('account', '?')} | "
                    f"ARN: {identity.get('arn', 'unknown')}"
                ),
            })

            session = self.credentials_manager._get_session(self.profile_name)

            # S3 permissions
            self.progress_updated.emit("Testing S3 permissions...")
            checks.extend(self._test_s3_permissions(session))

            # Bucket state
            if self.bucket_name:
                self.progress_updated.emit(
                    f"Checking bucket state: {self.bucket_name}..."
                )
                checks.extend(
                    self._test_bucket_state(session, self.bucket_name, self.distribution_id)
                )
            else:
                checks.append({
                    "category": "Bucket State",
                    "check": "Bucket configured",
                    "status": "SKIP",
                    "detail": "No bucket selected in UI - configure bucket to enable these checks",
                })

            # CloudFront
            if self.distribution_id:
                self.progress_updated.emit(
                    f"Checking CloudFront distribution {self.distribution_id}..."
                )
                checks.extend(
                    self._test_cloudfront(session, self.distribution_id, self.bucket_name)
                )
            else:
                checks.append({
                    "category": "CloudFront",
                    "check": "Distribution configured",
                    "status": "SKIP",
                    "detail": "No distribution ID configured - skipping CloudFront checks",
                })

            self.progress_updated.emit("Connection test complete.")
            has_failures = any(c["status"] == "FAIL" for c in checks)
            self.test_completed.emit(not has_failures, message, identity, checks)

        except Exception as e:
            self.error_occurred.emit(f"Connection test failed: {str(e)}", e)

    # ------------------------------------------------------------------
    # S3 permission checks
    # ------------------------------------------------------------------

    def _test_s3_permissions(self, session) -> list:
        checks = []
        try:
            s3 = session.client("s3")
        except Exception as e:
            checks.append({
                "category": "S3 Permissions", "check": "Create S3 client",
                "status": "FAIL", "detail": str(e),
            })
            return checks

        # List Buckets
        try:
            resp = s3.list_buckets()
            count = len(resp.get("Buckets", []))
            checks.append({
                "category": "S3 Permissions", "check": "List Buckets",
                "status": "PASS", "detail": f"Found {count} bucket(s)",
            })
        except Exception as e:
            checks.append({
                "category": "S3 Permissions", "check": "List Buckets",
                "status": "FAIL", "detail": str(e)[:120],
            })

        if not self.bucket_name:
            return checks

        # List Objects
        try:
            resp = s3.list_objects_v2(Bucket=self.bucket_name, MaxKeys=1)
            checks.append({
                "category": "S3 Permissions", "check": "List Objects",
                "status": "PASS",
                "detail": f"Accessible - sampled {resp.get('KeyCount', 0)} object(s)",
            })
        except Exception as e:
            checks.append({
                "category": "S3 Permissions", "check": "List Objects",
                "status": "FAIL", "detail": str(e)[:120],
            })
            for name in ("Put Object", "Get Object", "Delete Object"):
                checks.append({
                    "category": "S3 Permissions", "check": name,
                    "status": "SKIP", "detail": "Skipped - List Objects failed",
                })
            return checks

        # Put Object
        put_ok = False
        try:
            s3.put_object(
                Bucket=self.bucket_name, Key=self._TEST_KEY,
                Body=b"awg-connection-test", ContentType="text/plain",
            )
            checks.append({
                "category": "S3 Permissions", "check": "Put Object",
                "status": "PASS", "detail": f"Wrote {self._TEST_KEY}",
            })
            put_ok = True
        except Exception as e:
            checks.append({
                "category": "S3 Permissions", "check": "Put Object",
                "status": "FAIL", "detail": str(e)[:120],
            })
            for name in ("Get Object", "Delete Object"):
                checks.append({
                    "category": "S3 Permissions", "check": name,
                    "status": "SKIP", "detail": "Skipped - Put Object failed",
                })
            return checks

        # Get Object
        try:
            s3.get_object(Bucket=self.bucket_name, Key=self._TEST_KEY)
            checks.append({
                "category": "S3 Permissions", "check": "Get Object",
                "status": "PASS", "detail": f"Read {self._TEST_KEY}",
            })
        except Exception as e:
            checks.append({
                "category": "S3 Permissions", "check": "Get Object",
                "status": "FAIL", "detail": str(e)[:120],
            })

        # Delete Object (always attempt cleanup)
        try:
            s3.delete_object(Bucket=self.bucket_name, Key=self._TEST_KEY)
            checks.append({
                "category": "S3 Permissions", "check": "Delete Object",
                "status": "PASS", "detail": f"Deleted {self._TEST_KEY}",
            })
        except Exception as e:
            checks.append({
                "category": "S3 Permissions", "check": "Delete Object",
                "status": "FAIL", "detail": str(e)[:120],
            })

        return checks

    # ------------------------------------------------------------------
    # Bucket state checks
    # ------------------------------------------------------------------

    def _test_bucket_state(self, session, bucket_name: str, distribution_id: str) -> list:
        import json as _json
        checks = []
        try:
            s3 = session.client("s3")
        except Exception as e:
            checks.append({
                "category": "Bucket State", "check": "S3 client",
                "status": "FAIL", "detail": str(e),
            })
            return checks

        # Bucket exists
        try:
            s3.head_bucket(Bucket=bucket_name)
            checks.append({
                "category": "Bucket State", "check": "Bucket exists",
                "status": "PASS", "detail": f"{bucket_name} is accessible",
            })
        except Exception as e:
            checks.append({
                "category": "Bucket State", "check": "Bucket exists",
                "status": "FAIL", "detail": str(e)[:120],
            })
            return checks

        # Public access blocks
        try:
            resp = s3.get_public_access_block(Bucket=bucket_name)
            cfg = resp["PublicAccessBlockConfiguration"]
            flags = [
                cfg.get("BlockPublicAcls", False),
                cfg.get("IgnorePublicAcls", False),
                cfg.get("BlockPublicPolicy", False),
                cfg.get("RestrictPublicBuckets", False),
            ]
            if all(flags):
                detail = "All blocks ON - private bucket (Mode B / CloudFront OAC)"
                status = "INFO"
            elif not any(flags):
                detail = "All blocks OFF - public bucket (Mode A / S3 website)"
                status = "INFO"
            else:
                on_keys = [k for k, v in cfg.items() if v]
                off_keys = [k for k, v in cfg.items() if not v]
                detail = f"Mixed config - ON: {on_keys} | OFF: {off_keys}"
                status = "WARN"
            checks.append({
                "category": "Bucket State", "check": "Public access blocks",
                "status": status, "detail": detail,
            })
        except Exception as e:
            checks.append({
                "category": "Bucket State", "check": "Public access blocks",
                "status": "WARN", "detail": f"Could not read: {str(e)[:100]}",
            })

        # Bucket policy - OAC SourceArn validation
        try:
            resp = s3.get_bucket_policy(Bucket=bucket_name)
            policy = _json.loads(resp["Policy"])
            source_arns = []
            for stmt in policy.get("Statement", []):
                arn = stmt.get("Condition", {}).get("StringEquals", {}).get(
                    "AWS:SourceArn", ""
                )
                if arn:
                    source_arns.append(arn)

            if not source_arns:
                checks.append({
                    "category": "Bucket State", "check": "Bucket policy",
                    "status": "WARN",
                    "detail": "Policy exists but no CloudFront OAC SourceArn condition found",
                })
            elif distribution_id:
                matched = any(distribution_id in arn for arn in source_arns)
                if matched:
                    checks.append({
                        "category": "Bucket State", "check": "Bucket policy",
                        "status": "PASS",
                        "detail": f"OAC SourceArn matches distribution {distribution_id}",
                    })
                else:
                    policy_dist = source_arns[0].split("/")[-1]
                    checks.append({
                        "category": "Bucket State", "check": "Bucket policy",
                        "status": "FAIL",
                        "detail": (
                            f"OAC MISMATCH - policy allows {policy_dist} "
                            f"but config uses {distribution_id}. "
                            "This causes AccessDenied on the CloudFront URL."
                        ),
                    })
            else:
                checks.append({
                    "category": "Bucket State", "check": "Bucket policy",
                    "status": "PASS",
                    "detail": f"OAC SourceArn present: {source_arns[0][:80]}",
                })
        except Exception as e:
            if "NoSuchBucketPolicy" in str(e):
                checks.append({
                    "category": "Bucket State", "check": "Bucket policy",
                    "status": "WARN",
                    "detail": "No bucket policy - required for CloudFront OAC (Mode B)",
                })
            else:
                checks.append({
                    "category": "Bucket State", "check": "Bucket policy",
                    "status": "WARN", "detail": f"Could not read: {str(e)[:100]}",
                })

        return checks

    # ------------------------------------------------------------------
    # CloudFront checks
    # ------------------------------------------------------------------

    def _test_cloudfront(self, session, distribution_id: str, bucket_name: str) -> list:
        checks = []
        try:
            cf = session.client("cloudfront")
        except Exception as e:
            checks.append({
                "category": "CloudFront", "check": "CloudFront client",
                "status": "FAIL", "detail": str(e),
            })
            return checks

        try:
            resp = cf.get_distribution(Id=distribution_id)
            dist = resp["Distribution"]
            domain = dist["DomainName"]
            status_str = dist["Status"]
            origins = dist["DistributionConfig"]["Origins"]["Items"]

            checks.append({
                "category": "CloudFront", "check": "Get Distribution",
                "status": "PASS",
                "detail": f"{domain} | Status: {status_str}",
            })

            # Origin matches bucket
            if bucket_name:
                origin_domains = [o["DomainName"] for o in origins]
                match = any(bucket_name.lower() in d.lower() for d in origin_domains)
                checks.append({
                    "category": "CloudFront", "check": "Origin bucket",
                    "status": "PASS" if match else "WARN",
                    "detail": (
                        f"Origin points to {bucket_name}"
                        if match else
                        f"Origin {origin_domains} does not match bucket {bucket_name}"
                    ),
                })

            # OAC attached
            oac_ids = [o.get("OriginAccessControlId", "") for o in origins]
            oac_ids = [oid for oid in oac_ids if oid]
            checks.append({
                "category": "CloudFront", "check": "OAC attached",
                "status": "PASS" if oac_ids else "WARN",
                "detail": (
                    f"OAC ID: {oac_ids[0]}"
                    if oac_ids else
                    "No OAC attached - required for private bucket access (Mode B)"
                ),
            })

        except Exception as e:
            err = str(e)
            if "AccessDenied" in err:
                checks.append({
                    "category": "CloudFront", "check": "Get Distribution",
                    "status": "WARN",
                    "detail": "IAM role lacks cloudfront:GetDistribution - cannot verify distribution",
                })
            elif "NoSuchDistribution" in err:
                checks.append({
                    "category": "CloudFront", "check": "Get Distribution",
                    "status": "FAIL",
                    "detail": f"Distribution {distribution_id} not found",
                })
            else:
                checks.append({
                    "category": "CloudFront", "check": "Get Distribution",
                    "status": "WARN", "detail": err[:120],
                })

        return checks


class DeploymentWorker(QThread):
    """Background worker for deployment operations"""

    progress_updated = pyqtSignal(UploadProgress)
    deployment_completed = pyqtSignal(UploadResult)

    def __init__(
        self,
        s3_manager: S3Manager,
        local_path: str,
        bucket_name: str,
        s3_directory: str = "",
        distribution_id: str = "",
        auto_invalidate: bool = False,
    ):
        super().__init__()
        self.s3_manager = s3_manager
        self.local_path = local_path
        self.bucket_name = bucket_name
        self.s3_directory = s3_directory
        self.distribution_id = distribution_id
        self.auto_invalidate = auto_invalidate

    def run(self):
        """Execute deployment in background"""
        try:
            # Set up progress callback
            self.s3_manager.set_progress_callback(self.progress_updated.emit)

            # Upload directory
            result = self.s3_manager.upload_directory(
                self.local_path, self.bucket_name, s3_prefix=self.s3_directory
            )

            # Debug: Log deployment parameters
            logging.info(
                f"Deployment completed: success={result.success}, "
                f"distribution_id='{self.distribution_id}', "
                f"s3_directory='{self.s3_directory}', "
                f"auto_invalidate={self.auto_invalidate}"
            )

            # Update CloudFront origin path if directory is specified and distribution exists
            if result.success and self.distribution_id and self.s3_directory:
                # Log the update attempt for debugging
                update_info = (
                    f"Updating CloudFront origin path: "
                    f"distribution={self.distribution_id}, "
                    f"path={self.s3_directory}"
                )
                logging.info(update_info)
                result.message += (
                    f"\n[CloudFront] Updating origin path to: /{self.s3_directory}"
                )

                origin_update_success, origin_update_msg = (
                    self.s3_manager.update_cloudfront_origin_path(
                        self.distribution_id, self.s3_directory
                    )
                )

                if origin_update_success:
                    result.message += f"\n[CloudFront] {origin_update_msg}"
                    result.message += "\n[CloudFront] NOTE: Changes may take 2-15 minutes to propagate"
                else:
                    result.message += f"\n[CloudFront] ERROR: {origin_update_msg}"
                    logging.error(f"CloudFront update failed: {origin_update_msg}")
            elif result.success and self.distribution_id and not self.s3_directory:
                logging.info(
                    "CloudFront origin path update skipped: deploying to root directory"
                )
            elif result.success and not self.distribution_id:
                logging.info(
                    "CloudFront origin path update skipped: no distribution ID configured"
                )

            # Perform CloudFront cache invalidation if enabled
            if result.success and self.auto_invalidate and self.distribution_id:
                invalidation_success, invalidation_msg, invalidation_id = (
                    self.s3_manager.create_cloudfront_invalidation(self.distribution_id)
                )

                result.invalidation_id = invalidation_id
                if invalidation_success:
                    result.invalidation_status = "InProgress"
                    result.message += (
                        f" | Cache invalidation started (ID: {invalidation_id})"
                    )
                else:
                    result.invalidation_status = "Failed"
                    result.message += (
                        f" | Cache invalidation failed: {invalidation_msg}"
                    )

            self.deployment_completed.emit(result)
        except Exception as e:
            # Create a failure result and emit it
            from src.core.aws.s3_manager import UploadResult

            error_result = UploadResult(
                success=False,
                message=f"Deployment failed: {str(e)}",
                website_url="",
                uploaded_files=0,
                failed_files=0,
            )
            self.deployment_completed.emit(error_result)


class CloudTab(BaseTab):
    """Cloud deployment configuration tab"""

    # Signal emitted when a deployment is created/updated
    deployment_created = pyqtSignal(DeploymentConfig)

    def __init__(self, parent=None):
        self.credentials_manager = AWSCredentialsManager()
        self.s3_manager = S3Manager()
        self.deployment_worker: Optional[DeploymentWorker] = None

        # Client-specific AWS configuration
        self.aws_config_manager = get_client_aws_manager()
        self.current_client_aws_config: Optional[ClientAWSConfig] = None
        self.current_business_name: str = ""
        self.current_domain: str = ""

        # Store full config for deployment tracking (v3.5.0)
        self.current_config = None

        # Flag to prevent bucket clearing during client context loading
        self._loading_client_context: bool = False

        # Provider selection
        self.provider_combo = None
        self.current_provider = "aws_s3"  # Default to AWS

        # Provider-specific sections (for show/hide)
        self.aws_section = None
        self.gcs_section = None
        self.deployment_mode_section = None  # CloudFront settings (AWS-only)
        self.bucket_section = None
        self.meta_tags_section = None

        # UI components
        self.profile_combo = None
        self.bucket_combo = None
        self.directory_combo = None
        self.region_combo = None
        self.deployment_mode_group = None
        self.s3_mode_radio = None
        self.cloudfront_mode_radio = None
        self.cloudfront_settings_group = None  # Container for CloudFront settings
        self.distribution_id_input = None
        self.auto_invalidate_checkbox = None

        # SEO and canonical URL settings
        self.site_type_main_radio = None
        self.site_type_backlink_radio = None
        self.site_type_resource_radio = None
        self.main_site_url_input = None

        self.progress_bar = None
        self.deploy_button = None
        self.status_text = None

        # GCS-specific components
        self.gcs_project_input = None
        self.gcs_credentials_input = None
        self.gcs_bucket_input = None
        self.gcs_region_combo = None

        super().__init__(parent)

    def setup_ui(self):
        """Setup cloud deployment UI"""
        layout = QVBoxLayout()

        # Provider Selection Section (NEW)
        provider_group = self.create_provider_selection_section()
        layout.addWidget(provider_group)

        # AWS Profile Section
        self.aws_section = self.create_profile_section()
        layout.addWidget(self.aws_section)

        # GCS Credentials Section (NEW)
        self.gcs_section = self.create_gcs_credentials_section()
        layout.addWidget(self.gcs_section)
        self.gcs_section.setVisible(False)  # Hidden by default

        # Bucket Configuration Section
        bucket_group = self.create_bucket_section()
        layout.addWidget(bucket_group)

        # Two-column layout for CloudFront Settings and Meta Tags
        two_column_layout = QHBoxLayout()

        # Left Column: Deployment Mode (with CloudFront Distribution Settings) - AWS-specific
        self.deployment_mode_section = self.create_deployment_mode_section()
        two_column_layout.addWidget(self.deployment_mode_section)

        # Right Column: SEO Meta Tags
        meta_tags_group = self.create_meta_tags_section()
        two_column_layout.addWidget(meta_tags_group)

        layout.addLayout(two_column_layout)

        # Deployment Controls Section
        controls_group = self.create_deployment_controls_section()
        layout.addWidget(controls_group)

        # Status and Progress Section
        status_group = self.create_status_section()
        layout.addWidget(status_group)

        layout.addStretch()
        self.setLayout(layout)

        # Apply initial deployment mode state
        self.on_deployment_mode_changed()

    def create_provider_selection_section(self) -> QGroupBox:
        """Create cloud provider selection section"""
        group = QGroupBox("Cloud Provider")
        layout = QHBoxLayout()

        layout.addWidget(QLabel("Provider:"))

        self.provider_combo = QComboBox()
        self.provider_combo.addItem("AWS S3", "aws_s3")
        self.provider_combo.addItem("Google Cloud Storage", "google_gcs")
        self.provider_combo.setToolTip("Select cloud storage provider for deployment")
        self.provider_combo.currentIndexChanged.connect(self.on_provider_changed)
        layout.addWidget(self.provider_combo)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def create_gcs_credentials_section(self) -> QGroupBox:
        """Create Google Cloud Storage credentials section"""
        group = QGroupBox("Google Cloud Storage Configuration")
        layout = QGridLayout()

        # Project ID
        layout.addWidget(QLabel("Project ID:"), 0, 0)
        self.gcs_project_input = QLineEdit()
        self.gcs_project_input.setPlaceholderText("my-gcp-project")
        self.gcs_project_input.setToolTip("Your Google Cloud Platform project ID")
        layout.addWidget(self.gcs_project_input, 0, 1)

        # Service Account JSON
        layout.addWidget(QLabel("Service Account JSON:"), 1, 0)
        json_layout = QHBoxLayout()
        self.gcs_credentials_input = QLineEdit()
        self.gcs_credentials_input.setPlaceholderText(
            "/path/to/service-account-key.json"
        )
        self.gcs_credentials_input.setToolTip(
            "Path to your GCS service account JSON key file"
        )
        json_layout.addWidget(self.gcs_credentials_input)

        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_gcs_credentials)
        json_layout.addWidget(browse_button)

        layout.addLayout(json_layout, 1, 1)

        # Region
        layout.addWidget(QLabel("Region:"), 2, 0)
        self.gcs_region_combo = QComboBox()
        self.gcs_region_combo.addItems(
            [
                "us-central1 (Iowa)",
                "us-east1 (South Carolina)",
                "us-west1 (Oregon)",
                "europe-west1 (Belgium)",
                "asia-southeast1 (Singapore)",
                "us (Multi-region)",
                "eu (Multi-region)",
                "asia (Multi-region)",
            ]
        )
        self.gcs_region_combo.setToolTip("Select Google Cloud Storage region")
        layout.addWidget(self.gcs_region_combo, 2, 1)

        # Test Connection button
        test_gcs_button = QPushButton("Test GCS Connection")
        test_gcs_button.clicked.connect(self.test_gcs_connection)
        layout.addWidget(test_gcs_button, 3, 1)

        group.setLayout(layout)
        return group

    def on_provider_changed(self):
        """Handle provider selection change"""
        provider_data = self.provider_combo.currentData()
        self.current_provider = provider_data

        # Clear bucket list when switching providers
        if self.bucket_combo:
            self.bucket_combo.clear()

        # Show/hide provider-specific sections
        if provider_data == "aws_s3":
            # Show AWS-specific sections
            self.aws_section.setVisible(True)
            self.gcs_section.setVisible(False)
            self.deployment_mode_section.setVisible(True)  # CloudFront settings

            # Show AWS region selector in bucket section
            if hasattr(self, "aws_region_label") and self.aws_region_label:
                self.aws_region_label.setVisible(True)
            if self.region_combo:
                self.region_combo.setVisible(True)

            # Update refresh button tooltip
            if self.refresh_buckets_button:
                self.refresh_buckets_button.setToolTip(
                    "Refresh bucket list from AWS S3"
                )
        elif provider_data == "google_gcs":
            # Show GCS-specific sections, hide AWS-specific sections
            self.aws_section.setVisible(False)
            self.gcs_section.setVisible(True)
            self.deployment_mode_section.setVisible(False)  # Hide CloudFront settings

            # Hide AWS region selector in bucket section (GCS has its own in GCS section)
            if hasattr(self, "aws_region_label") and self.aws_region_label:
                self.aws_region_label.setVisible(False)
            if self.region_combo:
                self.region_combo.setVisible(False)

            # Update refresh button tooltip
            if self.refresh_buckets_button:
                self.refresh_buckets_button.setToolTip(
                    "Refresh bucket list from Google Cloud Storage"
                )

    def browse_gcs_credentials(self):
        """Browse for GCS service account JSON file"""
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        import json

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Service Account JSON File",
            "",
            "JSON Files (*.json);;All Files (*)",
        )

        if file_path:
            self.gcs_credentials_input.setText(file_path)

            # Auto-populate project ID from JSON key file
            try:
                with open(file_path, "r") as f:
                    credentials_data = json.load(f)
                    project_id = credentials_data.get("project_id", "")
                    if project_id:
                        self.gcs_project_input.setText(project_id)
                    else:
                        QMessageBox.warning(
                            self,
                            "Project ID Not Found",
                            "Could not find 'project_id' in the selected JSON file. Please enter it manually.",
                        )
            except json.JSONDecodeError:
                QMessageBox.warning(
                    self,
                    "Invalid JSON",
                    "The selected file is not a valid JSON file. Please check the file and try again.",
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error Reading File",
                    f"Could not read the JSON file: {str(e)}",
                )

    def test_gcs_connection(self):
        """Test Google Cloud Storage connection"""
        from PyQt6.QtWidgets import QMessageBox

        project_id = self.gcs_project_input.text().strip()
        credentials_path = self.gcs_credentials_input.text().strip()

        if not project_id or not credentials_path:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please provide both Project ID and Service Account JSON path.",
            )
            return

        try:
            from ...core.deployment.providers import create_provider_from_dict

            # Create GCS provider config
            config_dict = {
                "provider": "google_gcs",
                "credentials": {
                    "service_account_json": credentials_path,
                    "project_id": project_id,
                },
                "region": self.gcs_region_combo.currentText().split()[
                    0
                ],  # Extract region code
            }

            # Create provider and test connection
            provider = create_provider_from_dict(config_dict)

            if provider.authenticate():
                success, message = provider.test_connection()

                if success:
                    # Save GCS credentials to client configuration
                    self.save_gcs_credentials(
                        project_id,
                        credentials_path,
                        self.gcs_region_combo.currentText().split()[0],
                    )

                    QMessageBox.information(
                        self,
                        "Connection Successful",
                        f"Successfully connected to Google Cloud Storage!\n\n{message}\n\n"
                        f"Your GCS credentials have been saved to this client's configuration.",
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Connection Failed",
                        f"Failed to connect to Google Cloud Storage.\n\n{message}",
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Authentication Failed",
                    "Failed to authenticate with Google Cloud Storage.\n\n"
                    "Please check your credentials and try again.",
                )

        except ImportError:
            QMessageBox.warning(
                self,
                "GCS Support Not Available",
                "Google Cloud Storage support requires the google-cloud-storage library.\n\n"
                "Install it with: pip install google-cloud-storage",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Connection Error", f"Error testing GCS connection:\n\n{str(e)}"
            )

    def save_gcs_credentials(self, project_id: str, credentials_path: str, region: str):
        """Save GCS credentials to client configuration"""
        if not self.current_client_aws_config:
            self.log_status("Warning: No client AWS config to save GCS credentials")
            return

        # Update GCS credentials in the config object
        self.current_client_aws_config.gcs_project_id = project_id
        self.current_client_aws_config.gcs_service_account_json = credentials_path
        self.current_client_aws_config.gcs_region = region

        # Save to persistent storage
        success = self.aws_config_manager.save_client_aws_config(
            self.current_client_aws_config
        )
        if success:
            self.log_status(
                f"GCS credentials saved successfully for {self.current_business_name}"
            )
        else:
            self.log_status("Warning: Failed to save GCS credentials")

    def create_profile_section(self) -> QGroupBox:
        """Create AWS profile configuration section"""
        group = QGroupBox("AWS Profile")
        layout = QGridLayout()

        # Profile selector
        layout.addWidget(QLabel("Profile:"), 0, 0)
        self.profile_combo = QComboBox()
        self.profile_combo.setMinimumWidth(200)
        self.profile_combo.setToolTip("Select an AWS profile for cloud deployment")
        layout.addWidget(self.profile_combo, 0, 1)

        # Profile management buttons
        self.new_profile_button = QPushButton("New Profile")
        self.edit_profile_button = QPushButton("Edit Profile")
        self.edit_profile_button.setToolTip("Edit the selected AWS profile")
        self.edit_profile_button.setEnabled(False)  # Disabled until profile selected
        self.delete_profile_button = QPushButton("Delete Profile")
        self.delete_profile_button.setToolTip("Delete the selected AWS profile")
        self.delete_profile_button.setEnabled(False)  # Disabled until profile selected
        self.test_connection_button = QPushButton("Test Connection")
        self.configure_sso_button = QPushButton("Configure SSO")
        self.configure_sso_button.setToolTip("Configure AWS SSO for selected profile")
        self.configure_sso_button.setEnabled(False)  # Disabled until profile selected

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_profile_button)
        button_layout.addWidget(self.edit_profile_button)
        button_layout.addWidget(self.delete_profile_button)
        button_layout.addWidget(self.test_connection_button)
        button_layout.addWidget(self.configure_sso_button)
        button_layout.addStretch()

        layout.addLayout(button_layout, 1, 0, 1, 3)

        # Profile status
        self.profile_status_label = QLabel("No profile selected")
        self.profile_status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.profile_status_label, 2, 0, 1, 3)

        # Connection test progress widget
        self.connection_progress = ProgressWidget()
        self.connection_progress.set_status_height(
            60
        )  # Smaller height for this context
        layout.addWidget(self.connection_progress, 3, 0, 1, 3)

        group.setLayout(layout)

        # Connect signals
        self.new_profile_button.clicked.connect(self.create_new_profile)
        self.edit_profile_button.clicked.connect(self.edit_profile)
        self.delete_profile_button.clicked.connect(self.delete_profile)
        self.test_connection_button.clicked.connect(self.test_aws_connection)
        self.configure_sso_button.clicked.connect(self.configure_existing_profile_sso)
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)

        # Load existing profiles
        self.refresh_profiles()

        return group

    def create_bucket_section(self) -> QGroupBox:
        """Create cloud storage bucket configuration section"""
        group = QGroupBox("Cloud Storage Bucket Configuration")
        layout = QGridLayout()

        # Bucket selection/creation
        layout.addWidget(QLabel("Bucket Name:"), 0, 0)

        # Bucket combo (existing buckets) and input (new bucket) side by side
        bucket_layout = QHBoxLayout()

        self.bucket_combo = QComboBox()
        self.bucket_combo.setEditable(True)
        self.bucket_combo.setPlaceholderText("Select existing or enter new bucket name")
        self.bucket_combo.lineEdit().setPlaceholderText("client-website-projectname")
        bucket_layout.addWidget(self.bucket_combo)

        self.refresh_buckets_button = QPushButton("Refresh")
        self.refresh_buckets_button.setMaximumWidth(80)
        self.refresh_buckets_button.setToolTip(
            "Refresh bucket list from selected cloud provider"
        )
        bucket_layout.addWidget(self.refresh_buckets_button)

        layout.addLayout(bucket_layout, 0, 1)

        self.create_bucket_button = QPushButton("Create Bucket")
        layout.addWidget(self.create_bucket_button, 0, 2)

        # Directory field
        layout.addWidget(QLabel("Directory:"), 1, 0)

        directory_layout = QHBoxLayout()

        self.directory_combo = QComboBox()
        self.directory_combo.setEditable(True)
        self.directory_combo.setPlaceholderText(
            "Select existing or enter new directory"
        )
        self.directory_combo.lineEdit().setPlaceholderText(
            "/ (root) or subdirectory name"
        )
        directory_layout.addWidget(self.directory_combo)

        self.refresh_directories_button = QPushButton("Refresh")
        self.refresh_directories_button.setMaximumWidth(80)
        self.refresh_directories_button.setToolTip(
            "Refresh directory list from selected bucket"
        )
        directory_layout.addWidget(self.refresh_directories_button)

        self.create_directory_button = QPushButton("Create")
        self.create_directory_button.setMaximumWidth(80)
        self.create_directory_button.setToolTip(
            "Create a new directory in the selected bucket"
        )
        directory_layout.addWidget(self.create_directory_button)

        layout.addLayout(directory_layout, 1, 1, 1, 2)

        # Region (AWS-specific)
        self.aws_region_label = QLabel("Region:")
        layout.addWidget(self.aws_region_label, 2, 0)
        self.region_combo = QComboBox()
        self.region_combo.addItems(
            [
                "us-east-1",
                "us-west-2",
                "eu-west-1",
                "ap-southeast-1",
                "eu-central-1",
                "ap-northeast-1",
            ]
        )
        layout.addWidget(self.region_combo, 2, 1)

        # Bucket and directory status
        self.bucket_status_label = QLabel("No bucket configured")
        self.bucket_status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.bucket_status_label, 3, 0, 1, 3)

        group.setLayout(layout)

        # Connect signals
        self.create_bucket_button.clicked.connect(self.create_bucket)
        self.refresh_buckets_button.clicked.connect(self.refresh_bucket_list)
        self.refresh_directories_button.clicked.connect(self.refresh_directory_list)
        self.create_directory_button.clicked.connect(self.create_directory)
        self.bucket_combo.currentTextChanged.connect(self.on_bucket_selection_changed)
        self.bucket_combo.lineEdit().textChanged.connect(self.on_bucket_name_changed)
        self.directory_combo.currentTextChanged.connect(
            self.on_directory_selection_changed
        )

        # Initialize with default directory
        self.directory_combo.addItem("/ (root)")
        self.directory_combo.setCurrentText("/ (root)")

        return group

    def create_deployment_mode_section(self) -> QGroupBox:
        """Create deployment mode selection section"""
        group = QGroupBox("Deployment Mode")
        layout = QVBoxLayout()

        self.deployment_mode_group = QButtonGroup()

        # Mode A: S3 Static Website
        self.s3_mode_radio = QRadioButton("Mode A: S3 Static Website (Fast deployment)")
        self.s3_mode_radio.setChecked(True)
        self.s3_mode_radio.setToolTip(
            "Direct S3 website hosting - fastest deployment, public bucket required"
        )

        # Mode B: CloudFront + OAC (v3.2.0 - Production Ready)
        self.cloudfront_mode_radio = QRadioButton(
            "Mode B: CloudFront + OAC (Production CDN)"
        )
        self.cloudfront_mode_radio.setEnabled(
            True
        )  # v3.2.0: Mode B now fully implemented
        self.cloudfront_mode_radio.setToolTip(
            "CloudFront distribution with Origin Access Control - auto-created, production ready, private bucket, HTTPS"
        )

        self.deployment_mode_group.addButton(self.s3_mode_radio, 0)
        self.deployment_mode_group.addButton(self.cloudfront_mode_radio, 1)

        layout.addWidget(self.s3_mode_radio)
        layout.addWidget(self.cloudfront_mode_radio)

        # Mode description
        self.mode_description = QLabel(
            "S3 Static Website: Direct hosting from S3 bucket with public access"
        )
        self.mode_description.setStyleSheet("color: #666; font-style: italic;")
        self.mode_description.setWordWrap(True)
        layout.addWidget(self.mode_description)

        # CloudFront Settings Group (for Mode A with existing CloudFront)
        self.cloudfront_settings_group = QGroupBox("CloudFront Distribution (Optional)")
        cf_layout = QVBoxLayout()

        # Explanation label
        cf_info = QLabel(
            "If you have an existing CloudFront distribution, enter its ID here to automatically update the origin path and invalidate cache."
        )
        cf_info.setStyleSheet("color: #666; font-size: 10px;")
        cf_info.setWordWrap(True)
        cf_layout.addWidget(cf_info)

        # Distribution ID input
        dist_layout = QHBoxLayout()
        dist_layout.addWidget(QLabel("Distribution ID:"))
        self.distribution_id_input = QLineEdit()
        self.distribution_id_input.setPlaceholderText("E.g., E1DKVV3777HLXC (optional)")
        self.distribution_id_input.setToolTip(
            "CloudFront distribution ID - leave blank to deploy to S3 only"
        )
        dist_layout.addWidget(self.distribution_id_input)
        cf_layout.addLayout(dist_layout)

        # Auto-invalidate checkbox
        self.auto_invalidate_checkbox = QCheckBox(
            "Automatically invalidate CloudFront cache after deployment"
        )
        self.auto_invalidate_checkbox.setChecked(True)
        self.auto_invalidate_checkbox.setToolTip(
            "Create invalidation request for /* after successful upload"
        )
        cf_layout.addWidget(self.auto_invalidate_checkbox)

        # OAC Diagnostic Tools (v3.2.0)
        diagnostic_layout = QVBoxLayout()

        # OAC Status Label
        self.oac_status_label = QLabel("")
        self.oac_status_label.setWordWrap(True)
        self.oac_status_label.setStyleSheet("font-size: 10px; padding: 5px;")
        diagnostic_layout.addWidget(self.oac_status_label)

        # Diagnostic Buttons
        button_layout = QHBoxLayout()

        self.check_oac_button = QPushButton("Check OAC Status")
        self.check_oac_button.setToolTip(
            "Check if this distribution has Origin Access Control configured"
        )
        self.check_oac_button.clicked.connect(self.on_check_oac_status)
        button_layout.addWidget(self.check_oac_button)

        self.delete_distribution_button = QPushButton("Delete Distribution")
        self.delete_distribution_button.setToolTip(
            "Disable and delete this CloudFront distribution"
        )
        self.delete_distribution_button.setStyleSheet("background-color: #ffcccc;")
        self.delete_distribution_button.clicked.connect(self.on_delete_distribution)
        button_layout.addWidget(self.delete_distribution_button)

        button_layout.addStretch()
        diagnostic_layout.addLayout(button_layout)

        cf_layout.addLayout(diagnostic_layout)

        self.cloudfront_settings_group.setLayout(cf_layout)
        layout.addWidget(self.cloudfront_settings_group)

        group.setLayout(layout)

        # Connect signals
        self.deployment_mode_group.buttonClicked.connect(
            self.on_deployment_mode_changed
        )

        return group

    def create_deployment_controls_section(self) -> QGroupBox:
        """Create deployment controls section"""
        group = QGroupBox("Deployment")
        layout = QVBoxLayout()

        # Friendly Name (Optional)
        friendly_name_layout = QHBoxLayout()
        friendly_name_layout.addWidget(QLabel("Friendly Name (Optional):"))

        self.friendly_name_input = QLineEdit()
        self.friendly_name_input.setPlaceholderText(
            "Leave empty to auto-generate from Business Name, Industry, Date"
        )
        self.friendly_name_input.setToolTip(
            "Custom name for this deployment. If left empty, will auto-generate from business info."
        )
        friendly_name_layout.addWidget(self.friendly_name_input)

        layout.addLayout(friendly_name_layout)

        # Local path selection
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Local Website:"))

        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText(
            "Generated website will be deployed automatically"
        )
        self.local_path_input.setReadOnly(True)
        path_layout.addWidget(self.local_path_input)

        layout.addLayout(path_layout)

        # Deploy button
        button_layout = QHBoxLayout()
        self.deploy_button = QPushButton("Deploy to Cloud")
        self.deploy_button.setMinimumHeight(35)
        self.deploy_button.setEnabled(False)

        button_layout.addWidget(self.deploy_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

        group.setLayout(layout)

        # Connect signals
        self.deploy_button.clicked.connect(self.start_deployment)

        return group

    def create_status_section(self) -> QGroupBox:
        """Create status and progress section"""
        group = QGroupBox("Deployment Status")
        layout = QVBoxLayout()

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        self.status_text.setPlainText("Ready for deployment")
        layout.addWidget(self.status_text)

        # Website URL display
        self.website_url_label = QLabel("")
        self.website_url_label.setOpenExternalLinks(True)
        self.website_url_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        layout.addWidget(self.website_url_label)

        group.setLayout(layout)

        return group

    def create_meta_tags_section(self) -> QGroupBox:
        """Create SEO meta tags management section"""
        from PyQt6.QtWidgets import QTableWidget, QHeaderView

        group = QGroupBox("SEO Configuration")
        layout = QVBoxLayout()

        # Canonical URL Settings
        canonical_label = QLabel("Canonical URLs:")
        canonical_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(canonical_label)

        # Site Type selection
        site_type_layout = QHBoxLayout()
        site_type_label = QLabel("Site Type:")
        site_type_layout.addWidget(site_type_label)

        self.site_type_main_radio = QRadioButton("Main Site")
        self.site_type_main_radio.setChecked(True)
        self.site_type_main_radio.setToolTip(
            "Primary business website - canonical URLs point to this site"
        )
        self.site_type_main_radio.toggled.connect(self.on_site_type_changed)
        site_type_layout.addWidget(self.site_type_main_radio)

        self.site_type_backlink_radio = QRadioButton("Backlink Site")
        self.site_type_backlink_radio.setToolTip(
            "Satellite/city site - canonical URLs point to main site"
        )
        self.site_type_backlink_radio.toggled.connect(self.on_site_type_changed)
        site_type_layout.addWidget(self.site_type_backlink_radio)

        self.site_type_resource_radio = QRadioButton("Resource Site")
        self.site_type_resource_radio.setToolTip(
            "Independent editorial/topical authority site - fill in the "
            "Resource Site tab for identity and attribution details"
        )
        self.site_type_resource_radio.toggled.connect(self.on_site_type_changed)
        site_type_layout.addWidget(self.site_type_resource_radio)

        site_type_layout.addStretch()
        layout.addLayout(site_type_layout)

        # Contextual help panel - updates when site type changes
        self.site_type_help_label = QLabel(
            "Main Site: Your primary business website. All canonical URLs point "
            "here. Use this for your main customer-facing presence."
        )
        self.site_type_help_label.setWordWrap(True)
        self.site_type_help_label.setStyleSheet(
            "background:#f0f7ff; border:1px solid #b8d4f0; border-radius:4px; "
            "padding:8px; color:#1a3a5c; font-size:9pt; margin-top:2px;"
        )
        layout.addWidget(self.site_type_help_label)

        # Main Site URL (only enabled for backlink sites)
        main_site_layout = QHBoxLayout()
        main_site_label = QLabel("Main Site URL:")
        main_site_layout.addWidget(main_site_label)

        self.main_site_url_input = QLineEdit()
        self.main_site_url_input.setPlaceholderText("https://mainsite.com")
        self.main_site_url_input.setToolTip(
            "For backlink sites: URL of the main production site (canonical URLs will point here)"
        )
        self.main_site_url_input.setEnabled(
            False
        )  # Disabled by default (main site selected)
        main_site_layout.addWidget(self.main_site_url_input)

        layout.addLayout(main_site_layout)

        # Separator
        separator = QLabel()
        separator.setStyleSheet("border-top: 1px solid #ccc; margin: 10px 0;")
        layout.addWidget(separator)

        # Meta Tags section header
        meta_tags_header = QLabel("Meta Tags:")
        meta_tags_header.setStyleSheet("font-weight: bold;")
        layout.addWidget(meta_tags_header)

        # Info label
        info_label = QLabel("Paste complete meta tag (Google provides the full tag)")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)

        # Meta tags list (table showing full tags)
        self.meta_tags_table = QTableWidget()
        self.meta_tags_table.setColumnCount(1)
        self.meta_tags_table.setHorizontalHeaderLabels(["Meta Tag"])
        self.meta_tags_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.meta_tags_table.setMaximumHeight(150)
        layout.addWidget(self.meta_tags_table)

        # Single meta tag input field
        input_layout = QVBoxLayout()

        input_layout.addWidget(QLabel("Complete Meta Tag:"))
        self.meta_tag_input = QLineEdit()
        self.meta_tag_input.setPlaceholderText(
            '<meta name="google-site-verification" content="xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU" />'
        )
        input_layout.addWidget(self.meta_tag_input)

        layout.addLayout(input_layout)

        # Action buttons
        button_layout = QHBoxLayout()

        self.add_meta_tag_button = QPushButton("Add Tag")
        self.add_meta_tag_button.clicked.connect(self.add_or_update_meta_tag)
        button_layout.addWidget(self.add_meta_tag_button)

        self.remove_meta_tag_button = QPushButton("Remove Tag")
        self.remove_meta_tag_button.clicked.connect(self.remove_meta_tag)
        self.remove_meta_tag_button.setEnabled(False)
        button_layout.addWidget(self.remove_meta_tag_button)

        button_layout.addStretch()

        # Google Search Console integration button
        self.gsc_button = QPushButton("Get Google Verification Tag")
        self.gsc_button.clicked.connect(self.open_gsc_verification_dialog)
        self.gsc_button.setStyleSheet("background-color: #4285f4; color: white;")
        button_layout.addWidget(self.gsc_button)

        layout.addLayout(button_layout)

        group.setLayout(layout)

        # Connect table selection signal
        self.meta_tags_table.itemSelectionChanged.connect(
            self.on_meta_tag_selection_changed
        )
        self.meta_tags_table.cellDoubleClicked.connect(self.on_meta_tag_double_clicked)

        return group

    def connect_signals(self):
        """Connect UI signals"""
        # Signals are connected in individual create_* methods
        pass

    def create_new_profile(self):
        """Create new AWS profile"""
        existing_profiles = [
            self.profile_combo.itemText(i) for i in range(self.profile_combo.count())
        ]

        dialog = AWSProfileDialog(self, existing_profiles)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            profile_data = dialog.get_profile_data()

            if not profile_data["name"]:
                QMessageBox.warning(self, "Invalid Profile", "Profile name is required")
                return

            if profile_data["name"] in existing_profiles:
                QMessageBox.warning(
                    self,
                    "Profile Exists",
                    f"Profile '{profile_data['name']}' already exists",
                )
                return

            # Create AWS profile
            if profile_data["auth_method"] == AuthMethod.SSO:
                profile = self.credentials_manager.add_sso_profile(
                    name=profile_data["name"],
                    sso_start_url=profile_data["sso_start_url"],
                    sso_region=profile_data["sso_region"],
                    region=profile_data["region"],
                )
            else:  # ACCESS_KEYS
                # Validate access key credentials are provided
                if not profile_data.get("access_key_id") or not profile_data.get(
                    "secret_access_key"
                ):
                    QMessageBox.warning(
                        self,
                        "Missing Credentials",
                        "Access Key ID and Secret Access Key are required for Access Key authentication.",
                    )
                    return

                profile = self.credentials_manager.add_access_key_profile(
                    name=profile_data["name"], region=profile_data["region"]
                )

                # Store the access keys securely
                from ...core.security.api_key_manager import APIKeyManager

                api_key_manager = APIKeyManager()
                success = api_key_manager.set_aws_credentials(
                    profile_name=profile_data["name"],
                    access_key_id=profile_data["access_key_id"],
                    secret_access_key=profile_data["secret_access_key"],
                )

                if not success:
                    QMessageBox.critical(
                        self,
                        "Storage Error",
                        "Failed to securely store AWS credentials. Please try again.",
                    )
                    return

            profile.description = profile_data["description"]

            self.refresh_profiles()
            self.profile_combo.setCurrentText(profile_data["name"])

            # Explicitly save the profile selection
            self.on_aws_config_changed()

            QMessageBox.information(
                self,
                "Profile Created",
                f"AWS profile '{profile_data['name']}' created successfully.\n\n"
                "For SSO profiles, you'll need to run 'aws configure sso' in your terminal "
                "with the same profile name to complete the setup.",
            )

    def edit_profile(self):
        """Edit the selected AWS profile"""
        profile_name = self.profile_combo.currentText()

        # Validate selection
        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(
                self, "No Profile Selected", "Please select a profile to edit."
            )
            return

        # Get current profile data
        if profile_name not in self.credentials_manager.profiles:
            QMessageBox.warning(
                self, "Profile Not Found", f"Profile '{profile_name}' not found."
            )
            return

        current_profile = self.credentials_manager.profiles[profile_name]
        existing_profiles = [
            self.profile_combo.itemText(i) for i in range(self.profile_combo.count())
        ]
        existing_profiles.remove(
            profile_name
        )  # Remove current profile from list to allow keeping same name

        # Create dialog
        dialog = AWSProfileDialog(self, existing_profiles)
        dialog.setWindowTitle(f"Edit Profile: {profile_name}")

        # Pre-populate with current values
        dialog.profile_name_input.setText(profile_name)
        dialog.profile_name_input.setEnabled(True)  # Allow changing profile name

        # Set authentication method
        if current_profile.auth_method == AuthMethod.SSO:
            dialog.sso_radio.setChecked(True)
            dialog.on_auth_method_changed()
            if hasattr(current_profile, "sso_start_url"):
                dialog.sso_url_input.setText(current_profile.sso_start_url or "")
            if hasattr(current_profile, "sso_account_id"):
                dialog.sso_account_input.setText(current_profile.sso_account_id or "")
            if hasattr(current_profile, "sso_role_name"):
                dialog.sso_role_input.setText(current_profile.sso_role_name or "")
        else:
            dialog.access_keys_radio.setChecked(True)
            dialog.on_auth_method_changed()
            # Note: We don't pre-populate access keys for security reasons
            # User will need to re-enter them if changing

        # Set region
        if hasattr(current_profile, "region"):
            region_index = dialog.region_combo.findText(current_profile.region)
            if region_index >= 0:
                dialog.region_combo.setCurrentIndex(region_index)

        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                profile_data = dialog.get_profile_data()
                new_profile_name = profile_data["name"]

                # If profile name changed, delete old profile
                if new_profile_name != profile_name:
                    if new_profile_name in self.credentials_manager.profiles:
                        QMessageBox.warning(
                            self,
                            "Profile Exists",
                            f"A profile named '{new_profile_name}' already exists. Please choose a different name.",
                        )
                        return

                    # Remove old profile
                    del self.credentials_manager.profiles[profile_name]

                    # Remove stored credentials from secure storage
                    from ...core.security.api_key_manager import APIKeyManager

                    api_key_manager = APIKeyManager()
                    api_key_manager.remove_aws_credentials(profile_name)

                # Update/create profile with new data
                if profile_data["auth_method"] == AuthMethod.SSO:
                    profile = self.credentials_manager.add_sso_profile(
                        name=profile_data["name"],
                        sso_start_url=profile_data["sso_start_url"],
                        sso_region=profile_data["region"],
                        sso_account_id=profile_data.get("sso_account_id"),
                        sso_role_name=profile_data.get("sso_role_name"),
                    )
                    profile.description = profile_data.get("description", "")
                else:  # ACCESS_KEYS
                    # Validate access key credentials are provided
                    if not profile_data.get("access_key_id") or not profile_data.get(
                        "secret_access_key"
                    ):
                        QMessageBox.warning(
                            self,
                            "Missing Credentials",
                            "Access Key ID and Secret Access Key are required for Access Key authentication.",
                        )
                        return

                    profile = self.credentials_manager.add_access_key_profile(
                        name=profile_data["name"], region=profile_data["region"]
                    )

                    # Store the access keys securely
                    from ...core.security.api_key_manager import APIKeyManager

                    api_key_manager = APIKeyManager()
                    success = api_key_manager.set_aws_credentials(
                        profile_name=profile_data["name"],
                        access_key_id=profile_data["access_key_id"],
                        secret_access_key=profile_data["secret_access_key"],
                    )

                    if not success:
                        QMessageBox.critical(
                            self,
                            "Storage Error",
                            "Failed to securely store AWS credentials. Please try again.",
                        )
                        return

                    profile.description = profile_data.get("description", "")

                # Refresh profiles
                self.refresh_profiles()

                # Select the updated profile
                self.profile_combo.setCurrentText(new_profile_name)

                self.log_status(
                    f"AWS profile '{new_profile_name}' updated successfully"
                )

                QMessageBox.information(
                    self,
                    "Profile Updated",
                    f"AWS profile '{profile_name}' has been updated successfully."
                    + (
                        f"\n\nProfile renamed to '{new_profile_name}'."
                        if new_profile_name != profile_name
                        else ""
                    ),
                )

            except Exception as e:
                error_msg = f"Failed to update profile: {str(e)}"
                self.log_status(f"Error: {error_msg}")
                QMessageBox.critical(self, "Update Error", error_msg)

    def delete_profile(self):
        """Delete the selected AWS profile with confirmation"""
        profile_name = self.profile_combo.currentText()

        # Validate selection
        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(
                self, "No Profile Selected", "Please select a profile to delete."
            )
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the AWS profile '{profile_name}'?\n\n"
            "This will remove the profile configuration and any stored credentials.\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # Remove from credentials manager
            if profile_name in self.credentials_manager.profiles:
                del self.credentials_manager.profiles[profile_name]

            # Remove stored credentials from secure storage
            from ...core.security.api_key_manager import APIKeyManager

            api_key_manager = APIKeyManager()
            api_key_manager.remove_aws_credentials(profile_name)

            # Refresh the UI
            self.refresh_profiles()

            # Clear bucket list if this was the active profile
            if self.bucket_combo is not None:
                self.bucket_combo.clear()
                self.bucket_combo.addItem("No buckets found")

            # Update status
            self.profile_status_label.setText("Profile deleted")
            self.log_status(f"Profile '{profile_name}' deleted successfully")

            # Save updated configuration
            self.on_aws_config_changed()

            QMessageBox.information(
                self,
                "Profile Deleted",
                f"AWS profile '{profile_name}' has been deleted successfully.",
            )

        except Exception as e:
            error_msg = f"Failed to delete profile '{profile_name}': {str(e)}"
            self.log_status(f"Error: {error_msg}")
            QMessageBox.critical(self, "Delete Error", error_msg)

    def configure_existing_profile_sso(self):
        """Configure AWS SSO for existing profile"""
        profile_name = self.profile_combo.currentText()

        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(
                self, "No Profile Selected", "Please select a profile first."
            )
            return

        if profile_name not in self.credentials_manager.profiles:
            QMessageBox.warning(
                self, "Profile Not Found", f"Profile '{profile_name}' not found."
            )
            return

        profile = self.credentials_manager.profiles[profile_name]
        if profile.auth_method != AuthMethod.SSO:
            QMessageBox.information(
                self,
                "Not an SSO Profile",
                f"Profile '{profile_name}' is not configured for SSO authentication.",
            )
            return

        try:
            # Prepare AWS configure SSO command with profile name
            command = f"aws configure sso --profile {profile_name}"

            # Open terminal based on operating system
            system = platform.system().lower()

            if system == "windows":
                # Use Windows Terminal if available, otherwise use cmd
                try:
                    subprocess.run(["wt", "cmd", "/k", command], check=False)
                except FileNotFoundError:
                    # Fallback to cmd if Windows Terminal not available
                    subprocess.run(["cmd", "/k", command], check=False)
            elif system == "darwin":  # macOS
                # Use Terminal app
                applescript = f"""
                tell application "Terminal"
                    do script "{command}"
                    activate
                end tell
                """
                subprocess.run(["osascript", "-e", applescript], check=False)
            else:  # Linux and other Unix-like systems
                # Try common terminal emulators
                terminals = [
                    "gnome-terminal",
                    "konsole",
                    "xterm",
                    "x-terminal-emulator",
                ]
                for terminal in terminals:
                    try:
                        if terminal == "gnome-terminal":
                            subprocess.run(
                                [terminal, "--", "bash", "-c", f"{command}; exec bash"],
                                check=False,
                            )
                        elif terminal == "konsole":
                            subprocess.run(
                                [terminal, "-e", "bash", "-c", f"{command}; exec bash"],
                                check=False,
                            )
                        else:
                            subprocess.run(
                                [terminal, "-e", f"bash -c '{command}; exec bash'"],
                                check=False,
                            )
                        break
                    except FileNotFoundError:
                        continue
                else:
                    QMessageBox.warning(
                        self,
                        "Terminal Not Found",
                        "Could not find a suitable terminal application.",
                    )
                    return

            QMessageBox.information(
                self,
                "SSO Configuration",
                f"AWS SSO reconfiguration started for profile '{profile_name}'. "
                f"Please complete the configuration in the terminal window that opened.\n\n"
                f"This will update the SSO session for your existing profile.",
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open terminal: {str(e)}")

    def refresh_profiles(self):
        """Refresh profile dropdown"""
        current_text = self.profile_combo.currentText()
        self.profile_combo.clear()

        profiles = list(self.credentials_manager.profiles.keys())
        if profiles:
            self.profile_combo.addItems(profiles)
            if current_text in profiles:
                self.profile_combo.setCurrentText(current_text)
            # Don't change selection if current text not found - let user manually select
        else:
            self.profile_combo.addItem("No profiles configured")
            self.profile_combo.setCurrentText("No profiles configured")

    def on_profile_changed(self, profile_name: str):
        """Handle profile selection change"""
        self.log_status(f"Debug: Profile changed to '{profile_name}'")

        if profile_name == "No profiles configured":
            self.profile_status_label.setText("No profile selected")
            self.configure_sso_button.setEnabled(False)
            self.edit_profile_button.setEnabled(False)
            self.delete_profile_button.setEnabled(False)
            return

        # Handle empty string profile name
        if profile_name == "":
            self.log_status(
                "Debug: Empty profile name detected - not triggering auto-save"
            )
            self.profile_status_label.setText("No profile selected")
            self.profile_combo.setToolTip("Select an AWS profile for cloud deployment")
            self.configure_sso_button.setEnabled(False)
            self.edit_profile_button.setEnabled(False)
            self.delete_profile_button.setEnabled(False)
            return

        if profile_name in self.credentials_manager.profiles:
            profile = self.credentials_manager.profiles[profile_name]
            self.profile_status_label.setText(
                f"Profile: {profile.auth_method.value} | Region: {profile.region}"
            )
            # Only set region combo if it's been initialized
            if self.region_combo is not None:
                self.region_combo.setCurrentText(profile.region)
            # Update profile combo tooltip with detailed information
            tooltip_text = f"Profile: {profile_name}\nAuth Method: {profile.auth_method.value}\nRegion: {profile.region}"
            self.profile_combo.setToolTip(tooltip_text)
            # Enable Configure SSO button only for SSO profiles
            self.configure_sso_button.setEnabled(profile.auth_method == AuthMethod.SSO)
            # Enable Edit and Delete Profile buttons when a valid profile is selected
            self.edit_profile_button.setEnabled(True)
            self.delete_profile_button.setEnabled(True)
            # Only reset bucket list if not loading client context (preserve user selections)
            if not getattr(self, "_loading_client_context", False):
                if self.bucket_combo is not None:
                    self.bucket_combo.clear()
                    self.bucket_combo.addItem("No buckets found")
                    self.bucket_combo.setCurrentText("No buckets found")
                    self.log_status(
                        f"Profile '{profile_name}' selected. Click 'Refresh' next to Bucket Name to load S3 buckets."
                    )
                else:
                    self.log_status(
                        f"Profile '{profile_name}' selected. UI not fully initialized yet."
                    )
            else:
                self.log_status(
                    f"Profile '{profile_name}' restored from client context."
                )
            self.update_deploy_button_state()
            # Auto-save client AWS config
            self.log_status(f"Debug: Triggering auto-save for profile '{profile_name}'")
            self.on_aws_config_changed()
        else:
            self.profile_status_label.setText("Profile not found")
            self.profile_combo.setToolTip(
                f"Profile '{profile_name}' not found in credentials manager"
            )
            self.configure_sso_button.setEnabled(False)
            self.delete_profile_button.setEnabled(False)
            self.log_status(
                f"Debug: Profile '{profile_name}' not found in credentials manager"
            )

    def _populate_buckets_for_profile_silently(self, profile_name: str):
        """Silently populate bucket list for the given profile without showing error messages"""
        try:
            if not profile_name or profile_name == "No profiles configured":
                self.log_status("Debug: No profile selected for bucket population")
                return

            if profile_name not in self.credentials_manager.profiles:
                self.log_status(
                    f"Debug: Profile '{profile_name}' not found for bucket population"
                )
                return

            # Get AWS session for the profile
            session = self.credentials_manager._get_session(profile_name)
            if not session:
                self.log_status(
                    f"Debug: Could not create AWS session for profile '{profile_name}'"
                )
                return

            # Set session and get buckets
            self.s3_manager.set_session(session)

            # Get all client buckets with SOP compliance indicators
            buckets = self.credentials_manager.list_client_buckets(
                profile_name, show_all=True
            )

            # Store current selection (extract actual bucket name if it has indicators)
            current_bucket = ""
            if self.bucket_combo and self.bucket_combo.currentText():
                current_selection = self.bucket_combo.currentText()
                # If current selection has visual indicators, extract the actual bucket name
                if current_selection.startswith("✓ "):
                    current_bucket = current_selection[2:]  # Remove "✓ " prefix
                elif current_selection.startswith("• "):
                    current_bucket = current_selection[2:]  # Remove "• " prefix
                else:
                    current_bucket = current_selection

            # Clear and populate combo
            if self.bucket_combo:
                self.bucket_combo.clear()

                if buckets:
                    sop_compliant_count = 0
                    for bucket in buckets:
                        bucket_name = bucket["name"]
                        if bucket.get("sop_compliant", False):
                            # Mark SOP-compliant buckets with a prefix
                            display_name = f"✓ {bucket_name}"
                            sop_compliant_count += 1
                        else:
                            # Show non-SOP buckets with a different indicator
                            display_name = f"• {bucket_name}"

                        self.bucket_combo.addItem(display_name)
                        # Store the actual bucket name as item data
                        self.bucket_combo.setItemData(
                            self.bucket_combo.count() - 1, bucket_name
                        )

                    # Restore selection if it exists (match by actual bucket name)
                    for i in range(self.bucket_combo.count()):
                        if self.bucket_combo.itemData(i) == current_bucket:
                            self.bucket_combo.setCurrentIndex(i)
                            break

                    self.log_status(
                        f"Auto-populated {len(buckets)} buckets ({sop_compliant_count} SOP-compliant) for profile '{profile_name}'"
                    )
                else:
                    self.bucket_combo.addItem("No buckets found")
                    self.log_status(
                        f"No buckets found in AWS account for profile '{profile_name}'"
                    )

        except Exception as e:
            self.log_status(
                f"Debug: Failed to auto-populate buckets for profile '{profile_name}': {str(e)}"
            )

    def _get_actual_bucket_name(self) -> str:
        """Get the actual bucket name from the combo box, handling visual indicators"""
        if not self.bucket_combo:
            return ""

        current_index = self.bucket_combo.currentIndex()
        if current_index >= 0:
            # Try to get the stored bucket name from item data
            bucket_name = self.bucket_combo.itemData(current_index)
            if bucket_name:
                return bucket_name

        # Fallback: extract from display text
        current_text = self.bucket_combo.currentText().strip()
        if current_text.startswith("✓ "):
            return current_text[2:]  # Remove "✓ " prefix
        elif current_text.startswith("• "):
            return current_text[2:]  # Remove "• " prefix
        else:
            return current_text

    def test_aws_connection(self):
        """Test AWS connection for selected profile with progress indication"""
        profile_name = self.profile_combo.currentText()
        if profile_name == "No profiles configured":
            QMessageBox.warning(
                self, "No Profile", "Please create an AWS profile first"
            )
            return

        # Check if already running
        if (
            hasattr(self, "_connection_test_worker")
            and self._connection_test_worker.isRunning()
        ):
            return

        # Show progress and disable button
        self.connection_progress.show_progress(
            "Testing AWS connection...", indeterminate=True
        )
        self.test_connection_button.setEnabled(False)

        # Gather context for comprehensive checks
        bucket_name = self._get_actual_bucket_name()
        distribution_id = (
            self.distribution_id_input.text().strip()
            if self.distribution_id_input
            else ""
        )

        # Create and start worker thread
        self._connection_test_worker = ConnectionTestWorker(
            self.credentials_manager, profile_name, bucket_name, distribution_id
        )
        self._connection_test_worker.progress_updated.connect(
            self.connection_progress.update_status
        )
        self._connection_test_worker.test_completed.connect(
            self._on_connection_test_completed
        )
        self._connection_test_worker.error_occurred.connect(
            self._on_connection_test_error
        )
        self._connection_test_worker.start()

    def _on_connection_test_completed(
        self, success: bool, message: str, identity: dict, checks: list
    ):
        """Handle connection test completion - show structured results dialog."""
        try:
            self.connection_progress.hide_progress()

            dlg = ConnectionResultsDialog(identity, checks, parent=self)
            dlg.exec()

            if success:
                session = self.credentials_manager.get_active_session()
                if session:
                    self.s3_manager.set_session(session)
        finally:
            self.test_connection_button.setEnabled(True)

    def _on_connection_test_error(self, error_message: str, exception: Exception):
        """Handle connection test error"""
        try:
            # Safely update progress status
            try:
                self.connection_progress.update_status(f"Error: {error_message}")
            except Exception:
                pass  # Ignore progress update errors in tests

            # Also log to main status text for test visibility
            try:
                self.log_status(f"Connection failed: {error_message}")
            except Exception:
                pass  # Ignore logging errors in tests

            # Hide progress before showing dialog
            try:
                self.connection_progress.hide_progress()
            except Exception:
                pass  # Ignore progress hide errors in tests

            # Use error logger for consistent error handling
            log_error_dialog(self, "Connection Test Failed", error_message, exception)

        finally:
            # Re-enable button
            try:
                self.test_connection_button.setEnabled(True)
            except Exception:
                pass  # Ignore button state errors in tests

    def on_bucket_name_changed(self):
        """Handle bucket name change"""
        bucket_name = self._get_actual_bucket_name()

        if bucket_name:
            is_valid, message = self.s3_manager.validate_bucket_name(bucket_name)
            if is_valid:
                self.bucket_status_label.setText("Bucket name is valid")
                self.bucket_status_label.setStyleSheet("color: green;")
            else:
                self.bucket_status_label.setText(f"Invalid: {message}")
                self.bucket_status_label.setStyleSheet("color: red;")
        else:
            self.bucket_status_label.setText("No bucket configured")
            self.bucket_status_label.setStyleSheet("color: #666;")

        self.update_deploy_button_state()
        # Auto-save client AWS config
        self.on_aws_config_changed()

    def refresh_bucket_list(self):
        """Refresh the list of available buckets with progress indication"""
        # Check which provider is selected
        if self.current_provider == "google_gcs":
            self._refresh_gcs_bucket_list()
            return

        # AWS S3 path
        profile_name = self.profile_combo.currentText()

        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(
                self, "No Profile Selected", "Please select an AWS profile first."
            )
            return

        if profile_name not in self.credentials_manager.profiles:
            QMessageBox.warning(
                self, "Profile Not Found", f"Profile '{profile_name}' not found."
            )
            return

        # Check if already running
        if (
            hasattr(self, "_bucket_refresh_worker")
            and self._bucket_refresh_worker.isRunning()
        ):
            return

        # Show progress and disable button
        if not hasattr(self, "bucket_progress"):
            self.bucket_progress = ProgressWidget()
            self.bucket_progress.set_status_height(80)
            # Insert after bucket section - find parent layout
            for i in range(self.layout().count()):
                item = self.layout().itemAt(i)
                if (
                    hasattr(item.widget(), "title")
                    and "Bucket" in item.widget().title()
                ):
                    self.layout().insertWidget(i + 1, self.bucket_progress)
                    break

        self.bucket_progress.show_progress(
            "Refreshing bucket list...", indeterminate=True
        )
        self.refresh_buckets_button.setEnabled(False)

        # Create and start worker thread
        self._bucket_refresh_worker = BucketRefreshWorker(
            self.credentials_manager, self.s3_manager, profile_name
        )
        self._bucket_refresh_worker.progress_updated.connect(
            self.bucket_progress.update_status
        )
        self._bucket_refresh_worker.finished.connect(self._on_bucket_refresh_finished)
        self._bucket_refresh_worker.error_occurred.connect(
            self._on_bucket_refresh_error
        )
        self._bucket_refresh_worker.start()

    def _on_bucket_refresh_finished(self, buckets, profile_name):
        """Handle bucket refresh completion"""
        try:
            # Store current selection
            current_bucket = self.bucket_combo.currentText()

            # Clear and populate combo
            self.bucket_combo.clear()

            if buckets:
                sop_compliant_count = 0
                for bucket in buckets:
                    bucket_name = bucket["name"]
                    if bucket.get("sop_compliant", False):
                        # Mark SOP-compliant buckets with a prefix
                        display_name = f"[+] {bucket_name}"
                        sop_compliant_count += 1
                    else:
                        # Show non-SOP buckets with a different indicator
                        display_name = f"[-] {bucket_name}"

                    self.bucket_combo.addItem(display_name)
                    # Store the actual bucket name as item data
                    self.bucket_combo.setItemData(
                        self.bucket_combo.count() - 1, bucket_name
                    )

                # Restore selection if it exists (match by actual bucket name)
                for i in range(self.bucket_combo.count()):
                    if self.bucket_combo.itemData(i) == current_bucket:
                        self.bucket_combo.setCurrentIndex(i)
                        break

                self.bucket_progress.update_status(
                    f"Found {len(buckets)} buckets ({sop_compliant_count} SOP-compliant)"
                )
                self.log_status(
                    f"Found {len(buckets)} buckets ({sop_compliant_count} SOP-compliant)"
                )
            else:
                self.bucket_combo.addItem("No buckets found")
                self.bucket_progress.update_status("No buckets found in AWS account")
                self.log_status("No buckets found in AWS account")

        finally:
            # Hide progress and re-enable button
            self.bucket_progress.hide_progress()
            self.refresh_buckets_button.setEnabled(True)

    def _on_bucket_refresh_error(self, error_message, profile_name, exception):
        """Handle bucket refresh error"""
        try:
            self.bucket_progress.update_status(f"Error: {error_message}")
            QMessageBox.critical(
                self, "Error", f"Failed to retrieve bucket list:\n\n{error_message}"
            )
            self.log_status(f"Error retrieving buckets: {error_message}")

            # Log to error log file
            log_error_dialog(
                title="Bucket Retrieval Error",
                message=error_message,
                context=f"Retrieving bucket list for profile '{profile_name}'",
                component="CloudTab.refresh_bucket_list",
                exception=exception,
                user_action="Refreshing S3 bucket list",
            )

        finally:
            # Hide progress and re-enable button
            self.bucket_progress.hide_progress()
            self.refresh_buckets_button.setEnabled(True)

    def _refresh_gcs_bucket_list(self):
        """Refresh the list of available GCS buckets"""
        from PyQt6.QtWidgets import QMessageBox

        project_id = self.gcs_project_input.text().strip()
        credentials_path = self.gcs_credentials_input.text().strip()

        if not project_id or not credentials_path:
            QMessageBox.warning(
                self,
                "Missing Configuration",
                "Please provide both Project ID and Service Account JSON path.",
            )
            return

        try:
            from ...core.deployment.providers import create_provider_from_dict

            # Show progress
            if not hasattr(self, "bucket_progress"):
                self.bucket_progress = ProgressWidget()
                self.bucket_progress.set_status_height(80)
                for i in range(self.layout().count()):
                    item = self.layout().itemAt(i)
                    if (
                        hasattr(item.widget(), "title")
                        and "Bucket" in item.widget().title()
                    ):
                        self.layout().insertWidget(i + 1, self.bucket_progress)
                        break

            self.bucket_progress.show_progress(
                "Refreshing GCS bucket list...", indeterminate=True
            )
            self.refresh_buckets_button.setEnabled(False)

            # Create GCS provider config
            config_dict = {
                "provider": "google_gcs",
                "credentials": {
                    "service_account_json": credentials_path,
                    "project_id": project_id,
                },
                "region": self.gcs_region_combo.currentText().split()[0],
            }

            provider = create_provider_from_dict(config_dict)

            # Authenticate
            if not provider.authenticate():
                QMessageBox.warning(
                    self,
                    "Authentication Failed",
                    "Failed to authenticate with Google Cloud Storage.",
                )
                return

            # Get bucket list
            buckets = provider.list_buckets()

            # Clear and populate combo
            self.bucket_combo.clear()

            if buckets:
                for bucket_name in buckets:
                    self.bucket_combo.addItem(bucket_name)
                    self.bucket_combo.setItemData(
                        self.bucket_combo.count() - 1, bucket_name
                    )

                self.bucket_progress.update_status(f"Found {len(buckets)} GCS buckets")
                self.log_status(f"Found {len(buckets)} GCS buckets")
            else:
                self.bucket_combo.addItem("No buckets found")
                self.bucket_progress.update_status("No buckets found in GCS project")
                self.log_status("No buckets found in GCS project")

        except ImportError:
            QMessageBox.warning(
                self,
                "GCS Support Not Available",
                "Google Cloud Storage support requires the google-cloud-storage library.\n\n"
                "Install it with: pip install google-cloud-storage",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to retrieve GCS bucket list:\n\n{str(e)}"
            )
            self.log_status(f"Error retrieving GCS buckets: {str(e)}")

        finally:
            self.bucket_progress.hide_progress()
            self.refresh_buckets_button.setEnabled(True)

    def refresh_directory_list(self):
        """Refresh the list of directories in the selected bucket"""
        bucket_name = self._get_actual_bucket_name()
        profile_name = self.profile_combo.currentText()

        if not bucket_name or bucket_name == "No buckets found":
            QMessageBox.warning(
                self, "No Bucket Selected", "Please select a bucket first."
            )
            return

        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(
                self, "No Profile Selected", "Please select an AWS profile first."
            )
            return

        try:
            # Get AWS session for the profile
            session = self.credentials_manager._get_session(profile_name)
            if not session:
                QMessageBox.warning(
                    self,
                    "Session Error",
                    "Could not create AWS session for the selected profile.",
                )
                return

            # Set session and get bucket contents
            self.s3_manager.set_session(session)
            contents = self.s3_manager.list_bucket_contents(bucket_name)

            # Extract unique directory prefixes
            directories = set()
            directories.add("/ (root)")  # Always include root

            for item in contents:
                key = item["key"]
                # Look for directory-like paths (containing '/')
                if "/" in key:
                    parts = key.split("/")
                    # Build directory paths
                    for i in range(len(parts) - 1):
                        dir_path = "/".join(parts[: i + 1]) + "/"
                        directories.add(dir_path)

            # Store current selection
            current_directory = self.directory_combo.currentText()

            # Clear and populate combo
            self.directory_combo.clear()

            # Add directories sorted
            sorted_dirs = sorted(list(directories))
            for directory in sorted_dirs:
                self.directory_combo.addItem(directory)

            # Restore selection if it exists
            index = self.directory_combo.findText(current_directory)
            if index >= 0:
                self.directory_combo.setCurrentIndex(index)
            else:
                self.directory_combo.setCurrentText("/ (root)")

            self.log_status(
                f"Found {len(directories)} directories in bucket '{bucket_name}'"
            )

        except Exception as e:
            error_message = f"Failed to retrieve directory list: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)
            self.log_status(f"Error retrieving directories: {str(e)}")

            # Log to error log file
            log_error_dialog(
                title="Directory Retrieval Error",
                message=error_message,
                context=f"Retrieving directory list for bucket '{bucket_name}'",
                component="CloudTab.refresh_directory_list",
                exception=e,
                user_action="Refreshing S3 directory list",
            )

    def create_directory(self):
        """Create a new directory in the selected bucket - routes to provider-specific method"""
        if self.current_provider == "google_gcs":
            self.create_directory_gcs()
        else:
            # Default to AWS S3
            self.create_directory_s3()

    def create_directory_gcs(self):
        """GCS does not support directory creation (uses object prefixes)"""
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Directory Creation Not Applicable",
            "Google Cloud Storage does not use directories.\n\n"
            "Instead, use the directory/folder name as a prefix when uploading files.\n"
            "For example, to create a 'clean-restroom-rental-fl' folder structure,\n"
            "upload files with paths like: clean-restroom-rental-fl/index.html\n\n"
            "The directory structure will be created automatically during deployment.",
        )

    def create_directory_s3(self):
        """Create a new directory in the selected S3 bucket"""
        bucket_name = self._get_actual_bucket_name()
        profile_name = self.profile_combo.currentText()

        if not bucket_name or bucket_name == "No buckets found":
            QMessageBox.warning(
                self, "No Bucket Selected", "Please select a bucket first."
            )
            return

        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(
                self, "No Profile Selected", "Please select an AWS profile first."
            )
            return

        # Get directory name from user
        from PyQt6.QtWidgets import QInputDialog, QLineEdit

        directory_name, ok = QInputDialog.getText(
            self,
            "Create Directory",
            'Enter directory name:\n(e.g., "images" or "css/fonts")',
            QLineEdit.EchoMode.Normal,
            "",
        )

        if not ok or not directory_name.strip():
            return

        # Clean and validate directory name
        directory_name = directory_name.strip()

        # Ensure directory ends with '/' for S3 consistency
        if not directory_name.endswith("/"):
            directory_name += "/"

        # Validate directory name
        if not self._validate_directory_name(directory_name):
            QMessageBox.warning(
                self,
                "Invalid Directory Name",
                "Directory name contains invalid characters.\n"
                "Use only letters, numbers, hyphens, underscores, and forward slashes.",
            )
            return

        try:
            # Get AWS session for the profile
            session = self.credentials_manager._get_session(profile_name)
            if not session:
                QMessageBox.warning(
                    self,
                    "Session Error",
                    "Could not create AWS session for the selected profile.",
                )
                return

            # Set session and create directory
            self.s3_manager.set_session(session)

            # Create directory by uploading a placeholder object
            # S3 doesn't have true directories, so we create a placeholder file
            placeholder_key = directory_name + ".keep"

            try:
                # Upload empty placeholder to create directory structure
                s3_client = session.client("s3")
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=placeholder_key,
                    Body=b"",
                    ContentType="application/octet-stream",
                )

                self.log_status(
                    f"Created directory '{directory_name}' in bucket '{bucket_name}'"
                )

                # Add to directory combo if not already there
                if directory_name not in [
                    self.directory_combo.itemText(i)
                    for i in range(self.directory_combo.count())
                ]:
                    self.directory_combo.addItem(directory_name)

                # Select the newly created directory
                self.directory_combo.setCurrentText(directory_name)

                QMessageBox.information(
                    self,
                    "Directory Created",
                    f"Directory '{directory_name}' created successfully in bucket '{bucket_name}'",
                )

                # Refresh the directory list to show the new directory
                self.refresh_directory_list()

            except Exception as s3_error:
                error_msg = str(s3_error)

                # Provide more helpful error messages for common issues
                if "AccessDenied" in error_msg:
                    if "s3:PutObject" in error_msg:
                        friendly_msg = f"Permission denied: Your AWS profile doesn't have write access to bucket '{bucket_name}'.\n\nPlease check your S3 bucket permissions or contact your AWS administrator."
                    else:
                        friendly_msg = f"Access denied to bucket '{bucket_name}'.\n\nPlease check your AWS permissions or contact your AWS administrator."
                elif "NoSuchBucket" in error_msg:
                    friendly_msg = (
                        f"Bucket '{bucket_name}' does not exist or is not accessible."
                    )
                elif "InvalidBucketName" in error_msg:
                    friendly_msg = f"Invalid bucket name '{bucket_name}'. Please check the bucket name."
                else:
                    friendly_msg = f"S3 operation failed: {error_msg}"

                raise Exception(friendly_msg)

        except Exception as e:
            error_message = f"Failed to create directory: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)
            self.log_status(f"Error creating directory: {str(e)}")

            # Log to error log file
            log_error_dialog(
                title="Directory Creation Error",
                message=error_message,
                context=f"Creating directory '{directory_name}' in bucket '{bucket_name}'",
                component="CloudTab.create_directory",
                exception=e,
                user_action="Creating a new directory in S3 bucket",
            )

    def _validate_directory_name(self, directory_name: str) -> bool:
        """Validate directory name for S3 compatibility"""
        import re

        # Remove trailing slash for validation
        name_to_validate = directory_name.rstrip("/")

        if not name_to_validate:
            return False

        # S3 key naming conventions
        # Allow: letters, numbers, hyphens, underscores, periods, forward slashes
        # Avoid: spaces, special characters that could cause issues
        if not re.match(r"^[a-zA-Z0-9._/-]+$", name_to_validate):
            return False

        # Additional checks
        if name_to_validate.startswith("/") or "//" in name_to_validate:
            return False

        return True

    def on_bucket_selection_changed(self, bucket_name: str):
        """Handle bucket selection change"""
        self.on_bucket_name_changed()

        # Reset to default directory without auto-refreshing (for performance)
        # User can manually click Refresh if they want to see existing directories
        self.directory_combo.clear()
        self.directory_combo.addItem("/ (root)")
        self.directory_combo.setCurrentText("/ (root)")

        # Log that directories need manual refresh if user wants to see existing ones
        actual_bucket_name = self._get_actual_bucket_name()
        if actual_bucket_name and actual_bucket_name != "No buckets found":
            self.log_status(
                f"Bucket '{actual_bucket_name}' selected. Click 'Refresh' to load existing directories."
            )

        # Update status
        if bucket_name and bucket_name != "No buckets found":
            directory = self.directory_combo.currentText()
            self.bucket_status_label.setText(
                f"Bucket: {bucket_name} | Directory: {directory}"
            )
            self.bucket_status_label.setStyleSheet("color: green;")
        else:
            self.bucket_status_label.setText("No bucket configured")
            self.bucket_status_label.setStyleSheet("color: #666;")

    def on_directory_selection_changed(self, directory: str):
        """Handle directory selection change"""
        bucket_name = self._get_actual_bucket_name()

        if bucket_name and bucket_name != "No buckets found" and directory:
            self.bucket_status_label.setText(
                f"Bucket: {bucket_name} | Directory: {directory}"
            )
            self.bucket_status_label.setStyleSheet("color: green;")
        else:
            self.bucket_status_label.setText("No bucket configured")
            self.bucket_status_label.setStyleSheet("color: #666;")

        self.update_deploy_button_state()
        # Auto-save client AWS config
        self.on_aws_config_changed()

    def create_bucket(self):
        """Create cloud storage bucket - routes to provider-specific method"""
        if self.current_provider == "google_gcs":
            self.create_gcs_bucket()
        else:
            # Default to AWS S3
            self.create_s3_bucket()

    def create_gcs_bucket(self):
        """Create GCS bucket with validation and confirmation"""
        from PyQt6.QtWidgets import QMessageBox
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication

        bucket_name = self.bucket_combo.currentText().strip()
        project_id = self.gcs_project_input.text().strip()
        credentials_path = self.gcs_credentials_input.text().strip()
        region = self.gcs_region_combo.currentText().split()[0]

        if not project_id or not credentials_path:
            QMessageBox.warning(
                self,
                "Missing Configuration",
                "Please provide both Project ID and Service Account JSON path.",
            )
            return

        if not bucket_name:
            QMessageBox.warning(self, "No Bucket Name", "Please enter a bucket name")
            return

        try:
            from ...core.deployment.providers import create_provider_from_dict

            # Show progress
            self.setCursor(Qt.CursorShape.WaitCursor)
            self.create_bucket_button.setEnabled(False)
            self.create_bucket_button.setText("Creating...")
            QApplication.processEvents()

            # Create GCS provider config
            config_dict = {
                "provider": "google_gcs",
                "credentials": {
                    "service_account_json": credentials_path,
                    "project_id": project_id,
                },
                "region": region,
            }

            provider = create_provider_from_dict(config_dict)

            # Authenticate
            if not provider.authenticate():
                QMessageBox.warning(
                    self,
                    "Authentication Failed",
                    "Failed to authenticate with Google Cloud Storage.",
                )
                return

            # Check if bucket already exists
            existing_buckets = provider.list_buckets()
            if bucket_name in existing_buckets:
                reply = QMessageBox.question(
                    self,
                    "Bucket Already Exists",
                    f"Bucket '{bucket_name}' already exists in your GCS project.\n\n"
                    f"Do you want to proceed with configuring the existing bucket?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.No:
                    return

                # Configure existing bucket
                if provider.configure_website_hosting(bucket_name):
                    self.log_status(
                        f"Configured existing GCS bucket '{bucket_name}' for static hosting"
                    )
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Bucket '{bucket_name}' configured successfully for website hosting!",
                    )
                    self.refresh_bucket_list()
                else:
                    QMessageBox.critical(
                        self,
                        "Configuration Failed",
                        f"Failed to configure bucket '{bucket_name}' for website hosting.",
                    )
            else:
                # Create new bucket
                if provider.create_bucket(bucket_name):
                    self.log_status(
                        f"Created new GCS bucket '{bucket_name}' in region '{region}'"
                    )

                    # Configure for website hosting
                    if provider.configure_website_hosting(bucket_name):
                        self.log_status(
                            f"Website hosting configured for '{bucket_name}'"
                        )
                        QMessageBox.information(
                            self,
                            "Success",
                            f"Bucket '{bucket_name}' created with HTTPS Support!\n\n"
                            f"The bucket has been configured for static website hosting.",
                        )
                    else:
                        QMessageBox.warning(
                            self,
                            "Configuration Warning",
                            f"Bucket '{bucket_name}' created successfully, but website configuration failed.",
                        )

                    self.refresh_bucket_list()
                else:
                    QMessageBox.critical(
                        self,
                        "Creation Failed",
                        f"Failed to create bucket '{bucket_name}'.",
                    )

        except ImportError:
            QMessageBox.warning(
                self,
                "GCS Support Not Available",
                "Google Cloud Storage support requires the google-cloud-storage library.\n\n"
                "Install it with: pip install google-cloud-storage",
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to create GCS bucket:\n\n{str(e)}"
            )
            self.log_status(f"Error creating GCS bucket: {str(e)}")

        finally:
            # Restore UI state
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.create_bucket_button.setEnabled(True)
            self.create_bucket_button.setText("Create Bucket")

    def create_s3_bucket(self):
        """Create S3 bucket with validation and confirmation"""
        profile_name = self.profile_combo.currentText()
        bucket_name = self._get_actual_bucket_name()
        directory = self.directory_combo.currentText().strip()
        region = self.region_combo.currentText()

        if profile_name == "No profiles configured":
            QMessageBox.warning(
                self, "No Profile", "Please select an AWS profile first"
            )
            return

        if not bucket_name:
            QMessageBox.warning(self, "No Bucket Name", "Please enter a bucket name")
            return

        # Validate bucket name
        is_valid, message = self.s3_manager.validate_bucket_name(bucket_name)
        if not is_valid:
            QMessageBox.warning(self, "Invalid Bucket Name", message)
            return

        # Set active profile and session
        if not self.credentials_manager.set_active_profile(profile_name):
            QMessageBox.warning(self, "Profile Error", "Failed to activate AWS profile")
            return

        session = self.credentials_manager.get_active_session()
        self.s3_manager.set_session(session)

        # Show progress indicator and wait cursor
        self.setCursor(Qt.CursorShape.WaitCursor)
        self.create_bucket_button.setEnabled(False)
        self.create_bucket_button.setText("Creating...")
        QApplication.processEvents()  # Update UI immediately

        # Check if bucket already exists and get confirmation
        try:
            existing_buckets = self.credentials_manager.list_client_buckets(
                profile_name
            )
            bucket_exists = any(
                bucket["name"] == bucket_name for bucket in existing_buckets
            )

            if bucket_exists:
                reply = QMessageBox.question(
                    self,
                    "Bucket Already Exists",
                    f"Bucket '{bucket_name}' already exists.\n\n"
                    f"Do you want to proceed with using the existing bucket?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No,
                )

                if reply == QMessageBox.StandardButton.No:
                    return

                # Bucket exists, check directory if specified
                if directory and directory != "/ (root)":
                    directory_exists = self.check_directory_exists(
                        bucket_name, directory
                    )
                    if directory_exists:
                        dir_reply = QMessageBox.question(
                            self,
                            "Directory Already Exists",
                            f"Directory '{directory}' already exists in bucket '{bucket_name}'.\n\n"
                            f"Do you want to proceed with using the existing directory?\n"
                            f"Files may be overwritten during deployment.",
                            QMessageBox.StandardButton.Yes
                            | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No,
                        )

                        if dir_reply == QMessageBox.StandardButton.No:
                            return

                # Configure the existing bucket for HTTPS static website hosting
                success, message = self.s3_manager.configure_public_website(
                    bucket_name, enable_https=True
                )
                if success:
                    self.log_status(
                        f"Configured existing bucket '{bucket_name}' for static hosting"
                    )
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Bucket '{bucket_name}' configured successfully!",
                    )
                    self.refresh_bucket_list()
                else:
                    QMessageBox.critical(self, "Configuration Failed", message)

            else:
                # Create new bucket
                success, message = self.s3_manager.create_bucket(bucket_name, region)
                if success:
                    self.log_status(
                        f"Created new bucket '{bucket_name}' in region '{region}'"
                    )

                    # Configure new bucket for HTTPS static website hosting
                    self.log_status(
                        f"Configuring bucket '{bucket_name}' for HTTPS website hosting..."
                    )
                    config_success, config_message = (
                        self.s3_manager.configure_public_website(
                            bucket_name, enable_https=True
                        )
                    )

                    if config_success:
                        self.log_status(
                            f"HTTPS website hosting configured for '{bucket_name}'"
                        )
                        QMessageBox.information(
                            self,
                            "Success",
                            f"Bucket '{bucket_name}' created and configured with HTTPS support!\n\n{config_message}",
                        )
                    else:
                        self.log_status(
                            f"Warning: Website configuration failed: {config_message}"
                        )
                        QMessageBox.warning(
                            self,
                            "Configuration Warning",
                            f"Bucket '{bucket_name}' created successfully, but website configuration failed:\n\n{config_message}",
                        )

                    self.refresh_bucket_list()
                else:
                    QMessageBox.critical(self, "Creation Failed", message)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process bucket: {str(e)}")
            self.log_status(f"Error processing bucket: {str(e)}")

        finally:
            # Restore UI state
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.create_bucket_button.setEnabled(True)
            self.create_bucket_button.setText("Create Bucket")

    def check_directory_exists(self, bucket_name: str, directory: str) -> bool:
        """Check if directory exists in bucket"""
        try:
            contents = self.s3_manager.list_bucket_contents(bucket_name)

            # Normalize directory path
            if directory.endswith("/"):
                dir_prefix = directory
            else:
                dir_prefix = directory + "/"

            # Check if any objects start with the directory prefix
            for item in contents:
                if item["key"].startswith(dir_prefix):
                    return True

            return False

        except Exception as e:
            self.log_status(f"Error checking directory existence: {str(e)}")
            return False

    def on_deployment_mode_changed(self):
        """Handle deployment mode change"""
        if self.s3_mode_radio.isChecked():
            # Mode A: S3-only deployment (no CloudFront)
            self.mode_description.setText(
                "S3 Static Website: Direct hosting from S3 bucket with public access (no CloudFront)"
            )

            # Disable CloudFront settings for Mode A
            if self.cloudfront_settings_group:
                self.cloudfront_settings_group.setEnabled(False)
                self.cloudfront_settings_group.setTitle(
                    "CloudFront Distribution (Not Used in Mode A)"
                )
                # Gray out appearance
                self.cloudfront_settings_group.setStyleSheet(
                    "QGroupBox { color: #999999; }"
                )
        else:
            # Mode B: CloudFront + OAC deployment
            self.mode_description.setText(
                "CloudFront + OAC: Production-ready CDN with private bucket access (auto-created)"
            )

            # Enable CloudFront settings for Mode B
            if self.cloudfront_settings_group:
                self.cloudfront_settings_group.setEnabled(True)
                self.cloudfront_settings_group.setTitle(
                    "CloudFront Distribution (Auto-Created)"
                )
                # Restore normal appearance
                self.cloudfront_settings_group.setStyleSheet("")

    def on_site_type_changed(self):
        """Handle site type change (Main Site / Backlink Site / Resource Site)"""
        if not hasattr(self, "main_site_url_input") or self.main_site_url_input is None:
            return  # UI not fully initialized yet

        # Main Site URL only applies to Backlink Site
        is_backlink_site = (
            self.site_type_backlink_radio is not None
            and self.site_type_backlink_radio.isChecked()
        )
        is_resource_site = (
            self.site_type_resource_radio is not None
            and self.site_type_resource_radio.isChecked()
        )
        self.main_site_url_input.setEnabled(is_backlink_site)

        if not is_backlink_site:
            self.main_site_url_input.clear()

        # Update contextual help text
        if hasattr(self, "site_type_help_label") and self.site_type_help_label:
            if is_backlink_site:
                self.site_type_help_label.setText(
                    "Backlink Site: A satellite or city-specific site. Canonical "
                    "URLs point to the Main Site URL you enter below, which "
                    "consolidates SEO authority on your primary domain. Each city "
                    "page links back to the main site."
                )
            elif is_resource_site:
                self.site_type_help_label.setText(
                    "Resource Site: An independent topical authority site (e.g. "
                    "a buyer guide or industry reference). Appears editorially "
                    "neutral. Fill in the 'Resource Site' tab with identity, "
                    "editorial mission, money-site attribution, and authority "
                    "sources. Product Categories drive comparison guide pages."
                )
            else:
                self.site_type_help_label.setText(
                    "Main Site: Your primary business website. All canonical URLs "
                    "point here. Use this for your main customer-facing presence."
                )

    def update_deploy_button_state(self):
        """Update deploy button enabled state"""
        if not hasattr(self, "deploy_button") or self.deploy_button is None:
            return  # Button not yet created

        profile_selected = self.profile_combo.currentText() != "No profiles configured"
        bucket_name = self._get_actual_bucket_name()
        bucket_configured = bool(bucket_name) and (bucket_name != "No buckets found")

        self.deploy_button.setEnabled(profile_selected and bucket_configured)

    def start_deployment(self):
        """Start website deployment - implements test-file-first workflow"""
        from PyQt6.QtWidgets import QMessageBox

        # Check if generation is in progress from first deployment
        if hasattr(self, "_generation_in_progress") and self._generation_in_progress:
            # User clicked Deploy while generation is in progress
            # Check if they've now selected an output directory (which means generation completed)
            local_path = self.local_path_input.text().strip()
            if (
                local_path
                and Path(local_path).exists()
                and (Path(local_path) / "index.html").exists()
            ):
                # Generation completed! Clear flag and proceed with deployment
                self._generation_in_progress = False
                self.log_status(
                    f"Generation completed. Ready to deploy from: {local_path}"
                )
                # Continue to deployment below
            else:
                # Generation still in progress or failed
                QMessageBox.warning(
                    self,
                    "Generation In Progress",
                    "Website generation is still in progress.\n\n"
                    "Please wait for the generation to complete before deploying.\n"
                    "You'll see a completion dialog when it's ready.\n\n"
                    "After generation completes, you may need to manually set the\n"
                    "Local Website Path field to your output directory before deploying.",
                )
                return

        # Get the local website path
        local_path = self.local_path_input.text().strip()

        # Check if this is first deployment (no website generated yet)
        if not local_path or not Path(local_path).exists():
            # First deployment workflow: test file -> generate -> deploy
            self._handle_first_deployment()
        else:
            # Subsequent deployment: regenerate -> deploy
            self._handle_subsequent_deployment(local_path)

    def _handle_first_deployment(self):
        """Handle first-time deployment with test file workflow"""
        from PyQt6.QtWidgets import QMessageBox

        # Check provider type first
        if self.current_provider == "google_gcs":
            # GCS deployments: ask user to generate website first
            QMessageBox.information(
                self,
                "First Deployment",
                "This appears to be your first deployment.\n\n"
                "Please generate a website first using the main application, "
                "then return to this tab to deploy it to Google Cloud Storage.\n\n"
                "The deployment URL will be available after the first upload.",
            )
            return

        # AWS-specific: Only support CloudFront Mode B for first deployment canonical URL workflow
        is_mode_b = self.cloudfront_mode_radio.isChecked()
        if not is_mode_b:
            QMessageBox.information(
                self,
                "First Deployment",
                "This appears to be your first deployment.\n\n"
                "Please generate a website first using the main application, "
                "then return to this tab to deploy it.\n\n"
                "For Mode A (S3-only), the canonical URL workflow is not automated.",
            )
            return

        # Show message confirming first deployment workflow
        reply = QMessageBox.question(
            self,
            "First Deployment",
            "This website has not been deployed yet.\n\n"
            "The app will:\n"
            "1. Deploy a test file to determine the CloudFront URL\n"
            "2. Update your config with the CloudFront URL\n"
            "3. Trigger website generation (you'll select output folder)\n"
            "4. After generation completes, deploy the full website\n\n"
            "Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Step 1: Deploy test file to get CloudFront URL
        self.log_status("Step 1: Deploying test file to determine CloudFront URL...")
        cloudfront_url = self._deploy_test_file_and_get_url()

        if not cloudfront_url:
            QMessageBox.critical(
                self,
                "Deployment Failed",
                "Failed to deploy test file and retrieve CloudFront URL.\n"
                "Please check the logs and try again.",
            )
            return

        self.log_status(f"CloudFront URL determined: {cloudfront_url}")

        # Step 2: Update config with CloudFront URL
        self.log_status("Step 2: Updating config with CloudFront URL...")
        if not self._update_config_deployment_url(cloudfront_url):
            QMessageBox.critical(
                self,
                "Configuration Update Failed",
                "Failed to update configuration with CloudFront URL.\n"
                "Please update the deployment_url manually in your config.",
            )
            return

        # Step 3: Generate website with correct canonical URLs
        self.log_status("Step 3: Generating website with correct canonical URLs...")

        # Find parent window and trigger generation
        parent_window = self.parent()
        while parent_window and not hasattr(parent_window, "generate_website"):
            parent_window = parent_window.parent()

        if not parent_window or not hasattr(parent_window, "generate_website"):
            QMessageBox.critical(
                self,
                "Generation Failed",
                "Cannot trigger website generation: Main window not found.\n"
                "Please generate the website manually.",
            )
            return

        # Set flag to block deployment during generation
        self._generation_in_progress = True
        self._pending_output_dir = None  # Will be set by user during generation

        # Show instructions to user
        QMessageBox.information(
            self,
            "Step 3: Generate Website",
            f"CloudFront URL determined: {cloudfront_url}\n"
            f"Config updated successfully!\n\n"
            f"NEXT STEPS:\n"
            f"1. Click OK to start website generation\n"
            f"2. Select output folder when prompted\n"
            f"   (Recommended: output/clients/[client-name])\n"
            f"3. Wait for generation to complete (several minutes)\n"
            f"4. After generation dialog closes, return to Cloud Deploy tab\n"
            f"5. Click 'Deploy Website' to deploy the generated site\n\n"
            f"IMPORTANT: Do NOT click 'Deploy Website' until generation completes!\n"
            f"The website will be generated with correct canonical URLs.",
        )

        # Trigger generation
        parent_window.generate_website()

        # Note: local_path will be set when user clicks Deploy after generation completes

    def _handle_subsequent_deployment(self, local_path: str):
        """Handle subsequent deployment with regeneration confirmation"""
        from PyQt6.QtWidgets import QMessageBox

        # Show generation confirmation dialog (per webgen.txt workflow)
        reply = QMessageBox.information(
            self,
            "Website Generation Confirmation",
            f"The website will be regenerated and deployed.\n\n"
            f"Output folder: {local_path}\n\n"
            f"Click OK to continue.",
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Ok,
        )

        if reply == QMessageBox.StandardButton.Cancel:
            self.log_status("Deployment cancelled by user")
            return

        # Trigger regeneration
        parent_window = self.parent()
        while parent_window and not hasattr(parent_window, "generate_website"):
            parent_window = parent_window.parent()

        if parent_window and hasattr(parent_window, "generate_website"):
            self.log_status("Regenerating website...")
            parent_window.generate_website()

            QMessageBox.information(
                self,
                "Generation Started",
                "Website regeneration started.\n\n"
                "After generation completes, return to the Cloud Deploy tab\n"
                "and click 'Deploy Website' to deploy the updated site.",
            )
        else:
            # Fallback: Deploy existing website if can't regenerate
            QMessageBox.warning(
                self,
                "Cannot Regenerate",
                "Cannot trigger website regeneration (main window not found).\n\n"
                "Deploying existing website files instead.\n"
                "To regenerate, use the main application first.",
            )
            self.deploy_website(local_path)

    def _deploy_test_file_and_get_url(self) -> str:
        """Deploy a test file to S3/CloudFront and return the CloudFront URL"""
        import tempfile
        from pathlib import Path

        # Get deployment settings
        profile_name = self.profile_combo.currentText()
        bucket_name = self._get_actual_bucket_name()
        directory = self.directory_combo.currentText().strip()
        if directory == "/ (root)" or directory == "/":
            directory = ""

        if not profile_name or not bucket_name:
            self.log_status("Error: Missing AWS profile or bucket name")
            return ""

        try:
            # Create temporary test file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8"
            ) as tf:
                tf.write(
                    """<!DOCTYPE html>
<html>
<head>
    <title>Test Deployment</title>
</head>
<body>
    <h1>CloudFront Test File</h1>
    <p>This is a test file to determine the CloudFront distribution URL.</p>
</body>
</html>"""
                )
                test_file_path = tf.name

            test_file = Path(test_file_path)

            # Activate AWS profile
            if not self.credentials_manager.set_active_profile(profile_name):
                self.log_status("Error: Failed to activate AWS profile")
                test_file.unlink()
                return ""

            session = self.credentials_manager.get_active_session()
            self.s3_manager.set_session(session)

            # Configure bucket for static website hosting
            success, message = self.s3_manager.configure_public_website(bucket_name)
            if not success:
                self.log_status(f"Error configuring bucket: {message}")
                test_file.unlink()
                return ""

            # Get or create CloudFront distribution
            comment = f"Auto-created for {bucket_name}"
            if directory:
                comment += f" (directory: {directory})"

            success, dist_id, cf_domain, is_new, msg = (
                self.s3_manager.get_or_create_distribution(
                    bucket_name=bucket_name, origin_path=directory, comment=comment
                )
            )

            if not success:
                self.log_status(f"Error: {msg}")
                test_file.unlink()
                return ""

            # Store distribution ID for later
            self.distribution_id_input.setText(dist_id)

            # Upload test file to S3
            s3 = self.s3_manager.session.client("s3")
            s3_key = "test.html"
            if directory:
                s3_key = f"{directory.rstrip('/')}/{s3_key}"

            s3.upload_file(
                str(test_file),
                bucket_name,
                s3_key,
                ExtraArgs={
                    "ContentType": "text/html",
                    "CacheControl": "public, max-age=31536000, immutable",
                },
            )

            self.log_status(f"Test file uploaded to s3://{bucket_name}/{s3_key}")

            # Clean up temp file
            test_file.unlink()

            # Return CloudFront URL
            cloudfront_url = f"https://{cf_domain}"
            return cloudfront_url

        except Exception as e:
            self.log_status(f"Error deploying test file: {str(e)}")
            if test_file_path and Path(test_file_path).exists():
                Path(test_file_path).unlink()
            return ""

    def _update_config_deployment_url(self, cloudfront_url: str) -> bool:
        """Update config file with deployment_url"""
        import yaml
        from pathlib import Path

        try:
            # Find main window
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, "current_config_file"):
                parent_window = parent_window.parent()

            if not parent_window or not parent_window.current_config_file:
                self.log_status("Error: No config file loaded")
                return False

            config_file = Path(parent_window.current_config_file)
            if not config_file.exists():
                self.log_status(f"Error: Config file not found: {config_file}")
                return False

            # Load config YAML
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            # Update deployment_url
            if "cloud" not in config_data:
                config_data["cloud"] = {}
            config_data["cloud"]["deployment_url"] = cloudfront_url

            # Save config
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    config_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )

            self.log_status(f"Config updated: deployment_url = {cloudfront_url}")

            # CRITICAL: Update Cloud Tab's in-memory config to prevent auto-save from overwriting
            if (
                hasattr(self, "current_client_aws_config")
                and self.current_client_aws_config
            ):
                self.current_client_aws_config.deployment_url = cloudfront_url
                self.log_status(
                    "Cloud Tab in-memory config updated with deployment_url"
                )

            # Reload config in parent window
            if hasattr(parent_window, "load_config_file"):
                parent_window.load_config_file(str(config_file))
                self.log_status("Config reloaded in UI")

            # Regenerate sitemap.xml with correct CloudFront URL
            self.log_status("Regenerating sitemap.xml with CloudFront URL...")
            if self._regenerate_and_upload_sitemap(config_file, cloudfront_url):
                self.log_status("Sitemap.xml updated and uploaded successfully")
            else:
                self.log_status("Warning: Failed to update sitemap.xml")

            return True

        except Exception as e:
            self.log_status(f"Error updating config: {str(e)}")
            return False

    def _update_config_and_sitemap_for_deployment(self, deployment_url: str) -> bool:
        """Update config with deployment URL and regenerate sitemap (Mode A & B)"""
        import yaml
        from pathlib import Path

        try:
            # Find main window and config file
            parent_window = self.parent()
            while parent_window and not hasattr(parent_window, "current_config_file"):
                parent_window = parent_window.parent()

            if not parent_window or not parent_window.current_config_file:
                self.log_status("Info: No config file loaded, skipping sitemap update")
                return False

            config_file = Path(parent_window.current_config_file)
            if not config_file.exists():
                self.log_status(f"Info: Config file not found: {config_file}")
                return False

            # Load and update config
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if "cloud" not in config_data:
                config_data["cloud"] = {}

            # Update deployment_url in config
            config_data["cloud"]["deployment_url"] = deployment_url

            # Save updated config
            with open(config_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    config_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )

            self.log_status(f"Config updated: deployment_url = {deployment_url}")

            # Update in-memory config
            if (
                hasattr(self, "current_client_aws_config")
                and self.current_client_aws_config
            ):
                self.current_client_aws_config.deployment_url = deployment_url

            # Regenerate sitemap with correct URL
            self.log_status("Regenerating sitemap.xml with deployment URL...")
            if self._regenerate_and_upload_sitemap(config_file, deployment_url):
                self.log_status("Sitemap.xml updated successfully")
                return True
            else:
                self.log_status("Warning: Failed to update sitemap.xml")
                return False

        except Exception as e:
            self.log_status(f"Error updating config/sitemap: {str(e)}")
            return False

    def _regenerate_and_upload_sitemap(
        self, config_file: Path, deployment_url: str
    ) -> bool:
        """Regenerate sitemap.xml with deployment URL and upload to S3"""
        try:
            from pathlib import Path
            from src.core.config.parser import ConfigParser
            from src.core.generators.page_generator import PageGenerator

            # Load updated config
            parser = ConfigParser()
            config = parser.parse(str(config_file))

            # Verify deployment_url is set
            if not config.cloud.deployment_url:
                config.cloud.deployment_url = deployment_url

            # Generate updated sitemap
            generator = PageGenerator()
            sitemap_content = generator._generate_sitemap(config)

            # Find output directory
            output_dir = None
            if (
                hasattr(self, "last_generated_website_path")
                and self.last_generated_website_path
            ):
                output_dir = Path(self.last_generated_website_path)
            else:
                # Try to infer from config
                client_name = config.business.business_name.lower().replace(" ", "_")
                output_dir = Path("output") / "clients" / client_name

            if not output_dir or not output_dir.exists():
                self.log_status(f"Error: Output directory not found: {output_dir}")
                return False

            # Write updated sitemap.xml
            sitemap_path = output_dir / "sitemap.xml"
            with open(sitemap_path, "w", encoding="utf-8") as f:
                f.write(sitemap_content)

            self.log_status(f"Sitemap.xml regenerated at {sitemap_path}")

            # Upload to S3
            bucket_name = self._get_actual_bucket_name()
            if not bucket_name:
                self.log_status("Error: No bucket name available")
                return False

            # Get S3 client
            s3_client = self._get_s3_client()
            if not s3_client:
                self.log_status("Error: Failed to get S3 client")
                return False

            # Upload sitemap.xml
            try:
                s3_client.upload_file(
                    str(sitemap_path),
                    bucket_name,
                    "sitemap.xml",
                    ExtraArgs={"ContentType": "application/xml"},
                )
                self.log_status(
                    f"Uploaded sitemap.xml to s3://{bucket_name}/sitemap.xml"
                )
                return True

            except Exception as e:
                self.log_status(f"Error uploading sitemap.xml: {str(e)}")
                return False

        except Exception as e:
            self.log_status(f"Error regenerating sitemap: {str(e)}")
            import traceback

            self.log_status(traceback.format_exc())
            return False

    def deploy_website(self, website_path: str):
        """Deploy generated website to cloud - routes to provider-specific method"""
        if self.current_provider == "google_gcs":
            self.deploy_website_gcs(website_path)
        else:
            # Default to AWS S3
            self.deploy_website_s3(website_path)

    def deploy_website_gcs(self, website_path: str):
        """Deploy generated website to Google Cloud Storage"""
        from PyQt6.QtWidgets import QMessageBox

        bucket_name = self.bucket_combo.currentText().strip()
        project_id = self.gcs_project_input.text().strip()
        credentials_path = self.gcs_credentials_input.text().strip()
        region = self.gcs_region_combo.currentText().split()[0]

        if not project_id or not credentials_path:
            self.log_status("Error: GCS credentials not configured")
            QMessageBox.warning(
                self, "Missing Configuration", "Please configure GCS credentials first."
            )
            return

        if not bucket_name:
            self.log_status("Error: No bucket name configured")
            return

        try:
            from ...core.deployment.providers import create_provider_from_dict
            from pathlib import Path

            self.log_status(f"Starting GCS deployment to bucket '{bucket_name}'...")

            # Create GCS provider config
            config_dict = {
                "provider": "google_gcs",
                "credentials": {
                    "service_account_json": credentials_path,
                    "project_id": project_id,
                },
                "region": region,
            }

            provider = create_provider_from_dict(config_dict)

            # Authenticate
            if not provider.authenticate():
                self.log_status("Error: Failed to authenticate with GCS")
                QMessageBox.warning(
                    self,
                    "Authentication Failed",
                    "Failed to authenticate with Google Cloud Storage.",
                )
                return

            self.log_status("GCS authentication successful")

            # Configure bucket for website hosting
            self.log_status("Configuring bucket for static website hosting...")
            if not provider.configure_website_hosting(bucket_name):
                self.log_status("Warning: Failed to configure website hosting")

            # Upload website files
            self.log_status(f"Uploading files from {website_path}...")

            # Progress callback
            def progress_callback(current, total, filename):
                percent = int((current / total) * 100)
                self.log_status(
                    f"Uploading [{current}/{total}] {percent}% - {filename}"
                )

            result = provider.upload_directory(
                Path(website_path),
                bucket_name,
                prefix="",
                progress_callback=progress_callback,
            )

            if result.success:
                self.log_status(
                    f"Deployment successful! Uploaded {result.files_uploaded} files"
                )
                website_url = result.website_url

                # Create deployment config and emit signal
                from ...core.config.models import DeploymentConfig
                from datetime import datetime

                # Snapshot industry from current config
                snapshotted_industry = None
                if hasattr(self, "current_config") and self.current_config:
                    snapshotted_industry = self.current_config.business.industry

                # Use custom friendly name if provided, otherwise auto-generate
                custom_name = (
                    self.friendly_name_input.text().strip()
                    if hasattr(self, "friendly_name_input")
                    else ""
                )
                if custom_name:
                    friendly_name = custom_name
                else:
                    friendly_name = self._generate_default_friendly_name(
                        business_name=(
                            self.current_config.business.business_name
                            if self.current_config
                            else None
                        ),
                        industry=snapshotted_industry,
                        directory="",
                    )

                # Generate unique deployment ID with timestamp to preserve full history
                timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
                deployment_id = f"{bucket_name}-{timestamp}"
                deployment = DeploymentConfig(
                    deployment_id=deployment_id,
                    bucket=bucket_name,
                    directory="",
                    region=region,
                    mode="gcs",
                    cloudfront_distribution_id=None,
                    cloudfront_domain=None,
                    last_deployed=datetime.utcnow().isoformat() + "Z",
                    deployment_url=website_url,
                    meta_tags=self.get_meta_tags_from_table(),
                    friendly_name=friendly_name,
                    industry=snapshotted_industry,
                )

                # Emit signal for parent to handle
                self.deployment_created.emit(deployment)
                self.log_status(f"Deployment record created: {deployment_id}")

                # Clear friendly name input for next deployment
                if hasattr(self, "friendly_name_input"):
                    self.friendly_name_input.clear()

                self.log_status(f"Website URL: {website_url}")

                # Update website URL label in UI
                if self.website_url_label:
                    self.website_url_label.setText(
                        f'<a href="{website_url}">View Website: {website_url}</a>'
                    )

                QMessageBox.information(
                    self,
                    "Deployment Successful",
                    f"Website deployed successfully to GCS!\n\n"
                    f"Files uploaded: {result.files_uploaded}\n"
                    f"Website URL: {website_url}",
                )
            else:
                self.log_status(f"Deployment failed: {', '.join(result.errors)}")
                QMessageBox.critical(
                    self,
                    "Deployment Failed",
                    f"Failed to deploy website:\n\n{', '.join(result.errors)}",
                )

        except Exception as e:
            self.log_status(f"Error during GCS deployment: {str(e)}")
            QMessageBox.critical(
                self,
                "Deployment Error",
                f"Failed to deploy website to GCS:\n\n{str(e)}",
            )

    def deploy_website_s3(self, website_path: str):
        """Deploy generated website to AWS S3"""
        profile_name = self.profile_combo.currentText()
        bucket_name = self._get_actual_bucket_name()

        if not profile_name or profile_name == "No profiles configured":
            self.log_status("Error: No AWS profile selected")
            return

        if not bucket_name:
            self.log_status("Error: No bucket name configured")
            return

        # Activate profile
        if not self.credentials_manager.set_active_profile(profile_name):
            self.log_status("Error: Failed to activate AWS profile")
            return

        session = self.credentials_manager.get_active_session()
        self.s3_manager.set_session(session)

        # Get directory from UI
        directory = self.directory_combo.currentText().strip()
        if directory == "/ (root)" or directory == "/":
            directory = ""  # Root directory = empty prefix

        # Check deployment mode - CRITICAL: bucket configuration differs by mode
        is_mode_a = self.s3_mode_radio.isChecked()

        # Configure bucket based on deployment mode
        if is_mode_a:
            # Mode A: Configure bucket for public static website hosting
            self.log_status(
                "Mode A: Configuring bucket for public static website hosting..."
            )
            success, message = self.s3_manager.configure_public_website(bucket_name)

            if not success:
                self.log_status(f"Error: {message}")
                return

            self.log_status(message)
        else:
            # Mode B: Skip public configuration - OAC will handle permissions
            # Bucket will remain private and CloudFront will access via OAC
            self.log_status(
                "Mode B: Bucket will be configured for private access with CloudFront OAC"
            )

        # Get CloudFront settings (only for Mode B)
        if is_mode_a:
            # Mode A: S3-only deployment (no CloudFront)
            distribution_id = ""
            auto_invalidate = False
            cloudfront_domain = ""
            self.current_cloudfront_domain = ""  # No CloudFront for Mode A
            self.log_status("Mode A: S3-only deployment (CloudFront disabled)")
        else:
            # Mode B: CloudFront + OAC deployment (auto-create distribution)
            self.log_status(
                "Mode B: CloudFront + OAC deployment (auto-creating distribution...)"
            )

            # Auto-create or find existing CloudFront distribution
            comment = f"Auto-created for {bucket_name}"
            if directory:
                comment += f" (directory: {directory})"

            success, dist_id, cf_domain, is_new, msg = (
                self.s3_manager.get_or_create_distribution(
                    bucket_name=bucket_name, origin_path=directory, comment=comment
                )
            )

            if not success:
                self.log_status(f"Error: {msg}")
                return

            distribution_id = dist_id
            cloudfront_domain = cf_domain
            auto_invalidate = True  # Always invalidate cache for Mode B

            # Store CloudFront domain for deployment_finished() to use
            self.current_cloudfront_domain = cloudfront_domain

            # Log distribution info
            if is_new:
                self.log_status(
                    f"Created new CloudFront distribution: {distribution_id}"
                )
            else:
                self.log_status(f"Reusing existing distribution: {distribution_id}")

            self.log_status(f"CloudFront domain: {cloudfront_domain}")

            # Update UI with distribution ID
            self.distribution_id_input.setText(distribution_id)

            # CRITICAL: Enable public access blocks for private bucket (Mode B only)
            # OAC policy is now in place, safe to block public access
            self.log_status("Enabling public access blocks for private bucket...")
            try:
                s3_client = self.s3_manager._get_s3_client()
                s3_client.put_public_access_block(
                    Bucket=bucket_name,
                    PublicAccessBlockConfiguration={
                        "BlockPublicAcls": True,
                        "IgnorePublicAcls": True,
                        "BlockPublicPolicy": True,
                        "RestrictPublicBuckets": True,
                    },
                )
                self.log_status("Public access blocks enabled - bucket is now private")
            except Exception as e:
                self.log_status(
                    f"Warning: Could not enable public access blocks: {str(e)}"
                )
                self.log_status(
                    "Bucket policy is configured correctly, but public access blocks may need manual configuration"
                )

        # Start deployment worker
        self.deployment_worker = DeploymentWorker(
            self.s3_manager,
            website_path,
            bucket_name,
            s3_directory=directory,
            distribution_id=distribution_id,
            auto_invalidate=auto_invalidate,
        )
        self.deployment_worker.progress_updated.connect(self.update_deployment_progress)
        self.deployment_worker.deployment_completed.connect(self.deployment_finished)

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.deploy_button.setEnabled(False)

        self.log_status("Starting website deployment...")
        self.deployment_worker.start()

    def update_deployment_progress(self, progress: UploadProgress):
        """Update deployment progress"""
        if progress.total_files > 0:
            percentage = int((progress.uploaded_files / progress.total_files) * 100)
            self.progress_bar.setValue(percentage)

        if progress.current_file:
            self.log_status(f"Uploading: {progress.current_file}")

    def deployment_finished(self, result: UploadResult):
        """Handle deployment completion"""
        self.progress_bar.setVisible(False)
        self.deploy_button.setEnabled(True)

        if result.success:
            # Use website URL from deployment result (includes directory path)
            website_url = result.website_url

            # Fallback: generate URL if not provided in result
            if not website_url:
                bucket_name = self._get_actual_bucket_name()
                region = self.region_combo.currentText()
                directory = self.directory_combo.currentText().strip()
                if directory == "/ (root)" or directory == "/":
                    directory = ""

                # Check deployment mode to generate correct URL
                is_mode_a = self.s3_mode_radio.isChecked()

                if is_mode_a:
                    # Mode A: S3 website URL only (no CloudFront)
                    website_url = self.s3_manager.get_website_url(
                        bucket_name, region, prefer_https=False
                    )

                    # Mode A: Append directory to URL (S3 doesn't use origin path)
                    if website_url and directory:
                        website_url = website_url.rstrip("/")
                        website_url = f"{website_url}/{directory}"
                else:
                    # Mode B: Use stored CloudFront domain from deployment
                    if (
                        hasattr(self, "current_cloudfront_domain")
                        and self.current_cloudfront_domain
                    ):
                        website_url = f"https://{self.current_cloudfront_domain}/"
                    else:
                        # Fallback: use get_website_url (shouldn't happen with v3.2.0)
                        website_url = self.s3_manager.get_website_url(
                            bucket_name, region, prefer_https=True
                        )

                    # Mode B: DO NOT append directory - CloudFront origin path already includes it!
                    # The distribution's origin path is set to /directory, so we access the root URL
                    # CloudFront will automatically prepend the origin path when fetching from S3

            if website_url:
                self.website_url_label.setText(
                    f'<a href="{website_url}">View Website: {website_url}</a>'
                )

            self.log_status(f"Deployment completed successfully! {result.message}")

            # Create/update deployment record with current meta tags
            bucket_name = self._get_actual_bucket_name()
            directory = self.directory_combo.currentText().strip()
            if directory == "/ (root)" or directory == "/":
                directory = ""

            # Generate unique deployment ID with timestamp to preserve full history
            # Each deployment creates a new entry, even when deploying to same bucket/directory
            timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
            deployment_id = f"{bucket_name}"
            if directory:
                deployment_id += f"-{directory}"
            deployment_id += f"-{timestamp}"

            # Get mode and CloudFront settings
            mode = "s3" if self.s3_mode_radio.isChecked() else "cloudfront"
            distribution_id = (
                self.distribution_id_input.text().strip()
                if mode == "cloudfront"
                else ""
            )
            cloudfront_domain = ""

            # Extract CloudFront domain from distribution_id if available
            if distribution_id and mode == "cloudfront":
                try:
                    cloudfront = self.s3_manager.session.client("cloudfront")
                    response = cloudfront.get_distribution(Id=distribution_id)
                    cloudfront_domain = response["Distribution"]["DomainName"]
                except Exception:
                    pass  # CloudFront domain extraction failed, will use deployment URL

            # Get current meta tags from UI
            meta_tags = self.get_meta_tags_from_table()

            # Snapshot industry from current config
            snapshotted_industry = None
            if hasattr(self, "current_config") and self.current_config:
                snapshotted_industry = self.current_config.business.industry

            # Use custom friendly name if provided, otherwise auto-generate
            custom_name = (
                self.friendly_name_input.text().strip()
                if hasattr(self, "friendly_name_input")
                else ""
            )
            if custom_name:
                friendly_name = custom_name
            else:
                friendly_name = self._generate_default_friendly_name(
                    business_name=(
                        self.current_config.business.business_name
                        if self.current_config
                        else None
                    ),
                    industry=snapshotted_industry,
                    directory=directory,
                )

            # Create deployment config
            deployment = DeploymentConfig(
                deployment_id=deployment_id,
                bucket=bucket_name,
                directory=directory,
                region=self.region_combo.currentText(),
                mode=mode,
                cloudfront_distribution_id=(
                    distribution_id if mode == "cloudfront" else None
                ),
                cloudfront_domain=cloudfront_domain if mode == "cloudfront" else None,
                last_deployed=datetime.utcnow().isoformat() + "Z",
                deployment_url=website_url,
                meta_tags=meta_tags,
                friendly_name=friendly_name,
                industry=snapshotted_industry,
            )

            # Emit signal for parent to handle
            self.deployment_created.emit(deployment)
            self.log_status(f"Deployment record created: {deployment_id}")

            # Update config with deployment URL and regenerate sitemap (Mode A & B)
            if website_url:
                self._update_config_and_sitemap_for_deployment(website_url)

            # Clear friendly name input for next deployment
            if hasattr(self, "friendly_name_input"):
                self.friendly_name_input.clear()

            # Show success message
            success_msg = (
                f"Website deployed successfully!\n\n"
                f"URL: {website_url or 'Check AWS console for URL'}\n"
                f"Files uploaded: {len(result.uploaded_files)}"
            )

            QMessageBox.information(self, "Deployment Successful", success_msg)
        else:
            self.log_status(f"Deployment failed: {result.message}")
            QMessageBox.warning(self, "Deployment Failed", result.message)

    def _generate_default_friendly_name(
        self, business_name: Optional[str], industry: Optional[str], directory: str
    ) -> str:
        """
        Generate user-friendly default name for deployment.
        Format: "{Business Name} {Industry} MM/DD/YYYY"
        Example: "United Structural Systems Residential Foundation Repair 12/20/2025"
        """
        from datetime import datetime

        now = datetime.now()
        date_str = now.strftime("%m/%d/%Y")  # MM/DD/YYYY format

        parts = []

        if business_name:
            # Use FULL business name (no abbreviation or truncation)
            parts.append(business_name)
        else:
            # Fallback: use directory
            clean_dir = directory.replace("-", " ").replace("_", " ").title()
            parts.append(clean_dir)

        if industry:
            # Use FULL industry (no truncation)
            parts.append(industry)

        parts.append(date_str)

        return " ".join(parts)

    def log_status(self, message: str):
        """Add message to status log"""
        from datetime import datetime

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"

        # Safety check - status_text might not be initialized yet
        if self.status_text is not None:
            self.status_text.append(formatted_message)
        else:
            # Fallback to print if UI not ready
            logger.debug(f"CloudTab: {formatted_message}")

    # Meta Tags CRUD Methods

    def add_or_update_meta_tag(self):
        """Add or update a meta tag from full HTML tag"""
        from PyQt6.QtWidgets import QTableWidgetItem
        import re

        full_tag = self.meta_tag_input.text().strip()

        if not full_tag:
            QMessageBox.warning(
                self, "Invalid Input", "Please paste a complete meta tag"
            )
            return

        # Parse the meta tag to extract name and content
        # Pattern matches: <meta name="..." content="..." /> or similar variations
        name_match = re.search(r'name=["\']([^"\']+)["\']', full_tag)
        content_match = re.search(r'content=["\']([^"\']+)["\']', full_tag)

        if not name_match or not content_match:
            QMessageBox.warning(
                self,
                "Invalid Meta Tag",
                'Could not parse meta tag. Expected format:\n<meta name="tag-name" content="tag-content" />',
            )
            return

        tag_name = name_match.group(1)
        content_match.group(1)

        # Check if tag already exists
        existing_row = -1
        for row in range(self.meta_tags_table.rowCount()):
            existing_tag = self.meta_tags_table.item(row, 0).text()
            if tag_name in existing_tag:
                existing_row = row
                break

        if existing_row >= 0:
            # Update existing tag
            self.meta_tags_table.item(existing_row, 0).setText(full_tag)
            self.log_status(f"Updated meta tag: {tag_name}")
        else:
            # Add new tag
            row = self.meta_tags_table.rowCount()
            self.meta_tags_table.insertRow(row)
            self.meta_tags_table.setItem(row, 0, QTableWidgetItem(full_tag))
            self.log_status(f"Added meta tag: {tag_name}")

        # Clear input field
        self.meta_tag_input.clear()

        # Mark configuration as changed
        if hasattr(self, "config_changed"):
            self.config_changed.emit()

    def remove_meta_tag(self):
        """Remove selected meta tag"""
        import re

        selected_items = self.meta_tags_table.selectedItems()
        if not selected_items:
            return

        row = selected_items[0].row()
        full_tag = self.meta_tags_table.item(row, 0).text()

        # Extract tag name for display
        name_match = re.search(r'name=["\']([^"\']+)["\']', full_tag)
        tag_name = name_match.group(1) if name_match else "tag"

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to remove the meta tag '{tag_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.meta_tags_table.removeRow(row)
            self.log_status(f"Removed meta tag: {tag_name}")

            # Clear input field
            self.meta_tag_input.clear()
            self.remove_meta_tag_button.setEnabled(False)

            # Mark configuration as changed
            if hasattr(self, "config_changed"):
                self.config_changed.emit()

    def on_check_oac_status(self):
        """Check OAC status for entered distribution ID (v3.2.0 diagnostic tool)"""
        distribution_id = self.distribution_id_input.text().strip()

        if not distribution_id:
            self.oac_status_label.setText("⚠️ Enter a distribution ID first")
            self.oac_status_label.setStyleSheet(
                "font-size: 10px; padding: 5px; color: #ff9900; background-color: #fff3cd;"
            )
            return

        # Check if profile is selected
        profile_name = self.profile_combo.currentText()
        if not profile_name or profile_name == "No profiles configured":
            self.oac_status_label.setText("⚠️ Select an AWS profile first")
            self.oac_status_label.setStyleSheet(
                "font-size: 10px; padding: 5px; color: #ff9900; background-color: #fff3cd;"
            )
            return

        # Activate profile and check OAC
        if not self.credentials_manager.set_active_profile(profile_name):
            self.oac_status_label.setText("❌ Failed to activate AWS profile")
            self.oac_status_label.setStyleSheet(
                "font-size: 10px; padding: 5px; color: #cc0000; background-color: #ffdddd;"
            )
            return

        session = self.credentials_manager.get_active_session()
        self.s3_manager.set_session(session)

        self.log_status(f"Checking OAC status for distribution: {distribution_id}...")
        self.oac_status_label.setText("⏳ Checking OAC status...")
        self.oac_status_label.setStyleSheet(
            "font-size: 10px; padding: 5px; color: #0066cc; background-color: #e6f2ff;"
        )

        # Check OAC status
        success, has_oac, message = self.s3_manager.check_distribution_oac_status(
            distribution_id
        )

        if not success:
            self.oac_status_label.setText(f"❌ {message}")
            self.oac_status_label.setStyleSheet(
                "font-size: 10px; padding: 5px; color: #cc0000; background-color: #ffdddd;"
            )
            self.log_status(f"OAC check failed: {message}")
        elif has_oac:
            self.oac_status_label.setText(f"✅ {message}")
            self.oac_status_label.setStyleSheet(
                "font-size: 10px; padding: 5px; color: #006600; background-color: #ddffdd;"
            )
            self.log_status(f"OAC check passed: {message}")
        else:
            # Distribution lacks OAC - show warning and suggestion
            self.oac_status_label.setText(
                f"⚠️ WARNING: {message}\n"
                f"This distribution will cause 403 errors with private buckets. "
                f"Recommended: Delete this distribution and let Mode B create a new one with OAC."
            )
            self.oac_status_label.setStyleSheet(
                "font-size: 10px; padding: 5px; color: #cc6600; background-color: #ffeecc;"
            )
            self.log_status(f"WARNING: {message}")

    def on_delete_distribution(self):
        """Delete CloudFront distribution (v3.2.0 diagnostic tool)"""
        distribution_id = self.distribution_id_input.text().strip()

        if not distribution_id:
            QMessageBox.warning(
                self, "No Distribution ID", "Please enter a distribution ID first."
            )
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Delete CloudFront Distribution",
            f"Are you sure you want to delete distribution: {distribution_id}?\n\n"
            f"This will:\n"
            f"1. Disable the distribution (5-10 min wait)\n"
            f"2. Delete the distribution permanently\n\n"
            f"Note: This does NOT delete S3 bucket or files.\n\n"
            f"After deletion, Mode B can create a new distribution with OAC.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Check if profile is selected
        profile_name = self.profile_combo.currentText()
        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(
                self, "No Profile", "Please select an AWS profile first."
            )
            return

        # Activate profile
        if not self.credentials_manager.set_active_profile(profile_name):
            QMessageBox.warning(
                self, "Profile Error", "Failed to activate AWS profile."
            )
            return

        session = self.credentials_manager.get_active_session()
        self.s3_manager.set_session(session)

        # Step 1: Disable distribution
        self.log_status(f"Disabling distribution: {distribution_id}...")
        self.oac_status_label.setText("⏳ Step 1/2: Disabling distribution...")
        self.oac_status_label.setStyleSheet(
            "font-size: 10px; padding: 5px; color: #0066cc; background-color: #e6f2ff;"
        )

        success, message = self.s3_manager.disable_distribution(distribution_id)

        if not success:
            self.oac_status_label.setText(f"❌ Disable failed: {message}")
            self.oac_status_label.setStyleSheet(
                "font-size: 10px; padding: 5px; color: #cc0000; background-color: #ffdddd;"
            )
            QMessageBox.warning(
                self, "Disable Failed", f"Failed to disable distribution:\n\n{message}"
            )
            return

        self.log_status(message)

        # Check if already disabled or needs wait
        if "already disabled" in message:
            # Already disabled, try deleting immediately
            self.log_status("Distribution already disabled, attempting deletion...")
            self.oac_status_label.setText("⏳ Step 2/2: Deleting distribution...")

            delete_success, delete_message = self.s3_manager.delete_distribution(
                distribution_id
            )

            if delete_success:
                self.oac_status_label.setText(f"✅ {delete_message}")
                self.oac_status_label.setStyleSheet(
                    "font-size: 10px; padding: 5px; color: #006600; background-color: #ddffdd;"
                )
                self.distribution_id_input.clear()
                QMessageBox.information(
                    self,
                    "Distribution Deleted",
                    "Distribution deleted successfully!\n\n"
                    "You can now deploy with Mode B to create a new distribution with OAC.",
                )
            else:
                self.oac_status_label.setText(f"⚠️ {delete_message}")
                self.oac_status_label.setStyleSheet(
                    "font-size: 10px; padding: 5px; color: #cc6600; background-color: #ffeecc;"
                )
                QMessageBox.warning(
                    self,
                    "Delete Failed",
                    f"Failed to delete distribution:\n\n{delete_message}\n\n"
                    f"You may need to wait for the distribution to fully deploy before deleting.",
                )
        else:
            # Disabled successfully, but needs to wait
            self.oac_status_label.setText(
                "⏳ Distribution disabled. Wait 5-10 minutes for status 'Deployed', "
                "then click 'Delete Distribution' again to complete deletion."
            )
            self.oac_status_label.setStyleSheet(
                "font-size: 10px; padding: 5px; color: #0066cc; background-color: #e6f2ff;"
            )
            QMessageBox.information(
                self,
                "Distribution Disabled",
                "Distribution disabled successfully!\n\n"
                "Wait 5-10 minutes for CloudFront to finish deploying changes.\n\n"
                "Then click 'Delete Distribution' again to complete the deletion.",
            )

    def on_meta_tag_selection_changed(self):
        """Handle meta tag selection change"""
        selected_items = self.meta_tags_table.selectedItems()
        self.remove_meta_tag_button.setEnabled(len(selected_items) > 0)

    def on_meta_tag_double_clicked(self, row: int, column: int):
        """Handle double-click on meta tag for editing"""
        full_tag = self.meta_tags_table.item(row, 0).text()
        self.meta_tag_input.setText(full_tag)

    def load_meta_tags_from_config(self, meta_tags: Dict[str, str]):
        """Load meta tags from configuration dictionary (name: content pairs)"""
        from PyQt6.QtWidgets import QTableWidgetItem

        self.meta_tags_table.setRowCount(0)

        for tag_name, tag_content in meta_tags.items():
            # Reconstruct full meta tag from name/content pair
            full_tag = f'<meta name="{tag_name}" content="{tag_content}" />'
            row = self.meta_tags_table.rowCount()
            self.meta_tags_table.insertRow(row)
            self.meta_tags_table.setItem(row, 0, QTableWidgetItem(full_tag))

    def get_meta_tags_from_table(self) -> Dict[str, str]:
        """Parse full meta tags from table and return as dictionary"""
        import re

        meta_tags = {}
        for row in range(self.meta_tags_table.rowCount()):
            full_tag = self.meta_tags_table.item(row, 0).text()

            # Parse name and content from full tag
            name_match = re.search(r'name=["\']([^"\']+)["\']', full_tag)
            content_match = re.search(r'content=["\']([^"\']+)["\']', full_tag)

            if name_match and content_match:
                tag_name = name_match.group(1)
                tag_content = content_match.group(1)
                meta_tags[tag_name] = tag_content

        return meta_tags

    def open_gsc_verification_dialog(self):
        """Open Google Search Console verification dialog"""
        # Get current deployment URL if available
        deployment_url = ""

        # Try to get URL from current deployment
        if (
            hasattr(self, "current_client_aws_config")
            and self.current_client_aws_config
        ):
            deployment_url = getattr(
                self.current_client_aws_config, "deployment_url", ""
            )

        # If no deployment URL, try to construct from current UI state
        if not deployment_url:
            # For S3 mode, construct URL from bucket and region
            if self.s3_mode_radio.isChecked():
                bucket = self._get_actual_bucket_name()
                region = self.region_combo.currentText()
                if bucket and region:
                    deployment_url = (
                        f"https://{bucket}.s3-website-{region}.amazonaws.com/"
                    )
            # For CloudFront mode, deployment_url must come from config after deployment
            # (CloudFront domain is not a UI input - it's retrieved from AWS)

        # Open dialog
        dialog = GSCVerificationDialog(deployment_url, parent=self)
        dialog.meta_tag_generated.connect(self.add_meta_tag_from_gsc)
        dialog.exec()

    def add_meta_tag_from_gsc(self, name: str, content: str):
        """Add meta tag from GSC to table"""
        # Construct full meta tag HTML
        meta_tag_html = f'<meta name="{name}" content="{content}" />'

        # Add row to meta tags table
        row_count = self.meta_tags_table.rowCount()
        self.meta_tags_table.insertRow(row_count)
        self.meta_tags_table.setItem(row_count, 0, QTableWidgetItem(meta_tag_html))

        self.log_status(f"Added Google verification meta tag: {name}")

    def get_config_data(self) -> Dict[str, Any]:
        """Get cloud configuration data"""
        # Get deployment_url from current_client_aws_config if available
        deployment_url = ""
        if (
            hasattr(self, "current_client_aws_config")
            and self.current_client_aws_config
        ):
            deployment_url = getattr(
                self.current_client_aws_config, "deployment_url", ""
            )

        return {
            "aws_profile": (
                self.profile_combo.currentText()
                if self.profile_combo.currentText() != "No profiles configured"
                else ""
            ),
            "aws_region": self.region_combo.currentText(),
            "bucket_name": self._get_actual_bucket_name(),
            "directory": self.directory_combo.currentText().strip(),
            "deployment_mode": "s3" if self.s3_mode_radio.isChecked() else "cloudfront",
            "deployment_url": deployment_url,
            "distribution_id": self.distribution_id_input.text().strip(),
            "auto_invalidate_cache": self.auto_invalidate_checkbox.isChecked(),
            "site_type": (
                "backlink_site"
                if self.site_type_backlink_radio.isChecked()
                else "resource"
                if (
                    self.site_type_resource_radio is not None
                    and self.site_type_resource_radio.isChecked()
                )
                else "main_site"
            ),
            "main_site_url": self.main_site_url_input.text().strip(),
            "meta_tags": self.get_meta_tags_from_table(),
        }

    def set_config(self, config):
        """Store full config for deployment tracking (v3.5.0)"""
        self.current_config = config

    def set_config_data(self, data: Dict[str, Any]):
        """Set cloud configuration data"""
        # Refresh profiles first
        self.refresh_profiles()

        # If we have client-specific AWS config loaded, prefer that over YAML data
        if self.current_client_aws_config:
            # Use client-specific AWS configuration (already loaded by set_client_context)
            client_config = self.current_client_aws_config

            # Set AWS profile from client config, with YAML fallback
            if client_config.aws_profile:
                index = self.profile_combo.findText(client_config.aws_profile)
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
                    self.log_status(
                        f"Debug: Profile '{client_config.aws_profile}' restored from client config"
                    )
            elif data.get("aws_profile"):
                # Fallback to YAML if client config profile is empty
                index = self.profile_combo.findText(data["aws_profile"])
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
                    self.log_status(
                        f"Debug: Profile '{data['aws_profile']}' restored from YAML"
                    )

            # Set bucket - prefer client config, fallback to YAML
            bucket_to_use = client_config.bucket_name or data.get("bucket_name", "")
            if bucket_to_use:
                self.bucket_combo.setCurrentText(bucket_to_use)

            # Set directory - prefer client config, fallback to YAML
            directory_to_use = client_config.directory or data.get("directory", "")
            if directory_to_use:
                self.directory_combo.setCurrentText(directory_to_use)

            # Set region - prefer client config, fallback to YAML
            region_to_use = client_config.bucket_region or data.get("aws_region", "")
            if region_to_use:
                index = self.region_combo.findText(region_to_use)
                if index >= 0:
                    self.region_combo.setCurrentIndex(index)
        else:
            # Fall back to YAML data if no client-specific config exists
            if data.get("aws_profile"):
                index = self.profile_combo.findText(data["aws_profile"])
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)

            if data.get("aws_region"):
                index = self.region_combo.findText(data["aws_region"])
                if index >= 0:
                    self.region_combo.setCurrentIndex(index)

            if data.get("bucket_name"):
                self.bucket_combo.setCurrentText(data["bucket_name"])

            if data.get("directory"):
                self.directory_combo.setCurrentText(data["directory"])

        # Deployment mode can still come from YAML (not client-specific)
        deployment_mode = data.get("deployment_mode", "s3")
        if deployment_mode == "s3":
            self.s3_mode_radio.setChecked(True)
        else:
            self.cloudfront_mode_radio.setChecked(True)

        # Load meta tags
        meta_tags = data.get("meta_tags", {})
        if isinstance(meta_tags, dict):
            self.load_meta_tags_from_config(meta_tags)

        # Load CloudFront settings
        distribution_id = data.get("distribution_id", "")
        if distribution_id:
            self.distribution_id_input.setText(distribution_id)

        auto_invalidate = data.get("auto_invalidate_cache", True)
        self.auto_invalidate_checkbox.setChecked(auto_invalidate)

        # Load SEO and canonical URL settings
        site_type = data.get("site_type", "main_site")
        if site_type == "backlink_site":
            self.site_type_backlink_radio.setChecked(True)
        elif site_type == "resource" and self.site_type_resource_radio is not None:
            self.site_type_resource_radio.setChecked(True)
        else:
            self.site_type_main_radio.setChecked(True)

        main_site_url = data.get("main_site_url", "")
        if main_site_url:
            self.main_site_url_input.setText(main_site_url)

    def validate_data(self) -> tuple[bool, list[str]]:
        """Validate cloud configuration based on selected provider"""
        errors = []

        # Provider-specific validation
        if self.current_provider == "google_gcs":
            # GCS validation
            project_id = self.gcs_project_input.text().strip()
            if not project_id:
                errors.append("GCS Project ID is required for cloud deployment")

            credentials_path = self.gcs_credentials_input.text().strip()
            if not credentials_path:
                errors.append(
                    "GCS Service Account JSON is required for cloud deployment"
                )

            bucket_name = self._get_actual_bucket_name()
            if not bucket_name or bucket_name == "No buckets found":
                errors.append("GCS bucket name is required")
        else:
            # AWS S3 validation (default)
            profile_name = self.profile_combo.currentText()
            if not profile_name or profile_name == "No profiles configured":
                errors.append("AWS profile is required for cloud deployment")

            bucket_name = self._get_actual_bucket_name()
            if not bucket_name or bucket_name == "No buckets found":
                errors.append("S3 bucket name is required")
            else:
                is_valid, message = self.s3_manager.validate_bucket_name(bucket_name)
                if not is_valid:
                    errors.append(f"Invalid bucket name: {message}")

        # Validate backlink site configuration (common to all providers)
        if self.site_type_backlink_radio.isChecked():
            main_site_url = self.main_site_url_input.text().strip()
            if not main_site_url:
                errors.append(
                    "Main Site URL is required when 'Backlink Site' is selected"
                )
            elif not main_site_url.startswith(("http://", "https://")):
                errors.append("Main Site URL must start with http:// or https://")

        return len(errors) == 0, errors

    def set_client_context(self, business_name: str, domain: str):
        """
        Set the client context and load their AWS configuration

        Args:
            business_name: Client business name
            domain: Client domain
        """
        self.current_business_name = business_name
        self.current_domain = domain

        # Set flag to prevent bucket clearing during context reload
        self._loading_client_context = True

        try:
            # Refresh profiles first to ensure combo is populated
            self.refresh_profiles()

            # Load existing client AWS config or create default
            self.current_client_aws_config = (
                self.aws_config_manager.load_client_aws_config(business_name, domain)
            )

            if self.current_client_aws_config is None:
                # Create default config for new client
                self.current_client_aws_config = (
                    self.aws_config_manager.create_default_config(business_name, domain)
                )
                self.log_status(f"Created new AWS configuration for {business_name}")
            else:
                self.log_status(f"Loaded AWS configuration for {business_name}")

            # Update UI with client's AWS settings
            self._load_client_aws_config_to_ui()
        finally:
            # Always clear the flag
            self._loading_client_context = False

    def _load_client_aws_config_to_ui(self):
        """Load client AWS configuration into UI components"""
        if not self.current_client_aws_config:
            return

        config = self.current_client_aws_config

        # Preserve current UI selections to avoid clearing user's work
        current_bucket = self.bucket_combo.currentText()
        current_directory = self.directory_combo.currentText()
        current_region = self.region_combo.currentText()

        # Set AWS profile
        if config.aws_profile:
            self.log_status(f"Attempting to restore AWS profile: {config.aws_profile}")
            index = self.profile_combo.findText(config.aws_profile)
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
                self.log_status(
                    f"Successfully selected AWS profile: {config.aws_profile}"
                )
            else:
                self.log_status(
                    f"Warning: AWS profile '{config.aws_profile}' not found in available profiles"
                )

        # Only restore bucket name if user hasn't selected one
        if config.bucket_name and (
            not current_bucket or current_bucket in ["No buckets found", ""]
        ):
            self.bucket_combo.setCurrentText(config.bucket_name)

        # Only restore directory if user hasn't selected one
        if config.directory and (
            not current_directory or current_directory in ["/ (root)", ""]
        ):
            self.directory_combo.setCurrentText(config.directory)

        # Only restore region if user hasn't selected one
        if config.bucket_region and (not current_region or current_region == ""):
            index = self.region_combo.findText(config.bucket_region)
            if index >= 0:
                self.region_combo.setCurrentIndex(index)

        # Load GCS credentials if available
        if hasattr(config, "gcs_project_id") and config.gcs_project_id:
            self.gcs_project_input.setText(config.gcs_project_id)

        if (
            hasattr(config, "gcs_service_account_json")
            and config.gcs_service_account_json
        ):
            self.gcs_credentials_input.setText(config.gcs_service_account_json)

        if hasattr(config, "gcs_region") and config.gcs_region:
            # Find the region in the combo box (it may have descriptive text after it)
            for i in range(self.gcs_region_combo.count()):
                if self.gcs_region_combo.itemText(i).startswith(config.gcs_region):
                    self.gcs_region_combo.setCurrentIndex(i)
                    break

    def _save_client_aws_config_from_ui(self):
        """Save current UI state to client AWS configuration"""
        if not self.current_client_aws_config:
            self.log_status("Debug: No client AWS config to save")
            return

        # Get current profile selection
        current_combo_text = self.profile_combo.currentText()
        current_profile = (
            current_combo_text if current_combo_text != "No profiles configured" else ""
        )

        # CRITICAL FIX: Don't overwrite existing saved profile with empty profile
        # This protects against timing issues and unintended empty profile saves
        if current_profile == "" and self.current_client_aws_config.aws_profile != "":
            self.log_status(
                f"Debug: Preventing overwrite of saved profile '{self.current_client_aws_config.aws_profile}' with empty value (combo: '{current_combo_text}')"
            )
            return

        self.log_status(
            f"Debug: Saving AWS profile '{current_profile}' for {self.current_business_name}"
        )

        # Update config with current UI values
        self.current_client_aws_config.aws_profile = current_profile
        self.current_client_aws_config.bucket_name = self._get_actual_bucket_name()
        self.current_client_aws_config.directory = (
            self.directory_combo.currentText().strip()
        )
        self.current_client_aws_config.bucket_region = self.region_combo.currentText()

        # Update GCS credentials from UI if present
        if hasattr(self.current_client_aws_config, "gcs_project_id"):
            gcs_project = self.gcs_project_input.text().strip()
            gcs_credentials = self.gcs_credentials_input.text().strip()
            gcs_region = (
                self.gcs_region_combo.currentText().split()[0]
                if self.gcs_region_combo.currentText()
                else ""
            )

            self.current_client_aws_config.gcs_project_id = gcs_project
            self.current_client_aws_config.gcs_service_account_json = gcs_credentials
            self.current_client_aws_config.gcs_region = gcs_region

        # Save to persistent storage
        success = self.aws_config_manager.save_client_aws_config(
            self.current_client_aws_config
        )
        if success:
            self.log_status(
                f"AWS configuration saved successfully for {self.current_business_name}"
            )
        else:
            self.log_status("Warning: Failed to save AWS configuration")

    def on_aws_config_changed(self):
        """Handle AWS configuration changes in UI"""
        # Auto-save when configuration changes
        if self.current_client_aws_config:
            self._save_client_aws_config_from_ui()

    def get_client_aws_config(self) -> Optional[ClientAWSConfig]:
        """Get the current client's AWS configuration"""
        return self.current_client_aws_config
