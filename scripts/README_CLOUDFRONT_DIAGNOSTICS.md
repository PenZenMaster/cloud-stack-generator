# CloudFront Deployment Diagnostics

## Issue #12 - Enhanced Debugging

This document explains the diagnostic tools and enhanced logging added to debug CloudFront origin path issues.

## Problem Statement

After deploying to an S3 subdirectory (e.g., `clean-restroom-rentals-va/`), CloudFront was still returning 404 errors:
- S3 direct URL works: `https://bucket.s3.amazonaws.com/directory/index.html`
- CloudFront URL fails: `https://distribution.cloudfront.net/` (looking for `index.html` at root)

## Enhanced Deployment Logging

The deployment UI now shows detailed CloudFront update status:

### Success Output Example
```
Files uploaded successfully (123 files)
[CloudFront] Updating origin path to: /clean-restroom-rentals-va
[CloudFront] CloudFront origin path updated to: /clean-restroom-rentals-va
[CloudFront] NOTE: Changes may take 2-15 minutes to propagate
```

### Error Output Example
```
Files uploaded successfully (123 files)
[CloudFront] Updating origin path to: /clean-restroom-rentals-va
[CloudFront] ERROR: CloudFront update failed (AccessDenied): ...
```

### Conditions Not Met Example
If you don't see `[CloudFront]` messages, check:
- Distribution ID is configured in UI
- Directory is NOT set to "/ (root)"
- Upload succeeded

## Diagnostic Script

Use `check_cloudfront_config.py` to verify the current CloudFront configuration:

### Usage

```bash
# Basic usage with default AWS profile
python scripts/check_cloudfront_config.py E1234DISTRIBUTION

# With custom AWS profile
python scripts/check_cloudfront_config.py E1234DISTRIBUTION awg-cloud-stack
```

### Example Output

```
Checking CloudFront distribution: E1234DISTRIBUTION
Using AWS profile: awg-cloud-stack
------------------------------------------------------------

Origin Count: 1

Origin Details:

  Origin 0:
    ID: S3-portable-sanitation-solutions
    Domain: portable-sanitation-solutions.s3.amazonaws.com
    Origin Path: '/clean-restroom-rentals-va'
    Type: S3
    OAI: origin-access-identity/cloudfront/...

Default Root Object: 'index.html'

Distribution Status: Deployed

============================================================
DIAGNOSIS:
============================================================
Origin Path is: /clean-restroom-rentals-va
CloudFront URL will serve: https://[domain]/index.html
Maps to S3 key: clean-restroom-rentals-va/index.html

```

## Troubleshooting Steps

### 1. Check Deployment Output
Look for `[CloudFront]` messages in the deployment result window.

**If you see:**
- `[CloudFront] CloudFront origin path updated to: /...` - Update succeeded
- `[CloudFront] ERROR: ...` - Update failed (check AWS permissions)
- No `[CloudFront]` messages - Update was not attempted (check conditions)

### 2. Verify CloudFront Configuration
```bash
python scripts/check_cloudfront_config.py YOUR_DISTRIBUTION_ID YOUR_AWS_PROFILE
```

**Check that:**
- Origin Path matches your S3 directory (e.g., `/clean-restroom-rentals-va`)
- Distribution Status is "Deployed" (not "InProgress")

### 3. Wait for Propagation
If the update succeeded but CloudFront still returns 404:
- **Wait 2-15 minutes** for changes to propagate across CloudFront edge locations
- Run the diagnostic script again to verify the origin path was actually updated

### 4. Clear CloudFront Cache
If origin path is correct but old content is cached:
- Enable "Auto Invalidate Cache" checkbox in deployment UI, OR
- Manually invalidate cache: `/*` (all files)

### 5. Check AWS Permissions
If update fails with `AccessDenied`:
- Verify AWS credentials have `cloudfront:GetDistributionConfig` permission
- Verify AWS credentials have `cloudfront:UpdateDistribution` permission

## Understanding Origin Path

CloudFront Origin Path tells CloudFront where to look in the S3 bucket:

| Origin Path | User Requests | S3 Key Accessed |
|------------|---------------|-----------------|
| (empty) | `/index.html` | `index.html` |
| `/directory` | `/index.html` | `directory/index.html` |
| `/directory` | `/about.html` | `directory/about.html` |

## Common Issues

### Issue: "Changes may take 2-15 minutes to propagate"
- **Solution:** Wait. CloudFront distributes configuration to edge locations globally.
- **Check:** Run diagnostic script periodically to verify status becomes "Deployed"

### Issue: "No origins found in CloudFront distribution"
- **Solution:** CloudFront distribution is misconfigured. Check AWS Console.

### Issue: "CloudFront update failed (PreconditionFailed)"
- **Cause:** Another update is in progress or ETag mismatch
- **Solution:** Wait 1 minute and try deployment again

### Issue: Still getting 404 after successful update
- **Possible causes:**
  1. Propagation delay (wait 2-15 minutes)
  2. Cached 404 response (invalidate cache)
  3. Files not actually in S3 directory (check S3 directly)
  4. Default root object not configured (should be `index.html`)

## Testing Checklist

After deployment:

- [ ] Check deployment output for `[CloudFront]` success message
- [ ] Verify S3 direct URL works: `https://bucket.s3.amazonaws.com/directory/index.html`
- [ ] Run diagnostic script to confirm origin path: `python scripts/check_cloudfront_config.py ...`
- [ ] Wait 2-15 minutes if distribution status is "InProgress"
- [ ] Test CloudFront URL: `https://distribution.cloudfront.net/`
- [ ] If still 404, create cache invalidation for `/*`

## Log Files

Application logs contain detailed deployment information:
- Windows: `%APPDATA%\Local\cloud-stack-generator\logs\`
- Check for: "Updating CloudFront origin path", "CloudFront update failed"
