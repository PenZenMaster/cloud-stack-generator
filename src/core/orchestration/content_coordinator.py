"""
Module: content_coordinator
Path: src/core/orchestration/content_coordinator.py

Description:
Content generation coordination module. Coordinates between various content
generators and manages AI content service integration for home pages and city pages.

Author: Cloud Stack Generator Team
Created: 2025-11-11
Version: 1.0.0
"""

from typing import Optional
from pathlib import Path

from ..config.models import ClientConfig
from ..services.ai_content_service import AIContentService
from ..services.content_cache import ContentCache
from ..generators.html_generator import HTMLGenerator
from ..generators.city_page_generator import CityPageGenerator


class ContentCoordinator:
    """
    Coordinates content generation across multiple generators.

    Responsibilities:
    - Coordinate home page content generation
    - Coordinate city page content generation (legacy and enhanced)
    - Manage AI content service integration
    - Handle content caching
    - Delegate to specialized content generators
    """

    def __init__(
        self,
        ai_service: Optional[AIContentService] = None,
        content_cache: Optional[ContentCache] = None
    ):
        """
        Initialize ContentCoordinator.

        Args:
            ai_service: Optional AI content service for enhanced content
            content_cache: Optional content cache for performance
        """
        self.ai_service = ai_service
        self.content_cache = content_cache

    def generate_home_page(
        self,
        config: ClientConfig,
        use_ai: bool = True
    ) -> str:
        """
        Generate home page HTML content.

        Delegates to HTMLGenerator for actual generation.

        Args:
            config: Client configuration
            use_ai: Whether to use AI for enhanced content

        Returns:
            str: Complete HTML content for home page
        """
        html_generator = HTMLGenerator(
            ai_service=self.ai_service,
            cache=self.content_cache
        )
        return html_generator.generate_homepage(config, use_ai=use_ai)

    def generate_city_pages(
        self,
        config: ClientConfig,
        output_dir: str,
        use_ai: bool = True
    ) -> list[str]:
        """
        Generate all city pages using enhanced city page generator.

        Handles both enhanced city_pages and legacy target_cities fallback.

        Args:
            config: Client configuration
            output_dir: Output directory path
            use_ai: Whether to use AI for enhanced content

        Returns:
            list[str]: List of generated file paths
        """
        city_generator = CityPageGenerator(
            config,
            ai_service=self.ai_service,
            cache=self.content_cache
        )
        return city_generator.generate_all_city_pages(output_dir, use_ai=use_ai)

    def generate_single_city_page(
        self,
        config: ClientConfig,
        city_page,
        output_dir: str
    ) -> str:
        """
        Generate a single enhanced city page.

        Args:
            config: Client configuration
            city_page: CityPageConfig object
            output_dir: Output directory path

        Returns:
            str: Path to generated file
        """
        # Create city-specific HTML content
        html_content = self._create_enhanced_city_html(city_page, config)

        # Generate filename from city slug
        slug = city_page.slug or self._create_slug(city_page.city_name)
        file_path = Path(output_dir) / f"{slug}.html"

        # Write file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return str(file_path)

    def _create_enhanced_city_html(self, city_page, config: ClientConfig) -> str:
        """
        Create complete HTML for enhanced city page.

        Args:
            city_page: CityPageConfig object with rich city data
            config: Client configuration

        Returns:
            str: Complete HTML document
        """
        business_name = config.business.business_name
        title = city_page.title or f"{city_page.city_name} - {business_name}"

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{city_page.meta_description or f'Professional services in {city_page.city_name}'}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>{business_name}</h1>
            <nav>
                <ul>
                    <li><a href="index.html">Home</a></li>
                    <li><a href="#services">Services</a></li>
                    <li><a href="#about">About</a></li>
                    <li><a href="#contact">Contact</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main>
        <section class="hero">
            <div class="container">
                <h1>{city_page.hero_title or f'{city_page.city_name} Services'}</h1>
                <p>Professional {config.business.industry} services in {city_page.city_name}</p>
            </div>
        </section>

        <section class="about-city">
            <div class="container">
                <h2>About {city_page.city_name}</h2>
                <p>{city_page.about_city}</p>
            </div>
        </section>

        <section class="seo-content">
            <div class="container">
                <h2>{city_page.seo_content_title or f'Professional Services in {city_page.city_name}'}</h2>
                <div class="content-body">
                    {self._format_content_body(city_page.seo_content_body)}
                </div>
            </div>
        </section>"""

        # Add places of interest if available
        if city_page.places_of_interest:
            html += f"""
        <section class="places-of-interest">
            <div class="container">
                <h2>Places of Interest in {city_page.city_name}</h2>
                <div class="places-grid">"""

            for place in city_page.places_of_interest:
                html += f"""
                    <div class="place-item">
                        <h3>{place.name}</h3>
                        {f'<iframe src="{place.embed_url}" width="100%" height="200"></iframe>' if place.embed_url else ''}
                    </div>"""

            html += """
                </div>
            </div>
        </section>"""

        # Add FAQ section if available
        if city_page.city_faq:
            html += f"""
        <section class="city-faq">
            <div class="container">
                <h2>Frequently Asked Questions - {city_page.city_name}</h2>
                <div class="faq-items">"""

            for faq in city_page.city_faq:
                html += f"""
                    <div class="faq-item">
                        <h3>{faq.question}</h3>
                        <p>{faq.answer}</p>
                    </div>"""

            html += """
                </div>
            </div>
        </section>"""

        # Add contact section
        html += f"""
        <section class="contact">
            <div class="container">
                <h2>Contact Us for {city_page.city_name} Services</h2>
                <p>{city_page.service_area_note or f'We proudly serve {city_page.city_name} and surrounding areas.'}</p>
                <div class="contact-info">
                    <p><strong>Phone:</strong> {config.contact.phone}</p>
                    <p><strong>Email:</strong> {config.contact.email}</p>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <div class="container">
            <p>&copy; 2024 {business_name}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""

        return html

    def _format_content_body(self, content: str) -> str:
        """
        Format content body text with basic HTML formatting.

        Args:
            content: Plain text content

        Returns:
            str: HTML-formatted content
        """
        if not content:
            return ""

        # Split into paragraphs and wrap in <p> tags
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []

        for paragraph in paragraphs:
            if paragraph.strip():
                formatted_paragraphs.append(f"<p>{paragraph.strip()}</p>")

        return '\n'.join(formatted_paragraphs)

    def _create_slug(self, city_name: str) -> str:
        """
        Create URL-friendly slug from city name.

        Args:
            city_name: City name to convert

        Returns:
            str: URL-safe slug
        """
        import re
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', city_name.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        return slug
