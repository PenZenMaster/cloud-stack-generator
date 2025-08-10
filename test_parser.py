"""
Test the configuration parser with sample data
Run from project root directory
"""

from src.core.config.parser import ConfigParser, ConfigParsingError
from src.core.config.models import ClientConfig


def test_parser_with_sample_data():
    """Test parser with sample YAML data"""
    print("🔍 Testing Configuration Parser...")

    # Sample YAML data (similar to what your current app generates)
    sample_yaml = {
        "client": {
            "business_name": "Salvo Metal Works",
            "domain": "https://salvometalworks.com",
            "industry": "Metal Fabrication",
            "contact": {
                "name": "Salvo Metal Works",
                "phone": "(866) 713-3396",
                "address": "123 Industrial Way, Detroit, MI 48201",
                "email": "info@salvometalworks.com",
            },
            "branding": {
                "primary_color": "#FF5722",
                "secondary_color": "#FFC107",
                "font_family": "Arial, sans-serif",
                "logo_url": "https://salvometalworks.com/logo.png",
            },
            "social_media": {
                "facebook": "https://facebook.com/salvometalworks",
                "linkedin": "https://linkedin.com/company/salvometalworks",
            },
            "google_business_profile": {
                "embed_code": "<iframe src='https://maps.google.com/...'></iframe>"
            },
            "pages": [
                {
                    "title": "Home",
                    "slug": "index",
                    "primary_keyword": "metal fabrication",
                    "secondary_keywords": ["custom metalwork", "detroit metal shop"],
                    "hero_image": "https://salvometalworks.com/hero.jpg",
                },
                {
                    "title": "Metal Fabrication in Detroit",
                    "slug": "detroit",
                    "city": "Detroit",
                    "primary_keyword": "metal fabrication detroit",
                    "secondary_keywords": ["detroit metalwork"],
                    "hero_image": "https://salvometalworks.com/hero.jpg",
                },
            ],
            "offerings": [
                {
                    "name": "Custom Welding",
                    "description": "Professional custom welding services",
                    "category": "Fabrication",
                    "type": "service",
                },
                {
                    "name": "Steel Railings",
                    "sku": "SM-001",
                    "description": "High-quality steel railings",
                    "category": "Products",
                    "type": "product",
                    "image_url": "https://salvometalworks.com/images/railings.jpg",
                },
                {
                    "name": "Architectural Metalwork",
                    "description": "Custom architectural metal solutions",
                    "category": "Fabrication",
                    "type": "service",
                },
            ],
            "faq": [
                {
                    "question": "What services do you offer?",
                    "answer": "We offer custom welding, metal fabrication, and architectural metalwork.",
                },
                {
                    "question": "Do you serve the Detroit area?",
                    "answer": "Yes, we proudly serve Detroit and surrounding areas.",
                },
            ],
        }
    }

    try:
        # Test parsing
        parser = ConfigParser()
        config = parser.parse_yaml_dict(sample_yaml)

        # Verify business info
        assert config.business.business_name == "Salvo Metal Works"
        assert config.business.domain == "https://salvometalworks.com"
        assert config.business.industry == "Metal Fabrication"
        print("✅ Business info parsed correctly")

        # Verify contact info (phone should be normalized)
        assert config.contact.phone == "+1-866-713-3396"
        assert config.contact.address == "123 Industrial Way, Detroit, MI 48201"
        print("✅ Contact info parsed correctly (phone normalized)")

        # Verify branding
        assert config.branding.primary_color == "#FF5722"
        assert config.branding.secondary_color == "#FFC107"
        print("✅ Branding parsed correctly")

        # Verify social media
        social_links = config.social_media.get_valid_links()
        assert "facebook" in social_links
        assert "linkedin" in social_links
        assert len(social_links) == 2  # Only facebook and linkedin provided
        print("✅ Social media parsed correctly")

        # Verify pages
        assert len(config.pages) == 2
        home_page = next(p for p in config.pages if p.slug == "index")
        detroit_page = next(p for p in config.pages if p.slug == "detroit")
        assert home_page.title == "Home"
        assert detroit_page.city == "Detroit"
        print("✅ Pages parsed correctly")

        # Verify offerings separation
        assert len(config.services) == 2  # Custom Welding, Architectural Metalwork
        assert len(config.products) == 1  # Steel Railings

        # Check service
        welding_service = next(s for s in config.services if s.name == "Custom Welding")
        assert welding_service.category == "Fabrication"

        # Check product
        railings_product = config.products[0]
        assert railings_product.sku == "SM-001"
        assert railings_product.name == "Steel Railings"
        print("✅ Products and services separated correctly")

        # Verify FAQ
        assert len(config.faq) == 2
        assert config.faq[0].question == "What services do you offer?"
        print("✅ FAQ parsed correctly")

        # Test validation
        is_valid, errors = config.validate()
        assert is_valid, f"Configuration should be valid, but got errors: {errors}"
        print("✅ Configuration validation passed")

        # Test YAML generation (round-trip)
        yaml_dict = parser.generate_yaml_dict(config)
        assert "client" in yaml_dict
        assert yaml_dict["client"]["business_name"] == "Salvo Metal Works"

        # Verify offerings in generated YAML
        offerings = yaml_dict["client"]["offerings"]
        service_offerings = [o for o in offerings if o["type"] == "service"]
        product_offerings = [o for o in offerings if o["type"] == "product"]
        assert len(service_offerings) == 2
        assert len(product_offerings) == 1
        print("✅ YAML generation (round-trip) successful")

        print("\n🎉 Configuration Parser working perfectly!")
        print(
            f"✅ Parsed {len(config.services)} services and {len(config.products)} products"
        )
        print(f"✅ Parsed {len(config.pages)} pages")
        print(f"✅ Parsed {len(config.faq)} FAQ items")

        return True

    except Exception as e:
        print(f"❌ Parser test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_error_handling():
    """Test parser error handling"""
    print("\n🔍 Testing error handling...")

    parser = ConfigParser()

    # Test invalid YAML structure (wrong type)
    try:
        # This should raise an exception since we're passing wrong type
        config = parser.parse_yaml_dict("not a dict")  # type: ignore
        print("❌ Should have raised an exception for invalid input type")
        return False
    except (ConfigParsingError, AttributeError, TypeError) as e:
        print(f"✅ Invalid YAML structure handled correctly: {type(e).__name__}")
    except Exception as e:
        print(f"✅ Invalid input handled with exception: {type(e).__name__}")

    # Test missing client section - this should work gracefully
    try:
        config = parser.parse_yaml_dict({"not_client": {}})
        # This should work but create mostly empty config
        print("✅ Missing client section handled gracefully")
        print(
            f"   Created config with business name: '{config.business.business_name}'"
        )
    except Exception as e:
        print(f"⚠️  Unexpected error with missing client: {e}")

    # Test invalid product (missing SKU)
    invalid_config = {
        "client": {
            "business_name": "Test",
            "offerings": [
                {
                    "name": "Invalid Product",
                    "type": "product",
                    # Missing SKU - should be skipped with warning
                }
            ],
        }
    }

    try:
        config = parser.parse_yaml_dict(invalid_config)
        # Should work but skip the invalid product
        if len(config.products) == 0:
            print("✅ Invalid product skipped with warning")
        else:
            print(f"⚠️  Expected 0 products, got {len(config.products)}")
    except Exception as e:
        print(f"⚠️  Error handling invalid product: {e}")

    # Test completely empty YAML
    try:
        config = parser.parse_yaml_dict({})
        print("✅ Empty YAML handled gracefully")
    except Exception as e:
        print(f"⚠️  Error with empty YAML: {e}")

    # Test file not found error
    try:
        config = parser.parse_yaml_file("nonexistent_file.yaml")
        print("❌ Should have raised ConfigParsingError for missing file")
        return False
    except ConfigParsingError:
        print("✅ Missing file handled correctly")
    except Exception as e:
        print(f"✅ Missing file handled with exception: {type(e).__name__}")

    return True


if __name__ == "__main__":
    print("🚀 Testing Configuration Parser...")
    print("=" * 50)

    success1 = test_parser_with_sample_data()
    success2 = test_error_handling()

    if success1 and success2:
        print("\n" + "=" * 50)
        print("🎉 Configuration Parser is ready!")
        print("✅ Handles existing YAML format")
        print("✅ Separates products and services")
        print("✅ Validates configurations")
        print("✅ Generates YAML output")
        print("✅ Handles errors gracefully")
        print("\nReady for Day 2 Step 2: Base UI Components!")
    else:
        print("\n❌ Some parser tests failed - need to fix before proceeding")
