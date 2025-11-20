"""
Module: test_website_orchestrator
Path: tests/unit/test_website_orchestrator.py

Description:
Unit tests for WebsiteOrchestrator class. Tests high-level orchestration
workflow, coordination between components, and error handling.

Author: Cloud Stack Generator Team
Created: 2025-11-11
Version: 1.0.0
"""

import pytest
from unittest.mock import Mock, patch

from src.core.orchestration.website_orchestrator import (
    WebsiteOrchestrator,
    GenerationResult,
    GenerationError
)
from src.core.config.models import (
    ClientConfig,
    BusinessConfig,
    ContactConfig,
    BrandingConfig,
    CityPageConfig
)


@pytest.fixture
def sample_config():
    """Fixture for sample client configuration"""
    return ClientConfig(
        business=BusinessConfig(
            business_name="Test Business",
            industry="Technology",
            tagline="Testing Excellence"
        ),
        contact=ContactConfig(
            phone="555-0100",
            email="test@example.com",
            address="123 Test St"
        ),
        branding=BrandingConfig(
            primary_color="#0066cc",
            logo_url="logo.png"
        ),
        target_cities=["TestCity", "SampleTown"]
    )


@pytest.fixture
def sample_city_page():
    """Fixture for sample city page configuration"""
    return CityPageConfig(
        city_name="TestCity",
        slug="testcity",
        about_city="Test city description"
    )


class TestWebsiteOrchestratorInitialization:
    """Test WebsiteOrchestrator initialization"""

    def test_orchestrator_initialization_with_ai(self):
        """Test orchestrator initializes with AI services"""
        orchestrator = WebsiteOrchestrator(use_ai=True)

        assert orchestrator.use_ai is True
        assert orchestrator.ai_service is not None
        assert orchestrator.content_cache is not None
        assert orchestrator.content_coordinator is None  # Set during generation
        assert orchestrator.build_pipeline is None  # Set during generation

    def test_orchestrator_initialization_without_ai(self):
        """Test orchestrator initializes without AI services"""
        orchestrator = WebsiteOrchestrator(use_ai=False)

        assert orchestrator.use_ai is False
        assert orchestrator.ai_service is None
        assert orchestrator.content_cache is None
        assert orchestrator.content_coordinator is None
        assert orchestrator.build_pipeline is None

    def test_orchestrator_default_initialization(self):
        """Test orchestrator defaults to AI enabled"""
        orchestrator = WebsiteOrchestrator()

        assert orchestrator.use_ai is True
        assert orchestrator.ai_service is not None
        assert orchestrator.content_cache is not None


