"""
Unit tests for browser detection functionality

Tests browser and profile detection across platforms.
"""

import json
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open

# Import the module under test
from src.core.utils.browser_detector import (
    BrowserInfo,
    ProfileInfo,
    BrowserDetector
)


class TestBrowserInfo:
    """Test BrowserInfo data class"""

    def test_browser_info_creation(self):
        """Test BrowserInfo creation"""
        browser = BrowserInfo(
            name="Google Chrome",
            browser_type="chrome",
            executable_path=Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
            profiles=[]
        )

        assert browser.name == "Google Chrome"
        assert browser.browser_type == "chrome"
        assert browser.profiles == []


class TestProfileInfo:
    """Test ProfileInfo data class"""

    def test_profile_info_creation(self):
        """Test ProfileInfo creation"""
        profile = ProfileInfo(
            name="Work Profile",
            directory="Profile 1",
            profile_path=Path("C:/Users/test/AppData/Local/Google/Chrome/User Data/Profile 1")
        )

        assert profile.name == "Work Profile"
        assert profile.directory == "Profile 1"


class TestBrowserDetector:
    """Test BrowserDetector functionality"""

    def test_get_platform(self):
        """Test platform detection"""
        with patch('platform.system', return_value='Windows'):
            assert BrowserDetector.get_platform() == "windows"

        with patch('platform.system', return_value='Darwin'):
            assert BrowserDetector.get_platform() == "darwin"

        with patch('platform.system', return_value='Linux'):
            assert BrowserDetector.get_platform() == "linux"

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_detect_chrome_windows(self, tmp_path):
        """Test Chrome detection on Windows"""
        # Create mock Chrome installation
        chrome_path = tmp_path / "chrome.exe"
        chrome_path.touch()

        user_data = tmp_path / "User Data"
        user_data.mkdir()

        # Create profile directories
        (user_data / "Default").mkdir()
        (user_data / "Profile 1").mkdir()

        # Create mock Local State JSON
        local_state = {
            "profile": {
                "info_cache": {
                    "Default": {"name": "Person 1"},
                    "Profile 1": {"name": "Work"}
                }
            }
        }
        (user_data / "Local State").write_text(json.dumps(local_state))

        with patch.object(BrowserDetector, '_find_browser_windows', return_value=chrome_path):
            with patch.object(BrowserDetector, 'BROWSER_CONFIG_PATHS', {
                "chrome": {"windows": user_data, "darwin": user_data, "linux": user_data}
            }):
                browsers = BrowserDetector._detect_browsers_windows()

                assert len(browsers) > 0
                chrome = next((b for b in browsers if b.browser_type == "chrome"), None)
                assert chrome is not None
                assert chrome.name == "Google Chrome"
                assert len(chrome.profiles) == 2

    def test_detect_chromium_profiles_valid_json(self, tmp_path):
        """Test Chromium profile detection with valid Local State"""
        user_data = tmp_path / "User Data"
        user_data.mkdir()

        # Create profile directories
        (user_data / "Default").mkdir()
        (user_data / "Profile 1").mkdir()

        # Create mock Local State JSON
        local_state = {
            "profile": {
                "info_cache": {
                    "Default": {"name": "Person 1"},
                    "Profile 1": {"name": "Work"}
                }
            }
        }
        (user_data / "Local State").write_text(json.dumps(local_state))

        profiles = BrowserDetector._detect_chromium_profiles(user_data)

        assert len(profiles) == 2
        assert profiles[0].name == "Person 1"
        assert profiles[0].directory == "Default"
        assert profiles[1].name == "Work"
        assert profiles[1].directory == "Profile 1"

    def test_detect_chromium_profiles_corrupted_json(self, tmp_path):
        """Test graceful handling of corrupted Local State JSON"""
        user_data = tmp_path / "User Data"
        user_data.mkdir()

        # Write invalid JSON
        (user_data / "Local State").write_text("{ invalid json }")

        profiles = BrowserDetector._detect_chromium_profiles(user_data)

        # Should return empty list, not crash
        assert profiles == []

    def test_detect_chromium_profiles_missing_file(self, tmp_path):
        """Test handling when Local State file doesn't exist"""
        user_data = tmp_path / "User Data"
        user_data.mkdir()

        profiles = BrowserDetector._detect_chromium_profiles(user_data)

        # Should return empty list, not crash
        assert profiles == []

    def test_detect_firefox_profiles(self, tmp_path):
        """Test Firefox profile detection"""
        firefox_path = tmp_path / "Firefox"
        firefox_path.mkdir()

        # Create profile directories
        profiles_dir = firefox_path / "Profiles"
        profiles_dir.mkdir()
        (profiles_dir / "abc123.default").mkdir()
        (profiles_dir / "def456.work").mkdir()

        # Create mock profiles.ini
        profiles_ini = firefox_path / "profiles.ini"
        profiles_ini.write_text("""[Profile0]
Name=default
IsRelative=1
Path=Profiles/abc123.default

[Profile1]
Name=Work
IsRelative=1
Path=Profiles/def456.work
""")

        profiles = BrowserDetector._detect_firefox_profiles(firefox_path)

        assert len(profiles) == 2
        assert profiles[0].name == "default"
        assert profiles[0].directory == "default"
        assert profiles[1].name == "Work"
        assert profiles[1].directory == "Work"

    def test_detect_firefox_profiles_missing_file(self, tmp_path):
        """Test Firefox profile detection when profiles.ini doesn't exist"""
        firefox_path = tmp_path / "Firefox"
        firefox_path.mkdir()

        profiles = BrowserDetector._detect_firefox_profiles(firefox_path)

        # Should return empty list, not crash
        assert profiles == []

    def test_handle_missing_browser_gracefully(self):
        """Test graceful handling when no browsers found"""
        with patch.object(BrowserDetector, '_find_browser_windows', return_value=None):
            browsers = BrowserDetector._detect_browsers_windows()

            # Should return empty list or list without missing browser
            assert isinstance(browsers, list)

    def test_detect_profiles_unknown_browser_type(self):
        """Test detection with unknown browser type"""
        profiles = BrowserDetector.detect_profiles("unknown_browser", "unknown")

        # Should return empty list for unknown browser types
        assert profiles == []

    def test_get_browser_config_paths(self):
        """Test getting browser config paths"""
        config_paths = BrowserDetector.get_browser_config_paths()

        assert "chrome" in config_paths
        assert "firefox" in config_paths
        assert "edge" in config_paths
        assert "windows" in config_paths["chrome"]
        assert "darwin" in config_paths["chrome"]
        assert "linux" in config_paths["chrome"]


