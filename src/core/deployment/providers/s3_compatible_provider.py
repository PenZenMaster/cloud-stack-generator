"""
Module/Script Name: S3 Compatible Provider Base Class
Path: src/core/deployment/providers/s3_compatible_provider.py

Description:
Base class for S3-compatible cloud storage providers (AWS S3, Wasabi, Backblaze B2, etc.).
Implements common S3 API operations using boto3 with configurable endpoint URLs.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial S3-compatible provider base class
"""

from typing import Dict, List, Optional, Tuple, Callable
from pathlib import Path
import mimetypes

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

from .abstract_provider import (
    AbstractCloudProvider,
    ProviderType,
    DeploymentResult,
    ProviderConfig,
    AuthenticationError,
    BucketCreationError,
    UploadError,
    CDNConfigurationError,
)

from ...utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


class S3CompatibleProvider(AbstractCloudProvider):
    """
    Base class for S3-compatible cloud storage providers.

    This class provides common S3 API functionality using boto3 with
    configurable endpoint URLs to support AWS S3, Wasabi, Backblaze B2,
    DigitalOcean Spaces, and other S3-compatible services.

    Subclasses should override:
    - _get_endpoint_url() - Return provider-specific endpoint URL
    - configure_cdn() - Implement provider-specific CDN configuration
    - get_website_url() - Return provider-specific website URL format

    Features:
    - Bucket creation and management
    - File upload with metadata and cache control
    - Directory upload with progress tracking
    - Static website hosting configuration
    - Public access policy management
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize S3-compatible provider.

        Args:
            config: Provider configuration
        """
        super().__init__(config)

        self.session: Optional[boto3.Session] = None
        self.s3_client = None
        self.s3_resource = None

        # Cache settings for different file types (aligned with S3Manager)
        self.cache_settings = {
            # HTML files - short cache (5 minutes)
            'html': {'CacheControl': 'max-age=300,public', 'ContentType': 'text/html'},
            'htm': {'CacheControl': 'max-age=300,public', 'ContentType': 'text/html'},

            # Data files - longer cache (1 day)
            'json': {'CacheControl': 'max-age=86400,public', 'ContentType': 'application/json'},
            'csv': {'CacheControl': 'max-age=86400,public', 'ContentType': 'text/csv'},
            'xlsx': {'CacheControl': 'max-age=86400,public', 'ContentType': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'},

            # Static assets - long cache (1 day)
            'css': {'CacheControl': 'max-age=86400,public', 'ContentType': 'text/css'},
            'js': {'CacheControl': 'max-age=86400,public', 'ContentType': 'application/javascript'},
            'png': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/png'},
            'jpg': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/jpeg'},
            'jpeg': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/jpeg'},
            'gif': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/gif'},
            'webp': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/webp'},
            'svg': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/svg+xml'},
            'ico': {'CacheControl': 'max-age=86400,public', 'ContentType': 'image/x-icon'},

            # Documents and other files
            'txt': {'CacheControl': 'max-age=300,public', 'ContentType': 'text/plain'},
            'xml': {'CacheControl': 'max-age=300,public', 'ContentType': 'application/xml'},
            'pdf': {'CacheControl': 'max-age=86400,public', 'ContentType': 'application/pdf'},
        }

        logger.info(
            f"S3-compatible provider initialized: {self.provider_type.value}",
            extra={"extra_fields": {"region": config.region}}
        )

    def _get_endpoint_url(self) -> Optional[str]:
        """
        Get S3-compatible endpoint URL for this provider.

        Subclasses should override this to return provider-specific endpoints.
        AWS S3 returns None (uses default boto3 endpoints).

        Returns:
            Endpoint URL or None for AWS S3
        """
        # Default: AWS S3 (no custom endpoint)
        return None

    def _create_session(self) -> boto3.Session:
        """
        Create boto3 session from credentials.

        Returns:
            Configured boto3 Session

        Raises:
            AuthenticationError: If credentials are invalid
        """
        try:
            credentials = self.config.credentials

            # Extract AWS credentials
            aws_access_key_id = credentials.get("aws_access_key_id") or credentials.get("access_key_id")
            aws_secret_access_key = credentials.get("aws_secret_access_key") or credentials.get("secret_access_key")

            if not aws_access_key_id or not aws_secret_access_key:
                raise AuthenticationError(
                    "Missing required credentials. Provide:\n"
                    "- aws_access_key_id (or access_key_id)\n"
                    "- aws_secret_access_key (or secret_access_key)"
                )

            # Create session
            session = boto3.Session(
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=self.config.region
            )

            return session

        except Exception as e:
            raise AuthenticationError(f"Failed to create session: {str(e)}")

    def _get_s3_client(self):
        """Get or create S3 client with provider-specific endpoint"""
        if not self.s3_client:
            endpoint_url = self._get_endpoint_url()

            client_config = {
                's3': {'addressing_style': 'path'}  # Use path-style for compatibility
            }

            if endpoint_url:
                self.s3_client = self.session.client(
                    's3',
                    endpoint_url=endpoint_url,
                    config=boto3.session.Config(**client_config)
                )
            else:
                self.s3_client = self.session.client('s3')

        return self.s3_client

    def _get_s3_resource(self):
        """Get or create S3 resource with provider-specific endpoint"""
        if not self.s3_resource:
            endpoint_url = self._get_endpoint_url()

            if endpoint_url:
                self.s3_resource = self.session.resource(
                    's3',
                    endpoint_url=endpoint_url
                )
            else:
                self.s3_resource = self.session.resource('s3')

        return self.s3_resource

    def authenticate(self) -> bool:
        """
        Authenticate with S3-compatible provider.

        Returns:
            True if authentication successful

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            # Create session
            self.session = self._create_session()

            # Reset clients to use new session
            self.s3_client = None
            self.s3_resource = None

            # Test connection
            success, message = self.test_connection()

            if not success:
                raise AuthenticationError(message)

            self._authenticated = True
            logger.info(
                f"{self.provider_type.value} authentication successful",
                extra={"extra_fields": {"region": self.config.region}}
            )
            return True

        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            raise AuthenticationError(f"Authentication failed: {str(e)}")

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to S3-compatible provider.

        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.session:
                return False, "Not authenticated - session not initialized"

            s3 = self._get_s3_client()

            # List buckets to test connection
            s3.list_buckets()

            message = f"{self.provider_type.value} connection successful"
            logger.info(message)
            return True, message

        except NoCredentialsError:
            return False, "No credentials found"
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            return False, f"Connection failed ({error_code}): {str(e)}"
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"

    def create_bucket(self, bucket_name: str) -> bool:
        """
        Create S3-compatible bucket.

        Args:
            bucket_name: Name of bucket to create

        Returns:
            True if successful

        Raises:
            BucketCreationError: If bucket creation fails
        """
        try:
            self.require_authentication()

            # Validate bucket name
            valid, error = self.validate_bucket_name(bucket_name)
            if not valid:
                raise BucketCreationError(error)

            s3 = self._get_s3_client()
            region = self.config.region

            # Create bucket with region-specific logic
            if region == "us-east-1":
                # us-east-1 doesn't need LocationConstraint
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )

            logger.info(
                f"Bucket created successfully: {bucket_name}",
                extra={"extra_fields": {
                    "provider": self.provider_type.value,
                    "region": region
                }}
            )
            return True

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            if error_code == 'BucketAlreadyExists':
                raise BucketCreationError(f"Bucket '{bucket_name}' already exists globally")
            elif error_code == 'BucketAlreadyOwnedByYou':
                logger.info(f"Bucket '{bucket_name}' already exists and is owned by you")
                return True
            else:
                raise BucketCreationError(f"Failed to create bucket ({error_code}): {str(e)}")
        except Exception as e:
            raise BucketCreationError(f"Failed to create bucket: {str(e)}")

    def configure_website_hosting(self, bucket_name: str) -> bool:
        """
        Configure bucket for static website hosting.

        This configures public access and website hosting settings.

        Args:
            bucket_name: Name of bucket to configure

        Returns:
            True if successful
        """
        try:
            self.require_authentication()

            s3 = self._get_s3_client()

            # Step 1: Disable Block Public Access
            s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': False,
                    'IgnorePublicAcls': False,
                    'BlockPublicPolicy': False,
                    'RestrictPublicBuckets': False
                }
            )

            # Step 2: Apply public read policy
            import json
            bucket_policy = {
                "Version": "2012-10-17",
                "Statement": [{
                    "Sid": "PublicReadGetObject",
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{bucket_name}/*"]
                }]
            }

            s3.put_bucket_policy(
                Bucket=bucket_name,
                Policy=json.dumps(bucket_policy)
            )

            # Step 3: Configure website hosting
            s3.put_bucket_website(
                Bucket=bucket_name,
                WebsiteConfiguration={
                    'IndexDocument': {'Suffix': 'index.html'},
                    'ErrorDocument': {'Key': '404.html'}
                }
            )

            logger.info(
                f"Website hosting configured: {bucket_name}",
                extra={"extra_fields": {"provider": self.provider_type.value}}
            )
            return True

        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', 'Unknown')
            logger.error(
                f"Failed to configure website hosting ({error_code}): {str(e)}",
                extra={"extra_fields": {"bucket": bucket_name}}
            )
            return False
        except Exception as e:
            logger.error(
                f"Failed to configure website hosting: {str(e)}",
                extra={"extra_fields": {"bucket": bucket_name}}
            )
            return False

    def upload_file(
        self,
        local_path: Path,
        remote_path: str,
        content_type: str,
        cache_control: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Upload a single file to S3-compatible storage.

        Args:
            local_path: Path to local file
            remote_path: Remote path in bucket
            content_type: MIME type of file
            cache_control: Cache-Control header value
            metadata: Additional metadata

        Returns:
            True if successful

        Raises:
            UploadError: If upload fails
        """
        try:
            self.require_authentication()

            if not local_path.exists():
                raise UploadError(f"Local file not found: {local_path}")

            # Get bucket from config
            bucket_name = self.config.extra_config.get("current_bucket")
            if not bucket_name:
                raise UploadError("No bucket specified for upload")

            s3 = self._get_s3_client()

            # Prepare upload arguments
            extra_args = {
                'ContentType': content_type
            }

            if cache_control:
                extra_args['CacheControl'] = cache_control

            if metadata:
                extra_args['Metadata'] = metadata

            # Upload file
            s3.upload_file(
                str(local_path),
                bucket_name,
                remote_path,
                ExtraArgs=extra_args
            )

            return True

        except Exception as e:
            logger.error(f"Failed to upload file {local_path}: {str(e)}")
            raise UploadError(f"Failed to upload file: {str(e)}")

    def upload_directory(
        self,
        local_dir: Path,
        bucket_name: str,
        prefix: str = "",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> DeploymentResult:
        """
        Upload entire directory to S3-compatible storage.

        Args:
            local_dir: Path to local directory
            bucket_name: Name of bucket
            prefix: Optional prefix for remote paths
            progress_callback: Optional progress callback (current, total, filename)

        Returns:
            DeploymentResult with upload details
        """
        try:
            self.require_authentication()

            if not local_dir.exists() or not local_dir.is_dir():
                raise UploadError(f"Local directory not found: {local_dir}")

            # Store bucket name for file uploads
            self.config.extra_config["current_bucket"] = bucket_name

            # Collect all files
            files_to_upload = []
            for file_path in local_dir.rglob("*"):
                if file_path.is_file():
                    # Skip common excludes
                    if file_path.name.startswith('.') or file_path.name in ['Thumbs.db']:
                        continue
                    files_to_upload.append(file_path)

            total_files = len(files_to_upload)
            uploaded_count = 0
            errors = []

            logger.info(
                f"Uploading {total_files} files to bucket: {bucket_name}",
                extra={"extra_fields": {"provider": self.provider_type.value}}
            )

            # Upload each file
            for current, file_path in enumerate(files_to_upload, 1):
                try:
                    # Calculate remote path
                    relative_path = file_path.relative_to(local_dir)
                    if prefix:
                        remote_path = f"{prefix.rstrip('/')}/{relative_path}"
                    else:
                        remote_path = str(relative_path)

                    # Normalize path separators
                    remote_path = remote_path.replace('\\', '/')

                    # Get file metadata based on extension
                    file_ext = file_path.suffix.lstrip('.').lower()
                    file_metadata = self._get_file_metadata(file_ext)

                    content_type = file_metadata.get('ContentType', self.get_content_type(file_path))
                    cache_control = file_metadata.get('CacheControl', self.get_cache_control(file_path))

                    # Upload file
                    self.upload_file(
                        file_path,
                        remote_path,
                        content_type,
                        cache_control
                    )

                    uploaded_count += 1

                    # Progress callback
                    if progress_callback:
                        progress_callback(current, total_files, str(relative_path))

                except Exception as e:
                    error_msg = f"Failed to upload {file_path.name}: {str(e)}"
                    logger.warning(error_msg)
                    errors.append(error_msg)

            # Get website URL
            website_url = self.get_website_url(bucket_name)

            # Create result
            result = DeploymentResult(
                success=(uploaded_count > 0),
                provider=self.provider_type,
                bucket_name=bucket_name,
                website_url=website_url,
                files_uploaded=uploaded_count,
                errors=errors,
                metadata={
                    "total_files": total_files,
                    "region": self.config.region
                }
            )

            logger.info(
                f"Directory upload completed: {uploaded_count}/{total_files} files",
                extra={"extra_fields": {
                    "provider": self.provider_type.value,
                    "errors": len(errors)
                }}
            )

            return result

        except Exception as e:
            logger.error(f"Directory upload failed: {str(e)}")
            return DeploymentResult(
                success=False,
                provider=self.provider_type,
                bucket_name=bucket_name,
                website_url="",
                errors=[str(e)]
            )

    def _get_file_metadata(self, file_ext: str) -> Dict[str, str]:
        """
        Get S3 upload metadata for file extension.

        Args:
            file_ext: File extension (without dot)

        Returns:
            Dictionary with ContentType and CacheControl
        """
        if file_ext in self.cache_settings:
            return self.cache_settings[file_ext]

        # Default for unknown file types
        content_type, _ = mimetypes.guess_type(f"file.{file_ext}")
        return {
            'CacheControl': 'max-age=86400,public',
            'ContentType': content_type or 'application/octet-stream'
        }

    def configure_cdn(
        self,
        bucket_name: str,
        custom_domain: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Configure CDN for bucket.

        This is provider-specific and should be overridden by subclasses.
        Base implementation returns bucket URL without CDN.

        Args:
            bucket_name: Name of bucket
            custom_domain: Optional custom domain

        Returns:
            Tuple of (success, cdn_url)

        Raises:
            CDNConfigurationError: If CDN configuration fails
        """
        logger.warning(
            f"CDN configuration not implemented for {self.provider_type.value}",
            extra={"extra_fields": {"bucket": bucket_name}}
        )
        return False, None

    def get_website_url(self, bucket_name: str) -> str:
        """
        Get website URL for bucket.

        This should be overridden by subclasses to return provider-specific URLs.

        Args:
            bucket_name: Name of bucket

        Returns:
            Website URL
        """
        # Default implementation - should be overridden
        region = self.config.region
        if region == 'us-east-1':
            return f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
        else:
            return f"http://{bucket_name}.s3-website.{region}.amazonaws.com"

    def list_buckets(self) -> List[str]:
        """
        List all buckets accessible with current credentials.

        Returns:
            List of bucket names
        """
        try:
            self.require_authentication()

            s3 = self._get_s3_client()
            response = s3.list_buckets()

            bucket_names = [bucket['Name'] for bucket in response.get('Buckets', [])]

            logger.info(
                f"Listed {len(bucket_names)} buckets",
                extra={"extra_fields": {"provider": self.provider_type.value}}
            )
            return bucket_names

        except Exception as e:
            logger.error(f"Failed to list buckets: {str(e)}")
            return []

    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete bucket and optionally all contents.

        Args:
            bucket_name: Name of bucket to delete
            force: If True, delete all contents first

        Returns:
            True if successful
        """
        try:
            self.require_authentication()

            s3_client = self._get_s3_client()

            if force:
                # Delete all objects in bucket
                s3_resource = self._get_s3_resource()
                bucket = s3_resource.Bucket(bucket_name)

                objects_to_delete = []
                for obj in bucket.objects.all():
                    objects_to_delete.append({'Key': obj.key})

                # Delete objects in batches
                for i in range(0, len(objects_to_delete), 1000):
                    batch = objects_to_delete[i:i+1000]
                    s3_client.delete_objects(
                        Bucket=bucket_name,
                        Delete={'Objects': batch}
                    )

                logger.info(f"Deleted {len(objects_to_delete)} objects from bucket: {bucket_name}")

            # Delete bucket
            s3_client.delete_bucket(Bucket=bucket_name)

            logger.info(
                f"Bucket deleted: {bucket_name}",
                extra={"extra_fields": {"provider": self.provider_type.value}}
            )
            return True

        except Exception as e:
            logger.error(f"Failed to delete bucket: {str(e)}")
            return False
