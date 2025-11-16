"""
Test AWS profile persistence across sessions

This test specifically targets the regression issue where AWS profiles
are not being saved/restored properly between application sessions.

Author: Cloud Stack Generator Team
Version: 1.00
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication

from src.ui.components.cloud_tab import CloudTab
from src.core.config.client_aws_config import ClientAWSConfig, ClientAWSConfigManager
from src.core.aws.credentials import AWSCredentialsManager, AWSProfile, AuthMethod


@pytest.fixture(scope='module')
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def temp_config_dir():
    """Create temporary directory for config files"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_credentials_manager():
    """Mock AWS credentials manager with test profiles"""
    manager = Mock(spec=AWSCredentialsManager)
    
    # Create test profile
    test_profile = AWSProfile(
        name="test-profile",
        region="us-east-1", 
        auth_method=AuthMethod.SSO,
        description="Test Profile"
    )
    
    manager.profiles = {"test-profile": test_profile}
    manager.export_profiles.return_value = {"test-profile": test_profile}
    manager.list_client_buckets.return_value = []
    
    return manager


@pytest.mark.integration
class TestAWSProfilePersistence:
    """Test AWS profile persistence across sessions"""
    
    def test_profile_creation_and_persistence(self, qapp, temp_config_dir, mock_credentials_manager):
        """Test complete profile creation and persistence workflow"""
        
        # Setup CloudTab with temporary config
        with patch('src.ui.components.cloud_tab.get_client_aws_manager') as mock_manager_getter:
            config_manager = ClientAWSConfigManager(temp_config_dir)
            mock_manager_getter.return_value = config_manager
            
            # Initialize CloudTab with NO profiles initially (simulating fresh install)
            mock_credentials_manager.profiles = {}
            mock_credentials_manager.export_profiles.return_value = {}
            
            tab = CloudTab()
            tab.credentials_manager = mock_credentials_manager
            
            # Step 1: Set client context (simulates loading a business config)
            business_name = "Test Business"
            domain = "https://test.com"
            tab.set_client_context(business_name, domain)
            
            # Verify client config was created
            assert tab.current_client_aws_config is not None
            assert tab.current_client_aws_config.business_name == business_name
            assert tab.current_client_aws_config.domain == domain
            assert tab.current_client_aws_config.aws_profile == ""  # Initially empty
            
            # Step 2: Add a profile to simulate user creating/selecting one
            test_profile = AWSProfile(
                name="test-profile",
                region="us-east-1",
                auth_method=AuthMethod.SSO,
                description="Test Profile"
            )
            mock_credentials_manager.profiles = {"test-profile": test_profile}
            mock_credentials_manager.export_profiles.return_value = {"test-profile": test_profile}
            
            # Step 3: Simulate profile selection (user selects existing profile)
            tab.profile_combo.addItem("test-profile")  # Add profile to combo
            tab.profile_combo.setCurrentText("test-profile")  # Select it
            
            # This should trigger on_profile_changed -> on_aws_config_changed -> save
            tab.on_profile_changed("test-profile")
            
            # Step 4: Verify profile is saved to client config
            saved_config = config_manager.load_client_aws_config(business_name, domain)
            assert saved_config is not None
            assert saved_config.aws_profile == "test-profile"
            
            # Step 5: Simulate config loading (what happens when YAML config is loaded)
            yaml_data = {
                'aws_profile': '',  # Empty in YAML (this is the problem case)
                'aws_region': 'us-west-1',
                'bucket_name': 'test-bucket',
                'deployment_mode': 's3'
            }
            
            tab.set_config_data(yaml_data)
            
            # Step 6: Verify profile selection is preserved (not overwritten by empty YAML)
            assert tab.profile_combo.currentText() == "test-profile"
            
            # Step 7: Verify client config still has correct profile
            final_config = config_manager.load_client_aws_config(business_name, domain)
            assert final_config.aws_profile == "test-profile"

    def test_profile_restoration_on_app_restart(self, qapp, temp_config_dir, mock_credentials_manager):
        """Test profile restoration when app restarts"""
        
        with patch('src.ui.components.cloud_tab.get_client_aws_manager') as mock_manager_getter:
            config_manager = ClientAWSConfigManager(temp_config_dir)
            mock_manager_getter.return_value = config_manager
            
            # Step 1: Create saved client config with profile
            business_name = "Test Business"
            domain = "https://test.com"
            
            saved_config = ClientAWSConfig(
                business_name=business_name,
                domain=domain,
                aws_profile="test-profile",
                bucket_name="test-bucket"
            )
            config_manager.save_client_aws_config(saved_config)
            
            # Step 2: Create new CloudTab instance (simulates app restart)
            tab = CloudTab()
            tab.credentials_manager = mock_credentials_manager
            
            # Step 3: Set client context (loads saved config)
            tab.set_client_context(business_name, domain)
            
            # Step 4: Verify profile was restored
            assert tab.current_client_aws_config.aws_profile == "test-profile"
            
            # Step 5: Simulate config data loading with empty YAML
            yaml_data = {
                'aws_profile': '',  # Empty YAML data
                'aws_region': 'us-west-1',
                'bucket_name': 'yaml-bucket',
                'deployment_mode': 's3'
            }
            
            tab.set_config_data(yaml_data)
            
            # Step 6: Verify client config profile takes precedence over YAML
            assert tab.current_client_aws_config.aws_profile == "test-profile"

    def test_no_overwrite_with_no_profiles_configured(self, qapp, temp_config_dir, mock_credentials_manager):
        """Test that existing saved profile is not overwritten by 'No profiles configured' state"""
        
        with patch('src.ui.components.cloud_tab.get_client_aws_manager') as mock_manager_getter:
            config_manager = ClientAWSConfigManager(temp_config_dir)
            mock_manager_getter.return_value = config_manager
            
            # Step 1: Create client config with saved profile
            business_name = "Test Business"
            domain = "https://test.com"
            
            saved_config = ClientAWSConfig(
                business_name=business_name,
                domain=domain,
                aws_profile="saved-profile",  # Previously saved profile
                bucket_name="client-bucket"
            )
            config_manager.save_client_aws_config(saved_config)
            
            # Step 2: Mock credentials manager with NO profiles (simulating scenario where SSO profiles need reconfiguration)
            mock_credentials_manager.profiles = {}
            mock_credentials_manager.export_profiles.return_value = {}
            
            # Step 3: Create CloudTab
            tab = CloudTab()
            tab.credentials_manager = mock_credentials_manager
            
            # Step 4: Set client context (loads saved config)
            tab.set_client_context(business_name, domain)
            assert tab.current_client_aws_config.aws_profile == "saved-profile"
            
            # Step 4: Simulate combo in "No profiles configured" state (timing issue)
            tab.profile_combo.clear()
            tab.profile_combo.addItem("No profiles configured")
            tab.profile_combo.setCurrentText("No profiles configured")
            
            # Step 5: Trigger auto-save (this should NOT overwrite existing profile)
            tab.on_aws_config_changed()
            
            # Step 6: Verify saved profile was NOT overwritten
            final_config = config_manager.load_client_aws_config(business_name, domain)
            assert final_config.aws_profile == "saved-profile"  # Should still be saved-profile


