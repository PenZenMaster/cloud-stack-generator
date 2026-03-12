"""
Module/Script Name: Google Business Profile Client
Path: src/core/onboarding/gbp_client.py

Description:
Resolves a Google Business Profile share link to a Place ID and fetches
structured place details (address, hours, phone, lat/lng) via the
Google Places API (New) for use during client auto-onboarding.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-11

Last Modified Date:
2026-03-11 (v1.02)

Comments:
* v1.02 - SAB (Service Area Business) support: fetch() now enriches sparse
          place details (no city) with city/state from text search formattedAddress;
          search_place() retries without location bias for SABs;
          search_place_with_fallback() returns GBPData directly from search results
* v1.01 - Migrated from legacy Places API to Places API (New)
          New endpoints: places.googleapis.com/v1/
          Auth via X-Goog-Api-Key header, field masks via X-Goog-FieldMask header
          Response format: displayName, nationalPhoneNumber, location.latitude/longitude,
          addressComponents with longText/shortText, regularOpeningHours
* v1.00 - Initial implementation (legacy Places API)
"""

import os
import re
import urllib.parse
from dataclasses import dataclass, field
from typing import Dict, Optional

import requests
from dotenv import load_dotenv

from ..utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

PLACES_BASE_URL = "https://places.googleapis.com/v1"

PLACE_DETAILS_FIELD_MASK = (
    "id,displayName,formattedAddress,addressComponents,location,"
    "nationalPhoneNumber,regularOpeningHours,websiteUri,rating,userRatingCount,googleMapsUri"
)

DAY_NAMES = [
    "sunday",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
]

# weekdayDescriptions in Places API (New) is ordered Monday-Sunday
WEEKDAY_ORDER = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


@dataclass
class GBPData:
    """Structured data extracted from a Google Business Profile."""

    business_name: str = ""
    phone: str = ""
    website: str = ""
    street: str = ""
    city: str = ""
    state: str = ""
    zip_code: str = ""
    country: str = "United States"
    latitude: float = 0.0
    longitude: float = 0.0
    rating: str = ""
    review_count: str = ""
    place_id: str = ""
    profile_url: str = ""
    business_hours: Dict[str, str] = field(default_factory=dict)


