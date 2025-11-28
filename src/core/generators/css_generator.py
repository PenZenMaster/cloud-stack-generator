# src/core/generators/css_generator.py
"""
Module/Script Name: css_generator.py
Path: src/core/generators/css_generator.py

Description:
CSS Generator - Responsive Styling and Branding. Generates CSS from branding
configuration with responsive design and professional styling.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2024-09-15

Last Modified Date:
2025-11-25

Version: 1.01

Comments:
* v1.01 - Added H1/H2/H3/Menu text color variables and hero background image support
* v1.00 - Initial implementation with responsive styling
"""

from ..config.models import ClientConfig, BrandingConfig


class CSSGenerator:
    """Generates CSS styles from branding configuration"""

    def _get_base_styles(self) -> str:
        """Base styles for common elements"""
        return """/* Base Styles */
html {
    scroll-behavior: smooth;
}

body {
    font-family: var(--font-family);
    font-size: var(--font-size-base);
    color: var(--gray-800);
    background-color: var(--white);
    line-height: 1.6;
}

.container {
    max-width: var(--container-max-width);
    margin: 0 auto;
    padding: 0 var(--spacing-md);
}

@media (min-width: 768px) {
    .container {
        padding: 0 var(--spacing-lg);
    }
}

.sr-only {
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}"""

    def __init__(self):
        self.base_styles = self._get_base_styles()
        
    def generate_css(self, config: ClientConfig) -> str:
        """Generate CSS file with branding and responsive design (alias for generate_main_css)"""
        return self.generate_main_css(config)
        
    def generate_main_css(self, config: ClientConfig) -> str:
        """Generate main CSS file with branding and responsive design"""
        if not config or not hasattr(config, 'branding'):
            # Return an empty string or a default CSS if config is invalid
            return ""
        branding = config.branding

        css_parts = [
            self._generate_css_variables(branding),
            self._get_reset_styles(),
            self.base_styles,
            self._generate_typography_styles(branding),
            self._generate_color_scheme_styles(branding),
            self._generate_layout_styles(),
            self._generate_component_styles(branding),
            self._generate_responsive_styles(),
            self._generate_utility_styles(branding)
        ]

        return '\n\n'.join(css_parts)
    
    def _lighten_color(self, color: str, amount: float) -> str:
        """Lighten a hex color by the specified amount (0.0-1.0)"""
        if not color.startswith('#'):
            return color
        try:
            # Remove # and convert to RGB
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Lighten each component
            lightened = tuple(min(255, int(c + (255 - c) * amount)) for c in rgb)
            return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"
        except (ValueError, TypeError):
            return color

    def _darken_color(self, color: str, amount: float) -> str:
        """Darken a hex color by the specified amount (0.0-1.0)"""
        if not color.startswith('#'):
            return color
        try:
            # Remove # and convert to RGB
            hex_color = color.lstrip('#')
            rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            # Darken each component
            darkened = tuple(max(0, int(c * (1 - amount))) for c in rgb)
            return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"
        except (ValueError, TypeError):
            return color

    def _generate_css_variables(self, branding: BrandingConfig) -> str:
        """Generate CSS custom properties for consistent theming"""
        # Calculate additional colors based on primary/secondary
        primary_light = self._lighten_color(branding.primary_color, 0.1)
        primary_dark = self._darken_color(branding.primary_color, 0.1)
        secondary_light = self._lighten_color(branding.secondary_color, 0.1)
        secondary_dark = self._darken_color(branding.secondary_color, 0.1)
        
        # Get new color values with fallbacks
        body_bg_color = getattr(branding, 'body_background_color', '#ffffff')
        body_text_color = getattr(branding, 'body_text_color', '#333333')
        footer_bg_color = getattr(branding, 'footer_background_color', '#2c3e50')
        footer_text_color = getattr(branding, 'footer_text_color', '#ffffff')
        h1_text_color = getattr(branding, 'h1_text_color', '#2c3e50')
        h2_text_color = getattr(branding, 'h2_text_color', '#34495e')
        h3_text_color = getattr(branding, 'h3_text_color', '#34495e')
        menu_text_color = getattr(branding, 'main_menu_text_color', '#ffffff')
        hero_bg_image = getattr(branding, 'hero_background_image_url', '')
        
        return f"""/* CSS Custom Properties for Branding */
:root {{
    /* Header Colors (renamed from Brand Colors) */
    --header-bg-color-1: {branding.primary_color};
    --header-bg-color-2: {branding.secondary_color};
    --primary-color: {branding.primary_color}; /* Keep for backward compatibility */
    --secondary-color: {branding.secondary_color}; /* Keep for backward compatibility */
    --primary-light: {primary_light};
    --primary-dark: {primary_dark};
    --secondary-light: {secondary_light};
    --secondary-dark: {secondary_dark};

    /* New Body and Footer Colors */
    --body-bg-color: {body_bg_color};
    --body-text-color: {body_text_color};
    --footer-bg-color: {footer_bg_color};
    --footer-text-color: {footer_text_color};

    /* Heading Text Colors */
    --h1-text-color: {h1_text_color};
    --h2-text-color: {h2_text_color};
    --h3-text-color: {h3_text_color};

    /* Navigation Colors */
    --menu-text-color: {menu_text_color};

    /* Hero Background */
    --hero-bg-image: {'url(' + hero_bg_image + ')' if hero_bg_image else 'none'};

    /* Typography */
    --font-family: {branding.font_family};
    --font-size-base: 16px;
    --font-size-sm: 14px;
    --font-size-lg: 18px;
    --font-size-xl: 24px;
    --font-size-2xl: 32px;
    --font-size-3xl: 48px;
    
    /* Spacing */
    --spacing-xs: 0.25rem;
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    --spacing-xl: 2rem;
    --spacing-2xl: 3rem;
    --spacing-3xl: 4rem;
    
    /* Layout */
    --container-max-width: 1200px;
    --header-height: 70px;
    --border-radius: 8px;
    --box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    --box-shadow-lg: 0 4px 8px rgba(0, 0, 0, 0.15);
    
    /* Neutral Colors */
    --white: #ffffff;
    --gray-50: #f9fafb;
    --gray-100: #f3f4f6;
    --gray-200: #e5e7eb;
    --gray-300: #d1d5db;
    --gray-400: #9ca3af;
    --gray-500: #6b7280;
    --gray-600: #4b5563;
    --gray-700: #374151;
    --gray-800: #1f2937;
    --gray-900: #111827;
    
    /* Status Colors */
    --success: #10b981;
    --warning: #f59e0b;
    --error: #ef4444;
    --info: #3b82f6;
}}"""
    
    def _get_reset_styles(self) -> str:
        """CSS reset and normalize styles"""
        return """/* CSS Reset and Normalize */
*, *::before, *::after {
    box-sizing: border-box;
}

* {
    margin: 0;
    padding: 0;
}

html, body {
    height: 100%;
}

body {
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

img, picture, video, canvas, svg {
    display: block;
    max-width: 100%;
    height: auto;
}

input, button, textarea, select {
    font: inherit;
}

p, h1, h2, h3, h4, h5, h6 {
    overflow-wrap: break-word;
}

a {
    text-decoration: none;
    color: inherit;
}

ul, ol {
    list-style: none;
}"""
    

    def _generate_typography_styles(self, branding: BrandingConfig) -> str:
        """Generate typography styles"""
        return f"""/* Typography */
h1, h2, h3, h4, h5, h6 {{
    font-family: {branding.font_family};
    font-weight: 700;
    line-height: 1.2;
    color: var(--gray-900);
    margin-bottom: var(--spacing-md);
}}

h1 {{
    font-size: var(--font-size-3xl);
    color: var(--h1-text-color);
}}

h2 {{
    font-size: var(--font-size-2xl);
    color: var(--h2-text-color);
}}

h3 {{
    font-size: var(--font-size-xl);
    color: var(--h3-text-color);
}}

h4 {{
    font-size: var(--font-size-lg);
}}

h5, h6 {{
    font-size: var(--font-size-base);
}}

p {{
    margin-bottom: var(--spacing-md);
    line-height: 1.7;
}}

.lead {{
    font-size: var(--font-size-lg);
    font-weight: 300;
    color: var(--gray-600);
}}

.text-sm {{
    font-size: var(--font-size-sm);
}}

.text-lg {{
    font-size: var(--font-size-lg);
}}

.text-center {{
    text-align: center;
}}

"""

    def _generate_color_scheme_styles(self, branding: BrandingConfig) -> str:
        """Generate color scheme styles based on branding"""
        return """/* Color Scheme */
body {
    background-color: var(--body-bg-color);
    color: var(--body-text-color);
}

/* Header with gradient from header-bg-color-1 to header-bg-color-2 */
header, .header, .navbar {
    background: linear-gradient(135deg, var(--header-bg-color-1), var(--header-bg-color-2));
    color: white;
}

/* Footer with new footer colors */
footer, .footer {
    background-color: var(--footer-bg-color);
    color: var(--footer-text-color);
}

/* Footer links inherit footer text color */
footer a, .footer a {
    color: var(--footer-text-color);
    opacity: 0.8;
    text-decoration: none;
}

footer a:hover, .footer a:hover {
    opacity: 1;
    text-decoration: underline;
}

.button-primary {
    background-color: var(--primary-color);
    color: var(--white);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    border: none;
    padding: var(--spacing-sm) var(--spacing-lg);
    font-weight: 600;
    transition: background 0.2s;
}

.button-primary:hover, .button-primary:focus {
    background-color: var(--primary-dark);
}

.button-secondary {
    background-color: var(--secondary-color);
    color: var(--white);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    border: none;
    padding: var(--spacing-sm) var(--spacing-lg);
    font-weight: 600;
    transition: background 0.2s;
}

.button-secondary:hover, .button-secondary:focus {
    background-color: var(--secondary-dark);
}

.alert-success {
    background-color: var(--success);
    color: var(--white);
}

.alert-warning {
    background-color: var(--warning);
    color: var(--white);
}

.alert-error {
    background-color: var(--error);
    color: var(--white);
}

.alert-info {
    background-color: var(--info);
    color: var(--white);
}
"""

    def _generate_layout_styles(self) -> str:
        """Generate layout and grid styles"""
        return """/* Layout Styles */
.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

.grid {
    display: grid;
    gap: var(--spacing-lg);
}

.grid-2 { grid-template-columns: repeat(2, 1fr); }
.grid-3 { grid-template-columns: repeat(3, 1fr); }
.grid-4 { grid-template-columns: repeat(4, 1fr); }

.flex {
    display: flex;
    gap: var(--spacing-md);
}

.flex-center { justify-content: center; align-items: center; }
.flex-between { justify-content: space-between; align-items: center; }
"""

    def _generate_component_styles(self, branding: BrandingConfig) -> str:
        """Generate component-specific styles"""
        return """/* Component Styles */

/* Header Styles */
header {
    background: var(--primary-color);
    color: white;
    padding: var(--spacing-lg) 0;
}

.header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo-container {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.logo-image {
    height: 60px;
    width: auto;
}

.company-name {
    font-size: var(--font-size-xl);
    font-weight: bold;
}

/* Navigation Styles */
nav ul {
    display: flex;
    list-style: none;
    margin: 0;
    padding: 0;
    gap: var(--spacing-lg);
}

nav a {
    color: var(--menu-text-color);
    text-decoration: none;
    font-weight: 500;
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--border-radius);
    transition: background-color 0.2s;
}

nav a:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

/* Modern Dropdown Navigation Styles */
.has-dropdown {
    position: relative;
}

.dropdown {
    display: none;
    position: absolute;
    top: 100%;
    left: 0;
    background-color: white;
    min-width: 200px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 1000;
    border-radius: 0 0 6px 6px;
    padding: 8px 0;
    list-style: none;
    margin: 0;
}

.dropdown li {
    margin: 0;
}

.dropdown a {
    display: block;
    padding: 10px 16px;
    color: #333;
    text-decoration: none;
    font-size: 0.9rem;
    transition: background-color 0.3s ease;
    border: none;
    white-space: nowrap;
}

.dropdown a:hover {
    background-color: #f8f9fa;
}

.dropdown a.current-location {
    background-color: #fff3cd;
    color: #856404;
    font-weight: 600;
}

.dropdown a.current-location:hover {
    background-color: #ffeaa7;
}

/* Grid Layout for Dropdowns with 4+ Items */
.dropdown.grid-layout {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    max-width: 720px; /* 4 columns max */
    min-width: 400px;
    gap: 0;
    padding: 0;
}

.dropdown.grid-layout li {
    margin: 0;
}

.dropdown.grid-layout a {
    padding: 8px 12px;
    text-align: center;
    font-size: 0.85rem;
    border: 1px solid #dee2e6;
    background-color: #fff3cd;
    color: #856404;
    margin: 0;
}

.dropdown.grid-layout a:hover {
    background-color: #ffeaa7;
}

.dropdown.grid-layout a.current-location {
    background-color: #f8d7da;
    color: #721c24;
}

/* Show dropdown on hover */
.has-dropdown:hover .dropdown {
    display: flex;
}

.has-dropdown:hover .dropdown.grid-layout {
    display: grid;
}

/* Legacy dropdown support for backward compatibility */
.dropdown-content {
    display: none;
    position: absolute;
    background-color: white;
    min-width: 200px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    border-radius: 0 0 6px 6px;
    z-index: 1000;
    top: 100%;
    left: 0;
    padding: 8px 0;
    margin: 0;
}

.dropdown-content a {
    color: #333;
    padding: 10px 16px;
    display: block;
    border: none;
    white-space: nowrap;
    font-size: 0.9rem;
    transition: background-color 0.3s ease;
    text-decoration: none;
}

.dropdown-content a:hover {
    background-color: #f8f9fa;
}

/* Hero Section */
.hero {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    background-image: var(--hero-bg-image);
    background-size: cover;
    background-position: center;
    background-blend-mode: overlay;
    color: white;
    padding: var(--spacing-3xl) 0;
    text-align: center;
}

.hero-content {
    max-width: 800px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

.hero h1 {
    font-size: var(--font-size-3xl);
    margin-bottom: var(--spacing-lg);
    font-weight: bold;
}

.hero-subtitle {
    font-size: var(--font-size-lg);
    margin-bottom: var(--spacing-xl);
    opacity: 0.9;
}

.cta-button {
    display: inline-block;
    background: white;
    color: var(--primary-color);
    padding: var(--spacing-md) var(--spacing-xl);
    border-radius: var(--border-radius);
    text-decoration: none;
    font-weight: bold;
    transition: transform 0.2s;
}

.cta-button:hover {
    transform: translateY(-2px);
}

/* Footer Styles */
footer {
    background: var(--gray-800);
    color: white;
    padding: var(--spacing-xl) 0;
    margin-top: auto;
}

.footer-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

.footer-content {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
    text-align: center;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

.footer-column {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}

.footer-column h3,
.footer-column h4 {
    margin-bottom: var(--spacing-md);
    color: var(--footer-text-color);
}

.footer-column ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.footer-column ul li {
    margin-bottom: var(--spacing-sm);
}

.footer-section h3 {
    margin-bottom: var(--spacing-md);
    color: var(--secondary-color);
}

.footer-section a {
    color: white;
    text-decoration: none;
    display: block;
    margin-bottom: var(--spacing-sm);
}

.footer-section a:hover {
    color: var(--secondary-color);
}

.social-links {
    display: flex;
    gap: var(--spacing-md);
}

.social-links a {
    display: inline-block !important;
    background: var(--primary-color);
    width: 40px;
    height: 40px;
    border-radius: 50%;
    text-align: center;
    line-height: 40px;
    margin-bottom: 0 !important;
}

.map-container {
    border-radius: var(--border-radius);
    overflow: hidden;
}

.map-container iframe {
    width: 100%;
    height: 300px;
    border: 0;
}

.footer-bottom {
    border-top: 1px solid var(--gray-600);
    padding-top: var(--spacing-lg);
    text-align: center;
}

/* Content Sections */
.content-section {
    padding: var(--spacing-xl) 0;
}

.content-section .container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

.content-section h2 {
    color: var(--primary-color);
    margin-bottom: var(--spacing-lg);
}

.why-choose-item {
    margin-bottom: var(--spacing-lg);
}

.why-choose-item h3 {
    color: var(--secondary-color);
    margin-bottom: var(--spacing-sm);
}

/* Legacy component styles for compatibility */
.card {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: var(--spacing-lg);
    border: 1px solid var(--gray-200);
}

/* Product Page Styles */
.product-detail {
    max-width: 1200px;
    margin: 0 auto;
    padding: var(--spacing-lg);
}

.breadcrumb {
    margin-bottom: var(--spacing-lg);
    color: var(--gray-600);
    font-size: var(--font-size-sm);
}

.breadcrumb a {
    color: var(--primary-color);
    text-decoration: none;
}

.breadcrumb a:hover {
    text-decoration: underline;
}

.product-hero {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-xl);
    margin-bottom: var(--spacing-xl);
}

.product-image {
    text-align: center;
}

.main-product-image {
    max-width: 100%;
    height: auto;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
}

.placeholder-image {
    background-color: var(--gray-100);
    border: 2px dashed var(--gray-300);
    border-radius: var(--border-radius);
    padding: var(--spacing-xl);
    text-align: center;
    color: var(--gray-600);
    font-size: var(--font-size-lg);
    min-height: 300px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.product-info h1 {
    color: var(--primary-color);
    margin-bottom: var(--spacing-md);
}

.product-category {
    color: var(--secondary-color);
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
}

.product-price {
    font-size: var(--font-size-lg);
    font-weight: bold;
    color: var(--primary-color);
    margin-bottom: var(--spacing-md);
}

.product-description {
    margin-bottom: var(--spacing-lg);
    line-height: 1.6;
}

.product-actions {
    display: flex;
    gap: var(--spacing-md);
}

.btn {
    display: inline-block;
    padding: var(--spacing-md) var(--spacing-lg);
    border-radius: var(--border-radius);
    text-decoration: none;
    font-weight: 600;
    text-align: center;
    transition: all 0.3s ease;
    border: none;
    cursor: pointer;
}

.btn-primary {
    background-color: var(--primary-color);
    color: white;
}

.btn-primary:hover {
    background-color: var(--primary-dark);
    transform: translateY(-1px);
}

.btn-secondary {
    background-color: var(--secondary-color);
    color: white;
}

.btn-secondary:hover {
    background-color: var(--secondary-dark);
    transform: translateY(-1px);
}

.btn-sm {
    padding: var(--spacing-sm) var(--spacing-md);
    font-size: var(--font-size-sm);
}

.product-details-section {
    margin: var(--spacing-xl) 0;
    padding: var(--spacing-lg);
    background-color: var(--gray-50);
    border-radius: var(--border-radius);
}

.product-details-section h2 {
    color: var(--primary-color);
    margin-bottom: var(--spacing-lg);
}

.specifications, .features {
    margin-bottom: var(--spacing-lg);
}

.specifications h3, .features h3 {
    color: var(--secondary-color);
    margin-bottom: var(--spacing-md);
}

.specifications ul, .features ul {
    list-style-type: disc;
    padding-left: var(--spacing-lg);
}

.specifications li, .features li {
    margin-bottom: var(--spacing-sm);
}

.products-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-top: var(--spacing-lg);
}

.product-card {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    padding: var(--spacing-lg);
    text-align: center;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.product-card img {
    max-width: 100%;
    height: 200px;
    object-fit: cover;
    border-radius: var(--border-radius);
    margin-bottom: var(--spacing-md);
}

.product-card h3 {
    color: var(--primary-color);
    margin-bottom: var(--spacing-md);
}

.product-card .product-link {
    color: var(--secondary-color);
    text-decoration: none;
    font-weight: 600;
    display: inline-block;
    margin-top: var(--spacing-md);
}

.product-card .product-link:hover {
    color: var(--secondary-dark);
    text-decoration: underline;
}

.product-card-content {
    padding: var(--spacing-md);
}

.related-products {
    margin: var(--spacing-xl) 0;
}

.related-products h2 {
    color: var(--primary-color);
    margin-bottom: var(--spacing-lg);
}

.contact-cta {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: var(--spacing-xl);
    border-radius: var(--border-radius);
    text-align: center;
    margin-top: var(--spacing-xl);
}

.contact-cta h2 {
    color: white;
    margin-bottom: var(--spacing-md);
}

.contact-cta p {
    margin-bottom: var(--spacing-lg);
    opacity: 0.9;
}

.contact-cta .btn-primary {
    background-color: white;
    color: var(--primary-color);
}

.contact-cta .btn-primary:hover {
    background-color: var(--gray-100);
    transform: translateY(-2px);
}

/* Product Page Responsive Design */
@media (max-width: 768px) {
    .product-hero {
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
    }

    .product-actions {
        flex-direction: column;
    }

    .products-grid {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: var(--spacing-md);
    }

    .product-detail {
        padding: var(--spacing-md);
    }
}

@media (max-width: 480px) {
    .product-card {
        padding: var(--spacing-md);
    }

    .product-card img {
        height: 150px;
    }

    .contact-cta {
        padding: var(--spacing-lg);
    }
}

/* Privacy Policy Page Styles */
.privacy-policy-content {
    max-width: 800px;
    margin: var(--spacing-xl) auto;
    padding: var(--spacing-xl);
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    line-height: 1.7;
}

.privacy-policy-content h1 {
    color: var(--primary-color);
    text-align: center;
    margin-bottom: var(--spacing-md);
    font-size: 2.5rem;
    border-bottom: 3px solid var(--primary-color);
    padding-bottom: var(--spacing-md);
}

.privacy-policy-content .last-updated {
    text-align: center;
    color: var(--gray-600);
    font-style: italic;
    margin-bottom: var(--spacing-xl);
    padding-bottom: var(--spacing-lg);
    border-bottom: 1px solid var(--gray-200);
}

.privacy-policy-content h2 {
    color: var(--secondary-color);
    margin-top: var(--spacing-xl);
    margin-bottom: var(--spacing-lg);
    font-size: 1.5rem;
    padding-left: var(--spacing-sm);
    border-left: 4px solid var(--secondary-color);
}

.privacy-policy-content p {
    margin-bottom: var(--spacing-lg);
    color: var(--gray-700);
    text-align: justify;
}

.privacy-policy-content ul {
    margin: var(--spacing-lg) 0;
    padding-left: var(--spacing-xl);
}

.privacy-policy-content li {
    margin-bottom: var(--spacing-md);
    color: var(--gray-700);
    position: relative;
}

.privacy-policy-content li::marker {
    color: var(--primary-color);
    font-weight: bold;
}

.privacy-policy-content .contact-info {
    background-color: var(--gray-50);
    padding: var(--spacing-lg);
    border-radius: var(--border-radius);
    border: 1px solid var(--gray-200);
    margin-top: var(--spacing-lg);
}

.privacy-policy-content .contact-info p {
    margin-bottom: var(--spacing-sm);
    text-align: left;
}

.privacy-policy-content .contact-info strong {
    color: var(--primary-color);
    font-weight: 600;
}

/* Privacy Policy Responsive Design */
@media (max-width: 768px) {
    .privacy-policy-content {
        margin: var(--spacing-lg) auto;
        padding: var(--spacing-lg);
    }

    .privacy-policy-content h1 {
        font-size: 2rem;
    }

    .privacy-policy-content h2 {
        font-size: 1.25rem;
        margin-top: var(--spacing-lg);
    }

    .privacy-policy-content ul {
        padding-left: var(--spacing-lg);
    }
}

@media (max-width: 480px) {
    .privacy-policy-content {
        margin: var(--spacing-md) auto;
        padding: var(--spacing-md);
    }

    .privacy-policy-content h1 {
        font-size: 1.75rem;
    }

    .privacy-policy-content p {
        text-align: left;
    }

    .privacy-policy-content .contact-info {
        padding: var(--spacing-md);
    }
}

/* Services Page Styles */
.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: var(--spacing-xl);
    margin-top: var(--spacing-lg);
}

.service-card {
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    overflow: hidden;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.service-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
}

.service-image {
    width: 100%;
    height: 250px;
    object-fit: cover;
}

.service-card-content {
    padding: var(--spacing-lg);
}

.service-card h3 {
    color: var(--primary-color);
    margin-bottom: var(--spacing-md);
    font-size: 1.5rem;
}

.service-description {
    margin-bottom: var(--spacing-lg);
    line-height: 1.6;
    color: var(--gray-700);
}

.service-features {
    margin-bottom: var(--spacing-lg);
    padding: var(--spacing-md);
    background-color: var(--gray-50);
    border-radius: var(--border-radius);
}

.service-features h4 {
    color: var(--secondary-color);
    margin-bottom: var(--spacing-sm);
    font-size: 1rem;
}

.service-features ul {
    margin: 0;
    padding-left: var(--spacing-lg);
}

.service-features li {
    margin-bottom: var(--spacing-xs);
    color: var(--gray-700);
}

.service-actions {
    display: flex;
    gap: var(--spacing-md);
}

.process-steps {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-top: var(--spacing-lg);
}

.process-step {
    text-align: center;
    padding: var(--spacing-lg);
    background: white;
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    position: relative;
}

.step-number {
    width: 60px;
    height: 60px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    font-weight: bold;
    margin: 0 auto var(--spacing-md);
}

.process-step h3 {
    color: var(--primary-color);
    margin-bottom: var(--spacing-sm);
}

.process-step p {
    color: var(--gray-700);
    line-height: 1.6;
}

.service-benefits {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: var(--spacing-lg);
    margin-top: var(--spacing-lg);
}

.benefit-item {
    text-align: center;
    padding: var(--spacing-lg);
}

.benefit-item h3 {
    color: var(--secondary-color);
    margin-bottom: var(--spacing-md);
}

.benefit-item p {
    color: var(--gray-700);
    line-height: 1.6;
}

.services-cta {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    color: white;
    padding: var(--spacing-xl);
    border-radius: var(--border-radius);
    text-align: center;
    margin-top: var(--spacing-xl);
}

.services-cta h2 {
    color: white;
    margin-bottom: var(--spacing-md);
}

.services-cta p {
    margin-bottom: var(--spacing-lg);
    opacity: 0.9;
    font-size: 1.1rem;
}

.cta-actions {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
}

.services-cta .btn {
    background-color: white;
    color: var(--primary-color);
    border: 2px solid white;
}

.services-cta .btn:hover {
    background-color: transparent;
    color: white;
    transform: translateY(-2px);
}

.services-cta .btn-secondary {
    background-color: transparent;
    color: white;
    border: 2px solid white;
}

.services-cta .btn-secondary:hover {
    background-color: white;
    color: var(--primary-color);
}

/* Services Page Responsive Design */
@media (max-width: 768px) {
    .services-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
    }

    .service-actions {
        flex-direction: column;
    }

    .process-steps {
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
    }

    .service-benefits {
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
    }

    .cta-actions {
        flex-direction: column;
        align-items: center;
    }

    .services-cta .btn {
        width: 200px;
    }
}

@media (max-width: 480px) {
    .services-grid {
        grid-template-columns: 1fr;
        gap: var(--spacing-md);
    }

    .service-card-content {
        padding: var(--spacing-md);
    }

    .service-image {
        height: 200px;
    }

    .process-step, .benefit-item {
        padding: var(--spacing-md);
    }

    .services-cta {
        padding: var(--spacing-lg);
    }

    .step-number {
        width: 50px;
        height: 50px;
        font-size: 1.25rem;
    }
}

/* Places of Interest Link Styling */
.poi-link-container {
    height: 200px;
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    border-radius: var(--border-radius);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: var(--spacing-md);
}

.poi-map-link {
    color: white;
    text-decoration: none;
    font-weight: 600;
    padding: var(--spacing-lg);
    text-align: center;
    transition: transform 0.3s ease;
    display: block;
}

.poi-map-link:hover {
    transform: scale(1.05);
    text-decoration: underline;
}
"""

    def _generate_responsive_styles(self) -> str:
        """Generate responsive design styles"""
        return """/* Responsive Styles */
@media (max-width: 768px) {
    .container {
        padding: 0 var(--spacing-md);
    }
    
    .grid-2, .grid-3, .grid-4 {
        grid-template-columns: 1fr;
    }
    
    .flex {
        flex-direction: column;
    }
    
    /* Header responsive */
    .header-content {
        flex-direction: column;
        gap: var(--spacing-md);
        text-align: center;
    }
    
    nav ul {
        flex-direction: column;
        gap: var(--spacing-sm);
        width: 100%;
    }
    
    /* Hero responsive */
    .hero h1 {
        font-size: 2rem;
    }
    
    .hero-subtitle {
        font-size: var(--font-size-base);
    }
    
    /* Footer responsive */
    .footer-content {
        grid-template-columns: 1fr;
        gap: var(--spacing-lg);
        text-align: center;
    }
    
    .social-links {
        justify-content: center;
    }
    
    h1 { font-size: 2rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.25rem; }
    
    /* Mobile responsive navigation */
    .dropdown {{
        position: static;
        display: none;  /* Keep hidden by default */
        flex-direction: column;
        box-shadow: none;
        background-color: rgba(255, 255, 255, 0.1);
        margin-top: 0;
        border-radius: 0;
        min-width: auto;
    }}

    .dropdown.grid-layout {{
        display: none;  /* Keep hidden by default */
        flex-direction: column;
        grid-template-columns: none;
        min-width: auto;
        max-width: none;
    }}

    .dropdown.grid-layout a {{
        text-align: left;
        border: none;
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }}

    .dropdown.grid-layout a:hover,
    .dropdown a:hover {{
        background-color: rgba(255, 255, 255, 0.2);
    }}

    /* Show dropdowns on hover, using flex for proper layout */
    .has-dropdown:hover .dropdown {{
        display: flex;
    }}

    .has-dropdown:hover .dropdown.grid-layout {{
        display: flex;
    }}
}

@media (max-width: 480px) {
    .container {
        padding: 0 var(--spacing-sm);
    }
    
    .logo-image {
        height: 40px;
    }
    
    .company-name {
        font-size: var(--font-size-lg);
    }
    
    .hero h1 {
        font-size: 1.75rem;
    }
    
    .cta-button {
        padding: var(--spacing-sm) var(--spacing-lg);
    }
    
    h1 { font-size: 1.75rem; }
    h2 { font-size: 1.25rem; }
}
"""

    def _generate_utility_styles(self, branding: BrandingConfig) -> str:
        """Generate utility classes"""
        return """/* Utility Classes */
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

.mt-sm { margin-top: var(--spacing-sm); }
.mt-md { margin-top: var(--spacing-md); }
.mt-lg { margin-top: var(--spacing-lg); }
.mt-xl { margin-top: var(--spacing-xl); }

.mb-sm { margin-bottom: var(--spacing-sm); }
.mb-md { margin-bottom: var(--spacing-md); }
.mb-lg { margin-bottom: var(--spacing-lg); }
.mb-xl { margin-bottom: var(--spacing-xl); }

.p-sm { padding: var(--spacing-sm); }
.p-md { padding: var(--spacing-md); }
.p-lg { padding: var(--spacing-lg); }
.p-xl { padding: var(--spacing-xl); }

.hidden { display: none; }
.block { display: block; }
.inline { display: inline; }
.inline-block { display: inline-block; }

.w-full { width: 100%; }
.h-full { height: 100%; }

.rounded { border-radius: var(--border-radius); }
.shadow { box-shadow: var(--box-shadow); }
"""