"""
Unit tests for Google Search Console integration

Tests OAuth authentication, token refresh, and invalid_grant error handling.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, mock_open
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError


class TestGoogleSearchConsoleClient:
    """Test Google Search Console client authentication"""

    def test_authenticate_with_valid_token(self, tmp_path):
        """Test authentication with valid existing token"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        client.token_file = tmp_path / "test_token.json"

        # Create mock credentials
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = True
        mock_creds.expired = False

        with patch.object(
            Credentials, "from_authorized_user_file", return_value=mock_creds
        ):
            with patch("src.integrations.google_search_console.build") as mock_build:
                # Create token file
                client.token_file.write_text('{"token": "test"}')

                success, error = client.authenticate()

                assert success is True
                assert error is None
                assert client.creds == mock_creds
                mock_build.assert_called_once()

    def test_authenticate_with_expired_token_refresh_success(self, tmp_path):
        """Test successful token refresh when expired"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        client.token_file = tmp_path / "test_token.json"

        # Create mock expired credentials with refresh token
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token_123"

        with patch.object(
            Credentials, "from_authorized_user_file", return_value=mock_creds
        ):
            with patch("src.integrations.google_search_console.build") as mock_build:
                with patch("builtins.open", mock_open()):
                    # Create token file
                    client.token_file.write_text('{"token": "test"}')

                    # Mock successful refresh
                    def mock_refresh(request):
                        mock_creds.valid = True

                    mock_creds.refresh = MagicMock(side_effect=mock_refresh)

                    success, error = client.authenticate()

                    assert success is True
                    assert error is None
                    mock_creds.refresh.assert_called_once()
                    mock_build.assert_called_once()

    def test_authenticate_invalid_grant_auto_recovery(self, tmp_path):
        """Test automatic recovery from invalid_grant error"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        client.token_file = tmp_path / "test_token.json"
        client.credentials_file = "credentials.json"

        # Create mock expired credentials with refresh token
        mock_creds_expired = MagicMock(spec=Credentials)
        mock_creds_expired.valid = False
        mock_creds_expired.expired = True
        mock_creds_expired.refresh_token = "old_refresh_token"

        # Create mock new credentials from OAuth flow
        mock_creds_new = MagicMock(spec=Credentials)
        mock_creds_new.valid = True

        # Mock OAuth flow
        mock_flow = MagicMock()
        mock_flow.run_local_server.return_value = mock_creds_new

        with patch.object(
            Credentials, "from_authorized_user_file", return_value=mock_creds_expired
        ):
            with patch("src.integrations.google_search_console.build") as mock_build:
                with patch(
                    "src.integrations.google_search_console.InstalledAppFlow.from_client_secrets_file",
                    return_value=mock_flow,
                ):
                    with patch("os.path.exists", return_value=True):
                        with patch("builtins.open", mock_open()):
                            # Create token file
                            client.token_file.write_text('{"token": "test"}')

                            # Mock refresh raising invalid_grant error
                            refresh_error = RefreshError("invalid_grant: Token has been expired or revoked")
                            mock_creds_expired.refresh = MagicMock(
                                side_effect=refresh_error
                            )

                            success, error = client.authenticate()

                            # Should succeed after OAuth flow
                            assert success is True
                            assert error is None
                            # Token file should have been deleted and recreated
                            # OAuth flow should have been triggered
                            mock_flow.run_local_server.assert_called_once()
                            mock_build.assert_called_once()

    def test_authenticate_invalid_grant_deletes_token_file(self, tmp_path):
        """Test that invalid token file is deleted on invalid_grant"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        client.token_file = tmp_path / "test_token.json"
        client.credentials_file = "credentials.json"

        # Create token file
        client.token_file.write_text('{"token": "invalid"}')
        assert client.token_file.exists()

        # Create mock expired credentials
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"

        # Mock new credentials from OAuth flow
        mock_creds_new = MagicMock(spec=Credentials)
        mock_creds_new.valid = True

        # Mock OAuth flow
        mock_flow = MagicMock()
        mock_flow.run_local_server.return_value = mock_creds_new

        with patch.object(
            Credentials, "from_authorized_user_file", return_value=mock_creds
        ):
            with patch("src.integrations.google_search_console.build"):
                with patch(
                    "src.integrations.google_search_console.InstalledAppFlow.from_client_secrets_file",
                    return_value=mock_flow,
                ):
                    with patch("os.path.exists", return_value=True):
                        with patch("builtins.open", mock_open()):
                            # Mock refresh raising invalid_grant error
                            refresh_error = RefreshError("invalid_grant")
                            mock_creds.refresh = MagicMock(side_effect=refresh_error)

                            client.authenticate()

                            # Token file should have been deleted
                            assert not client.token_file.exists()

    def test_authenticate_other_refresh_error_not_caught(self, tmp_path):
        """Test that non-invalid_grant errors are properly raised"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        client.token_file = tmp_path / "test_token.json"

        # Create mock expired credentials
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh_token"

        with patch.object(
            Credentials, "from_authorized_user_file", return_value=mock_creds
        ):
            # Create token file
            client.token_file.write_text('{"token": "test"}')

            # Mock refresh raising non-invalid_grant error
            network_error = RefreshError("Network connection failed")
            mock_creds.refresh = MagicMock(side_effect=network_error)

            success, error = client.authenticate()

            # Should fail with error message
            assert success is False
            assert "Authentication failed" in error

    def test_authenticate_no_credentials_file(self, tmp_path):
        """Test authentication fails when credentials file missing"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        client.token_file = tmp_path / "test_token.json"
        client.credentials_file = "nonexistent_credentials.json"

        with patch("os.path.exists", return_value=False):
            success, error = client.authenticate()

            assert success is False
            assert "Credentials file not found" in error

    def test_authenticate_with_custom_browser(self, tmp_path):
        """Test authentication with custom browser selection"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient
        from src.core.utils.browser_detector import BrowserInfo, ProfileInfo
        from unittest.mock import MagicMock

        client = GoogleSearchConsoleClient()
        client.token_file = tmp_path / "test_token.json"
        client.credentials_file = "credentials.json"

        # Create mock browser info
        browser_info = BrowserInfo(
            name="Google Chrome",
            browser_type="chrome",
            executable_path=Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
            profiles=[]
        )

        with patch("os.path.exists", return_value=True):
            with patch('src.integrations.google_search_console.InstalledAppFlow') as mock_flow_class:
                mock_flow = MagicMock()
                mock_creds = MagicMock()
                mock_creds.valid = True
                mock_creds.to_json.return_value = '{"token": "test"}'
                mock_flow.run_local_server.return_value = mock_creds
                mock_flow_class.from_client_secrets_file.return_value = mock_flow

                with patch('src.integrations.google_search_console.build'):
                    with patch('builtins.open', mock_open()):
                        success, error = client.authenticate(
                            browser_info=browser_info,
                            profile_directory="Profile 1"
                        )

                        assert success is True
                        assert error is None

    def test_browser_launch_args_chrome(self):
        """Test Chrome browser launch arguments"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        args = client._get_browser_launch_args("chrome", "Profile 1")

        assert args == ["--profile-directory=Profile 1"]

    def test_browser_launch_args_firefox(self):
        """Test Firefox browser launch arguments"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        args = client._get_browser_launch_args("firefox", "work")

        assert args == ["-P", "work"]

    def test_browser_launch_args_no_profile(self):
        """Test browser launch arguments with no profile"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        args = client._get_browser_launch_args("chrome", "")

        assert args == []

    def test_browser_launch_args_unknown_browser(self):
        """Test browser launch arguments for unknown browser type"""
        from src.integrations.google_search_console import GoogleSearchConsoleClient

        client = GoogleSearchConsoleClient()
        args = client._get_browser_launch_args("unknown_browser", "profile")

        assert args == []
