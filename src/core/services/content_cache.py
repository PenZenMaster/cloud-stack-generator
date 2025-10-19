"""
Content Cache Manager
Path: E:/projects/cloud-stack-generator/src/core/services/content_cache.py

Description:
File-based caching system for AI-generated content to reduce API costs and
improve performance. Uses hash-based cache keys and supports configurable
time-to-live (TTL) for cache entries.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-10-19

Last Modified Date:
2025-10-19

Comments:
* v1.00 - Initial creation with file-based caching and TTL support
"""

import json
import hashlib
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from ..config.env_config import CacheConfig

logger = logging.getLogger(__name__)


class ContentCache:
    """
    File-based cache manager for AI-generated content.

    Features:
    - Hash-based cache keys for content identification
    - Configurable TTL (time-to-live) for cache entries
    - Automatic cache invalidation
    - JSON-based storage for easy inspection
    - Cache statistics and management
    """

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        ttl_hours: Optional[int] = None,
        enabled: Optional[bool] = None
    ):
        """
        Initialize the content cache manager.

        Args:
            cache_dir: Directory to store cache files (defaults to env config)
            ttl_hours: Cache time-to-live in hours (defaults to env config or 168)
            enabled: Whether caching is enabled (defaults to env config)
        """
        # Use centralized config with optional overrides
        self.cache_dir = Path(cache_dir) if cache_dir else CacheConfig.get_cache_dir()
        self.ttl_hours = ttl_hours or CacheConfig.get_ttl_hours()
        self.enabled = enabled if enabled is not None else CacheConfig.is_enabled()

        # Create cache directory if enabled
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Content cache initialized at {self.cache_dir} (TTL: {self.ttl_hours}h)")
        else:
            logger.info("Content cache disabled")

    def is_enabled(self) -> bool:
        """Check if caching is enabled"""
        return self.enabled

    def generate_cache_key(self, content_type: str, context: Dict[str, Any]) -> str:
        """
        Generate a unique cache key based on content type and context.

        Args:
            content_type: Type of content (e.g., 'home_page', 'city_page')
            context: Dictionary with content generation context

        Returns:
            SHA256 hash string as cache key
        """
        # Create a deterministic string from context
        # Sort keys to ensure consistent ordering
        context_str = json.dumps(context, sort_keys=True, default=str)

        # Combine content type and context
        key_input = f"{content_type}:{context_str}"

        # Generate hash
        cache_key = hashlib.sha256(key_input.encode('utf-8')).hexdigest()

        return cache_key

    def get(self, content_type: str, context: Dict[str, Any]) -> Optional[str]:
        """
        Retrieve cached content if available and not expired.

        Args:
            content_type: Type of content to retrieve
            context: Context dictionary for cache key generation

        Returns:
            Cached content string or None if not found/expired
        """
        if not self.enabled:
            return None

        cache_key = self.generate_cache_key(content_type, context)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            logger.debug(f"Cache miss for {content_type}")
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_entry = json.load(f)

            # Check if cache is expired
            cached_at = datetime.fromisoformat(cache_entry['cached_at'])
            expires_at = cached_at + timedelta(hours=self.ttl_hours)

            if datetime.now() > expires_at:
                logger.debug(f"Cache expired for {content_type} (cached at {cached_at})")
                # Optionally delete expired cache file
                cache_file.unlink()
                return None

            logger.info(f"Cache hit for {content_type} (age: {(datetime.now() - cached_at).total_seconds() / 3600:.1f}h)")
            return cache_entry['content']

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Failed to read cache file {cache_file}: {e}")
            return None

    def set(
        self,
        content_type: str,
        context: Dict[str, Any],
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store content in cache.

        Args:
            content_type: Type of content being cached
            context: Context dictionary for cache key generation
            content: The content to cache
            metadata: Optional metadata to store with the cache entry

        Returns:
            True if successfully cached, False otherwise
        """
        if not self.enabled:
            return False

        cache_key = self.generate_cache_key(content_type, context)
        cache_file = self.cache_dir / f"{cache_key}.json"

        cache_entry = {
            'content_type': content_type,
            'content': content,
            'cached_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(hours=self.ttl_hours)).isoformat(),
            'ttl_hours': self.ttl_hours,
            'context': context,
            'metadata': metadata or {}
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_entry, f, indent=2, ensure_ascii=False)

            logger.info(f"Cached {content_type} (key: {cache_key[:12]}...)")
            return True

        except Exception as e:
            logger.error(f"Failed to write cache file {cache_file}: {e}")
            return False

    def invalidate(self, content_type: str, context: Dict[str, Any]) -> bool:
        """
        Invalidate (delete) a specific cache entry.

        Args:
            content_type: Type of content to invalidate
            context: Context dictionary for cache key generation

        Returns:
            True if cache was invalidated, False if not found
        """
        if not self.enabled:
            return False

        cache_key = self.generate_cache_key(content_type, context)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                cache_file.unlink()
                logger.info(f"Invalidated cache for {content_type}")
                return True
            except Exception as e:
                logger.error(f"Failed to delete cache file {cache_file}: {e}")
                return False

        return False

    def clear_all(self) -> int:
        """
        Clear all cached content.

        Returns:
            Number of cache files deleted
        """
        if not self.enabled:
            return 0

        count = 0
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                cache_file.unlink()
                count += 1
            except Exception as e:
                logger.error(f"Failed to delete cache file {cache_file}: {e}")

        logger.info(f"Cleared {count} cache files")
        return count

    def clear_expired(self) -> int:
        """
        Remove expired cache entries.

        Returns:
            Number of expired cache files deleted
        """
        if not self.enabled:
            return 0

        count = 0
        for cache_file in self.cache_dir.glob('*.json'):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_entry = json.load(f)

                expires_at = datetime.fromisoformat(cache_entry['expires_at'])
                if datetime.now() > expires_at:
                    cache_file.unlink()
                    count += 1

            except Exception as e:
                logger.warning(f"Error processing cache file {cache_file}: {e}")
                continue

        logger.info(f"Cleared {count} expired cache files")
        return count

    def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        if not self.enabled:
            return {
                'enabled': False,
                'total_entries': 0,
                'expired_entries': 0,
                'valid_entries': 0
            }

        total = 0
        expired = 0
        valid = 0

        for cache_file in self.cache_dir.glob('*.json'):
            total += 1
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_entry = json.load(f)

                expires_at = datetime.fromisoformat(cache_entry['expires_at'])
                if datetime.now() > expires_at:
                    expired += 1
                else:
                    valid += 1

            except Exception:
                continue

        return {
            'enabled': True,
            'cache_dir': str(self.cache_dir),
            'ttl_hours': self.ttl_hours,
            'total_entries': total,
            'expired_entries': expired,
            'valid_entries': valid
        }
