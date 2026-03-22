# AWG Startup Context

**Last Updated:** 2026-03-22
**Branch:** main
**Version:** 4.1.0
**Last Commit:** 12137c4 - Sprint 5-4 - Batch Generate dialog for multi-client workflow

---

## Last 3 Accomplishments

1. **Sprint 5-1 - Product Categories UI Tab (10987ef)** -
   `ProductCategoriesTab` added to `src/ui/components/`. Split-panel
   list-manager: left = category list + Add/Remove, right = form for all
   `ProductCategoryConfig` fields (identity, competing brands, criteria,
   suitability, standards, product links). Full round-trip wired in
   `enhanced_main_window.py` (get/set/clear/create_client_config).

2. **Sprint 5-2 - Theme Preset Selector (9fbbbcf)** -
   `src/core/config/theme_presets.py` defines 7 named color palette presets
   (Default, Midnight Pro, Forest Service, Crimson Trades, Slate Corporate,
   Amber Warmth, Ocean Coastal). Branding tab gains a "Theme Preset" dropdown
   that applies the full palette + font to all color inputs in one click.

3. **Sprint 5-3 + 5-4 - Site Type Help Panel + Batch Generate (0c1c23b, 12137c4)** -
   Cloud Deploy tab: contextual help panel below site-type radios updates
   dynamically (Main/Backlink/Resource descriptions). New
   `BatchGenerateDialog` in Tools menu (F7): scan a config folder, select
   YAMLs, set base output dir, run sequential generation with live log,
   progress bar, cancel, and results summary.

---

## Next 3 Priorities

1. **QA Sprint 5** - Launch the app and test all 4 Sprint 5 features:
   Product Categories tab (add/remove/save/load roundtrip), theme preset
   dropdown (apply + customize), site type help text (all 3 states),
   batch generate (select configs + generate).

2. **Sprint 5 - Advanced City Page Content** - Enhance city page generation
   with richer localized content: nearby cities/regions, seasonal context,
   local landmarks, more FAQ depth. Improve `city_content_generator.py`.

3. **Sprint 5 - Analytics Integration Prep** - Add optional Google Analytics 4
   snippet injection field to the Cloud Deploy or Branding tab. The YAML
   key `cloud.analytics_id` → injected into all page `<head>` blocks via
   the Jinja2 base template.

---

## Current State

**Git:**
- Branch: main
- Version: 4.1.0
- Last commit: 12137c4 (pushed, Sprint 5 items 1-4)
- Working tree: minor non-code files (.claude/claude.md, settings.local.json, docs/qa1.png)

**Tests:**
- Total: 926 PASSING, 83 pre-existing failures (unchanged), 6 skipped
- Sprint 5 introduced 0 new failures
- Pre-existing failures: test_template_preview, test_template_validator,
  test_backup_manager, test_branding_tab (2), test_cloud_tab (2),
  test_cities_yaml_bug, test_meta_tags_feature - not our fault

**Blockers:**
- None

**Known Issues:**
- Camphouse Country Landscaping (SAB) GBP unresolved - try direct Place ID
- Cost display shows $0.0000 instead of actual cost - LOW priority
- Business tab "Generate with AI" buttons use OpenAI (not Claude) - works if OPENAI_API_KEY set

---

## Key Context Notes

1. **Sprint 5 features shipped** - Product Categories UI, Theme Presets, Site
   Type help panel, Batch Generate dialog. All await user QA before marking
   Sprint 5 complete.

2. **Product categories workflow** - Three site_type values: "main_site"
   (default), "backlink_site", "resource". Product categories are now
   UI-configurable via the new "Product Categories" tab (between Resource
   Site and Cloud Deploy). YAML round-trip confirmed at logic level.

3. **Batch generate** - Tools > Batch Generate (F7) opens dialog. Reads YAML
   configs from a selected folder, generates each to
   `<output_base>/<config_stem>/`. Uses `PageGenerator` directly (same
   pipeline as single-client generate). Each run is sequential; cancel button
   stops after current client completes.

---

## Quick Reference

**Run tests:**
```cmd
python -m pytest -q --ignore=tests/unit/test_ai_content_service.py
```

**Theme presets location:**
- `src/core/config/theme_presets.py` - PRESET_NAMES, get_preset(name)

**Model Presets:**
- fast: Claude Haiku 4.5 (~$0.01/page)
- balanced: Claude Sonnet 4.5 (~$0.025/page) - DEFAULT
- thorough: Claude Opus 4.6 (~$0.15/page)
