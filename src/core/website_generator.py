"""
Filename: src/core/website_generator.py
Path: E:\\projects\\cloud-stack-generator\\src\\core\\website_generator.py
Description: Enhanced Website Generator with GBP integration and complete fixes

Version: 2.2.0
Date: 2025-08-10
Author: Cloud Stack Generator Team
"""

import os
import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from .config.models import ClientConfig


class GenerationError(Exception):
    """Raised when website generation fails"""

    pass


@dataclass
class GenerationResult:
    """Result of website generation"""

    success: bool
    generated_files: List[str]
    errors: Optional[str] = None


class WebsiteGenerator:
    """Generate static HTML websites from configuration"""

    def __init__(self):
        self.output_dir: Optional[str] = None
        self.config: Optional[ClientConfig] = None

    def generate(self, config: ClientConfig, output_dir: str) -> GenerationResult:
        """Generate website from configuration"""
        try:
            self.output_dir = output_dir
            self.config = config
            generated_files = []

            # Ensure output directory exists
            Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Generate index.html
            index_path = self._generate_index_page(config)
            generated_files.append(index_path)

            # Generate city pages from enhanced city_pages first, then fallback to target_cities
            if hasattr(config, 'city_pages') and config.city_pages:
                # Use enhanced city pages data
                for city_page in config.city_pages:
                    city_file = self._generate_enhanced_city_page(city_page, config)
                    generated_files.append(city_file)
            elif hasattr(config, 'target_cities') and config.target_cities:
                # Fallback to legacy target_cities using CityPageGenerator
                from .generators.city_page_generator import CityPageGenerator
                city_generator = CityPageGenerator(config)
                city_files = city_generator.generate_all_city_pages(output_dir)
                generated_files.extend(city_files)

            # Generate CSS file
            css_path = self._generate_css_file(config)
            generated_files.append(css_path)

            # Create js directory (for future JavaScript files)
            js_dir = os.path.join(output_dir, "js")
            os.makedirs(js_dir, exist_ok=True)

            return GenerationResult(success=True, generated_files=generated_files)

        except Exception as e:
            return GenerationResult(success=False, generated_files=[], errors=str(e))

    def _generate_index_page(self, config: ClientConfig) -> str:
        """Generate the main index.html page using the enhanced template"""
        if not self.output_dir:
            raise GenerationError("Output directory not set")

        # Use the new HTML generator with enhanced template
        from .generators.html_generator import HTMLGenerator
        html_generator = HTMLGenerator()
        html_content = html_generator.generate_homepage(config)

        file_path = os.path.join(self.output_dir, "index.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return file_path

    def _generate_city_page(self, config: ClientConfig, page_config: dict) -> str:
        """Generate a city-specific page"""
        if not self.output_dir:
            raise GenerationError("Output directory not set")

        title = page_config.title or "Services"
        slug = page_config.slug or "page"
        city = page_config.city

        html_content = self._create_html_template(
            config, title, is_home=False, city=city
        )

        file_path = os.path.join(self.output_dir, f"{slug}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return file_path

    def _generate_enhanced_city_page(self, city_page, config: ClientConfig) -> str:
        """Generate enhanced city page from CityPageConfig object"""
        if not self.output_dir:
            raise GenerationError("Output directory not set")

        # Create city-specific HTML content using the rich city page data
        html_content = self._create_enhanced_city_html(city_page, config)

        # Generate filename from city slug
        slug = city_page.slug or self._create_slug(city_page.city_name)
        file_path = os.path.join(self.output_dir, f"{slug}.html")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return file_path

    def _create_slug(self, city_name: str) -> str:
        """Create URL-friendly slug from city name"""
        import re
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', city_name.lower())
        slug = re.sub(r'\s+', '-', slug.strip())
        return slug

    def _create_enhanced_city_html(self, city_page, config: ClientConfig) -> str:
        """Create complete HTML for enhanced city page"""
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
        """Format content body text with basic HTML formatting"""
        if not content:
            return ""
        
        # Split into paragraphs and wrap in <p> tags
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            if paragraph.strip():
                formatted_paragraphs.append(f"<p>{paragraph.strip()}</p>")
        
        return '\n'.join(formatted_paragraphs)

    def _generate_css_file(self, config: ClientConfig) -> str:
        """Generate CSS file in proper directory structure"""
        if not self.output_dir:
            raise GenerationError("Output directory not set")

        # Create css directory
        css_dir = os.path.join(self.output_dir, "css")
        os.makedirs(css_dir, exist_ok=True)

        css_content = self._create_css_template(config)

        file_path = os.path.join(css_dir, "style.css")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(css_content)

        return file_path

    def _create_html_template(
        self,
        config: ClientConfig,
        page_title: str,
        is_home: bool = False,
        city: str = "",
    ) -> str:
        """Create enhanced HTML template with proper data handling and logo/hero display"""
        business_name = config.business.business_name
        industry = config.business.industry
        contact = config.contact

        # Get branding
        branding = config.branding
        primary_color = branding.primary_color
        logo_url = branding.logo_url

        # Get hero image
        hero_image = ""
        if config.pages:
            for page in config.pages:
                if (is_home and page.slug == "index") or (
                    not is_home and page.city == city
                ):
                    hero_image = page.hero_image
                    break

        # Build navigation with proper page titles
        nav_links = self._build_navigation(config, city)

        # Page-specific content
        if is_home:
            # Use enhanced home content if enhanced data is available
            if config.business.has_enhanced_content():
                page_content = self._create_enhanced_home_content(config)
            else:
                page_content = self._create_home_content(config)
        else:
            page_content = self._create_city_content(config, city)

        # Footer content with GBP and city maps
        footer_content = self._create_footer_content(config, city, is_home)

        # Fix meta description - use industry instead of phone
        meta_description = f"{industry} services by {business_name}"
        if city:
            meta_description = f"{industry} services in {city} by {business_name}"

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - {business_name}</title>
    <meta name="description" content="{meta_description}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <div class="header-content">
            {f'<img src="{logo_url}" alt="{business_name} Logo" class="logo">' if logo_url else f'<h1>{business_name}</h1>'}
            <nav>{nav_links}</nav>
        </div>
    </header>
    
    <main>
        {page_content}
    </main>
    
    <footer>
        {footer_content}
    </footer>
    
    <script>
        // Enhanced dropdown functionality
        document.addEventListener('DOMContentLoaded', function() {{
            const dropdown = document.querySelector('.dropdown');
            const dropdownContent = document.querySelector('.dropdown-content');
            let timeoutId;
            
            if (dropdown && dropdownContent) {{
                // Show dropdown on hover
                dropdown.addEventListener('mouseenter', function() {{
                    clearTimeout(timeoutId);
                    dropdownContent.style.display = 'block';
                }});
                
                // Hide dropdown with delay on mouse leave
                dropdown.addEventListener('mouseleave', function() {{
                    timeoutId = setTimeout(function() {{
                        dropdownContent.style.display = 'none';
                    }}, 300);
                }});
                
                // Prevent dropdown from closing when hovering over content
                dropdownContent.addEventListener('mouseenter', function() {{
                    clearTimeout(timeoutId);
                }});
                
                dropdownContent.addEventListener('mouseleave', function() {{
                    timeoutId = setTimeout(function() {{
                        dropdownContent.style.display = 'none';
                    }}, 300);
                }});
                
                // Click to toggle dropdown (mobile friendly)
                const dropdownTrigger = dropdown.querySelector('.dropdown-trigger');
                dropdownTrigger.addEventListener('click', function(e) {{
                    e.preventDefault();
                    const isVisible = dropdownContent.style.display === 'block';
                    dropdownContent.style.display = isVisible ? 'none' : 'block';
                }});
                
                // Close dropdown when clicking outside
                document.addEventListener('click', function(e) {{
                    if (!dropdown.contains(e.target)) {{
                        dropdownContent.style.display = 'none';
                    }}
                }});
            }}
        }});
    </script>
</body>
</html>"""

    def _build_navigation(self, config: ClientConfig, current_city: str = "") -> str:
        """Build navigation menu with Service Area dropdown"""
        nav_html = '''
            <a href="index.html">Home</a>
            <span class="nav-divider">|</span>
            <a href="products.html">Products</a>
            <span class="nav-divider">|</span>
            <div class="dropdown">
                <a href="#" class="dropdown-trigger">Service Area <span class="dropdown-arrow">▼</span></a>
                <div class="dropdown-content">
                    <div class="cities-grid">
        '''
        
        # Add cities in 4-column grid format
        if hasattr(config, 'target_cities') and config.target_cities:
            for city in config.target_cities:
                city_slug = self._generate_city_slug(city)
                city_display = city.split(',')[0].strip()
                
                # Highlight current city if on a city page
                active_class = ' class="active-city"' if city_display.lower() == current_city.lower() else ''
                nav_html += f'                        <a href="{city_slug}.html"{active_class}>{city_display}</a>\n'
        
        nav_html += '''                    </div>
                </div>
            </div>
            <span class="nav-divider">|</span>
            <a href="contact.html">Contact Us</a>
        '''
        
        return nav_html
    
    def _generate_city_slug(self, city_name: str) -> str:
        """Generate URL slug from city name (matches location_page_generator pattern)"""
        # Replicate slugify functionality from location_page_generator
        slug = city_name.lower()
        slug = slug.replace(' ', '-')      # Spaces to hyphens
        slug = slug.replace(',', '')       # Remove commas
        slug = slug.replace(' illinois', '') # Remove state suffix
        slug = slug.replace(' il', '')     # Remove abbreviated state
        slug = slug.strip('-')            # Clean up trailing hyphens
        return slug

    # PART 2 - Continue from Part 1

    def _create_home_content(self, config: ClientConfig) -> str:
        """Create content for the home page with SEPARATE Services and Products sections"""
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

    def _create_enhanced_home_content(self, config: ClientConfig) -> str:
        """Create enhanced professional home page content using enhanced business data"""
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

    def _create_city_content(self, config: ClientConfig, city: str) -> str:
        """Create content for city-specific pages with separate Services and Products"""
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

    # PART 3 - Final section from Part 2

    def _create_footer_content(
        self, config: ClientConfig, city: str = "", is_home: bool = False
    ) -> str:
        """Create footer content with proper phone display and contact info"""
        business_name = config.business.business_name
        contact = config.contact

        footer_content = """
        <div class="footer-container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Contact Information</h3>
                    <p><strong>{business_name}</strong></p>""".format(business_name=business_name)

        # Add address
        if contact.address.street:
            footer_content += f'                    <p>{contact.address.street}<br>{contact.address.city}, {contact.address.state} {contact.address.zip_code}</p>\n'
        
        # Add phone with proper formatting for link
        if phone := contact.phone:
            # Display the phone as originally entered, not the normalized version
            display_phone = self._get_display_phone(phone)
            # Create tel link with normalized phone
            normalized_phone = self._normalize_phone(phone)
            footer_content += f'                    <p>Phone: <a href="tel:{normalized_phone}">{display_phone}</a></p>\n'

        if contact.email:
            footer_content += f'                    <p>Email: <a href="mailto:{contact.email}">{contact.email}</a></p>\n'

        footer_content += "                </div>\n                \n"

        # Add social media links if available in middle section
        social_links = config.social_media.get_valid_links()
        if social_links:
            footer_content += """                <div class="footer-section">
                    <h3>Follow Us</h3>
                    <div class="social-links">"""
            
            for platform, url in social_links.items():
                # Create single letter abbreviations for social platforms
                platform_letter = platform[0].lower()
                if platform == "youtube":
                    platform_letter = "y"
                elif platform == "instagram":
                    platform_letter = "i"
                elif platform == "linkedin":
                    platform_letter = "in"
                    
                footer_content += f'<a href="{url}" target="_blank" rel="noopener" title="{platform.title()}">{platform_letter}</a>'
            
            footer_content += """                    </div>
                </div>
                
"""

        # Add Google Business Profile map for home page
        if (
            is_home
            and config.google_business_profile
        ):
            gbp_embed = config.google_business_profile.get("embed_code", "")
            if gbp_embed:
                footer_content += f"""                <div class="footer-section">
                    <h3>Visit Our Location</h3>
                    <div class="map-container">
                        {gbp_embed}
                    </div>
                </div>"""

        # Add city-specific Google Map
        elif city and hasattr(config, "google_maps") and config.google_maps:
            city_maps = config.google_maps.get("cities", {})
            for city_key, city_data in city_maps.items():
                if city.lower() in city_key.lower():
                    city_embed = city_data.get("embed_code", "")
                    if city_embed:
                        footer_content += f"""                <div class="footer-section">
                    <h3>{city} Location</h3>
                    <div class="map-container">
                        {city_embed}
                    </div>
                </div>"""
                    break

        footer_content += """            </div>
            
            <div class="footer-bottom">
                <p>&copy; 2025 {business_name}. All rights reserved. | <a href="privacy-policy.html">Privacy Policy</a></p>
            </div>
        </div>""".format(business_name=business_name)

        return footer_content

    def _modify_iframe_size(self, iframe_code: str, width: int, height: int) -> str:
        """Modify iframe dimensions to specified size"""
        # Replace width and height attributes
        iframe_code = re.sub(r'width="[^"]*"', f'width="{width}"', iframe_code)
        iframe_code = re.sub(r'height="[^"]*"', f'height="{height}"', iframe_code)

        # Also replace in style attribute if present
        iframe_code = re.sub(r"width:\s*\d+px", f"width: {width}px", iframe_code)
        iframe_code = re.sub(r"height:\s*\d+px", f"height: {height}px", iframe_code)

        return iframe_code

    def _get_display_phone(self, phone: str) -> str:
        """Get proper display format for phone number"""
        if not phone:
            return ""

        # If phone looks like it's already formatted nicely, keep it
        if "(" in phone and ")" in phone and "-" in phone:
            return phone

        # Extract digits and format for display
        digits = "".join(filter(str.isdigit, phone))

        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits.startswith("1"):
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"

        return phone  # Return original if can't parse

    def _create_css_template(self, config: ClientConfig) -> str:
        """Create enhanced CSS template with logo and hero image support + Products styling"""
        branding = config.branding
        primary_color = branding.primary_color
        secondary_color = branding.secondary_color
        font_family = branding.font_family

        return f"""/* Enhanced styles for {config.business.business_name} website */

* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: {font_family};
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}}