class TestGenerateWorkflow:
    """Test main generate() workflow orchestration"""

    @patch('src.core.orchestration.website_orchestrator.ContentCoordinator')
    @patch('src.core.orchestration.website_orchestrator.BuildPipeline')
    def test_generate_initializes_coordinators(
        self,
        mock_build_pipeline_class,
        mock_content_coordinator_class,
        sample_config,
        tmp_path
    ):
        """Test generate() initializes content coordinator and build pipeline"""
        # Setup mocks
        mock_content_coordinator = Mock()
        mock_content_coordinator.generate_home_page = Mock(return_value="<html>Home</html>")
        mock_content_coordinator.generate_city_pages = Mock(return_value=["city1.html"])
        mock_content_coordinator_class.return_value = mock_content_coordinator

        mock_build_pipeline = Mock()
        mock_context = Mock()
        mock_context.phase = "SETUP"
        mock_build_pipeline.setup_build = Mock(return_value=mock_context)
        mock_build_pipeline.write_file = Mock()
        mock_build_pipeline_class.return_value = mock_build_pipeline

        # Create orchestrator and generate
        orchestrator = WebsiteOrchestrator(use_ai=True)

        with patch('os.makedirs'), patch('builtins.open', create=True):
            result = orchestrator.generate(sample_config, str(tmp_path))

        # Verify coordinators were initialized
        mock_content_coordinator_class.assert_called_once()
        mock_build_pipeline_class.assert_called_once_with(str(tmp_path))

        # Verify result
        assert result.success is True

    @patch('src.core.orchestration.website_orchestrator.ContentCoordinator')
    @patch('src.core.orchestration.website_orchestrator.BuildPipeline')
    def test_generate_creates_home_page(
        self,
        mock_build_pipeline_class,
        mock_content_coordinator_class,
        sample_config,
        tmp_path
    ):
        """Test generate() creates home page"""
        # Setup mocks
        mock_content_coordinator = Mock()
        mock_content_coordinator.generate_home_page = Mock(return_value="<html>Home Page</html>")
        mock_content_coordinator.generate_city_pages = Mock(return_value=[])
        mock_content_coordinator_class.return_value = mock_content_coordinator

        mock_build_pipeline = Mock()
        mock_context = Mock()
        mock_build_pipeline.setup_build = Mock(return_value=mock_context)
        mock_build_pipeline.write_file = Mock()
        mock_build_pipeline_class.return_value = mock_build_pipeline

        # Create orchestrator and generate
        orchestrator = WebsiteOrchestrator(use_ai=False)

        with patch('os.makedirs'), patch('builtins.open', create=True):
            result = orchestrator.generate(sample_config, str(tmp_path))

        # Verify home page generation was called
        mock_content_coordinator.generate_home_page.assert_called_once_with(
            sample_config,
            use_ai=False
        )

        # Verify file was written
        mock_build_pipeline.write_file.assert_called_once_with(
            "index.html",
            "<html>Home Page</html>"
        )

    @patch('src.core.orchestration.website_orchestrator.ContentCoordinator')
    @patch('src.core.orchestration.website_orchestrator.BuildPipeline')
    def test_generate_creates_city_pages_from_target_cities(
        self,
        mock_build_pipeline_class,
        mock_content_coordinator_class,
        sample_config,
        tmp_path
    ):
        """Test generate() creates city pages from target_cities"""
        # Setup mocks
        mock_content_coordinator = Mock()
        mock_content_coordinator.generate_home_page = Mock(return_value="<html>Home</html>")
        mock_content_coordinator.generate_city_pages = Mock(
            return_value=[str(tmp_path / "city1.html"), str(tmp_path / "city2.html")]
        )
        mock_content_coordinator_class.return_value = mock_content_coordinator

        mock_build_pipeline = Mock()
        mock_context = Mock()
        mock_build_pipeline.setup_build = Mock(return_value=mock_context)
        mock_build_pipeline.write_file = Mock()
        mock_build_pipeline_class.return_value = mock_build_pipeline

        # Create orchestrator and generate
        orchestrator = WebsiteOrchestrator(use_ai=True)

        with patch('os.makedirs'), patch('builtins.open', create=True):
            result = orchestrator.generate(sample_config, str(tmp_path))

        # Verify city pages generation was called
        mock_content_coordinator.generate_city_pages.assert_called_once_with(
            sample_config,
            str(tmp_path),
            use_ai=True
        )

        # Verify result contains city pages
        assert result.success is True
        assert len(result.generated_files) >= 2  # Home + cities

    @patch('src.core.orchestration.website_orchestrator.ContentCoordinator')
    @patch('src.core.orchestration.website_orchestrator.BuildPipeline')
    def test_generate_creates_city_pages_from_city_pages_config(
        self,
        mock_build_pipeline_class,
        mock_content_coordinator_class,
        sample_config,
        sample_city_page,
        tmp_path
    ):
        """Test generate() creates city pages from enhanced city_pages config"""
        # Add enhanced city pages to config
        sample_config.city_pages = [sample_city_page]

        # Setup mocks
        mock_content_coordinator = Mock()
        mock_content_coordinator.generate_home_page = Mock(return_value="<html>Home</html>")
        mock_content_coordinator.generate_single_city_page = Mock(
            return_value=str(tmp_path / "testcity.html")
        )
        mock_content_coordinator_class.return_value = mock_content_coordinator

        mock_build_pipeline = Mock()
        mock_context = Mock()
        mock_build_pipeline.setup_build = Mock(return_value=mock_context)
        mock_build_pipeline.write_file = Mock()
        mock_build_pipeline_class.return_value = mock_build_pipeline

        # Create orchestrator and generate
        orchestrator = WebsiteOrchestrator(use_ai=True)

        with patch('os.makedirs'), patch('builtins.open', create=True):
            result = orchestrator.generate(sample_config, str(tmp_path))

        # Verify enhanced city page generation was called
        mock_content_coordinator.generate_single_city_page.assert_called_once_with(
            sample_config,
            sample_city_page,
            str(tmp_path)
        )

        assert result.success is True

    @patch('src.core.orchestration.website_orchestrator.ContentCoordinator')
    @patch('src.core.orchestration.website_orchestrator.BuildPipeline')
    @patch('src.core.generators.css_generator.CSSGenerator')
    def test_generate_creates_css_assets(
        self,
        mock_css_generator_class,
        mock_build_pipeline_class,
        mock_content_coordinator_class,
        sample_config,
        tmp_path
    ):
        """Test generate() creates CSS assets"""
        # Setup mocks
        mock_content_coordinator = Mock()
        mock_content_coordinator.generate_home_page = Mock(return_value="<html>Home</html>")
        mock_content_coordinator.generate_city_pages = Mock(return_value=[])
        mock_content_coordinator_class.return_value = mock_content_coordinator

        mock_build_pipeline = Mock()
        mock_context = Mock()
        mock_build_pipeline.setup_build = Mock(return_value=mock_context)
        mock_build_pipeline.write_file = Mock()
        mock_build_pipeline_class.return_value = mock_build_pipeline

        mock_css_generator = Mock()
        mock_css_generator.generate_css = Mock(return_value="body { color: red; }")
        mock_css_generator_class.return_value = mock_css_generator

        # Create orchestrator and generate
        orchestrator = WebsiteOrchestrator(use_ai=False)

        with patch('os.makedirs'), patch('builtins.open', create=True):
            result = orchestrator.generate(sample_config, str(tmp_path))

        # Verify CSS generator was called
        mock_css_generator.generate_css.assert_called_once_with(sample_config)

        assert result.success is True


