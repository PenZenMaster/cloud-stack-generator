# src/core/generators/page_generator.py
"""
Page Generator - Multi-Page Website Coordination
Sprint 2 Week 2 - Days 7-8 Implementation

Coordinates HTML and CSS generation for complete multi-page websites
with navigation, internal linking, and SEO optimization.
"""

from typing import List, Optional, Callable
from pathlib import Path
import shutil
from datetime import datetime

from .html_generator import HTMLGenerator
from .css_generator import CSSGenerator
from ..config.models import ClientConfig
from ..utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


class GenerationResult:
    """Result of website generation process"""

    def __init__(self):
        self.success = False
        self.pages_generated = 0
        self.total_pages = 0
        self.output_directory = ""
        self.generation_time = 0.0
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.generated_files: List[str] = []

    def add_error(self, message: str):
        self.errors.append(message)
        self.success = False

    def add_warning(self, message: str):
        self.warnings.append(message)

    def add_generated_file(self, file_path: str):
        self.generated_files.append(file_path)


class PageGenerator:
    """Coordinates complete website generation"""

    def __init__(
        self, template_dir: str = "src/templates", output_base_dir: str = "output"
    ):
        self.html_generator = HTMLGenerator(template_dir)
        self.css_generator = CSSGenerator()
        self.template_dir = Path(template_dir)
        self.output_base_dir = Path(output_base_dir)

        # Ensure output directory exists
        self.output_base_dir.mkdir(exist_ok=True)

    def generate_complete_website(
        self, config: ClientConfig, progress_callback: Optional[Callable] = None
    ) -> GenerationResult:
        """Generate complete website from configuration"""
        result = GenerationResult()
        start_time = datetime.now()

        try:
            # Validate configuration before generation
            validation_errors = self._validate_config(config)
            if validation_errors:
                for error in validation_errors:
                    result.add_error(error)
                logger.error(
                    "Configuration validation failed",
                    extra={"extra_fields": {"errors": validation_errors}},
                )
                return result

            # Create output directory
            output_dir = self._create_output_directory(config)
            result.output_directory = str(output_dir)

            # Calculate total pages for progress tracking
            pages_to_generate = self._calculate_total_pages(config)
            result.total_pages = pages_to_generate

            if progress_callback:
                progress_callback(
                    0, pages_to_generate, "Starting website generation..."
                )

            # Generate CSS first
            self._generate_css_files(config, output_dir, result)

            if progress_callback:
                progress_callback(1, pages_to_generate, "Generated CSS files")

            # Generate main pages
            self._generate_main_pages(config, output_dir, result, progress_callback)

            # Generate individual product pages
            if config.products:
                self._generate_product_pages(
                    config, output_dir, result, progress_callback
                )

            # Generate product comparison guide pages (resource sites with categories)
            if getattr(config, "product_categories", []):
                self._generate_product_comparison_pages(
                    config, output_dir, result, progress_callback
                )

            # Generate individual service pages
            if config.services:
                self._generate_service_pages(
                    config, output_dir, result, progress_callback
                )

            # Generate city pages
            if config.city_pages:
                self._generate_city_pages(config, output_dir, result, progress_callback)

            # Generate additional files
            self._generate_additional_files(config, output_dir, result)

            # Copy static assets
            self._copy_static_assets(config, output_dir, result)

            result.success = len(result.errors) == 0
            result.generation_time = (datetime.now() - start_time).total_seconds()

            if progress_callback:
                if result.success:
                    progress_callback(
                        result.total_pages,
                        result.total_pages,
                        f"Website generated successfully! ({result.pages_generated} pages)",
                    )
                else:
                    progress_callback(
                        result.pages_generated,
                        result.total_pages,
                        f"Generation completed with {len(result.errors)} errors",
                    )

        except Exception as e:
            result.add_error(f"Critical error during generation: {str(e)}")
            result.generation_time = (datetime.now() - start_time).total_seconds()

            if progress_callback:
                progress_callback(0, result.total_pages, f"Generation failed: {str(e)}")

        return result

    def _create_output_directory(self, config: ClientConfig) -> Path:
        """Create output directory for the website"""
        # Use the exact directory selected by the user
        output_dir = self.output_base_dir

        output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (output_dir / "css").mkdir(exist_ok=True)
        (output_dir / "js").mkdir(exist_ok=True)
        (output_dir / "images").mkdir(exist_ok=True)

        if config.products or getattr(config, "product_categories", []):
            (output_dir / "products").mkdir(exist_ok=True)

        if config.services:
            (output_dir / "services").mkdir(exist_ok=True)

        if config.city_pages:
            (output_dir / "locations").mkdir(exist_ok=True)

        return output_dir

    def _validate_config(self, config: ClientConfig) -> List[str]:
        """
        Validate configuration before generation

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Validate backlink site configuration
        if hasattr(config, "cloud") and config.cloud:
            if config.cloud.site_type == "backlink_site":
                main_site_url = getattr(config.cloud, "main_site_url", "")
                if not main_site_url or not main_site_url.strip():
                    errors.append(
                        "Main Site URL is required when site_type is 'backlink_site'. "
                        "Please specify the URL of your main production site for canonical tags."
                    )
                elif not main_site_url.startswith(("http://", "https://")):
                    errors.append(
                        f"Main Site URL must start with http:// or https://. Got: {main_site_url}"
                    )

        return errors

    def _calculate_total_pages(self, config: ClientConfig) -> int:
        """Calculate total number of pages to be generated"""
        # Main pages: home, about, contact, faq
        total = 4

        # Services overview page + individual service pages
        if config.services:
            total += 1 + len(config.services)

        # Products overview page + individual product pages + category comparison pages
        product_categories = getattr(config, "product_categories", [])
        if config.products or product_categories:
            total += 1  # products.html hub
        if config.products:
            total += len(config.products)
        if product_categories:
            total += len(product_categories)

        # City pages
        if config.city_pages:
            total += len(config.city_pages)

        return total

    def generate_css(self, config):
        """Generate main CSS content based on the configuration"""
        # Example implementation
        return f"/* Main CSS for {config.business.business_name} */\nbody {{ font-family: Arial, sans-serif; }}"

    def _generate_css_files(
        self, config: ClientConfig, output_dir: Path, result: GenerationResult
    ):
        """Generate CSS files"""
        try:
            # Main stylesheet
            main_css = self.css_generator.generate_css(config)
            css_file = output_dir / "css" / "style.css"

            with open(css_file, "w", encoding="utf-8") as f:
                f.write(main_css)

            result.add_generated_file(str(css_file))

            # Generate print stylesheet
            print_css = self._generate_print_css()
            print_css_file = output_dir / "css" / "print.css"

            with open(print_css_file, "w", encoding="utf-8") as f:
                f.write(print_css)

            result.add_generated_file(str(print_css_file))

        except Exception as e:
            result.add_error(f"Error generating CSS files: {str(e)}")

    def _generate_main_pages(
        self,
        config: ClientConfig,
        output_dir: Path,
        result: GenerationResult,
        progress_callback: Optional[Callable] = None,
    ):
        """Generate main website pages"""
        pages = [
            ("index.html", "homepage", self.html_generator.generate_homepage),
            ("about.html", "about page", self.html_generator.generate_about_page),
            ("contact.html", "contact page", self.html_generator.generate_contact_page),
            ("faq.html", "FAQ page", self.html_generator.generate_faq_page),
            (
                "privacy-policy.html",
                "privacy policy page",
                self.html_generator.generate_privacy_page,
            ),
        ]

        # Add services overview page (always generate to match navigation)
        pages.append(
            (
                "services.html",
                "services page",
                self.html_generator.generate_services_page,
            )
        )

        # Add products overview page if products or product categories exist
        if config.products or getattr(config, "product_categories", []):
            pages.append(
                (
                    "products.html",
                    "products page",
                    self.html_generator.generate_products_page,
                )
            )

        for i, (filename, page_type, generator_func) in enumerate(pages):
            try:
                html_content = generator_func(config)
                page_file = output_dir / filename

                with open(page_file, "w", encoding="utf-8") as f:
                    f.write(html_content)

                result.add_generated_file(str(page_file))
                result.pages_generated += 1

                if progress_callback:
                    progress_callback(
                        result.pages_generated,
                        result.total_pages,
                        f"Generated {page_type}",
                    )

            except Exception as e:
                result.add_error(f"Error generating {page_type}: {str(e)}")

    def _generate_product_pages(
        self,
        config: ClientConfig,
        output_dir: Path,
        result: GenerationResult,
        progress_callback: Optional[Callable] = None,
    ):
        """Generate individual product pages"""
        products_dir = output_dir / "products"

        for product in config.products:
            try:
                html_content = self.html_generator.generate_individual_product_page(
                    product, config
                )
                filename = f"{self._sanitize_filename(product.name)}.html"
                product_file = products_dir / filename

                with open(product_file, "w", encoding="utf-8") as f:
                    f.write(html_content)

                result.add_generated_file(str(product_file))
                result.pages_generated += 1

                if progress_callback:
                    progress_callback(
                        result.pages_generated,
                        result.total_pages,
                        f"Generated product page: {product.name}",
                    )

            except Exception as e:
                result.add_error(
                    f"Error generating product page for {product.name}: {str(e)}"
                )

    def _generate_product_comparison_pages(
        self,
        config: ClientConfig,
        output_dir: Path,
        result: GenerationResult,
        progress_callback: Optional[Callable] = None,
    ):
        """Generate product comparison guide pages for resource sites."""
        products_dir = output_dir / "products"

        for category in getattr(config, "product_categories", []):
            try:
                html_content = self.html_generator.generate_product_comparison_page(
                    category, config
                )
                filename = f"{category.get_slug()}.html"
                category_file = products_dir / filename

                with open(category_file, "w", encoding="utf-8") as f:
                    f.write(html_content)

                result.add_generated_file(str(category_file))
                result.pages_generated += 1

                if progress_callback:
                    progress_callback(
                        result.pages_generated,
                        result.total_pages,
                        f"Generated comparison guide: {category.get_guide_title()}",
                    )

            except Exception as e:
                result.add_error(
                    f"Error generating comparison guide for {category.category_name}: {str(e)}"
                )

    def _generate_service_pages(
        self,
        config: ClientConfig,
        output_dir: Path,
        result: GenerationResult,
        progress_callback: Optional[Callable] = None,
    ):
        """Generate individual service pages"""
        services_dir = output_dir / "services"

        for service in config.services:
            try:
                html_content = self.html_generator.generate_individual_service_page(
                    service, config
                )
                filename = f"{self._sanitize_filename(service.name)}.html"
                service_file = services_dir / filename

                with open(service_file, "w", encoding="utf-8") as f:
                    f.write(html_content)

                result.add_generated_file(str(service_file))
                result.pages_generated += 1

                if progress_callback:
                    progress_callback(
                        result.pages_generated,
                        result.total_pages,
                        f"Generated service page: {service.name}",
                    )

            except Exception as e:
                result.add_error(
                    f"Error generating service page for {service.name}: {str(e)}"
                )

    def _generate_city_pages(
        self,
        config: ClientConfig,
        output_dir: Path,
        result: GenerationResult,
        progress_callback: Optional[Callable] = None,
    ):
        """Generate individual city pages"""
        locations_dir = output_dir / "locations"

        # Clean up old city pages to prevent cross-contamination between configs
        if locations_dir.exists():
            import shutil

            try:
                shutil.rmtree(locations_dir)
                logger.info(f"Cleaned old city pages from {locations_dir}")
            except Exception as e:
                logger.warning(f"Failed to clean locations directory: {str(e)}")

        # Import the unified city page generator
        from .city_page_generator import CityPageGenerator

        # Load Google Maps API key from config file if available
        google_maps_api_key = None
        try:
            import json
            from pathlib import Path

            api_keys_file = Path("config/api_keys.json")
            if api_keys_file.exists():
                with open(api_keys_file, "r") as f:
                    api_keys = json.load(f)
                    google_maps_api_key = api_keys.get("google_maps_api_key")
        except Exception as e:
            logger.debug(f"Could not load API keys: {e}")

        city_generator = CityPageGenerator(
            config, google_maps_api_key=google_maps_api_key
        )

        for city_page in config.city_pages:
            try:
                # Generate city page using the unified generator
                city_file_path = city_generator.generate_city_page(
                    city_page, str(locations_dir)
                )

                result.add_generated_file(city_file_path)
                result.pages_generated += 1

                if progress_callback:
                    progress_callback(
                        result.pages_generated,
                        result.total_pages,
                        f"Generated city page: {city_page.city_name}",
                    )

            except Exception as e:
                result.add_error(
                    f"Error generating city page for {city_page.city_name}: {str(e)}"
                )

    def _generate_additional_files(
        self, config: ClientConfig, output_dir: Path, result: GenerationResult
    ):
        """Generate additional files like sitemap, robots.txt"""
        try:
            # Generate sitemap.xml
            sitemap_content = self._generate_sitemap(config)
            sitemap_file = output_dir / "sitemap.xml"

            with open(sitemap_file, "w", encoding="utf-8") as f:
                f.write(sitemap_content)

            result.add_generated_file(str(sitemap_file))

            # Generate robots.txt
            robots_content = self._generate_robots_txt(config)
            robots_file = output_dir / "robots.txt"

            with open(robots_file, "w", encoding="utf-8") as f:
                f.write(robots_content)

            result.add_generated_file(str(robots_file))

            # Generate basic JavaScript file
            js_content = self._generate_basic_js()
            js_file = output_dir / "js" / "main.js"

            with open(js_file, "w", encoding="utf-8") as f:
                f.write(js_content)

            result.add_generated_file(str(js_file))

        except Exception as e:
            result.add_error(f"Error generating additional files: {str(e)}")

    def _copy_static_assets(
        self, config: ClientConfig, output_dir: Path, result: GenerationResult
    ):
        """Copy static assets if they exist (global assets first, then client-specific assets)"""
        try:
            # 1. Copy global static assets first
            static_dir = self.template_dir / "static"
            if static_dir.exists():
                # Copy images
                if (static_dir / "images").exists():
                    shutil.copytree(
                        static_dir / "images", output_dir / "images", dirs_exist_ok=True
                    )

                # Copy additional CSS/JS files
                if (static_dir / "css").exists():
                    for css_file in (static_dir / "css").glob("*.css"):
                        shutil.copy2(css_file, output_dir / "css")
                        result.add_generated_file(
                            str(output_dir / "css" / css_file.name)
                        )

                if (static_dir / "js").exists():
                    for js_file in (static_dir / "js").glob("*.js"):
                        shutil.copy2(js_file, output_dir / "js")
                        result.add_generated_file(str(output_dir / "js" / js_file.name))

            # 2. Copy client-specific assets (overrides global assets)
            if config.config_file_path:
                config_dir = Path(config.config_file_path).parent
                client_assets_dir = config_dir / "assets"

                if client_assets_dir.exists():
                    logger.info(
                        f"Copying client-specific assets from {client_assets_dir}"
                    )

                    # Copy client-specific images
                    if (client_assets_dir / "images").exists():
                        for image_file in (client_assets_dir / "images").rglob("*"):
                            if image_file.is_file():
                                dest_file = output_dir / "images" / image_file.name
                                shutil.copy2(image_file, dest_file)
                                logger.info(f"Copied client asset: {image_file.name}")

                    # Support for logo directly in assets/ directory
                    for asset_file in client_assets_dir.glob("*"):
                        if asset_file.is_file() and asset_file.suffix.lower() in [
                            ".png",
                            ".jpg",
                            ".jpeg",
                            ".gif",
                            ".svg",
                            ".webp",
                        ]:
                            dest_file = output_dir / "images" / asset_file.name
                            shutil.copy2(asset_file, dest_file)
                            logger.info(f"Copied client asset: {asset_file.name}")

            # 3. Copy city page pool images from their absolute local paths
            if hasattr(config, 'branding') and hasattr(config.branding, 'city_page_image_pool'):
                pool_images = config.branding.city_page_image_pool
                if pool_images and isinstance(pool_images, list):
                    for image_path in pool_images:
                        if image_path:
                            source_path = Path(image_path)
                            # Only copy if it's an absolute path (local file)
                            if source_path.is_absolute() and source_path.exists():
                                dest_file = output_dir / "images" / source_path.name
                                try:
                                    shutil.copy2(source_path, dest_file)
                                    logger.info(f"Copied pool image: {source_path.name} from {source_path}")
                                except Exception as e:
                                    logger.warning(f"Could not copy pool image {source_path.name}: {str(e)}")

            # 4. Copy hero background image if it's an absolute local path
            if hasattr(config, 'branding') and hasattr(config.branding, 'hero_background_image_url'):
                hero_image_path = config.branding.hero_background_image_url
                if hero_image_path:
                    source_path = Path(hero_image_path)
                    # Only copy if it's an absolute path (local file)
                    if source_path.is_absolute() and source_path.exists():
                        dest_file = output_dir / "images" / source_path.name
                        try:
                            shutil.copy2(source_path, dest_file)
                            logger.info(f"Copied hero background image: {source_path.name} from {source_path}")
                        except Exception as e:
                            logger.warning(f"Could not copy hero background image {source_path.name}: {str(e)}")

        except Exception as e:
            result.add_warning(f"Could not copy static assets: {str(e)}")

    def _get_canonical_base_url(self, config: ClientConfig) -> str:
        """
        Get the base URL for canonical tags and sitemaps.

        For backlink sites to work, they MUST:
        1. Be indexed independently by Google
        2. Have canonicals pointing to their own CloudFront URL
        3. Have content backlinks to main site

        Therefore: Use deployment_url for both backlink and main sites
        """
        # For both backlink and main sites, use deployment_url if available
        if config.cloud.deployment_url:
            return config.cloud.deployment_url.rstrip("/")

        # Fallback to business domain (should not happen for properly configured sites)
        return config.business.domain.rstrip("/")

    def _generate_sitemap(self, config: ClientConfig) -> str:
        """Generate sitemap.xml with industry-standard priority and changefreq values"""
        base_url = self._get_canonical_base_url(config)
        current_date = datetime.now().strftime("%Y-%m-%d")

        # Main pages with differentiated priority per Google/Bing best practices
        urls = [
            {
                "loc": f"{base_url}/",
                "priority": "1.0",
                "changefreq": "weekly",
            },
            {
                "loc": f"{base_url}/about.html",
                "priority": "0.6",
                "changefreq": "monthly",
            },
            {
                "loc": f"{base_url}/contact.html",
                "priority": "0.6",
                "changefreq": "monthly",
            },
            {
                "loc": f"{base_url}/faq.html",
                "priority": "0.6",
                "changefreq": "monthly",
            },
            {
                "loc": f"{base_url}/privacy-policy.html",
                "priority": "0.4",
                "changefreq": "yearly",
            },
        ]

        # Services hub and detail pages
        if config.services:
            urls.append(
                {
                    "loc": f"{base_url}/services.html",
                    "priority": "0.8",
                    "changefreq": "monthly",
                }
            )
            for service in config.services:
                service_slug = self._sanitize_filename(service.name)
                urls.append(
                    {
                        "loc": f"{base_url}/services/{service_slug}.html",
                        "priority": "0.7",
                        "changefreq": "monthly",
                    }
                )

        # Products hub, individual product pages, and category comparison guides
        product_categories = getattr(config, "product_categories", [])
        if config.products or product_categories:
            urls.append(
                {
                    "loc": f"{base_url}/products.html",
                    "priority": "0.8",
                    "changefreq": "monthly",
                }
            )
        for product in config.products:
            product_slug = self._sanitize_filename(product.name)
            urls.append(
                {
                    "loc": f"{base_url}/products/{product_slug}.html",
                    "priority": "0.7",
                    "changefreq": "monthly",
                }
            )
        for category in product_categories:
            urls.append(
                {
                    "loc": f"{base_url}/products/{category.get_slug()}.html",
                    "priority": "0.7",
                    "changefreq": "monthly",
                }
            )

        # City pages (critical for local SEO)
        if config.city_pages:
            for city_page in config.city_pages:
                # Use existing slug or generate from city_name (consistent with CityPageConfig)
                city_slug = (
                    city_page.slug
                    if city_page.slug
                    else self._sanitize_filename(city_page.city_name)
                )
                urls.append(
                    {
                        "loc": f"{base_url}/locations/{city_slug}.html",
                        "priority": "0.7",
                        "changefreq": "monthly",
                    }
                )

        # Build XML sitemap per sitemaps.org protocol 0.9
        sitemap_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""

        for url_data in urls:
            sitemap_content += f"""    <url>
        <loc>{url_data["loc"]}</loc>
        <lastmod>{current_date}</lastmod>
        <changefreq>{url_data["changefreq"]}</changefreq>
        <priority>{url_data["priority"]}</priority>
    </url>
