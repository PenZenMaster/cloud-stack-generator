# AWG Startup Context - Lightweight Session Resume

**Last Updated**: 2025-12-20 10:30
**Branch**: feature/v3.5.0-ui-improvements
**Last Commit**: 96de7c7

## Last 3 Accomplishments

1. **Deployment Tracking System (v3.5.0)** - Implemented friendly names and industry snapshots for deployments. Added `friendly_name` and `industry` fields to DeploymentConfig model with full YAML serialization support and backward compatibility.

2. **Deployment UI Enhancements** - Added friendly name input field to Cloud Tab (optional, auto-generates if empty), inline editing in Deployment History Tab, removed non-functional UI buttons (Re-Deploy, Update Meta Tags).

3. **Bug Fixes** - Fixed CloudTab config access AttributeError, updated both S3 and GCS deployment paths with new fields, improved friendly name display with proper formatting and readability.

## Next 3 Priorities

1. **Address User Feedback** - Fix friendly name format (remove "+" separator), standardize text sizing in Deployment History, fix deployment history persistence issue (redeployments replacing instead of adding).

2. **Semantic Versioning** - Update file version numbers per project standards (v1.00 baseline, +0.01 minor, +1.00 major).

3. **Wikipedia Image Persistence** - Fix Cities tab Wikipedia image embed not persisting from session to session.

## Current State

**Git**:
- Branch: feature/v3.5.0-ui-improvements
- Commit: 96de7c7 (feat(assets): Implement client-specific assets system with UI integration)
- Status: Modified (5 files) - deployment tracking implementation

**Tests**: Manual QA in progress

**Deployed Sites**:
- d20sn5sqv0dset.cloudfront.net - Test deployment with friendly name feature

**Blockers**: None - addressing user feedback

## Key Context Notes

1. **Deployment Tracking Architecture** - Uses existing DeploymentConfig model with two new optional fields (friendly_name, industry). Snapshots industry at deployment time for historical accuracy.

2. **Friendly Name Auto-Generation** - Format: "{Business Name} + {Industry} + MM/DD/YYYY". User feedback: remove "+" separator, use spaces only.

3. **Deployment History Issue** - When redeploying to same bucket/directory, system updates existing deployment instead of creating new entry. User wants full history preserved.

4. **Inline Editing** - Deployment History uses QLineEdit for direct editing (like Business Name field), no popup dialogs.

## Files Modified This Session (Uncommitted)

**Core System (2 files)**:
- src/core/config/models.py - Added friendly_name and industry fields to DeploymentConfig
- src/core/config/parser.py - YAML parsing/serialization for new fields

**UI Components (3 files)**:
- src/ui/components/cloud_tab.py - Added friendly name input, snapshot logic, auto-generation method
- src/ui/components/deployment_history_tab.py - Inline editing, removed non-functional buttons, improved display
- src/ui/enhanced_main_window.py - Added set_config call for CloudTab

## Quick Reference

**Current Issues to Fix**:
1. Remove "+" separator from auto-generated friendly names (use spaces)
2. Standardize text size in Deployment History Tab
3. Check for remaining non-functional UI elements (Delete button functionality?)
4. Fix deployment history persistence (create new vs update existing)
5. Apply semantic versioning to modified files
6. Cities tab Wikipedia image persistence

**Test Config**:
```
E:\projects\cloud-stack-generator\config\clients\unites-structural-systems\united_structural_systems_of_illinois_inc_residential_foundation_repair_config.yaml
```
