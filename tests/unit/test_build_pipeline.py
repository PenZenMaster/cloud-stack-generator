"""
Tests for build_pipeline module

Tests build process management and file operations.
"""

import os
import tempfile
import shutil
import pytest

from src.core.orchestration.build_pipeline import (
    BuildPipeline,
    BuildPhase,
    BuildContext,
)


class TestBuildContext:
    """Test BuildContext data class"""

    def test_context_initialization(self):
        """Test build context initializes with correct defaults"""
        context = BuildContext(output_dir="/tmp/test")

        assert context.output_dir == "/tmp/test"
        assert context.phase == BuildPhase.SETUP
        assert context.generated_files == []
        assert context.errors == []
        assert context.metadata == {}

    def test_add_generated_file(self):
        """Test adding generated files to context"""
        context = BuildContext(output_dir="/tmp/test")

        context.add_generated_file("/tmp/test/index.html")
        context.add_generated_file("/tmp/test/style.css")

        assert len(context.generated_files) == 2
        assert "/tmp/test/index.html" in context.generated_files

    def test_add_error(self):
        """Test adding errors to context"""
        context = BuildContext(output_dir="/tmp/test")

        context.add_error("File not found")
        context.add_error("Permission denied")

        assert len(context.errors) == 2
        assert context.has_errors()

    def test_has_errors(self):
        """Test error detection"""
        context = BuildContext(output_dir="/tmp/test")

        assert not context.has_errors()

        context.add_error("Test error")

        assert context.has_errors()

    def test_set_phase(self):
        """Test phase transitions"""
        context = BuildContext(output_dir="/tmp/test")

        context.set_phase(BuildPhase.GENERATE)
        assert context.phase == BuildPhase.GENERATE

        context.set_phase(BuildPhase.COMPLETE)
        assert context.phase == BuildPhase.COMPLETE