/* Header Styles with Logo Support */
header {{
    background-color: {primary_color};
    color: white;
    padding: 1rem;
}}

.header-content {{
    max-width: 1200px;
    margin: 0 auto;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
}}

.logo-container {{
    display: flex;
    align-items: center;
    gap: 1rem;
    flex-shrink: 0;
}}

.logo-image {{
    max-height: 50px;
    height: auto;
    width: auto;
    max-width: 120px;
}}

.company-name {{
    font-size: 1.5rem;
    font-weight: bold;
    color: white;
    white-space: nowrap;
}}

header h1 {{
    margin: 0;
    font-size: 2rem;
}}

nav {{
    display: flex;
    flex-wrap: wrap;
    align-items: center;
}}

nav ul {{
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: 1rem;
    align-items: center;
}}

nav li {{
    position: relative;
}}

nav a {{
    color: white;
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;
    display: block;
}}

nav a:hover {{
    background-color: rgba(255,255,255,0.2);
}}

/* Navigation dividers */
.nav-divider {{
    color: white;
    margin: 0 0.5rem;
}}

/* Dropdown Menu Styles */
.dropdown {{
    position: relative;
    display: inline-block;
}}

.dropdown-trigger {{
    color: white;
    text-decoration: none;
    font-weight: 500;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}}

