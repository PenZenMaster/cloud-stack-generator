"""
Configuration parsing and serialization

This module handles YAML configuration parsing and generation, bridging between
raw YAML data and our typed configuration models.

Version: 1.0.0
Author: Cloud Stack Generator Team
"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path
from .models import (
    ClientConfig,
    BusinessConfig,
    ContactConfig,
    BrandingConfig,
    ProductConfig,
    ServiceConfig,
    FAQItem,
    SocialMediaConfig,
    GoogleMapsConfig,
    PageConfig,
)


class ConfigParsingError(Exception):
    """Exception raised when configuration parsing fails"""

    pass


class ConfigParser:
    """Handles YAML configuration parsing and generation"""

    def __init__(self):
        self.current_config: Optional[ClientConfig] = None

    def parse_yaml_file(self, file_path: str) -> ClientConfig:
        """
        Parse YAML file into ClientConfig object

        Args:
            file_path: Path to the YAML configuration file

        Returns:
            ClientConfig object with parsed data

        Raises:
            ConfigParsingError: If parsing fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)
            return self.parse_yaml_dict(yaml_data)
        except FileNotFoundError:
            raise ConfigParsingError(f"Configuration file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ConfigParsingError(f"Invalid YAML format: {e}")
        except Exception as e:
            raise ConfigParsingError(f"Error parsing YAML file: {e}")

    def parse_yaml_dict(self, yaml_data: Dict[str, Any]) -> ClientConfig:
        """
        Parse YAML dictionary into ClientConfig object

        Args:
            yaml_data: Dictionary containing YAML configuration data

        Returns:
            ClientConfig object with parsed data
        """
        if not isinstance(yaml_data, dict):
            raise ConfigParsingError("YAML data must be a dictionary")

        client_data = yaml_data.get("client", {})
        if not isinstance(client_data, dict):
            raise ConfigParsingError("'client' section must be a dictionary")

        # Parse business information
        business = self._parse_business_config(client_data)

        # Parse contact information
        contact = self._parse_contact_config(client_data)

        # Parse branding
        branding = self._parse_branding_config(client_data)

        # Parse social media
        social_media = self._parse_social_media_config(client_data)

        # Parse Google Maps
        google_maps = self._parse_google_maps_config(client_data)

        # Parse Google Business Profile
        google_business_profile = client_data.get("google_business_profile", {})

        # Parse pages
        pages = self._parse_pages_config(client_data)

        # Parse offerings (products and services)
        products, services = self._parse_offerings_config(client_data)

        # Parse FAQ
        faq = self._parse_faq_config(client_data)

        # Build complete configuration
        config = ClientConfig(
            business=business,
            contact=contact,
            branding=branding,
            social_media=social_media,
            google_maps=google_maps,
            google_business_profile=google_business_profile,
            pages=pages,
            products=products,
            services=services,
            faq=faq,
        )

        self.current_config = config
        return config

    def _parse_business_config(self, client_data: Dict[str, Any]) -> BusinessConfig:
        """Parse business configuration section"""
        return BusinessConfig(
            business_name=client_data.get("business_name", ""),
            domain=client_data.get("domain", ""),
            industry=client_data.get("industry", ""),
            description=client_data.get("description", ""),
        )

    def _parse_contact_config(self, client_data: Dict[str, Any]) -> ContactConfig:
        """Parse contact configuration section"""
        contact_data = client_data.get("contact", {})
        if not isinstance(contact_data, dict):
            contact_data = {}

        return ContactConfig(
            name=contact_data.get("name", ""),
            phone=contact_data.get("phone", ""),
            address=contact_data.get("address", ""),
            email=contact_data.get("email", ""),
        )

    def _parse_branding_config(self, client_data: Dict[str, Any]) -> BrandingConfig:
        """Parse branding configuration section"""
        branding_data = client_data.get("branding", {})
        if not isinstance(branding_data, dict):
            branding_data = {}

        return BrandingConfig(
            primary_color=branding_data.get("primary_color", "#007bff"),
            secondary_color=branding_data.get("secondary_color", "#6c757d"),
            font_family=branding_data.get("font_family", "Arial, sans-serif"),
            logo_url=branding_data.get("logo_url", ""),
        )

    def _parse_social_media_config(
        self, client_data: Dict[str, Any]
    ) -> SocialMediaConfig:
        """Parse social media configuration section"""
        social_data = client_data.get("social_media", {})
        if not isinstance(social_data, dict):
            social_data = {}

        return SocialMediaConfig(
            facebook=social_data.get("facebook", ""),
            twitter=social_data.get("twitter", ""),
            linkedin=social_data.get("linkedin", ""),
            instagram=social_data.get("instagram", ""),
        )

    def _parse_google_maps_config(
        self, client_data: Dict[str, Any]
    ) -> GoogleMapsConfig:
        """Parse Google Maps configuration section"""
        maps_data = client_data.get("google_maps", {})
        if not isinstance(maps_data, dict):
            return GoogleMapsConfig()

        google_maps = GoogleMapsConfig()
        cities = maps_data.get("cities", {})
        if isinstance(cities, dict):
            google_maps.cities = cities

        return google_maps

    def _parse_pages_config(self, client_data: Dict[str, Any]) -> List[PageConfig]:
        """Parse pages configuration section"""
        pages_data = client_data.get("pages", [])
        if not isinstance(pages_data, list):
            return []

        pages = []
        for page_data in pages_data:
            if not isinstance(page_data, dict):
                continue

            page = PageConfig(
                title=page_data.get("title", ""),
                slug=page_data.get("slug", ""),
                city=page_data.get("city", ""),
                hero_image=page_data.get("hero_image", ""),
                primary_keyword=page_data.get("primary_keyword", ""),
                secondary_keywords=page_data.get("secondary_keywords", []),
            )
            pages.append(page)

        return pages

    def _parse_offerings_config(
        self, client_data: Dict[str, Any]
    ) -> tuple[List[ProductConfig], List[ServiceConfig]]:
        """Parse offerings into separate products and services lists"""
        offerings_data = client_data.get("offerings", [])
        if not isinstance(offerings_data, list):
            return [], []

        products = []
        services = []

        for offering_data in offerings_data:
            if not isinstance(offering_data, dict):
                continue

            offering_type = offering_data.get("type", "service")
            name = offering_data.get("name", "")

            if not name:
                continue  # Skip offerings without names

            if offering_type == "product":
                try:
                    product = ProductConfig(
                        sku=offering_data.get("sku", ""),
                        name=name,
                        image_url=offering_data.get("image_url", ""),
                        description=offering_data.get("description", ""),
                        category=offering_data.get("category", ""),
                        price=offering_data.get("price", ""),
                    )
                    products.append(product)
                except ValueError as e:
                    # Skip invalid products but continue processing
                    print(f"Warning: Skipping invalid product '{name}': {e}")
            else:
                try:
                    service = ServiceConfig(
                        name=name,
                        description=offering_data.get("description", ""),
                        category=offering_data.get("category", ""),
                    )
                    services.append(service)
                except ValueError as e:
                    # Skip invalid services but continue processing
                    print(f"Warning: Skipping invalid service '{name}': {e}")

        return products, services

    def _parse_faq_config(self, client_data: Dict[str, Any]) -> List[FAQItem]:
        """Parse FAQ configuration section"""
        faq_data = client_data.get("faq", [])
        if not isinstance(faq_data, list):
            return []

        faq_items = []
        for item_data in faq_data:
            if isinstance(item_data, dict):
                question = item_data.get("question", "")
                answer = item_data.get("answer", "")

                if question:  # Only add if question exists
                    try:
                        faq_item = FAQItem(question=question, answer=answer)
                        faq_items.append(faq_item)
                    except ValueError:
                        # Skip invalid FAQ items
                        continue

        return faq_items

    def generate_yaml_dict(self, config: ClientConfig) -> Dict[str, Any]:
        """
        Generate YAML dictionary from ClientConfig object

        Args:
            config: ClientConfig object to convert

        Returns:
            Dictionary suitable for YAML serialization
        """
        # Build offerings list (combine services and products)
        offerings = []

        # Add services
        for service in config.services:
            offerings.append(service.to_dict())

        # Add products
        for product in config.products:
            offerings.append(product.to_dict())

        # Build pages list
        pages_list = []
        for page in config.pages:
            page_dict = {
                "title": page.title,
                "slug": page.slug,
                "primary_keyword": page.primary_keyword,
                "secondary_keywords": page.secondary_keywords,
            }
            if page.city:
                page_dict["city"] = page.city
            if page.hero_image:
                page_dict["hero_image"] = page.hero_image
            pages_list.append(page_dict)

        # Build FAQ list
        faq_list = []
        for faq_item in config.faq:
            faq_list.append({"question": faq_item.question, "answer": faq_item.answer})

        # Build complete YAML structure
        yaml_data = {
            "client": {
                "business_name": config.business.business_name,
                "domain": config.business.domain,
                "industry": config.business.industry,
                "description": config.business.description,
                "contact": {
                    "name": config.contact.name,
                    "phone": config.contact.phone,
                    "address": config.contact.address,
                    "email": config.contact.email,
                },
                "branding": {
                    "primary_color": config.branding.primary_color,
                    "secondary_color": config.branding.secondary_color,
                    "font_family": config.branding.font_family,
                    "logo_url": config.branding.logo_url,
                },
                "social_media": config.social_media.get_valid_links(),
                "google_business_profile": config.google_business_profile,
                "pages": pages_list,
                "offerings": offerings,
                "faq": faq_list,
            }
        }

        # Add Google Maps if cities exist
        if config.google_maps.cities:
            yaml_data["client"]["google_maps"] = {"cities": config.google_maps.cities}

        return yaml_data

    def save_yaml_file(self, config: ClientConfig, file_path: str) -> bool:
        """
        Save ClientConfig to YAML file

        Args:
            config: ClientConfig object to save
            file_path: Output file path

        Returns:
            True if successful, False otherwise
        """
        try:
            yaml_data = self.generate_yaml_dict(config)

            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            with open(file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    yaml_data, f, default_flow_style=False, sort_keys=False, indent=2
                )

            return True

        except Exception as e:
            print(f"Error saving YAML file: {e}")
            return False

    def validate_config(self, config: ClientConfig) -> tuple[bool, List[str]]:
        """
        Validate a configuration object

        Args:
            config: ClientConfig to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        return config.validate()

    def migrate_legacy_config(self, legacy_yaml_data: Dict[str, Any]) -> ClientConfig:
        """
        Migrate legacy YAML configuration to new format

        Args:
            legacy_yaml_data: Old format YAML data

        Returns:
            ClientConfig with migrated data
        """
        # For now, just use the standard parser
        # In the future, we can add specific migration logic here
        return self.parse_yaml_dict(legacy_yaml_data)


# Convenience functions for quick operations
def load_config_from_file(file_path: str) -> ClientConfig:
    """Load configuration from YAML file"""
    parser = ConfigParser()
    return parser.parse_yaml_file(file_path)


def save_config_to_file(config: ClientConfig, file_path: str) -> bool:
    """Save configuration to YAML file"""
    parser = ConfigParser()
    return parser.save_yaml_file(config, file_path)


def convert_yaml_to_config(yaml_data: Dict[str, Any]) -> ClientConfig:
    """Convert YAML dictionary to ClientConfig"""
    parser = ConfigParser()
    return parser.parse_yaml_dict(yaml_data)
