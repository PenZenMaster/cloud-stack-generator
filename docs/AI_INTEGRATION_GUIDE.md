# AI Content Generator Integration Guide

**Date**: 2025-10-19
**Status**: Implementation Guide
**Version**: 1.0

---

## Overview

This guide provides step-by-step instructions for integrating the AI content generators into the main website generation workflow and implementing industry-specific prompt customization.

---

## Phase 1: Website Generator Integration

### 1.1 Update Website Generator to Use AI Content

**File**: `src/core/website_generator.py`

Add AI service initialization in the `__init__` method:

```python
from .services.ai_content_service import AIContentService
from .services.content_cache import ContentCache

class WebsiteGenerator:
    """Generate static HTML websites from configuration"""

    def __init__(self):
        self.output_dir: Optional[str] = None
        self.config: Optional[ClientConfig] = None

        # Initialize AI services
        self.ai_service = AIContentService()
        self.content_cache = ContentCache()
```

### 1.2 Update HTML Generator

**File**: `src/core/generators/html_generator.py`

Modify to accept and use AI services:

```python
from ..services.ai_content_service import AIContentService
from ..services.content_cache import ContentCache
from .content import HomeContentGenerator, CityContentGenerator

class HTMLGenerator:
    def __init__(
        self,
        ai_service: Optional[AIContentService] = None,
        cache: Optional[ContentCache] = None
    ):
        self.ai_service = ai_service or AIContentService()
        self.cache = cache or ContentCache()

        # Initialize content generators with AI support
        self.home_gen = HomeContentGenerator(
            ai_service=self.ai_service,
            cache=self.cache
        )
        self.city_gen = CityContentGenerator(
            ai_service=self.ai_service,
            cache=self.cache
        )

    def generate_homepage(self, config: ClientConfig) -> str:
        """Generate homepage HTML with AI-powered content"""
        # ... existing template code ...

        # Use AI-powered content generation
        content = self.home_gen.generate_enhanced_home_content(config, use_ai=True)

        # ... rest of template assembly ...
```

### 1.3 Update City Page Generator

**File**: `src/core/generators/city_page_generator.py`

```python
from ..services.ai_content_service import AIContentService
from ..services.content_cache import ContentCache
from .content import CityContentGenerator

class CityPageGenerator:
    def __init__(
        self,
        config: ClientConfig,
        ai_service: Optional[AIContentService] = None,
        cache: Optional[ContentCache] = None
    ):
        self.config = config
        self.ai_service = ai_service or AIContentService()
        self.cache = cache or ContentCache()

        # Initialize city content generator with AI support
        self.city_gen = CityContentGenerator(
            ai_service=self.ai_service,
            cache=self.cache
        )

    def generate_city_page(self, city: str, state: Optional[str] = None) -> str:
        """Generate city page with AI-powered content"""
        # ... existing template code ...

        # Use AI-powered content generation
        content = self.city_gen.generate_city_content(
            self.config,
            city=city,
            use_ai=True
        )

        # ... rest of template assembly ...
```

---

## Phase 2: Industry-Specific Prompt Customization

### 2.1 Create Industry Prompt Templates

**File**: `src/core/prompts/__init__.py` (NEW)

```python
"""
Prompt Templates Module
Industry-specific prompt templates for AI content generation
"""

from .industry_prompts import IndustryPromptManager

__all__ = ['IndustryPromptManager']
```

**File**: `src/core/prompts/industry_prompts.py` (NEW)

