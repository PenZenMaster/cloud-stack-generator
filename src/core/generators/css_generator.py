# src/core/generators/css_generator.py
"""
CSS Generator - Responsive Styling and Branding
Sprint 2 Week 2 - Days 7-8 Implementation

Generates CSS from branding configuration with responsive design
and professional styling.
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
        except:
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
        except:
            return color

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
        return """/* Color Scheme */
body {
    background-color: var(--white);
    color: var(--gray-800);
}

.header, .navbar {
    background-color: var(--primary-color);
    color: var(--white);
}

.footer {
    background-color: var(--secondary-dark);
    color: var(--white);
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
    color: white;
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
        display: flex;
        flex-direction: column;
        box-shadow: none;
        background-color: rgba(255, 255, 255, 0.1);
        margin-top: 0;
        border-radius: 0;
        min-width: auto;
    }}
    
    .dropdown.grid-layout {{
        display: flex;
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
    
    .has-dropdown:hover .dropdown {{
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