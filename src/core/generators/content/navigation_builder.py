"""
Navigation Builder
Path: E:/projects/cloud-stack-generator/src/core/generators/content/navigation_builder.py

Description:
Builds HTML navigation menu structures. Extracted from website_generator.py
to improve separation of concerns and maintainability.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-17

Last Modified Date:
2025-10-17

Comments:
* v1.00 - Initial extraction from website_generator.py
* v1.01 - Refactored to use centralized string_utils
"""

from typing import TYPE_CHECKING

# Import utilities
from ...utils.string_utils import generate_city_slug

if TYPE_CHECKING:
    from ...config.models import ClientConfig


class NavigationBuilder:
    """Builds HTML navigation menu structures"""

    def __init__(self):
        """Initialize the navigation builder"""
        pass

    def build_navigation(self, config: "ClientConfig", current_city: str = "") -> str:
        """
        Build navigation menu with Service Area dropdown.

        Args:
            config: Client configuration containing target cities
            current_city: Optional current city name to highlight in navigation

        Returns:
            HTML string for the navigation menu
        """
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
                city_slug = generate_city_slug(city)
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
