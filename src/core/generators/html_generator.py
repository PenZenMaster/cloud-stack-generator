"""
HTML Generator - Modular Website Page Generation
Sprint 2 Week 2 - Days 7-8 Implementation
src/core/generators/html_generator.py

Generates individual HTML pages from configuration data with SEO optimization
and template rendering using Jinja2.
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import jinja2
from datetime import datetime
from ..config.models import ClientConfig
from ..services.ai_content_service import AIContentService
from ..services.content_cache import ContentCache
from .content import HomeContentGenerator


class HTMLGenerator:
    """Generates HTML pages from configuration data"""

    def __init__(
        self,
        template_dir: str = None,
        ai_service: Optional[AIContentService] = None,
        cache: Optional[ContentCache] = None
    ):
        if template_dir is None:
            # Use absolute path relative to this file's location
            template_dir = Path(__file__).parent.parent.parent / "templates"
        self.template_dir = Path(template_dir)
        self.jinja_env = self._setup_jinja_environment()

        # Initialize AI content generation
        self.ai_service = ai_service or AIContentService()
        self.cache = cache or ContentCache()

        # Initialize content generators with AI support
        self.home_gen = HomeContentGenerator(
            ai_service=self.ai_service,
            cache=self.cache
        )

    def _setup_jinja_environment(self) -> Optional[jinja2.Environment]:
        """Setup Jinja2 environment with template loading"""
        try:
            loader = jinja2.FileSystemLoader(str(self.template_dir))
            env = jinja2.Environment(
                loader=loader,
                autoescape=jinja2.select_autoescape(["html", "xml"]),
                trim_blocks=True,
                lstrip_blocks=True,
            )

            # Add custom filters
            env.filters["format_phone"] = self._format_phone
            env.filters["format_price"] = self._format_price
            env.filters["slugify"] = self._slugify
            env.filters["truncate_words"] = self._truncate_words
            env.filters["date"] = self._date_filter

            return env
        except Exception as e:
            print(f"Warning: Could not setup Jinja2 environment: {e}")
            # Fallback to basic string templates
            return None

    def generate_homepage(self, config: ClientConfig, use_ai: bool = True) -> str:
        """Generate homepage HTML with AI-powered content"""
        template_data = self._prepare_template_data(config)

        # Use AI-powered content generation if available
        if use_ai and self.home_gen.use_ai:
            ai_content = self.home_gen.generate_enhanced_home_content(config, use_ai=True)
            if ai_content:
                template_data["ai_generated_content"] = ai_content

        template_data.update(
            {
                "page_title": f"{config.business.business_name} - {config.business.industry}",
                "page_description": f"Professional {config.business.industry.lower()} services from {config.business.business_name}",
                "page_type": "homepage",
                "is_homepage": True,
                "featured_services": config.services[:3],  # Show top 3 services
                "featured_products": config.products[:6],  # Show top 6 products
            }
        )

        return self._render_template("pages/index.html", template_data)

    def generate_about_page(self, config: ClientConfig) -> str:
        """Generate about us page"""
        template_data = self._prepare_template_data(config)
        template_data.update(
            {
                "page_title": f"About {config.business.business_name}",
                "page_description": f"Learn about {config.business.business_name} and our commitment to excellence",
                "page_type": "about",
                "company_story": self._generate_company_story(config),
                "team_members": self._get_team_members(config),
                "company_values": self._get_company_values(config),
            }
        )

        return self._render_template("pages/about.html", template_data)

    def generate_contact_page(self, config: ClientConfig) -> str:
        """Generate contact page"""
        template_data = self._prepare_template_data(config)
        template_data.update(
            {
                "page_title": f"Contact {config.business.business_name}",
                "page_description": f"Get in touch with {config.business.business_name} for professional {config.business.industry.lower()} services",
                "page_type": "contact",
                "contact_form": True,
                "google_maps_embed": self._generate_maps_embed(config.contact.address.to_single_line()),
                "business_hours": self._get_business_hours(config),
            }
        )

        return self._render_template("pages/contact.html", template_data)

    def generate_services_page(self, config: ClientConfig) -> str:
        """Generate services overview page"""
        template_data = self._prepare_template_data(config)

        # Handle case where services might be empty or None
        services = getattr(config, 'services', None) or []

        # Group services by category
        services_by_category = {}
        for service in services:
            category = service.category or "General Services"
            if category not in services_by_category:
                services_by_category[category] = []
            services_by_category[category].append(service)

        template_data.update(
            {
                "page_title": f"Services - {config.business.business_name}",
                "page_description": f"Professional {config.business.industry.lower()} services offered by {config.business.business_name}",
                "page_type": "services",
                "services_by_category": services_by_category,
                "total_services": len(services),
                "service_categories": list(services_by_category.keys()),
                "has_services": len(services) > 0,
            }
        )

        return self._render_template("pages/services.html", template_data)

    def generate_products_page(self, config: ClientConfig) -> str:
        """Generate products catalog page"""
        template_data = self._prepare_template_data(config)

        # Group products by category
        products_by_category = {}
        for product in config.products:
            category = product.category or "General Products"
            if category not in products_by_category:
                products_by_category[category] = []
            products_by_category[category].append(product)

        template_data.update(
            {
                "page_title": f"Products - {config.business.business_name}",
                "page_description": f"Quality products from {config.business.business_name}",
                "page_type": "products",
                "products_by_category": products_by_category,
                "total_products": len(config.products),
                "product_categories": list(products_by_category.keys()),
            }
        )

        return self._render_template("pages/products.html", template_data)

    def generate_individual_service_page(self, service, config: ClientConfig) -> str:
        """Generate individual service detail page"""
        template_data = self._prepare_template_data(config)

        # Related services (same category)
        related_services = [
            s
            for s in config.services
            if s.category == service.category and s.name != service.name
        ][:3]

        template_data.update(
            {
                "page_title": f"{service.name} - {config.business.business_name}",
                "page_description": (
                    f"{service.description[:150]}..."
                    if len(service.description) > 150
                    else service.description
                ),
                "page_type": "service-detail",
                "service": service,
                "related_services": related_services,
                "service_features": getattr(service, "features", []),
                "service_schema": self._generate_service_schema(service, config),
                "base_path": "../",  # Service detail pages are in subdirectory
            }
        )

        return self._render_template("pages/service-detail.html", template_data)

    def generate_individual_product_page(self, product, config: ClientConfig) -> str:
        """Generate individual product detail page"""
        template_data = self._prepare_template_data(config)

        # Related products (same category)
        related_products = [
            p
            for p in config.products
            if p.category == product.category and p.sku != product.sku
        ][:4]

        template_data.update(
            {
                "page_title": f"{product.name} - {config.business.business_name}",
                "page_description": (
                    f"{product.description[:150]}..."
                    if len(product.description) > 150
                    else product.description
                ),
                "page_type": "product-detail",
                "product": product,
                "related_products": related_products,
                "product_schema": self._generate_product_schema(product, config),
                "base_path": "../",  # Product pages are in subdirectory
            }
        )

        return self._render_template("pages/product-detail.html", template_data)

    def generate_faq_page(self, config: ClientConfig) -> str:
        """Generate FAQ page"""
        template_data = self._prepare_template_data(config)

        # Group FAQs by category if they exist
        if hasattr(config, "faq") and config.faq:
            faqs_by_category = {}
            for faq in config.faq:
                category = getattr(faq, "category", "General")
                if category not in faqs_by_category:
                    faqs_by_category[category] = []
                faqs_by_category[category].append(faq)
        else:
            faqs_by_category = {"General": []}

        template_data.update(
            {
                "page_title": f"FAQ - {config.business.business_name}",
                "page_description": f"Frequently asked questions about {config.business.business_name} services",
                "page_type": "faq",
                "faqs_by_category": faqs_by_category,
                "total_faqs": sum(len(faqs) for faqs in faqs_by_category.values()),
            }
        )

        return self._render_template("pages/faq.html", template_data)

    def generate_privacy_page(self, config: ClientConfig) -> str:
        """Generate privacy policy page"""
        template_data = self._prepare_template_data(config)

        template_data.update(
            {
                "page_title": f"Privacy Policy - {config.business.business_name}",
                "page_description": f"Privacy policy for {config.business.business_name}",
                "page_type": "privacy",
                "current_year": "2024",  # This will be handled by template data later
            }
        )

        return self._render_template("pages/privacy-policy.html", template_data)

    def _get_canonical_base_url(self, config: ClientConfig) -> str:
        """
        Get the base URL for canonical tags and sitemaps.

        For backlink sites: Use deployment_url (CloudFront) so Google indexes it independently
        For main sites: Use deployment_url if specified, otherwise business.domain
        """
        # For backlink sites, always use the deployed URL (CloudFront)
        if hasattr(config.cloud, 'site_type') and config.cloud.site_type == "backlink_site" and config.cloud.deployment_url:
            return config.cloud.deployment_url.rstrip("/")

        # For main sites, prefer deployment_url if specified
        if config.cloud.deployment_url:
            return config.cloud.deployment_url.rstrip("/")

        # Fallback to business domain
        return config.business.domain.rstrip("/")

    def _prepare_template_data(self, config: ClientConfig) -> Dict[str, Any]:
        """Prepare common template data for all pages"""
        canonical_base = self._get_canonical_base_url(config)

        template_data = {
            "business": config.business,
            "contact": config.contact,
            "branding": config.branding,
            "cloud": config.cloud,
            "services": config.services,
            "products": config.products,
            "faq": getattr(config, 'faq', []),
            "google_business_profile": getattr(config, 'google_business_profile', None),
            "current_year": datetime.now().year,
            "generation_date": datetime.now().strftime("%Y-%m-%d"),
            "site_url": config.business.domain,
            "canonical_base_url": canonical_base,  # NEW: For canonical tags
            "is_backlink_site": hasattr(config.cloud, 'site_type') and config.cloud.site_type == "backlink_site",  # NEW
            "main_site_url": getattr(config.cloud, 'main_site_url', '') if hasattr(config, 'cloud') else '',  # NEW: For backlink sites
            "navigation": self._generate_navigation(config),
            "footer_links": self._generate_footer_links(config),
            "social_links": self._get_social_links(config),
            "schema_organization": self._generate_organization_schema(config),
            "city_pages": getattr(config, 'city_pages', []),
            "base_path": "",  # Default for root-level pages, can be overridden by specific page generators
        }
        
        # Add enhanced data if available
        if hasattr(config, 'geo_coordinates'):
            template_data['geo_coordinates'] = config.geo_coordinates
        
        if hasattr(config, 'social_media'):
            template_data['social_media'] = config.social_media
            
        # Check for Google Business Profile data from multiple sources
        if hasattr(config, 'google_business_profile') and config.google_business_profile:
            template_data['google_business'] = config.google_business_profile
        elif hasattr(config, 'google_business') and config.google_business:
            template_data['google_business'] = config.google_business
        elif hasattr(config.contact, 'google_business') and config.contact.google_business:
            template_data['google_business'] = config.contact.google_business
            
        if hasattr(config, 'business_hours'):
            template_data['business_hours'] = config.business_hours
        elif hasattr(config.contact, 'business_hours'):
            template_data['business_hours'] = config.contact.business_hours
            
        return template_data

    def _generate_navigation(self, config: ClientConfig) -> List[Dict[str, str]]:
        """Generate navigation menu items"""
        nav_items = [
            {"name": "Home", "url": "/", "slug": "home"},
            {"name": "About", "url": "/about.html", "slug": "about"},
        ]

        if config.services:
            nav_items.append(
                {"name": "Services", "url": "/services.html", "slug": "services"}
            )

        if config.products:
            nav_items.append(
                {"name": "Products", "url": "/products.html", "slug": "products"}
            )

        # Add city pages navigation
        if hasattr(config, 'city_pages') and config.city_pages:
            city_nav_items = []
            for city_page in config.city_pages:
                city_nav_items.append({
                    "name": city_page.city_name,
                    "url": f"/locations/{city_page.slug}.html",
                    "slug": city_page.slug
                })
            
            nav_items.append({
                "name": "Locations", 
                "url": "#", 
                "slug": "locations",
                "dropdown": city_nav_items
            })

        nav_items.extend(
            [
                {"name": "FAQ", "url": "/faq.html", "slug": "faq"},
                {"name": "Contact", "url": "/contact.html", "slug": "contact"},
            ]
        )

        return nav_items

    def _generate_footer_links(
        self, config: ClientConfig
    ) -> Dict[str, List[Dict[str, str]]]:
        """Generate footer link sections"""
        return {
            "company": [
                {"name": "About Us", "url": "/about.html"},
                {"name": "Contact", "url": "/contact.html"},
                {"name": "FAQ", "url": "/faq.html"},
            ],
            "services": (
                [
                    {
                        "name": service.name,
                        "url": f"/services/{self._slugify(service.name)}.html",
                    }
                    for service in config.services[:5]  # Top 5 services
                ]
                if config.services
                else []
            ),
            "products": (
                [
                    {
                        "name": product.name,
                        "url": f"/products/{self._slugify(product.name)}.html",
                    }
                    for product in config.products[:5]  # Top 5 products
                ]
                if config.products
                else []
            ),
        }

    def _get_social_links(self, config: ClientConfig) -> List[Dict[str, str]]:
        """Get social media links if available"""
        # This would be extended when social media fields are added to config
        return []

    def _generate_organization_schema(self, config: ClientConfig) -> Dict[str, Any]:
        """Generate comprehensive JSON-LD @graph schema with Wikipedia entities"""
        # Generate @graph structure with proper entity linking
        graph = []

        # Main business entity
        business_schema = {
            "@type": "LocalBusiness",
            "@id": f"{config.business.domain}#business",
            "name": config.business.business_name,
            "description": getattr(config.business, 'description', f"Professional {config.business.industry} services"),
            "url": config.business.domain,
        }

        # Add contact information
        if config.contact.phone:
            business_schema["telephone"] = config.contact.phone
        if config.contact.email:
            business_schema["email"] = config.contact.email

        # Add address with proper PostalAddress structure
        if config.contact.address and config.contact.address.street:
            business_schema["address"] = {
                "@type": "PostalAddress",
                "streetAddress": config.contact.address.street,
                "addressLocality": config.contact.address.city,
                "addressRegion": config.contact.address.state,
                "postalCode": config.contact.address.zip_code,
                "addressCountry": config.contact.address.country or "US"
            }

        # Add geo coordinates if available
        if hasattr(config, 'geo_coordinates') and config.geo_coordinates:
            business_schema["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(config.geo_coordinates.get('latitude', '')),
                "longitude": str(config.geo_coordinates.get('longitude', ''))
            }

        # Add logo and images
        if hasattr(config, 'branding') and hasattr(config.branding, 'logo_url') and config.branding.logo_url:
            business_schema["logo"] = config.branding.logo_url
            business_schema["image"] = config.branding.logo_url

        # Add social media links
        social_links = self._get_social_links(config)
        if social_links:
            business_schema["sameAs"] = [link["url"] for link in social_links]

        # Add industry-specific Wikipedia entities for knowsAbout
        business_schema["knowsAbout"] = self._generate_industry_wikipedia_entities(config.business.industry)

        graph.append(business_schema)

        # Website entity
        website_schema = {
            "@type": "WebSite",
            "@id": f"{config.business.domain}#website",
            "url": config.business.domain,
            "name": config.business.business_name,
            "publisher": {"@id": f"{config.business.domain}#business"},
            "inLanguage": "en"
        }
        graph.append(website_schema)

        # Main page entity
        webpage_schema = {
            "@type": "WebPage",
            "@id": f"{config.business.domain}#webpage",
            "url": config.business.domain,
            "name": f"{config.business.business_name} - {getattr(config.business, 'tagline', config.business.industry)}",
            "description": getattr(config.business, 'description', f"Professional {config.business.industry} services"),
            "inLanguage": "en",
            "isPartOf": {"@id": f"{config.business.domain}#website"},
            "about": {"@id": f"{config.business.domain}#business"}
        }

        # Add primary image if available
        if hasattr(config, 'branding') and hasattr(config.branding, 'logo_url') and config.branding.logo_url:
            webpage_schema["primaryImageOfPage"] = {
                "@type": "ImageObject",
                "url": config.branding.logo_url
            }

        graph.append(webpage_schema)

        return {
            "@context": "https://schema.org",
            "@graph": graph
        }

    def _generate_industry_wikipedia_entities(self, industry: str) -> List[str]:
        """Generate Wikipedia URLs for industry-related topics"""
        industry_mappings = {
            "Construction": [
                "https://en.wikipedia.org/wiki/Construction",
                "https://en.wikipedia.org/wiki/Building",
                "https://en.wikipedia.org/wiki/Architecture"
            ],
            "Metal Fabrication": [
                "https://en.wikipedia.org/wiki/Metal_fabrication",
                "https://en.wikipedia.org/wiki/Metalworking",
                "https://en.wikipedia.org/wiki/Copper",
                "https://en.wikipedia.org/wiki/Architectural_metalwork"
            ],
            "Roofing": [
                "https://en.wikipedia.org/wiki/Roof",
                "https://en.wikipedia.org/wiki/Roofing_material",
                "https://en.wikipedia.org/wiki/Building_envelope"
            ],
            "HVAC": [
                "https://en.wikipedia.org/wiki/HVAC",
                "https://en.wikipedia.org/wiki/Ventilation_(architecture)",
                "https://en.wikipedia.org/wiki/Air_conditioning"
            ]
        }

        # Default fallback based on industry keywords
        industry_lower = industry.lower()
        if "metal" in industry_lower or "fabrication" in industry_lower:
            return industry_mappings.get("Metal Fabrication", [])
        elif "construction" in industry_lower or "building" in industry_lower:
            return industry_mappings.get("Construction", [])
        elif "roofing" in industry_lower or "roof" in industry_lower:
            return industry_mappings.get("Roofing", [])
        elif "hvac" in industry_lower or "heating" in industry_lower:
            return industry_mappings.get("HVAC", [])

        return industry_mappings.get(industry, [])

    def _generate_product_wikipedia_entities(self, product_name: str) -> List[str]:
        """Generate Wikipedia URLs for product-related topics"""
        product_mappings = {
            "cupola": "https://en.wikipedia.org/wiki/Cupola",
            "finial": "https://en.wikipedia.org/wiki/Finial",
            "dormer": "https://en.wikipedia.org/wiki/Dormer",
            "roof vent": "https://en.wikipedia.org/wiki/Ventilation",
            "chimney": "https://en.wikipedia.org/wiki/Chimney",
            "shroud": "https://en.wikipedia.org/wiki/Chimney",
            "leader box": "https://en.wikipedia.org/wiki/Box_gutter",
            "gutter": "https://en.wikipedia.org/wiki/Rain_gutter",
            "snow guard": "https://en.wikipedia.org/wiki/Snow_guard",
            "weathervane": "https://en.wikipedia.org/wiki/Weather_vane"
        }

        entities = []
        product_lower = product_name.lower()

        for keyword, wikipedia_url in product_mappings.items():
            if keyword in product_lower:
                entities.append(wikipedia_url)

        return entities

    def _generate_service_schema(self, service, config: ClientConfig) -> Dict[str, Any]:
        """Generate JSON-LD schema for service"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Service",
            "name": service.name,
            "description": service.description,
            "provider": {
                "@type": "Organization",
                "name": config.business.business_name,
                "url": config.business.domain,
            },
        }

        if hasattr(service, "price_range") and service.price_range:
            schema["offers"] = {
                "@type": "Offer",
                "price": service.price_range,
                "priceCurrency": "USD",
            }

        return schema

    def _generate_product_schema(self, product, config: ClientConfig) -> Dict[str, Any]:
        """Generate enhanced JSON-LD schema for product with Wikipedia entities"""
        schema = {
            "@context": "https://schema.org",
            "@type": "Product",
            "@id": f"{config.business.domain}/products/{getattr(product, 'slug', product.name.lower().replace(' ', '-'))}#product",
            "name": product.name,
            "description": product.description,
            "category": "Architectural Metalwork",
            "brand": {
                "@type": "Organization",
                "@id": f"{config.business.domain}#business",
                "name": config.business.business_name,
                "url": config.business.domain
            },
            "itemCondition": "https://schema.org/NewCondition"
        }

        # Add SKU if available
        if hasattr(product, "sku") and product.sku:
            schema["sku"] = product.sku
            schema["mpn"] = product.sku

        # Add material information if available
        if hasattr(product, "material") and product.material:
            schema["material"] = product.material

        # Add product images
        if hasattr(product, "image_url") and product.image_url:
            schema["image"] = [product.image_url]

        # Add Wikipedia entities for isSimilarTo
        wikipedia_entities = self._generate_product_wikipedia_entities(product.name)
        if wikipedia_entities:
            schema["isSimilarTo"] = wikipedia_entities

        # Add pricing information
        if hasattr(product, "price") and product.price:
            schema["offers"] = {
                "@type": "Offer",
                "price": str(product.price),
                "priceCurrency": "USD",
                "availability": "https://schema.org/InStock",
                "url": f"{config.business.domain}/products/{getattr(product, 'slug', product.name.lower().replace(' ', '-'))}",
                "seller": {
                    "@type": "Organization",
                    "name": config.business.business_name,
                    "url": config.business.domain
                }
            }

        return schema

    def _render_template(
        self, template_name: str, template_data: Dict[str, Any]
    ) -> str:
        """Render template with data"""
        if self.jinja_env:
            try:
                template = self.jinja_env.get_template(template_name)
                rendered = template.render(**template_data)
                return rendered
            except jinja2.TemplateNotFound:
                print(f"Warning: Template {template_name} not found, using fallback")
                return self._render_fallback_template(template_name, template_data)
            except Exception as e:
                print(f"Error rendering template {template_name}: {e}")
                return self._render_fallback_template(template_name, template_data)
        else:
            return self._render_fallback_template(template_name, template_data)

    def _render_fallback_template(
        self, template_name: str, data: Dict[str, Any]
    ) -> str:
        """Fallback template rendering when Jinja2 is not available"""
        business = data.get("business")
        contact = data.get("contact")
        branding = data.get("branding")

        # Basic HTML structure
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data.get('page_title', 'Website')}</title>
    <meta name="description" content="{data.get('page_description', '')}">
    <style>
        body {{ 
            font-family: {branding.font_family if branding else 'Arial, sans-serif'};
            margin: 0; padding: 0;
            background: white;
            color: #333;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        .header {{ background: {branding.primary_color if branding else '#007bff'}; color: white; padding: 20px 0; }}
        .nav {{ display: flex; gap: 20px; }}
        .nav a {{ color: white; text-decoration: none; }}
        .content {{ padding: 40px 0; }}
        .footer {{ background: #f8f9fa; padding: 20px 0; margin-top: 40px; }}
        h1 {{ color: {branding.primary_color if branding else '#007bff'}; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>{business.business_name if business else 'Business Name'}</h1>
            <nav class="nav">
                <a href="/">Home</a>
                <a href="/about.html">About</a>
                <a href="/services.html">Services</a>
                <a href="/products.html">Products</a>
                <a href="/contact.html">Contact</a>
            </nav>
        </div>
    </header>
    
    <main class="container">
        <div class="content">
            {self._get_fallback_content(template_name, data)}
        </div>
    </main>
    
    <footer class="footer">
        <div class="container">
            <p>&copy; {data.get('current_year')} {business.business_name if business else 'Business Name'}. All rights reserved.</p>
            {f'<p>Contact: {contact.phone} | {contact.email}</p>' if contact and (contact.phone or contact.email) else ''}
        </div>
    </footer>
</body>
</html>"""
        return html

    def _get_fallback_content(self, template_name: str, data: Dict[str, Any]) -> str:
        """Get content for fallback templates"""
        business = data.get("business")
        products = data.get("products", [])
        services = data.get("services", [])

        if "homepage" in template_name or "index" in template_name:
            return f"""
            <h1>Welcome to {business.business_name if business else 'Our Business'}</h1>
            <p>Professional {business.industry if business else 'services'} you can trust.</p>
            <h2>Our {'Products' if products else 'Services'}</h2>
            <p>We offer comprehensive {business.industry.lower() if business else 'business'} solutions.</p>
            """
        elif "about" in template_name:
            return f"""
            <h1>About {business.business_name if business else 'Us'}</h1>
            <p>We are a professional {business.industry.lower() if business else 'service'} company dedicated to excellence.</p>
            """
        elif "contact" in template_name:
            contact = data.get("contact")
            return f"""
            <h1>Contact Us</h1>
            {f'<p><strong>Phone:</strong> {contact.phone}</p>' if contact and contact.phone else ''}
            {f'<p><strong>Email:</strong> {contact.email}</p>' if contact and contact.email else ''}
            {f'<p><strong>Address:</strong> {contact.address.to_single_line()}</p>' if contact and contact.address.street else ''}
            """
        elif "services" in template_name:
            if services:
                service_list = '\n'.join([f'<li>{service.name if hasattr(service, "name") else str(service)}</li>' for service in services[:10]])
                return f"""
                <h1>Our Services</h1>
                <p>We offer the following professional services:</p>
                <ul>{service_list}</ul>
                """
            else:
                return f"""
                <h1>Services</h1>
                <p>We provide professional {business.industry.lower() if business else 'business'} services. Please contact us for more information about our capabilities.</p>
                """
        elif "products" in template_name:
            if products:
                product_list = '\n'.join([f'<li>{product.name if hasattr(product, "name") else str(product)}</li>' for product in products[:10]])
                return f"""
                <h1>Our Products</h1>
                <p>We offer high-quality products including:</p>
                <ul>{product_list}</ul>
                """
            else:
                return f"""
                <h1>Products</h1>
                <p>We provide quality {business.industry.lower() if business else 'business'} products. Please contact us for our current catalog.</p>
                """
        elif "faq" in template_name:
            faqs = data.get("faqs", [])
            if faqs:
                faq_content = '\n'.join([f'<div><h3>{faq.question if hasattr(faq, "question") else str(faq)}</h3><p>{faq.answer if hasattr(faq, "answer") else "Please contact us for more information."}</p></div>' for faq in faqs[:5]])
                return f"""
                <h1>Frequently Asked Questions</h1>
                {faq_content}
                """
            else:
                return f"""
                <h1>Frequently Asked Questions</h1>
                <p>Have questions about our {business.industry.lower() if business else 'services'}? Contact us and we'll be happy to help!</p>
                """
        elif "privacy" in template_name:
            return f"""
            <h1>Privacy Policy</h1>
            <p>At {business.business_name if business else 'our company'}, we respect your privacy and are committed to protecting your personal information.</p>
            <p>Last updated: {data.get('current_year', '2024')}</p>
            """
        else:
            return f"<h1>{data.get('page_title', 'Page')}</h1><p>Content for this page is being generated.</p>"

    # Utility methods
    def _format_phone(self, phone: str) -> str:
        """Format phone number for display"""
        if not phone:
            return ""
        # Simple formatting - can be enhanced
        cleaned = "".join(filter(str.isdigit, phone))
        if len(cleaned) == 10:
            return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
        elif len(cleaned) == 11 and cleaned[0] == "1":
            return f"+1 ({cleaned[1:4]}) {cleaned[4:7]}-{cleaned[7:]}"
        return phone

    def _format_price(self, price: str) -> str:
        """Format price for display"""
        if not price:
            return "Contact for pricing"
        return price

    def _slugify(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        import re

        slug = re.sub(r"[^\w\s-]", "", text.lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

    def _truncate_words(self, text: str, count: int) -> str:
        """Truncate text to specified word count"""
        words = text.split()
        if len(words) <= count:
            return text
        return " ".join(words[:count]) + "..."
        
    def _date_filter(self, date_input, format_str="%Y-%m-%d"):
        """Format date string - supports 'now' keyword for current date"""
        from datetime import datetime
        
        if isinstance(date_input, str) and date_input.lower() == "now":
            return datetime.now().strftime(format_str)
        elif isinstance(date_input, datetime):
            return date_input.strftime(format_str)
        else:
            # Try to parse string as date
            try:
                date_obj = datetime.fromisoformat(str(date_input))
                return date_obj.strftime(format_str)
            except:
                return str(date_input)

    def _generate_company_story(self, config: ClientConfig) -> str:
        """Generate company story for about page"""
        return f"""
        {config.business.business_name} is a leading {config.business.industry.lower()} company 
        dedicated to providing exceptional service and quality results. With years of experience 
        in the industry, we have built a reputation for reliability, professionalism, and 
        customer satisfaction.
        """

    def _get_team_members(self, config: ClientConfig) -> List[Dict[str, str]]:
        """Get team members (placeholder for future enhancement)"""
        return []

    def _get_company_values(self, config: ClientConfig) -> List[str]:
        """Get company values"""
        return [
            "Quality Excellence",
            "Customer Satisfaction",
            "Professional Integrity",
            "Reliable Service",
        ]

    def _generate_maps_embed(self, address: str) -> str:
        """Generate Google Maps embed code"""
        if not address:
            return ""
        # Placeholder for Google Maps embed - would need API key
        return f'<div class="map-placeholder">Map for: {address}</div>'

    def _get_business_hours(self, config: ClientConfig) -> Dict[str, str]:
        """Get business hours (placeholder for future enhancement)"""
        return {
            "Monday - Friday": "9:00 AM - 5:00 PM",
            "Saturday": "9:00 AM - 2:00 PM",
            "Sunday": "Closed",
        }
