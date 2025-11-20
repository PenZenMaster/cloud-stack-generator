"""
Test script to view schema output from enhanced schema generation
"""
import json
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config.models import (
    ClientConfig,
    BusinessConfig,
    ContactConfig,
    AddressConfig,
    BrandingConfig,
    ProductConfig,
    ServiceConfig,
    SocialMediaConfig,
    GoogleBusinessProfileConfig,
    CityPageConfig
)
from src.core.generators.html_generator import HTMLGenerator


def test_schema_with_public_address():
    """Test schema generation with publicly visible address (LocalBusiness)"""
    print("=" * 80)
    print("TEST 1: Schema with PUBLIC ADDRESS (LocalBusiness)")
    print("=" * 80)

    config = ClientConfig(
        business=BusinessConfig(
            business_name="Acme Metal Fabrication",
            domain="https://acmemetal.com",
            industry="Metal Fabrication",
            description="Custom architectural metalwork and fabrication services",
            tagline="Precision Metal Fabrication Since 1995"
        ),
        contact=ContactConfig(
            phone="+1-555-123-4567",
            email="info@acmemetal.com",
            address=AddressConfig(
                street="123 Industrial Way",
                city="Richmond",
                state="Virginia",
                zip_code="23219",
                country="United States",
                publish_on_website=True  # Address is public
            )
        ),
        branding=BrandingConfig(
            logo_url="https://acmemetal.com/logo.png"
        ),
        social_media=SocialMediaConfig(
            facebook="https://facebook.com/acmemetal",
            linkedin="https://linkedin.com/company/acmemetal",
            instagram="https://instagram.com/acmemetal"
        ),
        google_business_profile=GoogleBusinessProfileConfig(
            profile_url="https://g.page/acmemetal",
            expose_address=False,  # GBP doesn't expose address, but website does
            place_id="ChIJexample123",
            rating="4.8",
            review_count="127"
        )
    )

    # Add products
    config.products.append(ProductConfig(
        sku="CUP-001",
        name="Custom Copper Cupola",
        description="Hand-crafted copper cupola for architectural applications",
        category="Architectural Elements",
        price="2500",
        image_url="https://acmemetal.com/images/products/copper-cupola.jpg"
    ))

    # Add services
    config.services.append(ServiceConfig(
        name="Custom Metal Fabrication",
        description="Precision metal fabrication for architectural projects",
        category="Fabrication Services"
    ))

    # Add city pages for areaServed
    config.city_pages.append(CityPageConfig(
        city_name="Richmond",
        state="Virginia"
    ))
    config.city_pages.append(CityPageConfig(
        city_name="Charlottesville",
        state="Virginia"
    ))

    # Generate schema
    generator = HTMLGenerator()
    schema = generator._generate_organization_schema(config)

    print(json.dumps(schema, indent=2))
    print("\n")


def test_schema_with_private_address():
    """Test schema generation with private address (Organization)"""
    print("=" * 80)
    print("TEST 2: Schema with PRIVATE ADDRESS (Organization)")
    print("=" * 80)

    config = ClientConfig(
        business=BusinessConfig(
            business_name="Elite Consulting Services",
            domain="https://eliteconsulting.com",
            industry="Business Consulting",
            description="Strategic business consulting and advisory services"
        ),
        contact=ContactConfig(
            phone="+1-555-987-6543",
            email="contact@eliteconsulting.com",
            address=AddressConfig(
                street="456 Corporate Blvd",
                city="Arlington",
                state="Virginia",
                zip_code="22201",
                country="United States",
                publish_on_website=False  # Address is PRIVATE
            )
        ),
        google_business_profile=GoogleBusinessProfileConfig(
            expose_address=False  # GBP also doesn't expose address
        ),
        social_media=SocialMediaConfig(
            linkedin="https://linkedin.com/company/eliteconsulting",
            twitter="https://twitter.com/eliteconsult"
        )
    )

    # Add a service
    config.services.append(ServiceConfig(
        name="Business Strategy Consulting",
        description="Comprehensive business strategy development and execution"
    ))

    # Generate schema
    generator = HTMLGenerator()
    schema = generator._generate_organization_schema(config)

    print(json.dumps(schema, indent=2))
    print("\n")


