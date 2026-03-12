# AWG Startup Context

**Last Updated:** 2026-03-11
**Branch:** main
**Version:** 4.0.0
**Last Commit:** (see git log - auto-onboarding feature)

---

## Last 3 Accomplishments

1. **Auto Onboarding Feature - COMPLETE (v4.0.0)** - New `awg onboard` CLI command.
   Given a website URL + optional GBP share link + industry, it scrapes the site
   (BeautifulSoup4, up to 10 pages), runs Claude LLM extraction (services, products,
   branding colors), fetches GBP data via Places API (New), and writes a pre-populated
   client YAML config. Graceful partial failure: website/GBP failures are non-fatal.
   New module: `src/core/onboarding/` (6 files, 85 unit tests passing).

2. **SAB (Service Area Business) Support** - GBP client handles SABs that hide their
   physical address. `search_place()` retries without location bias when biased search
   returns 0 results. `search_place_with_fallback()` recovers city/state from the text
   search `formattedAddress`. `fetch()` enriches sparse place details with SAB city data.
   Places API (New) fully adopted (`places.googleapis.com/v1/`).

3. **API Keys UI Consolidated to .env** - API Keys tab now shows Google Maps, Claude,
   and OpenAI fields. Load reads from `.env` via `dotenv_values()`. Save writes to `.env`
   via `set_key()` and reloads env into the running process. Test Connections button
   tests Places API (New), Anthropic `/v1/models`, and OpenAI `/v1/models`. Dead
   `config/api_keys.json` storage removed. `env_config.py` gains `GoogleMapsConfig`
   and `ClaudeConfig` classes.

---

## Next 3 Priorities

1. **Implement BACK-007: CLI deploy command** - Wire boto3 S3 sync with correct
   content-type headers, --delete flag, and auto CloudFront invalidation when
   `auto_invalidate_cache: true`. `aws_s3` provider is priority; others remain stubs.

2. **GBP: Enable Places API (New) in Google Cloud Console** - The Google Maps API key
   currently fails "Places API: FAIL" (key not authorized). Must enable "Places API (New)"
   (not legacy) at APIs & Services > Library in Google Cloud Console for the onboarding
   GBP lookup to work end-to-end.

3. **Fix Site Generator SEO Issues (content)** - Generated pages score D/F. Primary
   issues: keywords missing from H1 tags, thin product page content, meta descriptions
   too long. Template or AI prompt improvements needed.

---

## Current State

**Git:**
- Branch: main
- Version: 4.0.0
- Working tree: clean after this session's commit
- All changes committed and pushed

**Tests:**
- 85 onboarding unit tests: PASSING
- Full suite (prior baseline): 852 passed, 77 failed (pre-existing failures in
  test_template_preview.py and test_template_validator.py - not related to this work)

**Onboard command usage:**
```cmd
python -m src.cli onboard -u https://example.com/ -i "plumbing" -g "https://maps.app.goo.gl/..."
```

**Blockers:**
- Google Maps API key needs "Places API (New)" enabled in Google Cloud Console
  (Geocoding and legacy Places API are also failing - same key, same restriction issue)

**Known Issues:**
- CLI deploy command is a stub (BACK-007)
- SEO content quality still low (keyword density, thin product pages)
- SABs completely unlisted in Places text search return no GBP data (graceful warning)
- Cost display shows $0.0000 instead of actual cost - LOW priority

---

## Key Context Notes

1. **Config directory is gitignored** - All client YAML configs (`config/clients/**`)
   are not tracked. Onboard command writes configs there. Florida config is local only.

2. **Auto-onboarding output** - Written to `config/clients/<slug>/<slug>_config.yaml`.
   Always overwrites if re-run (no prompt). Validate with `awg validate --config <file>`.

3. **Places API (New) vs legacy** - The onboarding GBP client uses the NEW API
   (`places.googleapis.com/v1/`, `X-Goog-Api-Key` header, POST searchText). The old
   legacy API (`maps.googleapis.com/maps/api/place/`) is NOT used anywhere in this project.

---

## Quick Reference

**Auto-onboard a client:**
```cmd
python -m src.cli onboard -u https://camphousecountrylandscaping.com/ -i landscaping -g "https://maps.app.goo.gl/..."
```

**Generate Florida site:**
```cmd
python -m src.cli generate -c "config/clients/Clean Restroom Rentals/clean_restroom_rental_florida_config.yaml" -o "output/clients/clean_restroom_rental_fl" --no-ai
```

**Run SEO analysis:**
```cmd
python -m src.cli analyze content "output/clients/clean_restroom_rental_fl/index.html" -k "portable restroom rental florida" --model balanced
```

**Model Presets:**
- fast: Claude Haiku 4.5 (~$0.01/page)
- balanced: Claude Sonnet 4.5 (~$0.025/page) - DEFAULT
- thorough: Claude Opus 4.6 (~$0.15/page)

---

**For Phase 1 details:** See `docs/phase1-multi-cloud-implementation.md`
**For Phase 2 demo:** See `docs/phase2-seo-analysis-demo.md`
**For full backlog:** See `docs/project-backlog.yaml`
