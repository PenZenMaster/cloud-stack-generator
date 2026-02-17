"""
City Field Content Generator
Path: E:/projects/cloud-stack-generator/src/core/generators/content/city_field_content_generator.py

Description:
Generates AI-powered content for individual city page SEO fields in the Cities Tab UI.
Provides targeted content generation for neighborhoods, pain points, case studies, and FAQs.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-20

Last Modified Date:
2025-11-20

Comments:
* v1.00 - Initial creation for Cities Tab UI field generation
"""

from typing import Optional, TYPE_CHECKING
from src.core.utils.logger import get_logger

logger = get_logger(__name__)

if TYPE_CHECKING:
    from ...services.ai_content_service import AIContentService


class CityFieldContentGenerator:
    """
    Generates AI-powered content for city page SEO fields.

    Provides methods to generate content for Cities Tab form fields:
    - City neighborhoods and landmarks descriptions
    - Local pain points and seasonal factors
    - Micro case studies and examples
    - City-specific FAQ questions
    """

    def __init__(self, ai_service: Optional["AIContentService"] = None):
        """
        Initialize the city field content generator.

        Args:
            ai_service: AI content service instance for generation
        """
        self.ai_service = ai_service
        self.use_ai = ai_service is not None and ai_service.is_available()

    def generate_neighborhoods_description(
        self,
        city_name: str,
        state: str,
        business_name: str,
        industry: str,
        existing_content: str = ""
    ) -> Optional[str]:
        """
        Generate neighborhoods and landmarks description for a city.

        Args:
            city_name: Name of the city
            state: State where city is located
            business_name: Name of the business
            industry: Business industry/type
            existing_content: Existing content to enhance (optional)

        Returns:
            Generated content or None if generation fails
        """
        if not self.use_ai:
            return None

        context = {
            "city_name": city_name,
            "state": state,
            "business_name": business_name,
            "industry": industry,
            "existing_content": existing_content
        }

        prompt = self._build_neighborhoods_prompt(context)

        try:
            response = self.ai_service._call_openai(prompt)
            return response.strip() if response else None
        except Exception as e:
            logger.error(f"Error generating neighborhoods description: {e}")
            return None

    def generate_pain_points(
        self,
        city_name: str,
        state: str,
        business_name: str,
        industry: str,
        existing_content: str = ""
    ) -> Optional[str]:
        """
        Generate local pain points and seasonal factors for a city.

        Args:
            city_name: Name of the city
            state: State where city is located
            business_name: Name of the business
            industry: Business industry/type
            existing_content: Existing content to enhance (optional)

        Returns:
            Generated content or None if generation fails
        """
        if not self.use_ai:
            return None

        context = {
            "city_name": city_name,
            "state": state,
            "business_name": business_name,
            "industry": industry,
            "existing_content": existing_content
        }

        prompt = self._build_pain_points_prompt(context)

        try:
            response = self.ai_service._call_openai(prompt)
            return response.strip() if response else None
        except Exception as e:
            logger.error(f"Error generating pain points: {e}")
            return None

    def generate_case_studies(
        self,
        city_name: str,
        state: str,
        business_name: str,
        industry: str,
        existing_content: str = ""
    ) -> Optional[str]:
        """
        Generate micro case studies and examples for a city.

        Args:
            city_name: Name of the city
            state: State where city is located
            business_name: Name of the business
            industry: Business industry/type
            existing_content: Existing content to enhance (optional)

        Returns:
            Generated content or None if generation fails
        """
        if not self.use_ai:
            return None

        context = {
            "city_name": city_name,
            "state": state,
            "business_name": business_name,
            "industry": industry,
            "existing_content": existing_content
        }

        prompt = self._build_case_studies_prompt(context)

        try:
            response = self.ai_service._call_openai(prompt)
            return response.strip() if response else None
        except Exception as e:
            logger.error(f"Error generating case studies: {e}")
            return None

    def generate_local_faq(
        self,
        city_name: str,
        state: str,
        business_name: str,
        industry: str,
        neighborhoods: str = "",
        pain_points: str = "",
        existing_content: str = ""
    ) -> Optional[str]:
        """
        Generate city-specific FAQ questions.

        Args:
            city_name: Name of the city
            state: State where city is located
            business_name: Name of the business
            industry: Business industry/type
            neighborhoods: City neighborhoods content (for context)
            pain_points: Pain points content (for context)
            existing_content: Existing FAQ content to enhance (optional)

        Returns:
            Generated FAQ questions (one per line) or None if generation fails
        """
        if not self.use_ai:
            return None

        context = {
            "city_name": city_name,
            "state": state,
            "business_name": business_name,
            "industry": industry,
            "neighborhoods": neighborhoods,
            "pain_points": pain_points,
            "existing_content": existing_content
        }

        prompt = self._build_local_faq_prompt(context)

        try:
            response = self.ai_service._call_openai(prompt)
            return response.strip() if response else None
        except Exception as e:
            logger.error(f"Error generating local FAQ: {e}")
            return None

    def _build_neighborhoods_prompt(self, context: dict) -> str:
        """Build prompt for neighborhoods and landmarks generation."""
        prompt = f"""Generate a concise description of key neighborhoods and landmarks for {context['city_name']}, {context['state']}.

Business: {context['business_name']}
Industry: {context['industry']}

Write a 2-3 sentence overview mentioning major neighborhoods, landmarks, and districts that {context['business_name']} serves. Focus on well-known areas that locals and potential customers would recognize.

Examples:
- "Downtown Detroit, Corktown, Midtown, Belle Isle Park, Eastern Market, New Center"
- "Historic downtown, University District, Tech Corridor, Riverfront area"

Keep it factual, concise, and locally relevant. Separate areas with commas."""

        if context.get('existing_content'):
            prompt += f"\n\nExisting content to enhance:\n{context['existing_content']}"

        return prompt

    def _build_pain_points_prompt(self, context: dict) -> str:
        """Build prompt for pain points and seasonal factors generation."""
        prompt = f"""Generate local pain points and seasonal factors that affect {context['industry']} services in {context['city_name']}, {context['state']}.

Business: {context['business_name']}
Industry: {context['industry']}

Write 2-3 sentences about:
- Weather-related challenges (winter, summer, storms)
- Seasonal service demand patterns
- Local infrastructure issues (construction, traffic, parking)
- Regional factors that create service needs

Make it specific to {context['city_name']} and relevant to {context['industry']} services.

Example format:
"Winter weather in Detroit creates challenges with freezing temperatures and heavy snowfall from November through March. Road construction peaks during summer months, affecting access and scheduling. Spring flooding along the Detroit River can impact waterfront properties and infrastructure."

Keep it professional and solution-oriented."""

        if context.get('existing_content'):
            prompt += f"\n\nExisting content to enhance:\n{context['existing_content']}"

        return prompt

    def _build_case_studies_prompt(self, context: dict) -> str:
        """Build prompt for micro case studies generation."""
        prompt = f"""Generate a brief micro case study example for {context['business_name']} services in {context['city_name']}, {context['state']}.

Business: {context['business_name']}
Industry: {context['industry']}

Write 2-3 sentences about a realistic project or service example that demonstrates:
- Type of project/service provided
- Location within the city (neighborhood or district)
- Brief outcome or result

Make it specific enough to be believable but generic enough to be broadly representative. Focus on local relevance to {context['city_name']}.

Example format:
"Recently completed a historic downtown renovation project in Detroit's Corktown district, restoring original brick facades while modernizing infrastructure. The project preserved the neighborhood's character while meeting modern building codes."

Keep it professional and results-oriented."""

        if context.get('existing_content'):
            prompt += f"\n\nExisting content to enhance:\n{context['existing_content']}"

        return prompt

    def _build_local_faq_prompt(self, context: dict) -> str:
        """Build prompt for local FAQ generation."""
        neighborhoods = context.get('neighborhoods', '')
        pain_points = context.get('pain_points', '')

        prompt = f"""Generate 4-6 city-specific FAQ questions for {context['business_name']} in {context['city_name']}, {context['state']}.

Business: {context['business_name']}
Industry: {context['industry']}"""

        if neighborhoods:
            prompt += f"\nAreas served: {neighborhoods}"

        if pain_points:
            prompt += f"\nLocal factors: {pain_points}"

        prompt += f"""

Generate FAQ questions (one per line) that are specific to {context['city_name']}. Questions should address:
- Service coverage in specific neighborhoods
- Response times in the city
- Local permits or regulations
- Seasonal considerations
- Parking, access, or local logistics

Format: One question per line, no numbering or bullets.

Example format:
Do you serve Detroit's downtown area?
What are your typical response times in Detroit?
Do you handle winter weather emergencies?
Is parking available for service visits in Midtown?

Keep questions natural and conversational."""

        if context.get('existing_content'):
            prompt += f"\n\nExisting questions to enhance:\n{context['existing_content']}"

        return prompt
