"""
Test suite for config_parser.py
Following TDD approach - these tests define the expected behavior

Version: 1.0.1
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from src.core.config_parser import ConfigParser
except ImportError:
    # Skip tests if modules not implemented yet
    pytest.skip("Config parser not implemented yet", allow_module_level=True)


class TestConfigParser:
    """Test suite for YAML configuration parsing and validation"""

    def test_config_parser_exists(self):
        """Test that ConfigParser class exists"""
        parser = ConfigParser()
        assert parser is not None

    def test_parse_valid_complete_config(self, sample_config_dict):
        """Test parsing a complete, valid configuration"""
        parser = ConfigParser()
        config = parser.parse(sample_config_dict)

        # Test client basic info
        assert config.client.business_name == "Acme Professional Services"
        assert config.client.domain == "https://acmeprofessional.com"
        assert config.client.industry == "Professional Services"

        # Test contact info (NAP)
        assert config.client.contact.name == "Acme Professional Services"
        expected_address = "123 Main St, Anytown, ST 12345"
        assert config.client.contact.address == expected_address
        assert config.client.contact.phone == "+1-555-123-4567"

    def test_parse_minimal_required_config(self, minimal_config_dict):
        """Test parsing with only required fields"""
        parser = ConfigParser()
        config = parser.parse(minimal_config_dict)

        assert config.client.business_name == "Test Business"
        assert config.client.contact.phone == "+1-555-987-6543"
        assert len(config.client.pages) == 1
