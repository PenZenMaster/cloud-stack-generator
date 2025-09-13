"""
City Page Generator - Enhanced SEO Authority Implementation
Generates comprehensive SEO-optimized city pages with 800-1200 word content structure

Enhanced with advanced features for SEO authority and strategic interlinking.
Supports both enhanced city pages and legacy migration in a single unified API.

Features:
- Enhanced 900+ word SEO authority content structure
- Industry-specific content sections for better SEO
- Strategic interlinking capabilities between city pages
- Wikipedia-style city information with rich media
- Places of interest with interactive maps
- City-specific FAQ sections with schema markup
- Comprehensive schema markup for local SEO
- Jinja2 templating with custom markdown and slugify filters
- Legacy migration support with automatic enhancement

Author: Cloud Stack Generator Team
Version: 3.1.0
Last Updated: 2025-08-29
"""

import re
from typing import List, Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from ..config.models import ClientConfig, CityPageConfig, CityImageConfig, PlaceOfInterest, CityFAQItem


class CityPageGenerator:
    """Generate unified SEO-optimized city pages with rich content"""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.template_dir = Path(__file__).parent.parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom filters
        self.jinja_env.filters['markdown_basic'] = self._markdown_basic_filter
        self.jinja_env.filters['slugify'] = self._slugify_filter
        
    def generate_city_page(self, city_page: CityPageConfig, output_dir: str) -> str:
        """Generate a single enhanced city page using Jinja2 templates"""
        try:
            # Load the SEO authority template
            template = self.jinja_env.get_template('pages/seo_authority_city_page.html')
            
            # Prepare template context
            context = self._build_template_context(city_page)
            
            # Render the template
            html_content = template.render(**context)
            
            # Write to file
            output_path = Path(output_dir) / f"{city_page.slug}.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Error generating city page for {city_page.city_name}: {str(e)}")
    
    def generate_city_page_from_string(self, city: str, output_dir: str) -> str:
        """Legacy method: Generate city page from string - creates enhanced city page"""
        # Parse city string into components
        parts = city.split(',')
        city_name = parts[0].strip()
        state = parts[1].strip() if len(parts) > 1 else ""
        
        # Create enhanced city page config
        city_page = self.create_sample_city_page(city_name, state)
        
        # Generate using unified method
        return self.generate_city_page(city_page, output_dir)
    
    def generate_all_city_pages(self, output_dir: str) -> List[str]:
        """Generate all city pages - supports both enhanced city_pages and legacy target_cities"""
        generated_files = []
        
        # Priority 1: Use enhanced city_pages if available
        if hasattr(self.config, 'city_pages') and self.config.city_pages:
            for city_page in self.config.city_pages:
                try:
                    file_path = self.generate_city_page(city_page, output_dir)
                    generated_files.append(file_path)
                    print(f"Generated enhanced city page: {city_page.city_name}")
                except Exception as e:
                    print(f"Error generating enhanced page for {city_page.city_name}: {e}")
                    
        # Fallback: Migrate legacy target_cities if no enhanced pages exist
        elif hasattr(self.config, 'target_cities') and self.config.target_cities:
            print("Migrating legacy target_cities to enhanced city pages...")
            for city in self.config.target_cities:
                try:
                    file_path = self.generate_city_page_from_string(city, output_dir)
                    generated_files.append(file_path)
                    print(f"Generated city page from legacy config: {city}")
                except Exception as e:
                    print(f"Error generating page for {city}: {e}")
        else:
            print("No city pages or target cities configured for generation")
                    
        return generated_files
    
    def create_sample_city_page(self, city_name: str, state: str = "") -> CityPageConfig:
        """Create a sample city page configuration for testing or migration"""
        return CityPageConfig(
            city_name=city_name,
            state=state,
            meta_description=f"{self.config.business.business_name} serves {city_name} with custom {self.config.business.industry.lower()} services. Professional craftsmanship and local expertise.",
            primary_keyword=f"custom {self.config.business.industry.lower()}",
            secondary_keywords=[city_name.lower(), f"{self.config.business.industry.lower()} services", "local business"],
            about_city=f"{city_name} is a vibrant community known for its architectural diversity and rich heritage. " +
                      f"The city presents unique opportunities and challenges for {self.config.business.industry.lower()} projects, " +
                      "requiring specialized knowledge of local building codes, climate considerations, and architectural styles. " +
                      f"Our team at {self.config.business.business_name} understands these local nuances and delivers solutions " +
                      f"that complement {city_name}'s distinctive character while meeting the highest standards of quality and durability.",
            city_image=CityImageConfig(
                image_url="images/placeholder-city.jpg",
                alt_text=f"{city_name} skyline and landmarks",
                caption=f"Caption: {city_name} cityscape highlighting local architecture.",
                credit="Image credit to be added when actual image is sourced",
                source="Wikipedia",
                embed_code=f"""<div class="wikipedia-embed">
                    <img src="images/placeholder-city.jpg" alt="{city_name} skyline and landmarks">
                    <p class="image-caption">Caption: {city_name} cityscape highlighting local architecture.</p>
                </div>"""
            ),
            seo_content_title=f"Professional {self.config.business.industry} Services for {city_name}",
            seo_content_body=self._generate_sample_seo_content(city_name),
            places_of_interest=[
                PlaceOfInterest(
                    name=f"{city_name} Downtown",
                    embed_url=f"https://www.google.com/maps?q={city_name}+Downtown&output=embed"
                ),
                PlaceOfInterest(
                    name=f"{city_name} Historic District", 
                    embed_url=f"https://www.google.com/maps?q={city_name}+Historic+District&output=embed"
                ),
                PlaceOfInterest(
                    name=f"{city_name} Main Street",
                    embed_url=f"https://www.google.com/maps?q={city_name}+Main+Street&output=embed"
                ),
                PlaceOfInterest(
                    name=f"{city_name} City Hall",
                    embed_url=f"https://www.google.com/maps?q={city_name}+City+Hall&output=embed"
                )
            ],
            city_faq=[
                CityFAQItem(
                    question=f"Do you provide {self.config.business.industry.lower()} services in {city_name}?",
                    answer=f"Yes, {self.config.business.business_name} proudly serves {city_name} and surrounding areas with professional {self.config.business.industry.lower()} services."
                ),
                CityFAQItem(
                    question=f"What makes your {self.config.business.industry.lower()} services ideal for {city_name}?",
                    answer=f"Our team understands {city_name}'s unique architectural styles, local building requirements, and climate considerations, ensuring our {self.config.business.industry.lower()} solutions are perfectly suited to the area."
                ),
                CityFAQItem(
                    question=f"How quickly can you respond to {city_name} service requests?",
                    answer=f"We strive to respond to all {city_name} service requests within 24 hours. For urgent projects, we offer expedited scheduling when possible."
                ),
                CityFAQItem(
                    question=f"Do you offer consultations for {city_name} projects?",
                    answer=f"Absolutely! We provide free consultations for all {city_name} projects, including site visits, project assessments, and detailed quotes."
                ),
                CityFAQItem(
                    question=f"What areas around {city_name} do you serve?",
                    answer=f"In addition to {city_name}, we serve the entire metropolitan area and surrounding communities. Contact us to confirm service availability for your specific location."
                )
            ],
            featured_products=[service.slug for service in self.config.services[:7]] if self.config.services else [],
            city_map_embed=f"https://www.google.com/maps?q={city_name},{state}&output=embed",
            service_area_note=f"Service Area: {city_name} and surrounding communities."
        )
    
    def migrate_legacy_cities(self) -> List[CityPageConfig]:
        """Migrate legacy target_cities to enhanced city pages"""
        migrated_pages = []
        
        if not hasattr(self.config, 'target_cities') or not self.config.target_cities:
            return migrated_pages
            
        for city_str in self.config.target_cities:
            # Parse city and state from string
            parts = city_str.split(',')
            city_name = parts[0].strip()
            state = parts[1].strip() if len(parts) > 1 else ""
            
            # Check if already exists in city_pages
            existing_cities = []
            if hasattr(self.config, 'city_pages') and self.config.city_pages:
                existing_cities = [cp.city_name.lower() for cp in self.config.city_pages]
            
            if city_name.lower() not in existing_cities:
                city_page = self.create_sample_city_page(city_name, state)
                migrated_pages.append(city_page)
                
        return migrated_pages
    
    def _build_template_context(self, city_page: CityPageConfig) -> Dict[str, Any]:
        """Build template context with all necessary data"""
        # Get other cities for strategic interlinking
        other_cities = []
        if hasattr(self.config, 'city_pages') and self.config.city_pages:
            other_cities = [cp for cp in self.config.city_pages if cp.city_name != city_page.city_name]
        
        # Get current date for content freshness
        from datetime import datetime
        current_date = datetime.now().strftime("%B %Y")
        
        # Get industry-specific content sections
        industry_sections = self._get_industry_specific_sections(city_page.city_name, self.config.business.industry)
        
        return {
            # City page data
            'city_page': city_page,
            
            # Business data
            'business': self.config.business,
            'contact': self.config.contact,
            'branding': self.config.branding,
            
            # Content data
            'services': self.config.services if hasattr(self.config, 'services') else [],
            'products': self.config.products if hasattr(self.config, 'products') else [],
            'social_media': getattr(self.config, 'social_media', None),
            'google_business_profile': getattr(self.config, 'google_business_profile', None),
            'google_business': getattr(self.config, 'google_business', None),
            
            # Strategic interlinking
            'other_cities': other_cities,
            'related_services': self._get_related_services(city_page),
            
            # Industry-specific content sections
            'industry_sections': industry_sections,
            
            # Page metadata
            'page_url': f"/{city_page.slug}/",
            'current_year': 2025,
            'current_date': current_date,
            
            # Template utilities
            'css_file': '/css/main.css',
            
            # SEO and schema data
            'schema_data': self._build_schema_data(city_page)
        }
    
    def _build_schema_data(self, city_page: CityPageConfig) -> Dict[str, Any]:
        """Build structured data for schema markup"""
        return {
            'business_name': self.config.business.business_name,
            'business_url': self.config.business.domain,
            'city_name': city_page.city_name,
            'service_area': city_page.full_city_name,
            'contact_phone': self.config.contact.phone,
            'contact_email': self.config.contact.email,
            'address': {
                'street': getattr(self.config.contact.address, 'street', ''),
                'city': getattr(self.config.contact.address, 'city', ''),
                'state': getattr(self.config.contact.address, 'state', ''),
                'zip': getattr(self.config.contact.address, 'zip_code', ''),
                'country': getattr(self.config.contact.address, 'country', 'US')
            }
        }
    
    def _generate_sample_seo_content(self, city_name: str) -> str:
        """Generate comprehensive 900+ word SEO content for city pages with enhanced sections"""
        business_name = self.config.business.business_name
        industry = self.config.business.industry.lower()
        
        # Get service names for content
        service_list = "professional services"
        if hasattr(self.config, 'services') and self.config.services:
            service_list = ", ".join([service.name.lower() for service in self.config.services[:5]])
        
        content = f"""<p>When {city_name} residents and businesses need professional {industry} services, they turn to {business_name}. Our experienced team provides comprehensive solutions tailored to the unique needs of the {city_name} area, combining industry expertise with local knowledge to deliver exceptional results that exceed expectations.</p>

<p>Our approach begins with understanding your specific requirements and the local context of {city_name}. We take into account critical factors such as local building codes, architectural heritage, climate considerations, seasonal variations, and community standards. This meticulous attention to detail ensures that our {industry} solutions not only meet your functional requirements but also complement the distinctive character and aesthetic appeal of {city_name}.</p>

<p>The comprehensive services we provide throughout {city_name} include {service_list}. Each project receives our complete attention and dedication, with highly skilled craftspeople who understand the paramount importance of quality workmanship, precision execution, and exceptional attention to detail. We're committed to utilizing only the finest materials, proven industry techniques, and innovative approaches to ensure lasting results that stand up to {city_name}'s unique climate conditions and environmental challenges.</p>

<h4>Local Expertise and Industry Leadership in {city_name}</h4>

<p>What distinguishes {business_name} as the premier choice in the competitive {city_name} market is our unwavering commitment to customer satisfaction combined with our deep understanding of local requirements, regulations, and preferences. We've systematically built our outstanding reputation by consistently delivering projects on schedule, within agreed budgets, and to the highest industry standards of quality and craftsmanship.</p>

<p>Our professional team takes genuine pride in being highly responsive to our clients' evolving needs while maintaining transparent, clear communication throughout every phase of the project lifecycle. This client-centric approach has earned us the trust and loyalty of hundreds of satisfied customers throughout the {city_name} metropolitan area.</p>

<h4>Residential Excellence and Property Value Enhancement</h4>

<p>For {city_name} homeowners, we fully understand that your residential property represents one of your most significant financial investments and personal sanctuaries. That's precisely why we approach every residential project with the exceptional care, attention, and respect it truly deserves. From the initial consultation and detailed planning phases through final project completion and follow-up, we work collaboratively with you to ensure that the final result not only exceeds your highest expectations but also substantially adds measurable value to your property.</p>

<p>Our residential services in {city_name} are designed to enhance both the functionality and aesthetic appeal of your home while respecting the neighborhood's architectural character. We understand the unique challenges of working in established residential areas and coordinate our activities to minimize disruption to your daily routine and neighborhood harmony.</p>

<h4>Commercial Solutions and Business Continuity</h4>

<p>Commercial clients throughout {city_name} consistently appreciate our thoroughly professional approach and our proven ability to work efficiently within their specific operational requirements and constraints. We understand that maintaining business continuity is absolutely crucial to your success, and we meticulously plan and execute our projects to minimize operational disruption while delivering superior results that enhance your business environment.</p>

<p>Our extensive experience with diverse commercial applications across various industries ensures that we can expertly handle projects of any scale, complexity, or specialized requirements. From small office improvements to large-scale commercial installations, we bring the same level of professionalism, expertise, and attention to detail that has made us the trusted choice for {city_name} businesses.</p>

<h4>Regional Knowledge and Environmental Considerations</h4>

<p>The {city_name} area presents unique opportunities and distinctive challenges that require specialized knowledge, extensive experience, and strategic thinking. Our team has accumulated years of hands-on experience working throughout this region and possesses comprehensive understanding of the local factors that can significantly impact {industry} projects, including seasonal weather patterns, soil conditions, local supplier networks, and regulatory requirements.</p>

<p>This invaluable regional expertise allows us to proactively anticipate potential challenges and implement effective solutions that ensure consistent project success while avoiding common pitfalls that less experienced contractors might encounter. We maintain strong relationships with local suppliers, inspectors, and other professionals, facilitating smooth project execution.</p>

<h4>Quality Materials and Sustainable Practices</h4>

<p>Premium quality materials form the foundation of longevity and superior performance in any {industry} project. We source our materials exclusively from trusted, established suppliers and manufacturers with proven track records, ensuring that every component meets or exceeds our rigorous standards for durability, performance, and aesthetic appeal. In {city_name}'s specific climate conditions, this unwavering attention to material quality is especially crucial for ensuring long-term satisfaction and lasting value.</p>

<p>Environmental responsibility and sustainability have become increasingly important priorities for {city_name} residents and forward-thinking businesses. We're fully committed to implementing sustainable practices throughout our operations and can expertly guide you in selecting eco-friendly options that minimize environmental impact while delivering superior performance and long-term value.</p>

<h4>Safety Standards and Professional Excellence</h4>

<p>Safety remains our absolute top priority on every single {city_name} project, regardless of size or complexity. Our entire team rigorously follows strict safety protocols and maintains current industry certifications and specialized training. We carry comprehensive insurance coverage to protect both our valued clients and our dedicated workers, providing complete peace of mind throughout the entire project process.</p>

<p>Customer service excellence forms the cornerstone of everything we accomplish in {city_name}. We firmly believe that clear, honest communication, reliable scheduling, and meticulous attention to detail are equally as important as technical expertise and craftsmanship. Our primary goal is to make the entire experience positive, educational, and completely stress-free for our clients while delivering results that exceed expectations.</p>

<p>Whether you're planning a small residential improvement, a major renovation, or a large commercial installation anywhere in {city_name}, {business_name} possesses the experience, expertise, resources, and unwavering commitment to excellence you need for guaranteed success. We cordially invite you to contact us today to discuss your specific project requirements and discover how we can help transform your vision into reality with exceptional results that last for years to come.</p>"""
        
        return content
    
    def _get_related_services(self, city_page: CityPageConfig) -> List:
        """Get services related to this city page for strategic interlinking"""
        if hasattr(self.config, 'services') and self.config.services:
            return self.config.services[:7]  # Limit to top 7 services for UI purposes
        return []
    
    def _get_industry_specific_sections(self, city_name: str, industry: str) -> Dict[str, str]:
        """Generate industry-specific content sections for enhanced SEO authority"""
        business_name = self.config.business.business_name
        industry_lower = industry.lower()
        
        # Industry-specific section templates
        industry_templates = {
            'construction': {
                'expertise_title': 'Construction Excellence and Building Innovation',
                'expertise_content': f"""Our construction expertise in {city_name} spans residential, commercial, and industrial projects of all sizes. We understand the unique building challenges that {city_name}'s climate, soil conditions, and architectural heritage present, adapting our construction methodologies to ensure optimal results that stand the test of time. From foundation work to final finishes, our construction professionals bring decades of combined experience to every {city_name} project.""",
                
                'specialization_title': 'Specialized Construction Services for {city_name}',
                'specialization_content': f"""The diverse construction needs of {city_name} require specialized approaches and expertise. Our team excels in working with both traditional construction methods that respect the area's architectural heritage and innovative building techniques that provide enhanced performance and energy efficiency. We coordinate closely with {city_name} building departments to ensure all work meets or exceeds local construction codes and standards."""
            },
            
            'roofing': {
                'expertise_title': 'Roofing Excellence and Weather Protection',
                'expertise_content': f"""Our roofing expertise in {city_name} addresses the specific challenges posed by local weather patterns, from intense summer heat to winter snow loads and everything in between. We understand how {city_name}'s climate affects different roofing materials and systems, enabling us to recommend and install solutions that provide optimal protection and longevity for your investment.""",
                
                'specialization_title': 'Advanced Roofing Solutions for {city_name} Properties',
                'specialization_content': f"""Every roof in {city_name} faces unique environmental stresses that require specialized attention. Our roofing professionals are experts in selecting and installing roofing systems that complement {city_name}'s architectural styles while providing superior weather protection. We work with premium materials specifically chosen for their performance in local climate conditions."""
            },
            
            'plumbing': {
                'expertise_title': 'Comprehensive Plumbing Solutions and Water Systems',
                'expertise_content': f"""Our plumbing services in {city_name} address everything from routine maintenance to complex system installations and emergency repairs. We understand the unique challenges that {city_name}'s water infrastructure, soil conditions, and building codes present, ensuring our plumbing solutions are both compliant and optimized for local conditions.""",
                
                'specialization_title': 'Advanced Plumbing Technologies for {city_name}',
                'specialization_content': f"""Modern plumbing in {city_name} requires understanding of both traditional systems and innovative technologies. Our certified plumbers stay current with the latest in water efficiency, smart home integration, and sustainable plumbing practices that benefit both {city_name} residents and the environment."""
            },
            
            'electrical': {
                'expertise_title': 'Electrical Systems and Power Solutions',
                'expertise_content': f"""Our electrical services in {city_name} encompass residential, commercial, and industrial electrical needs with a focus on safety, efficiency, and code compliance. We understand {city_name}'s electrical infrastructure requirements and work closely with local utility providers to ensure seamless integration of new electrical systems.""",
                
                'specialization_title': 'Smart Electrical Solutions for Modern {city_name} Properties',
                'specialization_content': f"""Today's electrical needs in {city_name} go far beyond basic wiring. Our licensed electricians specialize in smart home technologies, energy-efficient lighting systems, solar integration, and electric vehicle charging solutions that meet the evolving needs of {city_name} residents and businesses."""
            },
            
            'landscaping': {
                'expertise_title': 'Landscape Design and Environmental Harmony',
                'expertise_content': f"""Our landscaping services in {city_name} focus on creating outdoor spaces that thrive in the local climate while enhancing property value and environmental sustainability. We understand {city_name}'s growing conditions, native plant species, and seasonal considerations to design landscapes that remain beautiful year-round with minimal maintenance requirements.""",
                
                'specialization_title': 'Sustainable Landscaping for {city_name} Properties',
                'specialization_content': f"""Sustainable landscaping in {city_name} requires deep understanding of local ecosystems, water conservation, and native plant communities. Our landscape professionals create designs that support local wildlife, reduce water usage, and complement the natural beauty of the {city_name} area while meeting your aesthetic and functional requirements."""
            },
            
            # Default template for unlisted industries
            'default': {
                'expertise_title': f'{industry} Expertise and Professional Excellence',
                'expertise_content': f"""Our {industry_lower} expertise in {city_name} is built on years of experience serving the local community with professional, reliable service. We understand the unique requirements that {city_name} properties and businesses have, adapting our {industry_lower} services to meet local conditions, regulations, and client expectations with precision and care.""",
                
                'specialization_title': f'Specialized {industry} Services for {city_name}',
                'specialization_content': f"""The diverse {industry_lower} needs of {city_name} require specialized knowledge and flexible approaches. Our team combines traditional {industry_lower} expertise with innovative techniques and technologies to deliver solutions that are perfectly suited to the {city_name} market and local requirements."""
            }
        }
        
        # Get industry-specific template or default
        template = industry_templates.get(industry_lower, industry_templates['default'])
        
        # Format with city name
        return {
            'expertise_title': template['expertise_title'].format(city_name=city_name),
            'expertise_content': template['expertise_content'],
            'specialization_title': template['specialization_title'].format(city_name=city_name),
            'specialization_content': template['specialization_content']
        }
    
    def _markdown_basic_filter(self, text: str) -> str:
        """Basic markdown processing for simple formatting"""
        if not text:
            return text
        
        # Convert **Ready to talk details?** to <h2> (special case - do this FIRST)
        text = re.sub(r'\*\*Ready to talk details\?\*\*', r'<h2>Ready to talk details?</h2>', text)
        
        # Convert **bold** to <strong>
        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
        
        # Convert *italic* to <em>
        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
        
        # Convert [text](url) to <a href="url">text</a>
        text = re.sub(r'\[([^\]]*)\]\(([^)]*)\)', r'<a href="\2">\1</a>', text)
        
        return text
    
    def _slugify_filter(self, text: str) -> str:
        """Simple slugify function for URL-friendly strings"""
        if not text:
            return text
        
        text = text.lower()
        text = text.replace(' ', '-')
        text = text.replace(',', '')
        text = text.replace(' illinois', '')
        text = text.replace(' il', '')
        return text.strip('-')