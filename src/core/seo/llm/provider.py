"""
Module/Script Name: LLM Provider Interface
Path: src/core/seo/llm/provider.py

Description:
Abstract base class for LLM providers used in SEO analysis.
Provides unified interface for Claude, OpenAI, and future providers.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial LLM provider interface
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

from ...utils.logger import get_logger

logger = get_logger(__name__)


class ModelPreset(Enum):
    """LLM model quality/cost presets"""
    FAST = "fast"          # Fastest, cheapest (Claude Haiku, GPT-3.5-turbo)
    BALANCED = "balanced"  # Good balance (Claude Sonnet, GPT-4o-mini)
    THOROUGH = "thorough"  # Best quality (Claude Opus, GPT-4o)


@dataclass
class LLMResponse:
    """LLM provider response"""
    content: str
    model: str
    tokens_used: int
    cost_estimate: float  # USD
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.

    Provides unified interface for different LLM services (Claude, OpenAI, etc.)
    with model selection and cost control.
    """

    def __init__(
        self,
        api_key: str,
        model_preset: ModelPreset = ModelPreset.BALANCED,
        custom_model: Optional[str] = None
    ):
        """
        Initialize LLM provider.

        Args:
            api_key: API key for the LLM service
            model_preset: Quality/cost preset (fast/balanced/thorough)
            custom_model: Custom model identifier (overrides preset)
        """
        self.api_key = api_key
        self.model_preset = model_preset
        self.custom_model = custom_model
        self._model = custom_model or self._get_model_from_preset(model_preset)

        logger.info(
            f"Initialized {self.provider_name} provider",
            extra={"extra_fields": {
                "model": self._model,
                "preset": model_preset.value
            }}
        )

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Get provider name (e.g., 'Claude', 'OpenAI')"""
        pass

    @abstractmethod
    def _get_model_from_preset(self, preset: ModelPreset) -> str:
        """
        Get model identifier for preset.

        Args:
            preset: Model quality/cost preset

        Returns:
            Model identifier string
        """
        pass

    @abstractmethod
    def analyze_content(
        self,
        html_content: str,
        url: str,
        target_keywords: Optional[List[str]] = None,
        analysis_type: str = "comprehensive"
    ) -> LLMResponse:
        """
        Analyze HTML content for SEO quality.

        Args:
            html_content: HTML content to analyze
            url: Page URL
            target_keywords: Optional list of target keywords
            analysis_type: Type of analysis (comprehensive, quick, competitive)

        Returns:
            LLMResponse with analysis results
        """
        pass

    @abstractmethod
    def analyze_meta_tags(
        self,
        title: str,
        description: str,
        keywords: Optional[List[str]] = None,
        target_keywords: Optional[List[str]] = None
    ) -> LLMResponse:
        """
        Analyze meta tags for SEO optimization.

        Args:
            title: Page title tag
            description: Meta description
            keywords: Meta keywords (deprecated but sometimes used)
            target_keywords: Target keywords for optimization

        Returns:
            LLMResponse with optimization recommendations
        """
        pass

    @abstractmethod
    def generate_recommendations(
        self,
        analysis_data: Dict[str, Any],
        priority_level: str = "all"
    ) -> LLMResponse:
        """
        Generate actionable SEO recommendations.

        Args:
            analysis_data: Dictionary with analysis results
            priority_level: Filter by priority (high/medium/low/all)

        Returns:
            LLMResponse with prioritized recommendations
        """
        pass

    def get_cost_per_1k_tokens(self) -> tuple[float, float]:
        """
        Get cost per 1000 tokens (input, output).

        Returns:
            Tuple of (input_cost, output_cost) in USD
        """
        costs = self._get_pricing()
        return costs.get(self._model, (0.0, 0.0))

    @abstractmethod
    def _get_pricing(self) -> Dict[str, tuple[float, float]]:
        """
        Get pricing information for all models.

        Returns:
            Dictionary mapping model to (input_cost, output_cost) per 1k tokens
        """
        pass

    def estimate_cost(
        self,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """
        Estimate cost for token usage.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens

        Returns:
            Estimated cost in USD
        """
        input_cost, output_cost = self.get_cost_per_1k_tokens()
        return (
            (input_tokens / 1000) * input_cost +
            (output_tokens / 1000) * output_cost
        )

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about current model.

        Returns:
            Dictionary with model information
        """
        input_cost, output_cost = self.get_cost_per_1k_tokens()
        return {
            "provider": self.provider_name,
            "model": self._model,
            "preset": self.model_preset.value,
            "input_cost_per_1k": input_cost,
            "output_cost_per_1k": output_cost,
        }
