"""
Module/Script Name: Test Website Generator
Path: tests/unit/test_website_generator.py

Description:
Unit tests for WebsiteGenerator facade class

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-12-21

Comments:
* v1.00 - Initial comprehensive test suite for website_generator.py
"""

from unittest.mock import Mock, patch

from src.core.website_generator import (
    WebsiteGenerator,
    GenerationResult,
    GenerationError
)
from src.core.config.models import ClientConfig


class TestWebsiteGeneratorInitialization:
    """Test WebsiteGenerator initialization"""

    @patch('src.core.website_generator.WebsiteOrchestrator')
    def test_init_with_ai_enabled(self, mock_orchestrator_class):
        """Test initialization with AI enabled (default)"""
        mock_orchestrator = Mock()
        mock_orchestrator.ai_service = Mock()
        mock_orchestrator.content_cache = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        generator = WebsiteGenerator(use_ai=True)

        assert generator.use_ai is True
        assert generator.output_dir is None
        assert generator.config is None
        mock_orchestrator_class.assert_called_once_with(use_ai=True)
        assert generator.ai_service == mock_orchestrator.ai_service
        assert generator.content_cache == mock_orchestrator.content_cache

    @patch('src.core.website_generator.WebsiteOrchestrator')
    def test_init_with_ai_disabled(self, mock_orchestrator_class):
        """Test initialization with AI disabled"""
        mock_orchestrator = Mock()
        mock_orchestrator.ai_service = Mock()
        mock_orchestrator.content_cache = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        generator = WebsiteGenerator(use_ai=False)

        assert generator.use_ai is False
        mock_orchestrator_class.assert_called_once_with(use_ai=False)

    @patch('src.core.website_generator.WebsiteOrchestrator')
    def test_init_default_ai_setting(self, mock_orchestrator_class):
        """Test initialization uses AI by default"""
        mock_orchestrator = Mock()
        mock_orchestrator.ai_service = Mock()
        mock_orchestrator.content_cache = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        generator = WebsiteGenerator()

        assert generator.use_ai is True
        mock_orchestrator_class.assert_called_once_with(use_ai=True)


class TestWebsiteGeneratorGenerate:
    """Test WebsiteGenerator.generate() method"""

    @patch('src.core.website_generator.WebsiteOrchestrator')
    def test_generate_success(self, mock_orchestrator_class):
        """Test successful website generation"""
        # Setup mocks
        mock_orchestrator = Mock()
        mock_result = Mock(spec=GenerationResult)
        mock_result.success = True
        mock_result.pages_generated = 10
        mock_orchestrator.generate.return_value = mock_result
        mock_orchestrator.ai_service = Mock()
        mock_orchestrator.content_cache = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        # Create test config
        config = Mock(spec=ClientConfig)
        config.business_name = "Test Business"
        output_dir = "/path/to/output"

        # Execute
        generator = WebsiteGenerator()
        result = generator.generate(config, output_dir)

        # Verify
        assert result == mock_result
        assert result.success is True
        assert generator.output_dir == output_dir
        assert generator.config == config
        mock_orchestrator.generate.assert_called_once_with(config, output_dir)

    @patch('src.core.website_generator.WebsiteOrchestrator')
    def test_generate_failure(self, mock_orchestrator_class):
        """Test website generation failure handling"""
        # Setup mocks
        mock_orchestrator = Mock()
        mock_result = Mock(spec=GenerationResult)
        mock_result.success = False
        mock_result.error = "Generation failed"
        mock_orchestrator.generate.return_value = mock_result
        mock_orchestrator.ai_service = Mock()
        mock_orchestrator.content_cache = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        config = Mock(spec=ClientConfig)
        output_dir = "/path/to/output"

        # Execute
        generator = WebsiteGenerator()
        result = generator.generate(config, output_dir)

        # Verify failure handling
        assert result.success is False
        assert result.error == "Generation failed"

    @patch('src.core.website_generator.WebsiteOrchestrator')
    def test_generate_stores_config_and_output_dir(self, mock_orchestrator_class):
        """Test that generate stores config and output_dir for backward compatibility"""
        mock_orchestrator = Mock()
        mock_result = Mock(spec=GenerationResult)
        mock_orchestrator.generate.return_value = mock_result
        mock_orchestrator.ai_service = Mock()
        mock_orchestrator.content_cache = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        config = Mock(spec=ClientConfig)
        output_dir = "/test/output"

        generator = WebsiteGenerator()

        # Before generation
        assert generator.config is None
        assert generator.output_dir is None

        # After generation
        generator.generate(config, output_dir)
        assert generator.config == config
        assert generator.output_dir == output_dir

    @patch('src.core.website_generator.WebsiteOrchestrator')
    def test_generate_with_different_configs(self, mock_orchestrator_class):
        """Test generating with multiple different configurations"""
        mock_orchestrator = Mock()
        mock_result = Mock(spec=GenerationResult)
        mock_result.success = True
        mock_orchestrator.generate.return_value = mock_result
        mock_orchestrator.ai_service = Mock()
        mock_orchestrator.content_cache = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        generator = WebsiteGenerator()

        # First generation
        config1 = Mock(spec=ClientConfig)
        config1.business_name = "Business 1"
        result1 = generator.generate(config1, "/output1")

        # Second generation
        config2 = Mock(spec=ClientConfig)
        config2.business_name = "Business 2"
        result2 = generator.generate(config2, "/output2")

        # Verify both calls delegated correctly
        assert mock_orchestrator.generate.call_count == 2
        assert generator.config == config2  # Should store latest
        assert generator.output_dir == "/output2"  # Should store latest


class TestWebsiteGeneratorBackwardCompatibility:
    """Test backward compatibility features"""

    @patch('src.core.website_generator.WebsiteOrchestrator')
    def test_exposes_ai_service(self, mock_orchestrator_class):
        """Test that ai_service is exposed for backward compatibility"""
        mock_ai_service = Mock()
        mock_orchestrator = Mock()
        mock_orchestrator.ai_service = mock_ai_service
        mock_orchestrator.content_cache = Mock()
        mock_orchestrator_class.return_value = mock_orchestrator

        generator = WebsiteGenerator()

        assert generator.ai_service == mock_ai_service

    @patch('src.core.website_generator.WebsiteOrchestrator')
    def test_exposes_content_cache(self, mock_orchestrator_class):
        """Test that content_cache is exposed for backward compatibility"""
        mock_content_cache = Mock()
        mock_orchestrator = Mock()
        mock_orchestrator.ai_service = Mock()
        mock_orchestrator.content_cache = mock_content_cache
        mock_orchestrator_class.return_value = mock_orchestrator

        generator = WebsiteGenerator()

        assert generator.content_cache == mock_content_cache


class TestGenerationResultImport:
    """Test that exports are available"""

    def test_generation_result_exported(self):
        """Test GenerationResult is exported"""
        from src.core.website_generator import GenerationResult
        assert GenerationResult is not None

    def test_generation_error_exported(self):
        """Test GenerationError is exported"""
        assert GenerationError is not None

    def test_website_generator_exported(self):
        """Test WebsiteGenerator is exported"""
        from src.core.website_generator import WebsiteGenerator
        assert WebsiteGenerator is not None
