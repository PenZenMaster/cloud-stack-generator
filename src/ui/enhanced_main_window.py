# src/ui/enhanced_main_window.py
"""
Enhanced main window with integrated modular tab system
Sprint 2 Week 2 - Day 6 Implementation
"""

from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QPushButton,
    QMenuBar,
    QMenu,
    QFileDialog,
    QMessageBox,
    QLabel,
    QStatusBar,
    QProgressBar,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QIcon, QAction
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

# Import all modular components
from .components.business_tab import BusinessTab
from .components.contact_tab import ContactTab
from .components.branding_tab import BrandingTab
from .content_tabs.products_tab import ProductsTab
from .content_tabs.services_tab import ServicesTab

# Import core functionality
from ..core.config.models import ClientConfig
from ..core.config.parser import ConfigParser

# Import error logging
from ..utils import log_error_dialog, log_file_operation_error, log_validation_error


class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with full modular tab integration"""

    # Signals for application-wide communication
    config_loaded = pyqtSignal(dict)
    config_saved = pyqtSignal(str)
    website_generation_requested = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        # Initialize components
        self.config_parser = ConfigParser()
        self.current_config_file = None
        self.unsaved_changes = False

        # Initialize UI
        self.setup_window()
        self.setup_menu_bar()
        self.setup_main_ui()
        self.setup_status_bar()

        # Connect all signals
        self.connect_all_signals()

        # Set initial state
        self.update_window_title()

    def setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("SEO Authority Website Generator v2.0")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # Center window on screen
        self.move_to_center()

    def move_to_center(self):
        """Center the window on the screen"""
        screen = self.screen()
        if screen:
            geometry = screen.availableGeometry()
            size = self.geometry()
            self.move(
                (geometry.width() - size.width()) // 2,
                (geometry.height() - size.height()) // 2,
            )

    def setup_menu_bar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()
        if menubar is None:
            menubar = QMenuBar(self)
            self.setMenuBar(menubar)

        # File Menu
        file_menu = menubar.addMenu("&File")
        if file_menu is None:
            file_menu = QMenu("&File", self)
            menubar.addMenu(file_menu)

        # New Config
        new_action = QAction("&New Configuration", self)
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self.new_configuration)
        file_menu.addAction(new_action)

        # Open Config
        open_action = QAction("&Open Configuration...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_configuration)
        file_menu.addAction(open_action)

        # Save Config
        save_action = QAction("&Save Configuration", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_configuration)
        file_menu.addAction(save_action)

        # Save As Config
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_configuration_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Tools Menu
        tools_menu = menubar.addMenu("&Tools")
        if tools_menu is None:
            tools_menu = QMenu("&Tools", self)
            menubar.addMenu(tools_menu)

        # Validate All
        validate_action = QAction("&Validate All Tabs", self)
        validate_action.setShortcut("F5")
        validate_action.triggered.connect(self.validate_all_tabs)
        tools_menu.addAction(validate_action)

        # Generate Website
        generate_action = QAction("&Generate Website", self)
        generate_action.setShortcut("F6")
        generate_action.triggered.connect(self.generate_website)
        tools_menu.addAction(generate_action)

        # View Menu (NEW)
        view_menu = menubar.addMenu("&View")
        if view_menu is None:
            view_menu = QMenu("&View", self)
            menubar.addMenu(view_menu)

        # Font Size submenu
        font_menu = QMenu("Font Size", self)
        view_menu.addMenu(font_menu)

        font_sizes = [
            ("Small (10pt)", 10),
            ("Normal (12pt)", 12),
            ("Large (14pt)", 14),
            ("Extra Large (16pt)", 16),
            ("Huge (18pt)", 18),
        ]

        for name, size in font_sizes:
            action = QAction(name, self)
            action.triggered.connect(lambda checked, s=size: self.change_font_size(s))
            font_menu.addAction(action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")
        if help_menu is None:
            help_menu = QMenu("&Help", self)
            menubar.addMenu(help_menu)

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_main_ui(self):
        """Setup main user interface with tabs"""
        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        # Create main tab widget
        self.main_tabs = QTabWidget()
        self.main_tabs.setFont(QFont("Arial", 10))

        # Initialize all tabs
        self.business_tab = BusinessTab()
        self.contact_tab = ContactTab()
        self.branding_tab = BrandingTab()
        self.products_tab = ProductsTab()
        self.services_tab = ServicesTab()

        # Add tabs to main widget
        self.main_tabs.addTab(self.business_tab, "📊 Business Info")
        self.main_tabs.addTab(self.contact_tab, "📞 Contact Details")
        self.main_tabs.addTab(self.branding_tab, "🎨 Branding & Style")
        self.main_tabs.addTab(self.products_tab, "📦 Products")
        self.main_tabs.addTab(self.services_tab, "⚙️ Services & FAQ")

        layout.addWidget(self.main_tabs)

        # Action buttons
        button_layout = QHBoxLayout()

        self.validate_btn = QPushButton("🔍 Validate All")
        self.validate_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.validate_btn.clicked.connect(self.validate_all_tabs)

        self.save_btn = QPushButton("💾 Save Configuration")
        self.save_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.save_btn.clicked.connect(self.save_configuration)

        self.generate_btn = QPushButton("🚀 Generate Website")
        self.generate_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.generate_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #28a745;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """
        )
        self.generate_btn.clicked.connect(self.generate_website)

        button_layout.addStretch()
        button_layout.addWidget(self.validate_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.generate_btn)

        layout.addLayout(button_layout)

        self.setCentralWidget(central_widget)

    def setup_status_bar(self):
        """Setup status bar with progress indication"""
        self.status_bar = QStatusBar()

        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Progress bar (hidden by default)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Config file indicator
        self.config_indicator = QLabel("No configuration loaded")
        self.config_indicator.setStyleSheet("color: #666;")
        self.status_bar.addPermanentWidget(self.config_indicator)

        self.setStatusBar(self.status_bar)

    def connect_all_signals(self):
        """Connect signals from all tabs"""
        # Connect config_changed signals
        self.business_tab.config_changed.connect(self.on_config_changed)
        self.contact_tab.config_changed.connect(self.on_config_changed)
        self.branding_tab.config_changed.connect(self.on_config_changed)
        self.products_tab.config_changed.connect(self.on_config_changed)
        self.services_tab.config_changed.connect(self.on_config_changed)

        # Connect validation signals
        self.business_tab.validation_requested.connect(self.validate_all_tabs)
        self.contact_tab.validation_requested.connect(self.validate_all_tabs)
        self.branding_tab.validation_requested.connect(self.validate_all_tabs)

        # Tab change signal
        self.main_tabs.currentChanged.connect(self.on_tab_changed)

    def on_config_changed(self):
        """Handle configuration changes"""
        self.unsaved_changes = True
        self.update_window_title()
        self.status_label.setText("Configuration modified")

    def on_tab_changed(self, index):
        """Handle tab change events"""
        tab_names = [
            "Business Info",
            "Contact Details",
            "Branding & Style",
            "Products",
            "Services & FAQ",
        ]
        if 0 <= index < len(tab_names):
            self.status_label.setText(f"Editing: {tab_names[index]}")

    def update_window_title(self):
        """Update window title with current state"""
        title = "SEO Authority Website Generator v2.0"

        if self.current_config_file:
            filename = Path(self.current_config_file).name
            title += f" - {filename}"

        if self.unsaved_changes:
            title += " *"

        self.setWindowTitle(title)

        # Update config indicator
        if self.current_config_file:
            self.config_indicator.setText(
                f"Config: {Path(self.current_config_file).name}"
            )
        else:
            self.config_indicator.setText("No configuration loaded")

    def new_configuration(self):
        """Create new configuration"""
        if self.unsaved_changes:
            reply = self.ask_save_changes()
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Save:
                if not self.save_configuration():
                    return

        # Clear all tabs
        self.business_tab.clear_data()
        self.contact_tab.clear_data()
        self.branding_tab.clear_data()
        self.products_tab.clear_data()
        self.services_tab.clear_data()

        self.current_config_file = None
        self.unsaved_changes = False
        self.update_window_title()
        self.status_label.setText("New configuration created")

    def open_configuration(self):
        """Open existing configuration file"""
        if self.unsaved_changes:
            reply = self.ask_save_changes()
            if reply == QMessageBox.StandardButton.Cancel:
                return
            elif reply == QMessageBox.StandardButton.Save:
                if not self.save_configuration():
                    return

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration", "", "YAML Files (*.yaml *.yml);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Add your logic here
            config = self.config_parser.parse_yaml_file(file_path)
        except Exception as e:
            error_msg = f"Failed to load configuration:\n{str(e)}"
            log_file_operation_error(
                operation="load",
                file_path=file_path,
                error_message=error_msg,
                exception=e
            )
            QMessageBox.critical(
                self,
                "Error Loading Configuration",
                error_msg,
            )
            return

        # Load data into tabs
        self.load_config_into_tabs(config)

        self.current_config_file = file_path
        self.unsaved_changes = False
        self.update_window_title()
        self.status_label.setText(f"Configuration loaded: {Path(file_path).name}")

        # Emit signal for other components
        self.config_loaded.emit(self.get_all_config_data())

    def save_configuration(self) -> bool:
        """Save current configuration"""
        if not self.current_config_file:
            return self.save_configuration_as()

        return self.save_to_file(self.current_config_file)

    def save_configuration_as(self) -> bool:
        """Save configuration with new filename"""
        # Create default filename with business name if available
        default_filename = "website_config.yaml"
        try:
            business_data = self.business_tab.get_config_data()
            business_name = business_data.get("business_name", "").strip()
            if business_name:
                # Create safe filename from business name
                import re
                safe_name = re.sub(r'[^\w\s-]', '', business_name.lower())
                safe_name = re.sub(r'[-\s]+', '_', safe_name)
                default_filename = f"{safe_name}_config.yaml"
        except:
            pass  # Use default if there's any error
            
        # Use current working directory as default location
        default_path = str(Path.cwd() / default_filename)
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", default_path, "YAML Files (*.yaml);;All Files (*)"
        )

        if not file_path:
            # User cancelled the dialog - provide feedback
            self.status_label.setText("Save cancelled by user")
            return False

        if not file_path.endswith((".yaml", ".yml")):
            file_path += ".yaml"

        return self.save_to_file(file_path)

    def save_to_file(self, file_path: str) -> bool:
        """Save configuration to specific file"""
        try:
            # Get configuration from all tabs
            config_data = self.get_all_config_data()

            # Create ClientConfig object
            config = self.create_client_config(config_data)

            # Save to file
            success = self.config_parser.save_yaml_file(config, file_path)

            if success:
                self.current_config_file = file_path
                self.unsaved_changes = False
                self.update_window_title()
                self.status_label.setText(
                    f"Configuration saved: {Path(file_path).name}"
                )
                
                # Show success notification dialog with full path for clarity
                QMessageBox.information(
                    self,
                    "Configuration Saved",
                    f"✅ Configuration successfully saved!\n\n"
                    f"File: {Path(file_path).name}\n"
                    f"Full path: {Path(file_path).absolute()}\n\n"
                    f"You can find your configuration file at the above location."
                )
                
                self.config_saved.emit(file_path)
                return True
            else:
                error_msg = "Failed to save configuration file"
                log_file_operation_error(
                    operation="save",
                    file_path=file_path,
                    error_message=error_msg
                )
                QMessageBox.critical(
                    self, "Save Error", error_msg
                )
                return False

        except Exception as e:
            error_msg = f"Failed to save configuration:\n{str(e)}"
            log_file_operation_error(
                operation="save",
                file_path=file_path,
                error_message=error_msg,
                exception=e
            )
            QMessageBox.critical(
                self, "Save Error", error_msg
            )
            return False

    def get_all_config_data(self) -> Dict[str, Any]:
        """Get configuration data from all tabs"""
        return {
            "business": self.business_tab.get_config_data(),
            "contact": self.contact_tab.get_config_data(),
            "branding": self.branding_tab.get_config_data(),
            "products": self.products_tab.get_config_data(),
            "services": self.services_tab.get_config_data(),
        }

    def create_client_config(self, config_data: Dict[str, Any]) -> ClientConfig:
        """Create ClientConfig object from tab data"""
        from ..core.config.models import (
            BusinessConfig,
            ContactConfig,
            BrandingConfig,
            ProductConfig,
            ServiceConfig,
        )

        # Create business config
        business_data = config_data.get("business", {})
        business = BusinessConfig(
            business_name=business_data.get("business_name", ""),
            domain=business_data.get("domain", ""),
            industry=business_data.get("industry", ""),
        )

        # Create contact config
        contact_data = config_data.get("contact", {})
        contact = ContactConfig(
            name=contact_data.get("name", ""),
            phone=contact_data.get("phone", ""),
            address=contact_data.get("address", ""),
            email=contact_data.get("email", ""),
        )

        # Create branding config
        branding_data = config_data.get("branding", {})
        branding = BrandingConfig(
            primary_color=branding_data.get("primary_color", "#007bff"),
            secondary_color=branding_data.get("secondary_color", "#6c757d"),
            font_family=branding_data.get("font_family", "Arial, sans-serif"),
            logo_url=branding_data.get("logo_url", ""),
        )

        # Create products list
        products = []
        products_data = config_data.get("products", {}).get("products", [])
        for p_data in products_data:
            products.append(
                ProductConfig(
                    sku=p_data.get("sku", ""),
                    name=p_data.get("name", ""),
                    description=p_data.get("description", ""),
                    category=p_data.get("category", ""),
                    image_url=p_data.get("image_url", ""),
                )
            )

        # Create services list
        services = []
        services_data = config_data.get("services", {}).get("services", [])
        for s_data in services_data:
            services.append(
                ServiceConfig(
                    name=s_data.get("name", ""),
                    description=s_data.get("description", ""),
                    category=s_data.get("category", ""),
                )
            )

        # Create complete config
        return ClientConfig(
            business=business,
            contact=contact,
            branding=branding,
            products=products,
            services=services,
        )

    def load_config_into_tabs(self, config: ClientConfig):
        """Load ClientConfig data into tabs"""
        # Load business data
        business_data = {
            "business_name": config.business.business_name,
            "domain": config.business.domain,
            "industry": config.business.industry,
        }
        self.business_tab.set_config_data(business_data)

        # Load contact data
        contact_data = {
            "name": config.contact.name,
            "phone": config.contact.phone,
            "address": config.contact.address,
            "email": config.contact.email,
        }
        self.contact_tab.set_config_data(contact_data)

        # Load branding data
        branding_data = {
            "primary_color": config.branding.primary_color,
            "secondary_color": config.branding.secondary_color,
            "font_family": config.branding.font_family,
            "logo_url": config.branding.logo_url,
        }
        self.branding_tab.set_config_data(branding_data)

        # Load products data
        products_data = {
            "products": [
                {
                    "sku": p.sku,
                    "name": p.name,
                    "description": p.description,
                    "category": p.category,
                    "image_url": p.image_url,
                }
                for p in config.products
            ]
        }
        self.products_tab.set_config_data(products_data)

        # Load services data
        services_data = {
            "services": [
                {"name": s.name, "description": s.description, "category": s.category}
                for s in config.services
            ]
        }
        self.services_tab.set_config_data(services_data)

    def validate_all_tabs_simple(self):
        """Validate all tabs and show results with proper ValidationResult handling"""
        self.status_label.setText("Validating configuration...")

        validation_results = {}
        all_valid = True

        # Validate each tab
        tabs = {
            "Business Info": self.business_tab,
            "Contact Details": self.contact_tab,
            "Branding & Style": self.branding_tab,
            "Products": self.products_tab,
            "Services & FAQ": self.services_tab,
        }

        for tab_name, tab in tabs.items():
            if hasattr(tab, "validate_data"):
                try:
                    validation_result = tab.validate_data()
                except Exception as e:
                    print(f"DEBUG: Exception during validation of {tab_name}: {e}")
                    validation_results[tab_name] = {
                        "valid": False,
                        "errors": [f"Validation error: {str(e)}"],
                    }
                    all_valid = False

        self.show_validation_results(validation_results, all_valid)
        self.status_label.setText("Validating configuration...")

    def validate_all_tabs(self):
        """Validate all tabs and show results with proper ValidationResult handling"""
        self.status_label.setText("Validating configuration...")

        validation_results = {}
        all_valid = True

        # Validate each tab
        tabs = {
            "Business Info": self.business_tab,
            "Contact Details": self.contact_tab,
            "Branding & Style": self.branding_tab,
            "Products": self.products_tab,
            "Services & FAQ": self.services_tab,
        }

        for tab_name, tab in tabs.items():
            if hasattr(tab, "validate_data"):
                try:
                    # Handle different return types from validate_data()
                    validation_result = tab.validate_data()
                    if (
                        isinstance(validation_result, tuple)
                        and len(validation_result) == 2
                    ):
                        is_valid, errors = validation_result
                    elif isinstance(validation_result, bool):
                        is_valid = validation_result
                        errors = [] if validation_result else ["Validation failed"]
                    else:
                        # Handle ValidationResult objects with attributes
                        is_valid = getattr(validation_result, "is_valid", False)
                        errors = getattr(
                            validation_result,
                            "errors",
                            ["Unable to determine validation result"],
                        )
                        print(
                            f"DEBUG {tab_name}: ValidationResult object - is_valid: {is_valid}, errors: {errors}"
                        )

                    validation_results[tab_name] = {"valid": is_valid, "errors": errors}
                    if not is_valid:
                        all_valid = False

                except Exception as e:
                    print(f"DEBUG: Exception during validation of {tab_name}: {e}")
                    validation_results[tab_name] = {
                        "valid": False,
                        "errors": [f"Validation error: {str(e)}"],
                    }
                    all_valid = False

        # Show validation results
        self.show_validation_results(validation_results, all_valid)

    def show_validation_results(self, results: Dict[str, Dict], all_valid: bool):
        """Show validation results in a dialog"""
        if all_valid:
            QMessageBox.information(
                self,
                "Validation Results",
                "✅ All tabs passed validation!\n\nYour configuration is ready for website generation.",
            )
            self.status_label.setText("Validation passed - Ready to generate")
        else:
            error_text = "❌ Validation found the following issues:\n\n"
            for tab_name, result in results.items():
                if not result["valid"]:
                    error_text += f"**{tab_name}:**\n"
                    for error in result["errors"]:
                        error_text += f"  • {error}\n"
                    error_text += "\n"

            error_text += "Please fix these issues before generating your website."

            # Log validation errors
            log_error_dialog(
                title="Validation Errors",
                message=error_text,
                context="User attempted to validate all tabs",
                component="EnhancedMainWindow.show_validation_results",
                user_action="Validating configuration before website generation"
            )

            QMessageBox.warning(self, "Validation Errors", error_text)
            self.status_label.setText("Validation failed - Please fix errors")

    def generate_website(self):
        """Generate website from current configuration"""
        # First validate
        self.validate_all_tabs()

        # Get all configuration data
        config_data = self.get_all_config_data()

        # Emit signal for website generation
        self.website_generation_requested.emit(config_data)

        # Show progress (for now, just a message)
        QMessageBox.information(
            self,
            "Website Generation",
            "Website generation requested!\n\n"
            "This will be connected to the website generator in the next phase.",
        )

        self.status_label.setText("Website generation requested")

    def ask_save_changes(self) -> QMessageBox.StandardButton:
        """Ask user if they want to save unsaved changes"""
        return QMessageBox.question(
            self,
            "Unsaved Changes",
            "You have unsaved changes. Do you want to save them?",
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel,
        )

    def change_font_size(self, size: int):
        """Change application font size"""
        font = QFont("Arial", size)
        self.setFont(font)

        # Apply to all child widgets recursively
        self._apply_font_to_children(self, font)

        self.status_label.setText(f"Font size changed to {size}pt")

    def _apply_font_to_children(self, widget, font):
        """Recursively apply font to all child widgets"""
        for child in widget.findChildren(QWidget):
            if not child.font().bold():  # Preserve bold fonts
                child.setFont(font)
            else:
                bold_font = QFont("Arial", font.pointSize(), QFont.Weight.Bold)
                child.setFont(bold_font)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About SEO Authority Website Generator",
            "<h3>SEO Authority Website Generator v2.0</h3>"
            "<p>Sprint 2 Week 2 - Enhanced Modular Architecture</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>✅ Business Information Management</li>"
            "<li>✅ Contact Details with Validation</li>"
            "<li>✅ Branding & Color Management</li>"
            "<li>✅ Product Catalog with CSV Import</li>"
            "<li>✅ Services & FAQ Management</li>"
            "</ul>"
            "<p><b>Status:</b> Ready for Website Generation Integration</p>",
        )

    def closeEvent(self, event):
        """Handle application close event"""
        if self.unsaved_changes:
            reply = self.ask_save_changes()
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            elif reply == QMessageBox.StandardButton.Save:
                if not self.save_configuration():
                    event.ignore()
                    return

        event.accept()


# Integration test function
def create_enhanced_main_window():
    """Factory function to create enhanced main window"""
    return EnhancedMainWindow()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = create_enhanced_main_window()
    window.show()
    sys.exit(app.exec())
