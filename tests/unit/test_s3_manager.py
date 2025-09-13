"""
Unit tests for S3Manager functionality
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path
from datetime import datetime

from src.core.aws.s3_manager import (
    S3Manager, UploadProgress, UploadResult
)


@pytest.mark.unit
@pytest.mark.aws
class TestUploadProgress:
    """Test UploadProgress dataclass"""
    
    def test_upload_progress_creation(self):
        """Test UploadProgress creation"""
        progress = UploadProgress(
            total_files=10,
            uploaded_files=5,
            current_file="test.html",
            bytes_uploaded=1024,
            total_bytes=2048
        )
        
        assert progress.total_files == 10
        assert progress.uploaded_files == 5
        assert progress.current_file == "test.html"
        assert progress.bytes_uploaded == 1024
        assert progress.total_bytes == 2048
        assert progress.failed_files == 0


@pytest.mark.unit
@pytest.mark.aws
class TestUploadResult:
    """Test UploadResult dataclass"""
    
    def test_upload_result_success(self):
        """Test successful UploadResult"""
        result = UploadResult(
            success=True,
            message="Upload completed",
            uploaded_files=["index.html", "style.css"],
            website_url="http://bucket.s3-website-us-east-1.amazonaws.com"
        )
        
        assert result.success is True
        assert result.message == "Upload completed"
        assert len(result.uploaded_files) == 2
        assert result.website_url == "http://bucket.s3-website-us-east-1.amazonaws.com"
        assert len(result.failed_files) == 0
    
    def test_upload_result_failure(self):
        """Test failed UploadResult"""
        result = UploadResult(
            success=False,
            message="Upload failed",
            failed_files=["broken.html"]
        )
        
        assert result.success is False
        assert result.message == "Upload failed"
        assert len(result.failed_files) == 1
        assert len(result.uploaded_files) == 0


@pytest.mark.unit
@pytest.mark.aws
class TestS3Manager:
    """Test S3Manager functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.manager = S3Manager()
    
    def test_manager_initialization(self):
        """Test S3Manager initialization"""
        assert self.manager.session is not None
        assert self.manager.s3_client is None
        assert self.manager.s3_resource is None
        assert self.manager._progress_callback is None
    
    def test_cache_settings_configuration(self):
        """Test SOP-compliant cache settings"""
        # HTML files - short cache
        html_settings = self.manager.cache_settings['html']
        assert html_settings['CacheControl'] == 'max-age=300,public'
        assert html_settings['ContentType'] == 'text/html'
        
        # JSON files - long cache  
        json_settings = self.manager.cache_settings['json']
        assert json_settings['CacheControl'] == 'max-age=86400,public'
        assert json_settings['ContentType'] == 'application/json'
        
        # CSS files - long cache
        css_settings = self.manager.cache_settings['css']
        assert css_settings['CacheControl'] == 'max-age=86400,public'
        assert css_settings['ContentType'] == 'text/css'
    
    def test_set_session(self):
        """Test setting boto3 session"""
        import boto3
        new_session = boto3.Session(region_name='us-west-2')
        
        self.manager.set_session(new_session)
        
        assert self.manager.session == new_session
        assert self.manager.s3_client is None  # Should be reset
        assert self.manager.s3_resource is None  # Should be reset
    
    def test_set_progress_callback(self):
        """Test setting progress callback"""
        def mock_callback(progress):
            pass
        
        self.manager.set_progress_callback(mock_callback)
        assert self.manager._progress_callback == mock_callback
    
    @patch('boto3.Session')
    def test_test_connection_success(self, mock_session):
        """Test successful S3 connection"""
        mock_s3 = Mock()
        mock_s3.list_buckets.return_value = {'Buckets': []}
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        self.manager.session = mock_session_instance
        
        success, message = self.manager.test_connection()
        
        assert success is True
        assert "successful" in message
    
    @patch('boto3.Session')
    def test_test_connection_no_credentials(self, mock_session):
        """Test connection with no credentials"""
        from botocore.exceptions import NoCredentialsError
        
        mock_session_instance = Mock()
        mock_session_instance.client.side_effect = NoCredentialsError()
        self.manager.session = mock_session_instance
        
        success, message = self.manager.test_connection()
        
        assert success is False
        assert "No AWS credentials" in message
    
    @patch('boto3.Session')
    def test_create_bucket_us_east_1(self, mock_session):
        """Test bucket creation in us-east-1 (no LocationConstraint)"""
        mock_s3 = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        self.manager.session = mock_session_instance
        
        success, message = self.manager.create_bucket("client-website-test-123456", "us-east-1")
        
        assert success is True
        assert "created successfully" in message
        # Verify us-east-1 specific call (no LocationConstraint)
        mock_s3.create_bucket.assert_called_once_with(Bucket="client-website-test-123456")
    
    @patch('boto3.Session')
    def test_create_bucket_other_region(self, mock_session):
        """Test bucket creation in non us-east-1 region"""
        mock_s3 = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        self.manager.session = mock_session_instance
        
        success, message = self.manager.create_bucket("client-website-test-789012", "us-west-2")
        
        assert success is True
        # Verify other region call (with LocationConstraint)
        mock_s3.create_bucket.assert_called_once_with(
            Bucket="client-website-test-789012",
            CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
        )
    
    @patch('boto3.Session')
    def test_create_bucket_already_exists(self, mock_session):
        """Test bucket creation when bucket already exists"""
        from botocore.exceptions import ClientError
        
        mock_s3 = Mock()
        error_response = {'Error': {'Code': 'BucketAlreadyOwnedByYou'}}
        mock_s3.create_bucket.side_effect = ClientError(error_response, 'CreateBucket')
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        self.manager.session = mock_session_instance
        
        success, message = self.manager.create_bucket("existing-bucket", "us-east-1")
        
        assert success is True
        assert "already exists and is owned by you" in message
    
    @patch('boto3.Session')
    def test_configure_public_website_success(self, mock_session):
        """Test successful public website configuration"""
        mock_s3 = Mock()
        mock_s3.get_bucket_location.return_value = {'LocationConstraint': 'us-west-2'}
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        self.manager.session = mock_session_instance
        
        success, message = self.manager.configure_public_website("test-bucket")
        
        assert success is True
        assert "http://test-bucket.s3-website.us-west-2.amazonaws.com" in message
        
        # Verify all configuration calls were made
        mock_s3.put_public_access_block.assert_called_once()
        mock_s3.put_bucket_policy.assert_called_once()
        mock_s3.put_bucket_website.assert_called_once()
    
    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    @patch('boto3.Session')
    def test_upload_directory_success(self, mock_session, mock_is_dir, mock_exists, mock_rglob):
        """Test successful directory upload"""
        # Setup path mocks
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        
        # Create mock files
        mock_html_file = Mock()
        mock_html_file.is_file.return_value = True
        mock_html_file.name = "index.html"
        mock_html_file.suffix = ".html"
        mock_html_file.relative_to.return_value = Path("index.html")
        mock_html_file.stat.return_value.st_size = 1024
        
        mock_css_file = Mock()
        mock_css_file.is_file.return_value = True
        mock_css_file.name = "style.css"
        mock_css_file.suffix = ".css"
        mock_css_file.relative_to.return_value = Path("style.css")
        mock_css_file.stat.return_value.st_size = 512
        
        mock_rglob.return_value = [mock_html_file, mock_css_file]
        
        # Setup S3 mock
        mock_s3 = Mock()
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        self.manager.session = mock_session_instance
        
        # Setup progress callback
        progress_updates = []
        def progress_callback(progress):
            progress_updates.append(progress)
        self.manager.set_progress_callback(progress_callback)
        
        # Test upload
        result = self.manager.upload_directory("/test/path", "test-bucket")
        
        assert result.success is True
        assert len(result.uploaded_files) == 2
        assert "index.html" in result.uploaded_files
        assert "style.css" in result.uploaded_files
        assert len(result.failed_files) == 0
        
        # Verify S3 upload calls
        assert mock_s3.upload_file.call_count == 2
        
        # Verify progress updates
        assert len(progress_updates) >= 2
    
    def test_upload_directory_not_found(self):
        """Test upload when directory doesn't exist"""
        with patch('pathlib.Path.exists', return_value=False):
            result = self.manager.upload_directory("/nonexistent", "test-bucket")
            
            assert result.success is False
            assert "not found" in result.message
    
    @patch('pathlib.Path.rglob')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.is_dir')
    def test_upload_directory_no_files(self, mock_is_dir, mock_exists, mock_rglob):
        """Test upload when no files found"""
        mock_exists.return_value = True
        mock_is_dir.return_value = True
        mock_rglob.return_value = []
        
        result = self.manager.upload_directory("/empty/path", "test-bucket")
        
        assert result.success is False
        assert "No files found" in result.message
    
    @patch('boto3.Session')
    def test_get_website_url(self, mock_session):
        """Test getting website URL"""
        mock_s3 = Mock()
        mock_s3.get_bucket_location.return_value = {'LocationConstraint': 'us-west-2'}
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        self.manager.session = mock_session_instance
        
        url = self.manager.get_website_url("test-bucket")
        
        assert url == "http://test-bucket.s3-website.us-west-2.amazonaws.com"
    
    @patch('boto3.Session')
    def test_get_website_url_us_east_1(self, mock_session):
        """Test getting website URL for us-east-1 (null LocationConstraint)"""
        mock_s3 = Mock()
        mock_s3.get_bucket_location.return_value = {'LocationConstraint': None}
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        self.manager.session = mock_session_instance
        
        url = self.manager.get_website_url("test-bucket")
        
        assert url == "http://test-bucket.s3-website-us-east-1.amazonaws.com"
    
    @patch('boto3.Session')
    def test_list_bucket_contents(self, mock_session):
        """Test listing bucket contents"""
        mock_s3 = Mock()
        mock_s3.list_objects_v2.return_value = {
            'Contents': [
                {
                    'Key': 'index.html',
                    'Size': 1024,
                    'LastModified': datetime.now(),
                    'ETag': '"abc123"'
                },
                {
                    'Key': 'style.css',
                    'Size': 512,
                    'LastModified': datetime.now(),
                    'ETag': '"def456"'
                }
            ]
        }
        
        mock_session_instance = Mock()
        mock_session_instance.client.return_value = mock_s3
        self.manager.session = mock_session_instance
        
        contents = self.manager.list_bucket_contents("test-bucket")
        
        assert len(contents) == 2
        assert contents[0]['key'] == 'index.html'
        assert contents[0]['size'] == 1024
        assert contents[1]['key'] == 'style.css'
    
    @patch('boto3.Session')
    def test_delete_bucket_contents(self, mock_session):
        """Test deleting bucket contents"""
        # Mock S3 resource
        mock_obj1 = Mock()
        mock_obj1.key = 'file1.html'
        mock_obj2 = Mock()
        mock_obj2.key = 'file2.css'
        
        mock_bucket = Mock()
        mock_bucket.objects.filter.return_value = [mock_obj1, mock_obj2]
        
        mock_s3_resource = Mock()
        mock_s3_resource.Bucket.return_value = mock_bucket
        
        # Mock S3 client
        mock_s3_client = Mock()
        
        mock_session_instance = Mock()
        mock_session_instance.resource.return_value = mock_s3_resource
        mock_session_instance.client.return_value = mock_s3_client
        self.manager.session = mock_session_instance
        
        success, message = self.manager.delete_bucket_contents("test-bucket")
        
        assert success is True
        assert "Deleted 2 objects" in message
        mock_s3_client.delete_objects.assert_called_once()
    
    def test_get_file_metadata_html(self):
        """Test getting file metadata for HTML files"""
        metadata = self.manager._get_file_metadata("html")
        
        assert metadata['CacheControl'] == 'max-age=300,public'
        assert metadata['ContentType'] == 'text/html'
    
    def test_get_file_metadata_css(self):
        """Test getting file metadata for CSS files"""
        metadata = self.manager._get_file_metadata("css")
        
        assert metadata['CacheControl'] == 'max-age=86400,public'
        assert metadata['ContentType'] == 'text/css'
    
    def test_get_file_metadata_unknown(self):
        """Test getting file metadata for unknown file types"""
        metadata = self.manager._get_file_metadata("unknown")
        
        assert metadata['CacheControl'] == 'max-age=86400,public'
        assert metadata['ContentType'] == 'application/octet-stream'
    
    def test_matches_pattern(self):
        """Test file pattern matching for excludes"""
        assert self.manager._matches_pattern("test.tmp", "*.tmp") is True
        assert self.manager._matches_pattern("file.html", "*.tmp") is False
        assert self.manager._matches_pattern(".DS_Store", ".DS_Store") is True
        assert self.manager._matches_pattern("normal.txt", ".DS_Store") is False
    
    def test_validate_bucket_name_valid(self):
        """Test valid bucket name validation"""
        is_valid, message = self.manager.validate_bucket_name("client-website-test-123456")
        
        assert is_valid is True
        assert "valid" in message
    
    def test_validate_bucket_name_invalid_length(self):
        """Test bucket name validation - invalid length"""
        is_valid, message = self.manager.validate_bucket_name("ab")  # Too short
        
        assert is_valid is False
        assert "between 3 and 63 characters" in message
    
    def test_validate_bucket_name_invalid_characters(self):
        """Test bucket name validation - invalid characters"""
        is_valid, message = self.manager.validate_bucket_name("INVALID-BUCKET-NAME")  # Uppercase
        
        assert is_valid is False
        assert "lowercase letter or number" in message
    
    def test_validate_bucket_name_consecutive_periods(self):
        """Test bucket name validation - consecutive periods"""
        is_valid, message = self.manager.validate_bucket_name("client..website")
        
        assert is_valid is False
        assert "consecutive periods" in message
    
    def test_validate_bucket_name_with_periods(self):
        """Test bucket name validation - periods are allowed but not consecutive periods"""
        # Single periods are allowed in S3 bucket names
        is_valid, message = self.manager.validate_bucket_name("invalid.bucket.name")
        assert is_valid is True
        
        # But consecutive periods are not allowed
        is_valid, message = self.manager.validate_bucket_name("invalid..bucket..name")
        assert is_valid is False
        assert "consecutive periods" in message