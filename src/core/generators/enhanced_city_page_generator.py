"""
Enhanced City Page Generator
Generates rich SEO-optimized city pages using the new CityPageConfig data model

This generator creates sophisticated city pages with the Chicago.html structure:
- Wikipedia-style city information
- 800+ word SEO content sections  
- Places of interest with maps
- City-specific FAQ sections
- Rich schema markup

Author: Cloud Stack Generator Team  
Version: 2.3.0
"""

import os
from typing import List, Dict, Any, Optional
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader

from ..config.models import ClientConfig, CityPageConfig, CityImageConfig, PlaceOfInterest, CityFAQItem


class EnhancedCityPageGenerator:
    """Generate enhanced SEO-optimized city pages with rich content"""
    
    def __init__(self, config: ClientConfig):
        self.config = config
        self.template_dir = Path(__file__).parent.parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
    def generate_city_page(self, city_page: CityPageConfig, output_dir: str) -> str:
        """Generate a single enhanced city page"""
        try:
            # Load the enhanced template
            template = self.jinja_env.get_template('pages/enhanced_city_page.html')
            
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
    
    def generate_all_city_pages(self, output_dir: str) -> List[str]:
        """Generate all enhanced city pages from config.city_pages"""
        generated_files = []
        
        if not self.config.city_pages:
            print("No enhanced city pages configured")
            return generated_files
            
        for city_page in self.config.city_pages:
            try:
                file_path = self.generate_city_page(city_page, output_dir)
                generated_files.append(file_path)
                print(f"Generated enhanced city page: {city_page.city_name}")
            except Exception as e:
                print(f"Error generating enhanced page for {city_page.city_name}: {e}")
                
        return generated_files
    
    def create_sample_city_page(self, city_name: str, state: str = "") -> CityPageConfig:
        """Create a sample city page configuration for testing"""
        return CityPageConfig(
            city_name=city_name,
            state=state,
            meta_description=f"{self.config.business.business_name} serves {city_name} with custom {self.config.business.industry.lower()} services. Professional craftsmanship and local expertise.",
            primary_keyword=f"custom {self.config.business.industry.lower()}",
            secondary_keywords=[city_name.lower(), f"{self.config.business.industry.lower()} services", "local business"],
            about_city=f"{city_name} is a vibrant community known for its architectural diversity and rich heritage. " +
                      f"The city presents unique opportunities and challenges for {self.config.business.industry.lower()} projects, " +
                      f"requiring specialized knowledge of local building codes, climate considerations, and architectural styles. " +
                      f"Our team at {self.config.business.business_name} understands these local nuances and delivers solutions " +
                      f"that complement {city_name}'s distinctive character while meeting the highest standards of quality and durability.",
            city_image=CityImageConfig(
                image_url="images/placeholder-city.jpg",
                alt_text=f"{city_name} skyline and landmarks",
                caption=f"Caption: {city_name} cityscape highlighting local architecture.",
                credit="Image credit to be added when actual image is sourced",
                source="Wikipedia"
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
            featured_products=[service.slug for service in self.config.services[:7]],
            city_map_embed=f"https://www.google.com/maps?q={city_name},{state}&output=embed",
            service_area_note=f"Service Area: {city_name} and surrounding communities."
        )
    
    def _build_template_context(self, city_page: CityPageConfig) -> Dict[str, Any]:
        """Build template context with all necessary data"""
        return {
            # City page data
            'city_page': city_page,
            
            # Business data
            'business': self.config.business,
            'contact': self.config.contact,
            'branding': self.config.branding,
            
            # Content data
            'services': self.config.services,
            'products': self.config.products,
            'social_media': self.config.social_media,
            
            # Page metadata
            'page_url': f"/{city_page.slug}/",
            'current_year': 2025,
            
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
                'street': self.config.contact.address.street,
                'city': self.config.contact.address.city,
                'state': self.config.contact.address.state,
                'zip': self.config.contact.address.zip_code,
                'country': self.config.contact.address.country
            }
        }
    
    def _generate_sample_seo_content(self, city_name: str) -> str:
        """Generate sample 800+ word SEO content for city pages"""
        business_name = self.config.business.business_name
        industry = self.config.business.industry.lower()
        
        # Get service names for content
        service_list = ", ".join([service.name.lower() for service in self.config.services[:5]]) if self.config.services else f"{industry} services"
        
        content = f"""<p>When {city_name} residents and businesses need professional {industry} services, they turn to {business_name}. Our experienced team provides comprehensive solutions tailored to the unique needs of the {city_name} area, combining industry expertise with local knowledge to deliver exceptional results.</p>

<p>Our approach begins with understanding your specific requirements and the local context of {city_name}. We take into account factors such as local building codes, architectural styles, climate considerations, and community standards. This attention to detail ensures that our {industry} solutions not only meet your functional needs but also complement the character and aesthetics of {city_name}.</p>

<p>The services we provide in {city_name} include {service_list}. Each project receives our full attention, with skilled craftspeople who understand the importance of quality workmanship and attention to detail. We're committed to using the finest materials and proven techniques to ensure lasting results that stand up to {city_name}'s climate and environmental conditions.</p>

<p>What sets {business_name} apart in the {city_name} market is our commitment to customer satisfaction and our deep understanding of local needs. We've built our reputation by consistently delivering projects on time, within budget, and to the highest standards of quality. Our team takes pride in being responsive to our clients' needs and maintaining clear communication throughout every project.</p>

<p>For {city_name} homeowners, we understand that your property is one of your most important investments. That's why we approach every residential project with the care and attention it deserves. From initial consultation through project completion, we work closely with you to ensure that the final result exceeds your expectations and adds value to your property.</p>

<p>Commercial clients in {city_name} appreciate our professional approach and ability to work within their operational requirements. We understand that business continuity is crucial, and we plan our projects to minimize disruption while delivering superior results. Our experience with various commercial applications ensures that we can handle projects of any scale or complexity.</p>

<p>The {city_name} area presents unique opportunities and challenges that require specialized knowledge and experience. Our team has extensive experience working in this region and understands the local factors that can impact {industry} projects. This expertise allows us to anticipate potential issues and implement solutions that ensure project success.</p>

<p>Quality materials are essential to the longevity and performance of any {industry} project. We source our materials from trusted suppliers and manufacturers, ensuring that every component meets our high standards for durability and performance. In {city_name}'s climate, this attention to material quality is especially important for ensuring long-term satisfaction and value.</p>

<p>Safety is always our top priority on every {city_name} project. Our team follows strict safety protocols and maintains current certifications and training. We carry comprehensive insurance coverage to protect our clients and our workers, providing peace of mind throughout the project process.</p>

<p>Environmental responsibility is increasingly important to {city_name} residents and businesses. We're committed to sustainable practices and can help you choose options that minimize environmental impact while delivering superior performance. From material selection to waste management, we consider the environmental implications of every decision.</p>

<p>Customer service excellence is at the heart of everything we do in {city_name}. We believe that clear communication, reliable scheduling, and attention to detail are just as important as technical expertise. Our goal is to make the entire experience positive and stress-free for our clients.</p>

<p>Whether you're planning a small residential project or a large commercial installation in {city_name}, {business_name} has the experience, expertise, and commitment to excellence you need for success. We invite you to contact us today to discuss your project requirements and learn how we can help bring your vision to life.</p>

<p>Ready to get started with your {industry} project in {city_name}? Contact {business_name} today for a free consultation and detailed quote. We look forward to the opportunity to serve you and demonstrate why we're the trusted choice for {city_name} area clients seeking professional {industry} services.</p>"""
        
        return content
    
    def migrate_legacy_cities(self) -> List[CityPageConfig]:
        """Migrate legacy target_cities to enhanced city pages"""
        migrated_pages = []
        
        if not self.config.target_cities:
            return migrated_pages
            
        for city_str in self.config.target_cities:
            # Parse city and state from string
            parts = city_str.split(',')
            city_name = parts[0].strip()
            state = parts[1].strip() if len(parts) > 1 else ""
            
            # Check if already exists in city_pages
            if not any(cp.city_name.lower() == city_name.lower() for cp in self.config.city_pages):
                city_page = self.create_sample_city_page(city_name, state)
                migrated_pages.append(city_page)
                
        return migrated_pages