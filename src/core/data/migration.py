"""
Module/Script Name: YAML to SQLite Migration Utility
Path: src/core/data/migration.py

Description:
One-time migration script to import existing YAML deployments to SQLite database.
Scans config/clients directory for all YAML files and migrates deployment history
to the persistent SQLite database.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-01-17

Last Modified Date:
2025-01-17

Version: 1.00

Usage:
    python -m src.core.data.migration

Comments:
* v1.00 - Initial migration utility for deployment history
"""

from pathlib import Path
from typing import List, Tuple
import sys

from .deployment_store import DeploymentHistoryStore
from ..config.parser import load_config_from_file
from ..utils.logger import get_logger

logger = get_logger(__name__)


def find_config_files(base_dir: Path) -> List[Path]:
    """
    Find all YAML config files in the given directory.

    Args:
        base_dir: Base directory to search

    Returns:
        List[Path]: List of YAML file paths
    """
    yaml_files = []

    if not base_dir.exists():
        logger.warning(f"Directory does not exist: {base_dir}")
        return yaml_files

    # Search for .yaml and .yml files recursively
    yaml_files.extend(base_dir.rglob("*.yaml"))
    yaml_files.extend(base_dir.rglob("*.yml"))

    return sorted(yaml_files)


def migrate_single_config(store: DeploymentHistoryStore, yaml_file: Path) -> Tuple[int, int]:
    """
    Migrate a single config file's deployments.

    Args:
        store: DeploymentHistoryStore instance
        yaml_file: Path to YAML config file

    Returns:
        Tuple[int, int]: (deployments_found, deployments_migrated)
    """
    try:
        logger.info(f"Processing: {yaml_file}")

        # Load config
        config = load_config_from_file(str(yaml_file))

        if not config:
            logger.warning("  SKIP: Could not load config file")
            return (0, 0)

        if not hasattr(config, 'deployments') or not config.deployments:
            logger.info("  SKIP: No deployments found in config")
            return (0, 0)

        deployments_count = len(config.deployments)
        business_name = getattr(config.business, 'business_name', 'Unknown Business')

        # Migrate deployments
        migrated_count = store.migrate_yaml_deployments(
            config_file_path=str(yaml_file.resolve()),
            business_name=business_name,
            yaml_deployments=config.deployments
        )

        logger.info(f"  SUCCESS: Migrated {migrated_count}/{deployments_count} deployment(s)")
        logger.info(f"  Business: {business_name}")

        return (deployments_count, migrated_count)

    except Exception as e:
        logger.error(f"  ERROR: {str(e)}")
        logger.error(f"Migration failed for {yaml_file}: {e}")
        return (0, 0)


def migrate_all_client_configs(config_dir: str = "config/clients") -> None:
    """
    Scan config directory and migrate all YAML deployments to SQLite.

    Args:
        config_dir: Directory containing client config files
    """
    logger.info("=" * 70)
    logger.info("YAML to SQLite Migration Utility")
    logger.info("=" * 70)
    logger.info("")
    logger.info("This script will migrate deployment history from YAML configs")
    logger.info("to the new SQLite database (data/deployments.db)")
    logger.info("")
    logger.info("NOTE: Your YAML files will NOT be modified.")
    logger.info("")

    # Confirm before proceeding
    response = input("Continue with migration? (yes/no): ").strip().lower()

    if response != 'yes':
        logger.info("Migration cancelled by user")
        return

    logger.info("")

    # Find config files
    base_dir = Path(config_dir)
    yaml_files = find_config_files(base_dir)

    if not yaml_files:
        logger.error(f"ERROR: No YAML config files found in {base_dir}")
        logger.error(f"Please ensure you're running this script from the project root directory,")
        logger.error(f"and that config files exist in: {base_dir}")
        return

    logger.info(f"Found {len(yaml_files)} config file(s) in {base_dir}")
    logger.info("-" * 70)

    # Initialize store
    store = DeploymentHistoryStore()

    # Migrate each file
    total_files = 0
    total_deployments_found = 0
    total_deployments_migrated = 0

    for yaml_file in yaml_files:
        total_files += 1
        found, migrated = migrate_single_config(store, yaml_file)
        total_deployments_found += found
        total_deployments_migrated += migrated

    # Summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("Migration Complete:")
    logger.info("-" * 70)
    logger.info(f"  - Config files processed: {total_files}")
    logger.info(f"  - Deployments found: {total_deployments_found}")
    logger.info(f"  - Deployments migrated: {total_deployments_migrated}")
    logger.info(f"  - Database: data/deployments.db")
    logger.info("=" * 70)
    logger.info("")

    if total_deployments_migrated > 0:
        logger.info("SUCCESS: Deployment history has been migrated to SQLite!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Open the application")
        logger.info("  2. Load a client config")
        logger.info("  3. Check Deployment History tab - your deployments should appear")
        logger.info("")
    else:
        logger.info("No deployments were migrated.")
        logger.info("")
        if total_deployments_found == 0:
            logger.info("This is normal if you haven't created any deployments yet.")
        else:
            logger.warning("WARNING: Deployments were found but not migrated.")
            logger.warning("Check the error messages above for details.")
        logger.info("")


def main():
    """Main entry point for migration script"""
    # Allow custom config directory via command line
    if len(sys.argv) > 1:
        config_dir = sys.argv[1]
    else:
        config_dir = "config/clients"

    migrate_all_client_configs(config_dir)


if __name__ == "__main__":
    main()
