"""
Module: build_pipeline
Path: src/core/orchestration/build_pipeline.py

Description:
Build process management and file operations for website generation.
Handles the build lifecycle: setup → generate → finalize.

Author: Cloud Stack Generator Team
Created: 2025-10-20
Version: 1.0.0
"""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..utils.logger import get_logger

# Initialize module logger
logger = get_logger(__name__)


class BuildPhase(Enum):
    """Build pipeline phases"""

    SETUP = "setup"
    GENERATE = "generate"
    FINALIZE = "finalize"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class BuildContext:
    """Build context containing state and configuration"""

    output_dir: str
    phase: BuildPhase = BuildPhase.SETUP
    generated_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_generated_file(self, file_path: str) -> None:
        """Add a generated file to the context"""
        self.generated_files.append(file_path)

    def add_error(self, error: str) -> None:
        """Add an error to the context"""
        self.errors.append(error)

    def has_errors(self) -> bool:
        """Check if context has any errors"""
        return len(self.errors) > 0

    def set_phase(self, phase: BuildPhase) -> None:
        """Set the current build phase"""
        self.phase = phase


class BuildPipeline:
    """
    Manages the website build pipeline.

    Responsibilities:
    - Directory structure creation
    - File I/O operations
    - Build phase management
    - Asset generation coordination
    - Build validation
    """

    def __init__(self, output_dir: str):
        """
        Initialize build pipeline.

        Args:
            output_dir: Root output directory for generated website
        """
        self.output_dir = output_dir
        self.context: Optional[BuildContext] = None

    def setup_build(self) -> BuildContext:
        """
        Set up the build environment.

        Creates directory structure and initializes build context.

        Returns:
            BuildContext: Initialized build context

        Raises:
            OSError: If directory creation fails
        """
        # Create build context
        self.context = BuildContext(output_dir=self.output_dir)

        try:
            # Create root output directory
            Path(self.output_dir).mkdir(parents=True, exist_ok=True)

            # Create standard directory structure
            self._create_directory_structure()

            # Update phase
            self.context.set_phase(BuildPhase.SETUP)

            return self.context

        except OSError as e:
            self.context.add_error(f"Failed to setup build: {str(e)}")
            self.context.set_phase(BuildPhase.FAILED)
            raise

    def _create_directory_structure(self) -> None:
        """Create standard website directory structure"""
        directories = [
            "css",
            "js",
            "images",
            "assets"
        ]

        for directory in directories:
            dir_path = os.path.join(self.output_dir, directory)
            os.makedirs(dir_path, exist_ok=True)

    def write_file(self, relative_path: str, content: str) -> str:
        """
        Write content to a file in the output directory.

        Args:
            relative_path: Path relative to output_dir
            content: File content to write

        Returns:
            str: Absolute path to written file

        Raises:
            IOError: If file write fails
        """
        if not self.context:
            raise RuntimeError("Build context not initialized. Call setup_build() first.")

        # Construct full path
        file_path = os.path.join(self.output_dir, relative_path)

        try:
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Write file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)

            # Track in context
            self.context.add_generated_file(file_path)

            return file_path

        except IOError as e:
            error_msg = f"Failed to write file {relative_path}: {str(e)}"
            self.context.add_error(error_msg)
            raise IOError(error_msg) from e

    def write_binary_file(self, relative_path: str, content: bytes) -> str:
        """
        Write binary content to a file in the output directory.

        Args:
            relative_path: Path relative to output_dir
            content: Binary content to write

        Returns:
            str: Absolute path to written file

        Raises:
            IOError: If file write fails
        """
        if not self.context:
            raise RuntimeError("Build context not initialized. Call setup_build() first.")

        file_path = os.path.join(self.output_dir, relative_path)

        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, "wb") as f:
                f.write(content)

            self.context.add_generated_file(file_path)

            return file_path

        except IOError as e:
            error_msg = f"Failed to write binary file {relative_path}: {str(e)}"
            self.context.add_error(error_msg)
            raise IOError(error_msg) from e

    def copy_file(self, source_path: str, relative_dest_path: str) -> str:
        """
        Copy a file to the output directory.

        Args:
            source_path: Source file path
            relative_dest_path: Destination path relative to output_dir

        Returns:
            str: Absolute path to copied file

        Raises:
            IOError: If copy fails
        """
        if not self.context:
            raise RuntimeError("Build context not initialized. Call setup_build() first.")

        dest_path = os.path.join(self.output_dir, relative_dest_path)

        try:
            import shutil

            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            shutil.copy2(source_path, dest_path)

            self.context.add_generated_file(dest_path)

            return dest_path

        except (IOError, OSError) as e:
            error_msg = f"Failed to copy file {source_path}: {str(e)}"
            self.context.add_error(error_msg)
            raise IOError(error_msg) from e

    def begin_generation_phase(self) -> None:
        """Mark the start of the generation phase"""
        if not self.context:
            raise RuntimeError("Build context not initialized")

        self.context.set_phase(BuildPhase.GENERATE)

    def finalize_build(self) -> BuildContext:
        """
        Finalize the build process.

        Performs cleanup, validation, and marks build as complete.

        Returns:
            BuildContext: Final build context with results
        """
        if not self.context:
            raise RuntimeError("Build context not initialized")

        # Set final phase
        if self.context.has_errors():
            self.context.set_phase(BuildPhase.FAILED)
        else:
            self.context.set_phase(BuildPhase.COMPLETE)

        return self.context

    def get_context(self) -> BuildContext:
        """
        Get the current build context.

        Returns:
            BuildContext: Current build context

        Raises:
            RuntimeError: If context not initialized
        """
        if not self.context:
            raise RuntimeError("Build context not initialized")

        return self.context

    def validate_build(self) -> bool:
        """
        Validate the build output.

        Checks that required files exist and are valid.

        Returns:
            bool: True if build is valid, False otherwise
        """
        if not self.context:
            return False

        # Check for errors
        if self.context.has_errors():
            return False

        # Check that at least index.html was generated
        index_found = any(
            file_path.endswith("index.html")
            for file_path in self.context.generated_files
        )

        if not index_found:
            self.context.add_error("No index.html file generated")
            return False

        # Validate generated files exist
        for file_path in self.context.generated_files:
            if not os.path.exists(file_path):
                self.context.add_error(f"Generated file does not exist: {file_path}")
                return False

        return True

    def cleanup_on_error(self) -> None:
        """
        Clean up partial build on error.

        Optionally removes generated files if build failed.
        Note: Currently does not remove files to allow inspection.
        """
        if self.context and self.context.has_errors():
            # Log errors for debugging
            for error in self.context.errors:
                logger.error(f"Build error: {error}")

            # Optionally remove generated files here
            # Currently leaving files for inspection
            pass
