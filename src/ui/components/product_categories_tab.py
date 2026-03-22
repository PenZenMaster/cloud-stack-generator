"""
Module/Script Name: product_categories_tab.py
Path: src/ui/components/product_categories_tab.py

Description:
List-manager tab for ProductCategoryConfig entries. Lets users create,
edit, and delete product comparison guide categories without editing YAML
directly. Each category becomes one products/{slug}.html comparison guide
page on resource sites.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-22

Last Modified Date:
2026-03-22

Comments:
* v1.00 - Initial implementation for Sprint 5 UI update
"""

from typing import Any, Dict, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .base_tab import BaseTab, ValidationResult
from ...core.utils.logger import get_logger

logger = get_logger(__name__)

# ---- Internal data model ---------------------------------------------------- #

_EMPTY_CATEGORY: Dict[str, Any] = {
    "category_name": "",
    "guide_title": "",
    "slug": "",
    "description": "",
    "products": [],
    "competing_brands": [],
    "comparison_criteria": [],
    "best_for": [],
    "not_ideal_for": [],
    "standards": [],
}


class ProductCategoriesTab(BaseTab):
    """
    Tab for managing a list of ProductCategoryConfig entries.

    Layout: left panel = scrollable list of categories + Add/Remove buttons;
    right panel = form for the selected category's fields.
    All fields are optional; slug is auto-generated from category_name if blank.
    """

    config_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # In-memory list of category dicts (mirrors what get_config_data returns)
        self._categories: List[Dict[str, Any]] = []
        self._current_index: int = -1
        self._updating_form: bool = False  # guard against recursive signals
        self.setup_ui()

    # ---- UI construction ---------------------------------------------------- #

    def setup_ui(self):
        """Build the split-panel layout."""
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # Info banner
        info = QLabel(
            "Product Categories define comparison guide pages (products/{slug}.html) "
            "generated on Resource Sites. Each category groups related products and "
            "adds a comparison table, Best For / Not Ideal For boxes, and standards. "
            "Leave Slug blank to auto-generate from Category Name."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            "background:#e8f4fd; border:1px solid #bee5eb; "
            "border-radius:4px; padding:8px; color:#0c5460; margin:8px;"
        )
        outer.addWidget(info)

        # Splitter: list on left, form on right
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        outer.addWidget(splitter)

        # --- Left panel: list + buttons ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(8, 8, 4, 8)
        left_layout.setSpacing(6)

        list_label = QLabel("Categories")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(list_label)

        self.category_list = QListWidget()
        self.category_list.setMinimumWidth(160)
        self.category_list.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        self.category_list.currentRowChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.category_list)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("+ Add")
        self.add_btn.setToolTip("Add a new product category")
        self.add_btn.clicked.connect(self._add_category)
        btn_row.addWidget(self.add_btn)

        self.remove_btn = QPushButton("- Remove")
        self.remove_btn.setToolTip("Remove the selected category")
        self.remove_btn.clicked.connect(self._remove_category)
        self.remove_btn.setEnabled(False)
        btn_row.addWidget(self.remove_btn)

        left_layout.addLayout(btn_row)
        splitter.addWidget(left_widget)

        # --- Right panel: scrollable form ---
        right_widget = QWidget()
        right_outer = QVBoxLayout(right_widget)
        right_outer.setContentsMargins(4, 8, 8, 8)
        right_outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        right_outer.addWidget(scroll)

        form_container = QWidget()
        self.form_layout = QVBoxLayout(form_container)
        self.form_layout.setContentsMargins(12, 12, 12, 12)
        self.form_layout.setSpacing(14)
        scroll.setWidget(form_container)

        # Placeholder shown when no category is selected
        self.placeholder_label = QLabel(
            'Select a category on the left, or click "+ Add" to create one.'
        )
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color:#888; font-style:italic;")
        self.form_layout.addWidget(self.placeholder_label)

        # Form widget (hidden until a category is selected)
        self.form_widget = QWidget()
        self.form_widget.setVisible(False)
        form_inner = QVBoxLayout(self.form_widget)
        form_inner.setContentsMargins(0, 0, 0, 0)
        form_inner.setSpacing(14)

        # Identity group
        identity_group = QGroupBox("Identity")
        identity_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        id_layout = QVBoxLayout(identity_group)
        id_layout.setSpacing(8)

        self.category_name_input = self._make_field(
            id_layout,
            "Category Name",
            "e.g. Insulated Steel Sectional Doors",
            "Display name for this category. Used as the page heading.",
        )
        self.guide_title_input = self._make_field(
            id_layout,
            "Guide Title",
            "e.g. Insulated Commercial Steel Doors: R-Value Comparison",
            "Full SEO page title. Defaults to Category Name if blank.",
        )
        self.slug_input = self._make_field(
            id_layout,
            "URL Slug",
            "e.g. insulated-steel-sectional-doors  (auto-generated if blank)",
            "URL path segment: products/{slug}.html. Auto-derived from Category Name if blank.",
        )
        self.description_input = self._make_textarea(
            id_layout,
            "Description",
            "Introductory paragraph for the comparison guide...",
            "Intro paragraph rendered above the comparison table.",
            rows=3,
        )
        form_inner.addWidget(identity_group)

        # Comparison content group
        comp_group = QGroupBox("Comparison Content")
        comp_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        comp_layout = QVBoxLayout(comp_group)
        comp_layout.setSpacing(8)

        self.competing_brands_input = self._make_textarea(
            comp_layout,
            "Competing Brands",
            "Wayne Dalton\nClopay\nAmarr",
            "One brand per line. Listed in the comparison table header.",
            rows=3,
        )
        self.comparison_criteria_input = self._make_textarea(
            comp_layout,
            "Comparison Criteria",
            "R-Value\nMaterial\nPrice Range\nWarranty",
            "One criterion per line. These become the table row labels.",
            rows=4,
        )
        form_inner.addWidget(comp_group)

        # Suitability group
        suit_group = QGroupBox("Suitability")
        suit_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        suit_layout = QVBoxLayout(suit_group)
        suit_layout.setSpacing(8)

        self.best_for_input = self._make_textarea(
            suit_layout,
            "Best For",
            "High-traffic corridors\nStairwells\nWarehouses",
            "One scenario per line. Shown in the 'Best For' highlight box.",
            rows=3,
        )
        self.not_ideal_for_input = self._make_textarea(
            suit_layout,
            "Not Ideal For",
            "Exterior applications\nHigh-humidity environments",
            "One scenario per line. Shown in the 'Not Ideal For' warning box.",
            rows=3,
        )
        form_inner.addWidget(suit_group)

        # Standards group
        standards_group = QGroupBox("Standards & Products")
        standards_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        std_layout = QVBoxLayout(standards_group)
        std_layout.setSpacing(8)

        self.standards_input = self._make_textarea(
            std_layout,
            "Standards",
            "NFPA 80\nUL 10C\nIECC 2021 Section C402.5",
            "One standard per line. Shown in the standards/certifications section.",
            rows=3,
        )
        self.products_input = self._make_textarea(
            std_layout,
            "Products (names/SKUs)",
            "SKU-001\nSKU-002\nHeavy-Duty Steel Panel",
            "One product name or SKU per line. Links this category to matching product pages.",
            rows=3,
        )
        form_inner.addWidget(standards_group)

        form_inner.addStretch()
        self.form_layout.addWidget(self.form_widget)
        self.form_layout.addStretch()

        splitter.addWidget(right_widget)
        splitter.setSizes([200, 600])

    # ---- Helpers ------------------------------------------------------------- #

    def _make_field(
        self,
        parent_layout: QVBoxLayout,
        label: str,
        placeholder: str,
        tooltip: str,
    ) -> QLineEdit:
        """Add a labeled QLineEdit and return it."""
        row = QHBoxLayout()
        lbl = QLabel(f"{label}:")
        lbl.setMinimumWidth(160)
        lbl.setFont(QFont("Arial", 10))
        row.addWidget(lbl)

        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setToolTip(tooltip)
        field.textChanged.connect(self._on_form_changed)
        row.addWidget(field)
        parent_layout.addLayout(row)
        return field

    def _make_textarea(
        self,
        parent_layout: QVBoxLayout,
        label: str,
        placeholder: str,
        tooltip: str,
        rows: int = 3,
    ) -> QTextEdit:
        """Add a labeled QTextEdit and return it."""
        lbl = QLabel(f"{label}:")
        lbl.setFont(QFont("Arial", 10))
        parent_layout.addWidget(lbl)

        field = QTextEdit()
        field.setPlaceholderText(placeholder)
        field.setToolTip(tooltip)
        field.setMinimumHeight(rows * 28)
        field.setMaximumHeight(rows * 32)
        field.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        field.textChanged.connect(self._on_form_changed)
        parent_layout.addWidget(field)
        return field

    @staticmethod
    def _lines_to_list(text: str) -> List[str]:
        """Convert newline-separated text to a cleaned list of strings."""
        return [line.strip() for line in text.splitlines() if line.strip()]

    @staticmethod
    def _list_to_lines(items: List[str]) -> str:
        """Convert a list of strings to newline-separated text."""
        return "\n".join(items)

    def _read_form(self) -> Dict[str, Any]:
        """Read all form fields into a category dict."""
        return {
            "category_name": self.category_name_input.text().strip(),
            "guide_title": self.guide_title_input.text().strip(),
            "slug": self.slug_input.text().strip(),
            "description": self.description_input.toPlainText().strip(),
            "competing_brands": self._lines_to_list(
                self.competing_brands_input.toPlainText()
            ),
            "comparison_criteria": self._lines_to_list(
                self.comparison_criteria_input.toPlainText()
            ),
            "best_for": self._lines_to_list(self.best_for_input.toPlainText()),
            "not_ideal_for": self._lines_to_list(
                self.not_ideal_for_input.toPlainText()
            ),
            "standards": self._lines_to_list(self.standards_input.toPlainText()),
            "products": self._lines_to_list(self.products_input.toPlainText()),
        }

    def _populate_form(self, data: Dict[str, Any]):
        """Populate all form fields from a category dict (suppresses change signals)."""
        self._updating_form = True
        try:
            self.category_name_input.setText(data.get("category_name", ""))
            self.guide_title_input.setText(data.get("guide_title", ""))
            self.slug_input.setText(data.get("slug", ""))
            self.description_input.setPlainText(data.get("description", ""))
            self.competing_brands_input.setPlainText(
                self._list_to_lines(data.get("competing_brands", []))
            )
            self.comparison_criteria_input.setPlainText(
                self._list_to_lines(data.get("comparison_criteria", []))
            )
            self.best_for_input.setPlainText(
                self._list_to_lines(data.get("best_for", []))
            )
            self.not_ideal_for_input.setPlainText(
                self._list_to_lines(data.get("not_ideal_for", []))
            )
            self.standards_input.setPlainText(
                self._list_to_lines(data.get("standards", []))
            )
            self.products_input.setPlainText(
                self._list_to_lines(data.get("products", []))
            )
        finally:
            self._updating_form = False

    def _update_list_item_label(self, index: int):
        """Refresh the list widget label for the given index."""
        if 0 <= index < self.category_list.count():
            name = self._categories[index].get("category_name") or f"Category {index + 1}"
            self.category_list.item(index).setText(name)

    # ---- Slots --------------------------------------------------------------- #

    def _on_selection_changed(self, row: int):
        """Save current form back to memory, then load the newly selected row."""
        # Save any pending edits for the previously selected item
        if self._current_index >= 0 and not self._updating_form:
            self._categories[self._current_index] = self._read_form()
            self._update_list_item_label(self._current_index)

        self._current_index = row
        has_selection = row >= 0

        self.remove_btn.setEnabled(has_selection)
        self.placeholder_label.setVisible(not has_selection)
        self.form_widget.setVisible(has_selection)

        if has_selection:
            self._populate_form(self._categories[row])

    def _on_form_changed(self):
        """Write form state to in-memory store and refresh the list label."""
        if self._updating_form or self._current_index < 0:
            return
        self._categories[self._current_index] = self._read_form()
        self._update_list_item_label(self._current_index)
        self.config_changed.emit()

    def _add_category(self):
        """Append a blank category and select it."""
        import copy
        self._categories.append(copy.deepcopy(_EMPTY_CATEGORY))
        item = QListWidgetItem(f"Category {len(self._categories)}")
        self.category_list.addItem(item)
        self.category_list.setCurrentRow(len(self._categories) - 1)
        self.config_changed.emit()

    def _remove_category(self):
        """Remove the currently selected category."""
        row = self.category_list.currentRow()
        if row < 0:
            return
        self._categories.pop(row)
        self._current_index = -1  # prevent save-on-selection-change
        self.category_list.takeItem(row)
        # Re-select adjacent item
        new_row = min(row, self.category_list.count() - 1)
        if new_row >= 0:
            self.category_list.setCurrentRow(new_row)
        else:
            self.placeholder_label.setVisible(True)
            self.form_widget.setVisible(False)
            self.remove_btn.setEnabled(False)
        self.config_changed.emit()

    # ---- Public interface ---------------------------------------------------- #

    def get_config_data(self) -> List[Dict[str, Any]]:
        """Return all categories as a list of dicts for ClientConfig construction."""
        # Flush any unsaved edits for the current selection
        if self._current_index >= 0:
            self._categories[self._current_index] = self._read_form()
            self._update_list_item_label(self._current_index)
        return list(self._categories)

    def set_config_data(self, categories: List[Dict[str, Any]]):
        """Populate the list from a list of category dicts (e.g. loaded from YAML)."""
        self._current_index = -1
        self._categories = [dict(cat) for cat in categories]

        self.category_list.blockSignals(True)
        self.category_list.clear()
        for cat in self._categories:
            name = cat.get("category_name") or "Unnamed Category"
            self.category_list.addItem(QListWidgetItem(name))
        self.category_list.blockSignals(False)

        self.placeholder_label.setVisible(True)
        self.form_widget.setVisible(False)
        self.remove_btn.setEnabled(False)

        if self._categories:
            self.category_list.setCurrentRow(0)

    def clear_data(self):
        """Reset to empty state."""
        self.set_config_data([])

    def validate_data(self):
        """Validate all categories. category_name is required for each entry."""
        result = ValidationResult()
        for i, cat in enumerate(self.get_config_data()):
            if not cat.get("category_name", "").strip():
                result.add_error(
                    f"Category {i + 1}: Category Name is required.",
                    f"category_{i}_name",
                )
        return result.is_valid, result.errors
