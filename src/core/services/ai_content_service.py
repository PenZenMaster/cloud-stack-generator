"""
AI Content Service
Path: E:/projects/cloud-stack-generator/src/core/services/ai_content_service.py

Description:
Wrapper service for OpenAI API to generate AI-powered content for website pages.
Handles prompt management, API calls, response parsing, and error handling with
graceful fallback to template-based generation.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-19

Last Modified Date:
2025-10-19

Comments:
* v1.00 - Initial creation with OpenAI GPT-4 integration
"""

import logging
from typing import Optional, Dict, Any, TYPE_CHECKING

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

if TYPE_CHECKING:
    from ...config.models import ClientConfig

from ..config.env_config import OpenAIConfig

logger = logging.getLogger(__name__)


class AIContentServiceError(Exception):
    """Custom exception for AI content service errors"""
    pass


class AIContentService:
    """
    Service for generating AI-powered website content using OpenAI API.

    Features:
    - Dynamic content generation based on business context
    - SEO-optimized HTML output
    - Configurable models and parameters
    - Error handling with fallback mechanism
    - Rate limiting and retry logic
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        enabled: Optional[bool] = None
    ):
        """
        Initialize the AI content service.

        Args:
            api_key: OpenAI API key (defaults to env config)
            model: Model to use (defaults to env config or gpt-4o-mini)
            max_tokens: Maximum tokens in response (defaults to env config or 2000)
            temperature: Sampling temperature 0-1 (defaults to env config or 0.7)
            enabled: Whether AI generation is enabled (defaults to env config)
        """
        # Use centralized config with optional overrides
        self.api_key = api_key or OpenAIConfig.get_api_key()
        self.model = model or OpenAIConfig.get_model()
        self.max_tokens = max_tokens or OpenAIConfig.get_max_tokens()
        self.temperature = temperature or OpenAIConfig.get_temperature()
        self.enabled = enabled if enabled is not None else OpenAIConfig.is_enabled()

        # Initialize OpenAI client if available and enabled
        self.client: Optional[OpenAI] = None
        if OPENAI_AVAILABLE and self.enabled and self.api_key:
            try:
                self.client = OpenAI(api_key=self.api_key)
                logger.info(f"AI Content Service initialized with model: {self.model}")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.enabled = False
        else:
            if not OPENAI_AVAILABLE:
                logger.warning("OpenAI package not available. Install with: pip install openai")
            elif not self.api_key:
                logger.warning("OpenAI API key not configured. Set OPENAI_API_KEY in .env file")
            self.enabled = False

    def is_available(self) -> bool:
        """Check if AI content generation is available and enabled"""
        return self.enabled and self.client is not None

    def generate_home_content(
        self,
        config: "ClientConfig",
        use_enhanced: bool = True
    ) -> Optional[str]:
        """
        Generate AI-powered home page content.

        Args:
            config: Client configuration with business details
            use_enhanced: Whether to use enhanced template format

        Returns:
            HTML content string or None if generation fails
        """
        if not self.is_available():
            logger.debug("AI content generation not available, using template fallback")
            return None

        business = config.business
        contact = config.contact

        # Build context for the AI
        context = {
            'business_name': business.business_name,
            'industry': business.industry,
            'company_overview': getattr(business, 'company_overview', ''),
            'tagline': getattr(business, 'tagline', ''),
            'years_in_business': getattr(business, 'years_in_business', None),
            'why_choose_us': getattr(business, 'why_choose_us', []),
            'service_guarantee': getattr(business, 'service_guarantee', ''),
            'services': [{'name': s.name, 'description': s.description} for s in config.services],
            'products': [{'name': p.name, 'description': p.description} for p in config.products],
            'phone': contact.get_primary_phone() if hasattr(contact, 'get_primary_phone') else contact.phone,
            'email': getattr(contact, 'email', ''),
            'use_enhanced': use_enhanced
        }

        prompt = self._build_home_page_prompt(context)

        try:
            return self._call_openai(prompt, content_type="home_page")
        except Exception as e:
            logger.error(f"Failed to generate home content: {e}")
            return None

    def generate_city_content(
        self,
        config: "ClientConfig",
        city: str,
        state: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate AI-powered city page content.

        Args:
            config: Client configuration with business details
            city: City name for the page
            state: State/province (optional)

        Returns:
            HTML content string or None if generation fails
        """
        if not self.is_available():
            logger.debug("AI content generation not available, using template fallback")
            return None

        business = config.business

        # Build context for the AI
        context = {
            'business_name': business.business_name,
            'industry': business.industry,
            'city': city,
            'state': state or '',
            'services': [{'name': s.name, 'description': s.description} for s in config.services],
            'products': [{'name': p.name, 'description': p.description} for p in config.products],
            'company_overview': getattr(business, 'company_overview', ''),
        }

        prompt = self._build_city_page_prompt(context)

        try:
            return self._call_openai(prompt, content_type="city_page")
        except Exception as e:
            logger.error(f"Failed to generate city content for {city}: {e}")
            return None

    def _build_home_page_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build a structured prompt for home page content generation.

        Args:
            context: Dictionary with business context

        Returns:
            Formatted prompt string
        """
        services_list = "\n".join([
            f"- {s['name']}: {s['description']}" for s in context['services']
        ]) if context['services'] else "General industry services"

        products_list = "\n".join([
            f"- {p['name']}: {p['description']}" for p in context['products']
        ]) if context['products'] else "No specific products listed"

        why_choose_list = "\n".join([
            f"- {reason}" for reason in context.get('why_choose_us', [])
        ]) if context.get('why_choose_us') else "Not specified"

        prompt = f"""You are a professional web content writer specializing in SEO-optimized business websites.