.dropdown-trigger:hover {{
    background-color: rgba(255,255,255,0.2);
}}

.dropdown-arrow {{
    font-size: 0.8rem;
    transition: transform 0.3s;
}}

.dropdown:hover .dropdown-arrow {{
    transform: rotate(180deg);
}}

.dropdown-content {{
    display: none;
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    background-color: white;
    min-width: 800px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
    z-index: 1000;
    border-radius: 8px;
    padding: 1rem;
    margin-top: 0.5rem;
}}

.dropdown:hover .dropdown-content {{
    display: block;
}}

/* Cities Grid - 4 columns as shown in mockup */
.cities-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.5rem;
}}

.cities-grid a {{
    color: #333;
    text-decoration: none;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s;
    text-align: center;
    font-weight: 500;
}}

.cities-grid a:hover {{
    background-color: #f0f0f0;
}}

/* Active city highlighting - yellow as shown in mockup */
.cities-grid a.active-city {{
    background-color: #FFD700;
    color: #333;
    font-weight: bold;
}}

.cities-grid a.active-city:hover {{
    background-color: #FFD700;
}}

main {{
    flex: 1;
    max-width: 1200px;
    margin: 0 auto;
    width: 100%;
}}

/* Enhanced Hero Section with Image Support */
.hero {{
    position: relative;
    padding: 4rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
    border-radius: 8px;
    overflow: hidden;
    min-height: 400px;
    display: flex;
    align-items: center;
    justify-content: center;
}}

