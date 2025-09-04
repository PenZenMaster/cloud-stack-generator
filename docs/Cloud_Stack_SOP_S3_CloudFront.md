
# Cloud Stack SOP (S3 + Optional CloudFront) — **Reusable Playbook**
*Version:* 2025-08-15  
*Author:* Skippy the SEO Visionary 🛠️

> This SOP shows how to: (A) set up AWS Identity Center access, (B) create the least‑privilege role to publish static “Cloud Stack” sites, (C) deploy a pillar site to S3 (or CloudFront + OAC), and (D) update an existing stack safely.

---

## Table of Contents
- [0) What This Produces](#0-what-this-produces)
- [1) Prerequisites](#1-prerequisites)
- [2) Identity Center (SSO) Setup](#2-identity-center-sso-setup)
- [3) Permission Set (Least-Privilege)](#3-permission-set-least-privilege)
- [4) Assign Access](#4-assign-access)
- [5) Configure AWS CLI with SSO](#5-configure-aws-cli-with-sso)
- [6) Folder Structure (Per Pillar)](#6-folder-structure-per-pillar)
- [7) Hosting Models](#7-hosting-models)
- [8) Create & Deploy a New Pillar (Public S3)](#8-create--deploy-a-new-pillar-public-s3)
- [9) Create & Deploy via CloudFront + OAC (Private Bucket)](#9-create--deploy-via-cloudfront--oac-private-bucket)
- [10) Updating an Existing Stack](#10-updating-an-existing-stack)
- [11) SEO Wiring Checklist](#11-seo-wiring-checklist)
- [12) Naming & Conventions](#12-naming--conventions)
- [13) Troubleshooting Quick Hits](#13-troubleshooting-quick-hits)
- [Appendix A: Inline Policy JSON](#appendix-a-inline-policy-json)
- [Appendix B: Public S3 Bucket Policy](#appendix-b-public-s3-bucket-policy)
- [Appendix C: PowerShell Deploy Script (Public S3)](#appendix-c-powershell-deploy-script-public-s3)
- [Appendix D: Bash Deploy Script (Public S3)](#appendix-d-bash-deploy-script-public-s3)
- [Appendix E: CloudFront + OAC Notes](#appendix-e-cloudfront--oac-notes)

---

## 0) What This Produces
A small static **spec hub** (Docs/Diagrams/Calculator/FAQ/Schema) per product pillar that:
- lives on **Amazon S3** (optionally behind **CloudFront**),
- interlinks to the client’s money pages,
- is easy to re‑publish when files change.

---

## 1) Prerequisites
- **AWS CLI v2** installed
  ```powershell
  aws --version
  ```
- **Identity Center (SSO) profile** you can log into (we set this up below).

---

## 2) Identity Center (SSO) Setup
1. In AWS Console, search **IAM Identity Center** → **Enable** (creates org instance).  
2. **Groups** → **Create group** → `Cloud-Publishers`.  
3. **Users** → **Create user** → add yourself → add to **Cloud-Publishers**.  
4. **Settings → Setting summary** → note the **AWS access portal URL** and **Identity Center region**.

> MFA: In **Settings → Authentication → Multi‑factor authentication**, choose “Require users to provide an MFA code at every sign‑in.” Enroll via the access portal (Authenticator app / Security key).

---

## 3) Permission Set (Least-Privilege)
**IAM Identity Center → Permission sets → Create → Custom → Add Inline policy**.  
Use the inline JSON below (scoped to buckets that start `client-website-*`). Replace `client-website-*` with your preferred naming convention.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ListAll",
      "Effect": "Allow",
      "Action": ["s3:ListAllMyBuckets"],
      "Resource": "*"
    },
    {
      "Sid": "S3CreateBucket",
      "Effect": "Allow",
      "Action": ["s3:CreateBucket"],
      "Resource": "*"
    },
    {
      "Sid": "S3BucketMgmt",
      "Effect": "Allow",
      "Action": [
        "s3:PutBucketPolicy",
        "s3:GetBucketPolicy",
        "s3:PutBucketWebsite",
        "s3:GetBucketWebsite",
        "s3:PutBucketCors",
        "s3:GetBucketCors",
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "s3:PutBucketOwnershipControls",
        "s3:GetBucketOwnershipControls",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketPublicAccessBlock"
      ],
      "Resource": "arn:aws:s3:::client-website-*"
    },
    {
      "Sid": "S3ObjectOps",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:PutObjectTagging",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::client-website-*/*"
    }
  ]
}
```

**Name:** `S3-StaticSite-Publisher` (session duration 1h is fine).

---

## 4) Assign Access
- **AWS accounts** → select the target account → **Assign users or groups** → **Group = Cloud-Publishers** → **Permission set = S3-StaticSite-Publisher** → **Submit**.

---

## 5) Configure AWS CLI with SSO
```powershell
aws configure sso
# SSO start URL: your access portal URL (https://d-xxxx.awsapps.com/start)
# SSO region: Identity Center region (e.g., us-east-1)
# SSO registration scopes: sso:account:access
# Select account & role: pick your account + S3-StaticSite-Publisher
# Default region/output: e.g., us-east-1 / json
# Profile name: clientA
aws sso login --profile clientA
aws sts get-caller-identity --profile clientA
```

---

## 6) Folder Structure (Per Pillar)
```
client-name/
  pillar-slug/                       # e.g., roof-vents
    index.html
    spec_doc.html
    diagrams.html
    faq.html
    schema.json
    calculator.xlsx / calculator.csv
    robots.txt  | sitemap.xml | 404.html
    interlink_map.csv | utm_reference.csv (optional)
    s3-bucket-policy.json (template)
    s3-cors.json (template)
    deploy_to_s3.ps1  (PowerShell)
    deploy_to_s3.sh   (bash, optional)
```

---

## 7) Hosting Models
**A) Public S3 Website (fastest)** — requires public-read bucket policy and bucket‑level public access enabled.  
**B) CloudFront + Origin Access Control (recommended)** — bucket stays private; public via CDN; works even if account blocks public buckets.

---

## 8) Create & Deploy a New Pillar (Public S3)
> Variables (PowerShell)
```powershell
$env:AWS_PROFILE = "clientA"
$REGION = "us-east-1"
$ACCOUNT = "<your-account-id>"
$SLUG = "roof-vents"
$BUCKET = "client-website-$SLUG-$ACCOUNT"
```

### 8.1 Create bucket (handles us-east-1 quirk)
```powershell
# us-east-1: no LocationConstraint
aws s3api create-bucket --bucket $BUCKET --region $REGION
# non-us-east-1:
# aws s3api create-bucket --bucket $BUCKET --region $REGION --create-bucket-configuration LocationConstraint=$REGION
```

### 8.2 Allow public website (bucket-level)
```powershell
aws s3api put-bucket-public-access-block --bucket $BUCKET --public-access-block-configuration `
  BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false

@"
{
  "Version": "2012-10-17",
  "Statement": [{"Sid":"PublicReadGetObject","Effect":"Allow","Principal":"*","Action":["s3:GetObject"],"Resource":["arn:aws:s3:::$BUCKET/*"]}]
}
"@ | Set-Content -NoNewline policy.json

aws s3api put-bucket-policy --bucket $BUCKET --policy file://policy.json
aws s3 website s3://$BUCKET/ --index-document index.html --error-document 404.html
```

### 8.3 Upload with smart caching
```powershell
aws s3 sync . s3://$BUCKET/ --exclude "*" --include "*.html" --include "robots.txt" --include "sitemap.xml" `
  --cache-control "max-age=300,public" --content-type "text/html"
aws s3 sync . s3://$BUCKET/ --exclude "*" --include "*.json" --include "*.csv" --include "*.xlsx" `
  --cache-control "max-age=86400,public"
```

**Website endpoint:**
```
http://$BUCKET.s3-website-$REGION.amazonaws.com
```

---

## 9) Create & Deploy via CloudFront + OAC (Private Bucket)
**Summary:**
1. Create S3 bucket (no public policy needed).  
2. Create a **CloudFront distribution** with **Origin Access Control (OAC)** attached to this bucket.  
3. Apply the **bucket policy** CloudFront wizard gives you (grants `s3:GetObject` to the distribution).  
4. Upload content to the bucket.  
5. Use the CloudFront domain (or your own domain + ACM certificate).  
6. On updates, **create invalidations** (e.g., `/*` or targeted paths).

> Tip: Default Behavior = GET/HEAD only; Viewer protocol = Redirect HTTP → HTTPS; Cache policy = CachingOptimized; TTL short for `.html`, long for data files (use separate cache behaviors if desired).

---

## 10) Updating an Existing Stack
1. Edit files locally. If you add a new page, update **sitemap.xml** and hub links.
2. Re‑publish:
   ```powershell
   # HTML & sitemap → short cache
   aws s3 sync . s3://$BUCKET/ --exclude "*" --include "*.html" --include "robots.txt" --include "sitemap.xml" --cache-control "max-age=300,public" --content-type "text/html"
   # Data files → longer cache
   aws s3 sync . s3://$BUCKET/ --exclude "*" --include "*.json" --include "*.csv" --include "*.xlsx" --cache-control "max-age=86400,public"
   ```
3. If using CloudFront, **invalidate** changed paths (or `/*`).  
4. Hard refresh in browser (Ctrl/Cmd+Shift+R).  
5. In Google Search Console, **Inspect → Request indexing** for the hub URL after major updates.

---

## 11) SEO Wiring Checklist
- Unique **H1** + meta description per page (B2B intent).  
- **Interlinking:** Every asset links **up** to hub, **across** to 1–2 related clusters, **down** to money page.  
- **Sitemap** contains hub, spec/faq/diagrams, calculators, and case studies.  
- **JSON-LD:**  
  - `WebPage` on all pages.  
  - `Product` (Manufacturer, `additionalProperty`, `isSimilarTo`) on spec pages.  
  - `TechArticle` for case studies/how‑tos.  
- **UTMs** on offsite promos to hub: `?utm_source=s3&utm_medium=stack&utm_campaign=<pillar>&utm_content=spec-pack`.

---

## 12) Naming & Conventions
- Buckets: `client-website-<pillar>-<accountid>`  
- CLI profiles: one per customer (`clientA`, `clientB`)  
- Pillar folders: one per product line; copy previous pillar and swap content.

---

## 13) Troubleshooting Quick Hits
- **403 AccessDenied (S3 website):** Bucket policy missing or wrong ARN; bucket‑level Public Access Block still **true**; or account‑level Block Public Access enforced (use **CloudFront + OAC**).  
- **`invalid_scope` during `aws configure sso`:** Identity Center **region mismatch**; re‑run `aws sso logout` then `aws configure sso` with the correct region and scopes `sso:account:access`.  
- **Bucket create fails in us-east-1:** Omit `--create-bucket-configuration`.  
- **Changes not visible:** Browser/CDN cache; for CloudFront, run an invalidation.

---

## Appendix A: Inline Policy JSON
*(Scoped to buckets that start with `client-website-*`. Adjust the prefix to your convention.)*
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "S3ListAll",
      "Effect": "Allow",
      "Action": ["s3:ListAllMyBuckets"],
      "Resource": "*"
    },
    {
      "Sid": "S3CreateBucket",
      "Effect": "Allow",
      "Action": ["s3:CreateBucket"],
      "Resource": "*"
    },
    {
      "Sid": "S3BucketMgmt",
      "Effect": "Allow",
      "Action": [
        "s3:PutBucketPolicy",
        "s3:GetBucketPolicy",
        "s3:PutBucketWebsite",
        "s3:GetBucketWebsite",
        "s3:PutBucketCors",
        "s3:GetBucketCors",
        "s3:GetBucketLocation",
        "s3:ListBucket",
        "s3:PutBucketOwnershipControls",
        "s3:GetBucketOwnershipControls",
        "s3:PutBucketPublicAccessBlock",
        "s3:GetBucketPublicAccessBlock"
      ],
      "Resource": "arn:aws:s3:::client-website-*"
    },
    {
      "Sid": "S3ObjectOps",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:PutObjectTagging",
        "s3:PutObjectAcl"
      ],
      "Resource": "arn:aws:s3:::client-website-*/*"
    }
  ]
}
```

## Appendix B: Public S3 Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "PublicReadGetObject",
    "Effect": "Allow",
    "Principal": "*",
    "Action": ["s3:GetObject"],
    "Resource": ["arn:aws:s3:::client-website-<pillar>-<accountid>/*"]
  }]
}
```

