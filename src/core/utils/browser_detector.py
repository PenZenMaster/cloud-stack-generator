"""
Module: browser_detector.py
Path: E:/projects/cloud-stack-generator/src/core/utils/browser_detector.py

Description:
Cross-platform browser and profile detection for OAuth authentication.
Detects installed browsers (Chrome, Firefox, Edge, Brave, Opera, Vivaldi)
and their user profiles on Windows, macOS, and Linux.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date: 2026-01-14
Last Modified Date: 2026-01-14

Version: 1.0.0
"""

import json
import platform
import subprocess
import sys
from configparser import ConfigParser
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

# Windows-specific imports
if sys.platform == "win32":
    import winreg


@dataclass
class ProfileInfo:
    """Browser profile information"""

    name: str  # Profile display name (e.g., "Work Profile", "Personal")
    directory: str  # Profile directory identifier (e.g., "Profile 1", "default")
    profile_path: Path  # Full path to profile directory


@dataclass
class BrowserInfo:
    """Browser information"""

    name: str  # Display name (e.g., "Google Chrome")
    browser_type: str  # Type identifier (e.g., "chrome", "firefox", "edge")
    executable_path: Path  # Full path to browser executable
    profiles: List[ProfileInfo] = field(default_factory=list)  # Available profiles


class BrowserDetector:
    """Cross-platform browser detection"""

    # Browser configuration paths per platform
    BROWSER_CONFIG_PATHS = {
        "chrome": {
            "windows": Path.home() / "AppData" / "Local" / "Google" / "Chrome" / "User Data",
            "darwin": Path.home() / "Library" / "Application Support" / "Google" / "Chrome",
            "linux": Path.home() / ".config" / "google-chrome",
        },
        "edge": {
            "windows": Path.home() / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data",
            "darwin": Path.home() / "Library" / "Application Support" / "Microsoft Edge",
            "linux": Path.home() / ".config" / "microsoft-edge",
        },
        "brave": {
            "windows": Path.home() / "AppData" / "Local" / "BraveSoftware" / "Brave-Browser" / "User Data",
            "darwin": Path.home() / "Library" / "Application Support" / "BraveSoftware" / "Brave-Browser",
            "linux": Path.home() / ".config" / "BraveSoftware" / "Brave-Browser",
        },
        "opera": {
            "windows": Path.home() / "AppData" / "Roaming" / "Opera Software" / "Opera Stable",
            "darwin": Path.home() / "Library" / "Application Support" / "com.operasoftware.Opera",
            "linux": Path.home() / ".config" / "opera",
        },
        "vivaldi": {
            "windows": Path.home() / "AppData" / "Local" / "Vivaldi" / "User Data",
            "darwin": Path.home() / "Library" / "Application Support" / "Vivaldi",
            "linux": Path.home() / ".config" / "vivaldi",
        },
        "firefox": {
            "windows": Path.home() / "AppData" / "Roaming" / "Mozilla" / "Firefox",
            "darwin": Path.home() / "Library" / "Application Support" / "Firefox",
            "linux": Path.home() / ".mozilla" / "firefox",
        },
    }

    @staticmethod
    def get_platform() -> str:
        """Get current platform identifier"""
        system = platform.system().lower()
        if system == "darwin":
            return "darwin"
        elif system == "windows":
            return "windows"
        else:
            return "linux"

    @staticmethod
    def detect_installed_browsers() -> List[BrowserInfo]:
        """
        Detect all installed browsers on the system.

        Returns:
            List of BrowserInfo objects with detected browsers
        """
        browsers = []
        current_platform = BrowserDetector.get_platform()

        if current_platform == "windows":
            browsers.extend(BrowserDetector._detect_browsers_windows())
        elif current_platform == "darwin":
            browsers.extend(BrowserDetector._detect_browsers_macos())
        else:
            browsers.extend(BrowserDetector._detect_browsers_linux())

        return browsers

    @staticmethod
    def _detect_browsers_windows() -> List[BrowserInfo]:
        """Detect browsers on Windows"""
        browsers = []

        # Browser definitions: (name, type, executable_name, display_name)
        browser_defs = [
            ("chrome", "chrome.exe", "Google Chrome"),
            ("firefox", "firefox.exe", "Mozilla Firefox"),
            ("edge", "msedge.exe", "Microsoft Edge"),
            ("brave", "brave.exe", "Brave Browser"),
            ("opera", "opera.exe", "Opera"),
            ("vivaldi", "vivaldi.exe", "Vivaldi"),
        ]

        for browser_type, exe_name, display_name in browser_defs:
            try:
                # Try to find browser executable
                exe_path = BrowserDetector._find_browser_windows(exe_name)
                if exe_path and exe_path.exists():
                    # Detect profiles
                    profiles = BrowserDetector.detect_profiles(browser_type, browser_type)

                    browser_info = BrowserInfo(
                        name=display_name,
                        browser_type=browser_type,
                        executable_path=exe_path,
                        profiles=profiles
                    )
                    browsers.append(browser_info)
            except Exception as e:
                # Log warning but continue with other browsers
                print(f"Warning: Failed to detect {display_name}: {e}")
                continue

        return browsers

    @staticmethod
    def _find_browser_windows(exe_name: str) -> Optional[Path]:
        """Find browser executable on Windows using Registry and common paths"""
        # Try Windows Registry first
        try:
            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\\" + exe_name
            ) as key:
                path_value = winreg.QueryValue(key, None)
                if path_value:
                    exe_path = Path(path_value)
                    if exe_path.exists():
                        return exe_path
        except (FileNotFoundError, OSError):
            pass

        # Try common installation paths
        common_paths = [
            Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
            Path(r"C:\Program Files\Mozilla Firefox\firefox.exe"),
            Path(r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"),
            Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
            Path.home() / r"AppData\Local\Programs\Opera\opera.exe",
            Path.home() / r"AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe",
            Path.home() / r"AppData\Local\Vivaldi\Application\vivaldi.exe",
        ]

        for path in common_paths:
            if path.name.lower() == exe_name.lower() and path.exists():
                return path

        return None

    @staticmethod
    def _detect_browsers_macos() -> List[BrowserInfo]:
        """Detect browsers on macOS"""
        browsers = []

        # Browser definitions: (name, bundle_name, display_name)
        browser_defs = [
            ("chrome", "Google Chrome.app", "Google Chrome"),
            ("firefox", "Firefox.app", "Mozilla Firefox"),
            ("edge", "Microsoft Edge.app", "Microsoft Edge"),
            ("brave", "Brave Browser.app", "Brave Browser"),
            ("opera", "Opera.app", "Opera"),
            ("vivaldi", "Vivaldi.app", "Vivaldi"),
        ]

        applications_dir = Path("/Applications")

        for browser_type, bundle_name, display_name in browser_defs:
            try:
                bundle_path = applications_dir / bundle_name
                if bundle_path.exists():
                    # macOS app bundle executable is at Contents/MacOS/<name>
                    exe_name = bundle_name.replace(".app", "")
                    exe_path = bundle_path / "Contents" / "MacOS" / exe_name.replace(" Browser", "").replace(" ", "")

                    if not exe_path.exists():
                        # Try without spaces
                        exe_path = bundle_path / "Contents" / "MacOS" / exe_name.replace(" ", "")

                    if exe_path.exists():
                        # Detect profiles
                        profiles = BrowserDetector.detect_profiles(browser_type, browser_type)

                        browser_info = BrowserInfo(
                            name=display_name,
                            browser_type=browser_type,
                            executable_path=exe_path,
                            profiles=profiles
                        )
                        browsers.append(browser_info)
            except Exception as e:
                print(f"Warning: Failed to detect {display_name}: {e}")
                continue

        return browsers

    @staticmethod
    def _detect_browsers_linux() -> List[BrowserInfo]:
        """Detect browsers on Linux"""
        browsers = []

        # Browser definitions: (type, command_name, display_name)
        browser_defs = [
            ("chrome", "google-chrome", "Google Chrome"),
            ("firefox", "firefox", "Mozilla Firefox"),
            ("edge", "microsoft-edge", "Microsoft Edge"),
            ("brave", "brave-browser", "Brave Browser"),
            ("opera", "opera", "Opera"),
            ("vivaldi", "vivaldi", "Vivaldi"),
        ]

        for browser_type, command_name, display_name in browser_defs:
            try:
                # Use 'which' to find executable
                result = subprocess.run(
                    ["which", command_name],
                    capture_output=True,
                    text=True,
                    timeout=2
                )

                if result.returncode == 0 and result.stdout.strip():
                    exe_path = Path(result.stdout.strip())
                    if exe_path.exists():
                        # Detect profiles
                        profiles = BrowserDetector.detect_profiles(browser_type, browser_type)

                        browser_info = BrowserInfo(
                            name=display_name,
                            browser_type=browser_type,
                            executable_path=exe_path,
                            profiles=profiles
                        )
                        browsers.append(browser_info)
            except Exception as e:
                print(f"Warning: Failed to detect {display_name}: {e}")
                continue

        return browsers

    @staticmethod
    def detect_profiles(browser_type: str, browser_identifier: str) -> List[ProfileInfo]:
        """
        Detect browser profiles for a specific browser.

        Args:
            browser_type: Type of browser (chrome, firefox, edge, etc.)
            browser_identifier: Browser identifier (usually same as browser_type)

        Returns:
            List of ProfileInfo objects
        """
        current_platform = BrowserDetector.get_platform()

        # Get config path for this browser and platform
        if browser_type not in BrowserDetector.BROWSER_CONFIG_PATHS:
            return []

        config_path = BrowserDetector.BROWSER_CONFIG_PATHS[browser_type].get(current_platform)
        if not config_path or not config_path.exists():
            return []

        # Firefox uses different profile detection
        if browser_type == "firefox":
            return BrowserDetector._detect_firefox_profiles(config_path)
        else:
            # Chromium-based browsers (Chrome, Edge, Brave, Opera, Vivaldi)
            return BrowserDetector._detect_chromium_profiles(config_path)

    @staticmethod
    def _detect_chromium_profiles(user_data_path: Path) -> List[ProfileInfo]:
        """Detect profiles for Chromium-based browsers"""
        profiles = []

        try:
            # Read Local State JSON file
            local_state_file = user_data_path / "Local State"
            if not local_state_file.exists():
                return profiles

            with open(local_state_file, 'r', encoding='utf-8') as f:
                local_state = json.load(f)

            # Get profile info cache
            profile_cache = local_state.get("profile", {}).get("info_cache", {})

            for profile_dir, profile_data in profile_cache.items():
                profile_name = profile_data.get("name", profile_dir)
                profile_path = user_data_path / profile_dir

                if profile_path.exists():
                    profile_info = ProfileInfo(
                        name=profile_name,
                        directory=profile_dir,
                        profile_path=profile_path
                    )
                    profiles.append(profile_info)

        except (json.JSONDecodeError, KeyError, FileNotFoundError) as e:
            # Log warning but don't crash
            print(f"Warning: Failed to parse Chromium profiles: {e}")

        return profiles

    @staticmethod
    def _detect_firefox_profiles(firefox_path: Path) -> List[ProfileInfo]:
        """Detect profiles for Firefox"""
        profiles = []

        try:
            # Read profiles.ini file
            profiles_ini_file = firefox_path / "profiles.ini"
            if not profiles_ini_file.exists():
                return profiles

            config = ConfigParser()
            config.read(profiles_ini_file)

            # Parse profile sections
            for section in config.sections():
                if section.startswith("Profile"):
                    profile_name = config.get(section, "Name", fallback=section)
                    profile_path_str = config.get(section, "Path", fallback="")
                    is_relative = config.getint(section, "IsRelative", fallback=1)

                    if profile_path_str:
                        # Construct full profile path
                        if is_relative:
                            profile_path = firefox_path / profile_path_str
                        else:
                            profile_path = Path(profile_path_str)

                        if profile_path.exists():
                            profile_info = ProfileInfo(
                                name=profile_name,
                                directory=profile_name,  # Firefox uses name as identifier
                                profile_path=profile_path
                            )
                            profiles.append(profile_info)

        except Exception as e:
            # Log warning but don't crash
            print(f"Warning: Failed to parse Firefox profiles: {e}")

        return profiles

    @staticmethod
    def get_browser_config_paths() -> Dict[str, Dict[str, Path]]:
        """
        Get platform-specific browser configuration paths.

        Returns:
            Dict mapping browser types to platform-specific paths
        """
        return BrowserDetector.BROWSER_CONFIG_PATHS.copy()
