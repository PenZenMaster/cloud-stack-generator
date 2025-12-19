# AWG Blog Publishing System - Technical Specification

**Version**: 1.0.0
**Last Updated**: 2025-12-18
**Status**: Design Phase

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [File & Directory Structure](#3-file--directory-structure)
4. [Database & Storage Schema](#4-database--storage-schema)
5. [Template Specifications](#5-template-specifications)
6. [CLI Command Specification](#6-cli-command-specification)
7. [Configuration Format](#7-configuration-format)
8. [Component Specifications](#8-component-specifications)
9. [Integration Points](#9-integration-points)
10. [Implementation Phases](#10-implementation-phases)
11. [Security & Performance](#11-security--performance)
12. [Testing Strategy](#12-testing-strategy)

---

## 1. Executive Summary

### 1.1 Purpose

The AWG Blog Publishing System is a "lights-out" automated pipeline for publishing blog content to backlink sites deployed on AWS S3/CloudFront. It enables users to create content in ChatGPT and automatically publish it with intelligent backlinking, SEO optimization, and multi-site distribution.

### 1.2 Key Features

- **Multi-Source Content Input**: ChatGPT output, Markdown files, CSV bulk import, REST API
- **Metadata-Driven Publishing**: YAML frontmatter controls all publishing behavior
- **Smart Auto-Backlinking**: Configurable keyword-to-URL mapping with density controls
- **SEO Optimization**: Meta tags, Schema.org Article markup, Open Graph tags
- **Scheduling System**: Queue posts with publish_date, only publish when date is reached
- **Multi-Site Distribution**: Single blog post can deploy to multiple backlink sites
- **Automated Sitemap Updates**: Automatically regenerate sitemap.xml on publish
- **S3 Integration**: Leverages existing S3WebsiteDeployer for deployment
- **Windows Task Scheduler**: CLI designed for scheduled automation
- **Email Notifications**: Success/failure reports via SMTP

### 1.3 Technology Stack

- **Language**: Python 3.9+
- **Template Engine**: Jinja2
- **Storage**: SQLite (blog metadata), File system (content)
- **Deployment**: AWS S3/CloudFront (existing S3WebsiteDeployer)
- **CLI Framework**: argparse + custom command router
- **Email**: smtplib + email.mime
- **Scheduling**: Windows Task Scheduler (external) + internal publish_date checks

---

## 2. System Architecture

### 2.1 Architecture Diagram

```
+------------------+
|  Content Sources |
+------------------+
| - ChatGPT Output |
| - Markdown Files |
| - CSV Bulk       |
| - REST API       |
+--------+---------+
         |
         v
+------------------+
| Content Ingester |
+------------------+
| - Parse YAML     |
| - Validate       |
| - Store Metadata |
+--------+---------+
         |
         v
+------------------+
|  Blog Scheduler  |
+------------------+
| - Check Dates    |
| - Queue Posts    |
| - Trigger Publish|
+--------+---------+
         |
         v
+------------------+
| Content Processor|
+------------------+
| - Backlink Engine|
| - SEO Optimizer  |
| - Template Render|
+--------+---------+
         |
         v
+------------------+
|  Site Generator  |
+------------------+
| - Index Pages    |
| - Detail Pages   |
| - RSS Feed       |
| - Sitemap Update |
+--------+---------+
         |
         v
+------------------+
|   S3 Deployer    |
+------------------+
| - Upload Files   |
| - CloudFront Inv.|
+--------+---------+
         |
         v
+------------------+
| Notification Svc |
+------------------+
| - Email Reports  |
| - Status Logging |
+------------------+
```

### 2.2 Component Overview

| Component | Responsibility | Key Technologies |
|-----------|----------------|------------------|
| **Content Ingester** | Parse and validate incoming content | YAML parser, Markdown parser |
| **Blog Scheduler** | Manage publish dates and queue | SQLite, datetime |
| **Backlink Engine** | Insert contextual backlinks | Regex, keyword mapping |
| **SEO Optimizer** | Generate meta tags, schema markup | Jinja2, Schema.org JSON-LD |
| **Template Renderer** | Render blog pages from templates | Jinja2 |
| **Site Generator** | Generate index, RSS, sitemap | Jinja2, xml.etree |
| **S3 Deployer** | Deploy to AWS S3/CloudFront | boto3 (existing) |
| **Notification Service** | Send email reports | smtplib |

### 2.3 Data Flow

1. **Ingestion**: Content arrives via CLI, API, or file system
2. **Validation**: YAML frontmatter validated, content checked
3. **Storage**: Metadata stored in SQLite, content in `/content/blog/posts/`
4. **Scheduling**: Publish date checked against current date
5. **Processing**: Backlinks inserted, SEO tags generated
6. **Rendering**: Templates rendered with processed content
7. **Generation**: Index/RSS/sitemap regenerated
8. **Deployment**: Files synced to S3, CloudFront invalidated
9. **Notification**: Email sent with success/failure report

---

## 3. File & Directory Structure

### 3.1 Project Directory Layout

```
cloud-stack-generator/
├── src/
│   ├── core/
│   │   ├── blog/                      # NEW: Blog system core
│   │   │   ├── __init__.py
│   │   │   ├── content_ingester.py    # Parse and validate content
│   │   │   ├── blog_scheduler.py      # Publish date management
│   │   │   ├── backlink_engine.py     # Auto-backlinking logic
│   │   │   ├── seo_optimizer.py       # Meta tags, schema, OG tags
│   │   │   ├── blog_generator.py      # Page/feed/sitemap generation
│   │   │   ├── blog_deployer.py       # Wrapper for S3WebsiteDeployer
│   │   │   ├── notification_service.py # Email notifications
│   │   │   └── models.py              # BlogPost, BacklinkRule, etc.
│   │   ├── deployment/
│   │   │   └── s3_deployer.py         # EXISTING: S3 deployment
│   │   └── utils/
│   │       └── logger.py              # EXISTING: Logging
│   ├── templates/
│   │   ├── blog/                      # NEW: Blog templates
│   │   │   ├── listing.html           # Blog index/category pages
│   │   │   ├── detail.html            # Individual blog post
│   │   │   ├── rss.xml                # RSS feed template
│   │   │   └── components/
│   │   │       ├── post_card.html     # Post preview card
│   │   │       ├── sidebar.html       # Sidebar widget
│   │   │       └── pagination.html    # Pagination controls
│   │   └── pages/                     # EXISTING: Page templates
│   └── cli/
│       ├── __init__.py
│       └── blog_commands.py           # NEW: Blog CLI commands
├── data/
│   └── blog.db                        # NEW: SQLite database
├── content/
│   └── blog/
│       ├── posts/                     # NEW: Blog post markdown files
│       │   ├── 2025-01-15-example-post.md
│       │   └── ...
│       ├── config/
│       │   ├── backlink_rules.yaml    # NEW: Keyword-to-URL mappings
│       │   └── blog_config.yaml       # NEW: Global blog settings
│       └── drafts/                    # NEW: Unpublished drafts
├── output/
│   └── clients/
│       └── {client_slug}/
│           └── blog/                  # NEW: Generated blog files
│               ├── index.html
│               ├── post/
│               │   └── {slug}.html
│               ├── category/
│               │   └── {category}.html
│               ├── rss.xml
│               └── sitemap.xml (updated)
└── tests/
    └── blog/                          # NEW: Blog system tests
        ├── test_ingester.py
        ├── test_scheduler.py
        ├── test_backlink_engine.py
        └── ...
```

### 3.2 Content Organization

**Markdown File Naming Convention**:
```
{YYYY-MM-DD}-{slug}.md
```

Example: `2025-01-15-structural-engineering-trends.md`

**Directory Structure**:
- `/content/blog/posts/`: Published posts (with publish_date <= today)
- `/content/blog/drafts/`: Draft posts (with publish_date > today or status: draft)

---

## 4. Database & Storage Schema

### 4.1 SQLite Schema

**File**: `data/blog.db`

#### Table: `blog_posts`

```sql
CREATE TABLE blog_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    publish_date DATE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'draft',  -- draft, scheduled, published
    author TEXT,
    category TEXT,
    tags TEXT,  -- JSON array
    target_sites TEXT,  -- JSON array of site slugs
    backlink_density TEXT DEFAULT 'medium',  -- light, medium, aggressive
    meta_description TEXT,
    featured_image TEXT,
    keywords TEXT,  -- JSON array
    last_deployed DATETIME,
    deployment_status TEXT  -- pending, success, failed
);

CREATE INDEX idx_publish_date ON blog_posts(publish_date);
CREATE INDEX idx_status ON blog_posts(status);
CREATE INDEX idx_slug ON blog_posts(slug);
```

#### Table: `backlink_rules`

```sql
CREATE TABLE backlink_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    target_url TEXT NOT NULL,
    anchor_text TEXT,  -- Optional custom anchor
    priority INTEGER DEFAULT 50,  -- Higher = more important
    max_per_post INTEGER DEFAULT 2,  -- Limit backlinks per post
    site_slug TEXT,  -- NULL = applies to all sites
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_keyword ON backlink_rules(keyword);
CREATE INDEX idx_site_slug ON backlink_rules(site_slug);
```

#### Table: `deployment_log`

```sql
CREATE TABLE deployment_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id INTEGER NOT NULL,
    site_slug TEXT NOT NULL,
    deployed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT NOT NULL,  -- success, failed
    s3_url TEXT,
    cloudfront_url TEXT,
    error_message TEXT,
    FOREIGN KEY (post_id) REFERENCES blog_posts(id)
);

CREATE INDEX idx_post_deployment ON deployment_log(post_id);
CREATE INDEX idx_site_deployment ON deployment_log(site_slug);
```

### 4.2 File System Storage

**Markdown File Format**:

```markdown
---
title: "Ultimate Guide to Structural Engineering in Virginia"
slug: "structural-engineering-virginia-guide"
publish_date: 2025-01-15
author: "John Smith"
category: "Engineering"
tags: ["structural engineering", "Virginia", "construction"]
target_sites: ["structural-engineer", "commercial-structural-repair"]
backlink_density: "medium"
meta_description: "Comprehensive guide to structural engineering services in Virginia, including residential and commercial projects."
featured_image: "/assets/images/structural-engineering-virginia.jpg"
keywords: ["structural engineer", "structural repair", "beam analysis"]
---

# Main Content Here

Your blog post content in Markdown format...

## Section Headers

- Bullet points
- More content
```

**Backlink Rules YAML** (`content/blog/config/backlink_rules.yaml`):

```yaml
backlink_rules:
  - keyword: "structural engineer"
    target_url: "https://example.com/structural-engineering"
    anchor_text: "structural engineering services"  # Optional
    priority: 100
    max_per_post: 2
    site_slug: "structural-engineer"  # NULL = all sites
    active: true

  - keyword: "structural repair"
    target_url: "https://example.com/repair-services"
    priority: 90
    max_per_post: 1
    site_slug: null  # Applies to all sites

  - keyword: "beam analysis"
    target_url: "https://example.com/beam-analysis"
    priority: 70
    max_per_post: 1
```

**Blog Config YAML** (`content/blog/config/blog_config.yaml`):

```yaml
blog_settings:
  posts_per_page: 10
  enable_rss: true
  rss_items_limit: 20
  enable_categories: true
  enable_tags: true
  enable_author_pages: false
  date_format: "%B %d, %Y"
  excerpt_length: 160  # characters

seo:
  default_meta_description: "Read the latest articles from {business_name}"
  default_og_image: "/assets/images/default-blog-og.jpg"
  schema_type: "BlogPosting"  # Schema.org type

backlink_settings:
  densities:
    light:
      max_backlinks: 2
      min_content_length: 500
    medium:
      max_backlinks: 4
      min_content_length: 800
    aggressive:
      max_backlinks: 8
      min_content_length: 1200

  smart_placement: true  # Avoid first/last paragraphs
  avoid_headings: true   # Don't insert in headings
  nofollow: false        # Use nofollow for backlinks

email:
  smtp_host: "smtp.gmail.com"
  smtp_port: 587
  smtp_user: "your-email@gmail.com"
  smtp_password_env: "BLOG_SMTP_PASSWORD"
  from_address: "noreply@example.com"
  notification_recipients:
    - "admin@example.com"
    - "marketing@example.com"
```

---

## 5. Template Specifications

### 5.1 Blog Listing Template (`src/templates/blog/listing.html`)

**Purpose**: Display blog post index, category pages, tag pages

**Context Variables**:
```python
{
    "posts": List[BlogPost],      # Paginated list of posts
    "page_title": str,             # "Blog" or "Category: Engineering"
    "category": str,               # Optional category filter
    "tag": str,                    # Optional tag filter
    "pagination": {
        "current_page": int,
        "total_pages": int,
        "has_previous": bool,
        "has_next": bool,
        "previous_url": str,
        "next_url": str
    },
    "config": ClientConfig,        # Site configuration
    "meta": {
        "title": str,
        "description": str,
        "canonical_url": str
    }
}
```

**Key Features**:
- Responsive grid layout (3 columns desktop, 2 tablet, 1 mobile)
- Post cards with image, title, excerpt, date, category
- Category/tag filtering
- Pagination controls
- Schema.org Blog/ItemList markup

### 5.2 Blog Detail Template (`src/templates/blog/detail.html`)

**Purpose**: Display individual blog post

**Context Variables**:
```python
{
    "post": BlogPost,              # Full post object
    "content_html": str,           # Rendered markdown with backlinks
    "related_posts": List[BlogPost], # 3-5 related posts
    "config": ClientConfig,
    "meta": {
        "title": str,
        "description": str,
        "canonical_url": str,
        "og_image": str,
        "article_published_time": str,
        "article_modified_time": str,
        "keywords": List[str]
    },
    "schema": dict                 # Schema.org BlogPosting JSON-LD
}
```

**Key Features**:
- Full-width content area with sidebar
- Author info, publish date, category, tags
- Social sharing buttons
- Related posts section
- Breadcrumb navigation
- Schema.org BlogPosting + BreadcrumbList markup
- Open Graph tags

### 5.3 RSS Feed Template (`src/templates/blog/rss.xml`)

**Purpose**: Generate RSS 2.0 feed

**Context Variables**:
```python
{
    "posts": List[BlogPost],       # Latest 20 posts
    "site_title": str,
    "site_url": str,
    "site_description": str,
    "build_date": str,             # RFC 822 format
    "language": str                # "en-us"
}
```

**Key Features**:
- RSS 2.0 compliant
- Full content or excerpt (configurable)
- Proper GUID generation
- Media enclosures for featured images

### 5.4 Component Templates

#### `src/templates/blog/components/post_card.html`

**Purpose**: Reusable post preview card

**Context Variables**:
```python
{
    "post": BlogPost,
    "show_excerpt": bool,
    "show_image": bool,
    "show_category": bool
}
```

#### `src/templates/blog/components/sidebar.html`

**Purpose**: Blog sidebar with widgets

**Context Variables**:
```python
{
    "recent_posts": List[BlogPost],
    "categories": List[Category],
    "tags": List[Tag],
    "config": ClientConfig
}
```

#### `src/templates/blog/components/pagination.html`

**Purpose**: Pagination controls

**Context Variables**:
```python
{
    "current_page": int,
    "total_pages": int,
    "base_url": str,
    "show_first_last": bool
}
```

---

## 6. CLI Command Specification

### 6.1 Command Structure

All commands follow the pattern:
```bash
python -m src.cli.blog_commands <command> [options]
```

### 6.2 Command Reference

#### `add` - Add New Blog Post

**Purpose**: Ingest new blog post from various sources

**Syntax**:
```bash
# From ChatGPT output (markdown with frontmatter)
awg-blog add --source chatgpt --file "content.md"

# From markdown file
awg-blog add --source markdown --file "post.md"

# From CSV row (bulk import)
awg-blog add --source csv --file "posts.csv" --row 5

# From API payload
awg-blog add --source api --payload '{"title": "...", "content": "..."}'
```

**Options**:
```
--source {chatgpt|markdown|csv|api}  # Input source type
--file PATH                          # Path to content file
--row INTEGER                        # CSV row number (for CSV source)
--payload JSON                       # JSON payload (for API source)
--draft                              # Save as draft (ignore publish_date)
--validate-only                      # Validate without saving
```

**Output**:
```
[INFO] Parsing content from chatgpt source
[INFO] Validating YAML frontmatter
[PASS] Title: "Structural Engineering Trends 2025"
[PASS] Slug: "structural-engineering-trends-2025"
[PASS] Publish Date: 2025-01-15
[PASS] Target Sites: structural-engineer, commercial-structural-repair
[INFO] Storing metadata in blog.db
[INFO] Saving content to content/blog/posts/2025-01-15-structural-engineering-trends-2025.md
[SUCCESS] Blog post added successfully (ID: 42)
[INFO] Status: scheduled (publishes on 2025-01-15)
```

#### `publish` - Publish Scheduled Posts

**Purpose**: Check publish dates and publish ready posts

**Syntax**:
```bash
# Publish all posts with publish_date <= today
awg-blog publish

# Publish specific post by slug
awg-blog publish --slug "structural-engineering-trends-2025"

# Publish to specific sites only
awg-blog publish --sites "structural-engineer,commercial-structural-repair"

# Dry-run (preview without deploying)
awg-blog publish --dry-run
```

**Options**:
```
--slug TEXT                          # Publish specific post
--sites TEXT                         # Comma-separated site slugs
--dry-run                            # Preview without deploying
--force                              # Ignore publish_date check
--skip-deploy                        # Generate files but don't deploy
--skip-email                         # Skip email notification
```

**Output**:
```
[INFO] Checking for posts ready to publish...
[INFO] Found 3 posts with publish_date <= 2025-01-15

Processing post 1/3: "Structural Engineering Trends 2025"
[INFO] Applying backlink rules (density: medium)
[INFO] Inserted 4 backlinks (keywords: structural engineer, beam analysis, structural repair)
[INFO] Generating SEO meta tags
[INFO] Rendering detail page (detail.html)
[INFO] Updating blog index (listing.html)
[INFO] Regenerating RSS feed (rss.xml)
[INFO] Updating sitemap.xml
[INFO] Deploying to site: structural-engineer
[INFO] S3 sync: 15 files uploaded to s3://sanitation-rentals/structural-engineer/blog/
[INFO] CloudFront invalidation: /structural-engineer/blog/*
[SUCCESS] Post published: https://d2kqaxeqy8leud.cloudfront.net/structural-engineer/blog/post/structural-engineering-trends-2025.html

[INFO] Deploying to site: commercial-structural-repair
[INFO] S3 sync: 15 files uploaded to s3://sanitation-rentals/commercial-structural-repair/blog/
[SUCCESS] Post published: https://dfoay4cvr1g82.cloudfront.net/commercial-structural-repair/blog/post/structural-engineering-trends-2025.html

[INFO] Sending email notification to admin@example.com, marketing@example.com
[SUCCESS] 3 posts published successfully
```

#### `list` - List Blog Posts

**Purpose**: View all blog posts and their status

**Syntax**:
```bash
# List all posts
awg-blog list

# Filter by status
awg-blog list --status published

# Filter by category
awg-blog list --category "Engineering"

# Search by keyword
awg-blog list --search "structural"
```

**Options**:
```
--status {draft|scheduled|published}  # Filter by status
--category TEXT                       # Filter by category
--tag TEXT                            # Filter by tag
--search TEXT                         # Search in title/content
--limit INTEGER                       # Limit results (default: 50)
--format {table|json|csv}             # Output format
```

**Output**:
```
+----+---------------------------+---------------+------------+-----------+
| ID | Title                     | Slug          | Publish    | Status    |
+----+---------------------------+---------------+------------+-----------+
| 42 | Structural Engineering... | structural... | 2025-01-15 | published |
| 41 | Beam Analysis Guide       | beam-analy... | 2025-01-10 | published |
| 40 | Foundation Repair Tips    | foundatio... | 2025-01-20 | scheduled |
+----+---------------------------+---------------+------------+-----------+
Total: 3 posts
```

#### `update` - Update Existing Post

**Purpose**: Modify blog post metadata or content

**Syntax**:
```bash
# Update metadata
awg-blog update --slug "structural-engineering-trends-2025" \
                --set title="New Title" \
                --set publish_date="2025-01-20"

# Update content file
awg-blog update --slug "structural-engineering-trends-2025" \
                --content-file "updated-content.md"

# Re-publish updated post
awg-blog update --slug "structural-engineering-trends-2025" \
                --republish
```

**Options**:
```
--slug TEXT                          # Post slug (required)
--set KEY=VALUE                      # Update metadata field
--content-file PATH                  # Replace content
--republish                          # Re-deploy after update
```

#### `delete` - Delete Blog Post

**Purpose**: Remove blog post and unpublish from sites

**Syntax**:
```bash
# Delete post (soft delete - keeps in DB)
awg-blog delete --slug "structural-engineering-trends-2025"

# Permanently delete (remove from DB and filesystem)
awg-blog delete --slug "structural-engineering-trends-2025" --permanent

# Unpublish from sites but keep in DB
awg-blog delete --slug "structural-engineering-trends-2025" --unpublish-only
```

**Options**:
```
--slug TEXT                          # Post slug (required)
--permanent                          # Permanently delete
--unpublish-only                     # Remove from sites, keep in DB
--skip-confirmation                  # Skip confirmation prompt
```

#### `backlinks` - Manage Backlink Rules

**Purpose**: Add, update, or delete backlink rules

**Syntax**:
```bash
# Add new backlink rule
awg-blog backlinks add \
    --keyword "structural engineer" \
    --url "https://example.com/services" \
    --priority 100 \
    --max-per-post 2

# List all backlink rules
awg-blog backlinks list

# Update backlink rule
awg-blog backlinks update --id 5 --set priority=50

# Delete backlink rule
awg-blog backlinks delete --id 5

# Import from YAML
awg-blog backlinks import --file "content/blog/config/backlink_rules.yaml"

# Test backlink insertion (dry-run)
awg-blog backlinks test --slug "structural-engineering-trends-2025"
```

**Options**:
```
add:
  --keyword TEXT                     # Keyword to match
  --url TEXT                         # Target URL for backlink
  --anchor-text TEXT                 # Optional custom anchor
  --priority INTEGER                 # Priority (0-100)
  --max-per-post INTEGER             # Max backlinks per post
  --site-slug TEXT                   # Specific site (NULL = all)

list:
  --site-slug TEXT                   # Filter by site
  --active-only                      # Show only active rules
  --format {table|json|yaml}         # Output format

update:
  --id INTEGER                       # Rule ID (required)
  --set KEY=VALUE                    # Update field

delete:
  --id INTEGER                       # Rule ID (required)
  --skip-confirmation                # Skip confirmation

import:
  --file PATH                        # YAML file path
  --merge                            # Merge with existing (don't replace)

test:
  --slug TEXT                        # Post slug to test
  --density {light|medium|aggressive}  # Override density
```

#### `preview` - Preview Blog Post

**Purpose**: Generate local preview of blog post

**Syntax**:
```bash
# Preview specific post
awg-blog preview --slug "structural-engineering-trends-2025"

# Preview with specific density
awg-blog preview --slug "structural-engineering-trends-2025" \
                 --density aggressive

# Preview without backlinks
awg-blog preview --slug "structural-engineering-trends-2025" \
                 --no-backlinks
```

**Options**:
```
--slug TEXT                          # Post slug (required)
--density {light|medium|aggressive}  # Override backlink density
--no-backlinks                       # Disable backlinks
--open-browser                       # Open in default browser
```

#### `schedule` - Schedule Blog Posts

**Purpose**: Manage publish schedule

**Syntax**:
```bash
# Show upcoming scheduled posts
awg-blog schedule

# Show posts for specific date range
awg-blog schedule --from 2025-01-01 --to 2025-01-31

# Reschedule post
awg-blog schedule --slug "structural-engineering-trends-2025" \
                  --date 2025-02-01
```

**Options**:
```
--from DATE                          # Start date (YYYY-MM-DD)
--to DATE                            # End date (YYYY-MM-DD)
--slug TEXT                          # Reschedule specific post
--date DATE                          # New publish date
--format {table|calendar|json}       # Output format
```

#### `import` - Bulk Import Posts

**Purpose**: Import multiple posts from CSV

**Syntax**:
```bash
# Import from CSV
awg-blog import --csv "posts.csv"

# Import with custom column mapping
awg-blog import --csv "posts.csv" \
                --mapping "Title=post_title,Content=post_content"

# Dry-run import
awg-blog import --csv "posts.csv" --dry-run
```

**CSV Format**:
```csv
title,slug,publish_date,category,tags,content,target_sites,backlink_density
"Structural Engineering Trends 2025","structural-engineering-trends-2025","2025-01-15","Engineering","structural engineering,trends","# Content here...","structural-engineer,commercial-structural-repair","medium"
```

**Options**:
```
--csv PATH                           # CSV file path
--mapping TEXT                       # Custom column mapping
--dry-run                            # Validate without importing
--skip-errors                        # Continue on row errors
```

#### `deploy` - Deploy Blog to Sites

**Purpose**: Deploy generated blog files to S3

**Syntax**:
```bash
# Deploy to all configured sites
awg-blog deploy

# Deploy to specific sites
awg-blog deploy --sites "structural-engineer,commercial-structural-repair"

# Deploy specific files only
awg-blog deploy --files "index.html,rss.xml"

# Force re-deploy (skip cache)
awg-blog deploy --force
```

**Options**:
```
--sites TEXT                         # Comma-separated site slugs
--files TEXT                         # Specific files to deploy
--force                              # Force re-deploy
--invalidate-cloudfront              # Invalidate CloudFront cache
--dry-run                            # Preview without deploying
```

### 6.3 Windows Task Scheduler Integration

**Scheduled Task Example** (publish posts daily at 9 AM):

```batch
@echo off
REM Daily Blog Publishing Task
cd E:\projects\cloud-stack-generator
python -m src.cli.blog_commands publish --skip-email >> logs\blog_publish.log 2>&1
```

**Task Scheduler Configuration**:
- **Trigger**: Daily at 9:00 AM
- **Action**: Run batch script
- **Conditions**: Run only if network available
- **Settings**: Stop task if runs longer than 1 hour

---

## 7. Configuration Format

### 7.1 Blog Config YAML

**File**: `content/blog/config/blog_config.yaml`

See [Section 4.2](#42-file-system-storage) for full example.

### 7.2 Backlink Rules YAML

**File**: `content/blog/config/backlink_rules.yaml`

See [Section 4.2](#42-file-system-storage) for full example.

### 7.3 Site Configuration Integration

**Existing Cloud Config YAML** (updated):

```yaml
cloud:
  slug: "structural-engineer"
  site_type: "backlink_site"
  main_site_url: "https://example.com"
  deployment_url: "https://d2kqaxeqy8leud.cloudfront.net/structural-engineer"

  # NEW: Blog settings
  blog:
    enabled: true
    base_path: "/blog"  # Blog accessible at /blog/
    backlink_rules_file: "content/blog/config/backlink_rules.yaml"
    posts_per_page: 10
    enable_rss: true
```

### 7.4 Environment Variables

**.env File**:
```bash
# Email Configuration
BLOG_SMTP_HOST=smtp.gmail.com
BLOG_SMTP_PORT=587
BLOG_SMTP_USER=your-email@gmail.com
BLOG_SMTP_PASSWORD=your-app-password

# Notification Recipients
BLOG_NOTIFICATION_EMAILS=admin@example.com,marketing@example.com

# AWS Credentials (uses existing AWS profile)
AWS_PROFILE=AWS
AWS_REGION=us-east-1

# Blog Settings
BLOG_DB_PATH=data/blog.db
BLOG_CONTENT_DIR=content/blog
BLOG_OUTPUT_DIR=output/clients
```

---

## 8. Component Specifications

### 8.1 Content Ingester (`src/core/blog/content_ingester.py`)

**Purpose**: Parse and validate incoming blog content from multiple sources

**Key Classes**:

```python
class ContentSource(Enum):
    CHATGPT = "chatgpt"
    MARKDOWN = "markdown"
    CSV = "csv"
    API = "api"

class ContentIngester:
    """
    Parses and validates blog content from various sources.

    Methods:
        - ingest_from_file(source: ContentSource, file_path: Path) -> BlogPost
        - ingest_from_payload(payload: dict) -> BlogPost
        - validate_frontmatter(frontmatter: dict) -> List[ValidationError]
        - parse_markdown(content: str) -> Tuple[dict, str]
        - store_post(post: BlogPost) -> int
    """

    def __init__(self, db_path: Path, content_dir: Path):
        self.db = BlogDatabase(db_path)
        self.content_dir = content_dir

    def ingest_from_file(self, source: ContentSource, file_path: Path) -> BlogPost:
        """
        Parse content file and create BlogPost object.

        Args:
            source: Type of content source
            file_path: Path to content file

        Returns:
            BlogPost object with validated metadata

        Raises:
            ValidationError: If frontmatter or content invalid
        """
        # Implementation
        pass

    def validate_frontmatter(self, frontmatter: dict) -> List[ValidationError]:
        """
        Validate YAML frontmatter against schema.

        Required fields:
            - title (str, non-empty)
            - slug (str, URL-safe)
            - publish_date (date, YYYY-MM-DD)
            - target_sites (list of str, non-empty)

        Optional fields:
            - author (str)
            - category (str)
            - tags (list of str)
            - backlink_density (enum: light, medium, aggressive)
            - meta_description (str, max 160 chars)
            - featured_image (str, valid URL or path)
            - keywords (list of str)
        """
        # Implementation
        pass
```

**Integration Points**:
- `BlogDatabase`: Store metadata in SQLite
- `MarkdownParser`: Parse markdown to HTML
- `FileSystem`: Save content to `/content/blog/posts/`

### 8.2 Blog Scheduler (`src/core/blog/blog_scheduler.py`)

**Purpose**: Manage publish dates and determine which posts are ready to publish

**Key Classes**:

```python
class BlogScheduler:
    """
    Manages blog post scheduling and publish date checks.

    Methods:
        - get_publishable_posts(as_of_date: date = None) -> List[BlogPost]
        - schedule_post(post_id: int, publish_date: date) -> bool
        - get_upcoming_schedule(days: int = 30) -> Dict[date, List[BlogPost]]
        - reschedule_post(post_id: int, new_date: date) -> bool
    """

    def __init__(self, db: BlogDatabase):
        self.db = db

    def get_publishable_posts(self, as_of_date: date = None) -> List[BlogPost]:
        """
        Get all posts with publish_date <= as_of_date and status != 'published'.

        Args:
            as_of_date: Check date (defaults to today)

        Returns:
            List of BlogPost objects ready to publish
        """
        if as_of_date is None:
            as_of_date = date.today()

        return self.db.query_posts(
            filters={
                "publish_date__lte": as_of_date,
                "status__ne": "published"
            }
        )

    def get_upcoming_schedule(self, days: int = 30) -> Dict[date, List[BlogPost]]:
        """
        Get publishing schedule for next N days.

        Returns:
            Dict mapping dates to list of posts scheduled for that date
        """
        # Implementation
        pass
```

### 8.3 Backlink Engine (`src/core/blog/backlink_engine.py`)

**Purpose**: Insert contextual backlinks into blog content based on keyword rules

**Key Classes**:

```python
class BacklinkDensity(Enum):
    LIGHT = "light"       # Max 2 backlinks, min 500 words
    MEDIUM = "medium"     # Max 4 backlinks, min 800 words
    AGGRESSIVE = "aggressive"  # Max 8 backlinks, min 1200 words

class BacklinkEngine:
    """
    Intelligently insert backlinks into blog content.

    Methods:
        - apply_backlinks(content: str, density: BacklinkDensity, site_slug: str) -> str
        - find_keyword_matches(content: str, rules: List[BacklinkRule]) -> List[Match]
        - insert_backlink(content: str, match: Match, rule: BacklinkRule) -> str
        - validate_insertion_point(content: str, position: int) -> bool
    """

    def __init__(self, db: BlogDatabase, config: dict):
        self.db = db
        self.config = config

    def apply_backlinks(
        self,
        content: str,
        density: BacklinkDensity,
        site_slug: str
    ) -> str:
        """
        Apply backlinks to content based on rules and density.

        Algorithm:
            1. Load backlink rules for site (or global rules)
            2. Sort rules by priority (descending)
            3. Find keyword matches in content
            4. Filter matches based on density constraints:
               - Avoid first/last paragraphs (if smart_placement enabled)
               - Avoid headings (if avoid_headings enabled)
               - Respect max_per_post limits
            5. Insert backlinks at valid positions
            6. Return modified content

        Args:
            content: Markdown or HTML content
            density: Backlink density level
            site_slug: Target site slug

        Returns:
            Content with backlinks inserted
        """
        # Implementation
        pass

    def find_keyword_matches(
        self,
        content: str,
        rules: List[BacklinkRule]
    ) -> List[Match]:
        """
        Find all keyword matches in content.

        Returns list of matches with:
            - keyword: Matched keyword
            - position: Start position in content
            - rule: Matching BacklinkRule
            - context: Surrounding text (for validation)
        """
        # Implementation
        pass

    def validate_insertion_point(self, content: str, position: int) -> bool:
        """
        Check if position is valid for backlink insertion.

        Validation rules:
            - Not in first/last paragraph (if smart_placement)
            - Not in heading tags (<h1>-<h6>)
            - Not already a link (<a> tag)
            - Not in code blocks
        """
        # Implementation
        pass
```

**Backlink Insertion Example**:

**Input Content**:
```markdown
# Structural Engineering in Virginia

When hiring a structural engineer, it's important to choose...

Our team specializes in beam analysis and structural repair...
```

**Backlink Rules Applied**:
- `structural engineer` → `https://example.com/services` (priority 100)
- `beam analysis` → `https://example.com/beam-analysis` (priority 70)

**Output Content**:
```html
<h1>Structural Engineering in Virginia</h1>

<p>When hiring a <a href="https://example.com/services">structural engineer</a>, it's important to choose...</p>

<p>Our team specializes in <a href="https://example.com/beam-analysis">beam analysis</a> and structural repair...</p>
```

### 8.4 SEO Optimizer (`src/core/blog/seo_optimizer.py`)

**Purpose**: Generate SEO meta tags, Schema.org markup, and Open Graph tags

**Key Classes**:

```python
class SEOOptimizer:
    """
    Generate SEO-optimized meta tags and structured data.

    Methods:
        - generate_meta_tags(post: BlogPost, config: ClientConfig) -> dict
        - generate_schema_markup(post: BlogPost, config: ClientConfig) -> dict
        - generate_og_tags(post: BlogPost, config: ClientConfig) -> dict
    """

    def __init__(self, config: dict):
        self.config = config

    def generate_meta_tags(
        self,
        post: BlogPost,
        config: ClientConfig
    ) -> dict:
        """
        Generate HTML meta tags for blog post.

        Returns:
            {
                "title": "Page Title | Site Name",
                "description": "Meta description (max 160 chars)",
                "keywords": "keyword1, keyword2, keyword3",
                "canonical": "https://example.com/blog/post/slug",
                "robots": "index, follow"
            }
        """
        # Implementation
        pass

    def generate_schema_markup(
        self,
        post: BlogPost,
        config: ClientConfig
    ) -> dict:
        """
        Generate Schema.org BlogPosting JSON-LD.

        Returns:
            {
                "@context": "https://schema.org",
                "@type": "BlogPosting",
                "headline": "Blog Post Title",
                "description": "Meta description",
                "image": "https://example.com/featured-image.jpg",
                "datePublished": "2025-01-15T09:00:00Z",
                "dateModified": "2025-01-15T09:00:00Z",
                "author": {
                    "@type": "Person",
                    "name": "John Smith"
                },
                "publisher": {
                    "@type": "Organization",
                    "name": "Business Name",
                    "logo": {
                        "@type": "ImageObject",
                        "url": "https://example.com/logo.png"
                    }
                },
                "mainEntityOfPage": {
                    "@type": "WebPage",
                    "@id": "https://example.com/blog/post/slug"
                }
            }
        """
        # Implementation
        pass

    def generate_og_tags(
        self,
        post: BlogPost,
        config: ClientConfig
    ) -> dict:
        """
        Generate Open Graph meta tags.

        Returns:
            {
                "og:type": "article",
                "og:title": "Blog Post Title",
                "og:description": "Meta description",
                "og:url": "https://example.com/blog/post/slug",
                "og:image": "https://example.com/featured-image.jpg",
                "og:site_name": "Site Name",
                "article:published_time": "2025-01-15T09:00:00Z",
                "article:modified_time": "2025-01-15T09:00:00Z",
                "article:author": "John Smith",
                "article:section": "Engineering",
                "article:tag": ["tag1", "tag2"]
            }
        """
        # Implementation
        pass
```

### 8.5 Blog Generator (`src/core/blog/blog_generator.py`)

**Purpose**: Generate blog HTML pages, RSS feed, and update sitemap

**Key Classes**:

```python
class BlogGenerator:
    """
    Generate blog pages, feeds, and sitemaps.

    Methods:
        - generate_post_page(post: BlogPost, site_slug: str) -> Path
        - generate_index_page(site_slug: str, page: int = 1) -> Path
        - generate_category_page(category: str, site_slug: str) -> Path
        - generate_rss_feed(site_slug: str) -> Path
        - update_sitemap(site_slug: str, new_urls: List[str]) -> Path
    """

    def __init__(
        self,
        template_dir: Path,
        output_dir: Path,
        backlink_engine: BacklinkEngine,
        seo_optimizer: SEOOptimizer
    ):
        self.template_env = Environment(loader=FileSystemLoader(template_dir))
        self.output_dir = output_dir
        self.backlink_engine = backlink_engine
        self.seo_optimizer = seo_optimizer

    def generate_post_page(
        self,
        post: BlogPost,
        site_slug: str,
        config: ClientConfig
    ) -> Path:
        """
        Generate individual blog post detail page.

        Process:
            1. Load post content from markdown file
            2. Apply backlinks using BacklinkEngine
            3. Convert markdown to HTML
            4. Generate SEO meta tags and schema markup
            5. Render detail.html template
            6. Save to output/{site_slug}/blog/post/{slug}.html

        Returns:
            Path to generated HTML file
        """
        # Load and process content
        raw_content = self._load_post_content(post.file_path)
        content_with_backlinks = self.backlink_engine.apply_backlinks(
            raw_content,
            post.backlink_density,
            site_slug
        )
        content_html = markdown.markdown(content_with_backlinks)

        # Generate SEO data
        meta_tags = self.seo_optimizer.generate_meta_tags(post, config)
        schema_markup = self.seo_optimizer.generate_schema_markup(post, config)
        og_tags = self.seo_optimizer.generate_og_tags(post, config)

        # Render template
        template = self.template_env.get_template("blog/detail.html")
        html = template.render(
            post=post,
            content_html=content_html,
            meta=meta_tags,
            schema=schema_markup,
            og_tags=og_tags,
            config=config
        )

        # Save file
        output_path = self.output_dir / site_slug / "blog" / "post" / f"{post.slug}.html"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")

        return output_path

    def generate_index_page(
        self,
        site_slug: str,
        config: ClientConfig,
        page: int = 1
    ) -> Path:
        """
        Generate blog index page with pagination.

        Process:
            1. Query published posts for site
            2. Paginate results (posts_per_page from config)
            3. Render listing.html template
            4. Save to output/{site_slug}/blog/index.html (page 1)
               or output/{site_slug}/blog/page/{page}.html (page 2+)
        """
        # Implementation
        pass

    def update_sitemap(
        self,
        site_slug: str,
        new_urls: List[str]
    ) -> Path:
        """
        Update sitemap.xml with new blog URLs.

        Process:
            1. Load existing sitemap.xml
            2. Parse XML
            3. Add new <url> entries for blog posts
            4. Sort by lastmod date
            5. Save updated sitemap.xml
        """
        # Implementation
        pass
```

### 8.6 Blog Deployer (`src/core/blog/blog_deployer.py`)

**Purpose**: Wrapper for S3WebsiteDeployer with blog-specific logic

**Key Classes**:

```python
class BlogDeployer:
    """
    Deploy blog files to S3/CloudFront using existing S3WebsiteDeployer.

    Methods:
        - deploy_post(post: BlogPost, sites: List[str]) -> Dict[str, DeploymentResult]
        - deploy_full_blog(site_slug: str) -> DeploymentResult
        - invalidate_cloudfront(site_slug: str, paths: List[str]) -> bool
    """

    def __init__(self, s3_deployer: S3WebsiteDeployer, config: dict):
        self.s3_deployer = s3_deployer
        self.config = config

    def deploy_post(
        self,
        post: BlogPost,
        sites: List[str]
    ) -> Dict[str, DeploymentResult]:
        """
        Deploy single blog post to multiple sites.

        Process:
            1. For each target site:
               a. Generate post page
               b. Regenerate index page
               c. Update RSS feed
               d. Update sitemap.xml
               e. Deploy files to S3 using S3WebsiteDeployer
               f. Invalidate CloudFront cache
            2. Log deployment results
            3. Update deployment_log table

        Returns:
            Dict mapping site_slug -> DeploymentResult
        """
        results = {}

        for site_slug in sites:
            try:
                # Generate files
                generator = BlogGenerator(...)
                post_path = generator.generate_post_page(post, site_slug)
                generator.generate_index_page(site_slug)
                generator.generate_rss_feed(site_slug)
                generator.update_sitemap(site_slug, [post.get_url(site_slug)])

                # Deploy to S3
                blog_dir = self.output_dir / site_slug / "blog"
                result = self.s3_deployer.deploy_website(
                    bucket_name=self.config["bucket_name"],
                    local_path=blog_dir,
                    subdirectory=f"{site_slug}/blog"
                )

                # Invalidate CloudFront
                if result["success"]:
                    self.invalidate_cloudfront(
                        site_slug,
                        paths=[f"/blog/post/{post.slug}.html", "/blog/index.html"]
                    )

                results[site_slug] = result

            except Exception as e:
                logger.error(f"Deployment failed for {site_slug}: {e}")
                results[site_slug] = {"success": False, "errors": [str(e)]}

        return results
```

### 8.7 Notification Service (`src/core/blog/notification_service.py`)

**Purpose**: Send email notifications for publish success/failure

**Key Classes**:

```python
class NotificationService:
    """
    Send email notifications for blog publishing events.

    Methods:
        - send_publish_success(results: List[DeploymentResult]) -> bool
        - send_publish_failure(errors: List[str]) -> bool
        - send_schedule_reminder(posts: List[BlogPost]) -> bool
    """

    def __init__(self, smtp_config: dict):
        self.smtp_config = smtp_config

    def send_publish_success(
        self,
        results: List[DeploymentResult]
    ) -> bool:
        """
        Send success notification email.

        Email template:
            Subject: [AWG Blog] 3 Posts Published Successfully

            Blog Publishing Report - 2025-01-15

            Successfully published 3 posts:

            1. "Structural Engineering Trends 2025"
               - Sites: structural-engineer, commercial-structural-repair
               - URLs:
                 * https://d2kqaxeqy8leud.cloudfront.net/structural-engineer/blog/post/structural-engineering-trends-2025.html
                 * https://dfoay4cvr1g82.cloudfront.net/commercial-structural-repair/blog/post/structural-engineering-trends-2025.html

            2. "Beam Analysis Guide"
               ...

            Total files deployed: 42
            Total S3 upload size: 1.2 MB
            CloudFront invalidations: 6 paths
        """
        # Implementation
        pass

    def send_publish_failure(self, errors: List[str]) -> bool:
        """
        Send failure notification email.

        Email template:
            Subject: [AWG Blog] Publishing Failed

            Blog Publishing Error - 2025-01-15

            Publishing failed with the following errors:

            1. Failed to upload to S3: Access Denied
            2. CloudFront invalidation failed: Invalid distribution

            Please review logs and retry manually.
        """
        # Implementation
        pass
```

### 8.8 Blog Models (`src/core/blog/models.py`)

**Purpose**: Data models for blog system

**Key Classes**:

```python
from dataclasses import dataclass
from datetime import date, datetime
from typing import List, Optional
from enum import Enum

class PostStatus(Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"

class BacklinkDensity(Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    AGGRESSIVE = "aggressive"

@dataclass
class BlogPost:
    """Blog post data model"""
    id: Optional[int]
    slug: str
    title: str
    file_path: str
    publish_date: date
    created_at: datetime
    updated_at: datetime
    status: PostStatus
    author: Optional[str]
    category: Optional[str]
    tags: List[str]
    target_sites: List[str]
    backlink_density: BacklinkDensity
    meta_description: Optional[str]
    featured_image: Optional[str]
    keywords: List[str]
    last_deployed: Optional[datetime]
    deployment_status: Optional[str]

    def get_url(self, site_slug: str, base_url: str) -> str:
        """Generate full URL for post on specific site"""
        return f"{base_url}/{site_slug}/blog/post/{self.slug}.html"

    def is_publishable(self, as_of_date: date = None) -> bool:
        """Check if post is ready to publish"""
        if as_of_date is None:
            as_of_date = date.today()
        return (
            self.status != PostStatus.PUBLISHED and
            self.publish_date <= as_of_date
        )

@dataclass
class BacklinkRule:
    """Backlink rule data model"""
    id: Optional[int]
    keyword: str
    target_url: str
    anchor_text: Optional[str]
    priority: int
    max_per_post: int
    site_slug: Optional[str]
    active: bool
    created_at: datetime

    def matches_site(self, site_slug: str) -> bool:
        """Check if rule applies to site"""
        return self.site_slug is None or self.site_slug == site_slug

@dataclass
class DeploymentResult:
    """Deployment result data model"""
    success: bool
    site_slug: str
    s3_url: Optional[str]
    cloudfront_url: Optional[str]
    files_uploaded: int
    upload_size_bytes: int
    errors: List[str]
    deployed_at: datetime
```

---

## 9. Integration Points

### 9.1 Integration with Existing AWG Generators

#### 9.1.1 Generator Manager Integration

**File**: `src/core/generators/generator_manager.py`

**Integration**:
- Add `BlogGenerator` to generator pipeline
- Trigger blog generation after main site generation
- Include blog status in generation reports

**Code Changes**:
```python
class GeneratorManager:
    def __init__(self):
        # Existing generators
        self.page_generator = PageGenerator()

        # NEW: Blog generator
        self.blog_generator = BlogGenerator(...)

    def generate_website(self, config: ClientConfig) -> GenerationResult:
        # Existing site generation
        result = self.page_generator.generate_complete_website(config)

        # NEW: Generate blog if enabled
        if config.cloud.blog.enabled:
            blog_result = self.blog_generator.generate_full_blog(
                config.cloud.slug
            )
            result.merge(blog_result)

        return result
```

#### 9.1.2 S3 Deployer Integration

**File**: `src/core/deployment/s3_deployer.py`

**Integration**:
- BlogDeployer wraps existing S3WebsiteDeployer
- Reuse upload_directory() method
- Add blog-specific cache control headers

**Code Changes**:
```python
class S3WebsiteDeployer:
    def upload_directory(self, local_path: Path, bucket_name: str, prefix: str = "") -> bool:
        # Existing implementation
        # ...

        # NEW: Blog-specific cache control
        if "blog" in str(relative_path):
            extra_args["CacheControl"] = "public, max-age=3600"  # 1 hour for blog

        # Continue existing upload
        # ...
```

#### 9.1.3 Sitemap Generator Integration

**Integration**:
- BlogGenerator calls existing sitemap update logic
- Append blog URLs to main sitemap.xml
- Maintain proper XML structure

**Code Changes**:
```python
class BlogGenerator:
    def update_sitemap(self, site_slug: str, new_urls: List[str]) -> Path:
        # Load existing sitemap
        sitemap_path = self.output_dir / site_slug / "sitemap.xml"

        if sitemap_path.exists():
            # Parse existing sitemap
            tree = ET.parse(sitemap_path)
            root = tree.getroot()
        else:
            # Create new sitemap (use existing template)
            from src.core.generators.sitemap_generator import create_sitemap
            root = create_sitemap(site_slug)

        # Add blog URLs
        for url in new_urls:
            url_element = ET.SubElement(root, "url")
            ET.SubElement(url_element, "loc").text = url
            ET.SubElement(url_element, "lastmod").text = date.today().isoformat()
            ET.SubElement(url_element, "changefreq").text = "weekly"
            ET.SubElement(url_element, "priority").text = "0.7"

        # Save updated sitemap
        tree = ET.ElementTree(root)
        tree.write(sitemap_path, encoding="utf-8", xml_declaration=True)

        return sitemap_path
```

### 9.2 Integration with Cloud Config

**Existing Config Structure**:
```yaml
cloud:
  slug: "structural-engineer"
  site_type: "backlink_site"
  main_site_url: "https://example.com"
  deployment_url: "https://d2kqaxeqy8leud.cloudfront.net/structural-engineer"
```

**NEW: Blog Config Section**:
```yaml
cloud:
  # Existing fields
  slug: "structural-engineer"
  site_type: "backlink_site"

  # NEW: Blog configuration
  blog:
    enabled: true
    base_path: "/blog"
    backlink_rules_file: "content/blog/config/backlink_rules.yaml"
    posts_per_page: 10
    enable_rss: true
    rss_items_limit: 20
    enable_categories: true
    enable_tags: true
```

### 9.3 Integration with Template System

**Existing Templates**:
- `src/templates/pages/`: Main site pages
- `src/templates/components/`: Reusable components

**NEW: Blog Templates**:
- `src/templates/blog/listing.html`: Extends `src/templates/base/layout.html`
- `src/templates/blog/detail.html`: Extends `src/templates/base/layout.html`
- Reuse existing navigation/footer components

**Shared Components**:
- Navigation bar: Add "Blog" link
- Footer: Add RSS feed link
- Schema.org Organization markup: Include blog posts

### 9.4 CLI Integration

**Existing CLI**:
- No existing CLI structure (UI-driven application)

**NEW: Blog CLI**:
- Create new module `src/cli/blog_commands.py`
- Use `argparse` for command routing
- Standalone entry point for Windows Task Scheduler

**Entry Point** (`src/cli/blog_commands.py`):
```python
def main():
    parser = argparse.ArgumentParser(description="AWG Blog Publishing System")
    subparsers = parser.add_subparsers(dest="command")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add new blog post")
    add_parser.add_argument("--source", required=True, choices=["chatgpt", "markdown", "csv", "api"])
    add_parser.add_argument("--file", help="Content file path")
    # ... more arguments

    # Publish command
    publish_parser = subparsers.add_parser("publish", help="Publish scheduled posts")
    publish_parser.add_argument("--slug", help="Specific post slug")
    # ... more arguments

    args = parser.parse_args()

    # Route to command handler
    if args.command == "add":
        handle_add(args)
    elif args.command == "publish":
        handle_publish(args)
    # ... more commands

if __name__ == "__main__":
    main()
```

---

## 10. Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal**: Core data models, database, and content ingestion

**Deliverables**:
1. Database schema (`blog_posts`, `backlink_rules`, `deployment_log`)
2. Data models (`BlogPost`, `BacklinkRule`, `DeploymentResult`)
3. Content ingester (markdown + YAML frontmatter parsing)
4. Basic validation (frontmatter schema)
5. File system storage (`/content/blog/posts/`)

**Tasks**:
- [ ] Create SQLite database schema
- [ ] Implement `BlogPost`, `BacklinkRule` dataclasses
- [ ] Build `ContentIngester` class
- [ ] Write YAML frontmatter parser
- [ ] Implement validation logic
- [ ] Add unit tests (90% coverage)

**Success Criteria**:
- Can ingest markdown file with frontmatter
- Metadata stored in SQLite
- Content saved to filesystem
- Validation catches missing/invalid fields

### Phase 2: Backlink Engine & SEO (Week 3-4)

**Goal**: Smart backlinking and SEO optimization

**Deliverables**:
1. Backlink engine (keyword matching, insertion)
2. Density controls (light/medium/aggressive)
3. Smart placement logic (avoid headings/first paragraph)
4. SEO optimizer (meta tags, schema, OG tags)
5. Backlink rules YAML import

**Tasks**:
- [ ] Build `BacklinkEngine` class
- [ ] Implement keyword matching (regex)
- [ ] Add insertion point validation
- [ ] Implement density constraints
- [ ] Build `SEOOptimizer` class
- [ ] Generate Schema.org JSON-LD
- [ ] Generate Open Graph tags
- [ ] Add unit tests (90% coverage)

**Success Criteria**:
- Backlinks inserted correctly at valid positions
- Density constraints respected
- SEO tags generated with correct values
- Schema.org markup validates

### Phase 3: Templates & Generation (Week 5-6)

**Goal**: Blog page templates and site generation

**Deliverables**:
1. Jinja2 templates (listing, detail, RSS)
2. Component templates (post_card, sidebar, pagination)
3. Blog generator (render pages, feeds, sitemap)
4. Integration with existing page templates
5. Responsive design (mobile-friendly)

**Tasks**:
- [ ] Create `listing.html` template
- [ ] Create `detail.html` template
- [ ] Create `rss.xml` template
- [ ] Build `BlogGenerator` class
- [ ] Implement pagination logic
- [ ] Add sitemap update logic
- [ ] Integrate with existing layout templates
- [ ] Add template tests

**Success Criteria**:
- Blog pages render correctly
- Pagination works for large post counts
- RSS feed validates (W3C Feed Validator)
- Sitemap includes blog URLs
- Mobile-responsive design

### Phase 4: Deployment & Automation (Week 7-8)

**Goal**: S3 deployment, scheduling, notifications, CLI

**Deliverables**:
1. Blog deployer (S3 integration)
2. Scheduler (publish date checks)
3. Notification service (email reports)
4. CLI commands (add, publish, list, etc.)
5. Windows Task Scheduler integration
6. Configuration files (blog_config.yaml, backlink_rules.yaml)

**Tasks**:
- [ ] Build `BlogDeployer` class
- [ ] Integrate with `S3WebsiteDeployer`
- [ ] Add CloudFront invalidation
- [ ] Build `BlogScheduler` class
- [ ] Implement publish date logic
- [ ] Build `NotificationService` class
- [ ] Add SMTP email support
- [ ] Build CLI (`blog_commands.py`)
- [ ] Add all CLI commands (add, publish, list, etc.)
- [ ] Create config files
- [ ] Write Windows batch scripts
- [ ] Add integration tests

**Success Criteria**:
- Posts deploy to S3 successfully
- CloudFront cache invalidates
- Scheduler publishes posts on correct date
- Email notifications sent
- CLI commands work correctly
- Windows Task Scheduler can run CLI

---

## 11. Security & Performance

### 11.1 Security Considerations

#### 11.1.1 Input Validation

**Threats**:
- SQL injection (SQLite queries)
- XSS (user-generated content)
- Path traversal (file uploads)

**Mitigations**:
- Use parameterized queries (no string concatenation)
- Escape HTML in templates (Jinja2 auto-escaping)
- Validate file paths (no `../` traversal)
- Whitelist allowed HTML tags in markdown
- Sanitize YAML frontmatter

**Code Example**:
```python
# SAFE: Parameterized query
cursor.execute(
    "SELECT * FROM blog_posts WHERE slug = ?",
    (slug,)
)

# UNSAFE: String concatenation
cursor.execute(f"SELECT * FROM blog_posts WHERE slug = '{slug}'")  # DON'T DO THIS
```

#### 11.1.2 Secrets Management

**Sensitive Data**:
- SMTP password
- AWS credentials

**Best Practices**:
- Store in environment variables (`.env`)
- Use AWS IAM roles (not hardcoded keys)
- Encrypt SMTP password in config
- Never commit secrets to git

**.env Example**:
```bash
BLOG_SMTP_PASSWORD=your-app-password
AWS_PROFILE=AWS  # Use existing profile, no hardcoded keys
```

#### 11.1.3 Access Control

**File Permissions**:
- Blog database: Read/write by application only
- Config files: Read-only by application
- Output directory: Public read, application write

**S3 Bucket Policy**:
- Public read for blog files
- Application write via IAM role
- No public write access

### 11.2 Performance Optimization

#### 11.2.1 Database Indexing

**Indexes**:
```sql
CREATE INDEX idx_publish_date ON blog_posts(publish_date);
CREATE INDEX idx_status ON blog_posts(status);
CREATE INDEX idx_slug ON blog_posts(slug);
CREATE INDEX idx_keyword ON backlink_rules(keyword);
```

**Query Optimization**:
- Use indexes for frequent queries
- Limit result sets (pagination)
- Avoid SELECT * (specify columns)

#### 11.2.2 Caching

**Template Caching**:
- Cache compiled Jinja2 templates
- Use `Environment(loader=..., auto_reload=False)`

**Content Caching**:
- Cache rendered markdown (in-memory LRU cache)
- Cache backlink insertion results

**Code Example**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def render_markdown(content: str) -> str:
    """Cache rendered markdown"""
    return markdown.markdown(content)
```

#### 11.2.3 S3 Upload Optimization

**Multipart Uploads**:
- Use S3 multipart upload for large files (>5 MB)
- Parallel uploads for multiple files

**Cache Control Headers**:
```python
extra_args = {
    "CacheControl": "public, max-age=3600",  # 1 hour for blog
    "ContentType": "text/html"
}
```

**CloudFront Invalidation**:
- Batch invalidations (max 1000 paths)
- Use wildcards (`/blog/*`) for efficiency

#### 11.2.4 Backlink Engine Optimization

**Keyword Matching**:
- Compile regex patterns once (not per post)
- Use `re.compile()` with caching
- Limit backlinks per post (density constraints)

**Code Example**:
```python
class BacklinkEngine:
    def __init__(self):
        # Compile patterns once
        self.keyword_patterns = {
            rule.keyword: re.compile(r'\b' + re.escape(rule.keyword) + r'\b', re.IGNORECASE)
            for rule in self.rules
        }
```

---

## 12. Testing Strategy

### 12.1 Unit Tests

**Coverage Target**: 90%+

**Test Files**:
- `tests/blog/test_content_ingester.py`
- `tests/blog/test_backlink_engine.py`
- `tests/blog/test_seo_optimizer.py`
- `tests/blog/test_blog_generator.py`
- `tests/blog/test_blog_deployer.py`
- `tests/blog/test_notification_service.py`

**Key Test Cases**:

#### Content Ingester Tests
```python
def test_parse_valid_frontmatter():
    """Test parsing valid YAML frontmatter"""
    content = """---
title: "Test Post"
slug: "test-post"
publish_date: 2025-01-15
target_sites: ["site1", "site2"]
---
# Content
"""
    ingester = ContentIngester(...)
    post = ingester.parse_markdown(content)
    assert post.title == "Test Post"
    assert post.slug == "test-post"

def test_reject_missing_required_fields():
    """Test validation rejects missing required fields"""
    content = """---
title: "Test Post"
# Missing slug, publish_date
---
"""
    ingester = ContentIngester(...)
    with pytest.raises(ValidationError):
        ingester.parse_markdown(content)
```

#### Backlink Engine Tests
```python
def test_insert_backlink_medium_density():
    """Test backlink insertion with medium density"""
    content = "We provide structural engineer services."
    rules = [BacklinkRule(keyword="structural engineer", target_url="https://example.com")]

    engine = BacklinkEngine(...)
    result = engine.apply_backlinks(content, BacklinkDensity.MEDIUM, "site1")

    assert 'href="https://example.com"' in result
    assert result.count('<a ') == 1  # Only one backlink

def test_respect_max_per_post_limit():
    """Test max_per_post constraint"""
    content = "structural engineer " * 10  # 10 matches
    rules = [BacklinkRule(keyword="structural engineer", max_per_post=2)]

    engine = BacklinkEngine(...)
    result = engine.apply_backlinks(content, BacklinkDensity.AGGRESSIVE, "site1")

    assert result.count('<a ') == 2  # Only 2 backlinks (max_per_post)
```

### 12.2 Integration Tests

**Test Files**:
- `tests/blog/integration/test_full_publish_flow.py`
- `tests/blog/integration/test_s3_deployment.py`

**Key Test Cases**:

```python
def test_full_publish_flow():
    """Test complete publish workflow from ingestion to deployment"""
    # 1. Add post
    ingester = ContentIngester(...)
    post = ingester.ingest_from_file(ContentSource.MARKDOWN, "test-post.md")

    # 2. Check scheduler
    scheduler = BlogScheduler(...)
    publishable = scheduler.get_publishable_posts()
    assert post.id in [p.id for p in publishable]

    # 3. Generate pages
    generator = BlogGenerator(...)
    post_path = generator.generate_post_page(post, "site1", config)
    assert post_path.exists()

    # 4. Deploy to S3 (mock)
    deployer = BlogDeployer(s3_deployer_mock, config)
    result = deployer.deploy_post(post, ["site1"])
    assert result["site1"]["success"] == True
```

### 12.3 End-to-End Tests

**Scenario**: Publish blog post from ChatGPT to S3

**Steps**:
1. Create markdown file with frontmatter
2. Run `awg-blog add --source markdown --file test.md`
3. Verify post in database
4. Run `awg-blog publish --slug test-post --dry-run`
5. Verify generated files
6. Run `awg-blog publish --slug test-post` (with S3 mock)
7. Verify deployment success
8. Verify email notification sent

### 12.4 CLI Tests

**Test Files**:
- `tests/blog/test_cli.py`

**Key Test Cases**:
```python
def test_cli_add_command():
    """Test CLI add command"""
    result = subprocess.run(
        ["python", "-m", "src.cli.blog_commands", "add",
         "--source", "markdown", "--file", "test.md"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "SUCCESS" in result.stdout

def test_cli_publish_dry_run():
    """Test CLI publish --dry-run"""
    result = subprocess.run(
        ["python", "-m", "src.cli.blog_commands", "publish", "--dry-run"],
        capture_output=True, text=True
    )
    assert result.returncode == 0
    assert "DRY RUN" in result.stdout
```

---

## Appendix A: Example Workflows

### Workflow 1: Publish Single Post from ChatGPT

**User has ChatGPT output in markdown file** (`chatgpt-output.md`):

```markdown
---
title: "Top 10 Structural Engineering Trends in 2025"
slug: "structural-engineering-trends-2025"
publish_date: 2025-01-15
author: "John Smith"
category: "Engineering"
tags: ["structural engineering", "trends", "2025"]
target_sites: ["structural-engineer", "commercial-structural-repair"]
backlink_density: "medium"
meta_description: "Discover the top 10 structural engineering trends shaping the industry in 2025."
featured_image: "/assets/images/engineering-trends-2025.jpg"
keywords: ["structural engineer", "engineering trends", "2025 construction"]
---

# Top 10 Structural Engineering Trends in 2025

The structural engineering industry is evolving rapidly...

## 1. AI-Powered Structural Analysis

Artificial intelligence is transforming how structural engineers analyze...
```

**Steps**:

1. **Add post to system**:
```bash
cd E:\projects\cloud-stack-generator
python -m src.cli.blog_commands add --source chatgpt --file chatgpt-output.md
```

Output:
```
[INFO] Parsing content from chatgpt source
[INFO] Validating YAML frontmatter
[PASS] Title: "Top 10 Structural Engineering Trends in 2025"
[PASS] Slug: "structural-engineering-trends-2025"
[PASS] Publish Date: 2025-01-15
[PASS] Target Sites: structural-engineer, commercial-structural-repair
[INFO] Storing metadata in data/blog.db
[INFO] Saving content to content/blog/posts/2025-01-15-structural-engineering-trends-2025.md
[SUCCESS] Blog post added successfully (ID: 42)
[INFO] Status: scheduled (publishes on 2025-01-15)
```

2. **Preview post (optional)**:
```bash
python -m src.cli.blog_commands preview --slug "structural-engineering-trends-2025" --open-browser
```

3. **Publish on publish_date** (automated via Task Scheduler or manual):
```bash
python -m src.cli.blog_commands publish
```

Output:
```
[INFO] Checking for posts ready to publish...
[INFO] Found 1 post with publish_date <= 2025-01-15

Processing post 1/1: "Top 10 Structural Engineering Trends in 2025"
[INFO] Applying backlink rules (density: medium)
[INFO] Inserted 4 backlinks (keywords: structural engineer, engineering trends)
[INFO] Generating SEO meta tags
[INFO] Rendering detail page (detail.html)
[INFO] Updating blog index (listing.html)
[INFO] Regenerating RSS feed (rss.xml)
[INFO] Updating sitemap.xml
[INFO] Deploying to site: structural-engineer
[INFO] S3 sync: 15 files uploaded
[SUCCESS] Post published: https://d2kqaxeqy8leud.cloudfront.net/structural-engineer/blog/post/structural-engineering-trends-2025.html

[INFO] Deploying to site: commercial-structural-repair
[INFO] S3 sync: 15 files uploaded
[SUCCESS] Post published: https://dfoay4cvr1g82.cloudfront.net/commercial-structural-repair/blog/post/structural-engineering-trends-2025.html

[INFO] Sending email notification
[SUCCESS] 1 post published successfully
```

### Workflow 2: Bulk Import from CSV

**CSV file** (`bulk-posts.csv`):
```csv
title,slug,publish_date,category,tags,content,target_sites,backlink_density
"Beam Analysis 101","beam-analysis-101","2025-01-20","Engineering","beam analysis,structural engineering","# Beam Analysis 101\n\nContent here...","structural-engineer","medium"
"Foundation Repair Guide","foundation-repair-guide","2025-01-25","Repair","foundation,repair","# Foundation Repair Guide\n\nContent here...","commercial-structural-repair","light"
```

**Steps**:

1. **Import CSV**:
```bash
python -m src.cli.blog_commands import --csv bulk-posts.csv
```

Output:
```
[INFO] Importing from CSV: bulk-posts.csv
[INFO] Found 2 rows

Processing row 1/2: "Beam Analysis 101"
[PASS] Validation successful
[INFO] Storing post (ID: 43)

Processing row 2/2: "Foundation Repair Guide"
[PASS] Validation successful
[INFO] Storing post (ID: 44)

[SUCCESS] Imported 2 posts successfully
```

2. **View schedule**:
```bash
python -m src.cli.blog_commands schedule --from 2025-01-01 --to 2025-01-31
```

Output:
```
+------------+---------------------------+
| Date       | Posts                     |
+------------+---------------------------+
| 2025-01-15 | Top 10 Structural...      |
| 2025-01-20 | Beam Analysis 101         |
| 2025-01-25 | Foundation Repair Guide   |
+------------+---------------------------+
Total: 3 scheduled posts
```

### Workflow 3: Automated Daily Publishing

**Windows Task Scheduler Setup**:

1. **Create batch script** (`scripts/daily_blog_publish.bat`):
```batch
@echo off
REM Daily Blog Publishing Task
cd E:\projects\cloud-stack-generator

REM Publish posts (with email notifications)
python -m src.cli.blog_commands publish >> logs\blog_publish_%date:~10,4%%date:~4,2%%date:~7,2%.log 2>&1

REM Log completion
echo [%date% %time%] Daily publish task completed >> logs\blog_publish.log
```

2. **Create Task Scheduler task**:
   - **Name**: AWG Blog - Daily Publish
   - **Trigger**: Daily at 9:00 AM
   - **Action**: Run `scripts/daily_blog_publish.bat`
   - **Conditions**: Run only if network available
   - **Settings**: Stop task if runs longer than 1 hour

3. **Result**:
   - Every day at 9 AM, Task Scheduler runs the batch script
   - Script publishes all posts with `publish_date <= today`
   - Logs written to `logs/blog_publish_YYYYMMDD.log`
   - Email notifications sent to admins

---

## Appendix B: Configuration Examples

### B.1 Complete blog_config.yaml

```yaml
blog_settings:
  posts_per_page: 10
  enable_rss: true
  rss_items_limit: 20
  enable_categories: true
  enable_tags: true
  enable_author_pages: false
  date_format: "%B %d, %Y"
  excerpt_length: 160

seo:
  default_meta_description: "Read the latest articles from {business_name}"
  default_og_image: "/assets/images/default-blog-og.jpg"
  schema_type: "BlogPosting"

backlink_settings:
  densities:
    light:
      max_backlinks: 2
      min_content_length: 500
    medium:
      max_backlinks: 4
      min_content_length: 800
    aggressive:
      max_backlinks: 8
      min_content_length: 1200

  smart_placement: true
  avoid_headings: true
  nofollow: false

email:
  smtp_host: "smtp.gmail.com"
  smtp_port: 587
  smtp_user: "your-email@gmail.com"
  smtp_password_env: "BLOG_SMTP_PASSWORD"
  from_address: "noreply@example.com"
  notification_recipients:
    - "admin@example.com"
    - "marketing@example.com"

deployment:
  s3_bucket: "sanitation-rentals"
  aws_profile: "AWS"
  aws_region: "us-east-1"
  cloudfront_invalidation: true
```

### B.2 Complete backlink_rules.yaml

```yaml
backlink_rules:
  # High-priority main service keywords
  - keyword: "structural engineer"
    target_url: "https://example.com/structural-engineering"
    anchor_text: "professional structural engineering services"
    priority: 100
    max_per_post: 2
    site_slug: "structural-engineer"
    active: true

  - keyword: "structural engineering"
    target_url: "https://example.com/structural-engineering"
    priority: 95
    max_per_post: 2
    site_slug: "structural-engineer"
    active: true

  # Service-specific keywords
  - keyword: "beam analysis"
    target_url: "https://example.com/beam-analysis"
    priority: 90
    max_per_post: 1
    site_slug: "structural-engineer"
    active: true

  - keyword: "structural repair"
    target_url: "https://example.com/structural-repair"
    priority: 90
    max_per_post: 2
    site_slug: "commercial-structural-repair"
    active: true

  - keyword: "foundation repair"
    target_url: "https://example.com/foundation-repair"
    priority: 85
    max_per_post: 1
    site_slug: null  # Applies to all sites
    active: true

  # Location-based keywords
  - keyword: "structural engineer Virginia"
    target_url: "https://example.com/locations/virginia"
    priority: 80
    max_per_post: 1
    site_slug: null
    active: true

  # Lower-priority generic keywords
  - keyword: "engineering services"
    target_url: "https://example.com/services"
    priority: 50
    max_per_post: 1
    site_slug: null
    active: true
```

---

## Appendix C: Deployment Checklist

### Pre-Deployment Checklist

- [ ] SQLite database created (`data/blog.db`)
- [ ] Config files created:
  - [ ] `content/blog/config/blog_config.yaml`
  - [ ] `content/blog/config/backlink_rules.yaml`
- [ ] Environment variables set:
  - [ ] `BLOG_SMTP_PASSWORD`
  - [ ] `AWS_PROFILE`
- [ ] Directory structure created:
  - [ ] `content/blog/posts/`
  - [ ] `content/blog/drafts/`
  - [ ] `content/blog/config/`
  - [ ] `output/clients/{site_slug}/blog/`
- [ ] Templates created:
  - [ ] `src/templates/blog/listing.html`
  - [ ] `src/templates/blog/detail.html`
  - [ ] `src/templates/blog/rss.xml`
  - [ ] `src/templates/blog/components/*.html`
- [ ] S3 bucket exists with public read policy
- [ ] CloudFront distribution configured
- [ ] Email notifications tested (SMTP working)

### Post-Deployment Validation

- [ ] Test post ingestion:
  ```bash
  awg-blog add --source markdown --file test-post.md --validate-only
  ```
- [ ] Test backlink insertion:
  ```bash
  awg-blog backlinks test --slug test-post
  ```
- [ ] Test page generation:
  ```bash
  awg-blog preview --slug test-post --open-browser
  ```
- [ ] Test S3 deployment (dry-run):
  ```bash
  awg-blog deploy --dry-run
  ```
- [ ] Test email notifications:
  ```bash
  awg-blog publish --slug test-post --skip-deploy
  ```
- [ ] Verify RSS feed validates (https://validator.w3.org/feed/)
- [ ] Verify Schema.org markup (https://validator.schema.org/)
- [ ] Verify sitemap.xml includes blog URLs
- [ ] Verify CloudFront cache invalidation working
- [ ] Test Windows Task Scheduler integration

---

## Appendix D: Troubleshooting Guide

### Common Issues

#### Issue: "Blog post not publishing"

**Symptoms**: Post status remains "scheduled" after running `awg-blog publish`

**Possible Causes**:
1. `publish_date` is in the future
2. Post status is already "published"
3. Missing required frontmatter fields

**Solutions**:
```bash
# Check post details
awg-blog list --search "post-slug"

# Check publish date
awg-blog schedule

# Force publish (ignore date)
awg-blog publish --slug "post-slug" --force
```

#### Issue: "Backlinks not inserting"

**Symptoms**: Generated post has no backlinks

**Possible Causes**:
1. No matching backlink rules
2. Content too short for density level
3. Backlink rules inactive

**Solutions**:
```bash
# Test backlink insertion
awg-blog backlinks test --slug "post-slug"

# Check active backlink rules
awg-blog backlinks list --active-only

# Try different density
awg-blog preview --slug "post-slug" --density aggressive
```

#### Issue: "S3 deployment failed"

**Symptoms**: Error during `awg-blog deploy`

**Possible Causes**:
1. AWS credentials invalid/expired
2. S3 bucket doesn't exist
3. Network connectivity issues

**Solutions**:
```bash
# Verify AWS credentials
aws s3 ls --profile AWS

# Test S3 access
aws s3 ls s3://sanitation-rentals --profile AWS

# Try dry-run first
awg-blog deploy --dry-run
```

#### Issue: "Email notifications not sending"

**Symptoms**: No email received after publish

**Possible Causes**:
1. SMTP credentials invalid
2. Firewall blocking SMTP port
3. Email address incorrect

**Solutions**:
```bash
# Verify environment variables
echo %BLOG_SMTP_PASSWORD%

# Test SMTP connection
python -c "import smtplib; smtplib.SMTP('smtp.gmail.com', 587).connect()"

# Check email config
# Review content/blog/config/blog_config.yaml
```

---

## Appendix E: Future Enhancements

### Potential Enhancements (Post-MVP)

1. **AI-Generated Content**:
   - Integration with OpenAI API
   - Auto-generate blog posts from prompts
   - AI-powered keyword suggestions

2. **Advanced Analytics**:
   - Track backlink click-through rates
   - Blog post performance metrics
   - SEO ranking monitoring

3. **Social Media Integration**:
   - Auto-post to Twitter/LinkedIn on publish
   - Social sharing buttons with tracking
   - Open Graph image generation

4. **Content Optimization**:
   - Readability scoring (Flesch-Kincaid)
   - Keyword density analysis
   - Internal linking suggestions

5. **Multi-Author Support**:
   - Author profiles and bios
   - Author-specific RSS feeds
   - Contributor management UI

6. **Visual Editor**:
   - WYSIWYG blog post editor
   - Drag-and-drop image uploads
   - Real-time preview

7. **A/B Testing**:
   - Test multiple titles/descriptions
   - Track engagement metrics
   - Auto-select winning variant

8. **Internationalization**:
   - Multi-language blog support
   - Translation workflow
   - Language-specific backlink rules

---

## Document History

| Version | Date       | Author       | Changes                          |
|---------|------------|--------------|----------------------------------|
| 1.0.0   | 2025-12-18 | Claude Code  | Initial specification            |

---

**End of Specification**
