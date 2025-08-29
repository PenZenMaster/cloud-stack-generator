#!/usr/bin/env python3
"""
Test script for SEO Authority City Page Generation
Tests the new enhanced city page template with 800-1200 word content structure
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.config import load_config_from_file
from src.core.generators.enhanced_city_page_generator import EnhancedCityPageGenerator
from src.core.config.models import CityPageConfig, CityImageConfig, PlaceOfInterest, CityFAQItem


def test_seo_city_page_generation():
    """Test the SEO authority city page generation"""
    try:
        print("=== SEO Authority City Page Generation Test ===")
        
        # Load config
        print("Loading configuration...")
        config = load_config_from_file("config/clients/salvo_metal_works_config.yaml")
        
        print(f"+ Configuration loaded for: {config.business.business_name}")
        print(f"+ Industry: {config.business.industry}")
        print(f"+ Services: {len(config.services)}")
        print(f"+ City Pages: {len(config.city_pages)}")
        
        # Initialize generator
        generator = EnhancedCityPageGenerator(config)
        print("+ Generator initialized")
        
        # Test with existing city page or create sample
        if config.city_pages:
            test_city = config.city_pages[0]
            print(f"+ Using existing city page: {test_city.city_name}")
        else:
            # Create a sample city page with rich content
            test_city = create_sample_seo_city_page(config)
            config.city_pages.append(test_city)
            print(f"+ Created sample city page: {test_city.city_name}")
        
        # Test template context building
        print("\n--- Testing Template Context ---")
        context = generator._build_template_context(test_city)
        print(f"+ Context keys: {list(context.keys())}")
        print(f"+ Other cities for interlinking: {len(context.get('other_cities', []))}")
        print(f"+ Related services: {len(context.get('related_services', []))}")
        print(f"+ Current date: {context.get('current_date', 'N/A')}")
        
        # Test page generation
        print("\n--- Generating SEO City Page ---")
        output_dir = "test_output/seo_city_pages"
        os.makedirs(output_dir, exist_ok=True)
        
        generated_file = generator.generate_city_page(test_city, output_dir)
        print(f"+ Generated file: {generated_file}")
        
        # Analyze generated content
        print("\n--- Content Analysis ---")
        with open(generated_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Count key elements
        word_count = len(content.split())
        h1_count = content.count('<h1>')
        h2_count = content.count('<h2>')
        h3_count = content.count('<h3>')
        schema_count = content.count('application/ld+json')
        internal_links = content.count('href="/services/')
        
        print(f"+ Total word count: {word_count}")
        print(f"+ H1 headings: {h1_count}")
        print(f"+ H2 headings: {h2_count}")
        print(f"+ H3 headings: {h3_count}")
        print(f"+ Schema markup blocks: {schema_count}")
        print(f"+ Internal service links: {internal_links}")
        
        # Check for key SEO elements
        seo_elements = {
            "Title tag": "<title>" in content,
            "Meta description": 'name="description"' in content,
            "Open Graph": 'property="og:' in content,
            "Schema markup": 'application/ld+json' in content,
            "FAQ schema": '"@type":"FAQPage"' in content,
            "Wikipedia embed": 'city-showcase' in content or 'wikipedia-embed' in content,
            "Internal linking": 'href="/services/' in content,
            "Contact CTA": 'contact-cta' in content
        }
        
        print("\n--- SEO Elements Check ---")
        for element, present in seo_elements.items():
            status = "+ PRESENT" if present else "- MISSING"
            print(f"{status}: {element}")
        
        # Calculate SEO score
        seo_score = sum(seo_elements.values()) / len(seo_elements) * 100
        print(f"\n+ SEO Completeness Score: {seo_score:.1f}%")
        
        # Content structure analysis
        print("\n--- Content Structure Analysis ---")
        content_sections = [
            ("Hero section", 'class="hero-section"' in content),
            ("Wikipedia showcase", 'class="city-showcase"' in content),
            ("Main article content", 'class="main-article"' in content),
            ("Service grid", 'class="service-grid"' in content),
            ("Places of interest", 'class="poi-section"' in content),
            ("FAQ section", 'class="faq-section"' in content),
            ("Internal links", 'class="internal-links"' in content),
            ("Contact CTA", 'class="contact-cta"' in content),
            ("Footer", 'class="site-footer"' in content)
        ]
        
        for section, present in content_sections:
            status = "+ FOUND" if present else "- MISSING"
            print(f"{status}: {section}")
        
        print(f"\n=== SUCCESS: SEO Authority City Page Generated ===")
        print(f"File: {generated_file}")
        print(f"City: {test_city.city_name}")
        print(f"Word Count: {word_count}")
        print(f"SEO Score: {seo_score:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"\n=== ERROR: SEO City Page Generation Failed ===")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def create_sample_seo_city_page(config) -> CityPageConfig:
    """Create a sample city page with rich SEO content"""
    
    city_name = "Chicago"
    state = "Illinois"
    
    # Create comprehensive city page
    city_page = CityPageConfig(
        city_name=city_name,
        state=state,
        title=f"Custom Architectural Metal Fabrication in {city_name}, {state} | {config.business.business_name}",
        meta_description=f"{config.business.business_name} provides custom architectural metal fabrication services in {city_name}, {state}. Expert craftsmanship, local knowledge, and superior results. Get your free quote today.",
        primary_keyword="custom architectural metal fabrication",
        secondary_keywords=[
            f"{city_name.lower()} metal fabrication", 
            "architectural metalwork", 
            "custom steel fabrication",
            f"{state.lower()} metal services",
            "commercial metal fabrication"
        ],
        hero_title=f"Custom Architectural Metal Fabrication in {city_name}, {state}",
        breadcrumbs=["Home", "Service Areas", f"{city_name}, {state}"],
        about_city=f"{city_name} stands as one of America's architectural marvels, renowned for its innovative building designs, rich industrial heritage, and diverse commercial landscape. The city's unique combination of historic structures and modern developments creates exceptional opportunities for custom architectural metal fabrication. From the iconic steel-framed skyscrapers of the Loop to the industrial complexes along the Chicago River, {city_name}'s built environment demands the highest standards of metalwork craftsmanship and engineering excellence.",
        seo_content_title=f"Complete Guide to Architectural Metal Fabrication Services in {city_name}, {state}",
        seo_content_body=f"""<p>When {city_name} architects, contractors, and property developers need exceptional architectural metal fabrication, they trust the expertise and reliability of {config.business.business_name}. Our comprehensive approach combines advanced fabrication techniques with deep understanding of {city_name}'s unique architectural requirements, building codes, and design standards.</p>

