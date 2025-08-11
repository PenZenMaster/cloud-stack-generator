"""
Filename: tests/unit/test_business_tab.py
Path: E:/projects/cloud-stack-generator/tests/unit/test_business_tab.py
Description: Unit tests for BusinessTab component

Version: 1.0.0
Date: 2025-08-10
Author: Cloud Stack Generator Team
"""

import sys
import pytest
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QTimer
from PyQt6.QtTest import QTest
import os

# Add src directory to path for imports
project_root = os.path.join(os.path.dirname(__file__), "..", "..")
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

try:
    from ui.components.business_tab import BusinessTab
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Tried to import from: {src_path}")
    print(f"Current working directory: {os.getcwd()}")
    print("Make sure the files exist:")
    print("  - src/ui/components/base_tab.py")
    print("  - src/ui/components/business_tab.py")
    raise


class TestBusinessTab:
    """Test suite for BusinessTab component"""

    @classmethod
    def setup_class(cls):
        """Set up QApplication for all tests"""
        if not QApplication.instance():
            cls.app = QApplication([])
        else:
            cls.app = QApplication.instance()

    def setup_method(self):
        """Set up each test with a fresh BusinessTab instance"""
        self.business_tab = BusinessTab()
        # Show the widget to ensure proper initialization
        self.business_tab.show()
        # Process events to complete initialization
        QTest.qWait(100)  # Wait 100ms for signal processing

    def teardown_method(self):
        """Clean up after each test"""
        if hasattr(self, "business_tab"):
            self.business_tab.close()
            self.business_tab.deleteLater()
        QTest.qWait(50)  # Wait 50ms for cleanup

    def test_initialization(self):
        """Test that BusinessTab initializes correctly"""
        # Check that all widgets are created
        assert self.business_tab.business_name_input is not None
        assert self.business_tab.domain_input is not None
        assert self.business_tab.industry_input is not None
        assert self.business_tab.description_input is not None
        assert self.business_tab.char_counter_label is not None

        # Check initial states
        assert self.business_tab.business_name_input.text() == ""
        assert self.business_tab.domain_input.text() == ""
        assert self.business_tab.industry_input.currentText() == ""
        assert self.business_tab.description_input.toPlainText() == ""

        # Check that industry suggestions are loaded
        assert (
            self.business_tab.industry_input.count() > 20
        )  # Should have 20+ industries

    def test_get_config_data_empty(self):
        """Test getting configuration data when all fields are empty"""
        config_data = self.business_tab.get_config_data()

        expected = {
            "business_name": "",
            "domain": "",
            "industry": "",
            "description": "",
        }

        assert config_data == expected

    def test_set_config_data_basic(self):
        """Test setting basic configuration data"""
        test_data = {
            "business_name": "Salvo Metal Works",
            "domain": "https://www.salvometalworks.com",
            "industry": "Manufacturing",
            "description": "Professional metal fabrication services",
        }

        self.business_tab.set_config_data(test_data)

        # Verify data was set correctly
        assert self.business_tab.business_name_input.text() == "Salvo Metal Works"
        assert (
            self.business_tab.domain_input.text() == "https://www.salvometalworks.com"
        )
        assert self.business_tab.industry_input.currentText() == "Manufacturing"
        assert (
            self.business_tab.description_input.toPlainText()
            == "Professional metal fabrication services"
        )

    def test_set_config_data_custom_industry(self):
        """Test setting configuration data with custom industry"""
        test_data = {
            "business_name": "Tech Startup",
            "domain": "https://www.techstartup.com",
            "industry": "Custom AI Solutions",  # Not in predefined list
            "description": "",
        }

        self.business_tab.set_config_data(test_data)

        # Verify custom industry was added and selected
        assert self.business_tab.industry_input.currentText() == "Custom AI Solutions"

        # Verify it was added to the combo box
        items = [
            self.business_tab.industry_input.itemText(i)
            for i in range(self.business_tab.industry_input.count())
        ]
        assert "Custom AI Solutions" in items

    def test_get_required_fields(self):
        """Test that required fields are correctly identified"""
        required_fields = self.business_tab.get_required_fields()
        expected_fields = ["business_name", "domain", "industry"]

        assert set(required_fields) == set(expected_fields)

    def test_validation_empty_fields(self):
        """Test validation with empty required fields"""
        # Leave all fields empty
        result = self.business_tab.validate_data()

        assert not result.is_valid
        assert len(result.errors) == 3  # All required fields missing

        # Check specific field errors
        assert "business_name" in result.field_errors
        assert "domain" in result.field_errors
        assert "industry" in result.field_errors

    def test_validation_valid_data(self):
        """Test validation with valid data"""
        test_data = {
            "business_name": "Valid Business",
            "domain": "https://www.validbusiness.com",
            "industry": "Professional Services",
            "description": "A valid business description",
        }

        self.business_tab.set_config_data(test_data)
        result = self.business_tab.validate_data()

        assert result.is_valid
        assert len(result.errors) == 0

    def test_validation_invalid_url(self):
        """Test validation with invalid URL"""
        test_data = {
            "business_name": "Valid Business",
            "domain": "not-a-valid-url",
            "industry": "Professional Services",
        }

        self.business_tab.set_config_data(test_data)
        result = self.business_tab.validate_data()

        assert not result.is_valid
        assert "domain" in result.field_errors
        assert "valid website URL" in result.field_errors["domain"]

    def test_validation_short_fields(self):
        """Test validation with fields that are too short"""
        test_data = {
            "business_name": "A",  # Too short
            "domain": "https://www.valid.com",
            "industry": "IT",  # Too short
        }

        self.business_tab.set_config_data(test_data)
        result = self.business_tab.validate_data()

        assert not result.is_valid
        assert "business_name" in result.field_errors
        assert "industry" in result.field_errors

    def test_validation_long_description(self):
        """Test validation with very long description"""
        test_data = {
            "business_name": "Valid Business",
            "domain": "https://www.valid.com",
            "industry": "Professional Services",
            "description": "x" * 501,  # Over 500 character limit
        }

        self.business_tab.set_config_data(test_data)
        result = self.business_tab.validate_data()

        assert result.is_valid  # Still valid, just has warning
        assert len(result.warnings) > 0
        assert "quite long" in result.warnings[0]

    def test_url_formatting(self):
        """Test automatic URL formatting"""
        # Test various URL inputs that should be auto-formatted
        test_cases = [
            ("example.com", "https://www.example.com"),
            ("www.example.com", "https://www.example.com"),
            ("https://www.example.com", "https://www.example.com"),  # Already formatted
            ("http://example.com", "http://example.com"),  # Don't change http
        ]

        for input_url, expected_url in test_cases:
            # Set the input
            self.business_tab.domain_input.setText(input_url)
            # Trigger the formatting by simulating editingFinished
            self.business_tab._format_domain_url()
            # Check result
            actual_url = self.business_tab.domain_input.text()
            assert (
                actual_url == expected_url
            ), f"Input: {input_url}, Expected: {expected_url}, Got: {actual_url}"

    def test_clear_data(self):
        """Test clearing all data"""
        # First, set some data
        test_data = {
            "business_name": "Test Business",
            "domain": "https://www.test.com",
            "industry": "Technology",
            "description": "Test description",
        }

        self.business_tab.set_config_data(test_data)

        # Verify data is set
        assert self.business_tab.business_name_input.text() != ""

        # Clear data
        self.business_tab.clear_data()

        # Verify all fields are cleared
        assert self.business_tab.business_name_input.text() == ""
        assert self.business_tab.domain_input.text() == ""
        assert self.business_tab.industry_input.currentText() == ""
        assert self.business_tab.description_input.toPlainText() == ""

    def test_character_counter(self):
        """Test character counter functionality"""
        # Test with empty description
        self.business_tab.description_input.setPlainText("")
        self.business_tab._update_char_counter()
        assert "0 characters" in self.business_tab.char_counter_label.text()

        # Test with short description
        short_text = "Short description"
        self.business_tab.description_input.setPlainText(short_text)
        self.business_tab._update_char_counter()
        assert (
            f"{len(short_text)} characters"
            in self.business_tab.char_counter_label.text()
        )

        # Test with long description (should change color)
        long_text = "x" * 450  # Between 400-500 characters
        self.business_tab.description_input.setPlainText(long_text)
        self.business_tab._update_char_counter()
        assert (
            f"{len(long_text)} characters"
            in self.business_tab.char_counter_label.text()
        )

    def test_config_changed_signal(self):
        """Test that config_changed signal is emitted properly"""
        signal_emitted = False

        def on_config_changed():
            nonlocal signal_emitted
            signal_emitted = True

        # Connect to signal
        self.business_tab.config_changed.connect(on_config_changed)

        # Change business name (should emit signal)
        self.business_tab.business_name_input.setText("New Business Name")

        # Process events to handle signal
        QTest.qWait(100)  # Wait 100ms

        assert (
            signal_emitted
        ), "config_changed signal should be emitted when data changes"

    def test_tab_name(self):
        """Test that tab name is correct"""
        tab_name = self.business_tab.get_tab_name()
        assert tab_name == "Business"


