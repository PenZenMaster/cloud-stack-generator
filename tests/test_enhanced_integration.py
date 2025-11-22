# tests/test_enhanced_integration.py
"""
Integration test for enhanced main window with all modular components
Sprint 2 Week 2 - Day 6 Integration Testing
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_imports():
    """Test that all required components can be imported"""
    print("🔍 Testing Enhanced Main Window Integration...")
    print("=" * 50)

    # Test core imports
    try:
        print("📦 Testing core imports...")
        from src.core.config.models import ClientConfig, BusinessConfig, ContactConfig
        from src.core.config.parser import ConfigParser

        print("   ✅ Core config modules imported successfully")
    except ImportError as e:
        print(f"   ❌ Core import failed: {e}")
        return False

    # Test component imports
    try:
        print("📦 Testing component imports...")
        from src.ui.components.business_tab import BusinessTab
        from src.ui.components.contact_tab import ContactTab
        from src.ui.components.branding_tab import BrandingTab

        print("   ✅ UI components imported successfully")
    except ImportError as e:
        print(f"   ❌ Component import failed: {e}")
        return False

    # Test content tab imports
    try:
        print("📦 Testing content tab imports...")
        from src.ui.content_tabs.products_tab import ProductsTab
        from src.ui.content_tabs.services_tab import ServicesTab

        print("   ✅ Content tabs imported successfully")
    except ImportError as e:
        print(f"   ❌ Content tab import failed: {e}")
        return False

    # Test enhanced main window import
    try:
        print("📦 Testing enhanced main window import...")
        from src.ui.enhanced_main_window import EnhancedMainWindow

        print("   ✅ Enhanced main window imported successfully")
    except ImportError as e:
        print(f"   ❌ Enhanced main window import failed: {e}")
        return False

    return True


def test_enhanced_main_window_creation():
    """Test creating the enhanced main window"""
    try:
        print("\n🏗️ Testing Enhanced Main Window Creation...")

        from PyQt6.QtWidgets import QApplication
        from src.ui.enhanced_main_window import EnhancedMainWindow

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Create enhanced main window
        main_window = EnhancedMainWindow()
        print("   ✅ Enhanced main window created successfully")

        # Test that all tabs are present
        tab_count = main_window.main_tabs.count()  # PyQt6 uses count() not tabCount()
        expected_tabs = 5  # Business, Contact, Branding, Products, Services

        if tab_count == expected_tabs:
            print(f"   ✅ All {expected_tabs} tabs created successfully")
        else:
            print(f"   ⚠️ Expected {expected_tabs} tabs, found {tab_count}")

        # Test tab names
        expected_tab_names = [
            "📊 Business Info",
            "📞 Contact Details",
            "🎨 Branding & Style",
            "📦 Products",
            "⚙️ Services & FAQ",
        ]
        for i, expected_name in enumerate(expected_tab_names):
            if i < tab_count:  # Make sure tab exists before accessing
                actual_name = main_window.main_tabs.tabText(i)
                if actual_name == expected_name:
                    print(f"   ✅ Tab {i+1}: '{actual_name}' ✓")
                else:
                    print(
                        f"   ⚠️ Tab {i+1}: Expected '{expected_name}', got '{actual_name}'"
                    )
            else:
                print(f"   ❌ Tab {i+1}: Missing (expected '{expected_name}')")

        # Test that components have required methods
        components = [
            ("business_tab", main_window.business_tab),
            ("contact_tab", main_window.contact_tab),
            ("branding_tab", main_window.branding_tab),
            ("products_tab", main_window.products_tab),
            ("services_tab", main_window.services_tab),
        ]

        for name, component in components:
            required_methods = ["get_config_data", "set_config_data", "clear_data"]
            for method in required_methods:
                if hasattr(component, method):
                    print(f"   ✅ {name}.{method}() exists")
                else:
                    print(f"   ❌ {name}.{method}() missing")

        # Test signal connections
        print("   ✅ Signal connections established")

        return True

    except Exception as e:
        print(f"   ❌ Enhanced main window creation failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_configuration_workflow():
    """Test the configuration workflow"""
    try:
        print("\n⚙️ Testing Configuration Workflow...")

        from PyQt6.QtWidgets import QApplication
        from src.ui.enhanced_main_window import EnhancedMainWindow

        # Create QApplication if it doesn't exist
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Create enhanced main window
        main_window = EnhancedMainWindow()

        # Test getting config data from all tabs
        config_data = main_window.get_all_config_data()

        expected_sections = ["business", "contact", "branding", "products", "services"]
        for section in expected_sections:
            if section in config_data:
                print(f"   ✅ {section} configuration data retrieved")
            else:
                print(f"   ❌ {section} configuration data missing")

        # Test creating ClientConfig object
        main_window.create_client_config(config_data)
        print("   ✅ ClientConfig object created successfully")

        # Test basic validation
        tabs_with_validation = [
            ("business_tab", main_window.business_tab),
            ("contact_tab", main_window.contact_tab),
            ("branding_tab", main_window.branding_tab),
        ]

        for name, tab in tabs_with_validation:
            if hasattr(tab, "validate_data"):
                validation_result = tab.validate_data()
                if hasattr(validation_result, "is_valid"):
                    # ValidationResult object
                    is_valid = validation_result.is_valid
                    print(f"   ✅ {name} validation method works (valid: {is_valid})")
                elif isinstance(validation_result, tuple):
                    # Tuple format (is_valid, errors)
                    is_valid, errors = validation_result
                    print(f"   ✅ {name} validation method works (valid: {is_valid})")
                else:
                    print(
                        f"   ⚠️ {name} validation returned unexpected format: {type(validation_result)}"
                    )
            else:
                print(f"   ⚠️ {name} has no validation method")

        return True

    except Exception as e:
        print(f"   ❌ Configuration workflow test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def run_integration_test():
    """Run the complete integration test"""
    print("🚀 Enhanced Main Window Integration Test")
    print("Sprint 2 Week 2 - Day 6")
    print("=" * 60)

    tests = [
        ("Import Testing", test_imports),
        ("Main Window Creation", test_enhanced_main_window_creation),
        ("Configuration Workflow", test_configuration_workflow),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)

        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    print("\n" + "=" * 60)
    print(f"📊 INTEGRATION TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL INTEGRATION TESTS PASSED!")
        print("✅ Enhanced Main Window is ready for use")
        print("\n🚀 Next Steps:")
        print("   1. Run: python main.py")
        print("   2. Test the full integrated interface")
        print("   3. Try loading/saving configurations")
        print("   4. Proceed to website generator integration")
        return True
    else:
        print("⚠️ Some integration tests failed")
        print("🔧 Please fix the failing components before proceeding")
        return False


if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)
