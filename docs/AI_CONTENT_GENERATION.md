# AI-Powered Content Generation

**Version**: 1.00
**Created**: 2025-10-19
**Status**: Production Ready

---

## Overview

The Cloud Stack Generator now supports AI-powered content generation using OpenAI's GPT models. This feature dynamically generates high-quality, SEO-optimized content for home pages and city-specific pages based on business context.

### Key Benefits

- **Dynamic Content**: AI generates unique, contextual content for each business
- **SEO Optimized**: Content includes natural keyword usage and proper semantic structure
- **Cost Efficient**: Built-in caching reduces API costs
- **Graceful Fallback**: Automatically falls back to template-based generation if AI is unavailable
- **Configurable**: Easy to enable/disable and configure via environment variables

---

## Architecture

### Components

1. **AIContentService** (`src/core/services/ai_content_service.py`)
   - OpenAI API integration
   - Prompt template management
   - Error handling and retry logic

2. **ContentCache** (`src/core/services/content_cache.py`)
   - File-based caching system
   - Configurable TTL (time-to-live)
   - Cache statistics and management

3. **Enhanced Content Generators**
   - `HomeContentGenerator` - AI-powered home page content
   - `CityContentGenerator` - AI-powered city page content

### Data Flow

```
ClientConfig
    |
    v
Content Generator (check cache)
    |
    +--> Cache Hit? --> Return cached content
    |
    +--> Cache Miss? --> AI Service
                            |
                            +--> Generate with OpenAI
                            |
                            +--> Cache result
                            |
                            v
                         Return content
    |
    +--> AI Failed? --> Fallback to template-based generation
```

---

## Setup & Configuration

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `openai>=1.0.0` - OpenAI Python SDK
- `python-dotenv>=1.0.0` - Environment variable management

### 2. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
# OpenAI API Configuration
OPENAI_API_KEY=sk-proj-your-actual-api-key-here

# Optional: Model Configuration
OPENAI_MODEL=gpt-4o-mini          # Default model (cost-efficient)
OPENAI_MAX_TOKENS=2000            # Max tokens per response
OPENAI_TEMPERATURE=0.7            # Creativity level (0.0-1.0)

# AI Content Settings
AI_CONTENT_ENABLED=true           # Enable/disable AI generation
AI_CONTENT_CACHE_ENABLED=true    # Enable/disable caching
AI_CONTENT_CACHE_HOURS=168        # Cache TTL (7 days)
```

### 3. Get an OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Navigate to API Keys
4. Click "Create new secret key"
5. Copy the key and add it to your `.env` file

**Important**: Never commit your `.env` file to version control!

---

## Usage

### Basic Usage

The AI content generation is automatically integrated into the existing content generators. No code changes required if you're using the standard generator classes.

```python
from src.core.services.ai_content_service import AIContentService
from src.core.services.content_cache import ContentCache
from src.core.generators.content import HomeContentGenerator

# Initialize services
ai_service = AIContentService()
cache = ContentCache()

# Create generator with AI support
home_generator = HomeContentGenerator(ai_service=ai_service, cache=cache)

# Generate content (automatically uses AI if available)
content = home_generator.generate_enhanced_home_content(config)
```

### Disable AI for Specific Requests

```python
# Force template-based generation
content = home_generator.generate_enhanced_home_content(config, use_ai=False)
```

### Manual AI Service Usage

```python
from src.core.services.ai_content_service import AIContentService

service = AIContentService()

if service.is_available():
    # Generate home page content
    home_content = service.generate_home_content(config, use_enhanced=True)

    # Generate city page content
    city_content = service.generate_city_content(config, city="Denver", state="CO")
```

---

## Caching

### How Caching Works

1. **Cache Key Generation**: Hash of content type + business context
2. **Cache Lookup**: Check if valid cached content exists
3. **Cache Storage**: Store AI-generated content with TTL
4. **Expiration**: Automatic cleanup of expired entries

### Cache Management

```python
from src.core.services.content_cache import ContentCache

cache = ContentCache()

# Get cache statistics
stats = cache.get_stats()
print(f"Valid entries: {stats['valid_entries']}")
print(f"Expired entries: {stats['expired_entries']}")

# Clear expired entries
cache.clear_expired()

