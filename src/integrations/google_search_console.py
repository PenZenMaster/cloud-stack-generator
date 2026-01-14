"""
Module/Script Name: Google Search Console API Client
Path: src/integrations/google_search_console.py

Description:
Wrapper for Google Site Verification API to programmatically retrieve
and manage Google verification meta tags for deployed websites.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-12-20

Last Modified Date:
2025-12-20

Comments:
* v1.00 - Initial implementation with OAuth, token retrieval, and verification
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List, Dict
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# Scope for managing site verification
SCOPES = ["https://www.googleapis.com/auth/siteverification"]


class GoogleSearchConsoleClient:
    """
    Client for Google Site Verification API

    Handles OAuth authentication, token retrieval, and site verification
    for Google Search Console integration.
    """

    def __init__(self, credentials_file: str = "credentials.json"):
        """
        Initialize GSC client with OAuth credentials

        Args:
            credentials_file: Path to OAuth credentials JSON file
        """
        self.credentials_file = credentials_file
        self.token_file = self._get_token_path()
        self.creds: Optional[Credentials] = None
        self.service = None

    def _get_token_path(self) -> Path:
        """
        Get path to token storage file in user's config directory

        Returns:
            Path to token file
        """
        config_dir = Path.home() / ".config" / "cloud-stack-generator"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "gsc_token.json"

    def authenticate(self) -> Tuple[bool, Optional[str]]:
        """
        Run OAuth flow and return success status

        Returns:
            (success, error_message)
        """
        try:
            # Load existing token if available
            if self.token_file.exists():
                self.creds = Credentials.from_authorized_user_file(
                    str(self.token_file), SCOPES
                )

            # Refresh or run OAuth flow
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    try:
                        self.creds.refresh(Request())
                    except Exception as refresh_error:
                        # Handle invalid_grant error (token expired/revoked)
                        if "invalid_grant" in str(refresh_error).lower():
                            # Delete invalid token file
                            if self.token_file.exists():
                                self.token_file.unlink()
                            # Reset credentials to force re-authentication
                            self.creds = None
                            # Re-run OAuth flow
                            if not os.path.exists(self.credentials_file):
                                return False, f"Credentials file not found: {self.credentials_file}"

                            flow = InstalledAppFlow.from_client_secrets_file(
                                self.credentials_file, SCOPES
                            )
                            self.creds = flow.run_local_server(port=0)
                        else:
                            # Re-raise other refresh errors
                            raise
                else:
                    if not os.path.exists(self.credentials_file):
                        return False, f"Credentials file not found: {self.credentials_file}"

                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)

                # Save credentials for next run
                with open(self.token_file, "w") as token:
                    token.write(self.creds.to_json())

            # Build service
            self.service = build("siteVerification", "v1", credentials=self.creds)
            return True, None

        except FileNotFoundError as e:
            return False, f"File not found: {str(e)}"
        except Exception as e:
            return False, f"Authentication failed: {str(e)}"

    def is_authenticated(self) -> bool:
        """
        Check if client is currently authenticated

        Returns:
            True if authenticated, False otherwise
        """
        return self.creds is not None and self.creds.valid

    def get_verification_token(
        self,
        site_url: str,
        method: str = "META"
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Request verification token from GSC API

        Args:
            site_url: Full URL (e.g., "https://example.com/")
            method: "META", "FILE", or "DNS_TXT"

        Returns:
            (token, meta_tag_html, error_message)

        Examples:
            token: "abc123def456"
            meta_tag_html: '<meta name="google-site-verification" content="abc123def456" />'
        """
        if not self.is_authenticated():
            return None, None, "Not authenticated. Please authenticate first."

        try:
            # Ensure URL ends with /
            if not site_url.endswith("/"):
                site_url += "/"

            # Request token
            token_request_body = {
                "site": {
                    "identifier": site_url,
                    "type": "SITE"  # or "INET_DOMAIN" for domain-level
                },
                "verificationMethod": method
            }

            token_response = self.service.webResource().getToken(
                body=token_request_body
            ).execute()

            token = token_response.get("token", "")

            # Construct meta tag HTML
            if method == "META":
                meta_tag_html = f'<meta name="google-site-verification" content="{token}" />'
            else:
                meta_tag_html = None

            return token, meta_tag_html, None

        except HttpError as e:
            error_msg = f"API Error: {e.resp.status} - {e.error_details}"
            return None, None, error_msg
        except Exception as e:
            return None, None, f"Error retrieving token: {str(e)}"

    def verify_site(
        self,
        site_url: str,
        method: str = "META"
    ) -> Tuple[bool, Optional[str]]:
        """
        Attempt to verify site ownership

        Args:
            site_url: Full URL (e.g., "https://example.com/")
            method: "META", "FILE", or "DNS_TXT"

        Returns:
            (success, error_message)
        """
        if not self.is_authenticated():
            return False, "Not authenticated. Please authenticate first."

        try:
            # Ensure URL ends with /
            if not site_url.endswith("/"):
                site_url += "/"

            # Attempt verification
            insert_body = {
                "site": {
                    "identifier": site_url,
                    "type": "SITE"
                }
            }

            self.service.webResource().insert(
                verificationMethod=method,
                body=insert_body
            ).execute()

            return True, None

        except HttpError as e:
            if e.resp.status == 400:
                error_msg = "Verification failed. Token may not be correctly placed on site."
            elif e.resp.status == 403:
                error_msg = "Permission denied. Check API access."
            elif e.resp.status == 429:
                error_msg = "API quota exceeded. Try again later."
            else:
                error_msg = f"API Error: {e.resp.status} - {e.error_details}"
            return False, error_msg
        except Exception as e:
            return False, f"Verification error: {str(e)}"

    def get_verified_sites(self) -> Tuple[Optional[List[Dict[str, str]]], Optional[str]]:
        """
        List all verified sites for authenticated user

        Returns:
            (sites_list, error_message)

        Example sites_list:
            [{"site_url": "https://example.com/", "verified_at": "2025-12-20T16:30:45Z"}, ...]
        """
        if not self.is_authenticated():
            return None, "Not authenticated. Please authenticate first."

        try:
            result = self.service.webResource().list().execute()
            sites = result.get("items", [])

            sites_list = []
            for site in sites:
                sites_list.append({
                    "site_url": site.get("site", {}).get("identifier", ""),
                    "verified_at": ""  # API doesn't provide verification timestamp
                })

            return sites_list, None

        except HttpError as e:
            error_msg = f"API Error: {e.resp.status} - {e.error_details}"
            return None, error_msg
        except Exception as e:
            return None, f"Error listing sites: {str(e)}"

    def check_token_reuse(
        self,
        token: str,
        config_dir: str = "config/clients"
    ) -> Tuple[bool, List[str]]:
        """
        Check if token is already used in any deployment

        Args:
            token: The verification code (e.g., "abc123def456")
            config_dir: Directory containing client YAML configs

        Returns:
            (is_duplicate, [list of deployment friendly names where used])
        """
        try:
            from pathlib import Path
            import yaml

            config_path = Path(config_dir)
            if not config_path.exists():
                return False, []

            duplicates = []

            # Iterate through all client config YAML files
            for yaml_file in config_path.glob("*.yaml"):
                try:
                    with open(yaml_file, "r", encoding="utf-8") as f:
                        config_data = yaml.safe_load(f)

                    if not config_data:
                        continue

                    # Check deployments section
                    deployments = config_data.get("deployments", [])
                    for deployment in deployments:
                        meta_tags = deployment.get("meta_tags", {})
                        google_token = meta_tags.get("google-site-verification", "")

                        if google_token == token:
                            friendly_name = deployment.get("friendly_name", deployment.get("deployment_id", "Unknown"))
                            last_deployed = deployment.get("last_deployed", "")
                            duplicates.append(f"{friendly_name} (deployed {last_deployed[:10] if last_deployed else 'unknown'})")

                except Exception:
                    # Skip files that can't be parsed
                    continue

            return len(duplicates) > 0, duplicates

        except Exception:
            # If error checking, assume no duplicates (fail open)
            return False, []
