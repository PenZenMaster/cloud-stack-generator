# Google Business Profile (GBP) Data Flow Documentation

**Version**: 1.0.0  
**Date**: 2025-08-19  
**Purpose**: Prevent regression of GBP embed functionality

## Critical Issue History

The GBP embed code has disappeared **4 times** during development due to data flow mismatches. This documentation ensures it never happens again.

## Root Cause Analysis

**Problem**: Data structure key mismatch between UI components and configuration models
- Configuration uses: `google_business_profile` 
- Contact tab was using: `google_business` (WRONG)
- Enhanced main window was mapping to: `google_business` (WRONG)

## Data Flow Architecture

### 1. Configuration Structure (YAML)
```yaml
client:
  google_business_profile:
    embed_code: "<iframe src='...'></iframe>"
```

### 2. Data Model (src/core/config/models.py)
```python
class ClientConfig:
    google_business_profile: Dict[str, str] = field(default_factory=dict)
```

### 3. Contact Tab UI (src/ui/components/contact_tab.py)
```python
def get_config_data(self) -> Dict[str, Any]:
    return {
        "google_business_profile": google_data  # CORRECT KEY
    }

def set_config_data(self, data: Dict[str, Any]):
    if "google_business_profile" in data:  # CORRECT KEY
        embed_code = data["google_business_profile"].get("embed_code", "")
```

### 4. Enhanced Main Window (src/ui/enhanced_main_window.py)
```python
contact_data = {
    "google_business_profile": {  # CORRECT KEY
        "embed_code": getattr(config, 'google_business_profile', {}).get('embed_code', '')
    }
}
```

### 5. Website Generation (src/core/website_generator.py)
```python
if hasattr(config, 'google_business_profile') and config.google_business_profile:
    gbp_embed = config.google_business_profile.get("embed_code", "")
```

## Fixed Files

### Contact Tab (src/ui/components/contact_tab.py)
**Lines Changed**: 407, 447
- Changed `"google_business"` to `"google_business_profile"` in get_config_data()
- Changed `"google_business"` to `"google_business_profile"` in set_config_data()

### Enhanced Main Window (src/ui/enhanced_main_window.py)  
**Lines Changed**: 847
- Changed `"google_business"` to `"google_business_profile"` in load_configuration_data()

## Regression Prevention Checklist

Before making ANY changes to data flow, verify:

### ✅ UI Components Use Correct Keys
- [ ] Contact tab exports `google_business_profile` (not `google_business`)
- [ ] Contact tab imports `google_business_profile` (not `google_business`)

### ✅ Main Window Maps Correctly  
- [ ] Enhanced main window uses `google_business_profile` when setting Contact tab data
- [ ] Enhanced main window preserves `google_business_profile` during UI data collection

### ✅ Configuration Consistency
- [ ] YAML parser loads `google_business_profile` 
- [ ] Configuration model has `google_business_profile` attribute
- [ ] Website generator reads from `config.google_business_profile`

### ✅ End-to-End Testing
- [ ] Run `test_gbp_regression_prevention.py` after ANY data flow changes
- [ ] Manually test: UI → Save → Exit → Load → Generate Website → Verify GBP in HTML

## Test Commands

```bash
# Run regression prevention test
python test_gbp_regression_prevention.py

# Manual test workflow  
# 1. Run app
# 2. Add GBP embed code to Contact tab
# 3. Save configuration 
# 4. Exit app
# 5. Run app
# 6. Verify GBP code appears in Contact tab
# 7. Generate website
# 8. Verify GBP appears in footer HTML
```

## Critical Warning Signs

If ANY of these occur, GBP regression is imminent:
- Contact tab doesn't show GBP embed code after loading saved config
- YAML file missing `google_business_profile` section after UI save
- Generated HTML missing iframe embed in footer
- Any mention of `google_business` instead of `google_business_profile` in data flow code

## Key Lesson Learned

**UI data structure keys MUST exactly match configuration model attribute names.**

When adding new UI fields:
1. Check configuration model for exact attribute name
2. Use IDENTICAL key in UI get_config_data() and set_config_data()
3. Use IDENTICAL key in enhanced main window data mapping
4. Test complete data flow before committing

## Architecture Notes

The GBP embed appears in:
- **UI**: Contact tab Google Business Profile section  
- **Config**: `client.google_business_profile.embed_code`
- **Template**: Footer section with iframe
- **Generation**: footer.html template via `template_data['google_business']`

## Future Prevention

This documentation and the regression test suite will prevent this issue from occurring again. The systematic fix addresses the root cause permanently.

---

**This document must be updated if ANY changes are made to GBP data flow architecture.**