# Clear all cache
cache.clear_all()

# Invalidate specific content
cache.invalidate('home_page', context={'business_name': 'ACME Corp'})
```

### Cache Location

Cached content is stored in:
```
.cache/ai_content/
├── abc123def456...json  # Home page for Business A
├── 789xyz012abc...json  # City page for Denver
└── ...
```

Each cache file contains:
```json
{
  "content_type": "home_page",
  "content": "<section>...</section>",
  "cached_at": "2025-10-19T10:30:00",
  "expires_at": "2025-10-26T10:30:00",
  "ttl_hours": 168,
  "context": {
    "business_name": "ACME Corp",
    "industry": "Plumbing"
  },
  "metadata": {
    "business": "ACME Corp",
    "enhanced": true
  }
}
```

---

## Prompt Engineering

### Home Page Prompt

The home page prompt includes:
- Business name, industry, and overview
- Services and products
- Why choose us / unique selling points
- Contact information
- SEO requirements
- HTML structure requirements

### City Page Prompt

The city page prompt emphasizes:
- Local SEO keywords (city name, area, local, community)
- Geographic targeting
- Local trust signals
- Community commitment
- Location-specific services

### Customizing Prompts

To customize prompts, edit the `_build_home_page_prompt()` or `_build_city_page_prompt()` methods in `ai_content_service.py`:

```python
def _build_home_page_prompt(self, context: Dict[str, Any]) -> str:
    """Customize this method to change home page prompts"""

    prompt = f"""You are a professional web content writer...

    BUSINESS INFORMATION:
    - Business Name: {context['business_name']}
    - Industry: {context['industry']}

    YOUR CUSTOM REQUIREMENTS HERE...
    """

    return prompt
```

---

## Cost Management

### Estimated Costs (as of Oct 2025)

Using `gpt-4o-mini` (default):
- Input: $0.150 / 1M tokens
- Output: $0.600 / 1M tokens

**Typical Content Generation**:
- Home page: ~1,500 input tokens + 800 output tokens = $0.0007
- City page: ~1,200 input tokens + 600 output tokens = $0.0006

**With caching** (7-day TTL):
- 100 businesses with 10 cities each = 1,100 pages
- Initial cost: ~$0.70
- Subsequent regenerations within 7 days: $0 (cached)

### Cost Optimization Tips

1. **Enable Caching**: Set `AI_CONTENT_CACHE_ENABLED=true`
2. **Increase TTL**: Longer cache TTL reduces API calls
3. **Use gpt-4o-mini**: 10x cheaper than GPT-4
4. **Batch Operations**: Generate all content at once to benefit from cache
5. **Disable When Not Needed**: Set `AI_CONTENT_ENABLED=false` for testing

---

## Error Handling & Fallback

### Automatic Fallback

The system automatically falls back to template-based generation when:
- OpenAI API key is not configured
- API request fails or times out
- API returns empty/invalid response
- AI content generation is disabled

### Logging

The service logs important events:

```
INFO: AI Content Service initialized with model: gpt-4o-mini
INFO: Generating home content with AI (enhanced=True)
INFO: Successfully generated home_page (1234 characters)
INFO: Cached home_page (key: abc123def456...)
INFO: Using cached AI-generated home content
WARNING: Failed to initialize OpenAI client: Invalid API key
ERROR: AI content generation failed: Rate limit exceeded
```

---

## Testing

### Run Unit Tests

```bash
# Run all AI service tests
pytest tests/unit/test_ai_content_service.py -v

# Run with coverage
pytest tests/unit/test_ai_content_service.py --cov=src.core.services --cov-report=html
```

### Test Coverage

The test suite includes:
- ✅ Service initialization with/without API key
- ✅ Successful content generation (home and city)
- ✅ Error handling (empty responses, API errors)
- ✅ Prompt building and context injection
- ✅ Cache hit/miss scenarios
- ✅ Cache expiration and invalidation
- ✅ Statistics and usage reporting
- ✅ Custom configuration

### Mock Testing

Tests use mocked OpenAI responses to avoid API costs:

```python
@pytest.fixture
def mock_openai_response(self):
    response = Mock()
    response.choices = [Mock()]
    response.choices[0].message = Mock()
    response.choices[0].message.content = """<section>...</section>"""
    return response
