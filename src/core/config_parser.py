"""
Configuration parser for the SEO Authority Website Generator
This implementation is driven by the test requirements

Version: 1.0.1
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


class ConfigValidationError(Exception):
    """Raised when configuration validation fails"""

    pass


@dataclass
class ContactInfo:
    """Contact information (NAP - Name, Address, Phone)"""

    name: Optional[str] = None
    address: Optional[str] = None
    phone: str = ""


@dataclass
class SocialMedia:
    """Social media account URLs"""

    facebook: Optional[str] = None
    twitter: Optional[str] = None
    linkedin: Optional[str] = None
    instagram: Optional[str] = None


@dataclass
class GoogleMaps:
    """Google Maps configuration"""

    place_id: Optional[str] = None
    embed_url: Optional[str] = None


@dataclass
class Branding:
    """Branding configuration"""

    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    font_family: Optional[str] = None


@dataclass
class Page:
    """Page configuration"""

    title: str
    slug: str
    primary_keyword: Optional[str] = None
    secondary_keywords: List[str] = field(default_factory=list)
    hero_image: Optional[str] = None
    meta_description: Optional[str] = None


@dataclass
class Offering:
    """Product or service offering"""

    name: str
    description: Optional[str] = None
    price_range: Optional[str] = None
    category: Optional[str] = None


@dataclass
class ClientConfig:
    """Complete client configuration"""

    business_name: str
    contact: ContactInfo
    pages: List[Page]
    offerings: List[Offering] = field(default_factory=list)
    domain: Optional[str] = None
    industry: Optional[str] = None
    social_media: Optional[SocialMedia] = None
    google_maps: Optional[GoogleMaps] = None
    branding: Optional[Branding] = None


@dataclass
class Config:
    """Root configuration object"""

    client: ClientConfig


class ConfigParser:
    """Parser for YAML configuration files"""

    def parse(self, config_dict: Dict[str, Any]) -> Config:
        """Parse configuration dictionary into Config object"""
        client_data = config_dict.get("client", {})

        # Parse contact info
        contact_data = client_data.get("contact", {})
        contact = ContactInfo(
            name=contact_data.get("name"),
            address=contact_data.get("address"),
            phone=contact_data.get("phone", ""),
        )

        # Parse social media
        social_data = client_data.get("social_media", {})
        social_media = SocialMedia(**social_data) if social_data else None

        # Parse Google Maps
        maps_data = client_data.get("google_maps", {})
        google_maps = GoogleMaps(**maps_data) if maps_data else None

        # Parse branding
        branding_data = client_data.get("branding", {})
        branding = Branding(**branding_data) if branding_data else None

        # Parse pages
        pages_data = client_data.get("pages", [])
        pages = [Page(**page_data) for page_data in pages_data]

        # Parse offerings
        offerings_data = client_data.get("offerings", [])
        offerings = [Offering(**offering_data) for offering_data in offerings_data]

        # Create client config
        client = ClientConfig(
            business_name=client_data.get("business_name", ""),
            domain=client_data.get("domain"),
            industry=client_data.get("industry"),
            contact=contact,
            social_media=social_media,
            google_maps=google_maps,
            branding=branding,
            pages=pages,
            offerings=offerings,
        )

        return Config(client=client)
