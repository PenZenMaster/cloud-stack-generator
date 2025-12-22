# Feature Request: HTML Template Import & Export System

## Summary
**Implement a comprehensive template import/export system that allows users to export existing templates for external editing and import custom or modified HTML templates that are dynamically displayed in the Branding Style tab template selector.**

---

## Problem Statement

### Current Situation
- Templates are hardcoded within the application
- No ability to export templates for external editing
- No way to import custom or modified templates
- Template selection is limited to pre-built options
- External designers/developers cannot create custom templates

### Impact
- **Limited Customization**: Users stuck with pre-built templates only
- **Development Bottleneck**: All template changes must go through core development
- **External Designer Friction**: No way for designers to contribute custom templates
- **Workflow Inefficiency**: Cannot use external HTML editors or design tools
- **Business Limitation**: Cannot offer template marketplace or custom template services

---

## Proposed Solution

### Feature Description
Create a complete template import/export system that enables:
1. **Export Templates**: Package existing templates for external editing
2. **Import Templates**: Import custom or modified HTML templates 
3. **Dynamic Template Discovery**: Automatically detect and display imported templates
4. **Template Validation**: Ensure imported templates meet system requirements
5. **Preview System**: Preview imported templates before selection

### User Stories
- As a web designer, I want to export existing templates so that I can modify them in my preferred HTML editor
- As a business owner, I want to import custom templates so that I can have unique designs beyond the built-in options
- As a developer, I want to create custom templates externally so that I can use advanced design tools
- As a template creator, I want to package templates for distribution so that others can use my designs
- As a user, I want imported templates to appear in the template selector so that I can choose them like built-in templates

### Acceptance Criteria
- [ ] Export any existing template as a complete package (.zip)
- [ ] Import template packages with validation and error handling
- [ ] Imported templates automatically appear in Branding Style tab template selector
- [ ] Template preview system works for imported templates
- [ ] Template metadata system supports custom templates
- [ ] Package format includes template files, metadata, and documentation
- [ ] Import validation ensures templates are compatible with current data structure
- [ ] Export preserves all template functionality and styling
- [ ] Template management UI for organizing imported templates
- [ ] Backup system for template modifications

---

## Technical Requirements

### Components Affected
- [x] UI Layer (`src/ui/`) - Template selection and management UI
- [x] Core Logic (`src/core/templates/`) - Import/export engine
- [x] Branding Tab (`src/ui/components/branding_tab.py`) - Template selector integration
- [x] Template Manager (`src/core/templates/template_manager.py`) - Dynamic template discovery
- [x] Template Export (`src/core/templates/template_export.py`) - Export/import functionality
- [ ] Configuration (`config/`) - Template storage settings
- [ ] Testing (`tests/`) - Import/export validation tests
- [ ] Documentation (`docs/`) - Template creation guide

### Existing Infrastructure
Based on codebase analysis, the following components already exist:
- **TemplateManager**: Core template management system
- **TemplateExporter**: Export functionality (stub implementation)
- **TemplateImporter**: Import functionality (stub implementation)
- **TemplateSelectionDialog**: Template picker UI
- **Template metadata system**: JSON-based template configuration

### Missing Components
- **File dialog integration** for import/export operations
- **Template validation engine** for imported templates
- **Dynamic template refresh** in selection UI
- **Template conflict resolution** for duplicate IDs
- **Template package validation** and error reporting

### Performance Considerations
- Template discovery should be cached and refreshed on import
- Large template packages should show import progress
- Template preview generation should be optimized
- Template validation should be non-blocking

---

## Design Considerations

### User Interface Enhancement
Current Branding Style tab needs these additions:

