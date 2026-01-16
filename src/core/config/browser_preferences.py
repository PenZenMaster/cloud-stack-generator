"""
Module: browser_preferences.py
Path: E:/projects/cloud-stack-generator/src/core/config/browser_preferences.py

Description:
Browser preference storage for OAuth authentication.
Stores user's selected browser and profile for Google Search Console OAuth flows.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date: 2026-01-14
Last Modified Date: 2026-01-14

Version: 1.0.0
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class BrowserPreferences:
    """Manage browser and profile preferences for OAuth flows"""

    def __init__(self):
        """
        Initialize browser preferences manager.

        Uses same storage pattern as APIKeyManager for consistency.
        """
        # Store preferences in user's local app data
        self.app_data_dir = Path.home() / ".cloud-stack-generator"
        self.prefs_file = self.app_data_dir / "browser_prefs.json"

        # Ensure directory exists
        self.app_data_dir.mkdir(exist_ok=True)

    def get_browser_preference(self) -> Optional[Dict[str, str]]:
        """
        Get saved browser preference.

        Returns:
            Dict with keys: browser_type, browser_path, profile_name, profile_directory
            None if no preference saved or file doesn't exist
        """
        if not self.prefs_file.exists():
            return None

        try:
            with open(self.prefs_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate required fields
            if not data.get("browser_type") or not data.get("browser_path"):
                return None

            return data

        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            print(f"Warning: Could not load browser preferences: {e}")
            return None

    def set_browser_preference(
        self,
        browser_type: str,
        browser_path: str,
        profile_name: str = "",
        profile_directory: str = ""
    ) -> bool:
        """
        Save browser preference with validation.

        Args:
            browser_type: Browser identifier (chrome, firefox, edge, etc.)
            browser_path: Full path to browser executable
            profile_name: Display name of profile (optional)
            profile_directory: Profile directory identifier (optional)

        Returns:
            True if saved successfully, False if validation failed
        """
        # Validate browser executable exists
        browser_path_obj = Path(browser_path)
        if not browser_path_obj.exists():
            print(f"Warning: Browser executable not found: {browser_path}")
            return False

        # Validate it's actually a file
        if not browser_path_obj.is_file():
            print(f"Warning: Browser path is not a file: {browser_path}")
            return False

        # Platform-specific executable validation
        if os.name == 'nt':  # Windows
            if not browser_path.lower().endswith('.exe'):
                print(f"Warning: Not a Windows executable: {browser_path}")
                return False

        # Create preference dictionary
        preference = {
            "browser_type": browser_type,
            "browser_path": browser_path,
            "profile_name": profile_name,
            "profile_directory": profile_directory
        }

        # Save to file
        try:
            with open(self.prefs_file, 'w', encoding='utf-8') as f:
                json.dump(preference, f, indent=2)

            # Set restrictive permissions (owner only) on Unix-like systems
            try:
                os.chmod(self.prefs_file, 0o600)
            except (OSError, AttributeError):
                # chmod may not work on Windows, that's okay
                pass

            return True

        except Exception as e:
            print(f"Error: Could not save browser preference: {e}")
            return False

    def clear_browser_preference(self) -> bool:
        """
        Clear saved browser preference by deleting the file.

        Returns:
            True if cleared successfully or file didn't exist
        """
        try:
            if self.prefs_file.exists():
                self.prefs_file.unlink()
            return True
        except Exception as e:
            print(f"Warning: Could not clear browser preference: {e}")
            return False

    def validate_browser_exists(self) -> bool:
        """
        Validate that saved browser executable still exists.

        Returns:
            True if browser exists, False if uninstalled/moved or no preference saved
        """
        preference = self.get_browser_preference()
        if not preference:
            return False

        browser_path = Path(preference.get("browser_path", ""))
        return browser_path.exists()

    def get_preference_file_path(self) -> Path:
        """
        Get the path to the preference file.

        Returns:
            Path to browser_prefs.json
        """
        return self.prefs_file

    def preference_exists(self) -> bool:
        """
        Check if a browser preference has been saved.

        Returns:
            True if preference file exists
        """
        return self.prefs_file.exists()
