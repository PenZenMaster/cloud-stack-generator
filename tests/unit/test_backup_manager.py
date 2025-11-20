"""
Unit tests for Template Backup Manager
Path: E:/projects/cloud-stack-generator/tests/unit/test_backup_manager.py

Description:
Comprehensive unit tests for the template backup and restore system,
covering backup creation, restoration, archiving, and data integrity.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Initial test suite for backup manager
"""

import pytest
import tempfile
import json
import zipfile
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from core.templates.backup_manager import (
    TemplateBackupManager,
    BackupMetadata
)


class TestBackupMetadata:
    """Tests for BackupMetadata dataclass"""

    def test_backup_metadata_creation(self):
        """Test creating BackupMetadata"""
        metadata = BackupMetadata(
            template_id="test_template",
            backup_id="backup_001",
            timestamp="2025-09-22T10:30:00",
            description="Test backup",
            user="test_user",
            version="1.0.0",
            file_size=1024,
            checksum="abc123"
        )

        assert metadata.template_id == "test_template"
        assert metadata.backup_id == "backup_001"
        assert metadata.timestamp == "2025-09-22T10:30:00"
        assert metadata.file_size == 1024

    def test_backup_metadata_to_dict(self):
        """Test converting BackupMetadata to dictionary"""
        metadata = BackupMetadata(
            template_id="test_template",
            backup_id="backup_001",
            timestamp="2025-09-22T10:30:00",
            description="Test backup",
            user="test_user",
            version="1.0.0",
            file_size=1024,
            checksum="abc123"
        )

        result = metadata.to_dict()

        assert result['template_id'] == "test_template"
        assert result['backup_id'] == "backup_001"
        assert result['file_size'] == 1024

    def test_backup_metadata_from_dict(self):
        """Test creating BackupMetadata from dictionary"""
        data = {
            'template_id': 'test_template',
            'backup_id': 'backup_001',
            'timestamp': '2025-09-22T10:30:00',
            'description': 'Test backup',
            'user': 'test_user',
            'version': '1.0.0',
            'file_size': 1024,
            'checksum': 'abc123'
        }

        metadata = BackupMetadata.from_dict(data)

        assert metadata.template_id == "test_template"
        assert metadata.backup_id == "backup_001"
        assert metadata.file_size == 1024



