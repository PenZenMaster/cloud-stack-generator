# Critical Module Refactoring Plan
**Version**: 1.00
**Created**: 2025-10-17
**Status**: Planning Phase
**Duration**: 3 weeks (2 weeks website_generator + 1 week enhanced_main_window)

---

## Executive Summary

Two critical modules must be refactored before template system integration can proceed. These modules exceed recommended size limits and have multiple responsibilities that should be separated.

**Critical Blockers**:
1. **`website_generator.py`** (1947 lines) - Orchestrates generation, content creation, and output
2. **`enhanced_main_window.py`** (1546 lines) - Manages UI, menus, tabs, and state

**Goal**: Refactor into focused, maintainable modules (300-800 lines each) with clear separation of concerns.

---

## Module 1: website_generator.py Refactoring

### Current State Analysis

**File**: `src/core/website_generator.py`
**Lines**: 1947
**Classes**: 3 (GenerationError, GenerationResult, WebsiteGenerator)
**Methods**: 18 in WebsiteGenerator class

### Responsibilities (Too Many!)
1. ✅ Generation orchestration (main workflow)
2. ✅ Index page generation
3. ✅ City page generation (enhanced and legacy)
4. ✅ CSS file generation
5. ✅ HTML template creation (massive method - lines 289-413)
6. ✅ Navigation building
7. ✅ Content creation (home, city, footer)
8. ✅ Slug generation and string formatting
9. ✅ Phone number formatting
10. ✅ iFrame manipulation

### Method Size Analysis
**Large methods requiring attention**:
- `_create_html_template()` - Lines 289-413 (124 lines) - HTML scaffolding
- `_create_home_content()` - Lines 459-572 (113 lines) - Home page content
- `_create_enhanced_home_content()` - Lines 573-809 (236 lines) ⚠️ **HUGE**
- `_create_city_content()` - Lines 810-926 (116 lines) - City page content
- `_create_footer_content()` - Lines 927-1019 (92 lines) - Footer generation
- `_create_css_template()` - Lines 1051-1947 (896 lines) ⚠️ **MASSIVE**

### Proposed Refactoring Structure

```
src/core/orchestration/
├── __init__.py
├── website_orchestrator.py       # Main generation coordination (400-500 lines)
├── content_coordinator.py        # Content generation routing (300-400 lines)
├── asset_manager.py              # Asset processing (CSS, JS, images) (300-400 lines)
└── build_pipeline.py             # Build process management (300-400 lines)

src/core/generators/
├── html_generator.py             # (existing - keep)
├── css_generator.py              # (existing - may need split)
├── city_page_generator.py        # (existing - keep)
└── content/
    ├── __init__.py
    ├── home_content_generator.py    # Home page content (300-400 lines)
    ├── city_content_generator.py   # City page content (300-400 lines)
    ├── footer_generator.py         # Footer content (200-300 lines)
    └── navigation_builder.py       # Navigation HTML (200-300 lines)

src/core/utils/
├── string_utils.py               # Slug generation, phone formatting (100-200 lines)
└── html_utils.py                 # HTML manipulation utilities (100-200 lines)
```

### Refactoring Steps (Week 1-2)

#### Week 1: Extract Content Generators

**Day 1-2: Extract Content Generators**
1. Create `src/core/generators/content/` directory
2. Extract `home_content_generator.py`:
   - Move `_create_home_content()`
   - Move `_create_enhanced_home_content()`
   - Add proper imports and dependencies
3. Extract `city_content_generator.py`:
   - Move `_create_city_content()`
   - Move `_create_enhanced_city_html()`
4. Extract `footer_generator.py`:
   - Move `_create_footer_content()`
   - Move `_modify_iframe_size()`
5. Extract `navigation_builder.py`:
   - Move `_build_navigation()`

**Day 3: Extract Utilities**
6. Create `src/core/utils/string_utils.py`:
   - Move `_create_slug()`, `_generate_city_slug()`
   - Move `_get_display_phone()`
   - Move `_format_content_body()`
7. Create `src/core/utils/html_utils.py`:
   - Move HTML manipulation helpers
   - Move iframe utilities

