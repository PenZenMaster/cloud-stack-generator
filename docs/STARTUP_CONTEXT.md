# AWG Startup Context

**Last Updated:** 2026-01-19 14:23
**Branch:** main
**Version:** 3.12.0
**Last Commit:** 9c87f19

---

## Last 3 Accomplishments

1. **City Page Pool Images - Complete Fix (v3.9.0 → v3.12.0)** - Fixed critical regression in city page image handling through 4 iterations: corrected design from replace to augment, added header_image field, implemented path normalization, fixed asset copying from absolute paths, and resolved relative path resolution with base_path prefix. Pool images now display in article header, Wikipedia images preserved in showcase section.

2. **Hero Background Image Path Regression Fixed (v3.10.0)** - Resolved issue where hero background images stored as absolute Windows paths (D:/OneDrive/...) were embedded in HTML causing CloudFront failures. Added path normalization in _prepare_template_data() and extended asset copying to handle absolute paths.

3. **Comprehensive Testing & QA (17 Tests Added)** - Created 10 regression tests for city page pool images and 7 path normalization tests. All tests passing. Completed 4 QA cycles with user feedback leading to final QA Pass on v3.12.0.

---

## Next 3 Priorities

1. **Monitor Production Use** - Watch for edge cases with different image configurations and gather user feedback on pool image feature effectiveness

2. **Code Quality Cleanup** - Address ruff linting warnings (unused imports in deployment_store.py, migration.py, etc.) - non-blocking housekeeping

3. **Feature Documentation** - Update user documentation on City Page Pool feature to clarify that pool images augment (not replace) Wikipedia showcase images

---

## Current State

**Git:**
- Branch: main (up to date with origin/main)
- Working tree: Clean
- Last commit: 9c87f19 (v3.12.0 - Path resolution fix)
- Push status: All commits pushed ✅
- Version: 3.12.0

**Tests:**
- Cloud infrastructure: 113/113 passing
- Regression tests: 17/17 passing
- Total: 130+ tests passing
- Pre-commit hooks: Passing

**Blockers:**
- None (all critical issues resolved, QA approved)

**Known Issues (Non-blocking):**
- Minor ruff linting warnings (unused imports)
- Pre-existing test failures in backup_manager, template_manager (unrelated to recent work)

---

## Key Context Notes

1. **City Page Image Architecture:** Separate header_image (pool) and city_image (Wikipedia) fields allow both to coexist. Pool images showcase client products/services in article header; Wikipedia images provide city context in showcase section. Both render together on city pages.

2. **Path Normalization Strategy:** Normalize at assignment time in generator layer (not at template render). Absolute local paths (D:/OneDrive/...) converted to relative web paths (images/filename.jpg). Single source of truth prevents duplicate normalization logic.

3. **Relative Path Resolution:** City pages in /locations/ subdirectory require base_path="../" prefix for correct image path resolution. Template uses {{ base_path }}{{ image_url }} to resolve ../images/file.jpg → /images/file.jpg. Homepage at root level doesn't need base_path.

4. **Asset Copying (v3.11.0):** Extended _copy_static_assets() to copy pool images and hero images from absolute local paths to output/images/ directory. This ensures images are included in S3 deployment. Handles both branding.city_page_image_pool and branding.hero_background_image_url.

---

**For full checkpoint details:** See `docs/archive/checkpoints/CheckPoint-2026-01-19_1423.md`
