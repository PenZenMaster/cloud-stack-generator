"""
Unit tests for S3-compatible cloud providers (AWS S3, Wasabi, Backblaze B2).

Tests cover:
- Provider instantiation and configuration
- Endpoint URL configuration
- Authentication flow
- Bucket operations
- File upload operations
- Website hosting configuration
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, mock_open
from pathlib import Path
from botocore.exceptions import ClientError, NoCredentialsError

from src.core.deployment.providers import (
    ProviderType,
    ProviderConfig,
    DeploymentMode,
    AuthenticationError,
    BucketCreationError,
    UploadError,
)
from src.core.deployment.providers.s3_compatible_provider import S3CompatibleProvider
from src.core.deployment.providers.aws_s3_provider import AWSS3Provider
from src.core.deployment.providers.wasabi_provider import WasabiProvider, WASABI_ENDPOINTS
from src.core.deployment.providers.backblaze_b2_provider import (
    BackblazeB2Provider,
    BACKBLAZE_B2_ENDPOINTS,
)


# Test fixtures
@pytest.fixture
def aws_config():
    """AWS S3 provider configuration"""
    return ProviderConfig(
        provider_type=ProviderType.AWS_S3,
        credentials={
            "aws_access_key_id": "test-key-id",
            "aws_secret_access_key": "test-secret-key",
        },
        region="us-east-1",
        deployment_mode=DeploymentMode.STORAGE_ONLY,
    )


@pytest.fixture
def wasabi_config():
    """Wasabi provider configuration"""
    return ProviderConfig(
        provider_type=ProviderType.WASABI,
        credentials={
            "aws_access_key_id": "wasabi-key-id",
            "aws_secret_access_key": "wasabi-secret-key",
        },
        region="us-east-1",
        deployment_mode=DeploymentMode.STORAGE_ONLY,
    )


@pytest.fixture
def backblaze_config():
    """Backblaze B2 provider configuration"""
    return ProviderConfig(
        provider_type=ProviderType.BACKBLAZE_B2,
        credentials={
            "aws_access_key_id": "b2-key-id",
            "aws_secret_access_key": "b2-app-key",
        },
        region="us-west-001",
        deployment_mode=DeploymentMode.STORAGE_ONLY,
    )


@pytest.fixture
def mock_boto3_session():
    """Mock boto3 session"""
    with patch("src.core.deployment.providers.s3_compatible_provider.boto3.Session") as mock:
        session = MagicMock()
        mock.return_value = session

        # Mock S3 client
        s3_client = MagicMock()
        session.client.return_value = s3_client

        # Mock S3 resource
        s3_resource = MagicMock()
        session.resource.return_value = s3_resource

        yield mock, session, s3_client, s3_resource


# AWS S3 Provider Tests
class TestAWSS3Provider:
    """Tests for AWS S3 provider"""

    def test_provider_initialization(self, aws_config):
        """Test AWS S3 provider initialization"""
        provider = AWSS3Provider(aws_config)

        assert provider.provider_type == ProviderType.AWS_S3
        assert provider.config.region == "us-east-1"
        assert not provider.is_authenticated()

    def test_endpoint_url_is_none(self, aws_config):
        """Test that AWS S3 uses default endpoints (None)"""
        provider = AWSS3Provider(aws_config)

        endpoint = provider._get_endpoint_url()
        assert endpoint is None

    def test_get_website_url(self, aws_config):
        """Test AWS S3 website URL generation"""
        provider = AWSS3Provider(aws_config)

        # Test us-east-1
        url = provider.get_website_url("test-bucket")
        assert url == "http://test-bucket.s3-website-us-east-1.amazonaws.com"

        # Test other region
        provider.config.region = "us-west-2"
        url = provider.get_website_url("test-bucket")
        assert url == "http://test-bucket.s3-website.us-west-2.amazonaws.com"

    def test_configure_cdn_not_implemented(self, aws_config):
        """Test that CDN configuration returns not implemented"""
        provider = AWSS3Provider(aws_config)
        provider._authenticated = True

        success, cdn_url = provider.configure_cdn("test-bucket")
        assert not success
        assert cdn_url is None

    def test_provider_name(self, aws_config):
        """Test provider name"""
        provider = AWSS3Provider(aws_config)
        assert provider.get_provider_name() == "AWS S3"


# Wasabi Provider Tests
class TestWasabiProvider:
    """Tests for Wasabi provider"""

    def test_provider_initialization(self, wasabi_config):
        """Test Wasabi provider initialization"""
        provider = WasabiProvider(wasabi_config)

        assert provider.provider_type == ProviderType.WASABI
        assert provider.config.region == "us-east-1"
        assert not provider.is_authenticated()

    def test_endpoint_url_us_east_1(self, wasabi_config):
        """Test Wasabi endpoint URL for us-east-1"""
        provider = WasabiProvider(wasabi_config)

        endpoint = provider._get_endpoint_url()
        assert endpoint == WASABI_ENDPOINTS["us-east-1"]
        assert endpoint == "https://s3.wasabisys.com"

    def test_endpoint_url_other_regions(self):
        """Test Wasabi endpoint URLs for various regions"""
        regions_to_test = ["us-west-1", "eu-central-1", "ap-northeast-1"]

        for region in regions_to_test:
            config = ProviderConfig(
                provider_type=ProviderType.WASABI,
                credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"},
                region=region,
            )
            provider = WasabiProvider(config)

            endpoint = provider._get_endpoint_url()
            assert endpoint == WASABI_ENDPOINTS[region]
            assert "wasabisys.com" in endpoint

    def test_endpoint_url_unknown_region(self):
        """Test Wasabi defaults to us-east-1 for unknown region"""
        config = ProviderConfig(
            provider_type=ProviderType.WASABI,
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"},
            region="unknown-region",
        )
        provider = WasabiProvider(config)

        endpoint = provider._get_endpoint_url()
        assert endpoint == WASABI_ENDPOINTS["us-east-1"]

    def test_get_website_url(self, wasabi_config):
        """Test Wasabi website URL generation"""
        provider = WasabiProvider(wasabi_config)

        # Test us-east-1
        url = provider.get_website_url("test-bucket")
        assert url == "http://test-bucket.s3-website-us-east-1.wasabisys.com"

        # Test other region
        provider.config.region = "us-west-1"
        url = provider.get_website_url("test-bucket")
        assert url == "http://test-bucket.s3-website.us-west-1.wasabisys.com"

    def test_provider_name(self, wasabi_config):
        """Test provider name"""
        provider = WasabiProvider(wasabi_config)
        assert provider.get_provider_name() == "Wasabi Hot Cloud Storage"


# Backblaze B2 Provider Tests
class TestBackblazeB2Provider:
    """Tests for Backblaze B2 provider"""

    def test_provider_initialization(self, backblaze_config):
        """Test Backblaze B2 provider initialization"""
        provider = BackblazeB2Provider(backblaze_config)

        assert provider.provider_type == ProviderType.BACKBLAZE_B2
        assert provider.config.region == "us-west-001"
        assert not provider.is_authenticated()

    def test_endpoint_url_us_west_001(self, backblaze_config):
        """Test Backblaze B2 endpoint URL for us-west-001"""
        provider = BackblazeB2Provider(backblaze_config)

        endpoint = provider._get_endpoint_url()
        assert endpoint == BACKBLAZE_B2_ENDPOINTS["us-west-001"]
        assert endpoint == "https://s3.us-west-001.backblazeb2.com"

    def test_endpoint_url_other_regions(self):
        """Test Backblaze B2 endpoint URLs for various regions"""
        regions_to_test = ["us-west-002", "us-west-004", "eu-central-003"]

        for region in regions_to_test:
            config = ProviderConfig(
                provider_type=ProviderType.BACKBLAZE_B2,
                credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"},
                region=region,
            )
            provider = BackblazeB2Provider(config)

            endpoint = provider._get_endpoint_url()
            assert endpoint == BACKBLAZE_B2_ENDPOINTS[region]
            assert "backblazeb2.com" in endpoint

    def test_endpoint_url_unknown_region(self):
        """Test Backblaze B2 defaults to us-west-001 for unknown region"""
        config = ProviderConfig(
            provider_type=ProviderType.BACKBLAZE_B2,
            credentials={"aws_access_key_id": "key", "aws_secret_access_key": "secret"},
            region="unknown-region",
        )
        provider = BackblazeB2Provider(config)

        endpoint = provider._get_endpoint_url()
        assert endpoint == BACKBLAZE_B2_ENDPOINTS["us-west-001"]

    def test_get_website_url(self, backblaze_config):
        """Test Backblaze B2 website URL generation"""
        provider = BackblazeB2Provider(backblaze_config)

        url = provider.get_website_url("test-bucket")
        assert "us-west-001" in url
        assert "backblazeb2.com" in url
        assert "test-bucket" in url

    def test_provider_name(self, backblaze_config):
        """Test provider name"""
        provider = BackblazeB2Provider(backblaze_config)
        assert provider.get_provider_name() == "Backblaze B2"


# S3CompatibleProvider Base Class Tests
class TestS3CompatibleProviderAuthentication:
    """Tests for S3-compatible provider authentication"""

    def test_create_session_with_valid_credentials(self, aws_config, mock_boto3_session):
        """Test session creation with valid credentials"""
        mock_class, mock_session, _, _ = mock_boto3_session

        provider = AWSS3Provider(aws_config)
        session = provider._create_session()

        assert session is not None
        mock_class.assert_called_once()

    def test_create_session_missing_access_key(self, aws_config):
        """Test session creation fails with missing access key"""
        aws_config.credentials = {"aws_secret_access_key": "secret"}
        provider = AWSS3Provider(aws_config)

        with pytest.raises(AuthenticationError, match="Missing required credentials"):
            provider._create_session()

    def test_create_session_missing_secret_key(self, aws_config):
        """Test session creation fails with missing secret key"""
        aws_config.credentials = {"aws_access_key_id": "key"}
        provider = AWSS3Provider(aws_config)

        with pytest.raises(AuthenticationError, match="Missing required credentials"):
            provider._create_session()

    def test_authenticate_success(self, aws_config, mock_boto3_session):
        """Test successful authentication"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session
        mock_s3_client.list_buckets.return_value = {"Buckets": []}

        provider = AWSS3Provider(aws_config)
        result = provider.authenticate()

        assert result is True
        assert provider.is_authenticated()

    def test_authenticate_no_credentials_error(self, aws_config, mock_boto3_session):
        """Test authentication fails with no credentials"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session
        mock_s3_client.list_buckets.side_effect = NoCredentialsError()

        provider = AWSS3Provider(aws_config)

        with pytest.raises(AuthenticationError):
            provider.authenticate()

    def test_test_connection_success(self, aws_config, mock_boto3_session):
        """Test successful connection test"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session
        mock_s3_client.list_buckets.return_value = {"Buckets": []}

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session

        success, message = provider.test_connection()

        assert success is True
        assert "connection successful" in message.lower()

    def test_test_connection_no_session(self, aws_config):
        """Test connection test fails without session"""
        provider = AWSS3Provider(aws_config)

        success, message = provider.test_connection()

        assert success is False
        assert "not authenticated" in message.lower()