.hero-overlay {{
    position: relative;
    z-index: 2;
    background-color: rgba(255,255,255,0.95);
    padding: 2rem;
    border-radius: 8px;
    max-width: 600px;
}}

.hero-image {{
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
    z-index: 1;
}}

.hero-text h2 {{
    color: {primary_color};
    margin-bottom: 1rem;
    font-size: 2.5rem;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
}}

.hero-text p {{
    font-size: 1.2rem;
    color: {secondary_color};
}}

/* Content Styles */
.content {{
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin: 0 2rem 2rem 2rem;
}}

.content h3 {{
    color: {secondary_color};
    margin: 1.5rem 0 1rem 0;
    font-size: 1.5rem;
}}

.content h4 {{
    color: {primary_color};
    margin: 1rem 0 0.5rem 0;
}}

.content ul {{
    margin-left: 2rem;
    margin-bottom: 1.5rem;
}}

.content li {{
    margin-bottom: 0.5rem;
}}

/* Enhanced Content Section Styles */
.content-section {{
    background-color: white;
    padding: 3rem 2rem;
    margin: 2rem auto;
    max-width: 1200px;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}

.content-section h2 {{
    color: {primary_color};
    margin-bottom: 2rem;
    font-size: 2rem;
    text-align: center;
}}

.content-section h3 {{
    color: {secondary_color};
    margin: 2rem 0 1rem 0;
    font-size: 1.5rem;
}}

.content-section p {{
    margin-bottom: 1.5rem;
    line-height: 1.8;
}}

.content-section .highlight {{
    color: {primary_color};
    font-weight: bold;
    text-decoration: none;
}}

.content-section .highlight:hover {{
    text-decoration: underline;
}}

/* Services Grid */
.services-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 1.5rem 0;
}}

