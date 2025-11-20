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
import time


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
    
    def validate_image_url(self, image_url: str) -> bool:
        """
        Validate that an image URL actually exists and returns a valid image
        
        Args:
            image_url: URL to validate
            
        Returns:
            True if URL is valid and returns an image
        """
        try:
            request = urllib.request.Request(
                image_url,
                headers={'User-Agent': self.user_agent}
            )
            
            with urllib.request.urlopen(request, timeout=5) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '')
                    return content_type.startswith('image/')
                    
        except (urllib.error.URLError, urllib.error.HTTPError, Exception):
            pass
            
        return False
    
    def build_wikipedia_image_embed(self, city: str) -> Tuple[str, str, str]:
        """
        Build Wikipedia image embed using actual Wikipedia API calls
        
        Args:
            city: City name to get image for
            
        Returns:
            Tuple of (image_url, source_url, attribution)
        """
        # Get real Wikipedia page info first
        page_info = self.search_wikipedia_page(city)
        
        if page_info and page_info.get("thumbnail", {}).get("source"):
            thumbnail = page_info["thumbnail"]
            original_url = thumbnail["source"]
            
            # Try different sizes to find working image
            potential_urls = []
            
            if "/thumb/" in original_url:
                original_url.split("/thumb/")[0] + "/thumb/" + original_url.split("/thumb/")[1]
                
                # Try different sizes, from largest to smallest
                for size in ["1280px", "800px", "640px", "480px", "320px"]:
                    if f"/{size}-" in original_url:
                        # Use original size if it contains the size pattern
                        potential_urls.append(original_url)
                    else:
                        # Try to construct larger versions
                        if "/320px-" in original_url:
                            potential_urls.append(original_url.replace("/320px-", f"/{size}-"))
                        elif "/220px-" in original_url:
                            potential_urls.append(original_url.replace("/220px-", f"/{size}-"))
                        else:
                            potential_urls.append(original_url)
            else:
                potential_urls.append(original_url)
            
            # Test each URL to find working image
            for test_url in potential_urls:
                if self.validate_image_url(test_url):
                    source_url = page_info.get("page_url", "")
                    attribution = f"Wikipedia - {page_info.get('title', city)}"
                    return test_url, source_url, attribution
                    
                # Add small delay to avoid rate limiting
                time.sleep(0.1)
        
        # If no thumbnail available, try to construct a reasonable fallback
        # but this should rarely be reached with real Wikipedia API calls
        safe_city = self.normalize_city_name(city)
        fallback_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/No-image-available.svg/1280px-No-image-available.svg.png"
        fallback_source = f"https://en.wikipedia.org/wiki/{safe_city}"
        fallback_attribution = f"No image available for {city}"
        
        return fallback_url, fallback_source, fallback_attribution
    
    def search_wikipedia_page(self, city_name: str) -> Optional[Dict[str, Any]]:
        """
        Search for Wikipedia page for a city
        
        Args:
            city_name: City name to search for
            
        Returns:
            Dictionary with page information or None if not found
        """
        try:
            # Try multiple search variations to improve success rate
            search_terms = []
            
            # Original term
            search_terms.append(city_name.strip())
            
            # City name without state
            if "," in city_name:
                city_only = city_name.split(",")[0].strip()
                search_terms.append(city_only)
                
                # Add state back in different formats
                state_part = city_name.split(",")[1].strip()
                if state_part.lower() in ["il", "illinois"]:
                    search_terms.append(f"{city_only}, Illinois")
                    search_terms.append(f"{city_only} Illinois")
            
            # Try each search term until we find a match
            for search_term in search_terms:
                page_info = self._try_wikipedia_search(search_term)
                if page_info:
                    return page_info
                    
        except Exception:
            pass
            
        return None
    
    def get_city_about_content(self, city_name: str) -> str:
        """
        Get formatted about city content from Wikipedia for city pages
        
        Args:
            city_name: City name to get content for
            
        Returns:
            Formatted about city content suitable for city pages
        """
        page_info = self.search_wikipedia_page(city_name)
        
        if not page_info or not page_info.get("extract"):
            # Fallback content if Wikipedia not available
            city_only = city_name.split(",")[0].strip()
            return f"{city_only} is a vibrant community known for its unique character and local heritage. The area offers distinctive opportunities for architectural and construction projects, with local building standards and community requirements that demand specialized expertise and attention to detail."
        
        extract = page_info["extract"]
        
        # Clean up and format the Wikipedia extract
        # Remove any parenthetical pronunciations at the start
        extract = re.sub(r'^\([^)]*\)\s*', '', extract)
        
        # Limit to reasonable length (400-600 words)
        sentences = extract.split('. ')
        
        # Take first several sentences but ensure we don't cut off mid-thought
        about_content = []
        char_count = 0
        target_length = 500  # Target around 500 characters
        
        for sentence in sentences:
            if char_count + len(sentence) > target_length and len(about_content) >= 2:
                break
            about_content.append(sentence.strip())
            char_count += len(sentence)
        
        # Join sentences and ensure proper ending
        result = '. '.join(about_content)
        if not result.endswith('.'):
            result += '.'
            
        return result
    
    def _try_wikipedia_search(self, search_term: str) -> Optional[Dict[str, Any]]:
        """
        Try a single Wikipedia search term
        
        Args:
            search_term: Term to search for
            
        Returns:
            Dictionary with page information or None if not found
        """
        try:
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
        Get comprehensive city image information with embed code
        
        Args:
            city_name: City name to get image info for
            
        Returns:
            Dictionary with image URLs, attribution, metadata, and complete embed code
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
        
        # Generate complete embed code using the current result data
        result["embed_code"] = self._build_embed_code_from_info(result, **{})
        
        return result
    
    def _build_embed_code_from_info(self, image_info: Dict[str, Any], **options) -> str:
        """
        Build embed code from existing image info dictionary
        
        Args:
            image_info: Dictionary with image information
            **options: HTML options (width, height, style, class, etc.)
            
        Returns:
            Complete HTML embed code ready for template insertion
        """
        # Default options
        width = options.get("width", "100%")
        height = options.get("height", "auto")
        style = options.get("style", "margin: 20px 0;")
        css_class = options.get("class", "city-image")
        lazy_loading = options.get("lazy", True)
        
        # Build complete embed with section wrapper
        embed_code = f'''<section class="{css_class}">
    <a title="{image_info['attribution']}" href="{image_info['source_url']}" target="_blank" rel="noopener">
        <img src="{image_info['image_url']}" 
             alt="{image_info['alt_text']}"
             width="{width}" 
             style="height: {height}; {style}"
             {'loading="lazy"' if lazy_loading else ''}>
    </a>
    <p class="image-caption">{image_info['attribution']}</p>
</section>'''
        
        return embed_code
    
    def generate_image_embed_code(self, city_name: str, **options) -> str:
        """
        Generate complete Wikipedia image embed code with attribution
        
        Args:
            city_name: City name
            **options: HTML options (width, height, style, class, etc.)
            
        Returns:
            Complete HTML embed code ready for template insertion
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
        
        return self._build_embed_code_from_info(result, **options)
    
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


# Convenience functions for backward compatibility and new embed code approach
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
    Get Wikipedia information for a city with embed code
    
    Args:
        city_name: City name to lookup
        
    Returns:
        Dictionary with Wikipedia page, image information, and complete embed code
    """
    api = WikipediaAPI()
    return api.get_city_image_info(city_name)


def get_wikipedia_embed_code(city_name: str, **options) -> str:
    """
    Get complete Wikipedia image embed code for a city
    
    Args:
        city_name: City name to get embed for
        **options: HTML options (width, height, style, class, etc.)
        
    Returns:
        Complete HTML embed code ready for template insertion
    """
    api = WikipediaAPI()
    return api.generate_image_embed_code(city_name, **options)