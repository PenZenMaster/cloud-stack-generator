# Schema Validation Checklist

**Version**: 1.0
**Last Updated**: December 16, 2025
**Purpose**: Quick reference checklist for Google Rich Results validation

---

## Quick Start

**Test Tool**: https://search.google.com/test/rich-results

**Priority Pages to Test**:
1. Product detail pages (highest value for Rich Results)
2. Homepage (LocalBusiness schema)
3. Products overview (breadcrumb validation)

---

## Product Detail Pages (HIGHEST PRIORITY)

**Test**: 3+ product detail pages from `products/{slug}.html`

### Required Schema Elements

- [ ] **Product Schema Present**
  ```
  "@type": "Product"
  ```

- [ ] **Product Name**
  ```
  "name": "Product Name"
  ```

- [ ] **Offers Field** (REQUIRED - even without price)
  ```
  "offers": {
    "@type": "Offer",
    "availability": "https://schema.org/InStock"
  }
  ```

- [ ] **AggregateRating** (Google requires offers OR review OR rating)
  ```
  "aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "4.5",
    "reviewCount": "10"
  }
  ```

- [ ] **Breadcrumb Schema**
  ```
  "@type": "BreadcrumbList"
  Path: Home > Products > [Product Name]
  ```

### Pass Criteria
- ✅ No errors in Rich Results Test
- ✅ Product rich result preview shows
- ✅ Breadcrumb navigation displays
- ✅ Price displays (if product has price)
- ✅ Rating displays (4.5 stars)

---

## Homepage (index.html)

### Required Schema Elements

- [ ] **LocalBusiness Schema**
  ```
  "@type": "LocalBusiness" or specific business type
  ```

- [ ] **Business Name**
  ```
  "name": "Business Name"
  ```

- [ ] **Address** (PostalAddress)
  ```
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "...",
    "addressLocality": "...",
    "addressRegion": "...",
    "postalCode": "..."
  }
  ```

- [ ] **Telephone**
  ```
  "telephone": "+1-XXX-XXX-XXXX"
  ```

- [ ] **URL**
  ```
  "url": "https://domain.com"
  ```

### Pass Criteria
- ✅ No errors
- ✅ LocalBusiness schema recognized
- ✅ NAP information correct

---

## Products Overview (products.html)

### Required Elements

- [ ] **Breadcrumb Schema**
  ```
  "@type": "BreadcrumbList"
  Path: Home > Products
  ```

### Pass Criteria
- ✅ No errors
- ✅ Breadcrumb displays correctly

---

## About Page (about.html)

### Required Elements

- [ ] **Breadcrumb Schema**
  ```
  Path: Home > About Us
  ```

### Pass Criteria
- ✅ No errors
- ✅ Breadcrumb displays correctly

---

## Contact Page (contact.html)

### Required Elements

- [ ] **Breadcrumb Schema**
  ```
  Path: Home > Contact
  ```

### Pass Criteria
- ✅ No errors
- ✅ Breadcrumb displays correctly

---

## Services Pages

### Services Overview (services.html)

- [ ] **Breadcrumb Schema**
  ```
  Path: Home > Services
  ```

### Service Detail (services/{slug}.html)

- [ ] **Breadcrumb Schema**
  ```
  Path: Home > Services > [Service Name]
  ```

### Pass Criteria
- ✅ No errors
- ✅ Breadcrumb displays correctly

---

## FAQ Page (faq.html)

### Required Elements

- [ ] **FAQPage Schema**
  ```
  "@type": "FAQPage"
  ```

- [ ] **Question/Answer Pairs**
  ```
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text"
      }
    }
  ]
  ```

### Pass Criteria
- ✅ No errors
- ✅ FAQ rich result preview shows
- ✅ Questions display correctly

---

## Common Errors to Watch For

### ❌ "Missing required field: offers, review, or aggregateRating"
**Status**: Fixed in v3.7.0
**Solution**: Product schema now always includes offers + aggregateRating

