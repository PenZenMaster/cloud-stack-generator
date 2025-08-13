# src/core/generators/css_generator.py
"""
CSS Generator - Responsive Styling and Branding
Sprint 2 Week 2 - Days 7-8 Implementation

Generates CSS from branding configuration with responsive design
and professional styling.
"""

from typing import Dict, Any, List
from ..config.models import ClientConfig, BrandingConfig
import colorsys


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
    
    def _generate_css_variables(self, branding: BrandingConfig) -> str:
        """Generate CSS custom properties for consistent theming"""
        # Calculate additional colors based on primary/secondary
        primary_light = self._lighten_color(branding.primary_color, 0.1)
        primary_dark = self._darken_color(branding.primary_color, 0.1)
        secondary_light = self._lighten_color(branding.secondary_color, 0.1)
        secondary_dark = self._darken_color(branding.secondary_color, 0.1)
        
        return f"""/* CSS Custom Properties for Branding */
:root {{
    /* Brand Colors */
    --primary-color: {branding.primary_color};
    --primary-light: {primary_light};
    --primary-dark: {primary_dark};
    --secondary-color: {branding.secondary_color};
    --secondary-light: {secondary_light};
    --secondary-dark: {secondary_dark};
    
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
    color: var(--primary-color);
}}

h2 {{
    font-size: var(--font-size-2xl);
    color: var(--primary-dark);
}}

h3 {{
    font-size: var(--font-size-xl);
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
        return f"""/* Color Scheme */
body {{
    background-color: var(--white);
    color: var(--gray-800);
}}

.header, .navbar {{
    background-color: var(--primary-color);
    color: var(--white);
}}

.footer {{
    background-color: var(--secondary-dark);
    color: var(--white);
}}

.button-primary {{
    background-color: var(--primary-color);
    color: var(--white);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    border: none;
    padding: var(--spacing-sm) var(--spacing-lg);
    font-weight: 600;
    transition: background 0.2s;
}}

.button-primary:hover, .button-primary:focus {{
    background-color: var(--primary-dark);
}}

.button-secondary {{
    background-color: var(--secondary-color);
    color: var(--white);
    border-radius: var(--border-radius);
    box-shadow: var(--box-shadow);
    border: none;
    padding: var(--spacing-sm) var(--spacing-lg);
    font-weight: 600;
    transition: background 0.2s;
}}

.button-secondary:hover, .button-secondary:focus {{
    background-color: var(--secondary-dark);
}}

.alert-success {{
    background-color: var(--success);
    color: var(--white);
}}

.alert-warning {{
    background-color: var(--warning);
    color: var(--white);
}}

.alert-error {{
    background-color: var(--error);
    color: var(--white);
}}

.alert-info {{
    background-color: var(--info);
    color: var(--white);
}}
"""