#!/usr/bin/env python3
"""Simple test for Wikipedia embed code functionality"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_functionality():
    """Test basic Wikipedia embed functionality"""
    try:
        from src.core.utils.wikipedia_api import WikipediaAPI
        
        wiki_api = WikipediaAPI()
        city_info = wiki_api.get_city_image_info("Detroit")
        
        print(f"City: {city_info['city_name']}")
        print(f"Has embed code: {'embed_code' in city_info}")
        
        if 'embed_code' in city_info:
            embed_code = city_info['embed_code']
            print(f"Embed code length: {len(embed_code)}")
            print(f"Contains city-image class: {'city-image' in embed_code}")
            print(f"Contains attribution: {'image-caption' in embed_code}")
            print(f"Is HTML: {'<section' in embed_code}")
            
            print("\nSample embed code (first 200 chars):")
            print(embed_code[:200] + "..." if len(embed_code) > 200 else embed_code)
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Wikipedia Embed Code Basic Functionality")
    print("=" * 50)
    
    if test_basic_functionality():
        print("\nBASIC TEST PASSED")
    else:
        print("\nBASIC TEST FAILED")