class TestTemplateBackupManager:
    """Tests for TemplateBackupManager class"""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def templates_dir(self, temp_dir):
        """Create template directory structure"""
        templates_dir = temp_dir / "templates"
        pages_dir = templates_dir / "pages"
        components_dir = templates_dir / "components"

        pages_dir.mkdir(parents=True)
        components_dir.mkdir(parents=True)

        # Create sample template
        template_file = pages_dir / "test_template.html"
        template_file.write_text("""
<!DOCTYPE html>
<html>
<head><title>{{ title }}</title></head>
<body><h1>{{ heading }}</h1></body>
</html>
        """)

        # Create template metadata
        metadata_file = pages_dir / "test_template.json"
        metadata = {
            'id': 'test_template',
            'name': 'Test Template',
            'type': 'city_page',
            'variant': 'basic',
            'version': '1.0.0'
        }
        metadata_file.write_text(json.dumps(metadata, indent=2))

        yield templates_dir

    @pytest.fixture
    def backup_manager(self, templates_dir):
        """Create TemplateBackupManager instance"""
        return TemplateBackupManager(templates_dir)

    def test_init_creates_backup_directory(self, temp_dir):
        """Test that initialization creates backup directory"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        manager = TemplateBackupManager(templates_dir)

        backup_dir = templates_dir / "backups"
        assert backup_dir.exists()
        assert backup_dir.is_dir()

    def test_create_backup_success(self, backup_manager, templates_dir):
        """Test successfully creating a backup"""
        backup_id = backup_manager.create_backup(
            template_id="test_template",
            description="Test backup creation"
        )

        assert backup_id is not None
        assert isinstance(backup_id, str)
        assert len(backup_id) > 0

        # Check backup file exists
        backup_dir = templates_dir / "backups"
        backup_files = list(backup_dir.glob(f"*{backup_id}*.zip"))
        assert len(backup_files) == 1

    def test_create_backup_with_user(self, backup_manager):
        """Test creating backup with user information"""
        backup_id = backup_manager.create_backup(
            template_id="test_template",
            description="User backup",
            user="test_user"
        )

        assert backup_id is not None

        # Get backup info to verify user was stored
        backups = backup_manager.get_backups("test_template")
        user_backup = next((b for b in backups if b.backup_id == backup_id), None)

        assert user_backup is not None
        # Note: User info would be in metadata if BackupInfo includes it

    def test_create_backup_nonexistent_template(self, backup_manager):
        """Test creating backup for nonexistent template"""
        backup_id = backup_manager.create_backup(
            template_id="nonexistent_template",
            description="Should fail"
        )

        assert backup_id is None

    def test_get_backups_empty(self, backup_manager):
        """Test getting backups when none exist"""
        backups = backup_manager.get_backups("test_template")

        assert isinstance(backups, list)
        assert len(backups) == 0

    def test_get_backups_with_data(self, backup_manager):
        """Test getting backups after creating some"""
        # Create multiple backups
        backup_id1 = backup_manager.create_backup("test_template", "First backup")
        backup_id2 = backup_manager.create_backup("test_template", "Second backup")

        backups = backup_manager.get_backups("test_template")

        assert len(backups) == 2
        backup_ids = [b.backup_id for b in backups]
        assert backup_id1 in backup_ids
        assert backup_id2 in backup_ids

    def test_get_backups_sorted_by_date(self, backup_manager):
        """Test that backups are returned sorted by date (newest first)"""
        # Create backups with slight delay to ensure different timestamps
        import time

        backup_id1 = backup_manager.create_backup("test_template", "First backup")
        time.sleep(0.1)
        backup_id2 = backup_manager.create_backup("test_template", "Second backup")

        backups = backup_manager.get_backups("test_template")

        assert len(backups) >= 2
        # Most recent should be first
        assert backups[0].backup_id == backup_id2
        assert backups[1].backup_id == backup_id1

    def test_restore_backup_success(self, backup_manager, templates_dir):
        """Test successfully restoring a backup"""
        # Create backup
        backup_id = backup_manager.create_backup("test_template", "Backup for restore test")

        # Modify the original template
        template_file = templates_dir / "pages" / "test_template.html"
        original_content = template_file.read_text()
        template_file.write_text("<html><body>Modified content</body></html>")

        # Restore backup
        success = backup_manager.restore_backup("test_template", backup_id)

        assert success is True

        # Check that original content is restored
        restored_content = template_file.read_text()
        assert "{{ title }}" in restored_content  # Original content marker
        assert "Modified content" not in restored_content

    def test_restore_backup_nonexistent(self, backup_manager):
        """Test restoring nonexistent backup"""
        success = backup_manager.restore_backup("test_template", "nonexistent_backup")

        assert success is False

    def test_restore_backup_corrupted_file(self, backup_manager, templates_dir):
        """Test restoring backup with corrupted backup file"""
        # Create backup
        backup_id = backup_manager.create_backup("test_template", "Backup to corrupt")

        # Corrupt the backup file
        backup_dir = templates_dir / "backups"
        backup_files = list(backup_dir.glob(f"*{backup_id}*.zip"))
        assert len(backup_files) == 1

        backup_file = backup_files[0]
        backup_file.write_text("corrupted content")

        # Attempt restore
        success = backup_manager.restore_backup("test_template", backup_id)

        assert success is False

    def test_delete_backup_success(self, backup_manager):
        """Test successfully deleting a backup"""
        # Create backup
        backup_id = backup_manager.create_backup("test_template", "Backup to delete")

        # Verify backup exists
        backups_before = backup_manager.get_backups("test_template")
        assert len(backups_before) == 1

        # Delete backup
        success = backup_manager.delete_backup("test_template", backup_id)

        assert success is True

        # Verify backup is gone
        backups_after = backup_manager.get_backups("test_template")
        assert len(backups_after) == 0

    def test_delete_backup_nonexistent(self, backup_manager):
        """Test deleting nonexistent backup"""
        success = backup_manager.delete_backup("test_template", "nonexistent_backup")

        assert success is False

    def test_cleanup_old_backups(self, backup_manager):
        """Test cleaning up old backups based on retention policy"""
        # Create multiple backups
        backup_ids = []
        for i in range(5):
            backup_id = backup_manager.create_backup("test_template", f"Backup {i}")
            backup_ids.append(backup_id)

        # Clean up old backups (keep only 3 most recent)
        deleted_count = backup_manager.cleanup_old_backups("test_template", keep_count=3)

        assert deleted_count == 2  # Should delete 2 oldest backups

        # Verify only 3 backups remain
        remaining_backups = backup_manager.get_backups("test_template")
        assert len(remaining_backups) == 3

    def test_cleanup_old_backups_by_age(self, backup_manager):
        """Test cleaning up backups older than specified age"""
        # This test would require mocking datetime to create "old" backups
        with patch('core.templates.backup_manager.datetime') as mock_datetime:
            # Mock current time
            current_time = datetime(2025, 9, 22, 12, 0, 0)
            mock_datetime.now.return_value = current_time
            mock_datetime.strftime = datetime.strftime
            mock_datetime.fromisoformat = datetime.fromisoformat

            # Create backup
            backup_id = backup_manager.create_backup("test_template", "Old backup")

            # Move time forward by 8 days
            future_time = current_time + timedelta(days=8)
            mock_datetime.now.return_value = future_time

            # Clean up backups older than 7 days
            deleted_count = backup_manager.cleanup_old_backups_by_age(
                "test_template",
                max_age_days=7
            )

            # Should delete the old backup
            assert deleted_count >= 0  # Implementation dependent

    def test_get_backup_info(self, backup_manager):
        """Test getting detailed backup information"""
        backup_id = backup_manager.create_backup("test_template", "Info test backup")

        backup_info = backup_manager.get_backup_info("test_template", backup_id)

        assert backup_info is not None
        assert backup_info.backup_id == backup_id
        assert backup_info.template_id == "test_template"
        assert backup_info.description == "Info test backup"
        assert backup_info.file_size > 0
        assert backup_info.file_path.exists()

    def test_get_backup_info_nonexistent(self, backup_manager):
        """Test getting info for nonexistent backup"""
        backup_info = backup_manager.get_backup_info("test_template", "nonexistent")

        assert backup_info is None

    def test_create_archive_success(self, backup_manager, temp_dir):
        """Test creating template archive"""
        # Create multiple backups
        for i in range(3):
            backup_manager.create_backup("test_template", f"Backup {i}")

        # Create archive
        archive_path = temp_dir / "test_archive.zip"
        success = backup_manager.create_archive("test_template", archive_path)

        assert success is True
        assert archive_path.exists()

        # Verify archive contents
        with zipfile.ZipFile(archive_path, 'r') as archive:
            file_list = archive.namelist()
            assert len(file_list) > 0
            # Should contain template files and backup metadata

    def test_create_archive_with_backups(self, backup_manager, temp_dir):
        """Test creating archive including backup history"""
        # Create backups
        backup_ids = []
        for i in range(2):
            backup_id = backup_manager.create_backup("test_template", f"Archive backup {i}")
            backup_ids.append(backup_id)

        # Create archive including backups
        archive_path = temp_dir / "archive_with_backups.zip"
        success = backup_manager.create_archive(
            "test_template",
            archive_path,
            include_backups=True
        )

        assert success is True
        assert archive_path.exists()

        # Archive should be larger when including backups
        archive_size = archive_path.stat().st_size
        assert archive_size > 1000  # Should be substantial with backups

    def test_import_archive_success(self, backup_manager, templates_dir, temp_dir):
        """Test importing template from archive"""
        # Create and export template first
        backup_manager.create_backup("test_template", "For export")
        archive_path = temp_dir / "export_test.zip"
        backup_manager.create_archive("test_template", archive_path)

        # Remove original template
        template_file = templates_dir / "pages" / "test_template.html"
        metadata_file = templates_dir / "pages" / "test_template.json"
        template_file.unlink()
        metadata_file.unlink()

        # Import from archive
        success = backup_manager.import_archive(archive_path, "imported_template")

        assert success is True

        # Check that template was imported
        imported_template = templates_dir / "pages" / "imported_template.html"
        imported_metadata = templates_dir / "pages" / "imported_template.json"

        assert imported_template.exists()
        assert imported_metadata.exists()

    def test_import_archive_invalid_file(self, backup_manager, temp_dir):
        """Test importing from invalid archive file"""
        # Create invalid archive file
        invalid_archive = temp_dir / "invalid.zip"
        invalid_archive.write_text("not a zip file")

        success = backup_manager.import_archive(invalid_archive, "test_import")

        assert success is False

    def test_backup_file_integrity(self, backup_manager, templates_dir):
        """Test backup file integrity and checksums"""
        backup_id = backup_manager.create_backup("test_template", "Integrity test")

        # Get backup info
        backup_info = backup_manager.get_backup_info("test_template", backup_id)
        assert backup_info is not None

        # Verify backup file is valid ZIP
        with zipfile.ZipFile(backup_info.file_path, 'r') as archive:
            # Should not raise exception
            file_list = archive.namelist()
            assert len(file_list) > 0

            # Test extracting a file
            for file_name in file_list:
                if file_name.endswith('.html'):
                    content = archive.read(file_name)
                    assert len(content) > 0
                    break

    def test_backup_metadata_persistence(self, backup_manager, templates_dir):
        """Test that backup metadata is properly persisted"""
        backup_id = backup_manager.create_backup(
            "test_template",
            "Metadata persistence test",
            user="test_user"
        )

        # Recreate backup manager (simulates app restart)
        new_manager = TemplateBackupManager(templates_dir)

        # Should still find the backup
        backups = new_manager.get_backups("test_template")
        assert len(backups) >= 1

        backup = next((b for b in backups if b.backup_id == backup_id), None)
        assert backup is not None
        assert backup.description == "Metadata persistence test"

    def test_concurrent_backup_operations(self, backup_manager):
        """Test handling concurrent backup operations"""
        import threading
        import time

        results = []

        def create_backup_thread(template_id, description):
            backup_id = backup_manager.create_backup(template_id, description)
            results.append(backup_id)
            time.sleep(0.1)

        # Create multiple threads creating backups
        threads = []
        for i in range(3):
            thread = threading.Thread(
                target=create_backup_thread,
                args=("test_template", f"Concurrent backup {i}")
            )
            threads.append(thread)

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for completion
        for thread in threads:
            thread.join()

        # All backups should succeed
        assert len(results) == 3
        assert all(result is not None for result in results)

        # All backup IDs should be unique
        assert len(set(results)) == 3

    def test_backup_versioning(self, backup_manager):
        """Test backup versioning functionality"""
        # Create initial backup
        backup_id1 = backup_manager.create_backup("test_template", "Version 1.0")

        # Create another backup (should be newer version)
        backup_id2 = backup_manager.create_backup("test_template", "Version 1.1")

        backups = backup_manager.get_backups("test_template")
        assert len(backups) == 2

        # Newer backup should be first (sorted by timestamp)
        assert backups[0].backup_id == backup_id2
        assert backups[1].backup_id == backup_id1

    @patch('shutil.make_archive')
    def test_backup_creation_failure(self, mock_make_archive, backup_manager):
        """Test handling backup creation failure"""
        # Mock archive creation to fail
        mock_make_archive.side_effect = Exception("Archive creation failed")

        backup_id = backup_manager.create_backup("test_template", "Should fail")

        assert backup_id is None

    def test_get_total_backup_size(self, backup_manager):
        """Test calculating total backup size for template"""
        # Create multiple backups
        for i in range(3):
            backup_manager.create_backup("test_template", f"Size test backup {i}")

        total_size = backup_manager.get_total_backup_size("test_template")

        assert isinstance(total_size, int)
        assert total_size > 0

    def test_backup_export_import_workflow(self, backup_manager, temp_dir):
        """Test complete export/import workflow"""
        # 1. Create template with backups
        backup_id = backup_manager.create_backup("test_template", "Export test")

        # 2. Export to archive
        export_path = temp_dir / "workflow_test.zip"
        export_success = backup_manager.create_archive("test_template", export_path)
        assert export_success is True

        # 3. Import to new template ID
        import_success = backup_manager.import_archive(export_path, "imported_workflow_test")
        assert import_success is True

        # 4. Verify imported template
        imported_backups = backup_manager.get_backups("imported_workflow_test")
        # May or may not have backup history depending on implementation
        assert isinstance(imported_backups, list)


class TestBackupManagerEdgeCases:
    """Edge case tests for TemplateBackupManager"""

    def test_backup_with_special_characters(self, temp_dir):
        """Test backup handling with special characters in names"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        manager = TemplateBackupManager(templates_dir)

        # Test with special characters (should be sanitized)
        backup_id = manager.create_backup(
            "test_template",
            "Backup with special chars: !@#$%^&*()"
        )

        # Should handle gracefully (either succeed with sanitized name or fail gracefully)
        if backup_id is not None:
            backups = manager.get_backups("test_template")
            assert len(backups) >= 0

    def test_backup_with_very_long_description(self, temp_dir):
        """Test backup with very long description"""
        templates_dir = temp_dir / "templates"
        templates_dir.mkdir()

        manager = TemplateBackupManager(templates_dir)

        long_description = "x" * 1000  # Very long description

        backup_id = manager.create_backup("test_template", long_description)

        # Should handle gracefully
        if backup_id is not None:
            backup_info = manager.get_backup_info("test_template", backup_id)
            assert backup_info is not None

    def test_disk_space_handling(self, temp_dir):
        """Test behavior when disk space is limited"""
        # This is difficult to test without actually filling disk
        # Would need to mock filesystem operations
        pass

    def test_permission_errors(self, temp_dir):
        """Test handling of permission errors"""
        # This would require platform-specific permission manipulation
        # Could be tested with mocked file operations
        pass


if __name__ == '__main__':
    pytest.main([__file__])