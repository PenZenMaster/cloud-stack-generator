"""
Filename: city_page_generator.py
Path: E:\\projects\\cloud-stack-generator\\src\\core\\generators\\city_page_generator.py
Description: City page generator module based on Location Page Generator template
Generates SEO-optimized city landing pages with Google Maps and Wikipedia integration

Version: 1.0.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

import os
from typing import Dict, Any, List, Optional
from jinja2 import Environment, FileSystemLoader, Template
from datetime import datetime
from ..config.models import ClientConfig
from ..utils.google_maps_api import GoogleMapsAPI
from ..utils.wikipedia_api import WikipediaAPI


class CityPageGenerator:
    """Generator for SEO-optimized city landing pages"""
    
    def __init__(self, config: ClientConfig):
        """
        Initialize city page generator
        
        Args:
            config: Client configuration with business info and cities data
        """
        self.config = config
        self.google_maps_api = None
        self.wikipedia_api = WikipediaAPI() if WikipediaAPI else None
        
        # Initialize Google Maps API if key is available
        google_maps_key = config.api_keys.get("google_maps")
        if google_maps_key and GoogleMapsAPI:
            try:
                self.google_maps_api = GoogleMapsAPI(google_maps_key)
            except ValueError:
                self.google_maps_api = None
        
        # Setup Jinja2 environment
        template_dir = os.path.join(os.path.dirname(__file__), "..", "..", "templates")
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    def generate_city_page(self, city_name: str, **options) -> Dict[str, Any]:
        """
        Generate a complete city page
        
        Args:
            city_name: Name of the city to generate page for
            **options: Additional options for page generation
            
        Returns:
            Dictionary with HTML content and metadata
        """
        # Prepare template variables
        template_vars = self._prepare_template_variables(city_name, **options)
        
        # Load and render template
        template = self.jinja_env.get_template("pages/city_page.html")
        html_content = template.render(**template_vars)
        
        # Generate metadata
        metadata = self._generate_page_metadata(city_name, template_vars)
        
        return {
            "html_content": html_content,
            "metadata": metadata,
            "city_name": city_name,
            "template_vars": template_vars
        }
    
    def _prepare_template_variables(self, city_name: str, **options) -> Dict[str, Any]:
        """
        Prepare all template variables for city page generation
        
        Args:
            city_name: Name of the city
            **options: Additional options
            
        Returns:
            Dictionary of template variables
        """
        # Basic business information
        business = self.config.business
        contact = self.config.contact
        branding = self.config.branding
        
        # Determine focus keyword (from SEO content or default)
        focus_keyword = options.get("focus_keyword") or business.industry or "services"
        
        # Page title and meta information
        page_title = f"{focus_keyword.title()} in {city_name}"
        meta_description = f"Professional {focus_keyword.lower()} services in {city_name}. {business.description[:100]}..."
        
        # Get city-specific SEO content
        seo_content = self.config.seo_content
        
        # Google Maps integration
        maps_data = self._get_maps_data(city_name)
        
        # Wikipedia integration
        wikipedia_data = self._get_wikipedia_data(city_name)
        
        # Services information
        services_data = self._prepare_services_data()
        
        # Template variables
        template_vars = {
            # Page metadata
            "page_title": page_title,
            "meta_description": meta_description,
            "primary_keyword": focus_keyword,
            "secondary_keywords": [business.business_name.lower(), city_name.lower(), "local business"],
            "location": city_name,
            "page_url": options.get("page_url", ""),
            
            # Business information
            "business_name": business.business_name,
            "business_description": business.description,
            "service_category": business.industry or "Professional Services",
            
            # Contact information
            "phone": contact.phone,
            "email": contact.email,
            "street_address": contact.address.split(",")[0].strip() if contact.address else "",
            "address_locality": city_name.split(",")[0].strip(),
            "address_region": city_name.split(",")[1].strip() if "," in city_name else "",
            "postal_code": "",  # Would need to be extracted/configured
            "address_country": "US",
            "hq_address": contact.address,
            "website_url": f"https://{business.domain}" if business.domain else "",
            "hq_map_url": options.get("hq_map_url", "#"),
            
            # Branding
            "primary_color": branding.primary_color or "#007bff",
            "accent_color": branding.accent_color or "#28a745",
            "css_file": options.get("css_file", "style.css"),
            
            # Navigation URLs
            "home_url": options.get("home_url", "/"),
            "services_url": options.get("services_url", "/services/"),
            "about_url": options.get("about_url", "/about/"),
            "contact_url": options.get("contact_url", "/contact/"),
            
            # Content sections
            "intro_paragraph": self._generate_intro_paragraph(city_name, focus_keyword),
            "why_us_paragraph": self._generate_why_us_paragraph(city_name, focus_keyword),
            "local_paragraph": self._generate_local_paragraph(city_name),
            "cta_paragraph": self._generate_cta_paragraph(city_name, focus_keyword),
            
            # SEO content from Cities tab
            "neighborhoods": seo_content.get("neighborhoods", ""),
            "pain_points": seo_content.get("pain_points", ""),
            "seasonal_factors": seo_content.get("pain_points", ""),  # Can be expanded later
            "service_process": seo_content.get("directions", ""),
            
            # Case studies and testimonials
            "case_studies": self._parse_case_studies(seo_content.get("case_studies", "")),
            "testimonial": self._parse_testimonial(seo_content.get("testimonial", "")),
            
            # Services
            "services": services_data,
            
            # Maps and directions
            **maps_data,
            
            # Wikipedia data
            **wikipedia_data,
            
            # Utility
            "current_year": datetime.now().year,
            "featured_image": wikipedia_data.get("wikipedia_image", {}).get("image_url", ""),
        }
        
        return template_vars
    
    def _get_maps_data(self, city_name: str) -> Dict[str, Any]:
        """Get Google Maps data for the city"""
        maps_data = {
            "map_embed_url": "",
            "directions_embed_url": ""
        }
        
        if self.google_maps_api:
            try:
                # Generate place embed
                place_embed = self.google_maps_api.create_place_embed(city_name)
                maps_data["map_embed_url"] = place_embed["url"]
                
                # Generate directions embed if HQ address is available
                if self.config.contact.address:
                    directions_embed = self.google_maps_api.create_directions_embed(
                        city_name, self.config.contact.address
                    )
                    maps_data["directions_embed_url"] = directions_embed["url"]
                    
            except Exception:
                # Silently handle API errors
                pass
        
        # Check if city has manual embed in city_data
        city_maps = self.config.google_maps.cities
        if city_name in city_maps:
            city_data = city_maps[city_name]
            if city_data.get("embed_code"):
                # Extract URL from manual embed code (basic parsing)
                import re
                url_match = re.search(r'src=["\']([^"\']*)["\']', city_data["embed_code"])
                if url_match:
                    maps_data["map_embed_url"] = url_match.group(1)
        
        return maps_data
    
    def _get_wikipedia_data(self, city_name: str) -> Dict[str, Any]:
        """Get Wikipedia data for the city"""
        wikipedia_data = {"wikipedia_image": None}
        
        if self.wikipedia_api:
            try:
                city_info = self.wikipedia_api.get_city_image_info(city_name)
                wikipedia_data["wikipedia_image"] = {
                    "image_url": city_info["image_url"],
                    "source_url": city_info["source_url"],
                    "attribution": city_info["attribution"],
                    "alt_text": city_info["alt_text"]
                }
            except Exception:
                # Silently handle API errors
                pass
        
        return wikipedia_data
    
    def _prepare_services_data(self) -> List[Dict[str, str]]:
        """Prepare services data for template"""
        services = []
        
        # Add services from config
        for service in self.config.services:
            services.append({
                "name": service.name,
                "description": service.description
            })
        
        # Add products as services if no services defined
        if not services:
            for product in self.config.products:
                services.append({
                    "name": product.name,
                    "description": product.description
                })
        
        # Fallback to generic services
        if not services:
            industry = self.config.business.industry or "Professional Services"
            services = [
                {"name": f"Expert {industry}", "description": ""},
                {"name": "Quality Consultation", "description": ""},
                {"name": "Professional Installation", "description": ""},
                {"name": "Ongoing Support", "description": ""}
            ]
        
        return services
    
    def _generate_intro_paragraph(self, city_name: str, focus_keyword: str) -> str:
        """Generate introduction paragraph"""
        business_name = self.config.business.business_name
        return (f"Professional {focus_keyword.lower()} services in {city_name} from {business_name}. "
                f"We provide reliable, high-quality solutions with guaranteed satisfaction and lasting results.")
    
    def _generate_why_us_paragraph(self, city_name: str, focus_keyword: str) -> str:
        """Generate why choose us paragraph"""
        return (f"Our proven {focus_keyword.lower()} process includes thorough consultation, expert implementation, "
                f"and ongoing support using top-tier materials and industry best practices.")
    
    def _generate_local_paragraph(self, city_name: str) -> str:
        """Generate local area paragraph"""
        return (f"Discover the best of {city_name} while we work on your project. "
                f"Our efficient service means you can enjoy local attractions, dining, and activities "
                f"while we transform your space.")
    
    def _generate_cta_paragraph(self, city_name: str, focus_keyword: str) -> str:
        """Generate call-to-action paragraph"""
        return (f"Ready to experience the best {focus_keyword.lower()} services in {city_name}? "
                f"Contact us today for a free consultation and personalized quote.")
    
    def _parse_case_studies(self, case_studies_text: str) -> List[Dict[str, str]]:
        """Parse case studies from SEO content"""
        if not case_studies_text:
            return []
        
        # Simple parsing - can be enhanced
        studies = []
        lines = case_studies_text.split("\n")
        for line in lines:
            if line.strip():
                studies.append({
                    "title": "Recent Project",
                    "description": line.strip(),
                    "results": ""
                })
        
        return studies[:3]  # Limit to 3 case studies
    
    def _parse_testimonial(self, testimonial_text: str) -> Optional[Dict[str, str]]:
        """Parse testimonial from SEO content"""
        if not testimonial_text:
            return None
        
        # Simple parsing - can be enhanced to extract name, location, etc.
        return {
            "content": testimonial_text.strip(),
            "author": "Satisfied Customer",
            "location": ""
        }
    
    def _generate_page_metadata(self, city_name: str, template_vars: Dict[str, Any]) -> Dict[str, Any]:
        """Generate page metadata"""
        return {
            "title": template_vars["page_title"],
            "description": template_vars["meta_description"],
            "keywords": [template_vars["primary_keyword"]] + template_vars["secondary_keywords"],
            "city": city_name,
            "focus_keyword": template_vars["primary_keyword"],
            "generated_at": datetime.now().isoformat(),
            "word_count": len(template_vars.get("intro_paragraph", "").split()) + 
                         len(template_vars.get("why_us_paragraph", "").split()) +
                         len(template_vars.get("local_paragraph", "").split()),
            "has_maps": bool(template_vars.get("map_embed_url")),
            "has_wikipedia_image": bool(template_vars.get("wikipedia_image")),
            "services_count": len(template_vars.get("services", []))
        }
    
    def generate_multiple_cities(self, city_list: List[str], **options) -> Dict[str, Dict[str, Any]]:
        """
        Generate pages for multiple cities
        
        Args:
            city_list: List of city names
            **options: Generation options
            
        Returns:
            Dictionary mapping city names to page data
        """
        results = {}
        
        for city in city_list:
            if city.strip():
                try:
                    results[city] = self.generate_city_page(city.strip(), **options)
                except Exception as e:
                    results[city] = {
                        "error": str(e),
                        "city_name": city,
                        "html_content": "",
                        "metadata": {}
                    }
        
        return results
    
    def save_city_page(self, city_name: str, output_dir: str, **options) -> str:
        """
        Generate and save city page to file
        
        Args:
            city_name: Name of the city
            output_dir: Output directory
            **options: Generation options
            
        Returns:
            Path to saved file
        """
        # Generate page
        page_data = self.generate_city_page(city_name, **options)
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        safe_city_name = city_name.lower().replace(" ", "-").replace(",", "").replace(".", "")
        filename = f"{safe_city_name}.html"
        file_path = os.path.join(output_dir, filename)
        
        # Save file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(page_data["html_content"])
        
        return file_path