# tests/simple_config_test.py
"""
Simple Configuration Test - No Generators Required
Tests that ClientConfig can be created from UI data
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_config_creation():
    """Test creating ClientConfig from UI data"""
    print("🧪 Testing Configuration Creation")
    print("=" * 50)

    try:
        # Import core models
        print("📦 Importing core models...")
        from src.core.config.models import (
            ClientConfig,
            BusinessConfig,
            ContactConfig,
            BrandingConfig,
        )

        print("   ✅ Core models imported")

        # Test business config
        print("\n🏢 Testing BusinessConfig...")
        business = BusinessConfig(
            business_name="Test Company",
            domain="https://test.com",
            industry="Testing Services",
        )
        print(f"   ✅ Business: {business.business_name}")

        # Test contact config
        print("\n📞 Testing ContactConfig...")
        contact = ContactConfig(
            name="Test Company",
            phone="555-1234",
            email="test@test.com",
            address="123 Test Street",
        )
        print(f"   ✅ Contact: {contact.email}")

        # Test branding config
        print("\n🎨 Testing BrandingConfig...")
        branding = BrandingConfig(
            primary_color="#007bff",
            secondary_color="#6c757d",
            font_family="Arial, sans-serif",
            logo_url="",
        )
        print(f"   ✅ Branding: {branding.primary_color}")

        # Test complete client config
        print("\n📋 Testing ClientConfig...")
        client_config = ClientConfig(
            business=business,
            contact=contact,
            branding=branding,
            services=[],
            products=[],
        )
        print(f"   ✅ ClientConfig created successfully")
        print(f"   📊 Business: {client_config.business.business_name}")
        print(f"   📞 Contact: {client_config.contact.email}")
        print(f"   🎨 Primary Color: {client_config.branding.primary_color}")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_ui_data_conversion():
    """Test converting UI data to ClientConfig"""
    print("\n🖥️ Testing UI Data Conversion...")

    try:
        from src.ui.enhanced_main_window import EnhancedMainWindow
        from PyQt6.QtWidgets import QApplication

        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Create main window
        main_window = EnhancedMainWindow()
        print("   ✅ Enhanced main window created")

        # Test UI data conversion
        ui_data = {
            "business": {
                "business_name": "UI Test Company",
                "domain": "https://uitest.com",
                "industry": "UI Testing",
            },
            "contact": {
                "name": "UI Test Company",
                "phone": "555-UI-TEST",
                "email": "ui@test.com",
                "address": "123 UI Test Lane",
            },
            "branding": {
                "primary_color": "#ff5722",
                "secondary_color": "#ffc107",
                "font_family": "Roboto, sans-serif",
                "logo_url": "https://test.com/logo.png",
            },
            "products": {"products": []},
            "services": {"services": []},
        }

        # Convert to ClientConfig
        client_config = main_window.create_client_config(ui_data)
        print("   ✅ UI data converted to ClientConfig")
        print(f"   📊 Business: {client_config.business.business_name}")
        print(f"   📞 Contact: {client_config.contact.email}")
        print(f"   🎨 Primary Color: {client_config.branding.primary_color}")

        return True

    except Exception as e:
        print(f"❌ UI conversion test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run configuration tests"""
    print("🧪 Configuration Test Suite")
    print("Testing data models and UI integration")
    print("=" * 60)

    tests = [
        ("Configuration Creation", test_config_creation),
        ("UI Data Conversion", test_ui_data_conversion),
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
    print(f"📊 CONFIGURATION TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL CONFIGURATION TESTS PASSED!")
        print("✅ Configuration system is working correctly")
        print("\n🚀 Next Steps:")
        print("   1. Create the generator files")
        print("   2. Test website generation")
        print("   3. Generate your first website!")
        return True
    else:
        print("⚠️ Some configuration tests failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
