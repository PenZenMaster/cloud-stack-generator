# BACKUP FILE - enhanced_cities_tab.py functionality to be merged into CitiesTab
# Created: August 17, 2025 for Sprint 2.5 consolidation

"""
KEY METHODS TO PRESERVE FROM enhanced_cities_tab.py:

1. add_new_city(self)
2. remove_selected_city(self) 
3. duplicate_selected_city(self)
4. get_config_data(self) -> returns {"city_pages": [...]}

DATA STRUCTURE TO PRESERVE:
{
    "city_pages": [
        {
            "city_name": str,
            "state": str,
            "slug": str,
            "title": str,
            "meta_description": str,
            "primary_keyword": str,
            "secondary_keywords": List[str],
            "hero_title": str,
            "breadcrumbs": List[str],
            "about_city": str,
            "city_image": {
                "image_url": str,
                "alt_text": str,
                "caption": str,
                "credit": str,
                "source": str
            },
            "seo_content_title": str,
            "seo_content_body": str,
            "places_of_interest": [
                {
                    "name": str,
                    "embed_url": str
                }
            ],
            "city_faq": [
                {
                    "question": str,
                    "answer": str
                }
            ],
            "featured_products": List[str],
            "city_map_embed": str,
            "service_area_note": str
        }
    ]
}

INTEGRATION REQUIREMENTS:
- Must maintain backward compatibility with target_cities format
- Should support both data formats in get_config_data()
- Need to preserve all Sprint 2.5 verification requirements
- Must work with existing main window save/load logic
"""