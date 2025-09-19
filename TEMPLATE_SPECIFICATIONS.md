# Template System Specifications

## Overview

The Cloud Stack Generator template system uses HTML templates with Jinja2 templating and JSON metadata files for template configuration. This document outlines the specifications for creating custom templates.

## File Structure

Each template consists of two files:
- `template_name.html` - The Jinja2 HTML template
- `template_name.template.json` - The metadata configuration file

Templates are stored in the `src/templates/pages/` directory with metadata files in `src/templates/`.

## JSON Metadata Specification

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the template (lowercase, no spaces) |
| `name` | string | Human-readable template name |
| `description` | string | Detailed description of the template |
| `type` | string | Template type: `city_page`, `landing_page`, `product_page`, `service_page`, `contact_page` |
| `variant` | string | Template variant: `basic`, `enhanced`, `seo_authority`, `custom` |
| `version` | string | Semantic version (e.g., "1.0.0") |
| `author` | string | Template author/creator |
| `created_date` | string | Creation date (YYYY-MM-DD) |
| `last_modified` | string | Last modification date (YYYY-MM-DD) |
| `template_file` | string | Path to HTML template file relative to templates directory |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `preview_image` | string | Path to preview image |
| `required_data` | array | List of required data fields (dot notation) |
| `optional_data` | array | List of optional data fields |
| `features` | array | List of template features |
| `compatibility` | object | Compatibility requirements and flags |

### Compatibility Object

| Field | Type | Description |
|-------|------|-------------|
| `min_version` | string | Minimum generator version required |
| `supports_city_pages` | boolean | Supports city page generation |
| `supports_wikipedia` | boolean | Supports Wikipedia integration |
| `supports_google_maps` | boolean | Supports Google Maps integration |
| `supports_schema_markup` | boolean | Includes schema.org markup |
| `supports_responsive_design` | boolean | Responsive/mobile-friendly |
| `supports_seo_optimization` | boolean | SEO optimized |

## HTML Template Specification

### Template Engine
- Uses Jinja2 templating syntax
- Supports all Jinja2 features: variables, loops, conditionals, filters, etc.

### Available Data Context

The following data objects are available in all templates:

#### `city_page` Object
```
city_page.city_name          - City name (string)
city_page.state              - State/region (string)
city_page.slug               - URL slug (string)
city_page.title              - Page title (string)
city_page.meta_description   - Meta description (string)
city_page.primary_keyword    - Primary SEO keyword (string)
city_page.secondary_keywords - List of secondary keywords (array)
city_page.hero_title         - Hero section title (string)
city_page.breadcrumbs        - Breadcrumb navigation (array)
city_page.about_city         - About city content (string)
city_page.seo_content_title  - SEO content section title (string)
city_page.seo_content_body   - Main SEO content (string)
city_page.service_area_note  - Service area note (string)
city_page.featured_products  - List of featured products (array)
city_page.city_map_embed     - City map embed code (string)

city_page.city_image.image_url    - City image URL (string)
city_page.city_image.alt_text     - Image alt text (string)
city_page.city_image.caption      - Image caption (string)
city_page.city_image.credit       - Image credit (string)
city_page.city_image.source       - Image source (string)
city_page.city_image.embed_code   - Complete image embed HTML (string)

city_page.places_of_interest      - Array of places
├── name                           - Place name (string)
└── embed_url                      - Google Maps embed URL (string)

city_page.city_faq                 - Array of FAQ items
├── question                       - FAQ question (string)
└── answer                         - FAQ answer (string)
```

#### `business` Object
```
business.business_name       - Business name (string)
business.industry           - Industry/type (string)
business.description        - Business description (string)
business.website_url        - Website URL (string)
business.hours              - Business hours (string)
```

#### `contact` Object
```
contact.phone               - Phone number (string)
contact.email               - Email address (string)

contact.address.street      - Street address (string)
contact.address.city        - City (string)
contact.address.state       - State (string)
contact.address.zip_code    - ZIP code (string)
contact.address.country     - Country (string)
```

#### `branding` Object
```
branding.primary_color      - Primary brand color (hex string)
branding.secondary_color    - Secondary brand color (hex string)
branding.accent_color       - Accent color (hex string)
branding.logo_url          - Logo image URL (string)
branding.font_family       - Font family name (string)
```

#### `services` Array
```
services[].name            - Service name (string)
services[].description     - Service description (string)
services[].features        - Service features (array)
services[].pricing         - Pricing information (string)
```

#### `products` Array
```
products[].name            - Product name (string)
products[].description     - Product description (string)
products[].price           - Product price (string)
products[].features        - Product features (array)
products[].categories      - Product categories (array)
```

#### Helper Variables
```
page_url                   - Full page URL (string)
current_year              - Current year (integer)
timestamp                  - Generation timestamp (string)
template_info.id          - Template ID used (string)
template_info.generated_at - Generation datetime (string)
template_info.generator_version - Generator version (string)
```

### Template Best Practices

1. **Responsive Design**: Use mobile-first responsive CSS
2. **SEO Optimization**: Include proper meta tags, headings hierarchy
3. **Semantic HTML**: Use semantic HTML5 elements
4. **Accessibility**: Include ARIA labels, alt text, proper focus states
5. **Performance**: Minimize CSS/JS, optimize images
6. **Error Handling**: Use Jinja2 conditionals to handle missing data

### Required HTML Structure

All templates should include:
- DOCTYPE declaration
- HTML5 semantic structure
- Meta viewport tag for mobile
- Title and meta description
- Proper heading hierarchy (H1, H2, H3, etc.)

### CSS Guidelines

- Use inline CSS or embedded `<style>` blocks
- Avoid external CSS dependencies when possible
- Use CSS custom properties for branding colors
- Implement responsive breakpoints
- Follow BEM naming convention for classes

### JavaScript Guidelines

- Minimize JavaScript usage
- Use vanilla JavaScript when possible
- Avoid external dependencies
- Ensure progressive enhancement
- Include error handling

## Template Validation

The system validates templates for:
- Required data fields availability
- Template syntax errors
- Missing template files
- Invalid metadata format
- Compatibility requirements

## Template Testing

Templates can be tested using:
- Template preview system
- Sample data generation
- Validation functions
- Browser compatibility testing

## Template Distribution

Templates can be:
- Packaged as ZIP files with metadata
- Shared as template collections
- Imported/exported through the UI
- Version controlled with Git

## Example File Naming

```
enhanced_business.html           - Template file
enhanced_business.template.json  - Metadata file
```

## Data Field Naming Convention

Use dot notation for nested fields:
- `city_page.city_name`
- `contact.address.street`
- `branding.primary_color`

Required vs Optional:
- **Required**: Must be present for template to render
- **Optional**: Template handles gracefully if missing