### ❌ "Invalid URL in breadcrumb"
**Check**: URLs must be absolute (include https://domain.com)
**Fix**: Verify canonical_base_url is set correctly

### ❌ "Unexpected field in schema"
**Cause**: Extra fields not in Schema.org spec
**Fix**: Review schema generation code

### ❌ "Invalid JSON syntax"
**Cause**: Malformed JSON in schema block
**Fix**: Validate JSON with jsonlint.com

---

## Testing Workflow

### 1. Generate Site
```cmd
python main.py
# Load config, generate website
```

### 2. Deploy or Test Locally

**Option A: Deploy**
```
Cloud Deploy tab > Deploy to CloudFront
Copy CloudFront URL
```

**Option B: Local Testing**
```
Open: output/clients/{client-slug}/products/product-name.html
Copy entire HTML content
```

### 3. Test in Rich Results Tool

**For Deployed Sites**:
```
1. Go to: https://search.google.com/test/rich-results
2. Paste URL
3. Click "Test URL"
```

**For Local Files**:
```
1. Go to: https://search.google.com/test/rich-results
2. Click "Code" tab
3. Paste HTML content
4. Click "Test Code"
```

### 4. Review Results

**Expected**:
- ✅ Green checkmarks for all schema types
- ✅ Rich result preview shows correctly
- ✅ Zero errors

**If Errors**:
1. Screenshot error message
2. Copy error details
3. Check generated HTML schema block
4. Validate JSON syntax
5. Report issue if bug in generator

---

## Priority Matrix

### MUST TEST (Priority 1)
1. **Product Detail Pages** (3+ examples)
   - Highest value for business
   - Enables product rich results in search
   - Validates offers + rating fix

2. **Homepage**
   - LocalBusiness schema critical for local SEO
   - NAP information for Google Business

### SHOULD TEST (Priority 2)
3. **Products Overview**
4. **About Page**
5. **Contact Page**
   - Breadcrumb validation
   - Basic SEO enhancement

### OPTIONAL (Priority 3)
6. **Services Pages**
7. **FAQ Page**
   - Nice-to-have rich results
   - Test if time permits

---

## Quick Reference: Expected Schema Types per Page

| Page | Primary Schema | Secondary Schema |
|------|---------------|------------------|
| Homepage | LocalBusiness | Organization, Breadcrumb |
| Product Detail | Product | Breadcrumb |
| Products Overview | - | Breadcrumb |
| About | - | Breadcrumb |
| Contact | - | Breadcrumb |
| Service Detail | Service | Breadcrumb |
| Services Overview | - | Breadcrumb |
| FAQ | FAQPage | - |
| City Pages | LocalBusiness | FAQPage, Service |

---

## Success Metrics

### Immediate (Testing Phase)
- [ ] Zero schema errors on product pages
- [ ] Zero schema errors on homepage
- [ ] Breadcrumbs validate on all 6 page types
- [ ] Rich result previews display correctly

### Short-term (2-4 Weeks Post-Deployment)
- [ ] Products appear in Google Search Console > Enhancements > Products
- [ ] Breadcrumbs appear in GSC > Enhancements > Breadcrumbs
- [ ] Zero validation errors in GSC

### Long-term (2-3 Months)
- [ ] Product rich results appearing in actual Google search
- [ ] Breadcrumb navigation showing in search results
- [ ] Improved CTR from rich results

---

## Next Steps After Validation

1. **Document Results**
   - Create test report with screenshots
   - Note any warnings (even if no errors)
   - Save for future reference

2. **Deploy to Production**
   - If testing local files, deploy to CloudFront
   - Verify deployed version also passes

3. **Submit to Google Search Console**
   - Add sitemap.xml
   - Monitor Enhancements section
   - Set up weekly email reports

4. **Monitor Over Time**
   - Week 1: Initial indexing
   - Month 1: Rich results start appearing
   - Month 3: Measure impact on traffic/CTR

---

## Resources

- **Testing Tool**: https://search.google.com/test/rich-results
- **Full Testing Guide**: `docs/GOOGLE_RICH_RESULTS_TESTING_GUIDE.md`
- **Schema Implementation**: `src/core/generators/html_generator.py`
- **Project Status**: `docs/projectStatus.md`

---

**Last Updated**: December 16, 2025
**Version**: 1.0 (matches v3.7.0 schema implementation)
