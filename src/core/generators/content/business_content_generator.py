"""
Business Content Generator
Path: E:/projects/cloud-stack-generator/src/core/generators/content/business_content_generator.py

Description:
Generates AI-powered content for business information fields including business
description, company overview, mission statement, service guarantee, and service
area description. Integrates with AIContentService for dynamic content generation.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-20

Last Modified Date:
2025-11-20

Comments:
* v1.00 - Initial creation for Business Info AI content generation
"""

import logging
from typing import TYPE_CHECKING, Optional, Dict, Any

if TYPE_CHECKING:
    from ...config.models import ClientConfig
    from ...services.ai_content_service import AIContentService

logger = logging.getLogger(__name__)


class BusinessContentGenerator:
    """
    Generates AI-powered content for business information fields.

    Supports generating:
    - Business Description
    - Company Overview
    - Mission Statement
    - Service Guarantee
    - Service Area Description
    """

    def __init__(self, ai_service: Optional["AIContentService"] = None):
        """
        Initialize the business content generator.

        Args:
            ai_service: AI content service for dynamic generation
        """
        self.ai_service = ai_service
        self.use_ai = ai_service is not None and ai_service.is_available()

    def generate_business_description(
        self,
        business_name: str,
        industry: str,
        existing_description: str = ""
    ) -> Optional[str]:
        """
        Generate a business description.

        Args:
            business_name: Name of the business
            industry: Business industry
            existing_description: Existing description to enhance (optional)

        Returns:
            Generated business description or None if AI unavailable
        """
        if not self.use_ai:
            logger.warning("AI service not available for business description generation")
            return None

        context = {
            "business_name": business_name,
            "industry": industry,
            "existing_description": existing_description
        }

        prompt = self._build_business_description_prompt(context)

        try:
            response = self.ai_service._call_openai(prompt)
            content = response.strip()
            logger.info(f"Generated business description ({len(content)} characters)")
            return content
        except Exception as e:
            logger.error(f"Failed to generate business description: {e}")
            return None

    def generate_company_overview(
        self,
        business_name: str,
        industry: str,
        business_description: str = "",
        years_in_business: str = ""
    ) -> Optional[str]:
        """
        Generate a company overview section.

        Args:
            business_name: Name of the business
            industry: Business industry
            business_description: Brief business description
            years_in_business: How long business has been operating

        Returns:
            Generated company overview or None if AI unavailable
        """
        if not self.use_ai:
            logger.warning("AI service not available for company overview generation")
            return None

        context = {
            "business_name": business_name,
            "industry": industry,
            "business_description": business_description,
            "years_in_business": years_in_business
        }

        prompt = self._build_company_overview_prompt(context)

        try:
            response = self.ai_service._call_openai(prompt)
            content = response.strip()
            logger.info(f"Generated company overview ({len(content)} characters)")
            return content
        except Exception as e:
            logger.error(f"Failed to generate company overview: {e}")
            return None

    def generate_mission_statement(
        self,
        business_name: str,
        industry: str,
        business_description: str = ""
    ) -> Optional[str]:
        """
        Generate a mission statement.

        Args:
            business_name: Name of the business
            industry: Business industry
            business_description: Brief business description

        Returns:
            Generated mission statement or None if AI unavailable
        """
        if not self.use_ai:
            logger.warning("AI service not available for mission statement generation")
            return None

        context = {
            "business_name": business_name,
            "industry": industry,
            "business_description": business_description
        }

        prompt = self._build_mission_statement_prompt(context)

        try:
            response = self.ai_service._call_openai(prompt)
            content = response.strip()
            logger.info(f"Generated mission statement ({len(content)} characters)")
            return content
        except Exception as e:
            logger.error(f"Failed to generate mission statement: {e}")
            return None

    def generate_service_guarantee(
        self,
        business_name: str,
        industry: str,
        business_description: str = ""
    ) -> Optional[str]:
        """
        Generate a service guarantee.

        Args:
            business_name: Name of the business
            industry: Business industry
            business_description: Brief business description

        Returns:
            Generated service guarantee or None if AI unavailable
        """
        if not self.use_ai:
            logger.warning("AI service not available for service guarantee generation")
            return None

        context = {
            "business_name": business_name,
            "industry": industry,
            "business_description": business_description
        }

        prompt = self._build_service_guarantee_prompt(context)

        try:
            response = self.ai_service._call_openai(prompt)
            content = response.strip()
            logger.info(f"Generated service guarantee ({len(content)} characters)")
            return content
        except Exception as e:
            logger.error(f"Failed to generate service guarantee: {e}")
            return None

    def generate_service_area_description(
        self,
        business_name: str,
        industry: str,
        service_areas: list = None
    ) -> Optional[str]:
        """
        Generate a service area description.

        Args:
            business_name: Name of the business
            industry: Business industry
            service_areas: List of service area names (cities/regions)

        Returns:
            Generated service area description or None if AI unavailable
        """
        if not self.use_ai:
            logger.warning("AI service not available for service area description generation")
            return None

        context = {
            "business_name": business_name,
            "industry": industry,
            "service_areas": service_areas or []
        }

        prompt = self._build_service_area_description_prompt(context)

        try:
            response = self.ai_service._call_openai(prompt)
            content = response.strip()
            logger.info(f"Generated service area description ({len(content)} characters)")
            return content
        except Exception as e:
            logger.error(f"Failed to generate service area description: {e}")
            return None

    def _build_business_description_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for business description generation"""
        business_name = context['business_name']
        industry = context['industry']
        existing = context.get('existing_description', '')

        prompt = f"""You are a professional business copywriter.

