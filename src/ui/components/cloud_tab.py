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
    QProgressBar, QMessageBox, QDialog, QDialogButtonBox, QListWidget,
    QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QPalette
from typing import Dict, Any, Optional, List

from .base_tab import BaseTab
from ...core.aws.credentials import AWSCredentialsManager, AWSProfile, AuthMethod
from ...core.aws.s3_manager import S3Manager, UploadProgress, UploadResult
from ...core.security.api_key_manager import api_key_manager


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
        self.sso_radio = QRadioButton("AWS SSO (Recommended)")
        self.sso_radio.setChecked(True)
        self.access_keys_radio = QRadioButton("Access Keys")
        
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
        
        self.config_layout.addWidget(QLabel("SSO Region:"), 1, 0)
        self.sso_region_combo = QComboBox()
        self.sso_region_combo.addItems(["us-east-1", "us-west-2", "eu-west-1"])
        self.config_layout.addWidget(self.sso_region_combo, 1, 1)
        
        self.config_layout.addWidget(QLabel("Default Region:"), 2, 0)
        self.region_combo = QComboBox()
        self.region_combo.addItems(["us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1"])
        self.config_layout.addWidget(self.region_combo, 2, 1)
        
        self.config_group.setLayout(self.config_layout)
        layout.addWidget(self.config_group)
        
        # Connect signals
        self.auth_button_group.buttonClicked.connect(self.on_auth_method_changed)
        
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
        # For now, keep SSO fields visible for both methods
        # Access key configuration would be handled through secure storage
        pass
    
    def get_profile_data(self) -> Dict[str, Any]:
        """Get profile configuration data"""
        auth_method = AuthMethod.SSO if self.sso_radio.isChecked() else AuthMethod.ACCESS_KEYS
        
        return {
            'name': self.profile_name_input.text().strip(),
            'description': self.description_input.text().strip(),
            'auth_method': auth_method,
            'sso_start_url': self.sso_url_input.text().strip(),
            'sso_region': self.sso_region_combo.currentText(),
            'region': self.region_combo.currentText()
        }


class DeploymentWorker(QThread):
    """Background worker for deployment operations"""
    
    progress_updated = pyqtSignal(UploadProgress)
    deployment_completed = pyqtSignal(UploadResult)
    
    def __init__(self, s3_manager: S3Manager, local_path: str, bucket_name: str):
        super().__init__()
        self.s3_manager = s3_manager
        self.local_path = local_path
        self.bucket_name = bucket_name
    
    def run(self):
        """Execute deployment in background"""
        # Set up progress callback
        self.s3_manager.set_progress_callback(self.progress_updated.emit)
        
        # Upload directory
        result = self.s3_manager.upload_directory(self.local_path, self.bucket_name)
        
        self.deployment_completed.emit(result)


