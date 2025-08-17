#!/usr/bin/env python3
"""
Test that EnhancedCitiesTab saves both target_cities AND city_pages formats
"""

import sys
import tempfile
import yaml
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_dual_format_save():
    """Test that both target_cities and city_pages are saved"""
    print("Testing dual format save (target_cities + city_pages)...")
    
    try:
        from core.config.models import (
            ClientConfig, BusinessConfig, CityPageConfig
        )
        from core.config.parser import ConfigParser
        
        # Create a city page
        city_page = CityPageConfig(
            city_name="Detroit",
            state="MI",
            about_city="Detroit is a major city in Michigan",
            seo_content_body="Detroit offers excellent business opportunities with strong manufacturing heritage."
        )
        
        # Create config with city page
        config = ClientConfig(
            business=BusinessConfig(
                business_name="Test Business",
                domain="https://test.com",
                industry="Testing"
            ),
            city_pages=[city_page]
        )
        
        # Save to temporary file
        parser = ConfigParser()
        temp_file = tempfile.mktemp(suffix=".yaml")
        
        success = parser.save_yaml_file(config, temp_file)
        if not success:
            print("FAILED: Could not save configuration")
            return False
        
        # Read the raw YAML to check both formats
        with open(temp_file, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)
        
        client_data = yaml_content.get("client", {})
        
        # Check for target_cities (legacy format)
        target_cities = client_data.get("target_cities", [])
        print(f"target_cities found: {target_cities}")
        
        # Check for city_pages (enhanced format) 
        city_pages = client_data.get("city_pages", [])
        print(f"city_pages found: {len(city_pages)} cities")
        
        if city_pages:
            print(f"First city page: {city_pages[0].get('city_name', 'NO NAME')}")
        
        # Verify both formats exist
        if not target_cities:
            print("ERROR: target_cities not found in saved YAML")
            return False
            
        if not city_pages:
            print("ERROR: city_pages not found in saved YAML")
            return False
            
        if "Detroit, MI" not in target_cities:
            print(f"ERROR: Expected 'Detroit, MI' in target_cities, got: {target_cities}")
            return False
            
        detroit_city_page = None
        for cp in city_pages:
            if cp.get("city_name") == "Detroit":
                detroit_city_page = cp
                break
                
        if not detroit_city_page:
            print("ERROR: Detroit not found in city_pages")
            return False
            
        if detroit_city_page.get("state") != "MI":
            print(f"ERROR: Expected state MI, got: {detroit_city_page.get('state')}")
            return False
        
        print("SUCCESS: Both target_cities AND city_pages saved correctly!")
        print(f"  - target_cities: {target_cities}")
        print(f"  - city_pages: {len(city_pages)} cities with full data")
        
        # Cleanup
        import os
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run dual format test"""
    print("Enhanced Cities Tab - Dual Format Save Test")
    print("=" * 50)
    
    success = test_dual_format_save()
    
    print("\n" + "=" * 50)
    if success:
        print("SPRINT 2.5 FIX VERIFIED - Both formats save correctly!")
    else:
        print("Issue still exists - dual format not working")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)