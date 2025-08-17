#!/usr/bin/env python3
"""
Test actual save functionality with Salvo Metal Works configuration
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_salvo_config_save():
    """Test loading Salvo config, checking for cities, and saving"""
    print("Testing Salvo Metal Works configuration save functionality...")
    
    try:
        from core.config.parser import ConfigParser
        
        # Load existing Salvo config
        config_file = "config/clients/salvo_metal_works_config.yaml"
        parser = ConfigParser()
        
        print(f"Loading config from: {config_file}")
        config = parser.parse_yaml_file(config_file)
        
        # Check current cities data
        print(f"Loaded config - city_pages count: {len(config.city_pages)}")
        print(f"Loaded config - target_cities count: {len(config.target_cities)}")
        
        # Add a test city to verify save functionality
        from core.config.models import CityPageConfig
        
        test_city = CityPageConfig(
            city_name="Test City",
            state="IL",
            about_city="Test city for Sprint 2.5 verification",
            seo_content_body="This is a test city added to verify that the unified CitiesTab save functionality works correctly."
        )
        
        # Add to config
        config.city_pages.append(test_city)
        config.target_cities.append("Test City, IL")
        
        print(f"After adding test city - city_pages count: {len(config.city_pages)}")
        print(f"After adding test city - target_cities count: {len(config.target_cities)}")
        
        # Save to new file
        test_file = "config/clients/salvo_test_save.yaml"
        save_success = parser.save_yaml_file(config, test_file)
        
        if save_success:
            print(f"Save successful to: {test_file}")
            
            # Load back and verify
            loaded_config = parser.parse_yaml_file(test_file)
            
            print(f"Verification - city_pages count: {len(loaded_config.city_pages)}")
            print(f"Verification - target_cities count: {len(loaded_config.target_cities)}")
            
            # Check if test city is present
            test_city_found = any(cp.city_name == "Test City" for cp in loaded_config.city_pages)
            target_city_found = "Test City, IL" in loaded_config.target_cities
            
            print(f"Test city found in city_pages: {test_city_found}")
            print(f"Test city found in target_cities: {target_city_found}")
            
            if test_city_found and target_city_found:
                print("✅ SUCCESS: Cities data is being saved and loaded correctly!")
                return True
            else:
                print("❌ FAILED: Cities data not properly saved/loaded")
                return False
        else:
            print("❌ FAILED: Could not save configuration")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run Salvo save test"""
    print("Sprint 2.5 - Salvo Metal Works Save Functionality Test")
    print("=" * 60)
    
    success = test_salvo_config_save()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SPRINT 2.5 SAVE ISSUE RESOLVED - Cities data saves correctly!")
    else:
        print("⚠️  Save issue still exists - needs further investigation")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)