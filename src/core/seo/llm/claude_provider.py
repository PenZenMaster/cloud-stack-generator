"""
Module/Script Name: Claude LLM Provider
Path: src/core/seo/llm/claude_provider.py

Description:
Anthropic Claude provider for SEO analysis.
Supports Claude Sonnet 4.5, Claude Opus 4.6, and Claude Haiku 4.5.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial Claude provider implementation
"""

from typing import Optional, List, Dict, Any
import json

from .provider import LLMProvider, LLMResponse, ModelPreset
from ...utils.logger import get_logger

logger = get_logger(__name__)

try:
    from anthropic import Anthropic, AnthropicError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic library not installed. Install with: pip install anthropic")


class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude provider for SEO analysis.

    Supports multiple Claude models with varying cost/quality tradeoffs:
    - Claude Sonnet 4.5: Best balance of speed and quality
    - Claude Opus 4.6: Highest quality, slower, more expensive
    - Claude Haiku 4.5: Fastest, cheapest, good for simple tasks
    """

    # Model identifiers (updated Feb 2026)
    MODELS = {
        ModelPreset.FAST: "claude-haiku-4-5-20251001",
        ModelPreset.BALANCED: "claude-sonnet-4-5-20250929",
        ModelPreset.THOROUGH: "claude-opus-4-6",
    }

    # Pricing per 1k tokens (input, output) in USD as of Feb 2026
    PRICING = {
        "claude-haiku-4-5-20251001": (0.00025, 0.00125),
        "claude-sonnet-4-5-20250929": (0.003, 0.015),
        "claude-opus-4-6": (0.015, 0.075),
    }

    def __init__(
        self,
        api_key: str,
        model_preset: ModelPreset = ModelPreset.BALANCED,
        custom_model: Optional[str] = None
    ):
        """
        Initialize Claude provider.

        Args:
            api_key: Anthropic API key
            model_preset: Quality/cost preset
            custom_model: Custom Claude model (overrides preset)

        Raises:
            ImportError: If anthropic library not installed
        """
        if not ANTHROPIC_AVAILABLE:
            raise ImportError(
                "anthropic library required. Install with: pip install anthropic"
            )

        super().__init__(api_key, model_preset, custom_model)
        self.client = Anthropic(api_key=api_key)

    @property
    def provider_name(self) -> str:
        """Get provider name"""
        return "Claude"

    def _get_model_from_preset(self, preset: ModelPreset) -> str:
        """Get Claude model for preset"""
        return self.MODELS.get(preset, self.MODELS[ModelPreset.BALANCED])

    def _get_pricing(self) -> Dict[str, tuple[float, float]]:
        """Get Claude pricing"""
        return self.PRICING

    def analyze_content(
        self,
        html_content: str,
        url: str,
        target_keywords: Optional[List[str]] = None,
        analysis_type: str = "comprehensive"
    ) -> LLMResponse:
        """
        Analyze HTML content using Claude.

        Args:
            html_content: HTML content to analyze
            url: Page URL
            target_keywords: Optional target keywords
            analysis_type: Type of analysis

        Returns:
            LLMResponse with analysis
        """
        try:
            # Build prompt
            prompt = self._build_content_analysis_prompt(
                html_content, url, target_keywords, analysis_type
            )

            # Call Claude API
            response = self.client.messages.create(
                model=self._model,
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract response
            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = self.estimate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            return LLMResponse(
                content=content,
                model=self._model,
                tokens_used=tokens_used,
                cost_estimate=cost,
                success=True,
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "stop_reason": response.stop_reason,
                }
            )

        except AnthropicError as e:
            logger.error(f"Claude API error: {str(e)}")
            return LLMResponse(
                content="",
                model=self._model,
                tokens_used=0,
                cost_estimate=0.0,
                success=False,
                error=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return LLMResponse(
                content="",
                model=self._model,
                tokens_used=0,
                cost_estimate=0.0,
                success=False,
                error=str(e)
            )

    def analyze_meta_tags(
        self,
        title: str,
        description: str,
        keywords: Optional[List[str]] = None,
        target_keywords: Optional[List[str]] = None
    ) -> LLMResponse:
        """
        Analyze meta tags using Claude.

        Args:
            title: Page title
            description: Meta description
            keywords: Meta keywords
            target_keywords: Target keywords

        Returns:
            LLMResponse with recommendations
        """
        try:
            prompt = self._build_meta_analysis_prompt(
                title, description, keywords, target_keywords
            )

            response = self.client.messages.create(
                model=self._model,
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = self.estimate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            return LLMResponse(
                content=content,
                model=self._model,
                tokens_used=tokens_used,
                cost_estimate=cost,
                success=True,
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            )

        except Exception as e:
            logger.error(f"Meta analysis error: {str(e)}")
            return LLMResponse(
                content="",
                model=self._model,
                tokens_used=0,
                cost_estimate=0.0,
                success=False,
                error=str(e)
            )

    def generate_recommendations(
        self,
        analysis_data: Dict[str, Any],
        priority_level: str = "all"
    ) -> LLMResponse:
        """
        Generate SEO recommendations using Claude.

        Args:
            analysis_data: Analysis results
            priority_level: Priority filter

        Returns:
            LLMResponse with recommendations
        """
        try:
            prompt = self._build_recommendations_prompt(analysis_data, priority_level)

            response = self.client.messages.create(
                model=self._model,
                max_tokens=3072,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            content = response.content[0].text
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost = self.estimate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens
            )

            return LLMResponse(
                content=content,
                model=self._model,
                tokens_used=tokens_used,
                cost_estimate=cost,
                success=True,
                metadata={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            )

        except Exception as e:
            logger.error(f"Recommendations error: {str(e)}")
            return LLMResponse(
                content="",
                model=self._model,
                tokens_used=0,
                cost_estimate=0.0,
                success=False,
                error=str(e)
            )

    def _build_content_analysis_prompt(
        self,
        html_content: str,
        url: str,
        target_keywords: Optional[List[str]],
        analysis_type: str
    ) -> str:
        """Build prompt for content analysis"""
        keywords_text = ""
        if target_keywords:
            keywords_text = f"\nTarget keywords: {', '.join(target_keywords)}"

        return f"""Analyze this HTML page for SEO quality and provide detailed recommendations.

