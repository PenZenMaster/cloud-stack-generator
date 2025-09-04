# Debugging Guide
## SEO Authority Website Generator

**Version**: 1.0  
**Created**: August 18, 2025  
**Last Updated**: August 18, 2025

---

## Table of Contents
1. [Overview](#overview)
2. [Systematic Debugging Methodology](#systematic-debugging-methodology)
3. [Data Flow Tracing](#data-flow-tracing)
4. [Common Issue Patterns](#common-issue-patterns)
5. [Debug Tools & Techniques](#debug-tools--techniques)
6. [Case Study: GBP Embed Integration](#case-study-gbp-embed-integration)

---

## Overview

This guide documents the systematic debugging methodology developed during the Google Business Profile (GBP) embed integration troubleshooting session. The approach can be applied to any complex multi-layer system issue.

**Key Principle**: **Trace data through each layer systematically** rather than making assumptions about where issues occur.

---

## Systematic Debugging Methodology

### 1. **Issue Identification**
- Document the exact expected behavior
- Document the exact actual behavior
- Identify the gap between expected and actual

### 2. **System Layer Mapping**
Map out all layers the data flows through:
```
YAML File → Parser → Config Object → UI → Generator → Template → HTML Output
```

### 3. **Checkpoint Strategy**
Add debug output at **every layer transition** to identify exactly where data is lost or corrupted.

### 4. **Data Verification Points**
- **Input verification**: Is the source data correct?
- **Parsing verification**: Is the data being read correctly?
- **Object verification**: Is the data stored in objects correctly?
- **Processing verification**: Is the data being processed correctly?
- **Output verification**: Is the final output correct?

### 5. **Incremental Testing**
Test each layer independently before testing the full pipeline.

---

## Data Flow Tracing

### Configuration Data Flow
```mermaid
YAML File
    ↓ (ConfigParser.parse_yaml_file)
Config Object
    ↓ (UI loads config OR UI creates new config)
Active Config
    ↓ (HTMLGenerator._prepare_template_data)
Template Data
    ↓ (Jinja2 template rendering)
Generated HTML
```

### Key Checkpoints
1. **YAML Parsing**: `print(f"YAML data: {yaml_data}")`
2. **Config Creation**: `print(f"Config object: {config.field}")`
3. **Template Data**: `print(f"Template data: {'field' in template_data}")`
4. **Template Rendering**: `print(f"Rendered contains: {'text' in rendered}")`

---

## Common Issue Patterns

### 1. **Data Loss Between Layers**
**Symptoms**: Data exists in source but missing in output
**Cause**: One layer not passing data to the next
**Solution**: Add debug at each layer transition

### 2. **Object Attribute Mismatch**
**Symptoms**: `AttributeError` or empty values
**Cause**: Code expecting different object structure
**Solution**: Print object attributes and verify structure

### 3. **Template Condition Failures**
**Symptoms**: Template sections not rendering
**Cause**: Template conditions not met (missing data, wrong data types)
**Solution**: Debug template data structure and values

### 4. **UI vs File Configuration Conflicts**
**Symptoms**: Changes in files not reflected in generated output
**Cause**: UI creating new config instead of using loaded config
**Solution**: Ensure UI uses loaded config for generation

---

## Debug Tools & Techniques

### 1. **Strategic Print Statements**
```python
# Data structure debugging
print(f"DEBUG: Object type: {type(obj)}")
print(f"DEBUG: Object attributes: {dir(obj)}")
print(f"DEBUG: Object value: {obj}")

# Conditional debugging
print(f"DEBUG: Condition check: {condition}")
print(f"DEBUG: Field exists: {hasattr(obj, 'field')}")
print(f"DEBUG: Field value: {getattr(obj, 'field', 'NOT_FOUND')}")

# Template debugging
print(f"DEBUG: Template data keys: {list(template_data.keys())}")
print(f"DEBUG: Rendered contains text: {'search_text' in rendered}")
```

### 2. **Error Log Analysis**
- Check `logs/error_log.txt` for runtime errors
- Look for patterns in error messages
- Trace stack traces to identify failure points

### 3. **Configuration Verification**
```python
# Verify configuration loading
config = parser.parse_yaml_file(file_path)
print(f"Config loaded: {config}")
print(f"Specific field: {config.specific_field}")
```

### 4. **Template Data Inspection**
```python
# In template rendering
template_data = self._prepare_template_data(config)
print(f"Template data structure: {template_data.keys()}")
print(f"Specific data: {template_data.get('field', 'MISSING')}")
```

---

## Case Study: GBP Embed Integration

**Issue**: Google Business Profile embed not appearing in website footer despite being configured in YAML.

### Initial Symptoms
- YAML file contained correct GBP embed code
- Generated HTML missing "Visit Our Location" section
- No error messages in logs

### Debugging Process

#### Step 1: Verify Source Data
```bash
# Check YAML file
grep -A5 "google_business_profile" config/clients/salvo_metal_works_config.yaml
```
**Result**: ✅ Correct embed code in YAML

#### Step 2: Trace Parser
```python
# Added to parser.py
google_business_profile = client_data.get("google_business_profile", {})
print(f"DEBUG PARSER: google_business_profile from YAML: {google_business_profile}")
```
**Result**: ✅ Parser correctly loaded GBP data

#### Step 3: Trace Config Object
```python
# Added to parser.py after config creation
print(f"DEBUG PARSER: Created config.google_business_profile: {config.google_business_profile}")
```
**Result**: ✅ Config object correctly stored GBP data

#### Step 4: Trace Template Data
```python
# Added to html_generator.py
print(f"DEBUG: GBP in template_data: {'google_business' in template_data}")
```
**Result**: ❌ GBP data missing from template_data

#### Step 5: Identify Root Cause
**Discovery**: UI was creating new config from UI data instead of using loaded YAML config.

```python
# Found in enhanced_main_window.py
config_data = self.get_all_config_data()  # Only UI data
config = self.create_client_config(config_data)  # Missing YAML-only data
```

#### Step 6: Implement Fix
```python
# Use loaded config instead of creating new one
if hasattr(self, 'loaded_config') and self.loaded_config:
    config = self.loaded_config  # Contains full YAML data
```

### Lessons Learned
1. **Multiple configuration sources**: UI data vs file data can conflict
2. **Data persistence**: Objects created from different sources have different data
3. **Layer independence**: Each layer can work correctly in isolation but fail in integration
4. **Debug at boundaries**: Most issues occur at layer transitions

### Time Investment
- **Total debugging time**: 4.5 hours
- **Issue complexity**: High (multi-layer system interaction)
- **Resolution method**: Systematic layer-by-layer tracing

---

## Best Practices

### 1. **Proactive Debugging**
- Add debug statements during development, not just during troubleshooting
- Include data flow verification in critical paths
- Use meaningful debug messages with context

### 2. **Documentation During Debugging**
- Document each step and finding
- Note what was ruled out and why
- Record the exact solution and reasoning

### 3. **Systematic Approach**
- Don't skip layers - check each one systematically
- Verify assumptions with data
- Test fixes incrementally

### 4. **Debug Code Management**
- Mark debug code clearly for later removal
- Use consistent debug message formatting
- Document debug code locations for cleanup

---

## Debugging Checklist

**When encountering complex issues:**

- [ ] Map out the complete data flow
- [ ] Add debug output at each layer transition
- [ ] Verify source data is correct
- [ ] Check each layer processes data correctly
- [ ] Verify data reaches the final output
- [ ] Test the fix with multiple scenarios
- [ ] Document the root cause and solution
- [ ] Mark debug code for later removal

**Remember**: Complex issues rarely have obvious causes. Systematic tracing reveals the actual problem, which is often different from the apparent problem.