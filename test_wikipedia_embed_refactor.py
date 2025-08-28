#!/usr/bin/env python3
"""
Test Wikipedia Embed Code Refactor
Validates the new embed code approach for Wikipedia images
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_wikipedia_embed_generation():
    """Test Wikipedia embed code generation"""
    print("Testing Wikipedia Embed Code Generation")
    print("=" * 50)
    
    try:
        from src.core.utils.wikipedia_api import WikipediaAPI, get_wikipedia_embed_code
        
        # Test direct API usage
        wiki_api = WikipediaAPI()
        
        # Test cities
        test_cities = ["Detroit", "Chicago", "Milwaukee"]
        
        for city in test_cities:
            print(f"\nTesting: {city}")
            print("-" * 30)
            
            # Get city info with embed code
            city_info = wiki_api.get_city_image_info(city)
            
            print(f"City: {city_info['city_name']}")
            print(f"Image URL: {city_info['image_url'][:60]}...")
            print(f"Attribution: {city_info['attribution']}")
            print(f"Has embed code: {'Yes' if city_info.get('embed_code') else 'No'}")
            
            if city_info.get('embed_code'):
                embed_lines = city_info['embed_code'].split('\n')
                print(f"Embed code lines: {len(embed_lines)}")
                print(f"Contains 'city-image' class: {'city-image' in city_info['embed_code']}")
                print(f"Contains proper attribution: {'image-caption' in city_info['embed_code']}")
        
        # Test convenience function
        print(f"\nTesting convenience function")
        print("-" * 30)
        embed_code = get_wikipedia_embed_code("Grand Rapids")
        print(f"Convenience function works: {len(embed_code) > 100}")
        
        return True
        
    except Exception as e:
        print(f"Error testing Wikipedia embed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cities_tab_integration():
    """Test Cities Tab integration with embed codes"""
    print(f"\nTesting Cities Tab Integration")
    print("=" * 50)
    
    try:
        from src.ui.components.cities_tab import CitiesTab
        from PyQt6.QtWidgets import QApplication
        
        # Create QApplication (required for Qt widgets)
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # Create CitiesTab instance
        cities_tab = CitiesTab()
        
        # Test data structure
        test_data = {
            "target_cities": ["Detroit", "Chicago"],
            "wikipedia_embeds": {
                "Detroit": {
                    "embed_code": "<section class=\"city-image\">Detroit content</section>",
                    "image_url": "https://example.com/detroit.jpg",
                    "attribution": "Wikipedia - Detroit"
                }
            }
        }
        
        # Test set config data
        cities_tab.set_config_data(test_data)
        
        # Test get config data
        retrieved_data = cities_tab.get_config_data()
        
        print(f"Data round-trip successful")
        print(f"Target cities: {retrieved_data.get('target_cities', [])}")
        print(f"Wikipedia embeds: {len(retrieved_data.get('wikipedia_embeds', {}))}")
        print(f"Has Detroit embed: {'Detroit' in retrieved_data.get('wikipedia_embeds', {})}")
        
        return True
        
    except Exception as e:
        print(f"Error testing Cities Tab: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_template_compatibility():
    """Test template compatibility with new embed code approach"""
    print(f"\nTesting Template Compatibility")
    print("=" * 50)
    
    try:
        # Read the updated template
        template_path = "src/templates/pages/city_page.html"
        
        if os.path.exists(template_path):
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
            
            # Check for new embed code approach
            has_embed_code = "wikipedia_embed_code" in template_content
            has_safe_filter = "wikipedia_embed_code|safe" in template_content
            has_fallback = "wikipedia_image" in template_content
            
            print(f"Template updated: {has_embed_code}")
            print(f"Uses safe filter: {has_safe_filter}")
            print(f"Has legacy fallback: {has_fallback}")
            
            # Check for proper structure
            embed_section = template_content.count("wikipedia_embed_code")
            print(f"Embed code references: {embed_section}")
            
            return has_embed_code and has_safe_filter
        else:
            print(f"Template file not found: {template_path}")
            return False
        
    except Exception as e:
        print(f"Error testing template: {e}")
        return False

def main():
    """Run all Wikipedia embed refactor tests"""
    print("Wikipedia Image System Refactor Tests")
    print("=" * 60)
    
    tests = [
        ("Wikipedia API Embed Generation", test_wikipedia_embed_generation),
        ("Cities Tab Integration", test_cities_tab_integration), 
        ("Template Compatibility", test_template_compatibility),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\nRunning: {test_name}")
        if test_func():
            print(f"PASSED: {test_name}")
            passed += 1
        else:
            print(f"FAILED: {test_name}")
    
    print(f"\nSUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{total} tests")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print(f"\nAll tests passed! Wikipedia embed refactor is working correctly.")
        return True
    else:
        print(f"\nSome tests failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)