# AWG Startup Context

**Last Updated:** 2026-03-22
**Branch:** main
**Version:** 4.1.0
**Last Commit:** 506a6a1 - feat(providers): Listed Providers system for resource sites

---

## Last 3 Accomplishments

1. **Sprint 5 (1-4) - Product Categories, Theme Presets, Site Type Help, Batch Generate** -
   `ProductCategoriesTab`, 7 theme color presets in `theme_presets.py`, contextual help
   text on Cloud Deploy tab, `BatchGenerateDialog` (Tools > F7) for multi-client sequential
   generation with live log, progress bar, and cancel.

2. **Listed Providers - Data + Generation Layer (506a6a1)** -
   `ProviderConfig` dataclass in `models.py`; `_parse_providers()` + YAML serialization
   in `parser.py`; `html_generator.py` adds `_pick_provider()`, `generate_providers_index_page()`,
   `generate_provider_profile_page()`, Providers nav item, `featured_provider` injection;
   `page_generator.py` adds `providers/` dir, `_generate_provider_pages()`, sitemap entries.

3. **Listed Providers - UI + Templates (506a6a1)** -
   `ProvidersTab` (QSplitter list-manager) fully wired into `enhanced_main_window.py`
   (import, instantiate, tab registration, get/set/clear/create_client_config, load round-trip).
   New templates: `providers-index.html`, `provider-profile.html`, `provider-cta.html`.
   `service-detail.html` and `product-comparison.html` updated to use `provider-cta.html`.

---

## Next 3 Priorities

1. **QA Sprint 5 + Providers** - Launch app, test:
   - Providers tab: add/remove/save/load round-trip, slug auto-generation
   - provider-cta renders on service-detail and product-comparison pages
   - providers/index.html and providers/{slug}.html generate correctly
   - Batch generate, theme presets, product categories (existing Sprint 5 items)

2. **Sprint 5 - Advanced City Page Content** - Enhance city page generation
   with richer localized content: nearby cities/regions, seasonal context,
   local landmarks, more FAQ depth. Improve `city_content_generator.py`.

3. **Sprint 5 - Analytics Integration Prep** - Add optional Google Analytics 4
   snippet injection field to the Cloud Deploy or Branding tab. YAML key
   `cloud.analytics_id` injected into all page `<head>` blocks via Jinja2 base template.

---

## Current State

**Git:**
- Branch: main
- Version: 4.1.0
- Last commit: 506a6a1 (pushed, Providers system complete)
- Working tree: minor non-code files (.claude/claude.md, settings.local.json, docs/qa1.png)

**Tests:**
- Total: 926 PASSING, 83 pre-existing failures (unchanged), 6 skipped
- Providers feature introduced 0 new failures
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

1. **Listed Providers workflow** - Resource sites can now list multiple provider clients.
   Each provider gets a profile page at `providers/{slug}.html`. The `providers/index.html`
   is a vetted-directory listing page. `_pick_provider()` scores token overlap between
   provider specialties and service/category topics to inject a `featured_provider` CTA.

2. **provider-cta.html component** - Renders featured provider box if `featured_provider`
   is set AND `is_resource_site` is true. Falls back to legacy `money_site_name` attribution
   if no providers configured. Used in service-detail and product-comparison templates.

3. **Batch generate** - Tools > Batch Generate (F7) opens dialog. Reads YAML
   configs from a selected folder, generates each to `<output_base>/<config_stem>/`.

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
