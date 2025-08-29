#!/usr/bin/env python3
"""
Debug script for Wikipedia API issues
"""

import sys
import traceback

def test_wikipedia_api():
    """Test the Wikipedia API directly"""
    try:
        print("=== Testing Wikipedia API ===")
        
        # Import the Wikipedia API
        from src.core.utils.wikipedia_api import WikipediaAPI
        
        print("+ Successfully imported WikipediaAPI")
        
        # Create API instance
        wiki_api = WikipediaAPI()
        print("+ Created WikipediaAPI instance")
        
        # Test with Chicago
        city_name = "Chicago"
        print(f"\nTesting city: {city_name}")
        
        # Test individual methods
        print("\n--- Testing normalize_city_name ---")
        normalized = wiki_api.normalize_city_name(city_name)
        print(f"Normalized name: {normalized}")
        
        print("\n--- Testing search_wikipedia_page ---")
        page_info = wiki_api.search_wikipedia_page(city_name)
        if page_info:
            print(f"Page title: {page_info.get('title', 'N/A')}")
            print(f"Page URL: {page_info.get('page_url', 'N/A')}")
            print(f"Extract length: {len(page_info.get('extract', ''))}")
            print(f"Has thumbnail: {bool(page_info.get('thumbnail', {}))}")
        else:
            print("No page info found")
        
        print("\n--- Testing build_wikipedia_image_embed ---")
        image_url, source_url, attribution = wiki_api.build_wikipedia_image_embed(city_name)
        print(f"Image URL: {image_url}")
        print(f"Source URL: {source_url}")
        print(f"Attribution: {attribution}")
        
        print("\n--- Testing get_city_image_info ---")
        city_info = wiki_api.get_city_image_info(city_name)
        print(f"City info keys: {list(city_info.keys())}")
        print(f"Image URL: {city_info.get('image_url', 'N/A')}")
        print(f"Attribution: {city_info.get('attribution', 'N/A')}")
        print(f"Alt text: {city_info.get('alt_text', 'N/A')}")
        print(f"Embed code length: {len(city_info.get('embed_code', ''))}")
        
        if city_info.get('embed_code'):
            print(f"Embed code preview: {city_info['embed_code'][:100]}...")
        
        print("\n=== SUCCESS: All Wikipedia API tests passed ===")
        return True
        
    except Exception as e:
        print(f"\n=== ERROR in Wikipedia API ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print(f"Full traceback:")
        traceback.print_exc()
        return False

def test_imports():
    """Test individual imports"""
    print("=== Testing Imports ===")
    
    try:
        import urllib.parse
        print("+ urllib.parse imported")
    except Exception as e:
        print(f"- urllib.parse failed: {e}")
        return False
    
    try:
        import urllib.request
        print("+ urllib.request imported")
    except Exception as e:
        print(f"- urllib.request failed: {e}")
        return False
    
    try:
        import json
        print("+ json imported")
    except Exception as e:
        print(f"- json failed: {e}")
        return False
    
    try:
        from typing import Optional, Dict, Any, Tuple
        print("+ typing imports successful")
    except Exception as e:
        print(f"- typing failed: {e}")
        return False
    
    try:
        import re
        print("+ re imported")
    except Exception as e:
        print(f"- re failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Wikipedia API Debug Script")
    print("=" * 40)
    
    # Test imports first
    if not test_imports():
        print("\nFAILED Import tests failed!")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    
    # Test Wikipedia API
    if test_wikipedia_api():
        print("\nSUCCESS All tests passed!")
        sys.exit(0)
    else:
        print("\nFAILED Wikipedia API tests failed!")
        sys.exit(1)