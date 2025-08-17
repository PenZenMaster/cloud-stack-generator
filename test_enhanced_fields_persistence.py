#!/usr/bin/env python3
"""
Test enhanced fields persistence in configuration loading
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.core.config.parser import ConfigParser

def test_enhanced_fields_persistence():
    """Test that enhanced fields are properly loaded from saved configuration"""
    print("Testing enhanced fields persistence...")
    
    # Load the Salvo Metal Works configuration
    config_path = "config/clients/salvo_metal_works_config.yaml"
    
    try:
        parser = ConfigParser()
        config = parser.parse_yaml_file(config_path)
        
        print(f"[SUCCESS] Successfully loaded configuration from {config_path}")
        
        # Test enhanced business fields
        print("\n[TEST] Testing Enhanced Business Fields:")
        print(f"  Business Name: {config.business.business_name}")
        print(f"  Tagline: '{config.business.tagline}'")
        print(f"  Years in Business: '{config.business.years_in_business}'")
        print(f"  Company Overview: '{config.business.company_overview}'")
        print(f"  Mission Statement: '{config.business.mission_statement}'")
        print(f"  Service Guarantee: '{config.business.service_guarantee}'")
        print(f"  Service Area Description: '{config.business.service_area_description}'")
        print(f"  Why Choose Us: {config.business.why_choose_us}")
        print(f"  Company Stats: {config.business.company_stats}")
        
        # Test enhanced contact fields
        print("\n[TEST] Testing Enhanced Contact Fields:")
        print(f"  Primary Phone: {config.contact.phone}")
        print(f"  Office Phone: '{config.contact.office_phone}'")
        print(f"  Mobile Phone: '{config.contact.mobile_phone}'")
        print(f"  Emergency Phone: '{config.contact.emergency_phone}'")
        print(f"  Fax Number: '{config.contact.fax_number}'")
        print(f"  Response Time Promise: '{config.contact.response_time_promise}'")
        print(f"  Contact Preference: '{config.contact.contact_preference}'")
        
        print("\n[TEST] Testing Business Hours:")
        for day, hours in config.contact.business_hours.items():
            print(f"  {day.title()}: {hours}")
        
        print(f"\n[TEST] Additional Locations: {len(config.contact.additional_locations)} locations")
        
        # Test enhanced template detection
        print(f"\n[TEST] Enhanced Content Detection:")
        print(f"  Has Enhanced Content: {config.business.has_enhanced_content()}")
        print(f"  Hero Tagline: '{config.business.get_hero_tagline()}'")
        print(f"  Years Display: '{config.business.get_years_display()}'")
        print(f"  Has Multiple Contacts: {config.contact.has_multiple_contacts()}")
        
        # Test that the parser correctly includes enhanced fields in the output
        print(f"\n[TEST] Testing YAML Generation with Enhanced Fields:")
        yaml_dict = parser.generate_yaml_dict(config)
        
        # Check business enhanced fields in YAML output
        client_data = yaml_dict.get("client", {})
        
        business_enhanced_fields = [
            "tagline", "years_in_business", "company_overview", 
            "mission_statement", "service_guarantee", "service_area_description",
            "why_choose_us", "company_stats"
        ]
        
        for field in business_enhanced_fields:
            if field in client_data:
                print(f"  [OK] Business field '{field}' present in YAML output")
            else:
                print(f"  [ERROR] Business field '{field}' MISSING from YAML output")
        
        # Check contact enhanced fields in YAML output
        contact_data = client_data.get("contact", {})
        contact_enhanced_fields = [
            "business_hours", "emergency_phone", "office_phone", 
            "mobile_phone", "fax_number", "response_time_promise",
            "contact_preference", "additional_locations"
        ]
        
        for field in contact_enhanced_fields:
            if field in contact_data:
                print(f"  [OK] Contact field '{field}' present in YAML output")
            else:
                print(f"  [ERROR] Contact field '{field}' MISSING from YAML output")
        
        print(f"\n[SUCCESS] Enhanced fields persistence test completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Error testing enhanced fields persistence: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_fields_persistence()
    sys.exit(0 if success else 1)