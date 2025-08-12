"""
Filename: services_tab.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\content_tabs\\services_tab.py
Description: Services management tab with manual entry, categories, and FAQ integration
Handles service catalog management with detailed descriptions and pricing information

Version: 1.0.0
Date: 2025-08-11
Author: Cloud Stack Generator Team
"""

import json
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
    QMessageBox,
    QGroupBox,
    QComboBox,
    QTextEdit,
    QHeaderView,
    QAbstractItemView,
    QFrame,
    QSpinBox,
    QCheckBox,
    QTabWidget,
    QWidget,
    QSplitter,
)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt, pyqtSignal
from ..components.base_tab import BaseTab


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
        features: List[str] = None,
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


class FAQ:
    """FAQ data model"""

    def __init__(self, question: str = "", answer: str = "", category: str = "General"):
        self.question = question
        self.answer = answer
        self.category = category

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            "question": self.question,
            "answer": self.answer,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "FAQ":
        """Create from dictionary"""
        return cls(
            question=data.get("question", ""),
            answer=data.get("answer", ""),
            category=data.get("category", "General"),
        )

    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate FAQ data"""
        errors = []
        if not self.question.strip():
            errors.append("Question is required")
        if not self.answer.strip():
            errors.append("Answer is required")
        return len(errors) == 0, errors


class ServicesTab(BaseTab):
    """Tab for services and FAQ management"""

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

    # FAQ categories
    FAQ_CATEGORIES = [
        "General",
        "Services",
        "Pricing",
        "Support",
        "Process",
        "Technical",
    ]

    def __init__(self, parent=None):
        self.services: List[Service] = []
        self.faqs: List[FAQ] = []
        self.has_changes = False
        super().__init__(parent)

    def setup_ui(self):
        """Setup services and FAQ management UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        # Create main tab widget
        self.main_tabs = QTabWidget()

        # Services tab
        services_widget = QWidget()
        self._setup_services_tab(services_widget)
        self.main_tabs.addTab(services_widget, "🔧 Services")

        # FAQ tab
        faq_widget = QWidget()
        self._setup_faq_tab(faq_widget)
        self.main_tabs.addTab(faq_widget, "❓ FAQ")

        main_layout.addWidget(self.main_tabs)
        self.setLayout(main_layout)

    def _setup_services_tab(self, parent_widget: QWidget):
        """Setup services management tab"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Create services sections
        self._create_services_table_section(layout)
        self._create_service_entry_section(layout)
        self._create_services_actions_section(layout)

        parent_widget.setLayout(layout)

    def _setup_faq_tab(self, parent_widget: QWidget):
        """Setup FAQ management tab"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Create FAQ sections
        self._create_faq_table_section(layout)
        self._create_faq_entry_section(layout)
        self._create_faq_actions_section(layout)

        parent_widget.setLayout(layout)

    def _create_services_table_section(self, parent_layout: QVBoxLayout):
        """Create services table section"""
        # Section header
        header_label = self._create_section_header("🔧 Services Catalog")
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
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)  # Category
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Duration
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Actions

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
        header_label = self._create_section_header("➕ Add/Edit Service")
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

        self.add_service_btn = QPushButton("➕ Add Service")
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

        self.clear_service_form_btn = QPushButton("🗑️ Clear Form")
        self.clear_service_form_btn.clicked.connect(self._clear_service_form)

        self.validate_service_btn = QPushButton("✅ Validate")
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

        self.delete_selected_services_btn = QPushButton("🗑️ Delete Selected")
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
self.delete_selected_services_btn.clicked.connect(self._delete_selected_services)
        
        # Validation
        self.validate_all_services_btn = QPushButton("🔍 Validate All Services")
        self.validate_all_services_btn.setStyleSheet("""
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
        """)
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
        self.faq_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.faq_table.setAlternatingRowColors(True)
        self.faq_table.setSortingEnabled(True)
        
        # Set column widths
        header = self.faq_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Question
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Answer
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Actions
        
        self.faq_table.setColumnWidth(2, 100)  # Category
        self.faq_table.setColumnWidth(3, 80)   # Actions
        
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
        self.faq_inputs["question"].setPlaceholderText("Enter frequently asked question")
        self.faq_inputs["question"].setMaximumHeight(60)
        self.faq_inputs["question"].textChanged.connect(self._emit_config_changed)
        
        # Row 2: Answer
        answer_label = QLabel("* Answer:")
        answer_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["answer"] = QTextEdit()
        self.faq_inputs["answer"].setPlaceholderText("Enter detailed answer to the question")
        self.faq_inputs["answer"].setMaximumHeight(100)
        self.faq_inputs["answer"].textChanged.connect(self._emit_config_changed)
        
        # Row 3: Category
        category_label = QLabel("Category:")
        category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["category"] = QComboBox()
        self.faq_inputs["category"].addItems(self.FAQ_CATEGORIES)
        self.faq_inputs["category"].setEditable(True)
        self.faq_inputs["category"].currentTextChanged.connect(self._emit_config_changed)
        
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
        self.add_faq_btn.setStyleSheet("""
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
        """)
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
        self.delete_selected_faqs_btn.setStyleSheet("""
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
        """)
        self.delete_selected_faqs_btn.clicked.connect(self._delete_selected_faqs)
        
        # Validation
        self.validate_all_faqs_btn = QPushButton("🔍 Validate All FAQs")
        self.validate_all_faqs_btn.setStyleSheet("""
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
        """)
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
        features = [f.strip() for f in features_text.split('\n') if f.strip()] if features_text else []
        
        # Create service
        service = Service(
            name=self.service_inputs["name"].text().strip(),
            description=self.service_inputs["description"].toPlainText().strip(),
            category=self.service_inputs["category"].currentText().strip(),
            price_range=self.service_inputs["price_range"].text().strip(),
            duration=self.service_inputs["duration"].text().strip(),
            features=features
        )
        
        # Validate service
        is_valid, errors = service.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return
        
        # Check for duplicate name
        if any(s.name.lower() == service.name.lower() for s in self.services):
            QMessageBox.warning(self, "Duplicate Service", f"Service with name '{service.name}' already exists")
            return
        
        # Add service
        self.services.append(service)
        self._refresh_services_table()
        self._update_services_count()
        self._clear_service_form()
        self._emit_config_changed()
        
        QMessageBox.information(self, "Service Added", f"Successfully added service: {service.name}")
    
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
        features = [f.strip() for f in features_text.split('\n') if f.strip()] if features_text else []
        
        service = Service(
            name=self.service_inputs["name"].text().strip(),
            description=self.service_inputs["description"].toPlainText().strip(),
            category=self.service_inputs["category"].currentText().strip(),
            price_range=self.service_inputs["price_range"].text().strip(),
            duration=self.service_inputs["duration"].text().strip(),
            features=features
        )
        
        is_valid, errors = service.is_valid()
        
        if is_valid:
            QMessageBox.information(self, "Validation Success", "✅ Service data is valid!")
        else:
            QMessageBox.warning(self, "Validation Errors", "\n".join([f"• {error}" for error in errors]))
    
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
            desc_text = service.description[:80] + "..." if len(service.description) > 80 else service.description
            self.services_table.setItem(row, 4, QTableWidgetItem(desc_text))
            
            # Actions
            actions_btn = QPushButton("✏️ Edit")
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
        visible_count = sum(1 for row in range(self.services_table.rowCount()) 
                           if not self.services_table.isRowHidden(row))
        total_count = len(self.services)
        
        if visible_count == total_count:
            self.services_count_label.setText(f"Services: {total_count}")
        else:
            self.services_count_label.setText(f"Services: {visible_count}/{total_count}")
    
    def _update_service_description_counter(self):
        """Update service description character counter"""
        text = self.service_inputs["description"].toPlainText()
        count = len(text)
        self.service_desc_counter.setText(f"{count}/1000")
        
        # Color coding
        if count > 1000:
            self.service_desc_counter.setStyleSheet("color: #e74c3c; font-weight: bold;")
        elif count > 900:
            self.service_desc_counter.setStyleSheet("color: #f39c12; font-weight: bold;")
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
            self.service_inputs["features"].setPlainText('\n'.join(service.features))
            
            # Change button to update mode
            self.add_service_btn.setText("💾 Update Service")
            self.add_service_btn.clicked.disconnect()
            self.add_service_btn.clicked.connect(lambda: self._update_service(row))
    
    def _update_service(self, row: int):
        """Update service at specified row"""
        # Get features as list
        features_text = self.service_inputs["features"].toPlainText().strip()
        features = [f.strip() for f in features_text.split('\n') if f.strip()] if features_text else []
        
        # Create updated service
        updated_service = Service(
            name=self.service_inputs["name"].text().strip(),
            description=self.service_inputs["description"].toPlainText().strip(),
            category=self.service_inputs["category"].currentText().strip(),
            price_range=self.service_inputs["price_range"].text().strip(),
            duration=self.service_inputs["duration"].text().strip(),
            features=features
        )
        
        # Validate service
        is_valid, errors = updated_service.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return
        
        # Check for duplicate name (excluding current service)
        for i, s in enumerate(self.services):
            if i != row and s.name.lower() == updated_service.name.lower():
                QMessageBox.warning(self, "Duplicate Service", f"Service with name '{updated_service.name}' already exists")
                return
        
        # Update service
        self.services[row] = updated_service
        self._refresh_services_table()
        self._clear_service_form()
        self._reset_add_service_button()
        self._emit_config_changed()
        
        QMessageBox.information(self, "Service Updated", f"Successfully updated service: {updated_service.name}")
    
    def _reset_add_service_button(self):
        """Reset add service button to add mode"""
        self.add_service_btn.setText("➕ Add Service")
        self.add_service_btn.clicked.disconnect()
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
            QMessageBox.information(self, "No Selection", "Please select services to delete")
            return
        
        # Confirm deletion
        count = len(selected_rows)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {count} selected service(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove services (in reverse order to maintain indices)
            for row in sorted(selected_rows, reverse=True):
                if 0 <= row < len(self.services):
                    del self.services[row]
            
            self._refresh_services_table()
            self._update_services_count()
            self._emit_config_changed()
            
            QMessageBox.information(self, "Deletion Complete", f"Successfully deleted {count} service(s)")
    
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
            QMessageBox.information(self, "Validation Success", f"✅ All {len(self.services)} services are valid!")
    
    # FAQ methods
    def _add_faq(self):
        """Add FAQ from manual entry form"""
        # Create FAQ
        faq = FAQ(
            question=self.faq_inputs["question"].toPlainText().strip(),
            answer=self.faq_inputs["answer"].toPlainText().strip(),
            category=self.faq_inputs["category"].currentText().strip()
        )
        
        # Validate FAQ
        is_valid, errors = faq.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return
        
        # Check for duplicate question
        if any(f.question.lower() == faq.question.lower() for f in self.faqs):
            QMessageBox.warning(self, "Duplicate Question", f"FAQ with this question already exists")
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
        faq = FAQ(
            question=self.faq_inputs["question"].toPlainText().strip(),
            answer=self.faq_inputs["answer"].toPlainText().strip(),
            category=self.faq_inputs["category"].currentText().strip()
        )
        
        is_valid, errors = faq.is_valid()
        
        if is_valid:
            QMessageBox.information(self, "Validation Success", "✅ FAQ data is valid!")
        else:
            QMessageBox.warning(self, "Validation Errors", "\n".join([f"• {error}" for error in errors]))
    
    def _refresh_faq_table(self):
        """Refresh the FAQ table display"""
        self.faq_table.setRowCount(len(self.faqs))
        
        for row, faq in enumerate(self.faqs):
            # Question (truncated)
            question_text = faq.question[:100] + "..." if len(faq.question) > 100 else faq.question
            self.faq_table.setItem(row, 0, QTableWidgetItem(question_text))
            
            # Answer (truncated)
            answer_text = faq.answer[:100] + "..." if len(faq.answer) > 100 else faq.answer
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
        visible_count = sum(1 for row in range(self.faq_table.rowCount()) 
                           if not self.faq_table.isRowHidden(row))
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
            self.add_faq_btn.clicked.disconnect()
            self.add_faq_btn.clicked.connect(lambda: self._update_faq(row))
    
    def _update_faq(self, row: int):
        """Update FAQ at specified row"""
        # Create updated FAQ
        updated_faq = FAQ(
            question=self.faq_inputs["question"].toPlainText().strip(),
            answer=self.faq_inputs["answer"].toPlainText().strip(),
            category=self.faq_inputs["category"].currentText().strip()
        )
        
        # Validate FAQ
        is_valid, errors = updated_faq.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return
        
        # Check for duplicate question (excluding current FAQ)
        for i, f in enumerate(self.faqs):
            if i != row and f.question.lower() == updated_faq.question.lower():
                QMessageBox.warning(self, "Duplicate Question", "FAQ with this question already exists")
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
        self.add_faq_btn.clicked.disconnect()
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
            QMessageBox.information(self, "No Selection", "Please select FAQs to delete")
            return
        
        # Confirm deletion
        count = len(selected_rows)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {count} selected FAQ(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Remove FAQs (in reverse order to maintain indices)
            for row in sorted(selected_rows, reverse=True):
                if 0 <= row < len(self.faqs):
                    del self.faqs[row]
            
            self._refresh_faq_table()
            self._update_faq_count()
            self._emit_config_changed()
            
            QMessageBox.information(self, "Deletion Complete", f"Successfully deleted {count} FAQ(s)")
    
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
            QMessageBox.information(self, "Validation Success", f"✅ All {len(self.faqs)} FAQs are valid!")
    
    # BaseTab implementation
    def connect_signals(self):
        """Connect UI signals to emit config_changed"""
        # Signals already connected in individual widgets
        pass
    
    def get_required_fields(self) -> List[str]:
        """Get list of required field names"""
        return []  # No required fields at tab level (individual services/FAQs have requirements)
    
    def validate_data(self) -> ValidationResult:
        """Validate all services and FAQ data"""
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
        
        # Validate FAQs
        if not self.faqs:
            result.add_warning("No FAQs defined - consider adding common questions")
        else:
            for i, faq in enumerate(self.faqs):
                is_valid, errors = faq.is_valid()
                if not is_valid:
                    for error in errors:
                        result.add_error(f"FAQ {i+1}: {error}")
            
            # Check for duplicate FAQ questions
            faq_questions = [f.question.lower() for f in self.faqs]
            duplicates = []
            for question in faq_questions:
                if faq_questions.count(question) > 1 and question not in duplicates:
                    duplicates.append(question)
            
            for question in duplicates:
                result.add_error(f"Duplicate FAQ question found: {question}")
        
        # Best practice warnings
        if len(self.services) > 20:
            result.add_warning(f"Large service catalog ({len(self.services)} services) - consider categorization")
        
        services_without_prices = sum(1 for s in self.services if not s.price_range.strip())
        if services_without_prices > 0:
            result.add_warning(f"{services_without_prices} services missing price information")
        
        services_without_duration = sum(1 for s in self.services if not s.duration.strip())
        if services_without_duration > 0:
            result.add_warning(f"{services_without_duration} services missing duration information")
        
        if len(self.faqs) < 3:
            result.add_warning("Consider adding more FAQs (recommended: 5+ questions)")
        
        return result
    
    def validate_and_show_results(self):
        """Validate data and show results to user"""
        result = self.validate_data()
        
        if result.is_valid:
            msg = f"✅ Services & FAQ validation passed!\n\n"
            msg += f"• Services: {len(self.services)}\n"
            msg += f"• FAQs: {len(self.faqs)}\n"
            msg += f"• All data is valid\n"
            
            if result.warnings:
                msg += f"• Warnings: {len(result.warnings)}\n"
                
                # Show detailed warnings
                detailed_msg = msg + "\n" + "\n".join([f"⚠️ {w}" for w in result.warnings])
                msgbox = QMessageBox(self)
                msgbox.setWindowTitle("Validation Results")
                msgbox.setText(msg)
                msgbox.setDetailedText(detailed_msg)
                msgbox.exec()
            else:
                QMessageBox.information(self, "Validation Success", msg)
        else:
            msg = f"❌ Services & FAQ validation failed!\n\n"
            msg += f"• Services: {len(self.services)}\n"
            msg += f"• FAQs: {len(self.faqs)}\n"
            msg += f"• Errors: {len(result.errors)}\n"
            
            if result.warnings:
                msg += f"• Warnings: {len(result.warnings)}\n"
            
            # Show detailed errors and warnings
            details = []
            details.extend([f"❌ {e}" for e in result.errors])
            details.extend([f"⚠️ {w}" for w in result.warnings])
            
            detailed_msg = msg + "\n" + "\n".join(details)
            msgbox = QMessageBox(self)
            msgbox.setWindowTitle("Validation Results")
            msgbox.setText(msg)
            msgbox.setDetailedText(detailed_msg)
            msgbox.exec()
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get services and FAQ configuration data"""
        return {
            "services": [service.to_dict() for service in self.services],
            "faq": [faq.to_dict() for faq in self.faqs]
        }
    
    def set_config_data(self, data: Dict[str, Any]):
        """Set services and FAQ configuration data"""
        # Load services
        services_data = data.get("services", [])
        self.services = [Service.from_dict(s) for s in services_data]
        
        # Load FAQs
        faq_data = data.get("faq", [])
        self.faqs = [FAQ.from_dict(f) for f in faq_data]
        
        # Refresh displays
        self._refresh_services_table()
        self._refresh_faq_table()
        self._update_services_count()
        self._update_faq_count()
        
        # Clear forms
        self._clear_service_form()
        self._clear_faq_form()
        self._reset_add_service_button()
        self._reset_add_faq_button()
        
        # Emit data loaded signal
        self.data_loaded.emit()
    
    def clear_data(self):
        """Clear all services and FAQ data"""
        self.services.clear()
        self.faqs.clear()
        
        self._refresh_services_table()
        self._refresh_faq_table()
        self._update_services_count()
        self._update_faq_count()
        
        self._clear_service_form()
        self._clear_faq_form()
        self._reset_add_service_button()
        self._reset_add_faq_button()
        
        # Clear search filters
        self.services_search_input.clear()
        self.faq_search_input.clear()
        
        self.has_changes = False
    
    def _emit_config_changed(self):
        """Helper method to emit config changed signal"""
        self.has_changes = True
        self.config_changed.emit()
        
        # Update window title to show unsaved changes (*) - if method exists
        parent_window = self.window()
        if parent_window and hasattr(parent_window, 'update_title_with_changes'):
            try:
                getattr(parent_window, 'update_title_with_changes')()
            except Exception:
                pass  # Silently ignore if method call fails"""
Filename: services_tab.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\content_tabs\\services_tab.py
Description: Services management tab with manual entry, categories, and FAQ integration
Handles service catalog management with detailed descriptions and pricing information

Version: 1.0.0
Date: 2025-08-11
Author: Cloud Stack Generator Team
"""

import json
from typing import Dict, Any, List, Tuple, Optional
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                            QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                            QMessageBox, QGroupBox, QComboBox, QTextEdit, 
                            QHeaderView, QAbstractItemView, QFrame, QSpinBox,
                            QCheckBox, QTabWidget, QWidget, QSplitter)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt, pyqtSignal
from ..components.base_tab import BaseTab


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
    def __init__(self, name: str = "", description: str = "", category: str = "", 
                 price_range: str = "", duration: str = "", features: List[str] = None):
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
            "features": self.features
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Service':
        """Create from dictionary"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", ""),
            price_range=data.get("price_range", ""),
            duration=data.get("duration", ""),
            features=data.get("features", [])
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


class FAQ:
    """FAQ data model"""
    def __init__(self, question: str = "", answer: str = "", category: str = "General"):
        self.question = question
        self.answer = answer
        self.category = category
    
    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            "question": self.question,
            "answer": self.answer,
            "category": self.category
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> 'FAQ':
        """Create from dictionary"""
        return cls(
            question=data.get("question", ""),
            answer=data.get("answer", ""),
            category=data.get("category", "General")
        )
    
    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate FAQ data"""
        errors = []
        if not self.question.strip():
            errors.append("Question is required")
        if not self.answer.strip():
            errors.append("Answer is required")
        return len(errors) == 0, errors


class ServicesTab(BaseTab):
    """Tab for services and FAQ management"""
    
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
        "Custom Services"
    ]
    
    # FAQ categories
    FAQ_CATEGORIES = [
        "General",
        "Services", 
        "Pricing",
        "Support",
        "Process",
        "Technical"
    ]
    
    def __init__(self, parent=None):
        self.services: List[Service] = []
        self.faqs: List[FAQ] = []
        self.has_changes = False
        super().__init__(parent)
    
    def setup_ui(self):
        """Setup services and FAQ management UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        
        # Create main tab widget
        self.main_tabs = QTabWidget()
        
        # Services tab
        services_widget = QWidget()
        self._setup_services_tab(services_widget)
        self.main_tabs.addTab(services_widget, "🔧 Services")
        
        # FAQ tab
        faq_widget = QWidget()
        self._setup_faq_tab(faq_widget)
        self.main_tabs.addTab(faq_widget, "❓ FAQ")
        
        main_layout.addWidget(self.main_tabs)
        self.setLayout(main_layout)
    
    def _setup_services_tab(self, parent_widget: QWidget):
        """Setup services management tab"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Create services sections
        self._create_services_table_section(layout)
        self._create_service_entry_section(layout)
        self._create_services_actions_section(layout)
        
        parent_widget.setLayout(layout)
    
    def _setup_faq_tab(self, parent_widget: QWidget):
        """Setup FAQ management tab"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Create FAQ sections
        self._create_faq_table_section(layout)
        self._create_faq_entry_section(layout)
        self._create_faq_actions_section(layout)
        
        parent_widget.setLayout(layout)
    
    def _create_services_table_section(self, parent_layout: QVBoxLayout):
        """Create services table section"""
        # Section header
        header_label = self._create_section_header("🔧 Services Catalog")
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
        self.services_table.setColumnCount(6)  # Name, Category, Price, Duration, Description, Actions
        headers = ["Service Name", "Category", "Price Range", "Duration", "Description", "Actions"]
        self.services_table.setHorizontalHeaderLabels(headers)
        
        # Table settings
        self.services_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.services_table.setAlternatingRowColors(True)
        self.services_table.setSortingEnabled(True)
        
        # Set column widths
        header = self.services_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)   # Category
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)   # Price
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)   # Duration
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch) # Description
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)   # Actions
        
        self.services_table.setColumnWidth(1, 130)  # Category
        self.services_table.setColumnWidth(2, 100)  # Price
        self.services_table.setColumnWidth(3, 80)   # Duration
        self.services_table.setColumnWidth(5, 80)   # Actions
        
        table_layout.addLayout(controls_layout)
        table_layout.addWidget(self.services_table)
        
        table_group.setLayout(table_layout)
        parent_layout.addWidget(table_group)
    
    def _create_service_entry_section(self, parent_layout: QVBoxLayout):
        """Create service entry section"""
        # Section header
        header_label = self._create_section_header("➕ Add/Edit Service")
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
        self.service_inputs["category"].currentTextChanged.connect(self._emit_config_changed)
        
        # Row 2: Price Range and Duration
        price_label = QLabel("Price Range:")
        price_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["price_range"] = QLineEdit()
        self.service_inputs["price_range"].setPlaceholderText("$100-$500 or Contact for quote")
        self.service_inputs["price_range"].textChanged.connect(self._emit_config_changed)
        
        duration_label = QLabel("Duration:")
        duration_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["duration"] = QLineEdit()
        self.service_inputs["duration"].setPlaceholderText("1-2 hours, 1 week, etc.")
        self.service_inputs["duration"].textChanged.connect(self._emit_config_changed)
        
        # Row 3: Description (spans all columns)
        desc_label = QLabel("* Description:")
        desc_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["description"] = QTextEdit()
        self.service_inputs["description"].setPlaceholderText("Detailed service description (max 1000 characters)")
        self.service_inputs["description"].setMaximumHeight(100)
        self.service_inputs["description"].textChanged.connect(self._emit_config_changed)
        
        # Character counter for description
        self.service_desc_counter = QLabel("0/1000")
        self.service_desc_counter.setFont(QFont("Arial", 8))
        self.service_desc_counter.setStyleSheet("color: #7f8c8d;")
        self.service_inputs["description"].textChanged.connect(self._update_service_description_counter)
        
        # Features section
        features_label = QLabel("Key Features:")
        features_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.service_inputs["features"] = QTextEdit()
        self.service_inputs["features"].setPlaceholderText("Enter key features (one per line)")
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
        entry_layout.addWidget(self.service_desc_counter, 3, 3, Qt.AlignmentFlag.AlignRight)
        
        entry_layout.addWidget(features_label, 4, 0)
        entry_layout.addWidget(self.service_inputs["features"], 4, 1, 1, 3)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.add_service_btn = QPushButton("➕ Add Service")
        self.add_service_btn.setStyleSheet("""
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
        """)
        self.add_service_btn.clicked.connect(self._add_service)
        
        self.clear_service_form_btn = QPushButton("🗑️ Clear Form")
        self.clear_service_form_btn.clicked.connect(self._clear_service_form)
        
        self.validate_service_btn = QPushButton("✅ Validate")
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
        
        self.delete_selected_services_btn = QPushButton("🗑️ Delete Selected")
        self.delete_selected_services_btn.setStyleSheet("""
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
        """)
        self.delete_selected_services_btn.clicked.connect(self._delete