"""
Module/Script Name: Backblaze B2 Provider
Path: src/core/deployment/providers/backblaze_b2_provider.py

Description:
Backblaze B2 Cloud Storage provider implementation.
S3-compatible storage with region-specific endpoints.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial Backblaze B2 provider implementation
"""

from typing import Optional

from .s3_compatible_provider import S3CompatibleProvider
from .abstract_provider import (
    ProviderType,
    ProviderConfig,
)

from ...utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


# Backblaze B2 region endpoint mapping
# Note: B2 uses S3-compatible API since version 4
BACKBLAZE_B2_ENDPOINTS = {
    "us-west-001": "https://s3.us-west-001.backblazeb2.com",
    "us-west-002": "https://s3.us-west-002.backblazeb2.com",
    "us-west-004": "https://s3.us-west-004.backblazeb2.com",
    "eu-central-003": "https://s3.eu-central-003.backblazeb2.com",
}


class BackblazeB2Provider(S3CompatibleProvider):
    """
    Backblaze B2 Cloud Storage provider.

    Features:
    - S3-compatible API (v4)
    - Low-cost storage
    - Regional endpoints
    - Static website hosting
    - No minimum storage duration

    Supported Regions:
    - us-west-001 (US West)
    - us-west-002 (US West)
    - us-west-004 (US West)
    - eu-central-003 (EU Central)

    Note: Backblaze B2 requires application keys:
    - keyID as aws_access_key_id
    - applicationKey as aws_secret_access_key
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize Backblaze B2 provider.

        Args:
            config: Provider configuration
        """
        # Override provider type to BACKBLAZE_B2
        config.provider_type = ProviderType.BACKBLAZE_B2
        super().__init__(config)

        # Validate region
        if config.region not in BACKBLAZE_B2_ENDPOINTS:
            logger.warning(
                f"Unknown Backblaze B2 region: {config.region}. Using us-west-001 endpoint.",
                extra={"extra_fields": {
                    "requested_region": config.region,
                    "available_regions": list(BACKBLAZE_B2_ENDPOINTS.keys())
                }}
            )

        logger.info(
            "Backblaze B2 provider initialized",
            extra={"extra_fields": {
                "region": config.region,
                "endpoint": self._get_endpoint_url()
            }}
        )

    def _get_endpoint_url(self) -> Optional[str]:
        """
        Get Backblaze B2 endpoint URL for configured region.

        Returns:
            Backblaze B2 endpoint URL
        """
        region = self.config.region

        # Return region-specific endpoint or default to us-west-001
        endpoint = BACKBLAZE_B2_ENDPOINTS.get(region, BACKBLAZE_B2_ENDPOINTS["us-west-001"])

        return endpoint

    def get_website_url(self, bucket_name: str) -> str:
        """
        Get website URL for Backblaze B2 bucket.

        Note: Backblaze B2 website hosting uses a different URL format.
        The bucket must be configured for public access and website hosting.

        Args:
            bucket_name: Name of bucket

        Returns:
            Backblaze B2 website URL
        """
        region = self.config.region

        # Backblaze B2 website endpoint format
        # Format: https://f<bucket-id>.<region>.backblazeb2.com/file/<bucket-name>/index.html
        # For simplicity, return the S3-compatible URL
        return f"https://s3.{region}.backblazeb2.com/{bucket_name}/index.html"
