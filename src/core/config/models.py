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
    publish_on_website: bool = True  # Controls if address appears in LocalBusiness schema
    
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

    # Basic contact information
    name: str = ""
    phone: str = ""
    address: AddressConfig = field(default_factory=AddressConfig)
    email: str = ""
    
    # Enhanced fields for professional templates
    business_hours: Dict[str, str] = field(default_factory=dict)  # {"monday": "8AM-6PM"}
    emergency_phone: str = ""  # After-hours contact
    office_phone: str = ""  # Main office line
    mobile_phone: str = ""  # Mobile contact
    fax_number: str = ""  # Fax if applicable
    response_time_promise: str = ""  # "We respond within 24 hours"
    contact_preference: str = ""  # "Phone", "Email", "Online Form"
    additional_locations: List[AddressConfig] = field(default_factory=list)

    def __post_init__(self):
        """Validate contact data after initialization"""
        if self.phone:
            self.phone = self._normalize_phone(self.phone)
        if self.office_phone:
            self.office_phone = self._normalize_phone(self.office_phone)
        if self.mobile_phone:
            self.mobile_phone = self._normalize_phone(self.mobile_phone)
        if self.emergency_phone:
            self.emergency_phone = self._normalize_phone(self.emergency_phone)
        
        # Set default business hours if none provided
        if not self.business_hours:
            self.business_hours = {
                "monday": "8:00 AM - 6:00 PM",
                "tuesday": "8:00 AM - 6:00 PM", 
                "wednesday": "8:00 AM - 6:00 PM",
                "thursday": "8:00 AM - 6:00 PM",
                "friday": "8:00 AM - 6:00 PM",
                "saturday": "9:00 AM - 4:00 PM",
                "sunday": "Closed"
            }

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
    
    def get_primary_phone(self) -> str:
        """Get the primary phone number for display"""
        return self.phone or self.office_phone or self.mobile_phone
    
    def get_formatted_hours(self) -> str:
        """Get formatted business hours for display"""
        if not self.business_hours:
            return ""
        
        # Group consecutive days with same hours
        formatted = []
        for day, hours in self.business_hours.items():
            formatted.append(f"{day.title()}: {hours}")
        
        return "\n".join(formatted)
    
    def has_multiple_contacts(self) -> bool:
        """Check if multiple contact methods are available"""
        contacts = [self.phone, self.office_phone, self.mobile_phone, self.emergency_phone]
        return len([c for c in contacts if c.strip()]) > 1


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

    # Basic business information
    business_name: str = ""
    domain: str = ""
    industry: str = ""
    description: str = ""
    
    # Enhanced fields for professional templates
    tagline: str = ""  # Value proposition for hero section H1
    hero_subtitle: str = ""  # Subtitle text below hero H1
    years_in_business: str = ""  # "Since 1995" or "15+ Years"
    company_overview: str = ""  # Rich description for About section
    mission_statement: str = ""  # Company mission
    service_guarantee: str = ""  # Warranty/guarantee text
    service_area_description: str = ""  # Custom service territory text
    why_choose_us: List[str] = field(default_factory=list)  # Key differentiators
    company_stats: Dict[str, str] = field(default_factory=dict)  # {"projects": "500+", "years": "15+"}

    def __post_init__(self):
        """Clean up domain format and set defaults"""
        if self.domain and not self.domain.startswith(("http://", "https://")):
            self.domain = f"https://{self.domain}"
        
        # Set default tagline if not provided
        if not self.tagline and self.business_name:
            self.tagline = f"Professional {self.industry.lower()} services you can trust"
    
    def get_hero_tagline(self) -> str:
        """Get tagline for hero section"""
        return self.tagline or f"Professional {self.industry.lower()} services you can trust"
    
    def get_years_display(self) -> str:
        """Get formatted years in business for display"""
        if self.years_in_business:
            if self.years_in_business.isdigit():
                return f"{self.years_in_business}+ Years of Experience"
            return self.years_in_business
        return ""
    
    def has_enhanced_content(self) -> bool:
        """Check if enhanced content fields are populated"""
        return bool(self.company_overview or self.mission_statement or 
                   self.why_choose_us or self.company_stats)


