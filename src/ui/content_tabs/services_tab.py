"""
Module/Script Name: Services Tab
Path: src/ui/content_tabs/services_tab.py

Description:
Services management tab with manual entry, categories, and pricing information.
Handles service catalog management with detailed descriptions.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-08-11

Last Modified Date:
2025-11-22

Comments:
* v1.00 - Initial services management tab
* v1.01 - Removed FAQ functionality (now in separate FAQ tab)
* v1.02 - Added CSV import/export functionality matching Products and FAQ tabs
"""

import csv
import os
import chardet
from typing import Dict, Any, List, Tuple, Optional
from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QMessageBox,
    QGroupBox,
    QComboBox,
    QTextEdit,
    QHeaderView,
    QAbstractItemView,
    QFrame,
    QProgressBar,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal
from ..components.base_tab import BaseTab
from core.config.models import FAQItem
from utils import log_file_operation_error


class ValidationResult:
    """Validation result container"""

    def __init__(self):
        self.is_valid = True
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, message: str):
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        self.warnings.append(message)


class Service:
    """Service data model"""

    def __init__(
        self,
        name: str = "",
        description: str = "",
        category: str = "",
        price_range: str = "",
        duration: str = "",
        features: Optional[List[str]] = None,
    ):
        self.name = name
        self.description = description
        self.category = category
        self.price_range = price_range
        self.duration = duration
        self.features = features or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "price_range": self.price_range,
            "duration": self.duration,
            "features": self.features,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Service":
        """Create from dictionary"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", ""),
            price_range=data.get("price_range", ""),
            duration=data.get("duration", ""),
            features=data.get("features", []),
        )

    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate service data"""
        errors = []
        if not self.name.strip():
            errors.append("Service name is required")
        if not self.description.strip():
            errors.append("Service description is required")
        if len(self.description) > 1000:
            errors.append("Description too long (max 1000 characters)")
        return len(errors) == 0, errors


