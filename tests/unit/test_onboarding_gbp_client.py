"""
Tests for src/core/onboarding/gbp_client.py (Places API New) - v1.07

Covers: share link resolution, direct Place ID input, nearby search with name
validation, HTML Place ID extraction, name matching helpers, place details
parsing, hours parsing, SAB enrichment, and error handling.
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
    """Build a mock requests.Response for JSON endpoints."""
    mock = Mock()
    mock.ok = status_code < 400
    mock.status_code = status_code
    mock.json.return_value = data
    mock.text = str(data)
    return mock


def _make_html_response(html: str, status_code: int = 200):
    """Build a mock requests.Response for HTML endpoints."""
    mock = Mock()
    mock.ok = status_code < 400
    mock.status_code = status_code
    mock.text = html
    return mock


# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Place ID extraction from URL
# ---------------------------------------------------------------------------

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

    def test_does_not_return_ftid(self):
        """ftid is not a valid Place ID for Places API (New) - must not be returned."""
        client = GBPClient(api_key="test-key")
        url = "https://www.google.com/maps/place/Test+Biz?ftid=0xabc:0xdef"
        result = client._extract_place_id_from_url(url)
        assert result is None

    def test_extracts_name_from_maps_url(self):
        client = GBPClient(api_key="test-key")
        url = "https://www.google.com/maps/place/ACME+Plumbing+Co"
        name = client._extract_name_from_maps_url(url)
        assert "ACME" in name


# ---------------------------------------------------------------------------
# Direct Place ID input (v1.07)
# ---------------------------------------------------------------------------

class TestExtractNakedPlaceId:
    def test_returns_place_id_from_bare_input(self):
        client = GBPClient(api_key="test-key")
        result = client._extract_naked_place_id("ChIJabc123xyz789abcde")
        assert result == "ChIJabc123xyz789abcde"

    def test_returns_place_id_with_place_id_equals_prefix(self):
        client = GBPClient(api_key="test-key")
        result = client._extract_naked_place_id("place_id=ChIJabc123xyz789abcde")
        assert result == "ChIJabc123xyz789abcde"

    def test_returns_place_id_with_place_id_colon_prefix(self):
        client = GBPClient(api_key="test-key")
        result = client._extract_naked_place_id("place_id:ChIJabc123xyz789abcde")
        assert result == "ChIJabc123xyz789abcde"

    def test_returns_none_for_share_url(self):
        client = GBPClient(api_key="test-key")
        assert client._extract_naked_place_id("https://maps.app.goo.gl/abc123") is None

    def test_returns_none_for_empty(self):
        client = GBPClient(api_key="test-key")
        assert client._extract_naked_place_id("") is None

    def test_strips_surrounding_quotes(self):
        client = GBPClient(api_key="test-key")
        result = client._extract_naked_place_id('"ChIJabc123xyz789abcde"')
        assert result == "ChIJabc123xyz789abcde"

    def test_returns_none_for_short_chi_value(self):
        """Place IDs shorter than 10 chars after ChI are rejected."""
        client = GBPClient(api_key="test-key")
        assert client._extract_naked_place_id("ChIJshort") is None


class TestResolveShareLinkDirectPlaceId:
    def test_accepts_direct_place_id(self):
        client = GBPClient(api_key="test-key-12345678")
        result = client.resolve_share_link("ChIJabc123xyz789abcde")
        assert result == "ChIJabc123xyz789abcde"

    def test_bypasses_http_for_direct_place_id(self):
        """No network calls should occur when a bare Place ID is supplied."""
        client = GBPClient(api_key="test-key-12345678")
        with patch("requests.get") as mock_get:
            client.resolve_share_link("ChIJabc123xyz789abcde")
        mock_get.assert_not_called()


# ---------------------------------------------------------------------------
# Exact place coordinates from URL data block (v1.03)
# ---------------------------------------------------------------------------

class TestExtractPlaceCoordsFromUrl:
    def test_extracts_from_data_block(self):
        client = GBPClient(api_key="test-key")
        url = (
            "https://www.google.com/maps/place/Test/@46.499,-122.568,17z/"
            "data=!3m1!4b1!4m6!3m5!1s0xa!8m2!3d46.4990291!4d-122.5661186"
        )
        result = client._extract_place_coords_from_url(url)
        assert result == (46.4990291, -122.5661186)

    def test_returns_none_when_not_present(self):
        client = GBPClient(api_key="test-key")
        url = "https://www.google.com/maps/place/Test/@46.499,-122.568,17z"
        assert client._extract_place_coords_from_url(url) is None

    def test_handles_negative_coordinates(self):
        client = GBPClient(api_key="test-key")
        url = "https://maps/place/Test/@1,2,z/data=!8m2!3d-33.8688197!4d151.2092955"
        result = client._extract_place_coords_from_url(url)
        assert result == (-33.8688197, 151.2092955)


# ---------------------------------------------------------------------------
# HTML Place ID extraction (v1.06)
# ---------------------------------------------------------------------------

class TestExtractPlaceIdFromMapsHtml:
    def test_extracts_place_id_from_place_id_json_key(self):
        client = GBPClient(api_key="test-key")
        html = '..."place_id": "ChIJabc123xyz789abcde"...'
        with patch("requests.get", return_value=_make_html_response(html)):
            result = client._extract_place_id_from_maps_html("https://maps.google.com/url")
        assert result == "ChIJabc123xyz789abcde"

    def test_extracts_place_id_from_array_pattern(self):
        # Array pattern requires 20+ chars after "ChI" - use a realistic-length ID
        client = GBPClient(api_key="test-key")
        html = '...["ChIJabc123xyz789abcde01"]...'
        with patch("requests.get", return_value=_make_html_response(html)):
            result = client._extract_place_id_from_maps_html("https://maps.google.com/url")
        assert result == "ChIJabc123xyz789abcde01"

    def test_returns_none_when_no_place_id_in_html(self):
        client = GBPClient(api_key="test-key")
        with patch("requests.get", return_value=_make_html_response("<html>no id here</html>")):
            result = client._extract_place_id_from_maps_html("https://maps.google.com/url")
        assert result is None

    def test_returns_none_on_http_error(self):
        client = GBPClient(api_key="test-key")
        with patch("requests.get", return_value=_make_html_response("", status_code=403)):
            result = client._extract_place_id_from_maps_html("https://maps.google.com/url")
        assert result is None

    def test_returns_none_on_network_exception(self):
        client = GBPClient(api_key="test-key")
        with patch("requests.get", side_effect=Exception("timeout")):
            result = client._extract_place_id_from_maps_html("https://maps.google.com/url")
        assert result is None


# ---------------------------------------------------------------------------
# Nearby search with name validation (v1.03 - v1.05)
# ---------------------------------------------------------------------------

class TestSearchPlaceNearby:
    def _make_client(self):
        return GBPClient(api_key="test-key-12345678")

    def test_returns_place_id_without_expected_name(self):
        client = self._make_client()
        response = {"places": [{"id": "ChIJnear001", "displayName": {"text": "Nearby Biz"}}]}
        with patch("requests.post", return_value=_make_mock_response(response)):
            result = client.search_place_nearby((41.8, -87.6))
        assert result == "ChIJnear001"

    def test_returns_none_on_empty_results(self):
        client = self._make_client()
        with patch("requests.post", return_value=_make_mock_response({})):
            result = client.search_place_nearby((41.8, -87.6))
        assert result is None

    def test_validates_and_accepts_confident_name_match(self):
        client = self._make_client()
        response = {"places": [{"id": "ChIJmatch001", "displayName": {"text": "Rank Rocket Co"}}]}
        with patch("requests.post", return_value=_make_mock_response(response)):
            result = client.search_place_nearby((46.4, -122.5), expected_name="Rank Rocket")
        assert result == "ChIJmatch001"

    def test_rejects_unrelated_nearby_business(self):
        """Jewel-Osco must not be returned when looking for Camphouse Country Landscaping."""
        client = self._make_client()
        response = {"places": [{"id": "ChIJwrong", "displayName": {"text": "Jewel-Osco"}}]}
        with patch("requests.post", return_value=_make_mock_response(response)):
            result = client.search_place_nearby(
                (41.5, -87.9), expected_name="Camphouse Country Landscaping"
            )
        assert result is None

    def test_selects_best_match_among_multiple_results(self):
        client = self._make_client()
        response = {
            "places": [
                {"id": "ChIJwrong1", "displayName": {"text": "Starbucks"}},
                {"id": "ChIJcorrect", "displayName": {"text": "Rank Rocket SEO"}},
                {"id": "ChIJwrong2", "displayName": {"text": "McDonald's"}},
            ]
        }
        with patch("requests.post", return_value=_make_mock_response(response)):
            result = client.search_place_nearby((46.4, -122.5), expected_name="Rank Rocket")
        assert result == "ChIJcorrect"

    def test_retries_without_included_types_on_400(self):
        """When includedTypes causes a 400, retry without it."""
        client = self._make_client()
        fail_resp = _make_mock_response({}, status_code=400)
        success_resp = _make_mock_response(
            {"places": [{"id": "ChIJretry001", "displayName": {"text": "Test Biz"}}]}
        )
        with patch("requests.post", side_effect=[fail_resp, success_resp]):
            result = client.search_place_nearby((41.8, -87.6))
        assert result == "ChIJretry001"

    def test_returns_none_on_api_error_body(self):
        client = self._make_client()
        error_resp = _make_mock_response({"error": {"code": 403, "status": "PERMISSION_DENIED"}})
        with patch("requests.post", return_value=error_resp):
            result = client.search_place_nearby((41.8, -87.6))
        assert result is None

    def test_returns_none_on_network_exception(self):
        client = self._make_client()
        with patch("requests.post", side_effect=Exception("timeout")):
            result = client.search_place_nearby((41.8, -87.6))
        assert result is None


# ---------------------------------------------------------------------------
# Name matching helpers (v1.04 - v1.05)
# ---------------------------------------------------------------------------

class TestNameMatchingHelpers:
    def test_normalize_name_lowercases_and_strips_punctuation(self):
        client = GBPClient(api_key="test-key")
        assert client._normalize_name("Rank Rocket Co.") == "rank rocket co"

    def test_normalize_name_collapses_whitespace(self):
        client = GBPClient(api_key="test-key")
        assert client._normalize_name("  Spaces  Here  ") == "spaces here"

    def test_token_overlap_score_full_match(self):
        client = GBPClient(api_key="test-key")
        assert client._token_overlap_score("rank rocket", "rank rocket") == 1.0

    def test_token_overlap_score_no_match(self):
        client = GBPClient(api_key="test-key")
        assert client._token_overlap_score("rank rocket", "jewel osco") == 0.0

    def test_token_overlap_count_partial(self):
        client = GBPClient(api_key="test-key")
        count = client._token_overlap_count(
            "camphouse country landscaping", "camphouse landscaping services"
        )
        assert count == 2

    def test_is_confident_match_three_tokens_passes(self):
        client = GBPClient(api_key="test-key")
        assert client._is_confident_name_match("camphouse country landscaping", 0.8, 2) is True

    def test_is_confident_match_three_tokens_fails_low_overlap(self):
        client = GBPClient(api_key="test-key")
        assert client._is_confident_name_match("camphouse country landscaping", 0.8, 1) is False

    def test_is_confident_match_three_tokens_fails_low_score(self):
        client = GBPClient(api_key="test-key")
        assert client._is_confident_name_match("camphouse country landscaping", 0.4, 2) is False

    def test_is_confident_match_two_tokens_passes(self):
        client = GBPClient(api_key="test-key")
        assert client._is_confident_name_match("rank rocket", 0.7, 1) is True

    def test_is_confident_match_two_tokens_fails_low_score(self):
        client = GBPClient(api_key="test-key")
        assert client._is_confident_name_match("rank rocket", 0.5, 1) is False

    def test_is_confident_match_two_tokens_fails_zero_overlap(self):
        client = GBPClient(api_key="test-key")
        assert client._is_confident_name_match("rank rocket", 0.7, 0) is False

    def test_best_match_returns_highest_scoring_place(self):
        client = GBPClient(api_key="test-key")
        places = [
            {"id": "id1", "displayName": {"text": "Rank Rocket Co"}},
            {"id": "id2", "displayName": {"text": "Random Company"}},
        ]
        best, score, overlap = client._best_match_with_score(places, "Rank Rocket")
        assert best is not None
        assert best.get("id") == "id1"
        assert score > 0.0

    def test_best_match_returns_none_tuple_for_empty_list(self):
        client = GBPClient(api_key="test-key")
        best, score, overlap = client._best_match_with_score([], "Rank Rocket")
        assert best is None
        assert score == 0.0
        assert overlap == 0

    def test_pick_best_place_match_returns_dict(self):
        client = GBPClient(api_key="test-key")
        places = [{"id": "id1", "displayName": {"text": "Rank Rocket"}}]
        result = client._pick_best_place_match(places, "Rank Rocket")
        assert result is not None
        assert result.get("id") == "id1"


# ---------------------------------------------------------------------------
# Get Place Details
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Text search
# ---------------------------------------------------------------------------

class TestSearchPlace:
    def test_returns_place_id_on_success(self):
        client = GBPClient(api_key="test-key-12345678")
        search_response = {
            "places": [{"id": "ChIJfound123", "displayName": {"text": "ACME Plumbing Chicago"}}]
        }
        with patch("requests.post", return_value=_make_mock_response(search_response)):
            result = client.search_place("ACME Plumbing Chicago")
        assert result == "ChIJfound123"

    def test_returns_none_on_empty_results(self):
        client = GBPClient(api_key="test-key-12345678")
        with patch("requests.post", return_value=_make_mock_response({})):
            result = client.search_place("nonexistent business")
        assert result is None

    def test_retries_without_bias_for_sab(self):
        """When location-biased search returns 0 results, retries without bias (SAB)."""
        client = GBPClient(api_key="test-key-12345678")
        empty = _make_mock_response({})
        found = _make_mock_response(
            {"places": [{"id": "ChIJsab999", "displayName": {"text": "SAB Landscaping"}}]}
        )
        with patch("requests.post", side_effect=[empty, found]):
            result = client.search_place("SAB Landscaping", location=(41.8, -87.6))
        assert result == "ChIJsab999"

    def test_selects_best_match_by_name_score(self):
        client = GBPClient(api_key="test-key-12345678")
        response = {
            "places": [
                {"id": "ChIJwrong", "displayName": {"text": "ACME Hardware Store"}},
                {"id": "ChIJright", "displayName": {"text": "ACME Plumbing Co"}},
            ]
        }
        with patch("requests.post", return_value=_make_mock_response(response)):
            result = client.search_place("ACME Plumbing")
        assert result == "ChIJright"


# ---------------------------------------------------------------------------
# Search with fallback (SAB address recovery)
# ---------------------------------------------------------------------------

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
        empty = _make_mock_response({})
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
        with patch("requests.post", return_value=_make_mock_response({})):
            result = client.search_place_with_fallback("ghost business")
        assert result is None


# ---------------------------------------------------------------------------
# SAB enrichment via fetch()
# ---------------------------------------------------------------------------

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
            # GET 1: follow redirect
            resolve_resp = Mock()
            resolve_resp.url = "https://www.google.com/maps/place/SAB+Lawn+Co/@41.7,-88.1,15z"
            resolve_resp.ok = True
            # GET 2: HTML extraction attempt (no ChI found)
            html_resp = _make_html_response("<html>no place id here</html>")
            # GET 3: get_place_details
            details_resp = _make_mock_response(sparse_details)
            mock_get.side_effect = [resolve_resp, html_resp, details_resp]

            # POST 1: search_place for Place ID resolution
            place_id_resp = _make_mock_response(
                {"places": [{"id": "ChIJsab123", "displayName": {"text": "SAB Lawn Co"}}]}
            )
            # POST 2: search_place_with_fallback for SAB address enrichment
            fallback_resp = _make_mock_response(search_response)
            mock_post.side_effect = [place_id_resp, fallback_resp]

            result = client.fetch("https://maps.app.goo.gl/sab123")

        assert result is not None
        assert result.business_name == "SAB Lawn Co"
        assert result.city == "Naperville"
        assert result.state == "IL"


# ---------------------------------------------------------------------------
# Format helpers
# ---------------------------------------------------------------------------

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