"""

        sitemap_content += "</urlset>"
        return sitemap_content

    def _generate_robots_txt(self, config: ClientConfig) -> str:
        """Generate robots.txt for search engine indexing"""
        base_url = self._get_canonical_base_url(config)

        # Check allow_indexing from cloud config (preferred) or business config (legacy)
        allow_indexing = (
            config.cloud.allow_indexing
            if hasattr(config.cloud, "allow_indexing")
            else getattr(config.business, "allow_indexing", True)
        )

        if allow_indexing:
            # Production robots.txt - Allow full indexing
            robots_content = f"""# robots.txt - SEO Optimized
# Generated by CloudStack Generator

User-agent: *
Allow: /

# Sitemap for search engines
Sitemap: {base_url}/sitemap.xml

# Crawl-delay (optional, uncomment if needed)
# Crawl-delay: 10
"""
        else:
            # Staging/Development robots.txt - Block all indexing
            robots_content = f"""# robots.txt - Development/Staging Environment
# This site is not ready for search engine indexing
# Canonical domain: {base_url}

User-agent: *
Disallow: /

# Sitemap reference (for when indexing is enabled)
Sitemap: {base_url}/sitemap.xml
"""

        return robots_content

    def _generate_basic_js(self) -> str:
        """Generate basic JavaScript functionality"""
        return """// Main JavaScript functionality
