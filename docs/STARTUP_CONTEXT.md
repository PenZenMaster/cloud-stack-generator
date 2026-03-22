# AWG Startup Context

**Last Updated:** 2026-03-21
**Branch:** main
**Version:** 4.1.0
**Last Commit:** dd22f1d - Merge PR #29 (Sprint 1 - ResourceSiteConfig + resource site template conditionals)

---

## Last 3 Accomplishments

1. **Sprint 1 - Resource Site Identity/Branding (PR #29 merged)** -
   `ResourceSiteConfig` dataclass added to models.py with 8 fields
   (site_name, site_brand, site_mission, editorial_perspective,
   money_site_name, money_site_url, authoritative_sources, cta_style).
   Parser round-trips YAML. Template context adds is_resource_site,
   resource_site, site_display_name. All core templates (header, footer,
   index, about) now conditional on site_type == "resource".

2. **Comprehensive AWS Test Connection (PR #29 pipeline)** - ConnectionTestWorker
   runs 4 check categories: Identity (STS), S3 Permissions (PUT/GET/DELETE),
   Bucket State (OAC SourceArn validation), CloudFront (origin + OAC).
   Results shown in scrollable color-coded ConnectionResultsDialog.

3. **BACK-007 complete + v4.1.0 milestone** - deploy command wired to
   sync_to_s3(). 14/14 deploy sync tests pass. 926 tests passing total.

---

## Next 3 Priorities

1. **Sprint 2 - Schema + Service/Product Template Voice** - No LocalBusiness
   schema for resource sites; add Article/HowTo schema. Service page template
   educational voice for resource sites. Products hub "Resources" framing.

2. **Sprint 3 - Content Consolidation** - Consolidate 72 product pages into
   ~12 comparison guides. New generator mode for resource site product content.

3. **Sprint 4 - Linking Structure** - Diversify outbound links. Contextual
   money-site mention (max 1-2 per page). Remove sitewide footer link (done
   in Sprint 1). Add authoritative_sources to outbound link generation.

---

## Current State

**Git:**
- Branch: main
- Version: 4.1.0
- Last commit: dd22f1d (pushed, PR #29 merged)
- Working tree has 3 uncommitted changes (.claude/claude.md, settings.local.json - not code)

**Tests:**
- Total: 926 PASSING, 83 pre-existing failures (unchanged), 6 skipped
- Pre-existing failures: test_template_preview, test_template_validator,
  test_backup_manager, and others - confirmed pre-existing, not our fault
- Sprint 1 introduced 0 new failures

**Blockers:**
- None for Sprint 2

**Known Issues:**
- Camphouse Country Landscaping (SAB) GBP unresolved - try direct Place ID
- Cost display shows $0.0000 instead of actual cost - LOW priority

---

## Key Context Notes

1. **Resource site site_type flow** - Three values now: "main_site" (default),
   "backlink_site", "resource". Resource sites get independent identity via
   ResourceSiteConfig. site_display_name pre-computed in Python, not Jinja.

2. **Sprint 1 backward compatibility confirmed** - All new ResourceSiteConfig
   fields default to empty. Existing main_site/backlink_site configs unaffected.
   resource_site YAML section only written when is_configured() is True.

3. **Config directory is gitignored** - All client YAML configs (config/clients/**)
   are not tracked. Onboard command writes configs there.

---

## Quick Reference

**Generate resource site (after Sprint 1):**
Add to config YAML:
```yaml
cloud:
  site_type: resource
resource_site:
  site_name: "Commercial Door Guide"
  site_mission: "Independent guides for facility managers."
  money_site_name: "Overhead Door Company of Joliet"
  money_site_url: "https://overheaddoorjoliet.com"
  cta_style: educational
```

**Run tests:**
```cmd
python -m pytest -q --ignore=tests/unit/test_ai_content_service.py
```

**Model Presets:**
- fast: Claude Haiku 4.5 (~$0.01/page)
- balanced: Claude Sonnet 4.5 (~$0.025/page) - DEFAULT
- thorough: Claude Opus 4.6 (~$0.15/page)
