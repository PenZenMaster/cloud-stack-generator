# AWG Startup Context

**Last Updated:** 2026-01-11
**Branch:** main
**Last Commit:** fd5a275

---

## Last 3 Accomplishments

1. **Fixed GCS Validation Bug** - Cloud Deploy tab now correctly validates GCS-specific fields (Project ID, Service Account JSON) when Google Cloud Storage is selected; no longer shows incorrect "S3 Bucket Name Required" error

2. **Closed GitHub Issue #14 - city_page_image_pool Bug** - QA verified fix in parser.py:637; city page images now correctly saved to YAML config and assigned to city pages during generation

3. **XML Sitemap Enhancement QA Verified** - Confirmed in production: sitemap.xml contains correct CloudFront URLs, all city pages included, industry-standard priority/changefreq values working correctly

---

## Next 3 Priorities

1. **TBD** - Awaiting next feature request or bug report

2. **TBD** - Ready for new tasks

3. **TBD** - Ready for new tasks

---

## Current State

**Git Status:**
- Branch: main (up to date with origin/main)
- Working tree: Clean (only .claude/settings.local.json modified - local config)
- Last commit: fd5a275 (sitemap enhancement)
- Push status: All commits pushed
- Version: 3.6.2

**Tests:**
- All 113 cloud infrastructure tests passing
- Pre-commit hooks passing
- Black formatting applied

**Blockers:**
- None

---

## Key Context Notes

1. **Sitemap Enhancement (fd5a275) - MAJOR SEO IMPROVEMENT:**
   - **Coverage**: Added missing city pages and privacy-policy.html to sitemap (was ~10 URLs, now 10-50+ depending on city count)
   - **Priority Levels**: Homepage 1.0, hubs 0.8, details 0.7, info 0.6, legal 0.4 (Google/Bing best practices)
   - **Change Frequency**: Weekly (homepage), monthly (most pages), yearly (privacy)
   - **URL Fix**: Sitemap now uses deployment URL (CloudFront/S3) instead of business.domain fallback
   - **Auto-Regeneration**: After deployment, sitemap.xml regenerates with correct URL and re-uploads to S3

2. **Sitemap Deployment Flow (Mode A & B):**
   - Initial site generation creates sitemap with business.domain (temporary)
   - After S3/CloudFront deployment completes, `_update_config_and_sitemap_for_deployment()` runs
   - Config updated with deployment_url, sitemap regenerated with correct URLs, uploaded to S3
   - Result: `https://d3s4htkdtt2ze0.cloudfront.net/sitemap.xml` contains CloudFront URLs, not librami.com

3. **Deployment Mode Behavior (CRITICAL):**
   - Mode A (S3 Static Website): Bucket configured for public access with public policy
   - Mode B (CloudFront + OAC): Bucket kept private, CloudFront accesses via OAC policy, public blocks enabled
   - Both modes now properly update sitemap with deployment URL post-deployment

---

**For full checkpoint details:** See `docs/archive/checkpoints/CheckPoint-2026-01-10_1908.md`
