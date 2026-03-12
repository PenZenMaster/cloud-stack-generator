"""
Tests for src/core/onboarding/gbp_client.py (Places API New)

Covers: share link resolution, place details parsing, hours parsing, error handling.
"""

from unittest.mock import Mock, patch

import pytest

from src.core.onboarding.gbp_client import GBPClient, GBPData


# Mock response matching Places API (New) format
MOCK_PLACE_DETAILS_RESPONSE = {
    "id": "ChIJabc123",
    "displayName": {"text": "ACME Plumbing Co.", "languageCode": "en"},
    "nationalPhoneNumber": "(555) 123-4567",
    "websiteUri": "https://acmeplumbing.com",
    "googleMapsUri": "https://maps.google.com/?cid=12345",
    "rating": 4.7,
    "userRatingCount": 238,
    "location": {"latitude": 41.8781, "longitude": -87.6298},
    "addressComponents": [
        {"longText": "123", "shortText": "123", "types": ["street_number"]},
        {"longText": "Main Street", "shortText": "Main St", "types": ["route"]},
        {"longText": "Chicago", "shortText": "Chicago", "types": ["locality"]},
        {
            "longText": "Illinois",
            "shortText": "IL",
            "types": ["administrative_area_level_1"],
        },
        {"longText": "60601", "shortText": "60601", "types": ["postal_code"]},
        {"longText": "United States", "shortText": "US", "types": ["country"]},
    ],
    "regularOpeningHours": {
        "weekdayDescriptions": [
            "Monday: 8:00 AM \u2013 5:00 PM",
            "Tuesday: 8:00 AM \u2013 5:00 PM",
            "Wednesday: 8:00 AM \u2013 5:00 PM",
            "Thursday: 8:00 AM \u2013 5:00 PM",
            "Friday: 8:00 AM \u2013 5:00 PM",
            "Saturday: 9:00 AM \u2013 2:00 PM",
            "Sunday: Closed",
        ],
        "periods": [
            {"open": {"day": 1, "hour": 8, "minute": 0}, "close": {"day": 1, "hour": 17, "minute": 0}},
            {"open": {"day": 2, "hour": 8, "minute": 0}, "close": {"day": 2, "hour": 17, "minute": 0}},
            {"open": {"day": 3, "hour": 8, "minute": 0}, "close": {"day": 3, "hour": 17, "minute": 0}},
            {"open": {"day": 4, "hour": 8, "minute": 0}, "close": {"day": 4, "hour": 17, "minute": 0}},
            {"open": {"day": 5, "hour": 8, "minute": 0}, "close": {"day": 5, "hour": 17, "minute": 0}},
            {"open": {"day": 6, "hour": 9, "minute": 0}, "close": {"day": 6, "hour": 14, "minute": 0}},
        ],
    },
}


def _make_mock_response(data: dict, status_code: int = 200):
    """Build a mock requests.Response."""
    mock = Mock()
    mock.ok = status_code < 400
    mock.status_code = status_code
    mock.json.return_value = data
    mock.text = str(data)
    return mock


class TestGBPClientInit:
    def test_uses_provided_api_key(self):
        client = GBPClient(api_key="my-key")
        assert client.api_key == "my-key"

    def test_falls_back_to_env_var(self):
        with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": "env-key"}):
            client = GBPClient()
        assert client.api_key == "env-key"

    def test_is_api_key_valid_true(self):
        client = GBPClient(api_key="a" * 20)
        assert client.is_api_key_valid() is True

    def test_is_api_key_valid_false_when_empty(self):
        with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": ""}):
            client = GBPClient(api_key="")
        assert client.is_api_key_valid() is False


class TestResolvePlaceId:
    def test_extracts_place_id_from_data_param(self):
        client = GBPClient(api_key="test-key")
        url = "https://www.google.com/maps/place/ACME+Plumbing/data=!4m6!3m5!1sChIJabc123!8m2!3d41.8!4d-87.6!16s"
        result = client._extract_place_id_from_url(url)
        assert result == "ChIJabc123"

    def test_extracts_place_id_query_param(self):
        client = GBPClient(api_key="test-key")
        url = "https://maps.google.com/?place_id=ChIJxyz789"
        result = client._extract_place_id_from_url(url)
        assert result == "ChIJxyz789"

    def test_returns_none_for_unrecognized_url(self):
        client = GBPClient(api_key="test-key")
        result = client._extract_place_id_from_url("https://example.com/page")
        assert result is None

    def test_extracts_name_from_maps_url(self):
        client = GBPClient(api_key="test-key")
        url = "https://www.google.com/maps/place/ACME+Plumbing+Co"
        name = client._extract_name_from_maps_url(url)
        assert "ACME" in name


