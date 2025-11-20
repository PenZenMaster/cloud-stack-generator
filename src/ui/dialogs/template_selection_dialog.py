"""
Template Selection Dialog
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\dialogs\\template_selection_dialog.py

Description:
Dialog for selecting and previewing website templates.
Provides template information, preview capabilities, and selection options.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-18

Last Modified Date:
2025-09-18

Comments:
* v1.00 - Initial template selection dialog
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QFrame,
    QTextEdit,
    QSplitter,
    QGroupBox,
    QMessageBox,
    QApplication,
    QWidget,
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont

from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import webbrowser

import sys

# Add the src directory to the Python path for imports
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.templates.template_manager import TemplateManager, TemplateType  # noqa: E402
from core.templates.template_preview import TemplatePreviewGenerator  # noqa: E402


class TemplatePreviewWorker(QObject):
    """Worker for generating template previews in background"""

    finished = pyqtSignal(str, str)  # template_id, html_content
    error = pyqtSignal(str, str)  # template_id, error_message

    def __init__(self, template_manager: TemplateManager, template_id: str):
        super().__init__()
        self.template_manager = template_manager
        self.template_id = template_id

    def run(self):
        """Generate template preview"""
        try:
            preview_generator = TemplatePreviewGenerator(self.template_manager)
            html_content = preview_generator.generate_preview_html(self.template_id)

            if html_content:
                self.finished.emit(self.template_id, html_content)
            else:
                self.error.emit(self.template_id, "Failed to generate preview")

        except Exception as e:
            self.error.emit(self.template_id, str(e))


class TemplateCard(QFrame):
    """Individual template card widget"""

    template_selected = pyqtSignal(str)  # template_id
    preview_requested = pyqtSignal(str)  # template_id

    def __init__(self, template_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.template_id = template_data["id"]
        self.template_data = template_data
        self.is_selected = False

        self.setup_ui()
        self.update_selection_state()

    def setup_ui(self):
        """Setup the template card UI"""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedSize(280, 200)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)

        # Template name
        name_label = QLabel(self.template_data["name"])
        name_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(name_label)

        # Variant badge
        variant_label = QLabel(self.template_data["variant"].title())
        variant_label.setFont(QFont("Arial", 9))
        variant_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        variant_label.setStyleSheet(
            """
            background-color: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 10px;
            font-weight: bold;
        """
        )
        variant_label.setMaximumHeight(20)
        layout.addWidget(variant_label)

        # Description
        description = (
            self.template_data["description"][:100] + "..."
            if len(self.template_data["description"]) > 100
            else self.template_data["description"]
        )
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Arial", 9))
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        desc_label.setStyleSheet("color: #666; line-height: 1.2;")
        layout.addWidget(desc_label)

        # Features count
        features_count = len(self.template_data["features"])
        features_label = QLabel(
            f"{features_count} Features • v{self.template_data['version']}"
        )
        features_label.setFont(QFont("Arial", 8))
        features_label.setStyleSheet("color: #999;")
        features_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(features_label)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)

        select_btn = QPushButton("Select")
        select_btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))
        select_btn.clicked.connect(self.select_template)
        button_layout.addWidget(select_btn)

        preview_btn = QPushButton("Preview")
        preview_btn.setFont(QFont("Arial", 9))
        preview_btn.clicked.connect(self.preview_template)
        button_layout.addWidget(preview_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def select_template(self):
        """Handle template selection"""
        self.template_selected.emit(self.template_id)

    def preview_template(self):
        """Handle preview request"""
        self.preview_requested.emit(self.template_id)

    def set_selected(self, selected: bool):
        """Set selection state"""
        self.is_selected = selected
        self.update_selection_state()

    def update_selection_state(self):
        """Update visual selection state"""
        if self.is_selected:
            self.setStyleSheet(
                """
                TemplateCard {
                    border: 3px solid #2ecc71;
                    background-color: #e8f8f0;
                    border-radius: 8px;
                }
            """
            )
        else:
            self.setStyleSheet(
                """
                TemplateCard {
                    border: 1px solid #ddd;
                    background-color: white;
                    border-radius: 8px;
                }
                TemplateCard:hover {
                    border: 2px solid #3498db;
                    background-color: #f8f9fa;
                }
            """
            )

    def mousePressEvent(self, event):
        """Handle mouse press for selection"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.select_template()
        super().mousePressEvent(event)


