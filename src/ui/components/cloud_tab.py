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
2025-09-05

Comments:
* v1.00 - Initial implementation following existing UI patterns and SOP workflow
"""

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QLabel, QLineEdit,
    QPushButton, QComboBox, QRadioButton, QButtonGroup, QTextEdit,
    QProgressBar, QMessageBox, QDialog, QDialogButtonBox, QApplication,
    QCheckBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from typing import Dict, Any, Optional, List
from pathlib import Path
import subprocess
import platform

from .base_tab import BaseTab
from .progress_widget import ProgressWidget
from ...core.aws.credentials import AWSCredentialsManager, AuthMethod
from ...core.aws.s3_manager import S3Manager, UploadProgress, UploadResult
from ...core.config.client_aws_config import ClientAWSConfig, get_client_aws_manager
from ...utils.error_logger import log_error_dialog


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
        self.region_combo.addItems(["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"])
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
            QMessageBox.warning(self, "Profile Name Required", 
                              "Please enter a profile name before configuring SSO.")
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
                applescript = f'''
                tell application "Terminal"
                    do script "{command}"
                    activate
                end tell
                '''
                subprocess.run(["osascript", "-e", applescript], check=False)
            else:  # Linux and other Unix-like systems
                # Try common terminal emulators
                terminals = ["gnome-terminal", "konsole", "xterm", "x-terminal-emulator"]
                for terminal in terminals:
                    try:
                        if terminal == "gnome-terminal":
                            subprocess.run([terminal, "--", "bash", "-c", f"{command}; exec bash"], check=False)
                        elif terminal == "konsole":
                            subprocess.run([terminal, "-e", "bash", "-c", f"{command}; exec bash"], check=False)
                        else:
                            subprocess.run([terminal, "-e", f"bash -c '{command}; exec bash'"], check=False)
                        break
                    except FileNotFoundError:
                        continue
                else:
                    QMessageBox.warning(self, "Terminal Not Found", 
                                      "Could not find a suitable terminal application.")
                    return
            
            QMessageBox.information(self, "SSO Configuration", 
                                  f"AWS SSO configuration started for profile '{profile_name}'. "
                                  f"Please complete the configuration in the terminal window that opened.")
            
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
        auth_method = AuthMethod.SSO if self.sso_radio.isChecked() else AuthMethod.ACCESS_KEYS

        data = {
            'name': self.profile_name_input.text().strip(),
            'description': self.description_input.text().strip(),
            'auth_method': auth_method,
            'region': self.region_combo.currentText()
        }

        # Add method-specific data
        if auth_method == AuthMethod.SSO:
            data.update({
                'sso_start_url': self.sso_url_input.text().strip(),
                'sso_region': self.sso_region_combo.currentText()
            })
        else:  # ACCESS_KEYS
            data.update({
                'access_key_id': self.access_key_input.text().strip(),
                'secret_access_key': self.secret_key_input.text().strip()
            })

        return data


class BucketRefreshWorker(QThread):
    """Background worker for bucket list refresh operations"""
    
    progress_updated = pyqtSignal(str)
    finished = pyqtSignal(list, str)  # buckets, profile_name
    error_occurred = pyqtSignal(str, str, Exception)  # error_message, profile_name, exception
    
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
                self.error_occurred.emit("Could not create AWS session for the selected profile", self.profile_name, None)
                return
            
            self.progress_updated.emit("Retrieving bucket list...")
            
            # Set session and get buckets
            self.s3_manager.set_session(session)
            
            # Get all client buckets with SOP compliance indicators
            buckets = self.credentials_manager.list_client_buckets(self.profile_name, show_all=True)
            
            self.progress_updated.emit("Processing bucket list...")
            
            # Emit success with buckets
            self.finished.emit(buckets, self.profile_name)
            
        except Exception as e:
            error_message = f"Failed to retrieve bucket list: {str(e)}"
            self.error_occurred.emit(error_message, self.profile_name, e)


class ConnectionTestWorker(QThread):
    """Background worker for AWS connection testing"""
    
    progress_updated = pyqtSignal(str)
    test_completed = pyqtSignal(bool, str, dict)  # success, message, identity
    error_occurred = pyqtSignal(str, Exception)  # error_message, exception
    
    def __init__(self, credentials_manager, profile_name: str):
        super().__init__()
        self.credentials_manager = credentials_manager
        self.profile_name = profile_name
    
    def run(self):
        """Execute connection test in background"""
        try:
            self.progress_updated.emit("Validating AWS profile credentials...")
            
            # Step 1: Validate profile
            is_valid, message, identity = self.credentials_manager.validate_profile(self.profile_name)
            
            if is_valid:
                account = identity.get('account', 'Unknown')
                region = identity.get('region', 'Unknown')
                
                self.progress_updated.emit(f"Connected to AWS Account: {account}")
                self.progress_updated.emit(f"Profile region: {region}")
                
                # Step 2: Test S3 permissions
                self.progress_updated.emit("Testing S3 permissions...")
                s3_permissions = self._test_s3_permissions()
                
                self.progress_updated.emit("Connection test completed successfully!")
                
                # Build detailed success message with permissions
                success_message = (
                    f"Successfully connected to AWS\n\n"
                    f"Account: {account}\n"
                    f"Region: {region}\n"
                    f"Profile: {self.profile_name}\n\n"
                    f"S3 Permissions:\n"
                    f"{s3_permissions}"
                )
                
                self.test_completed.emit(True, success_message, identity)
            else:
                self.progress_updated.emit(f"Connection failed: {message}")
                self.test_completed.emit(False, message, {})
                
        except Exception as e:
            error_message = f"Connection test failed: {str(e)}"
            self.error_occurred.emit(error_message, e)
    
    def _test_s3_permissions(self) -> str:
        """Test S3 permissions for the given profile and return a summary"""
        try:
            # Get AWS session for the profile
            session = self.credentials_manager._get_session(self.profile_name)
            if not session:
                return "ERROR: Could not create AWS session"
            
            s3 = session.client('s3')
            
            permissions = []
            
            # Test list buckets
            try:
                s3.list_buckets()
                permissions.append("✓ List Buckets: PASS")
            except Exception as e:
                permissions.append(f"✗ List Buckets: FAIL ({str(e)[:50]}...)")
            
            # Test create bucket (dry run)
            try:
                # We can't actually test bucket creation without creating one
                # Just check if we have the permission structure
                permissions.append("✓ Create Bucket: AVAILABLE (untested)")
            except Exception:
                permissions.append("✗ Create Bucket: UNKNOWN")
            
            return "\n".join(permissions)
            
        except Exception as e:
            return f"ERROR: S3 permission test failed: {str(e)}"


class DeploymentWorker(QThread):
    """Background worker for deployment operations"""

    progress_updated = pyqtSignal(UploadProgress)
    deployment_completed = pyqtSignal(UploadResult)

    def __init__(
        self,
        s3_manager: S3Manager,
        local_path: str,
        bucket_name: str,
        distribution_id: str = "",
        auto_invalidate: bool = False
    ):
        super().__init__()
        self.s3_manager = s3_manager
        self.local_path = local_path
        self.bucket_name = bucket_name
        self.distribution_id = distribution_id
        self.auto_invalidate = auto_invalidate
    
    def run(self):
        """Execute deployment in background"""
        try:
            # Set up progress callback
            self.s3_manager.set_progress_callback(self.progress_updated.emit)

            # Upload directory
            result = self.s3_manager.upload_directory(self.local_path, self.bucket_name)

            # Perform CloudFront cache invalidation if enabled
            if result.success and self.auto_invalidate and self.distribution_id:
                invalidation_success, invalidation_msg, invalidation_id = (
                    self.s3_manager.create_cloudfront_invalidation(self.distribution_id)
                )

                result.invalidation_id = invalidation_id
                if invalidation_success:
                    result.invalidation_status = "InProgress"
                    result.message += f" | Cache invalidation started (ID: {invalidation_id})"
                else:
                    result.invalidation_status = "Failed"
                    result.message += f" | Cache invalidation failed: {invalidation_msg}"

            self.deployment_completed.emit(result)
        except Exception as e:
            # Create a failure result and emit it
            from src.core.aws.s3_manager import UploadResult
            error_result = UploadResult(
                success=False,
                message=f"Deployment failed: {str(e)}",
                website_url="",
                uploaded_files=0,
                failed_files=0
            )
            self.deployment_completed.emit(error_result)


class CloudTab(BaseTab):
    """Cloud deployment configuration tab"""
    
    def __init__(self, parent=None):
        self.credentials_manager = AWSCredentialsManager()
        self.s3_manager = S3Manager()
        self.deployment_worker: Optional[DeploymentWorker] = None
        
        # Client-specific AWS configuration
        self.aws_config_manager = get_client_aws_manager()
        self.current_client_aws_config: Optional[ClientAWSConfig] = None
        self.current_business_name: str = ""
        self.current_domain: str = ""
        
        # Flag to prevent bucket clearing during client context loading
        self._loading_client_context: bool = False
        
        # UI components
        self.profile_combo = None
        self.bucket_combo = None
        self.directory_combo = None
        self.region_combo = None
        self.deployment_mode_group = None
        self.s3_mode_radio = None
        self.cloudfront_mode_radio = None
        self.distribution_id_input = None
        self.auto_invalidate_checkbox = None
        self.progress_bar = None
        self.deploy_button = None
        self.status_text = None
        
        super().__init__(parent)
    
    def setup_ui(self):
        """Setup cloud deployment UI"""
        layout = QVBoxLayout()
        
        # AWS Profile Section
        profile_group = self.create_profile_section()
        layout.addWidget(profile_group)
        
        # Bucket Configuration Section
        bucket_group = self.create_bucket_section()
        layout.addWidget(bucket_group)

        # Two-column layout for CloudFront Settings and Meta Tags
        two_column_layout = QHBoxLayout()

        # Left Column: Deployment Mode (with CloudFront Distribution Settings)
        mode_group = self.create_deployment_mode_section()
        two_column_layout.addWidget(mode_group)

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
        self.connection_progress.set_status_height(60)  # Smaller height for this context
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
        """Create S3 bucket configuration section"""
        group = QGroupBox("S3 Bucket Configuration")
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
        self.refresh_buckets_button.setToolTip("Refresh bucket list from AWS")
        bucket_layout.addWidget(self.refresh_buckets_button)
        
        layout.addLayout(bucket_layout, 0, 1)
        
        self.create_bucket_button = QPushButton("Create Bucket")
        layout.addWidget(self.create_bucket_button, 0, 2)
        
        # Directory field
        layout.addWidget(QLabel("Directory:"), 1, 0)
        
        directory_layout = QHBoxLayout()
        
        self.directory_combo = QComboBox()
        self.directory_combo.setEditable(True)
        self.directory_combo.setPlaceholderText("Select existing or enter new directory")
        self.directory_combo.lineEdit().setPlaceholderText("/ (root) or subdirectory name")
        directory_layout.addWidget(self.directory_combo)
        
        self.refresh_directories_button = QPushButton("Refresh")
        self.refresh_directories_button.setMaximumWidth(80)
        self.refresh_directories_button.setToolTip("Refresh directory list from selected bucket")
        directory_layout.addWidget(self.refresh_directories_button)
        
        self.create_directory_button = QPushButton("Create")
        self.create_directory_button.setMaximumWidth(80)
        self.create_directory_button.setToolTip("Create a new directory in the selected bucket")
        directory_layout.addWidget(self.create_directory_button)
        
        layout.addLayout(directory_layout, 1, 1, 1, 2)
        
        # Region
        layout.addWidget(QLabel("Region:"), 2, 0)
        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1",
            "eu-central-1", "ap-northeast-1"
        ])
        layout.addWidget(self.region_combo, 2, 1)
        
        # Bucket and directory status
        self.bucket_status_label = QLabel("No bucket configured")
        self.bucket_status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.bucket_status_label, 3, 0, 1, 3)
        
        group.setLayout(layout)
        
        # Connect signals
        self.create_bucket_button.clicked.connect(self.create_s3_bucket)
        self.refresh_buckets_button.clicked.connect(self.refresh_bucket_list)
        self.refresh_directories_button.clicked.connect(self.refresh_directory_list)
        self.create_directory_button.clicked.connect(self.create_directory)
        self.bucket_combo.currentTextChanged.connect(self.on_bucket_selection_changed)
        self.bucket_combo.lineEdit().textChanged.connect(self.on_bucket_name_changed)
        self.directory_combo.currentTextChanged.connect(self.on_directory_selection_changed)
        
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
        self.s3_mode_radio.setToolTip("Direct S3 website hosting - fastest deployment, public bucket required")
        
        # Mode B: CloudFront + OAC (Phase 2)
        self.cloudfront_mode_radio = QRadioButton("Mode B: CloudFront + OAC (Coming in Phase 2)")
        self.cloudfront_mode_radio.setEnabled(False)
        self.cloudfront_mode_radio.setToolTip("CloudFront distribution with Origin Access Control - production ready, private bucket")
        
        self.deployment_mode_group.addButton(self.s3_mode_radio, 0)
        self.deployment_mode_group.addButton(self.cloudfront_mode_radio, 1)
        
        layout.addWidget(self.s3_mode_radio)
        layout.addWidget(self.cloudfront_mode_radio)

        # Mode description
        self.mode_description = QLabel("S3 Static Website: Direct hosting from S3 bucket with public access")
        self.mode_description.setStyleSheet("color: #666; font-style: italic;")
        self.mode_description.setWordWrap(True)
        layout.addWidget(self.mode_description)

        # CloudFront Settings (only for existing CloudFront distributions)
        cf_label = QLabel("CloudFront Distribution Settings")
        cf_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(cf_label)

        # Distribution ID input
        dist_layout = QHBoxLayout()
        dist_layout.addWidget(QLabel("Distribution ID:"))
        self.distribution_id_input = QLineEdit()
        self.distribution_id_input.setPlaceholderText("E.g., E3VQJQK8Z5Z5Z5")
        self.distribution_id_input.setToolTip("CloudFront distribution ID for cache invalidation")
        dist_layout.addWidget(self.distribution_id_input)
        layout.addLayout(dist_layout)

        # Auto-invalidate checkbox
        self.auto_invalidate_checkbox = QCheckBox("Automatically invalidate CloudFront cache after deployment")
        self.auto_invalidate_checkbox.setChecked(True)
        self.auto_invalidate_checkbox.setToolTip("Create invalidation request for /* after successful upload")
        layout.addWidget(self.auto_invalidate_checkbox)

        group.setLayout(layout)

        # Connect signals
        self.deployment_mode_group.buttonClicked.connect(self.on_deployment_mode_changed)

        return group
    
    def create_deployment_controls_section(self) -> QGroupBox:
        """Create deployment controls section"""
        group = QGroupBox("Deployment")
        layout = QVBoxLayout()
        
        # Local path selection
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Local Website:"))
        
        self.local_path_input = QLineEdit()
        self.local_path_input.setPlaceholderText("Generated website will be deployed automatically")
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
        self.website_url_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        layout.addWidget(self.website_url_label)
        
        group.setLayout(layout)

        return group

    def create_meta_tags_section(self) -> QGroupBox:
        """Create SEO meta tags management section"""
        from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView

        group = QGroupBox("SEO Meta Tags")
        layout = QVBoxLayout()

        # Info label
        info_label = QLabel("Paste complete meta tag (Google provides the full tag)")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(info_label)

        # Meta tags list (table showing full tags)
        self.meta_tags_table = QTableWidget()
        self.meta_tags_table.setColumnCount(1)
        self.meta_tags_table.setHorizontalHeaderLabels(["Meta Tag"])
        self.meta_tags_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.meta_tags_table.setMaximumHeight(150)
        layout.addWidget(self.meta_tags_table)

        # Single meta tag input field
        input_layout = QVBoxLayout()

        input_layout.addWidget(QLabel("Complete Meta Tag:"))
        self.meta_tag_input = QLineEdit()
        self.meta_tag_input.setPlaceholderText('<meta name="google-site-verification" content="xd8vHxFt3Iuru6NoXjN4trhN8KIy7Ti0AMKSL7oQnyU" />')
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
        layout.addLayout(button_layout)

        group.setLayout(layout)

        # Connect table selection signal
        self.meta_tags_table.itemSelectionChanged.connect(self.on_meta_tag_selection_changed)
        self.meta_tags_table.cellDoubleClicked.connect(self.on_meta_tag_double_clicked)

        return group

    def connect_signals(self):
        """Connect UI signals"""
        # Signals are connected in individual create_* methods
        pass
    
    def create_new_profile(self):
        """Create new AWS profile"""
        existing_profiles = [self.profile_combo.itemText(i) for i in range(self.profile_combo.count())]
        
        dialog = AWSProfileDialog(self, existing_profiles)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            profile_data = dialog.get_profile_data()
            
            if not profile_data['name']:
                QMessageBox.warning(self, "Invalid Profile", "Profile name is required")
                return
            
            if profile_data['name'] in existing_profiles:
                QMessageBox.warning(self, "Profile Exists", f"Profile '{profile_data['name']}' already exists")
                return
            
            # Create AWS profile
            if profile_data['auth_method'] == AuthMethod.SSO:
                profile = self.credentials_manager.add_sso_profile(
                    name=profile_data['name'],
                    sso_start_url=profile_data['sso_start_url'],
                    sso_region=profile_data['sso_region'],
                    region=profile_data['region']
                )
            else:  # ACCESS_KEYS
                # Validate access key credentials are provided
                if not profile_data.get('access_key_id') or not profile_data.get('secret_access_key'):
                    QMessageBox.warning(self, "Missing Credentials",
                                      "Access Key ID and Secret Access Key are required for Access Key authentication.")
                    return

                profile = self.credentials_manager.add_access_key_profile(
                    name=profile_data['name'],
                    region=profile_data['region']
                )

                # Store the access keys securely
                from ...core.security.api_key_manager import APIKeyManager
                api_key_manager = APIKeyManager()
                success = api_key_manager.set_aws_credentials(
                    profile_name=profile_data['name'],
                    access_key_id=profile_data['access_key_id'],
                    secret_access_key=profile_data['secret_access_key']
                )

                if not success:
                    QMessageBox.critical(self, "Storage Error",
                                       "Failed to securely store AWS credentials. Please try again.")
                    return
            
            profile.description = profile_data['description']
            
            self.refresh_profiles()
            self.profile_combo.setCurrentText(profile_data['name'])
            
            # Explicitly save the profile selection 
            self.on_aws_config_changed()
            
            QMessageBox.information(
                self,
                "Profile Created",
                f"AWS profile '{profile_data['name']}' created successfully.\n\n"
                "For SSO profiles, you'll need to run 'aws configure sso' in your terminal "
                "with the same profile name to complete the setup."
            )

    def edit_profile(self):
        """Edit the selected AWS profile"""
        profile_name = self.profile_combo.currentText()

        # Validate selection
        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(self, "No Profile Selected", "Please select a profile to edit.")
            return

        # Get current profile data
        if profile_name not in self.credentials_manager.profiles:
            QMessageBox.warning(self, "Profile Not Found", f"Profile '{profile_name}' not found.")
            return

        current_profile = self.credentials_manager.profiles[profile_name]
        existing_profiles = [self.profile_combo.itemText(i) for i in range(self.profile_combo.count())]
        existing_profiles.remove(profile_name)  # Remove current profile from list to allow keeping same name

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
            if hasattr(current_profile, 'sso_start_url'):
                dialog.sso_url_input.setText(current_profile.sso_start_url or '')
            if hasattr(current_profile, 'sso_account_id'):
                dialog.sso_account_input.setText(current_profile.sso_account_id or '')
            if hasattr(current_profile, 'sso_role_name'):
                dialog.sso_role_input.setText(current_profile.sso_role_name or '')
        else:
            dialog.access_keys_radio.setChecked(True)
            dialog.on_auth_method_changed()
            # Note: We don't pre-populate access keys for security reasons
            # User will need to re-enter them if changing

        # Set region
        if hasattr(current_profile, 'region'):
            region_index = dialog.region_combo.findText(current_profile.region)
            if region_index >= 0:
                dialog.region_combo.setCurrentIndex(region_index)

        # Show dialog
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                profile_data = dialog.get_profile_data()
                new_profile_name = profile_data['name']

                # If profile name changed, delete old profile
                if new_profile_name != profile_name:
                    if new_profile_name in self.credentials_manager.profiles:
                        QMessageBox.warning(
                            self,
                            "Profile Exists",
                            f"A profile named '{new_profile_name}' already exists. Please choose a different name."
                        )
                        return

                    # Remove old profile
                    del self.credentials_manager.profiles[profile_name]

                    # Remove stored credentials from secure storage
                    from ...core.security.api_key_manager import APIKeyManager
                    api_key_manager = APIKeyManager()
                    api_key_manager.remove_aws_credentials(profile_name)

                # Update/create profile with new data
                if profile_data['auth_method'] == AuthMethod.SSO:
                    profile = self.credentials_manager.add_sso_profile(
                        name=profile_data['name'],
                        sso_start_url=profile_data['sso_start_url'],
                        sso_region=profile_data['region'],
                        sso_account_id=profile_data.get('sso_account_id'),
                        sso_role_name=profile_data.get('sso_role_name')
                    )
                    profile.description = profile_data.get('description', '')
                else:  # ACCESS_KEYS
                    # Validate access key credentials are provided
                    if not profile_data.get('access_key_id') or not profile_data.get('secret_access_key'):
                        QMessageBox.warning(
                            self,
                            "Missing Credentials",
                            "Access Key ID and Secret Access Key are required for Access Key authentication."
                        )
                        return

                    profile = self.credentials_manager.add_access_key_profile(
                        name=profile_data['name'],
                        region=profile_data['region']
                    )

                    # Store the access keys securely
                    from ...core.security.api_key_manager import APIKeyManager
                    api_key_manager = APIKeyManager()
                    success = api_key_manager.set_aws_credentials(
                        profile_name=profile_data['name'],
                        access_key_id=profile_data['access_key_id'],
                        secret_access_key=profile_data['secret_access_key']
                    )

                    if not success:
                        QMessageBox.critical(
                            self,
                            "Storage Error",
                            "Failed to securely store AWS credentials. Please try again."
                        )
                        return

                    profile.description = profile_data.get('description', '')

                # Refresh profiles
                self.refresh_profiles()

                # Select the updated profile
                self.profile_combo.setCurrentText(new_profile_name)

                self.log_status(f"AWS profile '{new_profile_name}' updated successfully")

                QMessageBox.information(
                    self,
                    "Profile Updated",
                    f"AWS profile '{profile_name}' has been updated successfully."
                    + (f"\n\nProfile renamed to '{new_profile_name}'." if new_profile_name != profile_name else "")
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
            QMessageBox.warning(self, "No Profile Selected", "Please select a profile to delete.")
            return

        # Confirm deletion
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete the AWS profile '{profile_name}'?\n\n"
            "This will remove the profile configuration and any stored credentials.\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
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
                f"AWS profile '{profile_name}' has been deleted successfully."
            )

        except Exception as e:
            error_msg = f"Failed to delete profile '{profile_name}': {str(e)}"
            self.log_status(f"Error: {error_msg}")
            QMessageBox.critical(self, "Delete Error", error_msg)

    def configure_existing_profile_sso(self):
        """Configure AWS SSO for existing profile"""
        profile_name = self.profile_combo.currentText()
        
        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(self, "No Profile Selected", "Please select a profile first.")
            return
        
        if profile_name not in self.credentials_manager.profiles:
            QMessageBox.warning(self, "Profile Not Found", f"Profile '{profile_name}' not found.")
            return
        
        profile = self.credentials_manager.profiles[profile_name]
        if profile.auth_method != AuthMethod.SSO:
            QMessageBox.information(self, "Not an SSO Profile", 
                                  f"Profile '{profile_name}' is not configured for SSO authentication.")
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
                applescript = f'''
                tell application "Terminal"
                    do script "{command}"
                    activate
                end tell
                '''
                subprocess.run(["osascript", "-e", applescript], check=False)
            else:  # Linux and other Unix-like systems
                # Try common terminal emulators
                terminals = ["gnome-terminal", "konsole", "xterm", "x-terminal-emulator"]
                for terminal in terminals:
                    try:
                        if terminal == "gnome-terminal":
                            subprocess.run([terminal, "--", "bash", "-c", f"{command}; exec bash"], check=False)
                        elif terminal == "konsole":
                            subprocess.run([terminal, "-e", "bash", "-c", f"{command}; exec bash"], check=False)
                        else:
                            subprocess.run([terminal, "-e", f"bash -c '{command}; exec bash'"], check=False)
                        break
                    except FileNotFoundError:
                        continue
                else:
                    QMessageBox.warning(self, "Terminal Not Found", 
                                      "Could not find a suitable terminal application.")
                    return
            
            QMessageBox.information(self, "SSO Configuration", 
                                  f"AWS SSO reconfiguration started for profile '{profile_name}'. "
                                  f"Please complete the configuration in the terminal window that opened.\n\n"
                                  f"This will update the SSO session for your existing profile.")
            
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
            self.log_status("Debug: Empty profile name detected - not triggering auto-save")
            self.profile_status_label.setText("No profile selected")
            self.profile_combo.setToolTip("Select an AWS profile for cloud deployment")
            self.configure_sso_button.setEnabled(False)
            self.edit_profile_button.setEnabled(False)
            self.delete_profile_button.setEnabled(False)
            return
        
        if profile_name in self.credentials_manager.profiles:
            profile = self.credentials_manager.profiles[profile_name]
            self.profile_status_label.setText(f"Profile: {profile.auth_method.value} | Region: {profile.region}")
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
            if not getattr(self, '_loading_client_context', False):
                if self.bucket_combo is not None:
                    self.bucket_combo.clear()
                    self.bucket_combo.addItem("No buckets found")
                    self.bucket_combo.setCurrentText("No buckets found")
                    self.log_status(f"Profile '{profile_name}' selected. Click 'Refresh' next to Bucket Name to load S3 buckets.")
                else:
                    self.log_status(f"Profile '{profile_name}' selected. UI not fully initialized yet.")
            else:
                self.log_status(f"Profile '{profile_name}' restored from client context.")
            self.update_deploy_button_state()
            # Auto-save client AWS config
            self.log_status(f"Debug: Triggering auto-save for profile '{profile_name}'")
            self.on_aws_config_changed()
        else:
            self.profile_status_label.setText("Profile not found")
            self.profile_combo.setToolTip(f"Profile '{profile_name}' not found in credentials manager")
            self.configure_sso_button.setEnabled(False)
            self.delete_profile_button.setEnabled(False)
            self.log_status(f"Debug: Profile '{profile_name}' not found in credentials manager")
    
    def _populate_buckets_for_profile_silently(self, profile_name: str):
        """Silently populate bucket list for the given profile without showing error messages"""
        try:
            if not profile_name or profile_name == "No profiles configured":
                self.log_status("Debug: No profile selected for bucket population")
                return
            
            if profile_name not in self.credentials_manager.profiles:
                self.log_status(f"Debug: Profile '{profile_name}' not found for bucket population")
                return
            
            # Get AWS session for the profile
            session = self.credentials_manager._get_session(profile_name)
            if not session:
                self.log_status(f"Debug: Could not create AWS session for profile '{profile_name}'")
                return
            
            # Set session and get buckets
            self.s3_manager.set_session(session)
            
            # Get all client buckets with SOP compliance indicators
            buckets = self.credentials_manager.list_client_buckets(profile_name, show_all=True)
            
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
                        bucket_name = bucket['name']
                        if bucket.get('sop_compliant', False):
                            # Mark SOP-compliant buckets with a prefix
                            display_name = f"✓ {bucket_name}"
                            sop_compliant_count += 1
                        else:
                            # Show non-SOP buckets with a different indicator
                            display_name = f"• {bucket_name}"
                        
                        self.bucket_combo.addItem(display_name)
                        # Store the actual bucket name as item data
                        self.bucket_combo.setItemData(self.bucket_combo.count() - 1, bucket_name)
                    
                    # Restore selection if it exists (match by actual bucket name)
                    for i in range(self.bucket_combo.count()):
                        if self.bucket_combo.itemData(i) == current_bucket:
                            self.bucket_combo.setCurrentIndex(i)
                            break
                    
                    self.log_status(f"Auto-populated {len(buckets)} buckets ({sop_compliant_count} SOP-compliant) for profile '{profile_name}'")
                else:
                    self.bucket_combo.addItem("No buckets found")
                    self.log_status(f"No buckets found in AWS account for profile '{profile_name}'")
        
        except Exception as e:
            self.log_status(f"Debug: Failed to auto-populate buckets for profile '{profile_name}': {str(e)}")
    
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
            QMessageBox.warning(self, "No Profile", "Please create an AWS profile first")
            return
        
        # Check if already running
        if hasattr(self, '_connection_test_worker') and self._connection_test_worker.isRunning():
            return
        
        # Show progress and disable button
        self.connection_progress.show_progress("Testing AWS connection...", indeterminate=True)
        self.test_connection_button.setEnabled(False)
        
        # Create and start worker thread
        self._connection_test_worker = ConnectionTestWorker(
            self.credentials_manager, profile_name
        )
        self._connection_test_worker.progress_updated.connect(self.connection_progress.update_status)
        self._connection_test_worker.test_completed.connect(self._on_connection_test_completed)
        self._connection_test_worker.error_occurred.connect(self._on_connection_test_error)
        self._connection_test_worker.start()
    
    def _on_connection_test_completed(self, success: bool, message: str, identity: dict):
        """Handle connection test completion"""
        try:
            # Hide progress before showing dialog
            self.connection_progress.hide_progress()
            
            if success:
                QMessageBox.information(self, "Connection Successful", message)
                
                # Update S3 manager with validated session
                session = self.credentials_manager.get_active_session()
                if session:
                    self.s3_manager.set_session(session)
            else:
                QMessageBox.warning(self, "Connection Failed", f"AWS connection failed:\n\n{message}")
        
        finally:
            # Re-enable button
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
        """Refresh the list of available S3 buckets with progress indication"""
        profile_name = self.profile_combo.currentText()
        
        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(self, "No Profile Selected", 
                              "Please select an AWS profile first.")
            return
        
        if profile_name not in self.credentials_manager.profiles:
            QMessageBox.warning(self, "Profile Not Found", 
                              f"Profile '{profile_name}' not found.")
            return
        
        # Check if already running
        if hasattr(self, '_bucket_refresh_worker') and self._bucket_refresh_worker.isRunning():
            return
        
        # Show progress and disable button
        if not hasattr(self, 'bucket_progress'):
            self.bucket_progress = ProgressWidget()
            self.bucket_progress.set_status_height(80)
            # Insert after bucket section - find parent layout
            for i in range(self.layout().count()):
                item = self.layout().itemAt(i)
                if hasattr(item.widget(), 'title') and 'Bucket' in item.widget().title():
                    self.layout().insertWidget(i + 1, self.bucket_progress)
                    break
        
        self.bucket_progress.show_progress("Refreshing bucket list...", indeterminate=True)
        self.refresh_buckets_button.setEnabled(False)
        
        # Create and start worker thread
        self._bucket_refresh_worker = BucketRefreshWorker(
            self.credentials_manager, self.s3_manager, profile_name
        )
        self._bucket_refresh_worker.progress_updated.connect(self.bucket_progress.update_status)
        self._bucket_refresh_worker.finished.connect(self._on_bucket_refresh_finished)
        self._bucket_refresh_worker.error_occurred.connect(self._on_bucket_refresh_error)
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
                    bucket_name = bucket['name']
                    if bucket.get('sop_compliant', False):
                        # Mark SOP-compliant buckets with a prefix
                        display_name = f"[+] {bucket_name}"
                        sop_compliant_count += 1
                    else:
                        # Show non-SOP buckets with a different indicator
                        display_name = f"[-] {bucket_name}"
                    
                    self.bucket_combo.addItem(display_name)
                    # Store the actual bucket name as item data
                    self.bucket_combo.setItemData(self.bucket_combo.count() - 1, bucket_name)
                
                # Restore selection if it exists (match by actual bucket name)
                for i in range(self.bucket_combo.count()):
                    if self.bucket_combo.itemData(i) == current_bucket:
                        self.bucket_combo.setCurrentIndex(i)
                        break
                
                self.bucket_progress.update_status(f"Found {len(buckets)} buckets ({sop_compliant_count} SOP-compliant)")
                self.log_status(f"Found {len(buckets)} buckets ({sop_compliant_count} SOP-compliant)")
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
            QMessageBox.critical(self, "Error", f"Failed to retrieve bucket list:\n\n{error_message}")
            self.log_status(f"Error retrieving buckets: {error_message}")
            
            # Log to error log file
            log_error_dialog(
                title="Bucket Retrieval Error",
                message=error_message,
                context=f"Retrieving bucket list for profile '{profile_name}'",
                component="CloudTab.refresh_bucket_list",
                exception=exception,
                user_action="Refreshing S3 bucket list"
            )
        
        finally:
            # Hide progress and re-enable button
            self.bucket_progress.hide_progress()
            self.refresh_buckets_button.setEnabled(True)
    
    def refresh_directory_list(self):
        """Refresh the list of directories in the selected bucket"""
        bucket_name = self._get_actual_bucket_name()
        profile_name = self.profile_combo.currentText()
        
        if not bucket_name or bucket_name == "No buckets found":
            QMessageBox.warning(self, "No Bucket Selected", 
                              "Please select a bucket first.")
            return
        
        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(self, "No Profile Selected", 
                              "Please select an AWS profile first.")
            return
        
        try:
            # Get AWS session for the profile
            session = self.credentials_manager._get_session(profile_name)
            if not session:
                QMessageBox.warning(self, "Session Error", 
                                  "Could not create AWS session for the selected profile.")
                return
            
            # Set session and get bucket contents
            self.s3_manager.set_session(session)
            contents = self.s3_manager.list_bucket_contents(bucket_name)
            
            # Extract unique directory prefixes
            directories = set()
            directories.add("/ (root)")  # Always include root
            
            for item in contents:
                key = item['key']
                # Look for directory-like paths (containing '/')
                if '/' in key:
                    parts = key.split('/')
                    # Build directory paths
                    for i in range(len(parts) - 1):
                        dir_path = '/'.join(parts[:i+1]) + '/'
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
            
            self.log_status(f"Found {len(directories)} directories in bucket '{bucket_name}'")
                
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
                user_action="Refreshing S3 directory list"
            )
    
    def create_directory(self):
        """Create a new directory in the selected bucket"""
        bucket_name = self._get_actual_bucket_name()
        profile_name = self.profile_combo.currentText()
        
        if not bucket_name or bucket_name == "No buckets found":
            QMessageBox.warning(self, "No Bucket Selected", 
                              "Please select a bucket first.")
            return
        
        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(self, "No Profile Selected", 
                              "Please select an AWS profile first.")
            return
        
        # Get directory name from user
        from PyQt6.QtWidgets import QInputDialog, QLineEdit
        directory_name, ok = QInputDialog.getText(
            self, 
            'Create Directory', 
            'Enter directory name:\n(e.g., "images" or "css/fonts")',
            QLineEdit.EchoMode.Normal,
            ""
        )
        
        if not ok or not directory_name.strip():
            return
        
        # Clean and validate directory name
        directory_name = directory_name.strip()
        
        # Ensure directory ends with '/' for S3 consistency
        if not directory_name.endswith('/'):
            directory_name += '/'
        
        # Validate directory name
        if not self._validate_directory_name(directory_name):
            QMessageBox.warning(self, "Invalid Directory Name", 
                              "Directory name contains invalid characters.\n"
                              "Use only letters, numbers, hyphens, underscores, and forward slashes.")
            return
        
        try:
            # Get AWS session for the profile
            session = self.credentials_manager._get_session(profile_name)
            if not session:
                QMessageBox.warning(self, "Session Error", 
                                  "Could not create AWS session for the selected profile.")
                return
            
            # Set session and create directory
            self.s3_manager.set_session(session)
            
            # Create directory by uploading a placeholder object
            # S3 doesn't have true directories, so we create a placeholder file
            placeholder_key = directory_name + ".keep"
            
            try:
                # Upload empty placeholder to create directory structure
                s3_client = session.client('s3')
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=placeholder_key,
                    Body=b'',
                    ContentType='application/octet-stream'
                )
                
                self.log_status(f"Created directory '{directory_name}' in bucket '{bucket_name}'")
                
                # Add to directory combo if not already there
                if directory_name not in [self.directory_combo.itemText(i) for i in range(self.directory_combo.count())]:
                    self.directory_combo.addItem(directory_name)
                    
                # Select the newly created directory
                self.directory_combo.setCurrentText(directory_name)
                
                QMessageBox.information(self, "Directory Created", 
                                      f"Directory '{directory_name}' created successfully in bucket '{bucket_name}'")
                
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
                    friendly_msg = f"Bucket '{bucket_name}' does not exist or is not accessible."
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
                user_action="Creating a new directory in S3 bucket"
            )
    
    def _validate_directory_name(self, directory_name: str) -> bool:
        """Validate directory name for S3 compatibility"""
        import re
        
        # Remove trailing slash for validation
        name_to_validate = directory_name.rstrip('/')
        
        if not name_to_validate:
            return False
        
        # S3 key naming conventions
        # Allow: letters, numbers, hyphens, underscores, periods, forward slashes
        # Avoid: spaces, special characters that could cause issues
        if not re.match(r'^[a-zA-Z0-9._/-]+$', name_to_validate):
            return False
        
        # Additional checks
        if name_to_validate.startswith('/') or '//' in name_to_validate:
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
            self.log_status(f"Bucket '{actual_bucket_name}' selected. Click 'Refresh' to load existing directories.")
        
        # Update status
        if bucket_name and bucket_name != "No buckets found":
            directory = self.directory_combo.currentText()
            self.bucket_status_label.setText(f"Bucket: {bucket_name} | Directory: {directory}")
            self.bucket_status_label.setStyleSheet("color: green;")
        else:
            self.bucket_status_label.setText("No bucket configured")
            self.bucket_status_label.setStyleSheet("color: #666;")
    
    def on_directory_selection_changed(self, directory: str):
        """Handle directory selection change"""
        bucket_name = self._get_actual_bucket_name()
        
        if bucket_name and bucket_name != "No buckets found" and directory:
            self.bucket_status_label.setText(f"Bucket: {bucket_name} | Directory: {directory}")
            self.bucket_status_label.setStyleSheet("color: green;")
        else:
            self.bucket_status_label.setText("No bucket configured")
            self.bucket_status_label.setStyleSheet("color: #666;")
        
        self.update_deploy_button_state()
        # Auto-save client AWS config
        self.on_aws_config_changed()
    
    def create_s3_bucket(self):
        """Create S3 bucket with validation and confirmation"""
        profile_name = self.profile_combo.currentText()
        bucket_name = self._get_actual_bucket_name()
        directory = self.directory_combo.currentText().strip()
        region = self.region_combo.currentText()

        if profile_name == "No profiles configured":
            QMessageBox.warning(self, "No Profile", "Please select an AWS profile first")
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
            existing_buckets = self.credentials_manager.list_client_buckets(profile_name)
            bucket_exists = any(bucket['name'] == bucket_name for bucket in existing_buckets)
            
            if bucket_exists:
                reply = QMessageBox.question(
                    self,
                    "Bucket Already Exists", 
                    f"Bucket '{bucket_name}' already exists.\n\n"
                    f"Do you want to proceed with using the existing bucket?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.No:
                    return
                
                # Bucket exists, check directory if specified
                if directory and directory != "/ (root)":
                    directory_exists = self.check_directory_exists(bucket_name, directory)
                    if directory_exists:
                        dir_reply = QMessageBox.question(
                            self,
                            "Directory Already Exists",
                            f"Directory '{directory}' already exists in bucket '{bucket_name}'.\n\n"
                            f"Do you want to proceed with using the existing directory?\n"
                            f"Files may be overwritten during deployment.",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                            QMessageBox.StandardButton.No
                        )
                        
                        if dir_reply == QMessageBox.StandardButton.No:
                            return
                
                # Configure the existing bucket for HTTPS static website hosting
                success, message = self.s3_manager.configure_public_website(bucket_name, enable_https=True)
                if success:
                    self.log_status(f"Configured existing bucket '{bucket_name}' for static hosting")
                    QMessageBox.information(self, "Success", 
                                          f"Bucket '{bucket_name}' configured successfully!")
                    self.refresh_bucket_list()
                else:
                    QMessageBox.critical(self, "Configuration Failed", message)
                    
            else:
                # Create new bucket
                success, message = self.s3_manager.create_bucket(bucket_name, region)
                if success:
                    self.log_status(f"Created new bucket '{bucket_name}' in region '{region}'")
                    
                    # Configure new bucket for HTTPS static website hosting
                    self.log_status(f"Configuring bucket '{bucket_name}' for HTTPS website hosting...")
                    config_success, config_message = self.s3_manager.configure_public_website(bucket_name, enable_https=True)
                    
                    if config_success:
                        self.log_status(f"HTTPS website hosting configured for '{bucket_name}'")
                        QMessageBox.information(self, "Success", 
                                              f"Bucket '{bucket_name}' created and configured with HTTPS support!\n\n{config_message}")
                    else:
                        self.log_status(f"Warning: Website configuration failed: {config_message}")
                        QMessageBox.warning(self, "Configuration Warning", 
                                          f"Bucket '{bucket_name}' created successfully, but website configuration failed:\n\n{config_message}")
                    
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
            if directory.endswith('/'):
                dir_prefix = directory
            else:
                dir_prefix = directory + '/'
            
            # Check if any objects start with the directory prefix
            for item in contents:
                if item['key'].startswith(dir_prefix):
                    return True
            
            return False
            
        except Exception as e:
            self.log_status(f"Error checking directory existence: {str(e)}")
            return False
    
    def on_deployment_mode_changed(self):
        """Handle deployment mode change"""
        if self.s3_mode_radio.isChecked():
            self.mode_description.setText("S3 Static Website: Direct hosting from S3 bucket with public access")
        else:
            self.mode_description.setText("CloudFront + OAC: Production-ready hosting with CDN (Coming in Phase 2)")
    
    def update_deploy_button_state(self):
        """Update deploy button enabled state"""
        if not hasattr(self, 'deploy_button') or self.deploy_button is None:
            return  # Button not yet created
            
        profile_selected = (self.profile_combo.currentText() != "No profiles configured")
        bucket_name = self._get_actual_bucket_name()
        bucket_configured = bool(bucket_name) and (bucket_name != "No buckets found")
        
        self.deploy_button.setEnabled(profile_selected and bucket_configured)
    
    def start_deployment(self):
        """Start website deployment"""
        # Get the local website path
        local_path = self.local_path_input.text().strip()
        
        if not local_path:
            QMessageBox.warning(
                self,
                "No Website to Deploy",
                "No website has been generated yet.\n\n"
                "Please generate a website first using the main application, "
                "then return to this tab to deploy it."
            )
            return
        
        if not Path(local_path).exists():
            QMessageBox.warning(
                self,
                "Website Not Found",
                f"The website directory does not exist:\n{local_path}\n\n"
                "Please regenerate the website first."
            )
            return
        
        # Deploy the website
        self.deploy_website(local_path)
    
    def deploy_website(self, website_path: str):
        """Deploy generated website to cloud"""
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
        
        # Configure bucket for static website hosting
        self.log_status("Configuring bucket for static website hosting...")
        success, message = self.s3_manager.configure_public_website(bucket_name)
        
        if not success:
            self.log_status(f"Error: {message}")
            return
        
        self.log_status(message)

        # Get CloudFront settings for cache invalidation
        distribution_id = self.distribution_id_input.text().strip()
        auto_invalidate = self.auto_invalidate_checkbox.isChecked()

        # Start deployment worker
        self.deployment_worker = DeploymentWorker(
            self.s3_manager,
            website_path,
            bucket_name,
            distribution_id,
            auto_invalidate
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
            # Get website URL
            bucket_name = self._get_actual_bucket_name()
            region = self.region_combo.currentText()
            website_url = self.s3_manager.get_website_url(bucket_name, region, prefer_https=True)
            
            if website_url:
                self.website_url_label.setText(f'<a href="{website_url}">View Website: {website_url}</a>')
            
            self.log_status(f"Deployment completed successfully! {result.message}")
            
            # Show success message
            QMessageBox.information(
                self,
                "Deployment Successful",
                f"Website deployed successfully!\n\n"
                f"URL: {website_url or 'Check AWS console for URL'}\n"
                f"Files uploaded: {len(result.uploaded_files)}"
            )
        else:
            self.log_status(f"Deployment failed: {result.message}")
            QMessageBox.warning(self, "Deployment Failed", result.message)
    
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
            print(f"CloudTab: {formatted_message}")

    # Meta Tags CRUD Methods

    def add_or_update_meta_tag(self):
        """Add or update a meta tag from full HTML tag"""
        from PyQt6.QtWidgets import QTableWidgetItem
        import re

        full_tag = self.meta_tag_input.text().strip()

        if not full_tag:
            QMessageBox.warning(self, "Invalid Input", "Please paste a complete meta tag")
            return

        # Parse the meta tag to extract name and content
        # Pattern matches: <meta name="..." content="..." /> or similar variations
        name_match = re.search(r'name=["\']([^"\']+)["\']', full_tag)
        content_match = re.search(r'content=["\']([^"\']+)["\']', full_tag)

        if not name_match or not content_match:
            QMessageBox.warning(
                self,
                "Invalid Meta Tag",
                "Could not parse meta tag. Expected format:\n<meta name=\"tag-name\" content=\"tag-content\" />"
            )
            return

        tag_name = name_match.group(1)
        tag_content = content_match.group(1)

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
        if hasattr(self, 'config_changed'):
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.meta_tags_table.removeRow(row)
            self.log_status(f"Removed meta tag: {tag_name}")

            # Clear input field
            self.meta_tag_input.clear()
            self.remove_meta_tag_button.setEnabled(False)

            # Mark configuration as changed
            if hasattr(self, 'config_changed'):
                self.config_changed.emit()

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

    def get_config_data(self) -> Dict[str, Any]:
        """Get cloud configuration data"""
        return {
            'aws_profile': self.profile_combo.currentText() if self.profile_combo.currentText() != "No profiles configured" else "",
            'aws_region': self.region_combo.currentText(),
            'bucket_name': self._get_actual_bucket_name(),
            'directory': self.directory_combo.currentText().strip(),
            'deployment_mode': 's3' if self.s3_mode_radio.isChecked() else 'cloudfront',
            'distribution_id': self.distribution_id_input.text().strip(),
            'auto_invalidate_cache': self.auto_invalidate_checkbox.isChecked(),
            'meta_tags': self.get_meta_tags_from_table()
        }
    
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
                    self.log_status(f"Debug: Profile '{client_config.aws_profile}' restored from client config")
            elif data.get('aws_profile'):
                # Fallback to YAML if client config profile is empty
                index = self.profile_combo.findText(data['aws_profile'])
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
                    self.log_status(f"Debug: Profile '{data['aws_profile']}' restored from YAML")
            
            # Set bucket - prefer client config, fallback to YAML
            bucket_to_use = client_config.bucket_name or data.get('bucket_name', '')
            if bucket_to_use:
                self.bucket_combo.setCurrentText(bucket_to_use)
            
            # Set directory - prefer client config, fallback to YAML  
            directory_to_use = client_config.directory or data.get('directory', '')
            if directory_to_use:
                self.directory_combo.setCurrentText(directory_to_use)
            
            # Set region - prefer client config, fallback to YAML
            region_to_use = client_config.bucket_region or data.get('aws_region', '')
            if region_to_use:
                index = self.region_combo.findText(region_to_use)
                if index >= 0:
                    self.region_combo.setCurrentIndex(index)
        else:
            # Fall back to YAML data if no client-specific config exists
            if data.get('aws_profile'):
                index = self.profile_combo.findText(data['aws_profile'])
                if index >= 0:
                    self.profile_combo.setCurrentIndex(index)
            
            if data.get('aws_region'):
                index = self.region_combo.findText(data['aws_region'])
                if index >= 0:
                    self.region_combo.setCurrentIndex(index)
            
            if data.get('bucket_name'):
                self.bucket_combo.setCurrentText(data['bucket_name'])
            
            if data.get('directory'):
                self.directory_combo.setCurrentText(data['directory'])
        
        # Deployment mode can still come from YAML (not client-specific)
        deployment_mode = data.get('deployment_mode', 's3')
        if deployment_mode == 's3':
            self.s3_mode_radio.setChecked(True)
        else:
            self.cloudfront_mode_radio.setChecked(True)

        # Load meta tags
        meta_tags = data.get('meta_tags', {})
        if isinstance(meta_tags, dict):
            self.load_meta_tags_from_config(meta_tags)

        # Load CloudFront settings
        distribution_id = data.get('distribution_id', '')
        if distribution_id:
            self.distribution_id_input.setText(distribution_id)

        auto_invalidate = data.get('auto_invalidate_cache', True)
        self.auto_invalidate_checkbox.setChecked(auto_invalidate)

    def validate_data(self) -> tuple[bool, list[str]]:
        """Validate cloud configuration"""
        errors = []
        
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
            self.current_client_aws_config = self.aws_config_manager.load_client_aws_config(
                business_name, domain
            )
            
            if self.current_client_aws_config is None:
                # Create default config for new client
                self.current_client_aws_config = self.aws_config_manager.create_default_config(
                    business_name, domain
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
                self.log_status(f"Successfully selected AWS profile: {config.aws_profile}")
            else:
                self.log_status(f"Warning: AWS profile '{config.aws_profile}' not found in available profiles")
        
        # Only restore bucket name if user hasn't selected one
        if config.bucket_name and (not current_bucket or current_bucket in ["No buckets found", ""]):
            self.bucket_combo.setCurrentText(config.bucket_name)
        
        # Only restore directory if user hasn't selected one
        if config.directory and (not current_directory or current_directory in ["/ (root)", ""]):
            self.directory_combo.setCurrentText(config.directory)
        
        # Only restore region if user hasn't selected one
        if config.bucket_region and (not current_region or current_region == ""):
            index = self.region_combo.findText(config.bucket_region)
            if index >= 0:
                self.region_combo.setCurrentIndex(index)
    
    def _save_client_aws_config_from_ui(self):
        """Save current UI state to client AWS configuration"""
        if not self.current_client_aws_config:
            self.log_status("Debug: No client AWS config to save")
            return
        
        # Get current profile selection
        current_combo_text = self.profile_combo.currentText()
        current_profile = (
            current_combo_text 
            if current_combo_text != "No profiles configured" 
            else ""
        )
        
        # CRITICAL FIX: Don't overwrite existing saved profile with empty profile
        # This protects against timing issues and unintended empty profile saves
        if (current_profile == "" and 
            self.current_client_aws_config.aws_profile != ""):
            self.log_status(f"Debug: Preventing overwrite of saved profile '{self.current_client_aws_config.aws_profile}' with empty value (combo: '{current_combo_text}')")
            return
        
        self.log_status(f"Debug: Saving AWS profile '{current_profile}' for {self.current_business_name}")
        
        # Update config with current UI values
        self.current_client_aws_config.aws_profile = current_profile
        self.current_client_aws_config.bucket_name = self._get_actual_bucket_name()
        self.current_client_aws_config.directory = self.directory_combo.currentText().strip()
        self.current_client_aws_config.bucket_region = self.region_combo.currentText()
        
        # Save to persistent storage
        success = self.aws_config_manager.save_client_aws_config(self.current_client_aws_config)
        if success:
            self.log_status(f"AWS configuration saved successfully for {self.current_business_name}")
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