class TestBuildPipeline:
    """Test BuildPipeline class"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for tests"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def pipeline(self, temp_dir):
        """Create BuildPipeline instance"""
        return BuildPipeline(temp_dir)

    def test_pipeline_initialization(self, temp_dir):
        """Test pipeline initializes correctly"""
        pipeline = BuildPipeline(temp_dir)

        assert pipeline.output_dir == temp_dir
        assert pipeline.context is None

    def test_setup_build(self, pipeline, temp_dir):
        """Test build setup creates directories and context"""
        context = pipeline.setup_build()

        # Context created
        assert context is not None
        assert context.output_dir == temp_dir
        assert context.phase == BuildPhase.SETUP

        # Directories created
        assert os.path.exists(os.path.join(temp_dir, "css"))
        assert os.path.exists(os.path.join(temp_dir, "js"))
        assert os.path.exists(os.path.join(temp_dir, "images"))
        assert os.path.exists(os.path.join(temp_dir, "assets"))

    def test_setup_build_creates_root_directory(self):
        """Test setup creates root directory if it doesn't exist"""
        temp_dir = tempfile.mktemp()  # Don't create the directory

        try:
            pipeline = BuildPipeline(temp_dir)
            context = pipeline.setup_build()

            assert os.path.exists(temp_dir)
            assert context.phase == BuildPhase.SETUP

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)

    def test_write_file(self, pipeline, temp_dir):
        """Test writing text file"""
        pipeline.setup_build()

        content = "<html><body>Test</body></html>"
        file_path = pipeline.write_file("index.html", content)

        # File created
        assert os.path.exists(file_path)
        assert file_path == os.path.join(temp_dir, "index.html")

        # Content correct
        with open(file_path, "r", encoding="utf-8") as f:
            assert f.read() == content

        # Tracked in context
        assert file_path in pipeline.context.generated_files

    def test_write_file_creates_subdirectories(self, pipeline, temp_dir):
        """Test writing file creates necessary subdirectories"""
        pipeline.setup_build()

        file_path = pipeline.write_file("pages/cities/dallas.html", "<html></html>")

        # File and directories created
        assert os.path.exists(file_path)
        assert os.path.exists(os.path.join(temp_dir, "pages", "cities"))

    def test_write_file_without_setup_fails(self, pipeline):
        """Test writing file before setup raises error"""
        with pytest.raises(RuntimeError, match="Build context not initialized"):
            pipeline.write_file("test.html", "content")

    def test_write_binary_file(self, pipeline, temp_dir):
        """Test writing binary file"""
        pipeline.setup_build()

        binary_content = b"\x89PNG\r\n\x1a\n"
        file_path = pipeline.write_binary_file("images/test.png", binary_content)

        # File created
        assert os.path.exists(file_path)

        # Content correct
        with open(file_path, "rb") as f:
            assert f.read() == binary_content

        # Tracked in context
        assert file_path in pipeline.context.generated_files

    def test_copy_file(self, pipeline, temp_dir):
        """Test copying file"""
        # Create source file
        source_path = os.path.join(temp_dir, "source.txt")
        with open(source_path, "w") as f:
            f.write("test content")

        pipeline.setup_build()

        # Copy file
        dest_path = pipeline.copy_file(source_path, "assets/copied.txt")

        # File copied
        assert os.path.exists(dest_path)

        # Content matches
        with open(dest_path, "r") as f:
            assert f.read() == "test content"

        # Tracked in context
        assert dest_path in pipeline.context.generated_files

    def test_begin_generation_phase(self, pipeline):
        """Test phase transition to generation"""
        pipeline.setup_build()

        pipeline.begin_generation_phase()

        assert pipeline.context.phase == BuildPhase.GENERATE

    def test_finalize_build_success(self, pipeline):
        """Test finalizing successful build"""
        pipeline.setup_build()
        pipeline.write_file("index.html", "<html></html>")

        context = pipeline.finalize_build()

        assert context.phase == BuildPhase.COMPLETE
        assert not context.has_errors()

    def test_finalize_build_with_errors(self, pipeline):
        """Test finalizing build with errors"""
        pipeline.setup_build()
        pipeline.context.add_error("Test error")

        context = pipeline.finalize_build()

        assert context.phase == BuildPhase.FAILED
        assert context.has_errors()

    def test_get_context(self, pipeline):
        """Test getting current context"""
        context = pipeline.setup_build()

        assert pipeline.get_context() is context

    def test_get_context_before_setup_fails(self, pipeline):
        """Test getting context before setup raises error"""
        with pytest.raises(RuntimeError, match="Build context not initialized"):
            pipeline.get_context()

    def test_validate_build_success(self, pipeline):
        """Test validating successful build"""
        pipeline.setup_build()
        pipeline.write_file("index.html", "<html></html>")
        pipeline.write_file("css/style.css", "body { }")

        is_valid = pipeline.validate_build()

        assert is_valid is True

    def test_validate_build_missing_index(self, pipeline):
        """Test validation fails without index.html"""
        pipeline.setup_build()
        pipeline.write_file("css/style.css", "body { }")

        is_valid = pipeline.validate_build()

        assert is_valid is False
        assert pipeline.context.has_errors()
        assert any("index.html" in error for error in pipeline.context.errors)

    def test_validate_build_with_errors(self, pipeline):
        """Test validation fails with errors in context"""
        pipeline.setup_build()
        pipeline.write_file("index.html", "<html></html>")
        pipeline.context.add_error("Test error")

        is_valid = pipeline.validate_build()

        assert is_valid is False

    def test_validate_build_missing_file(self, pipeline, temp_dir):
        """Test validation fails if generated file doesn't exist"""
        pipeline.setup_build()

        # Manually add a non-existent file to context
        fake_file = os.path.join(temp_dir, "nonexistent.html")
        pipeline.context.add_generated_file(fake_file)
        pipeline.write_file("index.html", "<html></html>")  # Add valid index

        is_valid = pipeline.validate_build()

        assert is_valid is False
        assert any("does not exist" in error for error in pipeline.context.errors)

    def test_cleanup_on_error(self, pipeline):
        """Test cleanup on error (currently logs only)"""
        pipeline.setup_build()
        pipeline.context.add_error("Test error")

        # Should not raise exception
        pipeline.cleanup_on_error()

        # Errors still present (we don't clear them)
        assert pipeline.context.has_errors()


class TestBuildPhase:
    """Test BuildPhase enum"""

    def test_build_phases_defined(self):
        """Test all expected build phases are defined"""
        assert BuildPhase.SETUP.value == "setup"
        assert BuildPhase.GENERATE.value == "generate"
        assert BuildPhase.FINALIZE.value == "finalize"
        assert BuildPhase.COMPLETE.value == "complete"
        assert BuildPhase.FAILED.value == "failed"

    def test_build_phases_comparable(self):
        """Test build phases can be compared"""
        phase1 = BuildPhase.SETUP
        phase2 = BuildPhase.SETUP
        phase3 = BuildPhase.GENERATE

        assert phase1 == phase2
        assert phase1 != phase3