**Day 4-5: Extract Asset Manager**
8. Create `src/core/orchestration/asset_manager.py`:
   - Move `_generate_css_file()`
   - Move `_create_css_template()` (896 lines - may delegate to css_generator)
   - Add asset coordination logic (CSS, JS, images)
   - Handle directory creation

**Week 2: Orchestration Layer**

**Day 1-2: Create Build Pipeline**
9. Create `src/core/orchestration/build_pipeline.py`:
   - File writing operations
   - Directory structure creation
   - File path management
   - GenerationResult aggregation

**Day 3: Create Content Coordinator**
10. Create `src/core/orchestration/content_coordinator.py`:
    - Route to appropriate content generators
    - Coordinate index page generation
    - Coordinate city page generation
    - Delegate to content generators

**Day 4: Create Website Orchestrator**
11. Create `src/core/orchestration/website_orchestrator.py`:
    - Main `generate()` method
    - High-level workflow coordination
    - Call content_coordinator, asset_manager, build_pipeline
    - Error handling and result aggregation
    - Keep GenerationError and GenerationResult classes

**Day 5: Integration and Testing**
12. Update imports in existing code
13. Update tests to use new structure
14. Validate no regression - all generation tests pass
15. Update documentation

### Module Responsibilities (After Refactoring)

**website_orchestrator.py** (400-500 lines):
- Main `generate(config, output_dir)` entry point
- High-level workflow coordination
- Error handling and result collection
- Progress callbacks (if needed)

**content_coordinator.py** (300-400 lines):
- Route to appropriate page generators
- Coordinate homepage generation
- Coordinate city page generation
- Template selection integration (future)
- Content validation

**asset_manager.py** (300-400 lines):
- CSS file generation coordination
- JavaScript file management
- Image processing and optimization
- Asset directory structure
- Cache-control headers

**build_pipeline.py** (300-400 lines):
- File writing operations
- Directory structure creation
- File path resolution
- Output validation
- Cleanup operations

**Content generators** (200-400 lines each):
- `home_content_generator.py` - Home page HTML
- `city_content_generator.py` - City page HTML
- `footer_generator.py` - Footer HTML
- `navigation_builder.py` - Navigation HTML

**Utilities** (100-200 lines each):
- `string_utils.py` - Text formatting, slug generation
- `html_utils.py` - HTML manipulation helpers

---

## Module 2: enhanced_main_window.py Refactoring

### Current State Analysis

**File**: `src/ui/enhanced_main_window.py`
**Lines**: 1546
**Classes**: 1 (EnhancedMainWindow)
**Methods**: ~35+ methods

### Responsibilities (Too Many!)
1. ✅ Main window initialization
2. ✅ UI layout and widgets
3. ✅ Menu bar creation and management
4. ✅ Toolbar creation and management
5. ✅ Tab management (5 tabs: business, contact, branding, products, services)
6. ✅ Status bar updates
7. ✅ Configuration save/load
8. ✅ Validation orchestration
9. ✅ Website generation triggering
10. ✅ Preview window management
11. ✅ Window state persistence
12. ✅ Event handling
13. ✅ Signal/slot connections

### Proposed Refactoring Structure

```
src/ui/main_window/
├── __init__.py
├── main_window.py               # Core window structure (400-500 lines)
├── menu_manager.py              # Menu and toolbar (300-400 lines)
├── tab_manager.py               # Tab coordination (300-400 lines)
├── status_manager.py            # Status bar and notifications (200-300 lines)
├── window_state_manager.py     # Window state persistence (200-300 lines)
└── validation_coordinator.py   # Validation orchestration (200-300 lines)

src/ui/dialogs/
├── configuration_dialog.py      # Save/load config UI (if not exists)
└── preview_window.py            # Preview window (if not exists)
```

### Refactoring Steps (Week 3)

#### Day 1-2: Extract Managers

**Day 1: Extract Menu and Status Managers**
1. Create `src/ui/main_window/` directory
2. Extract `menu_manager.py`:
   - Move all menu creation methods
   - Move toolbar creation methods
   - Move menu action handlers
   - Menu enable/disable logic
