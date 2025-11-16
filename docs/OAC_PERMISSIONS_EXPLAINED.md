# CloudFront Origin Access Control (OAC) - Permissions Explained

**Date**: November 16, 2025
**Context**: Mode B implementation requires OAC setup

---

## What is Origin Access Control (OAC)?

**Purpose**: Allows CloudFront to access a **private** S3 bucket while preventing direct public access.

**Before OAC (Mode A - current):**
```
User → CloudFront → S3 Bucket (PUBLIC)
User → S3 Directly (PUBLIC) ← Security risk!
```

**With OAC (Mode B - target):**
```
User → CloudFront → S3 Bucket (PRIVATE via OAC)
User → S3 Directly (BLOCKED) ← Secure!
```

**Benefits:**
- S3 bucket is private (not publicly accessible)
- Only CloudFront can access bucket contents
- Better security (no direct S3 URL access)
- CloudFront is the only entry point

---

## How OAC Works

### Step 1: Create OAC Identity
CloudFront creates a service principal that will access S3:
```
Origin Access Control ID: ABC123XYZ
Service Principal: cloudfront.amazonaws.com
Signing Protocol: sigv4 (AWS Signature Version 4)
```

### Step 2: Attach OAC to CloudFront Distribution
The distribution uses this OAC identity to sign requests to S3.

### Step 3: Update S3 Bucket Policy
S3 bucket policy grants the CloudFront distribution access:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowCloudFrontServicePrincipal",
      "Effect": "Allow",
      "Principal": {
        "Service": "cloudfront.amazonaws.com"
      },
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::bucket-name/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::ACCOUNT_ID:distribution/DISTRIBUTION_ID"
        }
      }
    }
  ]
}
```

### Step 4: Block Public Access
S3 bucket has all public access blocked - only CloudFront can read.

---

## IAM Permissions Required

The AWS credentials (AWS V2 profile in your app) need these permissions:

### Required CloudFront Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateDistribution",
        "cloudfront:GetDistribution",
        "cloudfront:GetDistributionConfig",
        "cloudfront:UpdateDistribution",
        "cloudfront:ListDistributions",
        "cloudfront:CreateOriginAccessControl",
        "cloudfront:GetOriginAccessControl",
        "cloudfront:ListOriginAccessControls",
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "*"
    }
  ]
}
```

### Required S3 Permissions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:PutBucketPolicy",
        "s3:GetBucketPolicy",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketPublicAccessBlock",
        "s3:PutBucketWebsite",
        "s3:GetBucketWebsite"
      ],
      "Resource": [
        "arn:aws:s3:::bucket-name",
        "arn:aws:s3:::bucket-name/*"
      ]
    }
  ]
}
```

### Required IAM Permissions (for account ID lookup)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Implementation Options

### Option 1: Full Automation (Recommended)
**What it does:**
- App creates OAC automatically
- App creates CloudFront distribution with OAC
- App updates S3 bucket policy automatically
- App blocks public access on bucket

**Pros:**
- Zero AWS Console interaction
- Fully automated workflow
- User just clicks "Deploy"

**Cons:**
- Requires all permissions above
- If permissions missing, deploy will fail with clear error

**User Experience:**
```
[Deploy Button Clicked]
→ Checking for existing CloudFront distribution...
→ Not found - creating new distribution
→ Creating Origin Access Control...
→ Creating CloudFront distribution (this may take 5-10 minutes)...
→ Updating S3 bucket policy for CloudFront access...
→ Blocking public S3 access...
→ Uploading files to S3...
→ Invalidating CloudFront cache...
→ Deployment complete!
→ CloudFront URL: https://d123abc456.cloudfront.net/
```

**Implementation Complexity**: Medium
**Estimated Time**: 6 hours

---

### Option 2: Semi-Automated (OAC Pre-Created)
**What it does:**
- User creates ONE OAC manually in AWS Console (one-time setup)
- User provides OAC ID to app
- App reuses this OAC for all distributions
- App still auto-creates distributions
- App still updates bucket policies

**Pros:**
- Slightly fewer permissions needed
- User controls OAC configuration
- Still no AWS Console for distributions

**Cons:**
- One-time AWS Console visit required
- More complex initial setup
- OAC ID must be stored in app settings

**User Experience:**
```
[First Time Setup]
User: Creates OAC in AWS Console
User: Copies OAC ID: "ABC123XYZ"
User: Pastes into app settings

[Every Deploy After]
[Deploy Button Clicked]
→ Using existing OAC: ABC123XYZ
→ Creating CloudFront distribution...
→ Updating S3 bucket policy...
→ Uploading files...
→ Deployment complete!
```

**Implementation Complexity**: Low-Medium
**Estimated Time**: 4 hours

---

### Option 3: Manual CloudFront Creation (Not Recommended)
**What it does:**
- User creates CloudFront + OAC in AWS Console
- User provides Distribution ID to app
- App just uploads files and invalidates cache

**Pros:**
- Minimal permissions needed
- User has full control

**Cons:**
- **Violates your requirement**: User must use AWS Console
- Complex manual setup for each deployment
- Error-prone

**NOT RECOMMENDED** - Doesn't meet your "no AWS Console" requirement.

---

## Recommended Approach: Option 1 (Full Automation)

### Why Option 1?
1. ✅ **Meets your requirement**: No AWS Console needed
2. ✅ **Best user experience**: Just click Deploy
3. ✅ **Scalable**: Works for 1 or 100 deployments
4. ✅ **Error handling**: App can detect and report permission issues
5. ✅ **Future-proof**: Ready for additional automation

### Permission Verification Strategy
```python
def verify_oac_permissions(session: boto3.Session) -> Tuple[bool, List[str]]:
    """
    Verify user has all required permissions before attempting OAC setup.

    Returns:
        (has_permissions, missing_permissions)
    """
    required = [
        ('cloudfront', 'create_origin_access_control'),
        ('cloudfront', 'create_distribution'),
        ('s3', 'put_bucket_policy'),
        ('s3', 'put_bucket_public_access_block'),
        ('sts', 'get_caller_identity')
    ]

    missing = []
    for service, action in required:
        if not has_permission(session, service, action):
            missing.append(f"{service}:{action}")

    return (len(missing) == 0, missing)
