#!/usr/bin/env python3
"""
Simple test to verify Wikipedia embed codes are working
"""

import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.generators.city_page_generator import CityPageGenerator
from core.config.parser import ConfigParser


def test_embed_generation():
    """Test that cities with embed codes generate properly."""
    # Load config
    config_path = Path(__file__).parent.parent / "config" / "clients" / "salvo_metal_works_config.yaml"
    parser = ConfigParser(config_path)
    config = parser.load_configuration()
    
    # Find cities with embed codes
    cities_with_embeds = []
    for city_page in config.city_pages:
        if hasattr(city_page.city_image, 'embed_code') and city_page.city_image.embed_code:
            cities_with_embeds.append(city_page.city_name)
            
    print(f"Cities with embed codes: {cities_with_embeds}")
    
    if not cities_with_embeds:
        print("No cities found with embed codes!")
        return False
        
    # Test generation for first city with embed
    test_city = None
    for city_page in config.city_pages:
        if city_page.city_name in cities_with_embeds:
            test_city = city_page
            break
            
    if not test_city:
        print("Could not find test city!")
        return False
        
    print(f"\nTesting generation for: {test_city.city_name}")
    print(f"Embed code length: {len(test_city.city_image.embed_code)} characters")
    print(f"Embed code preview: {test_city.city_image.embed_code[:100]}...")
    
    # Initialize generator
    generator = CityPageGenerator(config)
    
    # Generate the page content
    try:
        content = generator.generate_city_page(test_city)
        
        # Check if embed code appears in content
        if 'city-image' in content and '<a title=' in content:
            print("[SUCCESS] Embed code found in generated content!")
            return True
        elif test_city.city_image.image_url in content:
            print("[PARTIAL] Image URL found but not as embed code")
            return False
        else:
            print("[FAILURE] No image content found")
            return False
            
    except Exception as e:
        print(f"[ERROR] Generation failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_embed_generation()
    sys.exit(0 if success else 1)