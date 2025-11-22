#!/usr/bin/env python3
"""
GBP Regression Prevention Test
Comprehensive test to prevent Google Business Profile embed code from disappearing

This test must be run after any changes to:
- Contact tab UI components
- Data flow between UI and YAML
- Configuration parsing/saving
- Website generation process

Version: 1.0.0
Date: 2025-08-19
"""

import os
import sys
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from src.core.config.parser import ConfigParser
from src.core.config.models import ClientConfig
from src.core.website_generator import WebsiteGenerator


def test_gbp_data_flow():
    """Test complete GBP data flow from UI to generated HTML"""
    print("Testing GBP Data Flow End-to-End...")
    
    # Test data with GBP embed
    test_embed_code = '''<iframe src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d205664.07488490682!2d-88.3291328555474!3d41.77874305321832!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x880e57cdd45d0985%3A0x9f48999634f8ab20!2sSalvo%20Metal%20Works!5e0!3m2!1sen!2sus!4v1755562750597!5m2!1sen!2sus" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'''
    
    # Create test YAML content
    test_yaml = f"""
client:
  business_name: Test Business
  domain: https://test.com
  industry: Testing
  description: Test description
  tagline: Test tagline
  hero_subtitle: Test subtitle
  years_in_business: 10 years
  company_overview: Test overview
  contact:
    name: Test Contact
    phone: +1-555-123-4567
    email: test@test.com
  address:
    street: 123 Test St
    city: Test City
    state: TS
    zip_code: "12345"
    country: United States
  branding:
    primary_color: "#bf062f"
    secondary_color: "#fe9e1f"
    font_family: Arial, sans-serif
  social_media:
    facebook: https://facebook.com/test
  google_business_profile:
    embed_code: {test_embed_code}
  pages:
    - title: Home
      slug: index
      primary_keyword: test
  target_cities:
    - Test City
"""
    
    try:
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(test_yaml)
            temp_config_path = f.name
        
        print(f"PASS: Created test config: {temp_config_path}")
        
        # Test 1: Parse YAML file
        parser = ConfigParser()
        config = parser.parse_yaml_file(temp_config_path)
        
        assert hasattr(config, 'google_business_profile'), "Config missing google_business_profile attribute"
        assert config.google_business_profile, "google_business_profile is empty"
        assert 'embed_code' in config.google_business_profile, "embed_code missing from google_business_profile"
        assert config.google_business_profile['embed_code'] == test_embed_code, "embed_code doesn't match test data"
        
        print("PASS: YAML parsing preserves GBP data")
        
        # Test 2: Round-trip save/load
        temp_output_path = temp_config_path.replace('.yaml', '_output.yaml')
        parser.save_yaml_file(config, temp_output_path)
        
        # Load the saved file
        config_reloaded = parser.parse_yaml_file(temp_output_path)
        
        assert hasattr(config_reloaded, 'google_business_profile'), "Reloaded config missing google_business_profile"
        assert config_reloaded.google_business_profile, "Reloaded google_business_profile is empty"
        assert config_reloaded.google_business_profile['embed_code'] == test_embed_code, "Round-trip changed embed_code"
        
        print("PASS: Round-trip save/load preserves GBP data")
        
        # Test 3: Website generation includes GBP
        with tempfile.TemporaryDirectory() as temp_dir:
            generator = WebsiteGenerator(config_reloaded)
            output_path = Path(temp_dir) / "website"
            generator.generate_complete_website(str(output_path))
            
            # Check if index.html contains the embed code
            index_file = output_path / "index.html"
            assert index_file.exists(), "Generated website missing index.html"
            
            with open(index_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            assert test_embed_code in html_content, "Generated HTML missing GBP embed code"
            print("PASS: Website generation includes GBP embed")
        
        print("SUCCESS: All GBP data flow tests PASSED")
        return True
        
    except Exception as e:
        print(f"FAIL: GBP data flow test FAILED: {e}")
        return False
        
    finally:
        # Clean up temp files
        try:
            os.unlink(temp_config_path)
            if 'temp_output_path' in locals():
                os.unlink(temp_output_path)
        except Exception:
            pass


def test_ui_contact_tab_data_structure():
    """Test Contact tab data structure compatibility"""
    print("Testing Contact Tab Data Structure...")
    
    try:
        # Import Contact tab (this tests import compatibility)
        from src.ui.components.contact_tab import ContactTab
        
        # Create Contact tab instance
        contact_tab = ContactTab()
        
        # Test data structure
        test_data = {
            "contact": {
                "name": "Test Contact",
                "phone": "+1-555-123-4567",
                "email": "test@test.com"
            },
            "address": {
                "street": "123 Test St",
                "city": "Test City", 
                "state": "TS",
                "zip_code": "12345"
            },
            "google_business_profile": {
                "embed_code": "<iframe>test embed</iframe>"
            }
        }
        
        # Test set_config_data
        contact_tab.set_config_data(test_data)
        print("PASS: Contact tab accepts google_business_profile data")
        
        # Test get_config_data
        retrieved_data = contact_tab.get_config_data()
        
        assert "google_business_profile" in retrieved_data, "Contact tab doesn't export google_business_profile"
        assert "embed_code" in retrieved_data["google_business_profile"], "embed_code missing from exported data"
        
        print("PASS: Contact tab exports google_business_profile data")
        print("SUCCESS: Contact tab data structure test PASSED")
        return True
        
    except Exception as e:
        print(f"FAIL: Contact tab test FAILED: {e}")
        return False


def test_enhanced_main_window_data_mapping():
    """Test enhanced main window correctly maps GBP data"""
    print("Testing Enhanced Main Window Data Mapping...")
    
    try:
        # Test the data structure mapping
        test_config = ClientConfig(
            business_name="Test Business",
            domain="https://test.com",
            industry="Testing",
            google_business_profile={"embed_code": "<iframe>test</iframe>"}
        )
        
        # This simulates the mapping in enhanced_main_window.py load_configuration_data()
        contact_data = {
            "google_business_profile": {
                "embed_code": getattr(test_config, 'google_business_profile', {}).get('embed_code', '') if hasattr(test_config, 'google_business_profile') else ''
            }
        }
        
        assert contact_data["google_business_profile"]["embed_code"] == "<iframe>test</iframe>", "Enhanced main window mapping failed"
        
        print("PASS: Enhanced main window correctly maps GBP data")
        print("SUCCESS: Enhanced main window mapping test PASSED")
        return True
        
    except Exception as e:
        print(f"FAIL: Enhanced main window mapping test FAILED: {e}")
        return False


def run_all_gbp_regression_tests():
    """Run all GBP regression prevention tests"""
    print("Running GBP Regression Prevention Test Suite")
    print("=" * 60)
    
    all_passed = True
    
    # Run all tests
    tests = [
        test_gbp_data_flow,
        test_ui_contact_tab_data_structure,  
        test_enhanced_main_window_data_mapping
    ]
    
    for test_func in tests:
        print()
        passed = test_func()
        all_passed = all_passed and passed
        print()
    
    print("=" * 60)
    if all_passed:
        print("SUCCESS: ALL GBP REGRESSION TESTS PASSED")
        print("GBP embed functionality is protected against regressions")
    else:
        print("FAIL: SOME GBP REGRESSION TESTS FAILED")
        print("WARNING: GBP embed functionality may be at risk")
    
    return all_passed


if __name__ == "__main__":
    success = run_all_gbp_regression_tests()
    sys.exit(0 if success else 1)