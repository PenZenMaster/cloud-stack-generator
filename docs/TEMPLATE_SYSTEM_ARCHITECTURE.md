# Template System Architecture Design
**Version**: 1.00
**Created**: 2025-10-17
**Status**: Design Phase

---

## Executive Summary

Comprehensive template system overhaul to enable template selection, import/export, and WYSIWYG editing capabilities. Moves from single hardcoded template to flexible multi-template architecture.

---

## Current State Assessment

### Existing Infrastructure (Ready to Use)
- ✅ **TemplateManager** - Template discovery, loading, Jinja2 environment
- ✅ **TemplateMetadata** - Dataclass with type/variant/version/features
- ✅ **TemplateValidator** - Accessibility, SEO, structure validation
- ✅ **TemplateFormatter** - BeautifulSoup HTML formatting
- ✅ **TemplatePreviewGenerator** - Jinja2 rendering with error classification
- ✅ **TemplateSelectionDialog** - UI scaffolding with preview worker
- ✅ **Multiple Template Files** - basic, enhanced, seo_authority variants exist

### Gaps (Need Implementation)
- ❌ **Template Metadata Files** - No *.template.json files for templates
- ❌ **Template Library UI** - Selection dialog not connected to generation flow
- ❌ **Import/Export System** - Template packaging and distribution
- ❌ **WYSIWYG Editor Integration** - Visual template editing
- ❌ **Template Persistence** - User template selection storage in config

---

## Architecture Design

### Phase 1: Template Metadata System (Foundation)

#### 1.1 Template Directory Structure
```
src/templates/
├── pages/                          # Template HTML files
│   ├── basic_city_page.html
│   ├── enhanced_business_city.html
│   ├── seo_authority_city_page.html
│   └── ...
├── metadata/                       # NEW: Template metadata
│   ├── basic_city_page.template.json
│   ├── enhanced_business_city.template.json
│   ├── seo_authority_city.template.json
│   └── custom/                     # User-imported templates
│       └── my_custom_template.template.json
├── previews/                       # NEW: Template preview images
│   ├── basic_city_preview.png
│   ├── enhanced_business_preview.png
│   ├── seo_authority_preview.png
│   └── ...
├── components/                     # Reusable components
│   ├── header.html
│   ├── footer.html
│   └── ...
└── backups/                        # Template edit backups
    └── ...
```

#### 1.2 Template Metadata Schema
```json
{
  "id": "seo_authority_city",
  "name": "SEO Authority City Page",
  "description": "Comprehensive SEO-optimized city page...",
  "type": "city_page",
  "variant": "seo_authority",
  "version": "2.1.0",
  "author": "Cloud Stack Generator Team",
  "created_date": "2025-08-15",
  "last_modified": "2025-10-17",
  "preview_image": "previews/seo_authority_preview.png",
  "template_file": "pages/seo_authority_city_page.html",
  "required_data": [
    "city_page.city_name",
    "city_page.title",
    "business.business_name"
  ],
  "optional_data": [
    "city_page.places_of_interest",
    "city_page.city_faq"
  ],
  "features": [
    "Advanced SEO optimization",
    "Schema.org markup",
    "Wikipedia integration"
  ],
  "compatibility": {
    "min_version": "2.0.0",
    "supports_city_pages": true,
    "supports_wikipedia": true
  },
  "tags": ["seo", "city", "local-business", "authority"],
  "thumbnail_url": null
}
```

#### 1.3 Template Registry Enhancement
**File**: `src/core/templates/template_manager.py`

**Changes**:
- Update `_discover_templates()` to scan `metadata/` directory
- Add `get_templates_by_type()` method
- Add `get_templates_by_variant()` method
- Add `get_template_preview_path()` method
- Add `export_template()` method
- Add `import_template()` method

---

### Phase 2: Template Selection Integration

