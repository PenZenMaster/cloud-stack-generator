"""
Module/Script Name: Abstract Cloud Provider
Path: src/core/deployment/providers/abstract_provider.py

Description:
Abstract base class defining the interface for all cloud storage providers.
Implements provider-agnostic deployment contract.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-19

Last Modified Date:
2025-11-19

Comments:
* v1.00 - Initial abstract provider interface
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Callable, Any
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import mimetypes
import re

from ...utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


class ProviderType(Enum):
    """Supported cloud storage providers"""
    AWS_S3 = "aws_s3"
    GOOGLE_GCS = "google_gcs"
    AZURE_BLOB = "azure_blob"
    BACKBLAZE_B2 = "backblaze_b2"
    WASABI = "wasabi"
    DIGITALOCEAN_SPACES = "digitalocean_spaces"


class DeploymentMode(Enum):
    """Deployment configuration modes"""
    STORAGE_ONLY = "storage_only"      # Just storage bucket
    CDN_INTEGRATED = "cdn_integrated"  # Storage + CDN


@dataclass
class DeploymentResult:
    """Result of a deployment operation"""
    success: bool
    provider: ProviderType
    bucket_name: str
    website_url: str
    cdn_url: Optional[str] = None
    files_uploaded: int = 0
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __str__(self) -> str:
        """String representation of deployment result"""
        status = "SUCCESS" if self.success else "FAILED"
        result = [
            f"Deployment Result: {status}",
            f"Provider: {self.provider.value}",
            f"Bucket: {self.bucket_name}",
            f"Website URL: {self.website_url}",
        ]

        if self.cdn_url:
            result.append(f"CDN URL: {self.cdn_url}")

        if self.success:
            result.append(f"Files Uploaded: {self.files_uploaded}")
        elif self.errors:
            result.append(f"Errors: {len(self.errors)}")
            for error in self.errors[:3]:  # Show first 3 errors
                result.append(f"  - {error}")

        return "\n".join(result)


@dataclass
class ProviderConfig:
    """Provider-specific configuration"""
    provider_type: ProviderType
    credentials: Dict[str, str]
    region: str
    deployment_mode: DeploymentMode = DeploymentMode.STORAGE_ONLY
    custom_domain: Optional[str] = None
    extra_config: Dict[str, Any] = field(default_factory=dict)


# Exception Hierarchy

class CloudProviderError(Exception):
    """Base exception for cloud provider errors"""
    pass


class AuthenticationError(CloudProviderError):
    """Authentication failed"""
    pass


class BucketCreationError(CloudProviderError):
    """Failed to create bucket"""
    pass


class UploadError(CloudProviderError):
    """File upload failed"""
    pass


class CDNConfigurationError(CloudProviderError):
    """CDN configuration failed"""
    pass


class PermissionError(CloudProviderError):
    """Insufficient permissions"""
    pass


class AbstractCloudProvider(ABC):
    """
    Abstract base class for cloud storage providers.

    All cloud provider implementations must inherit from this class
    and implement all abstract methods.

    Design Pattern: Template Method + Strategy
    - Template: Common workflow (authenticate, upload, configure)
    - Strategy: Provider-specific implementations
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize provider with configuration.

        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self.provider_type = config.provider_type
        self._authenticated = False

        logger.info(
            f"Initializing {self.provider_type.value} provider",
            extra={"extra_fields": {"region": config.region}}
        )

    # Core Operations (Abstract Methods)

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with cloud provider.

        This method should:
        1. Validate credentials
        2. Establish connection
        3. Set self._authenticated flag

        Returns:
            True if authentication successful, False otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to cloud provider.

        This method should verify:
        1. Authentication is valid
        2. Permissions are sufficient
        3. Service is accessible

        Returns:
            Tuple of (success, message)
        """
        pass

    @abstractmethod
    def create_bucket(self, bucket_name: str) -> bool:
        """
        Create storage bucket/container.

        Args:
            bucket_name: Name of bucket to create

        Returns:
            True if successful, False otherwise

        Raises:
            BucketCreationError: If bucket creation fails
        """
        pass

    @abstractmethod
    def configure_website_hosting(self, bucket_name: str) -> bool:
        """
        Configure bucket for static website hosting.

        This method should:
        1. Enable website hosting
        2. Set index document (index.html)
        3. Set error document (404.html)
        4. Configure public access (if needed)

        Args:
            bucket_name: Name of bucket to configure

        Returns:
            True if successful, False otherwise
        """
        pass

    @abstractmethod
    def upload_file(
        self,
        local_path: Path,
        remote_path: str,
        content_type: str,
        cache_control: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    ) -> bool:
        """
        Upload a single file to storage.

        Args:
            local_path: Path to local file
            remote_path: Remote path in bucket
            content_type: MIME type of file
            cache_control: Cache-Control header value
            metadata: Additional metadata

        Returns:
            True if successful, False otherwise

        Raises:
            UploadError: If upload fails
        """
        pass

    @abstractmethod
    def upload_directory(
        self,
        local_dir: Path,
        bucket_name: str,
        prefix: str = "",
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> DeploymentResult:
        """
        Upload entire directory to storage.

        Args:
            local_dir: Path to local directory
            bucket_name: Name of bucket
            prefix: Optional prefix for remote paths
            progress_callback: Optional progress callback (current, total, filename)

        Returns:
            DeploymentResult with upload details
        """
        pass

    @abstractmethod
    def configure_cdn(
        self,
        bucket_name: str,
        custom_domain: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Configure CDN for bucket.

        This method should:
        1. Create CDN distribution
        2. Configure SSL/TLS
        3. Set custom domain (if provided)
        4. Return CDN URL

        Args:
            bucket_name: Name of bucket
            custom_domain: Optional custom domain

        Returns:
            Tuple of (success, cdn_url)

        Raises:
            CDNConfigurationError: If CDN configuration fails
        """
        pass

    @abstractmethod
    def get_website_url(self, bucket_name: str) -> str:
        """
        Get website URL for bucket.

        Args:
            bucket_name: Name of bucket

        Returns:
            Website URL (e.g., http://bucket-name.s3-website-region.amazonaws.com)
        """
        pass

    @abstractmethod
    def list_buckets(self) -> List[str]:
        """
        List all buckets accessible with current credentials.

        Returns:
            List of bucket names
        """
        pass

    @abstractmethod
    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """
        Delete bucket and optionally all contents.

        Args:
            bucket_name: Name of bucket to delete
            force: If True, delete all contents first

        Returns:
            True if successful, False otherwise
        """
        pass

    # Helper Methods (with default implementations)

    def get_content_type(self, file_path: Path) -> str:
        """
        Determine MIME type for file.

        Args:
            file_path: Path to file

        Returns:
            MIME type string
        """
        content_type, _ = mimetypes.guess_type(str(file_path))
        return content_type or 'application/octet-stream'

    def get_cache_control(self, file_path: Path) -> str:
        """
        Determine cache control header for file.

        Strategy:
        - Static assets (CSS, JS, images, fonts): Long cache (1 year, immutable)
        - HTML files: Short cache (1 hour, must revalidate)
        - Other files: Medium cache (1 day)

        Args:
            file_path: Path to file

        Returns:
            Cache-Control header value
        """
        # Static assets get long cache
        if file_path.suffix in ['.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.svg', '.woff', '.woff2', '.ttf', '.eot', '.ico']:
            return 'public, max-age=31536000, immutable'
        # HTML gets short cache
        elif file_path.suffix in ['.html', '.htm']:
            return 'public, max-age=3600, must-revalidate'
        # Default - medium cache
        else:
            return 'public, max-age=86400'

    def validate_bucket_name(self, bucket_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate bucket name according to common cloud provider rules.

        Rules:
        - Must be between 3 and 63 characters
        - Can only contain lowercase letters, numbers, dots, and hyphens
        - Must start and end with alphanumeric character
        - Cannot contain consecutive dots
        - Cannot be formatted as IP address

        Args:
            bucket_name: Name to validate

        Returns:
            Tuple of (valid, error_message)
        """
        if not bucket_name:
            return False, "Bucket name cannot be empty"

        if len(bucket_name) < 3 or len(bucket_name) > 63:
            return False, "Bucket name must be between 3 and 63 characters"

        if not bucket_name[0].isalnum() or not bucket_name[-1].isalnum():
            return False, "Bucket name must start and end with alphanumeric character"

        if not re.match(r'^[a-z0-9][a-z0-9.-]*[a-z0-9]$', bucket_name):
            return False, "Bucket name can only contain lowercase letters, numbers, dots, and hyphens"

        if '..' in bucket_name:
            return False, "Bucket name cannot contain consecutive dots"

        # Check if formatted as IP address
        if re.match(r'^\d+\.\d+\.\d+\.\d+$', bucket_name):
            return False, "Bucket name cannot be formatted as IP address"

        return True, None

    def is_authenticated(self) -> bool:
        """
        Check if provider is authenticated.

        Returns:
            True if authenticated, False otherwise
        """
        return self._authenticated

    def require_authentication(self) -> None:
        """
        Raise exception if not authenticated.

        Raises:
            AuthenticationError: If not authenticated
        """
        if not self._authenticated:
            raise AuthenticationError(
                f"{self.provider_type.value} provider not authenticated. "
                "Call authenticate() first."
            )

    def get_provider_name(self) -> str:
        """
        Get human-readable provider name.

        Returns:
            Provider name (e.g., "AWS S3", "Google Cloud Storage")
        """
        name_map = {
            ProviderType.AWS_S3: "AWS S3",
            ProviderType.GOOGLE_GCS: "Google Cloud Storage",
            ProviderType.AZURE_BLOB: "Azure Blob Storage",
            ProviderType.BACKBLAZE_B2: "Backblaze B2",
            ProviderType.WASABI: "Wasabi Hot Cloud Storage",
            ProviderType.DIGITALOCEAN_SPACES: "DigitalOcean Spaces",
        }
        return name_map.get(self.provider_type, self.provider_type.value)