class TestS3CompatibleProviderBucketOperations:
    """Tests for S3-compatible provider bucket operations"""

    def test_create_bucket_success_us_east_1(self, aws_config, mock_boto3_session):
        """Test successful bucket creation in us-east-1"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        result = provider.create_bucket("test-bucket")

        assert result is True
        mock_s3_client.create_bucket.assert_called_once()

    def test_create_bucket_success_other_region(self, aws_config, mock_boto3_session):
        """Test successful bucket creation in non-us-east-1 region"""
        aws_config.region = "us-west-2"
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        result = provider.create_bucket("test-bucket")

        assert result is True
        mock_s3_client.create_bucket.assert_called_once()

    def test_create_bucket_invalid_name(self, aws_config, mock_boto3_session):
        """Test bucket creation fails with invalid name"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        with pytest.raises(BucketCreationError, match="lowercase"):
            provider.create_bucket("INVALID-BUCKET-NAME")

    def test_create_bucket_already_exists(self, aws_config, mock_boto3_session):
        """Test bucket creation when bucket already owned"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        error_response = {"Error": {"Code": "BucketAlreadyOwnedByYou"}}
        mock_s3_client.create_bucket.side_effect = ClientError(error_response, "CreateBucket")

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        result = provider.create_bucket("test-bucket")
        assert result is True

    def test_configure_website_hosting_success(self, aws_config, mock_boto3_session):
        """Test successful website hosting configuration"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        result = provider.configure_website_hosting("test-bucket")

        assert result is True
        mock_s3_client.put_public_access_block.assert_called_once()
        mock_s3_client.put_bucket_policy.assert_called_once()
        mock_s3_client.put_bucket_website.assert_called_once()

    def test_list_buckets_success(self, aws_config, mock_boto3_session):
        """Test successful bucket listing"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session
        mock_s3_client.list_buckets.return_value = {
            "Buckets": [
                {"Name": "bucket1"},
                {"Name": "bucket2"},
                {"Name": "bucket3"},
            ]
        }

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        buckets = provider.list_buckets()

        assert len(buckets) == 3
        assert "bucket1" in buckets
        assert "bucket2" in buckets
        assert "bucket3" in buckets

    def test_delete_bucket_success(self, aws_config, mock_boto3_session):
        """Test successful bucket deletion"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        result = provider.delete_bucket("test-bucket", force=False)

        assert result is True
        mock_s3_client.delete_bucket.assert_called_once_with(Bucket="test-bucket")

    def test_delete_bucket_with_force(self, aws_config, mock_boto3_session):
        """Test bucket deletion with force flag (deletes contents first)"""
        mock_class, mock_session, mock_s3_client, mock_s3_resource = mock_boto3_session

        # Mock bucket objects
        mock_bucket = MagicMock()
        mock_obj1 = MagicMock()
        mock_obj1.key = "file1.txt"
        mock_obj2 = MagicMock()
        mock_obj2.key = "file2.txt"
        mock_bucket.objects.all.return_value = [mock_obj1, mock_obj2]

        mock_s3_resource.Bucket.return_value = mock_bucket

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        result = provider.delete_bucket("test-bucket", force=True)

        assert result is True
        mock_s3_client.delete_objects.assert_called_once()
        mock_s3_client.delete_bucket.assert_called_once()


