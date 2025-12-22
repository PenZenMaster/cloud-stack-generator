# Cloud Stack Generator - Administration Guide

**Version**: 3.6.0
**Last Updated**: December 21, 2025
**Audience**: System administrators, DevOps engineers, technical staff

---

## Table of Contents

1. [Installation & Setup](#1-installation--setup)
2. [Environment Configuration](#2-environment-configuration)
3. [AWS Deployment Setup](#3-aws-deployment-setup)
4. [Google Cloud Setup](#4-google-cloud-setup)
5. [API Integration](#5-api-integration)
6. [Security Best Practices](#6-security-best-practices)
7. [Naming Conventions](#7-naming-conventions)
8. [Backup & Recovery](#8-backup--recovery)
9. [Monitoring & Maintenance](#9-monitoring--maintenance)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Installation & Setup

### System Requirements

- **Python**: 3.9 or higher
- **Operating System**: Windows 10/11, macOS, or Linux
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Disk Space**: 500MB for application + space for generated sites
- **Network**: Internet connection for cloud deployments and API calls

### Installation Steps

#### Option 1: Install from Source

```bash
# Clone repository
git clone https://github.com/your-org/cloud-stack-generator.git
cd cloud-stack-generator

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python main.py --version
```

#### Option 2: Install from Package

```bash
pip install cloud-stack-generator

# Verify installation
cloudstack --version
```

### Dependencies

**Core Dependencies** (`requirements.txt`):
```
PyQt6>=6.5.0
pyyaml>=6.0
jinja2>=3.1.2
boto3>=1.28.0
google-cloud-storage>=2.10.0
openai>=1.0.0
python-dotenv>=1.0.0
```

**Development Dependencies**:
```
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.0.0
ruff>=0.0.290
mypy>=1.5.0
```

---

## 2. Environment Configuration

### Environment Variables

Create `.env` file in project root:

```env
# Application Settings
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO

# AWS Configuration
AWS_PROFILE=default
AWS_DEFAULT_REGION=us-east-1

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# OpenAI API
OPENAI_API_KEY=sk-proj-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7

# AI Content Features
AI_CONTENT_ENABLED=true
AI_CONTENT_CACHE_ENABLED=true
AI_CONTENT_CACHE_HOURS=168

# GitHub Integration
GITHUB_TOKEN=ghp_your_token_here

# Application Paths
CONFIG_DIR=config/clients
OUTPUT_DIR=output/clients
CACHE_DIR=.cache

# Feature Flags
ENABLE_WIKIPEDIA_API=true
ENABLE_GOOGLE_MAPS_API=true
ENABLE_AI_CONTENT=true
```

### Security Note

**IMPORTANT**:
- Never commit `.env` file to version control
- `.env` is automatically excluded via `.gitignore`
- Store production credentials in secure key management systems
- Rotate API keys regularly

### Configuration File Locations

| Configuration | Location | Purpose |
|---------------|----------|---------|
| Client Configs | `config/clients/{client-name}/` | Client-specific settings |
| Assets | `config/clients/{client-name}/assets/` | Client logos, images |
| Templates | `src/templates/` | HTML templates and metadata |
| Credentials | `~/.aws/credentials` | AWS access keys |
| GCS Keys | `~/.config/gcloud/` | Google Cloud service accounts |

---

## 3. AWS Deployment Setup

### Overview

The application supports two AWS deployment modes:
- **Mode A**: S3-only deployment (public bucket, direct access)
- **Mode B**: CloudFront + OAC (private bucket, CDN distribution)

### 3.1 IAM User Setup

#### Create Dedicated IAM User (Recommended)

1. **AWS Console** → **IAM** → **Users** → **Create user**

2. **User Details**:
   - Name: `cloud-stack-generator-deployer`
   - Console access: NOT required

3. **Set Permissions** (Choose Custom Policy):

**Least-Privilege Policy JSON**:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ListAll",
      "Effect": "Allow",
      "Action": ["s3:ListAllMyBuckets", "s3:GetBucketLocation"],
      "Resource": "*"
    },
    {
      "Sid": "S3CreateBucket",
      "Effect": "Allow",
      "Action": ["s3:CreateBucket", "s3:DeleteBucket"],
      "Resource": "arn:aws:s3:::*"
    },
    {
      "Sid": "S3BucketManagement",
      "Effect": "Allow",
      "Action": [
        "s3:PutBucketPolicy",
        "s3:GetBucketPolicy",
        "s3:DeleteBucketPolicy",
        "s3:PutBucketWebsite",
        "s3:GetBucketWebsite",
        "s3:DeleteBucketWebsite",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketPublicAccessBlock",
        "s3:PutBucketAcl",
        "s3:GetBucketAcl",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::*"
    },
    {
      "Sid": "S3ObjectOps",
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
      "Sid": "CloudFrontManagement",
      "Effect": "Allow",
      "Action": [
        "cloudfront:CreateOriginAccessControl",
        "cloudfront:GetOriginAccessControl",
        "cloudfront:ListOriginAccessControls",
        "cloudfront:CreateDistribution",
        "cloudfront:GetDistribution",
        "cloudfront:GetDistributionConfig",
        "cloudfront:UpdateDistribution",
        "cloudfront:ListDistributions",
        "cloudfront:CreateInvalidation",
        "cloudfront:GetInvalidation",
        "cloudfront:ListInvalidations"
      ],
      "Resource": "*"
    },
    {
      "Sid": "AccountIdentity",
      "Effect": "Allow",
      "Action": ["sts:GetCallerIdentity"],
      "Resource": "*"
    }
  ]
}
```

4. **Create Access Key**:
   - Security Credentials tab → Create access key
   - Use case: **Application running outside AWS**
   - Save Access Key ID and Secret Access Key securely

### 3.2 Configure AWS CLI

**Method 1: Configure Profile**:
```bash
aws configure --profile AWS
# AWS Access Key ID: AKIA...
# AWS Secret Access Key: ...
# Default region: us-east-1
# Default output: json
```

**Method 2: Environment Variables**:
```bash
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
```

**Method 3: Application UI**:
1. Open Cloud Stack Generator
2. Cloud Deploy Tab → New Profile
3. Enter Access Key ID and Secret Access Key
4. Test Connection

### 3.3 Mode A: S3-Only Deployment

**Use Case**: Simple deployments, cost-sensitive projects

**Deployment Process**:
1. System creates S3 bucket with public-read policy
2. Enables static website hosting
3. Uploads files with appropriate caching headers
4. Returns S3 website URL

**Bucket Configuration**:
- **Public Access Block**: Disabled
- **Bucket Policy**: Public read for objects
- **Website Hosting**: Enabled (index.html, 404.html)
- **CORS**: Not required

**Website URL Format**:
```
http://{bucket-name}.s3-website-{region}.amazonaws.com
```

### 3.4 Mode B: CloudFront + OAC Deployment

**Use Case**: Production deployments, HTTPS required, CDN benefits

**Benefits**:
- HTTPS support out of the box
- Global CDN distribution
- Private S3 bucket (more secure)
- Custom domain support
- DDoS protection

**Deployment Process**:

1. **First Deployment**:
   - System creates S3 bucket (private)
   - Creates Origin Access Control (OAC) identity
   - Creates CloudFront distribution with OAC
   - Updates S3 bucket policy to allow CloudFront access
   - Blocks public S3 access
   - Uploads files to S3
   - Returns CloudFront URL

2. **Subsequent Deployments**:
   - System finds existing CloudFront distribution
   - Uploads updated files to S3
   - Creates CloudFront invalidation to clear cache
   - Returns same CloudFront URL

**Origin Access Control (OAC) Explained**:

OAC allows CloudFront to access private S3 buckets securely:

```
User Request → CloudFront Distribution → S3 Bucket (PRIVATE)
           ✅                      ✅ OAC Auth
```

Direct S3 access is **blocked**:
```
User → S3 Bucket (PRIVATE)
   ❌ Access Denied
```

**Bucket Policy Applied (Automatic)**:
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
      "Resource": "arn:aws:s3:::{bucket-name}/*",
      "Condition": {
        "StringEquals": {
          "AWS:SourceArn": "arn:aws:cloudfront::{account-id}:distribution/{distribution-id}"
        }
      }
    }
  ]
}
```

**CloudFront Distribution Settings**:
- **Origin**: S3 bucket with OAC
- **Viewer Protocol**: Redirect HTTP → HTTPS
- **Cache Policy**: CachingOptimized
- **Default Root Object**: index.html
- **Error Pages**: Custom 404.html
- **Invalidation**: Automatic on deployment (`/*`)

**Website URL Format**:
```
https://{distribution-id}.cloudfront.net
```

**Custom Domain Setup** (Optional):

1. **Request ACM Certificate** (us-east-1 region):
   ```bash
   aws acm request-certificate \
     --domain-name www.example.com \
     --validation-method DNS \
     --region us-east-1
   ```

2. **Add Alternate Domain Names** to CloudFront distribution

3. **Create Route 53 Record**:
   - Type: A (Alias)
   - Alias Target: CloudFront distribution
   - Routing Policy: Simple

### 3.5 Access Key Rotation

Rotate keys every 90 days:

```bash
# Create new access key
aws iam create-access-key --user-name cloud-stack-generator-deployer

# Update application configuration with new key
# Test new key works

# Delete old access key
aws iam delete-access-key --user-name cloud-stack-generator-deployer --access-key-id <OLD_KEY_ID>
```

---

## 4. Google Cloud Setup

### 4.1 GCP Project Setup

```bash
# Create project
gcloud projects create my-website-project --name="My Website"

# Set as default
gcloud config set project my-website-project

# Enable billing
gcloud beta billing projects link my-website-project \
  --billing-account=YOUR_BILLING_ACCOUNT_ID

# Enable APIs
gcloud services enable storage.googleapis.com
gcloud services enable compute.googleapis.com  # For Cloud CDN
```

### 4.2 Service Account Creation

```bash
# Create service account
gcloud iam service-accounts create website-deployer \
  --display-name="Website Deployer" \
  --description="Service account for deploying static websites"

# Grant Storage Admin role
gcloud projects add-iam-policy-binding my-website-project \
  --member="serviceAccount:website-deployer@my-website-project.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create ~/gcs-deployer-key.json \
  --iam-account=website-deployer@my-website-project.iam.gserviceaccount.com
```

### 4.3 Configure Application

**Method 1: Environment Variable**:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcs-deployer-key.json
```

**Method 2: .env File**:
```env
GOOGLE_APPLICATION_CREDENTIALS=/path/to/gcs-deployer-key.json
```

**Method 3: Application Config**:
```yaml
deployment:
  provider: google_gcs
  credentials:
    service_account_json: /path/to/gcs-deployer-key.json
  region: us-central1
  bucket_name: my-website-bucket
```

### 4.4 GCS Deployment

**Storage Classes**:
| Class | Use Case | Min Duration | Cost |
|-------|----------|--------------|------|
| STANDARD | Frequently accessed | None | Highest |
| NEARLINE | < 1x/month | 30 days | Lower |
| COLDLINE | < 1x/quarter | 90 days | Even lower |
| ARCHIVE | Rarely accessed | 365 days | Lowest |

**Regions**:
- **Single Region**: us-central1, us-east1, europe-west1 (lowest latency)
- **Multi-Region**: us, eu, asia (highest availability)

### 4.5 Cloud CDN Setup (Optional)

```bash
# Create backend bucket
gcloud compute backend-buckets create my-website-backend \
  --gcs-bucket-name=my-website-bucket \
  --enable-cdn

# Create URL map
gcloud compute url-maps create my-website-map \
  --default-backend-bucket=my-website-backend

# Create HTTP proxy
gcloud compute target-http-proxies create my-website-proxy \
  --url-map=my-website-map

# Create forwarding rule
gcloud compute forwarding-rules create my-website-rule \
  --global \
  --target-http-proxy=my-website-proxy \
  --ports=80
```

---

## 5. API Integration

### 5.1 OpenAI API (AI Content Generation)

#### Setup Steps

1. **Create Account**: [platform.openai.com](https://platform.openai.com)

2. **Create API Key**:
   - API Keys → Create new secret key
   - Name: "Cloud Stack Generator"
   - Copy key (starts with `sk-proj-...`)

3. **Add to Environment**:
   ```env
   OPENAI_API_KEY=sk-proj-your-actual-key-here
   OPENAI_MODEL=gpt-4o-mini
   AI_CONTENT_ENABLED=true
   AI_CONTENT_CACHE_ENABLED=true
   ```

4. **Verify Setup**:
   ```python
   from src.core.config import OpenAIConfig
   if OpenAIConfig.is_configured():
       print("OpenAI configured successfully")
   ```

#### Cost Optimization

**Recommended Model**: `gpt-4o-mini` (10x cheaper than GPT-4)

| Content Type | Cost per Page (gpt-4o-mini) |
|--------------|----------------------------|
| Home Page    | $0.0007                    |
| City Page    | $0.0006                    |

**With 7-day caching**:
- First generation: ~$0.0007 per page
- Subsequent runs (within 7 days): $0 (FREE)

**Example Costs**:
- 100 businesses, 10 cities each = 1,100 pages
- **Total cost**: ~$0.70
- **Cost per business**: ~$0.007

#### Cache Management

Cache is stored in `.cache/ai_content/` with 7-day TTL:

```python
from src.core.services.content_cache import ContentCache

cache = ContentCache()
stats = cache.get_statistics()
print(f"Cache hits: {stats['hits']}")
print(f"Cache misses: {stats['misses']}")
print(f"Total entries: {stats['total_entries']}")

# Clear cache if needed
cache.clear()
```

### 5.2 Google Maps API

**Not currently implemented** - reserved for future location features.

### 5.3 Wikipedia API

**Not currently implemented** - reserved for future city content enrichment.

### 5.4 Google Business Profile Integration

#### Data Flow Architecture

**Configuration**:
```yaml
client:
  google_business_profile:
    embed_code: "<iframe src='https://www.google.com/maps/embed?...'></iframe>"
```

**Data Model**:
```python
class ClientConfig:
    google_business_profile: Dict[str, str] = field(default_factory=dict)
```

**UI Component** (Contact Tab):
- Field: Google Business Profile embed code textarea
- Saves to: `config.google_business_profile.embed_code`

**Template Rendering**:
- Embed appears in footer section
- Variable: `{{ google_business.embed_code }}`

**CRITICAL**: Always use `google_business_profile` key (not `google_business`) to prevent data loss.

### 5.5 GitHub Token Setup

For GitHub issue tracking integration:

1. **Generate Token**:
   - GitHub → Settings → Developer settings → Personal access tokens
   - Create new token with scopes: `repo`, `write:discussion`, `project`

2. **Configure**:
   ```env
   GITHUB_TOKEN=ghp_your_token_here
   ```

3. **Verify**:
   ```bash
   python tools/github_token_manager.py
   ```

---

## 6. Security Best Practices

### 6.1 Credential Management

**DO**:
- Store credentials in `.env` file (excluded from git)
- Use environment variables for production
- Rotate access keys every 90 days
- Use IAM roles instead of access keys when possible
- Store service account keys securely
- Enable MFA on AWS root account

**DON'T**:
- Commit credentials to version control
- Share API keys between team members
- Use overly permissive IAM policies
- Store credentials in application code
- Email or message credentials

### 6.2 IAM Best Practices

**Least Privilege Principle**:
- Grant only necessary permissions
- Use custom policies instead of `FullAccess` managed policies
- Restrict resource scope when possible
- Review and remove unused permissions

**IP-Based Restrictions** (Advanced):
```json
{
  "Condition": {
    "IpAddress": {
      "aws:SourceIp": [
        "YOUR.IP.ADDRESS/32",
        "OFFICE.IP.ADDRESS/32"
      ]
    }
  }
}
```

**Monitoring**:
- Enable CloudTrail logging for all IAM users
- Set up billing alerts
- Review Access Advisor periodically
- Monitor for suspicious activity

### 6.3 API Key Security

**Rotation Schedule**:
- OpenAI API keys: Every 90 days
- GitHub tokens: Every 90 days or when team members change
- AWS access keys: Every 90 days
- GCS service account keys: Annually

**Storage**:
- **Development**: `.env` file (gitignored)
- **Production**: AWS Secrets Manager, Google Secret Manager, or equivalent
- **Backup**: Encrypted password manager (1Password, LastPass, Bitwarden)

**Incident Response**:
1. Immediately revoke compromised credentials
2. Review CloudTrail/audit logs for unauthorized activity
3. Rotate all related credentials
4. Audit affected resources for changes
5. Report to AWS Support if fraudulent charges detected

### 6.4 Bucket Security

**S3 Bucket Policies**:
- Mode A (Public): Only allow `s3:GetObject` (read-only public access)
- Mode B (Private): Only allow CloudFront OAC access
- Never allow `s3:*` to `Principal: "*"`

**CORS Configuration** (if needed):
```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET"],
    "AllowedOrigins": ["https://yourdomain.com"],
    "ExposeHeaders": []
  }
]
```

**Versioning**: Enable for critical content buckets

**Encryption**: Server-side encryption (SSE-S3) enabled by default

---

## 7. Naming Conventions

### Local File System (Python Standard)

**Convention**: `snake_case`

```
output/clients/clean_restroom_rental_va/
config/clients/united_structural_systems/
src/core/deployment/s3_deployer.py
```

### AWS S3

**Bucket Names** (AWS Requirement):

**Convention**: `kebab-case`

```
sanitation-rentals
my-company-website
client-hosting-bucket
```

**Rules**:
- Lowercase only
- Hyphens (no underscores)
- 3-63 characters
- Globally unique
- No spaces or special characters

**Directory Names** (Recommended):

**Convention**: `kebab-case`

```
s3://sanitation-rentals/clean-restroom-rental-va/
s3://sanitation-rentals/clean-restroom-rental-fl/
```

**Why**: URL-friendly, SEO-friendly, consistent with bucket naming

### URL Slugs

**Convention**: `kebab-case`

```
/locations/bethesda-md.html
/products/luxury-flushing-unit.html
/services/portable-restroom-rental.html
```

### Python Code

**Variables/Functions**: `snake_case` (PEP 8)
```python
client_slug = "clean_restroom_rental_va"
def deploy_client_website(client_slug: str):
```

**Classes**: `PascalCase` (PEP 8)
```python
class S3WebsiteDeployer:
class ClientConfig:
```

**Constants**: `UPPER_SNAKE_CASE` (PEP 8)
```python
DEFAULT_REGION = "us-east-1"
MAX_UPLOAD_RETRIES = 3
```

### Automatic Conversion

The deployment module auto-converts `snake_case` to `kebab-case` for S3:

```python
# Local: snake_case
local_path = Path("output/clients/clean_restroom_rental_va")

# S3: kebab-case (auto-converted)
s3_directory = "clean-restroom-rental-va"
```

---

## 8. Backup & Recovery

### Configuration Backups

**Automated Backups** (Recommended):

```bash
# Create backup script
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y-%m-%d)"
mkdir -p $BACKUP_DIR

# Backup client configurations
cp -r config/clients/* $BACKUP_DIR/

# Backup environment (exclude secrets)
cp .env.example $BACKUP_DIR/.env.template

# Compress
tar -czf "$BACKUP_DIR.tar.gz" $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload to S3 (optional)
aws s3 cp "$BACKUP_DIR.tar.gz" s3://my-backup-bucket/cloudstack/
```

**Backup Schedule**:
- Daily: Configurations that change frequently
- Weekly: Full system backup
- Monthly: Archive backup

### S3 Website Backups

**Versioning** (Recommended):

Enable versioning on deployment buckets:

```bash
aws s3api put-bucket-versioning \
  --bucket my-website-bucket \
  --versioning-configuration Status=Enabled
```

**Backup to Another Bucket**:

```bash
# Sync to backup bucket
aws s3 sync s3://production-bucket s3://backup-bucket --delete
```

### Database Backups

Not applicable - application uses file-based configurations, no database.

### Disaster Recovery

**Recovery Steps**:

1. **Restore Configurations**:
   ```bash
   tar -xzf backup-2025-12-21.tar.gz
   cp -r backup-2025-12-21/clients/* config/clients/
   ```

2. **Restore Environment**:
   - Recreate `.env` from template
   - Re-enter API keys from secure storage

3. **Redeploy Websites**:
   - Open application
   - Load each client configuration
   - Generate and deploy

4. **Verify**:
   - Test all deployed URLs
   - Check CloudFront distributions
   - Verify content accuracy

---

## 9. Monitoring & Maintenance

### CloudWatch Monitoring (AWS)

**S3 Metrics**:
- BucketSizeBytes
- NumberOfObjects
- 4xxErrors
- 5xxErrors

**CloudFront Metrics**:
- Requests
- BytesDownloaded
- ErrorRate
- CacheHitRate

**Set Up Alarms**:

```bash
# Alarm for high error rate
aws cloudwatch put-metric-alarm \
  --alarm-name cloudstack-high-errors \
  --metric-name 4xxErrorRate \
  --namespace AWS/CloudFront \
  --statistic Average \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --alarm-actions arn:aws:sns:us-east-1:123456789012:alerts
```

### Cost Monitoring

**AWS Budgets**:

1. AWS Console → Billing → Budgets → Create budget
2. Budget name: `CloudStackGenerator-Monthly`
3. Budgeted amount: $10/month (adjust based on usage)
4. Alert at 80% and 100%

**Cost Breakdown**:
- S3 storage: $0.023/GB/month
- S3 requests: Minimal (mostly GET requests)
- CloudFront data transfer: $0.085/GB (varies by region)
- CloudFront requests: $0.0075 per 10,000 requests

**Typical Monthly Cost** (100 small websites):
- S3 storage (10GB): $0.23
- CloudFront (1GB transfer): $0.09
- **Total**: ~$0.50/month

### Application Logs

**Log Locations**:
- Application logs: `.logs/` directory
- Deployment logs: Included in UI output
- Error logs: `.logs/errors.log`

**Log Rotation**:

```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    '.logs/app.log',
    maxBytes=10485760,  # 10MB
    backupCount=5
)
```

### Maintenance Tasks

**Daily**:
- Monitor deployment success/failure rates
- Check application logs for errors
- Verify critical deployments still accessible

**Weekly**:
- Review AWS billing dashboard
- Check CloudFront cache hit rates
- Review and rotate access keys if approaching 90 days

**Monthly**:
- Full backup of configurations
- Update dependencies: `pip list --outdated`
- Review and archive old client configurations
- Audit IAM permissions

**Quarterly**:
- Rotate all API keys and access credentials
- Review and update security policies
- Performance audit (load times, cache efficiency)
- Capacity planning (storage, bandwidth)

---

## 10. Troubleshooting

### AWS Deployment Issues

#### "Access Denied" Errors

**Symptom**: `AccessDenied` when deploying to S3

**Checks**:
1. Verify IAM user has required permissions
   ```bash
   aws iam list-user-policies --user-name cloud-stack-generator-deployer
   ```

2. Check AWS CLI profile is configured
   ```bash
   aws configure list --profile AWS
   ```

3. Test AWS credentials
   ```bash
   aws sts get-caller-identity --profile AWS
   ```

**Solutions**:
- Add missing permissions to IAM policy
- Verify access key is still active (not deleted/rotated)
- Check for account-level Block Public Access settings

#### "403 Forbidden" on Website

**Symptom**: Website returns 403 when accessing S3/CloudFront URL

**Mode A (S3-only) Checks**:
1. Bucket policy allows public read:
   ```bash
   aws s3api get-bucket-policy --bucket {bucket-name}
   ```

2. Public access block is disabled:
   ```bash
   aws s3api get-public-access-block --bucket {bucket-name}
   ```

3. Website hosting is enabled:
   ```bash
   aws s3api get-bucket-website --bucket {bucket-name}
   ```

**Mode B (CloudFront) Checks**:
1. CloudFront distribution has OAC configured
2. S3 bucket policy allows CloudFront service principal
3. Origin domain name is correct
4. Distribution is deployed (not "In Progress")

#### "InvalidBucketName" Error

**Symptom**: Bucket creation fails with invalid name

**Rules**:
- Must be lowercase
- Must use hyphens (no underscores)
- 3-63 characters
- No spaces or special characters
- Must be globally unique

**Solution**: Use kebab-case naming convention

### GCS Deployment Issues

#### "Service account file not found"

**Solution**:
1. Verify path in `.env` or config is correct
2. Check file exists and is readable
3. Ensure JSON file contains `project_id` field

#### "Insufficient permissions"

**Solution**:
1. Verify service account has `roles/storage.admin`
   ```bash
   gcloud projects get-iam-policy my-website-project
   ```

2. Grant required role:
   ```bash
   gcloud projects add-iam-policy-binding my-website-project \
     --member="serviceAccount:website-deployer@my-website-project.iam.gserviceaccount.com" \
     --role="roles/storage.admin"
   ```

### AI Content Generation Issues

#### "Service not available"

**Checks**:
1. `.env` file exists in project root
2. `OPENAI_API_KEY` is set and valid
3. `openai` package is installed

**Test**:
```python
from src.core.config import OpenAIConfig
print(OpenAIConfig.is_configured())
```

#### "Rate limit exceeded"

**Solutions**:
- Wait a few minutes and retry
- Enable caching: `AI_CONTENT_CACHE_ENABLED=true`
- Upgrade OpenAI account tier

#### Content Falls Back to Templates

**Possible Reasons**:
- API key not configured (check `.env`)
- API request failed (check logs)
- AI is disabled: `AI_CONTENT_ENABLED=false`
- OpenAI service is down

**This is OK**: System gracefully falls back to templates.

### Application Issues

#### Dependencies Conflicts

**Solution**:
```bash
# Create fresh virtual environment
python -m venv venv-new
source venv-new/bin/activate  # or venv-new\Scripts\activate on Windows

# Install from clean requirements
pip install -r requirements.txt
```

#### Qt/GUI Errors

**Common Issues**:
- Missing Qt platform plugin
- Display/screen resolution issues

**Solutions**:
```bash
# Reinstall PyQt6
pip uninstall PyQt6 PyQt6-Qt6 PyQt6-sip
pip install PyQt6

# Set Qt platform (if needed)
export QT_QPA_PLATFORM=offscreen  # For headless environments
```

#### Configuration Loading Errors

**Symptom**: YAML parse errors, missing fields

**Checks**:
1. Verify YAML syntax is correct
2. Check for required fields (business_name, etc.)
3. Ensure no tabs (use spaces for indentation)

**Solution**:
```python
# Validate YAML manually
import yaml
with open('config.yaml') as f:
    try:
        config = yaml.safe_load(f)
        print("Valid YAML")
    except yaml.YAMLError as e:
        print(f"YAML Error: {e}")
```

### Google Business Profile Data Loss

**Critical Issue**: GBP embed code disappearing

**Root Cause**: UI component using wrong data key

**Prevention**:
- Always use `google_business_profile` key (not `google_business`)
- Test complete data flow: UI → Save → Load → Generate → Verify

**Verification**:
```bash
# Run regression test
python tests/test_gbp_regression_prevention.py
```

---

## Appendix A: Command Reference

### AWS CLI Commands

```bash
# List buckets
aws s3 ls --profile AWS

# Create bucket (us-east-1)
aws s3api create-bucket --bucket my-bucket --region us-east-1

# Create bucket (other regions)
aws s3api create-bucket --bucket my-bucket --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2

# Upload files
aws s3 sync ./output/website s3://my-bucket/ --profile AWS

# Create CloudFront invalidation
aws cloudfront create-invalidation --distribution-id E123ABC \
  --paths "/*" --profile AWS

# Check account identity
aws sts get-caller-identity --profile AWS
```

### GCloud Commands

```bash
# List buckets
gsutil ls

# Create bucket
gsutil mb -c STANDARD -l us-central1 gs://my-bucket

# Upload files
gsutil -m rsync -r ./output/website gs://my-bucket/

# Make bucket public
gsutil iam ch allUsers:objectViewer gs://my-bucket
```

### Python Management

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Update dependencies
pip list --outdated
pip install --upgrade package-name

# Run tests
pytest tests/

# Run specific test
pytest tests/unit/test_s3_deployer.py -v

# Code formatting
black src/
ruff check src/

# Type checking
mypy src/
```

---

## Appendix B: Security Checklist

Before production deployment:

- [ ] All credentials stored in `.env` (not committed to git)
- [ ] IAM policies follow least privilege principle
- [ ] AWS access keys rotated within 90 days
- [ ] MFA enabled on AWS root account
- [ ] CloudTrail logging enabled
- [ ] Billing alerts configured
- [ ] S3 buckets use appropriate access policies
- [ ] CloudFront distributions use HTTPS
- [ ] Service account keys stored securely
- [ ] API keys have appropriate rate limits
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting configured
- [ ] Incident response plan documented
- [ ] Team members have individual IAM users
- [ ] Shared credentials prohibited

---

## Appendix C: Support Resources

**Documentation**:
- [USER_GUIDE.md](USER_GUIDE.md) - End user documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [GITHUB_ISSUES_WORKFLOW.md](GITHUB_ISSUES_WORKFLOW.md) - Issue tracking

**AWS Documentation**:
- [S3 Static Website Hosting](https://docs.aws.amazon.com/AmazonS3/latest/userguide/WebsiteHosting.html)
- [CloudFront Documentation](https://docs.aws.amazon.com/cloudfront/)
- [IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

**GCP Documentation**:
- [GCS Documentation](https://cloud.google.com/storage/docs)
- [Cloud CDN](https://cloud.google.com/cdn/docs)
- [Service Accounts](https://cloud.google.com/iam/docs/service-accounts)

**API Documentation**:
- [OpenAI API](https://platform.openai.com/docs)
- [GitHub API](https://docs.github.com/en/rest)

**Community**:
- GitHub Issues: [Report bugs and request features](../.github/ISSUE_TEMPLATE/)
- Discussions: Technical questions and community support

---

**End of Administration Guide**
For user-facing documentation, see [USER_GUIDE.md](USER_GUIDE.md).
For technical architecture, see [ARCHITECTURE.md](ARCHITECTURE.md).
