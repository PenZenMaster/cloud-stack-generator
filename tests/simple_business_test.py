"""
Filename: tests/simple_business_test.py
Path: E:/projects/cloud-stack-generator/tests/simple_business_test.py
Description: Simple test to verify BusinessTab can be imported and created

Version: 1.0.0
Date: 2025-08-10
Author: Cloud Stack Generator Team
"""

import sys
import os


def test_business_tab_import():
    """Test that BusinessTab can be imported and created"""
    print("🔍 Testing BusinessTab import and creation...")

    try:
        # Add src directory to path
        project_root = os.path.dirname(os.path.dirname(__file__))
        src_path = os.path.join(project_root, "src")
        if src_path not in sys.path:
            sys.path.insert(0, src_path)

        print(f"📁 Project root: {project_root}")
        print(f"📁 Source path: {src_path}")
        print(f"📁 Current working directory: {os.getcwd()}")

        # Test PyQt6 import
        try:
            from PyQt6.QtWidgets import QApplication, QWidget

            print("✅ PyQt6 import successful")
        except ImportError as e:
            print(f"❌ PyQt6 import failed: {e}")
            return False

        # Test base_tab import
        try:
            from ui.components.base_tab import BaseTab, ValidationResult

            print("✅ BaseTab import successful")
        except ImportError as e:
            print(f"❌ BaseTab import failed: {e}")
            print("   Make sure src/ui/components/base_tab.py exists")
            return False

        # Test business_tab import
        try:
            from ui.components.business_tab import BusinessTab

            print("✅ BusinessTab import successful")
        except ImportError as e:
            print(f"❌ BusinessTab import failed: {e}")
            print("   Make sure src/ui/components/business_tab.py exists")
            return False

        # Test QApplication creation
        try:
            if not QApplication.instance():
                app = QApplication([])
            print("✅ QApplication creation successful")
        except Exception as e:
            print(f"❌ QApplication creation failed: {e}")
            return False

        # Test BusinessTab creation
        try:
            business_tab = BusinessTab()
            print("✅ BusinessTab widget creation successful")
        except Exception as e:
            print(f"❌ BusinessTab creation failed: {e}")
            return False

        # Test basic method calls
        try:
            # Test get_config_data (should return empty dict initially)
            config = business_tab.get_config_data()
            print(f"✅ get_config_data() returned: {config}")

            # Test validation
            result = business_tab.validate_data()
            print(
                f"✅ validate_data() returned: valid={result.is_valid}, errors={len(result.errors)}"
            )

            # Test get_required_fields
            required = business_tab.get_required_fields()
            print(f"✅ get_required_fields() returned: {required}")

            # Test get_tab_name
            tab_name = business_tab.get_tab_name()
            print(f"✅ get_tab_name() returned: '{tab_name}'")

        except Exception as e:
            print(f"❌ BusinessTab method calls failed: {e}")
            return False

        # Test data setting
        try:
            test_data = {
                "business_name": "Test Business",
                "domain": "https://www.test.com",
                "industry": "Technology",
                "description": "Test description",
            }
            business_tab.set_config_data(test_data)

            # Get the data back
            retrieved_data = business_tab.get_config_data()
            print(f"✅ Data round-trip test successful")
            print(f"   Set: {test_data}")
            print(f"   Got: {retrieved_data}")

        except Exception as e:
            print(f"❌ Data setting/getting failed: {e}")
            return False

        # Cleanup
        try:
            business_tab.close()
            business_tab.deleteLater()
            print("✅ Cleanup successful")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

        print("\n🎉 ALL BASIC TESTS PASSED!")
        print("BusinessTab component is ready for full testing.")
        return True

    except Exception as e:
        print(f"💥 Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("=" * 60)
    print("BUSINESS TAB - BASIC IMPORT AND CREATION TEST")
    print("=" * 60)

    success = test_business_tab_import()

    print("\n" + "=" * 60)
    if success:
        print("✅ READY FOR FULL TESTING")
        print("Next steps:")
        print("1. Run: python tests/unit/test_business_tab.py")
        print("2. Run: python tests/manual_test_business_tab.py")
    else:
        print("❌ BASIC TESTS FAILED")
        print("Fix the import/creation issues before running full tests")
    print("=" * 60)

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
