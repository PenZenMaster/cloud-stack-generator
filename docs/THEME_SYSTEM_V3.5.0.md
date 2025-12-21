# Theme System v3.5.0 - Enhanced Branding & Customization

**Version**: 3.5.0
**Release Date**: November 27, 2025
**Status**: Complete
**Author**: Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

---

## Overview

Version 3.5.0 introduces a comprehensive theme customization system that provides fine-grained control over website appearance. This enhancement builds upon the existing branding system with expanded color controls, hero background image support, and improved semantic HTML structure.

### Key Features

1. **Independent Heading Color Controls** - Separate color customization for H1, H2, H3 elements
2. **Main Menu Text Color** - Custom navigation text color
3. **Hero Background Images** - Upload custom hero section backgrounds with gradient overlay
4. **Enhanced UI** - Two-column layout for better UX
5. **Improved HTML Semantics** - Better heading hierarchy in templates
6. **Full Test Coverage** - 18 comprehensive unit tests

---

## What's New in v3.5.0

### 1. Independent Heading Text Colors

Previously, heading colors were tied to primary/secondary brand colors. Now you have independent control:

**New Color Fields:**
- **H1 Text Color** - Main page headings (default: #2c3e50)
- **H2 Text Color** - Section headings (default: #34495e)
- **H3 Text Color** - Subsection headings (default: #34495e)
- **Main Menu Text Color** - Navigation text (default: #ffffff)

**Benefits:**
- Create distinct visual hierarchy
- Improve readability and accessibility
- Fine-tune brand consistency across elements
- Separate content colors from brand accent colors

### 2. Hero Background Image Support

Upload custom background images for hero sections:

**Features:**
- URL-based image upload
- Automatic gradient overlay blending
- Background size/position optimization
- Fallback to gradient if no image provided

**CSS Implementation:**
```css
.hero {
    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
    background-image: var(--hero-bg-image);
    background-size: cover;
    background-position: center;
    background-blend-mode: overlay;
}
```

### 3. Enhanced Branding Tab UI

**Two-Column Layout:**
- Left column: Color pickers with live preview
- Right column: Typography and logo settings
- Visual color preview squares
- Organized by function (colors, typography, logo)

**Improved UX:**
- Consistent button styling
- Clear field labels
- Live color preview updates
- Validation feedback

### 4. Better HTML Semantics

Updated city page templates for proper heading hierarchy:

**Changes:**
- Section titles: `<h3>` → `<h2>` (proper semantic structure)
- Added dedicated CSS for h2/h3 in content sections
- Better SEO and accessibility
- Screen reader improvements

---

## Technical Architecture

### Configuration Data Model

**BrandingConfig** (models.py v1.01):
```python
@dataclass
class BrandingConfig:
    # Existing colors
    primary_color: str = "#007bff"
    secondary_color: str = "#6c757d"
    body_background_color: str = "#ffffff"
    body_text_color: str = "#333333"
    footer_background_color: str = "#2c3e50"
    footer_text_color: str = "#ffffff"

    # NEW: Heading text colors
    h1_text_color: str = "#2c3e50"
    h2_text_color: str = "#34495e"
    h3_text_color: str = "#34495e"
    main_menu_text_color: str = "#ffffff"

    # Typography & Logo
    font_family: str = "Arial, sans-serif"
    logo_url: str = ""

    # NEW: Hero background
    hero_background_image_url: str = ""
```

### CSS Variable System

**CSS Generator** (css_generator.py v1.01):
```css
:root {
    /* Brand Colors */
    --primary-color: #007bff;
    --secondary-color: #6c757d;

    /* Body & Footer */
    --body-bg-color: #ffffff;
    --body-text-color: #333333;
    --footer-bg-color: #2c3e50;
    --footer-text-color: #ffffff;

    /* NEW: Heading Text Colors */
    --h1-text-color: #2c3e50;
    --h2-text-color: #34495e;
    --h3-text-color: #34495e;

    /* NEW: Navigation Colors */
    --menu-text-color: #ffffff;

    /* NEW: Hero Background */
    --hero-bg-image: url('...');
}
```

### Data Flow

**Config YAML → Parser → Models → CSS Generator → Templates**

1. User configures branding in UI or YAML
2. ConfigParser reads and validates branding data
3. BrandingConfig dataclass stores typed configuration
4. CSSGenerator creates CSS variables
5. Templates use CSS variables for styling

---

## User Guide

### How to Use the New Theme System

#### 1. Configure Heading Colors

**In the UI:**
1. Open the **Branding & Style** tab
2. Scroll to **Text Colors** section
3. Click color picker buttons for:
   - H1 Text Color
   - H2 Text Color
   - H3 Text Color
   - Menu Text Color
4. Preview updates live in the color square

**In YAML:**
```yaml
branding:
  h1_text_color: "#C41E3A"      # Industrial red for main headings
  h2_text_color: "#2C3E50"      # Dark blue-gray for sections
  h3_text_color: "#2C3E50"      # Match H2 for consistency
  main_menu_text_color: "#ffffff"  # White navigation text
```

#### 2. Add Hero Background Image

**In the UI:**
1. Open the **Branding & Style** tab
2. Find **Hero Background Image URL** field
3. Enter image URL (https://example.com/hero-bg.jpg)
4. Image will blend with gradient overlay

**In YAML:**
```yaml
branding:
  hero_background_image_url: "https://example.com/images/hero-background.jpg"
```

**Image Requirements:**
- Format: JPG, PNG, WebP
- Size: 1920x1080 recommended (16:9 ratio)
- Hosting: Must be publicly accessible URL
- Optimization: Compress for web (< 500KB recommended)

#### 3. Example Configuration: Salvo Metal Works

```yaml
branding:
  # Brand Colors
  primary_color: "#C41E3A"        # Industrial red
  secondary_color: "#2C3E50"      # Dark blue-gray

  # Body & Footer
  body_background_color: "#ffffff"
  body_text_color: "#333333"
  footer_background_color: "#2c3e50"
  footer_text_color: "#ffffff"

  # Heading Text Colors
  h1_text_color: "#C41E3A"        # Match primary for emphasis
  h2_text_color: "#2C3E50"        # Match secondary for hierarchy
  h3_text_color: "#2C3E50"        # Consistent with H2
  main_menu_text_color: "#ffffff" # White for contrast

  # Typography
  font_family: "Arial, sans-serif"

  # Logo & Hero
  logo_url: "https://salvometalworks.com/assets/logo.png"
  hero_background_image_url: "https://salvometalworks.com/assets/hero-industrial.jpg"
```

---

## Developer Guide

### Modified Files (v3.5.0)

**Backend Configuration:**
- `src/core/config/models.py` (v1.01) - Added heading color fields
- `src/core/config/parser.py` - Parse/serialize new fields
- `src/core/generators/css_generator.py` (v1.01) - Generate CSS variables

**Templates:**
- `src/templates/pages/seo_authority_city.html` - Improved heading semantics

**UI Components:**
- `src/ui/components/branding_tab.py` (v2.06) - Enhanced UI with new controls
- `src/ui/enhanced_main_window.py` (v3.04) - Styled buttons

**Tests:**
- `tests/unit/test_branding_tab.py` (v2.00) - Complete rewrite for v2.06

### API Changes

**BrandingTab v2.06:**

**New Methods:**
```python
def clear_data(self) -> None:
    """Reset all fields to default values"""

def _emit_config_changed(self) -> None:
    """Override base class to set has_changes flag"""
```

**Updated Data Structure:**
```python
# get_config_data() returns:
{
    "colors": {
        "primary_color": "#007bff",
        "secondary_color": "#6c757d",
        "body_background_color": "#ffffff",
        "body_text_color": "#333333",
        "footer_background_color": "#2c3e50",
        "footer_text_color": "#ffffff",
        "h1_text_color": "#2c3e50",      # NEW
        "h2_text_color": "#34495e",      # NEW
        "h3_text_color": "#34495e",      # NEW
        "main_menu_text_color": "#ffffff" # NEW
    },
    "typography": {
        "font_family": "Arial, sans-serif"
    },
    "logo": {
        "logo_url": "",
        "hero_background_image_url": ""  # NEW
    }
}
```

### Extending the Theme System

**Adding a New Color Field:**

1. **Add to BrandingConfig** (models.py):
```python
@dataclass
class BrandingConfig:
    # ... existing fields ...
    button_text_color: str = "#ffffff"  # NEW

    def __post_init__(self):
        # ... existing validation ...
        self._validate_color(self.button_text_color, "button_text_color")
```

2. **Update ConfigParser** (parser.py):
```python
def _parse_branding_config(self, branding_data: Dict[str, Any]) -> BrandingConfig:
    return BrandingConfig(
        # ... existing fields ...
        button_text_color=branding_data.get("button_text_color", "#ffffff"),
    )
```

3. **Add CSS Variable** (css_generator.py):
```python
# In _generate_css_variables():
button_text = getattr(branding, 'button_text_color', '#ffffff')

return f"""
:root {{
    /* ... existing variables ... */
    --button-text-color: {button_text};
}}
"""
```

4. **Add UI Control** (branding_tab.py):
```python
# In __init__():
self._add_color_picker_with_preview(
    colors_left,
    "Button Text Color:",
    "button_text",
    self.DEFAULT_BUTTON_TEXT
)
```

5. **Update Tests** (test_branding_tab.py):
```python
def test_button_text_color(self):
    """Test button text color field"""
    self.branding_tab.branding_inputs["button_text"].setText("#ff0000")
    config = self.branding_tab.get_config_data()
    self.assertEqual(config["colors"]["button_text_color"], "#ff0000")
```

---

## Testing

### Test Coverage: 18/18 Tests Passing

**Test Suite** (test_branding_tab.py v2.00):

1. **Initialization Tests** - Widget creation, field existence
2. **Default Values** - Verify all defaults set correctly
3. **Required Fields** - Validate required field list
4. **Config Data I/O** - Set/get configuration data
5. **Validation** - Empty fields, invalid colors, warnings
6. **Color Validation** - Hex format validation
7. **Font Selection** - Font family dropdown
8. **Color Tracking** - Internal color state management
9. **Logo URL Validation** - Optional URL field
10. **Color Contrast Warning** - Identical color detection
11. **Clear Data** - Reset to defaults
12. **Config Changed Signal** - Signal emission
13. **Realistic Data** - Real-world configuration test
14. **ValidationResult Class** - Helper class functionality
15. **Web Fonts** - Complete font list verification

**Run Tests:**
```bash
python -m pytest tests/unit/test_branding_tab.py -v
```

**Expected Output:**
```
18 passed in 4.52s
```

---

## Migration Guide

### Upgrading from v3.4.x to v3.5.0

**YAML Configuration:**

No breaking changes! Existing configurations work with defaults:

**Before (v3.4.x):**
```yaml
branding:
  primary_color: "#007bff"
  secondary_color: "#6c757d"
  font_family: "Arial, sans-serif"
  logo_url: "https://example.com/logo.png"
```

**After (v3.5.0) - Optional Enhancements:**
```yaml
branding:
  primary_color: "#007bff"
  secondary_color: "#6c757d"

  # NEW: Optional heading colors (use defaults if omitted)
  h1_text_color: "#2c3e50"
  h2_text_color: "#34495e"
  h3_text_color: "#34495e"
  main_menu_text_color: "#ffffff"

  font_family: "Arial, sans-serif"
  logo_url: "https://example.com/logo.png"

  # NEW: Optional hero background
  hero_background_image_url: "https://example.com/hero.jpg"
```

**UI Changes:**

- Branding tab now has two-column layout
- New color pickers for H1/H2/H3/Menu
- New hero background image field
- All existing functionality preserved

**No Code Changes Required** - Backward compatible!

---

## Performance Impact

**Minimal Performance Impact:**
- +4 CSS variables (negligible browser overhead)
- +1 background image (only if configured)
- No JavaScript changes
- No additional HTTP requests (CSS variables inline)
- Template rendering speed unchanged

**CSS File Size:**
- Added ~200 bytes (4 color variables + hero background)
- Gzip compression reduces impact to ~80 bytes

---

## Accessibility Improvements

**WCAG 2.1 Compliance:**

1. **Better Heading Hierarchy** - Proper h1/h2/h3 structure improves screen reader navigation
2. **Independent Text Colors** - Fine-tune contrast ratios per heading level
3. **Semantic HTML** - Section headings use h2 (not h3) for correct document outline

**Color Contrast:**
- Validation warns if primary/secondary colors identical
- Independent heading colors allow better contrast control
- Default colors meet WCAG AA standards

---

## Troubleshooting

### Common Issues

**Q: Hero background image not showing?**

A: Check:
1. Image URL is publicly accessible (test in browser)
2. URL uses HTTPS (not HTTP)
3. No CORS restrictions on image host
4. Image file format is JPG/PNG/WebP
5. CSS variable is applied (inspect element)

**Q: Heading colors not applying?**

A: Verify:
1. Color format is valid hex (#RRGGBB)
2. CSS has been regenerated after config change
3. Browser cache cleared
4. CSS variables present in generated stylesheet

**Q: Tests failing after customization?**

A: Ensure:
1. All color fields have valid hex values
2. Required fields (primary, secondary, font) not empty
3. URL fields use valid URL format (if provided)
4. Run tests with: `pytest tests/unit/test_branding_tab.py -v`

---

## Roadmap

### Future Enhancements (v3.6.0+)

**Planned Features:**
- [ ] Color scheme presets (Light/Dark/High Contrast)
- [ ] Theme import/export functionality
- [ ] Live preview in UI (iframe preview)
- [ ] Button color customization
- [ ] Link color customization
- [ ] Border/shadow color controls
- [ ] Typography scale settings (font sizes)
- [ ] CSS custom property editor (advanced mode)

**Community Requests:**
- Submit feature requests via GitHub Issues
- Tag with `enhancement` and `theme-system`

---

## Support

**Documentation:**
- This guide: `docs/THEME_SYSTEM_V3.5.0.md`
- Template guide: `docs/TEMPLATE_SYSTEM_GUIDE.md`
- Architecture: `docs/TEMPLATE_SYSTEM_ARCHITECTURE.md`

**Code References:**
- BrandingTab: `src/ui/components/branding_tab.py:1`
- BrandingConfig: `src/core/config/models.py:276`
- CSS Generator: `src/core/generators/css_generator.py:1`
- Tests: `tests/unit/test_branding_tab.py:1`

**Questions?**
- Check existing documentation
- Review test examples
- Examine example configurations in `config/clients/`

---

## Changelog

### v3.5.0 (November 27, 2025)

**Added:**
- Independent H1/H2/H3 text color controls
- Main menu text color customization
- Hero background image support with gradient overlay
- Two-column branding tab UI layout
- clear_data() method to BrandingTab
- _emit_config_changed() override for proper state management

**Changed:**
- BrandingTab UI from single to two-column layout
- City template heading semantics (h3 → h2 for sections)
- Test suite complete rewrite (v1.01 → v2.00)
- BrandingConfig with 4 new color fields + hero background

**Fixed:**
- Config changed signal emission (has_changes flag)
- Test data structure to match new config format
- Color tracking for new color fields

**Technical:**
- models.py: v1.00 → v1.01
- css_generator.py: v1.00 → v1.01
- branding_tab.py: v2.05 → v2.06
- enhanced_main_window.py: v3.03 → v3.04
- test_branding_tab.py: v1.01 → v2.00

---

**Document Version**: 1.0
**Last Updated**: November 27, 2025
**Maintained By**: Rank Rocket Co Development Team
