# Naming Conventions

## Overview

This project uses different naming conventions depending on the context to follow best practices for each platform.

## File System (Local)

**Convention**: `snake_case` (Python standard)

**Examples**:
```
output/clients/clean_restroom_rental_va/
output/clients/salvo_metal_works/
src/core/deployment/
```

**Why**: Python convention for file paths and module names

## AWS S3

### Bucket Names

**Convention**: `kebab-case` (required by AWS)

**Examples**:
```
sanitation-rentals
my-company-website
client-hosting-bucket
```

**Rules**:
- Must be lowercase
- Must use hyphens (underscores NOT allowed)
- 3-63 characters
- Must be globally unique across all AWS
- No spaces or special characters

### Directory Names (S3 Prefixes)

**Convention**: `kebab-case` (recommended)

**Examples**:
```
s3://sanitation-rentals/clean-restroom-rental-va/
s3://sanitation-rentals/clean-restroom-rental-fl/
```

**Why**:
- URL-friendly (directory becomes part of website URL)
- Consistent with bucket naming
- Better for SEO
- Standard web convention
- More readable in browser address bar

**URL Impact**:
```
Good: http://bucket.s3-website.amazonaws.com/clean-restroom-rental-va/
Bad:  http://bucket.s3-website.amazonaws.com/clean_restroom_rental_va/
```

## Python Code

### Variables and Functions

**Convention**: `snake_case` (PEP 8 standard)

**Examples**:
```python
client_slug = "clean_restroom_rental_va"
def deploy_client_website(client_slug: str):
    output_path = Path("output/clients") / client_slug
```

### Classes

**Convention**: `PascalCase` (PEP 8 standard)

**Examples**:
```python
class S3WebsiteDeployer:
class ClientConfig:
class CityPageGenerator:
```

### Constants

**Convention**: `UPPER_SNAKE_CASE` (PEP 8 standard)

**Examples**:
```python
DEFAULT_REGION = "us-east-1"
MAX_UPLOAD_RETRIES = 3
```

## Automatic Conversion

The deployment module automatically converts naming conventions:

```python
# Local filesystem uses snake_case
local_path = Path("output/clients/clean_restroom_rental_va")

# Automatically converted to kebab-case for S3
s3_directory = "clean-restroom-rental-va"

# Deployment function handles conversion
deploy_client_website("clean_restroom_rental_va")
# Deploys to: s3://bucket/clean-restroom-rental-va/
```

### Implementation

**File**: `src/core/deployment/s3_deployer.py`

```python
def deploy_client_website(client_slug: str, ...):
    # Local path uses snake_case (Python convention)
    output_path = Path("output/clients") / client_slug

    # Convert to kebab-case for S3 (web convention)
    s3_directory = client_slug.replace("_", "-")

    # Deploy with kebab-case directory name
    deployer.deploy_website(
        subdirectory=s3_directory,
        ...
    )
```

## Client Identifiers

**Local Storage**: `snake_case`
```
clean_restroom_rental_va
salvo_metal_works
```

**S3 Deployment**: `kebab-case` (auto-converted)
```
clean-restroom-rental-va
salvo-metal-works
```

**Configuration Files**: Either (converted during processing)
```yaml
# config/clients/clean_restroom_rental_va.yaml
client_slug: clean_restroom_rental_va  # or clean-restroom-rental-va
```

## URL Slugs

**Convention**: `kebab-case`

**Examples**:
- City pages: `/locations/bethesda-md.html`
- Product pages: `/products/luxury-flushing-unit.html`
- Service pages: `/services/portable-restroom-rental.html`

**Jinja2 Filter**:
```jinja2
{{ city.name|slugify }}  <!-- "Bethesda, MD" becomes "bethesda-md" -->
{{ product.name|slugify }}  <!-- "Luxury Flushing Unit" becomes "luxury-flushing-unit" -->
```

## Summary Table

| Context | Convention | Example | Required? |
|---------|-----------|---------|-----------|
| Local file paths | `snake_case` | `clean_restroom_rental_va/` | Python standard |
| S3 bucket names | `kebab-case` | `sanitation-rentals` | AWS requirement |
| S3 directories | `kebab-case` | `clean-restroom-rental-va/` | Best practice |
| Python variables | `snake_case` | `client_slug` | PEP 8 |
| Python classes | `PascalCase` | `S3WebsiteDeployer` | PEP 8 |
| Python constants | `UPPER_SNAKE_CASE` | `DEFAULT_REGION` | PEP 8 |
| URL slugs | `kebab-case` | `/bethesda-md.html` | Web standard |

## Migration Notes

If you have existing deployments with snake_case directories in S3:

```bash
# List existing deployments
aws s3 ls s3://sanitation-rentals/ --profile AWS

# Remove old snake_case directory
aws s3 rm s3://sanitation-rentals/old_snake_case_name/ --recursive --profile AWS

# Redeploy with kebab-case (automatic)
python -c "from src.core.deployment import deploy_client_website; deploy_client_website('client_name')"
```

The new deployment will create the kebab-case directory automatically.

## References

- [PEP 8 - Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [AWS S3 Bucket Naming Rules](https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html)
- [URL Slug Best Practices](https://moz.com/learn/seo/url)
