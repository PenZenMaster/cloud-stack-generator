#!/usr/bin/env python3
"""
Test Enhanced City Page Generation

This script tests the new enhanced city page generator with rich content
matching the Chicago.html structure.

Usage: python test_enhanced_city_pages.py
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.config.models import (
    ClientConfig, BusinessConfig, ContactConfig, AddressConfig, BrandingConfig,
    CityPageConfig, CityImageConfig, PlaceOfInterest, CityFAQItem, ServiceConfig
)
from src.core.generators.enhanced_city_page_generator import EnhancedCityPageGenerator


def create_test_config() -> ClientConfig:
    """Create a test configuration similar to Salvo Metal Works"""
    
    # Business configuration
    business = BusinessConfig(
        business_name="Salvo Metal Works",
        domain="https://salvometalworks.com",
        industry="Custom Architectural Metal",
        description="Forging Function with Metal Mastery"
    )
    
    # Contact configuration
    address = AddressConfig(
        street="566 W 5th Ave",
        city="Naperville",
        state="IL",
        zip_code="60563",
        country="United States"
    )
    
    contact = ContactConfig(
        name="Salvo Metal Works",
        phone="+1-866-713-3396",
        address=address,
        email="info@salvometalworks.com"
    )
    
    # Branding configuration
    branding = BrandingConfig(
        primary_color="#b87333",  # Copper color
        secondary_color="#a1602b",  # Darker copper
        font_family="Inter, system-ui, -apple-system",
        logo_url="https://salvometalworks.com/logo.png"
    )
    
    # Services
    services = [
        ServiceConfig(name="Custom Cupolas", description="Handcrafted copper cupolas for residential and commercial buildings"),
        ServiceConfig(name="Custom Dormers", description="Architectural dormers that enhance both form and function"),
        ServiceConfig(name="Custom Finials", description="Decorative finials and architectural accents"),
        ServiceConfig(name="Custom Leader Boxes", description="Copper leader boxes for superior water management"),
        ServiceConfig(name="Custom Roof Vents", description="Functional roof vents with architectural appeal"),
        ServiceConfig(name="Custom Snow Guards", description="Snow retention systems for metal and slate roofs"),
        ServiceConfig(name="Custom Chimney Shrouds", description="Protective chimney shrouds and caps"),
    ]
    
    return ClientConfig(
        business=business,
        contact=contact,
        branding=branding,
        services=services
    )


def create_chicago_city_page() -> CityPageConfig:
    """Create a Chicago city page similar to the example"""
    
    return CityPageConfig(
        city_name="Chicago",
        state="IL",
        meta_description="Salvo Metal Works serves Chicago, IL with custom cupolas, dormers, finials, leader boxes, roof vents, snow guards, and chimney shrouds. Forging Function with Metal Mastery.",
        primary_keyword="custom architectural metal",
        secondary_keywords=["Chicago metalwork", "copper cupolas", "architectural fabrication"],
        
        about_city="""Chicago is the largest city in Illinois and a global hub for architecture, commerce, transportation, and the arts. Located along the southwestern shore of Lake Michigan, the city is known for its skyline punctuated by influential skyscrapers, extensive park system, and a rich legacy of neighborhoods shaped by waves of immigration and industry. Today, Chicago balances historic districts and landmark buildings with cutting-edge development, making it one of the most architecturally diverse urban environments in the United States.

Neighborhoods like the Loop, Near North Side, Hyde Park, Pilsen, and Wicker Park each reflect distinct eras and architectural movements, from the Chicago School and Prairie Style to Art Deco and contemporary high-performance design. With its four-season climate, lake effect, and prevailing winds, the city imposes rigorous demands on exterior building materials and details, which is why high-quality metals, weatherproof seams, and proven fabrication methods perform so well here.""",
        
        city_image=CityImageConfig(
            image_url="images/chicago.jpg",
            alt_text="Chicago skyline from Lake Michigan",
            caption="Caption: Chicago skyline from Lake Michigan. Credit: Wikipedia contributors (add exact credit when you import the file).",
            credit="Wikipedia contributors",
            source="Wikipedia"
        ),
        
        seo_content_title="Architectural Metalwork for Chicago Homes and Buildings",
        seo_content_body="""<p>When Chicago homeowners, builders, and property managers seek exterior details that elevate curb appeal and withstand lakefront weather, they turn to custom metalwork. Salvo Metal Works fabricates copper cupolas, dormers, finials, leader boxes, roof vents, snow guards, and chimney shrouds that balance aesthetics with function. Every project is engineered for Chicago's realities: temperature swings, wind uplift, freeze–thaw cycles, and the corrosive effects of lake moisture and road salt.</p>

