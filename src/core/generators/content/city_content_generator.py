"""
City Content Generator
Path: E:/projects/cloud-stack-generator/src/core/generators/content/city_content_generator.py

Description:
Generates HTML content for city-specific pages. Extracted from website_generator.py
to improve separation of concerns and maintainability. Now supports AI-powered
content generation with fallback to template-based generation.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-17

Last Modified Date:
2025-10-19

Comments:
* v1.00 - Initial extraction from website_generator.py
* v1.01 - Added AI content generation integration with caching
"""

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ...config.models import ClientConfig
    from ...services.ai_content_service import AIContentService
    from ...services.content_cache import ContentCache

logger = logging.getLogger(__name__)


class CityContentGenerator:
    """
    Generates HTML content for city-specific pages.

    Supports both AI-powered and template-based content generation.
    Uses caching to reduce API costs and improve performance.
    """

    def __init__(
        self,
        ai_service: Optional["AIContentService"] = None,
        cache: Optional["ContentCache"] = None
    ):
        """
        Initialize the city content generator.

        Args:
            ai_service: Optional AI content service for dynamic generation
            cache: Optional cache manager for AI-generated content
        """
        self.ai_service = ai_service
        self.cache = cache
        self.use_ai = ai_service is not None and ai_service.is_available()

    def generate_city_content(self, config: "ClientConfig", city: str, use_ai: bool = True) -> str:
        """
        Create content for city-specific pages with separate Services and Products.

        Args:
            config: Client configuration containing business, services, products data
            city: Name of the city for this page
            use_ai: Whether to attempt AI generation (default True)

        Returns:
            HTML string for the city page content
        """
        # Try AI generation first if enabled
        if use_ai and self.use_ai:
            ai_content = self._generate_with_ai(config, city)
            if ai_content:
                return ai_content

        # Fall back to template-based generation
        logger.debug(f"Using template-based city content generation for {city}")
        return self._generate_template_city(config, city)

    def _generate_template_city(self, config: "ClientConfig", city: str) -> str:
        """
        Template-based generation for city content.

        Args:
            config: Client configuration
            city: Name of the city

        Returns:
            HTML string for the city page content
        """
        business_name = config.business.business_name
        industry = config.business.industry

        # Get hero image for this city page
        hero_image = ""
        if config.pages:
            for page in config.pages:
                if page.city == city:
                    hero_image = page.hero_image
                    break

        # Hero section with ONLY background image (no img tag)
        hero_style = ""
        if hero_image:
            hero_style = f" style=\"background-image: url('{hero_image}'); background-size: cover; background-position: center;\""

        content = f"""
        <section class="hero"{hero_style}>
            <div class="hero-overlay">
                <div class="hero-text">
                    <h2>{industry} Services in {city}</h2>
                    <p>Professional {industry.lower()} services serving {city} and surrounding areas</p>
                </div>
            </div>
        </section>

        <section class="content">
            <h3>Local {industry} Experts in {city}</h3>
            <p>{business_name} is proud to serve {city} with professional {industry.lower()} services. Our local expertise and commitment to excellence make us the preferred choice for {city} residents and businesses.</p>

            <h3>Why Choose Us in {city}</h3>
            <ul>
                <li>Local {city} expertise and knowledge</li>
                <li>Proven track record in the {city} area</li>
                <li>Personalized {industry.lower()} solutions</li>
                <li>Committed to the {city} community</li>
            </ul>

            <h3>Our {industry} Services in {city}</h3>
            <div class="services-grid">"""

        # Add services and products separately for city pages
        services = config.services
        products = config.products

        # Add services
        for service in services:
            service_name = service.name
            service_desc = service.description or f"Professional {service_name.lower()} in {city}"
            content += f"""
                <div class="service-item">
                    <h4>{service_name} in {city}</h4>
                    <p>{service_desc}</p>
                </div>"""

            content += "</div>"

            # Add products section if products exist
            if products:
                content += f"""

            <h3>Our Products Available in {city}</h3>
            <div class="products-grid">"""

                for product in products:
                    product_name = product.name
                    product_desc = product.description or f"High-quality {product_name.lower()} available in {city}"
                    content += f"""
                    <div class="product-item">
                        <h4>{product_name}</h4>
                        <p>{product_desc}</p>
                    </div>"""

                content += "</div>"
        else:
            # Default services if none specified
            content += f"""
                <div class="service-item">
                    <h4>Professional {industry} Consultation</h4>
                    <p>Expert {industry.lower()} consultation services in {city}</p>
                </div>
                <div class="service-item">
                    <h4>Local {industry} Solutions</h4>
                    <p>Customized {industry.lower()} solutions for {city} businesses</p>
                </div>
            </div>"""

        # Add FAQ section if available
        if config.faq:
            content += """

            <h3>Frequently Asked Questions</h3>
            <div class="faq-section">"""

            for faq_item in config.faq:
                question = faq_item.get("question", "")
                answer = faq_item.get("answer", "")
                content += f"""
                <div class="faq-item">
                    <h4>{question}</h4>
                    <p>{answer}</p>
                </div>"""

            content += "</div>"

        content += f"""

            <h3>Contact Us Today</h3>
            <p>Ready to get started? Contact us today to learn more about our services in {city}.</p>
        </section>"""

        return content

    def _generate_with_ai(self, config: "ClientConfig", city: str) -> Optional[str]:
        """
        Generate content using AI service with caching.

        Args:
            config: Client configuration
            city: City name

        Returns:
            AI-generated HTML content or None if generation fails
        """
        if not self.ai_service:
            return None

        # Extract state from page config if available
        state = None
        if config.pages:
            for page in config.pages:
                if page.city == city and hasattr(page, 'state'):
                    state = page.state
                    break

        # Build cache context
        cache_context = {
            'business_name': config.business.business_name,
            'industry': config.business.industry,
            'city': city,
            'state': state or '',
            'num_services': len(config.services),
            'num_products': len(config.products)
        }

        # Check cache first
        if self.cache and self.cache.is_enabled():
            cached_content = self.cache.get('city_page', cache_context)
            if cached_content:
                logger.info(f"Using cached AI-generated content for {city}")
                return cached_content

        # Generate with AI
        try:
            logger.info(f"Generating city content with AI for {city}")
            ai_content = self.ai_service.generate_city_content(config, city, state)

            if ai_content:
                # Cache the result
                if self.cache and self.cache.is_enabled():
                    self.cache.set('city_page', cache_context, ai_content, metadata={
                        'business': config.business.business_name,
                        'city': city,
                        'state': state
                    })

                return ai_content

        except Exception as e:
            logger.error(f"AI content generation failed for {city}: {e}")

        return None
