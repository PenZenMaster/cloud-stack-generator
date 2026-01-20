# AWG Startup Context

**Last Updated:** 2026-01-19 18:19
**Branch:** main
**Version:** 3.13.0
**Last Commit:** 338d1ed

---

## Last 3 Accomplishments

1. **GSC Meta Tag Format Fix (v3.13.0)** - Fixed critical formatting issue where Google Search Console verification meta tag was missing self-closing slash. Changed template rendering from `<meta name="..." content="...">` to `<meta name="..." content="..." />` in both index.html and city page templates. Added 2 regression tests (both passing).

2. **City Page Pool Images - Complete Fix (v3.9.0 → v3.12.0)** - Fixed critical regression in city page image handling through 4 iterations: corrected design from replace to augment, added header_image field, implemented path normalization, fixed asset copying from absolute paths, and resolved relative path resolution with base_path prefix. Pool images now display in article header, Wikipedia images preserved in showcase section.

3. **Comprehensive Testing & QA (19 Tests Added)** - Created 10 regression tests for city page pool images, 7 path normalization tests, and 2 meta tag formatting tests. All new tests passing. Completed 4 QA cycles with user feedback leading to final QA Pass on v3.12.0.

---

## Next 3 Priorities

1. **User QA & Deployment** - User needs to regenerate Salvo Metal Works GCS-scupper-box-206 site and deploy to GCS bucket to verify GSC meta tag fix works in production. Awaiting QA confirmation before committing changes.

2. **Commit v3.13.0** - After successful QA, commit meta tag fix with message "fix: GSC meta tag self-closing format (v3.13.0)" and push to main branch.

3. **Monitor Production Use** - Watch for edge cases with different meta tag configurations and verify GSC verification completes successfully after deployment.

---

## Current State

**Git:**
- Branch: main (up to date with origin/main)
- Working tree: Modified (5 files changed, awaiting QA)
- Last commit: 338d1ed (v3.12.0 checkpoint update)
- Push status: Local changes not yet committed ⚠️
- Version: 3.13.0 (updated in main.py)

**Tests:**
- Cloud infrastructure: 113/113 passing
- Regression tests: 19/19 passing (2 new meta tag tests)
- HTML generator suite: 55/75 passing (20 pre-existing failures unrelated to current work)
- New tests (v3.13.0): 2/2 PASSING ✅

**Blockers:**
- **CRITICAL: Awaiting user QA confirmation** - User needs to regenerate site and verify meta tag format before commit/push

**Known Issues (Non-blocking):**
- 20 pre-existing test failures in test_html_generator.py (unrelated to v3.13.0 work)
- Minor ruff linting warnings (unused imports)

---

## Key Context Notes

1. **GSC Meta Tag Format:** Self-closing format `<meta name="..." content="..." />` is required for proper XHTML compliance and GSC verification. Template changes applied to both index.html and city page templates to ensure all custom meta tags from cloud.meta_tags render correctly.

2. **Null Safety Added:** Fixed bug in `_get_canonical_base_url()` where method assumed config.cloud always exists. Added defensive hasattr checks to prevent AttributeError when cloud config is None or missing.

3. **City Page Image Architecture:** Separate header_image (pool) and city_image (Wikipedia) fields allow both to coexist. Pool images showcase client products/services in article header; Wikipedia images provide city context in showcase section. Both render together on city pages.

4. **Path Normalization Strategy:** Normalize at assignment time in generator layer (not at template render). Absolute local paths (D:/OneDrive/...) converted to relative web paths (images/filename.jpg). Single source of truth prevents duplicate normalization logic.

---

**For full checkpoint details:** See `docs/archive/checkpoints/CheckPoint-2026-01-19_1819.md`
