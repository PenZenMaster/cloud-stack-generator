"""
Unit tests for Google Cloud Storage Provider

Tests the GCS provider implementation including:
- Authentication methods
- Bucket operations
- File uploads
- Provider factory integration
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open
from tempfile import TemporaryDirectory
import json

from src.core.deployment.providers import (
    GCSProvider,
    ProviderType,
    ProviderConfig,
    DeploymentMode,
    DeploymentResult,
    AuthenticationError,
    BucketCreationError,
    UploadError,
    get_provider_factory,
    create_provider,
)


@pytest.mark.unit
class TestGCSProviderInitialization:
    """Test GCS provider initialization"""

    def test_provider_initialization(self):
        """Test basic provider initialization"""
        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={"project_id": "test-project"},
            region="us-central1"
        )

        provider = GCSProvider(config)

        assert provider.provider_type == ProviderType.GOOGLE_GCS
        assert provider.config == config
        assert not provider.is_authenticated()

    def test_provider_name(self):
        """Test provider name retrieval"""
        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={"project_id": "test-project"},
            region="us-central1"
        )

        provider = GCSProvider(config)
        assert provider.get_provider_name() == "Google Cloud Storage"


@pytest.mark.unit
class TestGCSAuthentication:
    """Test GCS authentication methods"""

    @patch('src.core.deployment.providers.gcs_provider.storage.Client')
    @patch('src.core.deployment.providers.gcs_provider.service_account.Credentials.from_service_account_file')
    def test_authenticate_with_json_file(self, mock_creds, mock_client):
        """Test authentication with service account JSON file"""
        # Mock credentials and client
        mock_creds.return_value = Mock()
        mock_client.return_value = Mock()

        # Mock the JSON file reading
        with patch('builtins.open', mock_open(read_data='{"project_id": "test-project"}')):
            with patch('pathlib.Path.exists', return_value=True):
                config = ProviderConfig(
                    provider_type=ProviderType.GOOGLE_GCS,
                    credentials={"service_account_json": "/path/to/key.json"},
                    region="us-central1"
                )

                provider = GCSProvider(config)
                result = provider.authenticate()

                assert result is True
                assert provider.is_authenticated()
                assert provider.project_id == "test-project"

    @patch('src.core.deployment.providers.gcs_provider.storage.Client')
    @patch('src.core.deployment.providers.gcs_provider.service_account.Credentials.from_service_account_info')
    def test_authenticate_with_key_components(self, mock_creds, mock_client):
        """Test authentication with service account key components"""
        mock_creds.return_value = Mock()
        mock_client.return_value = Mock()

        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={
                "project_id": "test-project",
                "private_key": "-----BEGIN PRIVATE KEY-----\ntest\n-----END PRIVATE KEY-----\n",
                "client_email": "test@test.iam.gserviceaccount.com"
            },
            region="us-central1"
        )

        provider = GCSProvider(config)
        result = provider.authenticate()

        assert result is True
        assert provider.is_authenticated()
        assert provider.project_id == "test-project"

    @patch('src.core.deployment.providers.gcs_provider.storage.Client')
    def test_authenticate_with_adc(self, mock_client):
        """Test authentication with Application Default Credentials"""
        mock_client_instance = Mock()
        mock_client_instance.project = "test-project"
        mock_client.return_value = mock_client_instance

        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={"use_adc": True},
            region="us-central1"
        )

        provider = GCSProvider(config)
        result = provider.authenticate()

        assert result is True
        assert provider.is_authenticated()
        assert provider.project_id == "test-project"

    def test_authenticate_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={},  # No valid credentials
            region="us-central1"
        )

        provider = GCSProvider(config)

        with pytest.raises(AuthenticationError):
            provider.authenticate()


@pytest.mark.unit
class TestGCSBucketOperations:
    """Test GCS bucket operations"""

    def setup_authenticated_provider(self):
        """Helper to create authenticated provider mock"""
        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={"project_id": "test-project"},
            region="us-central1"
        )

        provider = GCSProvider(config)
        provider._authenticated = True
        provider.project_id = "test-project"
        provider.client = Mock()

        return provider

    def test_create_bucket_success(self):
        """Test successful bucket creation"""
        provider = self.setup_authenticated_provider()

        # Mock bucket operations
        mock_bucket = Mock()
        provider.client.bucket.return_value = mock_bucket
        provider.client.create_bucket.return_value = mock_bucket

        # Mock NotFound exception for when bucket doesn't exist
        from google.cloud.exceptions import NotFound
        provider.client.get_bucket.side_effect = NotFound("Bucket not found")

        result = provider.create_bucket("test-bucket")

        assert result is True
        provider.client.create_bucket.assert_called_once()

    def test_create_bucket_already_exists(self):
        """Test creating bucket that already exists"""
        provider = self.setup_authenticated_provider()

        # Mock existing bucket
        mock_bucket = Mock()
        provider.client.get_bucket.return_value = mock_bucket

        result = provider.create_bucket("existing-bucket")

        assert result is True
        # Should not try to create if already exists
        provider.client.create_bucket.assert_not_called()

    def test_create_bucket_invalid_name(self):
        """Test bucket creation with invalid name"""
        provider = self.setup_authenticated_provider()

        with pytest.raises(BucketCreationError):
            provider.create_bucket("AB")  # Too short

    def test_configure_website_hosting(self):
        """Test website hosting configuration"""
        provider = self.setup_authenticated_provider()

        mock_bucket = Mock()
        mock_policy = Mock()
        mock_policy.bindings = []

        mock_bucket.get_iam_policy.return_value = mock_policy
        provider.client.get_bucket.return_value = mock_bucket

        result = provider.configure_website_hosting("test-bucket")

        assert result is True
        mock_bucket.configure_website.assert_called_once_with(
            main_page_suffix="index.html",
            not_found_page="404.html"
        )
        mock_bucket.set_iam_policy.assert_called_once()
        mock_bucket.patch.assert_called_once()

    def test_list_buckets(self):
        """Test listing buckets"""
        provider = self.setup_authenticated_provider()

        # Mock bucket list
        mock_bucket1 = Mock()
        mock_bucket1.name = "bucket-1"
        mock_bucket2 = Mock()
        mock_bucket2.name = "bucket-2"

        provider.client.list_buckets.return_value = [mock_bucket1, mock_bucket2]

        buckets = provider.list_buckets()

        assert len(buckets) == 2
        assert "bucket-1" in buckets
        assert "bucket-2" in buckets

    def test_delete_bucket(self):
        """Test bucket deletion"""
        provider = self.setup_authenticated_provider()

        mock_bucket = Mock()
        provider.client.get_bucket.return_value = mock_bucket

        result = provider.delete_bucket("test-bucket")

        assert result is True
        mock_bucket.delete.assert_called_once()

    def test_delete_bucket_with_force(self):
        """Test forced bucket deletion (with contents)"""
        provider = self.setup_authenticated_provider()

        mock_bucket = Mock()
        mock_blob1 = Mock()
        mock_blob2 = Mock()
        mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]

        provider.client.get_bucket.return_value = mock_bucket

        result = provider.delete_bucket("test-bucket", force=True)

        assert result is True
        mock_blob1.delete.assert_called_once()
        mock_blob2.delete.assert_called_once()
        mock_bucket.delete.assert_called_once()


@pytest.mark.unit
class TestGCSFileOperations:
    """Test GCS file upload operations"""

    def setup_authenticated_provider(self):
        """Helper to create authenticated provider mock"""
        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={"project_id": "test-project"},
            region="us-central1"
        )

        provider = GCSProvider(config)
        provider._authenticated = True
        provider.project_id = "test-project"
        provider.client = Mock()
        provider.config.extra_config["current_bucket"] = "test-bucket"

        return provider

    def test_upload_file_success(self):
        """Test successful file upload"""
        provider = self.setup_authenticated_provider()

        # Create temporary file
        with TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.html"
            test_file.write_text("<html></html>")

            mock_bucket = Mock()
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            provider.client.get_bucket.return_value = mock_bucket

            result = provider.upload_file(
                test_file,
                "path/to/test.html",
                "text/html",
                "public, max-age=3600"
            )

            assert result is True
            mock_blob.upload_from_filename.assert_called_once()
            assert mock_blob.content_type == "text/html"
            assert mock_blob.cache_control == "public, max-age=3600"

    def test_upload_file_not_found(self):
        """Test uploading non-existent file"""
        provider = self.setup_authenticated_provider()

        with pytest.raises(UploadError):
            provider.upload_file(
                Path("/nonexistent/file.txt"),
                "path/to/file.txt",
                "text/plain"
            )

    def test_upload_directory_success(self):
        """Test successful directory upload"""
        provider = self.setup_authenticated_provider()

        # Create temporary directory with files
        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Create test files
            (tmppath / "index.html").write_text("<html></html>")
            (tmppath / "style.css").write_text("body {}")
            (tmppath / "subdir").mkdir()
            (tmppath / "subdir" / "page.html").write_text("<html></html>")

            mock_bucket = Mock()
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            provider.client.get_bucket.return_value = mock_bucket

            # Mock upload_file to track calls
            upload_count = []

            def mock_upload(local_path, remote_path, content_type, cache_control=None, metadata=None):
                upload_count.append(str(local_path))
                return True

            provider.upload_file = mock_upload

            result = provider.upload_directory(
                tmppath,
                "test-bucket"
            )

            assert result.success is True
            assert result.files_uploaded == 3  # 3 files total
            assert result.provider == ProviderType.GOOGLE_GCS
            assert result.bucket_name == "test-bucket"

    def test_upload_directory_with_progress(self):
        """Test directory upload with progress callback"""
        provider = self.setup_authenticated_provider()

        # Track progress calls
        progress_calls = []

        def progress_callback(current, total, filename):
            progress_calls.append((current, total, filename))

        with TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            (tmppath / "file1.txt").write_text("test")
            (tmppath / "file2.txt").write_text("test")

            mock_bucket = Mock()
            mock_blob = Mock()
            mock_bucket.blob.return_value = mock_blob
            provider.client.get_bucket.return_value = mock_bucket

            provider.upload_file = Mock(return_value=True)

            result = provider.upload_directory(
                tmppath,
                "test-bucket",
                progress_callback=progress_callback
            )

            assert result.success is True
            assert len(progress_calls) == 2  # Called for each file


@pytest.mark.unit
class TestGCSHelperMethods:
    """Test GCS helper methods"""

    def setup_provider(self):
        """Helper to create provider"""
        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={"project_id": "test-project"},
            region="us-central1"
        )
        return GCSProvider(config)

    def test_get_content_type(self):
        """Test content type detection"""
        provider = self.setup_provider()

        assert provider.get_content_type(Path("index.html")) == "text/html"
        assert provider.get_content_type(Path("style.css")) == "text/css"
        assert provider.get_content_type(Path("script.js")) == "text/javascript"
        assert provider.get_content_type(Path("image.png")) == "image/png"
        assert provider.get_content_type(Path("unknown.xyz")) == "application/octet-stream"

    def test_get_cache_control(self):
        """Test cache control header generation"""
        provider = self.setup_provider()

        # Static assets get long cache
        assert "max-age=31536000" in provider.get_cache_control(Path("style.css"))
        assert "immutable" in provider.get_cache_control(Path("script.js"))
        assert "max-age=31536000" in provider.get_cache_control(Path("image.png"))

        # HTML gets short cache
        assert "max-age=3600" in provider.get_cache_control(Path("index.html"))
        assert "must-revalidate" in provider.get_cache_control(Path("page.html"))

        # Default cache
        assert "max-age=86400" in provider.get_cache_control(Path("data.json"))

    def test_validate_bucket_name(self):
        """Test bucket name validation"""
        provider = self.setup_provider()

        # Valid names
        valid, _ = provider.validate_bucket_name("my-bucket")
        assert valid is True

        valid, _ = provider.validate_bucket_name("my.bucket.123")
        assert valid is True

        # Invalid names
        valid, error = provider.validate_bucket_name("")
        assert valid is False
        assert "empty" in error.lower()

        valid, error = provider.validate_bucket_name("ab")
        assert valid is False
        assert "between 3 and 63" in error

        valid, error = provider.validate_bucket_name("MyBucket")
        assert valid is False
        assert "lowercase" in error

        valid, error = provider.validate_bucket_name("my..bucket")
        assert valid is False
        assert "consecutive dots" in error

        valid, error = provider.validate_bucket_name("192.168.1.1")
        assert valid is False
        assert "IP address" in error

    def test_get_website_url(self):
        """Test website URL generation"""
        provider = self.setup_provider()

        url = provider.get_website_url("my-bucket")

        assert url == "https://storage.googleapis.com/my-bucket/index.html"


@pytest.mark.unit
class TestProviderFactory:
    """Test provider factory"""

    def test_factory_initialization(self):
        """Test factory initialization and provider registration"""
        from src.core.deployment.providers import get_provider_factory

        factory = get_provider_factory()

        assert factory is not None
        assert ProviderType.GOOGLE_GCS in factory.get_available_providers()

    def test_create_gcs_provider(self):
        """Test creating GCS provider via factory"""
        from src.core.deployment.providers import create_provider

        config = ProviderConfig(
            provider_type=ProviderType.GOOGLE_GCS,
            credentials={"project_id": "test-project"},
            region="us-central1"
        )

        provider = create_provider(ProviderType.GOOGLE_GCS, config)

        assert isinstance(provider, GCSProvider)
        assert provider.provider_type == ProviderType.GOOGLE_GCS

    def test_create_provider_from_dict(self):
        """Test creating provider from dictionary config"""
        from src.core.deployment.providers import create_provider_from_dict

        config_dict = {
            "provider": "google_gcs",
            "credentials": {"project_id": "test-project"},
            "region": "us-central1",
            "deployment_mode": "storage_only"
        }

        provider = create_provider_from_dict(config_dict)

        assert isinstance(provider, GCSProvider)
        assert provider.config.region == "us-central1"

    def test_create_invalid_provider(self):
        """Test creating non-existent provider"""
        from src.core.deployment.providers import create_provider

        config = ProviderConfig(
            provider_type=ProviderType.AZURE_BLOB,  # Not implemented yet
            credentials={},
            region="us-east"
        )

        factory = get_provider_factory()

        with pytest.raises(ValueError, match="not registered"):
            factory.create_provider(ProviderType.AZURE_BLOB, config)
