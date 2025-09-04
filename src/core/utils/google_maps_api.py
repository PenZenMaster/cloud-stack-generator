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
import urllib.request
import json
import csv
import io
from typing import Optional, Dict, Any, List, Tuple
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()


class GoogleMapsAPI:
    """Google Maps API integration for automated embed generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize with API key from environment or parameter"""
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.places_base_url = "https://maps.googleapis.com/maps/api/place"
        self.geocoding_base_url = "https://maps.googleapis.com/maps/api/geocode"
        self.user_agent = "Cloud Stack Generator/1.0"
        
        # POI types relevant to architectural metal work
        self.relevant_poi_types = [
            "tourist_attraction",
            "museum", 
            "park",
            "city_hall",
            "library",
            "school",
            "university",
            "hospital",
            "church",
            "shopping_center",
            "restaurant"
        ]
        
        # Mock coordinates for development without API key
        self.mock_coords = {
            "Chicago": (41.8781, -87.6298),
            "Bellwood, Illinois": (41.8789, -87.8745),
            "Oak Park Illinois": (41.8850, -87.7845),
            "Oak Park, Illinois": (41.8850, -87.7845),
            "Berwyn, Illinois": (41.8503, -87.7937),
            "Bridgeview, Illinois": (41.7531, -87.8048),
            "Brookfield, Illinois": (41.8242, -87.8512),
            "Burbank, Illinois": (41.7392, -87.7790),
            "Cicero, Illinois": (41.8456, -87.7539),
            "Elmwood Park, Illinois": (41.9208, -87.8081),
            "Evanston, Illinois": (42.0451, -87.6877),
            "Forest Park, Illinois": (41.8792, -87.8137),
            "Franklin Park, Illinois": (41.9297, -87.8648),
            "Harwood Heights, Illinois": (41.9667, -87.8081),
            "Lincolnwood, Illinois": (42.0089, -87.7287),
            "Lyons, Illinois": (41.8131, -87.8184),
            "Maywood, Illinois": (41.8792, -87.8437),
            "Melrose Park, Illinois": (41.8992, -87.8581),
            "Norridge, Illinois": (41.9625, -87.8273),
            "Oak Lawn, Illinois": (41.7197, -87.7531),
            "Park Ridge, Illinois": (42.0112, -87.8406),
            "River Forest, Illinois": (41.8992, -87.8137),
            "River Grove, Illinois": (41.9292, -87.8381),
            "Riverside, Illinois": (41.8331, -87.8184),
            "Skokie, Illinois": (42.0334, -87.7334),
            "Summit, Illinois": (41.7886, -87.8165)
        }
    
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
    
    def get_city_coordinates(self, city_name: str) -> Optional[Tuple[float, float]]:
        """
        Get latitude and longitude for a city using geocoding
        
        Args:
            city_name: City name to geocode
            
        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        if not self.api_key:
            return self.mock_coords.get(city_name)
            
        try:
            encoded_city = urllib.parse.quote(city_name)
            url = f"{self.geocoding_base_url}/json?address={encoded_city}&key={self.api_key}"
            
            request = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            
            with urllib.request.urlopen(request, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    
                    if data.get('status') == 'OK' and data.get('results'):
                        location = data['results'][0]['geometry']['location']
                        return (location['lat'], location['lng'])
                        
        except Exception:
            return self.mock_coords.get(city_name)
            
        return None

    def search_nearby_pois(self, city_name: str, radius_miles: int = 5) -> List[Dict[str, Any]]:
        """
        Search for points of interest near a city center
        
        Args:
            city_name: City name to search around
            radius_miles: Search radius in miles (default 5)
            
        Returns:
            List of POI dictionaries with name, address, location, etc.
        """
        coordinates = self.get_city_coordinates(city_name)
        if not coordinates:
            return []
            
        lat, lng = coordinates
        
        if not self.api_key:
            return self._get_mock_pois(city_name, lat, lng)
            
        radius_meters = radius_miles * 1609.34
        pois = []
        
        try:
            for poi_type in self.relevant_poi_types[:3]:
                url = (f"{self.places_base_url}/nearbysearch/json?"
                       f"location={lat},{lng}&radius={radius_meters}&type={poi_type}&key={self.api_key}")
                
                request = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
                
                with urllib.request.urlopen(request, timeout=10) as response:
                    if response.status == 200:
                        data = json.loads(response.read().decode('utf-8'))
                        
                        if data.get('status') == 'OK':
                            for place in data.get('results', [])[:2]:
                                poi = self._format_poi_data(place)
                                if poi:
                                    pois.append(poi)
                                    
                time.sleep(0.1)
                
        except Exception:
            return self._get_mock_pois(city_name, lat, lng)
            
        return pois[:5]

    def _get_mock_pois(self, city_name: str, lat: float, lng: float) -> List[Dict[str, Any]]:
        """Generate mock POI data for development"""
        city_base = city_name.split(',')[0].strip()
        
        return [
            {
                "name": f"{city_base} Public Library",
                "address": f"123 Main St, {city_name}",
                "latitude": lat + 0.01,
                "longitude": lng + 0.01,
                "place_id": f"mock_library_{city_base.lower().replace(' ', '_')}",
                "rating": 4.2,
                "types": ["library", "establishment"]
            },
            {
                "name": f"{city_base} Community Park", 
                "address": f"456 Park Ave, {city_name}",
                "latitude": lat - 0.01,
                "longitude": lng - 0.01,
                "place_id": f"mock_park_{city_base.lower().replace(' ', '_')}",
                "rating": 4.5,
                "types": ["park", "establishment"]
            },
            {
                "name": f"{city_base} Historical Museum",
                "address": f"789 Heritage Blvd, {city_name}",
                "latitude": lat + 0.005,
                "longitude": lng - 0.005,
                "place_id": f"mock_museum_{city_base.lower().replace(' ', '_')}",
                "rating": 4.1,
                "types": ["museum", "tourist_attraction", "establishment"]
            }
        ]

    def _format_poi_data(self, place_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Format raw Google Places API data into our POI structure"""
        if not place_data.get('name'):
            return None
            
        location = place_data.get('geometry', {}).get('location', {})
        
        return {
            "name": place_data['name'],
            "address": place_data.get('vicinity', ''),
            "latitude": location.get('lat', 0),
            "longitude": location.get('lng', 0), 
            "place_id": place_data.get('place_id', ''),
            "rating": place_data.get('rating', 0),
            "types": place_data.get('types', [])
        }

    def parse_csv_pois(self, csv_content: str) -> List[Dict[str, Any]]:
        """
        Parse CSV content containing manual POI data
        
        Args:
            csv_content: CSV string with format: Name,Address,Latitude,Longitude
            
        Returns:
            List of POI dictionaries
        """
        pois = []
        
        try:
            csv_reader = csv.reader(io.StringIO(csv_content))
            
            for row in csv_reader:
                if len(row) >= 4:
                    name = row[0].strip().strip('"')
                    address = row[1].strip().strip('"')
                    
                    try:
                        latitude = float(row[2].strip())
                        longitude = float(row[3].strip())
                        
                        pois.append({
                            "name": name,
                            "address": address,
                            "latitude": latitude,
                            "longitude": longitude,
                            "place_id": f"manual_{name.lower().replace(' ', '_')}",
                            "rating": 0,
                            "types": ["establishment"]
                        })
                        
                    except (ValueError, IndexError):
                        continue
                        
        except Exception:
            pass
            
        return pois

    def generate_poi_embed(self, poi_data: Dict[str, Any]) -> str:
        """
        Generate Google Maps embed code for a POI
        
        Args:
            poi_data: POI dictionary with name, address, latitude, longitude
            
        Returns:
            HTML embed code for the POI
        """
        name = poi_data.get('name', 'Unknown Location')
        address = poi_data.get('address', '')
        lat = poi_data.get('latitude', 0)
        lng = poi_data.get('longitude', 0)
        
        query = f"{name} {address}".strip()
        encoded_query = urllib.parse.quote(query)
        
        if self.api_key:
            embed_url = (f"https://www.google.com/maps/embed/v1/place?"
                        f"key={self.api_key}&q={encoded_query}&center={lat},{lng}")
        else:
            search_query = query.replace(' ', '+')
            embed_url = (f"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3048.0!"
                        f"2d{lng}!3d{lat}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!"
                        f"3m3!1m2!1s0x0:0x0!2s{search_query}")
        
        return embed_url

    def get_city_poi_data(self, city_name: str, csv_override: str = None) -> List[Dict[str, Any]]:
        """
        Get comprehensive POI data for a city
        
        Args:
            city_name: City name to get POIs for
            csv_override: Optional CSV string with manual POI data
            
        Returns:
            List of POI data with embed codes
        """
        if csv_override:
            pois = self.parse_csv_pois(csv_override)
        else:
            pois = self.search_nearby_pois(city_name)
        
        for poi in pois:
            poi['embed_url'] = self.generate_poi_embed(poi)
            
        return pois

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