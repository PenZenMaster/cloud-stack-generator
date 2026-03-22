"""
Module/Script Name: resource_site_tab.py
Path: src/ui/components/resource_site_tab.py

Description:
Configuration tab for ResourceSiteConfig fields. Allows users to define the
editorial identity, money-site attribution, and authoritative sources for
resource (topical authority) sites without editing YAML directly.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-21

Last Modified Date:
2026-03-21

Comments:
* v1.00 - Initial implementation for Sprint 4 UI update
"""

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QScrollArea,
    QGroupBox,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from typing import Dict, Any, List

from .base_tab import BaseTab, ValidationResult
from ...core.utils.logger import get_logger

logger = get_logger(__name__)


class ResourceSiteTab(BaseTab):
    """
    Tab for configuring ResourceSiteConfig fields.

    Only relevant when Cloud Deploy > Site Type is set to 'Resource Site'.
    All fields are optional; leaving them blank produces reasonable template
    fallback text at generation time.
    """

    config_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Build the resource site configuration form."""
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        outer_layout.addWidget(scroll)

        container = QWidget()
        scroll.setWidget(container)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # -- Info banner -------------------------------------------------------
        info_label = QLabel(
            "These fields apply only when Site Type is set to 'Resource Site' "
            "in the Cloud Deploy tab. Leave blank to use template defaults."
        )
        info_label.setWordWrap(True)
        info_label.setStyleSheet(
            "background:#e8f4fd; border:1px solid #bee5eb; "
            "border-radius:4px; padding:8px; color:#0c5460;"
        )
        layout.addWidget(info_label)

        # -- Site Identity -----------------------------------------------------
        identity_group = QGroupBox("Site Identity")
        identity_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        identity_layout = QVBoxLayout(identity_group)
        identity_layout.setSpacing(10)

        self.site_name_input = self._make_field(
            identity_layout,
            "Site Name",
            "e.g. Commercial Door Guide",
            "Display name shown in the header and throughout the site. "
            "Should be distinct from the money-site name.",
        )
        self.site_brand_input = self._make_field(
            identity_layout,
            "Site Brand / Tagline",
            "e.g. Independent Guides for Facility Managers",
            "Short brand descriptor used in the logo area and footer.",
        )
        layout.addWidget(identity_group)

        # -- Editorial Content -------------------------------------------------
        editorial_group = QGroupBox("Editorial Content")
        editorial_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        editorial_layout = QVBoxLayout(editorial_group)
        editorial_layout.setSpacing(10)

        self.site_mission_input = self._make_textarea(
            editorial_layout,
            "Site Mission",
            "e.g. Helping facility managers and building owners make informed "
            "decisions about commercial doors, hardware, and access control.",
            "Used as the meta description and hero subtitle on the homepage.",
            rows=3,
        )
        self.editorial_perspective_input = self._make_textarea(
            editorial_layout,
            "Editorial Perspective",
            "e.g. Our guides are written by industry professionals and reviewed "
            "against published NFPA, ANSI, and UL standards.",
            "Shown in the About page and footer 'About This Resource' section.",
            rows=3,
        )
        layout.addWidget(editorial_group)

        # -- Money Site Attribution --------------------------------------------
        money_group = QGroupBox("Local Provider Attribution")
        money_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        money_layout = QVBoxLayout(money_group)
        money_layout.setSpacing(10)

        money_note = QLabel(
            "The money site is mentioned once per page in the CTA section as "
            "a local provider recommendation. Max one mention per page."
        )
        money_note.setWordWrap(True)
        money_note.setStyleSheet("color:#555; font-style:italic; font-size:9pt;")
        money_layout.addWidget(money_note)

        self.money_site_name_input = self._make_field(
            money_layout,
            "Money Site Name",
            "e.g. Overhead Door Company of Joliet",
            "Business name of the money site to attribute in CTAs.",
        )
        self.money_site_url_input = self._make_field(
            money_layout,
            "Money Site URL",
            "https://overheaddoorjoliet.com",
            "Full URL including https://. Used for the CTA hyperlink.",
        )

        cta_style_layout = QHBoxLayout()
        cta_style_label = QLabel("CTA Style:")
        cta_style_label.setMinimumWidth(150)
        cta_style_label.setFont(QFont("Arial", 10))
        cta_style_layout.addWidget(cta_style_label)

        self.cta_style_combo = QComboBox()
        self.cta_style_combo.addItems(["educational", "contextual"])
        self.cta_style_combo.setToolTip(
            "educational: neutral 'providers include X' framing.\n"
            "contextual: warmer 'ready to hire? contact X' framing."
        )
        self.cta_style_combo.currentIndexChanged.connect(self.config_changed)
        cta_style_layout.addWidget(self.cta_style_combo)
        cta_style_layout.addStretch()
        money_layout.addLayout(cta_style_layout)

        layout.addWidget(money_group)

        # -- Authoritative Sources ---------------------------------------------
        sources_group = QGroupBox("Authoritative Sources")
        sources_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        sources_layout = QVBoxLayout(sources_group)

        sources_note = QLabel(
            "One URL per line. These appear as linked references in the footer, "
            "About page, service guides, and product pages."
        )
        sources_note.setWordWrap(True)
        sources_note.setStyleSheet("color:#555; font-style:italic; font-size:9pt;")
        sources_layout.addWidget(sources_note)

        self.authoritative_sources_input = QTextEdit()
        self.authoritative_sources_input.setPlaceholderText(
            "https://www.nfpa.org\nhttps://www.ul.com\nhttps://www.ansi.org"
        )
        self.authoritative_sources_input.setMinimumHeight(100)
        self.authoritative_sources_input.setMaximumHeight(160)
        self.authoritative_sources_input.setToolTip(
            "One URL per line. Must include https://."
        )
        self.authoritative_sources_input.textChanged.connect(self.config_changed)
        sources_layout.addWidget(self.authoritative_sources_input)

        layout.addWidget(sources_group)
        layout.addStretch()

    # -- Helpers ---------------------------------------------------------------

    def _make_field(
        self,
        parent_layout: QVBoxLayout,
        label: str,
        placeholder: str,
        tooltip: str,
    ) -> QLineEdit:
        """Add a labeled QLineEdit to parent_layout and return the widget."""
        row = QHBoxLayout()
        lbl = QLabel(f"{label}:")
        lbl.setMinimumWidth(150)
        lbl.setFont(QFont("Arial", 10))
        row.addWidget(lbl)

        field = QLineEdit()
        field.setPlaceholderText(placeholder)
        field.setToolTip(tooltip)
        field.textChanged.connect(self.config_changed)
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
        """Add a labeled QTextEdit to parent_layout and return the widget."""
        lbl = QLabel(f"{label}:")
        lbl.setFont(QFont("Arial", 10))
        parent_layout.addWidget(lbl)

        field = QTextEdit()
        field.setPlaceholderText(placeholder)
        field.setToolTip(tooltip)
        field.setMinimumHeight(rows * 28)
        field.setMaximumHeight(rows * 32)
        field.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )
        field.textChanged.connect(self.config_changed)
        parent_layout.addWidget(field)
        return field

    # -- Public interface ------------------------------------------------------

    def get_config_data(self) -> Dict[str, Any]:
        """Return resource site config as a dict for use in ClientConfig construction."""
        sources_raw = self.authoritative_sources_input.toPlainText().strip()
        sources = [
            line.strip()
            for line in sources_raw.splitlines()
            if line.strip().startswith("http")
        ]
        return {
            "site_name": self.site_name_input.text().strip(),
            "site_brand": self.site_brand_input.text().strip(),
            "site_mission": self.site_mission_input.toPlainText().strip(),
            "editorial_perspective": self.editorial_perspective_input.toPlainText().strip(),
            "money_site_name": self.money_site_name_input.text().strip(),
            "money_site_url": self.money_site_url_input.text().strip(),
            "cta_style": self.cta_style_combo.currentText(),
            "authoritative_sources": sources,
        }

    def set_config_data(self, data: Dict[str, Any]):
        """Populate all fields from a dict (e.g. loaded from YAML)."""
        self.site_name_input.setText(data.get("site_name", ""))
        self.site_brand_input.setText(data.get("site_brand", ""))
        self.site_mission_input.setPlainText(data.get("site_mission", ""))
        self.editorial_perspective_input.setPlainText(
            data.get("editorial_perspective", "")
        )
        self.money_site_name_input.setText(data.get("money_site_name", ""))
        self.money_site_url_input.setText(data.get("money_site_url", ""))

        cta_style = data.get("cta_style", "educational")
        idx = self.cta_style_combo.findText(cta_style)
        if idx >= 0:
            self.cta_style_combo.setCurrentIndex(idx)

        sources: List[str] = data.get("authoritative_sources", [])
        self.authoritative_sources_input.setPlainText("\n".join(sources))

    def clear_data(self):
        """Reset all fields to empty defaults."""
        self.set_config_data({})

    def validate_data(self):
        """Validate resource site fields. All fields are optional."""
        result = ValidationResult()
        data = self.get_config_data()

        url = data.get("money_site_url", "")
        if url and not url.startswith(("http://", "https://")):
            result.add_error(
                "Money Site URL must start with http:// or https://",
                "money_site_url",
            )

        for src in data.get("authoritative_sources", []):
            if not src.startswith(("http://", "https://")):
                result.add_error(
                    f"Authoritative source URL invalid: {src}",
                    "authoritative_sources",
                )
                break

        return result.is_valid, result.errors
