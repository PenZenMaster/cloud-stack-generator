"""
Module/Script Name: Progress Widget
Path: src/ui/components/progress_widget.py

Description:
Reusable progress bar widget with status text for long-running operations.
Based on the Cloud Deploy tab progress bar design.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-10

Last Modified Date:
2025-09-10

Comments:
* v1.00 - Initial implementation based on Cloud Deploy tab design
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QProgressBar, QTextEdit
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QTextCursor
from typing import Optional


class ProgressWidget(QWidget):
    """
    Reusable progress bar widget with status text display.
    
    Provides visual feedback for long-running operations with:
    - Progress bar (percentage or indeterminate)
    - Status text area for operation details
    - Show/hide functionality
    """
    
    # Signals
    cancelled = pyqtSignal()  # Emitted if cancel functionality is added later
    
    def __init__(self, parent=None):
        """
        Initialize progress widget.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setup_ui()
        self.hide()  # Hidden by default
    
    def setup_ui(self):
        """Setup the progress widget UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status text
        self.status_text = QTextEdit()
        self.status_text.setMaximumHeight(100)
        self.status_text.setReadOnly(True)
        self.status_text.setPlainText("Ready")
        layout.addWidget(self.status_text)
        
        self.setLayout(layout)
    
    def show_progress(self, initial_message: str = "Starting operation...", 
                     max_value: int = 100, indeterminate: bool = False):
        """
        Show progress bar and start operation feedback.
        
        Args:
            initial_message: Initial status message
            max_value: Maximum progress value (for percentage mode)
            indeterminate: If True, shows indeterminate progress
        """
        self.show()
        self.progress_bar.setVisible(True)
        
        if indeterminate:
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
        else:
            self.progress_bar.setRange(0, max_value)
            self.progress_bar.setValue(0)
        
        self.update_status(initial_message)
    
    def hide_progress(self):
        """Hide progress bar and widget"""
        self.progress_bar.setVisible(False)
        self.hide()
    
    def update_progress(self, value: int, message: Optional[str] = None):
        """
        Update progress value and optional status message.
        
        Args:
            value: Progress value
            message: Optional status message to append
        """
        if not self.progress_bar.maximum() == 0:  # Not in indeterminate mode
            self.progress_bar.setValue(value)
        
        if message:
            self.update_status(message)
    
    def update_status(self, message: str, append: bool = True):
        """
        Update status text.
        
        Args:
            message: Status message
            append: If True, append to existing text. If False, replace.
        """
        if append and self.status_text.toPlainText().strip():
            current_text = self.status_text.toPlainText()
            self.status_text.setPlainText(f"{current_text}\n{message}")
        else:
            self.status_text.setPlainText(message)
        
        # Auto-scroll to bottom
        self.status_text.moveCursor(QTextCursor.MoveOperation.End)
    
    def set_progress_range(self, min_value: int, max_value: int):
        """Set progress bar range"""
        self.progress_bar.setRange(min_value, max_value)
    
    def get_progress_value(self) -> int:
        """Get current progress value"""
        return self.progress_bar.value()
    
    def is_indeterminate(self) -> bool:
        """Check if progress bar is in indeterminate mode"""
        return self.progress_bar.maximum() == 0
    
    def clear_status(self):
        """Clear status text"""
        self.status_text.clear()
    
    def set_status_height(self, height: int):
        """Set status text area height"""
        self.status_text.setMaximumHeight(height)