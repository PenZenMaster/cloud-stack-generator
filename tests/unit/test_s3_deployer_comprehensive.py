"""
Module/Script Name: Test S3 Website Deployer
Path: tests/unit/test_s3_deployer_comprehensive.py

Description:
Comprehensive unit tests for S3WebsiteDeployer class

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-12-21

Comments:
* v1.00 - Comprehensive test suite to improve coverage from 13.87% to 80%+
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from botocore.exceptions import ClientError

from src.core.deployment.s3_deployer import (
    S3WebsiteDeployer,
    deploy_client_website
)


@pytest.fixture
def mock_boto3_session():
    """Fixture for mocked boto3 session"""
    with patch('boto3.Session') as mock_session:
        mock_client = Mock()
        mock_resource = Mock()
        mock_session.return_value.client.return_value = mock_client
        mock_session.return_value.resource.return_value = mock_resource
        yield mock_session, mock_client, mock_resource


class TestS3WebsiteDeployerInitialization:
    """Test S3WebsiteDeployer initialization"""

    def test_init_default_parameters(self, mock_boto3_session):
        """Test initialization with default parameters"""
        mock_session_class, mock_client, mock_resource = mock_boto3_session

        deployer = S3WebsiteDeployer()

        mock_session_class.assert_called_once_with(
            profile_name="AWS",
            region_name="us-east-1"
        )
        assert deployer.region == "us-east-1"

    def test_init_custom_parameters(self, mock_boto3_session):
        """Test initialization with custom parameters"""
        mock_session_class, mock_client, mock_resource = mock_boto3_session

        deployer = S3WebsiteDeployer(
            profile_name="custom-profile",
            region="us-west-2"
        )

        mock_session_class.assert_called_once_with(
            profile_name="custom-profile",
            region_name="us-west-2"
        )
        assert deployer.region == "us-west-2"


class TestCreateBucket:
    """Test create_bucket method"""

    def test_create_bucket_already_exists(self, mock_boto3_session):
        """Test creating a bucket that already exists"""
        _, mock_client, _ = mock_boto3_session
        mock_client.head_bucket.return_value = {}

        deployer = S3WebsiteDeployer()
        result = deployer.create_bucket("existing-bucket")

        assert result is True
        mock_client.head_bucket.assert_called_once_with(Bucket="existing-bucket")
        mock_client.create_bucket.assert_not_called()

    def test_create_bucket_new_us_east_1(self, mock_boto3_session):
        """Test creating new bucket in us-east-1 (no LocationConstraint)"""
        _, mock_client, _ = mock_boto3_session

        # Simulate bucket doesn't exist
        not_found_error = ClientError(
            {'Error': {'Code': '404'}},
            'HeadBucket'
        )
        mock_client.head_bucket.side_effect = not_found_error
        mock_client.create_bucket.return_value = {}

        deployer = S3WebsiteDeployer(region="us-east-1")
        result = deployer.create_bucket("new-bucket")

        assert result is True
        mock_client.create_bucket.assert_called_once_with(Bucket="new-bucket")

    def test_create_bucket_new_other_region(self, mock_boto3_session):
        """Test creating new bucket in region other than us-east-1"""
        _, mock_client, _ = mock_boto3_session

        not_found_error = ClientError(
            {'Error': {'Code': '404'}},
            'HeadBucket'
        )
        mock_client.head_bucket.side_effect = not_found_error
        mock_client.create_bucket.return_value = {}

        deployer = S3WebsiteDeployer(region="eu-west-1")
        result = deployer.create_bucket("new-bucket")

        assert result is True
        mock_client.create_bucket.assert_called_once_with(
            Bucket="new-bucket",
            CreateBucketConfiguration={"LocationConstraint": "eu-west-1"}
        )

    def test_create_bucket_creation_fails(self, mock_boto3_session):
        """Test bucket creation failure"""
        _, mock_client, _ = mock_boto3_session

        # First call (head_bucket) returns 404
        not_found_error = ClientError(
            {'Error': {'Code': '404'}},
            'HeadBucket'
        )
        mock_client.head_bucket.side_effect = not_found_error

        # Second call (create_bucket) fails
        create_error = ClientError(
            {'Error': {'Code': 'BucketAlreadyExists'}},
            'CreateBucket'
        )
        mock_client.create_bucket.side_effect = create_error

        deployer = S3WebsiteDeployer()
        result = deployer.create_bucket("failing-bucket")

        assert result is False

    def test_create_bucket_head_bucket_error(self, mock_boto3_session):
        """Test handling of head_bucket errors other than 404"""
        _, mock_client, _ = mock_boto3_session

        access_denied_error = ClientError(
            {'Error': {'Code': '403'}},
            'HeadBucket'
        )
        mock_client.head_bucket.side_effect = access_denied_error

        deployer = S3WebsiteDeployer()
        result = deployer.create_bucket("access-denied-bucket")

        assert result is False


class TestConfigurePublicAccess:
    """Test configure_public_access method"""

    def test_configure_public_access_success(self, mock_boto3_session):
        """Test successful public access configuration"""
        _, mock_client, _ = mock_boto3_session
        mock_client.put_public_access_block.return_value = {}

        deployer = S3WebsiteDeployer()
        result = deployer.configure_public_access("test-bucket")

        assert result is True
        mock_client.put_public_access_block.assert_called_once_with(
            Bucket="test-bucket",
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": False,
                "IgnorePublicAcls": False,
                "BlockPublicPolicy": False,
                "RestrictPublicBuckets": False,
            }
        )

    def test_configure_public_access_failure(self, mock_boto3_session):
        """Test public access configuration failure"""
        _, mock_client, _ = mock_boto3_session

        error = ClientError(
            {'Error': {'Code': 'NoSuchBucket'}},
            'PutPublicAccessBlock'
        )
        mock_client.put_public_access_block.side_effect = error

        deployer = S3WebsiteDeployer()
        result = deployer.configure_public_access("nonexistent-bucket")

        assert result is False


class TestApplyPublicReadPolicy:
    """Test apply_public_read_policy method"""

    def test_apply_public_read_policy_success(self, mock_boto3_session):
        """Test successful application of public read policy"""
        _, mock_client, _ = mock_boto3_session
        mock_client.put_bucket_policy.return_value = {}

        deployer = S3WebsiteDeployer()
        result = deployer.apply_public_read_policy("test-bucket")

        assert result is True

        # Verify the policy was applied with correct structure
        call_args = mock_client.put_bucket_policy.call_args
        assert call_args[1]['Bucket'] == "test-bucket"

        policy = json.loads(call_args[1]['Policy'])
        assert policy['Version'] == "2012-10-17"
        assert len(policy['Statement']) == 1
        assert policy['Statement'][0]['Effect'] == "Allow"
        assert policy['Statement'][0]['Action'] == "s3:GetObject"
        assert "test-bucket" in policy['Statement'][0]['Resource']

    def test_apply_public_read_policy_failure(self, mock_boto3_session):
        """Test public read policy application failure"""
        _, mock_client, _ = mock_boto3_session

        error = ClientError(
            {'Error': {'Code': 'MalformedPolicy'}},
            'PutBucketPolicy'
        )
        mock_client.put_bucket_policy.side_effect = error

        deployer = S3WebsiteDeployer()
        result = deployer.apply_public_read_policy("test-bucket")

        assert result is False


class TestEnableStaticWebsite:
    """Test enable_static_website method"""

    def test_enable_static_website_default_documents(self, mock_boto3_session):
        """Test enabling static website with default documents"""
        _, mock_client, _ = mock_boto3_session
        mock_client.put_bucket_website.return_value = {}

        deployer = S3WebsiteDeployer()
        result = deployer.enable_static_website("test-bucket")

        assert result is True
        mock_client.put_bucket_website.assert_called_once_with(
            Bucket="test-bucket",
            WebsiteConfiguration={
                "IndexDocument": {"Suffix": "index.html"},
                "ErrorDocument": {"Key": "error.html"},
            }
        )

    def test_enable_static_website_custom_documents(self, mock_boto3_session):
        """Test enabling static website with custom documents"""
        _, mock_client, _ = mock_boto3_session
        mock_client.put_bucket_website.return_value = {}

        deployer = S3WebsiteDeployer()
        result = deployer.enable_static_website(
            "test-bucket",
            index_document="home.html",
            error_document="404.html"
        )

        assert result is True
        mock_client.put_bucket_website.assert_called_once_with(
            Bucket="test-bucket",
            WebsiteConfiguration={
                "IndexDocument": {"Suffix": "home.html"},
                "ErrorDocument": {"Key": "404.html"},
            }
        )

    def test_enable_static_website_failure(self, mock_boto3_session):
        """Test static website enabling failure"""
        _, mock_client, _ = mock_boto3_session

        error = ClientError(
            {'Error': {'Code': 'InvalidArgument'}},
            'PutBucketWebsite'
        )
        mock_client.put_bucket_website.side_effect = error

        deployer = S3WebsiteDeployer()
        result = deployer.enable_static_website("test-bucket")

        assert result is False


class TestGetWebsiteUrl:
    """Test get_website_url method"""

    def test_get_website_url_us_east_1(self, mock_boto3_session):
        """Test getting website URL for us-east-1"""
        deployer = S3WebsiteDeployer(region="us-east-1")
        url = deployer.get_website_url("my-bucket")

        assert url == "http://my-bucket.s3-website-us-east-1.amazonaws.com"

    def test_get_website_url_other_region(self, mock_boto3_session):
        """Test getting website URL for other regions"""
        deployer = S3WebsiteDeployer(region="eu-west-1")
        url = deployer.get_website_url("my-bucket")

        assert url == "http://my-bucket.s3-website-eu-west-1.amazonaws.com"


class TestGetContentType:
    """Test _get_content_type static method"""

    def test_get_content_type_html(self):
        """Test content type for HTML files"""
        assert S3WebsiteDeployer._get_content_type(Path("index.html")) == "text/html"

    def test_get_content_type_css(self):
        """Test content type for CSS files"""
        assert S3WebsiteDeployer._get_content_type(Path("style.css")) == "text/css"

    def test_get_content_type_javascript(self):
        """Test content type for JavaScript files"""
        assert S3WebsiteDeployer._get_content_type(Path("app.js")) == "application/javascript"

    def test_get_content_type_images(self):
        """Test content types for various image formats"""
        assert S3WebsiteDeployer._get_content_type(Path("logo.png")) == "image/png"
        assert S3WebsiteDeployer._get_content_type(Path("photo.jpg")) == "image/jpeg"
        assert S3WebsiteDeployer._get_content_type(Path("photo.jpeg")) == "image/jpeg"
        assert S3WebsiteDeployer._get_content_type(Path("icon.svg")) == "image/svg+xml"

    def test_get_content_type_fonts(self):
        """Test content types for font files"""
        assert S3WebsiteDeployer._get_content_type(Path("font.woff")) == "font/woff"
        assert S3WebsiteDeployer._get_content_type(Path("font.woff2")) == "font/woff2"

    def test_get_content_type_unknown(self):
        """Test content type for unknown file extension"""
        assert S3WebsiteDeployer._get_content_type(Path("file.unknown")) == "application/octet-stream"

    def test_get_content_type_case_insensitive(self):
        """Test content type detection is case-insensitive"""
        assert S3WebsiteDeployer._get_content_type(Path("INDEX.HTML")) == "text/html"
        assert S3WebsiteDeployer._get_content_type(Path("STYLE.CSS")) == "text/css"


class TestUploadDirectory:
    """Test upload_directory method"""

    def test_upload_directory_nonexistent_path(self, mock_boto3_session, tmp_path):
        """Test uploading from nonexistent path"""
        _, mock_client, mock_resource = mock_boto3_session

        deployer = S3WebsiteDeployer()
        nonexistent_path = tmp_path / "nonexistent"
        result = deployer.upload_directory(nonexistent_path, "test-bucket")

        assert result is False
        mock_resource.Bucket.assert_not_called()

    def test_upload_directory_empty(self, mock_boto3_session, tmp_path):
        """Test uploading empty directory"""
        _, mock_client, mock_resource = mock_boto3_session

        # Create empty directory
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        mock_bucket = Mock()
        mock_resource.Bucket.return_value = mock_bucket

        deployer = S3WebsiteDeployer()
        result = deployer.upload_directory(empty_dir, "test-bucket")

        assert result is True
        mock_bucket.upload_file.assert_not_called()

    def test_upload_directory_with_files(self, mock_boto3_session, tmp_path):
        """Test uploading directory with files"""
        _, mock_client, mock_resource = mock_boto3_session

        # Create test directory structure
        test_dir = tmp_path / "website"
        test_dir.mkdir()
        (test_dir / "index.html").write_text("<html></html>")
        (test_dir / "style.css").write_text("body {}")
        (test_dir / "js").mkdir()
        (test_dir / "js" / "app.js").write_text("console.log('test');")

        mock_bucket = Mock()
        mock_resource.Bucket.return_value = mock_bucket

        deployer = S3WebsiteDeployer()
        result = deployer.upload_directory(test_dir, "test-bucket")

        assert result is True
        assert mock_bucket.upload_file.call_count == 3

    def test_upload_directory_with_prefix(self, mock_boto3_session, tmp_path):
        """Test uploading directory with prefix"""
        _, mock_client, mock_resource = mock_boto3_session

        test_dir = tmp_path / "website"
        test_dir.mkdir()
        (test_dir / "index.html").write_text("<html></html>")

        mock_bucket = Mock()
        mock_resource.Bucket.return_value = mock_bucket

        deployer = S3WebsiteDeployer()
        result = deployer.upload_directory(test_dir, "test-bucket", prefix="client1")

        assert result is True
        # Verify prefix was used in upload
        call_args = mock_bucket.upload_file.call_args_list[0]
        s3_key = call_args[0][1]
        assert s3_key.startswith("client1/")

    def test_upload_directory_client_error(self, mock_boto3_session, tmp_path):
        """Test handling of upload errors"""
        _, mock_client, mock_resource = mock_boto3_session

        test_dir = tmp_path / "website"
        test_dir.mkdir()
        (test_dir / "index.html").write_text("<html></html>")

        mock_bucket = Mock()
        error = ClientError(
            {'Error': {'Code': 'NoSuchBucket'}},
            'PutObject'
        )
        mock_bucket.upload_file.side_effect = error
        mock_resource.Bucket.return_value = mock_bucket

        deployer = S3WebsiteDeployer()
        result = deployer.upload_directory(test_dir, "test-bucket")

        assert result is False


class TestDeployWebsite:
    """Test deploy_website method"""

    def test_deploy_website_full_success(self, mock_boto3_session, tmp_path):
        """Test complete successful website deployment"""
        _, mock_client, mock_resource = mock_boto3_session

        # Setup mocks for all steps
        mock_client.head_bucket.side_effect = ClientError(
            {'Error': {'Code': '404'}}, 'HeadBucket'
        )
        mock_client.create_bucket.return_value = {}
        mock_client.put_public_access_block.return_value = {}
        mock_client.put_bucket_policy.return_value = {}
        mock_client.put_bucket_website.return_value = {}

        mock_bucket = Mock()
        mock_resource.Bucket.return_value = mock_bucket

        # Create test website
        website_dir = tmp_path / "website"
        website_dir.mkdir()
        (website_dir / "index.html").write_text("<html></html>")

        deployer = S3WebsiteDeployer()
        result = deployer.deploy_website("test-bucket", website_dir)

        assert result['success'] is True
        assert 'bucket_created' in result['steps_completed']
        assert 'public_access_configured' in result['steps_completed']
        assert 'public_policy_applied' in result['steps_completed']
        assert 'website_hosting_enabled' in result['steps_completed']
        assert 'files_uploaded' in result['steps_completed']
        assert result['website_url'] is not None
        assert len(result['errors']) == 0

    def test_deploy_website_bucket_creation_fails(self, mock_boto3_session, tmp_path):
        """Test deployment when bucket creation fails"""
        _, mock_client, _ = mock_boto3_session

        error = ClientError(
            {'Error': {'Code': 'BucketAlreadyOwnedByYou'}},
            'CreateBucket'
        )
        mock_client.head_bucket.side_effect = ClientError(
            {'Error': {'Code': '404'}}, 'HeadBucket'
        )
        mock_client.create_bucket.side_effect = error

        website_dir = tmp_path / "website"
        website_dir.mkdir()

        deployer = S3WebsiteDeployer()
        result = deployer.deploy_website("test-bucket", website_dir)

        assert result['success'] is False
        assert 'Failed to create bucket' in result['errors']

    def test_deploy_website_with_subdirectory(self, mock_boto3_session, tmp_path):
        """Test deployment with subdirectory"""
        _, mock_client, mock_resource = mock_boto3_session

        # Setup successful mocks
        mock_client.head_bucket.return_value = {}
        mock_bucket = Mock()
        mock_resource.Bucket.return_value = mock_bucket

        website_dir = tmp_path / "website"
        website_dir.mkdir()
        (website_dir / "index.html").write_text("<html></html>")

        deployer = S3WebsiteDeployer()
        result = deployer.deploy_website(
            "test-bucket",
            website_dir,
            subdirectory="client-site",
            create_if_not_exists=False
        )

        assert result['success'] is True
        assert "client-site" in result['full_url']

    def test_deploy_website_without_creation(self, mock_boto3_session, tmp_path):
        """Test deployment to existing bucket without creation"""
        _, mock_client, mock_resource = mock_boto3_session

        mock_bucket = Mock()
        mock_resource.Bucket.return_value = mock_bucket

        website_dir = tmp_path / "website"
        website_dir.mkdir()
        (website_dir / "index.html").write_text("<html></html>")

        deployer = S3WebsiteDeployer()
        result = deployer.deploy_website(
            "existing-bucket",
            website_dir,
            create_if_not_exists=False
        )

        assert result['success'] is True
        # Verify bucket creation steps were skipped
        assert 'bucket_created' not in result['steps_completed']
        mock_client.create_bucket.assert_not_called()


class TestDeployClientWebsite:
    """Test deploy_client_website convenience function"""

    @patch('src.core.deployment.s3_deployer.S3WebsiteDeployer')
    @patch('src.core.deployment.s3_deployer.Path')
    def test_deploy_client_website_success(self, mock_path_class, mock_deployer_class):
        """Test successful client website deployment"""
        # Setup path mock
        mock_output_path = Mock()
        mock_output_path.exists.return_value = True
        mock_path_class.return_value.__truediv__.return_value = mock_output_path

        # Setup deployer mock
        mock_deployer = Mock()
        mock_deployer.deploy_website.return_value = {
            'success': True,
            'bucket_name': 'test-bucket',
            'full_url': 'http://test-bucket.s3-website-us-east-1.amazonaws.com/client-site/',
            'steps_completed': ['bucket_created', 'files_uploaded']
        }
        mock_deployer_class.return_value = mock_deployer

        result = deploy_client_website(
            "test_client",
            bucket_name="test-bucket",
            profile="AWS",
            region="us-east-1"
        )

        assert result['success'] is True
        mock_deployer_class.assert_called_once_with(
            profile_name="AWS",
            region="us-east-1"
        )

    @patch('src.core.deployment.s3_deployer.Path')
    def test_deploy_client_website_not_found(self, mock_path_class):
        """Test client website deployment when directory doesn't exist"""
        # Create a mock that represents the file path resolution chain
        mock_output_path = Mock()
        mock_output_path.exists.return_value = False

        # Mock the entire Path(...).parent.parent.parent.parent / "output" / "clients" / client_slug chain
        def path_div_side_effect(arg):
            result = Mock()
            if arg == "output" or arg == "clients" or isinstance(arg, str):
                result.__truediv__ = Mock(side_effect=path_div_side_effect)
                result.exists.return_value = False
                return result
            return mock_output_path

        mock_path_instance = Mock()
        mock_path_instance.parent.parent.parent.parent.__truediv__ = Mock(side_effect=path_div_side_effect)
        mock_path_class.return_value = mock_path_instance

        result = deploy_client_website("nonexistent_client")

        assert result['success'] is False
        assert len(result['errors']) > 0
        assert 'not found' in result['errors'][0].lower()
