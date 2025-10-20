# Test-Driven Development (TDD) Workflow Guide

**Project**: Cloud Stack Generator
**Created**: 2025-09-23
**Status**: ACTIVE - All new development must follow this workflow

## 🎯 Mission Statement

All future development in this project **MUST** follow Test-Driven Development (TDD) practices. This ensures:

- **Quality First**: Bugs are caught before they reach QA
- **Design Clarity**: Interface contracts are established before implementation
- **Refactoring Safety**: Changes can be made confidently with test coverage
- **Documentation**: Tests serve as living documentation of expected behavior

## 📋 TDD Workflow Process

### Phase 1: Red (Write Failing Test)
1. **Identify the requirement** from user story or bug report
2. **Write the smallest possible failing test** that describes the desired behavior
3. **Run the test** - it MUST fail (if it passes, the test is wrong)
4. **Commit the failing test** with message: `test: add failing test for [feature]`

### Phase 2: Green (Make It Pass)
1. **Write the minimal code** to make the test pass
2. **Don't worry about code quality** - just make it work
3. **Run the test** - it MUST pass
4. **Run all tests** - ensure no regression
5. **Commit the working code** with message: `feat: implement [feature] to pass test`

### Phase 3: Refactor (Clean Up)
1. **Improve the code quality** without changing behavior
2. **Run tests continuously** to ensure no breaking changes
3. **Apply SOLID principles, DRY, etc.**
4. **Commit refactoring** with message: `refactor: improve [component] implementation`

## 🏗️ Test Structure Requirements

### Test File Organization
```
tests/
├── unit/                 # Unit tests (isolated components)
├── integration/         # Integration tests (component interactions)
├── system/             # End-to-end system tests
├── fixtures/           # Test data and mock objects
└── conftest.py         # Shared pytest configuration
```

### Test Naming Conventions
- **Test files**: `test_[module_name].py`
- **Test classes**: `Test[ComponentName]`
- **Test methods**: `test_[action]_[expected_result]_[condition]`

**Examples**:
- `test_save_template_creates_file_when_valid_data()`
- `test_save_template_raises_error_when_invalid_path()`
- `test_load_template_returns_metadata_when_file_exists()`

### Required Test Categories

#### 1. **Happy Path Tests**
```python
def test_save_template_success_with_valid_data(self):
    """Test successful template saving with all required data"""
    # Given: Valid template data
    # When: Save template is called
    # Then: Template file is created and metadata is stored
```

#### 2. **Error Condition Tests**
```python
def test_save_template_raises_validation_error_when_missing_name(self):
    """Test that save fails appropriately when template name is missing"""
    # Given: Template data without name
    # When: Save template is called
    # Then: ValidationError is raised with specific message
```

#### 3. **Edge Case Tests**
```python
def test_save_template_handles_special_characters_in_filename(self):
    """Test template saving with special characters in name"""
    # Given: Template name with special characters
    # When: Save template is called
    # Then: Filename is properly sanitized and template is saved
```

#### 4. **Integration Tests**
```python
def test_template_editor_save_workflow_end_to_end(self):
    """Test complete template editing and saving workflow"""
    # Given: Template editor is opened
    # When: User creates, edits, and saves a template
    # Then: Template is available in template manager
```

## 🛠️ Enhanced Error Handling Integration

All new code MUST use the enhanced error handling system:

```python
from utils import handle_errors, get_error_handler, safe_operation

# Method decorator for automatic error logging
@handle_errors(component="TemplateManager", user_action="Saving template")
def save_template(self, template_data):
    # Implementation here
    pass

# Context manager for safe operations
def risky_operation(self):
    with safe_operation("Loading template", "TemplateManager", "Opening template file"):
        # Risky file operation
        pass
```

## 📝 Test Templates