<p>Our process starts with discovery. We review roof slope, substrate, and drainage, then study the building's architectural vocabulary—cornice lines, pane dimensions, eave depth, ridge height, and material transitions. For historic properties, we benchmark against period-correct details using photographs, field measurements, and archived drawings. For new construction, we collaborate with architects and roofers to align profiles, seam patterns, and flashing treatments with the overall design intent. The result is metalwork that looks born to the building.</p>

<p>Copper is our signature material for good reason. It forms a natural patina that protects the base metal, delivering service life measured in decades. In Chicago, where winter and wind are unforgiving, fully soldered seams make the difference between a detail that simply decorates and one that actively protects. Our dormers, leader boxes, and chimney shrouds are built with structural reinforcement and drip edges designed to move water away from critical joints and masonry. Where ventilation is required, we integrate screened openings sized for airflow while keeping out pests and debris.</p>

<p>Consider cupolas. Beyond their iconic profile, they help hot, moist air escape from attics and roof cavities—particularly useful during Chicago's humid summers and shoulder seasons. We custom-build bases to match roof pitch and integrate curb and flashing kits for asphalt, slate, and metal roofs. Lantern-style tops, louvered vents, and weathervane mounts are common options. For downtown or lakefront properties, we can increase seam strength and fastener schedules, or specify heavier copper to handle higher wind exposure.</p>

<p>Leader boxes (also called collector heads) are another Chicago essential. With heavy rain events increasingly common, gutters and downspouts benefit from a staging chamber that controls flow and reduces splash. We size inlets and outlets to your gutter profile, build integral backplates for clean mounting, and offer decorative face treatments—paneled, fluted, or embossed—that echo surrounding trim. The design goal is straightforward: keep water off the facade and foundation while adding a crafted focal point to the elevation.</p>

<p>Roof vents often hide in plain sight, but they do critical work. Our low-profile copper vents are fabricated for specific roof slopes, with internal baffles and stainless screens to maintain airflow while shedding wind-driven rain and snow. For long ridges, continuous ridge vent solutions can be matched to standing seam or shingle modules, maintaining the visual rhythm of the roof while improving performance. In winter, properly vented roof assemblies help minimize ice dams—a recurring issue in older Chicago housing stock.</p>

<p>Snow guards provide a different kind of protection. On metal and slate roofs, sliding snow can threaten gutters, landscaping, and pedestrian areas. We fabricate individual cleats or continuous bar systems in copper or color-matched metals, carefully spacing rows based on roof area, slope, and typical load. The goal is controlled melt and gradual release, not an abrupt avalanche. This is especially important over entryways, garage doors, and walkways where safety matters most.</p>

<p>Chimney shrouds round out the exterior protection story. Chicago's masonry chimneys endure repeated freeze–thaw cycles that exploit cracks and porous mortar. A properly designed shroud improves draft, shields the crown, and moves water away from the stack. We build to your flue arrangement and integrate screened vents for airflow. Anchor plates and hidden fasteners lock the assembly down while maintaining a refined profile that complements the roofline.</p>

<p>Every Salvo project follows a disciplined workflow: consultation and measurement, shop drawings for review, fabrication by skilled metalsmiths, and coordination with installers. If your project requires submittals or stamped drawings, we can support that process. We also provide care guidelines—how to let copper patina naturally, how to clean if you prefer a bright finish, and how to inspect flashing and sealants seasonally. Our aim is longevity, not just good looks on day one.</p>

