# Website Generator Orchestration Refactoring Plan

**Date**: 2025-10-20
**Current File**: `src/core/website_generator.py` (1961 lines)
**Target**: Split into 4 focused modules (<500 lines each)
**Branch**: `create-orchestration`

---

## Current Structure Analysis

### WebsiteGenerator Class Methods (18 methods total)

#### 1. Orchestration & Coordination (Main Entry Points)
- `__init__(self, use_ai: bool = True)` - Initialization
- `generate(self, config, output_dir) -> GenerationResult` - Main orchestration method

#### 2. Page Generation (High-Level)
- `_generate_index_page(self, config) -> str` - Home page generation
- `_generate_city_page(self, config, page_config) -> str` - Legacy city page
- `_generate_enhanced_city_page(self, city_page, config) -> str` - Enhanced city page

#### 3. Content Generation (Core Business Logic)
- `_create_html_template(self, config, ...)` - Main HTML structure builder
- `_create_home_content(self, config) -> str` - Legacy home content
- `_create_enhanced_home_content(self, config) -> str` - Enhanced home content
- `_create_city_content(self, config, city) -> str` - City-specific content
- `_create_enhanced_city_html(self, city_page, config) -> str` - Enhanced city HTML

#### 4. Content Components (Reusable Pieces)
- `_build_navigation(self, config, current_city) -> str` - Navigation menu
- `_create_footer_content(self, config, ...) -> str` - Footer generation
- `_format_content_body(self, content) -> str` - Content formatting

#### 5. Asset Generation
- `_generate_css_file(self, config) -> str` - CSS generation
- `_create_css_template(self, config) -> str` - CSS template (large)

#### 6. Utility Functions
- `_create_slug(self, city_name) -> str` - URL slug creation
- `_generate_city_slug(self, city_name) -> str` - City slug generation
- `_modify_iframe_size(self, iframe_code, width, height) -> str` - iframe manipulation
- `_get_display_phone(self, phone) -> str` - Phone number formatting

---

## Refactoring Strategy

### Module 1: `website_orchestrator.py` (400-500 lines)
**Purpose**: High-level coordination and workflow management

**Responsibilities**:
- Main `generate()` workflow orchestration
- Directory structure setup
- File generation coordination
- Error handling and result aggregation
- Dependency injection setup

**Classes**:
- `WebsiteOrchestrator` - Main orchestrator
- `GenerationResult` - Move from website_generator.py
- `GenerationError` - Move from website_generator.py

**Key Methods**:
- `__init__(use_ai, output_dir)`
- `generate(config) -> GenerationResult`
- `_setup_directories()`
- `_orchestrate_generation(config)`
- `_collect_results()`

---

### Module 2: `content_coordinator.py` (400-500 lines)
**Purpose**: Content generation coordination and delegation

**Responsibilities**:
- Coordinate page content generation
- Manage AI content service integration
- Delegate to specialized content generators
- Handle content caching
- Coordinate between legacy and enhanced content

**Classes**:
- `ContentCoordinator` - Main coordinator

**Key Methods**:
- `__init__(ai_service, content_cache)`
- `generate_home_page(config) -> str`
- `generate_city_page(city_page, config) -> str`
- `_coordinate_home_content(config)`
- `_coordinate_city_content(city_page, config)`
- `_use_legacy_or_enhanced(config)`

**Dependencies** (Already Extracted):
- `HomeContentGenerator` (from content/home_content_generator.py)
- `CityContentGenerator` (from content/city_content_generator.py)
- `NavigationBuilder` (from content/navigation_builder.py)
- `FooterGenerator` (from content/footer_generator.py)

---

### Module 3: `build_pipeline.py` (300-400 lines)
**Purpose**: Build process management and file operations

**Responsibilities**:
- Manage build phases (setup → generate → finalize)
- Handle file I/O operations
- Manage asset generation coordination
- Directory structure creation
- Build validation

**Classes**:
- `BuildPipeline` - Main pipeline manager
- `BuildPhase` - Enum for build phases
- `BuildContext` - Build state container