@pytest.mark.unit
class TestAWSConfigPriorityLogic:
    """Test the priority logic between client config and YAML data"""
    
    def test_client_config_priority_over_yaml(self):
        """Test that non-empty client config takes priority over YAML"""
        
        # Create sample data structures
        client_config = ClientAWSConfig(
            aws_profile="client-profile",
            bucket_name="client-bucket", 
            bucket_region="us-east-1"
        )
        
        yaml_data = {
            'aws_profile': 'yaml-profile',
            'bucket_name': 'yaml-bucket',
            'aws_region': 'us-west-2'
        }
        
        # Test priority logic (simplified version of actual method)
        # Client config takes priority when non-empty
        result_profile = client_config.aws_profile or yaml_data.get('aws_profile', '')
        result_bucket = client_config.bucket_name or yaml_data.get('bucket_name', '')
        result_region = client_config.bucket_region or yaml_data.get('aws_region', '')
        
        assert result_profile == "client-profile"
        assert result_bucket == "client-bucket"
        assert result_region == "us-east-1"
        
    def test_yaml_fallback_when_client_config_empty(self):
        """Test that YAML is used when client config is empty"""
        
        client_config = ClientAWSConfig(
            aws_profile="",  # Empty
            bucket_name="", 
            bucket_region=""
        )
        
        yaml_data = {
            'aws_profile': 'yaml-profile',
            'bucket_name': 'yaml-bucket',
            'aws_region': 'us-west-2'
        }
        
        # Test fallback logic
        result_profile = client_config.aws_profile or yaml_data.get('aws_profile', '')
        result_bucket = client_config.bucket_name or yaml_data.get('bucket_name', '')
        result_region = client_config.bucket_region or yaml_data.get('aws_region', '')
        
        assert result_profile == "yaml-profile"
        assert result_bucket == "yaml-bucket"  
        assert result_region == "us-west-2"