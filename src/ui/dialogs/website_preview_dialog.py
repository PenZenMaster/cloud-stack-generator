"""
Module/Script Name: Website Preview Dialog
Path: E:/projects/cloud-stack-generator/src/ui/dialogs/website_preview_dialog.py

Description:
Website preview dialog for QA testing before generation. Allows users to review all pages
and content before publishing the website.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
August 31, 2025

Last Modified Date:
August 31, 2025

Comments:
* v1.00 - Initial implementation with page navigation and HTML preview
"""

import tempfile
import webbrowser
from pathlib import Path
from typing import Dict, List, Optional
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget,
    QListWidgetItem, QTextEdit, QLabel, QSplitter, QMessageBox,
    QProgressBar, QComboBox, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from ...core.config.models import ClientConfig
from ...core.generators.page_generator import PageGenerator
from src.core.utils.logger import get_logger

logger = get_logger(__name__)


class PreviewGenerationThread(QThread):
    """Thread for generating preview files without blocking UI"""
    
    progress_updated = pyqtSignal(int, str)
    preview_ready = pyqtSignal(dict, list)  # preview_data, file_list
    error_occurred = pyqtSignal(str)
    
    def __init__(self, config: ClientConfig, temp_dir: str):
        super().__init__()
        self.config = config
        self.temp_dir = temp_dir
        
    def run(self):
        """Generate preview files in background thread"""
        try:
            self.progress_updated.emit(10, "Initializing preview generation...")
            
            # Create page generator
            generator = PageGenerator(output_base_dir=self.temp_dir)
            
            self.progress_updated.emit(30, "Generating home page...")
            
            # Generate website in preview mode
            result = generator.generate_complete_website(self.config)
            
            if not result.success:
                self.error_occurred.emit(f"Preview generation failed: {result.errors}")
                return
                
            self.progress_updated.emit(70, "Processing generated files...")
            
            # Read generated files for preview
            preview_data = {}
            file_list = []
            
            for file_path in result.generated_files:
                path_obj = Path(file_path)
                if path_obj.suffix == '.html':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Extract page title for display
                        page_name = path_obj.stem
                        if page_name == 'index':
                            page_name = 'Home'
                        elif page_name.startswith('city_'):
                            city_name = page_name.replace('city_', '').replace('_', ' ').title()
                            page_name = f"City: {city_name}"
                        
                        preview_data[page_name] = {
                            'content': content,
                            'file_path': file_path,
                            'file_name': path_obj.name
                        }
                        file_list.append(page_name)
                        
                    except Exception as e:
                        logger.error(f"Error reading {file_path}: {e}")
            
            self.progress_updated.emit(90, "Finalizing preview...")
            
            # Sort file list for consistent display
            file_list.sort(key=lambda x: (x != 'Home', x))
            
            self.progress_updated.emit(100, "Preview ready!")
            self.preview_ready.emit(preview_data, file_list)
            
        except Exception as e:
            self.error_occurred.emit(f"Error during preview generation: {str(e)}")


