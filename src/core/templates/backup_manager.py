"""
Template Backup Manager - Handles template versioning and backup
Path: E:/projects/cloud-stack-generator/src/core/templates/backup_manager.py

Description:
Manages template backups, versioning, and rollback functionality.
Provides automatic backup creation and restore capabilities for templates.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Initial backup management system
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime
import json
import shutil
import zipfile
import hashlib


@dataclass
class BackupMetadata:
    """Backup metadata information"""
    backup_id: str
    template_id: str
    template_name: str
    version: str
    created_date: str
    created_by: str
    description: str
    file_hash: str
    file_size: int
    backup_type: str  # 'manual', 'auto', 'pre_edit'


class TemplateBackupManager:
    """Manages template backups and versioning"""

    def __init__(self, templates_dir: Path):
        self.templates_dir = Path(templates_dir)
        self.backups_dir = self.templates_dir / "backups"
        self.backups_dir.mkdir(exist_ok=True)

        # Create subdirectories for organization
        (self.backups_dir / "manual").mkdir(exist_ok=True)
        (self.backups_dir / "auto").mkdir(exist_ok=True)
        (self.backups_dir / "pre_edit").mkdir(exist_ok=True)

        self.backup_index_file = self.backups_dir / "backup_index.json"
        self.backup_index = self._load_backup_index()

    def _load_backup_index(self) -> Dict[str, List[BackupMetadata]]:
        """Load the backup index from file"""
        if not self.backup_index_file.exists():
            return {}

        try:
            with open(self.backup_index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert dict data back to BackupMetadata objects
            index = {}
            for template_id, backups_data in data.items():
                index[template_id] = [
                    BackupMetadata(**backup_data) for backup_data in backups_data
                ]

            return index
        except Exception as e:
            print(f"Error loading backup index: {e}")
            return {}

    def _save_backup_index(self):
        """Save the backup index to file"""
        try:
            # Convert BackupMetadata objects to dict for JSON serialization
            data = {}
            for template_id, backups in self.backup_index.items():
                data[template_id] = [asdict(backup) for backup in backups]

            with open(self.backup_index_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving backup index: {e}")

    def create_backup(
        self,
        template_id: str,
        template_content: str,
        template_metadata: Dict[str, Any],
        backup_type: str = "manual",
        description: str = ""
    ) -> str:
        """
        Create a backup of a template

        Args:
            template_id: Template identifier
            template_content: Template HTML content
            template_metadata: Template metadata
            backup_type: Type of backup ('manual', 'auto', 'pre_edit')
            description: Optional description of the backup

        Returns:
            Backup ID
        """
        try:
            # Generate backup ID
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            content_hash = hashlib.md5(template_content.encode('utf-8')).hexdigest()[:8]
            backup_id = f"{template_id}_{timestamp}_{content_hash}"

            # Create backup directory
            backup_subdir = self.backups_dir / backup_type
            backup_dir = backup_subdir / backup_id
            backup_dir.mkdir(exist_ok=True)

            # Save template content
            template_file = backup_dir / f"{template_id}.html"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template_content)

            # Save metadata
            metadata_file = backup_dir / f"{template_id}.metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(template_metadata, f, indent=2, ensure_ascii=False, default=str)

            # Calculate file hash and size
            file_hash = self._calculate_file_hash(template_file)
            file_size = template_file.stat().st_size

            # Create backup metadata
            backup_metadata = BackupMetadata(
                backup_id=backup_id,
                template_id=template_id,
                template_name=template_metadata.get('name', template_id),
                version=template_metadata.get('version', '1.00'),
                created_date=datetime.now().isoformat(),
                created_by=template_metadata.get('author', 'Unknown'),
                description=description or f"{backup_type.title()} backup",
                file_hash=file_hash,
                file_size=file_size,
                backup_type=backup_type
            )

            # Add to index
            if template_id not in self.backup_index:
                self.backup_index[template_id] = []

            self.backup_index[template_id].append(backup_metadata)

            # Sort backups by date (newest first)
            self.backup_index[template_id].sort(
                key=lambda b: b.created_date, reverse=True
            )

            # Save index
            self._save_backup_index()

            # Clean up old backups if needed
            self._cleanup_old_backups(template_id, backup_type)

            return backup_id

        except Exception as e:
            print(f"Error creating backup: {e}")
            raise

    def restore_backup(self, backup_id: str) -> Tuple[str, Dict[str, Any]]:
        """
        Restore a template from backup

        Args:
            backup_id: Backup identifier

        Returns:
            Tuple of (template_content, template_metadata)
        """
        try:
            # Find backup metadata
            backup_metadata = None
            template_id = None

            for tid, backups in self.backup_index.items():
                for backup in backups:
                    if backup.backup_id == backup_id:
                        backup_metadata = backup
                        template_id = tid
                        break
                if backup_metadata:
                    break

            if not backup_metadata:
                raise ValueError(f"Backup {backup_id} not found")

            # Locate backup files
            backup_dir = self.backups_dir / backup_metadata.backup_type / backup_id
            template_file = backup_dir / f"{template_id}.html"
            metadata_file = backup_dir / f"{template_id}.metadata.json"

            if not template_file.exists():
                raise FileNotFoundError(f"Backup template file not found: {template_file}")

            # Read template content
            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()

            # Read metadata
            template_metadata = {}
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    template_metadata = json.load(f)

            # Verify file integrity
            current_hash = self._calculate_file_hash(template_file)
            if current_hash != backup_metadata.file_hash:
                print(f"Warning: Backup file hash mismatch for {backup_id}")

            return template_content, template_metadata

        except Exception as e:
            print(f"Error restoring backup: {e}")
            raise

    def get_backups(self, template_id: str) -> List[BackupMetadata]:
        """Get all backups for a template"""
        return self.backup_index.get(template_id, [])

    def get_all_backups(self) -> Dict[str, List[BackupMetadata]]:
        """Get all backups for all templates"""
        return self.backup_index.copy()

    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup

        Args:
            backup_id: Backup identifier

        Returns:
            True if backup was deleted, False if not found
        """
        try:
            # Find and remove from index
            template_id = None
            backup_metadata = None

            for tid, backups in self.backup_index.items():
                for i, backup in enumerate(backups):
                    if backup.backup_id == backup_id:
                        backup_metadata = backups.pop(i)
                        template_id = tid
                        break
                if backup_metadata:
                    break

            if not backup_metadata:
                return False

            # Delete backup directory
            backup_dir = self.backups_dir / backup_metadata.backup_type / backup_id
            if backup_dir.exists():
                shutil.rmtree(backup_dir)

            # Save updated index
            self._save_backup_index()

            return True

        except Exception as e:
            print(f"Error deleting backup: {e}")
            return False

    def create_archive(self, template_id: str, archive_path: Path) -> bool:
        """
        Create a ZIP archive of all backups for a template

        Args:
            template_id: Template identifier
            archive_path: Path where to save the archive

        Returns:
            True if archive was created successfully
        """
        try:
            backups = self.get_backups(template_id)
            if not backups:
                return False

            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add backup index for this template
                index_data = {template_id: [asdict(backup) for backup in backups]}
                zipf.writestr(f"{template_id}_backup_index.json",
                            json.dumps(index_data, indent=2, ensure_ascii=False))

                # Add all backup files
                for backup in backups:
                    backup_dir = self.backups_dir / backup.backup_type / backup.backup_id

                    for file_path in backup_dir.glob("*"):
                        if file_path.is_file():
                            arcname = f"{backup.backup_id}/{file_path.name}"
                            zipf.write(file_path, arcname)

            return True

        except Exception as e:
            print(f"Error creating archive: {e}")
            return False

    def import_archive(self, archive_path: Path) -> bool:
        """
        Import backups from a ZIP archive

        Args:
            archive_path: Path to the archive file

        Returns:
            True if import was successful
        """
        try:
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                # Extract all files to temporary location
                temp_dir = self.backups_dir / "temp_import"
                temp_dir.mkdir(exist_ok=True)

                try:
                    zipf.extractall(temp_dir)

                    # Find and load backup index files
                    for index_file in temp_dir.glob("*_backup_index.json"):
                        with open(index_file, 'r', encoding='utf-8') as f:
                            imported_index = json.load(f)

                        # Process each template's backups
                        for template_id, backups_data in imported_index.items():
                            for backup_data in backups_data:
                                backup_metadata = BackupMetadata(**backup_data)

                                # Create backup directory
                                backup_dir = (self.backups_dir /
                                            backup_metadata.backup_type /
                                            backup_metadata.backup_id)
                                backup_dir.mkdir(parents=True, exist_ok=True)

                                # Move backup files
                                source_dir = temp_dir / backup_metadata.backup_id
                                if source_dir.exists():
                                    for file_path in source_dir.glob("*"):
                                        if file_path.is_file():
                                            shutil.copy2(file_path, backup_dir)

                                    # Add to index
                                    if template_id not in self.backup_index:
                                        self.backup_index[template_id] = []

                                    # Check if backup already exists
                                    if not any(b.backup_id == backup_metadata.backup_id
                                             for b in self.backup_index[template_id]):
                                        self.backup_index[template_id].append(backup_metadata)

                    # Save updated index
                    self._save_backup_index()

                finally:
                    # Clean up temporary directory
                    shutil.rmtree(temp_dir, ignore_errors=True)

            return True

        except Exception as e:
            print(f"Error importing archive: {e}")
            return False

    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _cleanup_old_backups(self, template_id: str, backup_type: str, max_backups: int = 10):
        """Clean up old backups to maintain reasonable storage usage"""
        try:
            if template_id not in self.backup_index:
                return

            # Filter backups by type
            typed_backups = [
                backup for backup in self.backup_index[template_id]
                if backup.backup_type == backup_type
            ]

            # Keep only the most recent backups
            if len(typed_backups) > max_backups:
                # Sort by date (newest first)
                typed_backups.sort(key=lambda b: b.created_date, reverse=True)

                # Remove old backups
                for backup in typed_backups[max_backups:]:
                    backup_dir = self.backups_dir / backup_type / backup.backup_id
                    if backup_dir.exists():
                        shutil.rmtree(backup_dir)

                    # Remove from index
                    self.backup_index[template_id].remove(backup)

                # Save updated index
                self._save_backup_index()

        except Exception as e:
            print(f"Error cleaning up old backups: {e}")

    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup system statistics"""
        total_backups = 0
        total_size = 0
        backup_types = {"manual": 0, "auto": 0, "pre_edit": 0}

        for template_id, backups in self.backup_index.items():
            total_backups += len(backups)
            for backup in backups:
                total_size += backup.file_size
                backup_types[backup.backup_type] = backup_types.get(backup.backup_type, 0) + 1

        return {
            "total_templates": len(self.backup_index),
            "total_backups": total_backups,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "backup_types": backup_types,
            "backup_directory": str(self.backups_dir)
        }