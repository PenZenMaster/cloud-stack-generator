# AWS CloudFront Permissions Setup for HTTPS

## Issue
CloudFront setup fails with AccessDenied error:
```
User: arn:aws:iam::XXXXXXXXXXXX:user/your-user is not authorized to perform: cloudfront:CreateDistribution because no identity-based policy allows the cloudfront:CreateDistribution action
```

## When Do You Need CloudFront?

CloudFront is **optional** and provides these benefits:
- ✅ **HTTPS/SSL** - Secure encrypted connections
- ✅ **Global CDN** - Fast content delivery worldwide
- ✅ **Custom Domains** - Use your own domain name
- ✅ **DDoS Protection** - AWS Shield Standard included

**If you don't need these features**, you can skip CloudFront and use S3-only hosting (HTTP only).

---

## Required CloudFront Permissions

The AWS IAM user needs the following CloudFront permissions for HTTPS website deployment:

### Option 1: Least-Privilege CloudFront Policy (RECOMMENDED)

This policy grants **only** the permissions needed for Cloud Stack Generator:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudFrontDistributionManagement",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateDistribution",
                "cloudfront:GetDistribution",
                "cloudfront:GetDistributionConfig",
                "cloudfront:ListDistributions",
                "cloudfront:UpdateDistribution",
                "cloudfront:DeleteDistribution",
                "cloudfront:TagResource",
                "cloudfront:UntagResource",
                "cloudfront:ListTagsForResource"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "us-east-1"
                }
            }
        },
        {
            "Sid": "CloudFrontCacheInvalidation",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateInvalidation",
                "cloudfront:GetInvalidation",
                "cloudfront:ListInvalidations"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ACMCertificateReadOnly",
            "Effect": "Allow",
            "Action": [
                "acm:ListCertificates",
                "acm:DescribeCertificate",
                "acm:GetCertificate"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "us-east-1"
                }
            }
        },
        {
            "Sid": "CloudFrontOriginAccessIdentity",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateCloudFrontOriginAccessIdentity",
                "cloudfront:GetCloudFrontOriginAccessIdentity",
                "cloudfront:ListCloudFrontOriginAccessIdentities",
                "cloudfront:UpdateCloudFrontOriginAccessIdentity",
                "cloudfront:DeleteCloudFrontOriginAccessIdentity"
            ],
            "Resource": "*"
        }
    ]
}
```

**Policy Name Suggestion**: `CloudStackGeneratorCloudFrontAccess`

### Option 2: AWS Managed Policy (Simpler, Broader Access)

Use AWS managed policy for quick setup (grants more permissions than needed):
- Policy: `CloudFrontFullAccess`

**Note**: This grants full CloudFront access, not just what's needed.

---

## How to Apply Permissions

### Via AWS Console (Recommended)

1. **Log into AWS IAM Console**
   - Go to https://console.aws.amazon.com/iam/
   - Click **Policies** in left sidebar
   - Click **Create policy**

2. **Create Custom Policy**
   - Click **JSON** tab
   - Paste the least-privilege policy JSON from above
   - Click **Next**

3. **Name the Policy**
   - **Policy name**: `CloudStackGeneratorCloudFrontAccess`
   - **Description**: `CloudFront and ACM permissions for Cloud Stack Generator HTTPS deployment`
   - Add tags (optional):
     - Key: `Project`, Value: `CloudStackGenerator`
     - Key: `Purpose`, Value: `HTTPSDeployment`
   - Click **Create policy**

4. **Attach to Your IAM User**
   - Navigate to **Users** → Select your user (e.g., `cloud-stack-generator-deployer`)
   - Click **Add permissions** → **Attach policies directly**
   - Search for `CloudStackGeneratorCloudFrontAccess`
   - ✅ Check the box
   - Click **Add permissions**

### Via AWS CLI

```bash
# Save the least-privilege policy to a file (copy policy JSON from above)
cat > cloudfront-policy.json << 'EOF'
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "CloudFrontDistributionManagement",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateDistribution",
                "cloudfront:GetDistribution",
                "cloudfront:GetDistributionConfig",
                "cloudfront:ListDistributions",
                "cloudfront:UpdateDistribution",
                "cloudfront:DeleteDistribution",
                "cloudfront:TagResource",
                "cloudfront:UntagResource",
                "cloudfront:ListTagsForResource"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "us-east-1"
                }
            }
        },
        {
            "Sid": "CloudFrontCacheInvalidation",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateInvalidation",
                "cloudfront:GetInvalidation",
                "cloudfront:ListInvalidations"
            ],
            "Resource": "*"
        },
        {
            "Sid": "ACMCertificateReadOnly",
            "Effect": "Allow",
            "Action": [
                "acm:ListCertificates",
                "acm:DescribeCertificate",
                "acm:GetCertificate"
            ],
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "aws:RequestedRegion": "us-east-1"
                }
            }
        },
        {
            "Sid": "CloudFrontOriginAccessIdentity",
            "Effect": "Allow",
            "Action": [
                "cloudfront:CreateCloudFrontOriginAccessIdentity",
                "cloudfront:GetCloudFrontOriginAccessIdentity",
                "cloudfront:ListCloudFrontOriginAccessIdentities",
                "cloudfront:UpdateCloudFrontOriginAccessIdentity",
                "cloudfront:DeleteCloudFrontOriginAccessIdentity"
            ],
            "Resource": "*"
        }
    ]
}
EOF

