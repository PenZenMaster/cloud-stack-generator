"""
Module/Script Name: batch_generate_dialog.py
Path: src/ui/dialogs/batch_generate_dialog.py

Description:
Modal dialog for batch (multi-client) website generation. Users select a
directory containing YAML client config files, choose which configs to
process, pick a base output folder, and run generation for all selected
clients sequentially. A live log panel shows per-client progress and a
results summary is displayed on completion.

Author(s):
Rank Rocket Co (C) Copyright 2026 - All Rights Reserved

Created Date:
2026-03-22

Last Modified Date:
2026-03-22

Comments:
* v1.00 - Initial implementation for Sprint 5 batch/multi-client feature
"""

from pathlib import Path
from typing import List

from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ...core.utils.logger import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------------------------- #
# Worker thread
# ------------------------------------------------------------------------------- #


class BatchWorker(QThread):
    """Runs sequential generation for a list of (config_path, output_dir) pairs."""

    log = pyqtSignal(str)           # progress messages
    client_done = pyqtSignal(str, bool, str)  # (config_name, success, message)
    all_done = pyqtSignal(int, int)  # (success_count, fail_count)

    def __init__(self, jobs: List[tuple], parent=None):
        """
        Args:
            jobs: list of (yaml_path: str, output_dir: str) tuples
        """
        super().__init__(parent)
        self.jobs = jobs
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        from ...core.config.parser import ConfigParser
        from ...core.generators.page_generator import PageGenerator

        parser = ConfigParser()
        success_count = 0
        fail_count = 0

        for yaml_path, output_dir in self.jobs:
            if self._cancelled:
                self.log.emit("[CANCELLED] Batch run cancelled by user.")
                break

            name = Path(yaml_path).stem
            self.log.emit(f"\n[START] {name}")

            try:
                config = parser.parse_yaml_file(yaml_path)
                config.config_file_path = str(Path(yaml_path).resolve())
                generator = PageGenerator(output_base_dir=output_dir)
                result = generator.generate_complete_website(config)

                if result.success:
                    page_count = len(result.generated_files)
                    self.log.emit(f"[OK]    {name} - {page_count} files -> {output_dir}")
                    self.client_done.emit(name, True, f"{page_count} files generated")
                    success_count += 1
                else:
                    err = getattr(result, "errors", "unknown error")
                    self.log.emit(f"[FAIL]  {name} - {err}")
                    self.client_done.emit(name, False, str(err))
                    fail_count += 1

            except Exception as exc:
                self.log.emit(f"[ERROR] {name} - {exc}")
                self.client_done.emit(name, False, str(exc))
                fail_count += 1

        self.all_done.emit(success_count, fail_count)


# ------------------------------------------------------------------------------- #
# Dialog
# ------------------------------------------------------------------------------- #


