"""
Filename: people_also_ask_api.py
Path: E:\\projects\\cloud-stack-generator\\src\\core\\utils\\people_also_ask_api.py
Description: People Also Ask (PAA) API integration for FAQ content generation

Provides mock implementation for generating Google People Also Ask-style FAQ content
based on primary keywords and city-specific context.

Version: 1.0.0
Date: 2025-09-04
Author: Cloud Stack Generator Team
"""

import re
from typing import List, Dict
import random


class PeopleAlsoAskAPI:
    """People Also Ask API integration for FAQ content generation"""
    
    def __init__(self):
        """Initialize PAA API client"""
        self.base_questions = {
            "architectural metal fabrication": [
                "What types of architectural metal fabrication services are available?",
                "How much does custom architectural metalwork cost?",
                "What materials are used in architectural metal fabrication?",
                "How long does a custom metalwork project take?",
                "What is the difference between architectural and structural metalwork?"
            ],
            "metal fabrication": [
                "What is metal fabrication used for?",
                "What are the most common metal fabrication techniques?",
                "How do I choose the right metal fabrication company?",
                "What metals are best for outdoor applications?",
                "Can metal fabrication work be customized for my project?"
            ],
            "custom metal work": [
                "What can be made with custom metal work?",
                "How is custom metalwork priced?",
                "What design options are available for custom metal projects?",
                "How durable is custom metalwork?",
                "What maintenance does custom metalwork require?"
            ],
            "copper fabrication": [
                "Why is copper popular for architectural projects?",
                "How does copper patina affect the appearance?",
                "Is copper fabrication more expensive than other metals?",
                "What are the benefits of copper roofing elements?",
                "How long does copper architectural work last?"
            ]
        }
        
        # Question templates that can be customized per city
        self.city_question_templates = [
            "What are the building codes for {service} in {city}?",
            "Are there local contractors for {service} in {city}?", 
            "What permits are needed for {service} projects in {city}?",
            "How much does {service} cost in {city}?",
            "What is the best time of year for {service} in {city}?"
        ]
    
    def extract_service_from_keyword(self, primary_keyword: str) -> str:
        """
        Extract service type from primary keyword for FAQ generation
        
        Args:
            primary_keyword: Primary keyword like "architectural metal fabrication Chicago"
            
        Returns:
            Service type for FAQ questions
        """
        # Remove city names from the keyword
        keyword_clean = re.sub(r'\b(Chicago|Illinois|IL)\b', '', primary_keyword, flags=re.IGNORECASE).strip()
        
        # Map keywords to service types
        service_mapping = {
            "architectural metal fabrication": "architectural metalwork",
            "metal fabrication": "metal fabrication",
            "custom metal work": "custom metalwork",
            "copper fabrication": "copper work",
            "roofing": "metal roofing",
            "cupola": "cupola installation",
            "finial": "finial installation",
            "dormer": "dormer construction",
            "chimney": "chimney work",
            "snow guard": "snow guard installation"
        }
        
        # Find the best match
        for key, service in service_mapping.items():
            if key in keyword_clean.lower():
                return service
                
        return "architectural metalwork"  # Default fallback
    
    def generate_faq_questions(self, primary_keyword: str, city_name: str, count: int = 5) -> List[Dict[str, str]]:
        """
        Generate FAQ questions based on primary keyword and city
        
        Args:
            primary_keyword: Primary keyword for the city page
            city_name: City name for localization
            count: Number of questions to generate (default 5)
            
        Returns:
            List of FAQ dictionaries with question and answer
        """
        if not primary_keyword:
            primary_keyword = "architectural metal fabrication"
            
        faqs = []
        city_base = city_name.split(',')[0].strip()
        service = self.extract_service_from_keyword(primary_keyword)
        
        # Get base questions for the keyword
        base_questions = []
        for key, questions in self.base_questions.items():
            if key in primary_keyword.lower():
                base_questions = questions[:3]  # Take first 3
                break
        
        if not base_questions:
            base_questions = self.base_questions["architectural metal fabrication"][:3]
        
        # Add base questions
        for question in base_questions:
            answer = self._generate_answer(question, city_name, service)
            faqs.append({
                "question": question,
                "answer": answer
            })
        
        # Add city-specific questions
        remaining_count = count - len(faqs)
        if remaining_count > 0:
            city_questions = self._generate_city_questions(service, city_base, remaining_count)
            for question in city_questions:
                answer = self._generate_answer(question, city_name, service)
                faqs.append({
                    "question": question,
                    "answer": answer
                })
        
        return faqs[:count]  # Ensure we don't exceed requested count
    
    def _generate_city_questions(self, service: str, city_base: str, count: int) -> List[str]:
        """Generate city-specific questions"""
        
        templates = [
            f"What should I know about {service} in {city_base}?",
            f"Are there experienced {service} contractors in {city_base}?",
            f"What permits do I need for {service} in {city_base}?",
            f"How much does {service} typically cost in {city_base}?",
            f"What are the local building requirements for {service} in {city_base}?"
        ]
        
        # Shuffle and take the requested count
        random.shuffle(templates)
        return templates[:count]
    
    def _generate_answer(self, question: str, city_name: str, service: str) -> str:
        """
        Generate contextual answers for FAQ questions
        
        Args:
            question: The FAQ question
            city_name: City name for context
            service: Service type for context
            
        Returns:
            Generated answer text
        """
        city_base = city_name.split(',')[0].strip()
        
        # Answer templates based on question type
        if "cost" in question.lower() or "price" in question.lower():
            return (f"{service.title()} costs in {city_base} vary based on project complexity, "
                   f"materials, and design specifications. Salvo Metal Works provides detailed estimates "
                   f"that account for local factors and ensure transparent pricing for your {city_base} project.")
        
        elif "contractor" in question.lower() or "company" in question.lower():
            return (f"Salvo Metal Works serves {city_base} with expert {service} services. "
                   f"Our team understands local building practices and requirements, delivering "
                   f"quality craftsmanship that meets {city_base}'s architectural standards.")
        
        elif "permit" in question.lower() or "building code" in question.lower():
            return (f"{service.title()} projects in {city_base} may require permits depending on scope and location. "
                   f"Salvo Metal Works works with local authorities and can guide you through the permitting process "
                   f"to ensure your {city_base} project meets all requirements.")
        
        elif "material" in question.lower():
            return (f"Common materials for {service} include copper, zinc, stainless steel, and aluminum. "
                   f"Each offers different benefits for {city_base}'s climate and architectural styles. "
                   f"Salvo Metal Works helps select the right materials for durability and aesthetic appeal.")
        
        elif "time" in question.lower() or "long does" in question.lower():
            return (f"{service.title()} project timelines depend on complexity and customization requirements. "
                   f"Typical projects range from 2-8 weeks from design approval to installation. "
                   f"Salvo Metal Works provides realistic schedules that account for {city_base} project factors.")
        
        elif "type" in question.lower() or "service" in question.lower():
            return (f"Salvo Metal Works offers comprehensive {service} including design consultation, "
                   f"custom fabrication, and professional installation. We specialize in cupolas, finials, "
                   f"dormers, roof vents, chimney shrouds, leader boxes, and snow guards for {city_base} projects.")
        
        else:
            # Generic answer
            return (f"For {service} in {city_base}, Salvo Metal Works combines traditional craftsmanship "
                   f"with modern techniques to deliver exceptional results. Our team understands local "
                   f"requirements and climate considerations to ensure your project succeeds.")
    
    def get_city_faq_data(self, city_name: str, primary_keyword: str = "") -> List[Dict[str, str]]:
        """
        Get complete FAQ data for a city page
        
        Args:
            city_name: City name 
            primary_keyword: Primary keyword for the page
            
        Returns:
            List of FAQ data ready for template integration
        """
        return self.generate_faq_questions(primary_keyword, city_name, 5)


# Convenience functions
def generate_city_faqs(city_name: str, primary_keyword: str = "", count: int = 5) -> List[Dict[str, str]]:
    """
    Generate FAQ data for a city
    
    Args:
        city_name: City name
        primary_keyword: Primary keyword for context
        count: Number of FAQs to generate
        
    Returns:
        List of FAQ data
    """
    api = PeopleAlsoAskAPI()
    return api.generate_faq_questions(primary_keyword, city_name, count)


def get_service_faqs(service_keyword: str, count: int = 5) -> List[str]:
    """
    Get generic FAQ questions for a service
    
    Args:
        service_keyword: Service keyword to base questions on
        count: Number of questions to return
        
    Returns:
        List of FAQ questions
    """
    api = PeopleAlsoAskAPI()
    
    # Find matching questions
    for key, questions in api.base_questions.items():
        if key in service_keyword.lower():
            return questions[:count]
            
    return api.base_questions["architectural metal fabrication"][:count]