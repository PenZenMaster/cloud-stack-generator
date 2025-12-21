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
2025-11-19

Comments:
* v1.00 - Initial provider package with abstract interface
* v1.01 - Added GCS provider implementation
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
try:
    from .gcs_provider import GCSProvider  # noqa: F401
    __all_providers = ["GCSProvider"]
except ImportError:
    __all_providers = []

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
