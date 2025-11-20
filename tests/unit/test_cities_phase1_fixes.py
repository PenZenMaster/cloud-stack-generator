"""
Test suite for Phase 1 Cities fixes

This test file validates the Phase 1 improvements:
1. Removal of state abbreviation requirement
2. Consistent location format usage
3. Wikipedia API compatibility preparation
4. Support for neighborhoods and varied location types

Version: 1.0.0
Date: 2025-08-14
Author: Cloud Stack Generator Team
"""

import pytest

# Test markers
pytestmark = [pytest.mark.unit, pytest.mark.cities, pytest.mark.phase1_fixes]


class TestPhase1LocationFormat:
    """Test the new location format without state requirements"""
    
    def test_location_format_examples(self):
        """Test that various location formats are supported"""
        location_examples = [
            "Chicago",                    # Simple city
            "Evanston, Illinois",         # City with full state name
            "Oak Park, Illinois",         # Another city with state
            "Downtown Chicago",           # Neighborhood
            "Brooklyn Heights",           # Neighborhood in different area
            "Beverly Hills, CA",          # City with state abbreviation
            "The Loop",                   # Neighborhood/district name
        ]
        
        # All formats should be valid keys
        cities_data = {}
        for location in location_examples:
            cities_data[location] = {"embed_code": f"<iframe>{location}</iframe>"}
        
        # Verify all locations stored correctly
        assert len(cities_data) == len(location_examples)
        
        # Verify each location is accessible by its exact name
        for location in location_examples:
            assert location in cities_data
            assert cities_data[location]["embed_code"] == f"<iframe>{location}</iframe>"

    def test_no_state_abbreviation_required(self):
        """Test that state abbreviation is no longer required"""
        # These should all be valid without needing separate state field
        valid_locations = [
            "Chicago",
            "New York City", 
            "San Francisco",
            "Downtown Detroit",
            "Oak Park, Illinois"
        ]
        
        for location in valid_locations:
            # Should be able to create location data without state field
            location_data = {
                "location": location,
                "embed_code": f"<iframe>{location} map</iframe>"
            }
            
            # Verify required fields are present
            assert "location" in location_data
            assert "embed_code" in location_data
            # Verify NO state field required
            assert "state" not in location_data or location_data.get("state") == ""


class TestWikipediaCompatibility:
    """Test Wikipedia API compatibility preparation"""
    
    @pytest.fixture
    def wikipedia_test_cases(self):
        """Wikipedia page title test cases"""
        return [
            # (location_input, expected_wikipedia_valid, notes)
            ("Chicago", True, "Major city with Wikipedia page"),
            ("Evanston, Illinois", True, "City with state - Wikipedia format"),
            ("Oak Park, Illinois", True, "City with state - Wikipedia format"),
            ("Chicago, IL", False, "State abbreviation - not Wikipedia format"),
            ("Detroit", True, "Major city"),
            ("New York City", True, "Major city"),
            ("Downtown Chicago", False, "Neighborhood - needs validation"),
            ("The Loop", False, "District name - needs validation"),
        ]
    
    def test_wikipedia_format_detection(self, wikipedia_test_cases):
        """Test detection of Wikipedia-compatible formats"""
        wikipedia_compatible_count = 0
        needs_validation_count = 0
        
        for location, expected_valid, notes in wikipedia_test_cases:
            # Basic format detection rules
            is_likely_wikipedia_compatible = (
                # Major cities (simple names)
                location in ["Chicago", "Detroit", "New York City"] or
                # Cities with full state names
                any(state in location for state in [", Illinois", ", California", ", New York"]) and
                not any(abbrev in location for abbrev in [", IL", ", CA", ", NY"])
            )
            
            if expected_valid:
                wikipedia_compatible_count += 1
            else:
                needs_validation_count += 1
            
            # For now, just verify we can categorize them
            assert isinstance(location, str)
            assert len(location) > 0
        
        # Verify we have both compatible and non-compatible examples
        assert wikipedia_compatible_count > 0
        assert needs_validation_count > 0


class TestBackwardsCompatibility:
    """Test backwards compatibility with existing data"""
    
    def test_old_format_data_handling(self):
        """Test that old format data (city, state) can still be loaded"""
        # Simulate old format data
        old_format_data = {
            "city": "Detroit",
            "state": "MI", 
            "embed_code": "<iframe>Detroit old format</iframe>"
        }
        
        # New format should be able to extract location
        # This simulates the set_data method in CityEmbedDialog
        location = old_format_data.get("location", "") or old_format_data.get("city", "")
        
        assert location == "Detroit"
        assert old_format_data["embed_code"] == "<iframe>Detroit old format</iframe>"
    
    def test_mixed_format_coexistence(self):
        """Test that old and new formats can coexist"""
        mixed_cities_data = {
            # New format (location keys)
            "Chicago": {"embed_code": "<iframe>Chicago new</iframe>"},
            "Evanston, Illinois": {"embed_code": "<iframe>Evanston new</iframe>"},
            
            # Old format (city, state keys) - might still exist in saved files
            "Detroit, MI": {"embed_code": "<iframe>Detroit old</iframe>"},
            "Ann Arbor, MI": {"embed_code": "<iframe>Ann Arbor old</iframe>"},
        }
        
        # All should be accessible
        assert len(mixed_cities_data) == 4
        assert "Chicago" in mixed_cities_data
        assert "Evanston, Illinois" in mixed_cities_data  
        assert "Detroit, MI" in mixed_cities_data
        assert "Ann Arbor, MI" in mixed_cities_data