## Appendix C: PowerShell Deploy Script (Public S3)
```powershell
param([Parameter(Mandatory=$true)][string]$Bucket,[string]$Region="us-east-1",[string]$Profile="clientA")
$env:AWS_PROFILE = $Profile
if($Region -eq "us-east-1"){ aws s3api create-bucket --bucket $Bucket --region $Region } else { aws s3api create-bucket --bucket $Bucket --region $Region --create-bucket-configuration LocationConstraint=$Region }
aws s3api put-bucket-public-access-block --bucket $Bucket --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
@"
{"Version":"2012-10-17","Statement":[{"Sid":"PublicReadGetObject","Effect":"Allow","Principal":"*","Action":["s3:GetObject"],"Resource":["arn:aws:s3:::$Bucket/*"]}]}
"@ | Set-Content -NoNewline policy.json
aws s3api put-bucket-policy --bucket $Bucket --policy file://policy.json
aws s3 website s3://$Bucket/ --index-document index.html --error-document 404.html
aws s3 sync . s3://$Bucket/ --exclude "*" --include "*.html" --include "robots.txt" --include "sitemap.xml" --cache-control "max-age=300,public" --content-type "text/html"
aws s3 sync . s3://$Bucket/ --exclude "*" --include "*.json" --include "*.csv" --include "*.xlsx" --cache-control "max-age=86400,public"
```

