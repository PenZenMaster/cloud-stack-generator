"""
AI Content Generation Example
Path: E:/projects/cloud-stack-generator/examples/ai_content_example.py

Description:
Example script demonstrating how to use the AI content generation service
with the centralized environment configuration.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-19

Usage:
    python examples/ai_content_example.py
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.config import EnvironmentConfig, initialize_environment
from src.core.services.ai_content_service import AIContentService
from src.core.services.content_cache import ContentCache
from src.core.generators.content import HomeContentGenerator, CityContentGenerator


def main():
    """Main example function"""

    print("=" * 70)
    print("AI Content Generation - Example Script")
    print("=" * 70)
    print()

    # Initialize and validate environment
    initialize_environment()

    # Get environment configuration status
    config = EnvironmentConfig.get_all_settings()

    # Check OpenAI configuration
    if not config['openai']['configured']:
        print("ERROR: OpenAI API key not configured!")
        print()
        print("To use AI content generation:")
        print("  1. Copy .env.example to .env")
        print("  2. Add your OpenAI API key to the .env file")
        print("  3. Get API key from: https://platform.openai.com/api-keys")
        print()
        print("The system will fall back to template-based generation.")
        print()
        return

    # Initialize AI services
    print("Initializing AI services...")
    ai_service = AIContentService()
    cache = ContentCache()

    print(f"  AI Service: {'Available' if ai_service.is_available() else 'Not available'}")
    print(f"  Cache: {'Enabled' if cache.is_enabled() else 'Disabled'}")
    print()

    if not ai_service.is_available():
        print("AI service is not available. Using template-based generation.")
        print()

    # Create content generators
    home_gen = HomeContentGenerator(ai_service=ai_service, cache=cache)
    city_gen = CityContentGenerator(ai_service=ai_service, cache=cache)

    # Example: Create a mock configuration
    # In real usage, you would load this from a YAML file
    print("Creating example business configuration...")
    from unittest.mock import Mock

    mock_config = Mock()

    # Business details
    mock_config.business = Mock()
    mock_config.business.business_name = "Example Plumbing Co"
    mock_config.business.industry = "Plumbing"
    mock_config.business.company_overview = "We provide professional plumbing services"
    mock_config.business.tagline = "Your trusted plumbing experts"
    mock_config.business.years_in_business = 15
    mock_config.business.why_choose_us = [
        "Licensed and Insured",
        "24/7 Emergency Service",
        "Free Estimates"
    ]
    mock_config.business.service_guarantee = "100% satisfaction guaranteed"
    mock_config.business.company_stats = {"projects": "500+", "years": "15"}
    mock_config.business.service_area_description = "Serving the greater metro area"

    # Helper methods
    mock_config.business.get_hero_tagline = Mock(return_value="Your trusted plumbing experts")
    mock_config.business.get_years_display = Mock(return_value="15+ Years of Excellence")

    # Contact details
    mock_config.contact = Mock()
    mock_config.contact.phone = "555-1234"
    mock_config.contact.email = "info@example.com"
    mock_config.contact.office_phone = "555-5678"
    mock_config.contact.response_time_promise = "We respond within 1 hour"
    mock_config.contact.business_hours = {
        "monday": "8am-5pm",
        "tuesday": "8am-5pm",
        "wednesday": "8am-5pm",
        "thursday": "8am-5pm",
        "friday": "8am-5pm"
    }
    mock_config.contact.get_primary_phone = Mock(return_value="555-1234")
    mock_config.contact.has_multiple_contacts = Mock(return_value=True)

    # Services
    mock_config.services = [
        Mock(name="Pipe Repair", description="Expert pipe repair services"),
        Mock(name="Drain Cleaning", description="Professional drain cleaning")
    ]

    # Products
    mock_config.products = [
        Mock(name="Water Heaters", description="High-efficiency water heaters")
    ]

    mock_config.faq = []
    mock_config.pages = []

    print()
    print("-" * 70)
    print("Example 1: Generate Home Page Content")
    print("-" * 70)
    print()

    # Generate home page content
    print("Generating home page content...")
    home_content = home_gen.generate_enhanced_home_content(mock_config, use_ai=True)

    if home_content:
        print("SUCCESS! Generated home page content:")
        print()
        # Show first 500 characters
        preview = home_content[:500]
        print(preview)
        if len(home_content) > 500:
            print(f"... ({len(home_content) - 500} more characters)")
        print()
        print(f"Total length: {len(home_content)} characters")
    else:
        print("Content generation returned None (AI may not be configured)")

    print()
    print("-" * 70)
    print("Example 2: Generate City Page Content")
    print("-" * 70)
    print()

    # Generate city page content
    print("Generating city page content for Denver...")
    city_content = city_gen.generate_city_content(mock_config, city="Denver", use_ai=True)

    if city_content:
        print("SUCCESS! Generated city page content:")
        print()
        # Show first 500 characters
        preview = city_content[:500]
        print(preview)
        if len(city_content) > 500:
            print(f"... ({len(city_content) - 500} more characters)")
        print()
        print(f"Total length: {len(city_content)} characters")
    else:
        print("Content generation returned None (AI may not be configured)")

    print()
    print("-" * 70)
    print("Example 3: Check Cache Statistics")
    print("-" * 70)
    print()

    if cache.is_enabled():
        stats = cache.get_stats()
        print("Cache Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Valid entries: {stats['valid_entries']}")
        print(f"  Expired entries: {stats['expired_entries']}")
        print(f"  Cache directory: {stats['cache_dir']}")
    else:
        print("Cache is disabled")

    print()
    print("-" * 70)
    print("Example 4: Get AI Service Statistics")
    print("-" * 70)
    print()

    stats = ai_service.get_usage_stats()
    print("AI Service Statistics:")
    print(f"  Enabled: {stats['enabled']}")
    print(f"  Available: {stats['available']}")
    print(f"  Model: {stats['model']}")
    print(f"  Max tokens: {stats['max_tokens']}")
    print(f"  Temperature: {stats['temperature']}")
    print(f"  OpenAI installed: {stats['openai_installed']}")
    print(f"  API key configured: {stats['api_key_configured']}")

    print()
    print("=" * 70)
    print("Example completed!")
    print("=" * 70)


if __name__ == '__main__':
    main()