class BatchGenerateDialog(QDialog):
    """Multi-client batch generation dialog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Batch Generate - Multiple Clients")
        self.setMinimumSize(780, 600)
        self._worker: BatchWorker = None
        self._yaml_paths: List[str] = []
        self._setup_ui()

    # ---- UI ------------------------------------------------------------------ #

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        # Info banner
        info = QLabel(
            "Select a folder containing client YAML configs, choose which to process, "
            "set a base output folder, then click Generate. Each client's site is "
            "written to <output_base>/<config_stem>/."
        )
        info.setWordWrap(True)
        info.setStyleSheet(
            "background:#e8f4fd; border:1px solid #bee5eb; border-radius:4px; "
            "padding:8px; color:#0c5460;"
        )
        layout.addWidget(info)

        # Config directory row
        config_group = QGroupBox("1. Config Directory")
        config_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        cg_layout = QHBoxLayout(config_group)
        self.config_dir_input = QLineEdit()
        self.config_dir_input.setPlaceholderText("Path to folder containing *.yaml client configs...")
        self.config_dir_input.setReadOnly(True)
        cg_layout.addWidget(self.config_dir_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_config_dir)
        cg_layout.addWidget(browse_btn)
        layout.addWidget(config_group)

        # Config list
        list_group = QGroupBox("2. Select Configs to Process")
        list_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        list_layout = QVBoxLayout(list_group)

        ctrl_row = QHBoxLayout()
        select_all_btn = QPushButton("Select All")
        select_all_btn.clicked.connect(self._select_all)
        ctrl_row.addWidget(select_all_btn)
        deselect_btn = QPushButton("Deselect All")
        deselect_btn.clicked.connect(self._deselect_all)
        ctrl_row.addWidget(deselect_btn)
        ctrl_row.addStretch()
        self.count_label = QLabel("0 configs found")
        self.count_label.setStyleSheet("color:#555; font-style:italic;")
        ctrl_row.addWidget(self.count_label)
        list_layout.addLayout(ctrl_row)

        self.config_list = QListWidget()
        self.config_list.setMinimumHeight(140)
        self.config_list.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        list_layout.addWidget(self.config_list)
        layout.addWidget(list_group)

        # Output directory row
        out_group = QGroupBox("3. Base Output Directory")
        out_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        og_layout = QHBoxLayout(out_group)
        self.output_dir_input = QLineEdit()
        self.output_dir_input.setPlaceholderText("Base output folder (one sub-folder per client)...")
        self.output_dir_input.setReadOnly(True)
        og_layout.addWidget(self.output_dir_input)
        out_browse_btn = QPushButton("Browse...")
        out_browse_btn.clicked.connect(self._browse_output_dir)
        og_layout.addWidget(out_browse_btn)
        layout.addWidget(out_group)

        # Progress + log
        log_group = QGroupBox("Progress")
        log_group.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        log_layout = QVBoxLayout(log_group)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        log_layout.addWidget(self.progress_bar)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Courier New", 9))
        self.log_output.setMinimumHeight(120)
        log_layout.addWidget(self.log_output)
        layout.addWidget(log_group)

        # Button row
        btn_row = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Selected")
        self.generate_btn.setStyleSheet(
            "QPushButton { background-color:#28a745; color:white; font-weight:bold; "
            "padding:8px 20px; border:none; border-radius:4px; } "
            "QPushButton:hover { background-color:#218838; } "
            "QPushButton:disabled { background-color:#95a5a6; }"
        )
        self.generate_btn.clicked.connect(self._start_batch)
        btn_row.addWidget(self.generate_btn)

        self.cancel_btn = QPushButton("Cancel Run")
        self.cancel_btn.setEnabled(False)
        self.cancel_btn.setStyleSheet(
            "QPushButton { background-color:#e74c3c; color:white; font-weight:bold; "
            "padding:8px 20px; border:none; border-radius:4px; } "
            "QPushButton:hover { background-color:#c0392b; } "
            "QPushButton:disabled { background-color:#95a5a6; }"
        )
        self.cancel_btn.clicked.connect(self._cancel_batch)
        btn_row.addWidget(self.cancel_btn)

        btn_row.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

    # ---- Slots --------------------------------------------------------------- #

    def _browse_config_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Config Directory", str(Path.cwd())
        )
        if directory:
            self.config_dir_input.setText(directory)
            self._scan_configs(directory)

    def _scan_configs(self, directory: str):
        """Scan directory for YAML files and populate the list."""
        self.config_list.clear()
        self._yaml_paths = []

        yaml_files = sorted(
            list(Path(directory).glob("*.yaml")) + list(Path(directory).glob("*.yml"))
        )

        for path in yaml_files:
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, str(path))
            item.setCheckState(Qt.CheckState.Checked)
            self.config_list.addItem(item)
            self._yaml_paths.append(str(path))

        count = len(yaml_files)
        self.count_label.setText(f"{count} config{'s' if count != 1 else ''} found")
        if count == 0:
            self._log("No YAML files found in selected directory.")

    def _browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(
            self, "Select Base Output Directory", str(Path.cwd() / "output" / "clients")
        )
        if directory:
            self.output_dir_input.setText(directory)

    def _select_all(self):
        for i in range(self.config_list.count()):
            self.config_list.item(i).setCheckState(Qt.CheckState.Checked)

    def _deselect_all(self):
        for i in range(self.config_list.count()):
            self.config_list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def _start_batch(self):
        # Collect selected jobs
        output_base = self.output_dir_input.text().strip()
        if not output_base:
            QMessageBox.warning(self, "Missing Output", "Please select a base output directory.")
            return

        jobs = []
        for i in range(self.config_list.count()):
            item = self.config_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                yaml_path = item.data(Qt.ItemDataRole.UserRole)
                stem = Path(yaml_path).stem
                output_dir = str(Path(output_base) / stem)
                jobs.append((yaml_path, output_dir))

        if not jobs:
            QMessageBox.warning(self, "Nothing Selected", "Select at least one config to process.")
            return

        self.log_output.clear()
        self._log(f"Starting batch run: {len(jobs)} client(s)")
        self.progress_bar.setMaximum(len(jobs))
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self._set_running(True)

        self._worker = BatchWorker(jobs, parent=self)
        self._worker.log.connect(self._log)
        self._worker.client_done.connect(self._on_client_done)
        self._worker.all_done.connect(self._on_all_done)
        self._worker.start()

    def _cancel_batch(self):
        if self._worker and self._worker.isRunning():
            self._worker.cancel()

    def _on_client_done(self, name: str, success: bool, message: str):
        current = self.progress_bar.value()
        self.progress_bar.setValue(current + 1)

    def _on_all_done(self, success_count: int, fail_count: int):
        self._set_running(False)
        total = success_count + fail_count
        self._log(
            f"\n[SUMMARY] Batch complete: {success_count}/{total} succeeded, "
            f"{fail_count} failed."
        )
        if fail_count == 0:
            QMessageBox.information(
                self, "Batch Complete",
                f"All {success_count} client(s) generated successfully."
            )
        else:
            QMessageBox.warning(
                self, "Batch Complete",
                f"{success_count} succeeded, {fail_count} failed. "
                "See log for details."
            )

    # ---- Helpers ------------------------------------------------------------- #

    def _log(self, message: str):
        self.log_output.append(message)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum()
        )

    def _set_running(self, running: bool):
        self.generate_btn.setEnabled(not running)
        self.cancel_btn.setEnabled(running)