class CloudTab(BaseTab):
    """Cloud deployment configuration tab"""
    
    def __init__(self, parent=None):
        self.credentials_manager = AWSCredentialsManager()
        self.s3_manager = S3Manager()
        self.deployment_worker: Optional[DeploymentWorker] = None
        
        # UI components
        self.profile_combo = None
        self.bucket_input = None
        self.region_combo = None
        self.deployment_mode_group = None
        self.s3_mode_radio = None
        self.cloudfront_mode_radio = None
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
        
        # Deployment Mode Section
        mode_group = self.create_deployment_mode_section()
        layout.addWidget(mode_group)
        
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
        layout.addWidget(self.profile_combo, 0, 1)
        
        # Profile management buttons
        self.new_profile_button = QPushButton("New Profile")
        self.test_connection_button = QPushButton("Test Connection")
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.new_profile_button)
        button_layout.addWidget(self.test_connection_button)
        button_layout.addStretch()
        
        layout.addLayout(button_layout, 1, 0, 1, 3)
        
        # Profile status
        self.profile_status_label = QLabel("No profile selected")
        self.profile_status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.profile_status_label, 2, 0, 1, 3)
        
        group.setLayout(layout)
        
        # Connect signals
        self.new_profile_button.clicked.connect(self.create_new_profile)
        self.test_connection_button.clicked.connect(self.test_aws_connection)
        self.profile_combo.currentTextChanged.connect(self.on_profile_changed)
        
        # Load existing profiles
        self.refresh_profiles()
        
        return group
    
    def create_bucket_section(self) -> QGroupBox:
        """Create S3 bucket configuration section"""
        group = QGroupBox("S3 Bucket Configuration")
        layout = QGridLayout()
        
        # Bucket name
        layout.addWidget(QLabel("Bucket Name:"), 0, 0)
        self.bucket_input = QLineEdit()
        self.bucket_input.setPlaceholderText("client-website-projectname")
        layout.addWidget(self.bucket_input, 0, 1)
        
        self.create_bucket_button = QPushButton("Create Bucket")
        layout.addWidget(self.create_bucket_button, 0, 2)
        
        # Region
        layout.addWidget(QLabel("Region:"), 1, 0)
        self.region_combo = QComboBox()
        self.region_combo.addItems([
            "us-east-1", "us-west-2", "eu-west-1", "ap-southeast-1",
            "eu-central-1", "ap-northeast-1"
        ])
        layout.addWidget(self.region_combo, 1, 1)
        
        # Bucket status
        self.bucket_status_label = QLabel("No bucket configured")
        self.bucket_status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.bucket_status_label, 2, 0, 1, 3)
        
        group.setLayout(layout)
        
        # Connect signals
        self.create_bucket_button.clicked.connect(self.create_s3_bucket)
        self.bucket_input.textChanged.connect(self.on_bucket_name_changed)
        
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
            else:
                profile = self.credentials_manager.add_access_key_profile(
                    name=profile_data['name'],
                    region=profile_data['region']
                )
            
            profile.description = profile_data['description']
            
            self.refresh_profiles()
            self.profile_combo.setCurrentText(profile_data['name'])
            
            QMessageBox.information(
                self, 
                "Profile Created", 
                f"AWS profile '{profile_data['name']}' created successfully.\n\n"
                "For SSO profiles, you'll need to run 'aws configure sso' in your terminal "
                "with the same profile name to complete the setup."
            )
    
    def refresh_profiles(self):
        """Refresh profile dropdown"""
        current_text = self.profile_combo.currentText()
        self.profile_combo.clear()
        
        profiles = list(self.credentials_manager.profiles.keys())
        if profiles:
            self.profile_combo.addItems(profiles)
            if current_text in profiles:
                self.profile_combo.setCurrentText(current_text)
        else:
            self.profile_combo.addItem("No profiles configured")
    
    def on_profile_changed(self, profile_name: str):
        """Handle profile selection change"""
        if profile_name == "No profiles configured":
            self.profile_status_label.setText("No profile selected")
            return
        
        if profile_name in self.credentials_manager.profiles:
            profile = self.credentials_manager.profiles[profile_name]
            self.profile_status_label.setText(f"Profile: {profile.auth_method.value} | Region: {profile.region}")
            self.region_combo.setCurrentText(profile.region)
            self.update_deploy_button_state()
        else:
            self.profile_status_label.setText("Profile not found")
    
    def test_aws_connection(self):
        """Test AWS connection for selected profile"""
        profile_name = self.profile_combo.currentText()
        if profile_name == "No profiles configured":
            QMessageBox.warning(self, "No Profile", "Please create an AWS profile first")
            return
        
        is_valid, message, identity = self.credentials_manager.validate_profile(profile_name)
        
        if is_valid:
            account = identity.get('account', 'Unknown')
            region = identity.get('region', 'Unknown')
            QMessageBox.information(
                self, 
                "Connection Successful", 
                f"Successfully connected to AWS\n\n"
                f"Account: {account}\n"
                f"Region: {region}\n"
                f"Profile: {profile_name}"
            )
            
            # Update S3 manager with validated session
            session = self.credentials_manager.get_active_session()
            if session:
                self.s3_manager.set_session(session)
            
        else:
            QMessageBox.warning(self, "Connection Failed", f"AWS connection failed:\n\n{message}")
    
    def on_bucket_name_changed(self):
        """Handle bucket name change"""
        bucket_name = self.bucket_input.text().strip()
        
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
    
    def create_s3_bucket(self):
        """Create S3 bucket"""
        profile_name = self.profile_combo.currentText()
        bucket_name = self.bucket_input.text().strip()
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
        
        # Create bucket
        success, message = self.s3_manager.create_bucket(bucket_name, region)
        
        if success:
            QMessageBox.information(self, "Bucket Created", message)
            self.bucket_status_label.setText("Bucket ready for deployment")
            self.bucket_status_label.setStyleSheet("color: green;")
        else:
            QMessageBox.warning(self, "Bucket Creation Failed", message)
    
    def on_deployment_mode_changed(self):
        """Handle deployment mode change"""
        if self.s3_mode_radio.isChecked():
            self.mode_description.setText("S3 Static Website: Direct hosting from S3 bucket with public access")
        else:
            self.mode_description.setText("CloudFront + OAC: Production-ready hosting with CDN (Coming in Phase 2)")
    
    def update_deploy_button_state(self):
        """Update deploy button enabled state"""
        profile_selected = (self.profile_combo.currentText() != "No profiles configured")
        bucket_configured = bool(self.bucket_input.text().strip())
        
        self.deploy_button.setEnabled(profile_selected and bucket_configured)
    
    def start_deployment(self):
        """Start website deployment"""
        # This would be called by the main window after website generation
        # For now, show a placeholder message
        QMessageBox.information(
            self,
            "Deployment Ready",
            "Cloud deployment tab is ready!\n\n"
            "This will be integrated with the website generation process "
            "in the main application window."
        )
    
    def deploy_website(self, website_path: str):
        """Deploy generated website to cloud"""
        profile_name = self.profile_combo.currentText()
        bucket_name = self.bucket_input.text().strip()
        
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
        
        # Start deployment worker
        self.deployment_worker = DeploymentWorker(self.s3_manager, website_path, bucket_name)
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
            bucket_name = self.bucket_input.text().strip()
            region = self.region_combo.currentText()
            website_url = self.s3_manager.get_website_url(bucket_name, region)
            
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
        self.status_text.append(f"[{timestamp}] {message}")
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get cloud configuration data"""
        return {
            'aws_profile': self.profile_combo.currentText() if self.profile_combo.currentText() != "No profiles configured" else "",
            'aws_region': self.region_combo.currentText(),
            'bucket_name': self.bucket_input.text().strip(),
            'deployment_mode': 's3' if self.s3_mode_radio.isChecked() else 'cloudfront'
        }
    
    def set_config_data(self, data: Dict[str, Any]):
        """Set cloud configuration data"""
        # Refresh profiles first
        self.refresh_profiles()
        
        if data.get('aws_profile'):
            index = self.profile_combo.findText(data['aws_profile'])
            if index >= 0:
                self.profile_combo.setCurrentIndex(index)
        
        if data.get('aws_region'):
            index = self.region_combo.findText(data['aws_region'])
            if index >= 0:
                self.region_combo.setCurrentIndex(index)
        
        if data.get('bucket_name'):
            self.bucket_input.setText(data['bucket_name'])
        
        deployment_mode = data.get('deployment_mode', 's3')
        if deployment_mode == 's3':
            self.s3_mode_radio.setChecked(True)
        else:
            self.cloudfront_mode_radio.setChecked(True)
    
    def validate_data(self) -> tuple[bool, list[str]]:
        """Validate cloud configuration"""
        errors = []
        
        profile_name = self.profile_combo.currentText()
        if not profile_name or profile_name == "No profiles configured":
            errors.append("AWS profile is required for cloud deployment")
        
        bucket_name = self.bucket_input.text().strip()
        if not bucket_name:
            errors.append("S3 bucket name is required")
        else:
            is_valid, message = self.s3_manager.validate_bucket_name(bucket_name)
            if not is_valid:
                errors.append(f"Invalid bucket name: {message}")
        
        return len(errors) == 0, errors