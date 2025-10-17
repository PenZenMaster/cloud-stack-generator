# AWS CloudFront Permissions Setup for HTTPS

## Issue
CloudFront setup fails with AccessDenied error:
```
User: arn:aws:iam::924880149471:user/awg-cloud-stack is not authorized to perform: cloudfront:CreateDistribution because no identity-based policy allows the cloudfront:CreateDistribution action
```

## Required CloudFront Permissions

The AWS IAM user needs the following CloudFront permissions for HTTPS website deployment:

### Required Permissions Policy
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateDistribution",
                "cloudfront:GetDistribution",
                "cloudfront:ListDistributions",
                "cloudfront:UpdateDistribution",
                "cloudfront:DeleteDistribution",
                "cloudfront:GetDistributionConfig",
                "cloudfront:CreateInvalidation",
                "cloudfront:GetInvalidation",
                "cloudfront:ListInvalidations"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "acm:ListCertificates",
                "acm:DescribeCertificate"
            ],
            "Resource": "*"
        }
    ]
}
```

### How to Apply Permissions

#### Option 1: AWS Console (Recommended)
1. Log into AWS IAM Console
2. Navigate to Users → `awg-cloud-stack`
3. Click "Add permissions" → "Attach existing policies directly"
4. Create new policy with the JSON above
5. Name it "CloudStackCloudFrontAccess"
6. Attach to the user

#### Option 2: AWS CLI
```bash
# Create policy file
cat > cloudfront-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateDistribution",
                "cloudfront:GetDistribution",
                "cloudfront:ListDistributions",
                "cloudfront:UpdateDistribution",
                "cloudfront:DeleteDistribution",
                "cloudfront:GetDistributionConfig",
                "cloudfront:CreateInvalidation",
                "cloudfront:GetInvalidation",
                "cloudfront:ListInvalidations"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "acm:ListCertificates",
                "acm:DescribeCertificate"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Create and attach policy
aws iam create-policy --policy-name CloudStackCloudFrontAccess --policy-document file://cloudfront-policy.json
aws iam attach-user-policy --user-name awg-cloud-stack --policy-arn arn:aws:iam::924880149471:policy/CloudStackCloudFrontAccess
```

## Why These Permissions Are Needed

### Core CloudFront Operations
- `cloudfront:CreateDistribution` - Create new CloudFront distributions for HTTPS
- `cloudfront:ListDistributions` - Check existing distributions to avoid duplicates
- `cloudfront:GetDistribution` - Retrieve distribution details and status
- `cloudfront:UpdateDistribution` - Modify distribution settings
- `cloudfront:DeleteDistribution` - Clean up distributions when needed

### Cache Management
- `cloudfront:CreateInvalidation` - Clear cached files when website updates
- `cloudfront:GetInvalidation` - Check invalidation status
- `cloudfront:ListInvalidations` - Manage cache clearing operations

### SSL Certificate Support
- `acm:ListCertificates` - Find available SSL certificates
- `acm:DescribeCertificate` - Get certificate details for HTTPS setup

## Alternative: HTTP-Only Deployment

If CloudFront permissions cannot be granted immediately, the application will fall back to HTTP-only S3 static website hosting. This provides:

- ✅ Functional website deployment
- ✅ S3 static website hosting
- ❌ No HTTPS encryption
- ❌ No global CDN acceleration

## Security Note

CloudFront permissions have broad access scope. In production environments, consider:

1. **Resource restrictions** - Limit to specific distribution ARNs if possible
2. **Condition-based access** - Add IP or time-based restrictions
3. **Regular auditing** - Monitor CloudFront usage and costs
4. **Least privilege** - Remove permissions when not actively deploying

## Testing After Permission Grant

After applying permissions, test CloudFront functionality:

1. Generate website with HTTPS option enabled
2. Verify CloudFront distribution creation
3. Check SSL certificate association
4. Validate HTTPS website accessibility
5. Test cache invalidation on updates

## Troubleshooting CloudFront Access Issues

If you get "This site can't be reached" errors:

### 1. Check Distribution Status
```bash
# List distributions to check status
aws cloudfront list-distributions --query "DistributionList.Items[?Comment=='Cloud Stack Generator Website'].[Id,Status,DomainName]" --output table
```

Distribution must show **Status: Deployed** before it's accessible. Initial deployment takes 15-20 minutes.

### 2. Verify S3 Origin Configuration
```bash
# Check if S3 bucket is configured for website hosting
aws s3api get-bucket-website --bucket YOUR_BUCKET_NAME
```

S3 bucket must have static website hosting enabled with proper index document.

### 3. Check Distribution Configuration
```bash
# Get distribution details
aws cloudfront get-distribution --id YOUR_DISTRIBUTION_ID
```

Verify:
- **Origins**: Points to S3 bucket website endpoint (not bucket itself)
- **Default Cache Behavior**: Allows GET and HEAD methods
- **Status**: Shows "Deployed"

### 4. Test S3 Website Directly
```bash
# Test S3 website endpoint directly
curl -I http://YOUR_BUCKET.s3-website-REGION.amazonaws.com
```

If S3 website returns 403/404, the bucket or files aren't properly configured.

### 5. Common Fixes

**Distribution Still Deploying**:
- Wait 15-20 minutes for initial deployment
- Check AWS Console CloudFront section for status

**S3 Origin Misconfiguration**:
- Ensure origin points to S3 **website endpoint**, not bucket
- Format: `bucket-name.s3-website-region.amazonaws.com`
- NOT: `bucket-name.s3.region.amazonaws.com`

**Bucket Policy Issues**:
- Verify S3 bucket has public read policy
- Check bucket website hosting is enabled

**DNS Propagation**:
- Try accessing from different networks/devices
- Use `nslookup cloudfront-domain.net` to check DNS resolution

This will enable full HTTPS deployment with global CDN acceleration for optimal website performance and security.