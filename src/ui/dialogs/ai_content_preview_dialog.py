"""
AI Content Preview Dialog
Path: E:/projects/cloud-stack-generator/src/ui/dialogs/ai_content_preview_dialog.py

Description:
Dialog for previewing and accepting AI-generated content before inserting it into
input fields. Provides Accept, Regenerate, and Cancel options.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-20

Last Modified Date:
2025-11-20

Comments:
* v1.00 - Initial creation for AI content preview
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QProgressBar
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from typing import Callable, Optional


class AIContentPreviewDialog(QDialog):
    """
    Dialog for previewing AI-generated content.

    Provides:
    - Preview of generated content
    - Accept button to insert content
    - Regenerate button to generate new content
    - Cancel button to discard
    """

    content_accepted = pyqtSignal(str)  # Emitted when content is accepted
    regenerate_requested = pyqtSignal()  # Emitted when regenerate is clicked

    def __init__(
        self,
        title: str,
        field_name: str,
        content: str,
        regenerate_callback: Optional[Callable] = None,
        parent=None
    ):
        """
        Initialize the preview dialog.

        Args:
            title: Dialog window title
            field_name: Name of the field being generated
            content: Generated content to preview
            regenerate_callback: Function to call when regenerating
            parent: Parent widget
        """
        super().__init__(parent)
        self.field_name = field_name
        self.regenerate_callback = regenerate_callback
        self.is_regenerating = False

        self.setWindowTitle(title)
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)

        self.setup_ui(content)

    def setup_ui(self, content: str):
        """Setup the dialog UI"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title label
        title_label = QLabel(f"Preview: {self.field_name}")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title_label)

        # Info label
        info_label = QLabel(
            "Review the AI-generated content below. You can accept it, regenerate for a new version, or cancel."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666;")
        layout.addWidget(info_label)

        # Content preview
        self.content_preview = QTextEdit()
        self.content_preview.setFont(QFont("Arial", 10))
        self.content_preview.setPlainText(content)
        self.content_preview.setReadOnly(False)  # Allow editing
        layout.addWidget(self.content_preview)

        # Edit hint
        edit_hint = QLabel("Tip: You can edit the content directly before accepting.")
        edit_hint.setStyleSheet("color: #999; font-style: italic;")
        layout.addWidget(edit_hint)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                height: 20px;
            }
            QProgressBar::chunk {
                background-color: #007bff;
            }
        """)
        layout.addWidget(self.progress_bar)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Accept button
        self.accept_button = QPushButton("Accept")
        self.accept_button.setMinimumWidth(100)
        self.accept_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.accept_button.clicked.connect(self._on_accept)
        button_layout.addWidget(self.accept_button)

        # Regenerate button
        self.regenerate_button = QPushButton("Regenerate")
        self.regenerate_button.setMinimumWidth(100)
        self.regenerate_button.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #000;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                color: white;
            }
        """)
        self.regenerate_button.clicked.connect(self._on_regenerate)
        if not self.regenerate_callback:
            self.regenerate_button.setEnabled(False)
        button_layout.addWidget(self.regenerate_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumWidth(100)
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _on_accept(self):
        """Handle accept button click"""
        content = self.content_preview.toPlainText().strip()
        self.content_accepted.emit(content)
        self.accept()

    def _on_regenerate(self):
        """Handle regenerate button click"""
        if not self.regenerate_callback:
            return

        # Disable buttons and show progress
        self.is_regenerating = True
        self.accept_button.setEnabled(False)
        self.regenerate_button.setEnabled(False)
        self.progress_bar.setVisible(True)

        # Call regenerate callback
        try:
            new_content = self.regenerate_callback()
            if new_content:
                self.content_preview.setPlainText(new_content)
        finally:
            # Re-enable buttons and hide progress
            self.is_regenerating = False
            self.accept_button.setEnabled(True)
            self.regenerate_button.setEnabled(True)
            self.progress_bar.setVisible(False)

    def update_content(self, content: str):
        """Update the preview content"""
        self.content_preview.setPlainText(content)
