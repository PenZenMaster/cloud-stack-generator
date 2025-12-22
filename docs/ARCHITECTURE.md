# Cloud Stack Generator - Architecture Guide

**Version**: 3.6.0
**Last Updated**: December 21, 2025
**Audience**: Developers, architects, technical contributors

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Patterns](#2-architecture-patterns)
3. [Module Organization](#3-module-organization)
4. [Data Flow](#4-data-flow)
5. [Component Interactions](#5-component-interactions)
6. [Template System](#6-template-system)
7. [Deployment Pipeline](#7-deployment-pipeline)
8. [Testing Strategy](#8-testing-strategy)
9. [Development Workflow](#9-development-workflow)
10. [Extension Points](#10-extension-points)

---

## 1. System Overview

### Purpose

Cloud Stack Generator is a PyQt6-based desktop application that generates SEO-optimized static websites for local businesses. It creates comprehensive websites with city-specific landing pages, product/service showcases, and schema markup.

### Core Capabilities

- **Configuration Management**: YAML-based client configurations
- **Content Generation**: AI-powered and template-based content
- **Website Generation**: Static HTML/CSS websites
- **Cloud Deployment**: AWS S3/CloudFront and Google Cloud Storage
- **SEO Optimization**: Schema markup, sitemaps, canonical URLs

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **UI Framework** | PyQt6 6.10+ |
| **Template Engine** | Jinja2 3.1+ |
| **Configuration** | PyYAML 6.0+ |
| **Cloud - AWS** | Boto3 1.28+ |
| **Cloud - GCS** | Google Cloud Storage 2.10+ |
| **AI Content** | OpenAI API 1.0+ |
| **Testing** | Pytest 7.4+, pytest-qt |
| **Code Quality** | Ruff, Black, MyPy |

### System Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────────┐
│                      PyQt6 UI Layer                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ Business │ │ Products │ │ Services │ │  Cloud   │      │
│  │   Tab    │ │   Tab    │ │   Tab    │ │   Tab    │      │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Core Business Logic                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ Config       │ │ Website      │ │ Deployment   │       │
│  │ Management   │ │ Generator    │ │ Services     │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Infrastructure Layer                      │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐       │
│  │ Template     │ │ AI Content   │ │ Cloud        │       │
│  │ System       │ │ Service      │ │ Providers    │       │
│  └──────────────┘ └──────────────┘ └──────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Architecture Patterns

### Layered Architecture

**Presentation Layer** (UI):
- PyQt6 widgets and dialogs
- Tab-based content management
- User input validation
- Event handling and signals

**Business Logic Layer** (Core):
- Configuration management
- Content generation orchestration
- Template rendering
- Deployment coordination

**Data Access Layer**:
- YAML configuration parsing
- File system operations
- Cloud storage APIs
- Cache management

### Key Patterns Used

#### 1. **Model-View-Controller (MVC)**

```python
# Model: Configuration data structures
class ClientConfig:
    business_name: str
    services: List[Service]
    # ... data fields

# View: PyQt6 UI components
class BusinessTab(QWidget):
    def setup_ui(self):
        # Create widgets, layouts

# Controller: Main window coordination
class EnhancedMainWindow(QMainWindow):
    def on_generate_website(self):
        config = self.get_config_from_ui()
        generator.generate(config, output_dir)
```

#### 2. **Strategy Pattern** (Content Generation)

```python
class AIContentService:
    """Strategy for AI-powered content"""
    def generate_home_content(self, config):
        return openai.create(...)

class TemplateContentGenerator:
    """Strategy for template-based content"""
    def generate_home_content(self, config):
        return render_template(...)

# Context selects strategy
if ai_enabled and ai_service.is_available():
    content = ai_service.generate_home_content(config)
else:
    content = template_generator.generate_home_content(config)
```

#### 3. **Factory Pattern** (Cloud Providers)

```python
class ProviderFactory:
    @staticmethod
    def create_provider(provider_type: ProviderType, config: ProviderConfig):
        if provider_type == ProviderType.AWS_S3:
            return S3Provider(config)
        elif provider_type == ProviderType.GOOGLE_GCS:
            return GCSProvider(config)
        # ...

# Usage
provider = ProviderFactory.create_provider(ProviderType.AWS_S3, config)
provider.deploy(files)
```

#### 4. **Observer Pattern** (Signals/Slots)

```python
class CloudTab(QWidget):
    deployment_completed = pyqtSignal(str, bool)  # (url, success)

    def deploy(self):
        result = deployer.deploy_website(...)
        self.deployment_completed.emit(result.url, result.success)

# Main window observes
cloud_tab.deployment_completed.connect(self.on_deployment_done)
```

#### 5. **Facade Pattern** (Simplified APIs)

```python
class WebsiteGenerator:
    """Facade for complex generation workflow"""
    def __init__(self):
        self.html_generator = HTMLGenerator()
        self.css_generator = CSSGenerator()
        self.asset_manager = AssetManager()

    def generate(self, config, output_dir) -> GenerationResult:
        # Simplifies complex multi-step process
        self.create_directories()
        self.generate_pages(config)
        self.copy_assets()
        return GenerationResult(success=True)
```

---

## 3. Module Organization

### Directory Structure

```
cloud-stack-generator/
├── src/                          # Source code
│   ├── core/                     # Core business logic
│   │   ├── config/              # Configuration parsing
│   │   ├── generators/          # Content generators
│   │   ├── deployment/          # Cloud deployment
│   │   ├── services/            # AI, caching services
│   │   ├── security/            # Security utilities
│   │   └── utils/               # Common utilities
│   ├── ui/                       # User interface
│   │   ├── components/          # Tab components
│   │   ├── content_tabs/        # Content-specific tabs
│   │   ├── dialogs/             # Dialog windows
│   │   └── widgets/             # Custom widgets
│   ├── templates/               # Jinja2 templates
│   │   ├── base/                # Base templates
│   │   ├── pages/               # Page templates
│   │   └── components/          # Reusable components
│   └── integrations/            # External integrations
│       └── google_search_console.py
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── fixtures/                # Test data
├── config/                       # Configuration files
│   └── clients/                 # Client-specific configs
├── output/                       # Generated websites
├── docs/                         # Documentation
└── main.py                       # Application entry point
```

### Core Modules

#### src/core/config/

**Purpose**: Configuration management and parsing

| Module | Responsibility | Size |
|--------|---------------|------|
| `models.py` | Data classes for configuration | ~500 lines |
| `parser.py` | YAML parsing and validation | ~400 lines |
| `validator.py` | Configuration validation | ~300 lines |

**Key Classes**:
- `ClientConfig`: Main configuration model
- `Service`, `Product`, `CityPage`: Component models
- `DeploymentConfig`: Cloud deployment settings

#### src/core/generators/

**Purpose**: Content and website generation

| Module | Responsibility | Size |
|--------|---------------|------|
| `website_generator.py` | Main generation orchestration | ~400 lines |
| `html_generator.py` | HTML template rendering | ~600 lines |
| `css_generator.py` | CSS generation | ~400 lines |
| `city_page_generator.py` | City-specific pages | ~500 lines |
| `content/home_content_generator.py` | Home page content | ~400 lines |
| `content/city_content_generator.py` | City page content | ~400 lines |

**Refactoring Status**:
- ✅ Content generators extracted from monolithic `website_generator.py`
- ⏳ Planned: Orchestration layer separation (see ORCHESTRATION_REFACTOR_PLAN.md)

#### src/core/deployment/

**Purpose**: Cloud deployment abstraction

| Module | Responsibility | Size |
|--------|---------------|------|
| `s3_deployer.py` | AWS S3 deployment | ~800 lines |
| `s3_manager.py` | S3 operations | ~600 lines |
| `cloudfront_manager.py` | CloudFront management | ~400 lines |
| `providers/gcs_provider.py` | Google Cloud Storage | ~500 lines |
| `providers/provider_factory.py` | Multi-cloud abstraction | ~200 lines |

#### src/core/services/

**Purpose**: Supporting services

| Module | Responsibility | Size |
|--------|---------------|------|
| `ai_content_service.py` | OpenAI integration | ~300 lines |
| `content_cache.py` | AI content caching | ~200 lines |
| `api_key_manager.py` | Credential management | ~400 lines |

#### src/ui/components/

**Purpose**: UI tab components

| Module | Responsibility | Size | Refactor Status |
|--------|---------------|------|----------------|
| `enhanced_main_window.py` | Main application window | ~1,500 lines | ⚠️ Needs refactoring |
| `cloud_tab.py` | Cloud deployment UI | ~3,800 lines | ✅ Recently fixed |
| `business_tab.py` | Business info UI | ~600 lines | ✅ Good |
| `products_tab.py` | Products management | ~800 lines | ✅ Good |
| `services_tab.py` | Services management | ~700 lines | ✅ Good |

**Refactoring Planned** (see REFACTORING_PLAN.md):
- Extract managers from `enhanced_main_window.py`:
  - `menu_manager.py` (300-400 lines)
  - `tab_manager.py` (300-400 lines)
  - `status_manager.py` (200-300 lines)
  - `validation_coordinator.py` (200-300 lines)

---

## 4. Data Flow

### Configuration Loading Flow

```
User Opens File
    ↓
File Dialog → Select YAML
    ↓
ConfigParser.parse_yaml_file()
    ├─> Load YAML with PyYAML
    ├─> Extract client data
    ├─> Extract services, products
    ├─> Extract city pages
    └─> Build ClientConfig object
    ↓
EnhancedMainWindow.load_configuration_data()
    ├─> Set data on BusinessTab
    ├─> Set data on ProductsTab
    ├─> Set data on ServicesTab
    ├─> Set data on CloudTab
    └─> Store loaded_config reference
    ↓
UI Displays Configuration
```

### Website Generation Flow

```
User Clicks "Generate Website"
    ↓
EnhancedMainWindow.on_generate_website()
    ├─> Validate all tabs
    ├─> Get config from loaded_config (or UI if new)
    └─> Call WebsiteGenerator.generate(config, output_dir)
        ↓
WebsiteGenerator.generate()
    ├─> Create output directories
    ├─> Generate index.html
    │   ├─> HomeContentGenerator.generate()
    │   │   ├─> Check AI service available?
    │   │   ├─> Yes: AIContentService.generate_home_content()
    │   │   └─> No: Template-based generation
    │   └─> HTMLGenerator.render(home_content)
    ├─> Generate city pages (for each city)
    │   ├─> CityContentGenerator.generate()
    │   └─> HTMLGenerator.render(city_content)
    ├─> Generate CSS files
    │   └─> CSSGenerator.generate()
    ├─> Copy static assets
    │   └─> AssetManager.copy_assets()
    ├─> Generate sitemap.xml
    └─> Generate robots.txt
        ↓
Return GenerationResult
    ├─> success: True/False
    ├─> files_created: List[Path]
    └─> errors: List[str]
```

### Deployment Flow (Mode B: CloudFront + OAC)

```
User Clicks "Deploy to Cloud"
    ↓
CloudTab.on_deploy_website()
    ├─> Get AWS credentials from profile
    ├─> Check for existing CloudFront distribution
    │   └─> S3Manager.find_distribution_by_origin()
    ├─> Distribution exists?
    │   ├─> Yes: Use existing distribution_id
    │   └─> No: Create new distribution
    │       ├─> Create Origin Access Control (OAC)
    │       ├─> Create CloudFront distribution
    │       ├─> Wait for deployment (5-10 min)
    │       └─> Store distribution_id in config
    ├─> Upload files to S3
    │   ├─> S3Manager.upload_directory()
    │   ├─> Set cache headers (HTML: 5min, CSS/JS: 1hr)
    │   └─> Private ACL (OAC access only)
    ├─> Update S3 bucket policy
    │   └─> Allow cloudfront.amazonaws.com with SourceArn
    ├─> Create CloudFront invalidation
    │   └─> Invalidate /* (all files)
    └─> Return deployment_url
        ↓
Display Success + URL
```

### AI Content Generation Flow

```
Content Generator Requests AI Content
    ↓
Check Cache
    ├─> ContentCache.get(content_type, context_hash)
    ├─> Found + Valid? → Return cached content ✅
    └─> Not found or expired? → Continue ↓
        ↓
AIContentService.generate_content()
    ├─> Check API key configured?
    │   └─> No: Return None (fallback to template)
    ├─> Build prompt from context
    │   ├─> Include business info
    │   ├─> Include services/products
    │   └─> Include SEO requirements
    ├─> Call OpenAI API
    │   ├─> Model: gpt-4o-mini (default)
    │   ├─> Max tokens: 2000
    │   └─> Temperature: 0.7
    ├─> Receive response
    └─> Validate HTML structure
        ↓
Cache Result
    ├─> ContentCache.set(content, ttl=168 hours)
    └─> Return content to generator
        ↓
Generator uses AI content (or template if AI failed)
```

---

## 5. Component Interactions

### UI Layer → Core Layer

**Signal Flow**:

```python
# UI emits signal
class ProductsTab(QWidget):
    products_changed = pyqtSignal()

    def add_product(self, product_data):
        # Add product to table
        self.products_changed.emit()

# Main window connects to signal
class EnhancedMainWindow(QMainWindow):
    def __init__(self):
        self.products_tab.products_changed.connect(self.on_config_changed)

    def on_config_changed(self):
        self.unsaved_changes = True
        self.update_title()
```

### Core Layer → UI Layer

**Progress Updates**:

```python
# Generator reports progress
class WebsiteGenerator:
    def generate(self, config, output_dir, progress_callback=None):
        total_pages = len(config.city_pages) + 1  # cities + home

        for i, city in enumerate(config.city_pages):
            self.generate_city_page(city, config)
            if progress_callback:
                progress_callback(i + 1, total_pages, f"Generated {city.name}")

# UI handles progress
def on_generate_with_progress(self):
    def update_progress(current, total, message):
        progress = int((current / total) * 100)
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)

    generator.generate(config, output_dir, progress_callback=update_progress)
```

### Component Dependencies

**Dependency Injection Pattern**:

```python
class WebsiteGenerator:
    def __init__(
        self,
        html_generator: Optional[HTMLGenerator] = None,
        css_generator: Optional[CSSGenerator] = None,
        ai_service: Optional[AIContentService] = None,
        cache: Optional[ContentCache] = None
    ):
        # Allow injection for testing/customization
        self.html_generator = html_generator or HTMLGenerator()
        self.css_generator = css_generator or CSSGenerator()
        self.ai_service = ai_service or AIContentService()
        self.cache = cache or ContentCache()
```

**Benefits**:
- Testability: Easy to inject mocks
- Flexibility: Swap implementations
- Decoupling: Components don't create dependencies

---

## 6. Template System

### Jinja2 Template Architecture

**Template Hierarchy**:

```
templates/
├── base/
│   └── base.html              # Master template
├── pages/
│   ├── index.html             # Home page
│   ├── city.html              # City page
│   ├── product_detail.html    # Product page
│   └── service_detail.html    # Service page
└── components/
    ├── header.html            # Site header
    ├── footer.html            # Site footer
    ├── navigation.html        # Navigation menu
    └── schema.html            # Schema markup
```

**Template Inheritance**:

```jinja2
{# base/base.html #}
<!DOCTYPE html>
<html lang="en">
<head>
    {% block meta_tags %}{% endblock %}
    {% block stylesheets %}{% endblock %}
</head>
<body>
    {% include 'components/header.html' %}
    {% block content %}{% endblock %}
    {% include 'components/footer.html' %}
    {% block scripts %}{% endblock %}
</body>
</html>

{# pages/city.html #}
{% extends "base/base.html" %}

{% block content %}
<section class="hero">
    <h1>{{ service }} in {{ city.name }}, {{ city.state }}</h1>
</section>
{% endblock %}
```

### Template Data Structure

**Template Context**:

```python
template_data = {
    # Business Information
    "business_name": config.business_name,
    "phone": config.contact.phone,
    "email": config.contact.email,

    # Content
    "services": [
        {"name": "Service A", "description": "..."},
        {"name": "Service B", "description": "..."}
    ],
    "products": [...],

    # City-Specific (for city pages)
    "city": {
        "name": "Denver",
        "state": "CO",
        "content": "AI-generated or template content"
    },

    # Schema Markup
    "schema": {
        "type": "LocalBusiness",
        "name": config.business_name,
        "address": {...},
        "telephone": config.contact.phone
    },

    # Assets
    "logo_url": "/images/logo.png",
    "hero_image_url": "/images/hero.jpg",

    # SEO
    "canonical_url": "https://example.com/cities/denver.html",
    "meta_description": "...",
    "keywords": ["keyword1", "keyword2"]
}
```

### Custom Jinja2 Filters

```python
from jinja2 import Environment

def slugify(text):
    """Convert text to URL-friendly slug"""
    return text.lower().replace(' ', '-').replace(',', '')

def format_phone(phone):
    """Format phone number for display"""
    # (555) 123-4567
    return f"({phone[:3]}) {phone[3:6]}-{phone[6:]}"

# Register filters
env = Environment()
env.filters['slugify'] = slugify
env.filters['format_phone'] = format_phone

# Usage in template
{{ city.name|slugify }}  # "denver-co"
{{ phone|format_phone }} # "(555) 123-4567"
```

---

## 7. Deployment Pipeline

### Multi-Cloud Architecture

**Provider Abstraction**:

```python
class CloudProvider(ABC):
    @abstractmethod
    def authenticate(self) -> bool:
        pass

    @abstractmethod
    def create_bucket(self, name: str) -> bool:
        pass

    @abstractmethod
    def upload_directory(self, local_dir: Path, bucket: str) -> DeploymentResult:
        pass

class S3Provider(CloudProvider):
    """AWS S3 implementation"""
    pass

class GCSProvider(CloudProvider):
    """Google Cloud Storage implementation"""
    pass
```

### Deployment Modes

**Mode A: S3-Only**:
- Public bucket with website hosting
- Direct S3 URL access
- Simple, cost-effective
- No HTTPS (unless custom domain + ACM)

**Mode B: CloudFront + OAC** (Production):
- Private S3 bucket
- CloudFront distribution with OAC
- HTTPS included
- Global CDN
- Better security

### CloudFront OAC Flow

```
1. Check for existing distribution
   ├─> Query CloudFront API for distributions
   └─> Match by S3 origin + path

2. Create OAC (if needed)
   ├─> cloudfront.create_origin_access_control()
   └─> Store OAC ID

3. Create Distribution (if needed)
   ├─> Origin: S3 bucket with OAC
   ├─> Default root: index.html
   ├─> Viewer protocol: Redirect HTTP → HTTPS
   └─> Wait for deployment (~10 minutes)

4. Update S3 Bucket Policy
   ├─> Allow Service: cloudfront.amazonaws.com
   ├─> Condition: SourceArn = distribution ARN
   └─> Block all public access

5. Upload Files
   ├─> Private ACL (not public-read)
   ├─> Cache headers based on file type
   └─> Content-Type auto-detection

6. Create Invalidation
   ├─> Path: /* (all files)
   └─> Wait for invalidation (~5 minutes)

7. Return CloudFront URL
   └─> https://{distribution-id}.cloudfront.net
```

### Cache Strategy

**File Type Cache Headers**:

| File Type | Cache-Control | Rationale |
|-----------|--------------|-----------|
| HTML | `max-age=300` (5 min) | Content updates frequently |
| CSS | `max-age=3600` (1 hour) | Styles change occasionally |
| JS | `max-age=3600` (1 hour) | Scripts change occasionally |
| Images | `max-age=86400` (1 day) | Static assets |
| Fonts | `max-age=2592000` (30 days) | Rarely change |

---

## 8. Testing Strategy

### Test-Driven Development (TDD)

**TDD Workflow** (see TDD_WORKFLOW.md):

```
🔴 Red: Write failing test
    ↓
🟢 Green: Make test pass (minimal code)
    ↓
🔵 Refactor: Improve code quality
    ↓
Repeat
```

### Test Structure

```
tests/
├── unit/                              # Isolated component tests
│   ├── test_config_parser.py        # Config parsing
│   ├── test_html_generator.py       # HTML generation
│   ├── test_s3_deployer.py          # S3 deployment
│   ├── test_ai_content_service.py   # AI service
│   └── test_cloud_tab.py            # UI components
├── integration/                       # Component interaction tests
│   ├── test_website_generation.py   # Full generation workflow
│   └── test_deployment_workflow.py  # Deployment integration
├── fixtures/                          # Test data
│   ├── sample_config.yaml
│   └── mock_responses/
└── conftest.py                        # Shared pytest configuration
```

### Test Categories

**1. Unit Tests**:

```python
class TestConfigParser:
    def test_parse_valid_yaml_success(self):
        """Test parsing valid YAML succeeds"""
        parser = ConfigParser()
        config = parser.parse_yaml_file("tests/fixtures/sample_config.yaml")
        assert config.business_name == "Test Business"

    def test_parse_invalid_yaml_raises_error(self):
        """Test parsing invalid YAML raises appropriate error"""
        parser = ConfigParser()
        with pytest.raises(YAMLError):
            parser.parse_yaml_file("tests/fixtures/invalid.yaml")
```

**2. Integration Tests**:

```python
class TestWebsiteGeneration:
    def test_full_generation_workflow(self, temp_output_dir):
        """Test complete website generation workflow"""
        # Given: Valid configuration
        config = ConfigParser().parse_yaml_file("tests/fixtures/sample_config.yaml")

        # When: Generate website
        generator = WebsiteGenerator()
        result = generator.generate(config, temp_output_dir)

        # Then: All pages created successfully
        assert result.success is True
        assert (temp_output_dir / "index.html").exists()
        assert (temp_output_dir / "cities" / "denver-co.html").exists()
```

**3. Mock-Based Tests**:

```python
@patch('src.core.services.ai_content_service.openai.ChatCompletion')
def test_ai_content_generation_with_mock(mock_openai):
    """Test AI content generation with mocked OpenAI response"""
    # Given: Mocked OpenAI response
    mock_openai.create.return_value = Mock(
        choices=[Mock(message=Mock(content="<section>AI content</section>"))]
    )

    # When: Generate content
    service = AIContentService()
    content = service.generate_home_content(config)

    # Then: Returns AI-generated content
    assert "<section>AI content</section>" in content
    mock_openai.create.assert_called_once()
```

### Test Coverage

**Current Status** (v3.6.0):

| Module | Coverage | Status |
|--------|----------|--------|
| Core Config | 85% | ✅ Good |
| Generators | 72% | ⚠️ Needs improvement |
| Deployment (Cloud) | 95% | ✅ Excellent |
| UI Components | 45% | ❌ Low - planned Phase 2 |
| AI Services | 88% | ✅ Good |

**Coverage Goals**:
- Critical modules (config, deployment): 90%+
- Business logic (generators): 80%+
- UI components: 70%+
- Overall project: 80%+

### Pre-Commit Hooks

**Automated Quality Gates**:

```bash
# Defined in .pre-commit-config.yaml
hooks:
  - ruff check       # Linting
  - black --check    # Code formatting
  - mypy            # Type checking
  - pytest tests/unit/test_aws_credentials.py  # Cloud infrastructure tests
  - pytest tests/unit/test_s3_manager.py
  - pytest tests/unit/test_oac_methods.py
  # (113 cloud tests run on every commit)
```

**Result**: All 113 cloud infrastructure tests must pass before commit.

---

## 9. Development Workflow

### Test-Driven Development Process

**Workflow Steps**:

1. **Red Phase**: Write failing test
```python
def test_new_feature_not_yet_implemented(self):
    """Test new feature behavior"""
    result = new_feature_function(input_data)
    assert result == expected_output  # FAILS (not implemented yet)
```

2. **Green Phase**: Minimal implementation
```python
def new_feature_function(input_data):
    return expected_output  # Hardcoded to pass test
```

3. **Refactor Phase**: Real implementation
```python
def new_feature_function(input_data):
    # Proper implementation with business logic
    processed = process(input_data)
    return transform(processed)
```

4. **Commit**: `test: add feature X` → `feat: implement feature X` → `refactor: improve feature X`

### Git Workflow

**Branching Strategy**:

```
main (production-ready)
  ├─> feature/google-verification-tag
  ├─> feature/deployment-grid-view
  ├─> refactor/website-generator-orchestration
  └─> fix/cloudfront-oac-permissions
```

**Commit Message Convention** (Conventional Commits):

```
<type>(<scope>): <description>

[optional body]
[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code restructuring
- `test`: Test changes
- `docs`: Documentation
- `chore`: Maintenance
- `perf`: Performance improvement

**Examples**:
```
feat(gsc): Add Google Search Console verification integration
fix(cloud): Remove reference to non-existent cloudfront_domain_input
refactor(generators): Extract content generators from website_generator
test(deployment): Add comprehensive OAC permissions tests
docs(architecture): Create comprehensive architecture guide
```

### Code Quality Standards

**Python Style (PEP 8 + Project Standards)**:

```python
# GOOD: Clear, typed, documented
def generate_city_page(
    city: CityPage,
    config: ClientConfig,
    output_dir: Path
) -> GenerationResult:
    """
    Generate city-specific landing page.

    Args:
        city: City page configuration
        config: Client configuration
        output_dir: Output directory path

    Returns:
        GenerationResult with success status and file path

    Raises:
        TemplateError: If template rendering fails
    """
    # Implementation
    pass

# BAD: No types, no docs, unclear
def gen_page(city, cfg, dir):
    # Implementation
    pass
```

**Type Hints Required**:
- All function parameters
- All return types
- Complex data structures (use dataclasses or TypedDict)

**Docstring Requirements**:
- Google-style docstrings
- Required for: public methods, classes, modules
- Optional for: private methods, simple getters/setters

### Refactoring Guidelines

**When to Refactor**:
- Module >800 lines (see REFACTORING_PLAN.md)
- Class has >10 responsibilities
- Method >50 lines (consider extraction)
- Duplicated code (DRY principle)
- Complex conditionals (consider strategy pattern)

**Refactoring Safety**:
1. **Ensure test coverage**: Add tests BEFORE refactoring
2. **Small steps**: Incremental changes with tests passing
3. **Feature branch**: Use dedicated branch for refactoring
4. **Backward compatibility**: Maintain public APIs
5. **Documentation**: Update docs with refactored structure

**Planned Refactoring** (see ORCHESTRATION_REFACTOR_PLAN.md):

```
website_generator.py (1,947 lines) →
  ├─> website_orchestrator.py (400-500 lines)
  ├─> content_coordinator.py (400-500 lines)
  ├─> build_pipeline.py (300-400 lines)
  └─> asset_manager.py (300-400 lines)
```

### Debugging Methodology

**Systematic Debugging** (see DEBUGGING.md):

1. **Map data flow**: Trace through all layers
2. **Add checkpoints**: Debug output at transitions
3. **Verify each layer**: Test independently
4. **Incremental testing**: Test fixes step-by-step
5. **Document findings**: Record root cause and solution

**Debug Tools**:
- Strategic print statements
- Error log analysis (`logs/error_log.txt`)
- Configuration verification
- Template data inspection

---

## 10. Extension Points

### Adding New Cloud Providers

**1. Implement CloudProvider Interface**:

```python
class AzureBlobProvider(CloudProvider):
    """Azure Blob Storage provider"""

    def __init__(self, config: ProviderConfig):
        self.config = config
        self.client = None

    def authenticate(self) -> bool:
        """Authenticate with Azure"""
        # Implementation
        pass

    def create_bucket(self, name: str) -> bool:
        """Create Azure container"""
        # Implementation
        pass

    def upload_directory(self, local_dir: Path, container: str) -> DeploymentResult:
        """Upload to Azure Blob Storage"""
        # Implementation
        pass
```

**2. Register in ProviderFactory**:

```python
class ProviderFactory:
    @staticmethod
    def create_provider(provider_type: ProviderType, config: ProviderConfig):
        if provider_type == ProviderType.AWS_S3:
            return S3Provider(config)
        elif provider_type == ProviderType.GOOGLE_GCS:
            return GCSProvider(config)
        elif provider_type == ProviderType.AZURE_BLOB:
            return AzureBlobProvider(config)
        # ...
```

**3. Add UI Support** (CloudTab):

```python
# Add Azure option to provider selection
self.provider_combo.addItem("Azure Blob Storage", ProviderType.AZURE_BLOB)

# Add Azure-specific settings UI
def setup_azure_settings(self):
    # Azure connection string, container name, etc.
    pass
```

### Adding New AI Providers

**1. Create Provider Class**:

```python
class ClaudeContentService(AIContentService):
    """Anthropic Claude integration"""

    def _call_ai_api(self, prompt: str) -> str:
        """Call Claude API instead of OpenAI"""
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
```

**2. Configure via Environment**:

```env
AI_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-your-key-here
ANTHROPIC_MODEL=claude-3-sonnet-20240229
```

**3. Factory Selection**:

```python
def create_ai_service() -> AIContentService:
    provider = os.getenv("AI_PROVIDER", "openai")

    if provider == "openai":
        return OpenAIContentService()
    elif provider == "claude":
        return ClaudeContentService()
    # ...
```

### Adding New Template Types

**1. Create Template Files**:

```
templates/pages/
└── new_template_type.html      # New template
```

**2. Update Template Metadata**:

```json
{
  "template_id": "new_template_type",
  "name": "New Template Type",
  "description": "Description of new template",
  "required_data": {
    "fields": ["field1", "field2"]
  },
  "category": "page",
  "preview_url": "/templates/previews/new_template_type.html"
}
```

**3. Add Generation Logic**:

```python
class WebsiteGenerator:
    def generate_new_page_type(self, config: ClientConfig) -> str:
        """Generate new page type"""
        template_data = self._prepare_template_data(config)
        template = self.jinja_env.get_template("pages/new_template_type.html")
        return template.render(**template_data)
```

### Adding New UI Tabs

**1. Create Tab Class**:

```python
class NewFeatureTab(QWidget):
    """New feature tab"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        # Add widgets
        self.setLayout(layout)

    def get_config_data(self) -> Dict[str, Any]:
        """Export tab data for configuration"""
        return {
            "new_feature": {
                "field1": self.field1_input.text(),
                "field2": self.field2_input.text()
            }
        }

    def set_config_data(self, data: Dict[str, Any]):
        """Import configuration data to tab"""
        new_feature = data.get("new_feature", {})
        self.field1_input.setText(new_feature.get("field1", ""))
        self.field2_input.setText(new_feature.get("field2", ""))
```

**2. Register in Main Window**:

```python
class EnhancedMainWindow(QMainWindow):
    def setup_tabs(self):
        # ... existing tabs ...

        self.new_feature_tab = NewFeatureTab(self)
        self.tabs.addTab(self.new_feature_tab, "New Feature")
```

**3. Integrate in Config Flow**:

```python
def get_all_config_data(self) -> Dict[str, Any]:
    """Collect from all tabs"""
    return {
        **self.business_tab.get_config_data(),
        **self.products_tab.get_config_data(),
        **self.new_feature_tab.get_config_data(),  # New tab
        # ...
    }
```

### Plugin Architecture (Future)

**Planned Extension System**:

```python
class PluginInterface:
    """Base interface for plugins"""

    def initialize(self, app: QApplication):
        """Called when plugin loads"""
        pass

    def register_hooks(self, hook_manager: HookManager):
        """Register event hooks"""
        pass

    def shutdown(self):
        """Called when plugin unloads"""
        pass

# Example plugin
class CustomSchemaPlugin(PluginInterface):
    def register_hooks(self, hook_manager):
        hook_manager.register('pre_generation', self.add_custom_schema)

    def add_custom_schema(self, context):
        # Add custom schema to template context
        context['custom_schema'] = self.generate_schema()
```

---

## Appendix A: Configuration Reference

### ClientConfig Structure

```python
@dataclass
class ClientConfig:
    # Business Information
    business_name: str
    industry: str
    company_overview: str

    # Contact Information
    contact: ContactConfig

    # Content
    services: List[Service] = field(default_factory=list)
    products: List[Product] = field(default_factory=list)
    faqs: List[FAQ] = field(default_factory=list)

    # City Pages
    city_pages: List[CityPage] = field(default_factory=list)

    # Branding
    branding: BrandingConfig = field(default_factory=BrandingConfig)

    # Template Selection
    template_id: str = "seo_authority_city"

    # Deployment
    deployment: DeploymentConfig = field(default_factory=DeploymentConfig)

    # Google Business Profile
    google_business_profile: Dict[str, str] = field(default_factory=dict)
```

---

## Appendix B: Error Handling

### Error Handling Strategy

**1. Specific Exceptions**:

```python
# Define custom exceptions
class ConfigurationError(Exception):
    """Raised when configuration is invalid"""
    pass

class TemplateRenderError(Exception):
    """Raised when template rendering fails"""
    pass

class DeploymentError(Exception):
    """Raised when cloud deployment fails"""
    pass

# Use in code
def parse_yaml_file(self, file_path: str) -> ClientConfig:
    try:
        with open(file_path) as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise ConfigurationError(f"Config file not found: {file_path}")
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML: {e}")
```

**2. Error Logging**:

```python
import logging

logger = logging.getLogger(__name__)

def generate_website(self, config, output_dir):
    try:
        # Generation logic
        pass
    except TemplateRenderError as e:
        logger.error(f"Template rendering failed: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.exception("Unexpected error during generation")
        raise
```

**3. User-Friendly UI Errors**:

```python
def on_deploy_website(self):
    try:
        result = deployer.deploy(...)
    except DeploymentError as e:
        QMessageBox.critical(
            self,
            "Deployment Failed",
            f"Failed to deploy website:\n{str(e)}\n\n"
            "Please check your AWS credentials and try again."
        )
        logger.error(f"Deployment error: {e}", exc_info=True)
```

---

## Appendix C: Performance Optimization

### Caching Strategy

**AI Content Caching**:
- Cache duration: 7 days (configurable)
- Cache key: Hash of content type + business context
- Storage: `.cache/ai_content/` (file-based)
- Savings: $0 for cached requests vs $0.0007/page

**Template Caching**:
- Jinja2 bytecode cache enabled
- Templates compiled on first use
- Reused for subsequent generations

### Optimization Guidelines

**1. Database/File Operations**:
- Batch file writes when possible
- Use Path objects for cross-platform compatibility
- Avoid redundant file reads

**2. UI Responsiveness**:
- Run long operations in separate threads
- Use QThreads for generation/deployment
- Provide progress feedback

**3. Memory Management**:
- Clean up large objects after use
- Use generators for large datasets
- Limit in-memory caching

---

**End of Architecture Guide**

For user-facing documentation, see [USER_GUIDE.md](USER_GUIDE.md).
For administration and setup, see [ADMIN_GUIDE.md](ADMIN_GUIDE.md).
