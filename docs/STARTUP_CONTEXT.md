# AWG Startup Context
**Last Updated**: November 28, 2025
**Branch**: feature/v3.5.0-ui-improvements
**Last Commit**: 3f4c499

---

## Last 3 Accomplishments

1. **v3.6.0 - Canonical URL & Backlink Site Support** ✅
   - Added site_type field (main_site/backlink_site) to CloudConfig
   - Created UI controls in Cloud Deploy tab (SEO Configuration section)
   - Updated canonical URL logic to support backlink sites pointing to main site

2. **v3.7.0 - Schema Enhancements** ✅
   - Added breadcrumb schema to 6 missing page templates (about, contact, services, products, service-detail, product-detail)
   - Fixed product schema validation (always include offers + aggregateRating)
   - Resolved 10+ Google Rich Results validation errors

3. **QA Testing Passed** ✅
   - User confirmed all product schema errors resolved
   - Canonical URL workflow tested and working
   - All changes committed and pushed to feature branch

---

## Next 3 Priorities

1. **Test Google Rich Results** - Validate all schema changes in production
2. **Priority #3: Error Logging & Monitoring** - Implement structured logging framework
3. **Priority #4: FAQ System Enhancements** - Bulk import/export, category management

---

## Current State

**Git Status**: Clean (working tree clean, all changes pushed)
**Tests**: 113/113 passing ✅
**Branch**: feature/v3.5.0-ui-improvements
**Latest Commits**:
- 3f4c499 - chore: Add *.zip and docs/webgen.txt to .gitignore
- 9b09d2f - feat(schema): Add breadcrumb schema + fix product validation (v3.7.0)
- 89196f8 - feat(canonical): Add backlink site support with configurable canonical URLs (v3.6.0)

**No Blockers** - All features working, QA passed

---

## Key Context Notes

1. **Schema Coverage Complete**: All page types now have breadcrumb schema, product schema includes offers + rating for Google validation
2. **Backlink Site Workflow**: User workflow is Scenario 2 - backlink sites point to main CloudFront URL (cannot deploy to custom domains yet)
3. **UI Responsiveness**: Minor issue with SEO Configuration section at default window size - added to backlog as LOW priority
4. **Google Search Console**: User already knows how to set up GSC - removed from priorities

---

## Model Configuration

User switched to **Opus 4.5** in settings.json - next session will use Opus for deeper reasoning capability.
