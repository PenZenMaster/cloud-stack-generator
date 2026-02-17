"""
Module/Script Name: Provider Factory
Path: src/core/deployment/providers/provider_factory.py

Description:
Factory pattern for instantiating cloud storage providers.
Supports provider registration and dynamic instantiation.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-19

Last Modified Date:
2025-11-19

Comments:
* v1.00 - Initial provider factory implementation
"""

from typing import Dict, Type, Optional, List
from .abstract_provider import (
    AbstractCloudProvider,
    ProviderType,
    ProviderConfig,
)

from ...utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


class ProviderFactory:
    """
    Factory for creating cloud storage provider instances.

    Design Pattern: Factory + Registry
    - Factory: Creates provider instances
    - Registry: Maintains mapping of provider types to classes

    Usage:
        factory = ProviderFactory()
        provider = factory.create_provider(ProviderType.GOOGLE_GCS, config)
    """

    def __init__(self):
        """Initialize provider factory with registry."""
        self._registry: Dict[ProviderType, Type[AbstractCloudProvider]] = {}
        self._register_default_providers()

        logger.info("Provider factory initialized")

    def _register_default_providers(self) -> None:
        """Register default provider implementations."""
        # Register GCS provider
        try:
            from .gcs_provider import GCSProvider
            self.register_provider(ProviderType.GOOGLE_GCS, GCSProvider)
            logger.debug("Registered GCS provider")
        except ImportError as e:
            logger.warning(f"GCS provider not available: {str(e)}")

        # Register AWS S3 provider
        try:
            from .aws_s3_provider import AWSS3Provider
            self.register_provider(ProviderType.AWS_S3, AWSS3Provider)
            logger.debug("Registered AWS S3 provider")
        except ImportError as e:
            logger.warning(f"AWS S3 provider not available: {str(e)}")

        # Register Wasabi provider
        try:
            from .wasabi_provider import WasabiProvider
            self.register_provider(ProviderType.WASABI, WasabiProvider)
            logger.debug("Registered Wasabi provider")
        except ImportError as e:
            logger.warning(f"Wasabi provider not available: {str(e)}")

        # Register Backblaze B2 provider
        try:
            from .backblaze_b2_provider import BackblazeB2Provider
            self.register_provider(ProviderType.BACKBLAZE_B2, BackblazeB2Provider)
            logger.debug("Registered Backblaze B2 provider")
        except ImportError as e:
            logger.warning(f"Backblaze B2 provider not available: {str(e)}")

    def register_provider(
        self,
        provider_type: ProviderType,
        provider_class: Type[AbstractCloudProvider]
    ) -> None:
        """
        Register a provider implementation.

        Args:
            provider_type: Type of provider
            provider_class: Provider class (must inherit from AbstractCloudProvider)

        Raises:
            TypeError: If provider_class doesn't inherit from AbstractCloudProvider
        """
        if not issubclass(provider_class, AbstractCloudProvider):
            raise TypeError(
                f"Provider class must inherit from AbstractCloudProvider. "
                f"Got: {provider_class}"
            )

        self._registry[provider_type] = provider_class

        logger.info(
            f"Registered provider: {provider_type.value}",
            extra={"extra_fields": {"class": provider_class.__name__}}
        )

    def unregister_provider(self, provider_type: ProviderType) -> bool:
        """
        Unregister a provider implementation.

        Args:
            provider_type: Type of provider to unregister

        Returns:
            True if unregistered, False if not found
        """
        if provider_type in self._registry:
            del self._registry[provider_type]
            logger.info(f"Unregistered provider: {provider_type.value}")
            return True
        return False

    def is_provider_available(self, provider_type: ProviderType) -> bool:
        """
        Check if a provider is available.

        Args:
            provider_type: Type of provider to check

        Returns:
            True if provider is registered and available
        """
        return provider_type in self._registry

    def get_available_providers(self) -> List[ProviderType]:
        """
        Get list of available provider types.

        Returns:
            List of provider types that are registered
        """
        return list(self._registry.keys())

    def create_provider(
        self,
        provider_type: ProviderType,
        config: ProviderConfig
    ) -> AbstractCloudProvider:
        """
        Create a provider instance.

        Args:
            provider_type: Type of provider to create
            config: Provider configuration

        Returns:
            Instance of requested provider

        Raises:
            ValueError: If provider type not registered
            TypeError: If config has wrong provider_type
        """
        # Validate provider type
        if provider_type not in self._registry:
            available = ", ".join(p.value for p in self._registry.keys())
            raise ValueError(
                f"Provider type '{provider_type.value}' not registered. "
                f"Available providers: {available}"
            )

        # Validate config matches requested provider
        if config.provider_type != provider_type:
            raise TypeError(
                f"Config provider_type ({config.provider_type.value}) "
                f"doesn't match requested provider ({provider_type.value})"
            )

        # Get provider class and instantiate
        provider_class = self._registry[provider_type]

        logger.info(
            f"Creating provider instance: {provider_type.value}",
            extra={"extra_fields": {"region": config.region}}
        )

        try:
            provider = provider_class(config)
            return provider
        except Exception as e:
            logger.error(
                f"Failed to create provider: {str(e)}",
                extra={"extra_fields": {"provider": provider_type.value}}
            )
            raise

    def create_provider_from_config_dict(
        self,
        config_dict: Dict
    ) -> AbstractCloudProvider:
        """
        Create provider from dictionary configuration.

        Convenience method for creating providers from YAML/JSON configs.

        Args:
            config_dict: Dictionary with provider configuration
                Expected keys:
                - provider: str (provider type)
                - credentials: dict
                - region: str
                - deployment_mode: str (optional)
                - custom_domain: str (optional)
                - provider_config: dict (optional)

        Returns:
            Provider instance

        Raises:
            ValueError: If required keys missing or invalid
        """
        # Extract required fields
        try:
            provider_type_str = config_dict["provider"]
            credentials = config_dict["credentials"]
            region = config_dict["region"]
        except KeyError as e:
            raise ValueError(f"Missing required config field: {e}")

        # Convert provider string to enum
        try:
            provider_type = ProviderType(provider_type_str)
        except ValueError:
            raise ValueError(
                f"Invalid provider type: {provider_type_str}. "
                f"Valid types: {[p.value for p in ProviderType]}"
            )

        # Extract optional fields
        from .abstract_provider import DeploymentMode

        deployment_mode_str = config_dict.get("deployment_mode", "storage_only")
        try:
            deployment_mode = DeploymentMode(deployment_mode_str)
        except ValueError:
            deployment_mode = DeploymentMode.STORAGE_ONLY

        custom_domain = config_dict.get("custom_domain")
        extra_config = config_dict.get("provider_config", {})

        # Create config object
        config = ProviderConfig(
            provider_type=provider_type,
            credentials=credentials,
            region=region,
            deployment_mode=deployment_mode,
            custom_domain=custom_domain,
            extra_config=extra_config
        )

        # Create and return provider
        return self.create_provider(provider_type, config)

    def get_provider_info(self, provider_type: ProviderType) -> Dict:
        """
        Get information about a provider.

        Args:
            provider_type: Type of provider

        Returns:
            Dictionary with provider information
        """
        if provider_type not in self._registry:
            return {
                "available": False,
                "error": "Provider not registered"
            }

        provider_class = self._registry[provider_type]

        return {
            "available": True,
            "provider_type": provider_type.value,
            "class_name": provider_class.__name__,
            "module": provider_class.__module__,
        }


# Global factory instance
_global_factory: Optional[ProviderFactory] = None


def get_provider_factory() -> ProviderFactory:
    """
    Get the global provider factory instance.

    Singleton pattern - creates factory on first call.

    Returns:
        Global ProviderFactory instance
    """
    global _global_factory

    if _global_factory is None:
        _global_factory = ProviderFactory()

    return _global_factory


def create_provider(
    provider_type: ProviderType,
    config: ProviderConfig
) -> AbstractCloudProvider:
    """
    Convenience function to create a provider using global factory.

    Args:
        provider_type: Type of provider
        config: Provider configuration

    Returns:
        Provider instance
    """
    factory = get_provider_factory()
    return factory.create_provider(provider_type, config)


def create_provider_from_dict(config_dict: Dict) -> AbstractCloudProvider:
    """
    Convenience function to create provider from dictionary.

    Args:
        config_dict: Dictionary configuration

    Returns:
        Provider instance
    """
    factory = get_provider_factory()
    return factory.create_provider_from_config_dict(config_dict)
