# main.py
"""
SEO Authority Website Generator v3.12.0
Enhanced Main Application Entry Point

Updated: January 19, 2026
Version: 3.12.0 - Fix relative path resolution for city page pool images
Working Directory: E:\\projects\\cloud-stack-generator\
"""

import sys
import traceback
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtGui import QFont

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def trim_error_log(max_lines=50):
    """Trim error log to keep only the last N lines on startup"""
    try:
        error_log_path = Path(__file__).parent / "logs" / "error_log.txt"

        # Skip if log file doesn't exist
        if not error_log_path.exists():
            return

        # Read all lines from the log file
        with open(error_log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # If file has more than max_lines, keep only the last max_lines
        if len(lines) > max_lines:
            with open(error_log_path, "w", encoding="utf-8") as f:
                f.writelines(lines[-max_lines:])
            print(f"Error log trimmed: kept last {max_lines} lines (removed {len(lines) - max_lines} lines)")
        else:
            print(f"Error log size: {len(lines)} lines (no trim needed)")

    except Exception as e:
        print(f"Failed to trim error log: {e}")

def log_error_to_file(error_type, error_msg, stack_trace=""):
    """Log errors to error_log.txt for better debugging"""
    try:
        error_log_path = Path(__file__).parent / "logs" / "error_log.txt"
        error_log_path.parent.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(error_log_path, "a", encoding="utf-8") as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"ERROR LOG ENTRY - {timestamp}\n")
            f.write(f"{'='*60}\n")
            f.write(f"Error Type: {error_type}\n")
            f.write(f"Error Message: {error_msg}\n")
            if stack_trace:
                f.write(f"\nStack Trace:\n{stack_trace}\n")
            f.write(f"Working Directory: {Path.cwd()}\n")
            f.write(f"Python Path: {sys.path[:3]}...\n")  # First 3 entries
            f.write(f"{'='*60}\n\n")

        print(f"Error logged to: {error_log_path}")
        return str(error_log_path)
    except Exception as log_error:
        print(f"Failed to log error to file: {log_error}")
        return None

try:
    # Import the enhanced main window
    from src.ui.enhanced_main_window import EnhancedMainWindow

    def qt_exception_hook(exc_type, exc_value, exc_traceback):
        """Global Qt exception handler to catch and log Unicode errors"""
        error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # Log to file
        log_error_to_file(exc_type.__name__, str(exc_value), error_msg)
        
        # Special handling for Unicode errors
        if "UnicodeEncodeError" in str(exc_type) or "charmap" in str(exc_value):
            print(f"[ERROR] Unicode encoding error caught and logged: {exc_value}")
        else:
            print(f"[ERROR] Exception caught and logged: {exc_value}")
        
        # Continue with default behavior
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    def setup_application():
        """Setup QApplication with proper configuration"""
        # Install global exception handler
        sys.excepthook = qt_exception_hook
        
        app = QApplication(sys.argv)

        # Set application properties with dynamic version
        app.setApplicationName("SEO Authority Website Generator")
        try:
            from src.version import get_version
            app.setApplicationVersion(get_version())
        except ImportError:
            app.setApplicationVersion("3.2.0")  # Fallback version
        app.setOrganizationName("Cloud Stack Solutions")

        # Set default font
        font = QFont("Arial", 9)
        app.setFont(font)

        return app

    def main():
        """Main application entry point"""
        try:
            # Trim error log to prevent excessive growth
            trim_error_log(max_lines=50)

            # Create application
            app = setup_application()

            # Create and show main window
            main_window = EnhancedMainWindow()
            main_window.show()

            # Start event loop
            return app.exec()

        except ImportError as e:
            stack_trace = traceback.format_exc()
            error_msg = f"Import Error: {str(e)}"
            
            log_error_to_file("ImportError", error_msg, stack_trace)
            
            full_error_msg = f"""
Import Error: {str(e)}

This usually means one of the following:
1. You're not in the correct directory (should be E:\\projects\\cloud-stack-generator\\)
2. Some component files are missing
3. Python path is not set correctly

Please run this from the project root directory and ensure all component files exist.
Error logged to logs/error_log.txt for detailed analysis.
            """

            if "app" in locals():
                QMessageBox.critical(None, "Import Error", full_error_msg)
            else:
                print(full_error_msg)
            return 1

        except Exception as e:
            stack_trace = traceback.format_exc()
            error_msg = f"Unexpected Error: {str(e)}"
            
            log_error_to_file("Exception", error_msg, stack_trace)
            
            full_error_msg = f"""
Unexpected Error: {str(e)}

Stack trace:
{stack_trace}

Please check that all dependencies are installed:
pip install PyQt6 PyYAML pandas chardet

Error logged to logs/error_log.txt for detailed analysis.
            """

            if "app" in locals():
                QMessageBox.critical(None, "Application Error", full_error_msg)
            else:
                print(full_error_msg)
            return 1

    if __name__ == "__main__":
        print("Starting SEO Authority Website Generator v2.0...")
        print("Working Directory:", Path.cwd())
        print("Enhanced Modular Architecture")
        print("=" * 50)

        exit_code = main()

        if exit_code == 0:
            print("Application closed successfully")
        else:
            print("Application closed with errors")

        sys.exit(exit_code)

except ImportError as import_error:
    stack_trace = traceback.format_exc()
    error_msg = f"CRITICAL IMPORT ERROR: {str(import_error)}"
    
    log_error_to_file("CRITICAL_ImportError", error_msg, stack_trace)
    
    print(
        f"""
CRITICAL IMPORT ERROR

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

Error logged to logs/error_log.txt for detailed analysis.

Component Status Check:
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
            print(f"   OK {component}")
        else:
            print(f"   MISSING {component}")

    print("\nIf components are missing, you may need to create them first.")
    print("Try running your working tests to verify component status:")
    print("   python tests/simple_business_test.py")

    sys.exit(1)

except Exception as critical_error:
    stack_trace = traceback.format_exc()
    error_msg = f"CRITICAL APPLICATION ERROR: {str(critical_error)}"
    
    log_error_to_file("CRITICAL_Exception", error_msg, stack_trace)
    
    print(
        f"""
CRITICAL APPLICATION ERROR

Error: {str(critical_error)}
Stack Trace:
{stack_trace}

This is an unexpected error. Please check:
1. All dependencies are installed
2. File permissions are correct  
3. No syntax errors in component files

Error logged to logs/error_log.txt for detailed analysis.

If the problem persists, please run individual component tests:
- python tests/simple_business_test.py
- python tests/simple_contact_test.py  
- python tests/simple_branding_test.py
"""
    )
    sys.exit(1)
