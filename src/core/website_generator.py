"""
Filename: src/core/website_generator.py
Path: E:\\projects\\cloud-stack-generator\\src\\core\\website_generator.py
Description: Enhanced Website Generator with GBP integration and fixes

Version: 2.0.0
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

import os
import re
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from .config_parser import ClientConfig


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

            # Generate city pages if configured
            if config.pages:
                for page in config.pages:
                    if page.get("slug") != "index":  # Skip home page
                        page_path = self._generate_city_page(config, page)
                        generated_files.append(page_path)

            # Generate CSS file
            css_path = self._generate_css_file(config)
            generated_files.append(css_path)

            return GenerationResult(success=True, generated_files=generated_files)

        except Exception as e:
            return GenerationResult(success=False, generated_files=[], errors=str(e))

    def _generate_index_page(self, config: ClientConfig) -> str:
        """Generate the main index.html page"""
        if not self.output_dir:
            raise GenerationError("Output directory not set")

        html_content = self._create_html_template(config, "Home", is_home=True)

        file_path = os.path.join(self.output_dir, "index.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return file_path

    def _generate_city_page(self, config: ClientConfig, page_config: dict) -> str:
        """Generate a city-specific page"""
        if not self.output_dir:
            raise GenerationError("Output directory not set")

        title = page_config.get("title", "Services")
        slug = page_config.get("slug", "page")
        city = page_config.get("city", "")

        html_content = self._create_html_template(
            config, title, is_home=False, city=city
        )

        file_path = os.path.join(self.output_dir, f"{slug}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return file_path

    def _generate_css_file(self, config: ClientConfig) -> str:
        """Generate basic CSS file"""
        if not self.output_dir:
            raise GenerationError("Output directory not set")

        css_content = self._create_css_template(config)

        file_path = os.path.join(self.output_dir, "styles.css")
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
        """Create enhanced HTML template with proper navigation and GBP integration"""
        business_name = config.business_name
        industry = config.industry

        # Get branding colors
        branding = config.branding or {}
        primary_color = branding.get("primary_color", "#007bff")

        # Build navigation with proper page titles
        nav_links = self._build_navigation(config)

        # Page-specific content
        if is_home:
            page_content = self._create_home_content(config)
        else:
            page_content = self._create_city_content(config, city)

        # Footer content with GBP and city maps
        footer_content = self._create_footer_content(config, city, is_home)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title} - {business_name}</title>
    <meta name="description" content="{industry} services by {business_name}{' in ' + city if city else ''}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>{business_name}</h1>
        <nav>{nav_links}</nav>
    </header>
    
    <main>
        {page_content}
    </main>
    
    <footer>
        {footer_content}
    </footer>
</body>
</html>"""

    def _build_navigation(self, config: ClientConfig) -> str:
        """Build proper navigation menu"""
        nav_links = ""
        if config.pages:
            for page in config.pages:
                slug = page.get("slug", "")
                # Use proper page titles instead of phone numbers
                if slug == "index":
                    title = "Home"
                else:
                    # Extract city name from page title
                    page_title = page.get("title", "")
                    city = page.get("city", "")
                    title = (
                        city
                        if city
                        else page_title.replace(f"{config.industry} in ", "")
                    )

                link = "index.html" if slug == "index" else f"{slug}.html"
                nav_links += f'<a href="{link}">{title}</a> | '

        return nav_links.rstrip(" | ")

    def _create_home_content(self, config: ClientConfig) -> str:
        """Create content for the home page"""
        business_name = config.business_name
        industry = config.industry

        # Hero section
        content = f"""
        <section class="hero">
            <h2>Welcome to {business_name}</h2>
            <p>Professional {industry.lower()} services you can trust</p>
        </section>
        
        <section class="content">
            <h3>About Our {industry}</h3>
            <p>Welcome to {business_name}, your trusted provider of {industry.lower()} services. We are committed to delivering exceptional results and outstanding customer service.</p>
            
            <h3>Our Services</h3>
            <ul>"""

        # Add services if available
        if config.offerings:
            for offering in config.offerings:
                service_name = offering.get("name", "Service")
                content += f"                <li><strong>{service_name}</strong></li>\n"
        else:
            content += (
                f"                <li>Professional {industry} consultation</li>\n"
            )
            content += f"                <li>Expert {industry.lower()} solutions</li>\n"
            content += f"                <li>Quality {industry.lower()} services</li>\n"

        content += "            </ul>\n"

        # Add FAQ section if available
        if hasattr(config, "faq") and config.faq:
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
                if page.get("slug") != "index":
                    city = page.get("city", "")
                    if city:
                        content += f"                <li>{city}</li>\n"

            content += "            </ul>"

        content += "        </section>"
        return content

    def _create_city_content(self, config: ClientConfig, city: str) -> str:
        """Create content for city-specific pages"""
        business_name = config.business_name
        industry = config.industry

        content = f"""
        <section class="hero">
            <h2>{industry} Services in {city}</h2>
            <p>Professional {industry.lower()} services serving {city} and surrounding areas</p>
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
            <ul>"""

        # Add services if available
        if config.offerings:
            for offering in config.offerings:
                service_name = offering.get("name", "Service")
                content += f"                <li><strong>{service_name}</strong> in {city}</li>\n"
        else:
            content += f"                <li>Professional {industry} consultation in {city}</li>\n"
            content += f"                <li>Expert {industry.lower()} solutions for {city}</li>\n"
            content += f"                <li>Quality {industry.lower()} services in {city}</li>\n"

        content += (
            """            </ul>
            
            <h3>Contact Us Today</h3>
            <p>Ready to get started? Contact us today to learn more about our services in """
            + city
            + """.</p>
        </section>"""
        )

        return content

    def _create_footer_content(
        self, config: ClientConfig, city: str = "", is_home: bool = False
    ) -> str:
        """Create footer content with contact info, GBP map, and social links"""
        business_name = config.business_name
        contact = config.contact or {}

        footer_content = """
        <div class="footer-container">
            <div class="footer-section contact-info">
                <h4>Contact Information</h4>"""

        # Add contact info
        if contact.get("phone"):
            footer_content += (
                f'                <p><strong>Phone:</strong> {contact["phone"]}</p>\n'
            )
        if contact.get("address"):
            footer_content += f'                <p><strong>Address:</strong> {contact["address"]}</p>\n'
        if contact.get("email"):
            footer_content += (
                f'                <p><strong>Email:</strong> {contact["email"]}</p>\n'
            )

        footer_content += "            </div>\n"

        # Add Google Business Profile map for home page
        if (
            is_home
            and hasattr(config, "google_business_profile")
            and config.google_business_profile
        ):
            gbp_embed = config.google_business_profile.get("embed_code", "")
            if gbp_embed:
                # Modify the iframe to be 480x480
                modified_embed = self._modify_iframe_size(gbp_embed, 480, 480)
                footer_content += f"""
            <div class="footer-section gbp-map">
                <h4>Find Us</h4>
                {modified_embed}
            </div>"""

        # Add city-specific Google Map
        elif city and hasattr(config, "google_maps") and config.google_maps:
            city_maps = config.google_maps.get("cities", {})
            for city_key, city_data in city_maps.items():
                if city.lower() in city_key.lower():
                    city_embed = city_data.get("embed_code", "")
                    if city_embed:
                        modified_embed = self._modify_iframe_size(city_embed, 480, 480)
                        footer_content += f"""
            <div class="footer-section city-map">
                <h4>{city} Location</h4>
                {modified_embed}
            </div>"""
                    break

        # Add social media links
        if config.social_media:
            footer_content += """
            <div class="footer-section social-links">
                <h4>Follow Us</h4>"""

            for platform, url in config.social_media.items():
                footer_content += f'                <a href="{url}" target="_blank">{platform.title()}</a><br>\n'

            footer_content += "            </div>"

        footer_content += f"""
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 {business_name}. All rights reserved.</p>
        </div>"""

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

    def _create_css_template(self, config: ClientConfig) -> str:
        """Create enhanced CSS template with footer layout"""
        branding = config.branding or {}
        primary_color = branding.get("primary_color", "#007bff")
        secondary_color = branding.get("secondary_color", "#6c757d")
        font_family = branding.get("font_family", "Arial, sans-serif")

        return f"""/* Enhanced styles for {config.business_name} website */

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

header {{
    background-color: {primary_color};
    color: white;
    padding: 1rem;
    text-align: center;
}}

header h1 {{
    margin-bottom: 0.5rem;
    font-size: 2rem;
}}

nav a {{
    color: white;
    text-decoration: none;
    margin: 0 0.5rem;
    font-weight: 500;
}}

nav a:hover {{
    text-decoration: underline;
}}

main {{
    flex: 1;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
    width: 100%;
}}

.hero {{
    background-color: white;
    padding: 3rem 2rem;
    text-align: center;
    margin-bottom: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}}

.hero h2 {{
    color: {primary_color};
    margin-bottom: 1rem;
    font-size: 2.5rem;
}}

.content {{
    background-color: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
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
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    padding: 0 2rem;
}}

.footer-section {{
    text-align: center;
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
}}

.social-links a:hover {{
    text-decoration: underline;
}}

.footer-bottom {{
    text-align: center;
    padding: 1rem 2rem;
    border-top: 1px solid rgba(255,255,255,0.2);
    margin-top: 1rem;
}}

/* Responsive design */
@media (max-width: 768px) {{
    main {{
        padding: 1rem;
    }}
    
    .hero {{
        padding: 2rem 1rem;
    }}
    
    .hero h2 {{
        font-size: 2rem;
    }}
    
    nav a {{
        display: block;
        margin: 0.5rem 0;
    }}
    
    .footer-container {{
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
    
    .hero h2 {{
        font-size: 1.5rem;
    }}
    
    .content {{
        padding: 1rem;
    }}
}}
"""