URL: {url}
Analysis Type: {analysis_type}{keywords_text}

HTML Content:
{html_content[:50000]}  # Limit to ~50k chars

Please analyze:
1. **Content Quality**
   - Keyword density and distribution
   - Content length and depth
   - Readability and engagement
   - Topic relevance and authority signals

2. **Heading Structure**
   - H1-H6 hierarchy
   - Keyword usage in headings
   - Structural issues

3. **Internal Linking**
   - Link count and distribution
   - Anchor text optimization
   - Navigation structure

4. **External Links**
   - Quality and relevance
   - Authority signals
   - Nofollow/dofollow balance

5. **SEO Score**
   - Overall score (0-100)
   - Category scores
   - Key strengths and weaknesses

IMPORTANT: Respond with ONLY valid JSON. Do not include any explanatory text before or after the JSON.

Required JSON format:
{{
  "overall_score": 0-100,
  "category_scores": {{
    "content_quality": 0-100,
    "heading_structure": 0-100,
    "internal_linking": 0-100,
    "external_linking": 0-100
  }},
  "keyword_analysis": {{
    "primary_keywords": [...],
    "density": ...,
    "distribution": "..."
  }},
  "recommendations": [
    {{
      "priority": "high|medium|low",
      "category": "...",
      "issue": "...",
      "recommendation": "...",
      "impact": "..."
    }}
  ],
  "strengths": [...],
  "weaknesses": [...]
}}"""

    def _build_meta_analysis_prompt(
        self,
        title: str,
        description: str,
        keywords: Optional[List[str]],
        target_keywords: Optional[List[str]]
    ) -> str:
        """Build prompt for meta tag analysis"""
        keywords_text = f"\nMeta keywords: {', '.join(keywords)}" if keywords else ""
        target_text = f"\nTarget keywords: {', '.join(target_keywords)}" if target_keywords else ""

        return f"""Analyze these meta tags for SEO optimization:

Title: {title}
Description: {description}{keywords_text}{target_text}

Please evaluate:
1. **Title Tag**
   - Length (optimal: 50-60 chars)
   - Keyword placement
   - CTR optimization
   - Brand inclusion

2. **Meta Description**
   - Length (optimal: 150-160 chars)
   - Keyword inclusion
   - Call-to-action
   - Uniqueness

3. **Keyword Optimization**
   - Target keyword presence
   - Natural language
   - Relevance

IMPORTANT: Respond with ONLY valid JSON. Do not include any explanatory text before or after the JSON.

Required JSON format:
{{
  "title_analysis": {{
    "score": 0-100,
    "length": ...,
    "issues": [...],
    "suggestions": [...]
  }},
  "description_analysis": {{
    "score": 0-100,
    "length": ...,
    "issues": [...],
    "suggestions": [...]
  }},
  "overall_score": 0-100,
  "recommendations": [...]
}}"""

    def _build_recommendations_prompt(
        self,
        analysis_data: Dict[str, Any],
        priority_level: str
    ) -> str:
        """Build prompt for generating recommendations"""
        return f"""Based on this SEO analysis data, generate prioritized, actionable recommendations.

Analysis Data:
{json.dumps(analysis_data, indent=2)}

Priority Level: {priority_level}

Generate recommendations that are:
1. Specific and actionable
2. Prioritized by impact
3. Categorized by type
4. Include estimated effort
5. Explain expected impact

Provide response in JSON format:
{{
  "high_priority": [...],
  "medium_priority": [...],
  "low_priority": [...],
  "quick_wins": [...],
  "long_term": [...]
}}"""
