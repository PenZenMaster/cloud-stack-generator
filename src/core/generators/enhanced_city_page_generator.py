"""
Enhanced City Page Generator with Template System
Path: E:\\projects\\cloud-stack-generator\\src\\core\\generators\\enhanced_city_page_generator.py

Description:
Generates city pages using the new template management system.
Supports multiple templates and template selection.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-18

Last Modified Date:
2025-09-18

Comments:
* v1.00 - Initial enhanced city page generator with template selection
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime

from ..templates.template_manager import TemplateManager, TemplateType
from ..config.models import ClientConfig, CityPageConfig


class EnhancedCityPageGenerator:
    """Enhanced city page generator with template system support"""

    def __init__(self, config: ClientConfig, template_id: Optional[str] = None):
        self.config = config
        self.template_manager = TemplateManager()
        self.selected_template_id = template_id or "seo_authority_city"

    def set_template(self, template_id: str) -> bool:
        """
        Set the template to use for generation

        Args:
            template_id: ID of the template to use

        Returns:
            True if template exists and is valid, False otherwise
        """
        template_metadata = self.template_manager.get_template_by_id(template_id)
        if template_metadata and template_metadata.type == TemplateType.CITY_PAGE:
            self.selected_template_id = template_id
            return True
        return False

    def get_available_templates(self) -> List[Dict[str, Any]]:
        """
        Get list of available city page templates

        Returns:
            List of template metadata dictionaries
        """
        templates = self.template_manager.get_available_templates(TemplateType.CITY_PAGE)
        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description,
                "variant": t.variant.value,
                "features": t.features,
                "version": t.version
            }
            for t in templates
        ]

    def validate_city_data(self, city_page: CityPageConfig) -> tuple[bool, List[str]]:
        """
        Validate city page data against selected template requirements

        Args:
            city_page: City page configuration

        Returns:
            Tuple of (is_valid, error_messages)
        """
        # Build template context
        context = self._build_template_context(city_page)

        # Validate against template requirements
        return self.template_manager.validate_template_data(self.selected_template_id, context)

    def generate_city_page(self, city_page: CityPageConfig, output_dir: str) -> Dict[str, Any]:
        """
        Generate a single enhanced city page using selected template

        Args:
            city_page: City page configuration
            output_dir: Output directory for generated files

        Returns:
            Dictionary with generation results
        """
        try:
            # Validate data first
            is_valid, errors = self.validate_city_data(city_page)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Data validation failed: {', '.join(errors)}",
                    "file_path": None
                }

            # Load the selected template
            template = self.template_manager.load_template(self.selected_template_id)
            if not template:
                return {
                    "success": False,
                    "error": f"Template {self.selected_template_id} not found",
                    "file_path": None
                }

            # Prepare template context
            context = self._build_template_context(city_page)

            # Render the template
            html_content = template.render(**context)

            # Write to file
            output_path = Path(output_dir) / f"{city_page.slug}.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Get template metadata for result
            template_metadata = self.template_manager.get_template_by_id(self.selected_template_id)

            return {
                "success": True,
                "file_path": str(output_path),
                "city_name": city_page.city_name,
                "template_used": {
                    "id": self.selected_template_id,
                    "name": template_metadata.name if template_metadata else "Unknown",
                    "variant": template_metadata.variant.value if template_metadata else "unknown"
                },
                "content_stats": {
                    "html_size": len(html_content),
                    "word_count": len(html_content.split()),
                    "has_seo_content": bool(city_page.seo_content_body),
                    "places_count": len(city_page.places_of_interest),
                    "faq_count": len(city_page.city_faq)
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": None
            }

    def generate_multiple_city_pages(self, city_pages: List[CityPageConfig],
                                   output_dir: str) -> Dict[str, Any]:
        """
        Generate multiple city pages

        Args:
            city_pages: List of city page configurations
            output_dir: Output directory for generated files

        Returns:
            Dictionary with generation results for all pages
        """
        results = {
            "total_pages": len(city_pages),
            "successful": 0,
            "failed": 0,
            "pages": [],
            "template_used": self.selected_template_id,
            "errors": []
        }

        for city_page in city_pages:
            result = self.generate_city_page(city_page, output_dir)
            results["pages"].append(result)

            if result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"{city_page.city_name}: {result['error']}")

        return results

    def preview_template(self, city_page: CityPageConfig) -> Optional[str]:
        """
        Generate preview HTML for a city page with the selected template

        Args:
            city_page: City page configuration

        Returns:
            Preview HTML string or None if error
        """
        try:
            from ..templates.template_preview import TemplatePreviewGenerator

            preview_generator = TemplatePreviewGenerator(self.template_manager)

            # Use actual city data for preview
            context = self._build_template_context(city_page)

            return preview_generator.generate_preview_html(self.selected_template_id, context)

        except Exception as e:
            print(f"Error generating preview: {e}")
            return None

    def _build_template_context(self, city_page: CityPageConfig) -> Dict[str, Any]:
        """
        Build template context from city page and configuration data

        Args:
            city_page: City page configuration

        Returns:
            Dictionary with template context data
        """
        context = {
            "city_page": {
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
                    "embed_code": getattr(city_page.city_image, 'embed_code', ''),
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
            },
            "business": {
                "business_name": self.config.business.business_name,
                "industry": self.config.business.industry,
                "description": self.config.business.description,
                "website_url": self.config.business.website_url,
                "hours": getattr(self.config.business, 'hours', 'Mo-Fr 08:00-17:00'),
            },
            "contact": {
                "phone": self.config.contact.phone,
                "email": self.config.contact.email,
                "address": {
                    "street": self.config.contact.address.street,
                    "city": self.config.contact.address.city,
                    "state": self.config.contact.address.state,
                    "zip_code": self.config.contact.address.zip_code,
                    "country": self.config.contact.address.country,
                }
            },
            "branding": {
                "primary_color": self.config.branding.primary_color,
                "secondary_color": self.config.branding.secondary_color,
                "accent_color": self.config.branding.accent_color,
                "logo_url": self.config.branding.logo_url,
                "font_family": self.config.branding.font_family,
            },
            "services": [
                {
                    "name": service.name,
                    "description": service.description,
                    "features": service.features,
                    "pricing": getattr(service, 'pricing', None),
                }
                for service in self.config.services
            ],
            "products": [
                {
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "features": product.features,
                    "categories": product.categories,
                }
                for product in self.config.products
            ],
            # Template system metadata
            "template_info": {
                "id": self.selected_template_id,
                "generated_at": datetime.now().isoformat(),
                "generator_version": "2.1.0"
            },
            # Helper variables
            "page_url": f"https://{self.config.business.website_url}/{city_page.slug}",
            "current_year": datetime.now().year,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        return context

    def get_template_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the currently selected template

        Returns:
            Dictionary with template information or None if not found
        """
        metadata = self.template_manager.get_template_by_id(self.selected_template_id)
        if not metadata:
            return None

        return {
            "id": metadata.id,
            "name": metadata.name,
            "description": metadata.description,
            "type": metadata.type.value,
            "variant": metadata.variant.value,
            "version": metadata.version,
            "author": metadata.author,
            "features": metadata.features,
            "required_data": metadata.required_data,
            "optional_data": metadata.optional_data,
            "compatibility": metadata.compatibility
        }