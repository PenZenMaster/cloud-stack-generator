"""
Simple Template Editor - Fallback WYSIWYG Template Editor
Path: E:/projects/cloud-stack-generator/src/ui/dialogs/simple_template_editor.py

Description:
Simplified template editor that works without advanced dependencies.
Provides basic editing capabilities with text-based preview.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Simplified template editor for compatibility
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QSplitter, QGroupBox, QMessageBox, QTabWidget,
    QWidget, QLineEdit, QComboBox, QMenuBar, QStatusBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QKeySequence

from typing import Dict, Optional
from pathlib import Path
import sys

# Add the src directory to the Python path for imports
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

try:
    from core.templates.template_manager import TemplateManager, TemplateType, TemplateMetadata, TemplateVariant
    from core.templates.backup_manager import TemplateBackupManager
    CORE_AVAILABLE = True
except ImportError:
    print("Core template modules not available")
    CORE_AVAILABLE = False

# Import enhanced error handling
try:
    from ...utils import log_ui_error
    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    print("Enhanced error handling not available")
    ERROR_HANDLING_AVAILABLE = False


class SimpleTemplateEditor(QDialog):
    """Simplified Template Editor Dialog"""

    # Signals
    template_saved = pyqtSignal(str)  # template_id
    template_created = pyqtSignal(str)  # template_id

    def __init__(self, parent=None, template_id: Optional[str] = None):
        super().__init__(parent)
        self.template_id = template_id
        self.current_template_content = ""
        self.is_modified = False

        if CORE_AVAILABLE:
            self.template_manager = TemplateManager()
            self.backup_manager = TemplateBackupManager(self.template_manager.templates_dir)
        else:
            self.template_manager = None
            self.backup_manager = None

        self._setup_ui()
        self._load_template()

    def _setup_ui(self):
        """Setup the simplified UI"""
        self.setWindowTitle("Template Editor")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Menu bar
        self._create_menu_bar(main_layout)

        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Editor
        left_panel = self._create_editor_panel()
        splitter.addWidget(left_panel)

        # Right panel - Preview and properties
        right_panel = self._create_preview_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions (60% left, 40% right)
        splitter.setSizes([720, 480])

        # Status bar
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        main_layout.addWidget(self.status_bar)

    def _create_menu_bar(self, parent_layout: QVBoxLayout):
        """Create the menu bar"""
        menu_bar = QMenuBar()
        parent_layout.addWidget(menu_bar)

        # File menu
        file_menu = menu_bar.addMenu("File")

        save_action = QAction("Save", self)
        try:
            save_action.setShortcut(QKeySequence.StandardKey.Save)
        except AttributeError:
            save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._save_template)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self._save_template_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        if CORE_AVAILABLE:
            backup_action = QAction("Create Backup", self)
            backup_action.triggered.connect(self._create_backup)
            file_menu.addAction(backup_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        refresh_action = QAction("Refresh Preview", self)
        try:
            refresh_action.setShortcut(QKeySequence("F5"))
        except Exception:
            refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_preview)
        edit_menu.addAction(refresh_action)

    def _create_editor_panel(self) -> QWidget:
        """Create the editor panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Editor header
        header = QLabel("Template Editor")
        header.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(header)

        # HTML editor
        self.html_editor = QTextEdit()
        self.html_editor.setFont(QFont("Consolas", 11))
        self.html_editor.textChanged.connect(self._on_content_changed)
        self.html_editor.setPlaceholderText("Enter your HTML template code here...")
        layout.addWidget(self.html_editor)

        return panel

    def _create_preview_panel(self) -> QWidget:
        """Create the preview and properties panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for preview and properties
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Preview tab
        preview_widget = self._create_preview_tab()
        tab_widget.addTab(preview_widget, "Preview")

        # Properties tab
        properties_widget = self._create_properties_tab()
        tab_widget.addTab(properties_widget, "Properties")

        return panel

    def _create_preview_tab(self) -> QWidget:
        """Create the preview tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Preview header
        header_layout = QHBoxLayout()
        header = QLabel("Live Preview")
        header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(header)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_preview)
        header_layout.addWidget(refresh_btn)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Preview area
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setPlaceholderText("Preview will appear here after refresh...")
        layout.addWidget(self.preview_area)

        return widget

    def _create_properties_tab(self) -> QWidget:
        """Create the properties tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Properties form
        form_group = QGroupBox("Template Properties")
        form_layout = QVBoxLayout()

        # Template ID
        id_layout = QHBoxLayout()
        id_layout.addWidget(QLabel("Template ID:"))
        self.template_id_edit = QLineEdit()
        self.template_id_edit.textChanged.connect(self._on_property_changed)
        id_layout.addWidget(self.template_id_edit)
        form_layout.addLayout(id_layout)

        # Template name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.template_name_edit = QLineEdit()
        self.template_name_edit.textChanged.connect(self._on_property_changed)
        name_layout.addWidget(self.template_name_edit)
        form_layout.addLayout(name_layout)

        # Description
        desc_label = QLabel("Description:")
        form_layout.addWidget(desc_label)
        self.template_description_edit = QTextEdit()
        self.template_description_edit.setMaximumHeight(100)
        self.template_description_edit.textChanged.connect(self._on_property_changed)
        form_layout.addWidget(self.template_description_edit)

        # Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Type:"))
        self.template_type_combo = QComboBox()
        if CORE_AVAILABLE:
            self.template_type_combo.addItems([t.value for t in TemplateType])
        else:
            self.template_type_combo.addItems(["city_page", "landing_page", "product_page"])
        self.template_type_combo.currentTextChanged.connect(self._on_property_changed)
        type_layout.addWidget(self.template_type_combo)
        form_layout.addLayout(type_layout)

        # Version
        version_layout = QHBoxLayout()
        version_layout.addWidget(QLabel("Version:"))
        self.template_version_edit = QLineEdit()
        self.template_version_edit.setText("1.00")
        self.template_version_edit.textChanged.connect(self._on_property_changed)
        version_layout.addWidget(self.template_version_edit)
        form_layout.addLayout(version_layout)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        layout.addStretch()
        return widget

    def _load_template(self):
        """Load template if template_id is provided"""
        if not self.template_id or not CORE_AVAILABLE:
            self._new_template()
            return

        try:
            metadata = self.template_manager.get_template_by_id(self.template_id)
            if not metadata:
                QMessageBox.warning(self, "Error", f"Template {self.template_id} not found")
                self._new_template()
                return

            # Load template content
            template_path = self.template_manager.templates_dir / metadata.template_file
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    self.current_template_content = f.read()
                    self.html_editor.setPlainText(self.current_template_content)

            # Load metadata into properties
            self.template_id_edit.setText(metadata.id)
            self.template_name_edit.setText(metadata.name)
            self.template_description_edit.setPlainText(metadata.description)
            self.template_type_combo.setCurrentText(metadata.type.value)
            self.template_version_edit.setText(metadata.version)

            # Update window title
            self.setWindowTitle(f"Template Editor - {metadata.name}")

            # Generate initial preview
            self._refresh_preview()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error loading template: {str(e)}")
            self._new_template()

    def _new_template(self):
        """Create a new template"""
        self.template_id = None
        self.current_template_content = self._get_default_template_content()
        self.html_editor.setPlainText(self.current_template_content)

        # Clear properties
        self.template_id_edit.clear()
        self.template_name_edit.setText("New Template")
        self.template_description_edit.clear()
        self.template_type_combo.setCurrentIndex(0)
        self.template_version_edit.setText("1.00")

        self.setWindowTitle("Template Editor - New Template")
        self.is_modified = False

    def _get_default_template_content(self) -> str:
        """Get default template content for new templates"""
        return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title | default('New Page') }}</title>
    <meta name="description" content="{{ meta_description | default('') }}">

    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        .header {
            background-color: #f8f9fa;
            padding: 20px 0;
            margin-bottom: 30px;
        }

        .content {
            margin-bottom: 30px;
        }

        .footer {
            background-color: #343a40;
            color: white;
            padding: 20px 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <h1>{{ business.business_name | default('Your Business') }}</h1>
            <p>{{ business.tagline | default('Your tagline here') }}</p>
        </div>
    </header>

    <main class="content">
        <div class="container">
            <h2>{{ page_heading | default('Welcome') }}</h2>
            <p>{{ page_content | default('Your content goes here.') }}</p>
        </div>
    </main>

    <footer class="footer">
        <div class="container">
            <p>&copy; {{ current_year }} {{ business.business_name | default('Your Business') }}. All rights reserved.</p>
        </div>
    </footer>
</body>
</html>'''

    def _on_content_changed(self):
        """Handle content changes in the editor"""
        self.current_template_content = self.html_editor.toPlainText()
        self.is_modified = True
        self.status_label.setText("Modified")

    def _on_property_changed(self):
        """Handle property changes"""
        self.is_modified = True
        self.status_label.setText("Modified")

    def _load_component_templates(self) -> Dict[str, str]:
        """Load component templates for includes"""
        component_templates = {}
        try:
            from pathlib import Path

            # Get templates directory
            templates_dir = Path(__file__).parent.parent.parent / "templates"
            components_dir = templates_dir / "components"

            if components_dir.exists():
                # Load all .html files from components directory
                for component_file in components_dir.glob("*.html"):
                    try:
                        with open(component_file, 'r', encoding='utf-8') as f:
                            # Use relative path as key (e.g., 'components/header.html')
                            key = f"components/{component_file.name}"
                            component_templates[key] = f.read()
                    except Exception as e:
                        print(f"Error loading component {component_file}: {e}")

            # Also add common component names without the 'components/' prefix for compatibility
            for key, content in list(component_templates.items()):
                if key.startswith('components/'):
                    simple_key = key.replace('components/', '')
                    component_templates[simple_key] = content

        except Exception as e:
            print(f"Error loading component templates: {e}")

        return component_templates

    def _slugify_filter(self, text: str) -> str:
        """Convert text to URL-friendly slug"""
        import re
        if not text:
            return ""
        slug = re.sub(r"[^\w\s-]", "", str(text).lower())
        slug = re.sub(r"[-\s]+", "-", slug)
        return slug.strip("-")

    def _date_filter(self, date_input, format_str="%Y-%m-%d"):
        """Format date string - supports 'now' keyword for current date"""
        from datetime import datetime

        if isinstance(date_input, str) and date_input.lower() == "now":
            return datetime.now().strftime(format_str)
        elif isinstance(date_input, datetime):
            return date_input.strftime(format_str)
        else:
            try:
                date_obj = datetime.fromisoformat(str(date_input))
                return date_obj.strftime(format_str)
            except Exception:
                return str(date_input)

    def _urlencode_filter(self, text: str) -> str:
        """URL encode text"""
        from urllib.parse import quote
        if not text:
            return ""
        return quote(str(text))

    def _markdown_basic_filter(self, text: str) -> str:
        """Basic markdown to HTML conversion"""
        if not text:
            return ""
        # Simple markdown conversion for common cases
        text = str(text)
        text = text.replace('\n\n', '</p><p>')
        text = text.replace('\n', '<br>')
        if not text.startswith('<p>'):
            text = '<p>' + text
        if not text.endswith('</p>'):
            text = text + '</p>'
        return text

    def _refresh_preview(self):
        """Refresh the preview"""
        try:
            # Try to render with Jinja2 if available
            try:
                from jinja2 import Environment, DictLoader
                # Load component templates for includes
                component_templates = self._load_component_templates()
                env = Environment(loader=DictLoader(component_templates))

                # Add custom filters used by templates
                env.filters['slugify'] = self._slugify_filter
                env.filters['date'] = self._date_filter
                env.filters['urlencode'] = self._urlencode_filter
                env.filters['markdown_basic'] = self._markdown_basic_filter

                template = env.from_string(self.current_template_content)

                # Generate comprehensive sample data to match all template variables
                sample_data = {
                    'page_title': 'Sample Page Title',
                    'meta_description': 'Sample meta description for preview',
                    'page_heading': 'Welcome to Sample Page',
                    'page_content': 'This is sample content to show how the template looks.',
                    'page_url': 'https://example.com/sample',
                    'current_year': '2025',
                    'current_date': '2025-09-22',
                    'branding': {
                        'primary_color': '#2c3e50',
                        'secondary_color': '#3498db',
                        'accent_color': '#e74c3c',
                        'logo_url': 'https://via.placeholder.com/200x80/2c3e50/ffffff?text=LOGO',
                        'font_family': 'Arial'
                    },
                    'business': {
                        'business_name': 'Sample Business',
                        'tagline': 'Your trusted service provider',
                        'description': 'Quality services for our community',
                        'legal_name': 'Sample Business LLC',
                        'industry': 'Professional Services',
                        'service_overview': 'Comprehensive service solutions for your business needs.',
                        'domain': 'https://samplebusiness.com'
                    },
                    'contact': {
                        'phone': '(555) 123-4567',
                        'email': 'info@sample.com',
                        'address': {
                            'street': '123 Main Street',
                            'city': 'Sample City',
                            'state': 'ST',
                            'zip_code': '12345',
                            'country': 'US'
                        },
                        'full_address': '123 Main Street, Sample City, ST 12345'
                    },
                    'google_business_profile': {
                        'embed_code': '<iframe src="https://www.google.com/maps/embed/sample" width="600" height="450" style="border:0;" allowfullscreen="" loading="lazy"></iframe>',
                        'business_url': 'https://www.google.com/maps/place/Sample+Business',
                        'review_count': 25,
                        'average_rating': 4.8
                    },
                    'social_media': {
                        'facebook': 'https://facebook.com/samplebusiness',
                        'linkedin': 'https://linkedin.com/company/samplebusiness',
                        'instagram': 'https://instagram.com/samplebusiness',
                        'youtube': 'https://youtube.com/c/samplebusiness'
                    },
                    'city_page': {
                        'title': 'Sample City Services',
                        'meta_description': 'Professional services in Sample City',
                        'city_name': 'Sample City',
                        'state': 'Sample State',
                        'primary_keyword': 'services Sample City',
                        'secondary_keywords': ['local business', 'professional services'],
                        'hero_title': 'Professional Services in Sample City',
                        'about_city': 'Sample City is a great place for business',
                        'seo_content_body': 'We serve the Sample City area with quality services',
                        'city_image': {
                            'image_url': 'https://via.placeholder.com/800x400?text=Sample+City',
                            'alt_text': 'Sample City view',
                            'caption': 'Sample City',
                            'embed_code': '<div>Sample Image</div>'
                        },
                        'places_of_interest': [
                            {'name': 'Sample Park', 'description': 'Local park', 'google_maps_embed': '<div>Map</div>'}
                        ],
                        'city_faq': [
                            {'question': 'What services do you provide?', 'answer': 'We provide quality services'}
                        ]
                    },
                    'services': [
                        {'name': 'Service A', 'description': 'Quality service'}
                    ],
                    'products': [
                        {'name': 'Product A', 'description': 'Quality product', 'price': '$99'}
                    ]
                }

                rendered_html = template.render(**sample_data)
                self.preview_area.setHtml(rendered_html)
                self.status_label.setText("Preview updated")

            except ImportError:
                # Fallback: show raw HTML
                self.preview_area.setPlainText(self.current_template_content)
                self.status_label.setText("Preview updated (raw HTML)")

        except Exception as e:
            self.preview_area.setPlainText(f"Preview error: {str(e)}\n\nRaw content:\n{self.current_template_content}")
            self.status_label.setText(f"Preview error: {str(e)}")

    def _save_template(self):
        """Save the current template"""
        if not self.template_id:
            self._save_template_as()
            return

        if not CORE_AVAILABLE:
            QMessageBox.warning(self, "Error", "Core template system not available for saving")
            return

        try:
            # Create backup before saving
            if self.backup_manager:
                self._create_automatic_backup()

            # Save template file
            metadata = self._create_metadata_from_properties()
            template_path = self.template_manager.templates_dir / metadata.template_file

            # Ensure directory exists
            template_path.parent.mkdir(parents=True, exist_ok=True)

            # Write template file
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(self.current_template_content)

            # Save metadata
            import json
            metadata_path = template_path.with_suffix('.template.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.__dict__, f, indent=2, default=str)

            self.is_modified = False
            self.status_label.setText("Template saved successfully")

            # Emit signal
            self.template_saved.emit(self.template_id)

        except Exception as e:
            # Log error with enhanced error handler
            if ERROR_HANDLING_AVAILABLE:
                log_ui_error(
                    widget_name="SimpleTemplateEditor",
                    action="save_template",
                    error=e,
                    user_action="Saving template"
                )

            QMessageBox.critical(self, "Save Error", f"Error saving template:\n{str(e)}")
            self.status_label.setText(f"Save failed: {str(e)}")

    def _save_template_as(self):
        """Save template with a new name"""
        template_id = self.template_id_edit.text().strip()
        if not template_id:
            QMessageBox.warning(self, "Error", "Please enter a template ID")
            return

        if CORE_AVAILABLE and self.template_manager.get_template_by_id(template_id):
            reply = QMessageBox.question(
                self, "Template Exists",
                f"Template '{template_id}' already exists. Overwrite?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self.template_id = template_id
        self._save_template()

        # Update window title
        template_name = self.template_name_edit.text() or template_id
        self.setWindowTitle(f"Template Editor - {template_name}")

    def _create_metadata_from_properties(self):
        """Create template metadata from property fields"""
        if not CORE_AVAILABLE:
            # Return a simple dict if core not available
            return type('Metadata', (), {
                'id': self.template_id_edit.text(),
                'name': self.template_name_edit.text(),
                'description': self.template_description_edit.toPlainText(),
                'template_file': f"pages/{self.template_id}.html",
                '__dict__': {
                    'id': self.template_id_edit.text(),
                    'name': self.template_name_edit.text(),
                    'description': self.template_description_edit.toPlainText(),
                    'type': self.template_type_combo.currentText(),
                    'version': self.template_version_edit.text(),
                    'template_file': f"pages/{self.template_id}.html"
                }
            })()

        from datetime import datetime

        return TemplateMetadata(
            id=self.template_id_edit.text(),
            name=self.template_name_edit.text(),
            description=self.template_description_edit.toPlainText(),
            type=TemplateType(self.template_type_combo.currentText()),
            variant=TemplateVariant.CUSTOM,
            version=self.template_version_edit.text(),
            author="Template Editor User",
            created_date=datetime.now().strftime('%Y-%m-%d'),
            last_modified=datetime.now().strftime('%Y-%m-%d'),
            preview_image=f"previews/{self.template_id}_preview.png",
            template_file=f"pages/{self.template_id}.html",
            required_data=[],
            optional_data=[],
            features=[],
            compatibility={"min_version": "2.0.0"}
        )

    def _create_backup(self):
        """Create a manual backup"""
        if not self.template_id:
            QMessageBox.warning(self, "No Template", "Please save the template first")
            return

        if not CORE_AVAILABLE or not self.backup_manager:
            QMessageBox.warning(self, "Error", "Backup system not available")
            return

        try:
            metadata = self._create_metadata_from_properties()
            backup_id = self.backup_manager.create_backup(
                template_id=self.template_id,
                template_content=self.current_template_content,
                template_metadata=metadata.__dict__,
                backup_type="manual",
                description="Manual backup from simple editor"
            )

            QMessageBox.information(self, "Backup Created", f"Backup created: {backup_id}")

        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Error creating backup:\n{str(e)}")

    def _create_automatic_backup(self):
        """Create automatic backup before saving"""
        if not self.template_id or not self.backup_manager:
            return

        try:
            metadata = self._create_metadata_from_properties()
            self.backup_manager.create_backup(
                template_id=self.template_id,
                template_content=self.current_template_content,
                template_metadata=metadata.__dict__,
                backup_type="pre_edit",
                description="Automatic backup before save"
            )
        except Exception as e:
            print(f"Warning: Could not create automatic backup: {e}")

    def closeEvent(self, event):
        """Handle close event"""
        if self.is_modified:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Save before closing?",
                QMessageBox.StandardButton.Save |
                QMessageBox.StandardButton.Discard |
                QMessageBox.StandardButton.Cancel
            )

            if reply == QMessageBox.StandardButton.Save:
                self._save_template()
                event.accept()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()