.service-item {{
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid {primary_color};
    transition: transform 0.3s, box-shadow 0.3s;
}}

.service-item:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}}

.service-item h4 {{
    color: {primary_color};
    margin-bottom: 0.5rem;
}}

/* Products Grid - Similar to Services but with distinct styling */
.products-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    margin: 1.5rem 0;
}}

.product-item {{
    background-color: #f1f8ff;
    padding: 1.5rem;
    border-radius: 8px;
    border-left: 4px solid {secondary_color};
    transition: transform 0.3s, box-shadow 0.3s;
}}

.product-item:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}}

.product-item h4 {{
    color: {secondary_color};
    margin-bottom: 0.5rem;
}}

/* Enhanced Product Card Styles */
.product-card {{
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: transform 0.3s, box-shadow 0.3s;
}}

.product-card:hover {{
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}}

.product-card img {{
    width: 100%;
    height: 200px;
    object-fit: cover;
}}

.product-card-content {{
    padding: 1.5rem;
}}

.product-card-content h3 {{
    color: {primary_color};
    margin-bottom: 1rem;
    font-size: 1.3rem;
}}

.product-card-content p {{
    color: #666;
    margin-bottom: 1rem;
    line-height: 1.6;
}}

.product-link {{
    color: {secondary_color};
    text-decoration: none;
    font-weight: bold;
    transition: color 0.3s;
}}

