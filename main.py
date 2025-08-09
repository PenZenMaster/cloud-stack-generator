"""
Filename: main.py
Path: E:\\projects\\cloud-stack-generator\\main.py
Description: Main entry point for SEO Authority Website Generator
Proper Python module imports and application launcher

Version: 1.0.1
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

import sys
from pathlib import Path

# Add src to Python path for proper module resolution
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

# Now we can import from src
from ui.main_window import SEOGeneratorMainWindow
from PyQt6.QtWidgets import QApplication


def main():
    """Main application entry point with proper imports"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("SEO Authority Website Generator")
    app.setApplicationVersion("1.0.1-sprint1")
    app.setOrganizationName("Cloud Stack Generator")

    # Create and show main window
    window = SEOGeneratorMainWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
