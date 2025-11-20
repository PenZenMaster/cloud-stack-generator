"""
Filename: tests/unit/test_city_field_content_generator.py
Path: E:/projects/cloud-stack-generator/tests/unit/test_city_field_content_generator.py
Description: Unit tests for CityFieldContentGenerator

Version: 1.0.0
Date: 2025-11-20
Author: Cloud Stack Generator Team
"""

import sys
import pytest
from unittest.mock import Mock
import os

# Add src directory to path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

from core.generators.content.city_field_content_generator import CityFieldContentGenerator
from core.services.ai_content_service import AIContentService


class TestCityFieldContentGenerator:
    """Test suite for CityFieldContentGenerator"""

    def setup_method(self):
        """Set up each test with mocked AI service"""
        self.mock_ai_service = Mock(spec=AIContentService)
        self.mock_ai_service.is_available.return_value = True
        self.generator = CityFieldContentGenerator(self.mock_ai_service)

    def test_initialization_with_ai_service(self):
        """Test generator initialization with AI service"""
        assert self.generator.ai_service is not None
        assert self.generator.use_ai is True

    def test_initialization_without_ai_service(self):
        """Test generator initialization without AI service"""
        generator = CityFieldContentGenerator(None)
        assert generator.ai_service is None
        assert generator.use_ai is False

    def test_generate_neighborhoods_description_success(self):
        """Test successful neighborhood generation"""
        # Mock the AI service response
        expected_content = "Downtown Tampa, Ybor City, Hyde Park, Westshore"
        self.mock_ai_service._call_openai.return_value = expected_content

        # Generate content
        result = self.generator.generate_neighborhoods_description(
            city_name="Tampa",
            state="FL",
            business_name="Clean Restroom Rentals",
            industry="Portable Restroom Rentals"
        )

        # Verify result
        assert result == expected_content
        self.mock_ai_service._call_openai.assert_called_once()

        # Verify prompt includes city and business info
        call_args = self.mock_ai_service._call_openai.call_args[0][0]
        assert "Tampa" in call_args
        assert "FL" in call_args
        assert "Clean Restroom Rentals" in call_args

    def test_generate_neighborhoods_no_ai_service(self):
        """Test neighborhood generation without AI service"""
        generator = CityFieldContentGenerator(None)

        result = generator.generate_neighborhoods_description(
            city_name="Tampa",
            state="FL",
            business_name="Test Business",
            industry="Test Industry"
        )

        assert result is None

    def test_generate_pain_points_success(self):
        """Test successful pain points generation"""
        expected_content = "Summer heat and humidity, hurricane season preparedness"
        self.mock_ai_service._call_openai.return_value = expected_content

        result = self.generator.generate_pain_points(
            city_name="Tampa",
            state="FL",
            business_name="Clean Restroom Rentals",
            industry="Portable Restroom Rentals"
        )

        assert result == expected_content
        self.mock_ai_service._call_openai.assert_called_once()

    def test_generate_pain_points_with_error(self):
        """Test pain points generation handles errors"""
        self.mock_ai_service._call_openai.side_effect = Exception("API Error")

        result = self.generator.generate_pain_points(
            city_name="Tampa",
            state="FL",
            business_name="Test Business",
            industry="Test Industry"
        )

        assert result is None

    def test_generate_case_studies_success(self):
        """Test successful case study generation"""
        expected_content = "Recently completed project in downtown Tampa..."
        self.mock_ai_service._call_openai.return_value = expected_content

        result = self.generator.generate_case_studies(
            city_name="Tampa",
            state="FL",
            business_name="Clean Restroom Rentals",
            industry="Portable Restroom Rentals"
        )

        assert result == expected_content
        self.mock_ai_service._call_openai.assert_called_once()

        # Verify prompt structure
        call_args = self.mock_ai_service._call_openai.call_args[0][0]
        assert "Tampa" in call_args
        assert "case study" in call_args.lower() or "project" in call_args.lower()

    def test_generate_local_faq_success(self):
        """Test successful local FAQ generation"""
        expected_faqs = "Do you serve downtown Tampa?\nWhat are response times in Tampa Bay?"
        self.mock_ai_service._call_openai.return_value = expected_faqs

        result = self.generator.generate_local_faq(
            city_name="Tampa",
            state="FL",
            business_name="Clean Restroom Rentals",
            industry="Portable Restroom Rentals",
            neighborhoods="Downtown, Ybor City",
            pain_points="Summer heat, hurricane season"
        )

        assert result == expected_faqs
        self.mock_ai_service._call_openai.assert_called_once()

        # Verify prompt includes context
        call_args = self.mock_ai_service._call_openai.call_args[0][0]
        assert "Tampa" in call_args
        assert "FAQ" in call_args

    def test_generate_local_faq_with_context(self):
        """Test FAQ generation uses neighborhoods and pain points context"""
        self.mock_ai_service._call_openai.return_value = "Test FAQ"

        self.generator.generate_local_faq(
            city_name="Tampa",
            state="FL",
            business_name="Test Business",
            industry="Test Industry",
            neighborhoods="Downtown, Westshore",
            pain_points="Hurricane preparedness"
        )

        # Verify context was included in prompt
        call_args = self.mock_ai_service._call_openai.call_args[0][0]
        assert "Downtown, Westshore" in call_args
        assert "Hurricane preparedness" in call_args

    def test_neighborhoods_prompt_structure(self):
        """Test neighborhoods prompt is well-structured"""
        self.mock_ai_service._call_openai.return_value = "Test content"

        self.generator.generate_neighborhoods_description(
            city_name="Tampa",
            state="FL",
            business_name="Test Business",
            industry="Test Industry"
        )

        # Verify prompt structure
        prompt = self.mock_ai_service._call_openai.call_args[0][0]
        assert "Tampa" in prompt
        assert "FL" in prompt
        assert "neighborhood" in prompt.lower() or "landmark" in prompt.lower()

    def test_pain_points_prompt_structure(self):
        """Test pain points prompt is well-structured"""
        self.mock_ai_service._call_openai.return_value = "Test content"

        self.generator.generate_pain_points(
            city_name="Tampa",
            state="FL",
            business_name="Test Business",
            industry="Test Industry"
        )

        # Verify prompt structure
        prompt = self.mock_ai_service._call_openai.call_args[0][0]
        assert "Tampa" in prompt
        assert ("weather" in prompt.lower() or "seasonal" in prompt.lower() or
                "pain point" in prompt.lower())

    def test_case_studies_prompt_structure(self):
        """Test case studies prompt is well-structured"""
        self.mock_ai_service._call_openai.return_value = "Test content"

        self.generator.generate_case_studies(
            city_name="Tampa",
            state="FL",
            business_name="Test Business",
            industry="Test Industry"
        )

        # Verify prompt structure
        prompt = self.mock_ai_service._call_openai.call_args[0][0]
        assert "Tampa" in prompt
        assert ("case study" in prompt.lower() or "project" in prompt.lower() or
                "example" in prompt.lower())

    def test_faq_prompt_structure(self):
        """Test FAQ prompt is well-structured"""
        self.mock_ai_service._call_openai.return_value = "Test FAQ"

        self.generator.generate_local_faq(
            city_name="Tampa",
            state="FL",
            business_name="Test Business",
            industry="Test Industry"
        )

        # Verify prompt structure
        prompt = self.mock_ai_service._call_openai.call_args[0][0]
        assert "Tampa" in prompt
        assert "FAQ" in prompt or "question" in prompt.lower()

    def test_all_methods_handle_empty_strings(self):
        """Test that all methods handle empty existing content"""
        self.mock_ai_service._call_openai.return_value = "Generated content"

        # Test with empty existing_content parameter
        methods = [
            self.generator.generate_neighborhoods_description,
            self.generator.generate_pain_points,
            self.generator.generate_case_studies,
        ]

        for method in methods:
            result = method(
                city_name="Tampa",
                state="FL",
                business_name="Test",
                industry="Test",
                existing_content=""
            )
            assert result == "Generated content"

    def test_all_methods_return_none_on_api_failure(self):
        """Test that all methods return None when AI service returns None"""
        self.mock_ai_service._call_openai.return_value = None

        methods = [
            self.generator.generate_neighborhoods_description,
            self.generator.generate_pain_points,
            self.generator.generate_case_studies,
        ]

        for method in methods:
            result = method(
                city_name="Tampa",
                state="FL",
                business_name="Test",
                industry="Test"
            )
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
