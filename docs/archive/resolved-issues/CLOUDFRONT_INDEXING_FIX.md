# CloudFront Indexing Fix

## Issue
Pages are showing as "Non-Indexable" despite having correct HTML meta tags (`<meta name="robots" content="index, follow">`).

## Root Cause
CloudFront Response Headers Policy may be adding `X-Robots-Tag: noindex` header or other blocking headers.

## Solution

### 1. Check CloudFront Response Headers Policy

1. Go to AWS CloudFront Console
2. Find your distribution: `d2lcpb9bumubgm.cloudfront.net`
3. Go to **Behaviors** tab
4. Edit the default behavior
5. Scroll to **Response headers policy**
6. Check if a custom policy is attached
7. If attached, click to view the policy settings

### 2. Remove or Update Response Headers Policy

**Option A: Remove the policy** (simplest)
- Set Response headers policy to "None"

**Option B: Update the policy** (if you need it for other headers)
- Go to **Security headers**
- Ensure there is NO `X-Robots-Tag` header set to `noindex`
- If present, remove it or change to `index, follow`

### 3. Re-deploy Website with Updated Headers

The deployment code has been updated to include proper cache-control headers.

Run the deployment again:
```bash
python src/core/deployment/s3_deployer.py
```

Or from Python:
```python
from src.core.deployment.s3_deployer import deploy_client_website
deploy_client_website("salvo_metal_works")
```

### 4. Invalidate CloudFront Cache

After making changes:
```bash
aws cloudfront create-invalidation --distribution-id YOUR_DISTRIBUTION_ID --paths "/*" --profile AWS
```

### 5. Verify Fix

Test with a crawler or SEO tool:
- Check HTTP response headers for `X-Robots-Tag`
- Verify pages now show as "Indexable"
- Confirm canonical tags are still present and correct

## Updated Deployment Features

The S3 deployer now sets:
- **Static assets** (CSS, JS, images): `Cache-Control: public, max-age=31536000` (1 year)
- **HTML files**: `Cache-Control: public, max-age=3600` (1 hour)

This ensures:
- Better performance
- Proper cache behavior for SEO crawlers
- Easy content updates (short HTML cache)