#### 2.1 Template Selection UI Flow
```
User clicks "Choose Template" button
    ↓
TemplateSelectionDialog opens
    ↓
Displays template cards with:
  - Preview image
  - Template name/description
  - Feature badges (SEO, Schema, etc.)
  - Variant label (Basic/Enhanced/SEO Authority)
    ↓
User selects template
    ↓
Live preview generated in dialog
    ↓
User confirms selection
    ↓
Template ID saved to config
    ↓
Website generation uses selected template
```

#### 2.2 Configuration Storage
**File**: `config/site_config.yaml`

**Add new section**:
```yaml
template_config:
  selected_template_id: "seo_authority_city"
  template_variant: "seo_authority"
  template_type: "city_page"
  custom_template_path: null  # For imported templates
```

#### 2.3 UI Integration Points
**Files to modify**:
- `src/ui/enhanced_main_window.py` - Add "Choose Template" button
- `src/ui/dialogs/template_selection_dialog.py` - Connect to actual template data
- `src/core/generators/website_generator.py` - Use selected template from config

---

### Phase 3: Template Import/Export System

#### 3.1 Template Package Format
**File**: `template-name.ctpl` (Cloud Template Package - ZIP archive)

**Contents**:
```
template-name.ctpl (ZIP)
├── metadata.json              # Template metadata
├── template.html              # Main template file
├── preview.png                # Preview image
├── components/                # Optional: included components
│   └── custom-footer.html
└── README.md                  # Template documentation
```

#### 3.2 Import Workflow
```
User clicks "Import Template"
    ↓
File dialog opens (.ctpl filter)
    ↓
Validate package structure
    ↓
Check template compatibility
    ↓
Extract to templates/metadata/custom/
    ↓
Register in TemplateManager
    ↓
Show success notification
    ↓
Template appears in selection dialog
```

#### 3.3 Export Workflow
```
User selects template to export
    ↓
Click "Export Template"
    ↓
Package template files
    ↓
Create .ctpl archive
    ↓
Save dialog
    ↓
Success notification
```

#### 3.4 Import/Export Implementation
**New file**: `src/core/templates/template_package.py`

**Classes**:
- `TemplatePackage` - Represents .ctpl package
- `TemplateImporter` - Validates and imports templates
- `TemplateExporter` - Creates .ctpl packages

---

### Phase 4: WYSIWYG Template Editor

#### 4.1 Editor Architecture Decision

**Options Evaluated**:
1. **Monaco Editor** (VS Code engine)
   - Pros: Syntax highlighting, intellisense, mature
   - Cons: Web-based, requires embedding browser

2. **QScintilla** (PyQt native)
   - Pros: Native Qt integration, lightweight
   - Cons: Less modern UI, manual syntax setup

3. **Hybrid Approach** (RECOMMENDED)
   - Code view: QScintilla for HTML editing
   - Visual preview: QWebEngineView for live preview
   - Side-by-side or tabbed interface

#### 4.2 WYSIWYG Editor Components
**New file**: `src/ui/dialogs/wysiwyg_template_editor.py`

**Features**:
- Split pane: Code editor | Live preview
- Syntax highlighting for HTML/Jinja2
- Real-time preview updates (debounced)
- Template variable autocomplete
- Save/Save As functionality
- Undo/Redo support
- Template validation on save

#### 4.3 Editor Integration
**Access points**:
- Template Selection Dialog → "Edit Template" button
- Main window → "Template Editor" menu item
- Opens existing template or creates new from scratch

---

## Implementation Plan

### Sprint 1: Foundation (2-3 days)
**Goal**: Template metadata system operational

**Tasks**:
1. Create `src/templates/metadata/` directory structure
2. Generate metadata JSON files for existing templates (basic, enhanced, seo_authority)
3. Create preview images for each template
4. Update `TemplateManager._discover_templates()` to scan metadata directory
5. Add template filtering methods (by type, variant, tags)
6. Write unit tests for metadata loading and filtering

**Deliverables**:
- ✅ All existing templates have metadata JSON files
- ✅ Preview images generated and stored
- ✅ TemplateManager can discover and load all templates
- ✅ Unit tests passing

