#!/usr/bin/env python3
"""
Test the actual main window flow to see where target_cities is lost
"""

import sys
import tempfile
import yaml
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_main_window_cities_flow():
    """Test the actual main window save flow"""
    print("Testing main window cities save flow...")
    
    try:
        # Import what we need
        from core.config.models import CityPageConfig
        from ui.content_tabs.enhanced_cities_tab import EnhancedCitiesTab
        
        # Create an EnhancedCitiesTab and add a city
        cities_tab = EnhancedCitiesTab()
        
        # Add a test city directly to simulate user adding a city
        test_city = CityPageConfig(
            city_name="Detroit", 
            state="MI",
            about_city="Test city",
            seo_content_body="Test content"
        )
        cities_tab.city_pages.append(test_city)
        
        # Test what the tab returns
        cities_data = cities_tab.get_config_data()
        print(f"EnhancedCitiesTab.get_config_data() returns:")
        for key, value in cities_data.items():
            if key == "city_pages":
                print(f"  {key}: {len(value)} cities")
            else:
                print(f"  {key}: {value}")
        
        # Test the main window create_client_config logic
        # We can't easily import the main window due to PyQt, so let's simulate the logic
        
        # Simulate main window logic
        city_pages_data = cities_data.get("city_pages", [])
        print(f"\nProcessing {len(city_pages_data)} city pages...")
        
        # Simulate creating city page objects (main window logic)
        from core.config.models import CityPageConfig, CityImageConfig, PlaceOfInterest, CityFAQItem
        city_pages = []
        for cp_data in city_pages_data:
            city_image = CityImageConfig(
                image_url=cp_data.get("city_image", {}).get("image_url", ""),
                alt_text=cp_data.get("city_image", {}).get("alt_text", ""),
                caption=cp_data.get("city_image", {}).get("caption", ""),
                credit=cp_data.get("city_image", {}).get("credit", ""),
                source=cp_data.get("city_image", {}).get("source", "Wikipedia")
            )
            
            city_page = CityPageConfig(
                city_name=cp_data.get("city_name", ""),
                state=cp_data.get("state", ""),
                slug=cp_data.get("slug", ""),
                title=cp_data.get("title", ""),
                meta_description=cp_data.get("meta_description", ""),
                primary_keyword=cp_data.get("primary_keyword", ""),
                secondary_keywords=cp_data.get("secondary_keywords", []),
                hero_title=cp_data.get("hero_title", ""),
                breadcrumbs=cp_data.get("breadcrumbs", []),
                about_city=cp_data.get("about_city", ""),
                city_image=city_image,
                seo_content_title=cp_data.get("seo_content_title", ""),
                seo_content_body=cp_data.get("seo_content_body", ""),
                places_of_interest=[
                    PlaceOfInterest(name=poi.get("name", ""), embed_url=poi.get("embed_url", ""))
                    for poi in cp_data.get("places_of_interest", [])
                ],
                city_faq=[
                    CityFAQItem(question=faq.get("question", ""), answer=faq.get("answer", ""))
                    for faq in cp_data.get("city_faq", [])
                ],
                city_map_embed=cp_data.get("city_map_embed", ""),
                service_area_note=cp_data.get("service_area_note", ""),
                featured_products=cp_data.get("featured_products", [])
            )
            city_pages.append(city_page)
        
        # Get target_cities from cities tab (this is the new logic)
        target_cities = cities_data.get("target_cities", [])
        print(f"target_cities from cities_data: {target_cities}")
        
        # Fallback: create from city_pages if not provided
        if not target_cities:
            target_cities = [cp.city_name for cp in city_pages if cp.city_name]
            print(f"fallback target_cities: {target_cities}")
        
        # Now create ClientConfig and test save
        from core.config.models import ClientConfig, BusinessConfig
        
        config = ClientConfig(
            business=BusinessConfig(
                business_name="Test Business",
                domain="https://test.com", 
                industry="Testing"
            ),
            city_pages=city_pages,
            target_cities=target_cities
        )
        
        print(f"\nClientConfig created:")
        print(f"  city_pages: {len(config.city_pages)} cities")
        print(f"  target_cities: {config.target_cities}")
        
        # Test save
        from core.config.parser import ConfigParser
        parser = ConfigParser()
        temp_file = tempfile.mktemp(suffix=".yaml")
        
        success = parser.save_yaml_file(config, temp_file)
        if not success:
            print("FAILED: Could not save")
            return False
        
        # Check saved content
        with open(temp_file, 'r', encoding='utf-8') as f:
            yaml_content = yaml.safe_load(f)
        
        client_data = yaml_content.get("client", {})
        saved_target_cities = client_data.get("target_cities", [])
        saved_city_pages = client_data.get("city_pages", [])
        
        print(f"\nSaved to YAML:")
        print(f"  target_cities: {saved_target_cities}")
        print(f"  city_pages: {len(saved_city_pages)} cities")
        
        if saved_target_cities and saved_city_pages:
            print("SUCCESS: Both formats saved!")
            return True
        else:
            print("FAILED: Missing format(s)")
            return False
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run main window flow test"""
    print("Main Window Cities Save Flow Test")
    print("=" * 40)
    
    success = test_main_window_cities_flow()
    
    print("\n" + "=" * 40)
    if success:
        print("Main window flow working correctly!")
    else:
        print("Issue found in main window flow")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)