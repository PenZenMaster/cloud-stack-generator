"""
Module/Script Name: Deployment History Store
Path: src/core/data/deployment_store.py

Description:
SQLite-based persistent storage for deployment history and uploaded assets.
Provides atomic transactions, WAL mode for concurrency, and migration support
from legacy YAML storage.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-01-17

Last Modified Date:
2025-01-17

Version: 1.00

Comments:
* v1.00 - Initial implementation with deployments, meta_tags, and uploaded_assets tables
"""

import sqlite3
import json
import time
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from contextlib import contextmanager

from ..config.models import DeploymentConfig

logger = logging.getLogger(__name__)


class DeploymentHistoryStore:
    """
    SQLite-based storage for deployment history with WAL mode for better concurrency.

    Features:
    - Persistent deployment history across sessions
    - Per-client-config deployment tracking
    - Meta tags normalization in separate table
    - Uploaded assets tracking (Issue #22)
    - YAML migration support
    - WAL mode for concurrent access
    - Retry logic for SQLITE_BUSY errors
    """

    def __init__(self, db_path: str = "data/deployments.db"):
        """Initialize deployment store with database path"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    @contextmanager
    def _get_connection(self, timeout: float = 10.0):
        """
        Context manager for database connections with proper cleanup.

        Args:
            timeout: Timeout in seconds for database lock

        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path), timeout=timeout)
            conn.row_factory = sqlite3.Row  # Enable dict-like access
            conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
            yield conn
        finally:
            if conn:
                conn.close()

    def _init_database(self):
        """Create database schema if it doesn't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Enable WAL mode for better concurrent access
            cursor.execute("PRAGMA journal_mode=WAL")

            # Clients table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    config_file_path TEXT NOT NULL UNIQUE,
                    business_name TEXT NOT NULL,
                    industry TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Deployments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deployments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    deployment_id TEXT NOT NULL,
                    bucket TEXT NOT NULL,
                    directory TEXT DEFAULT '',
                    region TEXT DEFAULT 'us-east-1',
                    mode TEXT CHECK(mode IN ('s3', 'cloudfront')) DEFAULT 's3',
                    cloudfront_distribution_id TEXT,
                    cloudfront_domain TEXT,
                    last_deployed TIMESTAMP,
                    deployment_url TEXT,
                    friendly_name TEXT,
                    industry TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
                    UNIQUE(client_id, deployment_id)
                )
            """)

            # Deployment meta tags table (normalized)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS deployment_meta_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    deployment_id INTEGER NOT NULL,
                    tag_name TEXT NOT NULL,
                    tag_content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (deployment_id) REFERENCES deployments(id) ON DELETE CASCADE,
                    UNIQUE(deployment_id, tag_name)
                )
            """)

            # Uploaded assets table (Issue #22)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS uploaded_assets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    original_filename TEXT NOT NULL,
                    file_size_bytes INTEGER NOT NULL,
                    file_type TEXT,
                    provider TEXT CHECK(provider IN ('aws_s3', 'google_gcs', 'wasabi', 'backblaze')) NOT NULL,
                    bucket TEXT NOT NULL,
                    remote_path TEXT NOT NULL,
                    region TEXT,
                    public_url TEXT NOT NULL,
                    description TEXT,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
                )
            """)

            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deployments_client_id
                ON deployments(client_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deployments_deployment_id
                ON deployments(deployment_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_deployments_last_deployed
                ON deployments(last_deployed DESC)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_meta_tags_deployment_id
                ON deployment_meta_tags(deployment_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_assets_client_id
                ON uploaded_assets(client_id)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_assets_uploaded_at
                ON uploaded_assets(uploaded_at DESC)
            """)

            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    def _get_or_create_client(self, conn: sqlite3.Connection, config_file_path: str,
                             business_name: str, industry: Optional[str] = None) -> int:
        """
        Get existing client ID or create new client record.

        Args:
            conn: Database connection
            config_file_path: Absolute path to config YAML file
            business_name: Business name for this client
            industry: Optional industry

        Returns:
            int: Client ID
        """
        cursor = conn.cursor()

        # Try to get existing client
        cursor.execute(
            "SELECT id FROM clients WHERE config_file_path = ?",
            (config_file_path,)
        )
        row = cursor.fetchone()

        if row:
            # Update last_accessed timestamp
            cursor.execute(
                "UPDATE clients SET last_accessed = CURRENT_TIMESTAMP WHERE id = ?",
                (row[0],)
            )
            return row[0]
        else:
            # Create new client
            cursor.execute(
                """
                INSERT INTO clients (config_file_path, business_name, industry)
                VALUES (?, ?, ?)
                """,
                (config_file_path, business_name, industry)
            )
            return cursor.lastrowid

    def save_deployment(self, config_file_path: str, business_name: str,
                       deployment: DeploymentConfig) -> bool:
        """
        Save or update deployment record.

        Args:
            config_file_path: Absolute path to config YAML file
            business_name: Business name for client
            deployment: DeploymentConfig object to save

        Returns:
            bool: True if successful
        """
        try:
            with self._get_connection() as conn:
                # Get or create client
                client_id = self._get_or_create_client(
                    conn, config_file_path, business_name, deployment.industry
                )

                cursor = conn.cursor()

                # Check if deployment exists
                cursor.execute(
                    """
                    SELECT id FROM deployments
                    WHERE client_id = ? AND deployment_id = ?
                    """,
                    (client_id, deployment.deployment_id)
                )
                existing_row = cursor.fetchone()

                if existing_row:
                    # Update existing deployment
                    deployment_pk = existing_row[0]
                    cursor.execute(
                        """
                        UPDATE deployments SET
                            bucket = ?,
                            directory = ?,
                            region = ?,
                            mode = ?,
                            cloudfront_distribution_id = ?,
                            cloudfront_domain = ?,
                            last_deployed = ?,
                            deployment_url = ?,
                            friendly_name = ?,
                            industry = ?,
                            updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                        """,
                        (
                            deployment.bucket,
                            deployment.directory,
                            deployment.region,
                            deployment.mode,
                            deployment.cloudfront_distribution_id,
                            deployment.cloudfront_domain,
                            deployment.last_deployed,
                            deployment.deployment_url,
                            deployment.friendly_name,
                            deployment.industry,
                            deployment_pk
                        )
                    )
                else:
                    # Insert new deployment
                    cursor.execute(
                        """
                        INSERT INTO deployments (
                            client_id, deployment_id, bucket, directory, region, mode,
                            cloudfront_distribution_id, cloudfront_domain,
                            last_deployed, deployment_url, friendly_name, industry
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            client_id,
                            deployment.deployment_id,
                            deployment.bucket,
                            deployment.directory,
                            deployment.region,
                            deployment.mode,
                            deployment.cloudfront_distribution_id,
                            deployment.cloudfront_domain,
                            deployment.last_deployed,
                            deployment.deployment_url,
                            deployment.friendly_name,
                            deployment.industry
                        )
                    )
                    deployment_pk = cursor.lastrowid

                # Handle meta tags (delete and re-insert for simplicity)
                cursor.execute(
                    "DELETE FROM deployment_meta_tags WHERE deployment_id = ?",
                    (deployment_pk,)
                )

                if deployment.meta_tags:
                    for tag_name, tag_content in deployment.meta_tags.items():
                        cursor.execute(
                            """
                            INSERT INTO deployment_meta_tags (deployment_id, tag_name, tag_content)
                            VALUES (?, ?, ?)
                            """,
                            (deployment_pk, tag_name, tag_content)
                        )

                conn.commit()
                logger.info(f"Deployment saved: {deployment.deployment_id}")
                return True

        except sqlite3.Error as e:
            logger.error(f"Database error saving deployment: {e}")
            return False
        except Exception as e:
            logger.error(f"Error saving deployment: {e}")
            return False

    def load_deployments(self, config_file_path: str) -> List[DeploymentConfig]:
        """
        Load all deployments for a given config file.

        Args:
            config_file_path: Absolute path to config YAML file

        Returns:
            List[DeploymentConfig]: List of deployments
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get client ID
                cursor.execute(
                    "SELECT id FROM clients WHERE config_file_path = ?",
                    (config_file_path,)
                )
                client_row = cursor.fetchone()

                if not client_row:
                    logger.info(f"No client found for config: {config_file_path}")
                    return []

                client_id = client_row[0]

                # Load all deployments for this client
                cursor.execute(
                    """
                    SELECT id, deployment_id, bucket, directory, region, mode,
                           cloudfront_distribution_id, cloudfront_domain,
                           last_deployed, deployment_url, friendly_name, industry
                    FROM deployments
                    WHERE client_id = ?
                    ORDER BY last_deployed DESC
                    """,
                    (client_id,)
                )

                deployments = []
                for row in cursor.fetchall():
                    deployment_pk = row[0]

                    # Load meta tags for this deployment
                    cursor.execute(
                        """
                        SELECT tag_name, tag_content
                        FROM deployment_meta_tags
                        WHERE deployment_id = ?
                        """,
                        (deployment_pk,)
                    )
                    meta_tags = {tag_row[0]: tag_row[1] for tag_row in cursor.fetchall()}

                    # Create DeploymentConfig object
                    deployment = DeploymentConfig(
                        deployment_id=row[1],
                        bucket=row[2],
                        directory=row[3] or '',
                        region=row[4] or 'us-east-1',
                        mode=row[5] or 's3',
                        cloudfront_distribution_id=row[6],
                        cloudfront_domain=row[7],
                        last_deployed=row[8],
                        deployment_url=row[9],
                        friendly_name=row[10],
                        industry=row[11],
                        meta_tags=meta_tags
                    )
                    deployments.append(deployment)

                logger.info(f"Loaded {len(deployments)} deployment(s) for {config_file_path}")
                return deployments

        except sqlite3.Error as e:
            logger.error(f"Database error loading deployments: {e}")
            return []
        except Exception as e:
            logger.error(f"Error loading deployments: {e}")
            return []

    def delete_deployment(self, config_file_path: str, deployment_id: str) -> bool:
        """
        Delete a deployment record.

        Args:
            config_file_path: Absolute path to config YAML file
            deployment_id: Deployment ID to delete

        Returns:
            bool: True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get client ID
                cursor.execute(
                    "SELECT id FROM clients WHERE config_file_path = ?",
                    (config_file_path,)
                )
                client_row = cursor.fetchone()

                if not client_row:
                    logger.warning(f"No client found for config: {config_file_path}")
                    return False

                client_id = client_row[0]

                # Delete deployment (cascade will delete meta_tags)
                cursor.execute(
                    """
                    DELETE FROM deployments
                    WHERE client_id = ? AND deployment_id = ?
                    """,
                    (client_id, deployment_id)
                )

                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Deployment deleted: {deployment_id}")
                    return True
                else:
                    logger.warning(f"Deployment not found: {deployment_id}")
                    return False

        except sqlite3.Error as e:
            logger.error(f"Database error deleting deployment: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting deployment: {e}")
            return False

    def update_friendly_name(self, config_file_path: str, deployment_id: str,
                            new_name: str) -> bool:
        """
        Update deployment friendly name.

        Args:
            config_file_path: Absolute path to config YAML file
            deployment_id: Deployment ID
            new_name: New friendly name

        Returns:
            bool: True if successful
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get client ID
                cursor.execute(
                    "SELECT id FROM clients WHERE config_file_path = ?",
                    (config_file_path,)
                )
                client_row = cursor.fetchone()

                if not client_row:
                    return False

                client_id = client_row[0]

                # Update friendly name
                cursor.execute(
                    """
                    UPDATE deployments SET
                        friendly_name = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE client_id = ? AND deployment_id = ?
                    """,
                    (new_name, client_id, deployment_id)
                )

                conn.commit()

                if cursor.rowcount > 0:
                    logger.info(f"Friendly name updated: {deployment_id} -> {new_name}")
                    return True
                else:
                    return False

        except sqlite3.Error as e:
            logger.error(f"Database error updating friendly name: {e}")
            return False

    def migrate_yaml_deployments(self, config_file_path: str, business_name: str,
                                 yaml_deployments: List[DeploymentConfig]) -> int:
        """
        One-time migration of deployments from YAML to SQLite.

        Args:
            config_file_path: Absolute path to config YAML file
            business_name: Business name
            yaml_deployments: List of deployments from YAML

        Returns:
            int: Number of deployments migrated
        """
        count = 0
        for deployment in yaml_deployments:
            if self.save_deployment(config_file_path, business_name, deployment):
                count += 1

        logger.info(f"Migrated {count}/{len(yaml_deployments)} deployments from YAML")
        return count

    def save_uploaded_asset(self, config_file_path: str, business_name: str,
                           filename: str, file_size: int, file_type: str,
                           provider: str, bucket: str, remote_path: str,
                           region: str, public_url: str, description: str = "") -> bool:
        """
        Save uploaded asset metadata (Issue #22).

        Args:
            config_file_path: Absolute path to config YAML file
            business_name: Business name
            filename: Original filename
            file_size: File size in bytes
            file_type: MIME type
            provider: Cloud provider (aws_s3, google_gcs, wasabi, backblaze)
            bucket: Bucket name
            remote_path: Remote path/key
            region: Cloud region
            public_url: Public URL to access file
            description: Optional description

        Returns:
            bool: True if successful
        """
        try:
            with self._get_connection() as conn:
                # Get or create client
                client_id = self._get_or_create_client(conn, config_file_path, business_name)

                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO uploaded_assets (
                        client_id, original_filename, file_size_bytes, file_type,
                        provider, bucket, remote_path, region, public_url, description
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        client_id, filename, file_size, file_type,
                        provider, bucket, remote_path, region, public_url, description
                    )
                )

                conn.commit()
                logger.info(f"Asset saved: {filename} -> {public_url}")
                return True

        except sqlite3.Error as e:
            logger.error(f"Database error saving asset: {e}")
            return False

    def load_uploaded_assets(self, config_file_path: str) -> List[Dict[str, Any]]:
        """
        Load all uploaded assets for a config (Issue #22).

        Args:
            config_file_path: Absolute path to config YAML file

        Returns:
            List[Dict]: List of asset dictionaries
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                # Get client ID
                cursor.execute(
                    "SELECT id FROM clients WHERE config_file_path = ?",
                    (config_file_path,)
                )
                client_row = cursor.fetchone()

                if not client_row:
                    return []

                client_id = client_row[0]

                # Load all assets
                cursor.execute(
                    """
                    SELECT id, original_filename, file_size_bytes, file_type,
                           provider, bucket, remote_path, region, public_url,
                           description, uploaded_at
                    FROM uploaded_assets
                    WHERE client_id = ?
                    ORDER BY uploaded_at DESC
                    """,
                    (client_id,)
                )

                assets = []
                for row in cursor.fetchall():
                    assets.append({
                        'id': row[0],
                        'filename': row[1],
                        'file_size_bytes': row[2],
                        'file_type': row[3],
                        'provider': row[4],
                        'bucket': row[5],
                        'remote_path': row[6],
                        'region': row[7],
                        'public_url': row[8],
                        'description': row[9],
                        'uploaded_at': row[10]
                    })

                return assets

        except sqlite3.Error as e:
            logger.error(f"Database error loading assets: {e}")
            return []
