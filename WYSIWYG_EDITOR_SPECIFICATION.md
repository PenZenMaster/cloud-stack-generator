# WYSIWYG Template Editor Specification

## Overview

Design and implement a comprehensive WYSIWYG template editor that allows users to visually edit templates while maintaining code integrity through validation, error prevention, and automatic versioning.

## Core Requirements

### 1. **Save Guardrails** 🛡️
- **No saving with errors**: Validate template before allowing save
- **Syntax validation**: Check Jinja2 syntax and HTML structure
- **Data compatibility**: Ensure template works with available data
- **Performance validation**: Check for potential performance issues

### 2. **Automatic Backup System** 💾
- **Version on every save**: Create backup of entire template
- **Timestamp-based naming**: `template_id_YYYYMMDD_HHMMSS.backup`
- **Metadata preservation**: Backup both HTML and JSON metadata
- **Storage management**: Automatic cleanup of old backups (keep last 20)

### 3. **Rollback Functionality** ↩️
- **Version history**: Show list of previous versions with timestamps
- **Preview comparisons**: Compare current vs previous versions
- **One-click rollback**: Restore any previous version
- **Rollback validation**: Ensure rollback version still compatible

## Architecture Design

### Module Structure
```
src/ui/editors/
├── template_editor_dialog.py        # Main editor dialog (400-500 lines)
├── code_editor_widget.py           # Monaco/CodeMirror integration (300-400 lines)
├── preview_panel_widget.py         # Live preview display (200-300 lines)
├── validation_panel_widget.py      # Error display and validation UI (200-300 lines)
├── version_history_widget.py       # Version management UI (300-400 lines)
└── editor_toolbar_widget.py        # Editor toolbar and actions (200-300 lines)

src/core/templates/
├── template_validator.py           # Template validation engine (400-500 lines)
├── template_versioning.py          # Backup and version management (300-400 lines)
├── template_syntax_checker.py      # Jinja2 and HTML validation (300-400 lines)
└── template_backup_manager.py      # Backup storage and cleanup (200-300 lines)

src/core/editors/
├── wysiwyg_processor.py            # WYSIWYG processing logic (400-500 lines)
├── template_ast_analyzer.py        # Template parsing and analysis (300-400 lines)
└── live_preview_engine.py          # Live preview generation (300-400 lines)
```

## Detailed Component Specifications

### 1. **Template Editor Dialog** (`template_editor_dialog.py`)

#### Responsibilities:
- Main dialog window management
- Panel coordination and layout
- Save/cancel/rollback action coordination
- User interaction flow control

#### Key Features:
- **Split-pane layout**: Code editor (left) | Preview + validation (right)
- **Tabbed interface**: Edit, Preview, Versions, Settings
- **Status bar**: Current validation status, save state, word count
- **Modal behavior**: Block other application actions while editing

#### UI Layout:
```
┌─── Template Editor ─────────────────────────────────────────────┐
│ File: enhanced_business_city.html                   [✓] [Save] [✗] │
├─────────────────────────────────────────────────────────────────┤
│ ┌─── Code Editor ──────────┐ ┌─── Preview & Validation ──────┐ │
│ │ 1 <!DOCTYPE html>        │ │ ┌─ Live Preview ─────────────┐ │ │
│ │ 2 <html lang="en">       │ │ │ [Rendered template here]   │ │ │
│ │ 3 <head>                 │ │ │                            │ │ │
│ │ 4   <meta charset="UTF-8"│ │ │                            │ │ │
│ │ 5   <title>{{ city...    │ │ │                            │ │ │
│ │ ... [Monaco Editor]      │ │ └────────────────────────────┘ │ │
│ │                          │ │ ┌─ Validation ──────────────┐ │ │
│ │                          │ │ │ ✓ HTML syntax valid        │ │ │
│ │                          │ │ │ ✓ Jinja2 syntax valid     │ │ │
│ │                          │ │ │ ⚠ Missing: city_page.name │ │ │
│ │                          │ │ │ ✓ Performance OK          │ │ │
│ │                          │ │ └────────────────────────────┘ │ │
│ └──────────────────────────┘ └────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│ Status: Modified • 1,247 lines • 3 warnings • Last saved: 14:32 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. **Code Editor Widget** (`code_editor_widget.py`)

#### Features:
- **Monaco Editor integration**: VS Code-like editing experience
- **Syntax highlighting**: HTML, CSS, JavaScript, Jinja2
- **Auto-completion**: Jinja2 variables, HTML tags, CSS properties
- **Error underlining**: Real-time syntax error highlighting
- **Code folding**: Collapsible sections
- **Find/replace**: Advanced search capabilities

#### Technical Implementation:
```python
class CodeEditorWidget(QWidget):
    text_changed = pyqtSignal(str)  # Emit when content changes
    validation_requested = pyqtSignal()  # Request validation

    def __init__(self):
        # Embed Monaco Editor via QWebEngine
        self.web_view = QWebEngineView()
        self.setup_monaco_editor()

    def setup_monaco_editor(self):
        # Configure Monaco with Jinja2 syntax support
        # Add custom auto-completion for template variables
        # Configure theme and editor options

    def set_template_content(self, content: str):
        # Load template content into editor

    def get_template_content(self) -> str:
        # Get current editor content

    def highlight_errors(self, errors: List[ValidationError]):
        # Add error decorations to editor
