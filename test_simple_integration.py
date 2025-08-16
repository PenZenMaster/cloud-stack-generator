#!/usr/bin/env python3
"""
Simple Integration Test for Phase 2

Basic test to verify the enhanced cities integration is working.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_basic_integration():
    """Test basic integration functionality"""
    print("Testing basic integration...")
    
    try:
        # Test model imports
        from src.core.config.models import CityPageConfig, CityImageConfig, PlaceOfInterest, CityFAQItem
        print("[OK] Models imported successfully")
        
        # Test creating a city page
        city_page = CityPageConfig(
            city_name="Test City",
            state="TS",
            about_city="Test description"
        )
        print("[OK] CityPageConfig created successfully")
        
        # Test enhanced cities tab
        from src.ui.content_tabs.enhanced_cities_tab import EnhancedCitiesTab
        tab = EnhancedCitiesTab()
        print("[OK] EnhancedCitiesTab created successfully")
        
        # Test generator
        from src.core.generators.enhanced_city_page_generator import EnhancedCityPageGenerator
        from src.core.config.models import ClientConfig, BusinessConfig, ContactConfig, AddressConfig
        
        # Create minimal config
        config = ClientConfig(
            business=BusinessConfig(business_name="Test Business"),
            contact=ContactConfig(address=AddressConfig())
        )
        generator = EnhancedCityPageGenerator(config)
        print("[OK] EnhancedCityPageGenerator created successfully")
        
        # Test configuration parser
        from src.core.config.parser import ConfigParser
        parser = ConfigParser()
        print("[OK] ConfigParser created successfully")
        
        print("\n[SUCCESS] Basic integration test passed!")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Basic integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_basic_integration()
    if success:
        print("\nPhase 2 integration components are working correctly!")
    else:
        print("\nPhase 2 integration has issues.")
    sys.exit(0 if success else 1)