# Template System Implementation Guide

## Overview

The Cloud Stack Generator now features a comprehensive template system that allows users to choose from multiple website templates, preview them, and easily create new custom templates.

## Template System Components

### 1. Template Manager (`src/core/templates/template_manager.py`)
- Discovers and loads templates automatically
- Validates template data requirements
- Manages template metadata and compatibility

### 2. Template Preview System (`src/core/templates/template_preview.py`)
- Generates live previews with sample data
- Creates thumbnail images
- Supports template comparison views

### 3. Template Selection UI (`src/ui/dialogs/template_selection_dialog.py`)
- User-friendly template browser
- Preview generation and browser opening
- Template information display

### 4. Enhanced City Page Generator (`src/core/generators/enhanced_city_page_generator.py`)
- Uses template system for generation
- Supports template switching
- Validates data against template requirements

## Available Templates

### 1. **SEO Authority City Page** (Default)
- **ID**: `seo_authority_city`
- **Variant**: `seo_authority`
- **Features**: Advanced SEO, schema markup, Wikipedia integration, Google Maps
- **Best for**: Maximum search engine visibility and comprehensive content

### 2. **Enhanced Business City Page** (New)
- **ID**: `enhanced_business_city`
- **Variant**: `enhanced`
- **Features**: Professional business layout, service showcase, contact sections
- **Best for**: Service-based businesses wanting professional presence

### 3. **Basic City Page** (New)
- **ID**: `basic_city`
- **Variant**: `basic`
- **Features**: Clean, simple design with essential features
- **Best for**: Straightforward local business websites

### 4. **Simple Landing Page** (New)
- **ID**: `simple_landing`
- **Type**: `landing_page`
- **Features**: Conversion-focused, single-page design
- **Best for**: Lead generation and business promotion

## Template File Structure

Each template consists of two files:

### HTML Template File (`.html`)
- Location: `src/templates/pages/`
- Uses Jinja2 templating syntax
- Includes responsive CSS and JavaScript
- Follows semantic HTML5 structure

### Metadata File (`.template.json`)
- Location: `src/templates/`
- Contains template information and requirements
- Defines compatibility and features
- Specifies required and optional data fields

## How to Use Templates

### For Users:
1. Open the application
2. Go to the **Branding & Style** tab
3. Click **"Choose Template..."**
4. Browse available templates
5. Click **"Preview"** to see how templates look
6. Select desired template and click **"Use Selected Template"**

### For Developers:
1. Create HTML template file in `src/templates/pages/`
2. Create corresponding `.template.json` metadata file
3. Template system automatically discovers new templates
4. Templates appear in selection dialog immediately

## Template Specifications

### Required JSON Metadata Fields:
```json
{
  "id": "unique_template_id",
  "name": "Human Readable Name",
  "description": "Detailed description",
  "type": "city_page|landing_page|product_page|service_page|contact_page",
  "variant": "basic|enhanced|seo_authority|custom",
  "version": "1.0.0",
  "author": "Author Name",
  "created_date": "YYYY-MM-DD",
  "last_modified": "YYYY-MM-DD",
  "template_file": "pages/template_name.html",
  "required_data": ["list", "of", "required", "fields"],
  "optional_data": ["list", "of", "optional", "fields"],
  "features": ["list", "of", "template", "features"],
  "compatibility": {
    "min_version": "2.0.0",
    "supports_city_pages": true,
    "supports_responsive_design": true
  }
}
```

### Available Data Context in Templates:

#### Core Objects:
- `city_page` - City-specific content and settings
- `business` - Business information and branding
- `contact` - Contact details and address
- `branding` - Colors, fonts, and visual styling
- `services` - Array of business services
- `products` - Array of business products

#### Helper Variables:
- `page_url` - Full page URL
- `current_year` - Current year
- `timestamp` - Generation timestamp

### Template Best Practices:

1. **Responsive Design**: Use mobile-first CSS with proper breakpoints
2. **Performance**: Inline CSS, minimal JavaScript, optimized images
3. **SEO**: Proper meta tags, semantic HTML, structured data
4. **Accessibility**: ARIA labels, keyboard navigation, high contrast
5. **Error Handling**: Use Jinja2 conditionals for missing data

## Testing Templates

### Template Discovery Test:
```python
from core.templates.template_manager import TemplateManager
tm = TemplateManager()
templates = tm.get_available_templates()
print(f"Found {len(templates)} templates")
```

### Template Preview Test:
```python
from core.templates.template_preview import TemplatePreviewGenerator
preview_gen = TemplatePreviewGenerator(tm)
html = preview_gen.generate_preview_html("template_id")
```

### Template Validation Test:
```python
is_valid, errors = tm.validate_template_data("template_id", sample_data)
```

## Sample Template Creation

To create a new template:

1. **Create HTML file** (`src/templates/pages/my_template.html`):
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <title>{{ city_page.title }} | {{ business.business_name }}</title>
    <!-- Add responsive meta tags, CSS, etc. -->
</head>
<body>
    <!-- Template content using Jinja2 syntax -->
    <h1>{{ business.business_name }}</h1>
    <p>{{ city_page.about_city }}</p>
</body>
</html>
```

2. **Create metadata file** (`src/templates/my_template.template.json`):
```json
{
  "id": "my_template",
  "name": "My Custom Template",
  "description": "Description of template features",
  "type": "city_page",
  "variant": "custom",
  "version": "1.0.0",
  "author": "Your Name",
  "created_date": "2025-09-18",
  "last_modified": "2025-09-18",
  "template_file": "pages/my_template.html",
  "required_data": ["business.business_name"],
  "optional_data": ["city_page.about_city"],
  "features": ["Custom feature 1", "Custom feature 2"],
  "compatibility": {
    "min_version": "2.1.0",
    "supports_city_pages": true
  }
}
```

3. **Template automatically appears** in the template selection dialog.

## Template Import/Export (Future)

The system includes infrastructure for:
- Exporting templates as ZIP packages
- Importing custom templates
- Template collections and sharing
- Version management and updates

## Troubleshooting

### Common Issues:

1. **Template not appearing**: Check JSON syntax and file naming
2. **Preview fails**: Verify required data fields are available
3. **Rendering errors**: Check Jinja2 syntax and variable names
4. **Import failures**: Ensure proper file structure and metadata

### Debug Commands:
```python
# Check template discovery
tm = TemplateManager()
print(tm.templates_registry.keys())

# Validate template
is_valid, errors = tm.validate_template_data(template_id, data)
print(errors)

# Test template loading
template = tm.load_template(template_id)
print(template is not None)
```

## Next Steps

The template system is now fully functional and ready for:
1. User template selection and switching
2. Custom template creation
3. Template preview and comparison
4. Template import/export (when needed)
5. Template marketplace (future enhancement)

This comprehensive template system transforms the single hardcoded template limitation into a flexible, extensible template management platform.