## Appendix D: Bash Deploy Script (Public S3)
```bash
#!/usr/bin/env bash
set -euo pipefail
BUCKET="$1"; REGION="${2:-us-east-1}"
if [[ "$REGION" == "us-east-1" ]]; then
  aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" || true
else
  aws s3api create-bucket --bucket "$BUCKET" --region "$REGION" --create-bucket-configuration LocationConstraint="$REGION" || true
fi
aws s3api put-bucket-public-access-block --bucket "$BUCKET" --public-access-block-configuration BlockPublicAcls=false,IgnorePublicAcls=false,BlockPublicPolicy=false,RestrictPublicBuckets=false
cat > policy.json <<JSON
{"Version":"2012-10-17","Statement":[{"Sid":"PublicReadGetObject","Effect":"Allow","Principal":"*","Action":["s3:GetObject"],"Resource":["arn:aws:s3:::$BUCKET/*"]}]}
JSON
aws s3api put-bucket-policy --bucket "$BUCKET" --policy file://policy.json
aws s3 website "s3://$BUCKET/" --index-document index.html --error-document 404.html
aws s3 sync . "s3://$BUCKET/" --exclude "*" --include "*.html" --include "robots.txt" --include "sitemap.xml" --cache-control "max-age=300,public" --content-type "text/html"
aws s3 sync . "s3://$BUCKET/" --exclude "*" --include "*.json" --include "*.csv" --include "*.xlsx" --cache-control "max-age=86400,public"
```

## Appendix E: CloudFront + OAC Notes
- Keep the bucket **private**; let CloudFront handle all public access.  
- Use the **OAC wizard** in the console; copy the **exact bucket policy** it provides.  
- **Default behavior**: GET/HEAD, redirect HTTP→HTTPS, CachingOptimized policy.  
- **Invalidations** after HTML changes (e.g., `/*` or specific paths).  
- Use your own domain via **Route 53** + **ACM** (certificate in the **us-east-1** region for global distributions).

---

**That’s it.** Duplicate this folder per pillar, swap the copy, adjust JSON‑LD, update interlinks → deploy. FTP nostalgia optional. 😄