class TestErrorHandling:
    """Test error handling in orchestrator"""

    @patch('src.core.orchestration.website_orchestrator.ContentCoordinator')
    @patch('src.core.orchestration.website_orchestrator.BuildPipeline')
    def test_generate_handles_content_coordinator_error(
        self,
        mock_build_pipeline_class,
        mock_content_coordinator_class,
        sample_config,
        tmp_path
    ):
        """Test generate() handles ContentCoordinator errors"""
        # Setup mocks to raise error
        mock_content_coordinator = Mock()
        mock_content_coordinator.generate_home_page = Mock(
            side_effect=Exception("Content generation failed")
        )
        mock_content_coordinator_class.return_value = mock_content_coordinator

        mock_build_pipeline = Mock()
        mock_context = Mock()
        mock_build_pipeline.setup_build = Mock(return_value=mock_context)
        mock_build_pipeline_class.return_value = mock_build_pipeline

        # Create orchestrator and generate
        orchestrator = WebsiteOrchestrator(use_ai=False)
        result = orchestrator.generate(sample_config, str(tmp_path))

        # Verify error was handled
        assert result.success is False
        assert result.errors is not None
        assert "Content generation failed" in result.errors
        assert len(result.generated_files) == 0

    @patch('src.core.orchestration.website_orchestrator.ContentCoordinator')
    @patch('src.core.orchestration.website_orchestrator.BuildPipeline')
    def test_generate_handles_build_pipeline_error(
        self,
        mock_build_pipeline_class,
        mock_content_coordinator_class,
        sample_config,
        tmp_path
    ):
        """Test generate() handles BuildPipeline errors"""
        # Setup mocks to raise error
        mock_build_pipeline = Mock()
        mock_build_pipeline.setup_build = Mock(
            side_effect=Exception("Build setup failed")
        )
        mock_build_pipeline_class.return_value = mock_build_pipeline

        # Create orchestrator and generate
        orchestrator = WebsiteOrchestrator(use_ai=False)
        result = orchestrator.generate(sample_config, str(tmp_path))

        # Verify error was handled
        assert result.success is False
        assert result.errors is not None
        assert "Build setup failed" in result.errors