```python
"""
Industry-Specific Prompt Templates
Customized prompts for different business industries
"""

from typing import Dict, Any, Optional


class IndustryPromptManager:
    """Manage industry-specific prompt templates"""

    # Industry-specific prompt configurations
    INDUSTRY_PROMPTS = {
        "Plumbing": {
            "tone": "professional and trustworthy",
            "focus_areas": [
                "Emergency service availability",
                "Licensed and insured status",
                "Years of experience",
                "Quality workmanship",
                "Competitive pricing"
            ],
            "keywords": [
                "plumbing",
                "licensed plumber",
                "emergency plumbing",
                "pipe repair",
                "drain cleaning",
                "water heater",
                "leak detection"
            ],
            "cta_emphasis": "24/7 emergency service and free estimates"
        },

        "HVAC": {
            "tone": "knowledgeable and reliable",
            "focus_areas": [
                "Energy efficiency",
                "Indoor air quality",
                "Comfort solutions",
                "Preventive maintenance",
                "Licensed technicians"
            ],
            "keywords": [
                "HVAC",
                "heating",
                "cooling",
                "air conditioning",
                "furnace",
                "heat pump",
                "ductwork"
            ],
            "cta_emphasis": "Schedule maintenance and save on energy costs"
        },

        "Electrical": {
            "tone": "safety-focused and professional",
            "focus_areas": [
                "Safety compliance",
                "Code compliance",
                "Licensed electricians",
                "Emergency repairs",
                "Energy efficiency"
            ],
            "keywords": [
                "electrical",
                "electrician",
                "wiring",
                "panel upgrade",
                "lighting",
                "electrical safety",
                "surge protection"
            ],
            "cta_emphasis": "Safety inspections and 24/7 emergency service"
        },

        "Roofing": {
            "tone": "dependable and detail-oriented",
            "focus_areas": [
                "Warranty protection",
                "Quality materials",
                "Expert installation",
                "Storm damage repair",
                "Free inspections"
            ],
            "keywords": [
                "roofing",
                "roof repair",
                "roof replacement",
                "shingles",
                "leak repair",
                "storm damage",
                "roof inspection"
            ],
            "cta_emphasis": "Free roof inspection and lifetime warranties"
        },

        "Landscaping": {
            "tone": "creative and environmental-conscious",
            "focus_areas": [
                "Landscape design",
                "Sustainable practices",
                "Seasonal maintenance",
                "Property enhancement",
                "Professional expertise"
            ],
            "keywords": [
                "landscaping",
                "lawn care",
                "landscape design",
                "irrigation",
                "hardscaping",
                "tree service",
                "lawn maintenance"
            ],
            "cta_emphasis": "Transform your outdoor space with professional design"
        },

        "Portable Toilet Supplier": {
            "tone": "professional and service-focused",
            "focus_areas": [
                "Cleanliness standards",
                "Timely service",
                "Event support",
                "Construction site solutions",
                "ADA compliance"
            ],
            "keywords": [
                "portable toilets",
                "porta potty",
                "restroom rental",
                "construction restrooms",
                "event facilities",
                "sanitation services",
                "portable restrooms"
            ],
            "cta_emphasis": "Clean, reliable portable restroom solutions for any event"
        },

        # Default template for unlisted industries
        "General": {
            "tone": "professional and customer-focused",
            "focus_areas": [
                "Quality service",
                "Customer satisfaction",
                "Experienced professionals",
                "Competitive pricing",
                "Reliable service"
            ],
            "keywords": [],
            "cta_emphasis": "Contact us for professional service"
        }
    }

    @classmethod
    def get_industry_config(cls, industry: str) -> Dict[str, Any]:
        """
        Get prompt configuration for a specific industry.

        Args:
            industry: Industry name

        Returns:
            Industry-specific configuration dictionary
        """
        return cls.INDUSTRY_PROMPTS.get(industry, cls.INDUSTRY_PROMPTS["General"])

    @classmethod
    def build_home_page_prompt(cls, context: Dict[str, Any]) -> str:
        """
        Build industry-specific home page prompt.

        Args:
            context: Business context including industry

        Returns:
            Customized prompt string
        """
        industry = context.get('industry', 'General')
        industry_config = cls.get_industry_config(industry)

        # Extract basic info
        business_name = context['business_name']
        services_list = "\n".join([
            f"- {s['name']}: {s['description']}" for s in context['services']
        ]) if context['services'] else "General services"

        # Build focus areas section
        focus_areas = "\n".join([f"- {area}" for area in industry_config['focus_areas']])

        # Build keywords section
        keywords = ", ".join(industry_config['keywords']) if industry_config['keywords'] else "industry-specific terms"

        prompt = f"""You are a professional web content writer specializing in {industry} businesses.

Generate compelling, SEO-optimized HTML content for a home page with these specifications:

BUSINESS INFORMATION:
- Business Name: {business_name}
- Industry: {industry}
- Tone: {industry_config['tone']}
- Company Overview: {context.get('company_overview', 'Not provided')}

SERVICES:
{services_list}

INDUSTRY FOCUS AREAS (emphasize these):
{focus_areas}

SEO KEYWORDS (use naturally):
{keywords}

CALL-TO-ACTION EMPHASIS:
{industry_config['cta_emphasis']}

REQUIREMENTS:
1. Generate ONLY the HTML content sections (no <html>, <head>, or <body> tags)
2. Use semantic HTML5 with proper section tags
3. Maintain a {industry_config['tone']} tone throughout
4. Include these sections:
   - Hero section with compelling headline focusing on {industry_config['cta_emphasis']}
   - About section introducing the business
   - Why Choose Us section (highlight: {", ".join(industry_config['focus_areas'][:3])})
   - Services showcase
   - Strong call-to-action
5. Use appropriate CSS classes: hero, hero-overlay, hero-content, about-section, services-grid
6. Naturally incorporate these keywords: {keywords}
7. Content should be 600-800 words total
8. Include 2-3 clear calls-to-action
9. Emphasize trust signals specific to {industry}

OUTPUT FORMAT:
Return ONLY the HTML sections, starting with <section> tags. No explanatory text."""

        return prompt

    @classmethod
    def build_city_page_prompt(cls, context: Dict[str, Any]) -> str:
        """
        Build industry-specific city page prompt.

        Args:
            context: Business and city context

        Returns:
            Customized prompt string
        """
        industry = context.get('industry', 'General')
        industry_config = cls.get_industry_config(industry)
        city = context['city']

        # Build keywords with city
        base_keywords = industry_config['keywords'][:5]  # Top 5 keywords
        local_keywords = [f"{city} {kw}" for kw in base_keywords]
        keywords = ", ".join(local_keywords)

        prompt = f"""You are a professional web content writer specializing in local {industry} businesses.

Generate SEO-optimized, localized HTML content for a {city}-specific service page:

BUSINESS INFORMATION:
- Business Name: {context['business_name']}
- Industry: {industry}
- Location: {city}{', ' + context['state'] if context.get('state') else ''}
- Tone: {industry_config['tone']}

LOCAL KEYWORDS (use naturally):
{keywords}

INDUSTRY FOCUS AREAS:
{chr(10).join([f"- {area}" for area in industry_config['focus_areas']])}

REQUIREMENTS:
1. Generate ONLY the HTML content sections
2. Emphasize LOCAL service in {city}
3. Include these sections:
   - Hero section highlighting service in {city}
   - Local expertise section (why best choice in this city)
   - Services section for {city} residents
   - Local trust signals and community commitment
4. Use CSS classes: hero, hero-overlay, hero-text, content, services-grid
5. Naturally incorporate: {city}, local, area, community
6. Maintain {industry_config['tone']} tone
7. Content: 400-600 words
8. Include strong local call-to-action

OUTPUT FORMAT:
Return ONLY HTML sections. No explanatory text."""

        return prompt
```

