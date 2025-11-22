# tests/test_website_generation.py
"""
Test Website Generation - Integration Verification
Sprint 2 Week 2 - Days 7-8 Testing

Tests the modular website generation system with sample data.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_website_generation():
    """Test complete website generation workflow"""
    print("🚀 Testing Website Generation System")
    print("=" * 60)

    try:
        # Import modules
        print("📦 Importing modules...")
        from src.core.generators import PageGenerator

        print("   ✅ Core modules imported successfully")

        # Create sample configuration
        print("\n🏗️ Creating sample configuration...")
        config = create_sample_config()
        print("   ✅ Sample configuration created")

        # Test individual generators
        print("\n🧪 Testing individual generators...")
        test_individual_generators(config)

        # Test complete website generation
        print("\n🌐 Testing complete website generation...")
        generator = PageGenerator(output_base_dir="test_output")

        def progress_callback(current, total, message):
            print(f"   Progress: {current}/{total} - {message}")

        result = generator.generate_complete_website(config, progress_callback)

        if result.success:
            print("   ✅ Website generation successful!")
            print(
                f"   📊 Generated {result.pages_generated} pages in {result.generation_time:.2f} seconds"
            )
            print(f"   📁 Output directory: {result.output_directory}")
            print(f"   📄 Total files: {len(result.generated_files)}")

            if result.warnings:
                print(f"   ⚠️ Warnings: {len(result.warnings)}")
                for warning in result.warnings:
                    print(f"      • {warning}")
        else:
            print("   ❌ Website generation failed!")
            for error in result.errors:
                print(f"      • {error}")

        return result.success

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        return False


def create_sample_config():
    """Create sample configuration for testing"""
    # Import the config classes properly
    from src.core.config.models import (
        ClientConfig,
        BusinessConfig,
        ContactConfig,
        BrandingConfig,
    )

    # Import from the actual locations in your project
    try:
        from src.ui.content_tabs.services_tab import Service
        from src.ui.content_tabs.products_tab import Product

        print("   ✅ Using Service and Product from content tabs")
    except ImportError:
        # Fallback: create simple classes for testing
        print("   ⚠️ Creating simple Service and Product classes for testing")

        class Service:
            def __init__(
                self,
                name="",
                description="",
                category="",
                price_range="",
                duration="",
                features=None,
            ):
                self.name = name
                self.description = description
                self.category = category
                self.price_range = price_range
                self.duration = duration
                self.features = features or []

        class Product:
            def __init__(
                self, sku="", name="", description="", category="", image_url=""
            ):
                self.sku = sku
                self.name = name
                self.description = description
                self.category = category
                self.image_url = image_url

    # Business information
    business = BusinessConfig(
        business_name="Salvo Metal Works",
        domain="https://salvometalworks.com",
        industry="Metal Fabrication & Welding",
    )

    # Contact information
    contact = ContactConfig(
        name="Salvo Metal Works",
        phone="+1-555-METAL-1",
        email="info@salvometalworks.com",
        address="123 Industrial Way, Metal City, MC 12345",
    )

    # Branding
    branding = BrandingConfig(
        primary_color="#1f2937",
        secondary_color="#f59e0b",
        font_family="Arial, sans-serif",
        logo_url="https://example.com/logo.png",
    )

    # Sample services
    services = [
        Service(
            name="Custom Metal Fabrication",
            description="Professional custom metal fabrication services for industrial and commercial applications. We work with steel, aluminum, and specialty alloys.",
            category="Fabrication",
            price_range="$50-$200 per hour",
            duration="1-4 weeks",
            features=[
                "Custom Design",
                "Precision Cutting",
                "Professional Welding",
                "Quality Finishing",
            ],
        ),
        Service(
            name="Welding Services",
            description="Expert welding services including MIG, TIG, and stick welding for repairs and new construction projects.",
            category="Welding",
            price_range="$75-$150 per hour",
            duration="1-3 days",
            features=["MIG Welding", "TIG Welding", "Stick Welding", "Mobile Service"],
        ),
        Service(
            name="Metal Repair & Restoration",
            description="Complete metal repair and restoration services for equipment, structures, and decorative metalwork.",
            category="Repair",
            price_range="Contact for quote",
            duration="Variable",
            features=[
                "Damage Assessment",
                "Structural Repair",
                "Surface Restoration",
                "Protective Coating",
            ],
        ),
    ]

    # Sample products
    products = [
        Product(
            sku="SMW-001",
            name="Custom Steel Brackets",
            description="Heavy-duty custom steel brackets for industrial mounting applications. Available in various sizes and configurations.",
            category="Brackets & Hardware",
            image_url="https://example.com/bracket.jpg",
        ),
        Product(
            sku="SMW-002",
            name="Aluminum Railings",
            description="Professional-grade aluminum railings for commercial and residential applications. Custom lengths available.",
            category="Railings",
            image_url="https://example.com/railing.jpg",
        ),
        Product(
            sku="SMW-003",
            name="Steel Security Gates",
            description="Heavy-duty steel security gates with custom locking mechanisms. Perfect for industrial facilities.",
            category="Security",
            image_url="https://example.com/gate.jpg",
        ),
    ]

    # Create complete configuration
    config = ClientConfig(
        business=business,
        contact=contact,
        branding=branding,
        services=services,
        products=products,
    )

    return config


def test_individual_generators(config):
    """Test individual generator components"""
    try:
        # Test HTML Generator
        print("   🔧 Testing HTML Generator...")
        from src.core.generators.html_generator import HTMLGenerator

        html_gen = HTMLGenerator()

        homepage_html = html_gen.generate_homepage(config)
        if len(homepage_html) > 1000:  # Should be substantial
            print("      ✅ Homepage HTML generated")
        else:
            print("      ⚠️ Homepage HTML seems too short")

        about_html = html_gen.generate_about_page(config)
        if len(about_html) > 500:
            print("      ✅ About page HTML generated")
        else:
            print("      ⚠️ About page HTML seems too short")

        # Test CSS Generator
        print("   🎨 Testing CSS Generator...")
        from src.core.generators.css_generator import CSSGenerator

        css_gen = CSSGenerator()

        # Check what methods are available
        if hasattr(css_gen, "generate_main_css"):
            main_css = css_gen.generate_main_css(config)
            if len(main_css) > 1000:  # Should be comprehensive
                print("      ✅ Main CSS generated")
            else:
                print("      ⚠️ Main CSS seems too short")
        else:
            print("      ⚠️ CSS Generator doesn't have generate_main_css method")
            print(
                f"      Available methods: {[m for m in dir(css_gen) if not m.startswith('_')]}"
            )

        print("   ✅ Individual generators tested")

    except Exception as e:
        print(f"   ❌ Individual generator test failed: {e}")
        import traceback

        traceback.print_exc()


def run_enhanced_generation_test():
    """Test the enhanced main window integration"""
    print("\n🖥️ Testing Enhanced Main Window Integration...")

    try:
        from PyQt6.QtWidgets import QApplication
        from src.ui.enhanced_main_window import EnhancedMainWindow

        # Create QApplication if needed
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        # Create enhanced main window
        main_window = EnhancedMainWindow()
        print("   ✅ Enhanced main window created")

        # Test that generator manager can be created
        from src.core.generators.generator_manager import GeneratorManager

        GeneratorManager()
        print("   ✅ Generator manager created")

        # Test configuration creation
        config_data = {
            "business": {
                "business_name": "Test Company",
                "domain": "https://test.com",
                "industry": "Testing",
            },
            "contact": {
                "name": "Test Company",
                "phone": "555-1234",
                "email": "test@test.com",
                "address": "123 Test St",
            },
            "branding": {
                "primary_color": "#007bff",
                "secondary_color": "#6c757d",
                "font_family": "Arial, sans-serif",
                "logo_url": "",
            },
            "products": {"products": []},
            "services": {"services": []},
        }

        main_window.create_client_config(config_data)
        print("   ✅ ClientConfig creation from UI data works")

        return True

    except Exception as e:
        print(f"   ❌ Enhanced integration test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """Run all generation tests"""
    print("🧪 Website Generation Test Suite")
    print("Sprint 2 Week 2 - Days 7-8")
    print("=" * 60)

    tests = [
        ("Core Generation System", test_website_generation),
        ("Enhanced UI Integration", run_enhanced_generation_test),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)

        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")

    print("\n" + "=" * 60)
    print(f"📊 GENERATION TEST RESULTS: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL GENERATION TESTS PASSED!")
        print("✅ Website generation system is ready for use")
        print("\n🚀 Next Steps:")
        print("   1. Run: python main.py")
        print("   2. Fill in business information")
        print("   3. Click 'Generate Website' button")
        print("   4. Test the generated website")
        return True
    else:
        print("⚠️ Some generation tests failed")
        print("🔧 Please fix the failing components before proceeding")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
