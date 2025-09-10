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
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_configure_sso_cli_windows(self, mock_system, mock_subprocess, qapp):
        """Test SSO CLI configuration on Windows"""
        mock_system.return_value = "Windows"
        dialog = AWSProfileDialog()
        dialog.profile_name_input.setText("test-profile")
        
        with patch.object(QMessageBox, 'information') as mock_info:
            dialog.configure_sso_cli()
        
        # Should try Windows Terminal first
        mock_subprocess.assert_called()
        mock_info.assert_called_once()
        
        # Check that the correct command was used
        call_args = mock_subprocess.call_args[0][0]
        assert "test-profile" in str(call_args)
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_configure_sso_cli_macos(self, mock_system, mock_subprocess, qapp):
        """Test SSO CLI configuration on macOS"""
        mock_system.return_value = "Darwin"
        dialog = AWSProfileDialog()
        dialog.profile_name_input.setText("test-profile")
        
        with patch.object(QMessageBox, 'information') as mock_info:
            dialog.configure_sso_cli()
        
        mock_subprocess.assert_called()
        mock_info.assert_called_once()
        
        # Check osascript was called for macOS
        call_args = mock_subprocess.call_args[0][0]
        assert call_args[0] == "osascript"
    
    @patch('subprocess.run')
    @patch('platform.system')  
    def test_configure_sso_cli_linux(self, mock_system, mock_subprocess, qapp):
        """Test SSO CLI configuration on Linux"""
        mock_system.return_value = "Linux"
        dialog = AWSProfileDialog()
        dialog.profile_name_input.setText("test-profile")
        
        with patch.object(QMessageBox, 'information') as mock_info:
            dialog.configure_sso_cli()
        
        mock_subprocess.assert_called()
        mock_info.assert_called_once()
    
    def test_configure_sso_cli_no_profile_name(self, qapp):
        """Test SSO CLI configuration with no profile name"""
        dialog = AWSProfileDialog()
        dialog.profile_name_input.setText("")
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            dialog.configure_sso_cli()
        
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "Profile Name Required" in args[1]
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_configure_sso_cli_subprocess_error(self, mock_system, mock_subprocess, qapp):
        """Test SSO CLI configuration with subprocess error"""
        mock_system.return_value = "Windows"
        mock_subprocess.side_effect = Exception("Process failed")
        dialog = AWSProfileDialog()
        dialog.profile_name_input.setText("test-profile")
        
        with patch.object(QMessageBox, 'critical') as mock_critical:
            dialog.configure_sso_cli()
        
        mock_critical.assert_called_once()
        args = mock_critical.call_args[0]
        assert "Failed to open terminal" in args[2]
    
    def test_show_sso_help(self, qapp):
        """Test showing SSO help dialog"""
        dialog = AWSProfileDialog()
        
        with patch.object(QMessageBox, 'exec') as mock_exec:
            dialog.show_sso_help()
        
        mock_exec.assert_called_once()


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
        assert tab.bucket_combo is not None
        assert tab.directory_combo is not None
        assert tab.region_combo is not None
        assert tab.s3_mode_radio is not None
        assert tab.cloudfront_mode_radio is not None
        assert tab.deploy_button is not None
        assert tab.progress_bar is not None
        assert tab.status_text is not None
    
    @patch('src.core.aws.credentials.AWSCredentialsManager._load_profiles')
    def test_profile_combo_default_state(self, mock_load_profiles, qapp):
        """Test profile combo default state"""
        # Mock to prevent loading persistent profiles
        mock_load_profiles.return_value = None
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
    @patch('src.core.aws.credentials.AWSCredentialsManager._load_profiles')
    @patch('src.core.aws.credentials.AWSCredentialsManager._save_profiles')
    def test_create_new_profile_success(self, mock_save_profiles, mock_load_profiles, mock_dialog, qapp):
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
    
    @patch('src.core.aws.credentials.AWSCredentialsManager._load_profiles')
    def test_refresh_profiles_empty(self, mock_load_profiles, qapp):
        """Test refreshing profiles when none exist"""
        mock_load_profiles.return_value = None
        tab = CloudTab()
        
        tab.refresh_profiles()
        
        assert tab.profile_combo.currentText() == "No profiles configured"
    
    @patch('src.core.aws.credentials.AWSCredentialsManager._load_profiles')
    def test_refresh_profiles_with_data(self, mock_load_profiles, qapp):
        """Test refreshing profiles with existing profiles"""
        mock_load_profiles.return_value = None
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
        
        tab.bucket_combo.setCurrentText("client-website-test-123456")
        tab.on_bucket_name_changed()
        
        assert "valid" in tab.bucket_status_label.text()
        assert "color: green" in tab.bucket_status_label.styleSheet()
    
    def test_on_bucket_name_changed_invalid(self, qapp):
        """Test bucket name change validation - invalid name"""
        tab = CloudTab()
        
        tab.bucket_combo.setCurrentText("INVALID-NAME")
        tab.on_bucket_name_changed()
        
        assert "Invalid" in tab.bucket_status_label.text()
        assert "color: red" in tab.bucket_status_label.styleSheet()
    
    def test_on_bucket_name_changed_empty(self, qapp):
        """Test bucket name change validation - empty name"""
        tab = CloudTab()
        
        tab.bucket_combo.setCurrentText("")
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
        tab.bucket_combo.setCurrentText("client-website-test-123456")
        
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
        tab.bucket_combo.setCurrentText("client-website-test-123456")
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
        assert tab.bucket_combo.currentText() == "client-website-test-123456"
        assert tab.s3_mode_radio.isChecked() is True
    
    def test_validate_data_success(self, qapp):
        """Test successful data validation"""
        tab = CloudTab()
        
        # Set valid data
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        tab.bucket_combo.setCurrentText("client-website-test-123456")
        
        is_valid, errors = tab.validate_data()
        
        assert is_valid is True
        assert len(errors) == 0
    
    @patch('src.core.aws.credentials.AWSCredentialsManager._load_profiles')
    def test_validate_data_no_profile(self, mock_load_profiles, qapp):
        """Test validation with no profile"""
        mock_load_profiles.return_value = None
        tab = CloudTab()
        
        # No profile selected
        tab.bucket_combo.setCurrentText("client-website-test-123456")
        
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
        tab.bucket_combo.setCurrentText("INVALID-BUCKET-NAME")
        
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
    
    def test_configure_existing_profile_sso_no_profile_selected(self, qapp):
        """Test configure SSO with no profile selected"""
        tab = CloudTab()
        tab.profile_combo.addItem("No profiles configured")
        tab.profile_combo.setCurrentText("No profiles configured")
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            tab.configure_existing_profile_sso()
        
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "No Profile Selected" in args[1]
    
    def test_configure_existing_profile_sso_profile_not_found(self, qapp):
        """Test configure SSO with profile not found"""
        tab = CloudTab()
        tab.profile_combo.addItem("nonexistent-profile")
        tab.profile_combo.setCurrentText("nonexistent-profile")
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            tab.configure_existing_profile_sso()
        
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "Profile Not Found" in args[1]
    
    def test_configure_existing_profile_sso_not_sso_profile(self, qapp):
        """Test configure SSO with non-SSO profile"""
        tab = CloudTab()
        
        # Add access key profile
        profile = tab.credentials_manager.add_access_key_profile("test-keys", "us-east-1")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-keys")
        
        with patch.object(QMessageBox, 'information') as mock_info:
            tab.configure_existing_profile_sso()
        
        mock_info.assert_called_once()
        args = mock_info.call_args[0]
        assert "Not an SSO Profile" in args[1]
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_configure_existing_profile_sso_success(self, mock_system, mock_subprocess, qapp):
        """Test successful SSO configuration for existing profile"""
        mock_system.return_value = "Windows"
        tab = CloudTab()
        
        # Add SSO profile
        profile = tab.credentials_manager.add_sso_profile("test-sso", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-sso")
        
        with patch.object(QMessageBox, 'information') as mock_info:
            tab.configure_existing_profile_sso()
        
        mock_subprocess.assert_called()
        mock_info.assert_called_once()
        
        # Check that the correct command was used
        call_args = mock_subprocess.call_args[0][0]
        assert "test-sso" in str(call_args)
    
    @patch('subprocess.run')
    @patch('platform.system')
    def test_configure_existing_profile_sso_subprocess_error(self, mock_system, mock_subprocess, qapp):
        """Test SSO configuration with subprocess error"""
        mock_system.return_value = "Windows"
        mock_subprocess.side_effect = Exception("Terminal failed")
        tab = CloudTab()
        
        # Add SSO profile
        profile = tab.credentials_manager.add_sso_profile("test-sso", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-sso")
        
        with patch.object(QMessageBox, 'critical') as mock_critical:
            tab.configure_existing_profile_sso()
        
        mock_critical.assert_called_once()
        args = mock_critical.call_args[0]
        assert "Failed to open terminal" in args[2]
    
    @patch('src.core.aws.credentials.AWSCredentialsManager._load_profiles')
    def test_refresh_bucket_list_no_profile(self, mock_load_profiles, qapp):
        """Test refresh bucket list with no profile selected"""
        mock_load_profiles.return_value = None
        tab = CloudTab()
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            tab.refresh_bucket_list()
        
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "No Profile Selected" in args[1]
    
    @patch('src.core.aws.credentials.AWSCredentialsManager._load_profiles')
    @patch('src.ui.components.cloud_tab.CloudTab._populate_buckets_for_profile_silently')
    def test_automatic_bucket_population_on_profile_change(self, mock_populate_buckets, mock_load_profiles, qapp):
        """Test that bucket population method is called when profile changes"""
        mock_load_profiles.return_value = None
        tab = CloudTab()
        
        # Add a test profile
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        
        # Trigger profile change
        tab.on_profile_changed("test-profile")
        
        # Verify bucket population method was called
        mock_populate_buckets.assert_called_once_with("test-profile")
    
    @patch('src.core.aws.credentials.AWSCredentialsManager._get_session')
    @patch('src.core.aws.credentials.AWSCredentialsManager.list_client_buckets')
    def test_refresh_bucket_list_success(self, mock_list_buckets, mock_get_session, qapp):
        """Test successful bucket list refresh"""
        tab = CloudTab()
        
        # Setup mocks
        mock_get_session.return_value = Mock()
        mock_list_buckets.return_value = [
            {'name': 'client-website-test-123'},
            {'name': 'client-website-prod-456'}
        ]
        
        # Add profile and refresh
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        
        tab.refresh_bucket_list()
        
        # Check that buckets were added to combo
        assert tab.bucket_combo.count() == 2
        assert tab.bucket_combo.itemText(0) == 'client-website-test-123'
        assert tab.bucket_combo.itemText(1) == 'client-website-prod-456'
    
    def test_refresh_directory_list_no_bucket(self, qapp):
        """Test refresh directory list with no bucket selected"""
        tab = CloudTab()
        
        with patch.object(QMessageBox, 'warning') as mock_warning:
            tab.refresh_directory_list()
        
        mock_warning.assert_called_once()
        args = mock_warning.call_args[0]
        assert "No Bucket Selected" in args[1]
    
    @patch('src.core.aws.credentials.AWSCredentialsManager._get_session')
    @patch('src.core.aws.s3_manager.S3Manager.list_bucket_contents')
    def test_refresh_directory_list_success(self, mock_list_contents, mock_get_session, qapp):
        """Test successful directory list refresh"""
        tab = CloudTab()
        
        # Setup mocks
        mock_get_session.return_value = Mock()
        mock_list_contents.return_value = [
            {'key': 'subdir1/file.html'},
            {'key': 'subdir2/nested/file.css'},
            {'key': 'root-file.html'}
        ]
        
        # Setup tab state
        tab.credentials_manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        tab.refresh_profiles()
        tab.profile_combo.setCurrentText("test-profile")
        tab.bucket_combo.setCurrentText("test-bucket")
        
        tab.refresh_directory_list()
        
        # Check that directories were found (should include root, subdir1/, subdir2/, subdir2/nested/)
        assert tab.directory_combo.count() >= 3  # At least root, subdir1/, subdir2/
    
    def test_on_bucket_selection_changed(self, qapp):
        """Test bucket selection change handling"""
        tab = CloudTab()
        
        tab.on_bucket_selection_changed("test-bucket")
        
        # Should reset directory to root
        assert tab.directory_combo.currentText() == "/ (root)"
        assert "test-bucket" in tab.bucket_status_label.text()
    
    def test_on_directory_selection_changed(self, qapp):
        """Test directory selection change handling"""
        tab = CloudTab()
        
        tab.bucket_combo.setCurrentText("test-bucket")
        tab.on_directory_selection_changed("subdir/")
        
        assert "test-bucket" in tab.bucket_status_label.text()
        assert "subdir/" in tab.bucket_status_label.text()
    
    def test_check_directory_exists_true(self, qapp):
        """Test directory existence check - directory exists"""
        tab = CloudTab()
        
        with patch.object(tab.s3_manager, 'list_bucket_contents') as mock_list:
            mock_list.return_value = [
                {'key': 'testdir/file1.html'},
                {'key': 'testdir/file2.css'},
                {'key': 'other/file.html'}
            ]
            
            result = tab.check_directory_exists("test-bucket", "testdir")
            assert result is True
    
    def test_check_directory_exists_false(self, qapp):
        """Test directory existence check - directory does not exist"""
        tab = CloudTab()
        
        with patch.object(tab.s3_manager, 'list_bucket_contents') as mock_list:
            mock_list.return_value = [
                {'key': 'other/file1.html'},
                {'key': 'different/file2.css'}
            ]
            
            result = tab.check_directory_exists("test-bucket", "nonexistent")
            assert result is False


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