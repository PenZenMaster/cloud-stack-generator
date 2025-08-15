"""
City Page Generator
Generates SEO-optimized city-specific pages for local authority building

Based on location_page_generator.py but adapted for multiple business types
and integrated with the Cloud Stack Generator architecture.

Author: Cloud Stack Generator Team
Version: 2.0
"""

import os
import urllib.parse
from typing import List, Dict, Any
from ..config.models import ClientConfig


class CityPageGenerator:
    """Generate SEO-optimized city pages for local authority building"""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.google_maps_api_key = None  # Will be loaded from secure storage
        
    def generate_city_page(self, city: str, output_dir: str) -> str:
        """Generate a single city page"""
        # Generate slug using same pattern as location_page_generator
        city_slug = self._generate_city_slug(city)
        
        # Extract city name without state for content
        city_name = city.split(',')[0].strip()
        
        # Generate SEO-optimized content
        html_content = self._create_city_html(city, city_name)
        
        # Write to file
        file_path = os.path.join(output_dir, f"{city_slug}.html")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        return file_path
    
    def generate_all_city_pages(self, output_dir: str) -> List[str]:
        """Generate all city pages from target_cities"""
        generated_files = []
        
        if not hasattr(self.config, 'target_cities') or not self.config.target_cities:
            return generated_files
            
        for city in self.config.target_cities:
            try:
                file_path = self.generate_city_page(city, output_dir)
                generated_files.append(file_path)
            except Exception as e:
                print(f"Error generating page for {city}: {e}")
                
        return generated_files
    
    def _generate_city_slug(self, city_name: str) -> str:
        """Generate URL slug from city name (matches location_page_generator pattern)"""
        slug = city_name.lower()
        slug = slug.replace(' ', '-')      # Spaces to hyphens
        slug = slug.replace(',', '')       # Remove commas
        slug = slug.replace(' illinois', '') # Remove state suffix
        slug = slug.replace(' il', '')     # Remove abbreviated state
        slug = slug.strip('-')            # Clean up trailing hyphens
        return slug
    
    def _create_city_html(self, full_city: str, city_name: str) -> str:
        """Create complete HTML for city page"""
        business_name = self.config.business.business_name
        industry = self.config.business.industry
        contact = self.config.contact
        
        # Generate page title and focus keyword
        focus_keyword = f"{industry} in {city_name}"
        page_title = f"{focus_keyword} - {business_name}"
        
        # Create content sections
        intro_section = self._create_intro_section(city_name, focus_keyword, business_name)
        why_us_section = self._create_why_us_section(city_name, focus_keyword, business_name)
        services_section = self._create_services_section(city_name)
        local_section = self._create_local_section(city_name)
        contact_section = self._create_contact_section(city_name)
        
        # Build complete HTML
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{page_title}</title>
    <meta name="description" content="{industry} services in {city_name} by {business_name}">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <div class="header-content">
            <img src="{self.config.branding.logo_url}" alt="{business_name} Logo" class="logo">
            {self._build_navigation()}
        </div>
    </header>
    
    <main>
        <section class="hero" style="background-image: url('https://salvometalworks.com/wp-content/uploads/2024/11/Homepage_Hero_Fallback.webp'); background-size: cover; background-position: center;">
            <div class="hero-overlay">
                <div class="hero-text">
                    <h1>{focus_keyword}</h1>
                    <p>Professional {industry.lower()} services serving {city_name} and surrounding areas</p>
                </div>
            </div>
        </section>
        
        <section class="content">
            {intro_section}
            
            {why_us_section}
            
            {services_section}
            
            {local_section}
            
            {self._create_maps_section(full_city)}
            
            {self._create_directions_section(full_city)}
            
            {contact_section}
        </section>
    </main>
    
    <footer>
        <div class="footer-content">
            <div class="footer-section contact-info">
                <h4>Contact Information</h4>
                <p><strong>Phone:</strong> {self._format_phone_for_display(contact.phone)}</p>
                <p><strong>Address:</strong> {contact.address.to_single_line()}</p>
                <p><strong>Email:</strong> {contact.email}</p>
            </div>
            {self._create_social_media_section()}
        </div>
        <div class="footer-bottom">
            <p>&copy; 2025 {business_name}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>"""
        
        return html_content
    
    def _create_intro_section(self, city_name: str, focus_keyword: str, business_name: str) -> str:
        """Create introduction section"""
        return f"""
            <h2>Local {self.config.business.industry} Experts in {city_name}</h2>
            <p>{business_name} is proud to serve {city_name} with professional {self.config.business.industry.lower()} services. Our local expertise and commitment to excellence make us the preferred choice for {city_name} residents and businesses.</p>
        """
    
    def _create_why_us_section(self, city_name: str, focus_keyword: str, business_name: str) -> str:
        """Create why choose us section"""
        return f"""
            <h2>Why Choose Us in {city_name}</h2>
            <ul>
                <li>Local {city_name} expertise and knowledge</li>
                <li>Proven track record in the {city_name} area</li>
                <li>Personalized {self.config.business.industry.lower()} solutions</li>
                <li>Committed to the {city_name} community</li>
            </ul>
        """
    
    def _create_services_section(self, city_name: str) -> str:
        """Create services section"""
        services_html = f"""
            <h2>Our {self.config.business.industry} Services in {city_name}</h2>
            <div class="services-grid">
        """
        
        # Add services from config
        for service in self.config.services:
            services_html += f"""
                <div class="service-item">
                    <h4>{service.name} in {city_name}</h4>
                    <p>Professional {service.name.lower()} services</p>
                </div>
            """
        
        # If no services configured, add default content
        if not self.config.services:
            services_html += f"""
                <div class="service-item">
                    <h4>Professional {self.config.business.industry} in {city_name}</h4>
                    <p>Comprehensive {self.config.business.industry.lower()} solutions for {city_name} businesses and residents</p>
                </div>
            """
        
        services_html += """
            </div>
        """
        
        return services_html
    
    def _create_local_section(self, city_name: str) -> str:
        """Create local area section"""
        return f"""
            <h2>Serving the {city_name} Community</h2>
            <p>As a trusted provider in the {city_name} area, we understand the unique needs of local businesses and residents. Our team is committed to delivering exceptional results while supporting the {city_name} community.</p>
        """
    
    def _create_maps_section(self, full_city: str) -> str:
        """Create Google Maps embed section"""
        if self.google_maps_api_key:
            # Use API if available
            map_embed_url = self._build_google_map_embed(full_city)
            return f"""
                <h2>Explore {full_city.split(',')[0].strip()}</h2>
                <iframe src="{map_embed_url}" width="100%" height="400" style="border:0;" allowfullscreen loading="lazy"></iframe>
            """
        else:
            # Fallback without API
            return f"""
                <h2>Serving {full_city.split(',')[0].strip()}</h2>
                <p>We proudly serve the {full_city} area with professional {self.config.business.industry.lower()} services.</p>
            """
    
    def _create_directions_section(self, full_city: str) -> str:
        """Create driving directions section"""
        city_name = full_city.split(',')[0].strip()
        hq_address = self.config.contact.address.to_single_line()
        
        if self.google_maps_api_key:
            # Use API if available
            directions_embed_url = self._build_google_directions_embed(full_city, hq_address)
            return f"""
                <h2>Driving Directions to Our Office from {city_name}</h2>
                <p>We're located at {hq_address}.</p>
                <iframe src="{directions_embed_url}" width="100%" height="400" style="border:0;" allowfullscreen loading="lazy"></iframe>
            """
        else:
            # Fallback without API
            return f"""
                <h2>Contact Our {city_name} Team</h2>
                <p>Ready to discuss your {self.config.business.industry.lower()} project in {city_name}? Contact our team today for a consultation.</p>
            """
    
    def _create_contact_section(self, city_name: str) -> str:
        """Create contact/CTA section"""
        return f"""
            <h2>Get Your Free Quote Today</h2>
            <p>Looking for reliable {self.config.business.industry.lower()} services in {city_name}? Contact {self.config.business.business_name} today for a free consultation and quote.</p>
        """
    
    def _create_social_media_section(self) -> str:
        """Create social media section"""
        if not hasattr(self.config, 'social_media'):
            return ""
            
        social_links = []
        social_media = self.config.social_media
        
        if hasattr(social_media, 'facebook') and social_media.facebook:
            social_links.append(f'<a href="{social_media.facebook}" target="_blank" rel="noopener noreferrer">Facebook</a>')
        if hasattr(social_media, 'linkedin') and social_media.linkedin:
            social_links.append(f'<a href="{social_media.linkedin}" target="_blank" rel="noopener noreferrer">LinkedIn</a>')
        if hasattr(social_media, 'instagram') and social_media.instagram:
            social_links.append(f'<a href="{social_media.instagram}" target="_blank" rel="noopener noreferrer">Instagram</a>')
        if hasattr(social_media, 'youtube') and social_media.youtube:
            social_links.append(f'<a href="{social_media.youtube}" target="_blank" rel="noopener noreferrer">YouTube</a>')
        
        if social_links:
            return f"""
            <div class="footer-section social-media">
                <h4>Follow Us</h4>
                <div class="social-links">
                    {' | '.join(social_links)}
                </div>
            </div>
            """
        
        return ""
    
    def _build_navigation(self) -> str:
        """Build navigation menu (reuse from website_generator)"""
        nav_links = '<a href="index.html">Home</a>'
        
        # Add city pages dynamically from target_cities
        if hasattr(self.config, 'target_cities') and self.config.target_cities:
            for city in self.config.target_cities:
                city_slug = self._generate_city_slug(city)
                city_display = city.split(',')[0].strip()
                nav_links += f' | <a href="{city_slug}.html">{city_display}</a>'
        
        return f'<nav>{nav_links}</nav>'
    
    def _build_google_map_embed(self, location: str) -> str:
        """Build Google Maps embed URL"""
        if not self.google_maps_api_key:
            return ""
        q = urllib.parse.quote(location)
        return f"https://www.google.com/maps/embed/v1/place?key={self.google_maps_api_key}&q={q}"
    
    def _build_google_directions_embed(self, start: str, end: str) -> str:
        """Build Google Directions embed URL"""
        if not self.google_maps_api_key:
            return ""
        origin = urllib.parse.quote(start)
        destination = urllib.parse.quote(end)
        return f"https://www.google.com/maps/embed/v1/directions?key={self.google_maps_api_key}&origin={origin}&destination={destination}"
    
    def _format_phone_for_display(self, phone: str) -> str:
        """Format phone number for display"""
        if not phone:
            return ""
        
        # Extract digits and format for display
        digits = "".join(filter(str.isdigit, phone))
        
        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits.startswith("1"):
            return f"({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        
        return phone  # Return original if can't parse