class WebsitePreviewDialog(QDialog):
    """Dialog for previewing website before generation"""
    
    def __init__(self, config: ClientConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.preview_data: Dict[str, Dict[str, str]] = {}
        self.temp_dir: Optional[str] = None
        self.generation_thread: Optional[PreviewGenerationThread] = None
        
        self.setWindowTitle("Website Preview - QA Testing")
        self.setMinimumSize(1000, 700)
        self.setup_ui()
        self.start_preview_generation()
        
    def setup_ui(self):
        """Setup the preview dialog UI"""
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Website Preview & QA Testing")
        header_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(True)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Initializing preview generation...")
        layout.addWidget(self.status_label)
        
        # Main content area (hidden until preview is ready)
        self.content_widget = QSplitter(Qt.Orientation.Horizontal)
        self.content_widget.setVisible(False)
        
        # Left panel - Page list
        left_panel = QVBoxLayout()
        
        pages_label = QLabel("Pages:")
        pages_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_panel.addWidget(pages_label)
        
        self.page_list = QListWidget()
        self.page_list.setMaximumWidth(200)
        self.page_list.currentRowChanged.connect(self.on_page_selected)
        left_panel.addWidget(self.page_list)
        
        left_widget = QVBoxLayout()
        left_widget.addLayout(left_panel)
        left_container = QWidget()
        left_container.setLayout(left_widget)
        
        # Right panel - Preview content
        right_panel = QVBoxLayout()
        
        # Preview controls
        controls_layout = QHBoxLayout()
        
        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItems(["HTML Source", "Formatted Preview"])
        self.view_mode_combo.currentTextChanged.connect(self.on_view_mode_changed)
        
        self.open_in_browser_btn = QPushButton("Open in Browser")
        self.open_in_browser_btn.clicked.connect(self.open_current_page_in_browser)
        
        controls_layout.addWidget(QLabel("View:"))
        controls_layout.addWidget(self.view_mode_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(self.open_in_browser_btn)
        
        right_panel.addLayout(controls_layout)
        
        # Preview area
        self.preview_area = QTextEdit()
        self.preview_area.setFont(QFont("Consolas", 10))
        self.preview_area.setReadOnly(True)
        right_panel.addWidget(self.preview_area)
        
        right_container = QWidget()
        right_container.setLayout(right_panel)
        
        # Add to splitter
        self.content_widget.addWidget(left_container)
        self.content_widget.addWidget(right_container)
        self.content_widget.setSizes([200, 800])
        
        layout.addWidget(self.content_widget)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("Refresh Preview")
        self.refresh_btn.clicked.connect(self.refresh_preview)
        self.refresh_btn.setVisible(False)
        
        self.generate_btn = QPushButton("Approve & Generate Website")
        self.generate_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            """
        )
        self.generate_btn.clicked.connect(self.approve_and_generate)
        self.generate_btn.setVisible(False)
        
        close_btn = QPushButton("Cancel")
        close_btn.clicked.connect(self.reject)
        
        button_layout.addWidget(self.refresh_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.generate_btn)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def start_preview_generation(self):
        """Start generating preview in background thread"""
        # Create temporary directory for preview
        self.temp_dir = tempfile.mkdtemp(prefix="awg_preview_")
        
        # Start generation thread
        self.generation_thread = PreviewGenerationThread(self.config, self.temp_dir)
        self.generation_thread.progress_updated.connect(self.on_progress_updated)
        self.generation_thread.preview_ready.connect(self.on_preview_ready)
        self.generation_thread.error_occurred.connect(self.on_preview_error)
        self.generation_thread.finished.connect(self.on_generation_finished)
        self.generation_thread.start()
        
    def on_progress_updated(self, progress: int, message: str):
        """Handle progress updates from generation thread"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(message)
        
    def on_preview_ready(self, preview_data: Dict, file_list: List[str]):
        """Handle preview generation completion"""
        self.preview_data = preview_data
        
        # Populate page list
        self.page_list.clear()
        for page_name in file_list:
            item = QListWidgetItem(page_name)
            self.page_list.addItem(item)
            
        # Hide progress, show content
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"Preview ready - {len(file_list)} pages generated")
        self.content_widget.setVisible(True)
        self.refresh_btn.setVisible(True)
        self.generate_btn.setVisible(True)
        
        # Select first page
        if self.page_list.count() > 0:
            self.page_list.setCurrentRow(0)
            
    def on_preview_error(self, error_message: str):
        """Handle preview generation errors"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("Preview generation failed")
        
        QMessageBox.critical(
            self,
            "Preview Generation Failed",
            f"Failed to generate website preview:\n\n{error_message}"
        )
        
    def on_generation_finished(self):
        """Handle generation thread completion"""
        if self.generation_thread:
            self.generation_thread.deleteLater()
            self.generation_thread = None
            
    def on_page_selected(self, current_row: int):
        """Handle page selection in list"""
        if current_row < 0 or current_row >= self.page_list.count():
            return
            
        page_name = self.page_list.item(current_row).text()
        if page_name in self.preview_data:
            self.display_page_content(page_name)
            
    def display_page_content(self, page_name: str):
        """Display content for selected page"""
        if page_name not in self.preview_data:
            return
            
        page_data = self.preview_data[page_name]
        content = page_data['content']
        
        if self.view_mode_combo.currentText() == "HTML Source":
            self.preview_area.setPlainText(content)
        else:
            # For formatted preview, show HTML with some basic formatting
            formatted_content = self.format_html_for_preview(content)
            self.preview_area.setHtml(formatted_content)
            
    def format_html_for_preview(self, html_content: str) -> str:
        """Format HTML content for better preview display"""
        # Simple HTML formatting for preview
        # This is a basic implementation - could be enhanced with proper HTML parsing
        
        # Extract key sections for preview
        lines = html_content.split('\n')
        preview_lines = []
        
        in_head = False
        in_body = False
        
        for line in lines:
            line = line.strip()
            
            if '<head>' in line:
                in_head = True
                preview_lines.append("<h3>Document Head:</h3>")
            elif '</head>' in line:
                in_head = False
                preview_lines.append("<hr>")
            elif '<title>' in line:
                preview_lines.append(f"<b>Title:</b> {line}")
            elif '<body>' in line:
                in_body = True
                preview_lines.append("<h3>Page Body:</h3>")
            elif in_head and ('meta' in line or 'link' in line):
                preview_lines.append(f"<code>{line}</code><br>")
            elif in_body and line and not line.startswith('<!--'):
                # Show body content with basic formatting
                if line.startswith('<h'):
                    preview_lines.append(f"<b>{line}</b><br>")
                elif line.startswith('<p'):
                    preview_lines.append(f"{line}<br>")
                elif len(line) > 0:
                    preview_lines.append(f"{line}<br>")
                    
        return ''.join(preview_lines)
        
    def on_view_mode_changed(self):
        """Handle view mode change"""
        current_row = self.page_list.currentRow()
        if current_row >= 0:
            self.on_page_selected(current_row)
            
    def open_current_page_in_browser(self):
        """Open current page in web browser"""
        current_row = self.page_list.currentRow()
        if current_row < 0:
            return
            
        page_name = self.page_list.item(current_row).text()
        if page_name in self.preview_data:
            file_path = self.preview_data[page_name]['file_path']
            webbrowser.open(f"file://{file_path}")
            
    def refresh_preview(self):
        """Refresh the preview with current configuration"""
        self.content_widget.setVisible(False)
        self.refresh_btn.setVisible(False)
        self.generate_btn.setVisible(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Refreshing preview...")
        
        self.start_preview_generation()
        
    def approve_and_generate(self):
        """User approved preview - proceed with actual generation"""
        reply = QMessageBox.question(
            self,
            "Generate Website", 
            "You have approved the website preview. Would you like to generate the final website now?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.accept()  # Close dialog and return accepted
        else:
            # User clicked No - close both popup and preview dialog
            self.reject()  # Close preview dialog and return rejected
            
    def cleanup(self):
        """Clean up temporary files"""
        if self.temp_dir and Path(self.temp_dir).exists():
            try:
                import shutil
                shutil.rmtree(self.temp_dir)
            except Exception as e:
                logger.warning(f"Error cleaning up temp directory: {e}")
                
    def closeEvent(self, event):
        """Handle dialog close event"""
        if self.generation_thread and self.generation_thread.isRunning():
            self.generation_thread.terminate()
            self.generation_thread.wait()
            
        self.cleanup()
        event.accept()
        
    def reject(self):
        """Handle dialog rejection"""
        self.cleanup()
        super().reject()
        
    def accept(self):
        """Handle dialog acceptance"""
        self.cleanup()
        super().accept()