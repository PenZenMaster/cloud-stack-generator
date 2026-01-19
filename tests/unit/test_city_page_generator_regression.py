"""
Unit Tests for City Page Generator - City Image Pool Regression Fix
Path: E:/projects/cloud-stack-generator/tests/unit/test_city_page_generator_regression.py

Description:
Regression tests for city page image pool assignment (Issue #1).
Tests verify that pool images override explicit city images when configured.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-01-19

Last Modified Date:
2025-01-19

Comments:
* v1.00 - Regression tests for city page pool image assignment fix
"""

import pytest
import sys
import os
from unittest.mock import MagicMock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.generators.city_page_generator import CityPageGenerator


class MockBranding:
    """Mock branding configuration"""
    def __init__(self, **kwargs):
        self.city_page_image_pool = kwargs.get('city_page_image_pool', [])
        self.primary_color = kwargs.get('primary_color', '#007bff')
        self.secondary_color = kwargs.get('secondary_color', '#6c757d')


class MockCityImage:
    """Mock city image configuration"""
    def __init__(self, **kwargs):
        self.image_url = kwargs.get('image_url', '')
        self.alt_text = kwargs.get('alt_text', '')
        self.caption = kwargs.get('caption', '')


class MockCityPage:
    """Mock city page configuration"""
    def __init__(self, **kwargs):
        self.city_name = kwargs.get('city_name', 'Test City')
        self.slug = kwargs.get('slug', 'test-city')
        self.state = kwargs.get('state', 'TS')
        self.city_image = kwargs.get('city_image', None)
        self.header_image = kwargs.get('header_image', None)


class MockClientConfig:
    """Mock client configuration"""
    def __init__(self, **kwargs):
        self.branding = kwargs.get('branding', MockBranding())
        self.city_pages = kwargs.get('city_pages', [])
        self.business = MagicMock()
        self.business.business_name = 'Test Business'
        self.business.industry = 'Professional Services'
        self.business.domain = 'https://testbusiness.com'
        self.contact = MagicMock()
        self.contact.phone = '(555) 123-4567'


