# Backlink Satellite Site SEO Strategy

## Overview

A **backlink satellite site** is a secondary website designed to provide SEO value to a main production site through strategic backlinks. This is different from a staging/preview site or a primary production site.

## Critical SEO Configuration Differences

### Main Production Site vs Backlink Site

| Aspect | Main Site | Backlink Satellite Site |
|--------|-----------|------------------------|
| **Purpose** | Primary business website | SEO support through backlinks |
| **Domain** | restroomrentalsvirginia.com | CloudFront/S3 URL |
| **Canonical Tags** | Points to itself | Points to itself (NOT main site) |
| **Sitemap URLs** | Own domain URLs | Own CloudFront URLs |
| **Indexing** | MUST be indexed | MUST be indexed |
| **Content** | Primary content | Unique variations |
| **Links to Main** | Self-referential | Strategic backlinks |

## The Problem with Current Implementation

### What's Happening Now (WRONG for Backlink Sites)

**CloudFront Site**:
```html
<!-- Canonical points to main site -->
<link rel="canonical" href="https://restroomrentalsvirginia.com/">
```

**Sitemap.xml**:
```xml
<url>
  <loc>https://restroomrentalsvirginia.com/</loc>  <!-- Wrong! -->
</url>
```

**Result**: Google thinks CloudFront is a duplicate/mirror of the main site and **ignores it completely**. Zero backlink value.

### What Should Happen (CORRECT for Backlink Sites)

**CloudFront Site**:
```html
<!-- Canonical points to itself -->
<link rel="canonical" href="https://dslmqk0s3vj23.cloudfront.net/">
```

**Sitemap.xml**:
```xml
<url>
  <loc>https://dslmqk0s3vj23.cloudfront.net/</loc>  <!-- Correct! -->
</url>
```

**Result**: Google indexes CloudFront as an independent site, backlinks from it pass SEO value to main site.

## Configuration Solution

### Add to Client Config

```yaml
business:
  business_name: "Clean Restroom Rental Virginia"
  domain: "https://restroomrentalsvirginia.com"  # Main production site
  industry: "Porta Potty Rental"

# NEW SECTION: Deployment configuration
deployment:
  type: "backlink_site"  # Options: "main_site" or "backlink_site"
  deployed_url: "https://dslmqk0s3vj23.cloudfront.net"  # Actual deployment URL
  main_site_url: "https://restroomrentalsvirginia.com"  # Main site to link to
```

### Behavior Based on deployment.type

#### When `deployment.type: "main_site"`:
- Canonical tags → deployed_url (or domain if not specified)
- Sitemap URLs → deployed_url (or domain)
- robots.txt sitemap → deployed_url sitemap
- Links to own pages
- This is the primary site

#### When `deployment.type: "backlink_site"`:
- Canonical tags → deployed_url (CloudFront)
- Sitemap URLs → deployed_url (CloudFront)
- robots.txt sitemap → deployed_url sitemap
- Strategic links to main_site_url
- Content unique from main site
- Indexed independently

## Code Changes Needed

### 1. Update BusinessConfig Model

**File**: `src/core/config/models.py`

Add deployment configuration:
```python
@dataclass
class DeploymentConfig:
    """Deployment and SEO configuration"""
    type: str = "main_site"  # "main_site" or "backlink_site"
    deployed_url: str = ""  # Actual URL where site is deployed
    main_site_url: str = ""  # For backlink sites: URL to link to
```

Add to ClientConfig:
```python
@dataclass
class ClientConfig:
    business: BusinessConfig
    contact: ContactConfig
    products: List[ProductConfig]
    services: List[ServiceConfig]
    locations: List[LocationConfig]
    branding: BrandingConfig
    cloud: CloudConfig
    deployment: DeploymentConfig = field(default_factory=DeploymentConfig)  # NEW
```

### 2. Update Page Generator

**File**: `src/core/generators/page_generator.py`

Update canonical URL logic:
```python
def _get_canonical_base_url(self, config: ClientConfig) -> str:
    """Get the base URL for canonical tags and sitemaps"""

    # For backlink sites, use the deployed URL
    if config.deployment.type == "backlink_site" and config.deployment.deployed_url:
        return config.deployment.deployed_url.rstrip("/")

    # For main sites, use deployed_url if specified, otherwise domain
    if config.deployment.deployed_url:
        return config.deployment.deployed_url.rstrip("/")

    # Default to business domain
    return config.business.domain.rstrip("/")
```

Update sitemap generation:
```python
def _generate_sitemap(self, config: ClientConfig, pages: List[str]) -> str:
    base_url = self._get_canonical_base_url(config)
    # ... rest of sitemap generation using base_url
```

Update template context:
```python
# In _create_base_context()
context["canonical_base_url"] = self._get_canonical_base_url(config)
context["is_backlink_site"] = config.deployment.type == "backlink_site"
context["main_site_url"] = config.deployment.main_site_url if hasattr(config.deployment, 'main_site_url') else ""
```

### 3. Update Templates

