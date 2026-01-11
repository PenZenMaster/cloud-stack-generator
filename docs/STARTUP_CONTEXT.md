# AWG Startup Context

**Last Updated:** 2026-01-11
**Branch:** main
**Last Commit:** fd5a275

---

## Last 3 Accomplishments

1. **Closed GitHub Issue #18** - QA verified Mode B CloudFront fix, pushed commits, closed issue with comprehensive RCA summary (v3.6.2)

2. **Enhanced sitemap.xml with Complete Coverage** - Added city pages and privacy policy to sitemap, implemented industry-standard priority levels (1.0-0.4) and changefreq values per sitemaps.org protocol 0.9

3. **Fixed Sitemap Deployment URL Bug** - Sitemap URLs now use correct CloudFront/S3 deployment URLs instead of business domain fallback; auto-regenerates and uploads sitemap.xml after both Mode A & B deployments

---

## Next 3 Priorities

1. **User Testing of Sitemap Enhancement** - Next deployment will automatically regenerate sitemap.xml with correct CloudFront URL and include all city pages

2. **Font Fix Testing** - User needs to change Branding tab font from "Impact" to readable font (Arial, Inter, Georgia) and verify city page regeneration

3. **Monitor Sitemap in Production** - Verify sitemap.xml at deployment URL contains CloudFront domain and all pages (city pages, privacy policy)

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