class TestS3CompatibleProviderFileOperations:
    """Tests for S3-compatible provider file operations"""

    def test_upload_file_success(self, aws_config, mock_boto3_session, tmp_path):
        """Test successful file upload"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True
        provider.config.extra_config["current_bucket"] = "test-bucket"

        result = provider.upload_file(
            test_file,
            "remote/path/test.txt",
            "text/plain",
            "max-age=300"
        )

        assert result is True
        mock_s3_client.upload_file.assert_called_once()

    def test_upload_file_not_found(self, aws_config, mock_boto3_session):
        """Test file upload fails when file doesn't exist"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True
        provider.config.extra_config["current_bucket"] = "test-bucket"

        with pytest.raises(UploadError, match="not found"):
            provider.upload_file(
                Path("/nonexistent/file.txt"),
                "remote/path/test.txt",
                "text/plain"
            )

    def test_upload_file_no_bucket(self, aws_config, mock_boto3_session, tmp_path):
        """Test file upload fails when no bucket specified"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        with pytest.raises(UploadError, match="No bucket specified"):
            provider.upload_file(test_file, "remote/path/test.txt", "text/plain")

    def test_upload_directory_success(self, aws_config, mock_boto3_session, tmp_path):
        """Test successful directory upload"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        # Create test directory structure
        (tmp_path / "subdir").mkdir()
        (tmp_path / "file1.html").write_text("<html>test1</html>")
        (tmp_path / "file2.css").write_text("body { }")
        (tmp_path / "subdir" / "file3.js").write_text("console.log('test');")

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        result = provider.upload_directory(tmp_path, "test-bucket")

        assert result.success is True
        assert result.files_uploaded == 3
        assert result.provider == ProviderType.AWS_S3
        assert result.bucket_name == "test-bucket"

    def test_upload_directory_with_prefix(self, aws_config, mock_boto3_session, tmp_path):
        """Test directory upload with prefix"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        (tmp_path / "file.txt").write_text("test")

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        result = provider.upload_directory(tmp_path, "test-bucket", prefix="mysite")

        assert result.success is True
        assert result.files_uploaded == 1

    def test_upload_directory_with_progress(self, aws_config, mock_boto3_session, tmp_path):
        """Test directory upload with progress callback"""
        mock_class, mock_session, mock_s3_client, _ = mock_boto3_session

        (tmp_path / "file1.txt").write_text("test1")
        (tmp_path / "file2.txt").write_text("test2")

        progress_calls = []

        def progress_callback(current, total, filename):
            progress_calls.append((current, total, filename))

        provider = AWSS3Provider(aws_config)
        provider.session = mock_session
        provider._authenticated = True

        result = provider.upload_directory(
            tmp_path,
            "test-bucket",
            progress_callback=progress_callback
        )

        assert result.success is True
        assert len(progress_calls) == 2

    def test_get_file_metadata(self, aws_config):
        """Test file metadata generation"""
        provider = AWSS3Provider(aws_config)

        # Test known file types
        html_meta = provider._get_file_metadata("html")
        assert html_meta["ContentType"] == "text/html"
        assert "max-age=300" in html_meta["CacheControl"]

        css_meta = provider._get_file_metadata("css")
        assert css_meta["ContentType"] == "text/css"
        assert "max-age=86400" in css_meta["CacheControl"]

        # Test unknown file type
        unknown_meta = provider._get_file_metadata("xyz")
        assert "octet-stream" in unknown_meta["ContentType"]


class TestS3CompatibleProviderHelpers:
    """Tests for S3-compatible provider helper methods"""

    def test_cache_settings(self, aws_config):
        """Test cache settings are properly configured"""
        provider = AWSS3Provider(aws_config)

        assert "html" in provider.cache_settings
        assert "css" in provider.cache_settings
        assert "js" in provider.cache_settings
        assert "png" in provider.cache_settings

    def test_require_authentication_when_authenticated(self, aws_config):
        """Test require_authentication doesn't raise when authenticated"""
        provider = AWSS3Provider(aws_config)
        provider._authenticated = True

        # Should not raise
        provider.require_authentication()

    def test_require_authentication_when_not_authenticated(self, aws_config):
        """Test require_authentication raises when not authenticated"""
        provider = AWSS3Provider(aws_config)
        provider._authenticated = False

        with pytest.raises(AuthenticationError, match="not authenticated"):
            provider.require_authentication()
