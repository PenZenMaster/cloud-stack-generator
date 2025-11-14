# SEO and Search Engine Indexing Strategy

## Overview

Generated websites are **indexable by default** to maximize SEO value and search engine discoverability. This document explains the indexing strategy and how to control it.

## Default Behavior (Production)

**robots.txt**:
```
User-agent: *
Allow: /

Sitemap: https://yourdomain.com/sitemap.xml
```

**What this means**:
- ✓ All search engines can crawl and index the site
- ✓ Sitemap is provided for better indexing
- ✓ No restrictions on pages or directories
- ✓ Site will appear in Google, Bing, etc.

## When to Allow Indexing

**Use indexable robots.txt (default) when**:
1. Site is ready for production
2. Content is final and reviewed
3. This is the primary/only URL for the business
4. You want maximum SEO exposure
5. Client has paid for SEO-optimized content

**Benefits**:
- Search engine traffic
- Local SEO rankings
- Brand visibility
- Lead generation from organic search

## When to Block Indexing

**Use non-indexable robots.txt when**:
1. Site is in development/staging
2. Content is still being reviewed
3. This is a preview URL (client will use custom domain)
4. Avoiding duplicate content with another domain

**robots.txt for staging**:
```
User-agent: *
Disallow: /
```

## Configuration

### Option 1: Default (Recommended)

No configuration needed - sites are indexable by default.

### Option 2: Block Indexing (Staging)

Add to client config YAML:

```yaml
business:
  business_name: "My Company"
  domain: "https://mycompany.com"
  allow_indexing: false  # Add this line
```

## Deployment Scenarios

### Scenario 1: CloudFront is Production URL

**Setup**: CloudFront distribution is the only URL

```yaml
business:
  domain: "https://dslmqk0s3vj23.cloudfront.net"
  allow_indexing: true  # Default - allow search engines
```

**Result**: Site appears in search results under CloudFront URL

### Scenario 2: Custom Domain is Production

**Setup**: Client has custom domain (e.g., restroomrentalsvirginia.com)

**Option A - Dual Indexing** (both URLs indexable):
```yaml
business:
  domain: "https://restroomrentalsvirginia.com"
  allow_indexing: true  # CloudFront is also indexable
```

Use canonical tags to prefer custom domain:
```html
<link rel="canonical" href="https://restroomrentalsvirginia.com/page.html">
```

**Option B - Single Domain SEO** (block CloudFront):
```yaml
business:
  domain: "https://restroomrentalsvirginia.com"
  allow_indexing: false  # Block CloudFront indexing
```

CloudFront serves content but search engines ignore it. Custom domain needs its own robots.txt that allows indexing.

### Scenario 3: Development/Preview Site

**Setup**: Site is for client review before going live

```yaml
business:
  domain: "https://preview.cloudfront.net"
  allow_indexing: false  # Block until approved
```

**When to change**: Set `allow_indexing: true` when client approves and site goes live.

## SEO Best Practices

### 1. Canonical URLs

Always use canonical tags to indicate the preferred URL:

```html
<link rel="canonical" href="https://yourdomain.com/current-page.html">
```

Current implementation includes this automatically in all page templates.

### 2. Sitemap.xml

Every site gets an auto-generated sitemap.xml with:
- All main pages (index, about, contact, etc.)
- All city/location pages
- All product/service pages
- Proper priority and changefreq values

### 3. Meta Robots Tags

HTML pages include proper meta tags:

```html
<meta name="robots" content="index, follow">
```

### 4. Avoid Duplicate Content

If the same content appears at multiple URLs:

**Solution 1 - Canonical Tags** (preferred):
- Allow both URLs to be indexable
- Use canonical tags to indicate primary URL
- Search engines consolidate ranking signals

**Solution 2 - Block Secondary URL**:
- Block CloudFront with robots.txt
- Only custom domain is indexable
- Simpler but loses backup URL discoverability

## Google Search Console Setup

For maximum SEO benefit:

1. **Add Property** in Google Search Console:
   - Add the production URL (CloudFront or custom domain)

2. **Submit Sitemap**:
   ```
   https://yourdomain.com/sitemap.xml
   ```

3. **Request Indexing** for key pages:
   - Homepage
   - Top city pages
   - Main service/product pages

4. **Monitor**:
   - Coverage reports
   - Index status
   - Search performance

## Meta Tags and SEO

All generated pages include comprehensive SEO meta tags:

```html
<!-- Basic Meta -->
<title>Page Title - Business Name</title>
<meta name="description" content="...">
<meta name="keywords" content="...">
<meta name="robots" content="index, follow">

<!-- Open Graph -->
<meta property="og:title" content="...">
<meta property="og:description" content="...">
<meta property="og:url" content="...">

<!-- Canonical -->
<link rel="canonical" href="...">
```

## Checking Indexing Status

### Test if Your Site is Indexable

**Method 1 - Check robots.txt**:
```
https://yourdomain.com/robots.txt
```

Look for:
- `Allow: /` = Indexable ✓
- `Disallow: /` = Blocked ✗

**Method 2 - Google Search**:
```
site:yourdomain.com
```

If pages appear, site is indexed.

**Method 3 - robots.txt Tester**:
- Google Search Console → robots.txt Tester
- Test if Googlebot can access URLs

## Updating an Existing Site

If you need to change indexing status:

### Enable Indexing (was blocked, now allow)

1. Update client config: `allow_indexing: true`
2. Regenerate website
3. Deploy updated robots.txt
4. Submit sitemap to Google Search Console
5. Request indexing for key pages

**Timeline**: Google may take 2-4 weeks to fully index

### Disable Indexing (was allowed, now block)

1. Update client config: `allow_indexing: false`
2. Regenerate website
3. Deploy updated robots.txt
4. Pages will gradually drop from search results

**Timeline**: Google may take 4-12 weeks to fully de-index

## Summary

| Scenario | allow_indexing | robots.txt | Use Case |
|----------|---------------|------------|----------|
| Production | `true` (default) | `Allow: /` | Live client site |
| Staging | `false` | `Disallow: /` | Preview/testing |
| Custom Domain + CloudFront | `true` | `Allow: /` | Use canonical tags |
| Custom Domain Only | `false` on CloudFront | `Disallow: /` | Block CloudFront |

**Recommendation**: Use `allow_indexing: true` (default) for all production deployments unless you have a specific reason to block search engines.

## References

- [Google Robots.txt Specifications](https://developers.google.com/search/docs/crawling-indexing/robots/intro)
- [Canonical URLs Best Practices](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls)
- [XML Sitemaps Protocol](https://www.sitemaps.org/protocol.html)
