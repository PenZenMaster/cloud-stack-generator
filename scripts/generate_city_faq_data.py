#!/usr/bin/env python3
"""
Script to generate FAQ data for cities with empty city_faq fields

This script:
1. Loads all city pages from the config
2. Generates FAQ data based on primary keywords for cities that don't have them
3. Updates the YAML config with the new FAQ data
4. Preserves existing FAQ data where it exists
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.utils.people_also_ask_api import PeopleAlsoAskAPI


def load_config() -> Dict[str, Any]:
    """Load the current configuration from YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "clients" / "salvo_metal_works_config.yaml"
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def save_config(config_data: Dict[str, Any]) -> None:
    """Save the updated configuration to YAML file."""
    config_path = Path(__file__).parent.parent / "config" / "clients" / "salvo_metal_works_config.yaml"
    
    with open(config_path, 'w', encoding='utf-8') as f:
        yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True, width=80)


def main():
    """Main function to generate and update city FAQ data."""
    print("Loading configuration...")
    config_data = load_config()
    
    # Get city pages - they are under client section
    client_data = config_data.get('client', {})
    city_pages = client_data.get('city_pages', [])
    if not city_pages:
        print("No city pages found in configuration.")
        return
    
    print(f"Found {len(city_pages)} city pages.")
    
    # Initialize People Also Ask API
    paa_api = PeopleAlsoAskAPI()
    
    updated_count = 0
    
    for i, city_page in enumerate(city_pages):
        city_name = city_page.get('city_name', 'Unknown')
        primary_keyword = city_page.get('primary_keyword', '')
        print(f"\\nProcessing {i+1}/{len(city_pages)}: {city_name}")
        
        # Check if city_faq already has content
        existing_faqs = city_page.get('city_faq', [])
        if existing_faqs:
            print(f"  FAQ data already exists for {city_name} ({len(existing_faqs)} items), skipping...")
            continue
            
        try:
            # Generate FAQ data based on primary keyword
            print(f"  Generating FAQ data for {city_name}...")
            if primary_keyword:
                print(f"    Using primary keyword: {primary_keyword}")
            else:
                print(f"    No primary keyword found, using default")
            
            faq_data = paa_api.get_city_faq_data(city_name, primary_keyword)
            
            if faq_data:
                # Update the city page with the FAQ data
                city_page['city_faq'] = faq_data
                updated_count += 1
                print(f"  [OK] Generated {len(faq_data)} FAQs for {city_name}")
                
                # Show a preview of the FAQs
                for faq in faq_data[:2]:  # Show first 2
                    print(f"    Q: {faq['question']}")
                    preview = faq['answer'][:80] + "..." if len(faq['answer']) > 80 else faq['answer']
                    print(f"    A: {preview}")
                    print()
                    
            else:
                print(f"  [WARN] Could not generate FAQ data for {city_name}")
                
        except Exception as e:
            print(f"  [ERROR] Error processing {city_name}: {str(e)}")
            continue
    
    if updated_count > 0:
        print(f"\\nSaving updated configuration with {updated_count} cities having new FAQ data...")
        save_config(config_data)
        print("[SUCCESS] Configuration updated successfully!")
    else:
        print("\\nNo cities needed FAQ data updates.")


if __name__ == "__main__":
    main()