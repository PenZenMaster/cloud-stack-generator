"""
Module: website_orchestrator
Path: src/core/orchestration/website_orchestrator.py

Description:
High-level website generation orchestration. Coordinates the overall workflow
including directory setup, content generation, asset generation, and result collection.

Author: Cloud Stack Generator Team
Created: 2025-11-11
Version: 1.0.0
"""

import os
from typing import List, Optional
from dataclasses import dataclass

from ..config.models import ClientConfig
from ..services.ai_content_service import AIContentService
from ..services.content_cache import ContentCache
from .content_coordinator import ContentCoordinator
from .build_pipeline import BuildPipeline, BuildPhase


class GenerationError(Exception):
    """Raised when website generation fails"""
    pass


@dataclass
class GenerationResult:
    """Result of website generation"""
    success: bool
    generated_files: List[str]
    errors: Optional[str] = None


class WebsiteOrchestrator:
    """
    Orchestrates the complete website generation workflow.

    Responsibilities:
    - Main generate() workflow orchestration
    - Directory structure setup via BuildPipeline
    - Content generation coordination via ContentCoordinator
    - Asset generation coordination
    - Error handling and result aggregation
    - Dependency injection setup
    """

    def __init__(self, use_ai: bool = True):
        """
        Initialize WebsiteOrchestrator.

        Args:
            use_ai: Whether to use AI services for enhanced content generation
        """
        self.use_ai = use_ai

        # Initialize AI services
        self.ai_service = AIContentService() if use_ai else None
        self.content_cache = ContentCache() if use_ai else None

        # Initialize coordinators (will be set per generation)
        self.content_coordinator: Optional[ContentCoordinator] = None
        self.build_pipeline: Optional[BuildPipeline] = None

    def generate(self, config: ClientConfig, output_dir: str) -> GenerationResult:
        """
        Generate complete website from configuration.

        This is the main orchestration method that coordinates the entire
        website generation workflow.

        Args:
            config: Client configuration with business, branding, and content data
            output_dir: Output directory path for generated files

        Returns:
            GenerationResult: Result object with success status and generated files
        """
        try:
            # Initialize coordinators for this generation
            self.content_coordinator = ContentCoordinator(
                ai_service=self.ai_service,
                content_cache=self.content_cache
            )
            self.build_pipeline = BuildPipeline(output_dir)

            # Phase 1: Setup build environment
            build_context = self._setup_build_environment()

            # Phase 2: Generate content
            generated_files = self._generate_content(config, output_dir)

            # Phase 3: Generate assets
            asset_files = self._generate_assets(config, output_dir)
            generated_files.extend(asset_files)

            # Phase 4: Finalize build
            self._finalize_build(build_context)

            return GenerationResult(
                success=True,
                generated_files=generated_files
            )

        except Exception as e:
            error_msg = f"Website generation failed: {str(e)}"
            return GenerationResult(
                success=False,
                generated_files=[],
                errors=error_msg
            )

    def _setup_build_environment(self):
        """
        Setup build environment and directory structure.

        Returns:
            BuildContext: Build context for tracking generation state
        """
        # Setup build pipeline
        build_context = self.build_pipeline.setup_build()

        # Build pipeline creates root directory automatically
        # Additional directories will be created as needed during generation

        return build_context

    def _generate_content(self, config: ClientConfig, output_dir: str) -> List[str]:
        """
        Generate all HTML content (home page and city pages).

        Args:
            config: Client configuration
            output_dir: Output directory path

        Returns:
            List[str]: List of generated file paths
        """
        generated_files = []

        # Generate home page (index.html)
        home_html = self.content_coordinator.generate_home_page(
            config,
            use_ai=self.use_ai
        )
        home_path = os.path.join(output_dir, "index.html")
        self.build_pipeline.write_file("index.html", home_html)
        generated_files.append(home_path)

        # Generate city pages
        if hasattr(config, 'city_pages') and config.city_pages:
            # Use enhanced city pages data
            for city_page in config.city_pages:
                city_file = self.content_coordinator.generate_single_city_page(
                    config,
                    city_page,
                    output_dir
                )
                generated_files.append(city_file)
        elif hasattr(config, 'target_cities') and config.target_cities:
            # Fallback to legacy target_cities
            city_files = self.content_coordinator.generate_city_pages(
                config,
                output_dir,
                use_ai=self.use_ai
            )
            generated_files.extend(city_files)

        return generated_files

    def _generate_assets(self, config: ClientConfig, output_dir: str) -> List[str]:
        """
        Generate CSS and other static assets.

        Args:
            config: Client configuration
            output_dir: Output directory path

        Returns:
            List[str]: List of generated asset file paths
        """
        generated_files = []

        # Generate CSS file
        css_path = self._generate_css_file(config, output_dir)
        generated_files.append(css_path)

        # Create js directory for future JavaScript files
        js_dir = os.path.join(output_dir, "js")
        os.makedirs(js_dir, exist_ok=True)

        return generated_files

    def _generate_css_file(self, config: ClientConfig, output_dir: str) -> str:
        """
        Generate CSS file in proper directory structure.

        Args:
            config: Client configuration
            output_dir: Output directory path

        Returns:
            str: Path to generated CSS file
        """
        from ..generators.css_generator import CSSGenerator

        # Create css directory
        css_dir = os.path.join(output_dir, "css")
        os.makedirs(css_dir, exist_ok=True)

        # Generate CSS content
        css_generator = CSSGenerator()
        css_content = css_generator.generate_css(config)

        # Write CSS file
        css_path = os.path.join(css_dir, "style.css")
        with open(css_path, "w", encoding="utf-8") as f:
            f.write(css_content)

        return css_path

    def _finalize_build(self, build_context):
        """
        Finalize build and perform any cleanup.

        Args:
            build_context: Build context from setup phase
        """
        # Mark build as complete
        build_context.phase = BuildPhase.COMPLETE

        # Could add validation, cleanup, or post-processing here
        # For now, just ensure phase is marked complete

    def _collect_results(self, generated_files: List[str]) -> GenerationResult:
        """
        Collect and package generation results.

        Args:
            generated_files: List of generated file paths

        Returns:
            GenerationResult: Packaged result object
        """
        return GenerationResult(
            success=True,
            generated_files=generated_files
        )

    def _handle_generation_error(self, error: Exception) -> GenerationResult:
        """
        Handle generation errors and create error result.

        Args:
            error: Exception that occurred during generation

        Returns:
            GenerationResult: Error result object
        """
        error_msg = f"Website generation failed: {str(error)}"
        return GenerationResult(
            success=False,
            generated_files=[],
            errors=error_msg
        )