<p>Whether you are restoring a greystone in Lincoln Park, modernizing a flat in Wicker Park, or specifying details for a North Shore new build, Salvo Metal Works brings precision and pride to the job. Send us photos and dimensions, or invite us to coordinate with your roofer or architect. We will translate your vision into a durable, beautiful solution tailored to Chicago's climate and architectural heritage.</p>""",
        
        places_of_interest=[
            PlaceOfInterest(
                name="Millennium Park",
                embed_url="https://www.google.com/maps?q=Millennium+Park+Chicago&output=embed"
            ),
            PlaceOfInterest(
                name="Art Institute of Chicago",
                embed_url="https://www.google.com/maps?q=Art+Institute+of+Chicago&output=embed"
            ),
            PlaceOfInterest(
                name="Wrigley Field",
                embed_url="https://www.google.com/maps?q=Wrigley+Field+Chicago&output=embed"
            ),
            PlaceOfInterest(
                name="Navy Pier",
                embed_url="https://www.google.com/maps?q=Navy+Pier+Chicago&output=embed"
            )
        ],
        
        city_faq=[
            CityFAQItem(
                question="Do copper cupolas hold up to Chicago weather?",
                answer="Yes. Our 16–20 oz copper with fully soldered seams is engineered for snow, wind, and freeze–thaw cycles common in Chicago."
            ),
            CityFAQItem(
                question="Can you match historical styles found in Chicago neighborhoods?",
                answer="We fabricate to spec from photos, sketches, or architectural drawings, matching profiles, seams, and patinas."
            ),
            CityFAQItem(
                question="Do you install in Chicago or work with local roofers?",
                answer="We offer install options in Chicagoland and coordinate with vetted local roofers for projects in the city."
            ),
            CityFAQItem(
                question="What is the lead time for custom dormers or chimney shrouds?",
                answer="Typical lead times range from 3–6 weeks depending on complexity and season. Rush options may be available."
            ),
            CityFAQItem(
                question="Do you provide stamped drawings if required by the city?",
                answer="We can provide submittal drawings and coordinate stamped documents where required."
            )
        ],
        
        featured_products=["custom-cupolas", "custom-dormers", "custom-finials", "custom-leader-boxes", "custom-roof-vents", "custom-snow-guards", "custom-chimney-shrouds"],
        city_map_embed="https://www.google.com/maps?q=Chicago,IL&output=embed",
        service_area_note="Service Area: Chicago and surrounding communities."
    )


def test_enhanced_city_page_generation():
    """Test the enhanced city page generation"""
    print("Testing Enhanced City Page Generation")
    print("=" * 50)
    
    try:
        # Create test configuration
        print("1. Creating test configuration...")
        config = create_test_config()
        
        # Create Chicago city page
        print("2. Creating Chicago city page configuration...")
        chicago_page = create_chicago_city_page()
        
        # Add to config
        config.add_city_page(chicago_page)
        
        # Create generator
        print("3. Initializing enhanced city page generator...")
        generator = EnhancedCityPageGenerator(config)
        
        # Create output directory
        output_dir = Path("test_output/enhanced_cities")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate Chicago page
        print("4. Generating Chicago city page...")
        chicago_file = generator.generate_city_page(chicago_page, str(output_dir))
        
        print(f"[OK] Chicago page generated: {chicago_file}")
        
        # Test sample city page creation
        print("5. Testing sample city page creation...")
        detroit_page = generator.create_sample_city_page("Detroit", "MI")
        config.add_city_page(detroit_page)
        
        detroit_file = generator.generate_city_page(detroit_page, str(output_dir))
        print(f"[OK] Detroit page generated: {detroit_file}")
        
        # Test all city pages generation
        print("6. Testing bulk generation...")
        milwaukee_page = generator.create_sample_city_page("Milwaukee", "WI")
        config.add_city_page(milwaukee_page)
        
        all_files = generator.generate_all_city_pages(str(output_dir))
        print(f"[OK] Generated {len(all_files)} city pages total")
        
        # Display results
        print("\n" + "=" * 50)
        print("GENERATION COMPLETE")
        print("=" * 50)
        print(f"Output directory: {output_dir}")
        print("Generated files:")
        for file_path in all_files:
            file_size = Path(file_path).stat().st_size
            print(f"  - {Path(file_path).name} ({file_size:,} bytes)")
        
        # Validate HTML structure
        print("\n7. Validating HTML structure...")
        with open(chicago_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check for key sections
        required_sections = [
            "About Chicago",
            "Architectural Metalwork for Chicago",
            "Places of Interest in Chicago", 
            "FAQ — Chicago Projects",
            "Popular Services for Chicago",
            "Chicago Map"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            print(f"[WARNING] Missing sections: {missing_sections}")
        else:
            print("[OK] All required sections present")
        
        # Check schema markup
        schema_checks = [
            '"@type":"WebPage"',
            '"@type":"LocalBusiness"',
            '"@type":"FAQPage"'
        ]
        
        missing_schema = []
        for schema in schema_checks:
            if schema not in content:
                missing_schema.append(schema)
        
        if missing_schema:
            print(f"[WARNING] Missing schema types: {missing_schema}")
        else:
            print("[OK] All schema markup present")
        
        print(f"\n[SUCCESS] Enhanced city page generation test completed successfully!")
        print(f"[INFO] Check the generated files in: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_enhanced_city_page_generation()
    sys.exit(0 if success else 1)