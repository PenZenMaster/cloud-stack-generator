"""
Module/Script Name: FAQ Tab
Path: src/ui/content_tabs/faq_tab.py

Description:
Enhanced FAQ management tab with bulk import/export, categories, tags, and search.
Integrates with the EnhancedFAQItem model for advanced FAQ management.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-18

Last Modified Date:
2025-11-18

Comments:
* v1.00 - Initial enhanced FAQ tab with EnhancedFAQItem integration
"""

from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
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
    QCheckBox,
    QSpinBox,
    QFileDialog,
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, pyqtSignal

from ..components.base_tab import BaseTab
from ...core.content.faq_manager import FAQManager, EnhancedFAQItem, FAQCategory


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


class FAQTab(BaseTab):
    """Enhanced FAQ management tab with import/export and advanced features"""

    # Signals
    config_changed = pyqtSignal()
    validation_requested = pyqtSignal()
    data_loaded = pyqtSignal()

    def __init__(self, parent=None):
        self.faq_manager = FAQManager()
        self.has_changes = False
        super().__init__(parent)

    def setup_ui(self):
        """Setup enhanced FAQ management UI"""
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)

        # Create FAQ sections
        self._create_faq_table_section(main_layout)
        self._create_faq_entry_section(main_layout)
        self._create_faq_actions_section(main_layout)

        self.setLayout(main_layout)

    def _create_faq_table_section(self, parent_layout: QVBoxLayout):
        """Create FAQ table section with enhanced display"""
        # Section header
        header_label = self._create_section_header("FAQ Collection")
        parent_layout.addWidget(header_label)

        # Table group
        table_group = QGroupBox()
        table_layout = QVBoxLayout()

        # Controls: count, search, and filter
        controls_layout = QHBoxLayout()

        self.faq_count_label = QLabel("FAQs: 0")
        self.faq_count_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        # Search
        search_label = QLabel("Search:")
        self.faq_search_input = QLineEdit()
        self.faq_search_input.setPlaceholderText("Search questions, answers, or tags...")
        self.faq_search_input.setMaximumWidth(250)
        self.faq_search_input.textChanged.connect(self._filter_faqs)

        # Category filter
        filter_label = QLabel("Category:")
        self.category_filter = QComboBox()
        self.category_filter.addItem("All Categories", "")
        for category in FAQCategory:
            self.category_filter.addItem(category.value.title(), category.value)
        self.category_filter.setMaximumWidth(150)
        self.category_filter.currentIndexChanged.connect(self._filter_faqs)

        # Active only checkbox
        self.active_only_checkbox = QCheckBox("Active Only")
        self.active_only_checkbox.setChecked(True)
        self.active_only_checkbox.stateChanged.connect(self._filter_faqs)

        controls_layout.addWidget(self.faq_count_label)
        controls_layout.addStretch()
        controls_layout.addWidget(search_label)
        controls_layout.addWidget(self.faq_search_input)
        controls_layout.addWidget(filter_label)
        controls_layout.addWidget(self.category_filter)
        controls_layout.addWidget(self.active_only_checkbox)

        # FAQ table
        self.faq_table = QTableWidget()
        self.faq_table.setColumnCount(7)  # Question, Answer, Category, Tags, Priority, Active, Actions
        headers = ["Question", "Answer", "Category", "Tags", "Priority", "Active", "Actions"]
        self.faq_table.setHorizontalHeaderLabels(headers)

        # Table settings
        self.faq_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.faq_table.setAlternatingRowColors(True)
        self.faq_table.setSortingEnabled(True)

        # Set column widths
        header = self.faq_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(False)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Question
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Answer
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)    # Category
            header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)    # Tags
            header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)    # Priority
            header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)    # Active
            header.setSectionResizeMode(6, QHeaderView.ResizeMode.Fixed)    # Actions

        self.faq_table.setColumnWidth(2, 100)  # Category
        self.faq_table.setColumnWidth(3, 150)  # Tags
        self.faq_table.setColumnWidth(4, 70)   # Priority
        self.faq_table.setColumnWidth(5, 60)   # Active
        self.faq_table.setColumnWidth(6, 80)   # Actions

        table_layout.addLayout(controls_layout)
        table_layout.addWidget(self.faq_table)

        table_group.setLayout(table_layout)
        parent_layout.addWidget(table_group)

    def _create_faq_entry_section(self, parent_layout: QVBoxLayout):
        """Create FAQ entry section with enhanced fields"""
        # Section header
        header_label = self._create_section_header("Add/Edit FAQ")
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

        # Row 3: Category, Priority, Active
        category_label = QLabel("Category:")
        category_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["category"] = QComboBox()
        for category in FAQCategory:
            self.faq_inputs["category"].addItem(category.value.title(), category.value)
        self.faq_inputs["category"].currentIndexChanged.connect(self._emit_config_changed)

        priority_label = QLabel("Priority:")
        priority_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["priority"] = QSpinBox()
        self.faq_inputs["priority"].setRange(0, 100)
        self.faq_inputs["priority"].setValue(0)
        self.faq_inputs["priority"].setToolTip("Higher priority = more important (0-100)")
        self.faq_inputs["priority"].valueChanged.connect(self._emit_config_changed)

        active_label = QLabel("Active:")
        active_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["active"] = QCheckBox("Show on website")
        self.faq_inputs["active"].setChecked(True)
        self.faq_inputs["active"].stateChanged.connect(self._emit_config_changed)

        # Row 4: Tags
        tags_label = QLabel("Tags:")
        tags_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["tags"] = QLineEdit()
        self.faq_inputs["tags"].setPlaceholderText("Enter tags (comma-separated): pricing, shipping, returns")
        self.faq_inputs["tags"].textChanged.connect(self._emit_config_changed)

        # Row 5: City (optional)
        city_label = QLabel("City (optional):")
        city_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["city_name"] = QLineEdit()
        self.faq_inputs["city_name"].setPlaceholderText("e.g., Orlando")
        self.faq_inputs["city_name"].textChanged.connect(self._emit_config_changed)

        state_label = QLabel("State (optional):")
        state_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.faq_inputs["state"] = QLineEdit()
        self.faq_inputs["state"].setPlaceholderText("e.g., FL")
        self.faq_inputs["state"].setMaxLength(2)
        self.faq_inputs["state"].textChanged.connect(self._emit_config_changed)

        # Layout
        entry_layout.addWidget(question_label, 0, 0)
        entry_layout.addWidget(self.faq_inputs["question"], 0, 1, 1, 3)

        entry_layout.addWidget(answer_label, 1, 0)
        entry_layout.addWidget(self.faq_inputs["answer"], 1, 1, 1, 3)

        entry_layout.addWidget(category_label, 2, 0)
        entry_layout.addWidget(self.faq_inputs["category"], 2, 1)
        entry_layout.addWidget(priority_label, 2, 2)
        entry_layout.addWidget(self.faq_inputs["priority"], 2, 3)

        entry_layout.addWidget(tags_label, 3, 0)
        entry_layout.addWidget(self.faq_inputs["tags"], 3, 1, 1, 3)

        entry_layout.addWidget(city_label, 4, 0)
        entry_layout.addWidget(self.faq_inputs["city_name"], 4, 1)
        entry_layout.addWidget(state_label, 4, 2)
        entry_layout.addWidget(self.faq_inputs["state"], 4, 3)

        entry_layout.addWidget(active_label, 5, 0)
        entry_layout.addWidget(self.faq_inputs["active"], 5, 1)

        # Action buttons
        actions_layout = QHBoxLayout()

        self.add_faq_btn = QPushButton("Add FAQ")
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

        self.clear_faq_form_btn = QPushButton("Clear Form")
        self.clear_faq_form_btn.clicked.connect(self._clear_faq_form)

        self.validate_faq_btn = QPushButton("Validate")
        self.validate_faq_btn.clicked.connect(self._validate_current_faq)

        actions_layout.addWidget(self.add_faq_btn)
        actions_layout.addWidget(self.clear_faq_form_btn)
        actions_layout.addWidget(self.validate_faq_btn)
        actions_layout.addStretch()

        entry_layout.addLayout(actions_layout, 6, 0, 1, 4)

        entry_group.setLayout(entry_layout)
        parent_layout.addWidget(entry_group)

    def _create_faq_actions_section(self, parent_layout: QVBoxLayout):
        """Create FAQ bulk actions section"""
        # Separator
        separator = self._create_separator()
        parent_layout.addWidget(separator)

        # Actions layout
        actions_layout = QHBoxLayout()

        # Bulk actions
        self.select_all_faqs_btn = QPushButton("Select All")
        self.select_all_faqs_btn.clicked.connect(self._select_all_faqs)

        self.delete_selected_faqs_btn = QPushButton("Delete Selected")
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

        # Import/Export buttons
        self.import_csv_btn = QPushButton("Import CSV")
        self.import_csv_btn.setStyleSheet("""
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
        """)
        self.import_csv_btn.clicked.connect(self._import_csv)

        self.export_csv_btn = QPushButton("Export CSV")
        self.export_csv_btn.setStyleSheet("""
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
        """)
        self.export_csv_btn.clicked.connect(self._export_csv)

        self.import_json_btn = QPushButton("Import JSON")
        self.import_json_btn.setStyleSheet("""
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
        self.import_json_btn.clicked.connect(self._import_json)

        self.export_json_btn = QPushButton("Export JSON")
        self.export_json_btn.setStyleSheet("""
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
        self.export_json_btn.clicked.connect(self._export_json)

        # Statistics button
        self.show_stats_btn = QPushButton("Show Statistics")
        self.show_stats_btn.clicked.connect(self._show_statistics)

        actions_layout.addWidget(self.select_all_faqs_btn)
        actions_layout.addWidget(self.delete_selected_faqs_btn)
        actions_layout.addStretch()
        actions_layout.addWidget(self.import_csv_btn)
        actions_layout.addWidget(self.export_csv_btn)
        actions_layout.addWidget(self.import_json_btn)
        actions_layout.addWidget(self.export_json_btn)
        actions_layout.addWidget(self.show_stats_btn)

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

    # FAQ CRUD methods
    def _add_faq(self):
        """Add FAQ from manual entry form"""
        try:
            # Parse tags
            tags_text = self.faq_inputs["tags"].text().strip()
            tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []

            # Get city/state (optional)
            city_name = self.faq_inputs["city_name"].text().strip() or None
            state = self.faq_inputs["state"].text().strip().upper() or None

            # Create enhanced FAQ item
            faq = EnhancedFAQItem(
                question=self.faq_inputs["question"].toPlainText().strip(),
                answer=self.faq_inputs["answer"].toPlainText().strip(),
                category=self.faq_inputs["category"].currentData(),
                tags=tags,
                priority=self.faq_inputs["priority"].value(),
                active=self.faq_inputs["active"].isChecked(),
                city_name=city_name,
                state=state
            )

            # Check for duplicate question
            if self.faq_manager.get_faq_by_question(faq.question):
                QMessageBox.warning(
                    self,
                    "Duplicate Question",
                    "FAQ with this question already exists"
                )
                return

            # Add FAQ
            self.faq_manager.add_faq(faq)
            self._refresh_faq_table()
            self._update_faq_count()
            self._clear_faq_form()
            self._emit_config_changed()

            QMessageBox.information(self, "FAQ Added", "Successfully added FAQ")

        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to add FAQ: {str(e)}")

    def _clear_faq_form(self):
        """Clear the FAQ entry form"""
        self.faq_inputs["question"].clear()
        self.faq_inputs["answer"].clear()
        self.faq_inputs["category"].setCurrentIndex(0)
        self.faq_inputs["tags"].clear()
        self.faq_inputs["priority"].setValue(0)
        self.faq_inputs["active"].setChecked(True)
        self.faq_inputs["city_name"].clear()
        self.faq_inputs["state"].clear()

    def _validate_current_faq(self):
        """Validate current FAQ in form"""
        try:
            tags_text = self.faq_inputs["tags"].text().strip()
            tags = [tag.strip() for tag in tags_text.split(",")] if tags_text else []

            faq = EnhancedFAQItem(
                question=self.faq_inputs["question"].toPlainText().strip(),
                answer=self.faq_inputs["answer"].toPlainText().strip(),
                category=self.faq_inputs["category"].currentData(),
                tags=tags,
                priority=self.faq_inputs["priority"].value(),
                active=self.faq_inputs["active"].isChecked()
            )

            QMessageBox.information(self, "Validation Success", "FAQ data is valid!")

        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))

    def _refresh_faq_table(self):
        """Refresh the FAQ table display"""
        # Get current filter settings
        search_term = self.faq_search_input.text()
        category = self.category_filter.currentData()
        active_only = self.active_only_checkbox.isChecked()

        # Search FAQs
        if category or search_term or active_only:
            faqs = self.faq_manager.search(
                search_term=search_term,
                category=category if category else None,
                active_only=active_only
            )
        else:
            faqs = self.faq_manager.faqs

        self.faq_table.setRowCount(len(faqs))

        for row, faq in enumerate(faqs):
            # Question (truncated)
            question_text = faq.question[:100] + "..." if len(faq.question) > 100 else faq.question
            self.faq_table.setItem(row, 0, QTableWidgetItem(question_text))

            # Answer (truncated)
            answer_text = faq.answer[:100] + "..." if len(faq.answer) > 100 else faq.answer
            self.faq_table.setItem(row, 1, QTableWidgetItem(answer_text))

            # Category
            self.faq_table.setItem(row, 2, QTableWidgetItem(faq.category.title()))

            # Tags
            tags_text = ", ".join(faq.tags) if faq.tags else ""
            self.faq_table.setItem(row, 3, QTableWidgetItem(tags_text))

            # Priority
            self.faq_table.setItem(row, 4, QTableWidgetItem(str(faq.priority)))

            # Active
            active_text = "Yes" if faq.active else "No"
            self.faq_table.setItem(row, 5, QTableWidgetItem(active_text))

            # Actions
            actions_btn = QPushButton("Edit")
            actions_btn.setMaximumWidth(60)
            actions_btn.clicked.connect(lambda checked, f=faq: self._edit_faq(f))
            self.faq_table.setCellWidget(row, 6, actions_btn)

    def _filter_faqs(self):
        """Filter FAQs based on search and category"""
        self._refresh_faq_table()
        self._update_faq_count()

    def _update_faq_count(self):
        """Update FAQ count label"""
        total = len(self.faq_manager.faqs)
        visible = self.faq_table.rowCount()

        if visible == total:
            self.faq_count_label.setText(f"FAQs: {total}")
        else:
            self.faq_count_label.setText(f"FAQs: {visible}/{total}")

    def _edit_faq(self, faq: EnhancedFAQItem):
        """Edit FAQ"""
        # Load FAQ into form
        self.faq_inputs["question"].setPlainText(faq.question)
        self.faq_inputs["answer"].setPlainText(faq.answer)

        # Set category
        category_index = self.faq_inputs["category"].findData(faq.category)
        if category_index >= 0:
            self.faq_inputs["category"].setCurrentIndex(category_index)

        # Set tags
        self.faq_inputs["tags"].setText(", ".join(faq.tags))

        # Set priority and active
        self.faq_inputs["priority"].setValue(faq.priority)
        self.faq_inputs["active"].setChecked(faq.active)

        # Set city/state
        if faq.city_name:
            self.faq_inputs["city_name"].setText(faq.city_name)
        if faq.state:
            self.faq_inputs["state"].setText(faq.state)

        # Change button to update mode
        self.add_faq_btn.setText("Update FAQ")
        try:
            self.add_faq_btn.clicked.disconnect()
        except TypeError:
            pass
        self.add_faq_btn.clicked.connect(lambda: self._update_faq(faq.question))

    def _update_faq(self, original_question: str):
        """Update FAQ"""
        try:
            # Remove old FAQ
            self.faq_manager.remove_faq(original_question)

            # Add updated FAQ
            self._add_faq()

            # Reset button
            self._reset_add_faq_button()

            QMessageBox.information(self, "FAQ Updated", "Successfully updated FAQ")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to update FAQ: {str(e)}")

    def _reset_add_faq_button(self):
        """Reset add FAQ button to add mode"""
        self.add_faq_btn.setText("Add FAQ")
        try:
            self.add_faq_btn.clicked.disconnect()
        except TypeError:
            pass
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Get questions to delete
            questions_to_delete = []
            for row in selected_rows:
                question_item = self.faq_table.item(row, 0)
                if question_item:
                    # Get full question from manager (table might have truncated version)
                    question_text = question_item.text()
                    for faq in self.faq_manager.faqs:
                        if faq.question.startswith(question_text.rstrip("...")):
                            questions_to_delete.append(faq.question)
                            break

            # Delete FAQs
            for question in questions_to_delete:
                self.faq_manager.remove_faq(question)

            self._refresh_faq_table()
            self._update_faq_count()
            self._emit_config_changed()

            QMessageBox.information(self, "Deletion Complete", f"Successfully deleted {count} FAQ(s)")

    # Import/Export methods
    def _import_csv(self):
        """Import FAQs from CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import FAQs from CSV",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            try:
                count = self.faq_manager.import_from_csv(Path(file_path))
                self._refresh_faq_table()
                self._update_faq_count()
                self._emit_config_changed()

                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Successfully imported {count} FAQs from CSV"
                )
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Failed to import CSV: {str(e)}")

    def _export_csv(self):
        """Export FAQs to CSV file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export FAQs to CSV",
            "faqs.csv",
            "CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            try:
                active_only = self.active_only_checkbox.isChecked()
                count = self.faq_manager.export_to_csv(Path(file_path), active_only=active_only)

                if count == 0:
                    QMessageBox.information(
                        self,
                        "Template Exported",
                        "No FAQs to export. Created CSV template with headers.\n\n"
                        "You can use this template to add your FAQs and import them back."
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Successfully exported {count} FAQs to CSV"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export CSV: {str(e)}")

    def _import_json(self):
        """Import FAQs from JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import FAQs from JSON",
            "",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                count = self.faq_manager.import_from_json(Path(file_path))
                self._refresh_faq_table()
                self._update_faq_count()
                self._emit_config_changed()

                QMessageBox.information(
                    self,
                    "Import Successful",
                    f"Successfully imported {count} FAQs from JSON"
                )
            except Exception as e:
                QMessageBox.critical(self, "Import Failed", f"Failed to import JSON: {str(e)}")

    def _export_json(self):
        """Export FAQs to JSON file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export FAQs to JSON",
            "faqs.json",
            "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            try:
                active_only = self.active_only_checkbox.isChecked()
                count = self.faq_manager.export_to_json(
                    Path(file_path),
                    active_only=active_only,
                    pretty=True
                )

                if count == 0:
                    QMessageBox.information(
                        self,
                        "Template Exported",
                        "No FAQs to export. Created JSON template with example structure.\n\n"
                        "You can use this template to add your FAQs and import them back."
                    )
                else:
                    QMessageBox.information(
                        self,
                        "Export Successful",
                        f"Successfully exported {count} FAQs to JSON"
                    )
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export JSON: {str(e)}")

    def _show_statistics(self):
        """Show FAQ statistics"""
        stats = self.faq_manager.get_statistics()

        msg = f"FAQ Statistics:\n\n"
        msg += f"Total FAQs: {stats['total_faqs']}\n"
        msg += f"Active FAQs: {stats['active_faqs']}\n"
        msg += f"Inactive FAQs: {stats['inactive_faqs']}\n\n"

        if stats['categories']:
            msg += "By Category:\n"
            for category, count in sorted(stats['categories'].items()):
                msg += f"  - {category.title()}: {count}\n"
            msg += "\n"

        if stats['cities']:
            msg += "By City:\n"
            for city, count in sorted(stats['cities'].items()):
                msg += f"  - {city}: {count}\n"
            msg += "\n"

        msg += f"Total Unique Tags: {stats['total_tags']}\n"

        if stats['total_tags'] > 0:
            all_tags = sorted(list(self.faq_manager.get_all_tags()))
            msg += f"\nTags: {', '.join(all_tags[:20])}"
            if len(all_tags) > 20:
                msg += f"... and {len(all_tags) - 20} more"

        QMessageBox.information(self, "FAQ Statistics", msg)

    # BaseTab implementation
    def connect_signals(self):
        """Connect UI signals"""
        pass  # Signals already connected in widget creation

    def get_required_fields(self) -> List[str]:
        """Get list of required field names"""
        return []  # No required fields at tab level

    def validate_data(self) -> ValidationResult:
        """Validate all FAQ data"""
        result = ValidationResult()

        if len(self.faq_manager.faqs) == 0:
            result.add_warning("No FAQs defined - consider adding common questions")
        else:
            # Check for duplicate questions
            questions = [faq.question.lower() for faq in self.faq_manager.faqs]
            duplicates = []
            for question in questions:
                if questions.count(question) > 1 and question not in duplicates:
                    duplicates.append(question)

            for question in duplicates:
                result.add_error(f"Duplicate FAQ question found: {question}")

        # Best practice warnings
        if len(self.faq_manager.faqs) < 3:
            result.add_warning("Consider adding more FAQs (recommended: 5+ questions)")

        active_count = len([faq for faq in self.faq_manager.faqs if faq.active])
        if active_count == 0 and len(self.faq_manager.faqs) > 0:
            result.add_warning("No active FAQs - at least one FAQ should be active")

        return result

    def get_config_data(self) -> Dict[str, Any]:
        """Get FAQ configuration data in legacy format"""
        # Export to legacy format for backward compatibility
        return {
            "faq": self.faq_manager.export_to_legacy_format()
        }

    def set_config_data(self, data: Dict[str, Any]):
        """Set FAQ configuration data"""
        # Clear existing FAQs
        self.faq_manager.clear()

        # Load FAQs from config
        faq_data = data.get("faq", [])

        for item in faq_data:
            try:
                # Check if it's legacy format (question/answer only) or enhanced
                if isinstance(item, dict):
                    if "tags" in item or "priority" in item:
                        # Enhanced format
                        faq = EnhancedFAQItem(**item)
                    else:
                        # Legacy format
                        faq = EnhancedFAQItem(
                            question=item.get("question", ""),
                            answer=item.get("answer", ""),
                            category=item.get("category", FAQCategory.GENERAL.value)
                        )
                    self.faq_manager.add_faq(faq)
            except Exception as e:
                print(f"Warning: Skipping invalid FAQ: {e}")
                continue

        # Refresh display
        self._refresh_faq_table()
        self._update_faq_count()

        # Emit data loaded signal
        self.data_loaded.emit()

    def clear_data(self):
        """Clear all FAQ data"""
        self.faq_manager.clear()
        self._refresh_faq_table()
        self._update_faq_count()
        self._clear_faq_form()
        self._reset_add_faq_button()
        self.faq_search_input.clear()
        self.category_filter.setCurrentIndex(0)
        self.active_only_checkbox.setChecked(True)
        self.has_changes = False

    def _emit_config_changed(self):
        """Helper method to emit config changed signal"""
        self.has_changes = True
        self.config_changed.emit()