document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu toggle
    const mobileMenuButton = document.querySelector('.mobile-menu-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    
    if (mobileMenuButton && mobileMenu) {
        mobileMenuButton.addEventListener('click', function() {
            mobileMenu.classList.toggle('hidden');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Form submission handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Basic form validation
            const requiredFields = form.querySelectorAll('[required]');
            let valid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    valid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (valid) {
                // Show success message (in real implementation, would submit to server)
                alert('Thank you for your message! We will get back to you soon.');
                form.reset();
            } else {
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // Add animation classes when elements come into view
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    document.querySelectorAll('.card, .section').forEach(el => {
        observer.observe(el);
    });
    
    // Back to top button
    const backToTopButton = document.querySelector('.back-to-top');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 300) {
                backToTopButton.style.display = 'block';
            } else {
                backToTopButton.style.display = 'none';
            }
        });
        
        backToTopButton.addEventListener('click', function() {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }
});

// Utility functions
function formatPhoneNumber(phone) {
    const cleaned = phone.replace(/\\D/g, '');
    const match = cleaned.match(/^(\\d{3})(\\d{3})(\\d{4})$/);
    if (match) {
        return '(' + match[1] + ') ' + match[2] + '-' + match[3];
    }
    return phone;
}

function validateEmail(email) {
    const re = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return re.test(email);
}

// Contact form enhancement
function initContactForm() {
    const contactForm = document.querySelector('#contact-form');
    if (!contactForm) return;
    
    const phoneInput = contactForm.querySelector('input[type="tel"]');
    if (phoneInput) {
        phoneInput.addEventListener('input', function() {
            this.value = formatPhoneNumber(this.value);
        });
    }
    
    const emailInput = contactForm.querySelector('input[type="email"]');
    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            if (this.value && !validateEmail(this.value)) {
                this.classList.add('error');
                this.setCustomValidity('Please enter a valid email address');
            } else {
                this.classList.remove('error');
                this.setCustomValidity('');
            }
        });
    }
}