```

### 3. **Template Validator** (`template_validator.py`)

#### Validation Categories:

##### **Syntax Validation**:
- **HTML validation**: Well-formed markup, proper nesting
- **CSS validation**: Valid CSS syntax in `<style>` blocks
- **JavaScript validation**: Valid JS syntax in `<script>` blocks
- **Jinja2 validation**: Template syntax, variable references, loops

##### **Data Compatibility**:
- **Required fields**: Check all required template data available
- **Variable existence**: Verify all {{ variables }} have data sources
- **Loop compatibility**: Ensure arrays exist for {% for %} loops
- **Filter validation**: Check custom filters are available

##### **Performance Validation**:
- **Large loops**: Warn about potentially expensive loops
- **External resources**: Check for external CSS/JS dependencies
- **Image optimization**: Suggest image optimization opportunities
- **CSS efficiency**: Detect inefficient CSS selectors

#### Implementation:
```python
class TemplateValidator:
    def validate_template(self, content: str, metadata: dict) -> ValidationResult:
        """Comprehensive template validation"""
        result = ValidationResult()

        # 1. Syntax validation
        result.merge(self._validate_html_syntax(content))
        result.merge(self._validate_jinja2_syntax(content))
        result.merge(self._validate_css_syntax(content))

        # 2. Data compatibility
        result.merge(self._validate_data_compatibility(content, metadata))

        # 3. Performance checks
        result.merge(self._validate_performance(content))

        # 4. Best practices
        result.merge(self._validate_best_practices(content))

        return result

    def _validate_jinja2_syntax(self, content: str) -> ValidationResult:
        """Validate Jinja2 template syntax"""
        try:
            template = self.jinja_env.from_string(content)
            # Additional custom validation
        except TemplateSyntaxError as e:
            return ValidationResult().add_error(f"Jinja2 syntax error: {e}")

class ValidationResult:
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationWarning] = []
        self.info: List[ValidationInfo] = []

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def can_save(self) -> bool:
        return self.is_valid()  # Only allow save if no errors
