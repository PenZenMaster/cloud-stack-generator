# Phase 2: SEO Analysis - Quick Start Guide

**Status:** ✅ Demo Ready
**Date:** 2026-02-17
**Version:** 3.15.0

---

## Overview

Phase 2 adds LLM-powered SEO analysis to AWG. Analyze generated websites for content quality, meta tag optimization, and get actionable SEO recommendations.

**Current Features:**
- ✅ Claude-powered content analysis
- ✅ Keyword density & distribution
- ✅ Meta tag optimization
- ✅ SEO scoring (0-100)
- ✅ Prioritized recommendations
- ✅ CLI commands

**Coming Soon:**
- ⏭️ OpenAI GPT support
- ⏭️ HTML/JSON report export
- ⏭️ Batch directory analysis
- ⏭️ Competitive analysis

---

## Installation

1. **Install dependencies:**
```bash
pip install anthropic>=0.18.0
```

2. **Set up Claude API key:**
```bash
# Windows (CMD)
set CLAUDE_API_KEY=sk-ant-api03-...

# Windows (PowerShell)
$env:CLAUDE_API_KEY="sk-ant-api03-..."

# Linux/Mac
export CLAUDE_API_KEY=sk-ant-api03-...
```

---

## CLI Commands

### 1. Analyze Content

Comprehensive SEO analysis of HTML content:

```bash
# Basic analysis
awg analyze content output/clients/my-site/index.html

# With target keywords
awg analyze content output/clients/my-site/index.html \
  -k "plumbing services" \
  -k "emergency plumber"

# Choose model preset
awg analyze content output/clients/my-site/index.html \
  --model fast      # Fastest, cheapest (Claude Haiku)
  --model balanced  # Good balance (Claude Sonnet) - DEFAULT
  --model thorough  # Best quality (Claude Opus)

# With API key (if not in env)
awg analyze content output/clients/my-site/index.html \
  --api-key sk-ant-api03-...
```

**Output Example:**
```
Analyzing: output/clients/my-site/index.html
Model: balanced

SEO Score: 78/100 (Grade: C)

Category Scores:
  Content Quality:    75/100
  Heading Structure:  82/100
  Meta Tags:          68/100
  Internal Linking:   80/100

High Priority Recommendations (3):
  1. Meta description too short (142 chars)
     Recommendation: Expand to 150-160 characters with target keywords

  2. Missing H1 tag
     Recommendation: Add primary H1 heading with main keyword

  3. Low keyword density for "plumbing services"
     Recommendation: Increase keyword mentions in first paragraph

Content Stats:
  Word Count: 850
  Internal Links: 12
  External Links: 3

Model used: claude-3-5-sonnet-20241022
Estimated cost: $0.0245
```

---

### 2. Analyze Meta Tags

Focus specifically on title and meta description:

```bash
# Basic meta analysis
awg analyze meta output/clients/my-site/index.html

# With target keywords
awg analyze meta output/clients/my-site/index.html \
  -k "emergency plumbing" \
  -k "24/7 plumber"
```

**Output Example:**
```
Analyzing meta tags: output/clients/my-site/index.html

Meta Tags Score: 68/100

Title: Emergency Plumbing Services | Available 24/7
  Length: 48 chars (optimal: 50-60)
  Score: 75/100

Description: We provide emergency plumbing services 24/7 in your area. Fast response times guaranteed.
  Length: 142 chars (optimal: 150-160)
  Score: 65/100

Recommendations:
  1. [MEDIUM] Title too short (48 chars)
     Expand title to 50-60 characters for better SEO

  2. [HIGH] Description too short (142 chars)
     Expand to 150-160 characters with more keywords

  3. [LOW] Add location-specific keywords
     Include city/region name for local SEO
```

---

## Programmatic Usage

Use the SEO analyzer in your own scripts:

```python
from pathlib import Path
from src.core.seo.analyzer import SEOAnalyzer
from src.core.seo.llm.provider import ModelPreset

# Initialize analyzer
analyzer = SEOAnalyzer(
    claude_api_key="sk-ant-api03-...",
    model_preset=ModelPreset.BALANCED  # or FAST, THOROUGH
)

# Analyze single file
result = analyzer.analyze_file(
    Path("output/clients/my-site/index.html"),
    target_keywords=["plumbing services", "emergency plumber"]
)

# Access results
print(f"SEO Score: {result.overall_score.overall}/100")
print(f"Grade: {result.overall_score.get_grade()}")

# Get recommendations
for rec in result.overall_score.recommendations:
    if rec.priority.value == "high":
        print(f"[HIGH] {rec.issue}")
        print(f"  → {rec.recommendation}")

# Content analysis
content = result.content_analysis
print(f"Word count: {content.word_count}")
print(f"Keyword analysis: {content.keyword_analysis}")

# Meta analysis
meta = result.meta_analysis
print(f"Title: {meta.title} ({meta.title_length} chars)")
print(f"Description: {meta.description} ({meta.description_length} chars)")
```

