Feature Request
# 1) Overview

**Purpose**
Integration into AWG (Cloud Stack Generator) that securely stores AWS credentials, lets a user choose a local folder, creates/selects an S3 bucket and an (optional) prefix (“folder”), uploads contents with correct headers & caching, and publishes them as a public website via either:

* **Mode A (Simple):** S3 Static Website Hosting with a public bucket policy, or
* **Mode B (Recommended):** CloudFront + Origin Access Control (OAC) with the bucket kept private.

**Primary Users**

* SEO/marketing ops and devs who need fast, repeatable static site publishes.

**Platforms**

* Windows GUI (primary). CLI is optional (phase 2).

# 2) Goals & Non-Goals

**Goals**

* Secure credential storage (SSO/profile or access keys).
* Point-and-click folder selection; fast, resumable uploads.
* Create/select S3 bucket and key prefix.
* Publish as a public website in one click.
* Set proper `Content-Type`, `Cache-Control`, and other headers.
* Verify public reachability; show the live URL(s).

**Non-Goals**

* No dynamic back-end hosting.
* No WAF/CDN rules management beyond minimal CloudFront setup.
* No user management/SSO portal (beyond AWS SSO auth flow).

# 3) Assumptions & Constraints

* User has AWS account with sufficient permissions (see §10).
* Static sites include `index.html` (required) and optional `404.html`.
* Bucket names must be globally unique and DNS-compliant.
* Large folders must upload in parallel with multipart & retries.

# 4) Architecture

**High-Level Components**

1. **GUI** Current AWg Tool Kit.
2. **AWS Layer**: boto3 SDK wrappers for S3, STS, IAM (read-only), CloudFront, Route 53 (optional).
3. **Uploader**: parallel, resumable, checksum-verifying engine.
4. **Publishing Orchestrator**: applies website or CloudFront mode.
5. **Credential Store**: OS keychain (Windows Credential Manager / macOS Keychain).
6. **Config/Profiles**: local JSON or YAML for non-secret prefs.

**Data Flow (happy path)**

* User selects profile → selects local folder → selects/creates bucket → selects/creates prefix → choose publish mode → upload → set website/CF config → test & display public URL.

# 5) Security & Compliance

* **Credentials**:

  * Prefer **AWS SSO** or **AssumeRole** into target account.
  * If access keys are used, store **only** in OS keychain (encrypted at rest).
  * Never store plaintext secrets in config files.
* **Least Privilege**: use a dedicated IAM role or user with scoped policies (§10).
* **Public Access Controls**:

  * Mode A disables Block Public Access and installs **minimal** `GetObject` policy.
  * Mode B keeps bucket private; CloudFront OAC is the only reader.
* **Logging**: redact secrets; structured logs.

# 6) UX Specification

## 6.1 Onboarding Wizard (first run)

1. **Welcome** (explain Modes A vs B, quick comparison).
2. **AWS Auth**

   * Option 1: **AWS SSO** (enter start URL & account/role).
   * Option 2: **Assume Role** (source profile + role ARN).
   * Option 3: **Access Keys** (store in keychain).
3. **Profile Name** (save as reusable connection).

## 6.2 Cloud Upload tab

* **Profile selector** (dropdown) + “Manage Profiles”.
* **Local Folder**: choose path; show file count & total size; optional ignore patterns (`.git`, `node_modules`, custom globs).
* **Bucket**:

  * “Select existing” (list buckets) or “Create new”.
  * For “Create”: region, bucket name availability check.
* **Prefix (Folder in bucket)**: create/select (autocomplete).
* **Publishing Mode** (radio):

  * **Mode A:** S3 Static Website (fastest; public bucket).
  * **Mode B:** CloudFront + OAC (best-practice; private bucket).
* **Website Settings**: `index.html` (required), `error.html` (optional).
* **Caching & Headers** (presets + advanced):

  * HTML: `Cache-Control: no-cache` (or low TTL).
  * Assets (css/js/img/svg/webp): `Cache-Control: public, max-age=31536000, immutable`.
  * Auto-detect `Content-Type` from extension; allow overrides.
* **Start Upload** button with:

  * Progress bar, current file, throughput, ETA.
  * “Dry Run” toggle (phase 2).

## 6.3 Post-Upload Publish

* **Mode A** steps:

  * Enable static website hosting (new console API), set index/error.
  * Disable Block Public Access (bucket-level) and apply a **minimal** bucket policy for `s3:GetObject` on the chosen prefix or entire bucket.
  * Show website endpoint URL (e.g., `http://bucket.s3-website-<region>.amazonaws.com`).
