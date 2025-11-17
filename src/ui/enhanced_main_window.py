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
    QDialog,
)
from PyQt6.QtCore import pyqtSignal, QTimer, QThread, QSettings
from PyQt6.QtGui import QFont, QAction
from pathlib import Path
from typing import Dict, Any, Optional
import json

# Import all modular components
from ..utils.error_logger import ErrorLogger
from .components.business_tab import BusinessTab
from .components.contact_tab import ContactTab
from .components.branding_tab import BrandingTab
from .components.api_keys_tab import APIKeysTab
from .components.cloud_tab import CloudTab
from .components.deployment_history_tab import DeploymentHistoryTab
from .content_tabs.products_tab import ProductsTab
from .content_tabs.services_tab import ServicesTab
from .content_tabs.enhanced_cities_tab import EnhancedCitiesTab

# Import core functionality
from ..core.config.models import ClientConfig
from ..core.config.parser import ConfigParser
from ..version import get_version

# Import error logging
from ..utils import log_error_dialog, log_file_operation_error


class GenerationWorker(QThread):
    """Worker thread for website generation to keep UI responsive"""

    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str, list, str)

    def __init__(self, config, output_dir: str):
        super().__init__()
        self.config = config
        self.output_dir = output_dir

    def run(self):
        """Run website generation in background thread"""
        try:
            from ..core.generators.page_generator import PageGenerator

            self.progress.emit("Initializing website generator...")
            generator = PageGenerator(output_base_dir=self.output_dir)

            self.progress.emit("Generating HTML pages...")
            result = generator.generate_complete_website(self.config)

            if result.success:
                self.progress.emit("Website generation completed!")
                self.finished.emit(
                    True,
                    "Website generated successfully!",
                    result.generated_files,
                    self.output_dir,
                )
            else:
                self.finished.emit(
                    False, f"Generation failed: {result.errors}", [], self.output_dir
                )

        except Exception as e:
            self.finished.emit(False, f"Unexpected error: {str(e)}", [], self.output_dir)


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
        self.generation_worker: Optional[GenerationWorker] = None

        # Initialize settings for persistent preferences
        self.settings = QSettings("RankRocketCo", "SEOAuthorityWebsiteGenerator")

        # Initialize error logger
        self.error_logger = ErrorLogger()

        # Load application-wide API keys
        self.app_api_keys = self.load_app_api_keys()

        # Initialize UI
        self.setup_window()
        self.setup_menu_bar()
        self.setup_main_ui()
        self.setup_status_bar()

        # Connect all signals
        self.connect_all_signals()

        # Set initial state
        self.update_window_title()
        
        # Set API keys in the API Keys tab after UI is initialized
        QTimer.singleShot(100, self.set_api_keys_in_tab)

    def setup_window(self):
        """Configure main window properties"""
        current_version = get_version()
        self.setWindowTitle(f"SEO Authority Website Generator v{current_version}")
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
        validate_action.setShortcut("F4")
        validate_action.triggered.connect(self.validate_all_tabs)
        tools_menu.addAction(validate_action)

        # Website Preview
        preview_action = QAction("Website &Preview", self)
        preview_action.setShortcut("F5")
        preview_action.triggered.connect(self.preview_website)
        tools_menu.addAction(preview_action)

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
        self.api_keys_tab = APIKeysTab()
        self.enhanced_cities_tab = EnhancedCitiesTab()
        self.products_tab = ProductsTab()
        self.services_tab = ServicesTab()
        self.cloud_tab = CloudTab()
        self.deployment_history_tab = DeploymentHistoryTab()

        # Add tabs to main widget
        self.main_tabs.addTab(self.business_tab, "Business Info")
        self.main_tabs.addTab(self.contact_tab, "Contact Details")
        self.main_tabs.addTab(self.branding_tab, "Branding & Style")
        self.main_tabs.addTab(self.enhanced_cities_tab, "Cities")
        self.main_tabs.addTab(self.products_tab, "Products")
        self.main_tabs.addTab(self.services_tab, "Services & FAQ")
        self.main_tabs.addTab(self.api_keys_tab, "API Keys")
        self.main_tabs.addTab(self.cloud_tab, "Cloud Deploy")
        self.main_tabs.addTab(self.deployment_history_tab, "Deployment History")

        layout.addWidget(self.main_tabs)

        # Action buttons
        button_layout = QHBoxLayout()

        self.validate_btn = QPushButton("Validate All")
        self.validate_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.validate_btn.clicked.connect(self.validate_all_tabs)

        self.save_btn = QPushButton("Save Configuration")
        self.save_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.save_btn.clicked.connect(self.save_configuration)

        self.preview_btn = QPushButton("Website Preview")
        self.preview_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.preview_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #007bff;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """
        )
        self.preview_btn.clicked.connect(self.preview_website)

        self.generate_btn = QPushButton("Generate Website")
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
        button_layout.addWidget(self.preview_btn)
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
        self.enhanced_cities_tab.config_changed.connect(self.on_config_changed)
        self.products_tab.config_changed.connect(self.on_config_changed)
        self.services_tab.config_changed.connect(self.on_config_changed)
        # Note: API Keys tab handles its own persistence and should not trigger unsaved changes

        # Connect validation signals
        self.business_tab.validation_requested.connect(self.validate_all_tabs)
        self.contact_tab.validation_requested.connect(self.validate_all_tabs)
        self.branding_tab.validation_requested.connect(self.validate_all_tabs)
        self.enhanced_cities_tab.validation_requested.connect(self.validate_all_tabs)
        self.api_keys_tab.validation_requested.connect(self.validate_all_tabs)

        # Cloud deployment signal (v3.2.0 - Phase 5: Per-deployment meta tags)
        self.cloud_tab.deployment_created.connect(self.on_deployment_created)

        # Tab change signal
        self.main_tabs.currentChanged.connect(self.on_tab_changed)

    def on_config_changed(self):
        """Handle configuration changes (manual save only)"""
        self.unsaved_changes = True
        self.update_window_title()
        self.status_label.setText("Configuration modified - use Save Configuration to save changes")
        
        # Update cloud tab client context when business info changes
        try:
            business_data = self.business_tab.get_config_data()
            if business_data.get('business_name') and business_data.get('domain'):
                self.cloud_tab.set_client_context(
                    business_data['business_name'], 
                    business_data['domain']
                )
        except Exception as e:
            # Don't fail the config change event if cloud tab update fails
            print(f"Warning: Failed to update cloud tab client context: {e}")

    def on_deployment_created(self, deployment: "DeploymentConfig"):
        """Handle deployment creation/update (v3.2.0 - Phase 5)"""
        from src.core.config.models import DeploymentConfig

        if not hasattr(self, 'current_config') or not self.current_config:
            print("Warning: No config loaded, cannot save deployment")
            return

        # Find existing deployment with same ID
        existing_index = -1
        for i, dep in enumerate(self.current_config.deployments):
            if dep.deployment_id == deployment.deployment_id:
                existing_index = i
                break

        # Update or append deployment
        if existing_index >= 0:
            self.current_config.deployments[existing_index] = deployment
            print(f"Updated existing deployment: {deployment.deployment_id}")
        else:
            self.current_config.deployments.append(deployment)
            print(f"Added new deployment: {deployment.deployment_id}")

        # Refresh deployment history tab
        self.deployment_history_tab.set_config(self.current_config)

        # Mark config as modified and trigger auto-save
        self.unsaved_changes = True
        self.update_window_title()

        # Auto-save config after deployment
        if self.config_file_path:
            try:
                self.save_configuration()
                self.status_label.setText(f"Deployment saved: {deployment.deployment_id}")
            except Exception as e:
                print(f"Warning: Failed to auto-save after deployment: {e}")
                self.status_label.setText(f"Deployment created but not saved: {deployment.deployment_id}")

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

    def load_app_api_keys(self) -> Dict[str, str]:
        """Load application-wide API keys from config/api_keys.json"""
        try:
            api_keys_file = Path("config/api_keys.json")
            if api_keys_file.exists():
                with open(api_keys_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Error loading app API keys: {e}")
            return {}
    
    def save_app_api_keys(self, api_keys: Dict[str, str]):
        """Save application-wide API keys to config/api_keys.json"""
        try:
            api_keys_file = Path("config/api_keys.json")
            api_keys_file.parent.mkdir(exist_ok=True)
            with open(api_keys_file, 'w') as f:
                json.dump(api_keys, f, indent=2)
            self.app_api_keys = api_keys
        except Exception as e:
            print(f"Error saving app API keys: {e}")
    
    def set_api_keys_in_tab(self):
        """Set the loaded API keys in the API Keys tab"""
        if hasattr(self, 'api_keys_tab') and self.app_api_keys:
            google_maps_key = self.app_api_keys.get('google_maps_api_key', '')
            if google_maps_key:
                # Set the key directly in the field
                self.api_keys_tab.maps_api_key.setText(google_maps_key)

    def update_window_title(self):
        """Update window title with current state"""
        current_version = get_version()
        title = f"SEO Authority Website Generator v{current_version}"

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

        # Use /config/clients/ as default directory for opening files
        default_dir = Path.cwd() / "config" / "clients"
        default_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration", str(default_dir), "YAML Files (*.yaml *.yml);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Parse the YAML file and store the config
            config = self.config_parser.parse_yaml_file(file_path)
            self.loaded_config = config  # Store for website generation
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
            # No current file loaded - prompt for new file location
            self.status_label.setText("No config file loaded - prompting for save location...")
            return self.save_configuration_as()

        # Save to existing file location
        filename = Path(self.current_config_file).name
        self.status_label.setText(f"Saving to existing file: {filename}")
        return self.save_to_file(self.current_config_file)

    def save_configuration_as(self) -> bool:
        """Save configuration with new filename"""
        # If we have a loaded config file, use its name as default
        if self.current_config_file:
            default_filename = Path(self.current_config_file).name
        else:
            # Create default filename based on business name (consistent with existing files)
            default_filename = "website_config.yaml"
            try:
                business_data = self.business_tab.get_config_data()
                business_name = business_data.get("business_name", "").strip()
                if business_name:
                    # Create safe filename from business name (matches existing pattern)
                    import re
                    safe_name = re.sub(r'[^\w\s-]', '', business_name.lower())
                    safe_name = re.sub(r'[-\s]+', '_', safe_name)
                    default_filename = f"{safe_name}_config.yaml"
            except Exception:
                pass  # Use default if there's any error
            
        # Use /config/clients/ as default location
        default_dir = Path.cwd() / "config" / "clients"
        default_dir.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        default_path = str(default_dir / default_filename)
        
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
                    f"Configuration successfully saved!\n\n"
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
            "cities": self.enhanced_cities_tab.get_config_data(),
            "products": self.products_tab.get_config_data(),
            "services": self.services_tab.get_config_data(),
            "cloud": self.cloud_tab.get_config_data(),
            # API keys are application-level, not saved in client configs
        }

    def create_client_config(self, config_data: Dict[str, Any]) -> ClientConfig:
        """Create ClientConfig object from tab data"""
        from ..core.config.models import (
            BusinessConfig,
            ContactConfig,
            BrandingConfig,
            ProductConfig,
            ServiceConfig,
            SocialMediaConfig,
            CloudConfig,
        )

        # Create business config with enhanced fields
        business_data = config_data.get("business", {})
        business = BusinessConfig(
            business_name=business_data.get("business_name", ""),
            domain=business_data.get("domain", ""),
            industry=business_data.get("industry", ""),
            description=business_data.get("description", ""),
            # Enhanced business fields
            tagline=business_data.get("tagline", ""),
            hero_subtitle=business_data.get("hero_subtitle", ""),
            years_in_business=business_data.get("years_in_business", ""),
            company_overview=business_data.get("company_overview", ""),
            mission_statement=business_data.get("mission_statement", ""),
            service_guarantee=business_data.get("service_guarantee", ""),
            service_area_description=business_data.get("service_area_description", ""),
            why_choose_us=business_data.get("why_choose_us", []),
            company_stats=business_data.get("company_stats", {}),
        )

        # Create contact config
        contact_data = config_data.get("contact", {})
        
        # Handle address data - create AddressConfig from separate fields
        from src.core.config.models import AddressConfig
        address_data = contact_data.get("address", {})
        if isinstance(address_data, dict):
            # Create structured address from separate fields
            address_config = AddressConfig(
                street=address_data.get("street", ""),
                city=address_data.get("city", ""),
                state=address_data.get("state", ""),
                zip_code=address_data.get("zip_code", ""),
                country=address_data.get("country", "United States")
            )
        else:
            # Handle legacy single address string
            address_config = AddressConfig.from_single_line(str(address_data) if address_data else "")
        
        # Extract contact fields - handle both nested and flat structures
        contact_fields = contact_data.get("contact", {}) if "contact" in contact_data else contact_data
        
        # Parse additional locations
        additional_locations = []
        for loc_data in contact_fields.get("additional_locations", []):
            if isinstance(loc_data, dict):
                additional_locations.append(AddressConfig(
                    street=loc_data.get("street", ""),
                    city=loc_data.get("city", ""),
                    state=loc_data.get("state", ""),
                    zip_code=loc_data.get("zip_code", ""),
                    country=loc_data.get("country", "United States")
                ))
        
        contact = ContactConfig(
            name=contact_fields.get("name", ""),
            phone=contact_fields.get("phone", ""),
            address=address_config,
            email=contact_fields.get("email", ""),
            # Enhanced contact fields
            business_hours=contact_fields.get("business_hours", {}),
            emergency_phone=contact_fields.get("emergency_phone", ""),
            office_phone=contact_fields.get("office_phone", ""),
            mobile_phone=contact_fields.get("mobile_phone", ""),
            fax_number=contact_fields.get("fax_number", ""),
            response_time_promise=contact_fields.get("response_time_promise", ""),
            contact_preference=contact_fields.get("contact_preference", ""),
            additional_locations=additional_locations,
        )
        
        # Create social media config
        social_media_data = contact_data.get("social_media", {})
        social_media = SocialMediaConfig(
            facebook=social_media_data.get("facebook", ""),
            twitter=social_media_data.get("twitter", ""),
            linkedin=social_media_data.get("linkedin", ""),
            instagram=social_media_data.get("instagram", ""),
            youtube=social_media_data.get("youtube", ""),
        )
        
        # Get Google Business Profile data
        google_business_profile = contact_data.get("google_business_profile", {})

        # Create branding config
        branding_data = config_data.get("branding", {})
        colors = branding_data.get("colors", {})
        typography = branding_data.get("typography", {})
        logo = branding_data.get("logo", {})
        branding = BrandingConfig(
            primary_color=colors.get("primary_color", "#007bff"),
            secondary_color=colors.get("secondary_color", "#6c757d"),
            font_family=typography.get("font_family", "Arial, sans-serif"),
            logo_url=logo.get("logo_url", ""),
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

        # Create FAQ list from services tab
        from ..core.config.models import FAQItem
        faqs = []
        faq_data = config_data.get("services", {}).get("faq", [])
        for f_data in faq_data:
            faqs.append(
                FAQItem(
                    question=f_data.get("question", ""),
                    answer=f_data.get("answer", ""),
                )
            )

        # Import GoogleMapsConfig for cities data
        from ..core.config.models import GoogleMapsConfig
        
        # Create Google Maps config with cities data and API key
        cities_data = config_data.get("cities", {})
        google_maps = GoogleMapsConfig()
        
        # API keys are stored separately, not in main config
        
        # Add cities from the cities tab
        google_maps_cities = cities_data.get("google_maps", {}).get("cities", {})
        google_maps.cities = google_maps_cities
        
        # Get city pages data from enhanced cities tab
        city_pages_data = cities_data.get("city_pages", [])
        
        # Convert to CityPageConfig objects
        from ..core.config.models import CityPageConfig, CityImageConfig, PlaceOfInterest, CityFAQItem
        city_pages = []
        for cp_data in city_pages_data:
            # Create CityImageConfig
            image_data = cp_data.get("city_image", {})
            city_image = CityImageConfig(
                image_url=image_data.get("image_url", ""),
                alt_text=image_data.get("alt_text", ""),
                caption=image_data.get("caption", ""),
                credit=image_data.get("credit", ""),
                source=image_data.get("source", "Wikipedia"),
                embed_code=image_data.get("embed_code", "")
            )
            
            # Create PlaceOfInterest objects
            places_data = cp_data.get("places_of_interest", [])
            places = [PlaceOfInterest(name=p.get("name", ""), embed_url=p.get("embed_url", "")) for p in places_data]
            
            # Create CityFAQItem objects
            faq_data = cp_data.get("city_faq", [])
            city_faq = [CityFAQItem(question=f.get("question", ""), answer=f.get("answer", "")) for f in faq_data]
            
            # Create CityPageConfig
            city_page = CityPageConfig(
                city_name=cp_data.get("city_name", ""),
                state=cp_data.get("state", ""),
                slug=cp_data.get("slug", ""),
                title=cp_data.get("title", ""),
                meta_description=cp_data.get("meta_description", ""),
                primary_keyword=cp_data.get("primary_keyword", ""),
                secondary_keywords=cp_data.get("secondary_keywords", []),
                hero_title=cp_data.get("hero_title", ""),
                breadcrumbs=cp_data.get("breadcrumbs", []),
                about_city=cp_data.get("about_city", ""),
                city_image=city_image,
                places_of_interest=places,
                city_faq=city_faq,
                seo_content_title=cp_data.get("seo_content_title", ""),
                seo_content_body=cp_data.get("seo_content_body", ""),
                city_map_embed=cp_data.get("city_map_embed", ""),
                service_area_note=cp_data.get("service_area_note", ""),
                featured_products=cp_data.get("featured_products", [])
            )
            city_pages.append(city_page)
        
        # Get target_cities from cities tab (includes proper format with state)
        target_cities = cities_data.get("target_cities", [])
        # Fallback: create from city_pages if not provided
        if not target_cities:
            target_cities = [cp.city_name for cp in city_pages if cp.city_name]
        seo_content = cities_data.get("seo_content", {})

        # Create cloud config
        cloud_data = config_data.get("cloud", {})
        cloud = CloudConfig(
            # AWS credentials and settings
            aws_profile=cloud_data.get("aws_profile", ""),
            aws_region=cloud_data.get("aws_region", "us-east-1"),

            # S3 and deployment settings
            bucket_name=cloud_data.get("bucket_name", ""),
            deployment_mode=cloud_data.get("deployment_mode", "s3"),
            deployment_url=cloud_data.get("deployment_url", ""),

            # CloudFront settings
            distribution_id=cloud_data.get("distribution_id", ""),
            custom_domain=cloud_data.get("custom_domain", ""),
            auto_invalidate_cache=cloud_data.get("auto_invalidate_cache", True),

            # SEO and backlink configuration
            site_type=cloud_data.get("site_type", "main_site"),
            main_site_url=cloud_data.get("main_site_url", ""),
            allow_indexing=cloud_data.get("allow_indexing", True),
            meta_tags=cloud_data.get("meta_tags", {}),

            # Caching configuration
            html_cache_control=cloud_data.get("html_cache_control", "max-age=300,public"),
            asset_cache_control=cloud_data.get("asset_cache_control", "max-age=86400,public"),

            # Website configuration
            index_document=cloud_data.get("index_document", "index.html"),
            error_document=cloud_data.get("error_document", "404.html"),

            # Deployment history
            last_deployment=cloud_data.get("last_deployment"),
        )

        # Create complete config
        return ClientConfig(
            business=business,
            contact=contact,
            branding=branding,
            cloud=cloud,
            products=products,
            services=services,
            faq=faqs,  # Add FAQs from services tab
            social_media=social_media,
            google_business_profile=google_business_profile,
            google_maps=google_maps,
            city_pages=city_pages,  # Save rich city page data
            target_cities=target_cities,  # Keep for backward compatibility
            seo_content=seo_content,
        )

    def load_config_into_tabs(self, config: ClientConfig):
        """Load ClientConfig data into tabs"""
        # Load business data including enhanced fields
        business_data = {
            "business_name": config.business.business_name,
            "domain": config.business.domain,
            "industry": config.business.industry,
            "description": config.business.description,
            # Enhanced business fields
            "tagline": config.business.tagline,
            "hero_subtitle": config.business.hero_subtitle,
            "years_in_business": config.business.years_in_business,
            "company_overview": config.business.company_overview,
            "mission_statement": config.business.mission_statement,
            "service_guarantee": config.business.service_guarantee,
            "service_area_description": config.business.service_area_description,
            "why_choose_us": config.business.why_choose_us,
            "company_stats": config.business.company_stats,
        }
        self.business_tab.set_config_data(business_data)

        # Load contact data with new structure for migrated contact tab
        # Address is now a structured AddressConfig object
        contact_data = {
            "contact": {
                "name": config.contact.name,
                "phone": config.contact.phone,
                "email": config.contact.email,
                # Enhanced contact fields
                "business_hours": config.contact.business_hours,
                "emergency_phone": config.contact.emergency_phone,
                "office_phone": config.contact.office_phone,
                "mobile_phone": config.contact.mobile_phone,
                "fax_number": config.contact.fax_number,
                "response_time_promise": config.contact.response_time_promise,
                "contact_preference": config.contact.contact_preference,
                "additional_locations": [
                    {
                        "street": loc.street,
                        "city": loc.city,
                        "state": loc.state,
                        "zip_code": loc.zip_code,
                        "country": loc.country,
                    } for loc in config.contact.additional_locations
                ],
            },
            "address": {
                "street": config.contact.address.street,
                "city": config.contact.address.city,
                "state": config.contact.address.state,
                "zip_code": config.contact.address.zip_code,
                "country": config.contact.address.country
            },
            "social_media": {
                "facebook": getattr(config.social_media, 'facebook', ''),
                "twitter": getattr(config.social_media, 'twitter', ''),
                "linkedin": getattr(config.social_media, 'linkedin', ''),
                "instagram": getattr(config.social_media, 'instagram', ''),
                "youtube": getattr(config.social_media, 'youtube', ''),
            },
            "google_business_profile": {
                "embed_code": getattr(config, 'google_business_profile', {}).get('embed_code', '') if hasattr(config, 'google_business_profile') else ''
            },
        }
        self.contact_tab.set_config_data(contact_data)

        # Load branding data with new structure for migrated branding tab
        branding_data = {
            "colors": {
                "primary_color": config.branding.primary_color,
                "secondary_color": config.branding.secondary_color,
            },
            "typography": {
                "font_family": config.branding.font_family,
            },
            "logo": {
                "logo_url": config.branding.logo_url,
            },
        }
        self.branding_tab.set_config_data(branding_data)

        # API keys are application-level, not client-specific - don't reload them

        # Load enhanced cities data from config
        enhanced_cities_data = {
            "city_pages": []
        }
        if hasattr(config, 'city_pages') and config.city_pages:
            enhanced_cities_data["city_pages"] = [
                {
                    "city_name": cp.city_name,
                    "state": cp.state,
                    "slug": cp.slug,
                    "title": cp.title,
                    "meta_description": cp.meta_description,
                    "primary_keyword": cp.primary_keyword,
                    "secondary_keywords": cp.secondary_keywords,
                    "hero_title": cp.hero_title,
                    "breadcrumbs": cp.breadcrumbs,
                    "about_city": cp.about_city,
                    "city_image": {
                        "image_url": cp.city_image.image_url,
                        "alt_text": cp.city_image.alt_text,
                        "caption": cp.city_image.caption,
                        "credit": cp.city_image.credit,
                        "source": cp.city_image.source,
                    },
                    "places_of_interest": [
                        {
                            "name": poi.name,
                            "embed_url": poi.embed_url,
                        }
                        for poi in cp.places_of_interest
                    ],
                    "city_faq": [
                        {
                            "question": faq.question,
                            "answer": faq.answer,
                        }
                        for faq in cp.city_faq
                    ],
                    "seo_content_title": cp.seo_content_title,
                    "seo_content_body": cp.seo_content_body,
                    "city_map_embed": cp.city_map_embed,
                    "full_city_name": cp.full_city_name,
                    "service_area_note": cp.service_area_note,
                    "featured_products": cp.featured_products,
                }
                for cp in config.city_pages
            ]
        self.enhanced_cities_tab.set_config_data(enhanced_cities_data)


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
            ],
            "faq": [
                {"question": f.question, "answer": f.answer}
                for f in config.faq
            ]
        }
        self.services_tab.set_config_data(services_data)

        # Set client context for cloud tab (loads client-specific AWS config)
        self.cloud_tab.set_client_context(config.business.business_name, config.business.domain)
        
        # Load cloud deployment data
        cloud_data = {
            # AWS credentials and settings
            "aws_profile": config.cloud.aws_profile,
            "aws_region": config.cloud.aws_region,

            # S3 and deployment settings
            "bucket_name": config.cloud.bucket_name,
            "deployment_mode": config.cloud.deployment_mode,
            "deployment_url": config.cloud.deployment_url,

            # CloudFront settings
            "distribution_id": config.cloud.distribution_id,
            "custom_domain": config.cloud.custom_domain,
            "auto_invalidate_cache": config.cloud.auto_invalidate_cache,

            # SEO and backlink configuration
            "site_type": config.cloud.site_type,
            "main_site_url": config.cloud.main_site_url,
            "allow_indexing": config.cloud.allow_indexing,
            "meta_tags": config.cloud.meta_tags,

            # Caching configuration
            "html_cache_control": config.cloud.html_cache_control,
            "asset_cache_control": config.cloud.asset_cache_control,

            # Website configuration
            "index_document": config.cloud.index_document,
            "error_document": config.cloud.error_document,

            # Deployment history
            "last_deployment": config.cloud.last_deployment,
        }
        self.cloud_tab.set_config_data(cloud_data)

        # Load deployment history (v3.2.0 - Phase 2)
        self.deployment_history_tab.set_config(config)

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
            "Cities": self.enhanced_cities_tab,
            "Products": self.products_tab,
            "Services & FAQ": self.services_tab,
            "Cloud Deploy": self.cloud_tab,
            # API Keys tab excluded - it's application-level, not client-specific
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
                        is_valid = getattr(validation_result, 'is_valid', False)
                        errors = getattr(validation_result, 'errors', ["Unable to determine validation result"])

                    validation_results[tab_name] = {
                        "valid": is_valid,
                        "errors": errors if errors else [],
                    }
                    
                    if not is_valid:
                        all_valid = False

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
            "Cities": self.enhanced_cities_tab,
            "Products": self.products_tab,
            "Services & FAQ": self.services_tab,
            # API Keys tab excluded - it's application-level, not client-specific
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
        
    def get_validation_results(self) -> tuple[Dict[str, Dict], bool]:
        """Get validation results without showing dialog - for internal use"""
        validation_results = {}
        all_valid = True

        # Validate each tab
        tabs = {
            "Business Info": self.business_tab,
            "Contact Details": self.contact_tab,
            "Branding & Style": self.branding_tab,
            "Cities": self.enhanced_cities_tab,
            "Products": self.products_tab,
            "Services & FAQ": self.services_tab,
            "Cloud Deploy": self.cloud_tab,
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
                        is_valid = getattr(validation_result, 'is_valid', False)
                        errors = getattr(validation_result, 'errors', ["Unable to determine validation result"])

                    validation_results[tab_name] = {
                        "valid": is_valid,
                        "errors": errors if errors else [],
                    }
                    
                    if not is_valid:
                        all_valid = False

                except Exception as e:
                    validation_results[tab_name] = {
                        "valid": False,
                        "errors": [f"Validation error: {str(e)}"],
                    }
                    all_valid = False

        return validation_results, all_valid

    def get_preview_validation_results(self) -> tuple[Dict[str, Dict], bool]:
        """Get validation results for preview - excludes Cloud Deploy tab"""
        validation_results = {}
        all_valid = True

        # Validate tabs needed for preview (exclude Cloud Deploy)
        tabs = {
            "Business Info": self.business_tab,
            "Contact Details": self.contact_tab,
            "Branding & Style": self.branding_tab,
            "Cities": self.enhanced_cities_tab,
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
                        is_valid = getattr(validation_result, 'is_valid', False)
                        errors = getattr(validation_result, 'errors', ["Unable to determine validation result"])

                    validation_results[tab_name] = {
                        "valid": is_valid,
                        "errors": errors if errors else [],
                    }
                    
                    if not is_valid:
                        all_valid = False

                except Exception as e:
                    validation_results[tab_name] = {
                        "valid": False,
                        "errors": [f"Validation error: {str(e)}"],
                    }
                    all_valid = False

        return validation_results, all_valid

    def show_validation_results(self, results: Dict[str, Dict], all_valid: bool):
        """Show validation results in a dialog"""
        if all_valid:
            QMessageBox.information(
                self,
                "Validation Results",
                "All tabs passed validation!\n\nYour configuration is ready for website generation.",
            )
            self.status_label.setText("Validation passed - Ready to generate")
        else:
            error_text = "Validation found the following issues:\n\n"
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

    def preview_website(self):
        """Preview website before generation for QA testing"""
        try:
            # NOTE: Cloud context is NOT needed for preview since we exclude cloud deployment
            # Only set cloud context if preview validation passes and user wants to deploy
            
            # Use preview-specific validation (excludes Cloud Deploy tab)
            validation_results, all_valid = self.get_preview_validation_results()
            
            if not all_valid:
                # Log validation errors to human-readable log
                error_details = []
                for tab_name, result in validation_results.items():
                    if not result["valid"] and result["errors"]:
                        for error in result["errors"]:
                            error_details.append(f"{tab_name}: {error}")
                
                error_message = "Please fix validation errors before previewing the website."
                context_info = "Preview validation failed. Errors: " + "; ".join(error_details)
                
                # Log to error file
                self.error_logger.log_error_dialog(
                    title="Preview Website Validation Failed",
                    message=error_message,
                    context=context_info,
                    component="preview_website",
                    user_action="Attempting to preview website"
                )
                
                QMessageBox.warning(
                    self,
                    "Validation Required", 
                    error_message
                )
                return
            
            # Get current configuration
            config_data = self.get_all_config_data()
            config = self.create_client_config(config_data)
            
            # Show preview dialog
            from .dialogs.website_preview_dialog import WebsitePreviewDialog
            preview_dialog = WebsitePreviewDialog(config, self)
            
            self.status_label.setText("Generating website preview...")
            
            result = preview_dialog.exec()
            
            if result == QDialog.DialogCode.Accepted:
                # User approved preview - proceed with actual generation
                self.status_label.setText("Preview approved - Ready to generate website")
                QMessageBox.information(
                    self,
                    "Preview Approved",
                    "Website preview has been approved. Click 'Generate Website' to create the final version."
                )
            else:
                self.status_label.setText("Preview cancelled")
                
        except Exception as e:
            error_message = f"Error during website preview:\n\n{str(e)}"
            
            # Log exception to error file
            self.error_logger.log_error_dialog(
                title="Website Preview Error",
                message=error_message,
                context="Exception occurred during website preview process",
                component="preview_website",
                exception=e,
                user_action="Attempting to preview website"
            )
            
            QMessageBox.critical(
                self,
                "Website Preview Error",
                error_message
            )
            self.status_label.setText("Website preview error")

    def generate_website(self):
        """Generate website from current configuration"""
        try:
            # Ensure client context is set for cloud tab before validation
            business_data = self.business_tab.get_config_data()
            if business_data.get('business_name') and business_data.get('domain'):
                self.cloud_tab.set_client_context(
                    business_data['business_name'], 
                    business_data['domain']
                )
            
            # First validate
            validation_results, all_valid = self.get_validation_results()
            if not all_valid:
                error_messages = []
                for tab_name, result in validation_results.items():
                    if not result["valid"]:
                        for error in result["errors"]:
                            error_messages.append(f"{tab_name}: {error}")
                
                QMessageBox.warning(
                    self,
                    "Validation Errors",
                    "Please fix the following errors before generating:\n\n" + "\n".join(error_messages)
                )
                return

            # ALWAYS use current UI data for generation (WYSIWYG approach)
            # This ensures users see exactly what they've configured in the UI
            config_data = self.get_all_config_data()
            config = self.create_client_config(config_data)
            
            # Preserve essential data from loaded config that isn't in UI
            if hasattr(self, 'loaded_config') and self.loaded_config:
                # Preserve Google Business Profile data
                if hasattr(self.loaded_config, 'google_business_profile') and self.loaded_config.google_business_profile:
                    config.google_business_profile = self.loaded_config.google_business_profile
            
            # Ask user for output directory (use last used directory or default)
            last_output_dir = self.settings.value("last_output_directory", str(Path.cwd() / "output" / "websites"))
            output_dir = QFileDialog.getExistingDirectory(
                self,
                "Select Output Directory for Website",
                last_output_dir
            )
            
            if not output_dir:
                return  # User cancelled

            # Disable generate button during generation
            self.generate_btn.setEnabled(False)
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            self.status_label.setText("Generating website...")

            # Start generation in background thread
            self.generation_worker = GenerationWorker(config, output_dir)
            self.generation_worker.progress.connect(self._update_generation_progress)
            self.generation_worker.finished.connect(self._generation_finished)
            self.generation_worker.start()

        except Exception as e:
            error_message = f"An error occurred while starting website generation:\n\n{str(e)}"
            log_error_dialog(
                "Generation Start Error",
                error_message,
                context="Exception caught while initializing generation",
                component="EnhancedMainWindow.generate_website",
                exception=e,
                user_action="Attempting to start website generation"
            )
            QMessageBox.critical(
                self,
                "Generation Error",
                error_message
            )
            self.status_label.setText("Failed to start generation")

    def _update_generation_progress(self, message: str):
        """Update progress during generation"""
        self.status_label.setText(message)

    def _generation_finished(
        self, success: bool, message: str, generated_files: list, output_dir: str
    ):
        """Handle generation completion"""
        self.progress_bar.setVisible(False)
        self.generate_btn.setEnabled(True)

        if success:
            # Save the output directory for next time
            self.settings.setValue("last_output_directory", output_dir)

            result = type('obj', (object,), {
                'success': True,
                'generated_files': generated_files,
                'errors': []
            })()

            display_message = "Website generated successfully!\n\nFiles created:\n"
            for file_path in result.generated_files:
                display_message += f"+ {Path(file_path).name}\n"
            display_message += f"\nLocation: {output_dir}"

            # Show generation success and offer cloud deployment
            reply = QMessageBox.question(
                self,
                "Website Generation Complete",
                display_message + "\n\nWould you like to deploy this website to the cloud?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )

            if reply == QMessageBox.StandardButton.Yes:
                cloud_tab_index = self.main_tabs.indexOf(self.cloud_tab)
                self.main_tabs.setCurrentIndex(cloud_tab_index)

                if self.cloud_tab.get_config_data().get('aws_profile') and self.cloud_tab.get_config_data().get('bucket_name'):
                    self.cloud_tab.local_path_input.setText(output_dir)
                    self.cloud_tab.deploy_website(output_dir)
                else:
                    QMessageBox.information(
                        self,
                        "Cloud Configuration Required",
                        "Please configure your AWS profile and S3 bucket in the Cloud Deploy tab before deploying."
                    )
            else:
                QMessageBox.information(
                    self,
                    "Website Ready",
                    "Your website is ready for manual deployment or you can use the Cloud Deploy tab later."
                )

            self.status_label.setText(f"Website generated successfully in {output_dir}")
        else:
            error_message = f"Failed to generate website:\n\n{message}"
            log_error_dialog(
                "Website Generation Failed",
                error_message,
                context="Website generation process failed",
                component="EnhancedMainWindow._generation_finished",
                user_action="Background generation completed with errors"
            )
            QMessageBox.critical(
                self,
                "Website Generation Failed",
                error_message
            )
            self.status_label.setText("Website generation failed")

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
            "<h3>SEO Authority Website Generator v3.2.0</h3>"
            "<p>Sprint 2 Week 2 - Enhanced Modular Architecture</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Business Information Management</li>"
            "<li>Contact Details with Validation</li>"
            "<li>Branding & Color Management</li>"
            "<li>Product Catalog with CSV Import</li>"
            "<li>Services & FAQ Management</li>"
            "<li><b>NEW:</b> Mode A (S3-Only) & Mode B (CloudFront + OAC) Deployment</li>"
            "<li><b>NEW:</b> Auto-Create CloudFront Distributions with OAC</li>"
            "<li><b>NEW:</b> Multi-Deployment Management</li>"
            "<li><b>NEW:</b> Per-Deployment Meta Tags</li>"
            "</ul>"
            "<p><b>Status:</b> Production-Ready Cloud Deployment</p>",
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
