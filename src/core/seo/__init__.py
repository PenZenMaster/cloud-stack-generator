"""
Module/Script Name: SEO Analysis Package
Path: src/core/seo/__init__.py

Description:
LLM-powered SEO analysis tools for generated websites.
Provides content quality analysis, meta tag optimization, and SEO scoring.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2026-02-17

Last Modified Date:
2026-02-17

Comments:
* v1.00 - Initial SEO analysis package (Phase 2)
"""

from .analyzer import SEOAnalyzer, SEOAnalysisResult
from .analyzers.scoring_engine import SEOScore, SEORecommendation

__all__ = [
    "SEOAnalyzer",
    "SEOAnalysisResult",
    "SEOScore",
    "SEORecommendation",
]