class TestGetPlaceDetails:
    def _make_client(self):
        return GBPClient(api_key="test-key-12345678")

    def test_parses_business_name(self):
        client = self._make_client()
        with patch("requests.get", return_value=_make_mock_response(MOCK_PLACE_DETAILS_RESPONSE)):
            result = client.get_place_details("ChIJabc123")
        assert result is not None
        assert result.business_name == "ACME Plumbing Co."

    def test_parses_phone(self):
        client = self._make_client()
        with patch("requests.get", return_value=_make_mock_response(MOCK_PLACE_DETAILS_RESPONSE)):
            result = client.get_place_details("ChIJabc123")
        assert result.phone == "(555) 123-4567"

    def test_parses_address_components(self):
        client = self._make_client()
        with patch("requests.get", return_value=_make_mock_response(MOCK_PLACE_DETAILS_RESPONSE)):
            result = client.get_place_details("ChIJabc123")
        assert result.city == "Chicago"
        assert result.state == "IL"
        assert result.zip_code == "60601"
        assert "Main Street" in result.street or "Main St" in result.street

    def test_parses_lat_lng(self):
        client = self._make_client()
        with patch("requests.get", return_value=_make_mock_response(MOCK_PLACE_DETAILS_RESPONSE)):
            result = client.get_place_details("ChIJabc123")
        assert result.latitude == 41.8781
        assert result.longitude == -87.6298

    def test_parses_business_hours_from_weekday_descriptions(self):
        client = self._make_client()
        with patch("requests.get", return_value=_make_mock_response(MOCK_PLACE_DETAILS_RESPONSE)):
            result = client.get_place_details("ChIJabc123")
        assert result.business_hours.get("monday") == "8:00 AM - 5:00 PM"
        assert result.business_hours.get("saturday") == "9:00 AM - 2:00 PM"
        assert result.business_hours.get("sunday") == "Closed"

    def test_parses_business_hours_from_periods_fallback(self):
        """When weekdayDescriptions absent, fall back to periods."""
        response = dict(MOCK_PLACE_DETAILS_RESPONSE)
        response["regularOpeningHours"] = {
            "periods": MOCK_PLACE_DETAILS_RESPONSE["regularOpeningHours"]["periods"]
        }
        client = self._make_client()
        with patch("requests.get", return_value=_make_mock_response(response)):
            result = client.get_place_details("ChIJabc123")
        assert result.business_hours.get("monday") == "8:00 AM - 5:00 PM"
        assert result.business_hours.get("saturday") == "9:00 AM - 2:00 PM"
        assert result.business_hours.get("sunday") == "Closed"

    def test_returns_none_on_api_error(self):
        client = self._make_client()
        with patch("requests.get", return_value=_make_mock_response({}, status_code=403)):
            result = client.get_place_details("ChIJabc123")
        assert result is None

    def test_returns_none_when_no_api_key(self):
        client = GBPClient(api_key="")
        result = client.fetch("https://maps.app.goo.gl/abc123")
        assert result is None

    def test_handles_missing_optional_fields(self):
        minimal = {
            "id": "ChIJ123",
            "displayName": {"text": "Test Business"},
            "location": {"latitude": 0.0, "longitude": 0.0},
            "addressComponents": [],
        }
        client = self._make_client()
        with patch("requests.get", return_value=_make_mock_response(minimal)):
            result = client.get_place_details("ChIJ123")
        assert result is not None
        assert result.business_name == "Test Business"
        assert result.phone == ""
        assert result.place_id == "ChIJ123"

    def test_uses_correct_field_mask_header(self):
        client = self._make_client()
        mock_resp = _make_mock_response(MOCK_PLACE_DETAILS_RESPONSE)
        with patch("requests.get", return_value=mock_resp) as mock_get:
            client.get_place_details("ChIJabc123")
        call_kwargs = mock_get.call_args[1]
        assert "X-Goog-FieldMask" in call_kwargs["headers"]
        assert "X-Goog-Api-Key" in call_kwargs["headers"]


class TestSearchPlace:
    def test_returns_place_id_on_success(self):
        client = GBPClient(api_key="test-key-12345678")
        search_response = {"places": [{"id": "ChIJfound123"}]}
        with patch("requests.post", return_value=_make_mock_response(search_response)):
            result = client.search_place("ACME Plumbing Chicago")
        assert result == "ChIJfound123"

    def test_returns_none_on_empty_results(self):
        client = GBPClient(api_key="test-key-12345678")
        with patch("requests.post", return_value=_make_mock_response({"places": []})):
            result = client.search_place("nonexistent business")
        assert result is None

    def test_retries_without_bias_for_sab(self):
        """When location-biased search returns 0 results, retries without bias (SAB)."""
        client = GBPClient(api_key="test-key-12345678")
        empty = _make_mock_response({"places": []})
        found = _make_mock_response({"places": [{"id": "ChIJsab999"}]})
        with patch("requests.post", side_effect=[empty, found]):
            result = client.search_place("SAB Landscaping", location=(41.8, -87.6))
        assert result == "ChIJsab999"


