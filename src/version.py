"""
Version Management System

This module manages application versioning and automatic version updates.

Version: 1.00
Author: Cloud Stack Generator Team
"""

from pathlib import Path
from datetime import datetime
import re
from src.core.utils.logger import get_logger

logger = get_logger(__name__)


class VersionManager:
    """Manages application version and automatic updates"""
    
    def __init__(self, main_file_path: Path = None):
        """
        Initialize version manager
        
        Args:
            main_file_path: Path to main.py file (default: auto-detect)
        """
        if main_file_path is None:
            main_file_path = Path(__file__).parent.parent / "main.py"
        
        self.main_file_path = Path(main_file_path)
        self.current_version = self._parse_current_version()
    
    def _parse_current_version(self) -> str:
        """Parse current version from main.py"""
        try:
            with open(self.main_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for version pattern like "Version: 2.0.1"
            version_match = re.search(r'Version:\s*(\d+\.\d+\.\d+)', content)
            if version_match:
                return version_match.group(1)
            
            return "2.0.1"  # Default fallback
            
        except Exception as e:
            logger.warning(f"Could not parse version from main.py: {e}")
            return "2.0.1"
    
    def increment_patch_version(self) -> str:
        """Increment patch version (e.g., 2.0.1 -> 2.0.2)"""
        try:
            major, minor, patch = map(int, self.current_version.split('.'))
            new_version = f"{major}.{minor}.{patch + 1}"
            return new_version
        except Exception as e:
            logger.error(f"Error incrementing version: {e}")
            return self.current_version
    
    def increment_minor_version(self) -> str:
        """Increment minor version (e.g., 2.0.1 -> 2.1.0)"""
        try:
            major, minor, patch = map(int, self.current_version.split('.'))
            new_version = f"{major}.{minor + 1}.0"
            return new_version
        except Exception as e:
            logger.error(f"Error incrementing version: {e}")
            return self.current_version
    
    def increment_major_version(self) -> str:
        """Increment major version (e.g., 2.0.1 -> 3.0.0)"""
        try:
            major, minor, patch = map(int, self.current_version.split('.'))
            new_version = f"{major + 1}.0.0"
            return new_version
        except Exception as e:
            logger.error(f"Error incrementing version: {e}")
            return self.current_version
    
    def update_version_in_file(self, new_version: str, change_description: str = "") -> bool:
        """
        Update version in main.py file
        
        Args:
            new_version: New version string (e.g., "2.0.2")
            change_description: Description of changes made
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.main_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update version number
            content = re.sub(
                r'Version:\s*\d+\.\d+\.\d+',
                f'Version: {new_version}',
                content
            )
            
            # Update date
            today = datetime.now().strftime("%B %d, %Y")
            content = re.sub(
                r'Updated:\s*[^\n]+',
                f'Updated: {today}',
                content
            )
            
            # Add change description to docstring if provided
            if change_description:
                # Look for existing description line and update it
                description_pattern = r'(Version:\s*' + re.escape(new_version) + r')([^\n]*)'
                replacement = f'\\1 - {change_description}'
                content = re.sub(description_pattern, replacement, content)
            
            # Write back to file
            with open(self.main_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.current_version = new_version
            logger.info(f"Version updated to {new_version}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating version in file: {e}")
            return False
    
    def auto_increment_patch(self, change_description: str = "Bug fixes and improvements") -> str:
        """
        Automatically increment patch version for bug fixes/small changes
        
        Args:
            change_description: Description of changes
            
        Returns:
            New version string
        """
        new_version = self.increment_patch_version()
        self.update_version_in_file(new_version, change_description)
        return new_version
    
    def auto_increment_minor(self, change_description: str = "New features and enhancements") -> str:
        """
        Automatically increment minor version for new features
        
        Args:
            change_description: Description of changes
            
        Returns:
            New version string
        """
        new_version = self.increment_minor_version()
        self.update_version_in_file(new_version, change_description)
        return new_version
    
    def get_current_version(self) -> str:
        """Get current application version"""
        return self.current_version


# Global instance for easy access
version_manager = VersionManager()


def get_version() -> str:
    """Get current application version"""
    return version_manager.get_current_version()


def update_version_for_feature(description: str) -> str:
    """Update version for new feature (minor increment)"""
    return version_manager.auto_increment_minor(description)


def update_version_for_bugfix(description: str) -> str:
    """Update version for bug fix (patch increment)"""
    return version_manager.auto_increment_patch(description)