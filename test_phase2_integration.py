#!/usr/bin/env python3
"""
Test Phase 2 Integration: Enhanced Cities CRUD Interface Integration

This script tests the complete integration of the enhanced cities functionality
with the main application, including:
- Enhanced cities tab integration
- Configuration save/load with enhanced cities
- Migration from legacy target_cities
- UI validation and error handling

Usage: python test_phase2_integration.py
"""

import os
import sys
import tempfile
import yaml
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config.models import (
    ClientConfig, BusinessConfig, ContactConfig, AddressConfig, BrandingConfig,
    ServiceConfig, CityPageConfig, CityImageConfig, PlaceOfInterest, CityFAQItem
)
from src.core.config.parser import ConfigParser
from src.core.generators.enhanced_city_page_generator import EnhancedCityPageGenerator


def create_test_config_with_legacy_cities() -> ClientConfig:
    """Create a test configuration with legacy target_cities"""
    
    business = BusinessConfig(
        business_name="Test Metal Works",
        domain="https://testmetalworks.com",
        industry="Custom Metal Fabrication",
        description="Quality Metal Fabrication Services"
    )
    
    address = AddressConfig(
        street="123 Test Street",
        city="Test City",
        state="TS",
        zip_code="12345",
        country="United States"
    )
    
    contact = ContactConfig(
        name="Test Metal Works",
        phone="+1-555-123-4567",
        address=address,
        email="info@testmetalworks.com"
    )
    
    branding = BrandingConfig(
        primary_color="#b87333",
        secondary_color="#a1602b",
        font_family="Arial, sans-serif"
    )
    
    services = [
        ServiceConfig(name="Custom Fabrication", description="Custom metal fabrication services"),
        ServiceConfig(name="Welding", description="Professional welding services"),
        ServiceConfig(name="Design", description="Metal design and engineering"),
    ]
    
    # Legacy target cities
    target_cities = [
        "Chicago, IL",
        "Detroit, MI", 
        "Milwaukee, WI",
        "Indianapolis, IN",
        "Cleveland, OH"
    ]
    
    return ClientConfig(
        business=business,
        contact=contact,
        branding=branding,
        services=services,
        target_cities=target_cities
    )


def create_test_config_with_enhanced_cities() -> ClientConfig:
    """Create a test configuration with enhanced city pages"""
    
    # Start with basic config
    config = create_test_config_with_legacy_cities()
    
    # Create enhanced city page for Chicago
    chicago_page = CityPageConfig(
        city_name="Chicago",
        state="IL",
        meta_description="Test Metal Works serves Chicago with custom metal fabrication services.",
        primary_keyword="custom metal fabrication",
        secondary_keywords=["Chicago metalwork", "metal services"],
        about_city="Chicago is a major city in Illinois known for its architecture and industry.",
        city_image=CityImageConfig(
            image_url="images/chicago.jpg",
            alt_text="Chicago skyline",
            caption="Chicago city view",
            credit="Test source",
            source="Test"
        ),
        seo_content_title="Metal Fabrication Services for Chicago",
        seo_content_body="<p>Professional metal fabrication services in Chicago...</p>",
        places_of_interest=[
            PlaceOfInterest(name="Chicago Downtown", embed_url="https://maps.google.com/chicago"),
            PlaceOfInterest(name="Millennium Park", embed_url="https://maps.google.com/millennium")
        ],
        city_faq=[
            CityFAQItem(question="Do you serve Chicago?", answer="Yes, we serve Chicago and surrounding areas."),
            CityFAQItem(question="What services do you offer?", answer="We offer custom metal fabrication and welding.")
        ],
        featured_products=["custom-fabrication", "welding"],
        city_map_embed="https://maps.google.com/chicago",
        service_area_note="Serving Chicago and Greater Chicago Area"
    )
    
    config.add_city_page(chicago_page)
    return config


