# Cloud Stack Generator - User Guide

**Version**: 3.6.0
**Last Updated**: December 21, 2025
**Audience**: End users, content managers, marketing teams

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Business Configuration](#2-business-configuration)
3. [Content Management](#3-content-management)
4. [Branding & Themes](#4-branding--themes)
5. [Template Selection & Customization](#5-template-selection--customization)
6. [City Pages & Location Targeting](#6-city-pages--location-targeting)
7. [SEO Optimization](#7-seo-optimization)
8. [Website Generation](#8-website-generation)
9. [Cloud Deployment](#9-cloud-deployment)
10. [Preview & Testing](#10-preview--testing)
11. [Troubleshooting](#11-troubleshooting)

---

## 1. Getting Started

### What is Cloud Stack Generator?

Cloud Stack Generator is a PyQt6-based application that generates SEO-optimized static websites for local businesses. It creates comprehensive websites with city-specific landing pages, product/service showcases, FAQ sections, and schema markup for search engine visibility.

### System Requirements

- **Operating System**: Windows 10/11, macOS, or Linux
- **Python**: 3.9 or higher
- **Memory**: 4GB RAM minimum
- **Disk Space**: 500MB for application + space for generated sites

### First-Time Setup

1. **Launch the Application**
   - Run `main.py` or use the provided executable
   - The main window displays tabs for configuration

2. **Create Your First Configuration**
   - **File → New Configuration** to start fresh
   - Or use **File → Open** to load an existing YAML config

3. **Understanding the UI Tabs**
   - **Business Info**: Company details, contact information
   - **Branding & Style**: Colors, fonts, logo, templates
   - **Products**: Product catalog management
   - **Services**: Service offerings
   - **FAQs**: Frequently asked questions
   - **City Pages**: Location-based landing pages
   - **Cloud Deploy**: AWS/GCS deployment settings

---

## 2. Business Configuration

### Business Information Tab

#### Company Details

Fill in your business information:

- **Business Name**: Your company's official name
- **Industry**: Type of business (e.g., "Portable Restroom Rentals")
- **Description**: Brief company description (2-3 sentences)
- **Website URL**: Your primary domain (e.g., `https://example.com`)
- **Business Hours**: Operating hours (e.g., "Monday-Friday 9AM-5PM EST")

#### Contact Information

- **Phone Number**: Primary contact number
- **Email Address**: Primary contact email
- **Street Address**: Physical business address
- **City, State, ZIP**: Location details
- **Country**: Business country

### Saving Configurations

1. **File → Save Configuration** (or **Ctrl+S**)
2. Choose a location in `config/clients/{client-name}/`
3. Configuration is saved as YAML file
4. Client assets are automatically organized

**Configuration File Structure**:
```
config/clients/{client-name}/
├── assets/                    # Client-specific images/files
├── {client}_config.yaml       # Main configuration
└── {variant}_config.yaml      # Additional variants (optional)
```

---

## 3. Content Management

### Products Management

#### Adding Products

1. Go to **Products Tab**
2. Click **"Add Product"**
3. Fill in product details:
   - **Name**: Product name
   - **Description**: Detailed description
   - **Price**: Price or price range
   - **Features**: Bullet-point features
   - **Categories**: Product categories/tags

#### Bulk Import Products (CSV)

1. Click **"Import CSV"** button
2. Select your CSV file with columns:
   ```
   name,description,price,features,categories
   ```
3. Products are imported and displayed in the table

#### Export Products

1. Click **"Export CSV"** to backup or edit products
2. Edit in Excel or Google Sheets
3. Re-import to update catalog

### Services Management

Similar workflow to Products:

1. **Services Tab** → **"Add Service"**
2. Enter service details:
   - **Name**: Service name
   - **Description**: What the service includes
   - **Pricing**: Pricing structure
   - **Features**: Service benefits

### FAQ Management

#### Adding FAQs Manually

1. **FAQs Tab** → **"Add FAQ"**
2. Fill in:
   - **Question**: FAQ question text
   - **Answer**: Comprehensive answer
   - **Category**: general, products, services, pricing, shipping, returns, technical, location
   - **Tags**: Keywords (e.g., "hours, contact, availability")
   - **Priority**: 0-10 (higher = more important)
   - **Active**: Show on website (checked) or hide (unchecked)

#### City-Specific FAQs

For location-specific questions:

1. Add FAQ as usual
2. Fill in **City Name** and **State** fields
3. FAQ appears only on that city's page

#### Bulk FAQ Import/Export

**CSV Format**:
```csv
question,answer,category,tags,priority,active,city_name,state
"What are your hours?","Monday-Friday 9AM-5PM",general,"hours,contact",10,true,,
"Do you serve Orlando?","Yes, we serve all of Orlando metro area",location,"location",8,true,Orlando,FL
```

**Import Steps**:
1. Click **"Import CSV"** or **"Import JSON"**
2. Select file
3. FAQs are added to existing list

**Export Steps**:
1. Check **"Active Only"** to export only visible FAQs
2. Click **"Export CSV"** or **"Export JSON"**
3. Save file for backup or editing

**JSON Format Example**:
```json
[
  {
    "question": "What payment methods do you accept?",
    "answer": "We accept Visa, Mastercard, Amex, and PayPal.",
    "category": "general",
    "tags": ["payment", "billing"],
    "priority": 8,
    "active": true,
    "city_name": null,
    "state": null
  }
]
```

---

## 4. Branding & Themes

### Logo & Branding Assets

#### Uploading Your Logo

1. **Branding & Style Tab** → **"Logo & Branding Assets"** section
2. Click **"Upload Logo"** button
3. Select image file (PNG, JPG, JPEG, SVG, GIF, BMP supported)
4. Logo path is displayed in the field

#### Uploading Hero Background Image

1. Same section → Click **"Upload Image"** (Hero Background)
2. Select hero image (PNG, JPG, JPEG, WebP, GIF, BMP)
3. Image path is displayed

#### How Asset Management Works

When you **save the configuration**:

1. Assets are **automatically copied** to `config/clients/{client-name}/assets/`
2. Paths in config are **converted to relative URLs**: `images/logo.png`
3. During **site generation**, assets are copied to `output/.../images/`
4. Website correctly references assets

**Directory Flow**:
```
Upload: C:\Users\...\my-logo.png
   ↓
Save Config: Copied to config/clients/{client-name}/assets/my-logo.png
   ↓
Config Stores: images/my-logo.png (relative path)
   ↓
Generate Site: Copied to output/clients/{client-name}/{site}/images/my-logo.png
```

#### Using URLs for Assets

Instead of uploading, you can enter **public CDN URLs**:
- Example: `https://cdn.example.com/logo.png`
- These are used directly (not copied to assets)
- Good for assets hosted elsewhere

### Color Customization

Set your brand colors:

- **Primary Color**: Main brand color (e.g., `#007BFF`)
- **Secondary Color**: Accent color (e.g., `#6C757D`)
- **Accent Color**: Highlight color for CTAs (e.g., `#28A745`)

Use hex color codes (`#RRGGBB`) or color names.

### Font Selection

Choose fonts for your website:
- **Font Family**: Font name (e.g., "Roboto", "Open Sans", "Arial")
- Stick to web-safe fonts or Google Fonts

---

## 5. Template Selection & Customization

### Choosing a Template

1. **Branding & Style Tab** → Click **"Choose Template..."**
2. **Template Selection Dialog** opens showing available templates

### Available Templates

#### SEO Authority City Page (Default)
- **ID**: `seo_authority_city`
- **Features**: Advanced SEO, schema markup, Wikipedia integration, Google Maps
- **Best For**: Maximum search engine visibility
- **Content**: Comprehensive with rich snippets

#### Enhanced Business City Page
- **ID**: `enhanced_business_city`
- **Features**: Professional layout, service showcase, contact sections
- **Best For**: Service-based businesses
- **Content**: Clean, modern design

#### Basic City Page
- **ID**: `basic_city`
- **Features**: Simple, essential features
- **Best For**: Straightforward local business sites
- **Content**: Minimal, fast-loading

#### Simple Landing Page
- **ID**: `simple_landing`
- **Type**: Landing page (non-city specific)
- **Features**: Conversion-focused, single-page
- **Best For**: Lead generation campaigns

### Previewing Templates

1. In Template Selection Dialog, select a template
2. Click **"Preview"** button
3. Preview HTML opens in your default browser
4. Compare multiple templates by previewing each

### Applying a Template

1. Select desired template in the dialog
2. Click **"Use Selected Template"**
3. Template is applied to your configuration
4. All generated pages will use this template

### Template Data Requirements

Each template specifies:
- **Required Data**: Must be filled in (e.g., business name, city name)
- **Optional Data**: Enhances the site if provided (e.g., hero image)

Missing required data will cause validation errors during generation.

---

## 6. City Pages & Location Targeting

### Creating City-Specific Landing Pages

City pages are location-targeted landing pages optimized for local SEO.

#### Adding Cities

1. **City Pages Tab** → **"Add City"**
2. Fill in city details:
   - **City Name**: Full city name (e.g., "Orlando")
   - **State**: 2-letter code (e.g., "FL")
   - **SEO Content**: Custom content for this city
   - **Service Area Notes**: Service coverage details

#### City Page Components

Each city page includes:

- **Hero Section**: City name + business service
- **About the City**: Wikipedia-sourced content (if enabled)
- **City Image**: Wikimedia Commons image with attribution
- **Service Area Information**: Coverage details
- **Places of Interest**: Google Maps embeds for local landmarks
- **City-Specific FAQs**: Location-targeted questions
- **Featured Products/Services**: Your offerings for this location

#### City Page SEO

- **URL Structure**: `/cities/{city-slug}.html` (e.g., `/cities/orlando.html`)
- **Title Tag**: `{Service} in {City}, {State} | {Business Name}`
- **Meta Description**: Customized for city + service
- **Primary Keyword**: `{Service} {City} {State}`
- **Schema Markup**: LocalBusiness, Service, FAQPage

---

## 7. SEO Optimization

### Canonical URLs

**What They Are**: Canonical URLs tell search engines which version of a page is the "official" one to index.

**Why They Matter**: Prevents duplicate content issues, especially when deploying to CloudFront.

#### Canonical URL Workflow

**First Deployment** (Test-File-First):

1. Click **"Deploy to Cloud"** in Cloud Deploy tab
2. System detects no website has been generated yet
3. User selects output folder
4. System deploys a **small test file** to S3/CloudFront
5. System retrieves the **CloudFront URL** (e.g., `https://d8na4b3nx1cti.cloudfront.net`)
6. System **updates config** with canonical URL automatically
7. User generates website (canonicals are correct from the start)
8. User deploys full website

**Result**: Only **one full deployment** needed; canonicals correct immediately.

**Subsequent Deployments**:

1. Click **"Deploy to Cloud"**
2. System shows regeneration confirmation
3. User regenerates website
4. User redeploys

### Structured Data (Schema Markup)

Schema markup is automatically included in generated pages:

- **WebPage**: All pages
- **LocalBusiness**: Business information
- **Product**: Product pages with properties
- **Service**: Service offerings
- **FAQPage**: FAQ sections with questions/answers
- **BreadcrumbList**: Navigation breadcrumbs

### Sitemap & Robots.txt

Generated automatically:

- **sitemap.xml**: Lists all pages for search engines
- **robots.txt**: Controls crawler access

### Rich Snippets

To maximize rich snippet eligibility:

1. Fill in **all product/service fields**
2. Add comprehensive **FAQ answers**
3. Provide **high-quality images**
4. Use **structured pricing** information

---

## 8. Website Generation

### Generating Your Website

1. **File → Generate Website** (or use Generate button in UI)
2. **Select output directory** (e.g., `output/clients/{client-name}/`)
3. Generation process runs:
   - Loads configuration
   - Validates required data
   - Renders templates with your content
   - Copies static assets (images, CSS, JS)
   - Generates city pages
   - Creates sitemap.xml and robots.txt
4. **Success notification** appears
5. Website is ready in the output directory

### Generated File Structure

```
output/clients/{client-name}/{site-variant}/
├── index.html                     # Homepage
├── products.html                  # Products overview
├── products/
│   ├── product-1.html            # Individual product pages
│   └── product-2.html
├── services.html                  # Services overview
├── services/
│   ├── service-1.html            # Individual service pages
│   └── service-2.html
├── faq.html                       # FAQ page
├── cities/
│   ├── orlando.html              # City landing pages
│   ├── miami.html
│   └── tampa.html
├── contact.html                   # Contact page
├── images/                        # All images
│   ├── logo.png
│   ├── hero-bg.jpg
│   └── product-*.jpg
├── sitemap.xml                    # XML sitemap
├── robots.txt                     # Robots instructions
└── schema.json                    # Structured data (optional)
```

### Updating an Existing Website

1. Make changes to your configuration (content, branding, etc.)
2. **Save configuration** (Ctrl+S)
3. **Regenerate website** (File → Generate Website)
4. Select **same output directory** (overwrites old files)
5. **Redeploy to cloud** if using cloud hosting

---

## 9. Cloud Deployment

### Deployment Options

- **AWS S3 + CloudFront** (Recommended): Private S3 bucket + CDN
- **AWS S3 (Public)**: Direct S3 website hosting
- **Google Cloud Storage**: GCS bucket hosting

### AWS S3 + CloudFront Deployment (Mode B)

**Prerequisites**:
- AWS account with credentials configured
- AWS CLI v2 installed
- Appropriate IAM permissions

**Deployment Steps**:

1. **Cloud Deploy Tab** → Configure:
   - **Bucket Name**: `client-website-{client-slug}-{account-id}`
   - **Region**: `us-east-1` (or your preferred region)
   - **CloudFront**: Enable CloudFront distribution
   - **OAC (Origin Access Control)**: Enable (keeps bucket private)

2. **First Deployment** (Canonical URL Workflow):
   - Click **"Deploy Website"**
   - Select output folder
   - System deploys test file first
   - CloudFront URL is retrieved and saved to config
   - Generate website (canonical URLs correct)
   - Deploy full website

3. **Deployment Process**:
   - S3 bucket is created (if needed)
   - CloudFront distribution is created (if needed)
   - Files are synced to S3
   - Bucket policy is applied (OAC permissions)
   - Deployment confirmation shown

**Website URL**: `https://{cloudfront-id}.cloudfront.net`

**Custom Domain** (Optional):
- Use Route 53 for DNS
- Create ACM certificate (in `us-east-1`)
- Configure CloudFront alternate domain names

### AWS S3 Public Deployment (Mode A)

**When to Use**: Simple websites without CDN, cost-sensitive projects

**Steps**:

1. **Cloud Deploy Tab** → Configure:
   - **Bucket Name**: `client-website-{slug}`
   - **Region**: Your region
   - **Public Access**: Enable public website hosting

2. **Deploy**:
   - Click **"Deploy Website"**
   - Bucket is created with public-read policy
   - Files are uploaded with caching headers
   - Website endpoint: `http://{bucket}.s3-website-{region}.amazonaws.com`

### Updating a Deployed Website

**For S3 Only**:
1. Regenerate website locally
2. Click **"Deploy Website"** again
3. Files are synced (only changed files uploaded)

**For CloudFront**:
1. Regenerate website
2. Deploy to S3
3. **Create CloudFront invalidation** for changed paths:
   - Invalidation path: `/*` (all files) or specific paths
   - Invalidations clear CDN cache

### Google Cloud Storage Deployment

Similar to S3:
1. Configure GCS bucket and credentials
2. Deploy website to GCS
3. Configure bucket for static website hosting
4. Use Cloud CDN for caching (optional)

---

## 10. Preview & Testing

### Local Preview

**Before Deployment**:

1. After generating website, navigate to output folder
2. Open `index.html` in a web browser
3. Navigate through pages to verify:
   - Content accuracy
   - Links work correctly
   - Images load properly
   - Branding is consistent

**Using a Local Server** (Recommended):

```bash
# Navigate to output directory
cd output/clients/{client-name}/{site}/

# Python HTTP server
python -m http.server 8000

# Access at: http://localhost:8000
```

### Testing Checklist

Before deploying to production:

- [ ] **Content Accuracy**
  - Business information correct
  - Products/services up to date
  - FAQs answered completely
  - Contact information accurate

- [ ] **Visual Check**
  - Logo displays correctly
  - Colors match branding
  - Images load and look good
  - Responsive on mobile (resize browser)

- [ ] **Functionality**
  - All internal links work
  - External links open correctly
  - Forms submit (if applicable)
  - Maps embed properly

- [ ] **SEO Validation**
  - Title tags unique per page
  - Meta descriptions present
  - H1 tags on all pages
  - Sitemap.xml accessible
  - Robots.txt correct

### Google Rich Results Testing

After deployment:

1. Go to [Google Rich Results Test](https://search.google.com/test/rich-results)
2. Enter your deployed page URL
3. Verify structured data is detected:
   - LocalBusiness
   - Product
   - FAQPage
   - BreadcrumbList

### Browser Compatibility

Test in multiple browsers:
- **Chrome** (most common)
- **Firefox**
- **Safari** (macOS/iOS)
- **Edge** (Windows)

Test on mobile devices:
- **iOS Safari**
- **Android Chrome**

---

## 11. Troubleshooting

### Common Issues & Solutions

#### Asset Not Appearing on Generated Site

**Problem**: Logo or images don't show up

**Checks**:
1. File exists in `config/clients/{client-name}/assets/`
2. File extension is supported (.png, .jpg, .svg, etc.)
3. Config has correct relative path (`images/filename.png`)
4. Regenerate the site to trigger asset copying

**Solution**:
- Re-upload asset via Branding tab
- Save configuration
- Regenerate website

#### Wrong Logo Showing

**Problem**: Old or incorrect logo displays

**Causes**:
- Client-specific asset overrides global asset (same filename)
- Browser cache showing old version

**Solution**:
1. Check `config/clients/{client-name}/assets/` for duplicate filenames
2. Clear browser cache (Ctrl+Shift+R / Cmd+Shift+R)
3. Rename new logo before uploading if needed

#### Website Generation Fails

**Problem**: Error during generation

**Common Errors**:
- **"Missing required field"**: Fill in business name, contact info
- **"Template not found"**: Re-select template in Branding tab
- **"Invalid YAML"**: Check config file syntax
- **"Permission denied"**: Check output directory write permissions

**Solution**:
1. Review error message in console/logs
2. Validate required fields are filled
3. Check file permissions on output directory
4. Ensure no files are locked/open in other programs

#### FAQ Import Issues

**Problem**: CSV/JSON import fails

**Checks**:
1. File encoding is UTF-8
2. CSV has header row with correct column names
3. Required fields (question, answer) are not empty
4. JSON is valid array format `[{...}, {...}]`

**Solution**:
- Open file in text editor and verify encoding
- Use template files as reference for format
- Fix any syntax errors in JSON
- Ensure CSV quotes multi-line content

#### CloudFront Deployment 403 Error

**Problem**: `AccessDenied` when accessing CloudFront URL

**Causes**:
- Bucket policy missing or incorrect
- OAC not configured properly
- Files not uploaded to S3

**Solution**:
1. Verify S3 bucket has files
2. Check bucket policy allows CloudFront OAC
3. Use AWS Console to verify CloudFront origin settings
4. Redeploy with correct OAC configuration

#### Changes Not Visible After Deployment

**Problem**: Updated content not showing on deployed site

**Causes**:
- Browser cache
- CloudFront cache (if using CDN)
- Forgot to regenerate website before deploying

**Solution**:
1. **Regenerate website** with updated config
2. **Redeploy** to S3/CloudFront
3. **Clear browser cache** (hard refresh)
4. **Create CloudFront invalidation** if using CDN:
   - Path: `/*` (invalidates all files)
   - Or specific paths like `/index.html`

#### Template Preview Fails

**Problem**: Preview button doesn't generate preview

**Causes**:
- Missing required data fields
- Template file missing
- Permission issues creating temp files

**Solution**:
1. Fill in basic business information before previewing
2. Verify template file exists in `src/templates/pages/`
3. Check write permissions in temp directory
4. Review error logs for specific issue

### Getting Help

**Documentation**:
- This User Guide
- [ADMIN_GUIDE.md](ADMIN_GUIDE.md) for technical setup
- [ARCHITECTURE.md](ARCHITECTURE.md) for development details

**Issue Tracking**:
- Use [GitHub Issues](../.github/ISSUE_TEMPLATE/) to report bugs
- Use **Bug Report** template for defects
- Use **Feature Request** template for enhancements

**Logs**:
- Check application console output for error messages
- Enable debug logging if available
- Provide logs when reporting issues

---

## Appendix A: Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| **Ctrl+S** / **Cmd+S** | Save Configuration |
| **Ctrl+O** / **Cmd+O** | Open Configuration |
| **Ctrl+N** / **Cmd+N** | New Configuration |
| **Ctrl+Shift+R** | Hard Refresh Browser (clear cache) |

---

## Appendix B: File Format Reference

### CSV Format for FAQs

```csv
question,answer,category,tags,priority,active,city_name,state
"Question text","Answer text","general","tag1,tag2",10,true,,
```

**Fields**:
- **question** (required): FAQ question
- **answer** (required): FAQ answer
- **category** (optional): general, products, services, pricing, shipping, returns, technical, location
- **tags** (optional): Comma-separated keywords
- **priority** (optional): 0-10 integer
- **active** (optional): true/false
- **city_name** (optional): City name for location-specific
- **state** (optional): State code (2 letters)

### JSON Format for FAQs

```json
[
  {
    "question": "Question text",
    "answer": "Answer text",
    "category": "general",
    "tags": ["tag1", "tag2"],
    "priority": 10,
    "active": true,
    "city_name": null,
    "state": null
  }
]
```

**Notes**:
- Must be an array `[...]`
- Tags are JSON array, not comma-separated string
- Boolean values: `true`/`false` (lowercase, no quotes)
- Use `null` for empty optional fields

---

## Appendix C: AWS Deployment Reference

### S3 Bucket Naming Convention

```
client-website-{pillar}-{account-id}
```

Example: `client-website-roof-vents-123456789012`

### CloudFront Distribution Settings

- **Origin**: S3 bucket with OAC
- **Viewer Protocol**: Redirect HTTP to HTTPS
- **Cache Policy**: CachingOptimized
- **Default Root Object**: `index.html`
- **Error Pages**: Custom 404.html

### AWS CLI Commands (Reference)

**Create Bucket** (us-east-1):
```bash
aws s3api create-bucket --bucket {bucket-name} --region us-east-1
```

**Sync Files** (HTML with short cache):
```bash
aws s3 sync . s3://{bucket}/ --exclude "*" --include "*.html" \
  --cache-control "max-age=300,public" --content-type "text/html"
```

**Create CloudFront Invalidation**:
```bash
aws cloudfront create-invalidation --distribution-id {dist-id} --paths "/*"
```

---

## Appendix D: Glossary

- **Canonical URL**: The preferred URL for a page to avoid duplicate content
- **CDN**: Content Delivery Network (e.g., CloudFront)
- **CloudFront**: AWS content delivery network service
- **FAQ**: Frequently Asked Questions
- **GCS**: Google Cloud Storage
- **OAC**: Origin Access Control (CloudFront security feature)
- **S3**: Amazon Simple Storage Service
- **Schema Markup**: Structured data for search engines (schema.org)
- **SEO**: Search Engine Optimization
- **Sitemap**: XML file listing all website pages
- **Static Site**: Website with pre-generated HTML (no server-side processing)
- **YAML**: Configuration file format used for storing settings

---

**End of User Guide**
For administrator and technical documentation, see [ADMIN_GUIDE.md](ADMIN_GUIDE.md) and [ARCHITECTURE.md](ARCHITECTURE.md).
