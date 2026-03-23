# AWG Startup Context

**Last Updated:** 2026-03-22
**Branch:** main
**Version:** 4.1.0
**Last Commit:** 2e09426 - chore(checkpoint): 2026-03-22 - Listed Providers system complete

---

## Last 3 Accomplishments

1. **Listed Providers system shipped (506a6a1)** - Full stack: `ProviderConfig` dataclass,
   YAML round-trip in parser, `ProvidersTab` UI (QSplitter list-manager), wired into
   `enhanced_main_window.py`, `_pick_provider()` scoring, `generate_providers_index_page()`,
   `generate_provider_profile_page()`, `provider-cta.html` component, Providers nav item,
   sitemap entries. 926 tests passing, 0 new failures.

2. **Resource site workflow documented** - Walked through end-to-end: Business Info
   (Website field = resource domain), Resource Site tab, Providers tab for each client,
   generate, deploy. Clarified that `Main Site URL` is for backlink sites only; resource
   sites use Providers tab instead of money_site_url.

3. **AWS S3 + CloudFront setup walkthrough** - Full sequence for custom domain:
   ACM cert (us-east-1, DNS validation), S3 bucket (OAC, no public access),
   CloudFront distribution (OAC, CNAME, SSL cert, index.html root), DNS CNAME/ALIAS,
   bucket policy from CloudFront banner, Cloud Deploy tab wiring (bucket, region, dist ID).

---

## Next 3 Priorities

1. **QA - Resource Site + Providers** - User to complete AWS setup for
   `localgaragedoorcompanyreviews.com`, then do end-to-end test: create config,
   add first client as Provider, generate, deploy, verify providers/index.html,
   provider profile page, and provider CTA on service-detail pages.

2. **Sprint 5 - Advanced City Page Content** - Enhance city page generation
   with richer localized content: nearby cities/regions, seasonal context,
   local landmarks, more FAQ depth. Improve `city_content_generator.py`.

3. **Sprint 5 - Analytics Integration Prep** - Add optional Google Analytics 4
   snippet injection field to Cloud Deploy or Branding tab. YAML key
   `cloud.analytics_id` injected into all page `<head>` blocks via Jinja2 base template.

---

## Current State

**Git:**
- Branch: main
- Version: 4.1.0
- Last commit: 2e09426 (pushed, providers system + STARTUP_CONTEXT update)
- Working tree: minor non-code files only (.claude/claude.md, settings.local.json, docs/qa1.png)

**Tests:**
- Total: 926 PASSING, 83 pre-existing failures (unchanged), 6 skipped
- No new failures introduced by any Sprint 5 work

**Blockers:**
- User needs AWS S3/CloudFront setup for localgaragedoorcompanyreviews.com before QA deploy

**Known Issues:**
- Camphouse Country Landscaping (SAB) GBP unresolved - try direct Place ID
- Cost display shows $0.0000 instead of actual cost - LOW priority
- Business tab "Generate with AI" buttons use OpenAI (not Claude) - works if OPENAI_API_KEY set

---

## Key Context Notes

1. **Resource site domain** goes in Business Info tab > Website field (not "Domain" —
   the UI label is "Website" but the underlying key is `domain`). Main Site URL on
   Cloud Deploy tab is for backlink sites only — leave blank for resource sites.

2. **Providers workflow** - Each promoted client is added as a Provider (Providers tab).
   External followed link lives on `providers/{slug}.html`. Topic guide pages link
   internally to the profile (not directly to client domain). `_pick_provider()` matches
   provider specialties to topic keywords to inject featured CTA automatically.

3. **AWS setup sequence** - ACM cert must be in us-east-1. S3 uses OAC (not public
   access). Bucket policy comes from CloudFront banner after distribution creation.
   Cloud Deploy tab needs: S3 bucket name, AWS region, CloudFront distribution ID.

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
