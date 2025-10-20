# AI Content Generation - Quick Start Guide

**5-Minute Setup for ChatGPT-Powered Content**

---

## Prerequisites

- OpenAI account with API access
- Python 3.9+ environment

---

## Step 1: Install Dependencies (1 minute)

```bash
cd cloud-stack-generator
pip install openai python-dotenv
```

Or install all dependencies:
```bash
pip install -r requirements.txt
```

---

## Step 2: Get OpenAI API Key (2 minutes)

1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Click **"Create new secret key"**
4. Give it a name (e.g., "Cloud Stack Generator")
5. Copy the key (starts with `sk-proj-...`)

---

## Step 3: Configure Environment (1 minute)

Create `.env` file in project root:

```bash
# Copy example file
cp .env.example .env
```

Edit `.env` and add your API key:

```env
OPENAI_API_KEY=sk-proj-your-actual-api-key-here

# Optional: Use these defaults for cost efficiency
OPENAI_MODEL=gpt-4o-mini
AI_CONTENT_ENABLED=true
AI_CONTENT_CACHE_ENABLED=true
```

---

## Step 4: Test the Integration (1 minute)

**Option 1: Run the example script**

```bash
python examples/ai_content_example.py
```

This will:
- Validate your environment configuration
- Show configuration status
- Generate example home and city pages
- Display cache statistics

**Option 2: Quick Python test**

```python
from src.core.config import EnvironmentConfig, OpenAIConfig
from src.core.services.ai_content_service import AIContentService

# Check configuration
if OpenAIConfig.is_configured():
    print("SUCCESS! OpenAI API key is configured")
    print(f"Model: {OpenAIConfig.get_model()}")

    # Test service
    service = AIContentService()
    if service.is_available():
        print("AI content generation is ready!")
else:
    print("API key not configured. Check your .env file")
```

**Option 3: Run the test suite**

```bash
pytest tests/unit/test_ai_content_service.py::TestContentCache -v
```

---

## Step 5: Generate Your First AI Content

The integration is automatic! Just use the existing content generators:

```python
from src.core.services.ai_content_service import AIContentService
from src.core.services.content_cache import ContentCache
from src.core.generators.content import HomeContentGenerator

# Initialize AI services
ai_service = AIContentService()
cache = ContentCache()

# Create generator with AI support
generator = HomeContentGenerator(ai_service=ai_service, cache=cache)

# Generate content (AI-powered automatically)
content = generator.generate_enhanced_home_content(your_config)
```

---

## What Happens Now?

### First Run (AI Generation)
1. System checks cache (empty on first run)
2. Sends business context to OpenAI API
3. Receives AI-generated HTML content
4. Caches the result for 7 days
5. Returns beautiful, SEO-optimized content

**Cost**: ~$0.0007 per home page

### Subsequent Runs (Cached)
1. System checks cache (finds cached content)
2. Returns cached content instantly
3. Zero API calls

**Cost**: $0 (FREE!)

---

## Configuration Options

### Use Less Expensive Model (Recommended)
```env
OPENAI_MODEL=gpt-4o-mini       # 10x cheaper than GPT-4
```

### Adjust Content Length
```env
OPENAI_MAX_TOKENS=2000         # Increase for longer content
```

### Adjust Creativity
```env
OPENAI_TEMPERATURE=0.7         # 0.0 = focused, 1.0 = creative
```

### Extend Cache Duration
```env
AI_CONTENT_CACHE_HOURS=336     # 14 days instead of 7
```

### Disable AI (Fall Back to Templates)
```env
AI_CONTENT_ENABLED=false       # Use templates only
```

---

## Troubleshooting

### "Service not available"

**Check:**
1. `.env` file exists in project root
2. `OPENAI_API_KEY` is set correctly
3. API key is valid (test at platform.openai.com)
4. `openai` package is installed: `pip install openai`

### "Rate limit exceeded"

**Solutions:**
- Wait a few minutes and retry
- Enable caching: `AI_CONTENT_CACHE_ENABLED=true`
- Upgrade OpenAI account tier

### Content falls back to templates

**Possible reasons:**
- API key not configured
- API request failed (check logs)
- AI is disabled: `AI_CONTENT_ENABLED=false`
- OpenAI service is down (rare)

**This is OK!** The system gracefully falls back to templates.

---

## Cost Estimation

Using **gpt-4o-mini** (recommended):

| Content Type | Cost per Page | 100 Pages | 1000 Pages |
|--------------|---------------|-----------|------------|
| Home Page    | $0.0007       | $0.07     | $0.70      |
| City Page    | $0.0006       | $0.06     | $0.60      |

**With 7-day caching**: Regenerations within 7 days cost $0!

Example scenario:
- 100 businesses
- 10 cities each = 1,100 pages total
- **Total cost**: ~$0.70
- **Cost per business**: ~$0.007

---

## Next Steps

✅ **You're all set!** AI content generation is now active.

### Learn More:
- [Full Documentation](AI_CONTENT_GENERATION.md)
- [Prompt Customization](AI_CONTENT_GENERATION.md#prompt-engineering)
- [Cache Management](AI_CONTENT_GENERATION.md#caching)
- [Cost Optimization](AI_CONTENT_GENERATION.md#cost-management)

### Advanced Topics:
- Customizing prompts for your industry
- A/B testing AI vs template content
- Multi-language support (coming soon)
- Analytics integration

---

## Support

Having issues? Check:
1. [Full Documentation](AI_CONTENT_GENERATION.md#troubleshooting)
2. [GitHub Issues](https://github.com/your-repo/issues)
3. Application logs for error messages

---

**Happy generating!** 🚀

Your content is now powered by cutting-edge AI while maintaining full control and fallback options.
