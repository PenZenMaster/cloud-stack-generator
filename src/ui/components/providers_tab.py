"""
Module/Script Name: providers_tab.py
Path: src/ui/components/providers_tab.py

Description:
List-manager tab for ProviderConfig entries on resource sites. Lets users
create, edit, and delete listed provider records without editing YAML directly.
Each provider gets a profile page at providers/{slug}.html and CTA mentions
in relevant topic guide pages.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-22

Last Modified Date:
2026-03-22

Comments:
* v1.00 - Initial implementation for Sprint 5 providers feature
"""

import copy
from typing import Any, Dict, List

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
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

_EMPTY_PROVIDER: Dict[str, Any] = {
    "name": "",
    "slug": "",
    "url": "",
    "phone": "",
    "service_area": "",
    "specialties": [],
    "description": "",
    "verified": True,
}


class ProvidersTab(BaseTab):
    """
    Tab for managing a list of ProviderConfig entries.

    Layout: left panel = scrollable list of providers + Add/Remove buttons;
    right panel = form for the selected provider's fields.
    The 'name' field is required; 'slug' is auto-generated from name if blank.
    """

    config_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # In-memory list of provider dicts (mirrors what get_config_data returns)
        self._providers: List[Dict[str, Any]] = []
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
            "Providers are listed on the resource site's Providers index page and each "
            "gets a profile page at providers/{slug}.html. They are referenced in "
            "relevant topic guide CTAs. No provider content is deployed to the resource "
            "site -- only links back to their own domain."
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

        list_label = QLabel("Providers")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        left_layout.addWidget(list_label)

        self.provider_list = QListWidget()
        self.provider_list.setMinimumWidth(160)
        self.provider_list.setSizePolicy(
            QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding
        )
        self.provider_list.currentRowChanged.connect(self._on_selection_changed)
        left_layout.addWidget(self.provider_list)

        btn_row = QHBoxLayout()
        self.add_btn = QPushButton("+ Add")
        self.add_btn.setToolTip("Add a new provider")
        self.add_btn.clicked.connect(self._add_provider)
        btn_row.addWidget(self.add_btn)

        self.remove_btn = QPushButton("- Remove")
        self.remove_btn.setToolTip("Remove the selected provider")
        self.remove_btn.clicked.connect(self._remove_provider)
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

        # Placeholder shown when no provider is selected
        self.placeholder_label = QLabel(
            'Select a provider on the left, or click "+ Add" to create one.'
        )
        self.placeholder_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.placeholder_label.setStyleSheet("color:#888; font-style:italic;")
        self.form_layout.addWidget(self.placeholder_label)

        # Form widget (hidden until a provider is selected)
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

        self.name_input = self._make_field(
            id_layout,
            "Provider Name",
            "e.g. Overhead Door Company of Joliet",
            "Display name for this provider.",
        )
        self.slug_input = self._make_field(
            id_layout,
            "URL Slug",
            "auto-generated from name if blank",
            "URL path segment: providers/{slug}.html. Auto-derived from Provider Name if blank.",
        )
        self.url_input = self._make_field(
            id_layout,
            "Website URL",
            "https://overheaddoorjoliet.com",
            "Provider's own website URL. Must start with http:// or https:// if provided.",
        )
        self.phone_input = self._make_field(
            id_layout,
            "Phone",
            "e.g. (815) 555-0100  (optional)",
            "Provider's contact phone number (optional).",
        )
        form_inner.addWidget(identity_group)

        # Coverage & Expertise group
        coverage_group = QGroupBox("Coverage & Expertise")
        coverage_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        cov_layout = QVBoxLayout(coverage_group)
        cov_layout.setSpacing(8)

        self.service_area_input = self._make_field(
            cov_layout,
            "Service Area",
            "e.g. Will County, IL",
            "Geographic service area for this provider.",
        )
        self.specialties_input = self._make_textarea(
            cov_layout,
            "Specialties",
            "torsion springs\ncommercial doors\ngarage door repair",
            "One specialty per line. Used to match this provider to relevant topic guide pages.",
            rows=3,
        )
        form_inner.addWidget(coverage_group)

        # Editorial Description group
        content_group = QGroupBox("Editorial Description")
        content_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        content_layout = QVBoxLayout(content_group)
        content_layout.setSpacing(8)

        self.description_input = self._make_textarea(
            content_layout,
            "Description",
            "Brief 1-2 sentence editorial description of this provider...",
            "Short editorial description shown on the provider's profile page.",
            rows=3,
        )
        form_inner.addWidget(content_group)

        # Display Settings group
        settings_group = QGroupBox("Display Settings")
        settings_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(8)

        self.verified_check = QCheckBox("Show 'Verified Provider' badge on profile page")
        self.verified_check.setChecked(True)
        self.verified_check.stateChanged.connect(self._on_form_changed)
        settings_layout.addWidget(self.verified_check)
        form_inner.addWidget(settings_group)

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
        """Read all form fields into a provider dict."""
        return {
            "name": self.name_input.text().strip(),
            "slug": self.slug_input.text().strip(),
            "url": self.url_input.text().strip(),
            "phone": self.phone_input.text().strip(),
            "service_area": self.service_area_input.text().strip(),
            "specialties": self._lines_to_list(self.specialties_input.toPlainText()),
            "description": self.description_input.toPlainText().strip(),
            "verified": self.verified_check.isChecked(),
        }

    def _populate_form(self, data: Dict[str, Any]):
        """Populate all form fields from a provider dict (suppresses change signals)."""
        self._updating_form = True
        try:
            self.name_input.setText(data.get("name", ""))
            self.slug_input.setText(data.get("slug", ""))
            self.url_input.setText(data.get("url", ""))
            self.phone_input.setText(data.get("phone", ""))
            self.service_area_input.setText(data.get("service_area", ""))
            self.specialties_input.setPlainText(
                self._list_to_lines(data.get("specialties", []))
            )
            self.description_input.setPlainText(data.get("description", ""))
            self.verified_check.setChecked(data.get("verified", True))
        finally:
            self._updating_form = False

    def _update_list_item_label(self, index: int):
        """Refresh the list widget label for the given index."""
        if 0 <= index < self.provider_list.count():
            name = self._providers[index].get("name") or f"Provider {index + 1}"
            self.provider_list.item(index).setText(name)

    # ---- Slots --------------------------------------------------------------- #

    def _on_selection_changed(self, row: int):
        """Save current form back to memory, then load the newly selected row."""
        # Save any pending edits for the previously selected item
        if self._current_index >= 0 and not self._updating_form:
            self._providers[self._current_index] = self._read_form()
            self._update_list_item_label(self._current_index)

        self._current_index = row
        has_selection = row >= 0

        self.remove_btn.setEnabled(has_selection)
        self.placeholder_label.setVisible(not has_selection)
        self.form_widget.setVisible(has_selection)

        if has_selection:
            self._populate_form(self._providers[row])

    def _on_form_changed(self):
        """Write form state to in-memory store and refresh the list label."""
        if self._updating_form or self._current_index < 0:
            return
        self._providers[self._current_index] = self._read_form()
        self._update_list_item_label(self._current_index)
        self.config_changed.emit()

    def _add_provider(self):
        """Append a blank provider and select it."""
        self._providers.append(copy.deepcopy(_EMPTY_PROVIDER))
        item = QListWidgetItem(f"Provider {len(self._providers)}")
        self.provider_list.addItem(item)
        self.provider_list.setCurrentRow(len(self._providers) - 1)
        self.config_changed.emit()

    def _remove_provider(self):
        """Remove the currently selected provider."""
        row = self.provider_list.currentRow()
        if row < 0:
            return
        self._providers.pop(row)
        self._current_index = -1  # prevent save-on-selection-change
        self.provider_list.takeItem(row)
        # Re-select adjacent item
        new_row = min(row, self.provider_list.count() - 1)
        if new_row >= 0:
            self.provider_list.setCurrentRow(new_row)
        else:
            self.placeholder_label.setVisible(True)
            self.form_widget.setVisible(False)
            self.remove_btn.setEnabled(False)
        self.config_changed.emit()

    # ---- Public interface ---------------------------------------------------- #

    def get_config_data(self) -> List[Dict[str, Any]]:
        """Return all providers as a list of dicts for ClientConfig construction."""
        # Flush any unsaved edits for the current selection
        if self._current_index >= 0:
            self._providers[self._current_index] = self._read_form()
            self._update_list_item_label(self._current_index)
        return list(self._providers)

    def set_config_data(self, providers: List[Dict[str, Any]]):
        """Populate the list from a list of provider dicts (e.g. loaded from YAML)."""
        self._current_index = -1
        self._providers = [dict(p) for p in providers]

        self.provider_list.blockSignals(True)
        self.provider_list.clear()
        for p in self._providers:
            name = p.get("name") or "Unnamed Provider"
            self.provider_list.addItem(QListWidgetItem(name))
        self.provider_list.blockSignals(False)

        self.placeholder_label.setVisible(True)
        self.form_widget.setVisible(False)
        self.remove_btn.setEnabled(False)

        if self._providers:
            self.provider_list.setCurrentRow(0)

    def clear_data(self):
        """Reset to empty state."""
        self.set_config_data([])

    def validate_data(self):
        """Validate all providers. name is required; url must be http(s) if provided."""
        result = ValidationResult()
        for i, p in enumerate(self.get_config_data()):
            if not p.get("name", "").strip():
                result.add_error(
                    f"Provider {i + 1}: Provider Name is required.",
                    f"provider_{i}_name",
                )
            url = p.get("url", "").strip()
            if url and not (url.startswith("http://") or url.startswith("https://")):
                result.add_error(
                    f"Provider {i + 1}: Website URL must start with http:// or https://.",
                    f"provider_{i}_url",
                )
        return result.is_valid, result.errors