---

### Sprint 2: Template Selection UI (2-3 days)
**Goal**: Functional template selection dialog

**Tasks**:
1. Connect `TemplateSelectionDialog` to `TemplateManager`
2. Implement template card rendering with preview images
3. Add template filtering by type/variant/tags
4. Implement live preview generation
5. Add template selection confirmation
6. Store selected template in `site_config.yaml`
7. Update website generator to use selected template

**Deliverables**:
- ✅ Template selection dialog displays all available templates
- ✅ User can preview and select templates
- ✅ Selected template persists in configuration
- ✅ Website generation uses selected template

---

### Sprint 3: Import/Export (2 days)
**Goal**: Template sharing and distribution

**Tasks**:
1. Create `TemplatePackage` class for .ctpl format
2. Implement `TemplateImporter` with validation
3. Implement `TemplateExporter` with packaging
4. Add Import/Export buttons to template selection dialog
5. Add custom template directory management
6. Write unit tests for import/export

**Deliverables**:
- ✅ Users can export templates as .ctpl packages
- ✅ Users can import .ctpl templates
- ✅ Imported templates appear in selection dialog
- ✅ Validation prevents incompatible templates

---

### Sprint 4: WYSIWYG Editor (3-4 days)
**Goal**: Visual template editing

**Tasks**:
1. Implement QScintilla-based code editor
2. Add Jinja2 syntax highlighting
3. Implement live preview pane with QWebEngineView
4. Add template variable autocomplete
5. Integrate TemplateFormatter for code formatting
6. Add save/save-as with automatic backup
7. Integrate TemplateValidator for pre-save validation
8. Add to main window menu

**Deliverables**:
- ✅ WYSIWYG editor accessible from UI
- ✅ Side-by-side code/preview editing
- ✅ Real-time preview updates
- ✅ Template validation on save
- ✅ Automatic backups created

---

## Technical Considerations

### Dependencies
**Required packages**:
```python
# Already installed
PyQt6>=6.4.0
Jinja2>=3.1.0
beautifulsoup4>=4.11.0

# New dependencies (may need to add)
QScintilla>=2.13.0  # For WYSIWYG editor
```

### Performance Optimization
- **Lazy loading**: Load template metadata on demand
- **Preview caching**: Cache generated previews for performance
- **Debounced preview**: Limit preview updates in WYSIWYG editor (500ms delay)
- **Background workers**: Use QThread for preview generation

### Error Handling
- **Import validation**: Check compatibility before importing
- **Graceful fallback**: Use default template if selected template missing
- **User feedback**: Clear error messages for validation failures
- **Backup system**: Automatic backups before template edits

### Testing Strategy
- **Unit tests**: Template loading, metadata parsing, import/export
- **Integration tests**: UI dialog workflows, template selection persistence
- **Manual QA**: Template preview accuracy, WYSIWYG editing, cross-platform compatibility

---

## Migration Path

### Backward Compatibility
**Requirement**: Existing configurations must continue working

**Strategy**:
1. If no `template_config` section exists, use default SEO Authority template
2. Fallback chain: selected_template_id → default variant → hardcoded fallback
3. Migration script to add template_config to existing site_config.yaml files

### User Communication
- **Release notes**: Explain new template system
- **Tutorial**: How to select and customize templates
- **Documentation**: Template metadata schema for custom templates

---

## Success Metrics

### Phase 1 (Metadata System)
- ✅ All 3+ existing templates have metadata files
- ✅ Preview images generated for all templates
- ✅ TemplateManager discovers all templates correctly
- ✅ Unit test coverage: 80%+

### Phase 2 (Selection UI)
- ✅ Template selection dialog fully functional
- ✅ Selected template persists across sessions
- ✅ Website generation uses selected template
- ✅ User can switch templates without errors

### Phase 3 (Import/Export)
- ✅ User can export any template as .ctpl
- ✅ User can import .ctpl templates
- ✅ Validation prevents broken templates
- ✅ Custom templates work identically to built-in templates

