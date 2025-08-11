"""
Filename: tests/manual_test_business_tab.py
Path: E:/projects/cloud-stack-generator/tests/manual_test_business_tab.py
Description: Manual interactive test for BusinessTab component

Version: 1.0.0
Date: 2025-08-10
Author: Cloud Stack Generator Team
"""

import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QTextEdit,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt

# Add src directory to path for imports
project_root = os.path.join(os.path.dirname(__file__), "..")
src_path = os.path.join(project_root, "src")
sys.path.insert(0, src_path)

try:
    from ui.components.business_tab import BusinessTab
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Tried to import from: {src_path}")
    print(f"Current working directory: {os.getcwd()}")
    raise


class BusinessTabTestWindow(QMainWindow):
    """Test window for manually testing BusinessTab component"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("BusinessTab Manual Test")
        self.setGeometry(100, 100, 800, 700)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout()

        # Left side: BusinessTab
        self.business_tab = BusinessTab()
        main_layout.addWidget(self.business_tab, 2)  # 2/3 of width

        # Right side: Control panel
        control_panel = self.create_control_panel()
        main_layout.addWidget(control_panel, 1)  # 1/3 of width

        central_widget.setLayout(main_layout)

        # Connect signals
        self.business_tab.config_changed.connect(self.on_config_changed)
        self.business_tab.validation_requested.connect(self.on_validation_requested)

    def create_control_panel(self):
        """Create control panel for testing"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Test buttons
        self.load_salvo_btn = QPushButton("Load Salvo Metal Works Data")
        self.load_salvo_btn.clicked.connect(self.load_salvo_data)
        layout.addWidget(self.load_salvo_btn)

        self.load_minimal_btn = QPushButton("Load Minimal Data")
        self.load_minimal_btn.clicked.connect(self.load_minimal_data)
        layout.addWidget(self.load_minimal_btn)

        self.load_invalid_btn = QPushButton("Load Invalid Data")
        self.load_invalid_btn.clicked.connect(self.load_invalid_data)
        layout.addWidget(self.load_invalid_btn)

        self.clear_btn = QPushButton("Clear All Data")
        self.clear_btn.clicked.connect(self.business_tab.clear_data)
        layout.addWidget(self.clear_btn)

        self.validate_btn = QPushButton("Validate Data")
        self.validate_btn.clicked.connect(self.validate_data)
        layout.addWidget(self.validate_btn)

        self.get_config_btn = QPushButton("Get Config Data")
        self.get_config_btn.clicked.connect(self.get_config_data)
        layout.addWidget(self.get_config_btn)

        # Output area
        self.output_text = QTextEdit()
        self.output_text.setMaximumHeight(300)
        self.output_text.setPlaceholderText("Test results will appear here...")
        layout.addWidget(self.output_text)

        panel.setLayout(layout)
        return panel

    def load_salvo_data(self):
        """Load realistic Salvo Metal Works data"""
        data = {
            "business_name": "Salvo Metal Works",
            "domain": "https://www.salvometalworks.com",
            "industry": "Manufacturing",
            "description": "Professional metal fabrication and welding services. Specializing in custom metalwork, structural steel, and precision machining for industrial and commercial clients.",
        }

        self.business_tab.set_config_data(data)
        self.log("✅ Loaded Salvo Metal Works data")

    def load_minimal_data(self):
        """Load minimal valid data"""
        data = {
            "business_name": "ABC Co",
            "domain": "https://www.abc.com",
            "industry": "Technology",
            "description": "",
        }

        self.business_tab.set_config_data(data)
        self.log("✅ Loaded minimal valid data")

    def load_invalid_data(self):
        """Load data that should trigger validation errors"""
        data = {
            "business_name": "A",  # Too short
            "domain": "not-a-url",  # Invalid URL
            "industry": "IT",  # Too short
            "description": "x" * 600,  # Too long
        }

        self.business_tab.set_config_data(data)
        self.log("⚠️ Loaded invalid data (should show validation errors)")

    def validate_data(self):
        """Validate current data and show results"""
        result = self.business_tab.validate_data()

        if result.is_valid:
            self.log("✅ Validation PASSED: All data is valid")
        else:
            self.log(f"❌ Validation FAILED: {len(result.errors)} error(s)")
            for error in result.errors:
                self.log(f"   • {error}")

        if result.warnings:
            self.log(f"⚠️ Warnings: {len(result.warnings)}")
            for warning in result.warnings:
                self.log(f"   • {warning}")

    def get_config_data(self):
        """Get and display current configuration data"""
        config = self.business_tab.get_config_data()

        self.log("📋 Current Configuration Data:")
        for key, value in config.items():
            display_value = value if len(str(value)) <= 50 else str(value)[:50] + "..."
            self.log(f"   {key}: {repr(display_value)}")

    def on_config_changed(self):
        """Handle config changed signal"""
        self.log("🔄 Configuration changed")

        # Show unsaved changes indicator
        if self.business_tab.has_unsaved_changes():
            self.setWindowTitle("BusinessTab Manual Test *")
        else:
            self.setWindowTitle("BusinessTab Manual Test")

    def on_validation_requested(self):
        """Handle validation requested signal"""
        self.log("🔍 Validation requested")

    def log(self, message: str):
        """Add message to output log"""
        self.output_text.append(message)
        # Scroll to bottom
        cursor = self.output_text.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.output_text.setTextCursor(cursor)


def run_manual_test():
    """Run the manual test application"""
    print("Starting BusinessTab Manual Test...")
    print("=" * 50)
    print("MANUAL TEST INSTRUCTIONS:")
    print("1. Try entering data in different fields")
    print("2. Test URL auto-formatting by entering 'example.com'")
    print("3. Use the test buttons to load different data sets")
    print("4. Watch for validation errors and warnings")
    print("5. Check the character counter for descriptions")
    print("6. Try the industry dropdown and custom entries")
    print("=" * 50)

    app = QApplication(sys.argv)
    window = BusinessTabTestWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(run_manual_test())
