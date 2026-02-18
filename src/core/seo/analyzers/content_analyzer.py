"""
Module/Script Name: Content Analyzer
Path: src/core/seo/analyzers/content_analyzer.py

Description:
Analyzes HTML content for SEO quality using LLM.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial content analyzer
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
class ContentAnalysisResult:
    """Result of content analysis"""
    overall_score: int
    category_scores: Dict[str, int]
    keyword_analysis: Dict[str, Any]
    recommendations: List[SEORecommendation]
    strengths: List[str]
    weaknesses: List[str]

    word_count: int = 0
    heading_count: Dict[str, int] = None
    link_count: Dict[str, int] = None

    def __post_init__(self):
        if self.heading_count is None:
            self.heading_count = {}
        if self.link_count is None:
            self.link_count = {}


class ContentAnalyzer:
    """Analyzes HTML content for SEO quality"""

    def __init__(self, llm_provider: LLMProvider):
        """
        Initialize content analyzer.

        Args:
            llm_provider: LLM provider for analysis
        """
        self.llm = llm_provider
        logger.info(f"ContentAnalyzer initialized with {llm_provider.provider_name}")

    def analyze_file(
        self,
        html_file: Path,
        target_keywords: Optional[List[str]] = None
    ) -> ContentAnalysisResult:
        """
        Analyze HTML file.

        Args:
            html_file: Path to HTML file
            target_keywords: Optional target keywords

        Returns:
            ContentAnalysisResult
        """
        html_content = html_file.read_text(encoding='utf-8')
        url = f"file://{html_file}"

        return self.analyze_content(html_content, url, target_keywords)

    def analyze_content(
        self,
        html_content: str,
        url: str,
        target_keywords: Optional[List[str]] = None
    ) -> ContentAnalysisResult:
        """
        Analyze HTML content.

        Args:
            html_content: HTML content
            url: Page URL
            target_keywords: Optional target keywords

        Returns:
            ContentAnalysisResult
        """
        logger.info(f"Analyzing content: {url}")

        # Parse HTML for basic metrics
        soup = BeautifulSoup(html_content, 'html.parser')
        basic_metrics = self._extract_basic_metrics(soup)

        # Get LLM analysis
        llm_response = self.llm.analyze_content(
            html_content,
            url,
            target_keywords,
            analysis_type="comprehensive"
        )

        if not llm_response.success:
            logger.error(f"LLM analysis failed: {llm_response.error}")
            # Return basic analysis without LLM
            return self._create_basic_result(basic_metrics)

        # Parse LLM response (JSON)
        try:
            analysis_data = self._extract_json(llm_response.content)
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}, using basic analysis")
            return self._create_basic_result(basic_metrics)

        # Convert to ContentAnalysisResult
        recommendations = [
            SEORecommendation(
                priority=Priority(rec.get("priority", "medium")),
                category=rec.get("category", "general"),
                issue=rec.get("issue", ""),
                recommendation=rec.get("recommendation", ""),
                impact=rec.get("impact", ""),
                effort=rec.get("effort", "medium")
            )
            for rec in analysis_data.get("recommendations", [])
        ]

        return ContentAnalysisResult(
            overall_score=analysis_data.get("overall_score", 0),
            category_scores=analysis_data.get("category_scores", {}),
            keyword_analysis=analysis_data.get("keyword_analysis", {}),
            recommendations=recommendations,
            strengths=analysis_data.get("strengths", []),
            weaknesses=analysis_data.get("weaknesses", []),
            word_count=basic_metrics["word_count"],
            heading_count=basic_metrics["heading_count"],
            link_count=basic_metrics["link_count"],
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

    def _extract_basic_metrics(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract basic SEO metrics from HTML"""
        # Word count
        text = soup.get_text(strip=True)
        word_count = len(text.split())

        # Heading count
        heading_count = {}
        for level in range(1, 7):
            headings = soup.find_all(f'h{level}')
            heading_count[f'h{level}'] = len(headings)

        # Link count
        internal_links = 0
        external_links = 0
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('http'):
                external_links += 1
            else:
                internal_links += 1

        link_count = {
            "internal": internal_links,
            "external": external_links,
            "total": internal_links + external_links
        }

        return {
            "word_count": word_count,
            "heading_count": heading_count,
            "link_count": link_count,
        }

    def _create_basic_result(self, metrics: Dict[str, Any]) -> ContentAnalysisResult:
        """Create basic result without LLM analysis"""
        return ContentAnalysisResult(
            overall_score=50,  # Neutral score
            category_scores={},
            keyword_analysis={},
            recommendations=[],
            strengths=[],
            weaknesses=["LLM analysis unavailable"],
            word_count=metrics["word_count"],
            heading_count=metrics["heading_count"],
            link_count=metrics["link_count"],
        )
