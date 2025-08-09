"""
PyTest configuration and fixtures for the cloud stack generator tests

Version: 1.0.1
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

import pytest


@pytest.fixture
def sample_config_dict():
    """Complete sample configuration matching our specification"""
    return {
        "client": {
            "business_name": "Acme Professional Services",
            "domain": "https://acmeprofessional.com",
            "industry": "Professional Services",
            "contact": {
                "name": "Acme Professional Services",
                "address": "123 Main St, Anytown, ST 12345",
                "phone": "+1-555-123-4567",
            },
            "social_media": {
                "facebook": "https://facebook.com/acmepro",
                "twitter": "https://twitter.com/acmepro",
                "linkedin": "https://linkedin.com/company/acmepro",
                "instagram": "https://instagram.com/acmepro",
            },
            "google_maps": {
                "place_id": "ChIJExample123",
                "embed_url": "https://maps.google.com/embed?pb=example",
            },
            "branding": {
                "primary_color": "#FF5722",
                "secondary_color": "#FFC107",
                "logo_url": "https://acmeprofessional.com/logo.png",
                "font_family": "Roboto",
            },
            "pages": [
                {
                    "title": "Home",
                    "slug": "index",
                    "primary_keyword": "professional services",
                    "secondary_keywords": ["local business", "expert solutions"],
                    "hero_image": "https://images.unsplash.com/professional",
                },
                {
                    "title": "About Us",
                    "slug": "about",
                    "primary_keyword": "experienced professionals",
                    "secondary_keywords": ["trusted advisors", "local experts"],
                    "hero_image": "https://images.unsplash.com/team",
                },
            ],
            "offerings": [
                {
                    "name": "Business Consulting",
                    "description": "Expert business consulting services",
                    "price_range": "$150-$300",
                    "category": "Professional Service",
                },
                {
                    "name": "Strategic Planning",
                    "description": "Comprehensive strategic planning services",
                    "price_range": "$500-$1500",
                    "category": "Consulting",
                },
            ],
        }
    }


@pytest.fixture
def minimal_config_dict():
    """Minimal configuration with only required fields"""
    return {
        "client": {
            "business_name": "Test Business",
            "contact": {"phone": "+1-555-987-6543"},
            "pages": [{"title": "Home", "slug": "index"}],
        }
    }


@pytest.fixture
def legacy_config_dict():
    """Configuration in your existing flat format for conversion testing"""
    cities_text = "Detroit\\nGrand Rapids\\nAnn Arbor"
    services_text = "Business Consulting\\nStrategic Planning\\nManagement Advice"
    social_text = "https://facebook.com/legacy\\n" "https://linkedin.com/company/legacy"
    faq_text = "What services do you offer?\\nHow much do you charge?"

    return {
        "* Client Name": "Legacy Business Name",
        "* Business Category": "Professional Services",
        "* Phone": "(555) 123-4567",
        "Email": "info@legacy.com",
        "* Website": "https://legacy.com",
        "Street Address": "123 Main St",
        "City": "City",
        "State": "ST",
        "ZIP": "12345",
        "Country": "USA",
        "* Target Cities (one per line)": cities_text,
        "* Services (one per line)": services_text,
        "Social/Citation URLs (one per line)": social_text,
        "Hero Image URL": "https://example.com/hero.jpg",
        "Logo URL": "https://example.com/logo.png",
        "Contact Email Address": "contact@legacy.com",
        "Primary Business Category": "Professional Services",
        "FAQ Questions (one per line)": faq_text,
    }


@pytest.fixture
def legacy_config_with_city_embeds():
    """Legacy config with city embed data"""
    detroit_embed = "<iframe src='https://maps.google.com/embed?detroit'></iframe>"
    gr_embed = "<iframe src='https://maps.google.com/embed?grandrapids'></iframe>"

    return {
        "* Client Name": "Legacy Business Name",
        "* Phone": "(555) 123-4567",
        "* Target Cities (one per line)": "Detroit\\nGrand Rapids",
        "city_embeds": {
            "Detroit, MI": {"embed_code": detroit_embed},
            "Grand Rapids, MI": {"embed_code": gr_embed},
        },
    }


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for test files"""
    return tmp_path
