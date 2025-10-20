"""
Footer Generator
Path: E:/projects/cloud-stack-generator/src/core/generators/content/footer_generator.py

Description:
Generates HTML content for footer sections. Extracted from website_generator.py
to improve separation of concerns and maintainability.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-17

Last Modified Date:
2025-10-17

Comments:
* v1.00 - Initial extraction from website_generator.py
* Fixed missing _normalize_phone method bug from original code
* v1.01 - Refactored to use centralized string_utils and html_utils
"""

from typing import TYPE_CHECKING

# Import utilities
from ...utils.string_utils import normalize_phone, format_phone_display

if TYPE_CHECKING:
    from ...config.models import ClientConfig


class FooterGenerator:
    """Generates HTML content for footer sections"""

    def __init__(self):
        """Initialize the footer generator"""
        pass

    def generate_footer_content(
        self, config: "ClientConfig", city: str = "", is_home: bool = False
    ) -> str:
        """
        Create footer content with proper phone display and contact info.

        Args:
            config: Client configuration containing business and contact data
            city: Optional city name for city-specific content
            is_home: Whether this is the home page (affects GBP display)

        Returns:
            HTML string for the footer content
        """
        business_name = config.business.business_name
        contact = config.contact

        footer_content = """
        <div class="footer-container">
            <div class="footer-content">
                <div class="footer-section">
                    <h3>Contact Information</h3>
                    <p><strong>{business_name}</strong></p>""".format(
            business_name=business_name
        )

        # Add address
        if contact.address.street:
            footer_content += f'                    <p>{contact.address.street}<br>{contact.address.city}, {contact.address.state} {contact.address.zip_code}</p>\n'

        # Add phone with proper formatting for link
        if phone := contact.phone:
            # Display the phone as originally entered, not the normalized version
            display_phone = format_phone_display(phone)
            # Create tel link with normalized phone
            normalized_phone = normalize_phone(phone)
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
        if is_home and config.google_business_profile:
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
        </div>""".format(
            business_name=business_name
        )

        return footer_content
