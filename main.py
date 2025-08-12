# main.py
"""
SEO Authority Website Generator v2.0
Sprint 2 Week 2 - Enhanced Main Application Entry Point

Updated: August 12, 2025
Version: 2.0.0 - Enhanced Modular Architecture
Working Directory: E:\projects\cloud-stack-generator\
"""

import sys
import traceback
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    # Import the enhanced main window
    from src.ui.enhanced_main_window import EnhancedMainWindow

    def setup_application():
        """Setup QApplication with proper configuration"""
        app = QApplication(sys.argv)

        # Set application properties
        app.setApplicationName("SEO Authority Website Generator")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("Cloud Stack Solutions")

        # Set default font
        font = QFont("Arial", 9)
        app.setFont(font)

        # Enable high DPI support
        app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

        return app

    def main():
        """Main application entry point"""
        try:
            # Create application
            app = setup_application()

            # Create and show main window
            main_window = EnhancedMainWindow()
            main_window.show()

            # Start event loop
            return app.exec()

        except ImportError as e:
            error_msg = f"""
Import Error: {str(e)}

This usually means one of the following:
1. You're not in the correct directory (should be E:\\projects\\cloud-stack-generator\\)
2. Some component files are missing
3. Python path is not set correctly

Please run this from the project root directory and ensure all component files exist.
            """

            if "app" in locals():
                QMessageBox.critical(None, "Import Error", error_msg)
            else:
                print(error_msg)
            return 1

        except Exception as e:
            error_msg = f"""
Unexpected Error: {str(e)}

Stack trace:
{traceback.format_exc()}

Please check that all dependencies are installed:
pip install PyQt6 PyYAML pandas chardet
            """

            if "app" in locals():
                QMessageBox.critical(None, "Application Error", error_msg)
            else:
                print(error_msg)
            return 1

    if __name__ == "__main__":
        print("🚀 Starting SEO Authority Website Generator v2.0...")
        print("📂 Working Directory:", Path.cwd())
        print("🔧 Enhanced Modular Architecture")
        print("=" * 50)

        exit_code = main()

        if exit_code == 0:
            print("✅ Application closed successfully")
        else:
            print("❌ Application closed with errors")

        sys.exit(exit_code)

except ImportError as import_error:
    print(
        f"""
🚨 CRITICAL IMPORT ERROR 🚨

Error: {str(import_error)}

This appears to be a module import issue. Here are the most likely solutions:

1. **Check Current Directory**: 
   Current: {Path.cwd()}
   Expected: E:\\projects\\cloud-stack-generator\\
   
2. **Verify Component Files Exist**:
   Run this command to check:
   python tests/verify_files.py

3. **Check Python Dependencies**:
   pip install PyQt6 PyYAML pandas chardet

4. **Fallback to Legacy Mode**:
   If the enhanced main window isn't ready, you can temporarily use:
   python -c "from src.ui.main_window import MainWindow; import sys; from PyQt6.QtWidgets import QApplication; app=QApplication(sys.argv); w=MainWindow(); w.show(); sys.exit(app.exec())"

📋 Component Status Check:
"""
    )

    # Check which components exist
    components_to_check = [
        "src/ui/enhanced_main_window.py",
        "src/ui/components/business_tab.py",
        "src/ui/components/contact_tab.py",
        "src/ui/components/branding_tab.py",
        "src/ui/content_tabs/products_tab.py",
        "src/ui/content_tabs/services_tab.py",
    ]

    for component in components_to_check:
        if Path(component).exists():
            print(f"   ✅ {component}")
        else:
            print(f"   ❌ {component} (MISSING)")

    print(f"\n💡 If components are missing, you may need to create them first.")
    print(f"💡 Try running your working tests to verify component status:")
    print(f"   python tests/simple_business_test.py")

    sys.exit(1)

except Exception as critical_error:
    print(
        f"""
🚨 CRITICAL APPLICATION ERROR 🚨

Error: {str(critical_error)}
Stack Trace:
{traceback.format_exc()}

This is an unexpected error. Please check:
1. All dependencies are installed
2. File permissions are correct  
3. No syntax errors in component files

If the problem persists, please run individual component tests:
- python tests/simple_business_test.py
- python tests/simple_contact_test.py  
- python tests/simple_branding_test.py
"""
    )
    sys.exit(1)