<p>The {city_name} metropolitan area presents distinctive challenges and opportunities for metal fabrication projects. Our team understands the local factors that influence successful project outcomes, including seasonal weather patterns, municipal requirements, transportation logistics, and the city's diverse architectural styles ranging from classical to ultra-modern designs.</p>

<p>Our {city_name} services encompass every aspect of architectural metalwork, from initial concept development through final installation. We specialize in custom railings, structural elements, decorative panels, curtain wall systems, and specialty architectural features that enhance both the functionality and aesthetic appeal of commercial and residential properties throughout the region.</p>

<p>Quality materials and precision craftsmanship form the foundation of every {city_name} project we undertake. Our facility maintains extensive inventory of premium steel, aluminum, stainless steel, and specialty alloys, ensuring we can meet the specific requirements of any architectural application while adhering to local building codes and environmental standards.</p>

<p>The {city_name} construction industry moves at a rapid pace, and our project management systems are designed to support tight timelines without compromising quality. Our experienced team coordinates closely with general contractors, architects, and project managers to ensure seamless integration with overall construction schedules and milestones.</p>

<p>Safety remains our highest priority on every {city_name} project site. Our certified installation teams follow strict safety protocols and maintain current OSHA training and certifications. We carry comprehensive insurance coverage and bonding to protect our clients and ensure project continuity regardless of unforeseen circumstances.</p>

<p>Environmental responsibility guides our {city_name} operations through sustainable material sourcing, efficient fabrication processes, and responsible waste management practices. We can help specify materials and finishes that contribute to LEED certification goals while delivering superior performance and longevity.</p>