### Phase 4 (WYSIWYG)
- ✅ Editor provides real-time preview
- ✅ Syntax highlighting works for Jinja2
- ✅ Template validation prevents syntax errors
- ✅ Automatic backups protect against data loss

---

## Risk Assessment

### Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| QScintilla integration issues | Medium | Low | Use simpler QTextEdit as fallback |
| Preview rendering performance | Medium | Medium | Implement caching and debouncing |
| Template compatibility issues | High | Medium | Strict validation on import |
| Backward compatibility breaks | High | Low | Comprehensive testing, fallback chain |

### Implementation Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Scope creep (WYSIWYG too complex) | Medium | High | Phase 4 optional, deliver Phases 1-3 first |
| Test coverage degradation | Medium | Medium | Pre-commit hooks enforce coverage |
| User confusion with new UI | Low | Medium | Clear documentation and tutorials |

---

## Future Enhancements (Post-MVP)

### Advanced Features (v3.0+)
- **Template Marketplace**: Share templates with community
- **Template Versioning**: Track template history, rollback capability
- **AI Template Generation**: Generate templates from descriptions
- **Template Analytics**: Track which templates perform best
- **Responsive Preview**: Preview templates at multiple screen sizes
- **Component Library**: Reusable template components (headers, footers, CTAs)
- **Template Inheritance**: Base templates with child variations
- **Theme System**: Color scheme and font variations for templates

---

## References

### Related Files
- `src/core/templates/template_manager.py` - Core template management
- `src/ui/dialogs/template_selection_dialog.py` - Selection UI
- `src/core/templates/template_validator.py` - Validation system
- `src/core/templates/template_formatter.py` - HTML formatting
- `src/core/templates/template_preview.py` - Preview generation
- `docs/projectStatus.md` - Project status tracking

### External Resources
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [QScintilla Documentation](https://qscintilla.com/)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython-6/)

---

## Appendix: Template Metadata Examples

### Basic City Page Template
```json
{
  "id": "basic_city_page",
  "name": "Basic City Page",
  "description": "Simple, clean city page template with essential information",
  "type": "city_page",
  "variant": "basic",
  "version": "1.0.0",
  "author": "Cloud Stack Generator Team",
  "created_date": "2025-08-15",
  "last_modified": "2025-10-17",
  "preview_image": "previews/basic_city_preview.png",
  "template_file": "pages/basic_city_page.html",
  "required_data": [
    "city_page.city_name",
    "business.business_name",
    "contact.phone"
  ],
  "optional_data": [],
  "features": [
    "Clean design",
    "Mobile responsive",
    "Fast loading"
  ],
  "compatibility": {
    "min_version": "2.0.0",
    "supports_city_pages": true
  },
  "tags": ["simple", "basic", "lightweight"]
}
```

### Enhanced Business City Template
```json
{
  "id": "enhanced_business_city",
  "name": "Enhanced Business City Page",
  "description": "Feature-rich city page with business highlights and testimonials",
  "type": "city_page",
  "variant": "enhanced",
  "version": "1.5.0",
  "author": "Cloud Stack Generator Team",
  "created_date": "2025-08-20",
  "last_modified": "2025-10-17",
  "preview_image": "previews/enhanced_business_preview.png",
  "template_file": "pages/enhanced_business_city.html",
  "required_data": [
    "city_page.city_name",
    "business.business_name",
    "contact.phone",
    "contact.email"
  ],
  "optional_data": [
    "city_page.testimonials",
    "city_page.portfolio_images"
  ],
  "features": [
    "Business highlights",
    "Testimonial sections",
    "Portfolio showcase",
    "Call-to-action blocks"
  ],
  "compatibility": {
    "min_version": "2.0.0",
    "supports_city_pages": true,
    "supports_testimonials": true
  },
  "tags": ["business", "enhanced", "testimonials", "portfolio"]
}
```

---

**Document Status**: Draft - Ready for implementation
**Next Action**: Begin Sprint 1 - Create metadata files for existing templates
