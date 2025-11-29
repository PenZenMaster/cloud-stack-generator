# Canonical URL Workflow - Test-File-First Deployment

**Version**: 2.0
**Date**: 2025-11-28
**Feature**: Automatic canonical URL setup via test file deployment

---

## Problem Solved

**Chicken-and-egg issue**: When deploying a website to CloudFront for the first time, we don't know the CloudFront URL until after deployment, but we need it to generate correct canonical tags.

**Impact**: Pages deployed to CloudFront with incorrect canonical tags get marked as "Non-Indexable" by search engines with "Canonicalised" status.

---

## Solution: Test-File-First Deployment

### Workflow Overview

Instead of deploying the full website twice, the system deploys a small test file first to determine the CloudFront URL, then generates the website with correct canonical URLs from the start.

**Key Benefit**: Only ONE full website deployment needed (instead of two).

---

## First-Time Deployment Workflow

**Step 1: User initiates deployment**
- User clicks "Deploy to Cloud" button
- System detects no website has been generated yet
- System shows confirmation dialog

**Step 2: Test file deployment**
- User selects output folder
- System deploys a small test.html file to S3
- System creates or finds CloudFront distribution
- System retrieves CloudFront URL: `https://d8na4b3nx1cti.cloudfront.net`

**Step 3: Config update**
- System automatically updates config file
- Sets `cloud.deployment_url` to CloudFront URL
- Reloads config in UI

**Step 4: Website generation**
- System triggers website generation
- User selects the output folder (same as Step 2)
- Website is generated with correct canonical URLs from the start

**Step 5: Full deployment**
- User returns to Cloud Deploy tab
- User clicks "Deploy Website" again
- Full website is deployed to CloudFront
- Deployment confirmation shown
- DONE!

**Result**: Website has correct canonical URLs in a single deployment.

---

## Subsequent Deployment Workflow

**Step 1: User initiates deployment**
- User clicks "Deploy to Cloud" button
- System detects website already exists

**Step 2: Regeneration confirmation**
- System shows confirmation dialog
- User clicks OK to continue

**Step 3: Website regeneration**
- System triggers website regeneration
- User confirms output folder (pre-filled)
- Website is regenerated with latest config

**Step 4: Deployment**
- User returns to Cloud Deploy tab
- User clicks "Deploy Website" again
- Website is redeployed
- DONE!

---

## Code Changes

### 1. Canonical URL Logic (Unchanged)

The canonical URL logic from v1.0 remains the same:

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

### 2. Deployment Workflow (`src/ui/components/cloud_tab.py:2613-2626`)

Modified `start_deployment()` to detect first vs. subsequent deployment:

```python
def start_deployment(self):
    """Start website deployment - implements test-file-first workflow"""
    local_path = self.local_path_input.text().strip()

    # Check if this is first deployment (no website generated yet)
    if not local_path or not Path(local_path).exists():
        # First deployment workflow: test file -> generate -> deploy
        self._handle_first_deployment()
    else:
        # Subsequent deployment: regenerate -> deploy
        self._handle_subsequent_deployment(local_path)
```

### 3. First Deployment Handler (`src/ui/components/cloud_tab.py:2628-2740`)

New method `_handle_first_deployment()`:
- Shows confirmation dialog with workflow explanation
- User selects output folder
- Deploys test file to get CloudFront URL
- Updates config with CloudFront URL
- Triggers website generation with instructions
- User completes generation and returns to deploy

### 4. Test File Deployment (`src/ui/components/cloud_tab.py:2782-2879`)

New method `_deploy_test_file_and_get_url()`:
- Creates temporary test.html file
- Configures S3 bucket for static hosting
- Creates or finds CloudFront distribution
- Uploads test file to S3
- Returns CloudFront URL

### 5. Config Update (`src/ui/components/cloud_tab.py:2881-2925`)

New method `_update_config_deployment_url()`:
- Loads YAML config file
- Updates `cloud.deployment_url` field
- Saves config file
- Reloads config in UI

### 6. Subsequent Deployment Handler (`src/ui/components/cloud_tab.py:2742-2786`)

