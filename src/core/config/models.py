"""
Configuration data models using dataclasses

This module defines the core data structures for the SEO Authority Website Generator.
All configuration data is represented using type-safe dataclasses.

Version: 1.0.0
Author: Cloud Stack Generator Team
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class AddressConfig:
    """Address configuration with separate fields"""
    
    street: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = "United States"
    
    def to_single_line(self) -> str:
        """Convert to single line address string for display purposes"""
        parts = []
        if self.street:
            parts.append(self.street)
        if self.city:
            parts.append(self.city)
        if self.state:
            parts.append(self.state)
        if self.zip_code:
            parts.append(self.zip_code)
        if self.country and self.country != "United States":
            parts.append(self.country)
        return ", ".join(parts)
    
    @classmethod
    def from_single_line(cls, address_line: str) -> 'AddressConfig':
        """Create AddressConfig from single line address (for migration)"""
        if not address_line:
            return cls()
        
        # Simple parsing - split by comma and try to identify components
        parts = [part.strip() for part in address_line.split(",")]
        
        street = parts[0] if len(parts) > 0 else ""
        city = parts[1] if len(parts) > 1 else ""
        state = parts[2] if len(parts) > 2 else ""
        zip_code = parts[3] if len(parts) > 3 else ""
        country = parts[4] if len(parts) > 4 else "United States"
        
        return cls(
            street=street,
            city=city,
            state=state,
            zip_code=zip_code,
            country=country
        )


@dataclass
class ContactConfig:
    """Contact information configuration"""

    name: str = ""
    phone: str = ""
    address: AddressConfig = field(default_factory=AddressConfig)
    email: str = ""

    def __post_init__(self):
        """Validate contact data after initialization"""
        if self.phone:
            self.phone = self._normalize_phone(self.phone)

    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number format"""
        if not phone:
            return ""

        # If already normalized, return as-is
        if phone.startswith("+1-") and phone.count("-") == 3:
            return phone

        # Extract digits only
        digits = "".join(filter(str.isdigit, phone))

        # Format based on length
        if len(digits) == 10:
            return f"+1-{digits[:3]}-{digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits.startswith("1"):
            return f"+1-{digits[1:4]}-{digits[4:7]}-{digits[7:]}"

        return phone  # Return original if can't parse