class GBPClient:
    """
    Google Business Profile client using the Places API (New).

    Resolves GBP share links (g.co, maps.app.goo.gl, or full google.com/maps URLs)
    to a Place ID, then fetches structured place details via:
      GET  places.googleapis.com/v1/places/{place_id}
      POST places.googleapis.com/v1/places:searchText

    Args:
        api_key: Google Places API key. Falls back to GOOGLE_MAPS_API_KEY env var.
    """

    USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY", "")

    def is_api_key_valid(self) -> bool:
        """Return True if an API key is configured."""
        return bool(self.api_key and len(self.api_key) > 10)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def fetch(self, share_url: str) -> Optional[GBPData]:
        """
        Resolve a GBP share link and fetch place details.

        Handles Service Area Businesses (SABs) that hide their physical address:
        if place details return no city/state, a secondary text search is used
        to recover the service-area location from the search result's formattedAddress.

        Args:
            share_url: A GBP share URL in any supported format.

        Returns:
            GBPData if successful, None if the API key is missing or lookup fails.
        """
        if not self.is_api_key_valid():
            logger.warning("No Google API key configured - skipping GBP lookup.")
            return None

        place_id = self.resolve_share_link(share_url)
        if not place_id:
            logger.warning(f"Could not resolve Place ID from: {share_url}")
            return None

        result = self.get_place_details(place_id)
        if result and not result.city and result.business_name:
            # SAB: place details omit physical address. Recover city/state from
            # the text search formattedAddress (often shows service area city).
            logger.info(f"SAB detected for '{result.business_name}' - enriching from text search")
            search_data = self.search_place_with_fallback(result.business_name)
            if search_data:
                result.city = result.city or search_data.city
                result.state = result.state or search_data.state
                result.zip_code = result.zip_code or search_data.zip_code
                logger.info(
                    f"SAB enriched: city={result.city}, state={result.state}, "
                    f"zip={result.zip_code}"
                )
        return result

    def resolve_share_link(self, share_url: str) -> Optional[str]:
        """
        Follow redirects on a GBP share link and extract the Place ID.

        Handles:
          - https://maps.app.goo.gl/... (short redirect)
          - https://g.co/kgs/...       (short redirect)
          - https://www.google.com/maps/place/... (full URL)

        Falls back to location-biased text search using the business name and
        coordinates extracted from the resolved URL.

        Args:
            share_url: GBP share URL.

        Returns:
            Place ID string or None.
        """
        # Try to extract directly from the provided URL
        place_id = self._extract_place_id_from_url(share_url)
        if place_id:
            return place_id

        # Follow redirects to resolve short links (GET required - HEAD unreliable for Google)
        try:
            resp = requests.get(
                share_url,
                allow_redirects=True,
                timeout=10,
                headers={"User-Agent": self.USER_AGENT},
            )
            final_url = resp.url
            logger.info(f"Resolved {share_url} -> {final_url}")

            place_id = self._extract_place_id_from_url(final_url)
            if place_id:
                return place_id

            # Extract business name and coordinates for location-biased text search
            business_name = self._extract_name_from_maps_url(final_url)
            coords = self._extract_coords_from_maps_url(final_url)

            if business_name:
                logger.info(
                    f"Falling back to text search for: {business_name}"
                    + (f" near {coords}" if coords else "")
                )
                return self.search_place(business_name, location=coords)

            logger.warning(f"Could not extract Place ID or name from final URL: {final_url}")

        except Exception as exc:
            logger.warning(f"Redirect resolution failed for {share_url}: {exc}")

        return None

    def get_place_details(self, place_id: str) -> Optional[GBPData]:
        """
        Call the Places API (New) place details endpoint.

        Args:
            place_id: Google Place ID.

        Returns:
            Populated GBPData or None on error.
        """
        url = f"{PLACES_BASE_URL}/places/{place_id}"
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": PLACE_DETAILS_FIELD_MASK,
            "User-Agent": self.USER_AGENT,
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if not resp.ok:
                logger.error(
                    f"Places API (New) error {resp.status_code} for {place_id}: "
                    f"{resp.text[:200]}"
                )
                return None
            return self._parse_place_result(resp.json())
        except Exception as exc:
            logger.error(f"Place details request failed: {exc}")
            return None

    def search_place(
        self,
        query: str,
        location: Optional[tuple] = None,
    ) -> Optional[str]:
        """
        Use the Places API (New) text search to find a Place ID by name.

        Args:
            query: Business name or search string.
            location: Optional (latitude, longitude) tuple for location bias.

        Returns:
            Place ID string or None.
        """
        url = f"{PLACES_BASE_URL}/places:searchText"
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.rating",
            "Content-Type": "application/json",
            "User-Agent": self.USER_AGENT,
        }
        body: dict = {"textQuery": query}
        if location:
            lat, lng = location
            body["locationBias"] = {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": 10000.0,  # 10km radius
                }
            }
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=10)
            logger.info(f"Text search HTTP {resp.status_code} for: {query}")
            if not resp.ok:
                logger.error(f"Places text search error {resp.status_code}: {resp.text[:500]}")
                return None
            data = resp.json()
            # Places API (New) may return an error body even on 200
            if "error" in data:
                logger.error(f"Places text search API error: {data['error']}")
                return None
            places = data.get("places", [])
            logger.info(f"Text search returned {len(places)} result(s)")
            if places:
                return places[0].get("id")

            # SABs may not appear in location-biased searches - retry without bias
            if location:
                logger.info("No results with location bias - retrying without (SAB possible)")
                return self.search_place(query, location=None)

            logger.warning(f"Text search returned no places for: {query}")
        except Exception as exc:
            logger.error(f"Place text search request failed: {exc}")

        return None

    def search_place_with_fallback(
        self,
        query: str,
        location: Optional[tuple] = None,
    ) -> Optional[GBPData]:
        """
        Text search returning basic GBPData directly from the search result.

        Used as a fallback for SABs where place details may return sparse data.
        Returns a GBPData populated from the search result fields alone.

        Args:
            query: Business name or search string.
            location: Optional (latitude, longitude) tuple for location bias.

        Returns:
            Minimal GBPData or None.
        """
        url = f"{PLACES_BASE_URL}/places:searchText"
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.rating",
            "Content-Type": "application/json",
            "User-Agent": self.USER_AGENT,
        }
        body: dict = {"textQuery": query}
        if location:
            lat, lng = location
            body["locationBias"] = {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": 10000.0,
                }
            }
        try:
            resp = requests.post(url, headers=headers, json=body, timeout=10)
            if not resp.ok:
                return None
            places = resp.json().get("places", [])
            if not places and location:
                # Retry without bias for SABs
                body.pop("locationBias", None)
                resp = requests.post(url, headers=headers, json=body, timeout=10)
                if resp.ok:
                    places = resp.json().get("places", [])
            if places:
                hit = places[0]
                data = GBPData()
                data.place_id = hit.get("id", "")
                data.business_name = hit.get("displayName", {}).get("text", "")
                data.rating = str(hit.get("rating", "")) if hit.get("rating") else ""
                # formattedAddress for SABs is typically "City, State ZIP, Country"
                # Standard US format: "Naperville, IL 60540, USA"
                #   parts[-3] = city, parts[-2] = "IL 60540", parts[-1] = country
                formatted = hit.get("formattedAddress", "")
                if formatted:
                    parts = [p.strip() for p in formatted.split(",")]
                    if len(parts) >= 3:
                        data.city = parts[-3]
                    if len(parts) >= 2:
                        # State + zip may be combined e.g. "IL 60601"
                        state_zip = parts[-2].strip().split()
                        if state_zip:
                            data.state = state_zip[0]
                        if len(state_zip) > 1:
                            data.zip_code = state_zip[1]
                return data
        except Exception as exc:
            logger.error(f"search_place_with_fallback failed: {exc}")
        return None

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _extract_place_id_from_url(self, url: str) -> Optional[str]:
        """Extract a Place ID from a google.com/maps URL if present."""
        # Explicit place_id query parameter
        match = re.search(r"[?&]place_id=([A-Za-z0-9_-]+)", url)
        if match:
            return match.group(1)

        # ChIJ... style place ID embedded in data parameter (!1sChIJ...)
        match = re.search(r"!1s(ChI[A-Za-z0-9_-]+)", url)
        if match:
            return match.group(1)

        # Hex CID format (!1s0x...:0x...) - not a Place ID but signals we have a maps URL
        # handled downstream via business name text search

        # ChIJ... embedded in path segments
        match = re.search(r"/place/[^/]+/[^/]+/([A-Za-z0-9_-]{20,})", url)
        if match:
            candidate = match.group(1)
            if candidate.startswith("ChI"):
                return candidate

        # ftid parameter
        match = re.search(r"ftid=([A-Za-z0-9_:.-]+)", url)
        if match:
            return match.group(1)

        return None

    def _extract_coords_from_maps_url(self, url: str) -> Optional[tuple]:
        """Extract (latitude, longitude) from a google.com/maps URL (@lat,lng,zoom pattern)."""
        match = re.search(r"@(-?\d+\.\d+),(-?\d+\.\d+)", url)
        if match:
            return (float(match.group(1)), float(match.group(2)))
        return None

    def _extract_name_from_maps_url(self, url: str) -> Optional[str]:
        """Try to extract a business name from a google.com/maps/place/... URL."""
        match = re.search(r"/maps/place/([^/]+)", url)
        if match:
            name = urllib.parse.unquote_plus(match.group(1))
            return name.replace("+", " ").strip()
        return None

    def _parse_place_result(self, result: dict) -> GBPData:
        """Map a Places API (New) response dict to GBPData."""
        data = GBPData()

        # Core fields (new field names)
        data.business_name = result.get("displayName", {}).get("text", "")
        data.phone = result.get("nationalPhoneNumber", "")
        data.website = result.get("websiteUri", "")
        data.profile_url = result.get("googleMapsUri", "")
        data.place_id = result.get("id", "")

        rating = result.get("rating")
        if rating is not None:
            data.rating = str(rating)

        review_count = result.get("userRatingCount")
        if review_count is not None:
            data.review_count = str(review_count)

        # Location: new API uses latitude/longitude directly
        location = result.get("location", {})
        data.latitude = location.get("latitude", 0.0)
        data.longitude = location.get("longitude", 0.0)

        # Address components: new API uses longText/shortText
        for component in result.get("addressComponents", []):
            types = component.get("types", [])
            value = component.get("longText", "")
            short = component.get("shortText", "")

            if "street_number" in types:
                data.street = value + " " + data.street
            elif "route" in types:
                data.street = data.street.strip() + " " + value
            elif "locality" in types:
                data.city = value
            elif "administrative_area_level_1" in types:
                data.state = short  # state abbreviation
            elif "postal_code" in types:
                data.zip_code = value
            elif "country" in types:
                data.country = value

        data.street = data.street.strip()

        # Business hours: prefer weekdayDescriptions (pre-formatted strings)
        opening_hours = result.get("regularOpeningHours", {})
        weekday_descriptions = opening_hours.get("weekdayDescriptions", [])
        if weekday_descriptions:
            data.business_hours = self._parse_weekday_descriptions(weekday_descriptions)
        else:
            periods = opening_hours.get("periods", [])
            if periods:
                data.business_hours = self._parse_periods(periods)

        return data

    def _parse_weekday_descriptions(self, descriptions: list) -> Dict[str, str]:
        """
        Parse weekdayDescriptions from Places API (New).

        Format: ["Monday: 8:00 AM - 5:00 PM", ..., "Sunday: Closed"]
        Ordered Monday through Sunday.
        """
        hours: Dict[str, str] = {day: "Closed" for day in DAY_NAMES}

        for i, desc in enumerate(descriptions[:7]):
            if i < len(WEEKDAY_ORDER):
                day_name = WEEKDAY_ORDER[i]
                if ":" in desc:
                    time_part = desc.split(":", 1)[1].strip()
                    # Normalize unicode dashes to ASCII
                    time_part = time_part.replace("\u2013", "-").replace("\u2014", "-")
                    hours[day_name] = time_part

        return hours

    def _parse_periods(self, periods: list) -> Dict[str, str]:
        """
        Parse regularOpeningHours.periods from Places API (New).

        Each period: {"open": {"day": 1, "hour": 8, "minute": 0},
                      "close": {"day": 1, "hour": 17, "minute": 0}}
        Day 0 = Sunday, 1 = Monday, ..., 6 = Saturday.
        """
        hours: Dict[str, str] = {day: "Closed" for day in DAY_NAMES}

        for period in periods:
            open_info = period.get("open", {})
            close_info = period.get("close", {})
            day_num = open_info.get("day")
            if day_num is None:
                continue

            open_str = self._format_hhmm(
                open_info.get("hour", 0), open_info.get("minute", 0)
            )
            close_str = self._format_hhmm(
                close_info.get("hour", 0), close_info.get("minute", 0)
            )
            day_name = DAY_NAMES[day_num]

            if open_str and close_str:
                hours[day_name] = f"{open_str} - {close_str}"
            elif open_str:
                hours[day_name] = open_str

        return hours

    def _format_hhmm(self, hour: int, minute: int) -> str:
        """Convert hour/minute integers to '9:00 AM' display format."""
        suffix = "AM" if hour < 12 else "PM"
        display_hour = hour if hour <= 12 else hour - 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{minute:02d} {suffix}"

    def _format_time(self, military: str) -> str:
        """Convert '0900' -> '9:00 AM'. Kept for backwards compatibility."""
        if not military or len(military) < 4:
            return ""
        try:
            hour = int(military[:2])
            minute = military[2:4]
            suffix = "AM" if hour < 12 else "PM"
            display_hour = hour if hour <= 12 else hour - 12
            if display_hour == 0:
                display_hour = 12
            return f"{display_hour}:{minute} {suffix}"
        except (ValueError, IndexError):
            return military
