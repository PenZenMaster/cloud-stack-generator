# Codebase Structure Documentation

**Last Updated**: 2025-08-19  
**Version**: Post-Cleanup 2.0

## Project Organization

### Core Application (`src/`)
```
src/
├── core/                    # Core business logic
│   ├── config/             # Configuration parsing and models
│   ├── data/               # Data management (CSV, etc.)
│   ├── generators/         # Content generation (HTML, CSS, etc.)
│   ├── security/           # Security utilities
│   └── utils/              # Core utilities
├── ui/                     # User interface components
│   ├── components/         # Base UI components (tabs, etc.)
│   ├── content_tabs/       # Content-specific tabs
│   ├── dialogs/           # Dialog windows
│   ├── layouts/           # Layout utilities
│   └── widgets/           # Custom widgets
└── templates/             # HTML templates
    ├── base/              # Base templates
    ├── pages/             # Page templates
    └── components/        # Component templates
```

### Testing (`tests/`)
```
tests/
├── unit/                  # Unit tests for individual components
├── integration/           # Integration tests
└── fixtures/              # Test data and fixtures
```

### Configuration (`config/`)
```
config/
├── clients/               # Client-specific configurations
├── products/              # Product data files
└── website/               # Website configurations
```

### Documentation (`docs/`)
```
docs/
├── archive/               # Archived documentation
│   ├── checkpoints/       # Historical checkpoints
│   └── README.md          # Archive index
├── checkpoints/           # Current checkpoint storage
├── GBP-Data-Flow-Documentation.md
├── project-backlog.yaml
└── ProjectStatus.md
```

### External References (`external_code/`)
```
external_code/
├── product-import-with-schema/  # External schema import tools
└── README.md                    # External code documentation
```

### Output (`output/`)
```
output/
├── clients/               # Generated client websites
└── test_homepage.html     # Test outputs
```

## Cleanup Summary

### Removed Files
- **Root-level test files**: 13 obsolete test_*.py files
- **Debug files**: simple_test.py, debug_enhanced_cities_tab.py
- **Backup files**: *.bak files
- **Manual tests**: tests/manual_test_*.py, tests/simple_*.py
- **Test output**: Old test_output/ subdirectories

### Archived Files
- **Historical checkpoints**: 6 Sprint 2 checkpoint files moved to docs/archive/
- **Debug output**: Cleaned debug_output/ directory

### Active Files
- **Current checkpoint**: CheckPoint-S2W3D18-EOD-2025-08-18.md
- **Regression test**: test_gbp_regression_prevention.py
- **Organized tests**: tests/ directory structure maintained

## Development Guidelines

### File Organization
- **New features**: Add to appropriate src/ subdirectory
- **Tests**: Use tests/unit/ or tests/integration/
- **Documentation**: Add to docs/ with proper categorization
- **Temporary files**: Use output/ or debug_output/ (will be cleaned)

### Archive Policy
- Historical checkpoints → docs/archive/checkpoints/
- Obsolete code → Remove or document in archive
- Test files → Organize in tests/ structure only

## Clean Codebase Benefits

1. **Faster development**: Less clutter during searches
2. **Clear testing**: Only organized tests remain
3. **Better navigation**: Logical file organization
4. **Easier refactoring**: Clean slate for BACK-003 CSS work
5. **Maintainability**: Clear separation of concerns

Total files removed: ~20 files, ~1,700 lines of obsolete code