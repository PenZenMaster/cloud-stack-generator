# UI Theme System

**Version**: 3.5.0
**Created**: 2025-11-23
**Purpose**: Centralized UI styling system for consistent UX

---

## Overview

The theme system provides centralized button styles, colors, typography, and spacing configuration for the entire application. This eliminates code duplication and ensures visual consistency across all UI components.

---

## Quick Start

### Basic Usage

```python
from PyQt6.QtWidgets import QPushButton
from src.ui.themes import ButtonStyles, ThemeManager

# Method 1: Direct style assignment
generate_btn = QPushButton("Generate Website")
generate_btn.setStyleSheet(ButtonStyles.SUCCESS)

# Method 2: Using ThemeManager
ai_btn = QPushButton("Generate with AI")
ThemeManager.apply_button_style(ai_btn, "ai_generation")

# Method 3: Custom colors
custom_btn = QPushButton("Custom")
custom_style = ThemeManager.get_button_style(
    color="#ff5722",
    hover_color="#e64a19",
    pressed_color="#d84315"
)
custom_btn.setStyleSheet(custom_style)
```

---

## Available Button Styles

### Pre-defined Styles

| Style | Usage | Color | Purpose |
|-------|-------|-------|---------|
| `ButtonStyles.AI_GENERATION` | AI features | #007bff (Blue) | AI-powered generation buttons |
| `ButtonStyles.SUCCESS` | Primary actions | #28a745 (Green) | Generate, Create, Save |
| `ButtonStyles.VALIDATION` | Data validation | #9b59b6 (Purple) | Validate, Check, Verify |
| `ButtonStyles.IMPORT` | Import operations | #27ae60 (Green) | Import from CSV/file |
| `ButtonStyles.EXPORT` | Export operations | #3498db (Blue) | Export to CSV/file |
| `ButtonStyles.DANGER` | Destructive actions | #e74c3c (Red) | Delete, Remove, Clear |
| `ButtonStyles.DISABLED` | Inactive state | #95a5a6 (Gray) | Disabled buttons |

### Style Aliases

```python
# These are equivalent
ButtonStyles.AI_GENERATION
ThemeManager.apply_button_style(btn, "ai")
ThemeManager.apply_button_style(btn, "ai_generation")

# Success aliases
ButtonStyles.SUCCESS
ThemeManager.apply_button_style(btn, "success")
ThemeManager.apply_button_style(btn, "generate")

# Danger aliases
ButtonStyles.DANGER
ThemeManager.apply_button_style(btn, "danger")
ThemeManager.apply_button_style(btn, "delete")
```

---

## Color Palette

```python
from src.ui.themes import ColorPalette

# Primary Colors
ColorPalette.AI_BLUE              # #007bff
ColorPalette.SUCCESS_GREEN        # #28a745
ColorPalette.VALIDATION_PURPLE    # #9b59b6
ColorPalette.IMPORT_GREEN         # #27ae60
ColorPalette.EXPORT_BLUE          # #3498db
ColorPalette.DANGER_RED           # #e74c3c
ColorPalette.DISABLED_GRAY        # #95a5a6

# Hover States (automatically applied in button styles)
ColorPalette.AI_BLUE_HOVER        # #0056b3
ColorPalette.SUCCESS_GREEN_HOVER  # #218838
# ... etc

# Pressed States
ColorPalette.AI_BLUE_PRESSED      # #004085
ColorPalette.SUCCESS_GREEN_PRESSED # #1e7e34
# ... etc
```

---

## Typography

```python
from src.ui.themes import Typography

# Font Family
Typography.FONT_FAMILY    # "Arial"

# Font Sizes
Typography.SIZE_SMALL     # 10pt
Typography.SIZE_NORMAL    # 12pt (default for buttons)
Typography.SIZE_LARGE     # 14pt
Typography.SIZE_XLARGE    # 16pt

# Font Weights
Typography.WEIGHT_NORMAL  # "normal"
Typography.WEIGHT_BOLD    # "bold" (default for buttons)
```

---

## Spacing

```python
from src.ui.themes import Spacing

# Padding
Spacing.PADDING_SMALL     # "6px 12px"
Spacing.PADDING_NORMAL    # "8px 16px" (default for buttons)
Spacing.PADDING_LARGE     # "10px 20px"

# Border Radius
Spacing.RADIUS_SMALL      # 4px
Spacing.RADIUS_NORMAL     # 6px (default for buttons)
Spacing.RADIUS_LARGE      # 8px

# Margins
Spacing.MARGIN_SMALL      # 8px
Spacing.MARGIN_NORMAL     # 12px
Spacing.MARGIN_LARGE      # 16px
```

---

## Advanced Usage

### Custom Button with Different Font Size

```python
from src.ui.themes import ThemeManager, Typography

large_btn = QPushButton("Large Button")
large_style = ThemeManager.get_button_style(
    color="#28a745",
    hover_color="#218838",
    pressed_color="#1e7e34",
    font_size=Typography.SIZE_LARGE  # 14pt instead of default 12pt
)
large_btn.setStyleSheet(large_style)
```

### Custom Padding and Radius

```python
from src.ui.themes import ThemeManager, Spacing

compact_btn = QPushButton("Compact")
compact_style = ThemeManager.get_button_style(
    color="#3498db",
    hover_color="#2980b9",
    pressed_color="#216696",
    padding=Spacing.PADDING_SMALL,  # Smaller padding
    radius=Spacing.RADIUS_LARGE     # Larger border radius
)
compact_btn.setStyleSheet(compact_style)
```

### List Available Styles

```python
from src.ui.themes import ThemeManager

# Get all available style names
styles = ThemeManager.get_available_styles()
print(styles)
# Output: ['ai_generation', 'ai', 'success', 'generate', 'validation',
#          'validate', 'import', 'export', 'danger', 'delete', 'disabled']
```

---

## Migration Guide

### Before (Old Way)

```python
# Inline styles scattered everywhere
self.generate_btn = QPushButton("Generate")
self.generate_btn.setStyleSheet("""
    QPushButton {
        background-color: #28a745;
        color: white;
        padding: 8px 16px;
        border: none;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #218838;
    }
""")
```

### After (New Way)

```python
from src.ui.themes import ButtonStyles

# Centralized, consistent styling
self.generate_btn = QPushButton("Generate")
self.generate_btn.setStyleSheet(ButtonStyles.SUCCESS)
```

---

## Theme Specifications

### Current Theme: Default (v3.5.0)

- **Font**: Arial, 12pt, Bold
- **Padding**: 8px vertical, 16px horizontal
- **Border Radius**: 6px
- **States**: Normal, Hover, Pressed, Disabled

All button styles include:
- Smooth hover transitions
- Visible pressed state
- Graceful disabled state
- Consistent typography
- Uniform spacing

---

## Contributing

When adding new UI elements:

1. **Use existing styles** when possible
2. **Add new styles** to `default_theme.py` if needed
3. **Document** new styles in this README
4. **Maintain consistency** with existing color palette
5. **Test** across all themes (when multiple themes exist)

---

## Future Enhancements

- [ ] Dark theme support
- [ ] High-contrast accessibility theme
- [ ] Custom theme loading from config files
- [ ] Theme preview tool
- [ ] Additional widget styles (inputs, dropdowns, etc.)

---

## Version History

- **v1.00** (2025-11-23): Initial theme system
  - 7 button style presets
  - Color palette with hover/pressed states
  - Typography and spacing constants
  - ThemeManager helper class
