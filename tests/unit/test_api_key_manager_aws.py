"""
Unit tests for enhanced API Key Manager AWS functionality
"""

import pytest
import json
import base64
from unittest.mock import patch, mock_open

from src.core.security.api_key_manager import APIKeyManager


@pytest.mark.unit
@pytest.mark.aws
class TestAPIKeyManagerAWS:
    """Test AWS-specific API key manager functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = APIKeyManager()
    
    @patch('builtins.open', new_callable=mock_open, read_data='')
    @patch('pathlib.Path.exists')
    def test_set_aws_credentials(self, mock_exists, mock_file):
        """Test storing AWS credentials"""
        mock_exists.return_value = False  # No existing file
        
        success = self.manager.set_aws_credentials(
            "test-profile",
            "AKIATEST123",
            "secretkey123",
            "sessiontoken456"
        )
        
        assert success is True
        
        # Verify the file was written with correct data
        mock_file.assert_called()
        written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        
        # Decode and verify the stored data structure
        import base64
        decoded_data = base64.b64decode(written_data.encode()).decode()
        stored_data = json.loads(decoded_data)
        
        assert 'aws_test-profile' in stored_data
        credentials = json.loads(stored_data['aws_test-profile'])
        assert credentials['access_key_id'] == 'AKIATEST123'
        assert credentials['secret_access_key'] == 'secretkey123'
        assert credentials['session_token'] == 'sessiontoken456'
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_get_aws_credentials_success(self, mock_exists, mock_file):
        """Test retrieving AWS credentials"""
        mock_exists.return_value = True
        
        # Mock stored credentials
        credentials_data = {
            'access_key_id': 'AKIATEST123',
            'secret_access_key': 'secretkey123',
            'session_token': 'sessiontoken456'
        }
        stored_data = {'aws_test-profile': json.dumps(credentials_data)}
        encoded_data = base64.b64encode(json.dumps(stored_data).encode()).decode()
        mock_file.return_value.read.return_value = encoded_data
        
        credentials = self.manager.get_aws_credentials("test-profile")
        
        assert credentials is not None
        assert credentials['access_key_id'] == 'AKIATEST123'
        assert credentials['secret_access_key'] == 'secretkey123'
        assert credentials['session_token'] == 'sessiontoken456'
    
    def test_get_aws_credentials_not_found(self):
        """Test retrieving non-existent AWS credentials"""
        credentials = self.manager.get_aws_credentials("nonexistent-profile")
        assert credentials is None
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_get_aws_credentials_invalid_json(self, mock_exists, mock_file):
        """Test retrieving AWS credentials with invalid JSON"""
        mock_exists.return_value = True
        
        # Mock stored data with invalid JSON for credentials
        stored_data = {'aws_test-profile': 'invalid-json'}
        encoded_data = base64.b64encode(json.dumps(stored_data).encode()).decode()
        mock_file.return_value.read.return_value = encoded_data
        
        credentials = self.manager.get_aws_credentials("test-profile")
        assert credentials is None
    
    @patch.object(APIKeyManager, 'remove_api_key')
    def test_remove_aws_credentials(self, mock_remove):
        """Test removing AWS credentials"""
        mock_remove.return_value = True
        
        success = self.manager.remove_aws_credentials("test-profile")
        
        assert success is True
        mock_remove.assert_called_once_with("aws_test-profile")
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('pathlib.Path.exists')
    def test_list_aws_profiles(self, mock_exists, mock_file):
        """Test listing AWS profiles"""
        mock_exists.return_value = True
        
        # Mock stored data with multiple AWS profiles
        stored_data = {
            'aws_profile1': '{"access_key_id": "key1"}',
            'aws_profile2': '{"access_key_id": "key2"}',
            'non_aws_key': 'some_value',
            'aws_profile3': '{"access_key_id": "key3"}'
        }
        encoded_data = base64.b64encode(json.dumps(stored_data).encode()).decode()
        mock_file.return_value.read.return_value = encoded_data
        
        profiles = self.manager.list_aws_profiles()
        
        assert len(profiles) == 3
        assert 'profile1' in profiles
        assert 'profile2' in profiles
        assert 'profile3' in profiles
        assert 'non_aws_key' not in profiles  # Should be filtered out
    
    def test_list_aws_profiles_empty(self):
        """Test listing AWS profiles when none exist"""
        with patch.object(self.manager, '_load_keys', return_value={}):
            profiles = self.manager.list_aws_profiles()
            assert profiles == []
    
    @patch.object(APIKeyManager, 'get_aws_credentials')
    def test_has_aws_credentials_true(self, mock_get):
        """Test checking for existing AWS credentials"""
        mock_get.return_value = {'access_key_id': 'test'}
        
        has_credentials = self.manager.has_aws_credentials("test-profile")
        assert has_credentials is True
    
    @patch.object(APIKeyManager, 'get_aws_credentials')
    def test_has_aws_credentials_false(self, mock_get):
        """Test checking for non-existing AWS credentials"""
        mock_get.return_value = None
        
        has_credentials = self.manager.has_aws_credentials("test-profile")
        assert has_credentials is False
    
    @patch('builtins.open', new_callable=mock_open, read_data='')
    @patch('pathlib.Path.exists')
    def test_set_aws_credentials_no_session_token(self, mock_exists, mock_file):
        """Test storing AWS credentials without session token"""
        mock_exists.return_value = False
        
        success = self.manager.set_aws_credentials(
            "test-profile",
            "AKIATEST123", 
            "secretkey123"
            # No session token
        )
        
        assert success is True
        
        # Verify session token is empty string
        written_data = ''.join(call.args[0] for call in mock_file().write.call_args_list)
        decoded_data = base64.b64decode(written_data.encode()).decode()
        stored_data = json.loads(decoded_data)
        
        credentials = json.loads(stored_data['aws_test-profile'])
        assert credentials['session_token'] == ""
    
    @patch('builtins.open', side_effect=Exception("File error"))
    @patch('pathlib.Path.exists')
    def test_set_aws_credentials_file_error(self, mock_exists, mock_open):
        """Test AWS credential storage with file error"""
        mock_exists.return_value = False
        
        success = self.manager.set_aws_credentials(
            "test-profile",
            "AKIATEST123",
            "secretkey123"
        )
        
        # Should handle file error gracefully
        assert success is False
    
    @patch('builtins.open', new_callable=mock_open, read_data='invalid-base64')
    @patch('pathlib.Path.exists') 
    def test_get_aws_credentials_decode_error(self, mock_exists, mock_file):
        """Test AWS credential retrieval with decode error"""
        mock_exists.return_value = True
        
        credentials = self.manager.get_aws_credentials("test-profile")
        assert credentials is None
    
    @patch('builtins.open', new_callable=mock_open, read_data='')
    @patch('pathlib.Path.exists')
    def test_get_aws_credentials_empty_file(self, mock_exists, mock_file):
        """Test AWS credential retrieval with empty file"""
        mock_exists.return_value = True
        
        credentials = self.manager.get_aws_credentials("test-profile")
        assert credentials is None