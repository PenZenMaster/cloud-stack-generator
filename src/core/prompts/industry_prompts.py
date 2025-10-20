"""
Industry-Specific Prompt Templates
Path: E:/projects/cloud-stack-generator/src/core/prompts/industry_prompts.py

Description:
Customized AI prompts for different business industries. Provides industry-specific
tone, focus areas, keywords, and call-to-action emphasis for optimal content generation.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-19

Last Modified Date:
2025-10-19

Comments:
* v1.00 - Initial creation with prompts for 6+ industries
"""

from typing import Dict, Any, List


class IndustryPromptManager:
    """
    Manage industry-specific prompt templates for AI content generation.

    Provides customized prompts that adapt tone, keywords, focus areas,
    and call-to-action based on the business industry.
    """

    # Industry-specific prompt configurations
    INDUSTRY_PROMPTS = {
        "Plumbing": {
            "tone": "professional and trustworthy",
            "focus_areas": [
                "24/7 Emergency service availability",
                "Licensed and insured status",
                "Years of experience in plumbing",
                "Quality workmanship guarantee",
                "Competitive pricing and free estimates"
            ],
            "keywords": [
                "plumbing",
                "licensed plumber",
                "emergency plumbing",
                "pipe repair",
                "drain cleaning",
                "water heater",
                "leak detection",
                "sewer line",
                "plumbing installation"
            ],
            "cta_emphasis": "24/7 emergency service and free estimates",
            "trust_signals": [
                "Licensed and insured",
                "Background-checked technicians",
                "Upfront pricing",
                "Warranty on all work"
            ]
        },

        "HVAC": {
            "tone": "knowledgeable and reliable",
            "focus_areas": [
                "Energy efficiency and cost savings",
                "Indoor air quality improvement",
                "Comfort solutions year-round",
                "Preventive maintenance programs",
                "Licensed and certified technicians"
            ],
            "keywords": [
                "HVAC",
                "heating",
                "cooling",
                "air conditioning",
                "furnace",
                "heat pump",
                "ductwork",
                "AC repair",
                "HVAC installation",
                "thermostat"
            ],
            "cta_emphasis": "Schedule maintenance and save on energy costs",
            "trust_signals": [
                "NATE-certified technicians",
                "Energy Star partner",
                "Satisfaction guaranteed",
                "Same-day service available"
            ]
        },

        "Electrical": {
            "tone": "safety-focused and professional",
            "focus_areas": [
                "Safety compliance and inspections",
                "National Electric Code compliance",
                "Licensed master electricians",
                "Emergency electrical repairs",
                "Energy-efficient upgrades"
            ],
            "keywords": [
                "electrical",
                "electrician",
                "wiring",
                "panel upgrade",
                "lighting",
                "electrical safety",
                "surge protection",
                "electrical repair",
                "circuit breaker",
                "outlet installation"
            ],
            "cta_emphasis": "Safety inspections and 24/7 emergency service",
            "trust_signals": [
                "Licensed electricians",
                "Code compliant work",
                "Safety inspections included",
                "Fully insured"
            ]
        },

        "Roofing": {
            "tone": "dependable and detail-oriented",
            "focus_areas": [
                "Lifetime warranty protection",
                "Quality roofing materials",
                "Expert installation and repair",
                "Storm damage assessment",
                "Free roof inspections"
            ],
            "keywords": [
                "roofing",
                "roof repair",
                "roof replacement",
                "shingles",
                "leak repair",
                "storm damage",
                "roof inspection",
                "roofing contractor",
                "roof installation",
                "gutter repair"
            ],
            "cta_emphasis": "Free roof inspection and lifetime warranties",
            "trust_signals": [
                "Manufacturer certified",
                "Lifetime warranties",
                "Insurance claim assistance",
                "Local roofing experts"
            ]
        },

        "Landscaping": {
            "tone": "creative and environmental-conscious",
            "focus_areas": [
                "Custom landscape design",
                "Sustainable practices",
                "Seasonal maintenance programs",
                "Property value enhancement",
                "Professional horticulture expertise"
            ],
            "keywords": [
                "landscaping",
                "lawn care",
                "landscape design",
                "irrigation",
                "hardscaping",
                "tree service",
                "lawn maintenance",
                "landscape installation",
                "outdoor living",
                "garden design"
            ],
            "cta_emphasis": "Transform your outdoor space with professional design",
            "trust_signals": [
                "Licensed landscapers",
                "Design consultation included",
                "Eco-friendly practices",
                "Satisfaction guarantee"
            ]
        },

        "Portable Toilet Supplier": {
            "tone": "professional and service-focused",
            "focus_areas": [
                "Highest cleanliness standards",
                "Timely delivery and service",
                "Event support expertise",
                "Construction site solutions",
                "ADA-compliant units available"
            ],
            "keywords": [
                "portable toilets",
                "porta potty",
                "restroom rental",
                "construction restrooms",
                "event facilities",
                "sanitation services",
                "portable restrooms",
                "porta john",
                "toilet rental",
                "restroom trailer"
            ],
            "cta_emphasis": "Clean, reliable portable restroom solutions for any event",
            "trust_signals": [
                "Regularly serviced units",
                "On-time delivery guaranteed",
                "Event planning support",
                "ADA-compliant options"
            ]
        },

        "Automotive": {
            "tone": "trustworthy and technically proficient",
            "focus_areas": [
                "ASE-certified technicians",
                "Diagnostic expertise",
                "Quality parts and service",
                "Warranty on repairs",
                "Honest pricing"
            ],
            "keywords": [
                "auto repair",
                "car service",
                "mechanic",
                "oil change",
                "brake repair",
                "transmission",
                "engine repair",
                "automotive service",
                "auto maintenance"
            ],
            "cta_emphasis": "Schedule service today with ASE-certified technicians",
            "trust_signals": [
                "ASE-certified",
                "Warranty on repairs",
                "Honest estimates",
                "Loaner vehicles available"
            ]
        },

        "General": {
            "tone": "professional and customer-focused",
            "focus_areas": [
                "Quality service delivery",
                "Customer satisfaction",
                "Experienced professionals",
                "Competitive pricing",
                "Reliable and timely service"
            ],
            "keywords": [],
            "cta_emphasis": "Contact us for professional service",
            "trust_signals": [
                "Experienced professionals",
                "Customer satisfaction guaranteed",
                "Licensed and insured",
                "Competitive pricing"
            ]
        }
    }

    @classmethod
    def get_industry_config(cls, industry: str) -> Dict[str, Any]:
        """
        Get prompt configuration for a specific industry.

        Args:
            industry: Industry name

        Returns:
            Industry-specific configuration dictionary
        """
        return cls.INDUSTRY_PROMPTS.get(industry, cls.INDUSTRY_PROMPTS["General"])

    @classmethod
    def get_available_industries(cls) -> List[str]:
        """
        Get list of industries with custom prompt configurations.

        Returns:
            List of industry names
        """
        return list(cls.INDUSTRY_PROMPTS.keys())

    @classmethod
    def build_home_page_prompt(cls, context: Dict[str, Any]) -> str:
        """
        Build industry-specific home page prompt.

        Args:
            context: Business context including:
                - business_name: str
                - industry: str
                - company_overview: str (optional)
                - services: List[Dict]
                - products: List[Dict]
                - why_choose_us: List[str] (optional)

        Returns:
            Customized prompt string for home page generation
        """
        industry = context.get('industry', 'General')
        industry_config = cls.get_industry_config(industry)

        # Extract basic info
        business_name = context['business_name']
        services_list = "\n".join([
            f"- {s['name']}: {s['description']}" for s in context.get('services', [])
        ]) if context.get('services') else "General services"

        products_list = "\n".join([
            f"- {p['name']}: {p['description']}" for p in context.get('products', [])
        ]) if context.get('products') else "No specific products"

        # Build focus areas section
        focus_areas = "\n".join([f"- {area}" for area in industry_config['focus_areas']])

        # Build keywords section
        keywords = ", ".join(industry_config['keywords']) if industry_config['keywords'] else "industry-specific terms"

        # Build trust signals
        trust_signals = "\n".join([f"- {signal}" for signal in industry_config['trust_signals']])

        prompt = f"""You are a professional web content writer specializing in {industry} businesses.

Generate compelling, SEO-optimized HTML content for a home page with these specifications:

BUSINESS INFORMATION:
- Business Name: {business_name}
- Industry: {industry}
- Tone: {industry_config['tone']}
- Company Overview: {context.get('company_overview', 'Trusted provider of quality services')}
- Years in Business: {context.get('years_in_business', 'Many years')} of experience

SERVICES:
{services_list}

PRODUCTS:
{products_list}

INDUSTRY FOCUS AREAS (emphasize these):
{focus_areas}

TRUST SIGNALS (include these):
{trust_signals}

SEO KEYWORDS (use naturally throughout):
{keywords}

CALL-TO-ACTION EMPHASIS:
{industry_config['cta_emphasis']}

REQUIREMENTS:
1. Generate ONLY the HTML content sections (no <html>, <head>, or <body> tags)
2. Use semantic HTML5 with proper section tags
3. Maintain a {industry_config['tone']} tone throughout
4. Include these sections in order:
   - Hero section with compelling headline focusing on {industry_config['cta_emphasis']}
   - About section introducing the business and building trust
   - Why Choose Us section highlighting: {", ".join(industry_config['focus_areas'][:3])}
   - Services/Products showcase with clear descriptions
   - Trust signals section featuring: {", ".join(industry_config['trust_signals'][:2])}
   - Strong call-to-action section
5. Use appropriate CSS classes: hero, hero-overlay, hero-content, about-section, why-choose-us, services-grid, trust-signals
6. Naturally incorporate these SEO keywords: {keywords}
7. Content should be 600-800 words total
8. Include 2-3 clear calls-to-action throughout
9. Emphasize trust signals and credibility specific to {industry}
10. Use proper heading hierarchy (h1, h2, h3)

OUTPUT FORMAT:
Return ONLY the HTML sections, starting with <section> tags. No explanatory text before or after."""

        return prompt

    @classmethod
    def build_city_page_prompt(cls, context: Dict[str, Any]) -> str:
        """
        Build industry-specific city page prompt.

        Args:
            context: Business and city context including:
                - business_name: str
                - industry: str
                - city: str
                - state: str (optional)
                - services: List[Dict]
                - company_overview: str (optional)

        Returns:
            Customized prompt string for city page generation
        """
        industry = context.get('industry', 'General')
        industry_config = cls.get_industry_config(industry)
        city = context['city']
        state = context.get('state', '')

        # Build keywords with city localization
        base_keywords = industry_config['keywords'][:5]  # Top 5 keywords
        local_keywords = [f"{city} {kw}" for kw in base_keywords] if base_keywords else [city]
        keywords = ", ".join(local_keywords)

        # Build services list
        services_list = "\n".join([
            f"- {s['name']}: {s['description']}" for s in context.get('services', [])
        ]) if context.get('services') else "Professional services"

        # Location string
        location = f"{city}, {state}" if state else city

        prompt = f"""You are a professional web content writer specializing in local {industry} businesses.

Generate SEO-optimized, localized HTML content for a {location}-specific service page:

BUSINESS INFORMATION:
- Business Name: {context['business_name']}
- Industry: {industry}
- Location: {location}
- Tone: {industry_config['tone']}
- Service Area: Proudly serving {city} and surrounding areas

SERVICES PROVIDED IN {city.upper()}:
{services_list}

LOCAL SEO KEYWORDS (use naturally):
{keywords}

INDUSTRY FOCUS AREAS FOR {city.upper()}:
{chr(10).join([f"- {area}" for area in industry_config['focus_areas']])}

LOCAL TRUST SIGNALS:
- Local {city} business
- Serving the {city} community
- {industry_config['trust_signals'][0]}
- Fast response times in {city}

REQUIREMENTS:
1. Generate ONLY the HTML content sections (no <html>, <head>, or <body> tags)
2. Emphasize LOCAL service and expertise in {city}
3. Include these sections:
   - Hero section highlighting {industry} services in {city}
   - Local expertise section explaining why we're the best choice in {city}
   - Services section tailored for {city} residents and businesses
   - Why choose us for {city} services
   - Local trust signals and community commitment
   - Call-to-action with {city} focus
4. Use CSS classes: hero, hero-overlay, hero-text, content, services-grid, local-expertise
5. Naturally incorporate location keywords: {keywords}
6. Also use these location terms naturally: {city}, local, area, community, neighborhood
7. Maintain {industry_config['tone']} tone
8. Content should be 400-600 words
9. Include strong local call-to-action
10. Emphasize quick response time and local availability
11. Use proper heading hierarchy (h2, h3, h4)

OUTPUT FORMAT:
Return ONLY the HTML sections, starting with <section> tags. No explanatory text before or after."""

        return prompt