@dataclass
class BrandingConfig:
    """Branding and visual design configuration"""

    primary_color: str = "#007bff"
    secondary_color: str = "#6c757d"
    body_background_color: str = "#ffffff"
    body_text_color: str = "#333333"
    footer_background_color: str = "#2c3e50"
    footer_text_color: str = "#ffffff"
    font_family: str = "Arial, sans-serif"
    logo_url: str = ""

    def __post_init__(self):
        """Validate color formats"""
        self._validate_color(self.primary_color, "primary_color")
        self._validate_color(self.secondary_color, "secondary_color")
        self._validate_color(self.body_background_color, "body_background_color")
        self._validate_color(self.body_text_color, "body_text_color")
        self._validate_color(self.footer_background_color, "footer_background_color")
        self._validate_color(self.footer_text_color, "footer_text_color")

    def _validate_color(self, color: str, field_name: str):
        """Validate hex color format"""
        if color and not color.startswith("#"):
            raise ValueError(f"{field_name} must be a valid hex color (e.g., #007bff)")


@dataclass
class CityImageConfig:
    """City image configuration with attribution and embed code support"""
    
    image_url: str = ""
    alt_text: str = ""
    caption: str = ""
    credit: str = ""
    source: str = "Wikipedia"
    embed_code: str = ""  # Full HTML embed code for Wikipedia images


@dataclass
class PlaceOfInterest:
    """Places of interest with Google Maps embeds"""
    
    name: str
    embed_url: str = ""
    
    def __post_init__(self):
        if not self.name:
            raise ValueError("Place of interest name is required")


@dataclass
class CityFAQItem:
    """City-specific FAQ item"""
    
    question: str
    answer: str
    
    def __post_init__(self):
        if not self.question:
            raise ValueError("FAQ question is required")
        if not self.answer:
            raise ValueError("FAQ answer is required")


@dataclass
class CityPageConfig:
    """Enhanced city page configuration with rich content"""
    
    # Basic page info
    city_name: str
    state: str = ""
    slug: str = ""
    
    # SEO and meta
    title: str = ""
    meta_description: str = ""
    primary_keyword: str = ""
    secondary_keywords: List[str] = field(default_factory=list)
    
    # Hero section
    hero_title: str = ""
    breadcrumbs: List[str] = field(default_factory=list)
    
    # City information section
    about_city: str = ""  # Wikipedia-style description
    city_image: CityImageConfig = field(default_factory=CityImageConfig)
    
    # Main SEO content (800+ words)
    seo_content_title: str = ""
    seo_content_body: str = ""  # Main content block
    
    # Places of interest
    places_of_interest: List[PlaceOfInterest] = field(default_factory=list)
    
    # City-specific FAQ
    city_faq: List[CityFAQItem] = field(default_factory=list)
    
    # Internal links and products
    featured_products: List[str] = field(default_factory=list)  # Product slugs
    
    # Map configuration
    city_map_embed: str = ""
    
    # Business contact for this city
    service_area_note: str = ""
    
    def __post_init__(self):
        """Generate defaults and validate"""
        if not self.slug and self.city_name:
            import re
            self.slug = re.sub(r'[^a-zA-Z0-9\s]', '', self.city_name.lower())
            self.slug = re.sub(r'\s+', '-', self.slug.strip())
        
        if not self.title and self.city_name:
            self.title = f"{self.city_name} — Custom Architectural Metal"
        
        if not self.hero_title and self.city_name:
            self.hero_title = f"{self.city_name} — Custom Architectural Metal Fabrication"
        
        if not self.breadcrumbs:
            self.breadcrumbs = ["Home", "Locations", self.city_name]
    
    @property
    def full_city_name(self) -> str:
        """Get full city name with state"""
        if self.state:
            return f"{self.city_name}, {self.state}"
        return self.city_name


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
class GoogleBusinessProfileConfig:
    """Google Business Profile (GBP) configuration for schema.org LocalBusiness"""

    profile_url: str = ""  # Full GBP URL
    expose_address: bool = False  # Whether GBP publicly shows the business address
    place_id: str = ""  # Google Maps Place ID
    rating: str = ""  # Average rating (e.g., "4.8")
    review_count: str = ""  # Number of reviews

    def is_configured(self) -> bool:
        """Check if GBP is configured"""
        return bool(self.profile_url or self.place_id)


