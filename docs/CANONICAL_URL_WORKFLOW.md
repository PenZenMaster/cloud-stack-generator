# Canonical URL Workflow - Two-Pass Deployment

**Version**: 1.0
**Date**: 2025-11-28
**Feature**: Automatic canonical URL updates for CloudFront deployments

---

## Problem Solved

**Chicken-and-egg issue**: When deploying a website to CloudFront for the first time, we don't know the CloudFront URL until after deployment, but we need it to generate correct canonical tags.

**Impact**: Pages deployed to CloudFront had canonical tags pointing to different URLs, causing search engines to mark them as "Non-Indexable" with "Canonicalised" status.

---

## Solution: Two-Pass Deployment

### Workflow

**First Deployment:**
1. User generates website (canonical URLs use business.domain as fallback)
2. User deploys to CloudFront (Mode B)
3. System obtains CloudFront URL: `d8na4b3nx1cti.cloudfront.net`
4. **Automatic prompt appears** after successful deployment

**Prompt Dialog:**
```
Deployment Successful - Update Canonicals?

Website deployed successfully!

URL: https://d8na4b3nx1cti.cloudfront.net
Files uploaded: 27

CloudFront URL: https://d8na4b3nx1cti.cloudfront.net

Note: Canonical URLs in your site may not match the CloudFront URL.
Would you like to update canonical URLs and redeploy?

[Yes] [No]
```

**If user clicks Yes:**
1. System updates `config.cloud.deployment_url` in YAML file
2. System reloads config in UI
3. System prompts user to regenerate website
4. User regenerates (canonical URLs now use CloudFront URL)
5. User returns to Cloud Deploy tab and redeploys
6. CloudFront cache invalidation happens automatically
7. ✅ Site is now indexable with correct canonical URLs

---

## Code Changes

### 1. Canonical URL Logic (`src/core/generators/html_generator.py:332-345`)

**New simplified logic:**
```python
def _get_canonical_base_url(self, config: ClientConfig) -> str:
    """
    Canonical URLs should match where the site is actually deployed.
    If deployment_url is specified, use it (matches the deployed location).
    Otherwise, fallback to business.domain.
    """
    # Always prefer deployment_url if specified (canonical matches deployment)
    if config.cloud.deployment_url:
        return config.cloud.deployment_url.rstrip("/")

    # Fallback to business domain if no deployment URL specified
    return config.business.domain.rstrip("/")
```

**Result**: deployment_url always takes priority for canonical URLs, regardless of site type.

### 2. Post-Deployment Prompt (`src/ui/components/cloud_tab.py:2978-3025`)

Added logic in `deployment_finished()` method:
- Detects CloudFront deployments (Mode B)
- Checks if deployment_url is missing or different from CloudFront URL
- Shows prompt asking user to update canonical URLs
- Calls `_update_canonicals_and_redeploy()` if user agrees

### 3. Update and Regenerate Method (`src/ui/components/cloud_tab.py:3030-3129`)

New method `_update_canonicals_and_redeploy()`:
- Updates YAML config file with CloudFront URL
- Reloads config in UI
- Triggers website regeneration
- Guides user through redeploy process

---

## When Prompt Appears

The prompt **only appears** when:
1. **Deployment mode** is CloudFront (Mode B)
2. **CloudFront domain** was successfully obtained
3. **deployment_url** in config is either:
   - Empty/not set, OR
   - Different from the CloudFront URL

The prompt **does not appear** for:
- S3-only deployments (Mode A)
- When deployment_url already matches CloudFront URL
- Failed deployments

---

## User Experience

### Scenario 1: First Deployment
1. Load config (deployment_url is empty)
2. Generate website
3. Deploy to CloudFront
4. **Prompt appears** ✅
5. Click "Yes"
6. Config updated automatically
7. Regenerate website
8. Redeploy
9. Done!

### Scenario 2: Subsequent Deployments
1. Load config (deployment_url already set correctly)
2. Generate website (canonicals use CloudFront URL)
3. Deploy to CloudFront
4. **No prompt** (already correct)
5. Done!

### Scenario 3: Deploying to New CloudFront
1. Load config (deployment_url points to old CloudFront)
2. Generate website
3. Deploy to new CloudFront distribution
4. **Prompt appears** ✅ (URL changed)
5. Click "Yes"
6. Config updated to new CloudFront URL
7. Regenerate and redeploy
8. Done!

---

## Technical Details

### Config File Update
```yaml
cloud:
  deployment_url: 'https://d8na4b3nx1cti.cloudfront.net'
```

The system uses Python's PyYAML library to update the YAML file, preserving structure and comments.

### Canonical Tag Output
**Before update:**
```html
<link rel="canonical" href="https://pristineportablesil.com">
```

**After update:**
```html
<link rel="canonical" href="https://d8na4b3nx1cti.cloudfront.net">
```

### Sitemap Output
**Before update:**
```xml
<loc>https://pristineportablesil.com/</loc>
```

**After update:**
```xml
<loc>https://d8na4b3nx1cti.cloudfront.net/</loc>
```

---

## Benefits

✅ **Automatic detection** - System detects when update is needed
✅ **User control** - User can decline if not needed
✅ **Guided workflow** - Clear prompts guide user through process
✅ **Config persistence** - deployment_url saved for future use
✅ **SEO correct** - Canonical URLs match deployment location
✅ **Indexability** - Pages become indexable by search engines

---

## Future Enhancements

Potential improvements:
1. **Fully automatic regeneration** - Regenerate in background without user prompt
2. **Automatic redeployment** - Complete workflow without user intervention
3. **Rollback option** - Revert to previous deployment_url if needed
4. **Multi-deployment tracking** - Remember multiple CloudFront URLs

---

## Testing Checklist

- [ ] First deployment prompts for canonical update
- [ ] Clicking "Yes" updates config file
- [ ] Config reload works in UI
- [ ] Regeneration produces correct canonical URLs
- [ ] Redeployment works after regeneration
- [ ] Second deployment to same CloudFront doesn't prompt
- [ ] Deployment to different CloudFront prompts again
- [ ] Clicking "No" skips update workflow
- [ ] S3-only deployments don't trigger prompt

---

**Documentation**: CANONICAL_URL_WORKFLOW.md
**Author**: Rank Rocket Co Development Team
**Last Updated**: 2025-11-28