```

### 4. **Template Versioning System** (`template_versioning.py`)

#### Backup Strategy:
```python
class TemplateVersioning:
    def __init__(self, templates_dir: Path):
        self.templates_dir = templates_dir
        self.backups_dir = templates_dir / "backups"
        self.backups_dir.mkdir(exist_ok=True)

    def create_backup(self, template_id: str) -> str:
        """Create backup before saving changes"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{template_id}_{timestamp}"

        # Create backup directory
        backup_dir = self.backups_dir / backup_name
        backup_dir.mkdir(exist_ok=True)

        # Backup HTML template
        template_file = self._find_template_file(template_id)
        if template_file.exists():
            shutil.copy2(template_file, backup_dir / "template.html")

        # Backup JSON metadata
        metadata_file = self._find_metadata_file(template_id)
        if metadata_file.exists():
            shutil.copy2(metadata_file, backup_dir / "metadata.json")

        # Create backup manifest
        manifest = {
            "template_id": template_id,
            "backup_timestamp": timestamp,
            "original_files": {
                "template": str(template_file),
                "metadata": str(metadata_file)
            },
            "backup_reason": "manual_save",
            "generator_version": "2.1.0"
        }

        with open(backup_dir / "manifest.json", 'w') as f:
            json.dump(manifest, f, indent=2)

        self._cleanup_old_backups(template_id)
        return backup_name

    def get_version_history(self, template_id: str) -> List[TemplateVersion]:
        """Get list of available versions for rollback"""
        versions = []

        for backup_dir in self.backups_dir.glob(f"{template_id}_*"):
            manifest_file = backup_dir / "manifest.json"
            if manifest_file.exists():
                with open(manifest_file) as f:
                    manifest = json.load(f)
                    versions.append(TemplateVersion.from_manifest(manifest))

        return sorted(versions, key=lambda v: v.timestamp, reverse=True)

    def rollback_to_version(self, template_id: str, version_name: str) -> bool:
        """Rollback template to specific version"""
        backup_dir = self.backups_dir / version_name

        if not backup_dir.exists():
            return False

        # Create backup of current version first
        current_backup = self.create_backup(template_id)

        try:
            # Restore HTML template
            backup_template = backup_dir / "template.html"
            current_template = self._find_template_file(template_id)
            shutil.copy2(backup_template, current_template)

            # Restore metadata
            backup_metadata = backup_dir / "metadata.json"
            current_metadata = self._find_metadata_file(template_id)
            shutil.copy2(backup_metadata, current_metadata)

            return True

        except Exception as e:
            # If rollback fails, restore current backup
            self.rollback_to_version(template_id, current_backup)
            return False
```

### 5. **Live Preview Engine** (`live_preview_engine.py`)

#### Features:
- **Real-time rendering**: Update preview as user types (debounced)
- **Error highlighting**: Show rendering errors in preview
- **Sample data injection**: Use realistic sample data for preview
- **Responsive preview**: Toggle between desktop/tablet/mobile views
- **Performance metrics**: Show rendering time and size

#### Implementation:
```python
class LivePreviewEngine:
    def __init__(self, template_manager: TemplateManager):
        self.template_manager = template_manager
        self.preview_data = self._get_sample_data()
        self.last_preview_time = 0

    def generate_preview(self, template_content: str,
                        debounce_ms: int = 500) -> PreviewResult:
        """Generate live preview with debouncing"""
        current_time = time.time() * 1000

        if current_time - self.last_preview_time < debounce_ms:
            return self.cached_preview

        try:
            # Create temporary Jinja2 template
            template = self.jinja_env.from_string(template_content)

            # Render with sample data
            start_time = time.time()
            rendered_html = template.render(**self.preview_data)
            render_time = (time.time() - start_time) * 1000

            # Add preview enhancements
            enhanced_html = self._add_preview_styling(rendered_html)

            result = PreviewResult(
                html=enhanced_html,
                render_time_ms=render_time,
                size_bytes=len(rendered_html),
                errors=[],
                warnings=[]
            )

            self.cached_preview = result
            self.last_preview_time = current_time

            return result

        except Exception as e:
            return PreviewResult(
                html=self._generate_error_preview(str(e)),
                errors=[PreviewError(str(e), type(e).__name__)]
            )
```

## Save Guardrails Implementation

### Save Process Flow:
```python
def attempt_save(self) -> bool:
    """Attempt to save template with full validation"""

    # 1. Get current content
    content = self.code_editor.get_template_content()
    metadata = self.get_current_metadata()

    # 2. Run comprehensive validation
    validation_result = self.validator.validate_template(content, metadata)

    # 3. Check save eligibility
    if not validation_result.can_save():
        self.show_save_blocked_dialog(validation_result.errors)
        return False

    # 4. Show warnings (if any) but allow save
    if validation_result.warnings:
        if not self.confirm_save_with_warnings(validation_result.warnings):
            return False

    # 5. Create backup before saving
    backup_name = self.versioning.create_backup(self.template_id)

    try:
        # 6. Save template files
        self.save_template_files(content, metadata)

        # 7. Update UI state
        self.mark_as_saved()
        self.refresh_template_manager()

        return True

    except Exception as e:
        # 8. Rollback on save failure
        self.versioning.rollback_to_version(self.template_id, backup_name)
        self.show_save_error_dialog(str(e))
        return False
```

## User Experience Flow

### 1. **Opening Editor**:
```
Branding Tab → Choose Template → [Edit Template] button → WYSIWYG Editor
```

### 2. **Editing Experience**:
- **Real-time validation**: Errors highlighted as user types
- **Live preview**: Updated preview in right panel
- **Auto-save prompts**: Warn before losing changes
- **Performance feedback**: Show render time and warnings

### 3. **Save Validation**:
- **Red save button**: When errors exist (save disabled)
- **Yellow save button**: When warnings exist (save allowed)
- **Green save button**: When validation passes
- **Error panel**: Clear list of issues to fix

### 4. **Version Management**:
- **Version history**: Accessible via "Versions" tab
- **One-click rollback**: Select version and click "Restore"
- **Diff view**: Compare current vs previous versions
- **Backup notifications**: Confirm backup creation

## Implementation Priority

### Phase 1: Core Validation ⚡ **HIGH PRIORITY**
1. **Template syntax validation** (Jinja2, HTML, CSS)
2. **Save guardrails** (prevent saving invalid templates)
3. **Basic backup system** (create backup on save)

### Phase 2: Editor Interface 🎯 **MEDIUM PRIORITY**
1. **Monaco Editor integration** (code editing interface)
2. **Live preview panel** (real-time template rendering)
3. **Validation UI** (error display and guidance)

### Phase 3: Version Management 📅 **LOWER PRIORITY**
1. **Version history UI** (list previous versions)
2. **Rollback functionality** (restore previous versions)
3. **Diff viewer** (compare template versions)

This WYSIWYG editor will provide a professional template editing experience while maintaining the integrity and reliability of the template system through comprehensive validation and automatic backup functionality.