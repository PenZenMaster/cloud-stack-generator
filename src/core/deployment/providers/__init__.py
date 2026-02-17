"""
Module/Script Name: Cloud Provider Package
Path: src/core/deployment/providers/__init__.py

Description:
Cloud storage provider implementations for multi-cloud deployment support.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-19

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial provider package with abstract interface
* v1.01 - Added GCS provider implementation
* v1.02 - Added S3-compatible providers (AWS S3, Wasabi, Backblaze B2)
"""

from .abstract_provider import (
    AbstractCloudProvider,
    ProviderType,
    DeploymentMode,
    DeploymentResult,
    ProviderConfig,
    CloudProviderError,
    AuthenticationError,
    BucketCreationError,
    UploadError,
    CDNConfigurationError,
    PermissionError,
)

# Import provider implementations
__all_providers = []

try:
    from .gcs_provider import GCSProvider  # noqa: F401
    __all_providers.append("GCSProvider")
except ImportError:
    pass

try:
    from .s3_compatible_provider import S3CompatibleProvider  # noqa: F401
    __all_providers.append("S3CompatibleProvider")
except ImportError:
    pass

try:
    from .aws_s3_provider import AWSS3Provider  # noqa: F401
    __all_providers.append("AWSS3Provider")
except ImportError:
    pass

try:
    from .wasabi_provider import WasabiProvider  # noqa: F401
    __all_providers.append("WasabiProvider")
except ImportError:
    pass

try:
    from .backblaze_b2_provider import BackblazeB2Provider  # noqa: F401
    __all_providers.append("BackblazeB2Provider")
except ImportError:
    pass

# Import provider factory
from .provider_factory import (
    ProviderFactory,
    get_provider_factory,
    create_provider,
    create_provider_from_dict,
)

__all__ = [
    "AbstractCloudProvider",
    "ProviderType",
    "DeploymentMode",
    "DeploymentResult",
    "ProviderConfig",
    "CloudProviderError",
    "AuthenticationError",
    "BucketCreationError",
    "UploadError",
    "CDNConfigurationError",
    "PermissionError",
    "ProviderFactory",
    "get_provider_factory",
    "create_provider",
    "create_provider_from_dict",
] + __all_providers
