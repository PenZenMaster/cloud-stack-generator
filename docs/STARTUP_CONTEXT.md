# AWG Startup Context

**Last Updated:** 2026-03-21
**Branch:** feature/onboarding-gbp-fix
**Version:** 4.0.0
**Last Commit:** (see git log) - feat(deploy): BACK-007 - awg deploy command + 14 unit tests

---

## Last 3 Accomplishments

1. **BACK-007: awg deploy command** - `sync_to_s3()` in `s3_deployer.py` (v1.01)
   fully implemented: uploads all local files, deletes S3 orphans (batch 1000),
   correct ContentType + CacheControl headers (HTML vs assets), CloudFront `/*`
   invalidation when `auto_invalidate_cache: true`, `--dry-run` plan output.
   CLI `deploy` command wired in `cli.py`. 14/14 unit tests PASSING.

2. **GBP Place ID Resolution Fixed (v1.07)** - `gbp_client.py` resolves GBP
   share links via `places:searchNearby` with exact `!3d`/`!4d` coords.
   Progressive radius (50m->200m->1000m), name validation, HTML fallback,
   direct ChI input (-g flag). Rank Rocket QA confirmed PASS.

3. **Unit Tests Expanded: 30 -> 71 -> 85** - GBP client 71 tests + 14 new
   deploy sync tests. All 85 pass.

---

## Next 3 Priorities

1. **Merge feature/onboarding-gbp-fix -> main** - BACK-007 done, GBP v1.07 done.
   Update CHANGELOG, bump version (4.0.0 -> 4.1.0 or keep 4.0.0), open PR.

2. **QA: Test Camphouse Country Landscaping GBP lookup** - SAB still unresolved
   via Places API. Try direct Place ID via `-g ChIJ...` from the Google Maps URL
   to confirm full pipeline works for a SAB client.

3. **SEO content quality** - Keyword density low, product pages thin. Next sprint
   focus after branch merge.

---

## Current State

**Git:**
- Branch: feature/onboarding-gbp-fix
- Version: 4.0.0
- Last commit: e73b03c (pushed)
- Clean after BACK-007 commit
- Untracked (non-code): docs/qa*.txt, docs/qa1.png (QA artifacts, not committed)

**Tests:**
- Deploy sync: 14/14 PASSING
- GBP client: 71/71 PASSING
- Total: 85 tests PASSING
- Known pre-existing failures: test_ai_content_service.py (circular import)
  -> use --ignore=tests/unit/test_ai_content_service.py

**Blockers:**
- Camphouse Country Landscaping (SAB) unresolved via GBP API. Try direct Place ID.

**Known Issues:**
- CLI deploy command is a stub (BACK-007)
- SEO content quality still low (keyword density, thin product pages)
- Cost display shows $0.0000 instead of actual cost - LOW priority

---

## Key Context Notes

1. **Places API (New) behavior** - HTTP 200 + `{}` response = no results (NOT
   an auth error). Auth errors return 403. The API key (AWG key in Google Cloud
   Console) has Places API (New) enabled and confirmed working for businesses
   with physical pins (Rank Rocket QA PASS).

2. **GBP lookup strategy (v1.07 flow)**:
   1. Direct ChI... input (-g flag) -> skip all lookups
   2. ChIJ Place ID in URL data block (!1sChIJ...)
   3. HTML payload extraction (fetch Maps page, parse for ChI...)
   4. searchNearby at exact !3d/!4d coords (50m -> 200m -> 1000m) with name validation
   5. searchText by business name (biased -> unbiased SAB retry)

3. **Config directory is gitignored** - All client YAML configs (`config/clients/**`)
   are not tracked. Onboard command writes configs there.

---

## Quick Reference

**Auto-onboard (standard):**
```cmd
python -m src.cli onboard -u https://rankrocket.co/ -i "SEO Agency" -g "https://maps.app.goo.gl/rXeonmqPNnkCjHYh8"
```

**Auto-onboard with direct Place ID:**
```cmd
python -m src.cli onboard -u https://example.com/ -i "Industry" -g "ChIJabc123..."
```

**Run GBP tests:**
```cmd
python -m pytest tests/unit/test_onboarding_gbp_client.py -q
```

**Model Presets:**
- fast: Claude Haiku 4.5 (~$0.01/page)
- balanced: Claude Sonnet 4.5 (~$0.025/page) - DEFAULT
- thorough: Claude Opus 4.6 (~$0.15/page)

---

**For Phase 1 details:** See `docs/phase1-multi-cloud-implementation.md`
**For Phase 2 demo:** See `docs/phase2-seo-analysis-demo.md`
**For full backlog:** See `docs/project-backlog.yaml`
