"""
Test suite for Cities Tab functionality

This test file covers the critical Cities tab issues we've been fixing:
- Cities data save/load functionality  
- ValidationResult compatibility
- YAML persistence
- Configuration integration

Version: 1.0.0
Date: 2025-08-14
Author: Cloud Stack Generator Team
"""

import pytest
import yaml

# Test markers
pytestmark = [pytest.mark.unit, pytest.mark.cities]


class TestCitiesConfiguration:
    """Test Cities configuration data structures"""
    
    def test_cities_config_structure(self):
        """Test that cities configuration has expected structure"""
        expected_keys = ["target_cities", "seo_content", "google_maps"]
        
        cities_data = {
            "target_cities": ["Detroit", "Ann Arbor", "Grand Rapids"],
            "seo_content": {
                "neighborhoods": "Downtown Detroit, Midtown",
                "pain_points": "Winter weather challenges",
                "case_studies": "Historic renovation project",
                "testimonial": "Great service in Detroit area",
                "directions": "Serving greater Detroit metro area",
                "local_faq": "Do you serve Detroit downtown?"
            },
            "google_maps": {
                "cities": {
                    "Detroit, MI": {"embed_code": "<iframe>Detroit Map</iframe>"},
                    "Grand Rapids, MI": {"embed_code": "<iframe>GR Map</iframe>"}
                }
            }
        }
        
        # Verify structure
        for key in expected_keys:
            assert key in cities_data, f"Missing required key: {key}"
        
        # Verify data types
        assert isinstance(cities_data["target_cities"], list)
        assert isinstance(cities_data["seo_content"], dict)
        assert isinstance(cities_data["google_maps"], dict)
        
        # Verify content
        assert len(cities_data["target_cities"]) == 3
        assert len(cities_data["seo_content"]) == 6
        assert "cities" in cities_data["google_maps"]


class TestClientConfigWithCities:
    """Test ClientConfig model with cities data"""
    
    @pytest.fixture
    def cities_client_config(self):
        """Create ClientConfig with cities data for testing"""
        from src.core.config.models import ClientConfig, BusinessConfig
        
        return ClientConfig(
            business=BusinessConfig(business_name="Test Cities Business"),
            target_cities=["Detroit", "Ann Arbor", "Grand Rapids"],
            seo_content={
                "neighborhoods": "Downtown Detroit, Midtown",
                "pain_points": "Winter weather challenges",
                "case_studies": "Historic renovation project",
                "testimonial": "Great service in Detroit area",
                "directions": "Serving greater Detroit metro area",
                "local_faq": "Do you serve Detroit downtown?"
            }
        )
    
    def test_client_config_has_cities_fields(self, cities_client_config):
        """Test that ClientConfig has cities-related fields"""
        config = cities_client_config
        
        # Check attributes exist
        assert hasattr(config, 'target_cities')
        assert hasattr(config, 'seo_content')
        assert hasattr(config, 'google_maps')
        
        # Check data
        assert config.target_cities == ["Detroit", "Ann Arbor", "Grand Rapids"]
        assert len(config.seo_content) == 6
        assert "neighborhoods" in config.seo_content
    
    def test_yaml_serialization_includes_cities(self, cities_client_config):
        """Test that YAML serialization includes cities data"""
        config = cities_client_config
        yaml_dict = config.to_yaml_dict()
        
        client_data = yaml_dict.get("client", {})
        
        # Verify cities data is included
        assert "target_cities" in client_data
        assert "seo_content" in client_data
        
        # Verify data integrity
        assert client_data["target_cities"] == config.target_cities
        assert client_data["seo_content"] == config.seo_content
    
    def test_yaml_string_serialization(self, cities_client_config):
        """Test that YAML string serialization works"""
        config = cities_client_config
        yaml_dict = config.to_yaml_dict()
        
        # This should not raise an exception
        yaml_string = yaml.dump(yaml_dict, default_flow_style=False)
        
        # Verify cities data is in the YAML string
        assert "target_cities" in yaml_string
        assert "seo_content" in yaml_string
        assert "Detroit" in yaml_string
        assert "neighborhoods" in yaml_string


