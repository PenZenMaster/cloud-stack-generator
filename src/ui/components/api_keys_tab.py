"""
Module/Script Name: API Keys Tab
Path: src/ui/components/api_keys_tab.py

Description:
Tab for managing API keys for all external service integrations.
Reads from and writes to the project .env file (single source of truth).
Provides per-service live connection testing.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2025-08-15

Last Modified Date:
2026-03-11

Comments:
* v1.01 - Added Claude AI and OpenAI key fields; migrated storage from
          config/api_keys.json to .env (single source of truth); replaced
          legacy Places API test with Places API (New) test; added Claude
          and OpenAI connection tests
* v1.00 - Initial implementation (Google Maps only, config/api_keys.json storage)
"""

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QGroupBox,
    QMessageBox,
    QFrame,
)
from typing import Dict, Any

from .base_tab import BaseTab, ValidationResult


class APIKeysTab(BaseTab):
    """Tab for managing API keys for all external service integrations."""

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup the API Keys tab UI."""
        if self.layout() is not None:
            return

        layout = QVBoxLayout()

        title_label = QLabel("API Keys & Integrations")
        title_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; margin-bottom: 10px;"
        )

        description_label = QLabel(
            "Manage API keys for external services. "
            "Keys are saved directly to the project .env file and take effect immediately."
        )
        description_label.setStyleSheet(
            "color: #666; font-style: italic; margin-bottom: 20px;"
        )
        description_label.setWordWrap(True)

        layout.addWidget(title_label)
        layout.addWidget(description_label)

        layout.addWidget(self._make_google_section())
        layout.addWidget(self._make_claude_section())
        layout.addWidget(self._make_openai_section())
        layout.addWidget(self._make_actions_section())

        layout.addStretch()
        self.setLayout(layout)

    # ------------------------------------------------------------------
    # Section builders
    # ------------------------------------------------------------------

    def _make_google_section(self) -> QGroupBox:
        """Google Maps / Places API (New) section."""
        group = QGroupBox("Google Maps Integration  (GOOGLE_MAPS_API_KEY)")
        layout = QVBoxLayout()

        row, self.maps_api_key, _ = self._make_key_row("Google Maps API key")
        layout.addLayout(row)

        note = QLabel(
            "Required for GBP onboarding lookup. "
            "Enable 'Places API (New)' in Google Cloud Console > APIs & Services > Library."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-style: italic; margin-top: 6px;")
        layout.addWidget(note)

        group.setLayout(layout)
        return group

    def _make_claude_section(self) -> QGroupBox:
        """Anthropic / Claude API section."""
        group = QGroupBox("Claude AI / Anthropic  (CLAUDE_API_KEY)")
        layout = QVBoxLayout()

        row, self.claude_api_key, _ = self._make_key_row("Anthropic API key")
        layout.addLayout(row)

        note = QLabel(
            "Required for auto-onboarding website extraction and SEO analysis. "
            "Get your key at console.anthropic.com."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-style: italic; margin-top: 6px;")
        layout.addWidget(note)

        group.setLayout(layout)
        return group

    def _make_openai_section(self) -> QGroupBox:
        """OpenAI API section."""
        group = QGroupBox("OpenAI  (OPENAI_API_KEY)")
        layout = QVBoxLayout()

        row, self.openai_api_key, _ = self._make_key_row("OpenAI API key")
        layout.addLayout(row)

        note = QLabel(
            "Used for AI content generation. "
            "Get your key at platform.openai.com."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666; font-style: italic; margin-top: 6px;")
        layout.addWidget(note)

        group.setLayout(layout)
        return group

    def _make_actions_section(self) -> QFrame:
        """Save and Test buttons."""
        frame = QFrame()
        layout = QHBoxLayout()

        self.save_btn = QPushButton("Save API Keys")
        self.save_btn.clicked.connect(self.save_api_keys)

        self.test_btn = QPushButton("Test Connections")
        self.test_btn.clicked.connect(self.test_connections)

        layout.addWidget(self.save_btn)
        layout.addWidget(self.test_btn)
        layout.addStretch()

        frame.setLayout(layout)
        return frame

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _make_key_row(
        self, label_text: str
    ) -> tuple:
        """Create a labelled password field with a Show/Hide toggle button."""
        row = QHBoxLayout()

        field = QLineEdit()
        field.setPlaceholderText(f"Enter your {label_text}")
        field.setEchoMode(QLineEdit.EchoMode.Password)

        toggle_btn = QPushButton("Show")
        toggle_btn.setMaximumWidth(50)
        toggle_btn.setToolTip("Show / Hide key")
        toggle_btn.clicked.connect(
            lambda _checked, f=field, b=toggle_btn: self._toggle_visibility(f, b)
        )

        row.addWidget(QLabel("API Key:"))
        row.addWidget(field)
        row.addWidget(toggle_btn)
        return row, field, toggle_btn

    def _toggle_visibility(self, field: QLineEdit, btn: QPushButton):
        """Toggle between Password and Normal echo mode."""
        if field.echoMode() == QLineEdit.EchoMode.Password:
            field.setEchoMode(QLineEdit.EchoMode.Normal)
            btn.setText("Hide")
        else:
            field.setEchoMode(QLineEdit.EchoMode.Password)
            btn.setText("Show")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def save_api_keys(self):
        """Save all entered API keys to .env via the main window."""
        try:
            api_keys = {
                "google_maps_api_key": self.maps_api_key.text().strip(),
                "claude_api_key": self.claude_api_key.text().strip(),
                "openai_api_key": self.openai_api_key.text().strip(),
            }

            if not any(api_keys.values()):
                QMessageBox.warning(
                    self,
                    "No Keys Entered",
                    "Please enter at least one API key before saving.",
                )
                return

            main_window = self.window()
            if hasattr(main_window, "save_app_api_keys"):
                main_window.save_app_api_keys(api_keys)
                saved_names = [k for k, v in api_keys.items() if v]
                QMessageBox.information(
                    self,
                    "Saved",
                    f"Saved {len(saved_names)} key(s) to .env:\n"
                    + "\n".join(f"  - {n}" for n in saved_names),
                )
            else:
                QMessageBox.critical(self, "Error", "Could not access main window.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save API keys:\n{str(e)}")

    def test_connections(self):
        """Test each configured key against its live API."""
        from PyQt6.QtWidgets import QProgressDialog
        from PyQt6.QtCore import Qt

        keys = {
            "google_maps": self.maps_api_key.text().strip(),
            "claude": self.claude_api_key.text().strip(),
            "openai": self.openai_api_key.text().strip(),
        }

        if not any(keys.values()):
            QMessageBox.warning(
                self, "No Keys", "Enter at least one API key to test."
            )
            return

        progress = QProgressDialog("Testing API connections...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModality.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()

        results: Dict[str, tuple] = {}
        try:
            import requests as req

            # Google Maps: Places API (New)
            if keys["google_maps"]:
                progress.setLabelText("Testing Google Places API (New)...")
                try:
                    resp = req.post(
                        "https://places.googleapis.com/v1/places:searchText",
                        headers={
                            "X-Goog-Api-Key": keys["google_maps"],
                            "X-Goog-FieldMask": "places.id",
                            "Content-Type": "application/json",
                        },
                        json={"textQuery": "coffee shop"},
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        results["Google Maps (Places API New)"] = ("PASS", "")
                    else:
                        err = resp.json().get("error", {}).get(
                            "message", resp.text[:160]
                        )
                        results["Google Maps (Places API New)"] = (
                            "FAIL",
                            err,
                        )
                except Exception as exc:
                    results["Google Maps (Places API New)"] = ("ERROR", str(exc))

            # Claude / Anthropic
            if keys["claude"]:
                progress.setLabelText("Testing Claude (Anthropic) API...")
                try:
                    resp = req.get(
                        "https://api.anthropic.com/v1/models",
                        headers={
                            "x-api-key": keys["claude"],
                            "anthropic-version": "2023-06-01",
                        },
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        results["Claude (Anthropic)"] = ("PASS", "")
                    else:
                        err = resp.json().get("error", {}).get(
                            "message", resp.text[:160]
                        )
                        results["Claude (Anthropic)"] = ("FAIL", err)
                except Exception as exc:
                    results["Claude (Anthropic)"] = ("ERROR", str(exc))

            # OpenAI
            if keys["openai"]:
                progress.setLabelText("Testing OpenAI API...")
                try:
                    resp = req.get(
                        "https://api.openai.com/v1/models",
                        headers={"Authorization": f"Bearer {keys['openai']}"},
                        timeout=10,
                    )
                    if resp.status_code == 200:
                        results["OpenAI"] = ("PASS", "")
                    else:
                        err = resp.json().get("error", {}).get(
                            "message", resp.text[:160]
                        )
                        results["OpenAI"] = ("FAIL", err)
                except Exception as exc:
                    results["OpenAI"] = ("ERROR", str(exc))

        finally:
            progress.close()

        # Build result message
        sym = {"PASS": "+", "FAIL": "-", "ERROR": "X"}
        lines = ["Connection Test Results", "=" * 44, ""]
        for name, (status, detail) in results.items():
            lines.append(f"  [{sym[status]}] {name}: {status}")
            if detail:
                lines.append(f"       {detail}")

        lines.append("")
        all_pass = all(s == "PASS" for s, _ in results.values())
        any_fail = any(s in ("FAIL", "ERROR") for s, _ in results.values())

        if all_pass:
            lines.append("All tested connections are working.")
            icon = QMessageBox.Icon.Information
        elif any_fail:
            lines.append("One or more connections failed - check details above.")
            icon = QMessageBox.Icon.Warning
        else:
            icon = QMessageBox.Icon.Information

        from PyQt6.QtCore import Qt

        box = QMessageBox(
            icon,
            "Connection Test",
            "\n".join(lines),
            QMessageBox.StandardButton.Ok,
            self,
        )
        box.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        box.exec()

    # ------------------------------------------------------------------
    # BaseTab interface
    # ------------------------------------------------------------------

    def get_config_data(self) -> Dict[str, Any]:
        return {
            "google_maps_api_key": self.maps_api_key.text().strip(),
            "claude_api_key": self.claude_api_key.text().strip(),
            "openai_api_key": self.openai_api_key.text().strip(),
        }

    def set_config_data(self, data: Dict[str, Any]):
        self.maps_api_key.setText(data.get("google_maps_api_key", ""))
        self.claude_api_key.setText(data.get("claude_api_key", ""))
        self.openai_api_key.setText(data.get("openai_api_key", ""))

    def get_required_fields(self) -> list:
        return []

    def validate_data(self) -> ValidationResult:
        result = super().validate_data()
        for label, widget in [
            ("Google Maps API key", self.maps_api_key),
            ("Claude API key", self.claude_api_key),
            ("OpenAI API key", self.openai_api_key),
        ]:
            val = widget.text().strip()
            if val and len(val) < 10:
                result.add_error(f"{label} appears too short", label)
        return result
