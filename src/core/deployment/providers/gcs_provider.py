"""
Module/Script Name: Google Cloud Storage Provider
Path: src/core/deployment/providers/gcs_provider.py

Description:
Google Cloud Storage provider implementation for static website deployment.
Supports GCS bucket creation, website hosting configuration, and Cloud CDN integration.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-19

Last Modified Date:
2025-11-19

Comments:
* v1.00 - Initial GCS provider implementation
"""

from typing import Dict, List, Optional, Tuple, Callable
from pathlib import Path
import json

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

try:
    from google.cloud import storage
    from google.cloud.exceptions import NotFound, Conflict
    from google.oauth2 import service_account
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False
    logger.warning("google-cloud-storage library not installed. GCS provider unavailable.")


class GCSProvider(AbstractCloudProvider):
    """
    Google Cloud Storage provider implementation.

    Features:
    - GCS bucket creation and management
    - Static website hosting configuration
    - Cloud CDN integration
    - IAM and bucket policy management
    - Regional and multi-regional deployment

    Authentication Methods:
    1. Service Account JSON file
    2. Service Account key components (project_id, client_email, private_key)
    3. Application Default Credentials (ADC)
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize GCS provider.

        Args:
            config: Provider configuration

        Raises:
            ImportError: If google-cloud-storage not installed
        """
        if not GCS_AVAILABLE:
            raise ImportError(
                "google-cloud-storage library required for GCS provider. "
                "Install with: pip install google-cloud-storage"
            )

        super().__init__(config)

        self.client: Optional[storage.Client] = None
        self.project_id: Optional[str] = None

        logger.info(
            f"GCS Provider initialized for region: {config.region}",
            extra={"extra_fields": {"deployment_mode": config.deployment_mode.value}}
        )

    def authenticate(self) -> bool:
        """
        Authenticate with Google Cloud Storage.

        Supports three authentication methods:
        1. Service Account JSON file path
        2. Service Account key components
        3. Application Default Credentials

        Returns:
            True if authentication successful

        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            credentials = self.config.credentials

            # Method 1: Service Account JSON file
            if "service_account_json" in credentials:
                json_path = credentials["service_account_json"]
                logger.info(f"Authenticating with service account file: {json_path}")

                if not Path(json_path).exists():
                    raise AuthenticationError(f"Service account file not found: {json_path}")

                creds = service_account.Credentials.from_service_account_file(json_path)
                self.client = storage.Client(credentials=creds)

                # Extract project ID from service account file
                with open(json_path, 'r') as f:
                    sa_data = json.load(f)
                    self.project_id = sa_data.get("project_id")

            # Method 2: Service Account key components
            elif "project_id" in credentials and "private_key" in credentials:
                logger.info("Authenticating with service account key components")

                sa_info = {
                    "type": "service_account",
                    "project_id": credentials["project_id"],
                    "private_key": credentials["private_key"],
                    "client_email": credentials.get("client_email", ""),
                    "token_uri": "https://oauth2.googleapis.com/token",
                }

                creds = service_account.Credentials.from_service_account_info(sa_info)
                self.client = storage.Client(credentials=creds, project=credentials["project_id"])
                self.project_id = credentials["project_id"]

            # Method 3: Application Default Credentials
            elif credentials.get("use_adc"):
                logger.info("Using Application Default Credentials")
                self.client = storage.Client()
                self.project_id = self.client.project

            # Method 4: Project ID only (uses ADC)
            elif "project_id" in credentials:
                logger.info(f"Authenticating with project ID: {credentials['project_id']}")
                self.client = storage.Client(project=credentials["project_id"])
                self.project_id = credentials["project_id"]

            else:
                raise AuthenticationError(
                    "No valid authentication method found. Provide either:\n"
                    "1. service_account_json (path to JSON file)\n"
                    "2. project_id + private_key + client_email\n"
                    "3. use_adc: true (for Application Default Credentials)\n"
                    "4. project_id (uses ADC)"
                )

            if not self.project_id:
                raise AuthenticationError("Could not determine project_id")

            self._authenticated = True
            logger.info(
                "GCS authentication successful",
                extra={"extra_fields": {"project_id": self.project_id}}
            )
            return True

        except Exception as e:
            logger.error(f"GCS authentication failed: {str(e)}")
            raise AuthenticationError(f"GCS authentication failed: {str(e)}")

    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to Google Cloud Storage.

        Returns:
            Tuple of (success, message)
        """
        try:
            self.require_authentication()

            # List buckets to test connection
            list(self.client.list_buckets(max_results=1))

            message = f"GCS connection successful (Project: {self.project_id})"
            logger.info(message)
            return True, message

        except Exception as e:
            message = f"GCS connection test failed: {str(e)}"
            logger.error(message)
            return False, message

    def create_bucket(self, bucket_name: str) -> bool:
        """
        Create GCS bucket.

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

            # Check if bucket already exists
            try:
                bucket = self.client.get_bucket(bucket_name)
                logger.info(f"Bucket already exists: {bucket_name}")
                return True
            except NotFound:
                pass  # Bucket doesn't exist, proceed with creation

            # Create bucket
            bucket = self.client.bucket(bucket_name)

            # Set location (region or multi-region)
            location = self.config.region

            # Set storage class
            storage_class = self.config.extra_config.get("storage_class", "STANDARD")

            # Create with configuration
            bucket.storage_class = storage_class
            bucket = self.client.create_bucket(bucket, location=location)

            logger.info(
                f"GCS bucket created successfully: {bucket_name}",
                extra={"extra_fields": {
                    "location": location,
                    "storage_class": storage_class
                }}
            )
            return True

        except Conflict:
            # Bucket name already taken globally
            raise BucketCreationError(
                f"Bucket name '{bucket_name}' already exists globally. "
                "Choose a different name."
            )
        except Exception as e:
            logger.error(f"Failed to create bucket: {str(e)}")
            raise BucketCreationError(f"Failed to create bucket: {str(e)}")

    def configure_website_hosting(self, bucket_name: str) -> bool:
        """
        Configure GCS bucket for static website hosting.

        Args:
            bucket_name: Name of bucket to configure

        Returns:
            True if successful
        """
        try:
            self.require_authentication()

            bucket = self.client.get_bucket(bucket_name)

            # Set website configuration
            bucket.configure_website(
                main_page_suffix="index.html",
                not_found_page="404.html"
            )

            # Make bucket public (required for website hosting)
            # Add IAM binding for allUsers to have objectViewer role
            policy = bucket.get_iam_policy(requested_policy_version=3)
            policy.bindings.append({
                "role": "roles/storage.objectViewer",
                "members": {"allUsers"}
            })
            bucket.set_iam_policy(policy)

            # Update bucket
            bucket.patch()

            logger.info(
                f"GCS website hosting configured: {bucket_name}",
                extra={"extra_fields": {"public": True}}
            )
            return True

        except Exception as e:
            logger.error(f"Failed to configure website hosting: {str(e)}")
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
        Upload a single file to GCS.

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

            # Get bucket from config (assume last created/used bucket)
            # In practice, this should be passed as parameter
            bucket_name = self.config.extra_config.get("current_bucket")
            if not bucket_name:
                raise UploadError("No bucket specified for upload")

            bucket = self.client.get_bucket(bucket_name)
            blob = bucket.blob(remote_path)

            # Set content type
            blob.content_type = content_type

            # Set cache control
            if cache_control:
                blob.cache_control = cache_control

            # Set custom metadata
            if metadata:
                blob.metadata = metadata

            # Upload file
            blob.upload_from_filename(str(local_path))

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
        Upload entire directory to GCS.

        Args:
            local_dir: Path to local directory
            bucket_name: Name of bucket
            prefix: Optional prefix for remote paths
            progress_callback: Optional progress callback

        Returns:
            DeploymentResult with upload details
        """
        try:
            self.require_authentication()

            if not local_dir.exists() or not local_dir.is_dir():
                raise UploadError(f"Local directory not found: {local_dir}")

            _ = self.client.get_bucket(bucket_name)  # Validate bucket exists

            # Store bucket name for file uploads
            self.config.extra_config["current_bucket"] = bucket_name

            # Collect all files
            files_to_upload = []
            for file_path in local_dir.rglob("*"):
                if file_path.is_file():
                    files_to_upload.append(file_path)

            total_files = len(files_to_upload)
            uploaded_count = 0
            errors = []

            logger.info(f"Uploading {total_files} files to GCS bucket: {bucket_name}")

            # Upload each file
            for current, file_path in enumerate(files_to_upload, 1):
                try:
                    # Calculate remote path
                    relative_path = file_path.relative_to(local_dir)
                    remote_path = str(Path(prefix) / relative_path).replace("\\", "/")

                    # Get content type and cache control
                    content_type = self.get_content_type(file_path)
                    cache_control = self.get_cache_control(file_path)

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
                provider=ProviderType.GOOGLE_GCS,
                bucket_name=bucket_name,
                website_url=website_url,
                files_uploaded=uploaded_count,
                errors=errors,
                metadata={
                    "total_files": total_files,
                    "region": self.config.region,
                    "project_id": self.project_id
                }
            )

            logger.info(
                f"Directory upload completed: {uploaded_count}/{total_files} files",
                extra={"extra_fields": {"errors": len(errors)}}
            )

            return result

        except Exception as e:
            logger.error(f"Directory upload failed: {str(e)}")
            return DeploymentResult(
                success=False,
                provider=ProviderType.GOOGLE_GCS,
                bucket_name=bucket_name,
                website_url="",
                errors=[str(e)]
            )

    def configure_cdn(
        self,
        bucket_name: str,
        custom_domain: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Configure Cloud CDN for GCS bucket.

        Note: Cloud CDN requires a load balancer setup which is complex.
        This is a simplified implementation that returns the bucket URL.
        Full Cloud CDN setup requires additional configuration outside this scope.

        Args:
            bucket_name: Name of bucket
            custom_domain: Optional custom domain

        Returns:
            Tuple of (success, cdn_url)
        """
        try:
            self.require_authentication()

            # For now, return the standard GCS URL
            # Full Cloud CDN implementation would require:
            # 1. Create backend bucket
            # 2. Create URL map
            # 3. Create target HTTP/HTTPS proxy
            # 4. Create forwarding rule
            # 5. Configure SSL certificate
            # This is beyond the scope of basic deployment

            cdn_url = f"https://storage.googleapis.com/{bucket_name}"

            logger.warning(
                "Cloud CDN full configuration not implemented yet. "
                "Using standard GCS URL. For full CDN, configure manually via GCP Console."
            )

            return True, cdn_url

        except Exception as e:
            logger.error(f"CDN configuration failed: {str(e)}")
            raise CDNConfigurationError(f"CDN configuration failed: {str(e)}")

    def get_website_url(self, bucket_name: str) -> str:
        """
        Get website URL for GCS bucket.

        Args:
            bucket_name: Name of bucket

        Returns:
            Website URL
        """
        # GCS website hosting URL format
        return f"https://storage.googleapis.com/{bucket_name}/index.html"

    def list_buckets(self) -> List[str]:
        """
        List all GCS buckets in the project.

        Returns:
            List of bucket names
        """
        try:
            self.require_authentication()

            buckets = self.client.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]

            logger.info(f"Listed {len(bucket_names)} GCS buckets")
            return bucket_names

        except Exception as e:
            logger.error(f"Failed to list buckets: {str(e)}")
            return []

    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete GCS bucket.

        Args:
            bucket_name: Name of bucket to delete
            force: If True, delete all contents first

        Returns:
            True if successful
        """
        try:
            self.require_authentication()

            bucket = self.client.get_bucket(bucket_name)

            if force:
                # Delete all objects in bucket
                blobs = bucket.list_blobs()
                for blob in blobs:
                    blob.delete()
                logger.info(f"Deleted all objects from bucket: {bucket_name}")

            # Delete bucket
            bucket.delete()

            logger.info(f"GCS bucket deleted: {bucket_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete bucket: {str(e)}")
            return False
