"""
Filename: simple_branding_test.py
Path: E:\\projects\\cloud-stack-generator\\tests\\simple_branding_test.py
Description: Basic import and instantiation verification for BrandingTab component
Quick validation that BrandingTab can be imported and core functionality works

Version: 1.0.0
Date: 2025-08-11
Author: Cloud Stack Generator Team
"""

import sys
import os

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


def test_basic_imports():
    """Test basic imports and instantiation"""
    print("🧪 BrandingTab Basic Import Test")
    print("=" * 40)

    try:
        # Test PyQt6 imports
        print("📦 Testing PyQt6 imports...")
        from PyQt6.QtWidgets import QApplication, QWidget, QComboBox, QLineEdit
        from PyQt6.QtCore import pyqtSignal
        from PyQt6.QtGui import QColor

        print("  ✅ PyQt6 imports successful")

        # Test BrandingTab import
        print("📦 Testing BrandingTab import...")
        from src.ui.components.branding_tab import BrandingTab, ValidationResult

        print("  ✅ BrandingTab import successful")

        # Test application creation
        print("🖥️ Testing QApplication creation...")
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        print("  ✅ QApplication created")

        # Test BrandingTab instantiation
        print("🔧 Testing BrandingTab instantiation...")
        branding_tab = BrandingTab()
        print("  ✅ BrandingTab created successfully")

        # Test basic properties
        print("🔍 Testing basic properties...")

        # Check required inputs exist
        required_inputs = [
            "primary_color",
            "secondary_color",
            "font_family",
            "logo_url",
        ]
        for field_name in required_inputs:
            if field_name not in branding_tab.branding_inputs:
                raise Exception(f"Missing input field: {field_name}")
        print(f"  ✅ All {len(required_inputs)} input fields exist")

        # Check color buttons exist
        color_buttons = ["primary", "secondary"]
        for color_key in color_buttons:
            if color_key not in branding_tab.color_buttons:
                raise Exception(f"Missing color button: {color_key}")
        print(f"  ✅ All {len(color_buttons)} color buttons exist")

        # Check preview labels exist
        preview_keys = ["primary", "secondary", "font", "scheme"]
        for preview_key in preview_keys:
            if preview_key not in branding_tab.preview_labels:
                raise Exception(f"Missing preview label: {preview_key}")
        print(f"  ✅ All {len(preview_keys)} preview labels exist")

        # Test ValidationResult class
        print("🔍 Testing ValidationResult...")
        result = ValidationResult()
        if not result.is_valid:
            raise Exception("ValidationResult should be valid by default")
        result.add_error("Test error")
        if result.is_valid:
            raise Exception("ValidationResult should be invalid after adding error")
        print("  ✅ ValidationResult working correctly")

        # Test required fields method
        print("🔍 Testing get_required_fields...")
        required_fields = branding_tab.get_required_fields()
        expected_required = ["primary_color", "secondary_color", "font_family"]
        if set(required_fields) != set(expected_required):
            raise Exception(
                f"get_required_fields returned {required_fields}, expected {expected_required}"
            )
        print("  ✅ get_required_fields working correctly")

        # Test default values
        print("🔍 Testing default values...")
        if (
            branding_tab.branding_inputs["primary_color"].text()
            != BrandingTab.DEFAULT_PRIMARY
        ):
            raise Exception("Primary color default not set correctly")
        if (
            branding_tab.branding_inputs["secondary_color"].text()
            != BrandingTab.DEFAULT_SECONDARY
        ):
            raise Exception("Secondary color default not set correctly")
        if (
            branding_tab.branding_inputs["font_family"].currentText()
            != "Arial, sans-serif"
        ):
            raise Exception("Font family default not set correctly")
        print("  ✅ Default values set correctly")

        # Test config data methods
        print("🔍 Testing config data methods...")

        # Test get_config_data (should work with default data)
        config_data = branding_tab.get_config_data()
        if "branding" not in config_data:
            raise Exception("get_config_data should return dict with 'branding' key")
        print("  ✅ get_config_data working")

        # Test set_config_data
        test_data = {
            "branding": {
                "primary_color": "#ff0000",
                "secondary_color": "#00ff00",
                "font_family": "Georgia, serif",
                "logo_url": "https://test.com/logo.png",
            }
        }
        branding_tab.set_config_data(test_data)

        # Verify data was set
        if branding_tab.branding_inputs["primary_color"].text() != "#ff0000":
            raise Exception("set_config_data did not set primary color correctly")
        if (
            branding_tab.branding_inputs["font_family"].currentText()
            != "Georgia, serif"
        ):
            raise Exception("set_config_data did not set font correctly")
        print("  ✅ set_config_data working")

        # Test hex color validation
        print("🔍 Testing hex color validation...")
        if not branding_tab._is_valid_hex_color("#ff0000"):
            raise Exception("Valid hex color not recognized")
        if branding_tab._is_valid_hex_color("invalid"):
            raise Exception("Invalid hex color was accepted")
        print("  ✅ Hex color validation working")

        # Test dark color detection
        print("🔍 Testing dark color detection...")
        if not branding_tab._is_dark_color("#000000"):
            raise Exception("Black should be detected as dark")
        if branding_tab._is_dark_color("#ffffff"):
            raise Exception("White should not be detected as dark")
        print("  ✅ Dark color detection working")

        # Test validation
        print("🔍 Testing validation...")
        validation_result = branding_tab.validate_data()
        if not hasattr(validation_result, "is_valid"):
            raise Exception("validate_data should return ValidationResult object")
        print("  ✅ validate_data working")

        # Test clear_data
        print("🔍 Testing clear_data...")
        branding_tab.clear_data()
        if (
            branding_tab.branding_inputs["primary_color"].text()
            != BrandingTab.DEFAULT_PRIMARY
        ):
            raise Exception("clear_data did not reset primary color")
        print("  ✅ clear_data working")

        # Test web fonts
        print("🔍 Testing web fonts...")
        if len(BrandingTab.WEB_FONTS) < 5:
            raise Exception("Not enough web fonts defined")
        if "Arial, sans-serif" not in BrandingTab.WEB_FONTS:
            raise Exception("Arial should be in web fonts")
        print(f"  ✅ {len(BrandingTab.WEB_FONTS)} web fonts available")

        # Clean up
        branding_tab.close()
        branding_tab.deleteLater()

        print("=" * 40)
        print("🎉 ALL BASIC TESTS PASSED!")
        print("✅ BrandingTab is ready for comprehensive testing")
        return True

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure BrandingTab is in src/ui/components/branding_tab.py")
        return False

    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False


def verify_file_structure():
    """Verify required files exist"""
    print("📁 Verifying file structure...")

    required_files = [
        "src/ui/components/branding_tab.py",
        "src/ui/components/base_tab.py",  # BrandingTab depends on BaseTab
    ]

    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path} exists")
        else:
            print(f"  ❌ {file_path} missing")
            return False

    return True


def main():
    """Run basic BrandingTab tests"""
    print("🚀 BrandingTab Basic Verification")
    print("Testing import, instantiation, and basic functionality")
    print()

    # Check file structure first
    if not verify_file_structure():
        print("❌ File structure verification failed")
        return False

    # Run basic tests
    success = test_basic_imports()

    if success:
        print("\n✅ BrandingTab is working correctly!")
        print("📋 Ready for:")
        print("   • Comprehensive unit tests")
        print("   • Manual testing interface")
        print("   • Integration with main application")
    else:
        print("\n❌ BrandingTab has issues that need to be resolved")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
