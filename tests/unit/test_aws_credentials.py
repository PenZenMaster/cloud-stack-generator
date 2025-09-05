"""
Unit tests for AWS credentials management system
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

from src.core.aws.credentials import (
    AWSCredentialsManager, AWSProfile, AuthMethod, 
    check_aws_cli, get_aws_config_profiles
)


@pytest.mark.unit
@pytest.mark.aws
class TestAWSProfile:
    """Test AWSProfile dataclass"""
    
    def test_sso_profile_creation(self):
        """Test SSO profile creation"""
        profile = AWSProfile(
            name="test-sso",
            auth_method=AuthMethod.SSO,
            sso_start_url="https://test.awsapps.com/start",
            sso_region="us-east-1",
            region="us-east-1"
        )
        
        assert profile.name == "test-sso"
        assert profile.auth_method == AuthMethod.SSO
        assert profile.sso_start_url == "https://test.awsapps.com/start"
        assert profile.region == "us-east-1"
    
    def test_access_keys_profile_creation(self):
        """Test Access Keys profile creation"""
        profile = AWSProfile(
            name="test-keys",
            auth_method=AuthMethod.ACCESS_KEYS,
            region="us-west-2"
        )
        
        assert profile.name == "test-keys"
        assert profile.auth_method == AuthMethod.ACCESS_KEYS
        assert profile.region == "us-west-2"
        assert profile.sso_start_url == ""
    
    def test_assume_role_profile_creation(self):
        """Test AssumeRole profile creation"""
        profile = AWSProfile(
            name="test-role",
            auth_method=AuthMethod.ASSUME_ROLE,
            source_profile="base-profile",
            role_arn="arn:aws:iam::123456789012:role/TestRole",
            region="eu-west-1"
        )
        
        assert profile.name == "test-role"
        assert profile.auth_method == AuthMethod.ASSUME_ROLE
        assert profile.source_profile == "base-profile"
        assert profile.role_arn == "arn:aws:iam::123456789012:role/TestRole"


@pytest.mark.unit
@pytest.mark.aws
class TestAWSCredentialsManager:
    """Test AWSCredentialsManager"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = AWSCredentialsManager()
    
    def test_manager_initialization(self):
        """Test manager initialization"""
        assert self.manager.profiles == {}
        assert self.manager.active_profile is None
        assert self.manager._session_cache == {}
    
    def test_add_sso_profile(self):
        """Test adding SSO profile"""
        profile = self.manager.add_sso_profile(
            name="test-sso",
            sso_start_url="https://test.awsapps.com/start",
            sso_region="us-east-1",
            region="us-east-1"
        )
        
        assert profile.name == "test-sso"
        assert profile.auth_method == AuthMethod.SSO
        assert "test-sso" in self.manager.profiles
        assert self.manager.profiles["test-sso"] == profile
    
    def test_add_access_key_profile(self):
        """Test adding Access Key profile"""
        profile = self.manager.add_access_key_profile(
            name="test-keys",
            region="us-west-2"
        )
        
        assert profile.name == "test-keys"
        assert profile.auth_method == AuthMethod.ACCESS_KEYS
        assert "test-keys" in self.manager.profiles
    
    def test_add_assume_role_profile(self):
        """Test adding AssumeRole profile"""
        # First add source profile
        source_profile = self.manager.add_sso_profile(
            name="source-profile",
            sso_start_url="https://test.awsapps.com/start"
        )
        
        role_profile = self.manager.add_assume_role_profile(
            name="test-role",
            source_profile="source-profile",
            role_arn="arn:aws:iam::123456789012:role/TestRole"
        )
        
        assert role_profile.name == "test-role"
        assert role_profile.auth_method == AuthMethod.ASSUME_ROLE
        assert role_profile.source_profile == "source-profile"
        assert "test-role" in self.manager.profiles
    
    @patch('boto3.Session')
    def test_validate_profile_success(self, mock_session):
        """Test successful profile validation"""
        # Setup mocks
        mock_sts = Mock()
        mock_sts.get_caller_identity.return_value = {
            'Account': '123456789012',
            'UserId': 'AIDTEST123',
            'Arn': 'arn:aws:iam::123456789012:user/test'
        }
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_sts
        mock_session.return_value = mock_session_instance
        
        # Add profile
        profile = self.manager.add_sso_profile(
            name="test-profile",
            sso_start_url="https://test.awsapps.com/start"
        )
        
        # Test validation
        is_valid, message, identity = self.manager.validate_profile("test-profile")
        
        assert is_valid is True
        assert "validated successfully" in message
        assert identity['account'] == '123456789012'
        assert profile.account_id == '123456789012'
    
    @patch('boto3.Session')
    def test_validate_profile_no_credentials(self, mock_session):
        """Test profile validation with no credentials"""
        from botocore.exceptions import NoCredentialsError
        
        mock_session_instance = Mock()
        mock_session_instance.client.side_effect = NoCredentialsError()
        mock_session.return_value = mock_session_instance
        
        # Add profile
        self.manager.add_sso_profile(
            name="test-profile",
            sso_start_url="https://test.awsapps.com/start"
        )
        
        # Test validation
        is_valid, message, identity = self.manager.validate_profile("test-profile")
        
        assert is_valid is False
        assert "No credentials configured" in message
        assert identity == {}
    
    def test_validate_nonexistent_profile(self):
        """Test validation of nonexistent profile"""
        is_valid, message, identity = self.manager.validate_profile("nonexistent")
        
        assert is_valid is False
        assert "not found" in message
        assert identity == {}
    
    @patch('boto3.Session')
    def test_test_s3_permissions_success(self, mock_session):
        """Test successful S3 permissions check"""
        mock_s3 = Mock()
        mock_s3.list_buckets.return_value = {'Buckets': []}
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        mock_session.return_value = mock_session_instance
        
        # Add profile
        self.manager.add_sso_profile(name="test-profile", sso_start_url="https://test.awsapps.com/start")
        
        # Test S3 permissions
        success, message = self.manager.test_s3_permissions("test-profile")
        
        assert success is True
        assert "validated successfully" in message
    
    @patch('boto3.Session')
    def test_list_client_buckets(self, mock_session):
        """Test listing client buckets with SOP naming"""
        mock_s3 = Mock()
        mock_s3.list_buckets.return_value = {
            'Buckets': [
                {'Name': 'client-website-test-123456', 'CreationDate': datetime.now()},
                {'Name': 'other-bucket', 'CreationDate': datetime.now()},
                {'Name': 'client-website-prod-789012', 'CreationDate': datetime.now()}
            ]
        }
        mock_s3.get_bucket_location.return_value = {'LocationConstraint': 'us-west-2'}
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        mock_session.return_value = mock_session_instance
        
        # Add profile
        self.manager.add_sso_profile(name="test-profile", sso_start_url="https://test.awsapps.com/start")
        
        # Test bucket listing
        buckets = self.manager.list_client_buckets("test-profile")
        
        assert len(buckets) == 2  # Only client-website-* buckets
        assert buckets[0]['name'] == 'client-website-test-123456'
        assert buckets[1]['name'] == 'client-website-prod-789012'
        assert buckets[0]['region'] == 'us-west-2'
    
    def test_set_active_profile_success(self):
        """Test setting active profile"""
        # Add and validate a profile
        profile = self.manager.add_sso_profile(
            name="test-profile",
            sso_start_url="https://test.awsapps.com/start"
        )
        
        with patch.object(self.manager, 'validate_profile', return_value=(True, "Valid", {})):
            success = self.manager.set_active_profile("test-profile")
            
            assert success is True
            assert self.manager.active_profile == "test-profile"
            assert profile.is_active is True
    
    def test_set_active_profile_invalid(self):
        """Test setting invalid active profile"""
        success = self.manager.set_active_profile("nonexistent")
        assert success is False
        assert self.manager.active_profile is None
    
    def test_export_profiles(self):
        """Test exporting profiles configuration"""
        # Add test profiles
        sso_profile = self.manager.add_sso_profile(
            name="sso-profile",
            sso_start_url="https://test.awsapps.com/start",
            region="us-east-1"
        )
        
        keys_profile = self.manager.add_access_key_profile(
            name="keys-profile",
            region="us-west-2"
        )
        
        # Export configuration
        export_data = self.manager.export_profiles()
        
        assert 'profiles' in export_data
        assert 'active_profile' in export_data
        assert len(export_data['profiles']) == 2
        
        # Check SSO profile export
        sso_data = export_data['profiles']['sso-profile']
        assert sso_data['auth_method'] == 'sso'
        assert sso_data['sso_start_url'] == 'https://test.awsapps.com/start'
        assert sso_data['region'] == 'us-east-1'
        
        # Check Access Keys profile export
        keys_data = export_data['profiles']['keys-profile']
        assert keys_data['auth_method'] == 'access_keys'
        assert keys_data['region'] == 'us-west-2'
    
    def test_import_profiles(self):
        """Test importing profiles configuration"""
        import_data = {
            'profiles': {
                'imported-sso': {
                    'name': 'imported-sso',
                    'auth_method': 'sso',
                    'region': 'us-east-1',
                    'sso_start_url': 'https://imported.awsapps.com/start',
                    'sso_region': 'us-east-1',
                    'description': 'Imported SSO profile'
                },
                'imported-keys': {
                    'name': 'imported-keys',
                    'auth_method': 'access_keys',
                    'region': 'us-west-2',
                    'sso_start_url': '',
                    'sso_region': '',
                    'description': 'Imported keys profile'
                }
            },
            'active_profile': 'imported-sso'
        }
        
        success = self.manager.import_profiles(import_data)
        
        assert success is True
        assert len(self.manager.profiles) == 2
        assert 'imported-sso' in self.manager.profiles
        assert 'imported-keys' in self.manager.profiles
        assert self.manager.active_profile == 'imported-sso'
        
        # Verify imported data
        sso_profile = self.manager.profiles['imported-sso']
        assert sso_profile.auth_method == AuthMethod.SSO
        assert sso_profile.sso_start_url == 'https://imported.awsapps.com/start'
        
        keys_profile = self.manager.profiles['imported-keys']
        assert keys_profile.auth_method == AuthMethod.ACCESS_KEYS
    
    def test_import_profiles_invalid_data(self):
        """Test importing profiles with invalid data"""
        invalid_data = {'profiles': {'bad-profile': {'incomplete': 'data'}}}
        
        success = self.manager.import_profiles(invalid_data)
        assert success is False
    
    def test_get_active_session_no_profile(self):
        """Test getting active session when no profile is active"""
        session = self.manager.get_active_session()
        assert session is None
    
    @patch('boto3.Session')
    def test_get_active_session_with_profile(self, mock_session):
        """Test getting active session with active profile"""
        # Add and activate profile
        self.manager.add_sso_profile("test-profile", "https://test.awsapps.com/start")
        
        with patch.object(self.manager, 'validate_profile', return_value=(True, "Valid", {})):
            self.manager.set_active_profile("test-profile")
            
            session = self.manager.get_active_session()
            assert session is not None