```
┌─────────────────────────────────────────────────────────┐
│ Website Template                                        │
├─────────────────────────────────────────────────────────┤
│ Currently Selected: SEO Authority City Page            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [Choose Template...] [Import Template...] [⬇ Export] │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Template Management                                     │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [📂 Manage Templates...] [🔄 Refresh Templates]      │ │
│ └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### Template Package Structure
```
template_package.zip
├── template.html              # Main template file
├── metadata.json              # Template metadata
├── README.md                  # Documentation
├── assets/                    # Optional assets
│   ├── css/                   # Custom CSS files
│   ├── js/                    # Custom JavaScript
│   └── images/                # Template images
└── preview.png                # Template preview image
```

### Template Metadata Schema
```json
{
  "id": "custom_template_001",
  "name": "Custom Business Template",
  "description": "Professional business template with modern design",
  "type": "city_page",
  "variant": "enhanced",
  "version": "1.0.0",
  "author": "Designer Name",
  "created_date": "2025-10-17",
  "last_modified": "2025-10-17",
  "preview_image": "preview.png",
  "template_file": "template.html",
  "required_data": [
    "business.business_name",
    "contact.phone",
    "contact.email"
  ],
  "optional_data": [
    "business.logo_url",
    "branding.primary_color"
  ],
  "features": [
    "Custom header design",
    "Advanced product showcase",
    "Integrated contact forms"
  ],
  "compatibility": {
    "min_version": "2.1.0",
    "supports_city_pages": true,
    "supports_products": true,
    "supports_services": true
  }
}
```

---

## Implementation Plan

### Phase 1: Core Infrastructure (Week 1)
- [ ] Complete `TemplateExporter.export_template_package()` implementation
- [ ] Complete `TemplateImporter.import_template_package()` implementation  
- [ ] Add template validation system
- [ ] Implement file dialog integration for import/export

### Phase 2: UI Integration (Week 2)
- [ ] Add Import/Export buttons to Branding Style tab
- [ ] Update `TemplateSelectionDialog` to show imported templates
- [ ] Implement template management dialog
- [ ] Add progress indicators for import/export operations

### Phase 3: Dynamic Template System (Week 3)
- [ ] Implement automatic template discovery refresh
- [ ] Add template conflict resolution
- [ ] Create template preview system for imported templates
- [ ] Implement template metadata validation

### Phase 4: Advanced Features (Week 4)
- [ ] Add template collection import/export
- [ ] Implement template backup and versioning
- [ ] Create template creation wizard
- [ ] Add template marketplace preparation features

---

## Code Implementation

### 1. Enhanced Import Template Function

```python
# src/ui/dialogs/template_selection_dialog.py
def import_template(self):
    """Import a custom template"""
    from PyQt6.QtWidgets import QFileDialog
    from core.templates.template_export import TemplateImporter
    
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Import Template Package",
        "",
        "Template Packages (*.zip);;All Files (*)"
    )
    
    if not file_path:
        return
    
    try:
        importer = TemplateImporter(self.template_manager)
        success, message, template_id = importer.import_template_package(Path(file_path))
        
        if success:
            # Refresh template list
            self.load_templates()
            QMessageBox.information(self, "Import Successful", message)
            
            # Auto-select imported template
            if template_id:
                self.on_template_selected(template_id)
        else:
            QMessageBox.warning(self, "Import Failed", message)
            
    except Exception as e:
        QMessageBox.critical(self, "Import Error", f"Failed to import template:\\n{str(e)}")
```

### 2. Enhanced Export Template Function

```python
# src/ui/dialogs/template_selection_dialog.py
def export_template(self):
    """Export the selected template"""
    if not self.selected_template_id:
        QMessageBox.warning(self, "No Selection", "Please select a template to export.")
        return
    
    from PyQt6.QtWidgets import QFileDialog
    from core.templates.template_export import TemplateExporter
    
    # Get template metadata for default filename
    template_metadata = self.template_manager.get_template_by_id(self.selected_template_id)
    if not template_metadata:
        QMessageBox.warning(self, "Error", "Template metadata not found.")
        return
    
    default_name = f"{template_metadata.name.replace(' ', '_').lower()}_v{template_metadata.version}.zip"
    
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Export Template Package",
        default_name,
        "Template Packages (*.zip);;All Files (*)"
    )
    
    if not file_path:
        return
    
    try:
        exporter = TemplateExporter(self.template_manager)
        success = exporter.export_template_package(self.selected_template_id, Path(file_path))
        
        if success:
            QMessageBox.information(
                self, 
                "Export Successful", 
                f"Template '{template_metadata.name}' exported successfully to:\\n{file_path}"
            )
        else:
            QMessageBox.warning(self, "Export Failed", "Failed to export template.")
            
    except Exception as e:
        QMessageBox.critical(self, "Export Error", f"Failed to export template:\\n{str(e)}")
```

### 3. Enhanced Branding Tab Integration

```python
# src/ui/components/branding_tab.py
def _create_template_section(self, parent_layout: QVBoxLayout):
    """Create enhanced template selection section"""
    # ... existing code ...
    
    # Enhanced button layout
    button_layout = QHBoxLayout()
    
    self.select_template_btn = QPushButton("Choose Template...")
    self.select_template_btn.clicked.connect(self._open_template_selection)
    button_layout.addWidget(self.select_template_btn)
    
    # Import template button
    self.import_template_btn = QPushButton("Import Template...")
    self.import_template_btn.setStyleSheet("""
        QPushButton {
            background-color: #27ae60;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #2ecc71;
        }
    """)
    self.import_template_btn.clicked.connect(self._import_template)
    button_layout.addWidget(self.import_template_btn)
    
    # Export template button
    self.export_template_btn = QPushButton("Export Current")
    self.export_template_btn.setStyleSheet("""
        QPushButton {
            background-color: #f39c12;
            color: white;
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
        }
        QPushButton:hover {
            background-color: #e67e22;
        }
    """)
    self.export_template_btn.clicked.connect(self._export_current_template)
    button_layout.addWidget(self.export_template_btn)