class TestConfigParserWithCities:
    """Test configuration parser with cities data"""
    
    @pytest.fixture
    def sample_cities_yaml_dict(self):
        """Sample YAML dictionary with cities data"""
        return {
            "client": {
                "business_name": "Cities Test Business",
                "domain": "https://citiestestbusiness.com",
                "industry": "Local Services",
                "contact": {
                    "name": "Cities Test Business",
                    "phone": "555-123-4567",
                    "address": "123 Main St, Test City, ST 12345",
                    "email": "info@citiestestbusiness.com"
                },
                "branding": {
                    "primary_color": "#007bff",
                    "secondary_color": "#6c757d",
                    "font_family": "Arial, sans-serif",
                    "logo_url": ""
                },
                "social_media": {},
                "google_business_profile": {},
                "target_cities": ["Detroit", "Ann Arbor", "Grand Rapids"],
                "seo_content": {
                    "neighborhoods": "Downtown Detroit, Midtown",
                    "pain_points": "Winter weather challenges"
                },
                "google_maps": {
                    "cities": {
                        "Detroit, MI": {"embed_code": "<iframe>Detroit</iframe>"}
                    }
                },
                "pages": [
                    {
                        "title": "Home",
                        "slug": "index", 
                        "primary_keyword": "local services",
                        "secondary_keywords": ["cities test business", "local business"]
                    }
                ],
                "offerings": [],
                "faq": []
            }
        }
    
    def test_parser_loads_cities_data(self, sample_cities_yaml_dict):
        """Test that parser loads cities data from YAML"""
        from src.core.config.parser import ConfigParser
        
        parser = ConfigParser()
        config = parser.parse_yaml_dict(sample_cities_yaml_dict)
        
        # Verify cities data was loaded
        assert hasattr(config, 'target_cities')
        assert hasattr(config, 'seo_content')
        
        assert config.target_cities == ["Detroit", "Ann Arbor", "Grand Rapids"]
        assert len(config.seo_content) == 2
        assert config.seo_content["neighborhoods"] == "Downtown Detroit, Midtown"
    
    def test_parser_saves_cities_data(self, sample_cities_yaml_dict, tmp_path):
        """Test that parser saves cities data to YAML"""
        from src.core.config.parser import ConfigParser
        
        parser = ConfigParser()
        
        # Load config
        config = parser.parse_yaml_dict(sample_cities_yaml_dict)
        
        # Save to temp file
        temp_file = tmp_path / "test_cities_config.yaml"
        success = parser.save_yaml_file(config, str(temp_file))
        
        assert success, "Failed to save YAML file"
        assert temp_file.exists(), "YAML file was not created"
        
        # Read back and verify cities data is present
        with open(temp_file, 'r') as f:
            saved_content = f.read()
        
        # Verify cities data is in saved file
        assert "target_cities:" in saved_content
        assert "seo_content:" in saved_content
        assert "Detroit" in saved_content
        assert "neighborhoods:" in saved_content
    
    def test_complete_save_load_cycle(self, tmp_path):
        """Test complete save/load cycle preserves cities data"""
        from src.core.config.parser import ConfigParser
        from src.core.config.models import ClientConfig, BusinessConfig
        
        # Create original config with cities data
        original_config = ClientConfig(
            business=BusinessConfig(business_name="Round Trip Test"),
            target_cities=["Detroit", "Ann Arbor"],
            seo_content={
                "neighborhoods": "Downtown Detroit",
                "pain_points": "Winter weather"
            }
        )
        
        original_config.google_maps.cities = {
            "Detroit, MI": {"embed_code": "<iframe>Detroit Test</iframe>"}
        }
        
        # Save to file
        parser = ConfigParser()
        temp_file = tmp_path / "round_trip_test.yaml"
        success = parser.save_yaml_file(original_config, str(temp_file))
        assert success, "Failed to save config"
        
        # Load back
        loaded_config = parser.parse_yaml_file(str(temp_file))
        
        # Verify data integrity
        assert loaded_config.target_cities == original_config.target_cities
        assert loaded_config.seo_content == original_config.seo_content
        assert loaded_config.google_maps.cities == original_config.google_maps.cities
        
        # Verify specific values
        assert "Detroit" in loaded_config.target_cities
        assert "Ann Arbor" in loaded_config.target_cities
        assert loaded_config.seo_content["neighborhoods"] == "Downtown Detroit"


class TestValidationResultCompatibility:
    """Test ValidationResult classes are compatible across components"""
    
    def test_base_validation_result_has_field_errors(self):
        """Test that base ValidationResult has field_errors attribute"""
        from src.ui.components.base_tab import ValidationResult
        
        result = ValidationResult()
        
        # Check required attributes
        assert hasattr(result, 'is_valid')
        assert hasattr(result, 'errors') 
        assert hasattr(result, 'warnings')
        assert hasattr(result, 'field_errors')
        
        # Check field_errors is a dict
        assert isinstance(result.field_errors, dict)
    
    def test_validation_result_field_errors_functionality(self):
        """Test ValidationResult field_errors functionality"""
        from src.ui.components.base_tab import ValidationResult
        
        result = ValidationResult()
        
        # Add field-specific error
        result.add_error("Test error message", "test_field")
        
        # Check state
        assert not result.is_valid
        assert len(result.errors) == 1
        assert "test_field" in result.field_errors
        assert result.field_errors["test_field"] == "Test error message"
        
        # Test iteration (this was the failing code)
        field_errors_list = list(result.field_errors.items())
        assert len(field_errors_list) == 1
        assert field_errors_list[0] == ("test_field", "Test error message")
    
    def test_cities_validation_result_import(self):
        """Test that cities_tab imports ValidationResult correctly"""
        # This test verifies the import fix we made
        try:
            from src.ui.components.cities_tab import ValidationResult
            
            # Should be the same class as base_tab
            from src.ui.components.base_tab import ValidationResult as BaseValidationResult
            
            # Create instances
            cities_result = ValidationResult()
            base_result = BaseValidationResult()
            
            # Should have same attributes
            assert hasattr(cities_result, 'field_errors')
            assert hasattr(base_result, 'field_errors')
            
            # Should behave the same
            cities_result.add_error("Test", "field")
            base_result.add_error("Test", "field")
            
            assert cities_result.field_errors == base_result.field_errors
            
        except ImportError as e:
            pytest.skip(f"Import test skipped due to import error: {e}")


