"""
Filename: products_tab.py
Path: E:\\projects\\cloud-stack-generator\\src\\ui\\content_tabs\\products_tab.py
Description: Products management tab with CSV upload, validation, and individual product editing
Handles product catalog management with bulk import and manual entry capabilities

Version: 1.0.0
Date: 2025-08-11
Author: Cloud Stack Generator Team
"""

import csv
import os
import chardet
from typing import Dict, Any, List, Tuple
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

# Import error logging
from ...utils import log_file_operation_error


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


class Product:
    """Product data model"""

    def __init__(
        self,
        sku: str = "",
        name: str = "",
        description: str = "",
        category: str = "",
        price: str = "",
        image_url: str = "",
    ):
        self.sku = sku
        self.name = name
        self.description = description
        self.category = category
        self.price = price
        self.image_url = image_url

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "image_url": self.image_url,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "Product":
        """Create from dictionary"""
        return cls(
            sku=data.get("sku", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            category=data.get("category", ""),
            price=data.get("price", ""),
            image_url=data.get("image_url", ""),
        )

    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate product data"""
        errors = []
        if not self.sku.strip():
            errors.append("SKU is required")
        if not self.name.strip():
            errors.append("Product name is required")
        if len(self.description) > 500:
            errors.append("Description too long (max 500 characters)")
        return len(errors) == 0, errors


class CSVImportDialog(QMessageBox):
    """Dialog for CSV import results"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("CSV Import Results")
        self.setIcon(QMessageBox.Icon.Information)


class ProductsTab(BaseTab):
    """Tab for products management with CSV upload and manual editing"""

    # Signals
    config_changed = pyqtSignal()
    validation_requested = pyqtSignal()
    data_loaded = pyqtSignal()

    # Product categories
    PRODUCT_CATEGORIES = [
        "General",
        "Electronics",
        "Clothing & Apparel",
        "Home & Garden",
        "Sports & Outdoors",
        "Automotive",
        "Health & Beauty",
        "Books & Media",
        "Toys & Games",
        "Food & Beverages",
        "Industrial",
        "Professional Services",
        "Portable Toilet Supplier",
        "Custom Category",
    ]

    def __init__(self, parent=None):
        self.products: List[Product] = []
        self.products_table = None
        self.error_labels = {}
        self.has_changes = False
        self.current_file_path = ""
        super().__init__(parent)

    def setup_ui(self):
        """Setup products management UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Create main sections
        self._create_import_section(main_layout)
        self._create_products_table_section(main_layout)
        self._create_manual_entry_section(main_layout)
        self._create_actions_section(main_layout)

        self.setLayout(main_layout)

    def _create_import_section(self, parent_layout: QVBoxLayout):
        """Create CSV import section"""
        # Section header
        header_label = self._create_section_header("📂 CSV Import & Export")
        parent_layout.addWidget(header_label)

        # Import group
        import_group = QGroupBox()
        import_layout = QGridLayout()
        import_layout.setSpacing(10)

        # File selection
        file_label = QLabel("CSV File:")
        file_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("Select CSV file to import products...")
        self.file_path_input.setReadOnly(True)

        self.browse_btn = QPushButton("📁 Browse")
        self.browse_btn.clicked.connect(self._browse_csv_file)

        # Import controls
        self.import_btn = QPushButton("📤 Import CSV")
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

        self.validate_csv_btn = QPushButton("✅ Validate CSV")
        self.validate_csv_btn.clicked.connect(self._validate_csv_file)
        self.validate_csv_btn.setEnabled(False)

        # Export controls
        self.export_btn = QPushButton("📥 Export CSV")
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
        self.import_status = QLabel("Ready to import products from CSV")
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

    def _create_products_table_section(self, parent_layout: QVBoxLayout):
        """Create products table section"""
        # Section header
        header_label = self._create_section_header("📦 Products Catalog")
        parent_layout.addWidget(header_label)

        # Table group
        table_group = QGroupBox()
        table_layout = QVBoxLayout()

        # Products count and search
        controls_layout = QHBoxLayout()

        self.products_count_label = QLabel("Products: 0")
        self.products_count_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        # Search functionality
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by SKU, name, or category...")
        self.search_input.setMaximumWidth(250)
        self.search_input.textChanged.connect(self._filter_products)

        controls_layout.addWidget(self.products_count_label)
        controls_layout.addStretch()
        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.search_input)

        # Products table
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(
            7
        )  # SKU, Name, Category, Price, Description, Image, Actions
        headers = [
            "SKU",
            "Name",
            "Category",
            "Price",
            "Description",
            "Image URL",
            "Actions",
        ]
        self.products_table.setHorizontalHeaderLabels(headers)

        # Table settings
        self.products_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSortingEnabled(True)

        # Set column widths
        header = self.products_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # SKU
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Category
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)  # Price
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)  # Description
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)  # Image
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)  # Actions

        self.products_table.setColumnWidth(0, 100)  # SKU
        self.products_table.setColumnWidth(2, 120)  # Category
        self.products_table.setColumnWidth(3, 80)  # Price
        self.products_table.setColumnWidth(5, 100)  # Image
        self.products_table.setColumnWidth(6, 80)  # Actions

        table_layout.addLayout(controls_layout)
        table_layout.addWidget(self.products_table)

        table_group.setLayout(table_layout)
        parent_layout.addWidget(table_group)

    def _create_manual_entry_section(self, parent_layout: QVBoxLayout):
        """Create manual product entry section"""
        # Section header
        header_label = self._create_section_header("➕ Add/Edit Product")
        parent_layout.addWidget(header_label)

        # Manual entry group
        entry_group = QGroupBox()
        entry_layout = QGridLayout()
        entry_layout.setSpacing(10)

        # Product form fields
        self.product_inputs = {}

        # Row 1: SKU and Name
        sku_label = QLabel("* SKU:")
        sku_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.product_inputs["sku"] = QLineEdit()
        self.product_inputs["sku"].setPlaceholderText("Unique product identifier")
        self.product_inputs["sku"].textChanged.connect(self._emit_config_changed)

        name_label = QLabel("* Name:")
        name_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.product_inputs["name"] = QLineEdit()
        self.product_inputs["name"].setPlaceholderText("Product name")
        self.product_inputs["name"].textChanged.connect(self._emit_config_changed)

        # Row 2: Category and Price
        category_label = QLabel("Category:")
        category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.product_inputs["category"] = QComboBox()
        self.product_inputs["category"].addItems(self.PRODUCT_CATEGORIES)
        self.product_inputs["category"].setEditable(True)  # Allow custom categories
        self.product_inputs["category"].currentTextChanged.connect(
            self._emit_config_changed
        )

        price_label = QLabel("Price:")
        price_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.product_inputs["price"] = QLineEdit()
        self.product_inputs["price"].setPlaceholderText("$99.99 or price range")
        self.product_inputs["price"].textChanged.connect(self._emit_config_changed)

        # Row 3: Image URL
        image_label = QLabel("Image URL:")
        image_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.product_inputs["image_url"] = QLineEdit()
        self.product_inputs["image_url"].setPlaceholderText(
            "https://example.com/product-image.jpg"
        )
        self.product_inputs["image_url"].textChanged.connect(self._emit_config_changed)

        # Row 4: Description (spans multiple columns)
        desc_label = QLabel("Description:")
        desc_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.product_inputs["description"] = QTextEdit()
        self.product_inputs["description"].setPlaceholderText(
            "Product description (max 500 characters)"
        )
        self.product_inputs["description"].setMaximumHeight(80)
        self.product_inputs["description"].textChanged.connect(
            self._emit_config_changed
        )

        # Character counter for description
        self.desc_counter = QLabel("0/500")
        self.desc_counter.setFont(QFont("Arial", 8))
        self.desc_counter.setStyleSheet("color: #7f8c8d;")
        self.product_inputs["description"].textChanged.connect(
            self._update_description_counter
        )

        # Entry form layout
        entry_layout.addWidget(sku_label, 0, 0)
        entry_layout.addWidget(self.product_inputs["sku"], 0, 1)
        entry_layout.addWidget(name_label, 0, 2)
        entry_layout.addWidget(self.product_inputs["name"], 0, 3)

        entry_layout.addWidget(category_label, 1, 0)
        entry_layout.addWidget(self.product_inputs["category"], 1, 1)
        entry_layout.addWidget(price_label, 1, 2)
        entry_layout.addWidget(self.product_inputs["price"], 1, 3)

        entry_layout.addWidget(image_label, 2, 0)
        entry_layout.addWidget(self.product_inputs["image_url"], 2, 1, 1, 3)

        entry_layout.addWidget(desc_label, 3, 0)
        entry_layout.addWidget(self.product_inputs["description"], 3, 1, 1, 3)
        entry_layout.addWidget(self.desc_counter, 4, 3, Qt.AlignmentFlag.AlignRight)

        # Action buttons
        actions_layout = QHBoxLayout()

        self.add_product_btn = QPushButton("➕ Add Product")
        self.add_product_btn.setStyleSheet(
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
        self.add_product_btn.clicked.connect(self._add_product)

        self.clear_form_btn = QPushButton("🗑️ Clear Form")
        self.clear_form_btn.clicked.connect(self._clear_product_form)

        self.validate_product_btn = QPushButton("✅ Validate")
        self.validate_product_btn.clicked.connect(self._validate_current_product)

        actions_layout.addWidget(self.add_product_btn)
        actions_layout.addWidget(self.clear_form_btn)
        actions_layout.addWidget(self.validate_product_btn)
        actions_layout.addStretch()

        entry_layout.addLayout(actions_layout, 5, 0, 1, 4)

        entry_group.setLayout(entry_layout)
        parent_layout.addWidget(entry_group)

    def _create_actions_section(self, parent_layout: QVBoxLayout):
        """Create actions section"""
        # Separator
        separator = self._create_separator()
        parent_layout.addWidget(separator)

        # Actions layout
        actions_layout = QHBoxLayout()

        # Bulk actions
        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self._select_all_products)

        self.delete_selected_btn = QPushButton("🗑️ Delete Selected")
        self.delete_selected_btn.setStyleSheet(
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
        self.delete_selected_btn.clicked.connect(self._delete_selected_products)

        # Validation
        self.validate_all_btn = QPushButton("🔍 Validate All Products")
        self.validate_all_btn.setStyleSheet(
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
        self.validate_all_btn.clicked.connect(self.validate_and_show_results)

        actions_layout.addWidget(self.select_all_btn)
        actions_layout.addWidget(self.delete_selected_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.validate_all_btn)

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

    def _browse_csv_file(self):
        """Browse for CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Products CSV File", "", "CSV Files (*.csv);;All Files (*)"
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
            with open(file_path, 'rb') as f:
                raw_data = f.read(10000)  # Read first 10KB for detection
                
            if raw_data:
                # Use chardet to detect encoding
                result = chardet.detect(raw_data)
                encoding = result.get('encoding', 'utf-8').lower()
                confidence = result.get('confidence', 0)
                
                print(f"DEBUG: Detected encoding: {encoding} (confidence: {confidence:.2f})")
                
                # Map common encoding variations
                encoding_map = {
                    'windows-1252': 'cp1252',
                    'iso-8859-1': 'latin1', 
                    'ascii': 'utf-8'
                }
                
                encoding = encoding_map.get(encoding, encoding)
                
                # If confidence is low, try common fallbacks
                if confidence < 0.7:
                    fallback_encodings = ['utf-8', 'cp1252', 'latin1', 'utf-16']
                    for fallback in fallback_encodings:
                        try:
                            with open(file_path, 'r', encoding=fallback) as f:
                                f.read(1000)  # Try to read some content
                            print(f"DEBUG: Using fallback encoding: {fallback}")
                            return fallback
                        except (UnicodeDecodeError, UnicodeError):
                            continue
                
                return encoding
            
        except Exception as e:
            print(f"DEBUG: Error detecting encoding: {e}")
        
        # Default fallback
        return 'utf-8'

    def _validate_csv_file(self):
        """Validate CSV file structure with automatic encoding detection"""
        if not self.current_file_path:
            return

        try:
            # Detect file encoding
            encoding = self._detect_file_encoding(self.current_file_path)
            print(f"DEBUG: Using encoding {encoding} for CSV validation")
            
            with open(self.current_file_path, "r", encoding=encoding, errors='replace') as file:
                reader = csv.DictReader(file)

                # Check required columns
                required_columns = ["SKU", "Name"]
                optional_columns = ["Description", "Category", "Price", "Image URL"]

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

                # Count rows and validate each product
                rows = list(reader)
                row_count = len(rows)
                
                validation_errors = []
                validation_warnings = []
                valid_products = 0

                # Check for duplicates in CSV file
                skus = [row.get("SKU", "").strip() for row in rows]
                duplicate_skus = [sku for sku in set(skus) if skus.count(sku) > 1]
                
                for row_num, row in enumerate(rows, start=2):  # Start at 2 for header
                    try:
                        # Create temporary product for validation
                        product = Product(
                            sku=row.get("SKU", "").strip(),
                            name=row.get("Name", "").strip(),
                            description=row.get("Description", "").strip(),
                            category=row.get("Category", "General").strip(),
                            price=row.get("Price", "").strip(),
                            image_url=row.get("Image URL", "").strip(),
                        )

                        # Validate product data
                        is_valid, product_errors = product.is_valid()
                        if not is_valid:
                            validation_errors.extend(
                                [f"Row {row_num}: {error}" for error in product_errors]
                            )
                        else:
                            valid_products += 1
                            
                        # Check for existing SKU in current products
                        if any(p.sku == product.sku for p in self.products):
                            validation_warnings.append(
                                f"Row {row_num}: SKU '{product.sku}' already exists in current products"
                            )

                    except Exception as e:
                        validation_errors.append(f"Row {row_num}: {str(e)}")

                # Add CSV duplicate warnings
                for sku in duplicate_skus:
                    if sku:  # Only warn about non-empty SKUs
                        validation_warnings.append(f"SKU '{sku}' appears multiple times in CSV file")

                # Show comprehensive validation results
                if validation_errors:
                    msg = "❌ CSV Validation Failed!\n\n"
                    msg += f"• Total rows: {row_count}\n"
                    msg += f"• Valid products: {valid_products}\n"
                    msg += f"• Errors: {len(validation_errors)}\n"
                    
                    if validation_warnings:
                        msg += f"• Warnings: {len(validation_warnings)}\n"
                    
                    detailed_msg = msg + "\n\nERRORS:\n" + "\n".join(validation_errors)
                    if validation_warnings:
                        detailed_msg += "\n\nWARNINGS:\n" + "\n".join(validation_warnings)
                    
                    msgbox = QMessageBox(self)
                    msgbox.setWindowTitle("CSV Validation Failed")
                    msgbox.setIcon(QMessageBox.Icon.Warning)
                    msgbox.setText(msg)
                    msgbox.setDetailedText(detailed_msg)
                    msgbox.exec()
                    
                    self._update_import_status(f"❌ Validation failed - {len(validation_errors)} errors found")
                    
                elif validation_warnings:
                    msg = "⚠️ CSV Validation Passed with Warnings!\n\n"
                    msg += f"• Total rows: {row_count}\n"
                    msg += f"• Valid products: {valid_products}\n"
                    msg += f"• Warnings: {len(validation_warnings)}\n"
                    
                    detailed_msg = msg + "\n\nWARNINGS:\n" + "\n".join(validation_warnings)
                    
                    msgbox = QMessageBox(self)
                    msgbox.setWindowTitle("CSV Validation - Warnings Found")
                    msgbox.setIcon(QMessageBox.Icon.Information)
                    msgbox.setText(msg)
                    msgbox.setDetailedText(detailed_msg)
                    msgbox.exec()
                    
                    self._update_import_status(f"⚠️ Valid CSV with {len(validation_warnings)} warnings - {valid_products} products ready")
                    
                else:
                    msg = "✅ CSV Validation Successful!\n\n"
                    msg += f"• Total rows: {row_count}\n"
                    msg += f"• Valid products: {valid_products}\n"
                    msg += f"• Required columns: {', '.join(required_columns)} ✅\n"
                    msg += f"• Optional columns found: {', '.join(available_optional)}"

                    QMessageBox.information(self, "CSV Validation Results", msg)
                    self._update_import_status(f"✅ Valid CSV - {valid_products} products ready to import")

        except Exception as e:
            error_msg = f"Error reading CSV file:\n{str(e)}"
            log_file_operation_error(
                operation="validate_csv",
                file_path=self.current_file_path or "unknown",
                error_message=error_msg,
                exception=e
            )
            QMessageBox.critical(
                self, "CSV Validation Error", error_msg
            )

    def _import_csv(self):
        """Import products from CSV file"""
        if not self.current_file_path:
            return

        try:
            self.import_progress.show()
            self.import_progress.setRange(0, 0)  # Indeterminate progress

            imported_products = []
            errors = []
            warnings = []

            # Detect file encoding
            encoding = self._detect_file_encoding(self.current_file_path)
            print(f"DEBUG: Using encoding {encoding} for CSV import")
            
            with open(self.current_file_path, "r", encoding=encoding, errors='replace') as file:
                reader = csv.DictReader(file)

                for row_num, row in enumerate(reader, start=2):  # Start at 2 for header
                    try:
                        product = Product(
                            sku=row.get("SKU", "").strip(),
                            name=row.get("Name", "").strip(),
                            description=row.get("Description", "").strip(),
                            category=row.get("Category", "General").strip(),
                            price=row.get("Price", "").strip(),
                            image_url=row.get("Image URL", "").strip(),
                        )

                        # Validate product
                        is_valid, product_errors = product.is_valid()
                        if not is_valid:
                            errors.extend(
                                [f"Row {row_num}: {error}" for error in product_errors]
                            )
                            continue

                        # Check for duplicate SKU
                        if any(p.sku == product.sku for p in self.products):
                            warnings.append(
                                f"Row {row_num}: SKU '{product.sku}' already exists (skipped)"
                            )
                            continue

                        imported_products.append(product)

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")

            # Add imported products
            self.products.extend(imported_products)
            self._refresh_products_table()
            self._update_products_count()

            self.import_progress.hide()

            # Show import results
            msg = "Import completed!\n\n"
            msg += f"• Successfully imported: {len(imported_products)} products\n"

            if warnings:
                msg += f"• Warnings: {len(warnings)}\n"
            if errors:
                msg += f"• Errors: {len(errors)}\n"

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

            self._update_import_status(f"✅ Imported {len(imported_products)} products")
            self._emit_config_changed()

        except Exception as e:
            self.import_progress.hide()
            error_msg = f"Error importing CSV:\n{str(e)}"
            log_file_operation_error(
                operation="import_csv",
                file_path=self.current_file_path,
                error_message=error_msg,
                exception=e
            )
            QMessageBox.critical(
                self, "Import Error", error_msg
            )

    def _export_csv(self):
        """Export products to CSV file"""
        if not self.products:
            QMessageBox.information(self, "Export", "No products to export")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Products CSV",
            "products_export.csv",
            "CSV Files (*.csv);;All Files (*)",
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                fieldnames = [
                    "SKU",
                    "Name",
                    "Description",
                    "Category",
                    "Price",
                    "Image URL",
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()
                for product in self.products:
                    writer.writerow(
                        {
                            "SKU": product.sku,
                            "Name": product.name,
                            "Description": product.description,
                            "Category": product.category,
                            "Price": product.price,
                            "Image URL": product.image_url,
                        }
                    )

            QMessageBox.information(
                self,
                "Export Success",
                f"Successfully exported {len(self.products)} products to:\n{file_path}",
            )

        except Exception as e:
            QMessageBox.critical(
                self, "Export Error", f"Error exporting CSV:\n{str(e)}"
            )

    def _add_product(self):
        """Add product from manual entry form"""
        # Get form data
        product = Product(
            sku=self.product_inputs["sku"].text().strip(),
            name=self.product_inputs["name"].text().strip(),
            description=self.product_inputs["description"].toPlainText().strip(),
            category=self.product_inputs["category"].currentText().strip(),
            price=self.product_inputs["price"].text().strip(),
            image_url=self.product_inputs["image_url"].text().strip(),
        )

        # Validate product
        is_valid, errors = product.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Check for duplicate SKU
        if any(p.sku == product.sku for p in self.products):
            QMessageBox.warning(
                self,
                "Duplicate SKU",
                f"Product with SKU '{product.sku}' already exists",
            )
            return

        # Add product
        self.products.append(product)
        self._refresh_products_table()
        self._update_products_count()
        self._clear_product_form()
        self._emit_config_changed()

        QMessageBox.information(
            self, "Product Added", f"Successfully added product: {product.name}"
        )

    def _clear_product_form(self):
        """Clear the product entry form"""
        self.product_inputs["sku"].clear()
        self.product_inputs["name"].clear()
        self.product_inputs["description"].clear()
        self.product_inputs["category"].setCurrentIndex(0)
        self.product_inputs["price"].clear()
        self.product_inputs["image_url"].clear()
        self._update_description_counter()

    def _validate_current_product(self):
        """Validate current product in form"""
        product = Product(
            sku=self.product_inputs["sku"].text().strip(),
            name=self.product_inputs["name"].text().strip(),
            description=self.product_inputs["description"].toPlainText().strip(),
            category=self.product_inputs["category"].currentText().strip(),
            price=self.product_inputs["price"].text().strip(),
            image_url=self.product_inputs["image_url"].text().strip(),
        )

        is_valid, errors = product.is_valid()

        if is_valid:
            QMessageBox.information(
                self, "Validation Success", "✅ Product data is valid!"
            )
        else:
            QMessageBox.warning(
                self, "Validation Errors", "\n".join([f"• {error}" for error in errors])
            )

    def _refresh_products_table(self):
        """Refresh the products table display"""
        self.products_table.setRowCount(len(self.products))

        for row, product in enumerate(self.products):
            # SKU
            self.products_table.setItem(row, 0, QTableWidgetItem(product.sku))

            # Name
            self.products_table.setItem(row, 1, QTableWidgetItem(product.name))

            # Category
            self.products_table.setItem(row, 2, QTableWidgetItem(product.category))

            # Price
            self.products_table.setItem(row, 3, QTableWidgetItem(product.price))

            # Description (truncated)
            desc_text = (
                product.description[:50] + "..."
                if len(product.description) > 50
                else product.description
            )
            self.products_table.setItem(row, 4, QTableWidgetItem(desc_text))

            # Image URL (truncated)
            image_text = (
                product.image_url[:30] + "..."
                if len(product.image_url) > 30
                else product.image_url
            )
            self.products_table.setItem(row, 5, QTableWidgetItem(image_text))

            # Actions
            actions_btn = QPushButton("✏️ Edit")
            actions_btn.setMaximumWidth(60)
            actions_btn.clicked.connect(lambda checked, r=row: self._edit_product(r))
            self.products_table.setCellWidget(row, 6, actions_btn)

    def _filter_products(self):
        """Filter products table based on search input"""
        search_text = self.search_input.text().lower()

        for row in range(self.products_table.rowCount()):
            match = False
            for col in range(3):  # Search SKU, Name, Category
                item = self.products_table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break

            self.products_table.setRowHidden(row, not match)

    def _update_products_count(self):
        """Update products count label"""
        visible_count = sum(
            1
            for row in range(self.products_table.rowCount())
            if not self.products_table.isRowHidden(row)
        )
        total_count = len(self.products)

        if visible_count == total_count:
            self.products_count_label.setText(f"Products: {total_count}")
        else:
            self.products_count_label.setText(
                f"Products: {visible_count}/{total_count}"
            )

    def _update_description_counter(self):
        """Update description character counter with green (<=500) or red (>500)"""
        text = self.product_inputs["description"].toPlainText()
        count = len(text)
        self.desc_counter.setText(f"{count}/500")

        # Color coding: Green if <=500, Red if >500
        if count > 500:
            self.desc_counter.setStyleSheet("color: #e74c3c; font-weight: bold;")  # Red
        else:
            self.desc_counter.setStyleSheet("color: #27ae60; font-weight: bold;")  # Green

    def _update_import_status(self, message: str):
        """Update import status label"""
        self.import_status.setText(message)

    def _edit_product(self, row: int):
        """Edit product at specified row"""
        if 0 <= row < len(self.products):
            product = self.products[row]

            # Load product into form
            self.product_inputs["sku"].setText(product.sku)
            self.product_inputs["name"].setText(product.name)
            self.product_inputs["description"].setPlainText(product.description)

            # Set category
            category_index = self.product_inputs["category"].findText(product.category)
            if category_index >= 0:
                self.product_inputs["category"].setCurrentIndex(category_index)
            else:
                self.product_inputs["category"].setCurrentText(product.category)

            self.product_inputs["price"].setText(product.price)
            self.product_inputs["image_url"].setText(product.image_url)

            # Change button to update mode
            self.add_product_btn.setText("💾 Update Product")
            try:
                self.add_product_btn.clicked.disconnect()
            except TypeError:
                pass  # No connections to disconnect
            self.add_product_btn.clicked.connect(lambda: self._update_product(row))

    def _update_product(self, row: int):
        """Update product at specified row"""
        # Get form data
        updated_product = Product(
            sku=self.product_inputs["sku"].text().strip(),
            name=self.product_inputs["name"].text().strip(),
            description=self.product_inputs["description"].toPlainText().strip(),
            category=self.product_inputs["category"].currentText().strip(),
            price=self.product_inputs["price"].text().strip(),
            image_url=self.product_inputs["image_url"].text().strip(),
        )

        # Validate product
        is_valid, errors = updated_product.is_valid()
        if not is_valid:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Check for duplicate SKU (excluding current product)
        for i, p in enumerate(self.products):
            if i != row and p.sku == updated_product.sku:
                QMessageBox.warning(
                    self,
                    "Duplicate SKU",
                    f"Product with SKU '{updated_product.sku}' already exists",
                )
                return

        # Update product
        self.products[row] = updated_product
        self._refresh_products_table()
        self._clear_product_form()
        self._reset_add_button()
        self._emit_config_changed()

        QMessageBox.information(
            self,
            "Product Updated",
            f"Successfully updated product: {updated_product.name}",
        )

    def _reset_add_button(self):
        """Reset add button to add mode"""
        self.add_product_btn.setText("➕ Add Product")
        try:
            self.add_product_btn.clicked.disconnect()
        except TypeError:
            pass  # No connections to disconnect
        self.add_product_btn.clicked.connect(self._add_product)

    def _select_all_products(self):
        """Select all products in table"""
        self.products_table.selectAll()

    def _delete_selected_products(self):
        """Delete selected products"""
        selected_rows = set()
        for item in self.products_table.selectedItems():
            selected_rows.add(item.row())

        if not selected_rows:
            QMessageBox.information(
                self, "No Selection", "Please select products to delete"
            )
            return

        # Confirm deletion
        count = len(selected_rows)
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Are you sure you want to delete {count} selected product(s)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Remove products (in reverse order to maintain indices)
            for row in sorted(selected_rows, reverse=True):
                if 0 <= row < len(self.products):
                    del self.products[row]

            self._refresh_products_table()
            self._update_products_count()
            self._emit_config_changed()

            QMessageBox.information(
                self, "Deletion Complete", f"Successfully deleted {count} product(s)"
            )

    def connect_signals(self):
        """Connect UI signals to emit config_changed"""
        # Signals already connected in individual widgets
        pass

    def get_required_fields(self) -> List[str]:
        """Get list of required field names"""
        return (
            []
        )  # No required fields at tab level (individual products have requirements)

    def validate_data(self) -> ValidationResult:
        """Validate all products data"""
        result = ValidationResult()

        if not self.products:
            result.add_warning("No products defined")
            return result

        # Validate each product
        for i, product in enumerate(self.products):
            is_valid, errors = product.is_valid()
            if not is_valid:
                for error in errors:
                    result.add_error(f"Product {i+1} ({product.sku}): {error}")

        # Check for duplicate SKUs
        skus = [p.sku for p in self.products]
        duplicates = []
        for i, sku in enumerate(skus):
            if skus.count(sku) > 1 and sku not in duplicates:
                duplicates.append(sku)

        for sku in duplicates:
            result.add_error(f"Duplicate SKU found: {sku}")

        # Warnings for best practices
        if len(self.products) > 100:
            result.add_warning(
                f"Large product catalog ({len(self.products)} products) - consider categorization"
            )

        products_without_images = sum(
            1 for p in self.products if not p.image_url.strip()
        )
        if products_without_images > 0:
            result.add_warning(f"{products_without_images} products missing image URLs")

        products_without_descriptions = sum(
            1 for p in self.products if not p.description.strip()
        )
        if products_without_descriptions > 0:
            result.add_warning(
                f"{products_without_descriptions} products missing descriptions"
            )

        return result

    def validate_and_show_results(self):
        """Validate data and show results to user"""
        result = self.validate_data()

        if result.is_valid:
            msg = "✅ Products validation passed!\n\n"
            msg += f"• Total products: {len(self.products)}\n"
            msg += "• All products have valid data\n"

            if result.warnings:
                msg += f"• Warnings: {len(result.warnings)}\n"

                # Show detailed warnings
                detailed_msg = (
                    msg + "\n" + "\n".join([f"⚠️ {w}" for w in result.warnings])
                )
                msgbox = QMessageBox(self)
                msgbox.setWindowTitle("Validation Results")
                msgbox.setText(msg)
                msgbox.setDetailedText(detailed_msg)
                msgbox.exec()
            else:
                QMessageBox.information(self, "Validation Success", msg)
        else:
            msg = "❌ Products validation failed!\n\n"
            msg += f"• Total products: {len(self.products)}\n"
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
        """Get products configuration data"""
        return {"products": [product.to_dict() for product in self.products]}

    def set_config_data(self, data: Dict[str, Any]):
        """Set products configuration data"""
        products_data = data.get("products", [])
        self.products = [Product.from_dict(p) for p in products_data]

        self._refresh_products_table()
        self._update_products_count()

        # Clear any form data
        self._clear_product_form()
        self._reset_add_button()

        # Update status
        self._update_import_status(
            f"Loaded {len(self.products)} products from configuration"
        )

        # Emit data loaded signal
        self.data_loaded.emit()

    def clear_data(self):
        """Clear all products data"""
        self.products.clear()
        self._refresh_products_table()
        self._update_products_count()
        self._clear_product_form()
        self._reset_add_button()

        # Clear file selection
        self.file_path_input.clear()
        self.current_file_path = ""
        self.import_btn.setEnabled(False)
        self.validate_csv_btn.setEnabled(False)

        # Reset status
        self._update_import_status("Ready to import products from CSV")

        self.has_changes = False

    def _emit_config_changed(self):
        """Helper method to emit config changed signal"""
        self.has_changes = True
        self.config_changed.emit()

        # Update window title to show unsaved changes (*) - if method exists
        parent_window = self.window()
        if parent_window and hasattr(parent_window, "update_title_with_changes"):
            try:
                getattr(parent_window, "update_title_with_changes")()
            except Exception:
                pass  # Silently ignore if method call fails