* **Mode B** steps:

  * Create/attach CloudFront distribution with OAC to the bucket (origin path = prefix).
  * Default behavior: compress, HTTP/2+3, redirect to HTTPS, minimal cache behaviors; pass through index/error.
  * Optionally set custom domain & ACM cert (uploaded or requested).
  * Invalidate `/*` after first publish.
  * Show CloudFront domain (and custom domain if configured).
* **Validation**: test fetch of `/` and a random asset; display status.

## 6.4 Result Screen

* Live URL(s) (copy button).
* “Open site” button.
* “Save as Project” (stores mapping: profile, bucket, prefix, local folder, mode, header preset).
* “Publish again” shortcut.

## 6.5 Errors & Recovery

* Clear messages with remediation (e.g., “index.html not found”).
* Auto-retry transient network errors with exponential backoff.
* Multipart retry on failed parts only.
* Offer partial resume if interrupted.

# 7) Functional Requirements

1. **Credential Profiles**

   * Create, edit, delete.
   * Support SSO, AssumeRole, or Access Keys.
   * Store secrets in OS keychain; non-secrets in app config.

2. **Folder Selection**

   * Recursive discovery; ignore patterns; file count & size summary.
   * Detect missing `index.html`; warn prior to publish.

3. **Bucket Management**

   * List existing (with region).
   * Create bucket: validate name & region, configure options for chosen mode.

4. **Prefix (S3 “Folder”)**

   * Autocomplete existing prefixes.
   * Create new prefix; confirm when overwriting content.

5. **Upload**

   * Parallel transfer; multipart for large files (>8–16MB threshold).
   * Checksum (etag) compare & **smart diff** (skip unchanged; phase 2).
   * Set metadata: `Content-Type`, `Cache-Control`, `Content-Encoding` (gzip/brotli pass-through), `Expires` (optional), `x-amz-website-redirect-location` (optional).
   * Progress UI + summary (uploaded/ skipped/ failed).

6. **Publish Mode A — S3 Website**

   * Enable website hosting; set index & error docs.
   * Toggle Block Public Access off (with confirmation).
   * Install minimal bucket policy to allow `GetObject` for the site scope.
   * Surface website endpoint.

7. **Publish Mode B — CloudFront + OAC**

   * Create/attach distribution pointing to S3 origin with OAC.
   * Enforce HTTPS; compression; modern TLS.
   * Cache behaviors:

     * `/*` default; identify filetype TTL presets.
     * Optionally serve SPA with index fallback (phase 2).
   * Invalidate `/*` after deploy.
   * Optionally attach custom domain & ACM cert (user supplies domain or app can create Route 53 record if same account).

8. **Verification**

   * HTTP GET checks for `/` and one asset; show status & latency.

9. **Reporting**

   * Deployment log with timestamps, versions of changed files.
   * Exportable JSON summary.

# 8) Non-Functional Requirements

* **Performance**: 50k files or 5–10 GB should upload reliably with parallelism.
* **Reliability**: Retry transient failures; safe to re-run; idempotent bucket/prefix creation.
* **Usability**: 5-step wizard; defaults chosen for safety & speed.
* **Portability**: Works on macOS 13+ and Windows 10+.
* **Observability**: Structured logs; optional verbose mode.

# 9) File Handling & Headers (Default Matrix)

| Extension(s)                    | Content-Type             | Cache-Control                       |
| ------------------------------- | ------------------------ | ----------------------------------- |
| .html                           | text/html                | no-cache                            |
| .css                            | text/css                 | public, max-age=31536000, immutable |
| .js                             | application/javascript   | public, max-age=31536000, immutable |
| .mjs                            | text/javascript          | public, max-age=31536000, immutable |
| .png .jpg .jpeg .gif .webp .svg | image/\*                 | public, max-age=31536000, immutable |
| .ico                            | image/x-icon             | public, max-age=31536000, immutable |
| .json                           | application/json         | no-cache                            |
| .xml                            | application/xml          | no-cache                            |
| .txt                            | text/plain               | no-cache                            |
| fonts (.woff2 .woff .ttf .otf)  | font/\*                  | public, max-age=31536000, immutable |
| .map                            | application/octet-stream | no-cache                            |

* Advanced: allow custom per-path overrides (e.g., `/assets/legacy/*` shorter TTLs).

# 10) IAM & Permissions