3. Extract `status_manager.py`:
   - Move status bar creation
   - Move status message methods
   - Move progress indicator logic
   - Move notifications

**Day 2: Extract Tab and Validation Managers**
4. Extract `tab_manager.py`:
   - Move tab widget creation
   - Move tab instance management
   - Move tab switching logic
   - Tab enable/disable logic
5. Extract `validation_coordinator.py`:
   - Move `validate_all_tabs()` method
   - Move validation result aggregation
   - Move validation UI feedback
   - Error display coordination

**Day 3: Extract Window State Manager**
6. Create `window_state_manager.py`:
   - Move window geometry persistence
   - Move splitter state persistence
   - Move last directory tracking
   - Move settings save/load

**Day 4: Create Main Window**
7. Create `main_window.py`:
   - Main window initialization
   - Layout composition (use managers)
   - High-level event handling
   - Manager coordination
   - Signal/slot connections between managers

**Day 5: Integration and Testing**
8. Update imports in application entry point
9. Update tests to use new structure
10. Validate all UI functionality works
11. Test menu actions, tab switching, validation
12. Update documentation

### Module Responsibilities (After Refactoring)

**main_window.py** (400-500 lines):
- QMainWindow initialization
- Layout composition (central widget, dock widgets)
- Manager instantiation and coordination
- High-level event handling
- Application lifecycle (show, close, cleanup)

**menu_manager.py** (300-400 lines):
- Menu bar creation (File, Edit, View, Help)
- Toolbar creation
- Action creation and connection
- Menu state management (enable/disable)
- Keyboard shortcuts

**tab_manager.py** (300-400 lines):
- QTabWidget creation and setup
- Tab instance creation (BusinessTab, ContactTab, etc.)
- Tab switching logic
- Tab validation triggers
- Tab data synchronization

**status_manager.py** (200-300 lines):
- Status bar creation
- Status message display
- Progress indicators
- Notification system
- Temporary message timers

**window_state_manager.py** (200-300 lines):
- QSettings integration
- Window geometry save/restore
- Splitter positions save/restore
- Last used directories
- User preferences

**validation_coordinator.py** (200-300 lines):
- Validation orchestration across tabs
- Result aggregation
- Error message formatting
- UI feedback (dialogs, status messages)
- Validation caching

---

## Integration with Template System

### Why This Refactoring Enables Template Work

**website_generator.py refactoring**:
1. **content_coordinator.py** will gain template selection logic
2. **asset_manager.py** can handle template assets (CSS, JS)
3. **build_pipeline.py** provides clean file writing interface
4. Template rendering integrates cleanly with content generators

**enhanced_main_window.py refactoring**:
1. **menu_manager.py** can add "Templates" menu easily
2. **tab_manager.py** can add template selection tab if needed
3. Clean separation allows template dialog integration
4. Smaller modules = easier to understand template integration points

### Template System Integration Points (Post-Refactoring)

**In content_coordinator.py**:
```python
def _generate_index_page(self, config: ClientConfig) -> str:
    # Get selected template from config
    template_id = config.template_config.selected_template_id

    # Load template via TemplateManager
    template = self.template_manager.load_template(template_id)

    # Render with content from content generators
    html_content = template.render(
        home_content=self.home_generator.generate(config),
        navigation=self.nav_builder.build(config),
        footer=self.footer_generator.generate(config)
    )

    return html_content
```

**In menu_manager.py**:
```python
def _create_menus(self):
    # ... existing menus ...

    # Add Templates menu
    templates_menu = self.menuBar().addMenu("&Templates")
    templates_menu.addAction("Select Template...", self._open_template_selector)
    templates_menu.addAction("Edit Template...", self._open_template_editor)
    templates_menu.addAction("Import Template...", self._import_template)
    templates_menu.addAction("Export Template...", self._export_template)
```

---

## Testing Strategy

### Pre-Refactoring
1. ✅ Run full test suite - capture baseline
2. ✅ Document current test coverage
3. ✅ Identify integration tests vs unit tests
4. ✅ Create snapshot of current behavior