@pytest.mark.unit
class TestAWSUtilityFunctions:
    """Test AWS utility functions"""
    
    @patch('subprocess.run')
    def test_check_aws_cli_success(self, mock_run):
        """Test successful AWS CLI check"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "aws-cli/2.0.0 Python/3.8.0"
        mock_run.return_value = mock_result
        
        success, message = check_aws_cli()
        
        assert success is True
        assert "aws-cli/2.0.0" in message
    
    @patch('subprocess.run')
    def test_check_aws_cli_not_found(self, mock_run):
        """Test AWS CLI not found"""
        mock_run.side_effect = FileNotFoundError()
        
        success, message = check_aws_cli()
        
        assert success is False
        assert "not found" in message
    
    @patch('subprocess.run')  
    def test_check_aws_cli_timeout(self, mock_run):
        """Test AWS CLI timeout"""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired('aws', 10)
        
        success, message = check_aws_cli()
        
        assert success is False
        assert "timed out" in message
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open')
    def test_get_aws_config_profiles(self, mock_open, mock_exists):
        """Test getting AWS config profiles"""
        mock_exists.return_value = True
        mock_config = """[default]
region = us-east-1

[profile test-profile]
region = us-west-2
sso_start_url = https://test.awsapps.com/start

[profile prod-profile] 
region = eu-west-1
"""
        mock_open.return_value.__enter__.return_value = mock_config.splitlines()
        
        profiles = get_aws_config_profiles()
        
        assert len(profiles) == 2  # default is handled separately
        assert 'test-profile' in profiles
        assert 'prod-profile' in profiles
    
    @patch('pathlib.Path.exists')
    def test_get_aws_config_profiles_no_file(self, mock_exists):
        """Test getting profiles when config file doesn't exist"""
        mock_exists.return_value = False
        
        profiles = get_aws_config_profiles()
        
        assert profiles == []