**All page templates** should use:
```jinja2
<link rel="canonical" href="{{ canonical_base_url }}/{{ page_path }}">
```

**For backlink sites**, add strategic internal links:
```jinja2
{% if is_backlink_site and main_site_url %}
<!-- Strategic backlink to main site -->
<p>Visit our main website at <a href="{{ main_site_url }}" rel="noopener">{{ business.business_name }}</a></p>
{% endif %}
```

## Backlink Site Best Practices

### 1. Content Differentiation

**Don't**: Copy-paste content from main site
**Do**: Create unique variations with:
- Different writing style
- Additional details
- Alternative keywords
- Unique perspectives

### 2. Strategic Linking

**Don't**: Every page links to main site (looks spammy)
**Do**: Natural, strategic links:
- Footer: "Visit our main site"
- About page: Company profile link
- Service pages: "Learn more on our main site"
- City pages: "Also serving [city] from our main location"

### 3. Anchor Text Variety

**Don't**: All links say "click here" or company name
**Do**: Vary anchor text naturally:
- "portable restroom rentals in Virginia"
- "Clean Restroom Rental Virginia"
- "our main website"
- "professional porta potty services"

### 4. Link Placement

**Natural locations**:
- Contextual in body content
- Footer copyright/company info
- About us page
- Contact page ("or visit our main site")

**Avoid**:
- Sidebar with 20 links
- Header with multiple main site links
- Every paragraph linking out

## SEO Value Calculation

### Factors That Determine Backlink Value

1. **Site Authority**: How trusted is the satellite site?
   - Domain age
   - Content quality
   - Indexing status
   - Inbound links it receives

2. **Content Quality**: Is content unique and valuable?
   - Not duplicate
   - Comprehensive (800+ words per page)
   - Well-structured
   - Relevant keywords

3. **Link Context**: Where/how links appear?
   - Natural placement
   - Relevant anchor text
   - In-content (better) vs footer (weaker)

4. **Site Relationship**: Does Google detect same owner?
   - Different hosting (CloudFront vs main)
   - Different IP address
   - Different CMS/structure
   - Different content

## Monitoring Backlink Effectiveness

### Google Search Console

**CloudFront Site** (Backlink):
1. Add as separate property
2. Submit sitemap
3. Monitor indexing status
4. Check for manual actions

**Main Site**:
1. Monitor "Links" report
2. Check for CloudFront backlinks
3. Track position changes for targeted keywords

### Expected Timeline

- **Week 1-2**: Sitemap submitted, crawl begins
- **Week 3-4**: Pages start getting indexed
- **Week 6-8**: Backlinks detected by Google
- **Week 10-12**: SEO benefit starts showing
- **Month 3-6**: Full impact visible

## Risks and Considerations

### Private Blog Network (PBN) Concerns

**Risk**: Google penalizes PBNs (networks of sites solely for backlinks)

**Mitigation**:
- Provide genuine value (comprehensive city guides)
- Unique content on each site
- Don't overlink to main site
- Maintain quality standards
- Different hosting infrastructure

### Duplicate Content Penalty

**Risk**: If content too similar to main site

**Mitigation**:
- AI-generated unique variations
- Different page structures
- Focus on different aspects/angles
- Use canonical tags correctly (to self, not main)

### Link Schemes Violation

**Risk**: Google penalizes manipulative link building

**Mitigation**:
- Natural link placement
- Relevant, contextual links
- Disclosed relationships if required
- Focus on user value

## Example Configuration

**Clean Restroom Rental Virginia - Backlink Site**

```yaml
business:
  business_name: "Clean Restroom Rental Virginia"
  domain: "https://restroomrentalsvirginia.com"
  industry: "Porta Potty Rental"
  description: "Comprehensive guide to portable restroom rentals across Virginia and Maryland"

deployment:
  type: "backlink_site"
  deployed_url: "https://dslmqk0s3vj23.cloudfront.net"
  main_site_url: "https://restroomrentalsvirginia.com"

seo:
  allow_indexing: true  # MUST be true for backlink value
  index_follow: true

content:
  focus: "location_guides"  # Focus on comprehensive city guides
  unique_angle: "detailed_local_info"  # Differentiate from main site
```

## Testing Checklist

After deployment, verify:

- [ ] robots.txt allows indexing (`Allow: /`)
- [ ] Canonical tags point to CloudFront (not main site)
- [ ] Sitemap contains CloudFront URLs
- [ ] Sitemap submitted to Google Search Console
- [ ] Strategic backlinks to main site present
- [ ] Content is unique (run plagiarism check)
- [ ] Main site Google Search Console shows CloudFront backlinks (after indexing)

## Summary

**Current Status**: CloudFront site is configured as duplicate of main site (no SEO value)

**Required Changes**:
1. Add `deployment` configuration section
2. Update canonical tags to use CloudFront URL
3. Update sitemap to use CloudFront URLs
4. Keep indexing enabled (you fixed this!)
5. Ensure content differentiation

**Result**: CloudFront becomes an independent SEO asset providing backlink value to main production site.
