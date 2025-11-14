# AWS S3 Deployment Setup Guide

## Overview

This guide explains how to configure AWS IAM permissions for the `awg-cloud-stack` user to enable low-friction, automated website deployments to S3 with full bucket creation and configuration capabilities.

## IAM Policy: Recommended Restricted Access

The policy in `aws-s3-deployment-policy-full.json` provides the minimum permissions needed for the deployment workflow while maintaining security best practices.

### What This Policy Allows

#### 1. List and Locate Buckets (`ListAndLocateBuckets`)
- **Actions**: `s3:ListAllMyBuckets`, `s3:GetBucketLocation`
- **Resource**: All (`*`)
- **Purpose**: Required for CloudTab UI to display available buckets and for the app to check bucket regions

#### 2. Create and Delete Buckets (`CreateAndConfigureBuckets`)
- **Actions**: `s3:CreateBucket`, `s3:DeleteBucket`
- **Resource**: All buckets (`arn:aws:s3:::*`)
- **Purpose**: Allows programmatic creation of new client buckets and cleanup of test/old buckets

#### 3. Manage Bucket Configuration (`ManageBucketConfiguration`)
- **Actions**:
  - Website hosting: `PutBucketWebsite`, `GetBucketWebsite`, `DeleteBucketWebsite`
  - Public access: `PutPublicAccessBlock`, `GetPublicAccessBlock`, `DeletePublicAccessBlock`
  - Bucket policies: `PutBucketPolicy`, `GetBucketPolicy`, `DeleteBucketPolicy`
  - ACLs: `PutBucketAcl`, `GetBucketAcl`
  - CORS: `PutBucketCORS`, `GetBucketCORS`, `DeleteBucketCORS`
  - Other: `ListBucket`, `GetBucketVersioning`, `PutBucketVersioning`
- **Resource**: All buckets (`arn:aws:s3:::*`)
- **Purpose**: Full bucket configuration capabilities needed to make websites publicly accessible

#### 4. Manage Objects (`ManageAllBucketObjects`)
- **Actions**: `PutObject`, `GetObject`, `DeleteObject`, `PutObjectAcl`, `GetObjectAcl`, `ListMultipartUploadParts`, `AbortMultipartUpload`
- **Resource**: All objects in all buckets (`arn:aws:s3:::*/*`)
- **Purpose**: Upload, download, and manage website files

### What This Policy Does NOT Allow

- Creating/managing IAM users or policies
- Accessing services other than S3
- Modifying bucket lifecycle, replication, or inventory configurations
- Managing S3 access points or batch operations

### Comparison to Full Access

**Current Setup**: `s3:*` on all resources (Full Access)
- ALLOWS: Everything in S3 including advanced features you don't need
- RISK: If credentials compromised, attacker has unrestricted S3 access across all AWS accounts they can reach

**Recommended Setup**: Scoped permissions (aws-s3-deployment-policy-full.json)
- ALLOWS: Exactly what's needed for website deployment workflow
- RISK: If credentials compromised, attacker can only manipulate S3 buckets/objects (no IAM, EC2, Lambda, etc.)
- BENEFIT: Follows AWS least-privilege principle

## Applying the Policy

### Step 1: Remove Current Policies

Log into AWS Console as admin:
1. Navigate to IAM -> Users -> `awg-cloud-stack`
2. Click "Permissions" tab
3. Remove or detach:
   - Any managed policies (like `AmazonS3FullAccess`)
   - Any inline policies that grant `s3:*`

### Step 2: Apply New Inline Policy

```bash
# Using AWS CLI with admin profile
aws iam put-user-policy \
  --user-name awg-cloud-stack \
  --policy-name S3-Deployment-Full-Access \
  --policy-document file://aws-s3-deployment-policy-full.json \
  --profile <ADMIN_PROFILE>
```

Or via AWS Console:
1. IAM -> Users -> `awg-cloud-stack` -> Permissions tab
2. Click "Add permissions" -> "Create inline policy"
3. Click "JSON" tab
4. Paste contents of `aws-s3-deployment-policy-full.json`
5. Name it: `S3-Deployment-Full-Access`
6. Click "Create policy"

### Step 3: Verify Permissions

```bash
# Test listing buckets
aws s3 ls --profile AWS

# Test creating a bucket
aws s3 mb s3://test-awg-deployment-20251112 --profile AWS

# Test configuring website hosting
aws s3 website s3://test-awg-deployment-20251112 \
  --index-document index.html \
  --error-document error.html \
  --profile AWS

# Clean up test bucket
aws s3 rb s3://test-awg-deployment-20251112 --profile AWS
```

## Deployment Workflow

The `S3WebsiteDeployer` class in `src/core/deployment/s3_deployer.py` handles all deployment steps:

