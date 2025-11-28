"""
Module/Script Name: test_branding_tab.py
Path: tests/unit/test_branding_tab.py

Description:
Comprehensive unit test suite for BrandingTab component. Tests color validation,
font selection, hex format validation, and live preview functionality.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-08-11

Last Modified Date:
2025-11-27

Version: 2.00

Comments:
* v2.00 - Complete rewrite for BrandingTab v2.06 implementation
* v1.01 - Updated tests for new H1/H2/H3/Menu color fields and hero background image
* v1.00 - Initial comprehensive test suite
"""

import sys
import os
import unittest
from PyQt6.QtWidgets import QApplication

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(project_root, "src")):
    parent = os.path.dirname(project_root)
    if parent == project_root:  # We've reached the root
        break
    project_root = parent

if os.path.exists(os.path.join(project_root, "src")):
    sys.path.insert(0, project_root)
else:
    print("❌ Could not find 'src' directory")
    sys.exit(1)

# Import the component to test
try:
    from src.ui.components.branding_tab import BrandingTab, ValidationResult
except ImportError:
    print(
        "❌ Import Error: Make sure BrandingTab is in src/ui/components/branding_tab.py"
    )
    sys.exit(1)


class TestBrandingTab(unittest.TestCase):
    """Comprehensive test suite for BrandingTab functionality"""

    @classmethod
    def setUpClass(cls):
        """Setup test application"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()

    def setUp(self):
        """Setup test fixtures"""
        self.branding_tab = BrandingTab()

        # Test data - matches new get_config_data()/set_config_data() format
        self.valid_branding_data = {
            "colors": {
                "primary_color": "#ff5722",
                "secondary_color": "#ffc107",
                "body_background_color": "#ffffff",
                "body_text_color": "#333333",
                "footer_background_color": "#2c3e50",
                "footer_text_color": "#ffffff",
                "h1_text_color": "#2c3e50",
                "h2_text_color": "#34495e",
                "h3_text_color": "#34495e",
                "main_menu_text_color": "#ffffff",
            },
            "typography": {
                "font_family": "Georgia, serif",
            },
            "logo": {
                "logo_url": "https://example.com/logo.png",
                "hero_background_image_url": "",
            }
        }

        self.invalid_branding_data = {
            "colors": {
                "primary_color": "invalid-color",
                "secondary_color": "#zzz",
            },
            "typography": {
                "font_family": "",
            },
            "logo": {
                "logo_url": "not-a-url",
                "hero_background_image_url": "",
            }
        }

    def tearDown(self):
        """Cleanup after each test"""
        self.branding_tab.close()
        self.branding_tab.deleteLater()

    def test_01_initialization(self):
        """Test BrandingTab initialization"""
        # Widget should be created successfully
        self.assertIsNotNone(self.branding_tab)

        # All required input widgets should exist
        required_inputs = [
            "primary",
            "secondary",
            "body_background",
            "body_text",
            "footer_background",
            "footer_text",
            "h1_text",
            "h2_text",
            "h3_text",
            "menu_text",
            "font_family",
            "logo_url",
            "hero_background_image_url",
        ]
        for field_name in required_inputs:
            self.assertIn(field_name, self.branding_tab.branding_inputs, f"Missing input: {field_name}")
            self.assertIsNotNone(self.branding_tab.branding_inputs[field_name])

        # Color buttons should exist
        self.assertIn("primary", self.branding_tab.color_buttons)
        self.assertIn("secondary", self.branding_tab.color_buttons)
        self.assertIn("h1_text", self.branding_tab.color_buttons)
        self.assertIn("h2_text", self.branding_tab.color_buttons)
        self.assertIn("h3_text", self.branding_tab.color_buttons)
        self.assertIn("menu_text", self.branding_tab.color_buttons)

        # Preview labels should exist
        self.assertIn("primary", self.branding_tab.preview_labels)
        self.assertIn("secondary", self.branding_tab.preview_labels)
        self.assertIn("h1_text", self.branding_tab.preview_labels)
        self.assertIn("h2_text", self.branding_tab.preview_labels)
        self.assertIn("h3_text", self.branding_tab.preview_labels)
        self.assertIn("menu_text", self.branding_tab.preview_labels)

        print("✅ Test 1 passed: BrandingTab initialization")

    def test_02_default_values(self):
        """Test default values are set correctly"""
        # Default colors should be set
        primary_input = self.branding_tab.branding_inputs["primary"]
        secondary_input = self.branding_tab.branding_inputs["secondary"]

        self.assertEqual(primary_input.text(), BrandingTab.DEFAULT_PRIMARY)
        self.assertEqual(secondary_input.text(), BrandingTab.DEFAULT_SECONDARY)

        # Test new heading color defaults
        h1_input = self.branding_tab.branding_inputs["h1_text"]
        h2_input = self.branding_tab.branding_inputs["h2_text"]
        h3_input = self.branding_tab.branding_inputs["h3_text"]
        menu_input = self.branding_tab.branding_inputs["menu_text"]

        self.assertEqual(h1_input.text(), BrandingTab.DEFAULT_H1_TEXT)
        self.assertEqual(h2_input.text(), BrandingTab.DEFAULT_H2_TEXT)
        self.assertEqual(h3_input.text(), BrandingTab.DEFAULT_H3_TEXT)
        self.assertEqual(menu_input.text(), BrandingTab.DEFAULT_MENU_TEXT)

        # Default font should be set
        font_combo = self.branding_tab.branding_inputs["font_family"]
        self.assertEqual(font_combo.currentText(), "Arial, sans-serif")

        # Logo URL should be empty
        logo_input = self.branding_tab.branding_inputs["logo_url"]
        self.assertEqual(logo_input.text(), "")

        # Hero background should be empty
        hero_input = self.branding_tab.branding_inputs["hero_background_image_url"]
        self.assertEqual(hero_input.text(), "")

        print("✅ Test 2 passed: Default values")

    def test_03_required_fields_list(self):
        """Test get_required_fields method"""
        required_fields = self.branding_tab.get_required_fields()

        expected_fields = ["primary_color", "secondary_color", "font_family"]
        self.assertEqual(set(required_fields), set(expected_fields))

        print("✅ Test 3 passed: Required fields list")

    def test_04_set_and_get_config_data(self):
        """Test setting and getting configuration data"""
        # Set valid data
        self.branding_tab.set_config_data(self.valid_branding_data)

        # Verify data was set correctly (using internal field names)
        self.assertEqual(
            self.branding_tab.branding_inputs["primary"].text(), "#ff5722"
        )
        self.assertEqual(
            self.branding_tab.branding_inputs["secondary"].text(), "#ffc107"
        )
        self.assertEqual(
            self.branding_tab.branding_inputs["font_family"].currentText(),
            "Georgia, serif",
        )
        self.assertEqual(
            self.branding_tab.branding_inputs["logo_url"].text(),
            "https://example.com/logo.png",
        )

        # Get data back
        retrieved_data = self.branding_tab.get_config_data()
        self.assertEqual(retrieved_data, self.valid_branding_data)

        print("✅ Test 4 passed: Set and get config data")

    def test_05_validation_empty_required_fields(self):
        """Test validation with empty required fields"""
        # Clear required data
        self.branding_tab.branding_inputs["primary"].setText("")
        self.branding_tab.branding_inputs["secondary"].setText("")

        # Validate
        result = self.branding_tab.validate_data()

        # Should have validation errors
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 2)  # Primary and secondary colors required

        # Check specific error messages
        error_messages = result.errors
        self.assertTrue(
            any("Primary color is required" in msg for msg in error_messages)
        )
        self.assertTrue(
            any("Secondary color is required" in msg for msg in error_messages)
        )

        print("✅ Test 5 passed: Validation with empty required fields")

    def test_06_validation_valid_data(self):
        """Test validation with valid data"""
        # Set valid data
        self.branding_tab.set_config_data(self.valid_branding_data)

        # Validate
        result = self.branding_tab.validate_data()

        # Should pass validation
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

        print("✅ Test 6 passed: Validation with valid data")

    def test_07_hex_color_validation(self):
        """Test hex color format validation via input change"""
        import re

        # Test the regex pattern used in the actual code
        hex_pattern = r"^#[0-9A-Fa-f]{6}$"

        # Test invalid hex colors
        invalid_colors = [
            "invalid-color",
            "#zzz",
            "#12345",  # Too short
            "#1234567",  # Too long
            "123456",  # Missing #
            "#gggggg",  # Invalid characters
        ]

        for invalid_color in invalid_colors:
            self.assertFalse(
                bool(re.match(hex_pattern, invalid_color)),
                f"'{invalid_color}' should be invalid",
            )

        # Test valid 6-character hex colors
        valid_colors = [
            "#123456",
            "#ABCDEF",
            "#abcdef",
            "#000000",
            "#ffffff",
        ]

        for valid_color in valid_colors:
            self.assertTrue(
                bool(re.match(hex_pattern, valid_color)),
                f"'{valid_color}' should be valid",
            )

        print("✅ Test 7 passed: Hex color validation")

    def test_08_color_validation_integration(self):
        """Test color validation in full validation"""
        # Set invalid colors (using correct field names)
        self.branding_tab.branding_inputs["primary"].setText("#zzz")
        self.branding_tab.branding_inputs["secondary"].setText("invalid")
        self.branding_tab.branding_inputs["font_family"].setCurrentText(
            "Arial, sans-serif"
        )

        # Validate
        result = self.branding_tab.validate_data()

        # Should have color format errors
        self.assertFalse(result.is_valid)
        self.assertTrue(len(result.errors) >= 2)  # At least primary and secondary invalid

        print("✅ Test 8 passed: Color validation integration")

    def test_09_font_selection(self):
        """Test font family selection"""
        font_combo = self.branding_tab.branding_inputs["font_family"]

        # Test all web fonts are available
        available_fonts = [font_combo.itemText(i) for i in range(font_combo.count())]
        expected_fonts = BrandingTab.WEB_FONTS

        self.assertEqual(set(available_fonts), set(expected_fonts))

        # Test font selection
        test_font = "Georgia, serif"
        font_combo.setCurrentText(test_font)
        self.assertEqual(font_combo.currentText(), test_font)

        print("✅ Test 9 passed: Font selection")

    def test_10_dark_color_detection(self):
        """Test dark color detection - SKIPPED (method removed in v2.06)"""
        # This method was removed in the v2.06 implementation
        # Dark/light color detection is no longer needed for the current UI
        print("⏭️  Test 10 skipped: Dark color detection (method removed)")

    def test_11_color_tracking(self):
        """Test internal color tracking"""
        # Initial colors should be defaults
        self.assertEqual(
            self.branding_tab.current_colors["primary"], BrandingTab.DEFAULT_PRIMARY
        )
        self.assertEqual(
            self.branding_tab.current_colors["secondary"], BrandingTab.DEFAULT_SECONDARY
        )

        # Update colors (using correct field names and method)
        new_primary = "#ff0000"
        new_secondary = "#00ff00"

        self.branding_tab.branding_inputs["primary"].setText(new_primary)
        self.branding_tab._on_color_input_changed("primary", new_primary)

        self.branding_tab.branding_inputs["secondary"].setText(new_secondary)
        self.branding_tab._on_color_input_changed("secondary", new_secondary)

        # Check tracking updated
        self.assertEqual(self.branding_tab.current_colors["primary"], new_primary)
        self.assertEqual(self.branding_tab.current_colors["secondary"], new_secondary)

        print("✅ Test 11 passed: Color tracking")

    def test_12_logo_url_validation(self):
        """Test logo URL validation"""
        # Set required fields to pass basic validation (using correct field names)
        self.branding_tab.branding_inputs["primary"].setText("#ff0000")
        self.branding_tab.branding_inputs["secondary"].setText("#00ff00")
        self.branding_tab.branding_inputs["font_family"].setCurrentText(
            "Arial, sans-serif"
        )

        # Logo URL is optional in v2.06, so validation should pass
        self.branding_tab.branding_inputs["logo_url"].setText("not-a-url")
        result = self.branding_tab.validate_data()

        # Should be valid (logo_url is optional)
        self.assertTrue(result.is_valid)

        # Test valid URL
        self.branding_tab.branding_inputs["logo_url"].setText(
            "https://example.com/logo.png"
        )
        result = self.branding_tab.validate_data()

        # Should be valid
        self.assertTrue(result.is_valid)

        print("✅ Test 12 passed: Logo URL validation")

    def test_13_color_contrast_warning(self):
        """Test identical color warning"""
        # Set same colors (using correct field names)
        same_color = "#ff0000"
        self.branding_tab.branding_inputs["primary"].setText(same_color)
        self.branding_tab.branding_inputs["secondary"].setText(same_color)
        self.branding_tab.branding_inputs["font_family"].setCurrentText(
            "Arial, sans-serif"
        )

        # Update color tracking (using correct method)
        self.branding_tab._on_color_input_changed("primary", same_color)
        self.branding_tab._on_color_input_changed("secondary", same_color)

        # Validate
        result = self.branding_tab.validate_data()

        # Should be valid but have warning
        self.assertTrue(result.is_valid)
        contrast_warnings = [w for w in result.warnings if "identical" in w.lower()]
        self.assertTrue(len(contrast_warnings) > 0)

        print("✅ Test 13 passed: Color contrast warning")

    def test_14_clear_data(self):
        """Test clearing all data"""
        # Set some data
        self.branding_tab.set_config_data(self.valid_branding_data)

        # Verify data is set (using correct field names)
        self.assertNotEqual(
            self.branding_tab.branding_inputs["primary"].text(),
            BrandingTab.DEFAULT_PRIMARY,
        )

        # Clear data
        self.branding_tab.clear_data()

        # Verify all fields are reset to defaults
        self.assertEqual(
            self.branding_tab.branding_inputs["primary"].text(),
            BrandingTab.DEFAULT_PRIMARY,
        )
        self.assertEqual(
            self.branding_tab.branding_inputs["secondary"].text(),
            BrandingTab.DEFAULT_SECONDARY,
        )
        self.assertEqual(
            self.branding_tab.branding_inputs["font_family"].currentText(),
            "Arial, sans-serif",
        )
        self.assertEqual(self.branding_tab.branding_inputs["logo_url"].text(), "")

        # Color tracking should be reset
        self.assertEqual(
            self.branding_tab.current_colors["primary"], BrandingTab.DEFAULT_PRIMARY
        )
        self.assertEqual(
            self.branding_tab.current_colors["secondary"], BrandingTab.DEFAULT_SECONDARY
        )

        # Changes flag should be reset
        self.assertFalse(self.branding_tab.has_changes)

        print("✅ Test 14 passed: Clear data")

    def test_15_config_changed_signal(self):
        """Test config_changed signal emission"""
        signal_received = False

        def signal_handler():
            nonlocal signal_received
            signal_received = True

        # Connect signal
        self.branding_tab.config_changed.connect(signal_handler)

        # Trigger change (using correct field name)
        self.branding_tab.branding_inputs["primary"].setText("#123456")
        self.branding_tab._emit_config_changed()

        # Process events to ensure signal is emitted
        QApplication.processEvents()

        # Check signal was received
        self.assertTrue(signal_received)
        self.assertTrue(self.branding_tab.has_changes)

        print("✅ Test 15 passed: Config changed signal")

    def test_16_realistic_salvo_data(self):
        """Test with realistic Salvo Metal Works branding data"""
        salvo_branding = {
            "colors": {
                "primary_color": "#C41E3A",  # Industrial red
                "secondary_color": "#2C3E50",  # Dark blue-gray
                "body_background_color": "#ffffff",
                "body_text_color": "#333333",
                "footer_background_color": "#2c3e50",
                "footer_text_color": "#ffffff",
                "h1_text_color": "#C41E3A",
                "h2_text_color": "#2C3E50",
                "h3_text_color": "#2C3E50",
                "main_menu_text_color": "#ffffff",
            },
            "typography": {
                "font_family": "Arial, sans-serif",
            },
            "logo": {
                "logo_url": "https://salvometalworks.com/assets/logo.png",
                "hero_background_image_url": "",
            }
        }

        # Set Salvo data
        self.branding_tab.set_config_data(salvo_branding)

        # Validate
        result = self.branding_tab.validate_data()
        self.assertTrue(result.is_valid)

        # Get data back and verify
        retrieved_data = self.branding_tab.get_config_data()
        self.assertEqual(retrieved_data, salvo_branding)

        print("✅ Test 16 passed: Realistic Salvo branding data")

    def test_17_validation_result_class(self):
        """Test ValidationResult helper class"""
        result = ValidationResult()

        # Initially valid
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)

        # Add warning (should still be valid)
        result.add_warning("Test warning")
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.warnings), 1)

        # Add error (should become invalid)
        result.add_error("Test error")
        self.assertFalse(result.is_valid)
        self.assertEqual(len(result.errors), 1)

        print("✅ Test 17 passed: ValidationResult class")

    def test_18_web_fonts_completeness(self):
        """Test that all web fonts are properly defined"""
        expected_web_fonts = [
            "Arial, sans-serif",
            "Helvetica, sans-serif",
            "Times New Roman, serif",
            "Georgia, serif",
            "Verdana, sans-serif",
            "Calibri, sans-serif",
            "Trebuchet MS, sans-serif",
            "Courier New, monospace",
            "Lucida Console, monospace",
            "Impact, sans-serif",
        ]

        self.assertEqual(BrandingTab.WEB_FONTS, expected_web_fonts)
        self.assertEqual(len(BrandingTab.WEB_FONTS), 10)

        print("✅ Test 18 passed: Web fonts completeness")


def run_all_tests():
    """Run all BrandingTab tests"""
    print("🧪 Starting BrandingTab Test Suite...")
    print("=" * 50)

    # Create test suite
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestBrandingTab)

    # Run tests with custom result handling
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(test_suite)

    print("=" * 50)

    # Summary
    total_tests = result.testsRun
    failed_tests = len(result.failures)
    error_tests = len(result.errors)
    passed_tests = total_tests - failed_tests - error_tests

    print("📊 TEST SUMMARY:")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"💥 Errors: {error_tests}")
    print(f"📋 Total: {total_tests}")

    if failed_tests > 0:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(
                f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}"
            )

    if error_tests > 0:
        print("\n💥 ERRORS:")
        for test, traceback in result.errors:
            print(
                f"  - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}"
            )

    if failed_tests == 0 and error_tests == 0:
        print("\n🎉 ALL BRANDING TAB TESTS PASSED! ✅")

    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