def test_configuration_parsing():
    """Test that the configuration parser handles enhanced cities"""
    print("Testing configuration parsing...")
    
    try:
        # Create config with enhanced cities
        config = create_test_config_with_enhanced_cities()
        
        # Convert to YAML dict
        yaml_dict = config.to_yaml_dict()
        
        # Check that city_pages are included
        assert "city_pages" in yaml_dict["client"], "city_pages not found in YAML output"
        assert len(yaml_dict["client"]["city_pages"]) == 1, "Expected 1 city page in YAML"
        
        # Parse back from YAML
        parser = ConfigParser()
        parsed_config = parser.parse_yaml_dict(yaml_dict)
        
        # Verify enhanced cities were parsed correctly
        assert hasattr(parsed_config, 'city_pages'), "Parsed config missing city_pages attribute"
        assert len(parsed_config.city_pages) == 1, "Expected 1 city page in parsed config"
        
        chicago_page = parsed_config.city_pages[0]
        assert chicago_page.city_name == "Chicago", "City name mismatch"
        assert chicago_page.state == "IL", "State mismatch"
        assert len(chicago_page.places_of_interest) == 2, "Expected 2 places of interest"
        assert len(chicago_page.city_faq) == 2, "Expected 2 FAQ items"
        
        print("[OK] Configuration parsing test passed")
        return True
        
    except Exception as e:
        print(f"[ERROR] Configuration parsing test failed: {e}")
        return False


