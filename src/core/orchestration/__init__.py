"""
Module: orchestration
Path: src/core/orchestration/__init__.py

Description:
Orchestration modules for website generation workflow management.

This package contains the core orchestration logic split from the monolithic
website_generator.py module for better maintainability and testability.

Modules:
- build_pipeline: Build process management and file operations
- content_coordinator: Content generation coordination
- website_orchestrator: High-level workflow orchestration

Author: Cloud Stack Generator Team
Created: 2025-10-20
Version: 1.0.0
"""

from .build_pipeline import BuildPipeline, BuildPhase, BuildContext
from .content_coordinator import ContentCoordinator
from .website_orchestrator import WebsiteOrchestrator, GenerationResult, GenerationError

__all__ = [
    "BuildPipeline",
    "BuildPhase",
    "BuildContext",
    "ContentCoordinator",
    "WebsiteOrchestrator",
    "GenerationResult",
    "GenerationError",
]
