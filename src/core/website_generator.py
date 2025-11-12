"""
Filename: src/core/website_generator.py
Path: E:\\projects\\cloud-stack-generator\\src\\core\\website_generator.py
Description: Website Generator Facade - maintains backward compatibility

This module now acts as a facade that delegates to the orchestration layer.
The actual generation logic has been refactored into modular components:
- WebsiteOrchestrator: High-level workflow orchestration
- ContentCoordinator: Content generation coordination
- BuildPipeline: Build process and file operations

Version: 3.0.0
Date: 2025-11-11
Author: Cloud Stack Generator Team
"""

from typing import List, Optional
from .config.models import ClientConfig

# Import from orchestration layer
from .orchestration import (
    WebsiteOrchestrator,
    GenerationResult,
    GenerationError
)

# Re-export for backward compatibility
__all__ = ['WebsiteGenerator', 'GenerationResult', 'GenerationError']


class WebsiteGenerator:
    """
    Website Generator Facade - maintains backward compatibility.

    This class now delegates all operations to the WebsiteOrchestrator
    while maintaining the same public API for existing code.

    Deprecated: Consider using WebsiteOrchestrator directly for new code.
    """

    def __init__(self, use_ai: bool = True):
        """
        Initialize WebsiteGenerator.

        Args:
            use_ai: Whether to use AI services for content generation
        """
        # Maintain legacy instance variables for any code that might access them
        self.output_dir: Optional[str] = None
        self.config: Optional[ClientConfig] = None
        self.use_ai = use_ai

        # Initialize orchestrator for actual work
        self._orchestrator = WebsiteOrchestrator(use_ai=use_ai)

        # Expose orchestrator's services for backward compatibility
        self.ai_service = self._orchestrator.ai_service
        self.content_cache = self._orchestrator.content_cache

    def generate(self, config: ClientConfig, output_dir: str) -> GenerationResult:
        """
        Generate website from configuration.

        This method delegates to WebsiteOrchestrator while maintaining
        the exact same API for backward compatibility.

        Args:
            config: Client configuration with business, branding, and content data
            output_dir: Output directory path for generated files

        Returns:
            GenerationResult: Result object with success status and generated files
        """
        # Store for legacy compatibility
        self.output_dir = output_dir
        self.config = config

        # Delegate to orchestrator
        return self._orchestrator.generate(config, output_dir)


# Legacy support: Keep any methods that might be called externally
# (Currently none identified, but structure allows for easy addition)
