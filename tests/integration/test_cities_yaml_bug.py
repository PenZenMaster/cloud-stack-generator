"""
Test to reproduce and verify the Cities YAML updating bug

This test specifically targets the issue reported:
"When Testing Cities Location tab, the auto-save does not update the yaml file, 
clicking on the Save Configuration does not update the yaml file"

Version: 1.0.0
Date: 2025-08-14
Author: Cloud Stack Generator Team
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml

# Test markers
pytestmark = [pytest.mark.integration, pytest.mark.cities, pytest.mark.yaml_bug]


class TestCitiesYAMLBug:
    """Reproduce and test the cities YAML updating bug"""
    
    def test_reproduce_yaml_not_updating_bug(self, tmp_path):
        """Reproduce the exact bug: Cities data not being saved to YAML"""
        from src.core.config.models import ClientConfig, BusinessConfig, ContactConfig, BrandingConfig
        from src.core.config.parser import ConfigParser
        
        # Step 1: Create a basic config (simulating existing business data)
        config = ClientConfig(
            business=BusinessConfig(
                business_name="Bug Test Business",
                domain="https://bugtest.com",
                industry="Test Services"
            ),
            contact=ContactConfig(
                name="Bug Test Contact",
                phone="555-BUG-TEST",
                address="123 Bug St, Test City, ST 12345",
                email="bug@test.com"
            ),
            branding=BrandingConfig(
                primary_color="#ff0000",
                secondary_color="#00ff00"
            )
        )
        
        # Step 2: Save initial config (should work)
        parser = ConfigParser()
        yaml_file = tmp_path / "bug_test_config.yaml"
        success = parser.save_yaml_file(config, str(yaml_file))
        
        assert success, "Initial save failed"
        assert yaml_file.exists(), "YAML file not created"
        
        # Step 3: Add cities data (simulating user entering cities data)
        config.target_cities = ["Detroit", "Ann Arbor", "Grand Rapids"]
        config.seo_content = {
            "neighborhoods": "Downtown Detroit, Midtown, Corktown",
            "pain_points": "Winter weather challenges, road construction",
            "case_studies": "Historic downtown renovation project",
            "testimonial": "Great service in Detroit area",
            "directions": "Serving greater Detroit metro area",
            "local_faq": "Do you serve Detroit downtown?\\nWhat are response times?"
        }
        
        # Add Google Maps data
        config.google_maps.cities = {
            "Detroit, MI": {"embed_code": "<iframe>Detroit Map</iframe>"},
            "Grand Rapids, MI": {"embed_code": "<iframe>Grand Rapids Map</iframe>"}
        }
        
        # Step 4: Save updated config (this should include cities data)
        success = parser.save_yaml_file(config, str(yaml_file))
        assert success, "Updated save failed"
        
        # Step 5: Read the raw YAML file content
        with open(yaml_file, 'r') as f:
            yaml_content = f.read()
        
        print("Generated YAML content:")
        print("=" * 60)
        print(yaml_content)
        print("=" * 60)
        
        # Step 6: Check if cities data is actually in the YAML file
        yaml_checks = {
            "target_cities in file": "target_cities:" in yaml_content,
            "seo_content in file": "seo_content:" in yaml_content,
            "Detroit in file": "Detroit" in yaml_content,
            "neighborhoods in file": "neighborhoods:" in yaml_content,
            "google_maps in file": "google_maps:" in yaml_content
        }
        
        print("\\nYAML Content Checks:")
        print("-" * 30)
        for check_name, result in yaml_checks.items():
            status = "PASS" if result else "FAIL"
            print(f"{status}: {check_name}")
        
        # Step 7: Verify cities data is present (this should pass after our fixes)
        assert "target_cities:" in yaml_content, "target_cities missing from YAML"
        assert "seo_content:" in yaml_content, "seo_content missing from YAML" 
        assert "Detroit" in yaml_content, "Detroit missing from YAML"
        assert "neighborhoods:" in yaml_content, "neighborhoods missing from YAML"
        
        # Step 8: Load back and verify data integrity
        loaded_config = parser.parse_yaml_file(str(yaml_file))
        
        assert loaded_config.target_cities == config.target_cities, "target_cities not preserved"
        assert loaded_config.seo_content == config.seo_content, "seo_content not preserved"
        assert loaded_config.google_maps.cities == config.google_maps.cities, "google_maps not preserved"
        
        print("\\n✓ Bug test PASSED: Cities data is properly saved and loaded")
    
    def test_parser_generate_yaml_dict_includes_cities(self):
        """Test that ConfigParser.generate_yaml_dict includes cities data"""
        from src.core.config.models import ClientConfig, BusinessConfig
        from src.core.config.parser import ConfigParser
        
        # Create config with cities data
        config = ClientConfig(
            business=BusinessConfig(business_name="Parser Test"),
            target_cities=["Test City A", "Test City B"],
            seo_content={"test_field": "test_value"}
        )
        
        # Use parser's generate_yaml_dict method
        parser = ConfigParser()
        yaml_dict = parser.generate_yaml_dict(config)
        
        # Check if cities data is included
        client_section = yaml_dict.get("client", {})
        
        print("Parser generated YAML dict keys:", list(client_section.keys()))
        
        # These assertions should pass after our parser fixes
        assert "target_cities" in client_section, "target_cities missing from parser YAML dict"
        assert "seo_content" in client_section, "seo_content missing from parser YAML dict"
        
        # Verify data integrity
        assert client_section["target_cities"] == ["Test City A", "Test City B"]
        assert client_section["seo_content"] == {"test_field": "test_value"}
    
    def test_compare_clientconfig_vs_parser_yaml_generation(self):
        """Compare ClientConfig.to_yaml_dict vs ConfigParser.generate_yaml_dict"""
        from src.core.config.models import ClientConfig, BusinessConfig
        from src.core.config.parser import ConfigParser
        
        # Create identical config
        config = ClientConfig(
            business=BusinessConfig(business_name="Comparison Test"),
            target_cities=["Compare City"],
            seo_content={"compare_field": "compare_value"}
        )
        
        # Generate YAML using both methods
        config_yaml = config.to_yaml_dict()
        
        parser = ConfigParser()
        parser_yaml = parser.generate_yaml_dict(config)
        
        # Compare client sections
        config_client = config_yaml.get("client", {})
        parser_client = parser_yaml.get("client", {})
        
        print("ClientConfig method keys:", set(config_client.keys()))
        print("ConfigParser method keys:", set(parser_client.keys()))
        
        # Check cities data in both
        cities_checks = {
            "target_cities": {
                "config_method": "target_cities" in config_client,
                "parser_method": "target_cities" in parser_client
            },
            "seo_content": {
                "config_method": "seo_content" in config_client, 
                "parser_method": "seo_content" in parser_client
            }
        }
        
        print("\\nCities data presence comparison:")
        for field, methods in cities_checks.items():
            print(f"{field}:")
            print(f"  ClientConfig.to_yaml_dict: {methods['config_method']}")
            print(f"  ConfigParser.generate_yaml_dict: {methods['parser_method']}")
            
            # Both methods should include cities data
            assert methods['config_method'], f"{field} missing from ClientConfig.to_yaml_dict"
            assert methods['parser_method'], f"{field} missing from ConfigParser.generate_yaml_dict"
    
    def test_existing_yaml_file_update_with_cities(self, tmp_path):
        """Test updating an existing YAML file with cities data"""
        from src.core.config.models import ClientConfig, BusinessConfig, ContactConfig
        from src.core.config.parser import ConfigParser
        
        parser = ConfigParser()
        yaml_file = tmp_path / "existing_config.yaml"
        
        # Step 1: Create and save initial config without cities
        initial_config = ClientConfig(
            business=BusinessConfig(business_name="Existing Business"),
            contact=ContactConfig(name="Existing Contact", phone="555-0000")
        )
        
        success = parser.save_yaml_file(initial_config, str(yaml_file))
        assert success, "Failed to create initial YAML file"
        
        # Verify no cities data initially
        with open(yaml_file, 'r') as f:
            initial_content = f.read()
        
        assert "target_cities:" not in initial_content
        assert "seo_content:" not in initial_content
        
        # Step 2: Load, add cities data, save again
        loaded_config = parser.parse_yaml_file(str(yaml_file))
        
        # Add cities data
        loaded_config.target_cities = ["Added City 1", "Added City 2"]
        loaded_config.seo_content = {"added_field": "added_value"}
        
        # Save updated config
        success = parser.save_yaml_file(loaded_config, str(yaml_file))
        assert success, "Failed to save updated config"
        
        # Step 3: Verify cities data is now in the file
        with open(yaml_file, 'r') as f:
            updated_content = f.read()
        
        print("Updated YAML content:")
        print("-" * 40)
        print(updated_content)
        print("-" * 40)
        
        # These should pass after our fixes
        assert "target_cities:" in updated_content, "target_cities not added to existing file"
        assert "seo_content:" in updated_content, "seo_content not added to existing file"
        assert "Added City 1" in updated_content, "Cities data not in file"
        assert "added_field:" in updated_content, "SEO content not in file"
        
        # Step 4: Load again to verify data persistence
        final_config = parser.parse_yaml_file(str(yaml_file))
        
        assert final_config.target_cities == ["Added City 1", "Added City 2"]
        assert final_config.seo_content == {"added_field": "added_value"}
        
        print("\\n✓ Existing file update test PASSED")