# Get your AWS account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create the policy
aws iam create-policy \
    --policy-name CloudStackGeneratorCloudFrontAccess \
    --description "CloudFront and ACM permissions for Cloud Stack Generator" \
    --policy-document file://cloudfront-policy.json \
    --tags Key=Project,Value=CloudStackGenerator Key=Purpose,Value=HTTPSDeployment

# Attach to your user (replace YOUR_USERNAME with your actual IAM username)
aws iam attach-user-policy \
    --user-name YOUR_USERNAME \
    --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/CloudStackGeneratorCloudFrontAccess

# Verify attachment
aws iam list-attached-user-policies --user-name YOUR_USERNAME
```

**Note**: Replace `YOUR_USERNAME` with your actual IAM user name (e.g., `cloud-stack-generator-deployer`)

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

---

## Complete Combined Policy (S3 + CloudFront)

For convenience, here's a single policy that includes both S3 and CloudFront permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3BucketManagement",
      "Effect": "Allow",
      "Action": [
        "s3:CreateBucket",
        "s3:DeleteBucket",
        "s3:ListBucket",
        "s3:GetBucketWebsite",
        "s3:PutBucketWebsite",
        "s3:DeleteBucketWebsite",
        "s3:GetBucketPolicy",
        "s3:PutBucketPolicy",
        "s3:DeleteBucketPolicy",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketPublicAccessBlock",
        "s3:PutBucketAcl",
        "s3:GetBucketAcl",
        "s3:GetBucketLocation",
        "s3:ListAllMyBuckets"
      ],
      "Resource": "arn:aws:s3:::*"
    },
    {
      "Sid": "S3ObjectManagement",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:PutObjectAcl",
        "s3:GetObjectAcl"
      ],
      "Resource": "arn:aws:s3:::*/*"
    },
    {
      "Sid": "CloudFrontDistributionManagement",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateDistribution",
        "cloudfront:GetDistribution",
        "cloudfront:GetDistributionConfig",
        "cloudfront:ListDistributions",
        "cloudfront:UpdateDistribution",
        "cloudfront:DeleteDistribution",
        "cloudfront:TagResource",
        "cloudfront:UntagResource",
        "cloudfront:ListTagsForResource"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    },
    {
      "Sid": "CloudFrontCacheInvalidation",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "*"
    },
    {
      "Sid": "ACMCertificateReadOnly",
      "Effect": "Allow",
      "Action": [
        "acm:ListCertificates",
        "acm:DescribeCertificate",
        "acm:GetCertificate"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": "us-east-1"
        }
      }
    },
    {
      "Sid": "CloudFrontOriginAccessIdentity",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateCloudFrontOriginAccessIdentity",
        "cloudfront:GetCloudFrontOriginAccessIdentity",
        "cloudfront:ListCloudFrontOriginAccessIdentities",
        "cloudfront:UpdateCloudFrontOriginAccessIdentity",
        "cloudfront:DeleteCloudFrontOriginAccessIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

**Policy Name**: `CloudStackGeneratorFullAccess`
**Description**: `Complete S3 and CloudFront permissions for Cloud Stack Generator`

This single policy provides everything needed for full functionality including:
- ✅ S3 bucket creation and management
- ✅ S3 object upload and management
- ✅ CloudFront distribution creation and management
- ✅ SSL certificate management via ACM
- ✅ Cache invalidation

---

This will enable full HTTPS deployment with global CDN acceleration for optimal website performance and security.