def test_enhanced_cities_tab_integration():
    """Test the enhanced cities tab data handling"""
    print("Testing enhanced cities tab integration...")
    
    try:
        from src.ui.content_tabs.enhanced_cities_tab import EnhancedCitiesTab
        
        # Create tab instance
        tab = EnhancedCitiesTab()
        
        # Test with sample data
        test_data = {
            "city_pages": [
                {
                    "city_name": "Test City",
                    "state": "TC",
                    "slug": "test-city",
                    "title": "Test City Page",
                    "meta_description": "Test description",
                    "primary_keyword": "test keyword",
                    "secondary_keywords": ["test", "city"],
                    "hero_title": "Test Hero",
                    "breadcrumbs": ["Home", "Locations", "Test City"],
                    "about_city": "Test city description",
                    "city_image": {
                        "image_url": "test.jpg",
                        "alt_text": "Test image",
                        "caption": "Test caption",
                        "credit": "Test credit",
                        "source": "Test source"
                    },
                    "seo_content_title": "Test SEO Title",
                    "seo_content_body": "Test SEO content",
                    "places_of_interest": [
                        {"name": "Test Place", "embed_url": "test-url"}
                    ],
                    "city_faq": [
                        {"question": "Test question?", "answer": "Test answer."}
                    ],
                    "featured_products": ["test-product"],
                    "city_map_embed": "test-map-url",
                    "service_area_note": "Test service area"
                }
            ]
        }
        
        # Set data
        tab.set_config_data(test_data)
        
        # Verify data was loaded
        assert len(tab.city_pages) == 1, "Expected 1 city page"
        
        city_page = tab.city_pages[0]
        assert city_page.city_name == "Test City", "City name mismatch"
        assert len(city_page.places_of_interest) == 1, "Expected 1 place of interest"
        assert len(city_page.city_faq) == 1, "Expected 1 FAQ item"
        
        # Get data back
        retrieved_data = tab.get_config_data()
        assert "city_pages" in retrieved_data, "city_pages not in retrieved data"
        assert len(retrieved_data["city_pages"]) == 1, "Expected 1 city page in retrieved data"
        
        # Validate data
        is_valid, errors = tab.validate_data()
        assert is_valid, f"Validation failed: {errors}"
        
        print("[OK] Enhanced cities tab integration test passed")
        return True
        
    except Exception as e:
        print(f"[ERROR] Enhanced cities tab integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_migration_functionality():
    """Test migration from legacy target_cities to enhanced format"""
    print("Testing migration functionality...")
    
    try:
        # Create config with legacy cities
        legacy_config = create_test_config_with_legacy_cities()
        
        # Create generator for migration
        generator = EnhancedCityPageGenerator(legacy_config)
        
        # Test migration of legacy cities
        migrated_cities = generator.migrate_legacy_cities()
        
        # Verify migration results
        assert len(migrated_cities) == len(legacy_config.target_cities), "Migration count mismatch"
        
        # Check first migrated city
        chicago_page = next((cp for cp in migrated_cities if cp.city_name == "Chicago"), None)
        assert chicago_page is not None, "Chicago page not found in migration"
        assert chicago_page.state == "IL", "Chicago state not preserved"
        assert chicago_page.slug == "chicago", "Chicago slug not generated correctly"
        assert len(chicago_page.places_of_interest) > 0, "No places of interest generated"
        assert len(chicago_page.city_faq) > 0, "No FAQ items generated"
        assert len(chicago_page.seo_content_body) > 100, "SEO content too short"
        
        print("[OK] Migration functionality test passed")
        return True
        
    except Exception as e:
        print(f"[ERROR] Migration functionality test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yaml_roundtrip():
    """Test complete YAML save/load roundtrip with enhanced cities"""
    print("Testing YAML roundtrip...")
    
    try:
        # Create config with enhanced cities
        original_config = create_test_config_with_enhanced_cities()
        
        # Convert to YAML
        yaml_dict = original_config.to_yaml_dict()
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_dict, f, default_flow_style=False)
            temp_file = f.name
        
        try:
            # Load back from file
            parser = ConfigParser()
            loaded_config = parser.parse_yaml_file(temp_file)
            
            # Verify roundtrip preservation
            assert loaded_config.business.business_name == original_config.business.business_name
            assert len(loaded_config.city_pages) == len(original_config.city_pages)
            
            if loaded_config.city_pages:
                original_city = original_config.city_pages[0]
                loaded_city = loaded_config.city_pages[0]
                
                assert loaded_city.city_name == original_city.city_name
                assert loaded_city.state == original_city.state
                assert len(loaded_city.places_of_interest) == len(original_city.places_of_interest)
                assert len(loaded_city.city_faq) == len(original_city.city_faq)
                assert loaded_city.seo_content_body == original_city.seo_content_body
            
            print("[OK] YAML roundtrip test passed")
            return True
            
        finally:
            # Clean up temp file
            os.unlink(temp_file)
        
    except Exception as e:
        print(f"[ERROR] YAML roundtrip test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_page_generation_integration():
    """Test that enhanced city pages can be generated"""
    print("Testing page generation integration...")
    
    try:
        # Create config with enhanced cities
        config = create_test_config_with_enhanced_cities()
        
        # Create generator
        generator = EnhancedCityPageGenerator(config)
        
        # Create output directory
        output_dir = Path("test_output/phase2_integration")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate all city pages
        generated_files = generator.generate_all_city_pages(str(output_dir))
        
        # Verify generation
        assert len(generated_files) == len(config.city_pages), "Generation count mismatch"
        
        # Check generated file
        for file_path in generated_files:
            assert Path(file_path).exists(), f"Generated file not found: {file_path}"
            
            # Check file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Verify key sections
            required_sections = [
                "About Chicago",
                "Places of Interest",
                "FAQ",
                '"@type":"WebPage"',
                '"@type":"LocalBusiness"'
            ]
            
            for section in required_sections:
                assert section in content, f"Missing section '{section}' in {file_path}"
        
        print(f"[OK] Page generation integration test passed - {len(generated_files)} files generated")
        return True
        
    except Exception as e:
        print(f"[ERROR] Page generation integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_phase2_integration_tests():
    """Run all Phase 2 integration tests"""
    print("Phase 2 Integration Testing")
    print("=" * 50)
    
    tests = [
        ("Configuration Parsing", test_configuration_parsing),
        ("Enhanced Cities Tab", test_enhanced_cities_tab_integration),
        ("Migration Functionality", test_migration_functionality),
        ("YAML Roundtrip", test_yaml_roundtrip),
        ("Page Generation", test_page_generation_integration),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"[ERROR] {test_name} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print("PHASE 2 INTEGRATION TEST RESULTS")
    print("=" * 50)
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total:  {passed + failed}")
    
    if failed == 0:
        print("\n[SUCCESS] All Phase 2 integration tests passed!")
        print("Enhanced Cities CRUD interface is fully integrated.")
        return True
    else:
        print(f"\n[FAILURE] {failed} test(s) failed.")
        return False


if __name__ == "__main__":
    success = run_phase2_integration_tests()
    sys.exit(0 if success else 1)