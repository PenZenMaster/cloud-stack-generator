"""
Environment Configuration Manager
Path: E:/projects/cloud-stack-generator/src/core/config/env_config.py

Description:
Centralized environment variable management for the Cloud Stack Generator.
Provides type-safe access to environment variables with sensible defaults.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-19

Last Modified Date:
2025-10-19

Comments:
* v1.00 - Initial creation for centralized env config management
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
# This should be called once at application startup
_env_loaded = False


def load_environment() -> None:
    """
    Load environment variables from .env file.
    Safe to call multiple times (only loads once).
    """
    global _env_loaded
    if not _env_loaded:
        # Look for .env file in project root
        project_root = Path(__file__).parent.parent.parent.parent
        env_file = project_root / '.env'

        if env_file.exists():
            load_dotenv(env_file)
            _env_loaded = True


# Auto-load environment on module import
load_environment()


class GitHubConfig:
    """GitHub integration configuration"""

    @staticmethod
    def get_token() -> Optional[str]:
        """Get GitHub personal access token"""
        return os.getenv('GITHUB_TOKEN', '')

    @staticmethod
    def is_configured() -> bool:
        """Check if GitHub token is configured"""
        token = GitHubConfig.get_token()
        return bool(token and token != 'your_github_token_here')


class OpenAIConfig:
    """OpenAI API configuration"""

    @staticmethod
    def get_api_key() -> str:
        """Get OpenAI API key"""
        return os.getenv('OPENAI_API_KEY', '')

    @staticmethod
    def get_model() -> str:
        """Get OpenAI model name (default: gpt-4o-mini)"""
        return os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

    @staticmethod
    def get_max_tokens() -> int:
        """Get maximum tokens for OpenAI responses (default: 2000)"""
        try:
            return int(os.getenv('OPENAI_MAX_TOKENS', '2000'))
        except ValueError:
            return 2000

    @staticmethod
    def get_temperature() -> float:
        """Get temperature for OpenAI responses (default: 0.7)"""
        try:
            temp = float(os.getenv('OPENAI_TEMPERATURE', '0.7'))
            return max(0.0, min(1.0, temp))  # Clamp between 0 and 1
        except ValueError:
            return 0.7

    @staticmethod
    def is_enabled() -> bool:
        """Check if AI content generation is enabled"""
        enabled = os.getenv('AI_CONTENT_ENABLED', 'true').lower()
        return enabled in ['true', '1', 'yes', 'on']

    @staticmethod
    def is_configured() -> bool:
        """Check if OpenAI is properly configured with API key"""
        api_key = OpenAIConfig.get_api_key()
        return bool(api_key and api_key != 'your_openai_api_key_here')


class CacheConfig:
    """Content cache configuration"""

    @staticmethod
    def is_enabled() -> bool:
        """Check if content caching is enabled"""
        enabled = os.getenv('AI_CONTENT_CACHE_ENABLED', 'true').lower()
        return enabled in ['true', '1', 'yes', 'on']

    @staticmethod
    def get_ttl_hours() -> int:
        """Get cache TTL in hours (default: 168 = 7 days)"""
        try:
            return int(os.getenv('AI_CONTENT_CACHE_HOURS', '168'))
        except ValueError:
            return 168

    @staticmethod
    def get_cache_dir() -> Path:
        """Get cache directory path"""
        project_root = Path(__file__).parent.parent.parent.parent
        return project_root / '.cache' / 'ai_content'


class EnvironmentConfig:
    """
    Main environment configuration class.
    Provides access to all environment settings.
    """

    # Sub-configurations
    github = GitHubConfig
    openai = OpenAIConfig
    cache = CacheConfig

    @staticmethod
    def get_all_settings() -> dict:
        """
        Get all environment settings as a dictionary.
        Useful for debugging and configuration display.

        Returns:
            Dictionary with all configuration values (API keys redacted)
        """
        return {
            'github': {
                'configured': GitHubConfig.is_configured(),
                'token': '***' if GitHubConfig.is_configured() else 'Not set'
            },
            'openai': {
                'configured': OpenAIConfig.is_configured(),
                'enabled': OpenAIConfig.is_enabled(),
                'api_key': '***' if OpenAIConfig.is_configured() else 'Not set',
                'model': OpenAIConfig.get_model(),
                'max_tokens': OpenAIConfig.get_max_tokens(),
                'temperature': OpenAIConfig.get_temperature()
            },
            'cache': {
                'enabled': CacheConfig.is_enabled(),
                'ttl_hours': CacheConfig.get_ttl_hours(),
                'cache_dir': str(CacheConfig.get_cache_dir())
            }
        }

    @staticmethod
    def validate() -> list[str]:
        """
        Validate environment configuration and return any warnings.

        Returns:
            List of warning messages (empty if all OK)
        """
        warnings = []

        # Check GitHub
        if not GitHubConfig.is_configured():
            warnings.append("GitHub token not configured - GitHub features will be disabled")

        # Check OpenAI
        if OpenAIConfig.is_enabled() and not OpenAIConfig.is_configured():
            warnings.append(
                "AI content generation is enabled but API key not configured - "
                "will fall back to template-based generation"
            )

        # Check cache
        if not CacheConfig.is_enabled() and OpenAIConfig.is_enabled():
            warnings.append(
                "AI content caching is disabled - this may increase API costs"
            )

        return warnings


# Convenience function for application startup
def initialize_environment() -> None:
    """
    Initialize environment configuration and display status.
    Call this at application startup for validation and logging.
    """
    load_environment()

    warnings = EnvironmentConfig.validate()

    if warnings:
        print("\n=== Environment Configuration Warnings ===")
        for warning in warnings:
            print(f"  WARNING: {warning}")
        print()

    # Optional: Print configuration status
    settings = EnvironmentConfig.get_all_settings()
    print("\n=== Environment Configuration ===")
    print(f"  OpenAI: {'Configured' if settings['openai']['configured'] else 'Not configured'}")
    if settings['openai']['configured']:
        print(f"    Model: {settings['openai']['model']}")
        print(f"    Enabled: {settings['openai']['enabled']}")
    print(f"  Cache: {'Enabled' if settings['cache']['enabled'] else 'Disabled'}")
    if settings['cache']['enabled']:
        print(f"    TTL: {settings['cache']['ttl_hours']} hours")
    print()