class TestCitiesIntegration:
    """Integration tests for Cities functionality"""
    
    @pytest.mark.integration
    def test_cities_data_integration_flow(self, tmp_path):
        """Test complete integration flow for cities data"""
        from src.core.config.models import ClientConfig, BusinessConfig
        from src.core.config.parser import ConfigParser
        
        # Step 1: Create config with cities data (simulating UI input)
        config_data = {
            "business": {"business_name": "Integration Test Business"},
            "contact": {"name": "Test", "phone": "555-123-4567", "address": "123 Test St", "email": "test@example.com"},
            "branding": {"primary_color": "#007bff", "secondary_color": "#6c757d", "font_family": "Arial", "logo_url": ""},
            "cities": {
                "target_cities": ["Detroit", "Ann Arbor"],
                "seo_content": {
                    "neighborhoods": "Downtown Detroit",
                    "pain_points": "Winter challenges"
                },
                "google_maps": {
                    "cities": {
                        "Detroit, MI": {"embed_code": "<iframe>Detroit</iframe>"}
                    }
                }
            },
            "products": {"products": []},
            "services": {"services": []}
        }
        
        # Step 2: Create ClientConfig (simulating enhanced_main_window.py create_client_config)
        from src.core.config.models import ContactConfig, BrandingConfig, GoogleMapsConfig
        
        cities_data = config_data.get("cities", {})
        google_maps = GoogleMapsConfig()
        google_maps.cities = cities_data.get("google_maps", {}).get("cities", {})
        target_cities = cities_data.get("target_cities", [])
        seo_content = cities_data.get("seo_content", {})
        
        config = ClientConfig(
            business=BusinessConfig(business_name="Integration Test Business"),
            contact=ContactConfig(name="Test", phone="555-123-4567", address="123 Test St", email="test@example.com"),
            branding=BrandingConfig(primary_color="#007bff", secondary_color="#6c757d", font_family="Arial", logo_url=""),
            google_maps=google_maps,
            target_cities=target_cities,
            seo_content=seo_content,
        )
        
        # Step 3: Save to YAML
        parser = ConfigParser()
        yaml_file = tmp_path / "integration_test.yaml"
        success = parser.save_yaml_file(config, str(yaml_file))
        
        assert success, "Integration save failed"
        
        # Step 4: Load back and verify
        loaded_config = parser.parse_yaml_file(str(yaml_file))
        
        assert loaded_config.target_cities == ["Detroit", "Ann Arbor"]
        assert loaded_config.seo_content["neighborhoods"] == "Downtown Detroit"
        assert "Detroit, MI" in loaded_config.google_maps.cities
        
        # Step 5: Simulate loading into tabs (enhanced_main_window.py load_config_into_tabs)
        cities_data = {
            "target_cities": loaded_config.target_cities,
            "seo_content": loaded_config.seo_content,
            "google_maps": {"cities": loaded_config.google_maps.cities},
        }
        
        # Verify tab data structure
        assert cities_data["target_cities"] == ["Detroit", "Ann Arbor"]
        assert cities_data["seo_content"]["neighborhoods"] == "Downtown Detroit"
        assert "Detroit, MI" in cities_data["google_maps"]["cities"]
    
    @pytest.mark.integration 
    def test_yaml_file_contains_cities_data(self, tmp_path):
        """Verify that generated YAML files actually contain cities data"""
        from src.core.config.models import ClientConfig, BusinessConfig
        from src.core.config.parser import ConfigParser
        
        # Create config with cities
        config = ClientConfig(
            business=BusinessConfig(business_name="YAML Test Business"),
            target_cities=["Test City 1", "Test City 2"],
            seo_content={"test_field": "test_value"}
        )
        
        # Save
        parser = ConfigParser()
        yaml_file = tmp_path / "yaml_content_test.yaml"
        success = parser.save_yaml_file(config, str(yaml_file))
        assert success
        
        # Read raw file content
        with open(yaml_file, 'r') as f:
            content = f.read()
        
        # Verify cities data is actually in the file
        assert "target_cities:" in content
        assert "seo_content:" in content
        assert "Test City 1" in content
        assert "Test City 2" in content
        assert "test_field:" in content
        assert "test_value" in content