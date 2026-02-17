"""
Module/Script Name: Wasabi Provider
Path: src/core/deployment/providers/wasabi_provider.py

Description:
Wasabi Hot Cloud Storage provider implementation.
S3-compatible storage with region-specific endpoints.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial Wasabi provider implementation
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


# Wasabi region endpoint mapping
WASABI_ENDPOINTS = {
    "us-east-1": "https://s3.wasabisys.com",
    "us-east-2": "https://s3.us-east-2.wasabisys.com",
    "us-west-1": "https://s3.us-west-1.wasabisys.com",
    "eu-central-1": "https://s3.eu-central-1.wasabisys.com",
    "eu-west-1": "https://s3.eu-west-1.wasabisys.com",
    "eu-west-2": "https://s3.eu-west-2.wasabisys.com",
    "ap-northeast-1": "https://s3.ap-northeast-1.wasabisys.com",
    "ap-northeast-2": "https://s3.ap-northeast-2.wasabisys.com",
}


class WasabiProvider(S3CompatibleProvider):
    """
    Wasabi Hot Cloud Storage provider.

    Features:
    - S3-compatible API
    - No egress fees
    - Regional endpoints
    - Static website hosting
    - Lower cost than AWS S3

    Supported Regions:
    - us-east-1 (Virginia)
    - us-east-2 (N. Virginia)
    - us-west-1 (Oregon)
    - eu-central-1 (Amsterdam)
    - eu-west-1 (London)
    - eu-west-2 (Paris)
    - ap-northeast-1 (Tokyo)
    - ap-northeast-2 (Osaka)
    """

    def __init__(self, config: ProviderConfig):
        """
        Initialize Wasabi provider.

        Args:
            config: Provider configuration
        """
        # Override provider type to WASABI
        config.provider_type = ProviderType.WASABI
        super().__init__(config)

        # Validate region
        if config.region not in WASABI_ENDPOINTS:
            logger.warning(
                f"Unknown Wasabi region: {config.region}. Using us-east-1 endpoint.",
                extra={"extra_fields": {
                    "requested_region": config.region,
                    "available_regions": list(WASABI_ENDPOINTS.keys())
                }}
            )

        logger.info(
            "Wasabi provider initialized",
            extra={"extra_fields": {
                "region": config.region,
                "endpoint": self._get_endpoint_url()
            }}
        )

    def _get_endpoint_url(self) -> Optional[str]:
        """
        Get Wasabi endpoint URL for configured region.

        Returns:
            Wasabi endpoint URL
        """
        region = self.config.region

        # Return region-specific endpoint or default to us-east-1
        endpoint = WASABI_ENDPOINTS.get(region, WASABI_ENDPOINTS["us-east-1"])

        return endpoint

    def get_website_url(self, bucket_name: str) -> str:
        """
        Get website URL for Wasabi bucket.

        Args:
            bucket_name: Name of bucket

        Returns:
            Wasabi website URL
        """
        region = self.config.region

        # Wasabi website endpoint format
        if region == "us-east-1":
            return f"http://{bucket_name}.s3-website-us-east-1.wasabisys.com"
        else:
            return f"http://{bucket_name}.s3-website.{region}.wasabisys.com"
