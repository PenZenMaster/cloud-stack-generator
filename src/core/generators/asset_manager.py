"""
Asset Manager
Path: E:/projects/cloud-stack-generator/src/core/generators/asset_manager.py

Description:
Manages static asset operations including directory creation, file copying,
and asset organization. Extracted from page_generator.py to improve separation
of concerns and reusability.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-17

Last Modified Date:
2025-10-17

Comments:
* v1.00 - Initial extraction from page_generator.py
"""

import shutil
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config.models import ClientConfig


class AssetManager:
    """Manages static assets and directory structure for website generation"""

    def __init__(self, output_base_dir: Path, template_dir: Optional[Path] = None):
        """
        Initialize the asset manager.

        Args:
            output_base_dir: Base directory for output files
            template_dir: Optional directory containing template static assets
        """
        self.output_base_dir = Path(output_base_dir)
        self.template_dir = Path(template_dir) if template_dir else None

    def create_directory_structure(self, config: "ClientConfig") -> Path:
        """
        Create complete directory structure for website output.

        Creates base directories and subdirectories based on configuration:
        - css/ - Stylesheets
        - js/ - JavaScript files
        - images/ - Image assets
        - products/ - Product pages (if products exist)
        - services/ - Service pages (if services exist)
        - locations/ - City/location pages (if city pages exist)

        Args:
            config: Client configuration containing content structure

        Returns:
            Path to the created output directory

        Examples:
            >>> manager = AssetManager(Path("./output"))
            >>> output_dir = manager.create_directory_structure(config)
            >>> assert (output_dir / "css").exists()
            >>> assert (output_dir / "js").exists()
        """
        # Create main output directory
        output_dir = self.output_base_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create standard subdirectories
        (output_dir / "css").mkdir(exist_ok=True)
        (output_dir / "js").mkdir(exist_ok=True)
        (output_dir / "images").mkdir(exist_ok=True)

        # Create conditional subdirectories based on config
        if config.products:
            (output_dir / "products").mkdir(exist_ok=True)

        if config.services:
            (output_dir / "services").mkdir(exist_ok=True)

        if config.city_pages:
            (output_dir / "locations").mkdir(exist_ok=True)

        return output_dir

    def copy_static_assets(
        self, output_dir: Path, copied_files: Optional[List[str]] = None
    ) -> dict:
        """
        Copy static assets from template directory to output directory.

        Copies assets from template_dir/static/ to output directory:
        - static/images/ -> output/images/
        - static/css/*.css -> output/css/
        - static/js/*.js -> output/js/

        Args:
            output_dir: Destination directory for assets
            copied_files: Optional list to append copied file paths

        Returns:
            Dictionary with:
                - success: bool
                - copied_files: List of copied file paths
                - warnings: List of warning messages

        Examples:
            >>> manager = AssetManager(Path("./output"), Path("./templates"))
            >>> result = manager.copy_static_assets(Path("./output"))
            >>> assert result['success']
        """
        result = {"success": True, "copied_files": [], "warnings": []}

        if copied_files is None:
            copied_files = []

        try:
            # Check if template directory and static assets exist
            if not self.template_dir:
                result["warnings"].append("No template directory configured")
                return result

            static_dir = self.template_dir / "static"
            if not static_dir.exists():
                result["warnings"].append(
                    f"Static assets directory not found: {static_dir}"
                )
                return result

            # Copy images directory
            if (static_dir / "images").exists():
                shutil.copytree(
                    static_dir / "images", output_dir / "images", dirs_exist_ok=True
                )
                # Record all copied image files
                for img_file in (static_dir / "images").rglob("*"):
                    if img_file.is_file():
                        dest_file = output_dir / "images" / img_file.relative_to(
                            static_dir / "images"
                        )
                        result["copied_files"].append(str(dest_file))
                        copied_files.append(str(dest_file))

            # Copy additional CSS files
            if (static_dir / "css").exists():
                for css_file in (static_dir / "css").glob("*.css"):
                    dest_file = output_dir / "css" / css_file.name
                    shutil.copy2(css_file, dest_file)
                    result["copied_files"].append(str(dest_file))
                    copied_files.append(str(dest_file))

            # Copy additional JavaScript files
            if (static_dir / "js").exists():
                for js_file in (static_dir / "js").glob("*.js"):
                    dest_file = output_dir / "js" / js_file.name
                    shutil.copy2(js_file, dest_file)
                    result["copied_files"].append(str(dest_file))
                    copied_files.append(str(dest_file))

        except Exception as e:
            result["success"] = False
            result["warnings"].append(f"Could not copy static assets: {str(e)}")

        return result

    def copy_file(self, source: Path, destination: Path) -> bool:
        """
        Copy a single file to destination.

        Args:
            source: Source file path
            destination: Destination file path

        Returns:
            True if successful, False otherwise

        Examples:
            >>> manager = AssetManager(Path("./output"))
            >>> success = manager.copy_file(Path("logo.png"), Path("./output/images/logo.png"))
        """
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            return True
        except Exception:
            return False

    def ensure_directory_exists(self, directory: Path) -> bool:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory: Directory path to ensure exists

        Returns:
            True if directory exists or was created successfully

        Examples:
            >>> manager = AssetManager(Path("./output"))
            >>> manager.ensure_directory_exists(Path("./output/custom"))
            True
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception:
            return False

    def clean_directory(self, directory: Path, keep_patterns: Optional[List[str]] = None) -> bool:
        """
        Clean a directory of files, optionally keeping files matching patterns.

        Args:
            directory: Directory to clean
            keep_patterns: Optional list of glob patterns for files to keep

        Returns:
            True if successful, False otherwise

        Examples:
            >>> manager = AssetManager(Path("./output"))
            >>> manager.clean_directory(Path("./output/images"), keep_patterns=["*.png"])
        """
        try:
            if not directory.exists():
                return True

            keep_patterns = keep_patterns or []

            for item in directory.iterdir():
                # Check if item should be kept
                should_keep = False
                for pattern in keep_patterns:
                    if item.match(pattern):
                        should_keep = True
                        break

                if should_keep:
                    continue

                # Remove file or directory
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

            return True
        except Exception:
            return False