.product-link:hover {{
    color: {primary_color};
}}

/* FAQ Styles */
.faq-section {{
    margin-top: 1rem;
}}

.faq-item {{
    margin-bottom: 1.5rem;
    padding: 1rem;
    background-color: #f8f9fa;
    border-radius: 5px;
    border-left: 4px solid {primary_color};
}}

.faq-item h4 {{
    margin-bottom: 0.5rem;
    color: {primary_color};
}}

/* Footer Styles */
footer {{
    background-color: {secondary_color};
    color: white;
    padding: 2rem 0 1rem 0;
    margin-top: 2rem;
}}

.footer-container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 2rem;
}}

.footer-content {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}}

.footer-section {{
    text-align: left;
}}

.footer-section:first-child {{
    text-align: left;
}}

.footer-section h3 {{
    margin-bottom: 1rem;
    color: {primary_color};
    font-size: 1.2rem;
}}

.footer-section h4 {{
    margin-bottom: 1rem;
    color: white;
    font-size: 1.2rem;
}}

.footer-section p {{
    margin-bottom: 0.5rem;
}}

.footer-section iframe {{
    border-radius: 8px;
    max-width: 100%;
}}

.social-links a {{
    color: white;
    text-decoration: none;
    margin: 0 0.5rem;
    font-size: 1.1rem;
    display: inline-block;
    padding: 0.5rem;
    transition: color 0.3s;
}}

.social-links a:hover {{
    color: {primary_color};
}}

.footer-bottom {{
    text-align: center;
    padding: 1rem 2rem;
    border-top: 1px solid rgba(255,255,255,0.2);
    margin-top: 1rem;
}}

/* Responsive design */
@media (max-width: 768px) {{
    .header-content {{
        flex-direction: column;
        text-align: center;
        gap: 1rem;
    }}
    
    nav {{
        justify-content: center;
        flex-direction: column;
        gap: 0.5rem;
    }}
    
    .nav-divider {{
        display: none;
    }}
    
    .dropdown-content {{
        min-width: 300px;
        left: 0;
        transform: none;
    }}
    
    .cities-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
    
    .hero {{
        padding: 2rem 1rem;
        min-height: 300px;
    }}
    
    .hero-text h2 {{
        font-size: 2rem;
    }}
    
    .content {{
        margin: 0 1rem 1rem 1rem;
        padding: 1rem;
    }}
    
    .services-grid, .products-grid {{
        grid-template-columns: 1fr;
    }}
    
    .footer-content {{
        grid-template-columns: 1fr;
        gap: 1rem;
    }}
    
    .footer-section iframe {{
        width: 100%;
        height: 300px;
    }}
}}

@media (max-width: 480px) {{
    header h1 {{
        font-size: 1.5rem;
    }}
    
    .hero-text h2 {{
        font-size: 1.5rem;
    }}
    
    nav a {{
        padding: 0.25rem 0.5rem;
        font-size: 0.9rem;
    }}
}}

/* Enhanced Professional Template Styles */
.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}}

/* Enhanced Hero Section */
.hero-content {{
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
}}

.hero-tagline {{
    font-size: 1.2rem;
    margin: 1rem 0;
    font-weight: 300;
}}