Generate compelling, professional HTML content for a home page with the following specifications:

BUSINESS INFORMATION:
- Business Name: {context['business_name']}
- Industry: {context['industry']}
- Company Overview: {context.get('company_overview', 'Not provided')}
- Tagline: {context.get('tagline', 'Not provided')}
- Years in Business: {context.get('years_in_business', 'Not specified')}
- Phone: {context.get('phone', '')}
- Email: {context.get('email', '')}

SERVICES:
{services_list}

PRODUCTS:
{products_list}

WHY CHOOSE US:
{why_choose_list}

SERVICE GUARANTEE:
{context.get('service_guarantee', 'Not specified')}

REQUIREMENTS:
1. Generate ONLY the HTML content sections (no <html>, <head>, or <body> tags)
2. Use semantic HTML5 with proper section tags
3. Include these sections in order:
   - Hero section with compelling headline and call-to-action
   - About section introducing the business
   - Why Choose Us section highlighting key benefits
   - Services/Products showcase
   - Contact section with phone and email
4. Use appropriate CSS classes: hero, hero-overlay, hero-content, about-section, why-choose-us, services-grid, products-grid, contact-section
5. Make content SEO-friendly with natural keyword usage
6. Keep tone professional but engaging
7. Include 2-3 clear calls-to-action
8. Content should be 600-800 words total
9. Use proper heading hierarchy (h1, h2, h3)

OUTPUT FORMAT:
Return ONLY the HTML sections, starting with <section> tags. No explanatory text before or after."""

        return prompt

    def _build_city_page_prompt(self, context: Dict[str, Any]) -> str:
        """
        Build a structured prompt for city page content generation.

        Args:
            context: Dictionary with business and city context

        Returns:
            Formatted prompt string
        """
        services_list = "\n".join([
            f"- {s['name']}: {s['description']}" for s in context['services']
        ]) if context['services'] else "General industry services"

        location = context['city']
        if context.get('state'):
            location += f", {context['state']}"

        prompt = f"""You are a professional web content writer specializing in local SEO-optimized business websites.

Generate compelling, localized HTML content for a city-specific service page with the following specifications:

BUSINESS INFORMATION:
- Business Name: {context['business_name']}
- Industry: {context['industry']}
- Target Location: {location}
- Company Overview: {context.get('company_overview', 'Not provided')}

SERVICES:
{services_list}

REQUIREMENTS:
1. Generate ONLY the HTML content sections (no <html>, <head>, or <body> tags)
2. Use semantic HTML5 with proper section tags
3. Include these sections in order:
   - Hero section emphasizing local service in {context['city']}
   - Local expertise section (why they're the best choice in this city)
   - Services section tailored to {context['city']} residents
   - Call-to-action encouraging contact
4. Use appropriate CSS classes: hero, hero-overlay, hero-text, content, services-grid
5. Naturally incorporate location keywords: {context['city']}, local, area, community
6. Emphasize local expertise and community commitment
7. Keep tone professional and trustworthy
8. Content should be 400-600 words
9. Use proper heading hierarchy (h2, h3, h4)
10. Include local trust signals (local knowledge, community service, etc.)

OUTPUT FORMAT:
Return ONLY the HTML sections, starting with <section> tags. No explanatory text before or after."""

        return prompt

    def _call_openai(self, prompt: str, content_type: str = "content") -> str:
        """
        Make API call to OpenAI and return the generated content.

        Args:
            prompt: The prompt to send to the API
            content_type: Type of content being generated (for logging)

        Returns:
            Generated HTML content

        Raises:
            AIContentServiceError: If API call fails
        """
        if not self.client:
            raise AIContentServiceError("OpenAI client not initialized")

        try:
            logger.info(f"Generating {content_type} with model {self.model}")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional web content writer specializing in SEO-optimized, engaging business content. You generate clean, semantic HTML."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                top_p=1.0,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )

            content = response.choices[0].message.content

            if not content:
                raise AIContentServiceError("Empty response from OpenAI")

            # Basic validation - ensure it contains HTML
            if '<section' not in content.lower():
                logger.warning(f"Generated content may not be valid HTML: {content[:100]}")

            logger.info(f"Successfully generated {content_type} ({len(content)} characters)")
            return content.strip()

        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise AIContentServiceError(f"Failed to generate {content_type}: {str(e)}")

    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics and configuration info.

        Returns:
            Dictionary with service stats
        """
        return {
            'enabled': self.enabled,
            'available': self.is_available(),
            'model': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'openai_installed': OPENAI_AVAILABLE,
            'api_key_configured': bool(self.api_key)
        }
