# AWG Startup Context

**Last Updated:** 2026-01-10
**Branch:** main
**Last Commit:** ae1bb02

---

## Last 3 Accomplishments

1. **Fixed GitHub Issue #18 - Mode B CloudFront 403 Errors** - Resolved bucket policy conflict causing header images and logos to return 403 on CloudFront deployments (v3.6.2)

2. **Implemented Two-Part Security Fix** - Made bucket configuration conditional (Mode A vs Mode B) + added explicit public access blocking for Mode B after OAC setup

3. **Complete Root Cause Analysis** - Documented full technical RCA in GitHub issue #18 with verification steps and user instructions

---

## Next 3 Priorities

1. **User Verification of Fix** - Awaiting user to redeploy with Mode B and confirm: (a) all 4 public access blocks enabled, (b) CloudFront URL loads images, (c) deployment logs show success message

2. **Close GitHub Issue #18** - After user confirms successful verification of all checks

3. **Font Fix Testing** - User needs to change Branding tab font from "Impact" to readable font (Arial, Inter, Georgia) and verify city page regeneration

---

## Current State

**Git Status:**
- Branch: main (local commits not pushed)
- Working tree: Clean
- Last commits: ae1bb02, 2587b8a (both v3.6.2 fixes)
- Push status: Pending user verification before push
- Version: 3.6.2

**Tests:**
- All 113 cloud infrastructure tests passing
- Pre-commit hooks passing
- Black formatting applied

**Blockers:**
- None - awaiting user verification

---

## Key Context Notes

1. **GitHub Issue #18 Fix Details:**
   - Problem: Mode B deployments called `configure_public_website()` creating bucket policy conflict
   - Fix Part 1 (2587b8a): Made bucket config conditional - Mode A gets public config, Mode B skips it
   - Fix Part 2 (ae1bb02): Added explicit public access blocking after OAC setup with clear logging
   - User found blocks weren't enabled after Part 1, leading to Part 2 implementation

2. **Deployment Mode Behavior (CRITICAL):**
   - Mode A (S3 Static Website): Bucket configured for public access with public policy
   - Mode B (CloudFront + OAC): Bucket kept private, CloudFront accesses via OAC policy, public blocks enabled
   - These paths are now completely separated to prevent conflicts

3. **Expected Mode B Deployment Logs:**
   ```
   Mode B: Bucket will be configured for private access with CloudFront OAC
   Mode B: CloudFront + OAC deployment (auto-creating distribution...)
   CloudFront domain: d2e90hpz4khlyf.cloudfront.net
   Enabling public access blocks for private bucket...
   Public access blocks enabled - bucket is now private
   ```

---

**For full checkpoint details:** See `docs/archive/checkpoints/CheckPoint-2026-01-10_1908.md`
