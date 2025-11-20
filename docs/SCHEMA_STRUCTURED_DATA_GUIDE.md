# Schema.org Structured Data Guide

**Version:** 3.4.1+
**Feature:** Schema & Structured Data Enhancements
**Status:** Production Ready - Validated by Google Rich Results Test
**Last Updated:** November 19, 2025

## Overview

The SEO Authority Website Generator automatically generates comprehensive Schema.org structured data (JSON-LD) for enhanced search engine visibility and rich results. This guide covers the enhanced schema features implemented in version 3.4.1+.

## Table of Contents

- [Features](#features)
- [Configuration](#configuration)
- [Conditional LocalBusiness Schema](#conditional-localbusiness-schema)
- [Schema Properties](#schema-properties)
- [Graph Structure](#graph-structure)
- [Usage Examples](#usage-examples)
- [Validation](#validation)
- [Troubleshooting](#troubleshooting)

---

## Features

### Implemented Schema Enhancements (v3.4.1+)

1. **Conditional LocalBusiness/Organization Schema**
   - Automatically selects the correct schema type based on address visibility
   - Uses `LocalBusiness` when address is public
   - Falls back to `Organization` when address is private

2. **areaServed Property**
   - Populated from city pages configuration
   - Includes proper City and State schema objects
   - Geographic containment relationships

3. **Product Schema Integration**
   - Products integrated into @graph structure
   - Entity linking via @id references
   - Offer schema with pricing and availability
   - Wikipedia entity linking via `isSimilarTo`

4. **Service Schema Integration**
   - Services integrated into @graph structure
   - Provider linking to business entity
   - Proper entity relationships

5. **sameAs Property**
   - Social media profiles automatically included
   - Supports Facebook, LinkedIn, Instagram, Twitter, YouTube

6. **knowsAbout Property**
   - Industry-specific Wikipedia URLs
   - Enhanced semantic understanding

---

## Configuration

### New Configuration Fields

#### GoogleBusinessProfileConfig

New typed dataclass for Google Business Profile integration:

```python
from src.core.config.models import GoogleBusinessProfileConfig

gbp = GoogleBusinessProfileConfig(
    profile_url="https://g.page/yourbusiness",
    expose_address=True,  # Controls LocalBusiness schema
    place_id="ChIJexample123",
    rating="4.8",
    review_count="127"
)
```

**Fields:**
- `profile_url` (str): Full Google Business Profile URL
- `expose_address` (bool): Whether GBP publicly shows the business address
- `place_id` (str): Google Maps Place ID
- `rating` (str): Average rating (e.g., "4.8")
- `review_count` (str): Number of reviews

#### AddressConfig Enhancement

New field added to control address visibility:

```python
from src.core.config.models import AddressConfig

address = AddressConfig(
    street="123 Main Street",
    city="Richmond",
    state="Virginia",
    zip_code="23219",
    country="United States",
    publish_on_website=True  # NEW: Controls schema address inclusion
)
```

**New Field:**
- `publish_on_website` (bool): Controls if address appears in LocalBusiness schema
  - Default: `True`
  - When `False`, address is excluded from schema even if provided

---

## Conditional LocalBusiness Schema

### How It Works

The generator intelligently selects between `LocalBusiness` and `Organization` schema types based on address visibility:

```python
# Implementation logic (src/core/generators/html_generator.py:486-493)
has_public_address = (
    config.google_business_profile.expose_address OR
    config.contact.address.publish_on_website
)

business_type = "LocalBusiness" if has_public_address else "Organization"
```

### Decision Matrix

| GBP expose_address | Address publish_on_website | Schema Type | Address Included |
|-------------------|---------------------------|-------------|------------------|
| True              | True                      | LocalBusiness | Yes |
| True              | False                     | LocalBusiness | Yes |
| False             | True                      | LocalBusiness | Yes |
| False             | False                     | Organization  | No |

### Use Cases

**1. Retail/Service Business with Physical Location**
```yaml
google_business_profile:
  expose_address: true  # OR
contact:
  address:
    publish_on_website: true
```
→ Uses `LocalBusiness` schema with full address

**2. Home-Based Business (Private Address)**
```yaml
google_business_profile:
  expose_address: false
contact:
  address:
    publish_on_website: false
```
→ Uses `Organization` schema without address

**3. Consulting/Virtual Business**
```yaml
google_business_profile:
  expose_address: false
contact:
  address:
    publish_on_website: false
```
→ Uses `Organization` schema, focuses on services/expertise

---

## Schema Properties

### Core Business Properties

All configurations include:
- `@type`: LocalBusiness or Organization
- `@id`: Unique identifier for entity linking
- `name`: Business name
- `description`: Business description
- `url`: Website URL
- `telephone`: Phone number
- `email`: Email address
- `logo`: Logo URL
- `image`: Primary business image

### areaServed Property

Geographic areas served by the business, populated from city pages:

```json
"areaServed": [
  {
    "@type": "City",
    "name": "Richmond",
    "containedIn": {
      "@type": "State",
      "name": "Virginia"
    }
  }
]
```

**Configuration:**
```python
config.city_pages.append(CityPageConfig(
    city_name="Richmond",
    state="Virginia"
))
```

**Fallback:** If no city pages, uses `config.target_cities` list.

### Product Schema

Products are integrated into the @graph with full entity linking:

```json
{
  "@type": "Product",
  "@id": "https://example.com/products/cupola#product",
  "name": "Custom Copper Cupola",
  "description": "Hand-crafted copper cupola",
  "category": "Architectural Metalwork",
  "brand": {
    "@id": "https://example.com#business"
  },
  "itemCondition": "https://schema.org/NewCondition",
  "sku": "CUP-001",
  "mpn": "CUP-001",
  "image": ["https://example.com/images/cupola.jpg"],
  "isSimilarTo": ["https://en.wikipedia.org/wiki/Cupola"],
  "offers": {
    "@type": "Offer",
    "price": "2500",
    "priceCurrency": "USD",
    "availability": "https://schema.org/InStock",
    "seller": {
      "@id": "https://example.com#business"
    }
  }
}
```

**Configuration:**
```python
config.products.append(ProductConfig(
    sku="CUP-001",
    name="Custom Copper Cupola",
    description="Hand-crafted copper cupola",
    category="Architectural Elements",
    price="2500",
    image_url="https://example.com/images/cupola.jpg"
))
```

**Note:** Product images are recommended by Google for rich results. Always include `image_url`.

### Service Schema

Services are integrated with provider linking:

```json
{
  "@type": "Service",
  "@id": "https://example.com/services/fabrication#service",
  "name": "Custom Metal Fabrication",
  "description": "Precision metal fabrication services",
  "provider": {
    "@id": "https://example.com#business"
  }
}
```

**Configuration:**
```python
config.services.append(ServiceConfig(
    name="Custom Metal Fabrication",
    description="Precision metal fabrication services"
))
```

### sameAs Property

Social media profiles for brand consistency:

```json
"sameAs": [
  "https://facebook.com/yourbusiness",
  "https://linkedin.com/company/yourbusiness",
  "https://instagram.com/yourbusiness"
]
```

**Configuration:**
```python
config.social_media = SocialMediaConfig(
    facebook="https://facebook.com/yourbusiness",
    linkedin="https://linkedin.com/company/yourbusiness",
    instagram="https://instagram.com/yourbusiness"
)
```

---

## Graph Structure

The schema uses @graph for proper entity relationships:

```json
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "LocalBusiness",
      "@id": "https://example.com#business"
    },
    {
      "@type": "WebSite",
      "@id": "https://example.com#website",
      "publisher": { "@id": "https://example.com#business" }
    },
    {
      "@type": "WebPage",
      "@id": "https://example.com#webpage",
      "about": { "@id": "https://example.com#business" }
    },
    {
      "@type": "Product",
      "brand": { "@id": "https://example.com#business" }
    },
    {
      "@type": "Service",
      "provider": { "@id": "https://example.com#business" }
    }
  ]
}
```

### Entity Relationships

- **WebSite** → `publisher` references Business
- **WebPage** → `about` references Business
- **Product** → `brand` references Business
- **Service** → `provider` references Business

All relationships use `@id` references for proper semantic linking.

---

## Usage Examples

### Example 1: Retail Store with Public Address

```python
from src.core.config.models import *

config = ClientConfig(
    business=BusinessConfig(
        business_name="Acme Hardware",
        domain="https://acmehardware.com",
        industry="Retail",
        description="Your local hardware store"
    ),
    contact=ContactConfig(
        phone="+1-555-123-4567",
        email="info@acmehardware.com",
        address=AddressConfig(
            street="123 Main Street",
            city="Richmond",
            state="Virginia",
            zip_code="23219",
            publish_on_website=True  # Public address
        )
    ),
    google_business_profile=GoogleBusinessProfileConfig(
        profile_url="https://g.page/acmehardware",
        expose_address=True,
        rating="4.8",
        review_count="342"
    ),
    social_media=SocialMediaConfig(
        facebook="https://facebook.com/acmehardware"
    )
)

# Add products
config.products.append(ProductConfig(
    sku="HAMMER-001",
    name="Professional Hammer",
    description="Heavy-duty construction hammer",
    price="29.99",
    image_url="https://acmehardware.com/images/hammer.jpg"
))

# Add city pages for areaServed
config.city_pages.append(CityPageConfig(
    city_name="Richmond",
    state="Virginia"
))
```

**Result:** LocalBusiness schema with address, product, and areaServed.

### Example 2: Consulting Firm with Private Address

```python
config = ClientConfig(
    business=BusinessConfig(
        business_name="Elite Consulting",
        domain="https://eliteconsulting.com",
        industry="Business Consulting"
    ),
    contact=ContactConfig(
        phone="+1-555-987-6543",
        email="contact@eliteconsulting.com",
        address=AddressConfig(
            street="Private",
            city="Arlington",
            state="Virginia",
            publish_on_website=False  # Private address
        )
    ),
    google_business_profile=GoogleBusinessProfileConfig(
        expose_address=False  # Also private
    ),
    social_media=SocialMediaConfig(
        linkedin="https://linkedin.com/company/eliteconsulting"
    )
)

# Add services
config.services.append(ServiceConfig(
    name="Business Strategy Consulting",
    description="Strategic planning and execution"
))
```

**Result:** Organization schema without address, with service.

---

## Validation

### Google Rich Results Test

The generated schema is validated with Google's official tool:

**URL:** https://search.google.com/test/rich-results

**Validation Steps:**

1. Generate your site with the schema enhancements
2. Copy the JSON-LD from the `<head>` section
3. Paste into Google's Rich Results Test (CODE tab)
4. Review results

**Expected Results:**
- ✅ Valid LocalBusiness or Organization entity
- ✅ Valid Product entities (if products configured)
- ✅ Valid Service entities (if services configured)
- ✅ No critical errors
- ✅ Entity relationships recognized

**Test Status:** 100% validated as of November 19, 2025

### Validation Tools

Test files included in repository:
- `test_schema_output.py` - Comprehensive test scenarios
- `schema_for_google_test.json` - Sample validated schema

Run tests:
```bash
python test_schema_output.py
```

---

## Troubleshooting

### Issue: Address not appearing in schema

**Cause:** Both address visibility flags are false.

**Solution:** Set at least one to true:
```python
# Option 1: Publish address on website
config.contact.address.publish_on_website = True

# Option 2: Expose via Google Business Profile
config.google_business_profile.expose_address = True
```

### Issue: Product missing image warning

**Cause:** Product configured without `image_url`.

**Solution:** Always include product images:
```python
ProductConfig(
    sku="PROD-001",
    name="Product Name",
    image_url="https://example.com/image.jpg"  # Required for rich results
)
```

### Issue: No areaServed property

**Cause:** No city pages configured.

**Solution:** Add city pages:
```python
config.city_pages.append(CityPageConfig(
    city_name="Your City",
    state="Your State"
))
```

**Fallback:** Or use legacy target_cities:
```python
config.target_cities = ["City1", "City2"]
```

### Issue: Schema type is Organization instead of LocalBusiness

**Cause:** Address is marked as private.

**Solution:** If you want LocalBusiness schema, enable address:
```python
config.contact.address.publish_on_website = True
```

Or use GBP:
```python
config.google_business_profile.expose_address = True
```

---

## Best Practices

1. **Always include product images** - Required for Product rich results
2. **Add city pages** - Enhances local SEO with areaServed property
3. **Configure social media** - Builds brand authority with sameAs
4. **Use Google Business Profile** - Adds credibility signals
5. **Validate with Google** - Always test schema before deployment
6. **Keep addresses consistent** - Match GBP and website addresses exactly
7. **Include contact information** - Phone and email enhance schema value

---

## Related Documentation

- [Product Roadmap](PRODUCT_ROADMAP.md) - Schema enhancements roadmap item
- [Configuration Models](../src/core/config/models.py) - Complete config reference
- [HTML Generator](../src/core/generators/html_generator.py) - Schema implementation

---

## Support

For questions or issues with schema generation:
1. Check this documentation
2. Review test examples in `test_schema_output.py`
3. Validate with Google Rich Results Test
4. Check GitHub issues for similar problems

---

**Document Version:** 1.0.0
**Feature Branch:** feature/schema-enhancements
**Validated:** Google Rich Results Test - 100% Success