---

## Model Presets & Pricing

### Claude Models (as of Feb 2026)

| Preset | Model | Speed | Quality | Input Cost | Output Cost | Use Case |
|--------|-------|-------|---------|------------|-------------|----------|
| FAST | Claude 3 Haiku | ⚡⚡⚡ | ⭐⭐ | $0.25/1M | $1.25/1M | Quick checks, batch analysis |
| BALANCED | Claude 3.5 Sonnet | ⚡⚡ | ⭐⭐⭐⭐ | $3/1M | $15/1M | **Best for most use cases** |
| THOROUGH | Claude 3 Opus | ⚡ | ⭐⭐⭐⭐⭐ | $15/1M | $75/1M | In-depth analysis, critical pages |

**Estimated Cost Per Page:**
- FAST: ~$0.01-0.02
- BALANCED: ~$0.02-0.05
- THOROUGH: ~$0.10-0.20

---

## Features Breakdown

### Content Analysis
- **Keyword density & distribution** - LLM analyzes keyword placement
- **Content length & depth** - Evaluates comprehensiveness
- **Readability & engagement** - Checks clarity and structure
- **Topic relevance** - Assesses authority signals

### Heading Structure
- **H1-H6 hierarchy** - Validates semantic structure
- **Keyword usage** - Checks heading optimization
- **Structural issues** - Identifies missing/duplicate headings

### Meta Tags
- **Title tag** - Length, keywords, CTR optimization
- **Meta description** - Length, call-to-action, uniqueness
- **Keyword optimization** - Target keyword presence

### Linking Analysis
- **Internal links** - Count, distribution, anchor text
- **External links** - Quality, relevance, nofollow balance
- **Navigation structure** - Logical flow assessment

### SEO Scoring
- **Overall score** (0-100) - Weighted average
- **Category scores** - Content, meta, headings, links, technical
- **Letter grade** - A-F grading scale
- **Strengths & weaknesses** - Key findings

---

## Recommendations Format

Recommendations include:
- **Priority** - High/Medium/Low
- **Category** - Content, meta_tags, headings, links, technical
- **Issue** - What's wrong
- **Recommendation** - How to fix it
- **Impact** - Expected SEO benefit
- **Effort** - Implementation difficulty (low/medium/high)

---

## Next Steps (Phase 2.1)

1. **OpenAI GPT Provider** - Add GPT-4o, GPT-4o-mini support
2. **HTML Reports** - Generate shareable HTML reports
3. **JSON Export** - Machine-readable output for automation
4. **Batch Analysis** - Analyze entire website directories
5. **Competitive Analysis** - Compare against competitor pages
6. **Historical Tracking** - Track SEO score over time

---

## Troubleshooting

### Error: "anthropic library not installed"
```bash
pip install anthropic>=0.18.0
```

### Error: "Claude API key required"
Set the `CLAUDE_API_KEY` environment variable:
```bash
export CLAUDE_API_KEY=sk-ant-api03-...
```

### Error: "Failed to parse LLM JSON response"
This usually means the LLM returned invalid JSON. The analyzer will fall back to basic analysis without LLM insights. Try using a higher quality model (balanced or thorough).

### Cost concerns?
- Use `--model fast` for cheaper analysis
- Analyze only key pages (homepage, main service pages)
- Set a monthly API budget in Anthropic dashboard

---

## Complementary Tools

AWG SEO Analysis **complements** (not replaces) tools like:
- **Screaming Frog** - Technical crawling, link analysis, site architecture
- **Ahrefs/SEMrush** - Backlink analysis, keyword research, rank tracking
- **Google Search Console** - Search performance, indexing status
- **Lighthouse** - Performance, accessibility, PWA

**AWG focuses on:** Content quality analysis and LLM-powered recommendations that traditional crawlers can't provide.

---

## Examples

### Analyze homepage
```bash
awg analyze content output/clients/acme-plumbing/index.html \
  -k "plumbing services" \
  -k "licensed plumber" \
  --model balanced
```

### Check meta tags for service page
```bash
awg analyze meta output/clients/acme-plumbing/services/emergency-plumbing.html \
  -k "emergency plumber" \
  -k "24/7 plumbing"
```

### Quick batch check (using bash loop)
```bash
for file in output/clients/my-site/*.html; do
  echo "Analyzing $file..."
  awg analyze content "$file" --model fast
done
```

---

## Feedback & Issues

For bugs, feature requests, or questions about SEO analysis:
- Create an issue in the repository
- Tag with `phase-2` and `seo-analysis`
- Include sample HTML and expected behavior

---

**Phase 2 Demo Complete!** 🎉

Ready to analyze your generated websites for SEO quality!
