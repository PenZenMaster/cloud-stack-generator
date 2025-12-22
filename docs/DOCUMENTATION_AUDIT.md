# Documentation Audit & Reorganization Plan

**Date**: December 21, 2025
**Purpose**: Categorize all documentation files for archival, consolidation, and maintenance

---

## Current State Summary

- **Total Documentation Files**: 97
- **Root docs/ files**: 64
- **Already Archived**: 45
- **Current Version**: v3.6.0

---

## Documentation Categories

### ✅ KEEP - Active Core Documentation (15 files)

**Project Management**:
1. `projectStatus.md` - Active project status tracking
2. `STARTUP_CONTEXT.md` - Session context for AWG workflow
3. `AWG-Project-Plan.md` - Main project specification
4. `AWG_STARTUP_OPTIMIZATION.md` - Startup workflow optimization
5. `GITHUB_ISSUES_WORKFLOW.md` - Issue tracking integration (NEW)

**Architecture & Design**:
6. `MULTI_CLOUD_ARCHITECTURE.md` - Multi-cloud deployment architecture
7. `TEMPLATE_SYSTEM_ARCHITECTURE.md` - Template system design
8. `THEME_SYSTEM_V3.5.0.md` - Theme system specification
9. `ARCHITECTURE_ANALYSIS.md` - Architecture analysis and refactoring needs
10. `ARCHITECTURE_CONFLICT_ANALYSIS.md` - Conflict analysis between features

**SEO & Schema**:
11. `SCHEMA_ENHANCEMENT_ROADMAP.md` - Future schema enhancements
12. `SCHEMA_VALIDATION_CHECKLIST.md` - Schema validation procedures
13. `SCHEMA_STRUCTURED_DATA_GUIDE.md` - Schema implementation guide
14. `GOOGLE_RICH_RESULTS_TESTING_GUIDE.md` - Rich results testing
15. `SEO_AND_INDEXING.md` - SEO best practices

---

### 🔄 CONSOLIDATE - Merge into Comprehensive Docs (28 files)

**Should merge into END USER DOCUMENTATION**:
1. `CLIENT_ASSETS_GUIDE.md` - Client asset management
2. `LOGO_UPLOAD_WORKFLOW.md` - Logo upload procedures
3. `CANONICAL_URL_WORKFLOW.md` - Canonical URL setup
4. `FAQ_IMPORT_EXPORT.md` - FAQ import/export
5. `TEMPLATE_SPECIFICATIONS.md` - Template usage
6. `TEMPLATE_SYSTEM_GUIDE.md` - Template system guide
7. `user-guides/Cloud_Stack_SOP_S3_CloudFront.md` - Deployment SOP
8. `GoogleSearchConsole.txt` - GSC integration notes

**Should merge into ADMINISTRATION DOCUMENT**:
9. `AWS_S3_DEPLOYMENT_SETUP.md` - AWS S3 setup
10. `GCS_DEPLOYMENT_SETUP.md` - Google Cloud Storage setup
11. `OAC_PERMISSIONS_EXPLAINED.md` - CloudFront OAC permissions
12. `MODE_B_IMPLEMENTATION_PLAN.md` - Mode B deployment
13. `SECURITY_ALERT.md` - Security considerations
14. `NAMING_CONVENTIONS.md` - Naming standards
15. `GITHUB_TOKEN_SETUP.md` - GitHub token configuration
16. `user-guides/AWS_Access_Key_Setup_Guide.md` - AWS credentials
17. `AI_SETUP_QUICKSTART.md` - AI content setup
18. `AI_INTEGRATION_GUIDE.md` - AI integration guide
19. `GBP-Data-Flow-Documentation.md` - Google Business Profile integration

**Should merge into ARCHITECTURE DOCUMENT**:
20. `CODEBASE_STRUCTURE.md` - Codebase organization
21. `ORCHESTRATION_REFACTOR_PLAN.md` - Orchestration refactoring
22. `REFACTORING_PLAN.md` - General refactoring plan
23. `TDD_WORKFLOW.md` - Test-driven development workflow
24. `AI_CONTENT_GENERATION.md` - AI content architecture
25. `WYSIWYG_EDITOR_SPECIFICATION.md` - WYSIWYG editor spec
26. `DEBUGGING.md` - Debugging methodology
27. `TEST_STATUS_REPORT.md` - Testing status
28. `AGENT_HANDOFF.md` - Agent handoff procedures