New method `_handle_subsequent_deployment()`:
- Shows regeneration confirmation dialog
- Triggers website regeneration
- Guides user to redeploy after generation

---

## Removed Code

### Two-Pass Deployment Logic (REMOVED)

The following code was removed from `deployment_finished()`:
- Post-deployment prompt for canonical URL update
- `_update_canonicals_and_redeploy()` method
- Endless loop prevention flags

These are no longer needed because the test-file-first approach prevents the problem entirely.

---

## User Experience Comparison

### Old Workflow (v1.0 - Two-Pass)
1. Generate website (wrong canonicals)
2. Deploy to CloudFront (FULL DEPLOYMENT #1)
3. Prompt appears
4. Click Yes
5. Config updated
6. Regenerate website (correct canonicals)
7. Redeploy to CloudFront (FULL DEPLOYMENT #2)
8. Done!

**Total full deployments**: 2

### New Workflow (v2.0 - Test-File-First)
1. Click Deploy
2. Select output folder
3. Test file deployed (small file)
4. Config updated automatically
5. Generate website (correct canonicals from start)
6. Deploy to CloudFront (FULL DEPLOYMENT #1)
7. Done!

**Total full deployments**: 1

---

## Benefits Over Two-Pass Approach

Faster deployment - Only one full deployment instead of two
Simpler workflow - No prompts or manual config updates
Lower cost - Less data transfer to S3/CloudFront
Better UX - Automated and straightforward
Fewer errors - Less room for user mistakes
Correct from start - Canonical URLs right the first time

---

## Technical Details

### Test File Content

```html
<!DOCTYPE html>
<html>
<head>
    <title>Test Deployment</title>
</head>
<body>
    <h1>CloudFront Test File</h1>
    <p>This is a test file to determine the CloudFront distribution URL.</p>
</body>
</html>
```

The test file is uploaded to `test.html` at the root of the deployment directory.

### Config File Update

```yaml
cloud:
  deployment_url: 'https://d8na4b3nx1cti.cloudfront.net'
```

The system uses Python's PyYAML library to update the YAML file, preserving structure and comments.

### Canonical Tag Output

Since the config is updated before generation, canonical tags are correct from the first deployment:

```html
<link rel="canonical" href="https://d8na4b3nx1cti.cloudfront.net">
```

### Sitemap Output

```xml
<loc>https://d8na4b3nx1cti.cloudfront.net/</loc>
```

---

## Deployment Modes

### Mode A (S3-only)

The test-file-first workflow is **not used** for Mode A deployments since:
- S3 URLs are predictable (bucket name + region)
- No CloudFront distribution involved
- No canonical URL discovery needed

For Mode A, users should manually set `deployment_url` in config before generating.

### Mode B (CloudFront + OAC)

The test-file-first workflow is **automatically used** for Mode B when:
- No website has been generated yet
- `local_path` is empty or doesn't exist

---

## Testing Checklist

- [x] First deployment deploys test file successfully
- [x] CloudFront URL is correctly retrieved
- [x] Config file is updated with CloudFront URL
- [x] Website generation uses correct canonical URLs
- [x] Full deployment succeeds after generation
- [x] Subsequent deployments show regeneration confirmation
- [x] Test file deployment handles errors gracefully
- [x] S3-only deployments (Mode A) work as before

---

## Future Enhancements

Potential improvements:

1. **Fully automatic workflow** - Trigger generation and deployment without manual steps
2. **Custom domain support** - Update canonicals when custom domain is configured
3. **Multi-region support** - Handle CloudFront edge locations
4. **Deployment history** - Track all deployments and CloudFront URLs
5. **Test file cleanup** - Option to remove test.html after deployment

---

## Migration from v1.0 to v2.0

**Breaking Changes**: None

**Behavior Changes**:
- First deployment now uses test-file-first workflow
- No more post-deployment prompts for canonical URL updates
- Slightly different user workflow (test file before generation)

**Config Compatibility**: Fully compatible with existing configs

**User Action Required**: None - existing configs work as-is

---

**Documentation**: CANONICAL_URL_WORKFLOW.md
**Author**: Rank Rocket Co Development Team
**Last Updated**: 2025-11-28
**Version**: 2.0 (Test-File-First)
