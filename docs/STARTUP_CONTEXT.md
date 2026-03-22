# AWG Startup Context

**Last Updated:** 2026-03-22
**Branch:** main
**Version:** 4.1.0
**Last Commit:** b692626 - Merge PR #32 (Sprint 4 - Linking structure, UI tab, Windows log fix)

---

## Last 3 Accomplishments

1. **Sprint 3 - Product Comparison Framework (PR #31 merged)** -
   `ProductCategoryConfig` dataclass added. New `product-comparison.html`
   template with comparison table, Best For/Not Ideal For boxes, competing
   brands, standards, Article JSON-LD. `products.html` shows category guide
   cards when `product_categories` configured. `page_generator.py` fully
   wired: directory creation, page count, generation, sitemap URLs.

2. **Sprint 4 - Linking Structure + UI Tab (PR #32 merged)** -
   All resource-site external links upgraded to `rel="noopener noreferrer"`.
   Authority source links added to index, service-detail, product-detail pages.
   New `ResourceSiteTab` UI component with all 8 `ResourceSiteConfig` fields.
   Cloud Deploy tab gains "Resource Site" radio button. Full round-trip wiring
   in `enhanced_main_window.py`. `WindowsSafeRotatingFileHandler` fixes
   Windows WinError 32 log rotation crash.

3. **Resource Site UI fully operational** - Users can now create resource site
   configs entirely through the UI without manually editing YAML. Site identity,
   editorial content, money site attribution, and authority sources all
   configurable via the new "Resource Site" tab.

---

## Next 3 Priorities

1. **Sprint 5 - Product Categories UI** - Add UI tab/section for
   `ProductCategoryConfig` fields (category name, slug, description,
   competing brands, comparison criteria, best for, not ideal for, standards).
   Mirrors the ResourceSiteTab pattern.

2. **Sprint 5 - Enhanced Content & Automation** - Multiple themes, advanced
   city page content generation, bulk processing, multi-client workflow
   management.

3. **User Guidance / In-app Help** - Brief tooltip/help text explaining the
   three site types (main_site, backlink_site, resource) and when to use each.
   Consider a "Getting Started" dialog or sidebar panel.

---

## Current State

**Git:**
- Branch: main
- Version: 4.1.0
- Last commit: b692626 (pushed, PR #32 merged)
- Working tree: 2 uncommitted local files (.claude/claude.md, settings.local.json - not code)

**Tests:**
- Total: 926 PASSING, 83 pre-existing failures (unchanged), 6 skipped
- Pre-existing failures: test_template_preview, test_template_validator,
  test_backup_manager, test_cities_yaml_bug (GoogleBusinessProfileConfig tag) - not our fault
- Sprint 4 introduced 0 new failures

**Blockers:**
- None for Sprint 5

**Known Issues:**
- Camphouse Country Landscaping (SAB) GBP unresolved - try direct Place ID
- Cost display shows $0.0000 instead of actual cost - LOW priority
- Business tab "Generate with AI" buttons use OpenAI (not Claude) - works if OPENAI_API_KEY set

---

## Key Context Notes

1. **Resource site workflow** - Three site_type values: "main_site" (default),
   "backlink_site", "resource". Resource sites now fully UI-configurable via
   the "Resource Site" tab (between API Keys and Cloud Deploy).
   YAML round-trip confirmed. No manual YAML editing needed.

2. **Product categories** - `product_categories` YAML list drives comparison
   guide generation. No UI tab yet (Sprint 5). Still requires manual YAML
   editing for now.

3. **Config directory is gitignored** - All client YAML configs (config/clients/**)
   are not tracked. Onboard command writes configs there.

---

## Quick Reference

**Generate resource site via UI:**
1. Fill in Business Info, Contact, Branding tabs as normal
2. Go to "Resource Site" tab - fill in site identity, editorial content,
   money site, and authority sources
3. Go to "Cloud Deploy" tab - select "Resource Site" radio button
4. Generate and deploy

**Generate resource site via YAML:**
```yaml
cloud:
  site_type: resource
resource_site:
  site_name: "Commercial Door Guide"
  site_mission: "Independent guides for facility managers."
  money_site_name: "Overhead Door Company of Joliet"
  money_site_url: "https://overheaddoorjoliet.com"
  cta_style: educational
  authoritative_sources:
    - https://www.nfpa.org
    - https://www.ul.com
product_categories:
  - category_name: "Fire Doors"
    guide_title: "Fire Door Buyer Guide"
    competing_brands: ["Allegion", "ASSA ABLOY", "Mesker"]
    comparison_criteria: ["Fire Rating", "Material", "Price Range"]
    best_for: ["High-traffic corridors", "Stairwells"]
    not_ideal_for: ["Exterior applications"]
    standards: ["NFPA 80", "UL 10C"]
```

**Run tests:**
```cmd
python -m pytest -q --ignore=tests/unit/test_ai_content_service.py
```

**Model Presets:**
- fast: Claude Haiku 4.5 (~$0.01/page)
- balanced: Claude Sonnet 4.5 (~$0.025/page) - DEFAULT
- thorough: Claude Opus 4.6 (~$0.15/page)