---

### 📦 ARCHIVE - Obsolete/Superseded (16 files)

**Resolved Bug Fixes** (move to `docs/archive/resolved-issues/`):
1. `BACKLINK_SITE_BUG_FIX.md` - Backlink bug resolved
2. `CLOUDFRONT_INDEXING_FIX.md` - CloudFront indexing resolved
3. `Website Generation Button Fix.txt` - Button fix resolved

**Outdated Snapshots** (move to `docs/archive/historical-reports/`):
4. `CODE_QUALITY_SUMMARY.md` - Nov 21 snapshot (outdated)
5. `COVERAGE_REPORT.md` - Nov 21 snapshot (outdated)
6. `VULTURE_ANALYSIS.md` - Nov 21 analysis (outdated)

**Completed Features** (move to `docs/archive/completed-features/`):
7. `BACKLINK_SITE_IMPLEMENTATION.md` - Feature complete
8. `BACKLINK_SITE_STRATEGY.md` - Strategy implemented

**Old Notes** (move to `docs/archive/notes/`):
9. `city-page-considerations.txt` - Old notes
10. `start.txt` - Old notes
11. `webgen.txt` - Old notes
12. `wrap.txt` - Old notes

**Superseded Templates** (move to `docs/archive/templates/`):
13. `FEATURE_REQUEST_TEMPLATE.md` - Superseded by GitHub templates
14. `FEATURE_REQUEST_TEMPLATE_IMPORT_EXPORT.md` - Superseded
15. `GITHUB_ISSUES_TEMPLATE_IMPORT_EXPORT.md` - Superseded
16. `CREATE_GITHUB_ISSUES.md` - Superseded by GITHUB_ISSUES_WORKFLOW.md

---

### 🤔 REVIEW - Need Decision (5 files)

**Future Planning** (keep for now, may archive later):
1. `BLOG_SYSTEM_SPECIFICATION.md` - Future feature (Design Phase)
2. `PRODUCT_ROADMAP.md` - Product roadmap
3. `ADDITIONAL_FEATURE_REQUESTS.md` - Feature backlog
4. `BACKLOG.md` - General backlog
5. `FEATURE_REQUEST_PREVIEW_SYSTEM.md` - Preview system spec

**Decision**: Keep in root for visibility, review quarterly

**Project Board Docs** (may consolidate):
6. `PROJECT_BOARD_IMPROVEMENTS.md`
7. `PROJECT_BOARD_OPTIMIZATION_GUIDE.md`

**Decision**: Consolidate into single PROJECT_MANAGEMENT_GUIDE.md

---

## Archive Directory Structure

```
docs/archive/
├── checkpoints/                    # Session checkpoints (existing)
│   ├── 2025-08-historical/
│   └── CheckPoint-*.md
├── deprecated_context_files/       # Old context files (existing)
├── proposals/                      # Old proposals (existing)
├── troubleshooting/               # Old troubleshooting (existing)
├── resolved-issues/               # NEW: Resolved bug fixes
│   ├── BACKLINK_SITE_BUG_FIX.md
│   ├── CLOUDFRONT_INDEXING_FIX.md
│   └── Website_Generation_Button_Fix.txt
├── historical-reports/            # NEW: Outdated snapshots
│   ├── CODE_QUALITY_SUMMARY_2025-11-21.md
│   ├── COVERAGE_REPORT_2025-11-21.md
│   └── VULTURE_ANALYSIS_2025-11-21.md
├── completed-features/            # NEW: Implemented features
│   ├── BACKLINK_SITE_IMPLEMENTATION.md
│   └── BACKLINK_SITE_STRATEGY.md
├── notes/                         # NEW: Old development notes
│   ├── city-page-considerations.txt
│   ├── start.txt
│   ├── webgen.txt
│   └── wrap.txt
└── templates/                     # NEW: Superseded templates
    ├── FEATURE_REQUEST_TEMPLATE.md
    ├── FEATURE_REQUEST_TEMPLATE_IMPORT_EXPORT.md
    ├── GITHUB_ISSUES_TEMPLATE_IMPORT_EXPORT.md
    └── CREATE_GITHUB_ISSUES.md
```

---

## New Comprehensive Documentation Structure