class ServicesTab(BaseTab):
    """Tab for services management"""

    # Signals
    config_changed = pyqtSignal()
    validation_requested = pyqtSignal()
    data_loaded = pyqtSignal()

    # Service categories
    SERVICE_CATEGORIES = [
        "General Services",
        "Consulting",
        "Professional Services",
        "Technical Support",
        "Design Services",
        "Development",
        "Marketing",
        "Training",
        "Maintenance",
        "Installation",
        "Repair",
        "Custom Services",
    ]

    def __init__(self, parent=None):
        self.services: List[Service] = []
        self.has_changes = False
        self.current_file_path = ""
        super().__init__(parent)

    def setup_ui(self):
        """Setup services management UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Create services sections
        self._create_import_section(main_layout)
        self._create_services_table_section(main_layout)
        self._create_service_entry_section(main_layout)
        self._create_services_actions_section(main_layout)

        self.setLayout(main_layout)

    def _create_import_section(self, parent_layout: QVBoxLayout):
        """Create CSV import & export section"""
        # Section header
        header_label = self._create_section_header("CSV Import & Export")
        parent_layout.addWidget(header_label)

        # Import group
        import_group = QGroupBox()
        import_layout = QGridLayout()
        import_layout.setSpacing(10)

        # File selection
        file_label = QLabel("CSV File:")
        file_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Select CSV file to import services...")
        self.file_path_input.setReadOnly(True)

        self.browse_btn = QPushButton("Browse")
        self.browse_btn.clicked.connect(self._browse_csv_file)

        # Import controls
        self.import_btn = QPushButton("Import CSV")
        self.import_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """
        )
        self.import_btn.clicked.connect(self._import_csv)
        self.import_btn.setEnabled(False)

        self.validate_csv_btn = QPushButton("Validate CSV")
        self.validate_csv_btn.clicked.connect(self._validate_csv_file)
        self.validate_csv_btn.setEnabled(False)

        # Export controls
        self.export_btn = QPushButton("Export CSV")
        self.export_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        self.export_btn.clicked.connect(self._export_csv)

        # Layout file selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(self.browse_btn)

        # Layout buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.validate_csv_btn)
        buttons_layout.addWidget(self.import_btn)
        buttons_layout.addWidget(self.export_btn)
        buttons_layout.addStretch()

        # Status info
        self.import_status = QLabel("Ready to import services from CSV")
        self.import_status.setFont(QFont("Arial", 9))
        self.import_status.setStyleSheet("color: #7f8c8d; font-style: italic;")

        # Progress bar for import
        self.import_progress = QProgressBar()
        self.import_progress.hide()

        import_layout.addWidget(file_label, 0, 0)
        import_layout.addLayout(file_layout, 0, 1)
        import_layout.addLayout(buttons_layout, 1, 0, 1, 2)
        import_layout.addWidget(self.import_status, 2, 0, 1, 2)
        import_layout.addWidget(self.import_progress, 3, 0, 1, 2)

        import_group.setLayout(import_layout)
        parent_layout.addWidget(import_group)

    def _create_services_table_section(self, parent_layout: QVBoxLayout):
        """Create services table section"""
        # Section header
        header_label = self._create_section_header("Services Catalog")
        parent_layout.addWidget(header_label)

        # Table group
        table_group = QGroupBox()
        table_layout = QVBoxLayout()

        # Services count and search
        controls_layout = QHBoxLayout()

        self.services_count_label = QLabel("Services: 0")
        self.services_count_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        # Search functionality
        search_label = QLabel("Search:")
        self.services_search_input = QLineEdit()
        self.services_search_input.setPlaceholderText("Search by name or category...")
        self.services_search_input.setMaximumWidth(250)
        self.services_search_input.textChanged.connect(self._filter_services)

        controls_layout.addWidget(self.services_count_label)
        controls_layout.addStretch()
        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.services_search_input)

        # Services table
        self.services_table = QTableWidget()
        self.services_table.setColumnCount(
            6
        )  # Name, Category, Price, Duration, Description, Actions
        headers = [
            "Service Name",
            "Category",
            "Price Range",
            "Duration",
            "Description",
            "Actions",
        ]
        self.services_table.setHorizontalHeaderLabels(headers)

        # Table settings
        self.services_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.services_table.setAlternatingRowColors(True)
        self.services_table.setSortingEnabled(True)

        # Set column widths
        header = self.services_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(False)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Category
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Price
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Duration
            header.setSectionResizeMode(
                4, QHeaderView.ResizeMode.Stretch
            )  # Description
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Actions
        # Defensive: header is None, do nothing or log if needed

        self.services_table.setColumnWidth(1, 130)  # Category
        self.services_table.setColumnWidth(2, 100)  # Price
        self.services_table.setColumnWidth(3, 80)  # Duration
        self.services_table.setColumnWidth(5, 80)  # Actions

        table_layout.addLayout(controls_layout)
        table_layout.addWidget(self.services_table)

        table_group.setLayout(table_layout)
        parent_layout.addWidget(table_group)

    def _create_service_entry_section(self, parent_layout: QVBoxLayout):
        """Create service entry section"""
        # Section header
        header_label = self._create_section_header("Add/Edit Service")
        parent_layout.addWidget(header_label)

        # Entry group
        entry_group = QGroupBox()
        entry_layout = QGridLayout()
        entry_layout.setSpacing(10)

        # Service form fields
        self.service_inputs = {}

        # Row 1: Name and Category
        name_label = QLabel("* Service Name:")
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["name"] = QLineEdit()
        self.service_inputs["name"].setPlaceholderText("Enter service name")
        self.service_inputs["name"].textChanged.connect(self._emit_config_changed)

        category_label = QLabel("Category:")
        category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["category"] = QComboBox()
        self.service_inputs["category"].addItems(self.SERVICE_CATEGORIES)
        self.service_inputs["category"].setEditable(True)
        self.service_inputs["category"].currentTextChanged.connect(
            self._emit_config_changed
        )

        # Row 2: Price Range and Duration
        price_label = QLabel("Price Range:")
        price_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["price_range"] = QLineEdit()
        self.service_inputs["price_range"].setPlaceholderText(
            "$100-$500 or Contact for quote"
        )
        self.service_inputs["price_range"].textChanged.connect(
            self._emit_config_changed
        )

        duration_label = QLabel("Duration:")
        duration_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["duration"] = QLineEdit()
        self.service_inputs["duration"].setPlaceholderText("1-2 hours, 1 week, etc.")
        self.service_inputs["duration"].textChanged.connect(self._emit_config_changed)

        # Row 3: Description (spans all columns)
        desc_label = QLabel("* Description:")
        desc_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["description"] = QTextEdit()
        self.service_inputs["description"].setPlaceholderText(
            "Detailed service description (max 1000 characters)"
        )
        self.service_inputs["description"].setMaximumHeight(100)
        self.service_inputs["description"].textChanged.connect(
            self._emit_config_changed
        )

        # Character counter for description
        self.service_desc_counter = QLabel("0/1000")
        self.service_desc_counter.setFont(QFont("Arial", 8))
        self.service_desc_counter.setStyleSheet("color: #7f8c8d;")
        self.service_inputs["description"].textChanged.connect(
            self._update_service_description_counter
        )

        # Features section
        features_label = QLabel("Key Features:")
        features_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["features"] = QTextEdit()
        self.service_inputs["features"].setPlaceholderText(
            "Enter key features (one per line)"
        )
        self.service_inputs["features"].setMaximumHeight(80)
        self.service_inputs["features"].textChanged.connect(self._emit_config_changed)

        # Layout
        entry_layout.addWidget(name_label, 0, 0)
        entry_layout.addWidget(self.service_inputs["name"], 0, 1)
        entry_layout.addWidget(category_label, 0, 2)
        entry_layout.addWidget(self.service_inputs["category"], 0, 3)

        entry_layout.addWidget(price_label, 1, 0)
        entry_layout.addWidget(self.service_inputs["price_range"], 1, 1)
        entry_layout.addWidget(duration_label, 1, 2)
        entry_layout.addWidget(self.service_inputs["duration"], 1, 3)

        entry_layout.addWidget(desc_label, 2, 0)
        entry_layout.addWidget(self.service_inputs["description"], 2, 1, 1, 3)
        entry_layout.addWidget(
            self.service_desc_counter, 3, 3, Qt.AlignmentFlag.AlignRight
        )

        entry_layout.addWidget(features_label, 4, 0)
        entry_layout.addWidget(self.service_inputs["features"], 4, 1, 1, 3)

        # Action buttons
        actions_layout = QHBoxLayout()

        self.add_service_btn = QPushButton("Add Service")
        self.add_service_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """
        )
        self.add_service_btn.clicked.connect(self._add_service)

        self.clear_service_form_btn = QPushButton("Clear Form")
        self.clear_service_form_btn.clicked.connect(self._clear_service_form)

        self.validate_service_btn = QPushButton("Validate")
        self.validate_service_btn.clicked.connect(self._validate_current_service)

        actions_layout.addWidget(self.add_service_btn)
        actions_layout.addWidget(self.clear_service_form_btn)
        actions_layout.addWidget(self.validate_service_btn)
        actions_layout.addStretch()

        entry_layout.addLayout(actions_layout, 5, 0, 1, 4)

        entry_group.setLayout(entry_layout)
        parent_layout.addWidget(entry_group)

    def _create_services_actions_section(self, parent_layout: QVBoxLayout):
        """Create services actions section"""
        # Separator
        separator = self._create_separator()
        parent_layout.addWidget(separator)

        # Actions layout
        actions_layout = QHBoxLayout()

        # Bulk actions
        self.select_all_services_btn = QPushButton("Select All")
        self.select_all_services_btn.clicked.connect(self._select_all_services)

        self.delete_selected_services_btn = QPushButton("Delete Selected")
        self.delete_selected_services_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        self.delete_selected_services_btn.clicked.connect(
            self._delete_selected_services
        )

        # Validation
        self.validate_all_services_btn = QPushButton("Validate All Services")
        self.validate_all_services_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """
        )
        self.validate_all_services_btn.clicked.connect(self._validate_all_services)

        actions_layout.addWidget(self.select_all_services_btn)
        actions_layout.addWidget(self.delete_selected_services_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.validate_all_services_btn)

        parent_layout.addLayout(actions_layout)

    def _create_faq_table_section(self, parent_layout: QVBoxLayout):
        """Create FAQ table section"""
        # Section header
        header_label = self._create_section_header("❓ FAQ Collection")
        parent_layout.addWidget(header_label)

        # Table group
        table_group = QGroupBox()
        table_layout = QVBoxLayout()

        # FAQ count and search
        controls_layout = QHBoxLayout()

        self.faq_count_label = QLabel("FAQs: 0")
        self.faq_count_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        # Search functionality
        search_label = QLabel("Search:")
        self.faq_search_input = QLineEdit()
        self.faq_search_input.setPlaceholderText("Search questions or answers...")
        self.faq_search_input.setMaximumWidth(250)
        self.faq_search_input.textChanged.connect(self._filter_faqs)

        controls_layout.addWidget(self.faq_count_label)
        controls_layout.addStretch()
        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.faq_search_input)

        # FAQ table
        self.faq_table = QTableWidget()
        self.faq_table.setColumnCount(4)  # Question, Answer, Category, Actions
        headers = ["Question", "Answer", "Category", "Actions"]
        self.faq_table.setHorizontalHeaderLabels(headers)

        # Table settings
        self.faq_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.faq_table.setAlternatingRowColors(True)
        self.faq_table.setSortingEnabled(True)

        # Set column widths
        header = self.faq_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(False)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Question
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Answer
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Category
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Actions

        self.faq_table.setColumnWidth(2, 100)  # Category
        self.faq_table.setColumnWidth(3, 80)  # Actions

        table_layout.addLayout(controls_layout)
        table_layout.addWidget(self.faq_table)

        table_group.setLayout(table_layout)
        parent_layout.addWidget(table_group)

    def _create_faq_entry_section(self, parent_layout: QVBoxLayout):
        """Create FAQ entry section"""
        # Section header
        header_label = self._create_section_header("➕ Add/Edit FAQ")
        parent_layout.addWidget(header_label)

        # Entry group
        entry_group = QGroupBox()
        entry_layout = QGridLayout()
        entry_layout.setSpacing(10)

        # FAQ form fields
        self.faq_inputs = {}

        # Row 1: Question
        question_label = QLabel("* Question:")
        question_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["question"] = QTextEdit()
        self.faq_inputs["question"].setPlaceholderText(
            "Enter frequently asked question"
        )
        self.faq_inputs["question"].setMaximumHeight(60)
        self.faq_inputs["question"].textChanged.connect(self._emit_config_changed)

        # Row 2: Answer
        answer_label = QLabel("* Answer:")
        answer_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["answer"] = QTextEdit()
        self.faq_inputs["answer"].setPlaceholderText(
            "Enter detailed answer to the question"
        )
        self.faq_inputs["answer"].setMaximumHeight(100)
        self.faq_inputs["answer"].textChanged.connect(self._emit_config_changed)

        # Row 3: Category
        category_label = QLabel("Category:")
        category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["category"] = QComboBox()
        self.faq_inputs["category"].addItems(self.FAQ_CATEGORIES)
        self.faq_inputs["category"].setEditable(True)
        self.faq_inputs["category"].currentTextChanged.connect(
            self._emit_config_changed
        )

        # Layout
        entry_layout.addWidget(question_label, 0, 0)
        entry_layout.addWidget(self.faq_inputs["question"], 0, 1, 1, 3)

        entry_layout.addWidget(answer_label, 1, 0)
        entry_layout.addWidget(self.faq_inputs["answer"], 1, 1, 1, 3)

        entry_layout.addWidget(category_label, 2, 0)
        entry_layout.addWidget(self.faq_inputs["category"], 2, 1)

        # Action buttons
        actions_layout = QHBoxLayout()

        self.add_faq_btn = QPushButton("➕ Add FAQ")
        self.add_faq_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #219a52;
            }
        """
        )
        self.add_faq_btn.clicked.connect(self._add_faq)

        self.clear_faq_form_btn = QPushButton("🗑️ Clear Form")
        self.clear_faq_form_btn.clicked.connect(self._clear_faq_form)

        self.validate_faq_btn = QPushButton("✅ Validate")
        self.validate_faq_btn.clicked.connect(self._validate_current_faq)

        actions_layout.addWidget(self.add_faq_btn)
        actions_layout.addWidget(self.clear_faq_form_btn)
        actions_layout.addWidget(self.validate_faq_btn)
        actions_layout.addStretch()

        entry_layout.addLayout(actions_layout, 3, 0, 1, 4)

        entry_group.setLayout(entry_layout)
        parent_layout.addWidget(entry_group)

    def _create_faq_actions_section(self, parent_layout: QVBoxLayout):
        """Create FAQ actions section"""
        # Separator
        separator = self._create_separator()
        parent_layout.addWidget(separator)

        # Actions layout
        actions_layout = QHBoxLayout()

        # Bulk actions
        self.select_all_faqs_btn = QPushButton("Select All")
        self.select_all_faqs_btn.clicked.connect(self._select_all_faqs)

        self.delete_selected_faqs_btn = QPushButton("🗑️ Delete Selected")
        self.delete_selected_faqs_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """
        )
        self.delete_selected_faqs_btn.clicked.connect(self._delete_selected_faqs)

        # Validation
        self.validate_all_faqs_btn = QPushButton("🔍 Validate All FAQs")
        self.validate_all_faqs_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """
        )
        self.validate_all_faqs_btn.clicked.connect(self._validate_all_faqs)

        actions_layout.addWidget(self.select_all_faqs_btn)
        actions_layout.addWidget(self.delete_selected_faqs_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.validate_all_faqs_btn)

        parent_layout.addLayout(actions_layout)

    def _create_section_header(self, text: str) -> QLabel:
        """Create a styled section header"""
        label = QLabel(text)
        label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50; padding: 5px 0px;")
        return label

    def _create_separator(self) -> QFrame:
        """Create a horizontal separator line"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        line.setStyleSheet("color: #bdc3c7;")
        return line

    # Services methods
    def _add_service(self):
        """Add service from manual entry form"""
        # Get features as list
        features_text = self.service_inputs["features"].toPlainText().strip()
        features = (
            [f.strip() for f in features_text.split("\n") if f.strip()]
            if features_text
            else []
        )

        # Create service
        service = Service(
            name=self.service_inputs["name"].text().strip(),
            description=self.service_inputs["description"].toPlainText().strip(),
            category=self.service_inputs["category"].currentText().strip(),
            price_range=self.service_inputs["price_range"].text().strip(),
            duration=self.service_inputs["duration"].text().strip(),
            features=features,
        )

        # Validate service
        is_valid, errors = service.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Check for duplicate name
        if any(s.name.lower() == service.name.lower() for s in self.services):
            QMessageBox.warning(
                self,
                "Duplicate Service",
                f"Service with name '{service.name}' already exists",
            )
            return

        # Add service
        self.services.append(service)
        self._refresh_services_table()
        self._update_services_count()
        self._clear_service_form()
        self._emit_config_changed()

        QMessageBox.information(
            self, "Service Added", f"Successfully added service: {service.name}"
        )

    def _clear_service_form(self):
        """Clear the service entry form"""
        self.service_inputs["name"].clear()
        self.service_inputs["description"].clear()
        self.service_inputs["category"].setCurrentIndex(0)
        self.service_inputs["price_range"].clear()
        self.service_inputs["duration"].clear()
        self.service_inputs["features"].clear()
        self._update_service_description_counter()

    def _validate_current_service(self):
        """Validate current service in form"""
        features_text = self.service_inputs["features"].toPlainText().strip()
        features = (
            [f.strip() for f in features_text.split("\n") if f.strip()]
            if features_text
            else []
        )

        service = Service(
            name=self.service_inputs["name"].text().strip(),
            description=self.service_inputs["description"].toPlainText().strip(),
            category=self.service_inputs["category"].currentText().strip(),
            price_range=self.service_inputs["price_range"].text().strip(),
            duration=self.service_inputs["duration"].text().strip(),
            features=features,
        )

        is_valid, errors = service.is_valid()

        if is_valid:
            QMessageBox.information(
                self, "Validation Success", "Service data is valid!"
            )
        else:
            QMessageBox.warning(
                self, "Validation Errors", "\n".join([f"• {error}" for error in errors])
            )

    def _refresh_services_table(self):
        """Refresh the services table display"""
        self.services_table.setRowCount(len(self.services))

        for row, service in enumerate(self.services):
            # Name
            self.services_table.setItem(row, 0, QTableWidgetItem(service.name))

            # Category
            self.services_table.setItem(row, 1, QTableWidgetItem(service.category))

            # Price Range
            self.services_table.setItem(row, 2, QTableWidgetItem(service.price_range))

            # Duration
            self.services_table.setItem(row, 3, QTableWidgetItem(service.duration))

            # Description (truncated)
            desc_text = (
                service.description[:80] + "..."
                if len(service.description) > 80
                else service.description
            )
            self.services_table.setItem(row, 4, QTableWidgetItem(desc_text))

            # Actions
            actions_btn = QPushButton("Edit")
            actions_btn.setMaximumWidth(60)
            actions_btn.clicked.connect(lambda checked, r=row: self._edit_service(r))
            self.services_table.setCellWidget(row, 5, actions_btn)

    def _filter_services(self):
        """Filter services table based on search input"""
        search_text = self.services_search_input.text().lower()

        for row in range(self.services_table.rowCount()):
            match = False
            for col in range(2):  # Search name and category
                item = self.services_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break

            self.services_table.setRowHidden(row, not match)

    def _update_services_count(self):
        """Update services count label"""
        visible_count = sum(
            1
            for row in range(self.services_table.rowCount())
            if not self.services_table.isRowHidden(row)
        )
        total_count = len(self.services)

        if visible_count == total_count:
            self.services_count_label.setText(f"Services: {total_count}")
        else:
            self.services_count_label.setText(
                f"Services: {visible_count}/{total_count}"
            )

    def _update_service_description_counter(self):
        """Update service description character counter"""
        text = self.service_inputs["description"].toPlainText()
        count = len(text)
        self.service_desc_counter.setText(f"{count}/1000")

        # Color coding
        if count > 1000:
            self.service_desc_counter.setStyleSheet(
                "color: #e74c3c; font-weight: bold;"
            )
        elif count > 900:
            self.service_desc_counter.setStyleSheet(
                "color: #f39c12; font-weight: bold;"
            )
        else:
            self.service_desc_counter.setStyleSheet("color: #7f8c8d;")

    def _edit_service(self, row: int):
        """Edit service at specified row"""
        if 0 <= row < len(self.services):
            service = self.services[row]

            # Load service into form
            self.service_inputs["name"].setText(service.name)
            self.service_inputs["description"].setPlainText(service.description)

            # Set category
            category_index = self.service_inputs["category"].findText(service.category)
            if category_index >= 0:
                self.service_inputs["category"].setCurrentIndex(category_index)
            else:
                self.service_inputs["category"].setCurrentText(service.category)

            self.service_inputs["price_range"].setText(service.price_range)
            self.service_inputs["duration"].setText(service.duration)
            self.service_inputs["features"].setPlainText("\n".join(service.features))

            # Change button to update mode
            self.add_service_btn.setText("Update Service")
            try:
                self.add_service_btn.clicked.disconnect()
            except TypeError:
                pass  # No connections to disconnect
            self.add_service_btn.clicked.connect(lambda: self._update_service(row))

    def _update_service(self, row: int):
        """Update service at specified row"""
        # Get features as list
        features_text = self.service_inputs["features"].toPlainText().strip()
        features = (
            [f.strip() for f in features_text.split("\n") if f.strip()]
            if features_text
            else []
        )

        # Create updated service
        updated_service = Service(
            name=self.service_inputs["name"].text().strip(),
            description=self.service_inputs["description"].toPlainText().strip(),
            category=self.service_inputs["category"].currentText().strip(),
            price_range=self.service_inputs["price_range"].text().strip(),
            duration=self.service_inputs["duration"].text().strip(),
            features=features,
        )

        # Validate service
        is_valid, errors = updated_service.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Check for duplicate name (excluding current service)
        for i, s in enumerate(self.services):
            if i != row and s.name.lower() == updated_service.name.lower():
                QMessageBox.warning(
                    self,
                    "Duplicate Service",
                    f"Service with name '{updated_service.name}' already exists",
                )
                return

        # Update service
        self.services[row] = updated_service
        self._refresh_services_table()
        self._clear_service_form()
        self._reset_add_service_button()
        self._emit_config_changed()

        QMessageBox.information(
            self,
            "Service Updated",
            f"Successfully updated service: {updated_service.name}",
        )

    def _reset_add_service_button(self):
        """Reset add service button to add mode"""
        self.add_service_btn.setText("Add Service")
        try:
            self.add_service_btn.clicked.disconnect()
        except TypeError:
            pass  # No connections to disconnect
        self.add_service_btn.clicked.connect(self._add_service)

    def _select_all_services(self):
        """Select all services in table"""
        self.services_table.selectAll()

    def _delete_selected_services(self):
        """Delete selected services"""
        selected_rows = set()
        for item in self.services_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(
                self, "No Selection", "Please select services to delete"
            )
            return

        # Confirm deletion
        count = len(selected_rows)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {count} selected service(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove services (in reverse order to maintain indices)
            for row in sorted(selected_rows, reverse=True):
                if 0 <= row < len(self.services):
                    del self.services[row]

            self._refresh_services_table()
            self._update_services_count()
            self._emit_config_changed()

            QMessageBox.information(
                self, "Deletion Complete", f"Successfully deleted {count} service(s)"
            )

    def _validate_all_services(self):
        """Validate all services"""
        if not self.services:
            QMessageBox.information(self, "No Services", "No services to validate")
            return

        errors = []
        for i, service in enumerate(self.services):
            is_valid, service_errors = service.is_valid()
            if not is_valid:
                for error in service_errors:
                    errors.append(f"Service {i+1} ({service.name}): {error}")

        if errors:
            QMessageBox.warning(self, "Validation Errors", "\n".join(errors))
        else:
            QMessageBox.information(
                self,
                "Validation Success",
                f"All {len(self.services)} services are valid!",
            )

    # FAQ methods
    def _add_faq(self):
        """Add FAQ from manual entry form"""
        # Create FAQ
        faq = FAQItem(
            question=self.faq_inputs["question"].toPlainText().strip(),
            answer=self.faq_inputs["answer"].toPlainText().strip(),
            category=self.faq_inputs["category"].currentText().strip(),
        )

        # Validate FAQ
        is_valid, errors = faq.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Check for duplicate question
        if any(f.question.lower() == faq.question.lower() for f in self.faqs):
            QMessageBox.warning(
                self, "Duplicate Question", "FAQ with this question already exists"
            )
            return

        # Add FAQ
        self.faqs.append(faq)
        self._refresh_faq_table()
        self._update_faq_count()
        self._clear_faq_form()
        self._emit_config_changed()

        QMessageBox.information(self, "FAQ Added", "Successfully added FAQ")

    def _clear_faq_form(self):
        """Clear the FAQ entry form"""
        self.faq_inputs["question"].clear()
        self.faq_inputs["answer"].clear()
        self.faq_inputs["category"].setCurrentIndex(0)

    def _validate_current_faq(self):
        """Validate current FAQ in form"""
        faq = FAQItem(
            question=self.faq_inputs["question"].toPlainText().strip(),
            answer=self.faq_inputs["answer"].toPlainText().strip(),
            category=self.faq_inputs["category"].currentText().strip(),
        )

        is_valid, errors = faq.is_valid()

        if is_valid:
            QMessageBox.information(self, "Validation Success", "✅ FAQ data is valid!")
        else:
            QMessageBox.warning(
                self, "Validation Errors", "\n".join([f"• {error}" for error in errors])
            )

    def _refresh_faq_table(self):
        """Refresh the FAQ table display"""
        self.faq_table.setRowCount(len(self.faqs))

        for row, faq in enumerate(self.faqs):
            # Question (truncated)
            question_text = (
                faq.question[:100] + "..." if len(faq.question) > 100 else faq.question
            )
            self.faq_table.setItem(row, 0, QTableWidgetItem(question_text))

            # Answer (truncated)
            answer_text = (
                faq.answer[:100] + "..." if len(faq.answer) > 100 else faq.answer
            )
            self.faq_table.setItem(row, 1, QTableWidgetItem(answer_text))

            # Category
            self.faq_table.setItem(row, 2, QTableWidgetItem(faq.category))

            # Actions
            actions_btn = QPushButton("✏️ Edit")
            actions_btn.setMaximumWidth(60)
            actions_btn.clicked.connect(lambda checked, r=row: self._edit_faq(r))
            self.faq_table.setCellWidget(row, 3, actions_btn)

    def _filter_faqs(self):
        """Filter FAQ table based on search input"""
        search_text = self.faq_search_input.text().lower()

        for row in range(self.faq_table.rowCount()):
            match = False
            for col in range(3):  # Search question, answer, and category
                item = self.faq_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break

            self.faq_table.setRowHidden(row, not match)

    def _update_faq_count(self):
        """Update FAQ count label"""
        visible_count = sum(
            1
            for row in range(self.faq_table.rowCount())
            if not self.faq_table.isRowHidden(row)
        )
        total_count = len(self.faqs)

        if visible_count == total_count:
            self.faq_count_label.setText(f"FAQs: {total_count}")
        else:
            self.faq_count_label.setText(f"FAQs: {visible_count}/{total_count}")

    def _edit_faq(self, row: int):
        """Edit FAQ at specified row"""
        if 0 <= row < len(self.faqs):
            faq = self.faqs[row]

            # Load FAQ into form
            self.faq_inputs["question"].setPlainText(faq.question)
            self.faq_inputs["answer"].setPlainText(faq.answer)

            # Set category
            category_index = self.faq_inputs["category"].findText(faq.category)
            if category_index >= 0:
                self.faq_inputs["category"].setCurrentIndex(category_index)
            else:
                self.faq_inputs["category"].setCurrentText(faq.category)

            # Change button to update mode
            self.add_faq_btn.setText("💾 Update FAQ")
            try:
                self.add_faq_btn.clicked.disconnect()
            except TypeError:
                pass  # No connections to disconnect
            self.add_faq_btn.clicked.connect(lambda: self._update_faq(row))

    def _update_faq(self, row: int):
        """Update FAQ at specified row"""
        # Create updated FAQ
        updated_faq = FAQItem(
            question=self.faq_inputs["question"].toPlainText().strip(),
            answer=self.faq_inputs["answer"].toPlainText().strip(),
            category=self.faq_inputs["category"].currentText().strip(),
        )

        # Validate FAQ
        is_valid, errors = updated_faq.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Check for duplicate question (excluding current FAQ)
        for i, f in enumerate(self.faqs):
            if i != row and f.question.lower() == updated_faq.question.lower():
                QMessageBox.warning(
                    self, "Duplicate Question", "FAQ with this question already exists"
                )
                return

        # Update FAQ
        self.faqs[row] = updated_faq
        self._refresh_faq_table()
        self._clear_faq_form()
        self._reset_add_faq_button()
        self._emit_config_changed()

        QMessageBox.information(self, "FAQ Updated", "Successfully updated FAQ")

    def _reset_add_faq_button(self):
        """Reset add FAQ button to add mode"""
        self.add_faq_btn.setText("➕ Add FAQ")
        try:
            self.add_faq_btn.clicked.disconnect()
        except TypeError:
            pass  # No connections to disconnect
        self.add_faq_btn.clicked.connect(self._add_faq)

    def _select_all_faqs(self):
        """Select all FAQs in table"""
        self.faq_table.selectAll()

    def _delete_selected_faqs(self):
        """Delete selected FAQs"""
        selected_rows = set()
        for item in self.faq_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(
                self, "No Selection", "Please select FAQs to delete"
            )
            return

        # Confirm deletion
        count = len(selected_rows)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {count} selected FAQ(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove FAQs (in reverse order to maintain indices)
            for row in sorted(selected_rows, reverse=True):
                if 0 <= row < len(self.faqs):
                    del self.faqs[row]

            self._refresh_faq_table()
            self._update_faq_count()
            self._emit_config_changed()

            QMessageBox.information(
                self, "Deletion Complete", f"Successfully deleted {count} FAQ(s)"
            )

    def _validate_all_faqs(self):
        """Validate all FAQs"""
        if not self.faqs:
            QMessageBox.information(self, "No FAQs", "No FAQs to validate")
            return

        errors = []
        for i, faq in enumerate(self.faqs):
            is_valid, faq_errors = faq.is_valid()
            if not is_valid:
                for error in faq_errors:
                    errors.append(f"FAQ {i+1}: {error}")

        if errors:
            QMessageBox.warning(self, "Validation Errors", "\n".join(errors))
        else:
            QMessageBox.information(
                self, "Validation Success", f"✅ All {len(self.faqs)} FAQs are valid!"
            )

    # CSV Import/Export Methods
    def _browse_csv_file(self):
        """Browse for CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Services CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            self.file_path_input.setText(file_path)
            self.current_file_path = file_path
            self.import_btn.setEnabled(True)
            self.validate_csv_btn.setEnabled(True)
            self._update_import_status(f"Selected: {os.path.basename(file_path)}")

    def _detect_file_encoding(self, file_path: str) -> str:
        """Detect file encoding using chardet with fallback options"""
        try:
            # Read a sample of the file to detect encoding
            with open(file_path, "rb") as f:
                raw_data = f.read(10000)  # Read first 10KB for detection

            if raw_data:
                # Use chardet to detect encoding
                result = chardet.detect(raw_data)
                encoding = result.get("encoding", "utf-8").lower()
                confidence = result.get("confidence", 0)

                # Map common encoding variations
                encoding_map = {
                    "windows-1252": "cp1252",
                    "iso-8859-1": "latin1",
                    "ascii": "utf-8",
                }

                encoding = encoding_map.get(encoding, encoding)

                # If confidence is low, try common fallbacks
                if confidence < 0.7:
                    fallback_encodings = ["utf-8", "cp1252", "latin1", "utf-16"]
                    for fallback in fallback_encodings:
                        try:
                            with open(file_path, "r", encoding=fallback) as f:
                                f.read(1000)  # Try to read some content
                            return fallback
                        except (UnicodeDecodeError, UnicodeError):
                            continue

                return encoding

        except Exception:
            pass

        # Default fallback
        return "utf-8"

    def _validate_csv_file(self):
        """Validate CSV file structure with automatic encoding detection"""
        if not self.current_file_path:
            return

        try:
            # Detect file encoding
            encoding = self._detect_file_encoding(self.current_file_path)

            with open(
                self.current_file_path, "r", encoding=encoding, errors="replace"
            ) as file:
                reader = csv.DictReader(file)

                # Check required columns
                required_columns = ["Name", "Description"]
                optional_columns = ["Category", "Price Range", "Duration", "Features"]

                missing_required = [
                    col for col in required_columns if col not in reader.fieldnames
                ]
                available_optional = [
                    col for col in optional_columns if col in reader.fieldnames
                ]

                if missing_required:
                    QMessageBox.warning(
                        self,
                        "CSV Validation Error",
                        f"Missing required columns: {', '.join(missing_required)}\n\n"
                        f"Required: {', '.join(required_columns)}\n"
                        f"Optional: {', '.join(optional_columns)}",
                    )
                    return

                # Count rows and validate each service
                rows = list(reader)
                row_count = len(rows)

                validation_errors = []
                validation_warnings = []
                valid_services = 0

                # Check for duplicates in CSV file
                names = [row.get("Name", "").strip() for row in rows]
                duplicate_names = [name for name in set(names) if names.count(name) > 1]

                for row_num, row in enumerate(rows, start=2):  # Start at 2 for header
                    try:
                        # Parse features (can be pipe-separated or newline-separated)
                        features_text = row.get("Features", "").strip()
                        features = []
                        if features_text:
                            # Try pipe-separated first, then newline
                            if "|" in features_text:
                                features = [
                                    f.strip()
                                    for f in features_text.split("|")
                                    if f.strip()
                                ]
                            else:
                                features = [
                                    f.strip()
                                    for f in features_text.split("\n")
                                    if f.strip()
                                ]

                        # Create temporary service for validation
                        service = Service(
                            name=row.get("Name", "").strip(),
                            description=row.get("Description", "").strip(),
                            category=row.get("Category", "General Services").strip(),
                            price_range=row.get("Price Range", "").strip(),
                            duration=row.get("Duration", "").strip(),
                            features=features,
                        )

                        # Validate service data
                        is_valid, service_errors = service.is_valid()
                        if not is_valid:
                            validation_errors.extend(
                                [f"Row {row_num}: {error}" for error in service_errors]
                            )
                        else:
                            valid_services += 1

                        # Check for existing name in current services
                        if any(
                            s.name.lower() == service.name.lower()
                            for s in self.services
                        ):
                            validation_warnings.append(
                                f"Row {row_num}: Service '{service.name}' already exists in current services"
                            )

                    except Exception as e:
                        validation_errors.append(f"Row {row_num}: {str(e)}")

                # Add CSV duplicate warnings
                for name in duplicate_names:
                    if name:  # Only warn about non-empty names
                        validation_warnings.append(
                            f"Service name '{name}' appears multiple times in CSV file"
                        )

                # Show comprehensive validation results
                if validation_errors:
                    msg = "CSV Validation Failed!\n\n"
                    msg += f"Total rows: {row_count}\n"
                    msg += f"Valid services: {valid_services}\n"
                    msg += f"Errors: {len(validation_errors)}\n"

                    if validation_warnings:
                        msg += f"Warnings: {len(validation_warnings)}\n"

                    detailed_msg = msg + "\n\nERRORS:\n" + "\n".join(validation_errors)
                    if validation_warnings:
                        detailed_msg += "\n\nWARNINGS:\n" + "\n".join(
                            validation_warnings
                        )

                    msgbox = QMessageBox(self)
                    msgbox.setWindowTitle("CSV Validation Failed")
                    msgbox.setIcon(QMessageBox.Icon.Warning)
                    msgbox.setText(msg)
                    msgbox.setDetailedText(detailed_msg)
                    msgbox.exec()

                    self._update_import_status(
                        f"Validation failed - {len(validation_errors)} errors found"
                    )

                elif validation_warnings:
                    msg = "CSV Validation Passed with Warnings!\n\n"
                    msg += f"Total rows: {row_count}\n"
                    msg += f"Valid services: {valid_services}\n"
                    msg += f"Warnings: {len(validation_warnings)}\n"

                    detailed_msg = (
                        msg + "\n\nWARNINGS:\n" + "\n".join(validation_warnings)
                    )

                    msgbox = QMessageBox(self)
                    msgbox.setWindowTitle("CSV Validation - Warnings Found")
                    msgbox.setIcon(QMessageBox.Icon.Information)
                    msgbox.setText(msg)
                    msgbox.setDetailedText(detailed_msg)
                    msgbox.exec()

                    self._update_import_status(
                        f"Valid CSV with {len(validation_warnings)} warnings - {valid_services} services ready"
                    )

                else:
                    msg = "CSV Validation Successful!\n\n"
                    msg += f"Total rows: {row_count}\n"
                    msg += f"Valid services: {valid_services}\n"
                    msg += f"Required columns: {', '.join(required_columns)}\n"
                    msg += f"Optional columns found: {', '.join(available_optional)}"

                    QMessageBox.information(self, "CSV Validation Results", msg)
                    self._update_import_status(
                        f"Valid CSV - {valid_services} services ready to import"
                    )

        except Exception as e:
            error_msg = f"Error reading CSV file:\n{str(e)}"
            log_file_operation_error(
                operation="validate_csv",
                file_path=self.current_file_path or "unknown",
                error_message=error_msg,
                exception=e,
            )
            QMessageBox.critical(self, "CSV Validation Error", error_msg)

    def _import_csv(self):
        """Import services from CSV file"""
        if not self.current_file_path:
            return

        try:
            self.import_progress.show()
            self.import_progress.setRange(0, 0)  # Indeterminate progress

            imported_services = []
            errors = []
            warnings = []

            # Detect file encoding
            encoding = self._detect_file_encoding(self.current_file_path)

            with open(
                self.current_file_path, "r", encoding=encoding, errors="replace"
            ) as file:
                reader = csv.DictReader(file)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    try:
                        # Parse features (can be pipe-separated or newline-separated)
                        features_text = row.get("Features", "").strip()
                        features = []
                        if features_text:
                            # Try pipe-separated first, then newline
                            if "|" in features_text:
                                features = [
                                    f.strip()
                                    for f in features_text.split("|")
                                    if f.strip()
                                ]
                            else:
                                features = [
                                    f.strip()
                                    for f in features_text.split("\n")
                                    if f.strip()
                                ]

                        service = Service(
                            name=row.get("Name", "").strip(),
                            description=row.get("Description", "").strip(),
                            category=row.get("Category", "General Services").strip(),
                            price_range=row.get("Price Range", "").strip(),
                            duration=row.get("Duration", "").strip(),
                            features=features,
                        )

                        # Validate service
                        is_valid, service_errors = service.is_valid()
                        if not is_valid:
                            errors.extend(
                                [f"Row {row_num}: {error}" for error in service_errors]
                            )
                            continue

                        # Check for duplicate name (case-insensitive)
                        if any(
                            s.name.lower() == service.name.lower()
                            for s in self.services
                        ):
                            warnings.append(
                                f"Row {row_num}: Service '{service.name}' already exists (skipped)"
                            )
                            continue

                        imported_services.append(service)

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

            # Add imported services
            self.services.extend(imported_services)
            self._refresh_services_table()
            self._update_services_count()

            self.import_progress.hide()

            # Show import results
            msg = "Import completed!\n\n"
            msg += f"Successfully imported: {len(imported_services)} services\n"

            if warnings:
                msg += f"Warnings: {len(warnings)}\n"
            if errors:
                msg += f"Errors: {len(errors)}\n"

            if warnings or errors:
                detailed_msg = msg + "\n"
                if errors:
                    detailed_msg += "\nERRORS:\n" + "\n".join(errors)
                if warnings:
                    detailed_msg += "\nWARNINGS:\n" + "\n".join(warnings)

                msgbox = QMessageBox(self)
                msgbox.setWindowTitle("Import Results")
                msgbox.setText(msg)
                msgbox.setDetailedText(detailed_msg)
                msgbox.exec()
            else:
                QMessageBox.information(self, "Import Success", msg)

            self._update_import_status(f"Imported {len(imported_services)} services")
            self._emit_config_changed()

        except Exception as e:
            self.import_progress.hide()
            error_msg = f"Error importing CSV:\n{str(e)}"
            log_file_operation_error(
                operation="import_csv",
                file_path=self.current_file_path,
                error_message=error_msg,
                exception=e,
            )
            QMessageBox.critical(self, "Import Error", error_msg)

    def _export_csv(self):
        """Export services to CSV file"""
        if not self.services:
            QMessageBox.information(self, "Export", "No services to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Services CSV",
            "services_export.csv",
            "CSV Files (*.csv);;All Files (*)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                fieldnames = [
                    "Name",
                    "Description",
                    "Category",
                    "Price Range",
                    "Duration",
                    "Features",
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()
                for service in self.services:
                    # Join features with pipe separator for CSV export
                    features_str = (
                        " | ".join(service.features) if service.features else ""
                    )

                    writer.writerow(
                        {
                            "Name": service.name,
                            "Description": service.description,
                            "Category": service.category,
                            "Price Range": service.price_range,
                            "Duration": service.duration,
                            "Features": features_str,
                        }
                    )

            QMessageBox.information(
                self,
                "Export Success",
                f"Successfully exported {len(self.services)} services to:\n{file_path}",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", f"Error exporting CSV:\n{str(e)}"
            )

    def _update_import_status(self, message: str):
        """Update import status label"""
        self.import_status.setText(message)

    # BaseTab implementation
    def connect_signals(self):
        """Connect UI signals to emit config_changed"""
        # Signals already connected in individual widgets
        pass

    def get_required_fields(self) -> List[str]:
        """Get list of required field names"""
        return (
            []
        )  # No required fields at tab level (individual services/FAQs have requirements)

    def validate_data(self) -> ValidationResult:
        """Validate all services data"""
        result = ValidationResult()

        # Validate services
        if not self.services:
            result.add_warning("No services defined")
        else:
            for i, service in enumerate(self.services):
                is_valid, errors = service.is_valid()
                if not is_valid:
                    for error in errors:
                        result.add_error(f"Service {i+1} ({service.name}): {error}")

            # Check for duplicate service names
            service_names = [s.name.lower() for s in self.services]
            duplicates = []
            for name in service_names:
                if service_names.count(name) > 1 and name not in duplicates:
                    duplicates.append(name)

            for name in duplicates:
                result.add_error(f"Duplicate service name found: {name}")

        # Best practice warnings
        if len(self.services) > 20:
            result.add_warning(
                f"Large service catalog ({len(self.services)} services) - consider categorization"
            )

        services_without_prices = sum(
            1 for s in self.services if not s.price_range.strip()
        )
        if services_without_prices > 0:
            result.add_warning(
                f"{services_without_prices} services missing price information"
            )

        services_without_duration = sum(
            1 for s in self.services if not s.duration.strip()
        )
        if services_without_duration > 0:
            result.add_warning(
                f"{services_without_duration} services missing duration information"
            )

        return result

    def validate_and_show_results(self):
        """Validate data and show results to user"""
        result = self.validate_data()

        if result.is_valid:
            msg = "Services validation passed!\n\n"
            msg += f"- Services: {len(self.services)}\n"
            msg += "- All data is valid\n"

            if result.warnings:
                msg += f"- Warnings: {len(result.warnings)}\n"

                # Show detailed warnings
                detailed_msg = (
                    msg + "\n" + "\n".join([f"WARNING: {w}" for w in result.warnings])
                )
                msgbox = QMessageBox(self)
                msgbox.setWindowTitle("Validation Results")
                msgbox.setText(msg)
                msgbox.setDetailedText(detailed_msg)
                msgbox.exec()
            else:
                QMessageBox.information(self, "Validation Success", msg)
        else:
            msg = "Services validation failed!\n\n"
            msg += f"- Services: {len(self.services)}\n"
            msg += f"- Errors: {len(result.errors)}\n"

            if result.warnings:
                msg += f"- Warnings: {len(result.warnings)}\n"

            # Show detailed errors and warnings
            details = []
            details.extend([f"ERROR: {e}" for e in result.errors])
            details.extend([f"WARNING: {w}" for w in result.warnings])

            detailed_msg = msg + "\n" + "\n".join(details)
            msgbox = QMessageBox(self)
            msgbox.setWindowTitle("Validation Results")
            msgbox.setText(msg)
            msgbox.setDetailedText(detailed_msg)
            msgbox.exec()

    def get_config_data(self) -> Dict[str, Any]:
        """Get services configuration data"""
        return {
            "services": [service.to_dict() for service in self.services],
        }

    def set_config_data(self, data: Dict[str, Any]):
        """Set services configuration data"""
        # Load services
        services_data = data.get("services", [])
        self.services = [Service.from_dict(s) for s in services_data]

        # Refresh displays
        self._refresh_services_table()
        self._update_services_count()

        # Clear forms
        self._clear_service_form()
        self._reset_add_service_button()

        # Emit data loaded signal
        self.data_loaded.emit()

    def clear_data(self):
        """Clear all services data"""
        self.services.clear()

        self._refresh_services_table()
        self._update_services_count()

        self._clear_service_form()
        self._reset_add_service_button()

        # Clear search filters
        self.services_search_input.clear()

        # Clear CSV import state
        self.file_path_input.clear()
        self.current_file_path = ""
        self.import_btn.setEnabled(False)
        self.validate_csv_btn.setEnabled(False)
        self._update_import_status("Ready to import services from CSV")

        self.has_changes = False

    def _emit_config_changed(self):
        """Helper method to emit config changed signal"""
        self.has_changes = True
        self.config_changed.emit()