@dataclass
class ProductConfig:
    """Product configuration with validation"""

    sku: str
    name: str
    image_url: str = ""
    description: str = ""
    category: str = ""
    price: str = ""

    def __post_init__(self):
        """Validate product data after initialization"""
        if not self.sku:
            raise ValueError("Product SKU is required")
        if not self.name:
            raise ValueError("Product name is required")

    @property
    def slug(self) -> str:
        """Generate URL-friendly slug from product name"""
        import re

        slug = re.sub(r"[^a-zA-Z0-9\s]", "", self.name.lower())
        return re.sub(r"\s+", "-", slug.strip())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization"""
        return {
            "sku": self.sku,
            "name": self.name,
            "image_url": self.image_url,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "type": "product",
        }


@dataclass
class ServiceConfig:
    """Service configuration"""

    name: str
    description: str = ""
    category: str = ""

    def __post_init__(self):
        """Validate service data after initialization"""
        if not self.name:
            raise ValueError("Service name is required")

    @property
    def slug(self) -> str:
        """Generate URL-friendly slug from service name"""
        import re

        slug = re.sub(r"[^a-zA-Z0-9\s]", "", self.name.lower())
        return re.sub(r"\s+", "-", slug.strip())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML serialization"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "type": "service",
        }


@dataclass
class BusinessConfig:
    """Business information configuration"""

    business_name: str = ""
    domain: str = ""
    industry: str = ""
    description: str = ""

    def __post_init__(self):
        """Clean up domain format"""
        if self.domain and not self.domain.startswith(("http://", "https://")):
            self.domain = f"https://{self.domain}"


@dataclass
class BrandingConfig:
    """Branding and visual design configuration"""

    primary_color: str = "#007bff"
    secondary_color: str = "#6c757d"
    font_family: str = "Arial, sans-serif"
    logo_url: str = ""

    def __post_init__(self):
        """Validate color formats"""
        self._validate_color(self.primary_color, "primary_color")
        self._validate_color(self.secondary_color, "secondary_color")

    def _validate_color(self, color: str, field_name: str):
        """Validate hex color format"""
        if color and not color.startswith("#"):
            raise ValueError(f"{field_name} must be a valid hex color (e.g., #007bff)")


@dataclass
class PageConfig:
    """Individual page configuration"""

    title: str
    slug: str
    city: str = ""
    hero_image: str = ""
    primary_keyword: str = ""
    secondary_keywords: List[str] = field(default_factory=list)

    @property
    def url_path(self) -> str:
        """Get the URL path for this page"""
        return f"/{self.slug}.html" if self.slug != "index" else "/index.html"


@dataclass
class FAQItem:
    """FAQ question and answer pair"""

    question: str
    answer: str

    def __post_init__(self):
        if not self.question:
            raise ValueError("FAQ question is required")
        if not self.answer:
            self.answer = (
                f"Please contact us for more information about {self.question.lower()}"
            )


@dataclass
class SocialMediaConfig:
    """Social media links configuration"""

    facebook: str = ""
    twitter: str = ""
    linkedin: str = ""
    instagram: str = ""
    youtube: str = ""

    def get_valid_links(self) -> Dict[str, str]:
        """Get only the social media links that are provided"""
        return {platform: url for platform, url in self.__dict__.items() if url.strip()}


@dataclass
class GoogleMapsConfig:
    """Google Maps integration configuration"""

    embed_code: str = ""
    cities: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def add_city_map(self, city: str, state: str, embed_code: str):
        """Add a city-specific map"""
        key = f"{city}, {state}"
        self.cities[key] = {"embed_code": embed_code}


@dataclass
class ClientConfig:
    """Complete client configuration"""

    # Core business information
    business: BusinessConfig = field(default_factory=BusinessConfig)
    contact: ContactConfig = field(default_factory=ContactConfig)
    branding: BrandingConfig = field(default_factory=BrandingConfig)

    # Content
    products: List[ProductConfig] = field(default_factory=list)
    services: List[ServiceConfig] = field(default_factory=list)
    pages: List[PageConfig] = field(default_factory=list)
    faq: List[FAQItem] = field(default_factory=list)

    # Social and maps
    social_media: SocialMediaConfig = field(default_factory=SocialMediaConfig)
    google_maps: GoogleMapsConfig = field(default_factory=GoogleMapsConfig)
    google_business_profile: Dict[str, str] = field(default_factory=dict)
    
    # Cities and local SEO data
    target_cities: List[str] = field(default_factory=list)
    seo_content: Dict[str, str] = field(default_factory=dict)
    
    # API keys for integrations
    api_keys: Dict[str, str] = field(default_factory=dict)

    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    version: str = "2.2.0"

    def __post_init__(self):
        """Post-initialization validation and setup"""
        self.last_modified = datetime.now()

        # Ensure we have a home page
        if not any(page.slug == "index" for page in self.pages):
            self.add_home_page()

    def add_home_page(self):
        """Add default home page if none exists"""
        home_page = PageConfig(
            title="Home",
            slug="index",
            primary_keyword=(
                self.business.industry.lower() if self.business.industry else "services"
            ),
            secondary_keywords=[self.business.business_name.lower(), "local business"],
        )
        self.pages.insert(0, home_page)

    def add_product(self, product: ProductConfig):
        """Add a product to the configuration"""
        # Check for duplicate SKU
        if any(p.sku == product.sku for p in self.products):
            raise ValueError(f"Product with SKU {product.sku} already exists")

        self.products.append(product)
        self.last_modified = datetime.now()

    def add_service(self, service: ServiceConfig):
        """Add a service to the configuration"""
        # Check for duplicate name
        if any(s.name == service.name for s in self.services):
            raise ValueError(f"Service '{service.name}' already exists")

        self.services.append(service)
        self.last_modified = datetime.now()

    def get_target_cities(self) -> List[str]:
        """Get list of target cities from pages"""
        cities = []
        for page in self.pages:
            if page.city and page.city not in cities:
                cities.append(page.city)
        return cities

    def validate(self) -> tuple[bool, List[str]]:
        """Validate the entire configuration"""
        errors = []

        # Business validation
        if not self.business.business_name:
            errors.append("Business name is required")
        if not self.business.industry:
            errors.append("Business industry is required")

        # Contact validation
        if not self.contact.phone:
            errors.append("Phone number is required")

        # Content validation
        if not self.services and not self.products:
            errors.append("At least one service or product is required")

        return len(errors) == 0, errors

    def to_yaml_dict(self) -> Dict[str, Any]:
        """Convert to dictionary suitable for YAML serialization"""
        # Build offerings list (combining products and services)
        offerings = []
        offerings.extend([service.to_dict() for service in self.services])
        offerings.extend([product.to_dict() for product in self.products])

        # Build pages list
        pages_list = []
        for page in self.pages:
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
        faq_list = [
            {"question": item.question, "answer": item.answer} for item in self.faq
        ]

        return {
            "client": {
                "business_name": self.business.business_name,
                "domain": self.business.domain,
                "industry": self.business.industry,
                "contact": {
                    "name": self.contact.name,
                    "phone": self.contact.phone,
                    "address": self.contact.address,
                    "email": self.contact.email,
                },
                "branding": {
                    "primary_color": self.branding.primary_color,
                    "secondary_color": self.branding.secondary_color,
                    "font_family": self.branding.font_family,
                    "logo_url": self.branding.logo_url,
                },
                "social_media": self.social_media.get_valid_links(),
                "google_business_profile": self.google_business_profile,
                "google_maps": (
                    {"cities": self.google_maps.cities}
                    if self.google_maps.cities
                    else {}
                ),
                "target_cities": self.target_cities,
                "seo_content": self.seo_content,
                "api_keys": self.api_keys,
                "pages": pages_list,
                "offerings": offerings,
                "faq": faq_list,
            }
        }


# Type aliases for convenience
ConfigDict = Dict[str, Any]
ValidationResult = tuple[bool, List[str]]
