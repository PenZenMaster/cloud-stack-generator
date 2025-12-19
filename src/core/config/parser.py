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
    AddressConfig,
    BrandingConfig,
    CloudConfig,
    DeploymentConfig,
    ProductConfig,
    ServiceConfig,
    FAQItem,
    SocialMediaConfig,
    GoogleMapsConfig,
    PageConfig,
    CityPageConfig,
    CityImageConfig,
    PlaceOfInterest,
    CityFAQItem,
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
        
        # Parse cities data
        target_cities = client_data.get("target_cities", [])
        seo_content = client_data.get("seo_content", {})
        api_keys = client_data.get("api_keys", {})
        
        # Parse enhanced city pages
        city_pages = self._parse_city_pages_config(client_data)

        # Parse cloud deployment configuration
        cloud = self._parse_cloud_config(yaml_data)

        # Parse multi-deployment configuration (v3.2.0+)
        deployments = self._parse_deployments(yaml_data)

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
            city_pages=city_pages,
            target_cities=target_cities,
            seo_content=seo_content,
            api_keys=api_keys,
            cloud=cloud,
            deployments=deployments,
        )

        self.current_config = config
        return config

    def _parse_business_config(self, client_data: Dict[str, Any]) -> BusinessConfig:
        """Parse business configuration section"""
        # Parse enhanced business fields
        why_choose_us = client_data.get("why_choose_us", [])
        if isinstance(why_choose_us, str):
            # Convert single string to list
            why_choose_us = [why_choose_us]
        elif not isinstance(why_choose_us, list):
            why_choose_us = []
        
        company_stats = client_data.get("company_stats", {})
        if not isinstance(company_stats, dict):
            company_stats = {}
            
        return BusinessConfig(
            business_name=client_data.get("business_name", ""),
            domain=client_data.get("domain", ""),
            industry=client_data.get("industry", ""),
            description=client_data.get("description", ""),
            tagline=client_data.get("tagline", ""),
            hero_subtitle=client_data.get("hero_subtitle", ""),
            years_in_business=client_data.get("years_in_business", ""),
            company_overview=client_data.get("company_overview", ""),
            mission_statement=client_data.get("mission_statement", ""),
            service_guarantee=client_data.get("service_guarantee", ""),
            service_area_description=client_data.get("service_area_description", ""),
            why_choose_us=why_choose_us,
            company_stats=company_stats,
        )

    def _parse_contact_config(self, client_data: Dict[str, Any]) -> ContactConfig:
        """Parse contact configuration section"""
        contact_data = client_data.get("contact", {})
        if not isinstance(contact_data, dict):
            contact_data = {}

        # Handle address - could be string (legacy) or dict (new format)
        address_data = contact_data.get("address", "")
        if isinstance(address_data, dict):
            # New structured format
            address_config = AddressConfig(
                street=address_data.get("street", ""),
                city=address_data.get("city", ""),
                state=address_data.get("state", ""),
                zip_code=address_data.get("zip_code", ""),
                country=address_data.get("country", "United States")
            )
        else:
            # Legacy string format - convert to structured
            address_config = AddressConfig.from_single_line(str(address_data) if address_data else "")

        # Parse enhanced contact fields
        business_hours = contact_data.get("business_hours", {})
        if not isinstance(business_hours, dict):
            business_hours = {}
            
        # Parse additional locations
        additional_locations = []
        for loc_data in contact_data.get("additional_locations", []):
            if isinstance(loc_data, dict):
                additional_locations.append(AddressConfig(
                    street=loc_data.get("street", ""),
                    city=loc_data.get("city", ""),
                    state=loc_data.get("state", ""),
                    zip_code=loc_data.get("zip_code", ""),
                    country=loc_data.get("country", "United States")
                ))

        return ContactConfig(
            name=contact_data.get("name", ""),
            phone=contact_data.get("phone", ""),
            address=address_config,
            email=contact_data.get("email", ""),
            business_hours=business_hours,
            emergency_phone=contact_data.get("emergency_phone", ""),
            office_phone=contact_data.get("office_phone", ""),
            mobile_phone=contact_data.get("mobile_phone", ""),
            fax_number=contact_data.get("fax_number", ""),
            response_time_promise=contact_data.get("response_time_promise", ""),
            contact_preference=contact_data.get("contact_preference", ""),
            additional_locations=additional_locations,
        )

    def _parse_branding_config(self, client_data: Dict[str, Any]) -> BrandingConfig:
        """Parse branding configuration section"""
        branding_data = client_data.get("branding", {})
        if not isinstance(branding_data, dict):
            branding_data = {}

        return BrandingConfig(
            primary_color=branding_data.get("primary_color", "#007bff"),
            secondary_color=branding_data.get("secondary_color", "#6c757d"),
            body_background_color=branding_data.get("body_background_color", "#ffffff"),
            body_text_color=branding_data.get("body_text_color", "#333333"),
            footer_background_color=branding_data.get("footer_background_color", "#2c3e50"),
            footer_text_color=branding_data.get("footer_text_color", "#ffffff"),
            h1_text_color=branding_data.get("h1_text_color", "#2c3e50"),
            h2_text_color=branding_data.get("h2_text_color", "#34495e"),
            h3_text_color=branding_data.get("h3_text_color", "#34495e"),
            main_menu_text_color=branding_data.get("main_menu_text_color", "#ffffff"),
            font_family=branding_data.get("font_family", "Arial, sans-serif"),
            logo_url=branding_data.get("logo_url", ""),
            hero_background_image_url=branding_data.get("hero_background_image_url", ""),
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
            youtube=social_data.get("youtube", ""),
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

    def _parse_city_pages_config(self, client_data: Dict[str, Any]) -> List[CityPageConfig]:
        """Parse enhanced city pages configuration section"""
        city_pages_data = client_data.get("city_pages", [])
        if not isinstance(city_pages_data, list):
            return []

        city_pages = []
        for cp_data in city_pages_data:
            if not isinstance(cp_data, dict):
                continue

            try:
                # Parse city image
                image_data = cp_data.get("city_image", {})
                city_image = CityImageConfig(
                    image_url=image_data.get("image_url", ""),
                    alt_text=image_data.get("alt_text", ""),
                    caption=image_data.get("caption", ""),
                    credit=image_data.get("credit", ""),
                    source=image_data.get("source", "Wikipedia"),
                    embed_code=image_data.get("embed_code", ""),
                )

                # Parse places of interest
                places_of_interest = []
                for poi_data in cp_data.get("places_of_interest", []):
                    if isinstance(poi_data, dict) and poi_data.get("name"):
                        places_of_interest.append(
                            PlaceOfInterest(
                                name=poi_data.get("name", ""),
                                embed_url=poi_data.get("embed_url", "")
                            )
                        )

                # Parse city FAQ
                city_faq = []
                for faq_data in cp_data.get("city_faq", []):
                    if isinstance(faq_data, dict) and faq_data.get("question") and faq_data.get("answer"):
                        city_faq.append(
                            CityFAQItem(
                                question=faq_data.get("question", ""),
                                answer=faq_data.get("answer", "")
                            )
                        )

                # Create city page config
                city_page = CityPageConfig(
                    city_name=cp_data.get("city_name", ""),
                    state=cp_data.get("state", ""),
                    slug=cp_data.get("slug", ""),
                    title=cp_data.get("title", ""),
                    meta_description=cp_data.get("meta_description", ""),
                    primary_keyword=cp_data.get("primary_keyword", ""),
                    secondary_keywords=cp_data.get("secondary_keywords", []),
                    hero_title=cp_data.get("hero_title", ""),
                    breadcrumbs=cp_data.get("breadcrumbs", []),
                    about_city=cp_data.get("about_city", ""),
                    city_image=city_image,
                    seo_content_title=cp_data.get("seo_content_title", ""),
                    seo_content_body=cp_data.get("seo_content_body", ""),
                    places_of_interest=places_of_interest,
                    city_faq=city_faq,
                    featured_products=cp_data.get("featured_products", []),
                    city_map_embed=cp_data.get("city_map_embed", ""),
                    service_area_note=cp_data.get("service_area_note", ""),
                )

                city_pages.append(city_page)

            except Exception as e:
                # Skip invalid city page entries
                print(f"Warning: Skipping invalid city page entry: {e}")
                continue

        return city_pages

    def _parse_cloud_config(self, yaml_data: Dict[str, Any]) -> CloudConfig:
        """Parse cloud deployment configuration section"""
        cloud_data = yaml_data.get("cloud", {})
        if not isinstance(cloud_data, dict):
            return CloudConfig()

        return CloudConfig(
            # AWS credentials and settings
            aws_profile=cloud_data.get("aws_profile", ""),
            aws_region=cloud_data.get("aws_region", "us-east-1"),

            # S3 and deployment settings
            bucket_name=cloud_data.get("bucket_name", ""),
            deployment_mode=cloud_data.get("deployment_mode", "s3"),
            deployment_url=cloud_data.get("deployment_url", ""),

            # CloudFront settings
            distribution_id=cloud_data.get("distribution_id", ""),
            custom_domain=cloud_data.get("custom_domain", ""),
            auto_invalidate_cache=cloud_data.get("auto_invalidate_cache", True),

            # SEO and backlink configuration
            site_type=cloud_data.get("site_type", "main_site"),
            main_site_url=cloud_data.get("main_site_url", ""),
            allow_indexing=cloud_data.get("allow_indexing", True),
            meta_tags=cloud_data.get("meta_tags", {}),

            # Caching configuration
            html_cache_control=cloud_data.get("html_cache_control", "max-age=3600"),
            asset_cache_control=cloud_data.get("asset_cache_control", "max-age=31536000"),

            # Website configuration
            index_document=cloud_data.get("index_document", "index.html"),
            error_document=cloud_data.get("error_document", "404.html"),

            # Deployment history
            last_deployment=cloud_data.get("last_deployment", ""),
        )

    def _parse_deployments(self, yaml_data: Dict[str, Any]) -> List[DeploymentConfig]:
        """Parse deployments array (v3.2.0+ multi-deployment support)"""
        deployments_data = yaml_data.get("deployments", [])
        if not isinstance(deployments_data, list):
            return []

        deployments = []
        for deployment_item in deployments_data:
            if not isinstance(deployment_item, dict):
                continue

            try:
                deployment = DeploymentConfig(
                    deployment_id=deployment_item.get("deployment_id", ""),
                    bucket=deployment_item.get("bucket", ""),
                    directory=deployment_item.get("directory", ""),
                    region=deployment_item.get("region", "us-east-1"),
                    mode=deployment_item.get("mode", "s3"),
                    cloudfront_distribution_id=deployment_item.get("cloudfront_distribution_id"),
                    cloudfront_domain=deployment_item.get("cloudfront_domain"),
                    last_deployed=deployment_item.get("last_deployed"),
                    deployment_url=deployment_item.get("deployment_url"),
                    meta_tags=deployment_item.get("meta_tags", {}),
                )
                deployments.append(deployment)
            except Exception as e:
                print(f"Warning: Skipping invalid deployment entry: {e}")
                continue

        return deployments

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
                # Enhanced business fields
                "tagline": config.business.tagline,
                "hero_subtitle": config.business.hero_subtitle,
                "years_in_business": config.business.years_in_business,
                "company_overview": config.business.company_overview,
                "mission_statement": config.business.mission_statement,
                "service_guarantee": config.business.service_guarantee,
                "service_area_description": config.business.service_area_description,
                "why_choose_us": config.business.why_choose_us,
                "company_stats": config.business.company_stats,
                "contact": {
                    "name": config.contact.name,
                    "phone": config.contact.phone,
                    "address": {
                        "street": config.contact.address.street,
                        "city": config.contact.address.city,
                        "state": config.contact.address.state,
                        "zip_code": config.contact.address.zip_code,
                        "country": config.contact.address.country,
                    },
                    "email": config.contact.email,
                    # Enhanced contact fields
                    "business_hours": config.contact.business_hours,
                    "emergency_phone": config.contact.emergency_phone,
                    "office_phone": config.contact.office_phone,
                    "mobile_phone": config.contact.mobile_phone,
                    "fax_number": config.contact.fax_number,
                    "response_time_promise": config.contact.response_time_promise,
                    "contact_preference": config.contact.contact_preference,
                    "additional_locations": [
                        {
                            "street": loc.street,
                            "city": loc.city,
                            "state": loc.state,
                            "zip_code": loc.zip_code,
                            "country": loc.country,
                        } for loc in config.contact.additional_locations
                    ],
                },
                "branding": {
                    "primary_color": config.branding.primary_color,
                    "secondary_color": config.branding.secondary_color,
                    "body_background_color": config.branding.body_background_color,
                    "body_text_color": config.branding.body_text_color,
                    "footer_background_color": config.branding.footer_background_color,
                    "footer_text_color": config.branding.footer_text_color,
                    "h1_text_color": config.branding.h1_text_color,
                    "h2_text_color": config.branding.h2_text_color,
                    "h3_text_color": config.branding.h3_text_color,
                    "main_menu_text_color": config.branding.main_menu_text_color,
                    "font_family": config.branding.font_family,
                    "logo_url": config.branding.logo_url,
                    "hero_background_image_url": config.branding.hero_background_image_url,
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
            
        # Add cities data
        if config.target_cities:
            yaml_data["client"]["target_cities"] = config.target_cities
            
        if config.seo_content:
            yaml_data["client"]["seo_content"] = config.seo_content
            
        if config.api_keys:
            yaml_data["client"]["api_keys"] = config.api_keys
            
        # Add enhanced city pages data
        if config.city_pages:
            city_pages_data = []
            for cp in config.city_pages:
                city_page_dict = {
                    "city_name": cp.city_name,
                    "state": cp.state,
                    "slug": cp.slug,
                    "title": cp.title,
                    "meta_description": cp.meta_description,
                    "primary_keyword": cp.primary_keyword,
                    "secondary_keywords": cp.secondary_keywords,
                    "hero_title": cp.hero_title,
                    "breadcrumbs": cp.breadcrumbs,
                    "about_city": cp.about_city,
                    "city_image": {
                        "image_url": cp.city_image.image_url,
                        "alt_text": cp.city_image.alt_text,
                        "caption": cp.city_image.caption,
                        "credit": cp.city_image.credit,
                        "source": cp.city_image.source,
                        "embed_code": cp.city_image.embed_code,
                    },
                    "seo_content_title": cp.seo_content_title,
                    "seo_content_body": cp.seo_content_body,
                    "places_of_interest": [
                        {"name": poi.name, "embed_url": poi.embed_url}
                        for poi in cp.places_of_interest
                    ],
                    "city_faq": [
                        {"question": faq.question, "answer": faq.answer}
                        for faq in cp.city_faq
                    ],
                    "featured_products": cp.featured_products,
                    "city_map_embed": cp.city_map_embed,
                    "service_area_note": cp.service_area_note,
                }
                city_pages_data.append(city_page_dict)
            yaml_data["client"]["city_pages"] = city_pages_data

        # Add cloud deployment configuration
        if config.cloud:
            cloud_dict = {
                "aws_profile": config.cloud.aws_profile,
                "aws_region": config.cloud.aws_region,
                "bucket_name": config.cloud.bucket_name,
                "deployment_mode": config.cloud.deployment_mode,
                "deployment_url": config.cloud.deployment_url,
                "distribution_id": config.cloud.distribution_id,
                "custom_domain": config.cloud.custom_domain,
                "auto_invalidate_cache": config.cloud.auto_invalidate_cache,
                "site_type": config.cloud.site_type,
                "main_site_url": config.cloud.main_site_url,
                "allow_indexing": config.cloud.allow_indexing,
                "meta_tags": config.cloud.meta_tags,
                "html_cache_control": config.cloud.html_cache_control,
                "asset_cache_control": config.cloud.asset_cache_control,
                "index_document": config.cloud.index_document,
                "error_document": config.cloud.error_document,
            }
            if config.cloud.last_deployment:
                cloud_dict["last_deployment"] = config.cloud.last_deployment
            yaml_data["cloud"] = cloud_dict

        # Add deployments array (v3.2.0+ multi-deployment support)
        if config.deployments:
            deployments_data = []
            for deployment in config.deployments:
                deployment_dict = {
                    "deployment_id": deployment.deployment_id,
                    "bucket": deployment.bucket,
                    "directory": deployment.directory,
                    "region": deployment.region,
                    "mode": deployment.mode,
                }

                # Optional fields - only include if set
                if deployment.cloudfront_distribution_id:
                    deployment_dict["cloudfront_distribution_id"] = deployment.cloudfront_distribution_id
                if deployment.cloudfront_domain:
                    deployment_dict["cloudfront_domain"] = deployment.cloudfront_domain
                if deployment.last_deployed:
                    deployment_dict["last_deployed"] = deployment.last_deployed
                if deployment.deployment_url:
                    deployment_dict["deployment_url"] = deployment.deployment_url
                if deployment.meta_tags:
                    deployment_dict["meta_tags"] = deployment.meta_tags

                deployments_data.append(deployment_dict)

            yaml_data["deployments"] = deployments_data

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
    config = parser.parse_yaml_file(file_path)
    # Store the absolute path to the config file for asset resolution
    config.config_file_path = str(Path(file_path).resolve())
    return config


def save_config_to_file(config: ClientConfig, file_path: str) -> bool:
    """Save configuration to YAML file"""
    parser = ConfigParser()
    return parser.save_yaml_file(config, file_path)


def convert_yaml_to_config(yaml_data: Dict[str, Any]) -> ClientConfig:
    """Convert YAML dictionary to ClientConfig"""
    parser = ConfigParser()
    return parser.parse_yaml_dict(yaml_data)