**Key Methods**:
- `__init__(output_dir)`
- `setup_build() -> BuildContext`
- `generate_pages(context, pages) -> List[str]`
- `generate_assets(context, config) -> List[str]`
- `finalize_build(context) -> BuildResult`
- `_write_file(path, content)`
- `_create_directory_structure()`

---

### Module 4: `website_generator.py` (REFACTORED - 150-200 lines)
**Purpose**: Public API and backward compatibility facade

**Responsibilities**:
- Maintain public API for backward compatibility
- Simple delegation to orchestrator
- Legacy method support (deprecated but functional)

**Classes**:
- `WebsiteGenerator` - Facade for orchestrator

**Key Methods**:
- `__init__(use_ai)`
- `generate(config, output_dir) -> GenerationResult`
- (All legacy public methods delegate to orchestrator)

---

## Module 5: `asset_manager.py` (ALREADY EXISTS)
**Status**: ✅ Already extracted in previous refactoring

**Current Location**: `src/core/generators/asset_manager.py`

**Purpose**: Asset processing and management

**Responsibilities**:
- CSS generation
- Image processing
- Asset copying and optimization
- Static file management

---

## Dependencies Map

```
website_generator.py (facade)
  └─> website_orchestrator.py
       ├─> content_coordinator.py
       │    ├─> home_content_generator.py ✅
       │    ├─> city_content_generator.py ✅
       │    ├─> navigation_builder.py ✅
       │    └─> footer_generator.py ✅
       ├─> build_pipeline.py
       │    └─> asset_manager.py ✅
       └─> html_generator.py (existing)
```

---

## Implementation Steps

### Phase 1: Extract Build Pipeline (Day 1)
1. Create `build_pipeline.py` module
2. Extract file I/O and directory management
3. Create `BuildContext` and `BuildPhase` classes
4. Write unit tests for build pipeline
5. Validate no regression

### Phase 2: Extract Content Coordinator (Day 2)
1. Create `content_coordinator.py` module
2. Extract content generation coordination logic
3. Integrate with existing content generators
4. Write unit tests for content coordinator
5. Validate no regression

### Phase 3: Extract Website Orchestrator (Day 3)
1. Create `website_orchestrator.py` module
2. Move main orchestration logic
3. Integrate with content_coordinator and build_pipeline
4. Write unit tests for orchestrator
5. Validate no regression

### Phase 4: Refactor Website Generator Facade (Day 4)
1. Refactor `website_generator.py` to use orchestrator
2. Maintain backward compatibility
3. Update all imports across codebase
4. Run full test suite
5. Validate no regression

### Phase 5: Integration Testing (Day 5)
1. Run comprehensive integration tests
2. Test all legacy code paths
3. Test all new code paths
4. Performance testing
5. Documentation updates

---

## Success Criteria

- ✅ All modules <500 lines
- ✅ Clear separation of concerns
- ✅ No regression in functionality
- ✅ Test coverage maintained (80%+)
- ✅ All existing tests pass
- ✅ Performance not degraded
- ✅ Backward compatibility maintained

---

## Risk Mitigation

### Risk 1: Breaking Changes
**Mitigation**: Maintain `WebsiteGenerator` as facade, all existing code continues to work

### Risk 2: Test Coverage Gaps
**Mitigation**: Write tests for each new module before refactoring

### Risk 3: Hidden Dependencies
**Mitigation**: Careful analysis of method dependencies before extraction

### Risk 4: Performance Degradation
**Mitigation**: Benchmark before/after, optimize if needed

---

## Timeline

- **Day 1**: Build Pipeline extraction
- **Day 2**: Content Coordinator extraction
- **Day 3**: Website Orchestrator extraction
- **Day 4**: Facade refactoring and integration
- **Day 5**: Testing and validation

**Total**: 5 days for complete refactoring

---

## Next Steps

1. ✅ Create refactoring plan (this document)
2. Create `build_pipeline.py` module
3. Begin Phase 1 implementation
