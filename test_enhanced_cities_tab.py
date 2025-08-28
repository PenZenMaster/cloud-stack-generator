#!/usr/bin/env python3
"""
Test Enhanced Cities Tab Wikipedia Integration
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_city_image_config():
    """Test CityImageConfig with embed code"""
    print("Testing CityImageConfig with embed_code field...")
    
    try:
        from src.core.config.models import CityImageConfig
        
        # Test creation with embed code
        city_image = CityImageConfig(
            image_url="https://example.com/detroit.jpg",
            alt_text="Detroit cityscape",
            caption="Downtown Detroit",
            credit="Wikipedia",
            source="https://en.wikipedia.org/wiki/Detroit",
            embed_code="<section class=\"city-image\">test</section>"
        )
        
        print(f"+ CityImageConfig created successfully")
        print(f"+ Image URL: {city_image.image_url}")
        print(f"+ Embed code: {city_image.embed_code[:50]}...")
        return True
        
    except Exception as e:
        print(f"- Error: {e}")
        return False

def test_wikipedia_api():
    """Test Wikipedia API basic functionality"""
    print("\nTesting Wikipedia API embed generation...")
    
    try:
        from src.core.utils.wikipedia_api import WikipediaAPI
        
        api = WikipediaAPI()
        info = api.get_city_image_info("Detroit")
        
        print(f"+ Wikipedia API working")
        print(f"+ City: {info['city_name']}")
        print(f"+ Has embed_code: {'embed_code' in info}")
        print(f"+ Embed code length: {len(info.get('embed_code', ''))}")
        if info.get('embed_code'):
            print(f"+ Sample: {info['embed_code'][:100]}...")
        return True
        
    except Exception as e:
        print(f"- Error: {e}")
        return False

def main():
    print("Enhanced Cities Tab Integration Test")
    print("=" * 40)
    
    tests = [
        test_city_image_config,
        test_wikipedia_api,
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n{passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    print(f"\nResult: {'SUCCESS' if success else 'FAILURE'}")