def _import_template(self):
    """Handle template import from branding tab"""
    # Open import dialog and refresh template system
    pass

def _export_current_template(self):
    """Handle template export from branding tab"""
    # Export currently selected template
    pass
```

### 4. Template Manager Enhancement

```python
# src/core/templates/template_manager.py
def refresh_templates(self):
    """Refresh template discovery and reload registry"""
    self.templates_registry.clear()
    self._discover_templates()

def import_template(self, template_file: Path, metadata: TemplateMetadata) -> bool:
    """Import a template with metadata"""
    try:
        # Create template directory if needed
        template_dir = self.templates_dir / "imported"
        template_dir.mkdir(exist_ok=True)
        
        # Copy template file
        dest_file = template_dir / f"{metadata.id}.html"
        shutil.copy2(template_file, dest_file)
        
        # Update metadata with correct path
        metadata.template_file = f"imported/{metadata.id}.html"
        
        # Save metadata
        metadata_file = template_dir / f"{metadata.id}.template.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Add to registry
        self.templates_registry[metadata.id] = metadata
        
        return True
        
    except Exception as e:
        print(f"Error importing template: {e}")
        return False
```

---

## Testing Strategy

### Unit Tests
- Template package creation and extraction
- Metadata validation and parsing
- Template file validation
- Import conflict detection and resolution

### Integration Tests
- End-to-end import workflow from file selection to template availability
- Export workflow from template selection to package creation
- Template selection UI integration with imported templates
- Template preview generation for imported templates

### User Acceptance Testing
- Import custom templates created by external designers
- Export and re-import existing templates to verify integrity
- Template selector shows imported templates correctly
- Error handling for malformed template packages

---

## Risks & Mitigation

### Technical Risks
| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Malformed template packages | High | Medium | Comprehensive validation and error handling |
| Template ID conflicts | Medium | High | Conflict resolution dialog with rename options |
| Large package import performance | Medium | Low | Progress indicators and streaming import |
| Template compatibility issues | High | Medium | Version checking and compatibility validation |

### Security Risks
- **Malicious template content**: Sanitize HTML and validate against allowed tags
- **Path traversal attacks**: Validate file paths in packages
- **Resource consumption**: Limit package size and extraction time

---

## Success Metrics

### Quantitative Metrics
- Template import success rate: >95%
- Template export integrity: 100% round-trip success
- Import time for standard templates: <10 seconds
- User adoption of import feature: >30% of active users

### Qualitative Metrics
- User satisfaction with template customization options
- Designer feedback on export/import workflow
- Reduction in custom template development requests
- Community template sharing engagement

---

## Timeline & Effort

### Estimated Effort
- **Phase 1**: 40 hours (Core infrastructure)
- **Phase 2**: 32 hours (UI integration)
- **Phase 3**: 24 hours (Dynamic template system)
- **Phase 4**: 24 hours (Advanced features)
- **Testing**: 20 hours (Comprehensive testing)
- **Documentation**: 10 hours (User guides and API docs)
- **Total**: 150 hours (4-5 weeks)

### Target Milestones
- **Week 1**: Complete import/export core functionality
- **Week 2**: UI integration and basic workflow
- **Week 3**: Dynamic template discovery and validation
- **Week 4**: Advanced features and polish
- **Week 5**: Testing, documentation, and release

---

## Related Issues & References

### Existing Codebase Components
- `src/core/templates/template_export.py` - Import/export foundation (stub)
- `src/ui/dialogs/template_selection_dialog.py` - Template selection UI
- `src/ui/components/branding_tab.py` - Template selector integration
- `src/core/templates/template_manager.py` - Template management system

### Related Features
- Template preview system enhancement
- WYSIWYG template editor integration
- Template marketplace preparation
- Template versioning and backup system

---

## Appendix

### Template Creation Guidelines
For external template creators, provide documentation on:
- Required template structure and variables
- Jinja2 template syntax for dynamic content
- CSS and JavaScript integration guidelines
- Testing templates with sample data
- Packaging requirements and best practices

### Package Format Specification
Detailed specification for template package format including:
- File structure requirements
- Metadata schema validation
- Asset organization guidelines
- Compatibility requirements
- Version migration strategies

---

**Created by**: GitHub Copilot  
**Date**: October 17, 2025  
**Priority**: High (Core functionality enhancement)  
**Complexity**: Medium-High  
**Status**: Ready for Implementation