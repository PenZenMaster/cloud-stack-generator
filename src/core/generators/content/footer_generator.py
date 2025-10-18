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
"""

import re
from typing import TYPE_CHECKING

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

    def _normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number for tel: links (remove all non-digits).

        Args:
            phone: Phone number string in any format

        Returns:
            Phone number with only digits (suitable for tel: link)
        """
        if not phone:
            return ""
        # Remove all non-digit characters for tel: link
        return "".join(filter(str.isdigit, phone))

    def _get_display_phone(self, phone: str) -> str:
        """
        Get proper display format for phone number.

        Args:
            phone: Phone number string in any format

        Returns:
            Formatted phone number for display (xxx) xxx-xxxx
        """
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

    def modify_iframe_size(self, iframe_code: str, width: int, height: int) -> str:
        """
        Modify iframe dimensions to specified size.

        Args:
            iframe_code: HTML iframe code
            width: Desired width in pixels
            height: Desired height in pixels

        Returns:
            Modified iframe HTML with new dimensions
        """
        # Replace width and height attributes
        iframe_code = re.sub(r'width="[^"]*"', f'width="{width}"', iframe_code)
        iframe_code = re.sub(r'height="[^"]*"', f'height="{height}"', iframe_code)

        # Also replace in style attribute if present
        iframe_code = re.sub(r"width:\s*\d+px", f"width: {width}px", iframe_code)
        iframe_code = re.sub(r"height:\s*\d+px", f"height: {height}px", iframe_code)

        return iframe_code