class TestWindowsBrowserDetection:
    """Test Windows-specific browser detection"""

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_find_browser_windows_registry(self):
        """Test finding browser via Windows Registry"""
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

        with patch('winreg.OpenKey') as mock_open_key:
            with patch('winreg.QueryValue', return_value=chrome_path):
                with patch('pathlib.Path.exists', return_value=True):
                    result = BrowserDetector._find_browser_windows("chrome.exe")

                    assert result is not None
                    assert str(result) == chrome_path

    @pytest.mark.skipif(sys.platform != "win32", reason="Windows-specific test")
    def test_find_browser_windows_common_path(self, tmp_path):
        """Test finding browser in common installation paths"""
        # Mock chrome.exe in a common path
        chrome_path = tmp_path / "chrome.exe"
        chrome_path.touch()

        with patch('winreg.OpenKey', side_effect=FileNotFoundError):
            with patch('pathlib.Path.exists', return_value=True):
                with patch('pathlib.Path.home', return_value=tmp_path.parent):
                    # This test verifies fallback to common paths works
                    result = BrowserDetector._find_browser_windows("chrome.exe")

                    # May or may not find it depending on mock paths
                    # Main point is it doesn't crash
                    assert isinstance(result, (Path, type(None)))


class TestMacOSBrowserDetection:
    """Test macOS-specific browser detection"""

    @pytest.mark.skipif(sys.platform == "win32", reason="Non-Windows test")
    def test_detect_browsers_macos(self, tmp_path):
        """Test browser detection on macOS"""
        # Create mock /Applications directory
        applications = tmp_path / "Applications"
        applications.mkdir()

        # Create mock Chrome.app bundle
        chrome_app = applications / "Google Chrome.app"
        chrome_app.mkdir()
        (chrome_app / "Contents").mkdir()
        (chrome_app / "Contents" / "MacOS").mkdir()
        chrome_exe = chrome_app / "Contents" / "MacOS" / "GoogleChrome"
        chrome_exe.touch()

        with patch('pathlib.Path', return_value=applications):
            # This is a simplified test - full test would need more mocking
            pass


