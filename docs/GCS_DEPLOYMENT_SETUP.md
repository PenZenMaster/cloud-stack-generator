# Google Cloud Storage Deployment Setup Guide

**Version:** 1.0
**Created:** November 19, 2025
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [GCP Setup](#gcp-setup)
4. [Authentication Methods](#authentication-methods)
5. [Configuration](#configuration)
6. [Deployment Examples](#deployment-examples)
7. [Cloud CDN Setup](#cloud-cdn-setup)
8. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deploying static websites to **Google Cloud Storage (GCS)** using the cloud-stack-generator's multi-cloud provider architecture.

### Features

- ✅ Static website hosting on GCS
- ✅ Automatic bucket creation and configuration
- ✅ Public access configuration
- ✅ Custom domain support (with Cloud CDN)
- ✅ Regional and multi-regional deployment
- ✅ Automatic content-type detection
- ✅ Intelligent cache control headers

---

## Prerequisites

### Required Software

1. **Python 3.9+** with cloud-stack-generator installed
2. **Google Cloud SDK** (gcloud CLI)
3. **GCP Project** with billing enabled

### Required Python Packages

```bash
pip install google-cloud-storage>=2.10.0
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

###Required GCP Permissions

Your service account needs these roles:
- `roles/storage.admin` - Create and manage buckets
- `roles/iam.serviceAccountUser` - Set bucket policies

---

## GCP Setup

### Step 1: Create a GCP Project

```bash
# Create new project
gcloud projects create my-website-project --name="My Website"

# Set as default project
gcloud config set project my-website-project

# Enable billing (required)
gcloud beta billing projects link my-website-project \
  --billing-account=YOUR_BILLING_ACCOUNT_ID
```

### Step 2: Enable Required APIs

```bash
# Enable Cloud Storage API
gcloud services enable storage.googleapis.com

# Enable Cloud CDN API (optional, for CDN)
gcloud services enable compute.googleapis.com
```

### Step 3: Create Service Account

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

**Important:** Store the JSON key file securely. Never commit it to version control.

---

## Authentication Methods

The GCS provider supports three authentication methods:

### Method 1: Service Account JSON File (Recommended)

```python
from src.core.deployment.providers import GCSProvider, ProviderConfig, ProviderType, DeploymentMode

config = ProviderConfig(
    provider_type=ProviderType.GOOGLE_GCS,
    credentials={
        "service_account_json": "/path/to/gcs-deployer-key.json"
    },
    region="us-central1",
    deployment_mode=DeploymentMode.STORAGE_ONLY
)

provider = GCSProvider(config)
provider.authenticate()
```

### Method 2: Service Account Key Components

```python
config = ProviderConfig(
    provider_type=ProviderType.GOOGLE_GCS,
    credentials={
        "project_id": "my-website-project",
        "client_email": "website-deployer@my-website-project.iam.gserviceaccount.com",
        "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
    },
    region="us-central1"
)
```

### Method 3: Application Default Credentials

```python
# Set environment variable first:
# export GOOGLE_APPLICATION_CREDENTIALS="/path/to/gcs-deployer-key.json"

config = ProviderConfig(
    provider_type=ProviderType.GOOGLE_GCS,
    credentials={
        "use_adc": True
    },
    region="us-central1"
)
```

---

## Configuration

### YAML Configuration Format

```yaml
deployment:
  provider: google_gcs

  credentials:
    service_account_json: /path/to/gcs-deployer-key.json

  region: us-central1
  bucket_name: my-unique-website-bucket
  deployment_mode: storage_only

  provider_config:
    storage_class: STANDARD  # or NEARLINE, COLDLINE, ARCHIVE
    enable_versioning: false
```

### Storage Classes

| Class | Use Case | Pricing | Min Storage Duration |
|-------|----------|---------|---------------------|
| **STANDARD** | Frequently accessed | Highest storage cost | None |
| **NEARLINE** | < 1x/month access | Lower storage cost | 30 days |
| **COLDLINE** | < 1x/quarter access | Even lower cost | 90 days |
| **ARCHIVE** | Rarely accessed | Lowest cost | 365 days |

### Regions

**Single Region** (lowest latency for specific location):
- `us-central1` (Iowa)
- `us-east1` (South Carolina)
- `us-west1` (Oregon)
- `europe-west1` (Belgium)
- `asia-southeast1` (Singapore)

**Multi-Region** (highest availability):
- `us` (United States)
- `eu` (European Union)
- `asia` (Asia)

---

## Deployment Examples

### Example 1: Basic Deployment

```python
from pathlib import Path
from src.core.deployment.providers import (
    GCSProvider,
    ProviderConfig,
    ProviderType,
    DeploymentMode
)

# Configure provider
config = ProviderConfig(
    provider_type=ProviderType.GOOGLE_GCS,
    credentials={
        "service_account_json": "/path/to/gcs-deployer-key.json"
    },
    region="us-central1",
    deployment_mode=DeploymentMode.STORAGE_ONLY
)

# Create provider instance
provider = GCSProvider(config)

# Authenticate
if provider.authenticate():
    print("Authentication successful!")

    # Test connection
    success, message = provider.test_connection()
    print(message)

    # Create bucket
    bucket_name = "my-unique-website-bucket"
    if provider.create_bucket(bucket_name):
        print(f"Bucket created: {bucket_name}")

        # Configure for website hosting
        if provider.configure_website_hosting(bucket_name):
            print("Website hosting configured")

            # Upload website files
            website_dir = Path("./output/my-website")
            result = provider.upload_directory(
                website_dir,
                bucket_name,
                progress_callback=lambda c, t, f: print(f"Uploading {c}/{t}: {f}")
            )

            print(result)
            print(f"Website URL: {result.website_url}")
```

### Example 2: Deployment with Progress Tracking

```python
def progress_callback(current, total, filename):
    """Progress callback for deployment"""
    percent = (current / total) * 100
    print(f"[{percent:5.1f}%] {current}/{total} - {filename}")

# Deploy with progress tracking
result = provider.upload_directory(
    local_dir=Path("./output/my-website"),
    bucket_name="my-website-bucket",
    progress_callback=progress_callback
)

if result.success:
    print(f"\nDeployment successful!")
    print(f"Files uploaded: {result.files_uploaded}")
    print(f"Website URL: {result.website_url}")
else:
    print(f"\nDeployment failed!")
    print(f"Errors: {len(result.errors)}")
    for error in result.errors:
        print(f"  - {error}")
```

### Example 3: Multi-Region Deployment

```python
# Deploy to multiple regions for redundancy
regions = ["us", "eu", "asia"]
results = {}

for region in regions:
    config = ProviderConfig(
        provider_type=ProviderType.GOOGLE_GCS,
        credentials={"service_account_json": "/path/to/key.json"},
        region=region
    )

    provider = GCSProvider(config)
    provider.authenticate()

    bucket_name = f"my-website-{region}"
    provider.create_bucket(bucket_name)
    provider.configure_website_hosting(bucket_name)

    result = provider.upload_directory(
        Path("./output/my-website"),
        bucket_name
    )

    results[region] = result

# Print all deployment URLs
for region, result in results.items():
    print(f"{region.upper()}: {result.website_url}")
```

---

## Cloud CDN Setup

**Note:** Full Cloud CDN configuration requires additional setup beyond bucket deployment. The current implementation provides the basic GCS URL. For complete Cloud CDN with custom domains:

### Manual Cloud CDN Setup Steps

1. **Create Backend Bucket**
```bash
gcloud compute backend-buckets create my-website-backend \
  --gcs-bucket-name=my-website-bucket \
  --enable-cdn
```

2. **Create Load Balancer**
```bash
# Create URL map
gcloud compute url-maps create my-website-map \
  --default-backend-bucket=my-website-backend

# Create target HTTP proxy
gcloud compute target-http-proxies create my-website-proxy \
  --url-map=my-website-map

# Create forwarding rule
gcloud compute forwarding-rules create my-website-rule \
  --global \
  --target-http-proxy=my-website-proxy \
  --ports=80
```

3. **Add SSL Certificate** (for HTTPS)
```bash
# Create managed SSL certificate
gcloud compute ssl-certificates create my-website-cert \
  --domains=www.example.com

# Create target HTTPS proxy
gcloud compute target-https-proxies create my-website-https-proxy \
  --url-map=my-website-map \
  --ssl-certificates=my-website-cert
```

### Custom Domain Configuration

1. Get the load balancer IP:
```bash
gcloud compute forwarding-rules describe my-website-rule --global --format="get(IPAddress)"
```

2. Add DNS A record pointing to the IP address

3. Wait for DNS propagation (up to 48 hours)

---

## Troubleshooting

### Authentication Errors

**Error:** "Service account file not found"
```
Solution: Verify the path to your JSON key file is correct and accessible.
```

**Error:** "Could not determine project_id"
```
Solution: Ensure your service account JSON contains the "project_id" field.
```

### Bucket Creation Errors

**Error:** "Bucket name already exists globally"
```
Solution: Bucket names must be globally unique. Choose a different name.
```

**Error:** "Bucket name must be between 3 and 63 characters"
```
Solution: Rename your bucket to meet the length requirements.
```

### Upload Errors

**Error:** "Insufficient permissions"
```
Solution: Ensure your service account has roles/storage.admin role.
```

**Error:** "Quota exceeded"
```
Solution: Check your GCP quotas and request an increase if needed.
```

### Website Access Errors

**Error:** "403 Forbidden" when accessing website
```
Solution: Ensure you ran configure_website_hosting() to set public access.
```

**Error:** "404 Not Found" on custom domain
```
Solution: Verify DNS records and Cloud CDN configuration are correct.
```

---

## Pricing Estimates

### Storage Costs (STANDARD class, us-central1)

- Storage: $0.020 per GB/month
- Class A operations (uploads): $0.05 per 10,000 operations
- Class B operations (downloads): $0.004 per 10,000 operations
- Network egress: $0.12 per GB (worldwide, excluding China/Australia)

### Example: 100MB Website, 10,000 visitors/month

- Storage: $0.002/month
- Uploads (100 files): $0.0005
- Downloads (100 files × 10,000 visitors): $4.00
- **Total: ~$4.00/month**

### Cloud CDN Pricing

- Cache fill: $0.08 per GB
- Cache egress: $0.04 - $0.11 per GB (varies by region)
- HTTP(S) requests: $0.0075 per 10,000 requests

---

## Best Practices

1. **Use Service Account JSON files** for production deployments
2. **Store credentials securely** - never commit to version control
3. **Choose appropriate storage class** based on access patterns
4. **Use multi-region** for globally distributed users
5. **Enable versioning** for important content
6. **Set up monitoring** with Cloud Monitoring
7. **Configure lifecycle policies** to manage costs
8. **Use Cloud CDN** for high-traffic websites
9. **Implement CI/CD** for automated deployments
10. **Regular backups** of your bucket contents

---

## Additional Resources

- **GCS Documentation:** https://cloud.google.com/storage/docs
- **Cloud CDN Documentation:** https://cloud.google.com/cdn/docs
- **Pricing Calculator:** https://cloud.google.com/products/calculator
- **GCS Best Practices:** https://cloud.google.com/storage/docs/best-practices

---

## Version History

- **v1.0** (2025-11-19) - Initial GCS deployment guide
  - Service account setup
  - Authentication methods
  - Deployment examples
  - Cloud CDN overview
  - Troubleshooting guide
