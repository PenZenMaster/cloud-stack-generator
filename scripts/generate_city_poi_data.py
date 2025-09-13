#!/usr/bin/env python3
"""
Script to generate Places of Interest (POI) data for cities with empty places_of_interest fields

This script:
1. Loads all city pages from the config
2. Generates POI data for cities that don't have them
3. Updates the YAML config with the new POI data
4. Preserves existing POI data where it exists
"""

import sys
from pathlib import Path
from typing import Dict, Any
import yaml

# Add src to Python path
src_path = str(Path(__file__).resolve().parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.utils.google_maps_api import GoogleMapsAPI  # type: ignore


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
    """Main function to generate and update city POI data."""
    print("Loading configuration...")
    config_data = load_config()
    
    # Get city pages - they are under client section
    client_data = config_data.get('client', {})
    city_pages = client_data.get('city_pages', [])
    if not city_pages:
        print("No city pages found in configuration.")
        return
    
    print(f"Found {len(city_pages)} city pages.")
    
    # Initialize Google Maps API (without API key, will use mock data)
    maps_api = GoogleMapsAPI()
    
    updated_count = 0
    
    for i, city_page in enumerate(city_pages):
        city_name = city_page.get('city_name', 'Unknown')
        print(f"\\nProcessing {i+1}/{len(city_pages)}: {city_name}")
        
        # Check if places_of_interest already has content
        existing_pois = city_page.get('places_of_interest', [])
        if existing_pois:
            print(f"  POI data already exists for {city_name} ({len(existing_pois)} items), skipping...")
            continue
            
        try:
            # Generate POI data using mock data (since no API key)
            print(f"  Generating POI data for {city_name}...")
            poi_data = maps_api.get_city_poi_data(city_name)
            
            if poi_data:
                # Convert to the format expected in the YAML config
                formatted_pois = []
                for poi in poi_data:
                    formatted_pois.append({
                        'name': poi['name'],
                        'embed_url': poi['embed_url']
                    })
                
                # Update the city page with the POI data
                city_page['places_of_interest'] = formatted_pois
                updated_count += 1
                print(f"  [OK] Generated {len(formatted_pois)} POIs for {city_name}")
                
                # Show a preview of the POIs
                for poi in formatted_pois[:2]:  # Show first 2
                    print(f"    - {poi['name']}")
                    
            else:
                print(f"  [WARN] Could not generate POI data for {city_name}")
                
        except Exception as e:
            print(f"  [ERROR] Error processing {city_name}: {str(e)}")
            continue
    
    if updated_count > 0:
        print(f"\\nSaving updated configuration with {updated_count} cities having new POI data...")
        save_config(config_data)
        print("[SUCCESS] Configuration updated successfully!")
    else:
        print("\\nNo cities needed POI data updates.")


if __name__ == "__main__":
    main()