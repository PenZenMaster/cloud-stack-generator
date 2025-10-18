"""
City Content Generator
Path: E:/projects/cloud-stack-generator/src/core/generators/content/city_content_generator.py

Description:
Generates HTML content for city-specific pages. Extracted from website_generator.py
to improve separation of concerns and maintainability.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-17

Last Modified Date:
2025-10-17

Comments:
* v1.00 - Initial extraction from website_generator.py
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ...config.models import ClientConfig


class CityContentGenerator:
    """Generates HTML content for city-specific pages"""

    def __init__(self):
        """Initialize the city content generator"""
        pass

    def generate_city_content(self, config: "ClientConfig", city: str) -> str:
        """
        Create content for city-specific pages with separate Services and Products.

        Args:
            config: Client configuration containing business, services, products data
            city: Name of the city for this page

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
