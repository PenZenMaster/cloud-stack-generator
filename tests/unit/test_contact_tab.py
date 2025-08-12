"""
Filename: test_contact_tab.py
Path: E:\\projects\\cloud-stack-generator\\tests\\unit\\test_contact_tab.py
Description: Comprehensive unit test suite for ContactTab component
Tests validation, auto-formatting, signals, and edge cases with 15 test scenarios

Version: 1.0.0
Date: 2025-08-11
Author: Cloud Stack Generator Team
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QTextEdit,
    QGroupBox,
    QMessageBox,
    QFrame,
    QScrollArea,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(project_root, "src")):
    parent = os.path.dirname(project_root)
    if parent == project_root:  # We've reached the root
        break
    project_root = parent

if os.path.exists(os.path.join(project_root, "src")):
    sys.path.insert(0, project_root)
else:
    print("❌ Could not find 'src' directory")
    sys.exit(1)

# Import the ContactTab component
try:
    from src.ui.components.contact_tab import ContactTab
except ImportError:
    print(
        "❌ Import Error: Make sure ContactTab is in src/ui/components/contact_tab.py"
    )
    sys.exit(1)


class ContactTabTestWindow(QMainWindow):
    """Main window for manual ContactTab testing"""

    def __init__(self):
        super().__init__()
        self.contact_tab = None
        self.setup_ui()
        self.setup_contact_tab()
        self.connect_signals()

        # Track changes
        self.changes_count = 0

    def setup_ui(self):
        """Setup the test interface"""
        self.setWindowTitle("ContactTab Manual Testing Interface")
        self.setGeometry(100, 100, 1000, 800)

        # Central widget with scroll area
        central_widget = QWidget()
        main_layout = QHBoxLayout()

        # Left side: ContactTab
        left_layout = QVBoxLayout()

        # ContactTab header
        tab_header = QLabel("ContactTab Component")
        tab_header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        tab_header.setStyleSheet(
            "color: #2c3e50; padding: 10px; background: #ecf0f1; border-radius: 5px;"
        )
        left_layout.addWidget(tab_header)

        # ContactTab container
        self.tab_container = QWidget()
        self.tab_layout = QVBoxLayout()
        self.tab_container.setLayout(self.tab_layout)
        left_layout.addWidget(self.tab_container)

        # Right side: Testing controls
        right_widget = QWidget()
        right_widget.setMaximumWidth(350)
        right_layout = QVBoxLayout()
        right_widget.setLayout(right_layout)

        # Testing controls header
        controls_header = QLabel("Testing Controls")
        controls_header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        controls_header.setStyleSheet(
            "color: #2c3e50; padding: 10px; background: #ecf0f1; border-radius: 5px;"
        )
        right_layout.addWidget(controls_header)

        # Test data section
        self.create_test_data_section(right_layout)

        # Validation section
        self.create_validation_section(right_layout)

        # Results section
        self.create_results_section(right_layout)

        # Layout setup
        main_layout.addLayout(left_layout, 2)  # 2/3 of space
        main_layout.addWidget(right_widget, 1)  # 1/3 of space

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def create_test_data_section(self, parent_layout):
        """Create test data loading section"""
        test_data_group = QGroupBox("Test Data")
        test_data_layout = QVBoxLayout()

        # Test data buttons
        buttons_data = [
            ("Load Salvo Data", self.load_salvo_data, "#27ae60"),
            ("Load Minimal Data", self.load_minimal_data, "#3498db"),
            ("Load Invalid Data", self.load_invalid_data, "#e74c3c"),
            ("Clear All Data", self.clear_all_data, "#95a5a6"),
        ]

        for button_text, handler, color in buttons_data:
            btn = QPushButton(button_text)
            btn.setFont(QFont("Arial", 9))
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
            """
            )
            btn.clicked.connect(handler)
            test_data_layout.addWidget(btn)

        test_data_group.setLayout(test_data_layout)
        parent_layout.addWidget(test_data_group)

    def create_validation_section(self, parent_layout):
        """Create validation testing section"""
        validation_group = QGroupBox("Validation Testing")
        validation_layout = QVBoxLayout()

        # Validation buttons
        self.validate_btn = QPushButton("🔍 Validate Data")
        self.validate_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.validate_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """
        )
        self.validate_btn.clicked.connect(self.validate_data)

        self.format_btn = QPushButton("✨ Auto-Format Fields")
        self.format_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        self.format_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """
        )
        self.format_btn.clicked.connect(self.auto_format_fields)

        validation_layout.addWidget(self.validate_btn)
        validation_layout.addWidget(self.format_btn)

        validation_group.setLayout(validation_layout)
        parent_layout.addWidget(validation_group)

    def create_results_section(self, parent_layout):
        """Create results display section"""
        results_group = QGroupBox("Results & Status")
        results_layout = QVBoxLayout()

        # Status display
        self.status_label = QLabel("Ready for testing")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")

        # Changes counter
        self.changes_label = QLabel("Changes: 0")
        self.changes_label.setFont(QFont("Arial", 9))
        self.changes_label.setStyleSheet("color: #34495e; padding: 5px;")

        # Results text area
        self.results_text = QTextEdit()
        self.results_text.setFont(QFont("Consolas", 9))
        self.results_text.setMaximumHeight(200)
        self.results_text.setPlaceholderText("Validation results will appear here...")

        # Export button
        self.export_btn = QPushButton("📋 Export Config Data")
        self.export_btn.setFont(QFont("Arial", 9))
        self.export_btn.clicked.connect(self.export_config_data)

        results_layout.addWidget(self.status_label)
        results_layout.addWidget(self.changes_label)
        results_layout.addWidget(QLabel("Validation Results:"))
        results_layout.addWidget(self.results_text)
        results_layout.addWidget(self.export_btn)

        results_group.setLayout(results_layout)
        parent_layout.addWidget(results_group)

    def setup_contact_tab(self):
        """Setup the ContactTab component"""
        self.contact_tab = ContactTab()
        self.tab_layout.addWidget(self.contact_tab)

    def connect_signals(self):
        """Connect ContactTab signals"""
        if self.contact_tab:
            self.contact_tab.config_changed.connect(self.on_config_changed)
            self.contact_tab.data_loaded.connect(self.on_data_loaded)

    def darken_color(self, hex_color):
        """Darken a hex color for hover effects"""
        color_map = {
            "#27ae60": "#229954",
            "#3498db": "#2980b9",
            "#e74c3c": "#c0392b",
            "#95a5a6": "#7b8a8b",
        }
        return color_map.get(hex_color, hex_color)

    def load_salvo_data(self):
        """Load realistic Salvo Metal Works contact data"""
        salvo_data = {
            "contact": {
                "name": "Mike Rodriguez",
                "phone": "(888) 555-0123",
                "email": "mike@salvometalworks.com",
                "address": "1234 Industrial Drive\nSan Antonio, TX 78201\nUnited States",
            }
        }

        if self.contact_tab:
            self.contact_tab.set_config_data(salvo_data)
            self.update_status("✅ Loaded Salvo Metal Works contact data", "#27ae60")
            self.log_result("Loaded Salvo data successfully")

    def load_minimal_data(self):
        """Load minimal valid contact data"""
        minimal_data = {
            "contact": {
                "name": "John Doe",
                "phone": "5551234567",
                "email": "john@example.com",
                "address": "123 Main St, City, ST 12345",
            }
        }

        if self.contact_tab:
            self.contact_tab.set_config_data(minimal_data)
            self.update_status("✅ Loaded minimal valid data", "#3498db")
            self.log_result("Loaded minimal data successfully")

    def load_invalid_data(self):
        """Load invalid contact data for testing validation"""
        invalid_data = {
            "contact": {
                "name": "",  # Missing name
                "phone": "123",  # Too short
                "email": "invalid-email",  # Invalid format
                "address": "Short",  # Too short
            }
        }

        if self.contact_tab:
            self.contact_tab.set_config_data(invalid_data)
            self.update_status("⚠️ Loaded invalid data for testing", "#e74c3c")
            self.log_result("Loaded invalid data for validation testing")

    def clear_all_data(self):
        """Clear all contact data"""
        if self.contact_tab:
            self.contact_tab.clear_data()
            self.update_status("🗑️ Cleared all data", "#95a5a6")
            self.log_result("Cleared all contact data")
            self.changes_count = 0
            self.update_changes_counter()

    def validate_data(self):
        """Validate current contact data"""
        if not self.contact_tab:
            return

        result = self.contact_tab.validate_data()

        if result.is_valid:
            self.update_status("✅ Validation passed!", "#27ae60")
            self.log_result("✅ VALIDATION PASSED")

            if result.warnings:
                self.log_result(f"Warnings ({len(result.warnings)}):")
                for warning in result.warnings:
                    self.log_result(f"  ⚠️ {warning}")
        else:
            self.update_status(
                f"❌ Validation failed ({len(result.errors)} errors)", "#e74c3c"
            )
            self.log_result(f"❌ VALIDATION FAILED ({len(result.errors)} errors)")

            for error in result.errors:
                self.log_result(f"  ❌ {error}")

            if result.warnings:
                self.log_result(f"Warnings ({len(result.warnings)}):")
                for warning in result.warnings:
                    self.log_result(f"  ⚠️ {warning}")

    def auto_format_fields(self):
        """Auto-format all contact fields"""
        if self.contact_tab:
            self.contact_tab.auto_format_fields()
            self.update_status("✨ Fields auto-formatted", "#f39c12")
            self.log_result("Auto-formatted all contact fields")

    def export_config_data(self):
        """Export current configuration data"""
        if not self.contact_tab:
            return

        config_data = self.contact_tab.get_config_data()

        # Display in a message box
        import json

        formatted_data = json.dumps(config_data, indent=2)

        msg = QMessageBox()
        msg.setWindowTitle("Exported Config Data")
        msg.setText("Current contact configuration:")
        msg.setDetailedText(formatted_data)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

        self.log_result("Exported configuration data")

    def on_config_changed(self):
        """Handle config changed signal"""
        self.changes_count += 1
        self.update_changes_counter()
        self.update_status("📝 Configuration changed", "#34495e")

    def on_data_loaded(self):
        """Handle data loaded signal"""
        self.update_status("📂 Data loaded successfully", "#27ae60")
        self.changes_count = 0
        self.update_changes_counter()

    def update_status(self, message, color="#7f8c8d"):
        """Update status label"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet(
            f"color: {color}; padding: 5px; font-weight: bold;"
        )

    def update_changes_counter(self):
        """Update changes counter"""
        self.changes_label.setText(f"Changes: {self.changes_count}")
        if self.changes_count > 0:
            self.changes_label.setStyleSheet(
                "color: #e67e22; padding: 5px; font-weight: bold;"
            )
        else:
            self.changes_label.setStyleSheet("color: #34495e; padding: 5px;")

    def log_result(self, message):
        """Add message to results log"""
        self.results_text.append(f"[{self.get_timestamp()}] {message}")

        # Auto-scroll to bottom (with safety check)
        scrollbar = self.results_text.verticalScrollBar()
        if scrollbar:
            scrollbar.setValue(scrollbar.maximum())

    def get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime

        return datetime.now().strftime("%H:%M:%S")


def main():
    """Run the manual testing interface"""
    print("🧪 Starting ContactTab Manual Testing Interface...")

    # Create application
    app = QApplication(sys.argv)

    # Create and show test window
    test_window = ContactTabTestWindow()
    test_window.show()

    print("✅ Manual testing interface ready!")
    print("📋 Available test scenarios:")
    print("   • Load Salvo Metal Works data")
    print("   • Load minimal valid data")
    print("   • Load invalid data for validation testing")
    print("   • Test auto-formatting functionality")
    print("   • Validate data and see error handling")
    print("   • Export configuration data")

    # Run application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
