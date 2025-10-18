"""
Home Content Generator
Path: E:/projects/cloud-stack-generator/src/core/generators/content/home_content_generator.py

Description:
Generates HTML content for home/index pages. Extracted from website_generator.py
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


class HomeContentGenerator:
    """Generates HTML content for home/index pages"""

    def __init__(self):
        """Initialize the home content generator"""
        pass

    def generate_basic_home_content(self, config: "ClientConfig") -> str:
        """
        Create content for the home page with SEPARATE Services and Products sections.

        Args:
            config: Client configuration containing business, services, products data

        Returns:
            HTML string for the home page content
        """
        business_name = config.business.business_name
        industry = config.business.industry

        # Get hero image for home page
        hero_image = ""
        if config.pages:
            for page in config.pages:
                if page.slug == "index":
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
                    <h2>Welcome to {business_name}</h2>
                    <p>Professional {industry.lower()} services you can trust</p>
                </div>
            </div>
        </section>

        <section class="content">
            <h3>About Our {industry}</h3>
            <p>Welcome to {business_name}, your trusted provider of {industry.lower()} services. We are committed to delivering exceptional results and outstanding customer service.</p>"""

        # Add services and products sections SEPARATELY
        services = config.services
        products = config.products

        # SERVICES SECTION
        if services:
            content += """
            <h3>Our Services</h3>
            <div class="services-grid">"""

            for service in services:
                service_name = service.name
                service_desc = service.description or f"Professional {service_name.lower()}"
                content += f"""
                    <div class="service-item">
                        <h4>{service_name}</h4>
                        <p>{service_desc}</p>
                    </div>"""

            content += "</div>"

        # PRODUCTS SECTION - SEPARATE with different styling
        if products:
            content += """
            <h3>Our Products</h3>
            <div class="products-grid">"""

            for product in products:
                product_name = product.name
                product_desc = product.description or f"High-quality {product_name.lower()}"
                content += f"""
                    <div class="product-item">
                        <h4>{product_name}</h4>
                        <p>{product_desc}</p>
                    </div>"""

            content += "</div>"
        else:
            # Default services if none specified
            content += f"""
            <h3>Our Services</h3>
            <ul>
                <li>Professional {industry} consultation</li>
                <li>Expert {industry.lower()} solutions</li>
                <li>Quality {industry.lower()} services</li>
            </ul>"""

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

        # Add service areas if city pages exist
        if config.pages and len(config.pages) > 1:
            content += """
            <h3>Service Areas</h3>
            <p>We proudly serve the following areas:</p>
            <ul>"""

            for page in config.pages:
                if page.slug != "index":
                    city = page.city
                    if city:
                        content += f"                <li>{city}</li>\n"

            content += "            </ul>"

        content += "        </section>"
        return content

    def generate_enhanced_home_content(self, config: "ClientConfig") -> str:
        """
        Create enhanced professional home page content using enhanced business data.

        Args:
            config: Client configuration with enhanced business data

        Returns:
            HTML string for enhanced home page content
        """
        business = config.business
        contact = config.contact
        business_name = business.business_name
        industry = business.industry

        # Get hero image for home page
        hero_image = ""
        if config.pages:
            for page in config.pages:
                if page.slug == "index":
                    hero_image = page.hero_image
                    break

        # Hero section with enhanced tagline and CTA
        hero_style = ""
        if hero_image:
            hero_style = f" style=\"background-image: url('{hero_image}'); background-size: cover; background-position: center;\""

        # Use enhanced tagline or fall back to default
        tagline = business.get_hero_tagline()
        years_display = business.get_years_display()

        content = f"""
        <section class="hero"{hero_style}>
            <div class="hero-overlay">
                <div class="hero-content">
                    <h1>Welcome to {business_name}</h1>
                    <p class="hero-tagline">{tagline}</p>"""

        if years_display:
            content += f"""
                    <p class="years-experience">{years_display}</p>"""

        content += f"""
                    <div class="hero-cta">
                        <a href="#{'' if not contact.get_primary_phone() else 'contact'}" class="cta-button primary">Get Free Quote</a>
                        <a href="tel:{contact.get_primary_phone()}" class="cta-button secondary">Call Now: {contact.get_primary_phone()}</a>
                    </div>
                </div>
            </div>
        </section>"""

        # About section with company overview
        if business.company_overview:
            content += f"""
        <section class="about-section">
            <div class="container">
                <h2>About Our {industry}</h2>
                <p class="company-overview">{business.company_overview}</p>
            </div>
        </section>"""
        else:
            content += f"""
        <section class="about-section">
            <div class="container">
                <h2>About Our {industry}</h2>
                <p>Welcome to {business_name}, your trusted provider of {industry.lower()} services. We are committed to delivering exceptional results and outstanding customer service.</p>
            </div>
        </section>"""

        # Why Choose Us section
        if business.why_choose_us:
            content += """
        <section class="why-choose-us">
            <div class="container">
                <h2>Why Choose Us?</h2>
                <div class="reasons-grid">"""

            for reason in business.why_choose_us:
                content += f"""
                    <div class="reason-item">
                        <h3>{reason}</h3>
                    </div>"""

            content += """
                </div>
            </div>
        </section>"""

        # Company Statistics section
        if business.company_stats:
            content += """
        <section class="company-stats">
            <div class="container">
                <div class="stats-grid">"""

            for stat_key, stat_value in business.company_stats.items():
                content += f"""
                    <div class="stat-item">
                        <div class="stat-number">{stat_value}</div>
                        <div class="stat-label">{stat_key.title()}</div>
                    </div>"""

            content += """
                </div>
            </div>
        </section>"""

        # Products section with enhanced layout
        content += """
        <section class="products-section">
            <div class="container">"""

        if config.products:
            content += """
                <h2>Our Products</h2>
                <div class="products-grid">"""

            for product in config.products:
                product_name = product.name
                product_desc = product.description or f"High-quality {product_name.lower()}"
                content += f"""
                    <div class="product-item">
                        <h3>{product_name}</h3>
                        <p>{product_desc}</p>
                    </div>"""

            content += "</div>"
        else:
            content += f"""
                <h2>Our Services</h2>
                <div class="services-grid">
                    <div class="service-item">
                        <h3>Professional {industry} Consultation</h3>
                        <p>Expert guidance and planning for your projects</p>
                    </div>
                    <div class="service-item">
                        <h3>Custom {industry} Solutions</h3>
                        <p>Tailored solutions to meet your specific needs</p>
                    </div>
                    <div class="service-item">
                        <h3>Quality {industry} Services</h3>
                        <p>High-quality workmanship and reliable service</p>
                    </div>
                </div>"""

        content += """
            </div>
        </section>"""

        # Service guarantee section
        if business.service_guarantee:
            content += f"""
        <section class="service-guarantee">
            <div class="container">
                <h2>Our Guarantee</h2>
                <p class="guarantee-text">{business.service_guarantee}</p>
            </div>
        </section>"""

        # Enhanced contact section with business hours
        if contact.has_multiple_contacts() or contact.business_hours:
            content += """
        <section class="enhanced-contact">
            <div class="container">
                <h2>Contact Us</h2>
                <div class="contact-grid">"""

            # Contact methods
            content += """
                    <div class="contact-methods">
                        <h3>Get In Touch</h3>"""

            if contact.get_primary_phone():
                content += f"""
                        <p><strong>Phone:</strong> <a href="tel:{contact.get_primary_phone()}">{contact.get_primary_phone()}</a></p>"""

            if contact.office_phone and contact.office_phone != contact.phone:
                content += f"""
                        <p><strong>Office:</strong> <a href="tel:{contact.office_phone}">{contact.office_phone}</a></p>"""

            if contact.email:
                content += f"""
                        <p><strong>Email:</strong> <a href="mailto:{contact.email}">{contact.email}</a></p>"""

            if contact.response_time_promise:
                content += f"""
                        <p class="response-time">{contact.response_time_promise}</p>"""

            content += """
                    </div>"""

            # Business hours
            if contact.business_hours:
                content += """
                    <div class="business-hours">
                        <h3>Business Hours</h3>"""

                for day, hours in contact.business_hours.items():
                    if hours.strip():
                        content += f"""
                        <p><strong>{day.title()}:</strong> {hours}</p>"""

                content += """
                    </div>"""

            content += """
                </div>
            </div>
        </section>"""

        # Service area section
        if business.service_area_description:
            content += f"""
        <section class="service-area">
            <div class="container">
                <h2>Service Area</h2>
                <p>{business.service_area_description}</p>
            </div>
        </section>"""

        # Add FAQ section if available
        if config.faq:
            content += """
        <section class="faq-section">
            <div class="container">
                <h2>Frequently Asked Questions</h2>
                <div class="faq-items">"""

            for faq_item in config.faq:
                question = faq_item.question if hasattr(faq_item, 'question') else faq_item.get("question", "")
                answer = faq_item.answer if hasattr(faq_item, 'answer') else faq_item.get("answer", "")
                content += f"""
                <div class="faq-item">
                    <h3>{question}</h3>
                    <p>{answer}</p>
                </div>"""

            content += """
                </div>
            </div>
        </section>"""

        return content