.years-experience {{
    font-size: 1rem;
    margin: 0.5rem 0;
    opacity: 0.9;
}}

.hero-cta {{
    margin-top: 2rem;
    display: flex;
    gap: 1rem;
    justify-content: center;
    flex-wrap: wrap;
}}

.cta-button {{
    display: inline-block;
    padding: 12px 24px;
    text-decoration: none;
    border-radius: 5px;
    font-weight: bold;
    transition: all 0.3s ease;
}}

.cta-button.primary {{
    background-color: {primary_color};
    color: white;
}}

.cta-button.secondary {{
    background-color: transparent;
    color: white;
    border: 2px solid white;
}}

.cta-button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}}

/* About Section */
.about-section {{
    padding: 4rem 0;
    background-color: white;
}}

.company-overview {{
    font-size: 1.1rem;
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
}}

/* Why Choose Us Section */
.why-choose-us {{
    padding: 4rem 0;
    background-color: #f8f9fa;
}}

.reasons-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}}

.reason-item {{
    background: white;
    padding: 2rem;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    transition: transform 0.3s ease;
}}

.reason-item:hover {{
    transform: translateY(-5px);
}}

/* Company Statistics */
.company-stats {{
    padding: 4rem 0;
    background-color: {primary_color};
    color: white;
}}

.stats-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 2rem;
    text-align: center;
}}

.stat-item {{
    padding: 1rem;
}}

.stat-number {{
    font-size: 3rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}}

.stat-label {{
    font-size: 1.1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}}

/* Products Section Enhancement */
.products-section {{
    padding: 4rem 0;
    background-color: white;
}}

.products-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}}

.product-item {{
    background: #f8f9fa;
    padding: 2rem;
    border-radius: 8px;
    border-left: 4px solid {primary_color};
    transition: transform 0.3s ease;
}}

.product-item:hover {{
    transform: translateY(-3px);
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
}}

/* Service Guarantee */
.service-guarantee {{
    padding: 4rem 0;
    background-color: #f8f9fa;
    text-align: center;
}}

.guarantee-text {{
    font-size: 1.2rem;
    max-width: 600px;
    margin: 0 auto;
    font-style: italic;
}}

/* Enhanced Contact Section */
.enhanced-contact {{
    padding: 4rem 0;
    background-color: white;
}}

.contact-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 3rem;
    margin-top: 2rem;
}}

.contact-methods a {{
    color: {primary_color};
    text-decoration: none;
}}

.contact-methods a:hover {{
    text-decoration: underline;
}}

.response-time {{
    font-style: italic;
    color: {secondary_color};
    margin-top: 1rem;
}}

.business-hours p {{
    margin: 0.5rem 0;
    padding: 0.25rem 0;
    border-bottom: 1px solid #eee;
}}

/* Service Area */
.service-area {{
    padding: 4rem 0;
    background-color: #f8f9fa;
    text-align: center;
}}

/* FAQ Section Enhancement */
.faq-section {{
    padding: 4rem 0;
    background-color: white;
}}

.faq-items {{
    max-width: 800px;
    margin: 2rem auto 0;
}}

.faq-item {{
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: #f8f9fa;
    border-radius: 8px;
    border-left: 4px solid {primary_color};
}}

.faq-item h3 {{
    margin-bottom: 1rem;
    color: {primary_color};
}}

/* Responsive Enhancements */
@media (max-width: 768px) {{
    .hero-cta {{
        flex-direction: column;
        align-items: center;
    }}
    
    .stats-grid {{
        grid-template-columns: repeat(2, 1fr);
    }}
    
    .stat-number {{
        font-size: 2rem;
    }}
    
    .contact-grid {{
        grid-template-columns: 1fr;
    }}
}}

@media (max-width: 480px) {{
    .stats-grid {{
        grid-template-columns: 1fr;
    }}
    
    .reasons-grid {{
        grid-template-columns: 1fr;
    }}
    
    .products-grid {{
        grid-template-columns: 1fr;
    }}
}}
"""