<p>From the prestigious commercial developments of River North to the historic renovations in Lincoln Park, {config.business.business_name} has established a reputation for excellence throughout {city_name}. Our portfolio includes work on landmark buildings, cutting-edge commercial projects, and distinctive residential developments that showcase our versatility and commitment to quality.</p>""",
        city_image=CityImageConfig(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Chicago_River_ferry_b.jpg/800px-Chicago_River_ferry_b.jpg",
            alt_text=f"Chicago skyline featuring architectural metalwork",
            caption=f"Chicago's iconic skyline showcases diverse architectural styles requiring expert metal fabrication",
            credit="Wikipedia",
            source="https://en.wikipedia.org/wiki/Chicago",
            embed_code="""<section class="city-image">
    <a title="Wikipedia - Chicago" href="https://en.wikipedia.org/wiki/Chicago" target="_blank" rel="noopener">
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/a/a5/Chicago_River_ferry_b.jpg/800px-Chicago_River_ferry_b.jpg" 
             alt="Chicago skyline featuring architectural metalwork"
             width="100%" 
             style="height: auto; margin: 20px 0;"
             loading="lazy">
    </a>
    <p class="image-caption">Wikipedia - Chicago</p>
</section>"""
        ),
        places_of_interest=[
            PlaceOfInterest(
                name="Millennium Park",
                embed_url="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2970.5234!2d-87.6226014!3d41.8825524!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x880e2ca55810a493%3A0x6c0d3cb8247dd428!2sMillennium%20Park!5e0!3m2!1sen!2sus!4v1234567890"
            ),
            PlaceOfInterest(
                name="Chicago Riverwalk",
                embed_url="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2970.3456!2d-87.6276543!3d41.8876654!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x880e2cb3e7c3c7c7%3A0x12345!2sChicago%20Riverwalk!5e0!3m2!1sen!2sus!4v1234567890"
            ),
            PlaceOfInterest(
                name="Navy Pier",
                embed_url="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2970.1234!2d-87.6098857!3d41.8919857!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x880e2b4f8f8f8f8f%3A0x87654!2sNavy%20Pier!5e0!3m2!1sen!2sus!4v1234567890"
            ),
            PlaceOfInterest(
                name="Willis Tower",
                embed_url="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2970.7890!2d-87.6356456!3d41.8789567!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x880e2d4d4d4d4d4d%3A0x98765!2sWillis%20Tower!5e0!3m2!1sen!2sus!4v1234567890"
            )
        ],
        city_faq=[
            CityFAQItem(
                question=f"Do you provide architectural metal fabrication services throughout {city_name}?",
                answer=f"Yes, {config.business.business_name} provides comprehensive architectural metal fabrication services throughout {city_name} and the entire metropolitan area, including all surrounding suburbs and communities."
            ),
            CityFAQItem(
                question=f"What makes your {city_name} metal fabrication services unique?",
                answer=f"Our deep understanding of {city_name}'s architectural heritage, building codes, and design standards, combined with state-of-the-art fabrication capabilities and expert craftsmanship, ensures superior results for every project."
            ),
            CityFAQItem(
                question=f"How quickly can you respond to {city_name} project requests?",
                answer=f"We typically respond to all {city_name} project inquiries within 24 hours with initial consultation scheduling. Our project timelines are customized based on complexity, with most installations completed within 2-6 weeks."
            ),
            CityFAQItem(
                question=f"Do you work with {city_name} architects and contractors?",
                answer=f"Absolutely! We collaborate closely with {city_name} architectural firms, general contractors, and development teams throughout the design and construction process to ensure seamless project integration."
            ),
            CityFAQItem(
                question=f"What areas around {city_name} do you serve?",
                answer=f"Beyond {city_name}, we serve the entire Chicagoland area including Evanston, Oak Park, Cicero, and other surrounding communities. Contact us to confirm service availability for your specific location."
            )
        ],
        featured_products=["custom-railings", "structural-steel", "architectural-panels"],
        city_map_embed=f"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d190055.0!2d-87.6500523!3d41.8337329!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x880e2c3cd0f4cbed%3A0xafe0a6ad09c0c000!2s{city_name}%2C%20{state}!5e0!3m2!1sen!2sus!4v1234567890",
        service_area_note=f"Service Area: {city_name} and all Chicagoland communities - Emergency services available"
    )
    
    return city_page


if __name__ == "__main__":
    success = test_seo_city_page_generation()
    sys.exit(0 if success else 1)