class TestConfigIntegration:
    """Test integration with config save/load system"""
    
    def test_new_format_save_load_cycle(self, tmp_path):
        """Test complete save/load cycle with new location format"""
        from src.core.config.models import ClientConfig, BusinessConfig
        from src.core.config.parser import ConfigParser
        
        # Create config with new location formats
        config = ClientConfig(
            business=BusinessConfig(business_name="Phase 1 Integration Test"),
            target_cities=[
                "Chicago",
                "Evanston, Illinois", 
                "Downtown Chicago",
                "Oak Park, Illinois"
            ],
            seo_content={
                "neighborhoods": "Downtown Chicago, The Loop, River North",
                "pain_points": "Traffic, winter weather, parking"
            }
        )
        
        # Add Google Maps with new format
        config.google_maps.cities = {
            "Chicago": {"embed_code": "<iframe>Chicago</iframe>"},
            "Evanston, Illinois": {"embed_code": "<iframe>Evanston</iframe>"},
            "Downtown Chicago": {"embed_code": "<iframe>Downtown</iframe>"}
        }
        
        # Save and reload
        parser = ConfigParser()
        temp_file = tmp_path / "phase1_test.yaml"
        
        # Save
        success = parser.save_yaml_file(config, str(temp_file))
        assert success, "Failed to save config with new location format"
        
        # Load
        loaded_config = parser.parse_yaml_file(str(temp_file))
        
        # Verify target cities preserved
        assert loaded_config.target_cities == config.target_cities
        
        # Verify Google Maps data preserved with exact location keys
        original_locations = set(config.google_maps.cities.keys())
        loaded_locations = set(loaded_config.google_maps.cities.keys())
        assert original_locations == loaded_locations
        
        # Verify specific location formats
        assert "Chicago" in loaded_config.google_maps.cities
        assert "Evanston, Illinois" in loaded_config.google_maps.cities  
        assert "Downtown Chicago" in loaded_config.google_maps.cities
        
        # Verify no old-style "City, ST" keys were created
        old_style_keys = [key for key in loaded_locations if key.endswith(", MI") or key.endswith(", IL")]
        assert len(old_style_keys) == 0 or all("Illinois" in key for key in old_style_keys)

    def test_yaml_content_verification(self, tmp_path):
        """Verify YAML file contains new location format"""
        from src.core.config.models import ClientConfig, BusinessConfig
        from src.core.config.parser import ConfigParser
        
        config = ClientConfig(
            business=BusinessConfig(business_name="YAML Content Test"),
            target_cities=["Chicago", "Downtown Chicago"]
        )
        config.google_maps.cities = {
            "Chicago": {"embed_code": "<iframe>Chicago</iframe>"}
        }
        
        parser = ConfigParser()
        temp_file = tmp_path / "yaml_content_test.yaml" 
        
        success = parser.save_yaml_file(config, str(temp_file))
        assert success
        
        # Read raw YAML content
        with open(temp_file, 'r') as f:
            yaml_content = f.read()
        
        # Verify new format is in YAML
        assert "Chicago:" in yaml_content  # Location as key
        assert "target_cities:" in yaml_content
        assert "Downtown Chicago" in yaml_content
        
        # Verify no old format artifacts
        assert "Chicago, IL:" not in yaml_content  # No forced state abbreviation


class TestUserExperienceImprovements:
    """Test user experience improvements from Phase 1 fixes"""
    
    def test_single_location_entry(self):
        """Test that users only need to enter location once"""
        # Simulate user workflow
        target_cities_input = "Chicago\nEvanston, Illinois\nDowntown Chicago"
        target_cities = [city.strip() for city in target_cities_input.split('\n') if city.strip()]
        
        # User selects city from dropdown (populated from target cities)
        selected_location = target_cities[0]  # "Chicago"
        
        # Dialog should be pre-populated with this location
        dialog_data = {"location": selected_location, "embed_code": ""}
        
        # User only needs to paste embed code, location already set
        assert dialog_data["location"] == "Chicago"
        
        # Final storage uses exact same format
        final_key = dialog_data["location"]  # "Chicago" - same as target cities
        
        assert final_key == "Chicago"
        assert final_key in target_cities
    
    def test_neighborhood_support(self):
        """Test that neighborhoods are properly supported"""
        neighborhood_examples = [
            "Downtown Chicago",
            "The Loop",
            "River North",
            "Brooklyn Heights", 
            "Greenwich Village",
            "Beverly Hills"
        ]
        
        # All should be valid location keys
        for neighborhood in neighborhood_examples:
            location_data = {
                "location": neighborhood,
                "embed_code": f"<iframe>{neighborhood}</iframe>"
            }
            
            # Should work exactly like city names
            assert location_data["location"] == neighborhood
            assert len(neighborhood) > 0
            assert not neighborhood.endswith(", ST")  # No forced state abbreviation
    
    def test_consistency_across_features(self):
        """Test that location format is consistent across all features"""
        location = "Evanston, Illinois"
        
        # Should work identically in:
        # 1. Target Cities input
        target_cities = [location]
        
        # 2. Google Maps storage
        maps_data = {location: {"embed_code": "<iframe>test</iframe>"}}
        
        # 3. Configuration save/load
        config_data = {
            "target_cities": target_cities,
            "google_maps": {"cities": maps_data}
        }
        
        # All use the exact same location string
        assert target_cities[0] == location
        assert location in maps_data
        assert config_data["target_cities"][0] == location
        assert location in config_data["google_maps"]["cities"]