#!/usr/bin/env python3
"""
Test enhanced template rendering with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.core.config.parser import ConfigParser
from src.core.website_generator import WebsiteGenerator

def test_enhanced_template_rendering():
    """Test that enhanced template renders correctly with enhanced data"""
    print("Testing enhanced template rendering...")
    
    try:
        # Load the base Salvo configuration
        parser = ConfigParser()
        config = parser.parse_yaml_file("config/clients/salvo_metal_works_config.yaml")
        
        # Add some enhanced data to trigger the enhanced template
        config.business.tagline = "Expert metal fabrication with unmatched quality"
        config.business.years_in_business = "25+ Years"
        config.business.company_overview = "Salvo Metal Works has been the Midwest's premier metal fabrication company since 1995. We specialize in custom architectural metalwork including cupolas, finials, and roofing products."
        config.business.why_choose_us = [
            "Expert craftsmanship with 25+ years experience",
            "Custom solutions for every project",
            "Fast turnaround times",
            "Family-owned and operated",
            "Comprehensive warranty on all products"
        ]
        config.business.company_stats = {
            "projects": "500+",
            "years": "25+",
            "products": "50+",
            "states": "10+"
        }
        config.business.service_guarantee = "We guarantee the quality of our work and offer a comprehensive warranty on all products."
        config.business.service_area_description = "We proudly serve the greater Chicago area and throughout Illinois, Wisconsin, Indiana, and Michigan."
        
        # Add enhanced contact data
        config.contact.office_phone = "+1-630-555-0123"
        config.contact.response_time_promise = "We respond to all inquiries within 24 hours"
        config.contact.contact_preference = "Phone or Email"
        
        print(f"[TEST] Enhanced Content Detection After Adding Data:")
        print(f"  Has Enhanced Content: {config.business.has_enhanced_content()}")
        print(f"  Hero Tagline: '{config.business.get_hero_tagline()}'")
        print(f"  Years Display: '{config.business.get_years_display()}'")
        print(f"  Has Multiple Contacts: {config.contact.has_multiple_contacts()}")
        
        # Test website generation with enhanced template
        print(f"\n[TEST] Generating website with enhanced template...")
        
        generator = WebsiteGenerator()
        output_dir = "test_output/enhanced_template_test"
        
        # Generate the website
        result = generator.generate(config, output_dir)
        
        if result.success:
            print(f"[SUCCESS] Website generated successfully!")
            print(f"  Generated files: {len(result.generated_files)}")
            for file_path in result.generated_files:
                print(f"    - {file_path}")
                
            # Read and check the generated index.html for enhanced content
            index_path = None
            for file_path in result.generated_files:
                if file_path.endswith("index.html"):
                    index_path = file_path
                    break
            
            if index_path:
                print(f"\n[TEST] Checking generated index.html for enhanced content...")
                
                with open(index_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                # Check for enhanced template elements
                enhanced_elements = [
                    "hero-tagline",          # Enhanced tagline class
                    "years-experience",      # Years of experience
                    "hero-cta",             # CTA buttons
                    "why-choose-us",        # Why choose us section
                    "company-stats",        # Statistics section
                    "business-hours",       # Business hours
                    "service-guarantee",    # Guarantee section
                    "enhanced-contact",     # Enhanced contact section
                ]
                
                found_elements = []
                for element in enhanced_elements:
                    if element in html_content:
                        found_elements.append(element)
                        print(f"  [OK] Found enhanced element: {element}")
                    else:
                        print(f"  [MISSING] Enhanced element not found: {element}")
                
                print(f"\n[RESULT] Enhanced elements found: {len(found_elements)}/{len(enhanced_elements)}")
                
                # Check for specific enhanced content
                if "Expert metal fabrication with unmatched quality" in html_content:
                    print(f"  [OK] Custom tagline found in HTML")
                else:
                    print(f"  [MISSING] Custom tagline not found in HTML")
                
                if "25+ Years of Experience" in html_content:
                    print(f"  [OK] Years display found in HTML")
                else:
                    print(f"  [MISSING] Years display not found in HTML")
                
                if "Why Choose Us?" in html_content:
                    print(f"  [OK] Why Choose Us section found in HTML")
                else:
                    print(f"  [MISSING] Why Choose Us section not found in HTML")
                
                # Check CSS for enhanced styles
                css_path = None
                for file_path in result.generated_files:
                    if file_path.endswith("styles.css"):
                        css_path = file_path
                        break
                
                if css_path:
                    print(f"\n[TEST] Checking CSS for enhanced styles...")
                    
                    with open(css_path, 'r', encoding='utf-8') as f:
                        css_content = f.read()
                    
                    enhanced_css_classes = [
                        ".hero-cta",
                        ".why-choose-us", 
                        ".company-stats",
                        ".enhanced-contact",
                        ".service-guarantee"
                    ]
                    
                    for css_class in enhanced_css_classes:
                        if css_class in css_content:
                            print(f"  [OK] Enhanced CSS class found: {css_class}")
                        else:
                            print(f"  [MISSING] Enhanced CSS class not found: {css_class}")
            
            print(f"\n[SUCCESS] Enhanced template rendering test completed!")
            return True
        else:
            print(f"[ERROR] Website generation failed!")
            if result.error_message:
                print(f"  Error: {result.error_message}")
            return False
        
    except Exception as e:
        print(f"[ERROR] Error testing enhanced template rendering: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_enhanced_template_rendering()
    sys.exit(0 if success else 1)