"""
Module/Script Name: Meta Tag Analyzer
Path: src/core/seo/analyzers/meta_analyzer.py

Description:
Analyzes meta tags for SEO optimization.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial meta analyzer
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
import json

from bs4 import BeautifulSoup

from ..llm.provider import LLMProvider
from .scoring_engine import SEORecommendation, Priority
from ...utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class MetaAnalysisResult:
    """Result of meta tag analysis"""
    title_score: int
    description_score: int
    overall_score: int
    recommendations: List[SEORecommendation]

    title: str = ""
    title_length: int = 0
    description: str = ""
    description_length: int = 0
    keywords: List[str] = None

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []


class MetaAnalyzer:
    """Analyzes meta tags for SEO"""

    # Optimal lengths
    TITLE_MIN = 50
    TITLE_MAX = 60
    DESC_MIN = 150
    DESC_MAX = 160

    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize meta analyzer.

        Args:
            llm_provider: LLM provider for analysis
        """
        self.llm = llm_provider
        logger.info(f"MetaAnalyzer initialized with {llm_provider.provider_name}")

    def analyze_file(
        self,
        html_file: Path,
        target_keywords: Optional[List[str]] = None
    ) -> MetaAnalysisResult:
        """
        Analyze meta tags in HTML file.

        Args:
            html_file: Path to HTML file
            target_keywords: Optional target keywords

        Returns:
            MetaAnalysisResult
        """
        html_content = html_file.read_text(encoding='utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')

        return self.analyze_html(soup, target_keywords)

    def analyze_html(
        self,
        soup: BeautifulSoup,
        target_keywords: Optional[List[str]] = None
    ) -> MetaAnalysisResult:
        """
        Analyze meta tags in parsed HTML.

        Args:
            soup: BeautifulSoup parsed HTML
            target_keywords: Optional target keywords

        Returns:
            MetaAnalysisResult
        """
        # Extract meta tags
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ""

        desc_tag = soup.find('meta', attrs={'name': 'description'})
        description = desc_tag.get('content', '') if desc_tag else ""

        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        keywords = keywords_tag.get('content', '').split(',') if keywords_tag else []
        keywords = [k.strip() for k in keywords if k.strip()]

        logger.info(f"Analyzing meta tags: title={len(title)} chars, desc={len(description)} chars")

        # Get LLM analysis
        llm_response = self.llm.analyze_meta_tags(
            title, description, keywords, target_keywords
        )

        # Basic scores
        title_score = self._score_title(title, target_keywords or [])
        desc_score = self._score_description(description, target_keywords or [])
        overall_score = int((title_score + desc_score) / 2)

        recommendations = []

        if llm_response.success:
            try:
                analysis_data = self._extract_json(llm_response.content)
                recommendations = self._parse_recommendations(analysis_data)
                # Use LLM scores if available
                title_score = analysis_data.get("title_analysis", {}).get("score", title_score)
                desc_score = analysis_data.get("description_analysis", {}).get("score", desc_score)
                overall_score = analysis_data.get("overall_score", overall_score)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse LLM meta analysis JSON: {e}")

        # Add basic recommendations if LLM didn't provide any
        if not recommendations:
            recommendations = self._generate_basic_recommendations(
                title, description, target_keywords or []
            )

        return MetaAnalysisResult(
            title_score=title_score,
            description_score=desc_score,
            overall_score=overall_score,
            recommendations=recommendations,
            title=title,
            title_length=len(title),
            description=description,
            description_length=len(description),
            keywords=keywords,
        )

    def _extract_json(self, content: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response, handling various formats.

        Tries multiple strategies:
        1. Direct JSON parse
        2. Extract from markdown code fences
        3. Find first { to last }

        Args:
            content: LLM response content

        Returns:
            Parsed JSON dict

        Raises:
            ValueError: If JSON cannot be extracted
        """
        # Strategy 1: Direct parse
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from code fences
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            if end > start:
                try:
                    return json.loads(content[start:end].strip())
                except json.JSONDecodeError:
                    pass

        if "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            if end > start:
                try:
                    return json.loads(content[start:end].strip())
                except json.JSONDecodeError:
                    pass

        # Strategy 3: Find first { to last }
        first_brace = content.find("{")
        last_brace = content.rfind("}")
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            try:
                return json.loads(content[first_brace:last_brace + 1])
            except json.JSONDecodeError:
                pass

        raise ValueError("Could not extract valid JSON from LLM response")

    def _score_title(self, title: str, target_keywords: List[str]) -> int:
        """Score title tag (0-100)"""
        score = 100
        length = len(title)

        # Length check
        if length < self.TITLE_MIN:
            score -= 20
        elif length > self.TITLE_MAX:
            score -= 10

        # Keyword check
        if target_keywords:
            title_lower = title.lower()
            has_keyword = any(kw.lower() in title_lower for kw in target_keywords)
            if not has_keyword:
                score -= 30

        # Empty title
        if not title:
            score = 0

        return max(0, score)

    def _score_description(self, description: str, target_keywords: List[str]) -> int:
        """Score meta description (0-100)"""
        score = 100
        length = len(description)

        # Length check
        if length < self.DESC_MIN:
            score -= 20
        elif length > self.DESC_MAX:
            score -= 10

        # Keyword check
        if target_keywords:
            desc_lower = description.lower()
            has_keyword = any(kw.lower() in desc_lower for kw in target_keywords)
            if not has_keyword:
                score -= 30

        # Empty description
        if not description:
            score = 0

        return max(0, score)

    def _parse_recommendations(self, analysis_data: Dict[str, Any]) -> List[SEORecommendation]:
        """Parse recommendations from LLM analysis"""
        recommendations = []
        for rec in analysis_data.get("recommendations", []):
            if isinstance(rec, dict):
                recommendations.append(SEORecommendation(
                    priority=Priority(rec.get("priority", "medium")),
                    category="meta_tags",
                    issue=rec.get("issue", ""),
                    recommendation=rec.get("recommendation", ""),
                    impact=rec.get("impact", ""),
                    effort=rec.get("effort", "low")
                ))
        return recommendations

    def _generate_basic_recommendations(
        self,
        title: str,
        description: str,
        target_keywords: List[str]
    ) -> List[SEORecommendation]:
        """Generate basic recommendations without LLM"""
        recommendations = []

        # Title recommendations
        if not title:
            recommendations.append(SEORecommendation(
                priority=Priority.HIGH,
                category="meta_tags",
                issue="Missing title tag",
                recommendation="Add a descriptive title tag (50-60 characters)",
                impact="Critical for SEO and click-through rates",
                effort="low"
            ))
        elif len(title) < self.TITLE_MIN:
            recommendations.append(SEORecommendation(
                priority=Priority.MEDIUM,
                category="meta_tags",
                issue=f"Title too short ({len(title)} chars)",
                recommendation=f"Expand title to {self.TITLE_MIN}-{self.TITLE_MAX} characters",
                impact="Short titles may not be descriptive enough",
                effort="low"
            ))
        elif len(title) > self.TITLE_MAX:
            recommendations.append(SEORecommendation(
                priority=Priority.MEDIUM,
                category="meta_tags",
                issue=f"Title too long ({len(title)} chars)",
                recommendation=f"Shorten title to {self.TITLE_MIN}-{self.TITLE_MAX} characters",
                impact="Long titles get truncated in search results",
                effort="low"
            ))

        # Description recommendations
        if not description:
            recommendations.append(SEORecommendation(
                priority=Priority.HIGH,
                category="meta_tags",
                issue="Missing meta description",
                recommendation="Add a compelling meta description (150-160 characters)",
                impact="Important for click-through rates",
                effort="low"
            ))
        elif len(description) < self.DESC_MIN:
            recommendations.append(SEORecommendation(
                priority=Priority.MEDIUM,
                category="meta_tags",
                issue=f"Description too short ({len(description)} chars)",
                recommendation=f"Expand description to {self.DESC_MIN}-{self.DESC_MAX} characters",
                impact="Short descriptions don't provide enough information",
                effort="low"
            ))
        elif len(description) > self.DESC_MAX:
            recommendations.append(SEORecommendation(
                priority=Priority.LOW,
                category="meta_tags",
                issue=f"Description too long ({len(description)} chars)",
                recommendation=f"Shorten description to {self.DESC_MIN}-{self.DESC_MAX} characters",
                impact="Long descriptions get truncated",
                effort="low"
            ))

        return recommendations