class TestSearchPlaceWithFallback:
    def test_returns_gbp_data_from_search_result(self):
        client = GBPClient(api_key="test-key-12345678")
        search_response = {
            "places": [
                {
                    "id": "ChIJsab001",
                    "displayName": {"text": "SAB Landscaping Co"},
                    "formattedAddress": "Naperville, IL 60540, USA",
                    "rating": 4.8,
                }
            ]
        }
        with patch("requests.post", return_value=_make_mock_response(search_response)):
            result = client.search_place_with_fallback("SAB Landscaping Co")
        assert result is not None
        assert result.place_id == "ChIJsab001"
        assert result.business_name == "SAB Landscaping Co"
        assert result.city == "Naperville"
        assert result.state == "IL"
        assert result.rating == "4.8"

    def test_retries_without_bias_for_sab(self):
        client = GBPClient(api_key="test-key-12345678")
        empty = _make_mock_response({"places": []})
        found = _make_mock_response({
            "places": [{"id": "ChIJsab002", "displayName": {"text": "SAB Co"},
                        "formattedAddress": "Aurora, IL 60505, USA"}]
        })
        with patch("requests.post", side_effect=[empty, found]):
            result = client.search_place_with_fallback("SAB Co", location=(41.8, -88.3))
        assert result is not None
        assert result.city == "Aurora"

    def test_returns_none_on_no_results(self):
        client = GBPClient(api_key="test-key-12345678")
        with patch("requests.post", return_value=_make_mock_response({"places": []})):
            result = client.search_place_with_fallback("ghost business")
        assert result is None


class TestFetchSABEnrichment:
    def test_sab_city_enriched_when_details_sparse(self):
        """When place details lack city (SAB), fetch() enriches from search_place_with_fallback."""
        client = GBPClient(api_key="test-key-12345678")
        sparse_details = {
            "id": "ChIJsab123",
            "displayName": {"text": "SAB Lawn Co"},
            "location": {"latitude": 41.7, "longitude": -88.1},
            "addressComponents": [],
        }
        search_response = {
            "places": [
                {
                    "id": "ChIJsab123",
                    "displayName": {"text": "SAB Lawn Co"},
                    "formattedAddress": "Naperville, IL 60540, USA",
                }
            ]
        }
        with patch("requests.get") as mock_get, patch("requests.post") as mock_post:
            # resolve_share_link follows redirect then calls search_place for place_id
            resolve_resp = Mock()
            resolve_resp.url = "https://www.google.com/maps/place/SAB+Lawn+Co/@41.7,-88.1,15z"
            resolve_resp.ok = True
            # get_place_details call
            details_resp = _make_mock_response(sparse_details)
            mock_get.side_effect = [resolve_resp, details_resp]
            # search_place (for place_id) returns ChIJsab123, then search_place_with_fallback
            place_id_resp = _make_mock_response({"places": [{"id": "ChIJsab123"}]})
            fallback_resp = _make_mock_response(search_response)
            mock_post.side_effect = [place_id_resp, fallback_resp]
            result = client.fetch("https://maps.app.goo.gl/sab123")
        assert result is not None
        assert result.business_name == "SAB Lawn Co"
        assert result.city == "Naperville"
        assert result.state == "IL"


class TestFormatHelpers:
    def test_format_hhmm_am(self):
        client = GBPClient(api_key="test-key")
        assert client._format_hhmm(8, 0) == "8:00 AM"
        assert client._format_hhmm(9, 30) == "9:30 AM"

    def test_format_hhmm_pm(self):
        client = GBPClient(api_key="test-key")
        assert client._format_hhmm(17, 0) == "5:00 PM"
        assert client._format_hhmm(14, 0) == "2:00 PM"

    def test_format_hhmm_midnight(self):
        client = GBPClient(api_key="test-key")
        assert client._format_hhmm(0, 0) == "12:00 AM"

    def test_format_hhmm_noon(self):
        client = GBPClient(api_key="test-key")
        assert client._format_hhmm(12, 0) == "12:00 PM"

    def test_format_time_legacy(self):
        """_format_time kept for backwards compatibility."""
        client = GBPClient(api_key="test-key")
        assert client._format_time("0900") == "9:00 AM"
        assert client._format_time("1700") == "5:00 PM"
        assert client._format_time("") == ""
