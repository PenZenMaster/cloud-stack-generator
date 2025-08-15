"""
Filename: google_maps_api.py
Path: E:\\projects\\cloud-stack-generator\\src\\core\\utils\\google_maps_api.py
Description: Google Maps API integration utilities for automated embed generation
Provides API-based Google Maps and Directions embed URL generation

Version: 1.0.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

import os
import urllib.parse
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class GoogleMapsAPI:
    """Google Maps API integration for automated embed generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key from environment or parameter"""
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google Maps API key required. Set GOOGLE_MAPS_API_KEY environment variable "
                "or pass api_key parameter."
            )
    
    def build_place_embed_url(self, location: str, **params) -> str:
        """
        Build Google Maps Embed API URL for a place
        
        Args:
            location: Location to embed (e.g., "Chicago, IL" or "Evanston, Illinois")
            **params: Additional parameters (width, height, zoom, etc.)
            
        Returns:
            Complete iframe src URL for Google Maps embed
        """
        encoded_location = urllib.parse.quote(location)
        
        # Base embed URL
        base_url = "https://www.google.com/maps/embed/v1/place"
        
        # Required parameters
        url_params = {
            "key": self.api_key,
            "q": encoded_location
        }
        
        # Optional parameters
        if "zoom" in params:
            url_params["zoom"] = str(params["zoom"])
        if "maptype" in params:
            url_params["maptype"] = params["maptype"]  # roadmap, satellite, hybrid, terrain
        if "language" in params:
            url_params["language"] = params["language"]
        if "region" in params:
            url_params["region"] = params["region"]
            
        # Build query string
        query_string = urllib.parse.urlencode(url_params)
        return f"{base_url}?{query_string}"
    
    def build_directions_embed_url(self, origin: str, destination: str, **params) -> str:
        """
        Build Google Maps Embed API URL for directions
        
        Args:
            origin: Starting location
            destination: Ending location
            **params: Additional parameters (mode, avoid, units, etc.)
            
        Returns:
            Complete iframe src URL for Google Maps directions embed
        """
        encoded_origin = urllib.parse.quote(origin)
        encoded_destination = urllib.parse.quote(destination)
        
        # Base directions URL
        base_url = "https://www.google.com/maps/embed/v1/directions"
        
        # Required parameters
        url_params = {
            "key": self.api_key,
            "origin": encoded_origin,
            "destination": encoded_destination
        }
        
        # Optional parameters
        if "mode" in params:
            url_params["mode"] = params["mode"]  # driving, walking, bicycling, transit
        if "avoid" in params:
            url_params["avoid"] = params["avoid"]  # tolls, highways, ferries
        if "units" in params:
            url_params["units"] = params["units"]  # metric, imperial
        if "language" in params:
            url_params["language"] = params["language"]
        if "region" in params:
            url_params["region"] = params["region"]
            
        # Build query string
        query_string = urllib.parse.urlencode(url_params)
        return f"{base_url}?{query_string}"
    
    def generate_embed_iframe(self, src_url: str, width: str = "100%", 
                            height: str = "400", **iframe_attrs) -> str:
        """
        Generate complete iframe HTML for Google Maps embed
        
        Args:
            src_url: The Google Maps embed URL
            width: iframe width (default: "100%")
            height: iframe height (default: "400")
            **iframe_attrs: Additional iframe attributes
            
        Returns:
            Complete HTML iframe element
        """
        # Default iframe attributes
        attrs = {
            "src": src_url,
            "width": width,
            "height": height,
            "style": "border:0;",
            "allowfullscreen": "",
            "loading": "lazy",
            "referrerpolicy": "no-referrer-when-downgrade"
        }
        
        # Override with custom attributes
        attrs.update(iframe_attrs)
        
        # Build attribute string
        attr_string = " ".join(f'{key}="{value}"' for key, value in attrs.items())
        
        return f"<iframe {attr_string}></iframe>"
    
    def create_place_embed(self, location: str, width: str = "100%", 
                          height: str = "400", **params) -> Dict[str, str]:
        """
        Create complete place embed with URL and iframe HTML
        
        Args:
            location: Location to embed
            width: iframe width
            height: iframe height
            **params: Additional parameters for maps and iframe
            
        Returns:
            Dictionary with 'url' and 'iframe' keys
        """
        # Separate iframe params from maps params
        iframe_params = {k: v for k, v in params.items() 
                        if k in ["style", "allowfullscreen", "loading", "referrerpolicy"]}
        maps_params = {k: v for k, v in params.items() 
                      if k not in iframe_params}
        
        url = self.build_place_embed_url(location, **maps_params)
        iframe = self.generate_embed_iframe(url, width, height, **iframe_params)
        
        return {
            "url": url,
            "iframe": iframe,
            "location": location
        }
    
    def create_directions_embed(self, origin: str, destination: str, 
                              width: str = "100%", height: str = "400", 
                              **params) -> Dict[str, str]:
        """
        Create complete directions embed with URL and iframe HTML
        
        Args:
            origin: Starting location
            destination: Ending location
            width: iframe width
            height: iframe height
            **params: Additional parameters for maps and iframe
            
        Returns:
            Dictionary with 'url' and 'iframe' keys
        """
        # Separate iframe params from maps params
        iframe_params = {k: v for k, v in params.items() 
                        if k in ["style", "allowfullscreen", "loading", "referrerpolicy"]}
        maps_params = {k: v for k, v in params.items() 
                      if k not in iframe_params}
        
        url = self.build_directions_embed_url(origin, destination, **maps_params)
        iframe = self.generate_embed_iframe(url, width, height, **iframe_params)
        
        return {
            "url": url,
            "iframe": iframe,
            "origin": origin,
            "destination": destination
        }
    
    def is_api_key_valid(self) -> bool:
        """
        Check if API key is present (basic validation)
        
        Returns:
            True if API key exists, False otherwise
        """
        return bool(self.api_key and len(self.api_key.strip()) > 10)


# Convenience functions for backward compatibility with Location Page Generator
def build_google_map_embed(location: str, api_key: Optional[str] = None) -> str:
    """
    Build Google Maps embed URL (Location Page Generator compatibility)
    
    Args:
        location: Location to embed
        api_key: Optional API key (uses environment if not provided)
        
    Returns:
        Google Maps embed URL
    """
    api = GoogleMapsAPI(api_key)
    return api.build_place_embed_url(location)


def build_google_directions_embed(origin: str, destination: str, 
                                 api_key: Optional[str] = None) -> str:
    """
    Build Google Maps directions embed URL (Location Page Generator compatibility)
    
    Args:
        origin: Starting location
        destination: Ending location
        api_key: Optional API key (uses environment if not provided)
        
    Returns:
        Google Maps directions embed URL
    """
    api = GoogleMapsAPI(api_key)
    return api.build_directions_embed_url(origin, destination)