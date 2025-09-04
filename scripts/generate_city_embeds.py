#!/usr/bin/env python3
"""
Script to generate Wikipedia embed codes for all cities and update YAML config

This script:
1. Loads all city pages from the config
2. Generates Wikipedia embed codes for cities that don't have them
3. Updates the YAML config with the new embed codes
4. Preserves existing embed codes where they exist
"""

import sys
import os
from pathlib import Path
from typing import Dict, List, Any
import yaml

# Add src to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

try:
    from core.utils.wikipedia_api import WikipediaAPI
except ModuleNotFoundError:
    print(
        "Error: The module 'core.utils.wikipedia_api' could not be found. Ensure the 'src' directory is correctly structured and added to the Python path."
    )
    sys.exit(1)


def load_config() -> Dict[str, Any]:
    """Load the current configuration from YAML file."""
    config_path = (
        Path(__file__).parent.parent
        / "config"
        / "clients"
        / "salvo_metal_works_config.yaml"
    )

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_config(config_data: Dict[str, Any]) -> None:
    """Save the updated configuration to YAML file."""
    config_path = (
        Path(__file__).parent.parent
        / "config"
        / "clients"
        / "salvo_metal_works_config.yaml"
    )

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(
            config_data, f, default_flow_style=False, allow_unicode=True, width=80
        )


def main():
    """Main function to generate and update city embed codes."""
    print("Loading configuration...")
    config_data = load_config()

    # Get city pages - they are under client section
    client_data = config_data.get("client", {})
    city_pages = client_data.get("city_pages", [])
    if not city_pages:
        print("No city pages found in configuration.")
        return

    print(f"Found {len(city_pages)} city pages.")

    # Initialize Wikipedia API
    wiki_api = WikipediaAPI()

    updated_count = 0

    for i, city_page in enumerate(city_pages):
        city_name = city_page.get("city_name", "Unknown")
        print(f"\nProcessing {i+1}/{len(city_pages)}: {city_name}")

        # Check if city_image exists
        if "city_image" not in city_page:
            print(f"  No city_image section found for {city_name}, skipping...")
            continue

        city_image = city_page["city_image"]

        # Check if embed_code already exists
        if city_image.get("embed_code", "").strip():
            print(f"  Embed code already exists for {city_name}, skipping...")
            continue

        try:
            # Generate Wikipedia image info with embed code
            print(f"  Fetching Wikipedia information for {city_name}...")
            image_info = wiki_api.get_city_image_info(city_name)

            if image_info and image_info.get("embed_code"):
                # Update the city_image with the complete Wikipedia info
                city_image["image_url"] = image_info.get("image_url", "")
                city_image["alt_text"] = image_info.get(
                    "alt_text", f"View of {city_name}"
                )
                city_image["caption"] = image_info.get(
                    "attribution", f"Wikipedia - {city_name}"
                )
                city_image["credit"] = image_info.get(
                    "attribution", f"Wikipedia - {city_name}"
                )
                city_image["source"] = image_info.get(
                    "source_url", image_info.get("wikipedia_page", "")
                )
                city_image["embed_code"] = image_info["embed_code"]

                updated_count += 1
                print(f"  [OK] Wikipedia data fetched and saved for {city_name}")

                # Log the image URL we found
                if image_info.get("image_url"):
                    print(f"      Image: {image_info['image_url']}")

            else:
                print(f"  [WARN] Could not fetch Wikipedia information for {city_name}")

        except Exception as e:
            print(f"  [ERROR] Error processing {city_name}: {str(e)}")
            continue

    if updated_count > 0:
        print(f"\nSaving updated configuration with {updated_count} new embed codes...")
        save_config(config_data)
        print("[SUCCESS] Configuration updated successfully!")
    else:
        print("\nNo cities needed embed code updates.")


if __name__ == "__main__":
    main()
