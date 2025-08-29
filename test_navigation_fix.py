#!/usr/bin/env python3
"""
Test script to verify city pages appear in navigation menu
"""

import sys
from pathlib import Path
import re

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.config import load_config_from_file
from src.core.generators.page_generator import PageGenerator


def test_navigation_includes_cities():
    """Test that generated websites include city pages in navigation"""
    try:
        print("=== Navigation City Pages Test ===")
        
        # Load configuration
        print("Loading configuration...")
        config = load_config_from_file("config/clients/salvo_metal_works_config.yaml")
        
        print(f"+ Configuration loaded: {config.business.business_name}")
        print(f"+ City pages in config: {len(config.city_pages)}")
        
        # Create output directory
        output_dir = "test_output/navigation_test"
        if Path(output_dir).exists():
            import shutil
            shutil.rmtree(output_dir)
        
        # Initialize page generator
        generator = PageGenerator(output_base_dir=output_dir)
        
        # Generate website
        print("\n--- Generating Website ---")
        result = generator.generate_complete_website(config)
        
        print(f"+ Generation success: {result.success}")
        print(f"+ Pages generated: {result.pages_generated}")
        
        # Test navigation in generated index.html
        index_file = Path(output_dir) / "index.html"
        if not index_file.exists():
            print("- ERROR: index.html not generated")
            return False
        
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Locations dropdown
        print("\n--- Navigation Analysis ---")
        
        navigation_checks = {
            "Locations dropdown exists": 'href="#locations">Locations</a>' in content,
            "City pages in dropdown": len(re.findall(r'href="locations/.*\.html"', content)) > 0,
            "Chicago city link": 'href="locations/chicago.html"' in content,
            "Bellwood city link": 'href="locations/bellwood-illinois.html"' in content,
            "Oak Park city link": 'href="locations/oak-park-illinois.html"' in content
        }
        
        for check, passed in navigation_checks.items():
            status = "PASS" if passed else "FAIL"
            print(f"+ {check}: {status}")
        
        # Count city links in navigation
        city_links = re.findall(r'href="locations/(.*?)\.html"', content)
        print(f"+ City links found: {len(city_links)}")
        if city_links:
            print(f"+ Cities in navigation: {', '.join(city_links)}")
        
        # Overall result
        all_passed = all(navigation_checks.values())
        
        if all_passed:
            print(f"\n=== SUCCESS: Navigation includes city pages ===")
            print(f"+ All {len(navigation_checks)} checks passed")
            print(f"+ {len(city_links)} city links found in navigation")
        else:
            failed_checks = [check for check, passed in navigation_checks.items() if not passed]
            print(f"\n=== PARTIAL SUCCESS: Some navigation checks failed ===")
            print(f"+ Passed: {sum(navigation_checks.values())}/{len(navigation_checks)}")
            print(f"+ Failed checks: {', '.join(failed_checks)}")
        
        return all_passed
        
    except Exception as e:
        print(f"\n=== ERROR: Navigation test failed ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_navigation_includes_cities()
    sys.exit(0 if success else 1)