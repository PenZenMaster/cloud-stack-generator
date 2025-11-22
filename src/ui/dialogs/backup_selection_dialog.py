"""
Backup Selection Dialog - Select and restore template backups
Path: E:/projects/cloud-stack-generator/src/ui/dialogs/backup_selection_dialog.py

Description:
Dialog for selecting template backups for restoration.
Shows backup metadata and allows selection.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Initial backup selection dialog
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTextEdit, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from typing import List, Optional
import sys
from pathlib import Path

# Add the src directory to the Python path for imports
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.templates.backup_manager import BackupMetadata  # noqa: E402


class BackupSelectionDialog(QDialog):
    """Dialog for selecting template backups"""

    def __init__(self, backups: List[BackupMetadata], parent=None):
        super().__init__(parent)
        self.backups = backups
        self.selected_backup = None

        self._setup_ui()
        self._populate_table()

    def _setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Select Backup to Restore")
        self.setMinimumSize(800, 500)
        self.resize(900, 600)

        # Main layout
        layout = QVBoxLayout(self)

        # Header
        header_label = QLabel("Select a backup to restore:")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header_label)

        # Splitter for table and details
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)

        # Backup table
        self.backup_table = QTableWidget()
        self.backup_table.setColumnCount(6)
        self.backup_table.setHorizontalHeaderLabels([
            "Backup ID", "Type", "Created Date", "Version", "Size", "Description"
        ])

        # Configure table
        header = self.backup_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Backup ID
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Version
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Size
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)  # Description

        self.backup_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.backup_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.backup_table.itemSelectionChanged.connect(self._on_selection_changed)

        splitter.addWidget(self.backup_table)

        # Details section
        details_group = QGroupBox("Backup Details")
        details_layout = QVBoxLayout(details_group)

        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(150)
        self.details_text.setReadOnly(True)
        details_layout.addWidget(self.details_text)

        splitter.addWidget(details_group)

        # Set splitter proportions (70% table, 30% details)
        splitter.setSizes([350, 150])

        # Button layout
        button_layout = QHBoxLayout()

        # Info button
        info_button = QPushButton("Show Info")
        info_button.clicked.connect(self._show_backup_info)
        button_layout.addWidget(info_button)

        button_layout.addStretch()

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        # Restore button
        self.restore_button = QPushButton("Restore Selected")
        self.restore_button.setEnabled(False)
        self.restore_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.restore_button.clicked.connect(self.accept)
        button_layout.addWidget(self.restore_button)

        layout.addLayout(button_layout)

    def _populate_table(self):
        """Populate the table with backup data"""
        self.backup_table.setRowCount(len(self.backups))

        for row, backup in enumerate(self.backups):
            # Backup ID
            id_item = QTableWidgetItem(backup.backup_id)
            id_item.setData(Qt.ItemDataRole.UserRole, backup)
            self.backup_table.setItem(row, 0, id_item)

            # Type
            type_item = QTableWidgetItem(backup.backup_type.title())
            if backup.backup_type == "manual":
                type_item.setBackground(Qt.GlobalColor.lightGreen)
            elif backup.backup_type == "auto":
                type_item.setBackground(Qt.GlobalColor.lightBlue)
            else:  # pre_edit
                type_item.setBackground(Qt.GlobalColor.lightYellow)
            self.backup_table.setItem(row, 1, type_item)

            # Created date
            try:
                from datetime import datetime
                created_dt = datetime.fromisoformat(backup.created_date.replace('Z', '+00:00'))
                date_str = created_dt.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                date_str = backup.created_date
            date_item = QTableWidgetItem(date_str)
            self.backup_table.setItem(row, 2, date_item)

            # Version
            version_item = QTableWidgetItem(backup.version)
            self.backup_table.setItem(row, 3, version_item)

            # Size
            size_mb = backup.file_size / (1024 * 1024)
            if size_mb < 1:
                size_str = f"{backup.file_size / 1024:.1f} KB"
            else:
                size_str = f"{size_mb:.2f} MB"
            size_item = QTableWidgetItem(size_str)
            self.backup_table.setItem(row, 4, size_item)

            # Description
            desc_item = QTableWidgetItem(backup.description)
            self.backup_table.setItem(row, 5, desc_item)

        # Sort by creation date (newest first)
        self.backup_table.sortItems(2, Qt.SortOrder.DescendingOrder)

    def _on_selection_changed(self):
        """Handle table selection changes"""
        selected_rows = self.backup_table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            backup_item = self.backup_table.item(row, 0)
            self.selected_backup = backup_item.data(Qt.ItemDataRole.UserRole)
            self.restore_button.setEnabled(True)
            self._update_details()
        else:
            self.selected_backup = None
            self.restore_button.setEnabled(False)
            self.details_text.clear()

    def _update_details(self):
        """Update the details section with selected backup info"""
        if not self.selected_backup:
            return

        backup = self.selected_backup

        details_html = f"""
        <h3>{backup.template_name}</h3>
        <p><strong>Backup ID:</strong> {backup.backup_id}</p>
        <p><strong>Template ID:</strong> {backup.template_id}</p>
        <p><strong>Version:</strong> {backup.version}</p>
        <p><strong>Type:</strong> {backup.backup_type.title()}</p>
        <p><strong>Created:</strong> {backup.created_date}</p>
        <p><strong>Author:</strong> {backup.created_by}</p>
        <p><strong>Size:</strong> {backup.file_size:,} bytes</p>
        <p><strong>Hash:</strong> {backup.file_hash}</p>
        <p><strong>Description:</strong> {backup.description}</p>
        """

        self.details_text.setHtml(details_html)

    def _show_backup_info(self):
        """Show detailed backup information"""
        if not self.selected_backup:
            QMessageBox.information(self, "No Selection", "Please select a backup first.")
            return

        backup = self.selected_backup

        info_text = f"""Backup Information

Backup ID: {backup.backup_id}
Template: {backup.template_name} ({backup.template_id})
Version: {backup.version}
Type: {backup.backup_type.title()}
Created: {backup.created_date}
Created By: {backup.created_by}
File Size: {backup.file_size:,} bytes
File Hash: {backup.file_hash}

Description:
{backup.description}
"""

        QMessageBox.information(self, "Backup Information", info_text)

    def get_selected_backup(self) -> Optional[BackupMetadata]:
        """Get the selected backup"""
        return self.selected_backup