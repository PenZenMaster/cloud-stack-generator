# Multi-Cloud Storage Provider Architecture

**Version:** 1.0
**Status:** Design & Implementation
**Created:** November 19, 2025
**Author:** Cloud Stack Generator Team

---

## Table of Contents

1. [Overview](#overview)
2. [Design Goals](#design-goals)
3. [Architecture](#architecture)
4. [Abstract Interface](#abstract-interface)
5. [Provider Implementations](#provider-implementations)
6. [Configuration Schema](#configuration-schema)
7. [Authentication](#authentication)
8. [Deployment Workflow](#deployment-workflow)
9. [Error Handling](#error-handling)
10. [Testing Strategy](#testing-strategy)
11. [Migration Path](#migration-path)

---

## Overview

This document describes the architecture for a **provider-agnostic cloud storage deployment system** that supports multiple cloud storage providers (AWS S3, Google Cloud Storage, Azure Blob Storage, etc.) through a unified abstract interface.

### Current State

- **Implemented:** AWS S3 deployment with CloudFront integration
- **Target:** Extensible multi-cloud support with pluggable providers

### Design Philosophy

- **Abstract Interface:** Common contract for all cloud providers
- **Provider Isolation:** Provider-specific logic encapsulated in dedicated modules
- **Backward Compatibility:** Existing AWS deployments continue to work
- **Configuration-Driven:** Provider selection via configuration files
- **Fail-Safe:** Graceful degradation if provider unavailable

---

## Design Goals

### Primary Goals

1. **Abstraction:** Common interface for all cloud storage providers
2. **Extensibility:** Easy to add new providers without modifying core code
3. **Consistency:** Uniform deployment experience across providers
4. **Maintainability:** Clear separation of concerns
5. **Testability:** Mock providers for testing

### Secondary Goals

1. **Multi-Provider Deployment:** Deploy same site to multiple clouds simultaneously
2. **Provider Migration:** Easy migration between providers
3. **Cost Optimization:** Choose providers based on pricing
4. **Redundancy:** Deploy to multiple providers for failover

---

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Deployment Manager                        │
│                  (Orchestration Layer)                       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Provider Factory                            │
│              (Registry & Instantiation)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              AbstractCloudProvider (ABC)                     │
│           (Interface/Contract Definition)                    │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ S3Provider   │ │ GCSProvider  │ │ AzureProvider│
    │ (AWS S3)     │ │ (Google)     │ │ (Microsoft)  │
    └──────────────┘ └──────────────┘ └──────────────┘
            │               │               │
            ▼               ▼               ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   boto3      │ │ google-cloud │ │ azure-storage│
    │   (AWS SDK)  │ │   -storage   │ │     -blob    │
    └──────────────┘ └──────────────┘ └──────────────┘
```

### Component Layers

1. **Deployment Manager** - Orchestrates multi-provider deployments
2. **Provider Factory** - Instantiates provider implementations
3. **Abstract Interface** - Defines provider contract
4. **Provider Implementations** - Cloud-specific logic
5. **SDK Layer** - Cloud provider SDKs

---

## Abstract Interface

### AbstractCloudProvider Base Class

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple, Callable
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


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
    errors: List[str] = None
    metadata: Dict[str, any] = None


@dataclass
class ProviderConfig:
    """Provider-specific configuration"""
    provider_type: ProviderType
    credentials: Dict[str, str]
    region: str
    deployment_mode: DeploymentMode
    custom_domain: Optional[str] = None
    extra_config: Dict[str, any] = None


class AbstractCloudProvider(ABC):
    """
    Abstract base class for cloud storage providers.

    All cloud provider implementations must inherit from this class
    and implement all abstract methods.
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize provider with configuration.

        Args:
            config: Provider-specific configuration
        """
        self.config = config
        self.provider_type = config.provider_type

    # Core Operations

    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with cloud provider.

        Returns:
            True if authentication successful, False otherwise
        """
        pass

    @abstractmethod
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test connection to cloud provider.

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
        """
        pass

    @abstractmethod
    def configure_website_hosting(self, bucket_name: str) -> bool:
        """
        Configure bucket for static website hosting.

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
        """
        pass

    @abstractmethod
    def upload_directory(
        self,
        local_dir: Path,
        bucket_name: str,
        prefix: str = "",
        progress_callback: Optional[Callable] = None
    ) -> DeploymentResult:
        """
        Upload entire directory to storage.

        Args:
            local_dir: Path to local directory
            bucket_name: Name of bucket
            prefix: Optional prefix for remote paths
            progress_callback: Optional progress callback

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

        Args:
            bucket_name: Name of bucket
            custom_domain: Optional custom domain

        Returns:
            Tuple of (success, cdn_url)
        """
        pass

    @abstractmethod
    def get_website_url(self, bucket_name: str) -> str:
        """
        Get website URL for bucket.

        Args:
            bucket_name: Name of bucket

        Returns:
            Website URL
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
        import mimetypes
        content_type, _ = mimetypes.guess_type(str(file_path))
        return content_type or 'application/octet-stream'

    def get_cache_control(self, file_path: Path) -> str:
        """
        Determine cache control header for file.

        Args:
            file_path: Path to file

        Returns:
            Cache-Control header value
        """
        # Static assets get long cache
        if file_path.suffix in ['.css', '.js', '.jpg', '.png', '.gif', '.svg', '.woff', '.woff2']:
            return 'public, max-age=31536000, immutable'
        # HTML gets short cache
        elif file_path.suffix in ['.html', '.htm']:
            return 'public, max-age=3600, must-revalidate'
        # Default
        else:
            return 'public, max-age=86400'

    def validate_bucket_name(self, bucket_name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate bucket name according to common cloud provider rules.

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

        import re
        if not re.match(r'^[a-z0-9][a-z0-9.-]*[a-z0-9]$', bucket_name):
            return False, "Bucket name can only contain lowercase letters, numbers, dots, and hyphens"

        return True, None
```

---

## Provider Implementations

### 1. AWS S3 Provider

**File:** `src/core/deployment/providers/aws_s3_provider.py`

**Features:**
- S3 bucket creation and configuration
- Static website hosting
- CloudFront CDN integration (Mode A & Mode B)
- OAC (Origin Access Control) support
- Multi-region deployment

**Status:** ✅ **Implemented** (refactor existing `s3_deployer.py`)

### 2. Google Cloud Storage Provider

**File:** `src/core/deployment/providers/gcs_provider.py`

**Features:**
- GCS bucket creation and configuration
- Static website hosting
- Cloud CDN integration
- IAM and bucket policies
- Regional deployment options

**Status:** 🚧 **In Development** (NEW)

**GCS-Specific Configuration:**
```python
{
    "provider_type": "google_gcs",
    "credentials": {
        "service_account_json": "/path/to/service-account.json",
        # OR
        "project_id": "my-project",
        "client_email": "service@project.iam.gserviceaccount.com",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
    },
    "region": "us-central1",
    "deployment_mode": "cdn_integrated",
    "extra_config": {
        "storage_class": "STANDARD",  # or NEARLINE, COLDLINE, ARCHIVE
        "enable_versioning": false,
        "lifecycle_rules": []
    }
}
```

### 3. Azure Blob Storage Provider (Future)

**File:** `src/core/deployment/providers/azure_blob_provider.py`

**Status:** 📋 **Planned**

### 4. Backblaze B2 Provider (Future)

**File:** `src/core/deployment/providers/b2_provider.py`

**Status:** 📋 **Planned**

---

## Configuration Schema

### Unified Configuration Format

```yaml
deployment:
  # Provider selection
  provider: google_gcs  # aws_s3, google_gcs, azure_blob, etc.

  # Provider-specific credentials (varies by provider)
  credentials:
    # For GCS:
    service_account_json: /path/to/credentials.json
    project_id: my-gcp-project

    # For AWS:
    # profile: my-aws-profile
    # access_key_id: AKIAIOSFODNN7EXAMPLE
    # secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

  # Common settings
  region: us-central1
  bucket_name: my-website-bucket
  deployment_mode: cdn_integrated  # storage_only or cdn_integrated

  # Optional settings
  custom_domain: www.example.com
  enable_https: true

  # Provider-specific extra config
  provider_config:
    storage_class: STANDARD
    enable_versioning: false
```

---

## Authentication

### Authentication Strategies by Provider

#### AWS S3
```python
# Strategy 1: Named Profile
credentials = {
    "profile": "my-aws-profile"
}

# Strategy 2: Access Keys
credentials = {
    "access_key_id": "AKIAIOSFODNN7EXAMPLE",
    "secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

# Strategy 3: Assume Role
credentials = {
    "role_arn": "arn:aws:iam::123456789012:role/MyRole"
}
```

#### Google Cloud Storage
```python
# Strategy 1: Service Account JSON File
credentials = {
    "service_account_json": "/path/to/service-account.json"
}

# Strategy 2: Service Account Key Components
credentials = {
    "project_id": "my-project",
    "client_email": "service@project.iam.gserviceaccount.com",
    "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
}

# Strategy 3: Application Default Credentials (ADC)
credentials = {
    "use_adc": true
}
```

---

## Deployment Workflow

### Deployment Process

```
1. Configuration Loading
   ├─ Read config file
   ├─ Parse provider type
   └─ Extract credentials

2. Provider Initialization
   ├─ Factory creates provider instance
   ├─ Inject configuration
   └─ Authenticate

3. Pre-Deployment Validation
   ├─ Test connection
   ├─ Validate bucket name
   ├─ Check permissions
   └─ Validate deployment mode

4. Bucket Setup
   ├─ Create bucket (if not exists)
   ├─ Configure website hosting
   ├─ Set CORS policies
   └─ Set access policies

5. Content Upload
   ├─ Generate file list
   ├─ Calculate content types
   ├─ Set cache headers
   ├─ Upload files with progress
   └─ Verify uploads

6. CDN Configuration (if enabled)
   ├─ Create CDN distribution
   ├─ Configure SSL/TLS
   ├─ Set custom domain
   └─ Wait for propagation

7. Post-Deployment
   ├─ Generate deployment report
   ├─ Return website URLs
   └─ Log deployment details
```

### Multi-Provider Deployment

```python
# Deploy to multiple providers simultaneously
deployment_manager = DeploymentManager()

results = deployment_manager.deploy_to_providers(
    local_dir="/path/to/website",
    providers=["aws_s3", "google_gcs"],
    configs={
        "aws_s3": aws_config,
        "google_gcs": gcs_config
    }
)

for provider, result in results.items():
    if result.success:
        print(f"{provider}: {result.website_url}")
```

---

## Error Handling

### Error Hierarchy

```python
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
```

### Error Handling Strategy

- **Fail Fast:** Authentication errors stop deployment immediately
- **Retry Logic:** Network errors retry with exponential backoff
- **Partial Success:** Track successful uploads, resume on failure
- **Detailed Logging:** All errors logged with context
- **User Feedback:** Clear error messages in UI

---

## Testing Strategy

### Unit Tests

```python
# Mock provider for testing
class MockCloudProvider(AbstractCloudProvider):
    def __init__(self, config):
        super().__init__(config)
        self.uploaded_files = []

    def authenticate(self):
        return True

    def upload_file(self, local_path, remote_path, ...):
        self.uploaded_files.append((local_path, remote_path))
        return True
```

### Integration Tests

- **AWS S3:** Test with LocalStack or MinIO
- **GCS:** Test with GCS emulator
- **Real Provider Tests:** Marked with `@pytest.mark.integration`

### Test Coverage Goals

- Abstract Interface: 100%
- Provider Implementations: 80%+
- Deployment Manager: 90%+

---

## Migration Path

### Phase 1: Refactoring (Current)
1. Extract abstract interface
2. Refactor existing S3 deployer
3. Create provider factory
4. Update tests

### Phase 2: GCS Implementation
1. Implement GCS provider
2. Add GCS authentication
3. Create GCS unit tests
4. Update UI for provider selection

### Phase 3: Multi-Provider Support
1. Implement deployment manager
2. Support simultaneous deployment
3. Add provider comparison tools
4. Create migration utilities

---

## Implementation Checklist

### Core Infrastructure
- [ ] Create `AbstractCloudProvider` base class
- [ ] Create `ProviderFactory` for instantiation
- [ ] Create `DeploymentManager` for orchestration
- [ ] Define `ProviderConfig` and `DeploymentResult` dataclasses
- [ ] Create provider exception hierarchy

### AWS S3 Refactoring
- [ ] Refactor `s3_deployer.py` to implement `AbstractCloudProvider`
- [ ] Move S3-specific logic to `aws_s3_provider.py`
- [ ] Update existing tests
- [ ] Ensure backward compatibility

### GCS Implementation
- [ ] Create `gcs_provider.py`
- [ ] Implement all abstract methods
- [ ] Add GCS authentication handling
- [ ] Create GCS unit tests
- [ ] Create GCS integration tests
- [ ] Add GCS documentation

### UI Updates
- [ ] Add provider selection dropdown
- [ ] Create provider-specific credential forms
- [ ] Update deployment tab for multi-provider
- [ ] Add provider status indicators

### Documentation
- [ ] Update deployment documentation
- [ ] Create GCS setup guide
- [ ] Add provider comparison guide
- [ ] Update configuration examples

---

## Appendix

### Provider Comparison Matrix

| Feature | AWS S3 | Google GCS | Azure Blob | Backblaze B2 |
|---------|--------|------------|------------|--------------|
| Static Hosting | ✅ Yes | ✅ Yes | ✅ Yes | ⚠️ Limited |
| CDN Integration | CloudFront | Cloud CDN | Azure CDN | CloudFlare |
| Custom Domains | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| SSL/TLS | ✅ Auto | ✅ Auto | ✅ Auto | ✅ Auto |
| Min File Size | None | None | None | None |
| Max File Size | 5 TB | 5 TB | 4.77 TB | 10 TB |
| Pricing Model | Pay per use | Pay per use | Pay per use | Fixed tiers |
| Free Tier | 5 GB/month | 5 GB/month | 5 GB/month | 10 GB/month |

### Reference Documentation

- **AWS S3:** https://docs.aws.amazon.com/s3/
- **Google Cloud Storage:** https://cloud.google.com/storage/docs
- **Azure Blob Storage:** https://docs.microsoft.com/en-us/azure/storage/blobs/
- **Backblaze B2:** https://www.backblaze.com/b2/docs/

---

## Version History

- **v1.0** (2025-11-19) - Initial design document
  - Abstract interface specification
  - Provider implementation guidelines
  - GCS as first target provider
  - Multi-cloud deployment strategy