class TestCityPageImagePoolAssignment:
    """Test city page image pool assignment logic (Issue #1 regression fix)"""

    @pytest.fixture
    def generator(self):
        """Create CityPageGenerator instance"""
        config = MockClientConfig()
        gen = CityPageGenerator(config)
        gen.template_loader = MagicMock()  # Mock template loader
        return gen

    def test_assign_pool_image_augments_wikipedia_image(self, generator):
        """Test that pool images augment (not replace) existing Wikipedia images"""
        # Setup: City page with existing Wikipedia image
        city_page = MockCityPage(
            city_name='Elmwood Park, Illinois',
            slug='elmwood-park-illinois'
        )
        city_page.city_image = MockCityImage(
            image_url='https://upload.wikimedia.org/wikipedia/commons/123/elmwood.jpg',
            alt_text='View of Elmwood Park',
            caption='Wikipedia - Elmwood Park, Illinois'
        )
        city_page.header_image = MockCityImage()  # Initially empty

        # Setup: Config with pool images
        generator.config.city_pages = [city_page]
        generator.config.branding.city_page_image_pool = [
            'images/copper-scupper-box-1.jpg',
            'images/copper-scupper-box-2.jpg',
            'images/copper-scupper-box-3.jpg'
        ]

        # Execute
        generator._assign_city_image_from_pool(city_page)

        # Assert: Pool image goes to header_image, Wikipedia image preserved in city_image
        assert city_page.header_image.image_url == 'images/copper-scupper-box-1.jpg'
        assert city_page.city_image.image_url == 'https://upload.wikimedia.org/wikipedia/commons/123/elmwood.jpg'
        assert city_page.city_image.caption == 'Wikipedia - Elmwood Park, Illinois'

    def test_assign_pool_image_cycles_through_pool(self, generator):
        """Test that pool images are assigned sequentially with cycling"""
        # Setup: Multiple city pages with Wikipedia images
        city_pages = [
            MockCityPage(city_name='City 1', slug='city-1', city_image=MockCityImage(image_url='wikipedia1.jpg')),
            MockCityPage(city_name='City 2', slug='city-2', city_image=MockCityImage(image_url='wikipedia2.jpg')),
            MockCityPage(city_name='City 3', slug='city-3', city_image=MockCityImage(image_url='wikipedia3.jpg')),
            MockCityPage(city_name='City 4', slug='city-4', city_image=MockCityImage(image_url='wikipedia4.jpg'))
        ]
        # Initialize header_image for all
        for cp in city_pages:
            cp.header_image = MockCityImage()

        # Setup: Pool with 3 images (fewer than city pages)
        generator.config.city_pages = city_pages
        generator.config.branding.city_page_image_pool = [
            'images/pool-image-1.jpg',
            'images/pool-image-2.jpg',
            'images/pool-image-3.jpg'
        ]

        # Execute: Assign pool images to all city pages
        for city_page in city_pages:
            generator._assign_city_image_from_pool(city_page)

        # Assert: Pool images should cycle through header_image, Wikipedia preserved
        assert city_pages[0].header_image.image_url == 'images/pool-image-1.jpg'
        assert city_pages[1].header_image.image_url == 'images/pool-image-2.jpg'
        assert city_pages[2].header_image.image_url == 'images/pool-image-3.jpg'
        assert city_pages[3].header_image.image_url == 'images/pool-image-1.jpg'  # Cycles back
        # Wikipedia images should be untouched
        assert city_pages[0].city_image.image_url == 'wikipedia1.jpg'
        assert city_pages[1].city_image.image_url == 'wikipedia2.jpg'

    def test_assign_pool_image_no_pool_configured(self, generator):
        """Test behavior when no pool images are configured"""
        # Setup: City page with header_image
        city_page = MockCityPage(city_name='Test City')
        city_page.header_image = MockCityImage()  # Empty initially

        # Setup: No pool images
        generator.config.city_pages = [city_page]
        generator.config.branding.city_page_image_pool = []

        # Execute
        generator._assign_city_image_from_pool(city_page)

        # Assert: header_image should remain empty
        assert city_page.header_image.image_url == ''

    def test_assign_pool_image_empty_pool(self, generator):
        """Test behavior when pool is empty list"""
        city_page = MockCityPage(city_name='Test City')
        city_page.header_image = MockCityImage()

        generator.config.city_pages = [city_page]
        generator.config.branding.city_page_image_pool = []

        generator._assign_city_image_from_pool(city_page)

        # Should not set header_image when pool is empty
        assert city_page.header_image.image_url == ''

    def test_assign_pool_image_no_pool_attribute(self, generator):
        """Test behavior when branding has no city_page_image_pool attribute"""
        city_page = MockCityPage(city_name='Test City')
        city_page.header_image = MockCityImage()

        # Remove pool attribute
        if hasattr(generator.config.branding, 'city_page_image_pool'):
            delattr(generator.config.branding, 'city_page_image_pool')

        generator.config.city_pages = [city_page]

        generator._assign_city_image_from_pool(city_page)

        # Should not set header_image when pool doesn't exist
        assert city_page.header_image.image_url == ''

    def test_assign_pool_image_creates_header_image_if_none(self, generator):
        """Test that header image is created if it doesn't exist"""
        city_page = MockCityPage(city_name='Test City')
        city_page.header_image = None  # No existing header image

        generator.config.city_pages = [city_page]
        generator.config.branding.city_page_image_pool = ['images/pool-1.jpg']

        generator._assign_city_image_from_pool(city_page)

        # Should create header_image and assign pool image
        assert city_page.header_image is not None
        assert city_page.header_image.image_url == 'images/pool-1.jpg'

    def test_assign_pool_image_sets_default_alt_text(self, generator):
        """Test that default alt text is set when not present"""
        city_page = MockCityPage(city_name='Chicago, Illinois')
        city_page.header_image = MockCityImage(alt_text='')

        generator.config.city_pages = [city_page]
        generator.config.branding.city_page_image_pool = ['images/pool-1.jpg']

        generator._assign_city_image_from_pool(city_page)

        # Should set default alt text with business industry
        assert 'Professional Services services in Chicago, Illinois' in city_page.header_image.alt_text

    def test_assign_pool_image_preserves_existing_alt_text(self, generator):
        """Test that existing alt text is preserved"""
        city_page = MockCityPage(city_name='Test City')
        city_page.header_image = MockCityImage(alt_text='Custom alt text')

        generator.config.city_pages = [city_page]
        generator.config.branding.city_page_image_pool = ['images/pool-1.jpg']

        generator._assign_city_image_from_pool(city_page)

        # Should preserve existing alt text
        assert city_page.header_image.alt_text == 'Custom alt text'

    def test_path_normalization_absolute_path(self, generator):
        """Test that absolute local paths are normalized to relative web paths"""
        city_page = MockCityPage(city_name='Test City')
        city_page.header_image = MockCityImage()

        generator.config.city_pages = [city_page]
        # Absolute Windows path
        generator.config.branding.city_page_image_pool = [
            'D:/OneDrive/RankRocket/Clients/Adventure Marketing/Salvo Metal/GBP/images/processed/copper-scupper-box-206-generated-5.jpg'
        ]

        generator._assign_city_image_from_pool(city_page)

        # Should normalize to relative web path
        assert city_page.header_image.image_url == 'images/copper-scupper-box-206-generated-5.jpg'
        assert not city_page.header_image.image_url.startswith('D:/')
        assert not city_page.header_image.image_url.startswith('file:///')

    def test_real_world_scenario_salvo_metal_works(self, generator):
        """Test real-world scenario from corrected Issue #1 (Salvo Metal Works config)"""
        # Setup: Simulate Salvo Metal Works configuration
        city_page = MockCityPage(
            city_name='Elmwood Park, Illinois',
            slug='elmwood-park-illinois',
            city_image=MockCityImage(
                image_url='https://upload.wikimedia.org/wikipedia/commons/abc/elmwood.jpg',
                alt_text='View of Elmwood Park',
                caption='Wikipedia - Elmwood Park, Illinois'
            )
        )
        city_page.header_image = MockCityImage()  # Initially empty

        # Pool with absolute paths (as they appear in real config)
        pool_images = [f'D:/OneDrive/Clients/images/copper-scupper-box-206-generated-{i}.jpg' for i in range(1, 21)]

        generator.config.city_pages = [city_page]
        generator.config.branding.city_page_image_pool = pool_images

        # Execute
        generator._assign_city_image_from_pool(city_page)

        # Assert: Pool image goes to header, Wikipedia preserved, path normalized
        assert city_page.header_image.image_url == 'images/copper-scupper-box-206-generated-1.jpg'
        assert city_page.city_image.image_url == 'https://upload.wikimedia.org/wikipedia/commons/abc/elmwood.jpg'
        assert city_page.city_image.caption == 'Wikipedia - Elmwood Park, Illinois'
        # Verify normalization (no absolute path in output)
        assert not city_page.header_image.image_url.startswith('D:/')
        assert 'wikimedia.org' in city_page.city_image.image_url.lower()


if __name__ == '__main__':
    pytest.main([__file__])