### End User Documentation
**File**: `docs/USER_GUIDE.md`
**Consolidates**:
- CLIENT_ASSETS_GUIDE.md
- LOGO_UPLOAD_WORKFLOW.md
- CANONICAL_URL_WORKFLOW.md
- FAQ_IMPORT_EXPORT.md
- TEMPLATE_SPECIFICATIONS.md
- TEMPLATE_SYSTEM_GUIDE.md
- Cloud_Stack_SOP_S3_CloudFront.md
- GoogleSearchConsole.txt

**Sections**:
1. Getting Started
2. Business Configuration
3. Content Management (Products, Services, FAQs)
4. Branding & Themes
5. Template Selection & Customization
6. City Pages & Location Targeting
7. SEO Optimization
8. Website Generation
9. Preview & Testing
10. Troubleshooting

---

### Administration Document
**File**: `docs/ADMIN_GUIDE.md`
**Consolidates**:
- AWS_S3_DEPLOYMENT_SETUP.md
- GCS_DEPLOYMENT_SETUP.md
- OAC_PERMISSIONS_EXPLAINED.md
- MODE_B_IMPLEMENTATION_PLAN.md
- SECURITY_ALERT.md
- NAMING_CONVENTIONS.md
- GITHUB_TOKEN_SETUP.md
- AWS_Access_Key_Setup_Guide.md
- AI_SETUP_QUICKSTART.md
- AI_INTEGRATION_GUIDE.md
- GBP-Data-Flow-Documentation.md

**Sections**:
1. Installation & Setup
2. Environment Configuration
3. AWS Deployment Setup
   - S3 Configuration
   - CloudFront Setup (Mode A & Mode B)
   - OAC Permissions
4. Google Cloud Setup (GCS)
5. API Integration
   - Google Maps API
   - Wikipedia API
   - AI Content Generation (OpenAI)
   - Google Business Profile
6. Security Best Practices
7. Naming Conventions & Standards
8. Backup & Recovery
9. Monitoring & Maintenance
10. Troubleshooting

---

### Architecture Document
**File**: `docs/ARCHITECTURE.md`
**Consolidates**:
- CODEBASE_STRUCTURE.md
- ORCHESTRATION_REFACTOR_PLAN.md
- REFACTORING_PLAN.md
- TDD_WORKFLOW.md
- AI_CONTENT_GENERATION.md
- WYSIWYG_EDITOR_SPECIFICATION.md
- DEBUGGING.md
- TEST_STATUS_REPORT.md
- AGENT_HANDOFF.md

**Sections**:
1. System Overview
2. Architecture Principles
3. Module Organization
4. Core Components
   - Website Generator
   - Content Generators
   - Template System
   - Deployment System
5. UI Components (PyQt6)
6. Data Flow & Orchestration
7. Testing Strategy
8. Refactoring Plans
9. Future Enhancements
10. Development Workflows
11. Debugging & Troubleshooting
12. Agent Handoff Procedures

---

## Implementation Plan

### Phase 1: Archive Obsolete Files (Today)
1. Create new archive subdirectories
2. Move 16 obsolete files to appropriate archive locations
3. Update README.md in each archive directory
4. Commit archival changes

### Phase 2: Create Comprehensive Docs (Next Session)
5. Create USER_GUIDE.md (consolidate 8 files)
6. Create ADMIN_GUIDE.md (consolidate 11 files)
7. Create ARCHITECTURE.md (consolidate 9 files)
8. Cross-reference between documents

### Phase 3: Clean Up (Next Session)
9. Remove/archive consolidated source files
10. Update projectStatus.md with new doc structure
11. Update AWG-Project-Plan.md references
12. Create DOCUMENTATION_INDEX.md (master index)

---

## Metrics

**Before**:
- Total docs: 64 files in root
- Difficult to navigate
- Duplicate information
- Outdated content mixed with current

**After**:
- Core docs: 15 files (kept)
- Comprehensive docs: 3 files (new)
- Archived: 16 files (obsolete)
- Future planning: 5 files (review)
- Total root docs: ~23 files (64% reduction)

---

## Next Steps

1. Get approval for archival plan
2. Execute Phase 1 (archival)
3. Begin Phase 2 (comprehensive doc creation)
4. Review and iterate

---

**Last Updated**: December 21, 2025
**Status**: Awaiting Approval
**Version**: 1.0
