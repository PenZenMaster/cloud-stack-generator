"""
Template Editor Dialog - WYSIWYG Template Editor
Path: E:/projects/cloud-stack-generator/src/ui/dialogs/template_editor_dialog.py

Description:
WYSIWYG editor for creating and modifying website templates.
Provides visual editing capabilities with live preview and validation.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-22

Last Modified Date:
2025-09-22

Comments:
* v1.00 - Initial WYSIWYG template editor implementation
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QTextEdit, QScrollArea, QSplitter, QGroupBox, QMessageBox,
    QTabWidget, QWidget, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QTreeWidget, QTreeWidgetItem, QToolBar,
    QMenuBar, QStatusBar, QProgressBar, QInputDialog
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QFont, QAction, QTextCharFormat,
    QColor, QSyntaxHighlighter, QTextDocument, QKeySequence
)
# Try to import QWebEngineView, fall back to QTextEdit if not available
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    print("QtWebEngineWidgets not available, using QTextEdit for preview")
    QWebEngineView = None
    WEBENGINE_AVAILABLE = False

from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import tempfile
import json
import re
import sys

# Add the src directory to the Python path for imports
src_path = str(Path(__file__).parent.parent.parent)
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from core.templates.template_manager import TemplateManager, TemplateType, TemplateMetadata, TemplateVariant
from core.templates.template_preview import TemplatePreviewGenerator
from core.templates.backup_manager import TemplateBackupManager

# Import enhanced error handling
try:
    from ...utils import get_error_handler, handle_errors, safe_operation, log_ui_error
    from ...utils.error_classification import classify_and_handle_error
    ERROR_HANDLING_AVAILABLE = True
except ImportError:
    print("Enhanced error handling not available")
    ERROR_HANDLING_AVAILABLE = False

# Try to import backup selection dialog
try:
    from .backup_selection_dialog import BackupSelectionDialog
    BACKUP_DIALOG_AVAILABLE = True
except ImportError:
    print("BackupSelectionDialog not available")
    BackupSelectionDialog = None
    BACKUP_DIALOG_AVAILABLE = False


class TemplateEditorDialog(QDialog):
    """WYSIWYG Template Editor Dialog"""

    # Signals
    template_saved = pyqtSignal(str)  # template_id
    template_created = pyqtSignal(str)  # template_id
    preview_updated = pyqtSignal()

    def __init__(self, parent=None, template_id: Optional[str] = None):
        super().__init__(parent)
        self.template_id = template_id
        self.template_manager = TemplateManager()
        self.preview_generator = TemplatePreviewGenerator(self.template_manager)
        self.backup_manager = TemplateBackupManager(self.template_manager.templates_dir)
        self.current_template_content = ""
        self.is_modified = False
        self.backup_content = ""

        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.start(30000)  # Auto-save every 30 seconds

        self._setup_ui()
        self._load_template()
        self._connect_signals()

    def _setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Template Editor - WYSIWYG")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)

        # Main layout
        main_layout = QVBoxLayout(self)

        # Menu bar
        self._create_menu_bar(main_layout)

        # Toolbar
        self._create_toolbar(main_layout)

        # Main content area with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - Editor and properties
        left_panel = self._create_left_panel()
        splitter.addWidget(left_panel)

        # Right panel - Live preview
        right_panel = self._create_right_panel()
        splitter.addWidget(right_panel)

        # Set splitter proportions (60% left, 40% right)
        splitter.setSizes([960, 640])

        # Status bar
        self._create_status_bar(main_layout)

    def _create_menu_bar(self, parent_layout: QVBoxLayout):
        """Create the menu bar"""
        menu_bar = QMenuBar()
        parent_layout.addWidget(menu_bar)

        # File menu
        file_menu = menu_bar.addMenu("File")

        new_action = QAction("New Template", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_template)
        file_menu.addAction(new_action)

        open_action = QAction("Open Template", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_template)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_template)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_template_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("Export Template", self)
        export_action.triggered.connect(self._export_template)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        backup_action = QAction("Create Backup", self)
        backup_action.triggered.connect(self._create_backup)
        file_menu.addAction(backup_action)

        restore_action = QAction("Restore from Backup", self)
        restore_action.triggered.connect(self._restore_backup)
        file_menu.addAction(restore_action)

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")

        undo_action = QAction("Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)

        redo_action = QAction("Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)

        edit_menu.addSeparator()

        find_action = QAction("Find/Replace", self)
        find_action.setShortcut(QKeySequence.StandardKey.Find)
        find_action.triggered.connect(self._show_find_replace)
        edit_menu.addAction(find_action)

        # View menu
        view_menu = menu_bar.addMenu("View")

        preview_action = QAction("Refresh Preview", self)
        preview_action.setShortcut(QKeySequence("F5"))
        preview_action.triggered.connect(self._refresh_preview)
        view_menu.addAction(preview_action)

        # Tools menu
        tools_menu = menu_bar.addMenu("Tools")

        validate_action = QAction("Validate Template", self)
        validate_action.triggered.connect(self._validate_template)
        tools_menu.addAction(validate_action)

        format_action = QAction("Format Code", self)
        format_action.triggered.connect(self._format_code)
        tools_menu.addAction(format_action)

    def _create_toolbar(self, parent_layout: QVBoxLayout):
        """Create the toolbar"""
        toolbar = QToolBar()
        parent_layout.addWidget(toolbar)

        # Save button
        save_btn = QPushButton("Save")
        save_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogSaveButton))
        save_btn.clicked.connect(self._save_template)
        toolbar.addWidget(save_btn)

        toolbar.addSeparator()

        # Undo/Redo
        undo_btn = QPushButton("Undo")
        undo_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowLeft))
        undo_btn.clicked.connect(self._undo)
        toolbar.addWidget(undo_btn)

        redo_btn = QPushButton("Redo")
        redo_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_ArrowRight))
        redo_btn.clicked.connect(self._redo)
        toolbar.addWidget(redo_btn)

        toolbar.addSeparator()

        # Preview refresh
        refresh_btn = QPushButton("Refresh Preview")
        refresh_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_BrowserReload))
        refresh_btn.clicked.connect(self._refresh_preview)
        toolbar.addWidget(refresh_btn)

        # Validate
        validate_btn = QPushButton("Validate")
        validate_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_DialogApplyButton))
        validate_btn.clicked.connect(self._validate_template)
        toolbar.addWidget(validate_btn)

    def _create_left_panel(self) -> QWidget:
        """Create the left panel with editor and properties"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Tab widget for different editing modes
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # HTML Editor tab
        self.html_editor = self._create_html_editor()
        tab_widget.addTab(self.html_editor, "HTML Editor")

        # Template Properties tab
        properties_widget = self._create_properties_tab()
        tab_widget.addTab(properties_widget, "Properties")

        # Data Mapping tab
        data_mapping_widget = self._create_data_mapping_tab()
        tab_widget.addTab(data_mapping_widget, "Data Mapping")

        return panel

    def _create_html_editor(self) -> QWidget:
        """Create the HTML editor with syntax highlighting"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Editor controls
        controls_layout = QHBoxLayout()

        # Line numbers checkbox
        self.show_line_numbers = QCheckBox("Line Numbers")
        self.show_line_numbers.setChecked(True)
        self.show_line_numbers.toggled.connect(self._toggle_line_numbers)
        controls_layout.addWidget(self.show_line_numbers)

        # Word wrap checkbox
        self.word_wrap = QCheckBox("Word Wrap")
        self.word_wrap.setChecked(False)
        self.word_wrap.toggled.connect(self._toggle_word_wrap)
        controls_layout.addWidget(self.word_wrap)

        # Font size
        controls_layout.addWidget(QLabel("Font Size:"))
        self.font_size_spinner = QSpinBox()
        self.font_size_spinner.setRange(8, 24)
        self.font_size_spinner.setValue(12)
        self.font_size_spinner.valueChanged.connect(self._change_font_size)
        controls_layout.addWidget(self.font_size_spinner)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # HTML editor
        self.html_text_edit = QTextEdit()
        self.html_text_edit.setFont(QFont("Consolas", 12))
        self.html_text_edit.textChanged.connect(self._on_content_changed)
        layout.addWidget(self.html_text_edit)

        # Add syntax highlighting
        self.html_highlighter = HTMLSyntaxHighlighter(self.html_text_edit.document())

        return widget

    def _create_properties_tab(self) -> QWidget:
        """Create the template properties tab"""
        widget = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)

        # Template metadata
        metadata_group = QGroupBox("Template Metadata")
        metadata_layout = QGridLayout()

        # Template ID
        metadata_layout.addWidget(QLabel("Template ID:"), 0, 0)
        self.template_id_edit = QLineEdit()
        metadata_layout.addWidget(self.template_id_edit, 0, 1)

        # Template name
        metadata_layout.addWidget(QLabel("Name:"), 1, 0)
        self.template_name_edit = QLineEdit()
        metadata_layout.addWidget(self.template_name_edit, 1, 1)

        # Description
        metadata_layout.addWidget(QLabel("Description:"), 2, 0)
        self.template_description_edit = QTextEdit()
        self.template_description_edit.setMaximumHeight(80)
        metadata_layout.addWidget(self.template_description_edit, 2, 1)

        # Type
        metadata_layout.addWidget(QLabel("Type:"), 3, 0)
        self.template_type_combo = QComboBox()
        self.template_type_combo.addItems([t.value for t in TemplateType])
        metadata_layout.addWidget(self.template_type_combo, 3, 1)

        # Version
        metadata_layout.addWidget(QLabel("Version:"), 4, 0)
        self.template_version_edit = QLineEdit()
        metadata_layout.addWidget(self.template_version_edit, 4, 1)

        # Author
        metadata_layout.addWidget(QLabel("Author:"), 5, 0)
        self.template_author_edit = QLineEdit()
        metadata_layout.addWidget(self.template_author_edit, 5, 1)

        metadata_group.setLayout(metadata_layout)
        layout.addWidget(metadata_group)

        # Features
        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout()

        self.features_list = QTreeWidget()
        self.features_list.setHeaderLabels(["Feature", "Enabled"])
        self._populate_features_list()
        features_layout.addWidget(self.features_list)

        features_group.setLayout(features_layout)
        layout.addWidget(features_group)

        layout.addStretch()
        widget.setWidget(content)
        widget.setWidgetResizable(True)

        return widget

    def _create_data_mapping_tab(self) -> QWidget:
        """Create the data mapping configuration tab"""
        widget = QScrollArea()
        content = QWidget()
        layout = QVBoxLayout(content)

        # Required data fields
        required_group = QGroupBox("Required Data Fields")
        required_layout = QVBoxLayout()

        self.required_fields_list = QTreeWidget()
        self.required_fields_list.setHeaderLabels(["Field Path", "Description"])
        required_layout.addWidget(self.required_fields_list)

        # Buttons for required fields
        required_buttons = QHBoxLayout()
        add_required_btn = QPushButton("Add Required")
        add_required_btn.clicked.connect(self._add_required_field)
        required_buttons.addWidget(add_required_btn)

        remove_required_btn = QPushButton("Remove")
        remove_required_btn.clicked.connect(self._remove_required_field)
        required_buttons.addWidget(remove_required_btn)

        required_buttons.addStretch()
        required_layout.addLayout(required_buttons)
        required_group.setLayout(required_layout)
        layout.addWidget(required_group)

        # Optional data fields
        optional_group = QGroupBox("Optional Data Fields")
        optional_layout = QVBoxLayout()

        self.optional_fields_list = QTreeWidget()
        self.optional_fields_list.setHeaderLabels(["Field Path", "Description"])
        optional_layout.addWidget(self.optional_fields_list)

        # Buttons for optional fields
        optional_buttons = QHBoxLayout()
        add_optional_btn = QPushButton("Add Optional")
        add_optional_btn.clicked.connect(self._add_optional_field)
        optional_buttons.addWidget(add_optional_btn)

        remove_optional_btn = QPushButton("Remove")
        remove_optional_btn.clicked.connect(self._remove_optional_field)
        optional_buttons.addWidget(remove_optional_btn)

        optional_buttons.addStretch()
        optional_layout.addLayout(optional_buttons)
        optional_group.setLayout(optional_layout)
        layout.addWidget(optional_group)

        layout.addStretch()
        widget.setWidget(content)
        widget.setWidgetResizable(True)

        return widget

    def _create_right_panel(self) -> QWidget:
        """Create the right panel with live preview"""
        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Preview controls
        controls_layout = QHBoxLayout()

        # Preview mode selector
        controls_layout.addWidget(QLabel("Preview Mode:"))
        self.preview_mode_combo = QComboBox()
        self.preview_mode_combo.addItems(["Desktop", "Tablet", "Mobile"])
        self.preview_mode_combo.currentTextChanged.connect(self._change_preview_mode)
        controls_layout.addWidget(self.preview_mode_combo)

        # Auto-refresh checkbox
        self.auto_refresh = QCheckBox("Auto Refresh")
        self.auto_refresh.setChecked(True)
        controls_layout.addWidget(self.auto_refresh)

        controls_layout.addStretch()

        # Manual refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self._refresh_preview)
        controls_layout.addWidget(refresh_btn)

        layout.addLayout(controls_layout)

        # Web view for preview (fallback to QTextEdit if WebEngine not available)
        if WEBENGINE_AVAILABLE:
            self.preview_web_view = QWebEngineView()
            self.preview_web_view.setMinimumHeight(400)
        else:
            self.preview_web_view = QTextEdit()
            self.preview_web_view.setMinimumHeight(400)
            self.preview_web_view.setReadOnly(True)
            self.preview_web_view.setPlaceholderText("HTML preview will be shown here...\n(WebEngine not available, showing raw HTML)")

        layout.addWidget(self.preview_web_view)

        return panel

    def _create_status_bar(self, parent_layout: QVBoxLayout):
        """Create the status bar"""
        self.status_bar = QStatusBar()
        parent_layout.addWidget(self.status_bar)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Modified indicator
        self.modified_label = QLabel("")
        self.status_bar.addPermanentWidget(self.modified_label)

    def _populate_features_list(self):
        """Populate the features list with common template features"""
        features = [
            ("SEO Optimization", "Advanced search engine optimization features"),
            ("Schema Markup", "Structured data for search engines"),
            ("Responsive Design", "Mobile-first responsive layout"),
            ("Social Media Tags", "Open Graph and Twitter Card meta tags"),
            ("Local Business", "Local business information integration"),
            ("Google Maps", "Google Maps integration support"),
            ("Wikipedia", "Wikipedia content integration"),
            ("FAQ Support", "Frequently asked questions sections"),
            ("Image Gallery", "Image gallery and slideshow support"),
            ("Contact Forms", "Contact form integration"),
            ("Analytics", "Google Analytics integration"),
            ("Performance", "Performance optimization features")
        ]

        for feature_name, description in features:
            item = QTreeWidgetItem([feature_name, ""])
            item.setData(1, Qt.ItemDataRole.UserRole, description)
            item.setCheckState(1, Qt.CheckState.Unchecked)
            self.features_list.addTopLevelItem(item)

    def _connect_signals(self):
        """Connect all UI signals"""
        # Connect property changes to modification tracking
        self.template_id_edit.textChanged.connect(self._on_property_changed)
        self.template_name_edit.textChanged.connect(self._on_property_changed)
        self.template_description_edit.textChanged.connect(self._on_property_changed)
        self.template_type_combo.currentTextChanged.connect(self._on_property_changed)
        self.template_version_edit.textChanged.connect(self._on_property_changed)
        self.template_author_edit.textChanged.connect(self._on_property_changed)

    def _load_template(self):
        """Load template if template_id is provided"""
        if not self.template_id:
            self._new_template()
            return

        metadata = self.template_manager.get_template_by_id(self.template_id)
        if not metadata:
            QMessageBox.warning(self, "Error", f"Template {self.template_id} not found")
            self._new_template()
            return

        # Load template content
        template_obj = self.template_manager.load_template(self.template_id)
        if template_obj:
            # Get the raw template source
            template_path = self.template_manager.templates_dir / metadata.template_file
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    self.current_template_content = f.read()
                    self.html_text_edit.setPlainText(self.current_template_content)
                    self.backup_content = self.current_template_content

        # Load metadata into properties
        self._load_template_properties(metadata)

        # Update window title
        self.setWindowTitle(f"Template Editor - {metadata.name}")

        # Generate initial preview
        self._refresh_preview()

    def _load_template_properties(self, metadata: TemplateMetadata):
        """Load template metadata into property fields"""
        self.template_id_edit.setText(metadata.id)
        self.template_name_edit.setText(metadata.name)
        self.template_description_edit.setPlainText(metadata.description)
        self.template_type_combo.setCurrentText(metadata.type.value)
        self.template_version_edit.setText(metadata.version)
        self.template_author_edit.setText(metadata.author)

        # Load features
        for i in range(self.features_list.topLevelItemCount()):
            item = self.features_list.topLevelItem(i)
            feature_name = item.text(0)
            is_enabled = any(feature_name.lower() in f.lower() for f in metadata.features)
            item.setCheckState(1, Qt.CheckState.Checked if is_enabled else Qt.CheckState.Unchecked)

        # Load data fields
        self._load_data_fields(metadata.required_data, self.required_fields_list)
        self._load_data_fields(metadata.optional_data, self.optional_fields_list)

    def _load_data_fields(self, fields: List[str], tree_widget: QTreeWidget):
        """Load data fields into a tree widget"""
        tree_widget.clear()
        for field in fields:
            item = QTreeWidgetItem([field, f"Data field: {field}"])
            tree_widget.addTopLevelItem(item)

    def _new_template(self):
        """Create a new template"""
        self.template_id = None
        self.current_template_content = self._get_default_template_content()
        self.html_text_edit.setPlainText(self.current_template_content)
        self.backup_content = self.current_template_content

        # Clear properties
        self.template_id_edit.clear()
        self.template_name_edit.setText("New Template")
        self.template_description_edit.clear()
        self.template_type_combo.setCurrentIndex(0)
        self.template_version_edit.setText("1.00")
        self.template_author_edit.setText("Cloud Stack Generator Team")

        # Clear features
        for i in range(self.features_list.topLevelItemCount()):
            item = self.features_list.topLevelItem(i)
            item.setCheckState(1, Qt.CheckState.Unchecked)

        # Clear data fields
        self.required_fields_list.clear()
        self.optional_fields_list.clear()

        self.setWindowTitle("Template Editor - New Template")
        self.is_modified = False
        self._update_modified_indicator()

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
            <p>{{ page_content | default('Your content goes here. This is a template that you can customize.') }}</p>
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
        if not hasattr(self, 'is_loading') or not self.is_loading:
            self.current_template_content = self.html_text_edit.toPlainText()
            self.is_modified = True
            self._update_modified_indicator()

            # Auto-refresh preview if enabled
            if hasattr(self, 'auto_refresh') and self.auto_refresh.isChecked():
                self._refresh_preview_delayed()

    def _on_property_changed(self):
        """Handle property changes"""
        if not hasattr(self, 'is_loading') or not self.is_loading:
            self.is_modified = True
            self._update_modified_indicator()

    def _update_modified_indicator(self):
        """Update the modified indicator in status bar"""
        if self.is_modified:
            self.modified_label.setText("Modified")
            self.modified_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.modified_label.setText("Saved")
            self.modified_label.setStyleSheet("color: green;")

    def _refresh_preview_delayed(self):
        """Refresh preview with a small delay to avoid too frequent updates"""
        if hasattr(self, 'preview_timer'):
            self.preview_timer.stop()
        else:
            self.preview_timer = QTimer()
            self.preview_timer.timeout.connect(self._refresh_preview)
            self.preview_timer.setSingleShot(True)

        self.preview_timer.start(500)  # 500ms delay

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
            except:
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
        """Refresh the live preview"""
        try:
            self.status_label.setText("Generating preview...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress

            # Generate sample data for preview
            sample_data = self._generate_sample_data()

            # Render template with sample data
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

            rendered_html = template.render(**sample_data)

            # Inject responsive CSS if available
            if hasattr(self, 'responsive_css'):
                # Insert the responsive CSS right after the <head> tag
                if '<head>' in rendered_html:
                    rendered_html = rendered_html.replace('<head>', f'<head>\n{self.responsive_css}')

            # Add preview-specific styling
            preview_css = """
            <style id="preview-enhancements">
            /* Preview mode indicator */
            body::before {
                content: "Preview Mode - """ + self.preview_mode_combo.currentText() + """";
                position: fixed;
                top: 0;
                right: 0;
                background: rgba(0,0,0,0.8);
                color: white;
                padding: 5px 10px;
                font-size: 12px;
                z-index: 9999;
                border-bottom-left-radius: 5px;
            }

            /* Highlight template variables in preview */
            .template-variable {
                background-color: #ffffcc;
                border: 1px dashed #ccc;
                padding: 2px;
            }
            </style>
            """

            if '<head>' in rendered_html:
                rendered_html = rendered_html.replace('<head>', f'<head>\n{preview_css}')

            # Create temporary file for preview
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(rendered_html)
            temp_file.close()

            # Load in web view or text edit
            if WEBENGINE_AVAILABLE and hasattr(self.preview_web_view, 'load'):
                self.preview_web_view.load(f"file:///{temp_file.name}")
            else:
                # Fallback: show raw HTML in text edit
                self.preview_web_view.setHtml(rendered_html)

            self.status_label.setText("Preview updated")
            self.progress_bar.setVisible(False)

        except Exception as e:
            self.status_label.setText(f"Preview generation failed: {str(e)}")
            self.progress_bar.setVisible(False)

            # Use proper error classification for preview errors
            if ERROR_HANDLING_AVAILABLE:
                classification = classify_and_handle_error(
                    exception=e,
                    context="Preview generation",
                    user_action="Generating template preview",
                    component="TemplateEditor"
                )

                # Log the warning (previews are non-critical)
                log_ui_error(
                    widget_name="TemplateEditorDialog",
                    action="generate_preview",
                    error=e,
                    user_action="Generating template preview"
                )

                # Show appropriate dialog with correct icon
                msg_box = QMessageBox(self)
                msg_box.setIcon(classification.dialog_icon)
                msg_box.setWindowTitle(classification.title)
                msg_box.setText(classification.message)
                msg_box.setInformativeText(classification.user_action_suggestion)
                msg_box.setDetailedText(f"Technical details: {classification.technical_details}")
                msg_box.exec()
            else:
                QMessageBox.warning(self, "Preview Warning", f"Unable to generate preview:\n{str(e)}")

    def _generate_sample_data(self) -> Dict[str, Any]:
        """Generate sample data for preview"""
        return {
            'page_title': 'Sample Page Title',
            'meta_description': 'This is a sample meta description for the preview.',
            'page_heading': 'Welcome to Our Sample Page',
            'page_content': 'This is sample content to demonstrate how your template will look with real data.',
            'page_url': 'https://example.com/sample-page',
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
                'business_name': 'Sample Business Name',
                'tagline': 'Your trusted local service provider',
                'description': 'We provide excellent services to our local community.',
                'legal_name': 'Sample Business LLC',
                'founded_year': '2020',
                'industry': 'Professional Services',
                'service_overview': 'Comprehensive service solutions for your business needs.',
                'domain': 'https://samplebusiness.com'
            },
            'contact': {
                'phone': '(555) 123-4567',
                'email': 'info@samplebusiness.com',
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
                'title': 'Sample City Services - Sample Business',
                'meta_description': 'Professional services in Sample City. Contact Sample Business for reliable local solutions.',
                'city_name': 'Sample City',
                'state': 'Sample State',
                'primary_keyword': 'sample services Sample City',
                'secondary_keywords': ['local business', 'professional services', 'Sample City contractor'],
                'hero_title': 'Professional Services in Sample City',
                'about_city': 'Sample City is a vibrant community where we proudly serve local residents with quality services.',
                'seo_content_body': 'Our team has been serving the Sample City area for years, providing reliable and professional services to local residents and businesses.',
                'city_image': {
                    'image_url': 'https://via.placeholder.com/800x400/007bff/ffffff?text=Sample+City',
                    'alt_text': 'Beautiful view of Sample City',
                    'caption': 'Sample City - Our service area',
                    'embed_code': '<div class="sample-image"><img src="https://via.placeholder.com/800x400/007bff/ffffff?text=Sample+City" alt="Sample City" /></div>'
                },
                'places_of_interest': [
                    {
                        'name': 'Sample City Park',
                        'description': 'Beautiful downtown park perfect for families',
                        'google_maps_embed': '<iframe src="https://www.google.com/maps/embed" width="300" height="200"></iframe>'
                    },
                    {
                        'name': 'Sample Historical Museum',
                        'description': 'Learn about our city\'s rich history',
                        'google_maps_embed': '<iframe src="https://www.google.com/maps/embed" width="300" height="200"></iframe>'
                    },
                    {
                        'name': 'Sample Shopping Center',
                        'description': 'Local shopping and dining destination',
                        'google_maps_embed': '<iframe src="https://www.google.com/maps/embed" width="300" height="200"></iframe>'
                    }
                ],
                'city_faq': [
                    {
                        'question': 'What services do you provide in Sample City?',
                        'answer': 'We provide comprehensive professional services throughout the Sample City area, including residential and commercial solutions.'
                    },
                    {
                        'question': 'Do you serve areas outside Sample City?',
                        'answer': 'Yes, we serve Sample City and surrounding communities within a 25-mile radius.'
                    },
                    {
                        'question': 'How long have you been serving Sample City?',
                        'answer': 'We have been proudly serving the Sample City community since 2020.'
                    },
                    {
                        'question': 'What makes your Sample City services special?',
                        'answer': 'Our local expertise, community commitment, and personalized service approach set us apart in Sample City.'
                    },
                    {
                        'question': 'How can I get a quote for services in Sample City?',
                        'answer': 'Contact us today for a free consultation and quote for your Sample City project.'
                    }
                ]
            },
            'services': [
                {
                    'name': 'Professional Service A',
                    'description': 'High-quality service tailored to your needs',
                    'features': ['Expert technicians', 'Quality guarantee', 'Local service']
                },
                {
                    'name': 'Professional Service B',
                    'description': 'Comprehensive solutions for your requirements',
                    'features': ['Fast response', 'Competitive pricing', 'Satisfaction guaranteed']
                }
            ],
            'products': [
                {
                    'name': 'Sample Product 1',
                    'description': 'Quality product for your needs',
                    'price': '$99.99'
                },
                {
                    'name': 'Sample Product 2',
                    'description': 'Professional-grade solution',
                    'price': '$149.99'
                }
            ]
        }

    def _save_template(self):
        """Save the current template"""
        if not self.template_id:
            self._save_template_as()
            return

        try:
            # Validate before saving
            is_valid, errors = self._validate_current_template()
            if not is_valid:
                reply = QMessageBox.question(
                    self, "Validation Errors",
                    "Template has validation errors:\n\n" + "\n".join(errors) +
                    "\n\nSave anyway?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            # Create automatic backup before saving
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
            metadata_path = template_path.with_suffix('.template.json')
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.__dict__, f, indent=2, default=str)

            self.is_modified = False
            self._update_modified_indicator()
            self.status_label.setText("Template saved successfully")

            # Emit signal
            self.template_saved.emit(self.template_id)

        except Exception as e:
            # Log error with enhanced error handler
            if ERROR_HANDLING_AVAILABLE:
                log_ui_error(
                    widget_name="TemplateEditorDialog",
                    action="save_template",
                    error=e,
                    user_action="Saving template"
                )

            QMessageBox.critical(self, "Save Error", f"Error saving template:\n{str(e)}")
            self.status_label.setText(f"Save failed: {str(e)}")

    def _save_template_as(self):
        """Save template with a new name"""
        # Get new template ID
        template_id = self.template_id_edit.text().strip()
        if not template_id:
            QMessageBox.warning(self, "Error", "Please enter a template ID")
            return

        # Check if template already exists
        if self.template_manager.get_template_by_id(template_id):
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

    def _create_metadata_from_properties(self) -> TemplateMetadata:
        """Create template metadata from property fields"""
        from datetime import datetime

        # Get enabled features
        features = []
        for i in range(self.features_list.topLevelItemCount()):
            item = self.features_list.topLevelItem(i)
            if item.checkState(1) == Qt.CheckState.Checked:
                features.append(item.text(0))

        # Get data fields
        required_data = []
        for i in range(self.required_fields_list.topLevelItemCount()):
            item = self.required_fields_list.topLevelItem(i)
            required_data.append(item.text(0))

        optional_data = []
        for i in range(self.optional_fields_list.topLevelItemCount()):
            item = self.optional_fields_list.topLevelItem(i)
            optional_data.append(item.text(0))

        # Determine template file path
        template_type = TemplateType(self.template_type_combo.currentText())
        template_file = f"pages/{self.template_id}.html"

        return TemplateMetadata(
            id=self.template_id_edit.text(),
            name=self.template_name_edit.text(),
            description=self.template_description_edit.toPlainText(),
            type=template_type,
            variant=TemplateVariant.CUSTOM,  # Default to custom for user-created templates
            version=self.template_version_edit.text(),
            author=self.template_author_edit.text(),
            created_date=datetime.now().strftime('%Y-%m-%d'),
            last_modified=datetime.now().strftime('%Y-%m-%d'),
            preview_image=f"previews/{self.template_id}_preview.png",
            template_file=template_file,
            required_data=required_data,
            optional_data=optional_data,
            features=features,
            compatibility={
                "min_version": "2.0.0",
                "supports_responsive_design": True
            }
        )

    def _validate_current_template(self) -> Tuple[bool, List[str]]:
        """Validate the current template"""
        errors = []

        # Check if template ID is provided
        if not self.template_id_edit.text().strip():
            errors.append("Template ID is required")

        # Check if template name is provided
        if not self.template_name_edit.text().strip():
            errors.append("Template name is required")

        # Try to parse as Jinja2 template
        try:
            from jinja2 import Environment, DictLoader
            # Use DictLoader to avoid "no loader specified" warning
            env = Environment(loader=DictLoader({}))
            template = env.from_string(self.current_template_content)
        except Exception as e:
            errors.append(f"Jinja2 template syntax error: {str(e)}")

        # Check for basic HTML structure
        if '<!DOCTYPE html>' not in self.current_template_content:
            errors.append("Template should include DOCTYPE declaration")

        if '<html' not in self.current_template_content:
            errors.append("Template should include HTML element")

        if '<head>' not in self.current_template_content:
            errors.append("Template should include HEAD section")

        if '<body>' not in self.current_template_content:
            errors.append("Template should include BODY section")

        return len(errors) == 0, errors

    def _create_backup(self):
        """Create a manual backup of the current template"""
        if not self.template_id:
            QMessageBox.warning(self, "No Template", "Please save the template first before creating a backup.")
            return

        try:
            # Get current metadata
            metadata = self._create_metadata_from_properties()

            # Create backup
            backup_id = self.backup_manager.create_backup(
                template_id=self.template_id,
                template_content=self.current_template_content,
                template_metadata=metadata.__dict__,
                backup_type="manual",
                description="Manual backup created from template editor"
            )

            QMessageBox.information(
                self,
                "Backup Created",
                f"Backup created successfully!\n\nBackup ID: {backup_id}\n\n"
                f"You can restore this backup later using the 'Restore from Backup' option."
            )

        except Exception as e:
            QMessageBox.critical(self, "Backup Error", f"Error creating backup:\n{str(e)}")

    def _create_automatic_backup(self):
        """Create an automatic backup before saving"""
        if not self.template_id:
            return

        try:
            # Get current metadata
            metadata = self._create_metadata_from_properties()

            # Create pre-edit backup
            self.backup_manager.create_backup(
                template_id=self.template_id,
                template_content=self.backup_content,  # Use the original content
                template_metadata=metadata.__dict__,
                backup_type="pre_edit",
                description="Automatic backup before save"
            )

        except Exception as e:
            print(f"Warning: Could not create automatic backup: {e}")
            # Don't fail the save operation if backup fails

    def _restore_backup(self):
        """Restore template from a backup"""
        if not self.template_id:
            QMessageBox.warning(self, "No Template", "Please select a template first.")
            return

        try:
            # Get available backups
            backups = self.backup_manager.get_backups(self.template_id)
            if not backups:
                QMessageBox.information(self, "No Backups", "No backups found for this template.")
                return

            # Show backup selection dialog or simple list
            if BACKUP_DIALOG_AVAILABLE:
                backup_dialog = BackupSelectionDialog(backups, self)
                if backup_dialog.exec() == QDialog.DialogCode.Accepted:
                    selected_backup = backup_dialog.get_selected_backup()
            else:
                # Fallback: simple selection using message box
                backup_names = [f"{backup.backup_id} ({backup.created_date})" for backup in backups]
                selected_text, ok = QInputDialog.getItem(
                    self, "Select Backup", "Choose a backup to restore:", backup_names, 0, False
                )
                selected_backup = None
                if ok and selected_text:
                    # Find the selected backup
                    for backup in backups:
                        if selected_text.startswith(backup.backup_id):
                            selected_backup = backup
                            break

            if selected_backup:
                    # Confirm restore
                    reply = QMessageBox.question(
                        self,
                        "Confirm Restore",
                        f"Are you sure you want to restore from backup?\n\n"
                        f"Backup: {selected_backup.backup_id}\n"
                        f"Created: {selected_backup.created_date}\n"
                        f"Description: {selected_backup.description}\n\n"
                        f"Current unsaved changes will be lost.",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )

                    if reply == QMessageBox.StandardButton.Yes:
                        # Restore the backup
                        content, metadata = self.backup_manager.restore_backup(selected_backup.backup_id)

                        # Update editor
                        self.is_loading = True
                        self.current_template_content = content
                        self.html_text_edit.setPlainText(content)

                        # Update properties if metadata available
                        if metadata:
                            self._load_template_properties_from_dict(metadata)

                        self.is_loading = False
                        self.is_modified = True
                        self._update_modified_indicator()

                        # Refresh preview
                        self._refresh_preview()

                        QMessageBox.information(self, "Restore Complete", "Template restored from backup successfully!")

        except Exception as e:
            QMessageBox.critical(self, "Restore Error", f"Error restoring backup:\n{str(e)}")

    def _load_template_properties_from_dict(self, metadata: Dict[str, Any]):
        """Load template metadata from dictionary"""
        self.template_id_edit.setText(metadata.get('id', ''))
        self.template_name_edit.setText(metadata.get('name', ''))
        self.template_description_edit.setPlainText(metadata.get('description', ''))
        self.template_version_edit.setText(metadata.get('version', '1.00'))
        self.template_author_edit.setText(metadata.get('author', ''))

    def _auto_save(self):
        """Auto-save functionality"""
        if self.is_modified and self.template_id:
            try:
                # Save to temporary backup
                temp_dir = Path(tempfile.gettempdir()) / "template_editor_autosave"
                temp_dir.mkdir(exist_ok=True)

                autosave_file = temp_dir / f"{self.template_id}_autosave.html"
                with open(autosave_file, 'w', encoding='utf-8') as f:
                    f.write(self.current_template_content)

                self.status_label.setText("Auto-saved")
            except Exception as e:
                print(f"Auto-save error: {e}")

    # Additional UI event handlers
    def _toggle_line_numbers(self, checked: bool):
        """Toggle line numbers display"""
        # This would require a custom editor widget with line numbers
        pass

    def _toggle_word_wrap(self, checked: bool):
        """Toggle word wrap in editor"""
        if checked:
            self.html_text_edit.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.html_text_edit.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)

    def _change_font_size(self, size: int):
        """Change editor font size"""
        font = self.html_text_edit.font()
        font.setPointSize(size)
        self.html_text_edit.setFont(font)

    def _change_preview_mode(self, mode: str):
        """Change preview mode (Desktop/Tablet/Mobile)"""
        # Adjust the preview web view size based on mode
        if mode == "Desktop":
            self.preview_web_view.setMinimumWidth(800)
            self.preview_web_view.setMaximumWidth(16777215)  # Remove max width constraint
            # Inject CSS for desktop view
            self._inject_responsive_css("desktop")
        elif mode == "Tablet":
            self.preview_web_view.setMinimumWidth(600)
            self.preview_web_view.setMaximumWidth(768)
            # Inject CSS for tablet view
            self._inject_responsive_css("tablet")
        elif mode == "Mobile":
            self.preview_web_view.setMinimumWidth(350)
            self.preview_web_view.setMaximumWidth(480)
            # Inject CSS for mobile view
            self._inject_responsive_css("mobile")

        # Refresh preview to apply new viewport
        self._refresh_preview()

    def _inject_responsive_css(self, device_type: str):
        """Inject CSS for responsive preview"""
        css_injection = """
        <style id="preview-responsive-css">
        """

        if device_type == "mobile":
            css_injection += """
            body { font-size: 14px !important; }
            .container { padding: 10px !important; max-width: 100% !important; }
            h1 { font-size: 1.8em !important; }
            h2 { font-size: 1.5em !important; }
            h3 { font-size: 1.3em !important; }
            .responsive-hide-mobile { display: none !important; }
            """
        elif device_type == "tablet":
            css_injection += """
            body { font-size: 15px !important; }
            .container { padding: 15px !important; max-width: 750px !important; }
            h1 { font-size: 2.2em !important; }
            h2 { font-size: 1.8em !important; }
            h3 { font-size: 1.5em !important; }
            .responsive-hide-tablet { display: none !important; }
            """
        else:  # desktop
            css_injection += """
            body { font-size: 16px !important; }
            .container { max-width: 1200px !important; }
            """

        css_injection += """
        </style>
        """

        # Store the CSS injection for later use in preview generation
        self.responsive_css = css_injection

    def _undo(self):
        """Undo last change"""
        self.html_text_edit.undo()

    def _redo(self):
        """Redo last undone change"""
        self.html_text_edit.redo()

    def _show_find_replace(self):
        """Show find/replace dialog"""
        # This would open a find/replace dialog
        pass

    def _validate_template(self):
        """Validate current template and show results"""
        is_valid, errors = self._validate_current_template()

        if is_valid:
            QMessageBox.information(self, "Validation", "Template is valid!")
        else:
            QMessageBox.warning(self, "Validation Errors",
                              "Template has the following errors:\n\n" + "\n".join(errors))

    def _format_code(self):
        """Format HTML code"""
        try:
            from bs4 import BeautifulSoup

            # Parse and format HTML
            soup = BeautifulSoup(self.current_template_content, 'html.parser')
            formatted_html = soup.prettify()

            self.html_text_edit.setPlainText(formatted_html)
            self.status_label.setText("Code formatted")

        except ImportError as e:
            # This is a configuration warning - missing dependency
            if ERROR_HANDLING_AVAILABLE:
                classification = classify_and_handle_error(
                    exception=e,
                    context="Format code operation",
                    user_action="Formatting template HTML",
                    component="TemplateEditor"
                )

                # Log the issue
                log_ui_error(
                    widget_name="TemplateEditorDialog",
                    action="format_code_missing_dependency",
                    error=e,
                    user_action="Formatting template code"
                )

                # Show appropriate dialog
                QMessageBox.warning(
                    self,
                    classification.title,
                    f"{classification.message}\n\n{classification.user_action_suggestion}"
                )
            else:
                QMessageBox.warning(self, "Configuration Warning", "BeautifulSoup4 is required for code formatting")

            self.status_label.setText("Code formatting unavailable - missing dependency")

        except Exception as e:
            # This is a template parsing error
            if ERROR_HANDLING_AVAILABLE:
                classification = classify_and_handle_error(
                    exception=e,
                    context="Format code operation",
                    user_action="Formatting template HTML",
                    component="TemplateEditor"
                )

                # Log the error
                log_ui_error(
                    widget_name="TemplateEditorDialog",
                    action="format_code_parsing_error",
                    error=e,
                    user_action="Formatting template code"
                )

                # Show appropriate dialog with correct icon
                msg_box = QMessageBox(self)
                msg_box.setIcon(classification.dialog_icon)
                msg_box.setWindowTitle(classification.title)
                msg_box.setText(classification.message)
                msg_box.setInformativeText(classification.user_action_suggestion)
                msg_box.setDetailedText(f"Technical details: {classification.technical_details}")
                msg_box.exec()
            else:
                QMessageBox.critical(self, "Template Error", f"Error formatting code: {str(e)}")

            self.status_label.setText(f"Code formatting failed: {str(e)}")

    def _open_template(self):
        """Open an existing template"""
        # This would show a template selection dialog
        pass

    def _export_template(self):
        """Export template as a package"""
        # This would export the template with metadata as a package
        pass

    def _add_required_field(self):
        """Add a required data field"""
        # This would show a dialog to add a new required field
        pass

    def _remove_required_field(self):
        """Remove selected required field"""
        current_item = self.required_fields_list.currentItem()
        if current_item:
            self.required_fields_list.takeTopLevelItem(
                self.required_fields_list.indexOfTopLevelItem(current_item)
            )
            self._on_property_changed()

    def _add_optional_field(self):
        """Add an optional data field"""
        # This would show a dialog to add a new optional field
        pass

    def _remove_optional_field(self):
        """Remove selected optional field"""
        current_item = self.optional_fields_list.currentItem()
        if current_item:
            self.optional_fields_list.takeTopLevelItem(
                self.optional_fields_list.indexOfTopLevelItem(current_item)
            )
            self._on_property_changed()

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


class HTMLSyntaxHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for HTML/Jinja2 templates"""

    def __init__(self, document: QTextDocument):
        super().__init__(document)
        self._setup_highlighting_rules()

    def _setup_highlighting_rules(self):
        """Setup syntax highlighting rules"""
        self.highlighting_rules = []

        # HTML tags
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#0000FF"))
        tag_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'<[!?/]?\b[A-Za-z0-9_-]+(?:\s[^>]*)?\/?>', tag_format))

        # HTML attributes
        attr_format = QTextCharFormat()
        attr_format.setForeground(QColor("#008000"))
        self.highlighting_rules.append((r'\b[A-Za-z0-9_-]+(?=\s*=)', attr_format))

        # Attribute values
        value_format = QTextCharFormat()
        value_format.setForeground(QColor("#FF0000"))
        self.highlighting_rules.append((r'"[^"]*"', value_format))
        self.highlighting_rules.append((r"'[^']*'", value_format))

        # Jinja2 template tags
        jinja_format = QTextCharFormat()
        jinja_format.setForeground(QColor("#800080"))
        jinja_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r'\{\{.*?\}\}', jinja_format))
        self.highlighting_rules.append((r'\{%.*?%\}', jinja_format))
        self.highlighting_rules.append((r'\{#.*?#\}', jinja_format))

        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#808080"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((r'<!--.*?-->', comment_format))

    def highlightBlock(self, text: str):
        """Apply syntax highlighting to a block of text"""
        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                start = match.start()
                length = match.end() - start
                self.setFormat(start, length, format)