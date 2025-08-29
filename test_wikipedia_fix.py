#!/usr/bin/env python3
"""
Test script for Wikipedia embed generation fix
Tests that the Wikipedia API calls work without blocking
"""

import sys
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QTextEdit
from PyQt6.QtCore import QThread, QObject, pyqtSignal


class WikipediaWorker(QObject):
    """Worker thread for Wikipedia API calls"""
    
    finished = pyqtSignal(dict)  # Signal emitted when work is done
    error = pyqtSignal(str)      # Signal emitted when error occurs
    
    def __init__(self, city_name: str):
        super().__init__()
        self.city_name = city_name
    
    def run(self):
        """Run the Wikipedia API call in background thread"""
        try:
            # Import the Wikipedia API
            from src.core.utils.wikipedia_api import WikipediaAPI
            wiki_api = WikipediaAPI()
            city_info = wiki_api.get_city_image_info(self.city_name)
            self.finished.emit(city_info)
        except Exception as e:
            self.error.emit(str(e))


class TestWindow(QMainWindow):
    """Test window for Wikipedia embed generation"""
    
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.wikipedia_worker = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup test UI"""
        self.setWindowTitle("Wikipedia Embed Test")
        self.setGeometry(100, 100, 600, 400)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Test button
        self.test_btn = QPushButton("Test Chicago Wikipedia Embed")
        self.test_btn.clicked.connect(self.test_wikipedia_embed)
        layout.addWidget(self.test_btn)
        
        # Output area
        self.output_area = QTextEdit()
        self.output_area.setPlainText("Click the button to test Wikipedia embed generation...")
        layout.addWidget(self.output_area)
        
        central_widget.setLayout(layout)
    
    def test_wikipedia_embed(self):
        """Test Wikipedia embed generation"""
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Testing...")
        self.output_area.setPlainText("Starting Wikipedia API test for Chicago...\n")
        
        # Clean up any existing worker thread
        self._cleanup_worker_thread()
        
        # Create new worker thread
        self.worker_thread = QThread()
        self.wikipedia_worker = WikipediaWorker("Chicago")
        self.wikipedia_worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.wikipedia_worker.run)
        self.wikipedia_worker.finished.connect(self._on_success)
        self.wikipedia_worker.error.connect(self._on_error)
        self.wikipedia_worker.finished.connect(self.worker_thread.quit)
        self.wikipedia_worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self._cleanup_worker_thread)
        
        # Start the worker thread
        self.worker_thread.start()
        
        # Update UI to show we're not blocking
        self.output_area.append("Wikipedia API call started in background thread...")
        self.output_area.append("UI should remain responsive during this operation.")
    
    def _on_success(self, city_info):
        """Handle successful API response"""
        self.output_area.append(f"\n=== SUCCESS ===")
        self.output_area.append(f"City: {city_info['city_name']}")
        self.output_area.append(f"Image URL: {city_info['image_url']}")
        self.output_area.append(f"Attribution: {city_info['attribution']}")
        self.output_area.append(f"Alt Text: {city_info['alt_text']}")
        self.output_area.append(f"Embed Code Length: {len(city_info['embed_code'])} characters")
        self.output_area.append(f"\nEmbed Code Preview:")
        self.output_area.append(city_info['embed_code'][:200] + "..." if len(city_info['embed_code']) > 200 else city_info['embed_code'])
        self._reset_button()
    
    def _on_error(self, error_message):
        """Handle API error"""
        self.output_area.append(f"\n=== ERROR ===")
        self.output_area.append(f"Failed to generate Wikipedia embed: {error_message}")
        self._reset_button()
    
    def _reset_button(self):
        """Reset button state"""
        self.test_btn.setEnabled(True)
        self.test_btn.setText("Test Chicago Wikipedia Embed")
    
    def _cleanup_worker_thread(self):
        """Clean up worker thread"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        if self.wikipedia_worker:
            self.wikipedia_worker.deleteLater()
            self.wikipedia_worker = None
        
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None
    
    def closeEvent(self, event):
        """Handle window close"""
        self._cleanup_worker_thread()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())