```

---

## Troubleshooting

### AI Content Not Generating

**Symptom**: Content falls back to templates even with API key configured

**Checklist**:
1. ✅ Check `.env` file has `OPENAI_API_KEY` set
2. ✅ Verify API key is valid (test at platform.openai.com)
3. ✅ Ensure `AI_CONTENT_ENABLED=true` in `.env`
4. ✅ Check `openai` package is installed: `pip install openai`
5. ✅ Review logs for error messages

### Cache Not Working

**Symptom**: Every request generates new content (no cache hits)

**Checklist**:
1. ✅ Verify `AI_CONTENT_CACHE_ENABLED=true` in `.env`
2. ✅ Check `.cache/ai_content/` directory exists
3. ✅ Ensure context is consistent between requests
4. ✅ Review cache statistics: `cache.get_stats()`

### API Rate Limits

**Symptom**: Errors about rate limits

**Solutions**:
- Reduce number of simultaneous requests
- Increase cache TTL to reduce API calls
- Upgrade OpenAI account tier
- Add retry logic with exponential backoff

### Content Quality Issues

**Symptom**: Generated content doesn't meet expectations

**Solutions**:
- Customize prompts in `_build_*_prompt()` methods
- Adjust temperature (lower = more focused, higher = more creative)
- Increase max_tokens for longer content
- Add more business context to config
- Use gpt-4 for higher quality (higher cost)

---

## Security Best Practices

### API Key Management

- ✅ **DO**: Store API keys in `.env` file
- ✅ **DO**: Add `.env` to `.gitignore`
- ✅ **DO**: Use environment-specific keys (dev, staging, prod)
- ✅ **DO**: Rotate keys periodically
- ❌ **DON'T**: Commit API keys to version control
- ❌ **DON'T**: Share keys in chat/email
- ❌ **DON'T**: Use production keys in development

### Content Validation

Always validate AI-generated content before deployment:
- Check for inappropriate content
- Verify HTML is valid and safe
- Review for accuracy and brand alignment
- Test rendering in browsers

---

## Future Enhancements

### Planned Features

1. **Multi-Language Support**
   - Automatic translation of content
   - Language-specific prompts
   - Localized SEO optimization

2. **Content Variation**
   - Generate multiple versions (A/B testing)
   - Different tone/style options
   - Industry-specific templates

3. **Advanced Caching**
   - Redis/Memcached integration
   - Distributed caching for multi-instance deployments
   - Cache warming strategies

4. **Analytics Integration**
   - Track content performance
   - A/B test AI vs template content
   - Cost analytics and optimization

5. **Content Review Workflow**
   - Admin approval before publishing
   - Content diff visualization
   - Version history and rollback

---

## FAQ

**Q: How much does AI content generation cost?**
A: Using gpt-4o-mini (default), approximately $0.0007 per home page and $0.0006 per city page. With caching enabled, subsequent requests are free.

**Q: Can I use my own AI model or API?**
A: Yes, extend the `AIContentService` class and override the `_call_openai()` method to integrate with other APIs.

**Q: Does AI-generated content replace templates completely?**
A: No, templates remain as fallback. You can disable AI anytime by setting `AI_CONTENT_ENABLED=false`.

**Q: How do I know if AI is being used?**
A: Check logs for messages like "Generating content with AI" or "Using cached AI-generated content".

**Q: Can I manually edit AI-generated content?**
A: Yes, after generation you can edit the HTML files directly. Future AI regenerations will overwrite unless cached.

**Q: Is my business data sent to OpenAI?**
A: Yes, business context (name, industry, services) is sent in prompts. Review OpenAI's privacy policy and data usage terms.

---

## Support & Contributing

### Getting Help

- 📚 Review this documentation
- 🐛 Check logs for error messages
- 💬 Open an issue on GitHub
- 📧 Contact support team

### Contributing

Contributions welcome! Areas of interest:
- Additional AI providers (Anthropic Claude, Google Gemini)
- Prompt optimization
- Cost reduction strategies
- Content quality improvements

---

**Last Updated**: 2025-10-19
**Version**: 1.00
**Maintainer**: Rank Rocket Co