@dataclass
class GoogleMapsConfig:
    """Google Maps integration configuration"""

    api_key: str = ""
    embed_code: str = ""
    cities: Dict[str, Dict[str, str]] = field(default_factory=dict)

    def add_city_map(self, city: str, state: str, embed_code: str):
        """Add a city-specific map"""
        key = f"{city}, {state}"
        self.cities[key] = {"embed_code": embed_code}


@dataclass
class DeploymentConfig:
    """
    Individual deployment configuration for multi-deployment support.

    Each deployment represents a unique bucket/directory combination with its own
    CloudFront distribution, meta tags, and deployment history.
    """

    # Deployment identification
    deployment_id: str  # Unique identifier: e.g., "portable-sanitation-solutions-clean-restroom-rentals-va"
    bucket: str  # S3 bucket name
    directory: str  # Directory/prefix within bucket (can be empty for root)
    region: str = "us-east-1"  # AWS region

    # Deployment mode
    mode: str = "s3"  # "s3" or "cloudfront"

    # CloudFront settings (for Mode B)
    cloudfront_distribution_id: Optional[str] = None  # E.g., "E1DKVV3777HLXC"
    cloudfront_domain: Optional[str] = None  # E.g., "d35dpqbrqrzecj.cloudfront.net"

    # Deployment history
    last_deployed: Optional[str] = None  # ISO format datetime string
    deployment_url: Optional[str] = None  # Full URL to deployed site

    # SEO meta tags specific to this deployment
    meta_tags: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        """Validate deployment configuration"""
        if self.mode not in ["s3", "cloudfront"]:
            self.mode = "s3"

        # Generate deployment_id if not provided
        if not self.deployment_id:
            safe_bucket = self.bucket.replace("_", "-")
            safe_directory = self.directory.replace("/", "-").replace("_", "-")
            if safe_directory:
                self.deployment_id = f"{safe_bucket}-{safe_directory}"
            else:
                self.deployment_id = safe_bucket

    def get_website_url(self) -> str:
        """Get the public website URL for this deployment"""
        if self.deployment_url:
            return self.deployment_url

        if self.mode == "cloudfront" and self.cloudfront_domain:
            url = f"https://{self.cloudfront_domain}"
            if self.directory:
                url += f"/{self.directory}"
            return url
        elif self.mode == "s3" and self.bucket:
            base_url = f"http://{self.bucket}.s3-website-{self.region}.amazonaws.com"
            if self.directory:
                base_url += f"/{self.directory}"
            return base_url

        return ""

    def is_configured(self) -> bool:
        """Check if deployment is properly configured"""
        return bool(self.bucket and self.region)