### 2.2 Integrate Industry Prompts into AI Service

**File**: `src/core/services/ai_content_service.py`

Update the `_build_home_page_prompt` and `_build_city_page_prompt` methods:

```python
from ..prompts.industry_prompts import IndustryPromptManager

class AIContentService:
    # ... existing code ...

    def _build_home_page_prompt(self, context: Dict[str, Any]) -> str:
        """Build industry-specific prompt for home page"""
        return IndustryPromptManager.build_home_page_prompt(context)

    def _build_city_page_prompt(self, context: Dict[str, Any]) -> str:
        """Build industry-specific prompt for city page"""
        return IndustryPromptManager.build_city_page_prompt(context)
```

---

## Phase 3: Configuration and Testing

### 3.1 Add UI Toggle for AI Content

**File**: `src/ui/components/generation_tab.py` (or similar)

Add checkbox to enable/disable AI content:

```python
# In setup_ui method
self.use_ai_content_checkbox = QCheckBox("Use AI-Generated Content")
self.use_ai_content_checkbox.setChecked(True)  # Default enabled
self.use_ai_content_checkbox.setToolTip(
    "Generate unique content using AI. Falls back to templates if disabled or if AI fails."
)
```

### 3.2 Update Generation Call

Pass AI preference to generator:

```python
def generate_website(self):
    use_ai = self.use_ai_content_checkbox.isChecked()

    # Configure generators
    generator.home_gen.use_ai = use_ai
    generator.city_gen.use_ai = use_ai

    # Generate
    result = generator.generate(config, output_dir)
```

