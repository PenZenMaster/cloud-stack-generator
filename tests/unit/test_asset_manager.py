"""
Unit tests for Asset Manager
Path: E:/projects/cloud-stack-generator/tests/unit/test_asset_manager.py

Description:
Tests for the asset manager module to ensure proper functionality
of directory creation and asset copying operations.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-17

Last Modified Date:
2025-10-17

Comments:
* v1.00 - Initial tests for refactored asset manager
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.generators.asset_manager import AssetManager


class TestAssetManager:
    """Tests for AssetManager"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)

    @pytest.fixture
    def mock_config(self):
        """Create a mock ClientConfig for testing"""
        config = Mock()
        config.products = []
        config.services = []
        config.city_pages = []
        return config

    @pytest.fixture
    def mock_config_with_content(self):
        """Create a mock ClientConfig with products and services"""
        config = Mock()
        config.products = [Mock()]  # Has products
        config.services = [Mock()]  # Has services
        config.city_pages = [Mock()]  # Has city pages
        return config

    def test_initialization_basic(self, temp_dir):
        """Test basic initialization"""
        manager = AssetManager(temp_dir)
        assert manager.output_base_dir == temp_dir
        assert manager.template_dir is None

    def test_initialization_with_template_dir(self, temp_dir):
        """Test initialization with template directory"""
        template_dir = temp_dir / "templates"
        manager = AssetManager(temp_dir, template_dir)
        assert manager.output_base_dir == temp_dir
        assert manager.template_dir == template_dir

    def test_create_directory_structure_basic(self, temp_dir, mock_config):
        """Test basic directory structure creation"""
        manager = AssetManager(temp_dir)
        output_dir = manager.create_directory_structure(mock_config)

        assert output_dir.exists()
        assert (output_dir / "css").exists()
        assert (output_dir / "js").exists()
        assert (output_dir / "images").exists()

    def test_create_directory_structure_no_optional_dirs(self, temp_dir, mock_config):
        """Test that optional directories are not created when not needed"""
        manager = AssetManager(temp_dir)
        output_dir = manager.create_directory_structure(mock_config)

        assert not (output_dir / "products").exists()
        assert not (output_dir / "services").exists()
        assert not (output_dir / "locations").exists()

    def test_create_directory_structure_with_products(self, temp_dir, mock_config_with_content):
        """Test directory creation with products"""
        manager = AssetManager(temp_dir)
        output_dir = manager.create_directory_structure(mock_config_with_content)

        assert (output_dir / "products").exists()
        assert (output_dir / "services").exists()
        assert (output_dir / "locations").exists()

    def test_create_directory_structure_idempotent(self, temp_dir, mock_config):
        """Test that directory creation is idempotent"""
        manager = AssetManager(temp_dir)
        output_dir1 = manager.create_directory_structure(mock_config)
        output_dir2 = manager.create_directory_structure(mock_config)

        assert output_dir1 == output_dir2
        assert output_dir1.exists()

    def test_copy_static_assets_no_template_dir(self, temp_dir):
        """Test asset copying with no template directory"""
        manager = AssetManager(temp_dir)
        result = manager.copy_static_assets(temp_dir)

        assert result["success"]
        assert len(result["warnings"]) > 0
        assert "No template directory" in result["warnings"][0]

    def test_copy_static_assets_no_static_dir(self, temp_dir):
        """Test asset copying when static directory doesn't exist"""
        template_dir = temp_dir / "templates"
        template_dir.mkdir()

        manager = AssetManager(temp_dir, template_dir)
        result = manager.copy_static_assets(temp_dir)

        assert result["success"]
        assert len(result["warnings"]) > 0
        assert "not found" in result["warnings"][0]

    def test_copy_static_assets_with_images(self, temp_dir):
        """Test copying image assets"""
        # Setup template directory with images
        template_dir = temp_dir / "templates"
        static_images = template_dir / "static" / "images"
        static_images.mkdir(parents=True)

        # Create test image file
        test_image = static_images / "test.png"
        test_image.write_text("fake image content")

        # Setup output directory
        output_dir = temp_dir / "output"
        output_dir.mkdir()
        (output_dir / "images").mkdir()

        manager = AssetManager(output_dir, template_dir)
        result = manager.copy_static_assets(output_dir)

        assert result["success"]
        assert (output_dir / "images" / "test.png").exists()
        assert len(result["copied_files"]) == 1

    def test_copy_static_assets_with_css(self, temp_dir):
        """Test copying CSS assets"""
        # Setup template directory with CSS
        template_dir = temp_dir / "templates"
        static_css = template_dir / "static" / "css"
        static_css.mkdir(parents=True)

        # Create test CSS file
        test_css = static_css / "custom.css"
        test_css.write_text("body { color: red; }")

        # Setup output directory
        output_dir = temp_dir / "output"
        (output_dir / "css").mkdir(parents=True)

        manager = AssetManager(output_dir, template_dir)
        result = manager.copy_static_assets(output_dir)

        assert result["success"]
        assert (output_dir / "css" / "custom.css").exists()
        assert str(output_dir / "css" / "custom.css") in result["copied_files"]

    def test_copy_static_assets_with_js(self, temp_dir):
        """Test copying JavaScript assets"""
        # Setup template directory with JS
        template_dir = temp_dir / "templates"
        static_js = template_dir / "static" / "js"
        static_js.mkdir(parents=True)

        # Create test JS file
        test_js = static_js / "app.js"
        test_js.write_text("console.log('test');")

        # Setup output directory
        output_dir = temp_dir / "output"
        (output_dir / "js").mkdir(parents=True)

        manager = AssetManager(output_dir, template_dir)
        result = manager.copy_static_assets(output_dir)

        assert result["success"]
        assert (output_dir / "js" / "app.js").exists()

    def test_copy_static_assets_tracks_files(self, temp_dir):
        """Test that copied files are tracked"""
        template_dir = temp_dir / "templates"
        static_css = template_dir / "static" / "css"
        static_css.mkdir(parents=True)
        (static_css / "test.css").write_text("test")

        output_dir = temp_dir / "output"
        (output_dir / "css").mkdir(parents=True)

        tracked_files = []
        manager = AssetManager(output_dir, template_dir)
        result = manager.copy_static_assets(output_dir, tracked_files)

        assert len(tracked_files) > 0
        assert len(result["copied_files"]) > 0

    def test_copy_file_basic(self, temp_dir):
        """Test copying a single file"""
        source = temp_dir / "source.txt"
        source.write_text("test content")

        dest = temp_dir / "output" / "dest.txt"

        manager = AssetManager(temp_dir)
        success = manager.copy_file(source, dest)

        assert success
        assert dest.exists()
        assert dest.read_text() == "test content"

    def test_copy_file_creates_parent_dirs(self, temp_dir):
        """Test that copy_file creates parent directories"""
        source = temp_dir / "source.txt"
        source.write_text("test")

        dest = temp_dir / "deep" / "nested" / "path" / "file.txt"

        manager = AssetManager(temp_dir)
        success = manager.copy_file(source, dest)

        assert success
        assert dest.exists()

    def test_copy_file_nonexistent_source(self, temp_dir):
        """Test copying a file that doesn't exist"""
        source = temp_dir / "nonexistent.txt"
        dest = temp_dir / "dest.txt"

        manager = AssetManager(temp_dir)
        success = manager.copy_file(source, dest)

        assert not success

    def test_ensure_directory_exists_creates_dir(self, temp_dir):
        """Test ensuring a directory exists"""
        new_dir = temp_dir / "new_directory"

        manager = AssetManager(temp_dir)
        success = manager.ensure_directory_exists(new_dir)

        assert success
        assert new_dir.exists()

    def test_ensure_directory_exists_nested(self, temp_dir):
        """Test creating nested directories"""
        nested_dir = temp_dir / "level1" / "level2" / "level3"

        manager = AssetManager(temp_dir)
        success = manager.ensure_directory_exists(nested_dir)

        assert success
        assert nested_dir.exists()

    def test_ensure_directory_exists_already_exists(self, temp_dir):
        """Test ensuring a directory that already exists"""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()

        manager = AssetManager(temp_dir)
        success = manager.ensure_directory_exists(existing_dir)

        assert success

    def test_clean_directory_removes_files(self, temp_dir):
        """Test cleaning a directory removes files"""
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        (target_dir / "file1.txt").write_text("test")
        (target_dir / "file2.txt").write_text("test")

        manager = AssetManager(temp_dir)
        success = manager.clean_directory(target_dir)

        assert success
        assert len(list(target_dir.iterdir())) == 0

    def test_clean_directory_keeps_patterns(self, temp_dir):
        """Test cleaning a directory keeps matching patterns"""
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        (target_dir / "keep.png").write_text("keep")
        (target_dir / "remove.txt").write_text("remove")

        manager = AssetManager(temp_dir)
        success = manager.clean_directory(target_dir, keep_patterns=["*.png"])

        assert success
        assert (target_dir / "keep.png").exists()
        assert not (target_dir / "remove.txt").exists()

    def test_clean_directory_nonexistent(self, temp_dir):
        """Test cleaning a directory that doesn't exist"""
        nonexistent = temp_dir / "nonexistent"

        manager = AssetManager(temp_dir)
        success = manager.clean_directory(nonexistent)

        assert success

    def test_clean_directory_removes_subdirs(self, temp_dir):
        """Test cleaning removes subdirectories"""
        target_dir = temp_dir / "target"
        target_dir.mkdir()
        subdir = target_dir / "subdir"
        subdir.mkdir()
        (subdir / "file.txt").write_text("test")

        manager = AssetManager(temp_dir)
        success = manager.clean_directory(target_dir)

        assert success
        assert not subdir.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