@dataclass
class CloudConfig:
    """Cloud deployment configuration following SOP patterns"""

    # AWS profile and authentication
    aws_profile: str = ""
    aws_region: str = "us-east-1"

    # Google Cloud Storage authentication
    gcs_project_id: str = ""
    gcs_service_account_json: str = ""  # Path to JSON file
    gcs_region: str = "us-central1"

    # Deployment settings
    bucket_name: str = ""
    deployment_mode: str = "s3"  # "s3" or "cloudfront"

    # CloudFront settings (for cloudfront mode)
    distribution_id: str = ""
    custom_domain: str = ""

    # Caching configuration following SOP
    html_cache_control: str = "max-age=300,public"  # 5 minutes for HTML
    asset_cache_control: str = "max-age=86400,public"  # 1 day for assets

    # S3 website configuration (for s3 mode)
    index_document: str = "index.html"
    error_document: str = "404.html"

    # Deployment history and metadata
    last_deployment: Optional[str] = None
    deployment_url: str = ""

    # SEO and backlink site configuration
    site_type: str = "main_site"  # "main_site" or "backlink_site"
    main_site_url: str = ""  # For backlink sites: the main production site to link to
    allow_indexing: bool = True  # Control search engine indexing

    # SEO meta tags (name -> content mapping)
    meta_tags: Dict[str, str] = field(default_factory=dict)  # {"google-site-verification": "code", "facebook-domain-verification": "code"}

    # CloudFront cache invalidation
    auto_invalidate_cache: bool = True  # Automatically invalidate CloudFront cache after deployment

    def __post_init__(self):
        """Post-initialization validation and setup"""
        # Validate deployment mode
        if self.deployment_mode not in ["s3", "cloudfront"]:
            self.deployment_mode = "s3"
        
        # Generate bucket name if not provided (following SOP pattern)
        if not self.bucket_name and self.aws_profile:
            import re
            # This will be enhanced when integrated with business config
            safe_profile = re.sub(r'[^a-zA-Z0-9-]', '-', self.aws_profile.lower())
            self.bucket_name = f"client-website-{safe_profile}"
    
    def get_website_url(self) -> str:
        """Get the public website URL based on deployment mode"""
        if self.deployment_url:
            return self.deployment_url
        
        if self.deployment_mode == "cloudfront" and self.distribution_id:
            return f"https://{self.distribution_id}.cloudfront.net"
        elif self.deployment_mode == "s3" and self.bucket_name:
            return f"http://{self.bucket_name}.s3-website-{self.aws_region}.amazonaws.com"
        
        return ""
    
    def is_configured(self) -> bool:
        """Check if cloud deployment is properly configured"""
        return bool(self.aws_profile and self.bucket_name)


