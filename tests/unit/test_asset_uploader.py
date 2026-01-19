"""
Unit tests for Asset Uploader
Path: E:/projects/cloud-stack-generator/tests/unit/test_asset_uploader.py

Description:
Tests for the asset uploader module to ensure proper S3Manager initialization
and cloud upload functionality.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-01-18

Last Modified Date:
2026-01-18

Version: 1.00

Comments:
* v1.00 - Initial tests for AssetUploader fixes (Issue #23, #24)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.deployment.asset_uploader import AssetUploader, UploadResult


class TestAssetUploader:
    """Tests for AssetUploader"""

    def test_initialization_aws_s3(self):
        """Test initialization with AWS S3 provider"""
        provider_type = 'aws_s3'
        credentials = {'profile_name': 'default'}

        uploader = AssetUploader(provider_type, credentials)

        assert uploader.provider_type == 'aws_s3'
        assert uploader.credentials == credentials
        assert uploader._client is None

    def test_initialization_google_gcs(self):
        """Test initialization with Google GCS provider"""
        provider_type = 'google_gcs'
        credentials = {
            'project_id': 'test-project',
            'service_account_json': '/path/to/key.json'
        }

        uploader = AssetUploader(provider_type, credentials)

        assert uploader.provider_type == 'google_gcs'
        assert uploader.credentials == credentials

    @patch('boto3.Session')
    @patch('core.deployment.asset_uploader.S3Manager')
    def test_get_client_aws_creates_session_correctly(self, mock_s3_manager, mock_boto3_session):
        """Test that _get_client creates boto3.Session before passing to S3Manager (Issue #24)"""
        # Setup
        provider_type = 'aws_s3'
        credentials = {'profile_name': 'test-profile'}
        uploader = AssetUploader(provider_type, credentials)

        mock_session = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_s3_instance = MagicMock()
        mock_s3_manager.return_value = mock_s3_instance

        # Execute
        client = uploader._get_client()

        # Verify boto3.Session was created with profile_name
        mock_boto3_session.assert_called_once_with(profile_name='test-profile')

        # Verify S3Manager was initialized with session (NOT profile_name)
        mock_s3_manager.assert_called_once_with(session=mock_session)

        # Verify returned client is S3Manager instance
        assert client == mock_s3_instance

    @patch('boto3.Session')
    @patch('core.deployment.asset_uploader.S3Manager')
    def test_get_client_aws_no_profile_uses_default_session(self, mock_s3_manager, mock_boto3_session):
        """Test that _get_client creates default session when no profile specified"""
        # Setup
        provider_type = 'aws_s3'
        credentials = {}  # No profile_name
        uploader = AssetUploader(provider_type, credentials)

        mock_session = MagicMock()
        mock_boto3_session.return_value = mock_session

        # Execute
        uploader._get_client()

        # Verify boto3.Session was created without profile_name (default session)
        mock_boto3_session.assert_called_once_with()

    @patch('boto3.Session')
    @patch('core.deployment.asset_uploader.S3Manager')
    def test_get_client_caches_client(self, mock_s3_manager, mock_boto3_session):
        """Test that _get_client caches the client after first call"""
        provider_type = 'aws_s3'
        credentials = {'profile_name': 'test-profile'}
        uploader = AssetUploader(provider_type, credentials)

        mock_session = MagicMock()
        mock_boto3_session.return_value = mock_session
        mock_s3_instance = MagicMock()
        mock_s3_manager.return_value = mock_s3_instance

        # First call
        client1 = uploader._get_client()
        # Second call
        client2 = uploader._get_client()

        # Verify Session/S3Manager created only once
        assert mock_boto3_session.call_count == 1
        assert mock_s3_manager.call_count == 1

        # Verify same client returned
        assert client1 == client2

    @patch('core.deployment.asset_uploader.GCSProvider')
    def test_get_client_google_gcs(self, mock_gcs_provider):
        """Test _get_client for Google GCS"""
        provider_type = 'google_gcs'
        credentials = {
            'project_id': 'test-project',
            'service_account_json': '/path/to/key.json'
        }
        uploader = AssetUploader(provider_type, credentials)

        mock_gcs_instance = MagicMock()
        mock_gcs_provider.return_value = mock_gcs_instance

        # Execute
        client = uploader._get_client()

        # Verify GCSProvider initialized correctly
        mock_gcs_provider.assert_called_once_with(
            project_id='test-project',
            service_account_json='/path/to/key.json'
        )
        assert client == mock_gcs_instance

    def test_get_client_unsupported_provider(self):
        """Test _get_client raises error for unsupported provider"""
        provider_type = 'unsupported_provider'
        credentials = {}
        uploader = AssetUploader(provider_type, credentials)

        with pytest.raises(ValueError) as exc_info:
            uploader._get_client()

        assert "Unsupported provider" in str(exc_info.value)

    def test_validate_file_exists(self, tmp_path):
        """Test validate_file with existing file"""
        # Create test file
        test_file = tmp_path / "test.pdf"
        test_file.write_text("test content")

        uploader = AssetUploader('aws_s3', {})
        is_valid, error_msg = uploader.validate_file(test_file)

        assert is_valid
        assert error_msg == ""

    def test_validate_file_not_exists(self, tmp_path):
        """Test validate_file with non-existent file"""
        test_file = tmp_path / "nonexistent.pdf"

        uploader = AssetUploader('aws_s3', {})
        is_valid, error_msg = uploader.validate_file(test_file)

        assert not is_valid
        assert "File not found" in error_msg

    def test_validate_file_too_large(self, tmp_path):
        """Test validate_file with file exceeding size limit"""
        # Create large file (101 MB worth of data)
        test_file = tmp_path / "large.pdf"
        test_file.write_bytes(b'0' * (101 * 1024 * 1024))

        uploader = AssetUploader('aws_s3', {})
        is_valid, error_msg = uploader.validate_file(test_file, max_size_mb=100)

        assert not is_valid
        assert "File too large" in error_msg

    def test_validate_file_unsupported_extension_warns(self, tmp_path):
        """Test validate_file logs warning for unsupported extension but doesn't reject"""
        test_file = tmp_path / "test.unknown"
        test_file.write_text("test")

        uploader = AssetUploader('aws_s3', {})

        with patch('core.deployment.asset_uploader.logger') as mock_logger:
            is_valid, error_msg = uploader.validate_file(test_file)

            # Should still be valid (just warns)
            assert is_valid
            assert error_msg == ""

            # Should log warning
            mock_logger.warning.assert_called_once()

    def test_format_file_size(self):
        """Test format_file_size utility"""
        assert AssetUploader.format_file_size(100) == "100.0 B"
        assert AssetUploader.format_file_size(1024) == "1.0 KB"
        assert AssetUploader.format_file_size(1024 * 1024) == "1.0 MB"
        assert AssetUploader.format_file_size(1024 * 1024 * 1024) == "1.0 GB"

    @patch('boto3.Session')
    @patch('core.deployment.asset_uploader.S3Manager')
    def test_get_client_uses_provided_session(self, mock_s3_manager, mock_boto3_session):
        """REGRESSION: Test that provided session is used instead of creating new one (Issue #24)"""
        # Setup - pass pre-authenticated session in credentials
        mock_session = MagicMock()
        credentials = {'session': mock_session, 'profile_name': 'test-profile'}
        uploader = AssetUploader('aws_s3', credentials)

        mock_s3_instance = MagicMock()
        mock_s3_manager.return_value = mock_s3_instance

        # Execute
        client = uploader._get_client()

        # Verify: Should NOT create new boto3.Session when session is provided
        mock_boto3_session.assert_not_called()

        # Verify: S3Manager initialized with provided session
        mock_s3_manager.assert_called_once_with(session=mock_session)
        assert client == mock_s3_instance

    def test_image_extensions_supported(self):
        """REGRESSION: Test that image file extensions are supported (QA Bug Fix)"""
        # Image extensions that were missing and caused warnings
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']

        for ext in image_extensions:
            assert ext in AssetUploader.SUPPORTED_EXTENSIONS, \
                f"Image extension {ext} should be in SUPPORTED_EXTENSIONS"

    @patch('boto3.Session')
    @patch('core.deployment.asset_uploader.S3Manager')
    def test_upload_file_uses_session_client(self, mock_s3_manager, mock_boto3_session):
        """REGRESSION: Test that upload_file uses S3Manager methods (same as website deploy)"""
        # Setup
        mock_session = MagicMock()
        mock_s3_client = MagicMock()

        mock_s3_instance = MagicMock()
        mock_s3_instance.session = mock_session
        mock_s3_instance._get_s3_client.return_value = mock_s3_client
        mock_s3_instance._get_file_metadata.return_value = {'ContentType': 'image/jpeg'}
        mock_s3_manager.return_value = mock_s3_instance

        credentials = {'session': mock_session}
        uploader = AssetUploader('aws_s3', credentials)

        # Create test file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.jpg', delete=False) as tf:
            tf.write('test image content')
            test_file = Path(tf.name)

        try:
            # Execute upload
            result = uploader.upload_file(
                test_file,
                bucket='test-bucket',
                remote_path='assets/test.jpg',
                region='us-east-1'
            )

            # Verify: S3Manager's _get_s3_client was called (uses authenticated session)
            mock_s3_instance._get_s3_client.assert_called_once()

            # Verify: S3Manager's _get_file_metadata was called
            mock_s3_instance._get_file_metadata.assert_called_with('jpg')

            # Verify: upload_file was called on S3Manager's client
            mock_s3_client.upload_file.assert_called_once()
            call_args = mock_s3_client.upload_file.call_args

            # Verify correct parameters
            assert str(test_file) in str(call_args[0][0])
            assert call_args[0][1] == 'test-bucket'
            assert call_args[0][2] == 'assets/test.jpg'

        finally:
            # Cleanup
            test_file.unlink(missing_ok=True)

    @patch('boto3.Session')
    @patch('core.deployment.asset_uploader.S3Manager')
    def test_upload_file_no_acl_set(self, mock_s3_manager, mock_boto3_session):
        """REGRESSION: Test that upload uses S3Manager metadata (no ACL, proper caching)"""
        # Setup
        mock_session = MagicMock()
        mock_s3_client = MagicMock()

        # S3Manager returns metadata WITHOUT ACL (same as website deployment)
        mock_metadata = {'ContentType': 'application/pdf', 'CacheControl': 'max-age=86400,public'}

        mock_s3_instance = MagicMock()
        mock_s3_instance.session = mock_session
        mock_s3_instance._get_s3_client.return_value = mock_s3_client
        mock_s3_instance._get_file_metadata.return_value = mock_metadata
        mock_s3_manager.return_value = mock_s3_instance

        credentials = {'session': mock_session}
        uploader = AssetUploader('aws_s3', credentials)

        # Create test file
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as tf:
            tf.write('test content')
            test_file = Path(tf.name)

        try:
            # Execute upload
            result = uploader.upload_file(
                test_file,
                bucket='test-bucket',
                remote_path='assets/test.pdf',
                region='us-east-1'
            )

            # Verify: upload_file was called
            mock_s3_client.upload_file.assert_called_once()
            call_args = mock_s3_client.upload_file.call_args

            # Verify: ExtraArgs uses S3Manager metadata (no ACL, has caching headers)
            extra_args = call_args[1]['ExtraArgs']
            assert extra_args == mock_metadata, "Should use S3Manager's metadata"
            assert 'ACL' not in extra_args, "ACL should NOT be set (causes AccessControlListNotSupported error)"
            assert 'ContentType' in extra_args, "ContentType should be set"
            assert 'CacheControl' in extra_args, "CacheControl should be set (same as website deployment)"

        finally:
            # Cleanup
            test_file.unlink(missing_ok=True)


class TestUploadResult:
    """Tests for UploadResult dataclass"""

    def test_upload_result_success(self):
        """Test UploadResult for successful upload"""
        from datetime import datetime

        result = UploadResult(
            filename="test.pdf",
            size_bytes=1024,
            file_type="application/pdf",
            public_url="https://s3.amazonaws.com/bucket/test.pdf",
            bucket="test-bucket",
            remote_path="assets/test.pdf",
            region="us-east-1",
            provider="aws_s3",
            uploaded_at=datetime.now(),
            success=True
        )

        assert result.success
        assert result.filename == "test.pdf"
        assert result.error_message is None

    def test_upload_result_failure(self):
        """Test UploadResult for failed upload"""
        from datetime import datetime

        result = UploadResult(
            filename="test.pdf",
            size_bytes=1024,
            file_type="application/pdf",
            public_url="",
            bucket="test-bucket",
            remote_path="assets/test.pdf",
            region="us-east-1",
            provider="aws_s3",
            uploaded_at=datetime.now(),
            success=False,
            error_message="Access Denied"
        )

        assert not result.success
        assert result.error_message == "Access Denied"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
