"""
Filename: branding_tab_fixed.py
Path: E:/projects/cloud-stack-generator/src/ui/components/branding_tab_fixed.py
Description: Branding configuration tab with fixed layout issues
Simple, working layout that displays correctly in all screen modes

Version: 2.1.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

import re
import os
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QFrame,
    QGroupBox,
    QColorDialog,
    QFileDialog,
    QMessageBox,
    QWidget,
    QScrollArea,
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt, pyqtSignal
from .base_tab import BaseTab, ValidationResult
from typing import Dict, Any, List

# Import error logging


class BrandingTab(BaseTab):
    """Branding configuration tab with fixed layout"""

    # Signals
    config_changed = pyqtSignal()
    validation_requested = pyqtSignal()
    data_loaded = pyqtSignal()

    # Default colors
    DEFAULT_PRIMARY = "#007bff"
    DEFAULT_SECONDARY = "#6c757d"
    DEFAULT_BODY_BACKGROUND = "#ffffff"
    DEFAULT_BODY_TEXT = "#333333"
    DEFAULT_FOOTER_BACKGROUND = "#2c3e50"
    DEFAULT_FOOTER_TEXT = "#ffffff"

    # Web-safe fonts
    WEB_FONTS = [
        "Arial, sans-serif",
        "Helvetica, sans-serif",
        "Times New Roman, serif",
        "Georgia, serif",
        "Verdana, sans-serif",
        "Calibri, sans-serif",
        "Trebuchet MS, sans-serif",
        "Courier New, monospace",
        "Lucida Console, monospace",
        "Impact, sans-serif",
    ]

    def __init__(self, parent=None):
        self.branding_inputs = {}
        self.color_buttons = {}
        self.preview_labels = {}
        self.current_colors = {
            "primary": self.DEFAULT_PRIMARY,
            "secondary": self.DEFAULT_SECONDARY,
            "body_background": self.DEFAULT_BODY_BACKGROUND,
            "body_text": self.DEFAULT_BODY_TEXT,
            "footer_background": self.DEFAULT_FOOTER_BACKGROUND,
            "footer_text": self.DEFAULT_FOOTER_TEXT,
        }
        self.has_changes = False
        super().__init__(parent)

    def setup_ui(self):
        """Setup branding configuration UI with working layout"""
        # Create main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Create content widget
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Create sections
        self._create_color_section(content_layout)
        self._create_font_section(content_layout)
        self._create_logo_section(content_layout)
        self._create_template_section(content_layout)
        self._create_preview_section(content_layout)

        # Add validation button
        validation_button = QPushButton("Validate Branding Configuration")
        validation_button.clicked.connect(self.validate_data)
        validation_button.setStyleSheet(
            """
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """
        )
        validation_button.setMaximumWidth(300)
        content_layout.addWidget(validation_button)

        # Add stretch to push content to top
        content_layout.addStretch()

        # Create container widget
        container = QFrame()
        container.setLayout(content_layout)

        # Set up scroll area
        scroll_area.setWidget(container)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)

    def _create_color_section(self, parent_layout: QVBoxLayout):
        """Create color selection section"""
        # Section header
        header = QLabel("Brand Colors")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Color form in group box
        color_group = QGroupBox()
        color_group.setMaximumHeight(350)
        color_layout = QGridLayout()
        color_layout.setSpacing(15)

        # Color fields with updated names and new options
        colors = [
            (
                "Header Background Color 1",
                "primary",
                "Primary gradient color for header background",
            ),
            (
                "Header Background Color 2",
                "secondary",
                "Secondary gradient color for header background",
            ),
            (
                "Body Background Color",
                "body_background",
                "Background color for main content areas",
            ),
            ("Body Text Color", "body_text", "Text color for main content"),
            (
                "Footer Background Color",
                "footer_background",
                "Background color for footer section",
            ),
            ("Footer Text Color", "footer_text", "Text color for footer content"),
        ]

        for row, (label_text, color_key, description) in enumerate(colors):
            # Label
            label = QLabel(f"* {label_text}")
            label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            color_layout.addWidget(label, row, 0)

            # Color container
            color_container = QHBoxLayout()

            # Hex input
            hex_input = QLineEdit()
            hex_input.setFont(QFont("Arial", 10))
            hex_input.setPlaceholderText("#FFFFFF")
            hex_input.setMaximumWidth(100)
            hex_input.setText(self.current_colors[color_key])
            hex_input.textChanged.connect(
                lambda text, key=color_key: self._on_color_input_changed(key, text)
            )
            color_container.addWidget(hex_input)

            # Color preview
            color_preview = QLabel()
            color_preview.setMinimumSize(30, 30)
            color_preview.setMaximumSize(30, 30)
            color_preview.setStyleSheet(
                f"""
                QLabel {{
                    background-color: {self.current_colors[color_key]};
                    border: 2px solid #ccc;
                    border-radius: 4px;
                }}
            """
            )
            color_container.addWidget(color_preview)

            # Pick color button
            pick_button = QPushButton("Pick Color")
            pick_button.setMaximumWidth(80)
            pick_button.clicked.connect(
                lambda checked, key=color_key: self._open_color_picker(key)
            )
            color_container.addWidget(pick_button)

            color_container.addStretch()

            # Store references
            self.branding_inputs[color_key] = hex_input
            self.preview_labels[color_key] = color_preview
            self.color_buttons[color_key] = pick_button

            # Add to grid
            container_widget = QWidget()
            container_widget.setLayout(color_container)
            color_layout.addWidget(container_widget, row, 1)

        color_group.setLayout(color_layout)
        parent_layout.addWidget(color_group)

    def _create_font_section(self, parent_layout: QVBoxLayout):
        """Create font selection section"""
        # Section header
        header = QLabel("Typography")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Font form in group box
        font_group = QGroupBox()
        font_group.setMaximumHeight(100)
        font_layout = QGridLayout()
        font_layout.setSpacing(10)

        # Font family selection
        font_label = QLabel("* Font Family")
        font_label.setFont(QFont("Arial", 10))
        font_layout.addWidget(font_label, 0, 0)

        font_combo = QComboBox()
        font_combo.addItems(self.WEB_FONTS)
        font_combo.setFont(QFont("Arial", 10))
        font_combo.currentTextChanged.connect(self._on_font_changed)
        font_layout.addWidget(font_combo, 0, 1)

        self.branding_inputs["font_family"] = font_combo

        font_group.setLayout(font_layout)
        parent_layout.addWidget(font_group)

    def _create_logo_section(self, parent_layout: QVBoxLayout):
        """Create logo upload section"""
        # Section header
        header = QLabel("Logo & Branding Assets (Optional)")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Logo form in group box
        logo_group = QGroupBox()
        logo_group.setMaximumHeight(120)
        logo_layout = QVBoxLayout()
        logo_layout.setSpacing(10)

        # Logo URL field with button
        url_container = QHBoxLayout()

        logo_url_input = QLineEdit()
        logo_url_input.setFont(QFont("Arial", 10))
        logo_url_input.setPlaceholderText("Enter logo image URL or upload file")
        logo_url_input.textChanged.connect(self._emit_config_changed)
        url_container.addWidget(logo_url_input)

        upload_button = QPushButton("Upload Logo")
        upload_button.setMaximumWidth(100)
        upload_button.clicked.connect(self._upload_logo_file)
        url_container.addWidget(upload_button)

        logo_layout.addLayout(url_container)

        # Help text
        help_label = QLabel(
            "Upload a logo image (PNG, JPG, SVG recommended) or provide a URL. Logo will be displayed in the website header."
        )
        help_label.setFont(QFont("Arial", 9))
        help_label.setStyleSheet("color: #666; font-style: italic;")
        help_label.setWordWrap(True)
        logo_layout.addWidget(help_label)

        self.branding_inputs["logo_url"] = logo_url_input

        logo_group.setLayout(logo_layout)
        parent_layout.addWidget(logo_group)

    def _create_template_section(self, parent_layout: QVBoxLayout):
        """Create enhanced template selection section"""
        # Section header
        header = QLabel("Website Template")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Template selection group
        template_group = QGroupBox()
        template_layout = QVBoxLayout()
        template_layout.setSpacing(10)

        # Current template info
        self.current_template_info = QLabel("Loading template information...")
        self.current_template_info.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.current_template_info.setStyleSheet(
            "color: #2c5aa0; padding: 10px; background-color: #f8f9fa; border-radius: 5px;"
        )
        template_layout.addWidget(self.current_template_info)

        # Template description
        self.template_description = QLabel(
            "Select a template to customize your website's appearance and features."
        )
        self.template_description.setFont(QFont("Arial", 9))
        self.template_description.setStyleSheet("color: #666666; padding: 5px 0;")
        self.template_description.setWordWrap(True)
        template_layout.addWidget(self.template_description)

        # Template selection button
        button_layout = QHBoxLayout()

        self.select_template_btn = QPushButton("Choose Template...")
        self.select_template_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.select_template_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        self.select_template_btn.clicked.connect(self._open_template_selection)
        button_layout.addWidget(self.select_template_btn)

        # Import template button
        self.import_template_btn = QPushButton("Import Template...")
        self.import_template_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.import_template_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """
        )
        self.import_template_btn.clicked.connect(self._import_template)
        button_layout.addWidget(self.import_template_btn)

        # Export template button
        self.export_template_btn = QPushButton("Export Current")
        self.export_template_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.export_template_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #f39c12;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """
        )
        self.export_template_btn.clicked.connect(self._export_current_template)
        button_layout.addWidget(self.export_template_btn)

        # Template editor button
        self.edit_template_btn = QPushButton("Edit Template...")
        self.edit_template_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.edit_template_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        self.edit_template_btn.clicked.connect(self._open_template_editor)
        button_layout.addWidget(self.edit_template_btn)

        button_layout.addStretch()
        template_layout.addLayout(button_layout)

        template_group.setLayout(template_layout)
        parent_layout.addWidget(template_group)

        # Initialize template system
        self._initialize_template_system()

    def _create_preview_section(self, parent_layout: QVBoxLayout):
        """Create live preview section"""
        # Section header
        header = QLabel("Live Preview")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0 5px 0;")
        parent_layout.addWidget(header)

        # Preview widget
        self.preview_widget = QLabel("Color and Font Preview")
        self.preview_widget.setMinimumHeight(60)
        self.preview_widget.setMaximumHeight(60)
        self.preview_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._update_preview()

        parent_layout.addWidget(self.preview_widget)

    def _on_color_input_changed(self, color_key: str, hex_value: str):
        """Handle color input changes"""
        if re.match(r"^#[0-9A-Fa-f]{6}$", hex_value):
            self.current_colors[color_key] = hex_value

            # Update preview
            if color_key in self.preview_labels:
                self.preview_labels[color_key].setStyleSheet(
                    f"""
                    QLabel {{
                        background-color: {hex_value};
                        border: 2px solid #ccc;
                        border-radius: 4px;
                    }}
                """
                )

            self._update_preview()

        self._emit_config_changed()

    def _open_color_picker(self, color_key: str):
        """Open color picker dialog"""
        current_color = QColor(self.current_colors[color_key])
        color = QColorDialog.getColor(
            current_color, self, f"Choose {color_key.title()} Color"
        )

        if color.isValid():
            hex_color = color.name()
            self.current_colors[color_key] = hex_color

            # Update input and preview
            self.branding_inputs[color_key].setText(hex_color)
            self.preview_labels[color_key].setStyleSheet(
                f"""
                QLabel {{
                    background-color: {hex_color};
                    border: 2px solid #ccc;
                    border-radius: 4px;
                }}
            """
            )

            self._update_preview()
            self._emit_config_changed()

    def _update_preview(self):
        """Update live preview"""
        primary_color = self.current_colors.get("primary", self.DEFAULT_PRIMARY)
        secondary_color = self.current_colors.get("secondary", self.DEFAULT_SECONDARY)
        font_family = (
            self.branding_inputs.get("font_family", {}).currentText()
            if "font_family" in self.branding_inputs
            else "Arial, sans-serif"
        )

        self.preview_widget.setStyleSheet(
            f"""
            QLabel {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {primary_color},
                    stop:0.5 {secondary_color},
                    stop:1 {primary_color}
                );
                border: 2px solid #ddd;
                border-radius: 8px;
                font-family: {font_family.split(',')[0].strip('"')};
                color: white;
                font-size: 14px;
                font-weight: bold;
            }}
        """
        )

    def _on_font_changed(self, value: str):
        """Handle font changes"""
        self._update_preview()
        self._emit_config_changed()

    def _upload_logo_file(self):
        """Handle logo file upload"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Logo File",
            "",
            "Image Files (*.png *.jpg *.jpeg *.svg *.gif *.bmp)",
        )

        if file_path:
            self.branding_inputs["logo_url"].setText(file_path)
            QMessageBox.information(
                self,
                "Logo Uploaded",
                f"Logo file selected: {os.path.basename(file_path)}",
            )

    def get_config_data(self) -> Dict[str, Any]:
        """Get configuration data"""
        return {
            "colors": {
                "primary_color": self.current_colors.get(
                    "primary", self.DEFAULT_PRIMARY
                ),
                "secondary_color": self.current_colors.get(
                    "secondary", self.DEFAULT_SECONDARY
                ),
                "body_background_color": self.current_colors.get(
                    "body_background", self.DEFAULT_BODY_BACKGROUND
                ),
                "body_text_color": self.current_colors.get(
                    "body_text", self.DEFAULT_BODY_TEXT
                ),
                "footer_background_color": self.current_colors.get(
                    "footer_background", self.DEFAULT_FOOTER_BACKGROUND
                ),
                "footer_text_color": self.current_colors.get(
                    "footer_text", self.DEFAULT_FOOTER_TEXT
                ),
            },
            "typography": {
                "font_family": (
                    self.branding_inputs["font_family"].currentText()
                    if "font_family" in self.branding_inputs
                    else "Arial, sans-serif"
                )
            },
            "logo": {
                "logo_url": (
                    self.branding_inputs["logo_url"].text()
                    if "logo_url" in self.branding_inputs
                    else ""
                )
            },
            # Note: Template system will be redesigned in future updates
        }

    def set_config_data(self, data: Dict[str, Any]):
        """Set configuration data"""
        self._start_loading()

        try:
            # Set color data
            if "colors" in data:
                colors = data["colors"]
                if "primary_color" in colors:
                    self.current_colors["primary"] = colors["primary_color"]
                    if "primary" in self.branding_inputs:
                        self.branding_inputs["primary"].setText(colors["primary_color"])
                    if "primary" in self.preview_labels:
                        self.preview_labels["primary"].setStyleSheet(
                            f"""
                            QLabel {{
                                background-color: {colors["primary_color"]};
                                border: 2px solid #ccc;
                                border-radius: 4px;
                            }}
                        """
                        )

                if "secondary_color" in colors:
                    self.current_colors["secondary"] = colors["secondary_color"]
                    if "secondary" in self.branding_inputs:
                        self.branding_inputs["secondary"].setText(
                            colors["secondary_color"]
                        )
                    if "secondary" in self.preview_labels:
                        self.preview_labels["secondary"].setStyleSheet(
                            f"""
                            QLabel {{
                                background-color: {colors["secondary_color"]};
                                border: 2px solid #ccc;
                                border-radius: 4px;
                            }}
                        """
                        )

                # Handle new color fields
                color_mappings = [
                    ("body_background_color", "body_background"),
                    ("body_text_color", "body_text"),
                    ("footer_background_color", "footer_background"),
                    ("footer_text_color", "footer_text"),
                ]

                for config_key, internal_key in color_mappings:
                    if config_key in colors:
                        self.current_colors[internal_key] = colors[config_key]
                        if internal_key in self.branding_inputs:
                            self.branding_inputs[internal_key].setText(
                                colors[config_key]
                            )
                        if internal_key in self.preview_labels:
                            self.preview_labels[internal_key].setStyleSheet(
                                f"""
                                QLabel {{
                                    background-color: {colors[config_key]};
                                    border: 2px solid #ccc;
                                    border-radius: 4px;
                                }}
                            """
                            )

            # Set font data
            if "typography" in data:
                font_family = data["typography"].get("font_family", "Arial, sans-serif")
                if "font_family" in self.branding_inputs:
                    index = self.branding_inputs["font_family"].findText(font_family)
                    if index >= 0:
                        self.branding_inputs["font_family"].setCurrentIndex(index)

            # Set logo data
            if "logo" in data:
                logo_url = data["logo"].get("logo_url", "")
                if "logo_url" in self.branding_inputs:
                    self.branding_inputs["logo_url"].setText(logo_url)

            # Template data handling removed - template system will be redesigned

            # Update preview
            self._update_preview()

        finally:
            self._finish_loading()

    def get_required_fields(self) -> List[str]:
        """Get list of required field names for validation"""
        return ["primary_color", "secondary_color", "font_family"]

    def validate_data(self) -> ValidationResult:
        """Validate branding configuration"""
        result = ValidationResult()

        # Validate required color fields by checking actual input values
        primary_color = ""
        secondary_color = ""

        if "primary" in self.branding_inputs:
            primary_color = self.branding_inputs["primary"].text().strip()
        if "secondary" in self.branding_inputs:
            secondary_color = self.branding_inputs["secondary"].text().strip()

        if not primary_color or not re.match(r"^#[0-9A-Fa-f]{6}$", primary_color):
            result.add_error(
                "Primary color is required and must be a valid hex color", "primary"
            )

        if not secondary_color or not re.match(r"^#[0-9A-Fa-f]{6}$", secondary_color):
            result.add_error(
                "Secondary color is required and must be a valid hex color", "secondary"
            )

        # Check color contrast
        if primary_color and secondary_color:
            if primary_color.upper() == secondary_color.upper():
                result.add_warning(
                    "Primary and secondary colors are identical - consider using different colors for better visual hierarchy"
                )

        return result

    def get_tab_name(self) -> str:
        """Get tab name for title display"""
        return "Branding & Style"

    def connect_signals(self):
        """Connect UI signals"""
        pass

    def _initialize_template_system(self):
        """Initialize the template system"""
        try:
            import sys
            from pathlib import Path

            # Add the src directory to the Python path for imports
            src_path = str(Path(__file__).parent.parent.parent)
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            from core.templates.template_manager import TemplateManager

            self.template_manager = TemplateManager()
            self.selected_template_id = "seo_authority_city"  # Default template
            self._update_template_display()
        except Exception as e:
            print(f"Error initializing template system: {e}")
            self.current_template_info.setText("Error loading template system")

    def _update_template_display(self):
        """Update the template information display"""
        if hasattr(self, "template_manager") and self.template_manager:
            template_metadata = self.template_manager.get_template_by_id(
                self.selected_template_id
            )
            if template_metadata:
                self.current_template_info.setText(
                    f"Current Template: {template_metadata.name} - {template_metadata.variant.value.title()}"
                )
                self.template_description.setText(template_metadata.description)
            else:
                self.current_template_info.setText("Template not found")
        else:
            self.current_template_info.setText("Template system not available")

    def _open_template_selection(self):
        """Open the template selection dialog"""
        try:
            import sys
            from pathlib import Path

            # Add the src directory to the Python path for imports
            src_path = str(Path(__file__).parent.parent.parent)
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            from ui.dialogs.template_selection_dialog import TemplateSelectionDialog

            dialog = TemplateSelectionDialog(self.selected_template_id, self)
            dialog.template_selected.connect(self._on_template_selected)

            if dialog.exec() == TemplateSelectionDialog.DialogCode.Accepted:
                selected_id = dialog.get_selected_template_id()
                if selected_id and selected_id != self.selected_template_id:
                    self._on_template_selected(selected_id)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Template Selection Error",
                f"Failed to open template selection dialog:\\n{str(e)}",
            )

    def _on_template_selected(self, template_id: str):
        """Handle template selection"""
        self.selected_template_id = template_id
        self._update_template_display()
        self._emit_config_changed()

        # Show confirmation
        if hasattr(self, "template_manager") and self.template_manager:
            template_metadata = self.template_manager.get_template_by_id(template_id)
            if template_metadata:
                QMessageBox.information(
                    self,
                    "Template Selected",
                    f"Template '{template_metadata.name}' has been selected.\\n\\n"
                    f"This template will be used for generating city pages and other content.",
                )

    def get_selected_template_id(self) -> str:
        """Get the currently selected template ID"""
        return getattr(self, "selected_template_id", "seo_authority_city")

    def _import_template(self):
        """Handle template import from branding tab"""
        from PyQt6.QtWidgets import (
            QFileDialog,
            QProgressDialog,
            QMessageBox,
            QApplication,
        )
        from pathlib import Path

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Template Package",
            "",
            "Template Packages (*.zip);;All Files (*)",
        )

        if not file_path:
            return

        # Show progress dialog
        progress = QProgressDialog("Importing template...", "Cancel", 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.show()
        QApplication.processEvents()

        try:
            # Import using the existing template system
            import sys
            from pathlib import Path

            # Add the src directory to the Python path for imports
            src_path = str(Path(__file__).parent.parent.parent)
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            from core.templates.template_export import TemplateImporter

            if hasattr(self, "template_manager") and self.template_manager:
                importer = TemplateImporter(self.template_manager)
                success, message, template_id = importer.import_template_package(
                    Path(file_path)
                )

                progress.close()

                if success:
                    # Refresh template system
                    self.template_manager.refresh_templates()
                    self._update_template_display()

                    QMessageBox.information(
                        self,
                        "Import Successful",
                        f"Template imported successfully!\n\n{message}",
                    )

                    # Auto-select imported template
                    if template_id:
                        self.selected_template_id = template_id
                        self._update_template_display()
                else:
                    QMessageBox.warning(
                        self,
                        "Import Failed",
                        f"Failed to import template:\n\n{message}",
                    )
            else:
                progress.close()
                QMessageBox.warning(self, "Error", "Template system not initialized.")

        except Exception as e:
            progress.close()
            QMessageBox.critical(
                self,
                "Import Error",
                f"An error occurred while importing the template:\n\n{str(e)}",
            )

        finally:
            if progress.isVisible():
                progress.close()

    def _export_current_template(self):
        """Handle template export from branding tab"""
        from PyQt6.QtWidgets import (
            QFileDialog,
            QProgressDialog,
            QMessageBox,
            QApplication,
        )
        from pathlib import Path

        current_template_id = self.get_selected_template_id()
        if not current_template_id:
            QMessageBox.warning(
                self, "No Template", "No template is currently selected."
            )
            return

        try:
            # Get template metadata for default filename
            if hasattr(self, "template_manager") and self.template_manager:
                template_metadata = self.template_manager.get_template_by_id(
                    current_template_id
                )
                if not template_metadata:
                    QMessageBox.warning(self, "Error", "Template metadata not found.")
                    return

                # Create default filename
                safe_name = (
                    template_metadata.name.replace(" ", "_").replace("/", "_").lower()
                )
                default_name = f"{safe_name}_v{template_metadata.version}.zip"
            else:
                QMessageBox.warning(self, "Error", "Template system not initialized.")
                return

            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Template Package",
                default_name,
                "Template Packages (*.zip);;All Files (*)",
            )

            if not file_path:
                return

            # Show progress dialog
            progress = QProgressDialog("Exporting template...", "Cancel", 0, 0, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.show()
            QApplication.processEvents()

            # Import the exporter
            import sys
            from pathlib import Path

            # Add the src directory to the Python path for imports
            src_path = str(Path(__file__).parent.parent.parent)
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            from core.templates.template_export import TemplateExporter

            exporter = TemplateExporter(self.template_manager)
            success = exporter.export_template_package(
                current_template_id, Path(file_path)
            )

            progress.close()

            if success:
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Template '{template_metadata.name}' exported successfully!\n\n"
                    f"Package saved to:\n{file_path}\n\n"
                    f"You can now modify the template externally and re-import it.",
                )
            else:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    "Failed to export template. Please check file permissions and try again.",
                )

        except Exception as e:
            if "progress" in locals() and progress.isVisible():
                progress.close()
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting the template:\n\n{str(e)}",
            )

    def _open_template_editor(self):
        """Open WYSIWYG template editor"""
        try:
            import sys
            from pathlib import Path

            # Add the src directory to the Python path for imports
            src_path = str(Path(__file__).parent.parent.parent)
            if src_path not in sys.path:
                sys.path.insert(0, src_path)

            # Try the full editor first, fallback to simple editor
            try:
                from ui.dialogs.template_editor_dialog import TemplateEditorDialog

                editor_class = TemplateEditorDialog
                editor_type = "Advanced"
            except Exception as e:
                print(f"Advanced editor not available: {e}")
                from ui.dialogs.simple_template_editor import SimpleTemplateEditor

                editor_class = SimpleTemplateEditor
                editor_type = "Simple"

            # Get current template ID or None for new template
            template_id = getattr(self, "selected_template_id", None)

            dialog = editor_class(self, template_id)

            # Connect signals
            dialog.template_saved.connect(self._on_template_saved)
            dialog.template_created.connect(self._on_template_created)

            # Show info about editor type
            if editor_type == "Simple":
                QMessageBox.information(
                    self,
                    "Template Editor",
                    "Opening simplified template editor.\n\n"
                    "Some advanced features may not be available, but core editing functionality is preserved.",
                )

            # Show dialog
            dialog.exec()

        except Exception as e:
            # Log the error to error log
            import traceback

            error_msg = f"Template Editor Error: {str(e)}\n{traceback.format_exc()}"

            # Try to write to error log
            try:
                from pathlib import Path

                log_file = Path("logs/error_log.txt")
                log_file.parent.mkdir(exist_ok=True)

                with open(log_file, "a", encoding="utf-8") as f:
                    from datetime import datetime

                    f.write(f"\n[{datetime.now()}] TEMPLATE EDITOR ERROR:\n")
                    f.write(error_msg)
                    f.write("\n" + "=" * 50 + "\n")
            except Exception as log_error:
                print(f"Failed to log error: {log_error}")

            # Show error to user
            QMessageBox.critical(
                self,
                "Template Editor Error",
                f"Failed to open template editor:\n{str(e)}\n\n"
                f"Error details have been logged to logs/error_log.txt\n\n"
                f"Please ensure all dependencies are installed.",
            )

    def _on_template_saved(self, template_id: str):
        """Handle template saved event"""
        try:
            # Refresh template information if it's the current template
            if template_id == getattr(self, "selected_template_id", None):
                self._update_template_display()

                # Emit configuration change
                self._emit_config_changed()

            # Show success message
            if hasattr(self, "template_manager") and self.template_manager:
                template_metadata = self.template_manager.get_template_by_id(
                    template_id
                )
                template_name = (
                    template_metadata.name if template_metadata else template_id
                )
                QMessageBox.information(
                    self,
                    "Template Saved",
                    f"Template '{template_name}' saved successfully!",
                )

        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Error updating template information: {str(e)}"
            )

    def _on_template_created(self, template_id: str):
        """Handle new template created event"""
        try:
            # Update the selected template to the new one
            self.selected_template_id = template_id
            self._update_template_display()
            self._emit_config_changed()

            # Show success message
            if hasattr(self, "template_manager") and self.template_manager:
                template_metadata = self.template_manager.get_template_by_id(
                    template_id
                )
                template_name = (
                    template_metadata.name if template_metadata else template_id
                )
                QMessageBox.information(
                    self,
                    "Template Created",
                    f"New template '{template_name}' created and selected successfully!",
                )

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error handling new template: {str(e)}")
