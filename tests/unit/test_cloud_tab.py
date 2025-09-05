"""
Unit tests for CloudTab UI component
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from src.ui.components.cloud_tab import CloudTab, AWSProfileDialog, DeploymentWorker
from src.core.aws.credentials import AuthMethod, AWSProfile
from src.core.aws.s3_manager import UploadResult, UploadProgress


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit here - let pytest handle cleanup


@pytest.mark.ui
@pytest.mark.unit
class TestAWSProfileDialog:
    """Test AWS Profile Dialog"""
    
    def test_dialog_initialization(self, qapp):
        """Test dialog initialization"""
        dialog = AWSProfileDialog(existing_profiles=["profile1", "profile2"])
        
        assert dialog.existing_profiles == ["profile1", "profile2"]
        assert dialog.windowTitle() == "AWS Profile Setup"
        assert dialog.profile_name_input is not None
        assert dialog.description_input is not None
        assert dialog.sso_radio is not None
        assert dialog.access_keys_radio is not None
        assert dialog.sso_radio.isChecked() is True  # Default to SSO
    
    def test_get_profile_data_sso(self, qapp):
        """Test getting SSO profile data"""
        dialog = AWSProfileDialog()
        
        # Set form data
        dialog.profile_name_input.setText("test-sso")
        dialog.description_input.setText("Test SSO Profile")
        dialog.sso_url_input.setText("https://test.awsapps.com/start")
        dialog.sso_region_combo.setCurrentText("us-west-2")
        dialog.region_combo.setCurrentText("eu-west-1")
        dialog.sso_radio.setChecked(True)
        
        data = dialog.get_profile_data()
        
        assert data['name'] == "test-sso"
        assert data['description'] == "Test SSO Profile"
        assert data['auth_method'] == AuthMethod.SSO
        assert data['sso_start_url'] == "https://test.awsapps.com/start"
        assert data['sso_region'] == "us-west-2"
        assert data['region'] == "eu-west-1"
    
    def test_get_profile_data_access_keys(self, qapp):
        """Test getting Access Keys profile data"""
        dialog = AWSProfileDialog()
        
        # Set form data
        dialog.profile_name_input.setText("test-keys")
        dialog.description_input.setText("Test Keys Profile")
        dialog.region_combo.setCurrentText("us-east-1")
        dialog.access_keys_radio.setChecked(True)
        
        data = dialog.get_profile_data()
        
        assert data['name'] == "test-keys"
        assert data['description'] == "Test Keys Profile"
        assert data['auth_method'] == AuthMethod.ACCESS_KEYS
        assert data['region'] == "us-east-1"


@pytest.mark.ui
@pytest.mark.unit
class TestCloudTab:
    """Test CloudTab component"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Don't create QApplication here - use fixture
        pass
    
    def test_cloud_tab_initialization(self, qapp):
        """Test CloudTab initialization"""
        tab = CloudTab()
        
        assert tab.credentials_manager is not None
        assert tab.s3_manager is not None
        assert tab.deployment_worker is None
        
        # Check UI components exist
        assert tab.profile_combo is not None
        assert tab.bucket_input is not None
        assert tab.region_combo is not None
        assert tab.s3_mode_radio is not None
        assert tab.cloudfront_mode_radio is not None
        assert tab.deploy_button is not None
        assert tab.progress_bar is not None
        assert tab.status_text is not None
    
    def test_profile_combo_default_state(self, qapp):
        """Test profile combo default state"""
        tab = CloudTab()
        
        # Should show "No profiles configured" by default
        assert tab.profile_combo.currentText() == "No profiles configured"
        assert tab.profile_status_label.text() == "No profile selected"
    
    def test_deployment_mode_default(self, qapp):
        """Test default deployment mode"""
        tab = CloudTab()
        
        assert tab.s3_mode_radio.isChecked() is True
        assert tab.cloudfront_mode_radio.isChecked() is False
        assert tab.cloudfront_mode_radio.isEnabled() is False  # Phase 2 feature
    
    @patch('src.ui.components.cloud_tab.AWSProfileDialog')
    def test_create_new_profile_success(self, mock_dialog, qapp):
        """Test successful profile creation"""
        tab = CloudTab()
        
        # Mock dialog
        dialog_instance = Mock()
        dialog_instance.exec.return_value = QMessageBox.DialogCode.Accepted
        dialog_instance.get_profile_data.return_value = {
            'name': 'test-profile',
            'description': 'Test Profile',
            'auth_method': AuthMethod.SSO,
            'sso_start_url': 'https://test.awsapps.com/start',
            'sso_region': 'us-east-1',
            'region': 'us-east-1'
        }
        mock_dialog.return_value = dialog_instance
        
        with patch.object(QMessageBox, 'information') as mock_info:
            tab.create_new_profile()
            
            # Verify profile was added
            assert 'test-profile' in tab.credentials_manager.profiles
            profile = tab.credentials_manager.profiles['test-profile']
            assert profile.auth_method == AuthMethod.SSO
            assert profile.sso_start_url == 'https://test.awsapps.com/start'
            
            # Verify success message
            mock_info.assert_called_once()
    
    @patch('src.ui.components.cloud_tab.AWSProfileDialog')
    def test_create_new_profile_cancelled(self, mock_dialog, qapp):
        """Test cancelled profile creation"""
        tab = CloudTab()
        
        # Mock dialog cancellation
        dialog_instance = Mock()
        dialog_instance.exec.return_value = QMessageBox.DialogCode.Rejected
        mock_dialog.return_value = dialog_instance
        
        initial_profiles = len(tab.credentials_manager.profiles)
        tab.create_new_profile()
        
        # Verify no profile was added
        assert len(tab.credentials_manager.profiles) == initial_profiles
    
    @patch('src.ui.components.cloud_tab.AWSProfileDialog')
    def test_create_new_profile_empty_name(self, mock_dialog, qapp):
        """Test profile creation with empty name"""
        tab = CloudTab()
        
        # Mock dialog with empty name
        dialog_instance = Mock()
        dialog_instance.exec.return_value = QMessageBox.DialogCode.Accepted
        dialog_instance.get_profile_data.return_value = {
            'name': '',  # Empty name
            'description': 'Test Profile',
            'auth_method': AuthMethod.SSO,
            'sso_start_url': 'https://test.awsapps.com/start',
            'sso_region': 'us-east-1',
            'region': 'us-east-1'
        }
        mock_dialog.return_value = dialog_instance
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            tab.create_new_profile()
            
            # Verify warning was shown
            mock_warning.assert_called_once()
            args, kwargs = mock_warning.call_args
            assert "Profile name is required" in args[2]
    
    def test_refresh_profiles_empty(self, qapp):
        """Test refreshing profiles when none exist"""
        tab = CloudTab()
        
        tab.refresh_profiles()
        
        assert tab.profile_combo.currentText() == "No profiles configured"
    
    def test_refresh_profiles_with_data(self, qapp):
        """Test refreshing profiles with existing profiles"""
        tab = CloudTab()
        
        # Add test profiles
        tab.credentials_manager.add_sso_profile("profile1", "https://test1.awsapps.com/start")
        tab.credentials_manager.add_access_key_profile("profile2")
        
        tab.refresh_profiles()
        
        assert tab.profile_combo.count() == 2
        items = [tab.profile_combo.itemText(i) for i in range(tab.profile_combo.count())]
        assert "profile1" in items
        assert "profile2" in items
    
    def test_on_profile_changed_valid(self, qapp):
        """Test profile change with valid profile"""
        tab = CloudTab()
        
        # Add test profile
        profile = tab.credentials_manager.add_sso_profile(
            "test-profile", 
            "https://test.awsapps.com/start",
            region="us-west-2"
        )
        
        tab.on_profile_changed("test-profile")
        
        assert "sso" in tab.profile_status_label.text()
        assert "us-west-2" in tab.profile_status_label.text()
        assert tab.region_combo.currentText() == "us-west-2"
    
    def test_on_profile_changed_invalid(self, qapp):
        """Test profile change with invalid profile"""
        tab = CloudTab()
        
        tab.on_profile_changed("nonexistent")
        
        assert "not found" in tab.profile_status_label.text()
    
    @patch('src.core.aws.credentials.AWSCredentialsManager.validate_profile')
    def test_test_aws_connection_success(self, mock_validate, qapp):
        """Test successful AWS connection test"""
        tab = CloudTab()
        
        # Add test profile
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        
        # Mock successful validation
        mock_validate.return_value = (True, "Success", {
            'account': '123456789012',
            'region': 'us-east-1'
        })
        
        with patch.object(QMessageBox, 'information') as mock_info:
            tab.test_aws_connection()
            
            mock_info.assert_called_once()
            args, kwargs = mock_info.call_args
            assert "Successfully connected" in args[2]
            assert "123456789012" in args[2]
    
    @patch('src.core.aws.credentials.AWSCredentialsManager.validate_profile')
    def test_test_aws_connection_failure(self, mock_validate, qapp):
        """Test failed AWS connection test"""
        tab = CloudTab()
        
        # Add test profile
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        
        # Mock failed validation
        mock_validate.return_value = (False, "No credentials found", {})
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            tab.test_aws_connection()
            
            mock_warning.assert_called_once()
            args, kwargs = mock_warning.call_args
            assert "Connection Failed" in args[1]
            assert "No credentials found" in args[2]
    
    def test_on_bucket_name_changed_valid(self, qapp):
        """Test bucket name change validation - valid name"""
        tab = CloudTab()
        
        tab.bucket_input.setText("client-website-test-123456")
        tab.on_bucket_name_changed()
        
        assert "valid" in tab.bucket_status_label.text()
        assert "color: green" in tab.bucket_status_label.styleSheet()
    
    def test_on_bucket_name_changed_invalid(self, qapp):
        """Test bucket name change validation - invalid name"""
        tab = CloudTab()
        
        tab.bucket_input.setText("INVALID-NAME")
        tab.on_bucket_name_changed()
        
        assert "Invalid" in tab.bucket_status_label.text()
        assert "color: red" in tab.bucket_status_label.styleSheet()
    
    def test_on_bucket_name_changed_empty(self, qapp):
        """Test bucket name change validation - empty name"""
        tab = CloudTab()
        
        tab.bucket_input.setText("")
        tab.on_bucket_name_changed()
        
        assert "No bucket configured" in tab.bucket_status_label.text()
        assert "color: #666" in tab.bucket_status_label.styleSheet()
    
    def test_update_deploy_button_state_enabled(self, qapp):
        """Test deploy button enabled state"""
        tab = CloudTab()
        
        # Add profile and set bucket
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        tab.bucket_input.setText("client-website-test-123456")
        
        tab.update_deploy_button_state()
        
        assert tab.deploy_button.isEnabled() is True
    
    def test_update_deploy_button_state_disabled(self, qapp):
        """Test deploy button disabled state"""
        tab = CloudTab()
        
        # No profile or bucket configured
        tab.update_deploy_button_state()
        
        assert tab.deploy_button.isEnabled() is False
    
    def test_get_config_data(self, qapp):
        """Test getting configuration data"""
        tab = CloudTab()
        
        # Set test data
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        tab.bucket_input.setText("client-website-test-123456")
        tab.region_combo.setCurrentText("us-west-2")
        tab.s3_mode_radio.setChecked(True)
        
        config_data = tab.get_config_data()
        
        assert config_data['aws_profile'] == "test-profile"
        assert config_data['aws_region'] == "us-west-2"
        assert config_data['bucket_name'] == "client-website-test-123456"
        assert config_data['deployment_mode'] == "s3"
    
    def test_set_config_data(self, qapp):
        """Test setting configuration data"""
        tab = CloudTab()
        
        # Add profile first
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        
        config_data = {
            'aws_profile': 'test-profile',
            'aws_region': 'us-west-2',
            'bucket_name': 'client-website-test-123456',
            'deployment_mode': 's3'
        }
        
        tab.set_config_data(config_data)
        
        assert tab.profile_combo.currentText() == "test-profile"
        assert tab.region_combo.currentText() == "us-west-2"
        assert tab.bucket_input.text() == "client-website-test-123456"
        assert tab.s3_mode_radio.isChecked() is True
    
    def test_validate_data_success(self, qapp):
        """Test successful data validation"""
        tab = CloudTab()
        
        # Set valid data
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        tab.bucket_input.setText("client-website-test-123456")
        
        is_valid, errors = tab.validate_data()
        
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_data_no_profile(self, qapp):
        """Test validation with no profile"""
        tab = CloudTab()
        
        # No profile selected
        tab.bucket_input.setText("client-website-test-123456")
        
        is_valid, errors = tab.validate_data()
        
        assert is_valid is False
        assert len(errors) == 1
        assert "AWS profile is required" in errors[0]
    
    def test_validate_data_no_bucket(self, qapp):
        """Test validation with no bucket"""
        tab = CloudTab()
        
        # Set profile but no bucket
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        
        is_valid, errors = tab.validate_data()
        
        assert is_valid is False
        assert len(errors) == 1
        assert "bucket name is required" in errors[0]
    
    def test_validate_data_invalid_bucket(self, qapp):
        """Test validation with invalid bucket name"""
        tab = CloudTab()
        
        # Set profile and invalid bucket
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        tab.bucket_input.setText("INVALID-BUCKET-NAME")
        
        is_valid, errors = tab.validate_data()
        
        assert is_valid is False
        assert len(errors) == 1
        assert "Invalid bucket name" in errors[0]
    
    def test_log_status(self, qapp):
        """Test status logging"""
        tab = CloudTab()
        
        tab.log_status("Test message")
        
        text_content = tab.status_text.toPlainText()
        assert "Test message" in text_content
        assert "[" in text_content  # Timestamp should be present


