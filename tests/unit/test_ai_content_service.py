"""
Unit Tests for AI Content Service
Path: E:/projects/cloud-stack-generator/tests/unit/test_ai_content_service.py

Description:
Comprehensive unit tests for the AI content service with mocked OpenAI API responses.
Tests include successful generation, error handling, fallback behavior, and caching.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-19

Last Modified Date:
2025-10-19

Comments:
* v1.00 - Initial creation with comprehensive test coverage
"""

import pytest
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.core.services.ai_content_service import AIContentService
from src.core.services.content_cache import ContentCache


class TestAIContentService:
    """Test suite for AIContentService"""

    @pytest.fixture
    def mock_config(self):
        """Create a mock client configuration for testing"""
        config = Mock()

        # Business details
        config.business = Mock()
        config.business.business_name = "Test Plumbing Co"
        config.business.industry = "Plumbing"
        config.business.company_overview = "We are a trusted plumbing company"
        config.business.tagline = "Your trusted plumbing experts"
        config.business.years_in_business = 15
        config.business.why_choose_us = [
            "Licensed and Insured",
            "24/7 Emergency Service",
            "Free Estimates"
        ]
        config.business.service_guarantee = "100% satisfaction guaranteed"
        config.business.company_stats = {"projects": "500+", "years": "15"}

        # Contact details
        config.contact = Mock()
        config.contact.phone = "555-1234"
        config.contact.email = "info@testplumbing.com"
        config.contact.office_phone = "555-5678"
        config.contact.business_hours = {"monday": "8am-5pm"}
        config.contact.response_time_promise = "We respond within 1 hour"
        config.contact.get_primary_phone = Mock(return_value="555-1234")
        config.contact.has_multiple_contacts = Mock(return_value=True)

        # Services and products
        config.services = [
            Mock(name="Pipe Repair", description="Expert pipe repair services"),
            Mock(name="Drain Cleaning", description="Professional drain cleaning")
        ]
        config.products = [
            Mock(name="Water Heaters", description="High-efficiency water heaters"),
        ]

        config.faq = []
        config.pages = []

        return config

    @pytest.fixture
    def mock_openai_response(self):
        """Create a mock OpenAI API response"""
        response = Mock()
        response.choices = [Mock()]
        response.choices[0].message = Mock()
        response.choices[0].message.content = """
        <section class="hero">
            <h1>Welcome to Test Plumbing Co</h1>
            <p>Your trusted plumbing experts</p>
        </section>
        <section class="about">
            <h2>About Us</h2>
            <p>We are a trusted plumbing company with 15 years of experience.</p>
        </section>
        """
        return response

    def test_initialization_with_api_key(self):
        """Test AI service initializes correctly with API key"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key-123'}):
            with patch('src.core.services.ai_content_service.OPENAI_AVAILABLE', True):
                with patch('openai.OpenAI') as mock_openai:
                    service = AIContentService()

                    assert service.api_key == 'test-key-123'
                    assert service.model == 'gpt-4o-mini'
                    assert service.max_tokens == 2000
                    assert service.temperature == 0.7
                    mock_openai.assert_called_once()

    def test_initialization_without_api_key(self):
        """Test AI service handles missing API key gracefully"""
        with patch.dict(os.environ, {}, clear=True):
            service = AIContentService()

            assert not service.enabled
            assert not service.is_available()

    def test_is_available_when_enabled(self):
        """Test is_available returns True when properly configured"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.services.ai_content_service.OPENAI_AVAILABLE', True):
                with patch('openai.OpenAI'):
                    service = AIContentService()
                    assert service.is_available()

    def test_is_available_when_disabled(self):
        """Test is_available returns False when disabled"""
        with patch.dict(os.environ, {'AI_CONTENT_ENABLED': 'false'}):
            service = AIContentService()
            assert not service.is_available()

    def test_generate_home_content_success(self, mock_config, mock_openai_response):
        """Test successful home content generation"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.services.ai_content_service.OPENAI_AVAILABLE', True):
                with patch('openai.OpenAI') as mock_openai_class:
                    mock_client = Mock()
                    mock_client.chat.completions.create.return_value = mock_openai_response
                    mock_openai_class.return_value = mock_client

                    service = AIContentService()
                    content = service.generate_home_content(mock_config, use_enhanced=True)

                    assert content is not None
                    assert '<section class="hero">' in content
                    assert 'Test Plumbing Co' in content

                    # Verify API was called with correct parameters
                    mock_client.chat.completions.create.assert_called_once()
                    call_args = mock_client.chat.completions.create.call_args

                    assert call_args.kwargs['model'] == 'gpt-4o-mini'
                    assert call_args.kwargs['max_tokens'] == 2000
                    assert call_args.kwargs['temperature'] == 0.7
                    assert len(call_args.kwargs['messages']) == 2

    def test_generate_home_content_when_unavailable(self, mock_config):
        """Test home content generation returns None when service unavailable"""
        with patch.dict(os.environ, {}, clear=True):
            service = AIContentService()
            content = service.generate_home_content(mock_config)

            assert content is None

    def test_generate_city_content_success(self, mock_config, mock_openai_response):
        """Test successful city content generation"""
        mock_openai_response.choices[0].message.content = """
        <section class="hero">
            <h2>Plumbing Services in Denver</h2>
        </section>
        """

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.services.ai_content_service.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_client.chat.completions.create.return_value = mock_openai_response
                mock_openai_class.return_value = mock_client

                service = AIContentService()
                content = service.generate_city_content(mock_config, city="Denver", state="CO")

                assert content is not None
                assert 'Denver' in content

    def test_generate_content_handles_empty_response(self, mock_config):
        """Test handling of empty API response"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = None

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.services.ai_content_service.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai_class.return_value = mock_client

                service = AIContentService()
                content = service.generate_home_content(mock_config)

                assert content is None

    def test_generate_content_handles_api_error(self, mock_config):
        """Test handling of OpenAI API errors"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.services.ai_content_service.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_client.chat.completions.create.side_effect = Exception("API Error")
                mock_openai_class.return_value = mock_client

                service = AIContentService()
                content = service.generate_home_content(mock_config)

                assert content is None

    def test_build_home_page_prompt(self, mock_config):
        """Test home page prompt includes all necessary context"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.services.ai_content_service.OpenAI'):
                service = AIContentService()

                context = {
                    'business_name': 'Test Business',
                    'industry': 'Plumbing',
                    'services': [{'name': 'Service 1', 'description': 'Desc 1'}],
                    'products': [{'name': 'Product 1', 'description': 'Desc 1'}],
                }

                prompt = service._build_home_page_prompt(context)

                assert 'Test Business' in prompt
                assert 'Plumbing' in prompt
                assert 'Service 1' in prompt
                assert 'Product 1' in prompt
                assert 'SEO' in prompt
                assert 'HTML' in prompt

    def test_build_city_page_prompt(self, mock_config):
        """Test city page prompt includes location context"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.services.ai_content_service.OpenAI'):
                service = AIContentService()

                context = {
                    'business_name': 'Test Business',
                    'industry': 'Plumbing',
                    'city': 'Denver',
                    'state': 'CO',
                    'services': []
                }

                prompt = service._build_city_page_prompt(context)

                assert 'Denver' in prompt
                assert 'Test Business' in prompt
                assert 'local' in prompt.lower()

    def test_get_usage_stats(self):
        """Test usage statistics reporting"""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'}):
            with patch('src.core.services.ai_content_service.OpenAI'):
                service = AIContentService()
                stats = service.get_usage_stats()

                assert 'enabled' in stats
                assert 'available' in stats
                assert 'model' in stats
                assert 'max_tokens' in stats
                assert 'temperature' in stats
                assert stats['model'] == 'gpt-4o-mini'

    def test_custom_model_configuration(self):
        """Test service accepts custom model configuration"""
        with patch('src.core.services.ai_content_service.OpenAI'):
            service = AIContentService(
                api_key='custom-key',
                model='gpt-4',
                max_tokens=4000,
                temperature=0.5
            )

            assert service.model == 'gpt-4'
            assert service.max_tokens == 4000
            assert service.temperature == 0.5


class TestContentCache:
    """Test suite for ContentCache"""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path):
        """Create a temporary cache directory"""
        return tmp_path / "test_cache"

    @pytest.fixture
    def cache(self, temp_cache_dir):
        """Create a ContentCache instance for testing"""
        return ContentCache(cache_dir=temp_cache_dir, ttl_hours=1)

    def test_initialization(self, temp_cache_dir):
        """Test cache initializes correctly"""
        cache = ContentCache(cache_dir=temp_cache_dir)

        assert cache.cache_dir == temp_cache_dir
        assert cache.enabled
        assert cache.ttl_hours == 168
        assert temp_cache_dir.exists()

    def test_initialization_disabled(self, temp_cache_dir):
        """Test cache can be disabled"""
        cache = ContentCache(cache_dir=temp_cache_dir, enabled=False)

        assert not cache.enabled
        assert not cache.is_enabled()

    def test_generate_cache_key(self, cache):
        """Test cache key generation is deterministic"""
        context1 = {'business': 'Test Co', 'city': 'Denver'}
        context2 = {'city': 'Denver', 'business': 'Test Co'}  # Different order

        key1 = cache.generate_cache_key('home_page', context1)
        key2 = cache.generate_cache_key('home_page', context2)

        assert key1 == key2
        assert len(key1) == 64  # SHA256 hex length

    def test_set_and_get_content(self, cache):
        """Test storing and retrieving cached content"""
        context = {'business': 'Test Co', 'city': 'Denver'}
        content = '<section>Test Content</section>'

        # Set content
        success = cache.set('city_page', context, content)
        assert success

        # Get content
        retrieved = cache.get('city_page', context)
        assert retrieved == content

    def test_get_nonexistent_content(self, cache):
        """Test retrieving non-existent cached content"""
        context = {'business': 'Test Co', 'city': 'Austin'}
        retrieved = cache.get('city_page', context)

        assert retrieved is None

    def test_cache_expiration(self, cache, temp_cache_dir):
        """Test cache entries expire after TTL"""
        cache.ttl_hours = 0.001  # Very short TTL for testing

        context = {'business': 'Test Co'}
        content = '<section>Test</section>'

        # Store content
        cache.set('home_page', context, content)

        # Immediately should be available
        assert cache.get('home_page', context) == content

        # After expiration, should be None
        import time
        time.sleep(0.01)  # Sleep longer than TTL

        # Manually expire by modifying the cache file
        cache_key = cache.generate_cache_key('home_page', context)
        cache_file = temp_cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            import json
            with open(cache_file, 'r') as f:
                data = json.load(f)

            # Set expired timestamp
            data['expires_at'] = (datetime.now() - timedelta(hours=1)).isoformat()

            with open(cache_file, 'w') as f:
                json.dump(data, f)

        retrieved = cache.get('home_page', context)
        assert retrieved is None

    def test_invalidate_cache(self, cache):
        """Test cache invalidation"""
        context = {'business': 'Test Co'}
        content = '<section>Test</section>'

        cache.set('home_page', context, content)
        assert cache.get('home_page', context) is not None

        cache.invalidate('home_page', context)
        assert cache.get('home_page', context) is None

    def test_clear_all_cache(self, cache):
        """Test clearing all cache entries"""
        # Add multiple cache entries
        cache.set('home_page', {'business': 'A'}, '<section>A</section>')
        cache.set('home_page', {'business': 'B'}, '<section>B</section>')
        cache.set('city_page', {'business': 'C'}, '<section>C</section>')

        count = cache.clear_all()
        assert count == 3

        # All should be gone
        assert cache.get('home_page', {'business': 'A'}) is None
        assert cache.get('home_page', {'business': 'B'}) is None

    def test_get_stats(self, cache):
        """Test cache statistics"""
        # Add some entries
        cache.set('home_page', {'business': 'A'}, '<section>A</section>')
        cache.set('city_page', {'business': 'B'}, '<section>B</section>')

        stats = cache.get_stats()

        assert stats['enabled'] is True
        assert stats['total_entries'] == 2
        assert stats['valid_entries'] == 2
        assert stats['expired_entries'] == 0
        assert stats['ttl_hours'] == 1

    def test_cache_with_metadata(self, cache):
        """Test caching with metadata"""
        context = {'business': 'Test Co'}
        content = '<section>Test</section>'
        metadata = {'generated_at': str(datetime.now()), 'version': '1.0'}

        cache.set('home_page', context, content, metadata=metadata)

        # Verify metadata is stored
        cache_key = cache.generate_cache_key('home_page', context)
        cache_file = cache.cache_dir / f"{cache_key}.json"

        import json
        with open(cache_file, 'r') as f:
            data = json.load(f)

        assert data['metadata'] == metadata