### Unit Test Template
```python
"""
Unit tests for [ComponentName]
Path: tests/unit/test_[module_name].py

Tests [component] functionality in isolation with mocked dependencies.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# Import component under test
from core.path.to.component import ComponentName

# Import enhanced error handling for testing
from utils import get_error_handler


class TestComponentName:
    """Test [ComponentName] class"""

    @pytest.fixture
    def component(self):
        """Create component instance for testing"""
        return ComponentName()

    @pytest.fixture
    def mock_dependencies(self):
        """Mock external dependencies"""
        with patch('component.external_dependency') as mock_dep:
            yield mock_dep

    def test_method_success_with_valid_input(self, component):
        """Test [method] succeeds with valid input"""
        # Given
        valid_input = "test_data"
        expected_result = "expected_output"

        # When
        result = component.method(valid_input)

        # Then
        assert result == expected_result

    def test_method_raises_error_with_invalid_input(self, component):
        """Test [method] raises appropriate error with invalid input"""
        # Given
        invalid_input = None

        # When/Then
        with pytest.raises(ValueError, match="Input cannot be None"):
            component.method(invalid_input)

    def test_method_logs_error_when_exception_occurs(self, component):
        """Test that errors are properly logged"""
        # Given
        error_handler = get_error_handler()
        initial_error_count = error_handler.get_error_statistics()['session_errors']

        # When
        try:
            component.method("invalid_input_that_causes_error")
        except Exception:
            pass  # Expected

        # Then
        final_error_count = error_handler.get_error_statistics()['session_errors']
        assert final_error_count > initial_error_count
```

### Integration Test Template
```python
"""
Integration tests for [Feature/Workflow]
Path: tests/integration/test_[feature_name].py

Tests interaction between multiple components in realistic scenarios.
"""

import pytest
import tempfile
from pathlib import Path

# Import components that need to work together
from core.component_a import ComponentA
from core.component_b import ComponentB


class TestFeatureWorkflow:
    """Test [feature] workflow integration"""

    @pytest.fixture
    def temp_directory(self):
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def integrated_system(self, temp_directory):
        """Set up integrated system for testing"""
        component_a = ComponentA(temp_directory)
        component_b = ComponentB(component_a)
        return {"a": component_a, "b": component_b}

    def test_complete_workflow_success(self, integrated_system):
        """Test complete [feature] workflow succeeds"""
        # Given
        system = integrated_system
        input_data = {"key": "value"}

        # When
        result = system["b"].process_workflow(input_data)

        # Then
        assert result.success is True
        assert system["a"].get_processed_count() == 1
```

## 🚨 Quality Gates

Before any code can be committed, ALL of the following must pass:

### 1. **Test Requirements**
```bash
# All tests must pass
pytest tests/ -v

# Coverage must be >= 80%
pytest tests/ --cov=src --cov-report=term-missing --cov-fail-under=80
```

### 2. **Code Quality**
```bash
# Linting must pass
ruff check src/

# Type checking must pass
mypy src/

# Code formatting must be consistent
black src/
```

### 3. **Error Logging Verification**
- All exceptions must be logged using enhanced error handler
- No bare `except:` clauses allowed
- All UI errors must use `log_ui_error()` function

## 📊 TDD Metrics & Success Criteria

### Tracked Metrics
- **Test Coverage**: Target >= 80% line coverage
- **Test-to-Code Ratio**: Target >= 1:2 (1 line of test for every 2 lines of code)
- **Bug Escape Rate**: Target < 5% of bugs reach QA
- **Refactoring Safety**: All refactoring accompanied by existing test suite

### Success Indicators
- ✅ Zero `TemplateVariant` or similar import errors
- ✅ All exceptions logged to `logs/error_log.txt`
- ✅ UI errors display user-friendly messages AND log technical details
- ✅ New features have tests written BEFORE implementation
- ✅ Test suite runs in < 30 seconds for rapid feedback

## 🎯 Next Steps for Current Codebase

### Priority 1: Template Editor System Tests
1. **Create failing tests** for template save functionality
2. **Mock file system operations** to avoid test pollution
3. **Test error scenarios** including permission errors, disk full, etc.
4. **Integration tests** for template editor → template manager workflow

### Priority 2: Error Handling Refactor
1. **Replace all bare `except:` clauses** with specific exception handling
2. **Add error logging** to all exception handlers
3. **Create tests** for error handling paths
4. **Verify error logs** are written to file system

### Priority 3: Test Infrastructure
1. **Set up pytest configuration** with coverage reporting
2. **Create mock factories** for common test objects
3. **Add test fixtures** for database/file system operations
4. **Configure CI/CD** to run tests automatically

## 📚 Resources & References

- **PyTest Documentation**: https://docs.pytest.org/
- **Mock Documentation**: https://docs.python.org/3/library/unittest.mock.html
- **TDD Best Practices**: Martin Fowler's "Test-Driven Development" principles
- **Project Error Handler**: `src/utils/enhanced_error_handler.py`

---

**Remember**: If you don't have a test for it, it doesn't work. If it breaks in QA, the test was missing or wrong. Fix the test FIRST, then fix the code.

**TDD Mantra**: 🔴 Red → 🟢 Green → 🔵 Refactor → Repeat