def run_business_tab_tests():
    """Run all BusinessTab tests and return results"""
    print("=" * 60)
    print("RUNNING BUSINESS TAB COMPONENT TESTS")
    print("=" * 60)

    try:
        # Create test instance
        test_instance = TestBusinessTab()
        test_instance.setup_class()

        # List of test methods
        test_methods = [
            "test_initialization",
            "test_get_config_data_empty",
            "test_set_config_data_basic",
            "test_set_config_data_custom_industry",
            "test_get_required_fields",
            "test_validation_empty_fields",
            "test_validation_valid_data",
            "test_validation_invalid_url",
            "test_validation_short_fields",
            "test_validation_long_description",
            "test_url_formatting",
            "test_clear_data",
            "test_character_counter",
            "test_config_changed_signal",
            "test_tab_name",
        ]

        passed_tests = 0
        failed_tests = 0

        for test_method_name in test_methods:
            try:
                test_instance.setup_method()
                test_method = getattr(test_instance, test_method_name)
                test_method()
                test_instance.teardown_method()
                print(f"✅ {test_method_name}")
                passed_tests += 1
            except Exception as e:
                print(f"❌ {test_method_name}: {str(e)}")
                failed_tests += 1
                test_instance.teardown_method()

        print("\n" + "=" * 60)
        print(f"BUSINESS TAB TEST RESULTS")
        print("=" * 60)
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"📊 Total:  {passed_tests + failed_tests}")

        if failed_tests == 0:
            print("🎉 ALL BUSINESS TAB TESTS PASSED!")
            return True
        else:
            print(f"⚠️  {failed_tests} test(s) failed")
            return False

    except Exception as e:
        print(f"💥 Test setup failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = run_business_tab_tests()
    sys.exit(0 if success else 1)
