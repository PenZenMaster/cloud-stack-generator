#!/usr/bin/env python3
"""
Debug what EnhancedCitiesTab actually returns when empty vs populated
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_enhanced_cities_tab_empty_state():
    """Test what EnhancedCitiesTab returns when empty"""
    print("Testing EnhancedCitiesTab in empty state...")
    
    try:
        from ui.content_tabs.enhanced_cities_tab import EnhancedCitiesTab
        
        # Create tab instance (simulates what main window does)
        tab = EnhancedCitiesTab()
        
        # Get config data when empty
        empty_data = tab.get_config_data()
        print(f"Empty EnhancedCitiesTab config data: {empty_data}")
        print(f"Type: {type(empty_data)}")
        
        if "city_pages" in empty_data:
            print(f"city_pages found: {empty_data['city_pages']}")
            print(f"city_pages count: {len(empty_data['city_pages'])}")
        else:
            print("ERROR: No 'city_pages' key in config data!")
            print(f"Available keys: {list(empty_data.keys())}")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_main_window_data_collection():
    """Test what main window gets from enhanced cities tab"""
    print("\nTesting main window data collection...")
    
    try:
        from ui.enhanced_main_window import EnhancedMainWindow
        from ui.content_tabs.enhanced_cities_tab import EnhancedCitiesTab
        
        # Create just the cities tab (not full main window to avoid PyQt issues)
        cities_tab = EnhancedCitiesTab()
        
        # Simulate main window get_all_config_data logic
        cities_data = cities_tab.get_config_data()
        print(f"Cities data from tab: {cities_data}")
        
        # Check the specific logic from main window
        if "city_pages" in cities_data:
            city_count = len(cities_data["city_pages"])
            print(f"DEBUG: Collecting {city_count} cities from EnhancedCitiesTab")
            if city_count == 0:
                print("WARNING: No cities found in EnhancedCitiesTab - configuration will not include city data")
        else:
            print("ERROR: No city_pages key found - this would cause save issues!")
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_creation_logic():
    """Test the create_client_config logic for cities"""
    print("\nTesting create_client_config cities logic...")
    
    try:
        # Simulate the cities data the main window would pass
        cities_data = {"city_pages": []}  # Empty cities as user reported
        
        # Test the city pages extraction logic from main window
        city_pages_data = cities_data.get("city_pages", [])
        print(f"Extracted city_pages_data: {city_pages_data}")
        print(f"Length: {len(city_pages_data)}")
        
        if not city_pages_data:
            print("This is the issue! Empty city_pages means no cities in config")
            
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all debug tests"""
    print("Enhanced Cities Tab Debug Analysis")
    print("=" * 50)
    
    tests = [
        test_enhanced_cities_tab_empty_state,
        test_main_window_data_collection,
        test_config_creation_logic
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"Test failed: {e}")
        print()

if __name__ == "__main__":
    main()