"""
Filename: wikipedia_api.py
Path: E:\\projects\\cloud-stack-generator\\src\\core\\utils\\wikipedia_api.py
Description: Wikipedia API integration utilities for automated image fetching
Provides Wikipedia image fetching and attribution for city pages

Version: 1.0.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

import urllib.parse
import urllib.request
import json
from typing import Optional, Dict, Any, Tuple
import re


class WikipediaAPI:
    """Wikipedia API integration for automated image fetching"""
    
    def __init__(self):
        """Initialize Wikipedia API client"""
        self.base_url = "https://en.wikipedia.org/api/rest_v1"
        self.commons_base = "https://commons.wikimedia.org/wiki"
        self.user_agent = "Cloud Stack Generator/1.0 (https://github.com/cloud-stack-generator)"
    
    def normalize_city_name(self, city_name: str) -> str:
        """
        Normalize city name for Wikipedia page lookup
        
        Args:
            city_name: Original city name (e.g., "Chicago, IL" or "Evanston, Illinois")
            
        Returns:
            Normalized name for Wikipedia lookup
        """
        # Remove state abbreviations and extra formatting
        city = city_name.split(",")[0].strip()
        
        # Replace spaces with underscores for Wikipedia URLs
        return city.replace(" ", "_")
    
    def build_wikipedia_image_embed(self, city: str) -> Tuple[str, str, str]:
        """
        Build Wikipedia image embed (Location Page Generator compatibility)
        
        Args:
            city: City name to get image for
            
        Returns:
            Tuple of (image_url, source_url, attribution)
        """
        safe_city = self.normalize_city_name(city)
        
        # Common Wikipedia image patterns for cities
        possible_files = [
            f"{safe_city}.jpg",
            f"{safe_city}_skyline.jpg", 
            f"{safe_city}_panorama.jpg",
            f"Downtown_{safe_city}.jpg",
            f"{safe_city}_view.jpg"
        ]
        
        # Try each possible file
        for filename in possible_files:
            image_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/{filename}/1280px-{filename}"
            source_url = f"{self.commons_base}/File:{filename}"
            attribution = f"Wikimedia Commons, {filename}"
            
            # For now, return the first pattern (can be enhanced with actual API calls)
            return image_url, source_url, attribution
            
        # Fallback to generic pattern
        image_url = f"https://upload.wikimedia.org/wikipedia/commons/thumb/1/1d/{safe_city}.jpg/1280px-{safe_city}.jpg"
        source_url = f"{self.commons_base}/File:{safe_city}.jpg"
        attribution = f"Wikimedia Commons, {safe_city}.jpg"
        
        return image_url, source_url, attribution
    
    def search_wikipedia_page(self, city_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for Wikipedia page for a city
        
        Args:
            city_name: City name to search for
            
        Returns:
            Dictionary with page information or None if not found
        """
        try:
            # Normalize city name for search
            search_term = city_name.replace(",", "").strip()
            encoded_term = urllib.parse.quote(search_term)
            
            # Wikipedia API search endpoint
            search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded_term}"
            
            request = urllib.request.Request(
                search_url,
                headers={'User-Agent': self.user_agent}
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    return {
                        "title": data.get("title", ""),
                        "extract": data.get("extract", ""),
                        "page_url": data.get("content_urls", {}).get("desktop", {}).get("page", ""),
                        "thumbnail": data.get("thumbnail", {})
                    }
        except (urllib.error.URLError, urllib.error.HTTPError, json.JSONDecodeError, Exception):
            # Silently handle errors - Wikipedia lookup is not critical
            pass
            
        return None
    
    def get_city_image_info(self, city_name: str) -> Dict[str, Any]:
        """
        Get comprehensive city image information
        
        Args:
            city_name: City name to get image info for
            
        Returns:
            Dictionary with image URLs, attribution, and metadata
        """
        # Get basic Wikipedia page info
        page_info = self.search_wikipedia_page(city_name)
        
        # Get image embed info (using Location Page Generator method)
        image_url, source_url, attribution = self.build_wikipedia_image_embed(city_name)
        
        result = {
            "city_name": city_name,
            "normalized_name": self.normalize_city_name(city_name),
            "image_url": image_url,
            "source_url": source_url,
            "attribution": attribution,
            "alt_text": f"View of {city_name.split(',')[0].strip()}",
            "wikipedia_page": page_info.get("page_url", "") if page_info else "",
            "description": page_info.get("extract", "")[:200] + "..." if page_info and page_info.get("extract") else ""
        }
        
        # If we have a Wikipedia thumbnail, prefer that
        if page_info and page_info.get("thumbnail", {}).get("source"):
            thumbnail = page_info["thumbnail"]
            # Use larger version if available
            if thumbnail.get("source"):
                # Try to get a larger version
                thumb_url = thumbnail["source"]
                if "/thumb/" in thumb_url and thumb_url.endswith(".jpg"):
                    # Increase size to 800px width
                    larger_url = thumb_url.replace("/320px-", "/800px-").replace("/220px-", "/800px-")
                    result["image_url"] = larger_url
                    result["source_url"] = page_info.get("page_url", result["source_url"])
                    result["attribution"] = f"Wikipedia - {page_info.get('title', city_name)}"
        
        return result
    
    def generate_image_html(self, city_name: str, **options) -> str:
        """
        Generate HTML for city image with proper attribution
        
        Args:
            city_name: City name
            **options: HTML options (width, height, style, etc.)
            
        Returns:
            Complete HTML for image with attribution
        """
        image_info = self.get_city_image_info(city_name)
        
        # Default options
        width = options.get("width", "100%")
        height = options.get("height", "auto")
        style = options.get("style", "margin: 20px 0;")
        
        html = f'''<a title="{image_info['attribution']}" href="{image_info['source_url']}" target="_blank" rel="noopener">
  <img width="{width}" style="height:{height}; {style}" src="{image_info['image_url']}" alt="{image_info['alt_text']}">
</a>'''
        
        return html
    
    def get_multiple_cities_info(self, city_list: list) -> Dict[str, Dict[str, Any]]:
        """
        Get image information for multiple cities
        
        Args:
            city_list: List of city names
            
        Returns:
            Dictionary mapping city names to their image info
        """
        results = {}
        
        for city in city_list:
            if city.strip():
                results[city] = self.get_city_image_info(city.strip())
                
        return results


# Convenience functions for backward compatibility with Location Page Generator
def build_wikipedia_image_embed(city: str) -> Tuple[str, str, str]:
    """
    Build Wikipedia image embed (Location Page Generator compatibility)
    
    Args:
        city: City name to get image for
        
    Returns:
        Tuple of (image_url, source_url, attribution)
    """
    api = WikipediaAPI()
    return api.build_wikipedia_image_embed(city)


def get_city_wikipedia_info(city_name: str) -> Dict[str, Any]:
    """
    Get Wikipedia information for a city
    
    Args:
        city_name: City name to lookup
        
    Returns:
        Dictionary with Wikipedia page and image information
    """
    api = WikipediaAPI()
    return api.get_city_image_info(city_name)