def test_schema_with_gbp_exposed_address():
    """Test schema with GBP exposed address"""
    print("=" * 80)
    print("TEST 3: Schema with GBP EXPOSED ADDRESS (LocalBusiness)")
    print("=" * 80)

    config = ClientConfig(
        business=BusinessConfig(
            business_name="Main Street Cafe",
            domain="https://mainstreetcafe.com",
            industry="Restaurant",
            description="Family-owned cafe serving fresh, local cuisine"
        ),
        contact=ContactConfig(
            phone="+1-555-CAFE-123",
            email="hello@mainstreetcafe.com",
            address=AddressConfig(
                street="789 Main Street",
                city="Alexandria",
                state="Virginia",
                zip_code="22301",
                publish_on_website=False  # Not on website
            )
        ),
        google_business_profile=GoogleBusinessProfileConfig(
            profile_url="https://g.page/mainstreetcafe",
            expose_address=True,  # BUT exposed on GBP
            place_id="ChIJcafe789",
            rating="4.9",
            review_count="342"
        ),
        social_media=SocialMediaConfig(
            facebook="https://facebook.com/mainstreetcafe",
            instagram="https://instagram.com/mainstreetcafe"
        )
    )

    # Add city for areaServed
    config.city_pages.append(CityPageConfig(
        city_name="Alexandria",
        state="Virginia"
    ))

    # Generate schema
    generator = HTMLGenerator()
    schema = generator._generate_organization_schema(config)

    print(json.dumps(schema, indent=2))
    print("\n")


def analyze_schema_features(schema):
    """Analyze and report on schema features"""
    print("=" * 80)
    print("SCHEMA ANALYSIS")
    print("=" * 80)

    graph = schema.get("@graph", [])

    # Find business entity
    business = next((e for e in graph if e["@type"] in ["LocalBusiness", "Organization"]), None)

    if business:
        print(f"\nBusiness Type: {business['@type']}")
        print(f"Has Address: {'address' in business}")
        print(f"Has areaServed: {'areaServed' in business}")
        print(f"Has sameAs: {'sameAs' in business}")

        if "areaServed" in business:
            print(f"  - Service Areas: {len(business['areaServed'])}")
            for area in business["areaServed"]:
                print(f"    - {area['name']}")

        if "sameAs" in business:
            print(f"  - Social Media Links: {len(business['sameAs'])}")

    # Count entity types
    products = [e for e in graph if e.get("@type") == "Product"]
    services = [e for e in graph if e.get("@type") == "Service"]

    print("\nEntities in @graph:")
    print(f"  - Total: {len(graph)}")
    print(f"  - Products: {len(products)}")
    print(f"  - Services: {len(services)}")
    print(f"  - WebSite: {len([e for e in graph if e.get('@type') == 'WebSite'])}")
    print(f"  - WebPage: {len([e for e in graph if e.get('@type') == 'WebPage'])}")
    print("\n")


if __name__ == "__main__":
    # Run tests
    test_schema_with_public_address()
    test_schema_with_private_address()
    test_schema_with_gbp_exposed_address()

    # Generate one for detailed analysis
    print("\n")
    print("#" * 80)
    print("DETAILED ANALYSIS - Test 1 Schema")
    print("#" * 80)

    config = ClientConfig(
        business=BusinessConfig(
            business_name="Test Business",
            domain="https://test.com",
            industry="Testing"
        ),
        contact=ContactConfig(
            address=AddressConfig(publish_on_website=True)
        ),
        google_business_profile=GoogleBusinessProfileConfig()
    )
    config.products.append(ProductConfig(sku="TEST-001", name="Test Product"))
    config.services.append(ServiceConfig(name="Test Service"))
    config.city_pages.append(CityPageConfig(city_name="TestCity", state="TestState"))

    generator = HTMLGenerator()
    schema = generator._generate_organization_schema(config)
    analyze_schema_features(schema)