@pytest.mark.unit
class TestDeploymentWorker:
    """Test DeploymentWorker thread"""
    
    def test_deployment_worker_initialization(self):
        """Test DeploymentWorker initialization"""
        s3_manager = Mock()
        worker = DeploymentWorker(s3_manager, "/test/path", "test-bucket")
        
        assert worker.s3_manager == s3_manager
        assert worker.local_path == "/test/path"
        assert worker.bucket_name == "test-bucket"
    
    def test_deployment_worker_run_success(self):
        """Test successful deployment worker run"""
        s3_manager = Mock()
        s3_manager.upload_directory.return_value = UploadResult(
            success=True,
            message="Upload completed",
            uploaded_files=["index.html"]
        )
        
        worker = DeploymentWorker(s3_manager, "/test/path", "test-bucket")
        
        # Mock the signals
        worker.progress_updated = Mock()
        worker.deployment_completed = Mock()
        
        worker.run()
        
        # Verify S3 manager was called correctly
        s3_manager.set_progress_callback.assert_called_once()
        s3_manager.upload_directory.assert_called_once_with("/test/path", "test-bucket")
        
        # Verify completion signal was emitted
        worker.deployment_completed.emit.assert_called_once()
        result = worker.deployment_completed.emit.call_args[0][0]
        assert result.success is True
        assert result.message == "Upload completed"