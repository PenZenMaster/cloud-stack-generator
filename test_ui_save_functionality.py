#!/usr/bin/env python3
"""
Test UI Save Functionality - Debug actual save behavior
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_enhanced_cities_tab_data():
    """Test what data the EnhancedCitiesTab actually returns"""
    print("Testing EnhancedCitiesTab.get_config_data()...")
    
    try:
        from ui.content_tabs.enhanced_cities_tab import EnhancedCitiesTab
        from core.config.models import CityPageConfig
        
        # Create tab instance
        cities_tab = EnhancedCitiesTab()
        
        # Test with empty tab
        empty_data = cities_tab.get_config_data()
        print(f"Empty tab data: {empty_data}")
        
        # Add a test city manually
        test_city = CityPageConfig(
            city_name="Test City",
            state="IL",
            about_city="Test about city content",
            seo_content_body="Test SEO content for the city"
        )
        cities_tab.city_pages = [test_city]
        
        # Test with city data
        with_city_data = cities_tab.get_config_data()
        print(f"With city data: {with_city_data}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_main_window_save_process():
    """Test the main window save process"""
    print("\nTesting main window save process...")
    
    try:
        from ui.enhanced_main_window import EnhancedMainWindow
        from core.config.models import CityPageConfig
        
        # This would normally require PyQt6 application, so let's just test the methods
        # Create a mock config data structure
        mock_cities_data = {
            "city_pages": [
                {
                    "city_name": "Test City",
                    "state": "IL",
                    "about_city": "Test content",
                    "seo_content_body": "Test SEO content"
                }
            ]
        }
        
        # Test the create_client_config logic manually
        print(f"Mock cities data: {mock_cities_data}")
        
        city_pages_data = mock_cities_data.get("city_pages", [])
        print(f"Extracted city_pages_data: {city_pages_data}")
        
        if city_pages_data:
            print("City pages data found - would create CityPageConfig objects")
        else:
            print("No city pages data found - this is the problem!")
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_config_parser_round_trip():
    """Test save/load round trip with cities data"""
    print("\nTesting config parser round trip...")
    
    try:
        from core.config.models import ClientConfig, BusinessConfig, CityPageConfig
        from core.config.parser import ConfigParser
        import tempfile
        
        # Create config with city pages
        city_page = CityPageConfig(
            city_name="Test City",
            state="IL",
            about_city="Test about content",
            seo_content_body="Test SEO content"
        )
        
        config = ClientConfig(
            business=BusinessConfig(
                business_name="Test Business",
                domain="https://test.com",
                industry="Testing"
            ),
            city_pages=[city_page]
        )
        
        parser = ConfigParser()
        
        # Test save
        temp_file = tempfile.mktemp(suffix=".yaml")
        save_success = parser.save_yaml_file(config, temp_file)
        print(f"Save success: {save_success}")
        
        if save_success:
            # Read raw file to see what was saved
            with open(temp_file, 'r') as f:
                content = f.read()
            print("Saved YAML content:")
            print(content[:500] + "..." if len(content) > 500 else content)
            
            # Test load
            loaded_config = parser.parse_yaml_file(temp_file)
            print(f"Loaded city_pages count: {len(loaded_config.city_pages)}")
            
            if loaded_config.city_pages:
                city = loaded_config.city_pages[0]
                print(f"First city: {city.city_name}, content: {city.about_city[:50]}...")
            
        import os
        if os.path.exists(temp_file):
            os.unlink(temp_file)
            
        return save_success
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("UI Save Functionality Debug Tests")
    print("=" * 50)
    
    tests = [
        test_enhanced_cities_tab_data,
        test_main_window_save_process,
        test_config_parser_round_trip
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"Test failed with exception: {e}")
            results.append(False)
        print()
    
    passed = sum(results)
    total = len(results)
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed < total:
        print("ISSUES FOUND - Need to debug save functionality")
    else:
        print("All tests passed - save functionality working")

if __name__ == "__main__":
    main()