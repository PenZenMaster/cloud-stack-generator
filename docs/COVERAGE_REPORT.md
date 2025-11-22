# Code Coverage Report

**Generated**: 2025-11-21
**Overall Coverage**: 35.47%
**Target**: 60-80%
**Status**: ⚠️ Below Target

---

## Summary

| Metric | Value |
|--------|-------|
| Total Statements | 18,230 |
| Covered Statements | 6,467 |
| Missed Statements | 11,763 |
| **Coverage Percentage** | **35.47%** |

## Test Execution

- **Passed**: 565 tests
- **Failed**: 120 tests (pre-existing)
- **Skipped**: 2 tests
- **Duration**: 3 minutes

---

## Coverage by Category

### ✅ Well-Covered Modules (>60%)

| Module | Coverage | Status |
|--------|----------|--------|
| `src/core/aws/credentials.py` | 76.81% | ✅ Good |
| `src/core/aws/s3_manager.py` | 74.43% | ✅ Good |
| `src/core/deployment/providers/gcs_provider.py` | 89.66% | ✅ Excellent |
| `src/core/config/models.py` | 67.06% | ✅ Good |
| `src/utils/enhanced_error_handler.py` | 64.02% | ✅ Good |
| `src/utils/error_classification.py` | 66.10% | ✅ Good |

### ⚠️ Partial Coverage (30-60%)

| Module | Coverage | Priority |
|--------|----------|----------|
| `src/core/generators/html_generator.py` | 47.87% | Medium |
| `src/ui/dialogs/simple_template_editor.py` | 59.83% | Medium |
| `src/ui/dialogs/template_editor_dialog.py` | 56.32% | Medium |
| `src/utils/error_logger.py` | 53.12% | Medium |

### ❌ Low/No Coverage (0-30%)

**Critical UI Components** (0% coverage):
- `src/ui/enhanced_main_window.py` - 0%
- `src/ui/main_window.py` - 0%
- `src/ui/content_tabs/enhanced_cities_tab.py` - 0%
- `src/ui/content_tabs/products_tab.py` - 0%
- `src/ui/content_tabs/services_tab.py` - 0%
- `src/ui/content_tabs/faq_tab.py` - 0%
- `src/ui/components/api_keys_tab.py` - 0%
- `src/ui/components/deployment_history_tab.py` - 0%

**Core Modules** (0% coverage):
- `src/core/website_generator.py` - 0%
- `src/core/config_parser.py` - 0%
- `src/location_page_generator.py` - 0%
- `src/ui/yaml_builder.py` - 0%

---

## Recommendations

### Phase 1: Quick Wins (Reach 50%)

Target modules with existing test infrastructure:
1. **Increase html_generator.py** from 47.87% to 60%
   - Add tests for schema generation methods
   - Add tests for Wikipedia entity generation

2. **Add basic tests for website_generator.py** (currently 0%)
   - Test page generation workflow
   - Test error handling

3. **Test core utilities** (error handling already good at 64-66%)
   - Maintain current coverage levels

### Phase 2: UI Coverage (Reach 60%)

UI testing is complex but valuable:
1. **Add integration tests** for main workflows
   - Website generation flow
   - Configuration save/load
   - Deployment process

2. **Mock UI components** for isolated testing
   - Test business logic separately from PyQt6 widgets
   - Focus on data validation and state management

### Phase 3: Reach 80% (Long-term)

1. Add comprehensive UI tests
2. Test edge cases and error paths
3. Add integration tests for full workflows
4. Document untestable code (UI rendering, external APIs)

---

## Coverage Configuration

Coverage is configured via `.coveragerc`:

```ini
[run]
source = src
omit = */tests/*, */examples/*, */scripts/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if TYPE_CHECKING:
    @abstractmethod

[html]
directory = htmlcov
```

---

## Running Coverage Locally

```bash
# Run full coverage analysis
pytest tests/unit/ --cov=src --cov-report=html --cov-report=term

# Open HTML report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows

# Check specific module
pytest tests/unit/test_html_generator.py --cov=src.core.generators.html_generator --cov-report=term-missing

# Fail if below threshold
pytest tests/unit/ --cov=src --cov-fail-under=60
```

---

## Pre-Commit Integration

Coverage checks are integrated into pre-commit hooks:
- **Cloud Infrastructure**: Minimum 69% (enforced)
- **Overall Codebase**: Minimum 60% (warning only)

Pre-commit will warn but not block commits if overall coverage is below 60%, maintaining development momentum while encouraging test additions.

---

## Next Steps

1. ✅ Coverage tooling configured
2. ⏳ Add tests to reach 50% coverage (Phase 1)
3. ⏳ Run vulture analysis for dead code
4. ⏳ Clean up untested dead code
5. ⏳ Add UI integration tests (Phase 2)
6. ⏳ Reach 60% coverage milestone

---

**Last Updated**: 2025-11-21
**Report Generator**: pytest-cov 6.2.1
**Python Version**: 3.13.5