class TestGenerationResult:
    """Test GenerationResult dataclass"""

    def test_generation_result_success(self):
        """Test GenerationResult creation for success"""
        result = GenerationResult(
            success=True,
            generated_files=["index.html", "city.html"]
        )

        assert result.success is True
        assert len(result.generated_files) == 2
        assert result.errors is None

    def test_generation_result_failure(self):
        """Test GenerationResult creation for failure"""
        result = GenerationResult(
            success=False,
            generated_files=[],
            errors="Generation failed"
        )

        assert result.success is False
        assert len(result.generated_files) == 0
        assert result.errors == "Generation failed"


class TestGenerationError:
    """Test GenerationError exception"""

    def test_generation_error_raised(self):
        """Test GenerationError can be raised"""
        with pytest.raises(GenerationError) as exc_info:
            raise GenerationError("Test error")

        assert str(exc_info.value) == "Test error"

    def test_generation_error_is_exception(self):
        """Test GenerationError is an Exception subclass"""
        error = GenerationError("Test")
        assert isinstance(error, Exception)


class TestSetupBuildEnvironment:
    """Test build environment setup"""

    @patch('src.core.orchestration.website_orchestrator.BuildPipeline')
    def test_setup_build_environment_calls_pipeline(
        self,
        mock_build_pipeline_class,
        tmp_path
    ):
        """Test _setup_build_environment() calls BuildPipeline.setup_build()"""
        mock_build_pipeline = Mock()
        mock_context = Mock()
        mock_build_pipeline.setup_build = Mock(return_value=mock_context)
        mock_build_pipeline_class.return_value = mock_build_pipeline

        orchestrator = WebsiteOrchestrator()
        orchestrator.build_pipeline = mock_build_pipeline

        result_context = orchestrator._setup_build_environment()

        mock_build_pipeline.setup_build.assert_called_once()
        assert result_context == mock_context


class TestGenerateAssets:
    """Test asset generation"""

    @patch('src.core.generators.css_generator.CSSGenerator')
    def test_generate_assets_creates_css_directory(
        self,
        mock_css_generator_class,
        sample_config,
        tmp_path
    ):
        """Test _generate_assets() creates CSS directory"""
        mock_css_generator = Mock()
        mock_css_generator.generate_css = Mock(return_value="/* CSS */")
        mock_css_generator_class.return_value = mock_css_generator

        orchestrator = WebsiteOrchestrator()

        with patch('builtins.open', create=True):
            assets = orchestrator._generate_assets(sample_config, str(tmp_path))

        # Verify CSS directory was created
        css_dir = tmp_path / "css"
        assert css_dir.exists()

        # Verify JS directory was created
        js_dir = tmp_path / "js"
        assert js_dir.exists()

    @patch('src.core.generators.css_generator.CSSGenerator')
    def test_generate_assets_creates_css_file(
        self,
        mock_css_generator_class,
        sample_config,
        tmp_path
    ):
        """Test _generate_assets() creates CSS file"""
        mock_css_generator = Mock()
        mock_css_generator.generate_css = Mock(return_value="body { margin: 0; }")
        mock_css_generator_class.return_value = mock_css_generator

        orchestrator = WebsiteOrchestrator()
        assets = orchestrator._generate_assets(sample_config, str(tmp_path))

        # Verify CSS file path is in assets list
        assert len(assets) > 0
        assert any("style.css" in asset for asset in assets)

        # Verify CSS generator was called
        mock_css_generator.generate_css.assert_called_once_with(sample_config)