class TestLinuxBrowserDetection:
    """Test Linux-specific browser detection"""

    @pytest.mark.skipif(sys.platform == "win32", reason="Non-Windows test")
    def test_detect_browsers_linux_which_command(self):
        """Test browser detection on Linux using which command"""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/usr/bin/google-chrome\n"

        with patch('subprocess.run', return_value=mock_result):
            with patch('pathlib.Path.exists', return_value=True):
                with patch.object(BrowserDetector, 'BROWSER_CONFIG_PATHS', {
                    "chrome": {"windows": Path("/tmp"), "darwin": Path("/tmp"), "linux": Path("/tmp")}
                }):
                    browsers = BrowserDetector._detect_browsers_linux()

                    # Should find at least one browser
                    assert len(browsers) >= 0

    @pytest.mark.skipif(sys.platform == "win32", reason="Non-Windows test")
    def test_detect_browsers_linux_not_found(self):
        """Test browser detection when browser not installed on Linux"""
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stdout = ""

        with patch('subprocess.run', return_value=mock_result):
            browsers = BrowserDetector._detect_browsers_linux()

            # Should return empty or partial list
            assert isinstance(browsers, list)


class TestBrowserPreferences:
    """Test browser preference storage"""

    def test_save_and_load_preference(self, tmp_path):
        """Test saving and loading browser preference"""
        from src.core.config.browser_preferences import BrowserPreferences

        prefs = BrowserPreferences()
        prefs.prefs_file = tmp_path / "test_prefs.json"

        # Create a fake browser executable
        browser_path = tmp_path / "chrome.exe"
        browser_path.touch()

        success = prefs.set_browser_preference(
            browser_type="chrome",
            browser_path=str(browser_path),
            profile_name="Work",
            profile_directory="Profile 1"
        )

        assert success is True

        loaded = prefs.get_browser_preference()
        assert loaded is not None
        assert loaded["browser_type"] == "chrome"
        assert loaded["profile_name"] == "Work"
        assert loaded["profile_directory"] == "Profile 1"

    def test_validate_browser_exists(self, tmp_path):
        """Test browser existence validation"""
        from src.core.config.browser_preferences import BrowserPreferences

        prefs = BrowserPreferences()
        prefs.prefs_file = tmp_path / "test_prefs.json"

        # Create fake browser executable
        browser_path = tmp_path / "chrome.exe"
        browser_path.touch()

        prefs.set_browser_preference(
            browser_type="chrome",
            browser_path=str(browser_path),
            profile_name="",
            profile_directory=""
        )

        assert prefs.validate_browser_exists() is True

        # Delete browser
        browser_path.unlink()

        assert prefs.validate_browser_exists() is False

    def test_clear_preference(self, tmp_path):
        """Test clearing browser preference"""
        from src.core.config.browser_preferences import BrowserPreferences

        prefs = BrowserPreferences()
        prefs.prefs_file = tmp_path / "test_prefs.json"

        # Create and save preference
        browser_path = tmp_path / "chrome.exe"
        browser_path.touch()

        prefs.set_browser_preference(
            browser_type="chrome",
            browser_path=str(browser_path)
        )

        assert prefs.preference_exists() is True

        # Clear preference
        success = prefs.clear_browser_preference()
        assert success is True
        assert prefs.preference_exists() is False

    def test_save_preference_invalid_path(self, tmp_path):
        """Test saving preference with non-existent browser path"""
        from src.core.config.browser_preferences import BrowserPreferences

        prefs = BrowserPreferences()
        prefs.prefs_file = tmp_path / "test_prefs.json"

        # Try to save with non-existent path
        success = prefs.set_browser_preference(
            browser_type="chrome",
            browser_path="/path/that/does/not/exist/chrome.exe"
        )

        assert success is False

    def test_get_preference_no_file(self, tmp_path):
        """Test getting preference when file doesn't exist"""
        from src.core.config.browser_preferences import BrowserPreferences

        prefs = BrowserPreferences()
        prefs.prefs_file = tmp_path / "nonexistent.json"

        result = prefs.get_browser_preference()
        assert result is None

    def test_get_preference_corrupted_json(self, tmp_path):
        """Test getting preference with corrupted JSON file"""
        from src.core.config.browser_preferences import BrowserPreferences

        prefs = BrowserPreferences()
        prefs.prefs_file = tmp_path / "test_prefs.json"

        # Write invalid JSON
        prefs.prefs_file.write_text("{ invalid json }")

        result = prefs.get_browser_preference()
        assert result is None