Generate a compelling business description for the following business:

BUSINESS INFORMATION:
- Business Name: {business_name}
- Industry: {industry}
{f'- Current Description: {existing}' if existing else ''}

REQUIREMENTS:
1. Write a concise, engaging description (2-3 sentences, 100-200 characters)
2. Highlight what makes this business unique
3. Focus on value proposition and expertise
4. Use professional, confident tone
5. Include industry-specific keywords naturally
6. Make it suitable for website headers and meta descriptions

OUTPUT FORMAT:
Return ONLY the business description text. No explanations, no quotes, no prefixes."""

        return prompt

    def _build_company_overview_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for company overview generation"""
        business_name = context['business_name']
        industry = context['industry']
        business_description = context.get('business_description', '')
        years = context.get('years_in_business', '')

        prompt = f"""You are a professional business copywriter specializing in About sections.

Generate a comprehensive company overview for the following business:

BUSINESS INFORMATION:
- Business Name: {business_name}
- Industry: {industry}
{f'- Years in Business: {years}' if years else ''}
{f'- Brief Description: {business_description}' if business_description else ''}

REQUIREMENTS:
1. Write 2-3 paragraphs (200-300 words total)
2. Tell the company story - history, expertise, values
3. Emphasize trust, reliability, and quality
4. Include specific industry expertise
5. Mention commitment to customers
6. Professional yet approachable tone
7. Suitable for "About Us" section

OUTPUT FORMAT:
Return ONLY the company overview text. No explanations, no HTML tags, no headings."""

        return prompt

    def _build_mission_statement_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for mission statement generation"""
        business_name = context['business_name']
        industry = context['industry']
        business_description = context.get('business_description', '')

        prompt = f"""You are a professional business copywriter specializing in mission statements.

Generate a compelling mission statement for the following business:

BUSINESS INFORMATION:
- Business Name: {business_name}
- Industry: {industry}
{f'- Brief Description: {business_description}' if business_description else ''}

REQUIREMENTS:
1. Write 2-3 sentences (50-100 words)
2. Articulate the company's core purpose
3. Focus on customer value and impact
4. Inspiring yet realistic tone
5. Industry-specific language
6. Forward-looking perspective

OUTPUT FORMAT:
Return ONLY the mission statement text. No explanations, no prefixes like "Our mission is:"."""

        return prompt

    def _build_service_guarantee_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for service guarantee generation"""
        business_name = context['business_name']
        industry = context['industry']
        business_description = context.get('business_description', '')

        prompt = f"""You are a professional business copywriter specializing in guarantees and trust signals.

Generate a compelling service guarantee for the following business:

BUSINESS INFORMATION:
- Business Name: {business_name}
- Industry: {industry}
{f'- Brief Description: {business_description}' if business_description else ''}

REQUIREMENTS:
1. Write 2-3 sentences (50-100 words)
2. Emphasize quality, reliability, satisfaction
3. Build trust and confidence
4. Include industry-specific assurances
5. Professional and confident tone
6. Avoid unrealistic promises
7. Focus on commitment to excellence

OUTPUT FORMAT:
Return ONLY the guarantee text. No explanations, no prefixes."""

        return prompt

    def _build_service_area_description_prompt(self, context: Dict[str, Any]) -> str:
        """Build prompt for service area description generation"""
        business_name = context['business_name']
        industry = context['industry']
        service_areas = context.get('service_areas', [])

        areas_text = ', '.join(service_areas[:5]) if service_areas else "the local area and surrounding communities"

        prompt = f"""You are a professional business copywriter specializing in local service descriptions.

Generate a service area description for the following business:

BUSINESS INFORMATION:
- Business Name: {business_name}
- Industry: {industry}
- Service Areas: {areas_text}

REQUIREMENTS:
1. Write 2-3 sentences (50-100 words)
2. Highlight local presence and availability
3. Emphasize community commitment
4. Include geographic coverage naturally
5. Professional yet friendly tone
6. Focus on accessibility and responsiveness

OUTPUT FORMAT:
Return ONLY the service area description text. No explanations."""

        return prompt