```

### Error Handling
If permissions are missing:
```
❌ CloudFront Deployment Failed

Missing AWS Permissions:
- cloudfront:CreateOriginAccessControl
- s3:PutBucketPolicy

Required Actions:
1. Update your AWS IAM policy to include these permissions
2. See documentation: docs/OAC_PERMISSIONS_EXPLAINED.md
3. Contact your AWS administrator if needed

Would you like to:
[Retry] [Deploy to S3 Only (Mode A)] [Cancel]
```

---

## Security Considerations

### Current Setup (Your AWS Credentials)
- Profile: "AWS V2"
- Auth Method: Access Keys
- Currently has: S3 upload, CloudFront update permissions

### Additional Permissions Needed for OAC
You'll need to add these to your IAM user/role policy:
1. `cloudfront:CreateOriginAccessControl`
2. `cloudfront:CreateDistribution` (you may already have this)
3. `s3:PutBucketPolicy`
4. `s3:PutBucketPublicAccessBlock`

### How to Add Permissions

**If you manage your own IAM:**
1. Go to AWS Console → IAM → Users → [Your User]
2. Add inline policy or attach managed policy
3. Use JSON policies from "IAM Permissions Required" section above

**If your company manages IAM:**
1. Send IAM permissions JSON to your AWS admin
2. Request: "CloudFront OAC and S3 bucket policy permissions"
3. Reference this document

### Least Privilege Principle
The app only needs:
- **CloudFront**: Create distributions, OAC, invalidations
- **S3**: Upload files, update bucket policies (only for your buckets)
- **STS**: Get account ID (for ARN construction)

**The app cannot:**
- Delete distributions (we keep them)
- Access other AWS accounts
- Modify IAM policies
- Access EC2, RDS, or other services

---

## Alternative: Managed Policy

AWS provides a managed policy that includes most of what we need:
- `arn:aws:iam::aws:policy/CloudFrontFullAccess`
- `arn:aws:iam::aws:policy/AmazonS3FullAccess`

**Pros:**
- Easy to attach
- Maintained by AWS

**Cons:**
- More permissions than necessary (not least privilege)
- Includes delete/modify permissions we don't need

**Recommendation**: Use custom policy with only required permissions (shown above)

---

## Questions for User

### 1. Do you currently have CloudFront permissions?
Run this test in the app:
```python
python scripts/test_cloudfront_permissions.py
```

We can create this script to test your current permissions.

### 2. Can you add IAM permissions yourself?
- **Yes**: We'll provide exact JSON policy to add
- **No**: We'll provide request template for your AWS admin

### 3. Same credentials for all clients?
- **Yes**: One set of permissions covers all deployments
- **No**: Each client has separate AWS credentials (more complex)

### 4. Preferred approach?
Based on explanation above:
- **Option 1**: Full automation (recommended)
- **Option 2**: Semi-automated with manual OAC
- **Option 3**: Manual setup (not recommended)

---

## Next Steps (After Your Feedback)

1. **You confirm Option 1** (full automation)
2. **We verify/add IAM permissions** to your AWS V2 profile
3. **We implement OAC auto-creation** in Mode B
4. **We test with your AWS credentials**
5. **Deploy without touching AWS Console!**

---

## Appendix: Complete IAM Policy

Here's the complete policy you'll need to add:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CloudFrontOACManagement",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateOriginAccessControl",
        "cloudfront:GetOriginAccessControl",
        "cloudfront:ListOriginAccessControls",
        "cloudfront:UpdateOriginAccessControl"
      ],
      "Resource": "*"
    },
    {
      "Sid": "CloudFrontDistributionManagement",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateDistribution",
        "cloudfront:GetDistribution",
        "cloudfront:GetDistributionConfig",
        "cloudfront:UpdateDistribution",
        "cloudfront:ListDistributions"
      ],
      "Resource": "*"
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
      "Sid": "S3BucketManagement",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket",
        "s3:PutBucketPolicy",
        "s3:GetBucketPolicy",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketPublicAccessBlock",
        "s3:PutBucketWebsite",
        "s3:GetBucketWebsite",
        "s3:PutBucketAcl",
        "s3:GetBucketAcl"
      ],
      "Resource": [
        "arn:aws:s3:::*",
        "arn:aws:s3:::*/*"
      ]
    },
    {
      "Sid": "AccountIdentityLookup",
      "Effect": "Allow",
      "Action": [
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

**Policy Name Suggestion**: `CloudStackGeneratorDeploymentPolicy`
