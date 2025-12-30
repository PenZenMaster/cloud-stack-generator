#!/usr/bin/env python
"""
Quick CLI script to generate a website from a config file
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.config.parser import load_config_from_file
from core.generators.page_generator import PageGenerator


def main():
    """Generate website from config file"""
    if len(sys.argv) < 2:
        print("Usage: python generate_site.py <config_file> [output_dir]")
        print("Example: python generate_site.py config/clients/pristine_portables_restroom_trailer_rentals_config.yaml")
        sys.exit(1)

    config_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "output/websites"

    print(f"Loading config from: {config_file}")
    config = load_config_from_file(config_file)

    # Ensure output directory exists
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    print(f"Generating website to: {output_dir}")
    generator = PageGenerator(output_base_dir=output_dir)

    print("Generating HTML pages...")
    result = generator.generate_complete_website(config)

    if result.success:
        print("\nWebsite generated successfully!")
        print(f"Files created: {len(result.generated_files)}")
        print(f"Output directory: {output_dir}")
        for file_path in result.generated_files[:5]:  # Show first 5
            print(f"  - {Path(file_path).name}")
        if len(result.generated_files) > 5:
            print(f"  ... and {len(result.generated_files) - 5} more files")
    else:
        print("\nGeneration failed!")
        print(f"Errors: {result.errors}")
        sys.exit(1)


if __name__ == "__main__":
    main()