---

## Implementation Checklist

### Core Integration
- [ ] Update `WebsiteGenerator.__init__` to initialize AI services
- [ ] Update `HTMLGenerator` to use `HomeContentGenerator` with AI
- [ ] Update `CityPageGenerator` to use `CityContentGenerator` with AI
- [ ] Add AI service parameters to all generator constructors

### Industry Prompts
- [ ] Create `src/core/prompts/` directory
- [ ] Implement `IndustryPromptManager` class
- [ ] Add industry configs for: Plumbing, HVAC, Electrical, Roofing, Landscaping, Portable Toilet Supplier
- [ ] Update `AIContentService` to use `IndustryPromptManager`

### UI Integration
- [ ] Add "Use AI Content" checkbox to generation settings
- [ ] Add industry-specific preview in settings
- [ ] Show AI vs template indicator during generation
- [ ] Display cache hit/miss statistics

### Testing
- [ ] Test AI content generation for each industry
- [ ] Verify fallback to templates when AI disabled
- [ ] Test caching behavior (first vs subsequent runs)
- [ ] Validate SEO keywords in generated content
- [ ] Check tone consistency for each industry

### Documentation
- [ ] Update user manual with AI content features
- [ ] Add industry customization guide
- [ ] Document cost estimates per industry
- [ ] Create troubleshooting guide

---

## Quick Implementation Script

For rapid implementation, run these commands:

```bash
# Create prompts directory
mkdir -p src/core/prompts

# Copy industry prompts template (you'll need to create this file)
# cp industry_prompts.py src/core/prompts/

# Update existing generators (manual edit required)
# Edit: src/core/website_generator.py
# Edit: src/core/generators/html_generator.py
# Edit: src/core/generators/city_page_generator.py
# Edit: src/core/services/ai_content_service.py

# Test the integration
python examples/ai_content_example.py
```

---

## Expected Improvements

### Content Quality
- **Before**: Generic, template-based content
- **After**: Industry-specific, engaging, SEO-optimized content

### SEO Performance
- Natural keyword integration
- Location-specific content for city pages
- Industry-specific trust signals

### User Experience
- Toggle AI on/off per generation
- View cache statistics
- See industry-specific previews

### Cost Efficiency
- First generation: ~$0.0007 per page
- Cached regenerations: $0 (FREE for 7 days)
- 1000 pages initial: ~$0.70
- Subsequent runs: ~$0

---

## Support

For questions or issues:
1. Review `docs/AI_CONTENT_GENERATION.md`
2. Check `docs/AI_SETUP_QUICKSTART.md`
3. Run example: `python examples/ai_content_example.py`
4. Review logs for AI service errors

---

**Last Updated**: 2025-10-19
**Version**: 1.0
**Status**: Ready for Implementation
