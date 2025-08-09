"""
Filename: src/core/config_parser.py
Path: E:\\projects\\cloud-stack-generator\\src\\core\\config_parser.py
Description: Enhanced Configuration Parser with GBP and FAQ support

Version: 1.1.0
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""

    pass


@dataclass
class ClientConfig:
    """Client configuration data class"""

    business_name: str
    domain: str
    industry: str
    contact: Dict[str, Any]
    social_media: Optional[Dict[str, str]] = None
    branding: Optional[Dict[str, str]] = None
    google_business_profile: Optional[Dict[str, str]] = None
    google_maps: Optional[Dict[str, Any]] = None
    pages: Optional[list] = None
    offerings: Optional[list] = None
    faq: Optional[list] = None


class ConfigParser:
    """Parse and validate YAML configuration for website generation"""

    def __init__(self):
        self.required_fields = [
            "client.business_name",
            "client.domain",
            "client.industry",
            "client.contact.phone",
        ]

    def parse(self, config_dict: Dict[str, Any]) -> ClientConfig:
        """Parse configuration dictionary and return ClientConfig object"""
        try:
            # Basic validation
            if "client" not in config_dict:
                raise ConfigValidationError("Missing 'client' section in configuration")

            client_data = config_dict["client"]

            # Validate required fields
            self._validate_required_fields(client_data)

            # Create ClientConfig object
            return ClientConfig(
                business_name=client_data.get("business_name", ""),
                domain=client_data.get("domain", ""),
                industry=client_data.get("industry", ""),
                contact=client_data.get("contact", {}),
                social_media=client_data.get("social_media"),
                branding=client_data.get("branding"),
                google_business_profile=client_data.get("google_business_profile"),
                google_maps=client_data.get("google_maps"),
                pages=client_data.get("pages", []),
                offerings=client_data.get("offerings", []),
                faq=client_data.get("faq", []),
            )

        except KeyError as e:
            raise ConfigValidationError(f"Missing required configuration key: {e}")
        except Exception as e:
            raise ConfigValidationError(f"Configuration parsing error: {e}")

    def _validate_required_fields(self, client_data: Dict[str, Any]) -> None:
        """Validate required fields in client data"""
        errors = []

        if not client_data.get("business_name"):
            errors.append("Business name is required")

        if not client_data.get("domain"):
            errors.append("Domain is required")

        if not client_data.get("industry"):
            errors.append("Industry is required")

        contact = client_data.get("contact", {})
        if not contact.get("phone"):
            errors.append("Contact phone is required")

        if errors:
            raise ConfigValidationError("; ".join(errors))
