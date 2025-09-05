#!/usr/bin/env python3
"""
Script to generate Wikipedia About City content for cities with empty about_city fields

This script:
1. Loads all city pages from the config
2. Generates Wikipedia about content for cities that don't have them
3. Updates the YAML config with the new about content
4. Preserves existing about content where it exists (like Chicago)
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Add src to Python path
src_path = str(Path(__file__).resolve().parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.utils.wikipedia_api import WikipediaAPI  # type: ignore


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
    """Main function to generate and update city about content."""
    print("Loading configuration...")
    config_data = load_config()
    
    # Get city pages - they are under client section
    client_data = config_data.get('client', {})
    city_pages = client_data.get('city_pages', [])
    if not city_pages:
        print("No city pages found in configuration.")
        return
    
    print(f"Found {len(city_pages)} city pages.")
    
    # Initialize Wikipedia API
    wiki_api = WikipediaAPI()
    
    updated_count = 0
    
    for i, city_page in enumerate(city_pages):
        city_name = city_page.get('city_name', 'Unknown')
        print(f"\nProcessing {i+1}/{len(city_pages)}: {city_name}")
        
        # Check if about_city already has content
        existing_about = city_page.get('about_city', '').strip()
        if existing_about:
            print(f"  About content already exists for {city_name}, skipping...")
            continue
            
        try:
            # Generate Wikipedia about content
            print(f"  Fetching Wikipedia about content for {city_name}...")
            about_content = wiki_api.get_city_about_content(city_name)
            
            if about_content:
                # Update the city page with the about content
                city_page['about_city'] = about_content
                updated_count += 1
                print(f"  [OK] Generated about content for {city_name}")
                print(f"      Content length: {len(about_content)} characters")
                
                # Show a preview of the content
                preview = about_content[:100] + "..." if len(about_content) > 100 else about_content
                print(f"      Preview: {preview}")
                    
            else:
                print(f"  [WARN] Could not generate about content for {city_name}")
                
        except Exception as e:
            print(f"  [ERROR] Error processing {city_name}: {str(e)}")
            continue
    
    if updated_count > 0:
        print(f"\nSaving updated configuration with {updated_count} new about city contents...")
        save_config(config_data)
        print("[SUCCESS] Configuration updated successfully!")
    else:
        print("\nNo cities needed about content updates.")


if __name__ == "__main__":
    main()