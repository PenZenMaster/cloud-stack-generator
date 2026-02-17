"""
Module/Script Name: SEO Scoring Engine
Path: src/core/seo/analyzers/scoring_engine.py

Description:
SEO scoring and recommendation prioritization engine.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial scoring engine
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum


class Priority(Enum):
    """Recommendation priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SEORecommendation:
    """Individual SEO recommendation"""
    priority: Priority
    category: str
    issue: str
    recommendation: str
    impact: str
    effort: str = "medium"  # low, medium, high

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "priority": self.priority.value,
            "category": self.category,
            "issue": self.issue,
            "recommendation": self.recommendation,
            "impact": self.impact,
            "effort": self.effort,
        }


@dataclass
class SEOScore:
    """SEO score with category breakdown"""
    overall: int  # 0-100
    content_quality: int = 0
    heading_structure: int = 0
    meta_tags: int = 0
    internal_linking: int = 0
    external_linking: int = 0
    technical: int = 0

    recommendations: List[SEORecommendation] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    def get_grade(self) -> str:
        """Get letter grade based on score"""
        if self.overall >= 90:
            return "A"
        elif self.overall >= 80:
            return "B"
        elif self.overall >= 70:
            return "C"
        elif self.overall >= 60:
            return "D"
        else:
            return "F"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "overall": self.overall,
            "grade": self.get_grade(),
            "categories": {
                "content_quality": self.content_quality,
                "heading_structure": self.heading_structure,
                "meta_tags": self.meta_tags,
                "internal_linking": self.internal_linking,
                "external_linking": self.external_linking,
                "technical": self.technical,
            },
            "recommendations": [r.to_dict() for r in self.recommendations],
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
        }


class ScoringEngine:
    """SEO scoring engine"""

    @staticmethod
    def calculate_score(
        content_score: int = 0,
        heading_score: int = 0,
        meta_score: int = 0,
        linking_score: int = 0,
        technical_score: int = 0
    ) -> int:
        """
        Calculate overall SEO score.

        Args:
            content_score: Content quality score (0-100)
            heading_score: Heading structure score (0-100)
            meta_score: Meta tags score (0-100)
            linking_score: Linking score (0-100)
            technical_score: Technical SEO score (0-100)

        Returns:
            Overall score (0-100)
        """
        # Weighted average
        weights = {
            "content": 0.35,    # Content is most important
            "meta": 0.25,       # Meta tags are very important
            "headings": 0.15,   # Heading structure matters
            "linking": 0.15,    # Internal/external links
            "technical": 0.10,  # Technical SEO
        }

        score = (
            content_score * weights["content"] +
            meta_score * weights["meta"] +
            heading_score * weights["headings"] +
            linking_score * weights["linking"] +
            technical_score * weights["technical"]
        )

        return int(round(score))

    @staticmethod
    def prioritize_recommendations(
        recommendations: List[SEORecommendation]
    ) -> Dict[str, List[SEORecommendation]]:
        """
        Prioritize recommendations by priority level.

        Args:
            recommendations: List of recommendations

        Returns:
            Dictionary grouped by priority
        """
        prioritized = {
            "high": [],
            "medium": [],
            "low": [],
        }

        for rec in recommendations:
            prioritized[rec.priority.value].append(rec)

        return prioritized