### During Refactoring
1. ✅ Create unit tests for each new module **before** extracting
2. ✅ Test-driven refactoring:
   - Write test for new module
   - Extract code to new module
   - Run tests - must pass
   - Refactor/clean up
   - Tests still pass
3. ✅ Run integration tests after each major extraction
4. ✅ Validate no behavioral changes

### Post-Refactoring
1. ✅ Full test suite must pass
2. ✅ Coverage must be maintained or improved
3. ✅ Manual QA of all UI functionality
4. ✅ Performance benchmarks (should be same or better)

---

## Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking existing functionality | High | Medium | TDD approach, comprehensive tests before refactoring |
| Import circular dependencies | Medium | Medium | Careful dependency design, use interfaces |
| Test coverage degradation | Medium | Low | Require tests for each new module |
| Performance regression | Low | Low | Keep same algorithms, benchmark before/after |

### Schedule Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Refactoring takes >3 weeks | High | Medium | Timebox: accept incremental progress, defer less critical splits |
| Broken builds during refactoring | Medium | Medium | Use feature branch, atomic commits |
| Team confusion during transition | Medium | Low | Clear documentation, pair programming |

---

## Success Criteria

### Code Quality Metrics
- ✅ No module >800 lines
- ✅ Clear single responsibility per module
- ✅ All modules have 80%+ test coverage
- ✅ No circular dependencies
- ✅ Passes ruff, black, mypy without warnings

### Functional Metrics
- ✅ All existing tests pass
- ✅ No behavioral changes (website generation output identical)
- ✅ UI functionality unchanged
- ✅ Performance same or better

### Documentation Metrics
- ✅ Each new module has clear docstring
- ✅ Module responsibilities documented
- ✅ Integration points documented
- ✅ Migration guide for developers

---

## Timeline

### Week 1: website_generator.py Content Extraction
- Day 1-2: Extract content generators (home, city, footer, navigation)
- Day 3: Extract utilities (string_utils, html_utils)
- Day 4-5: Extract asset_manager
- **Deliverable**: 6 new modules, tests passing

### Week 2: website_generator.py Orchestration
- Day 1-2: Create build_pipeline
- Day 3: Create content_coordinator
- Day 4: Create website_orchestrator (main entry point)
- Day 5: Integration testing, documentation
- **Deliverable**: website_generator.py refactored, all tests passing

### Week 3: enhanced_main_window.py Refactoring
- Day 1: Extract menu_manager and status_manager
- Day 2: Extract tab_manager and validation_coordinator
- Day 3: Extract window_state_manager
- Day 4: Create new main_window (manager composition)
- Day 5: Integration testing, documentation
- **Deliverable**: enhanced_main_window.py refactored, all tests passing

---

## Rollback Plan

### If Refactoring Fails
1. **Immediate**: Revert to last known good commit on main branch
2. **Short-term**: Continue with partial refactoring (keep what works)
3. **Long-term**: Re-plan with smaller scope, longer timeline

### Feature Branch Strategy
- Work on `refactor/website-generator` branch
- Merge to `html-templates` only when tests pass
- Keep daily backups/checkpoints
- Can abandon branch if needed without impacting main

---

## Next Steps

### Immediate Actions (This Session)
1. ✅ Review and approve refactoring plan
2. Create `refactor/website-generator` branch
3. Run baseline test suite
4. Create first new module: `home_content_generator.py`

### Before Starting Refactoring
1. Ensure comprehensive test coverage exists
2. Document current behavior (screenshots, outputs)
3. Set up performance benchmarks
4. Communicate plan to team/stakeholders

---

## Dependencies

### Blocked By
- None (can start immediately after approval)

### Blocks
- Template System Phase 2 (Selection UI)
- Template System Phase 4 (WYSIWYG Editor)
- Any other features requiring website generation changes

### Can Proceed in Parallel
- Template System Phase 1 (Metadata files) ✅
- Test coverage improvements ✅
- Documentation updates ✅

---

**Document Status**: Complete - Ready for Implementation
**Next Action**: Review with stakeholder, create refactor branch, begin Week 1 Day 1
**Estimated Completion**: 3 weeks from start date