// Initialize contact form when DOM is ready
document.addEventListener('DOMContentLoaded', initContactForm);
"""

    def _generate_print_css(self) -> str:
        """Generate print-specific CSS"""
        return """/* Print Styles */
@media print {
    * {
        background: transparent !important;
        color: black !important;
        box-shadow: none !important;
        text-shadow: none !important;
    }
    
    body {
        font-size: 12pt;
        line-height: 1.3;
    }
    
    .header, .footer, .nav, .btn, .back-to-top {
        display: none !important;
    }
    
    .main-content {
        margin: 0 !important;
        padding: 0 !important;
    }
    
    .container {
        max-width: none !important;
        padding: 0 !important;
    }
    
    .card {
        border: 1px solid #ccc !important;
        page-break-inside: avoid;
        margin-bottom: 1em;
    }
    
    h1, h2, h3 {
        page-break-after: avoid;
        color: black !important;
    }
    
    p, li {
        orphans: 3;
        widows: 3;
    }
    
    a[href]:after {
        content: " (" attr(href) ")";
        font-size: 0.8em;
        color: #666;
    }
    
    a[href^="#"]:after,
    a[href^="javascript:"]:after {
        content: "";
    }
    
    .page-break {
        page-break-before: always;
    }
    
    @page {
        margin: 1in;
    }
}"""

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for safe file system use"""
        import re

        # Remove or replace unsafe characters
        safe_name = re.sub(r"[^\w\s-]", "", filename.lower())
        safe_name = re.sub(r"[-\s]+", "-", safe_name)
        return safe_name.strip("-")

    def get_generation_summary(self, result: GenerationResult) -> str:
        """Get a formatted summary of the generation process"""
        if result.success:
            summary = f"""✅ Website Generation Successful!

📊 Generation Summary:
• Pages Generated: {result.pages_generated}/{result.total_pages}
• Total Files: {len(result.generated_files)}
• Generation Time: {result.generation_time:.2f} seconds
• Output Directory: {result.output_directory}

📁 Generated Files:
"""
            for file_path in result.generated_files:
                summary += f"  • {Path(file_path).name}\n"

            if result.warnings:
                summary += f"\n⚠️ Warnings ({len(result.warnings)}):\n"
                for warning in result.warnings:
                    summary += f"  • {warning}\n"
        else:
            summary = f"""❌ Website Generation Failed

📊 Generation Summary:
• Pages Generated: {result.pages_generated}/{result.total_pages}
• Generation Time: {result.generation_time:.2f} seconds
• Output Directory: {result.output_directory}

❌ Errors ({len(result.errors)}):
"""
            for error in result.errors:
                summary += f"  • {error}\n"

            if result.warnings:
                summary += f"\n⚠️ Warnings ({len(result.warnings)}):\n"
                for warning in result.warnings:
                    summary += f"  • {warning}\n"

        return summary

    def open_generated_website(self, result: GenerationResult) -> bool:
        """Open the generated website in the default browser"""
        if not result.success or not result.output_directory:
            return False

        try:
            import webbrowser

            index_file = Path(result.output_directory) / "index.html"
            if index_file.exists():
                webbrowser.open(f"file://{index_file.absolute()}")
                return True
        except Exception as e:
            logger.error(
                "Could not open website", extra={"extra_fields": {"error": str(e)}}
            )

        return False