**Minimum Effective Permissions** (attach to the role/user used by the app; scope to the target bucket where possible):

* **S3** (scoped to `arn:aws:s3:::<bucket>` and `arn:aws:s3:::<bucket>/*`):

  * `s3:ListAllMyBuckets` (for listing; or avoid by requiring bucket name)
  * `s3:ListBucket`, `s3:GetBucketLocation`, `s3:PutBucketPolicy`, `s3:GetBucketPolicy`, `s3:PutBucketWebsite`, `s3:GetBucketWebsite`, `s3:PutPublicAccessBlock`, `s3:GetPublicAccessBlock`
  * `s3:PutObject`, `s3:PutObjectAcl` (Mode A only if needed), `s3:DeleteObject`, `s3:GetObject`, `s3:ListBucketMultipartUploads`, `s3:AbortMultipartUpload`
* **CloudFront** (Mode B):

  * `cloudfront:CreateDistribution`, `cloudfront:UpdateDistribution`, `cloudfront:GetDistribution`, `cloudfront:CreateInvalidation`, `cloudfront:GetInvalidation`
* **IAM** (for OAC via CloudFront service, typically no direct IAM writes required if using CloudFront OAC APIs)
* **ACM** (optional if creating/requesting a cert in us-east-1):

  * `acm:RequestCertificate`, `acm:DescribeCertificate`
* **Route 53** (optional custom domain):

  * `route53:ChangeResourceRecordSets`, `route53:ListHostedZones`

**Mode A Note**: Requires disabling S3 Block Public Access and adding a public `GetObject` policy (app must show a strong warning).

# 11) Publishing Modes — Decision Matrix

| Criterion     | Mode A: S3 Website (Public)           | Mode B: CloudFront + OAC (Private) |
| ------------- | ------------------------------------- | ---------------------------------- |
| Setup Speed   | Fastest                               | Slower (distribution creation)     |
| Security      | Public bucket                         | Private bucket (best practice)     |
| HTTPS         | Not supported on S3 website endpoints | Native HTTPS, HTTP/2/3             |
| Performance   | Good (regional)                       | Global CDN, best performance       |
| Custom Domain | Possible via DNS CNAME (HTTP only)    | Fully supported with TLS           |
| Recommended   | For quick testing/demo                | For production                     |

# 12) Config & Persistence

* **Profiles**:

  * `name`, `auth_method` (sso/assume\_role/keys), `account_id`, `role`, `region`, optional `source_profile`.
  * Secrets (refresh tokens, keys) live in OS keychain only.
* **Projects**:

  * `profile_name`, `local_folder`, `bucket`, `region`, `prefix`, `mode`, `headers_preset`, `index`, `error`, `domain (optional)`, `last_deploy_at`.
* **Logs**: Rotating files; optional export.

# 13) Validation & Pre-flight Checks

* Bucket name validity and uniqueness (create path or choose existing).
* Region consistency (S3 + ACM us-east-1 nuance for CloudFront certs).
* `index.html` exists.
* Total size and est. time (advisory).
* DNS records present if custom domain is chosen (or offer to create).

# 14) Testing Plan

* **Unit**: header resolver, MIME mapping, diff logic, retry strategy.
* **Integration**: end-to-end to test buckets in a sandbox account for both modes.
* **UX**: cancel/resume mid-upload; handle network flap.
* **Security**: verify no plaintext secrets in logs/config.
* **Performance**: 10k/50k file test matrices with timing and error rates.

# 15) Telemetry & Observability

* Optional anonymous metrics: upload size, duration, success/failure (opt-in only).
* Error reports: stack traces with redaction.

# 16) Accessibility & i18n

* Keyboard-navigable UI; high-contrast theme option.
* Ready for future i18n (strings externalized).

# 17) Rollout & Backwards Compatibility

* Config versioning with migration logic.
* Safe handling of previously public buckets switching to Mode B (warn & assist).

# 18) Future Enhancements (nice-to-haves)

* CLI mode + CI integration (GitHub Actions) for automated deploys.
* Delta deploys via hashing to skip unchanged files.
* Brotli/Gzip pre-compression with `Content-Encoding`.
* SPA fallback routing (`/index.html` on 403/404) with CloudFront function.
* Multi-account quick-switch.
* Object lock for accidental deletes (off by default).

---

If you want, I can convert this spec into a short **requirements checklist** or a **work breakdown (WBS) + estimates**. When you’re ready for code, say the word and tell me your preferred stack (I suggest Python + PyQt + boto3).