class TemplateSelectionDialog(QDialog):
    """Dialog for selecting website templates"""

    template_selected = pyqtSignal(str)  # template_id

    def __init__(self, current_template_id: str = None, parent=None):
        super().__init__(parent)
        self.current_template_id = current_template_id
        self.template_manager = TemplateManager()
        self.template_cards: List[TemplateCard] = []
        self.selected_template_id = current_template_id
        self.preview_worker = None
        self.preview_thread = None

        self.setup_ui()
        self.load_templates()

    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle("Select Website Template")
        self.setModal(True)
        self.resize(1000, 700)

        layout = QVBoxLayout()

        # Header
        header_label = QLabel("Choose a Website Template")
        header_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("color: #2c3e50; padding: 10px;")
        layout.addWidget(header_label)

        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left panel - Template selection
        left_panel = self.create_template_selection_panel()
        splitter.addWidget(left_panel)

        # Right panel - Template details and preview
        right_panel = self.create_template_details_panel()
        splitter.addWidget(right_panel)

        # Set splitter sizes
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)

        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        import_btn = QPushButton("Import Template...")
        import_btn.clicked.connect(self.import_template)
        button_layout.addWidget(import_btn)

        export_btn = QPushButton("Export Template...")
        export_btn.clicked.connect(self.export_template)
        button_layout.addWidget(export_btn)

        button_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        select_btn = QPushButton("Use Selected Template")
        select_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        select_btn.setStyleSheet(
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
        select_btn.clicked.connect(self.accept_selection)
        button_layout.addWidget(select_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def create_template_selection_panel(self) -> QWidget:
        """Create the template selection panel"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Section header
        header = QLabel("Available Templates")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; padding: 10px 0;")
        layout.addWidget(header)

        # Scroll area for template cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container for template cards
        self.templates_container = QWidget()
        self.templates_layout = QGridLayout()
        self.templates_layout.setSpacing(20)
        self.templates_container.setLayout(self.templates_layout)

        scroll_area.setWidget(self.templates_container)
        layout.addWidget(scroll_area)

        panel.setLayout(layout)
        return panel

    def create_template_details_panel(self) -> QWidget:
        """Create the template details and preview panel"""
        panel = QWidget()
        layout = QVBoxLayout()

        # Template details section
        details_group = QGroupBox("Template Details")
        details_layout = QVBoxLayout()

        self.template_name_label = QLabel("No template selected")
        self.template_name_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        details_layout.addWidget(self.template_name_label)

        self.template_description = QTextEdit()
        self.template_description.setMaximumHeight(80)
        self.template_description.setReadOnly(True)
        details_layout.addWidget(self.template_description)

        self.template_features = QTextEdit()
        self.template_features.setMaximumHeight(120)
        self.template_features.setReadOnly(True)
        details_layout.addWidget(self.template_features)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        # Preview section
        preview_group = QGroupBox("Template Preview")
        preview_layout = QVBoxLayout()

        preview_buttons = QHBoxLayout()

        self.preview_btn = QPushButton("Generate Preview")
        self.preview_btn.clicked.connect(self.generate_preview)
        preview_buttons.addWidget(self.preview_btn)

        self.open_preview_btn = QPushButton("Open in Browser")
        self.open_preview_btn.clicked.connect(self.open_preview_in_browser)
        self.open_preview_btn.setEnabled(False)
        preview_buttons.addWidget(self.open_preview_btn)

        preview_buttons.addStretch()
        preview_layout.addLayout(preview_buttons)

        self.preview_status = QLabel("Click 'Generate Preview' to see template preview")
        self.preview_status.setStyleSheet("color: #666; font-style: italic;")
        preview_layout.addWidget(self.preview_status)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        panel.setLayout(layout)
        return panel

    def load_templates(self):
        """Load available templates into the UI"""
        templates = self.template_manager.get_available_templates(
            TemplateType.CITY_PAGE
        )

        row = 0
        col = 0
        max_cols = 2

        for template in templates:
            template_data = {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "variant": template.variant.value,
                "features": template.features,
                "version": template.version,
            }

            card = TemplateCard(template_data)
            card.template_selected.connect(self.on_template_selected)
            card.preview_requested.connect(self.on_preview_requested)

            if template.id == self.current_template_id:
                card.set_selected(True)
                self.selected_template_id = template.id
                self.update_template_details(template)

            self.template_cards.append(card)
            self.templates_layout.addWidget(card, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        # Add stretch to push cards to top
        self.templates_layout.setRowStretch(row + 1, 1)

    def on_template_selected(self, template_id: str):
        """Handle template selection"""
        self.selected_template_id = template_id

        # Update card selection states
        for card in self.template_cards:
            card.set_selected(card.template_id == template_id)

        # Update details panel
        template_metadata = self.template_manager.get_template_by_id(template_id)
        if template_metadata:
            self.update_template_details(template_metadata)

    def on_preview_requested(self, template_id: str):
        """Handle preview request"""
        self.selected_template_id = template_id
        self.on_template_selected(template_id)
        self.generate_preview()

    def update_template_details(self, template_metadata):
        """Update the template details panel"""
        self.template_name_label.setText(
            f"{template_metadata.name} (v{template_metadata.version})"
        )
        self.template_description.setPlainText(template_metadata.description)

        features_text = "Features:\\n" + "\\n".join(
            [f"• {feature}" for feature in template_metadata.features]
        )
        features_text += "\\n\\nCompatibility:\\n"
        for key, value in template_metadata.compatibility.items():
            features_text += f"• {key.replace('_', ' ').title()}: {value}\\n"

        self.template_features.setPlainText(features_text)

    def generate_preview(self):
        """Generate template preview"""
        if not self.selected_template_id:
            return

        self.preview_btn.setEnabled(False)
        self.preview_btn.setText("Generating...")
        self.preview_status.setText("Generating template preview...")

        # Clean up existing worker
        self._cleanup_preview_worker()

        # Create new worker thread
        self.preview_thread = QThread()
        self.preview_worker = TemplatePreviewWorker(
            self.template_manager, self.selected_template_id
        )
        self.preview_worker.moveToThread(self.preview_thread)

        # Connect signals
        self.preview_thread.started.connect(self.preview_worker.run)
        self.preview_worker.finished.connect(self._on_preview_generated)
        self.preview_worker.error.connect(self._on_preview_error)
        self.preview_worker.finished.connect(self.preview_thread.quit)
        self.preview_worker.error.connect(self.preview_thread.quit)
        self.preview_thread.finished.connect(self._cleanup_preview_worker)

        # Start the worker
        self.preview_thread.start()

    def _on_preview_generated(self, template_id: str, html_content: str):
        """Handle successful preview generation"""
        self.preview_html = html_content
        self.preview_btn.setEnabled(True)
        self.preview_btn.setText("Generate Preview")
        self.open_preview_btn.setEnabled(True)
        self.preview_status.setText(
            "Preview generated successfully! Click 'Open in Browser' to view."
        )

    def _on_preview_error(self, template_id: str, error_message: str):
        """Handle preview generation error"""
        self.preview_btn.setEnabled(True)
        self.preview_btn.setText("Generate Preview")
        self.preview_status.setText(f"Error generating preview: {error_message}")
        QMessageBox.warning(
            self, "Preview Error", f"Failed to generate preview:\\n{error_message}"
        )

    def _cleanup_preview_worker(self):
        """Clean up preview worker thread"""
        if self.preview_worker:
            self.preview_worker.deleteLater()
            self.preview_worker = None

        if self.preview_thread:
            self.preview_thread.deleteLater()
            self.preview_thread = None

    def open_preview_in_browser(self):
        """Open the generated preview in the default browser"""
        if not hasattr(self, "preview_html") or not self.preview_html:
            return

        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8"
            ) as f:
                f.write(self.preview_html)
                temp_path = f.name

            # Open in browser
            webbrowser.open(f"file://{temp_path}")

        except Exception as e:
            QMessageBox.warning(
                self, "Preview Error", f"Failed to open preview in browser:\\n{str(e)}"
            )

    def import_template(self):
        """Import a custom template"""
        from PyQt6.QtWidgets import QFileDialog, QProgressDialog
        from core.templates.template_export import TemplateImporter

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
            importer = TemplateImporter(self.template_manager)
            success, message, template_id = importer.import_template_package(
                Path(file_path)
            )

            progress.close()

            if success:
                # Refresh template list
                self.template_manager.refresh_templates()
                self.load_templates()

                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Template imported successfully!\n\n{message}",
                )

                # Auto-select imported template if available
                if template_id and hasattr(self, "template_cards"):
                    for card in self.template_cards:
                        if card.template_id == template_id:
                            self.on_template_selected(template_id)
                            break
            else:
                QMessageBox.warning(
                    self, "Import Failed", f"Failed to import template:\n\n{message}"
                )

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

    def export_template(self):
        """Export the selected template"""
        if not self.selected_template_id:
            QMessageBox.warning(
                self, "No Selection", "Please select a template to export."
            )
            return

        from PyQt6.QtWidgets import QFileDialog, QProgressDialog
        from core.templates.template_export import TemplateExporter

        # Get template metadata for default filename
        template_metadata = self.template_manager.get_template_by_id(
            self.selected_template_id
        )
        if not template_metadata:
            QMessageBox.warning(self, "Error", "Template metadata not found.")
            return

        # Create default filename
        safe_name = template_metadata.name.replace(" ", "_").replace("/", "_").lower()
        default_name = f"{safe_name}_v{template_metadata.version}.zip"

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

        try:
            exporter = TemplateExporter(self.template_manager)
            success = exporter.export_template_package(
                self.selected_template_id, Path(file_path)
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
            progress.close()
            QMessageBox.critical(
                self,
                "Export Error",
                f"An error occurred while exporting the template:\n\n{str(e)}",
            )

        finally:
            if progress.isVisible():
                progress.close()

    def accept_selection(self):
        """Accept the selected template"""
        if not self.selected_template_id:
            QMessageBox.warning(
                self, "No Selection", "Please select a template before proceeding."
            )
            return

        self.template_selected.emit(self.selected_template_id)
        self.accept()

    def get_selected_template_id(self) -> Optional[str]:
        """Get the selected template ID"""
        return self.selected_template_id

    def closeEvent(self, event):
        """Handle dialog close event"""
        self._cleanup_preview_worker()
        super().closeEvent(event)
