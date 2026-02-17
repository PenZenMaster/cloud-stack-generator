"""
Module/Script Name: SEO Analyzer
Path: src/core/seo/analyzer.py

Description:
Main SEO analyzer orchestrator that coordinates content analysis, meta analysis, and scoring.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial SEO analyzer
"""

from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

from .llm.provider import LLMProvider, ModelPreset
from .llm.claude_provider import ClaudeProvider
from .analyzers.content_analyzer import ContentAnalyzer, ContentAnalysisResult
from .analyzers.meta_analyzer import MetaAnalyzer, MetaAnalysisResult
from .analyzers.scoring_engine import SEOScore, ScoringEngine, SEORecommendation
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class SEOAnalysisResult:
    """Complete SEO analysis result"""
    overall_score: SEOScore
    content_analysis: ContentAnalysisResult
    meta_analysis: MetaAnalysisResult

    url: str
    model_used: str
    cost_estimate: float


class SEOAnalyzer:
    """
    Main SEO analyzer that coordinates all analysis components.

    Usage:
        analyzer = SEOAnalyzer(claude_api_key="...")
        result = analyzer.analyze_file(Path("output/index.html"))
        print(f"SEO Score: {result.overall_score.overall}/100")
    """

    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        claude_api_key: Optional[str] = None,
        model_preset: ModelPreset = ModelPreset.BALANCED
    ):
        """
        Initialize SEO analyzer.

        Args:
            llm_provider: Pre-configured LLM provider (optional)
            claude_api_key: Claude API key (if llm_provider not provided)
            model_preset: Model quality/cost preset

        Raises:
            ValueError: If neither llm_provider nor claude_api_key provided
        """
        if llm_provider:
            self.llm = llm_provider
        elif claude_api_key:
            self.llm = ClaudeProvider(claude_api_key, model_preset)
        else:
            raise ValueError("Either llm_provider or claude_api_key must be provided")

        self.content_analyzer = ContentAnalyzer(self.llm)
        self.meta_analyzer = MetaAnalyzer(self.llm)
        self.scoring_engine = ScoringEngine()

        logger.info(
            f"SEO Analyzer initialized with {self.llm.provider_name}",
            extra={"extra_fields": {"model": self.llm._model}}
        )

    def analyze_file(
        self,
        html_file: Path,
        target_keywords: Optional[List[str]] = None
    ) -> SEOAnalysisResult:
        """
        Analyze HTML file for SEO.

        Args:
            html_file: Path to HTML file
            target_keywords: Optional target keywords

        Returns:
            SEOAnalysisResult with complete analysis
        """
        if not html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {html_file}")

        logger.info(f"Starting SEO analysis: {html_file}")

        # Run content analysis
        logger.info("Analyzing content...")
        content_result = self.content_analyzer.analyze_file(html_file, target_keywords)

        # Run meta analysis
        logger.info("Analyzing meta tags...")
        meta_result = self.meta_analyzer.analyze_file(html_file, target_keywords)

        # Calculate overall score
        logger.info("Calculating overall score...")
        overall_score = self._calculate_overall_score(content_result, meta_result)

        # Get model info
        model_info = self.llm.get_model_info()

        result = SEOAnalysisResult(
            overall_score=overall_score,
            content_analysis=content_result,
            meta_analysis=meta_result,
            url=str(html_file),
            model_used=model_info["model"],
            cost_estimate=0.0  # Will be updated with actual costs
        )

        logger.info(
            f"Analysis complete. Score: {overall_score.overall}/100 ({overall_score.get_grade()})",
            extra={"extra_fields": {
                "content_score": content_result.overall_score,
                "meta_score": meta_result.overall_score
            }}
        )

        return result

    def analyze_directory(
        self,
        directory: Path,
        target_keywords: Optional[List[str]] = None,
        file_pattern: str = "*.html"
    ) -> List[SEOAnalysisResult]:
        """
        Analyze all HTML files in directory.

        Args:
            directory: Directory path
            target_keywords: Optional target keywords
            file_pattern: File pattern (default: *.html)

        Returns:
            List of SEOAnalysisResult
        """
        if not directory.exists() or not directory.is_dir():
            raise NotADirectoryError(f"Directory not found: {directory}")

        html_files = list(directory.glob(file_pattern))
        logger.info(f"Found {len(html_files)} HTML files in {directory}")

        results = []
        for html_file in html_files:
            try:
                result = self.analyze_file(html_file, target_keywords)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to analyze {html_file}: {str(e)}")

        return results

    def _calculate_overall_score(
        self,
        content_result: ContentAnalysisResult,
        meta_result: MetaAnalysisResult
    ) -> SEOScore:
        """Calculate overall SEO score"""
        # Get category scores
        content_score = content_result.overall_score
        heading_score = content_result.category_scores.get("heading_structure", 0)
        meta_score = meta_result.overall_score
        linking_score = (
            content_result.category_scores.get("internal_linking", 0) +
            content_result.category_scores.get("external_linking", 0)
        ) // 2

        # Calculate overall
        overall = self.scoring_engine.calculate_score(
            content_score=content_score,
            heading_score=heading_score,
            meta_score=meta_score,
            linking_score=linking_score,
            technical_score=70  # Default technical score
        )

        # Combine recommendations
        all_recommendations = (
            content_result.recommendations +
            meta_result.recommendations
        )

        # Combine strengths/weaknesses
        all_strengths = content_result.strengths
        all_weaknesses = content_result.weaknesses

        return SEOScore(
            overall=overall,
            content_quality=content_score,
            heading_structure=heading_score,
            meta_tags=meta_score,
            internal_linking=linking_score,
            technical=70,
            recommendations=all_recommendations,
            strengths=all_strengths,
            weaknesses=all_weaknesses
        )