@dataclass
class ClientConfig:
    """Complete client configuration"""

    # Core business information
    business: BusinessConfig = field(default_factory=BusinessConfig)
    contact: ContactConfig = field(default_factory=ContactConfig)
    branding: BrandingConfig = field(default_factory=BrandingConfig)

    # Cloud deployment configuration
    cloud: CloudConfig = field(default_factory=CloudConfig)

    # Multi-deployment support (v3.2.0+)
    deployments: List[DeploymentConfig] = field(default_factory=list)

    # Content
    products: List[ProductConfig] = field(default_factory=list)
    services: List[ServiceConfig] = field(default_factory=list)
    pages: List[PageConfig] = field(default_factory=list)
    faq: List[FAQItem] = field(default_factory=list)

    # Enhanced city pages
    city_pages: List[CityPageConfig] = field(default_factory=list)

    # Social and maps
    social_media: SocialMediaConfig = field(default_factory=SocialMediaConfig)
    google_maps: GoogleMapsConfig = field(default_factory=GoogleMapsConfig)
    google_business_profile: GoogleBusinessProfileConfig = field(default_factory=GoogleBusinessProfileConfig)
    
    # Cities and local SEO data (legacy support)
    target_cities: List[str] = field(default_factory=list)
    seo_content: Dict[str, str] = field(default_factory=dict)
    
    # API keys for integrations
    api_keys: Dict[str, str] = field(default_factory=dict)

    # Metadata
    created_date: datetime = field(default_factory=datetime.now)
    last_modified: datetime = field(default_factory=datetime.now)
    version: str = "2.3.0"

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

    def add_city_page(self, city_page: CityPageConfig):
        """Add a city page to the configuration"""
        # Check for duplicate city
        if any(cp.city_name == city_page.city_name for cp in self.city_pages):
            raise ValueError(f"City page for '{city_page.city_name}' already exists")

        self.city_pages.append(city_page)
        self.last_modified = datetime.now()

    def get_city_page(self, city_name: str) -> Optional[CityPageConfig]:
        """Get city page configuration by name"""
        for city_page in self.city_pages:
            if city_page.city_name.lower() == city_name.lower():
                return city_page
        return None

    def remove_city_page(self, city_name: str) -> bool:
        """Remove city page by name"""
        for i, city_page in enumerate(self.city_pages):
            if city_page.city_name.lower() == city_name.lower():
                del self.city_pages[i]
                self.last_modified = datetime.now()
                return True
        return False

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

        # Build city pages list
        city_pages_list = []
        for city_page in self.city_pages:
            city_dict = {
                "city_name": city_page.city_name,
                "state": city_page.state,
                "slug": city_page.slug,
                "title": city_page.title,
                "meta_description": city_page.meta_description,
                "primary_keyword": city_page.primary_keyword,
                "secondary_keywords": city_page.secondary_keywords,
                "hero_title": city_page.hero_title,
                "breadcrumbs": city_page.breadcrumbs,
                "about_city": city_page.about_city,
                "city_image": {
                    "image_url": city_page.city_image.image_url,
                    "alt_text": city_page.city_image.alt_text,
                    "caption": city_page.city_image.caption,
                    "credit": city_page.city_image.credit,
                    "source": city_page.city_image.source,
                },
                "seo_content_title": city_page.seo_content_title,
                "seo_content_body": city_page.seo_content_body,
                "places_of_interest": [
                    {"name": poi.name, "embed_url": poi.embed_url}
                    for poi in city_page.places_of_interest
                ],
                "city_faq": [
                    {"question": faq.question, "answer": faq.answer}
                    for faq in city_page.city_faq
                ],
                "featured_products": city_page.featured_products,
                "city_map_embed": city_page.city_map_embed,
                "service_area_note": city_page.service_area_note,
            }
            city_pages_list.append(city_dict)

        return {
            "client": {
                "business_name": self.business.business_name,
                "domain": self.business.domain,
                "industry": self.business.industry,
                "description": self.business.description,
                "tagline": self.business.tagline,
                "hero_subtitle": self.business.hero_subtitle,
                "years_in_business": self.business.years_in_business,
                "company_overview": self.business.company_overview,
                "mission_statement": self.business.mission_statement,
                "service_guarantee": self.business.service_guarantee,
                "service_area_description": self.business.service_area_description,
                "why_choose_us": self.business.why_choose_us,
                "company_stats": self.business.company_stats,
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
                "google_business_profile": {
                    "profile_url": self.google_business_profile.profile_url,
                    "expose_address": self.google_business_profile.expose_address,
                    "place_id": self.google_business_profile.place_id,
                    "rating": self.google_business_profile.rating,
                    "review_count": self.google_business_profile.review_count,
                },
                "google_maps": {
                    "api_key": self.google_maps.api_key,
                    "embed_code": self.google_maps.embed_code,
                    "cities": self.google_maps.cities
                },
                "target_cities": self.target_cities,
                "seo_content": self.seo_content,
                "api_keys": self.api_keys,
                "cloud": {
                    "aws_profile": self.cloud.aws_profile,
                    "aws_region": self.cloud.aws_region,
                    "bucket_name": self.cloud.bucket_name,
                    "deployment_mode": self.cloud.deployment_mode,
                    "distribution_id": self.cloud.distribution_id,
                    "custom_domain": self.cloud.custom_domain,
                    "html_cache_control": self.cloud.html_cache_control,
                    "asset_cache_control": self.cloud.asset_cache_control,
                    "index_document": self.cloud.index_document,
                    "error_document": self.cloud.error_document,
                    "last_deployment": self.cloud.last_deployment,
                    "deployment_url": self.cloud.deployment_url,
                },
                "pages": pages_list,
                "offerings": offerings,
                "faq": faq_list,
                "city_pages": city_pages_list,
            }
        }


# Type aliases for convenience
ConfigDict = Dict[str, Any]
ValidationResult = tuple[bool, List[str]]