### Automatic Steps Performed

When deploying a new website, the app will automatically:

1. **Create Bucket** (if it doesn't exist)
   - Uses `s3:CreateBucket` permission
   - Handles region-specific requirements

2. **Disable Public Access Block**
   - Uses `s3:PutPublicAccessBlock` permission
   - Sets all block settings to False

3. **Apply Public Read Policy**
   - Uses `s3:PutBucketPolicy` permission
   - Grants `s3:GetObject` to `Principal: "*"` (public)

4. **Enable Static Website Hosting**
   - Uses `s3:PutBucketWebsite` permission
   - Configures index.html and error.html

5. **Upload Website Files**
   - Uses `s3:PutObject` and `s3:PutObjectAcl` permissions
   - Maintains directory structure
   - Sets appropriate Content-Type headers

### Example Usage

```python
from src.core.deployment import deploy_client_website

# Deploy a client website
result = deploy_client_website(
    client_slug="clean_restroom_rental_va",
    bucket_name="sanitation-rentals",
    profile="AWS",
    region="us-east-1"
)

if result["success"]:
    print(f"Website live at: {result['full_url']}")
else:
    print(f"Deployment failed: {result['errors']}")
```

### Command Line Usage

```bash
# Deploy from command line
cd E:\projects\cloud-stack-generator
python -m src.core.deployment.s3_deployer
```

## Security Considerations

### Access Key Management

1. **Create Access Keys** (one-time):
   - AWS Console -> IAM -> Users -> awg-cloud-stack -> Security credentials -> Create access key
   - Select "Command Line Interface (CLI)"
   - Save both Access Key ID and Secret Access Key

2. **Configure AWS CLI**:
   ```bash
   aws configure set aws_access_key_id <KEY_ID> --profile AWS
   aws configure set aws_secret_access_key <SECRET> --profile AWS
   aws configure set region us-east-1 --profile AWS
   ```

3. **Never Commit Credentials**:
   - Access keys are stored in `~/.aws/credentials` (not in repo)
   - If keys are accidentally committed, AWS may auto-quarantine the user

### Key Rotation

Rotate access keys every 90 days:
```bash
# Create new access key (max 2 keys per user)
aws iam create-access-key --user-name awg-cloud-stack --profile <ADMIN_PROFILE>

# Update AWS CLI config with new key
aws configure set aws_access_key_id <NEW_KEY_ID> --profile AWS

# Test new key works
aws s3 ls --profile AWS

# Delete old access key
aws iam delete-access-key --user-name awg-cloud-stack --access-key-id <OLD_KEY_ID> --profile <ADMIN_PROFILE>
```

### Bucket Policy Security

The deployer applies this policy to each bucket:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::bucket-name/*"
    }
  ]
}
```

This allows:
- Public read access to website files
- Required for static website hosting

This does NOT allow:
- Listing bucket contents
- Uploading/modifying/deleting files
- Changing bucket configuration

## Troubleshooting

### "AccessDenied" errors

If you get AccessDenied errors after applying the policy:

1. **Verify policy is attached**:
   ```bash
   aws iam list-user-policies --user-name awg-cloud-stack --profile <ADMIN_PROFILE>
   ```

2. **Check for deny policies**:
   Look for any policies with `"Effect": "Deny"` that might override the allow policy

3. **Verify AWS CLI profile**:
   ```bash
   aws configure list --profile AWS
   ```

### CloudTab can't see buckets

1. Ensure CloudTab is configured to use the correct profile
2. Refresh CloudTab's bucket list
3. Check that `s3:ListAllMyBuckets` permission is granted in the policy

### Website returns 403 Forbidden

1. Verify public access block is disabled:
   ```bash
   aws s3api get-public-access-block --bucket <BUCKET_NAME> --profile AWS
   ```

2. Verify bucket policy allows public read:
   ```bash
   aws s3api get-bucket-policy --bucket <BUCKET_NAME> --profile AWS
   ```

3. Verify website hosting is enabled:
   ```bash
   aws s3api get-bucket-website --bucket <BUCKET_NAME> --profile AWS
   ```

## Future Enhancements

Potential improvements to the deployment system:

1. **CloudFront Integration**: Add CDN distribution for better performance
2. **Custom Domain Support**: Automate Route 53 DNS configuration
3. **Deployment History**: Track deployments in DynamoDB
4. **Rollback Capability**: Store previous versions and enable quick rollback
5. **Multi-Region Deployment**: Deploy to multiple regions simultaneously
6. **Cost Monitoring**: Track S3 storage and bandwidth costs per client

## References

- [AWS S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [IAM Policy Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [S3 Bucket Policies](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-policies.html)
