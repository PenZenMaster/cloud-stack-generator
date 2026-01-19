"""
Module/Script Name: Asset Upload Tab
Path: src/ui/components/asset_upload_tab.py

Description:
UI tab for uploading arbitrary files (Excel, PDF, Word, etc.) to cloud storage
and managing uploaded asset URLs.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-01-17

Last Modified Date:
2025-01-17

Version: 1.00

Comments:
* v1.00 - Initial simplified implementation with S3 and GCS support
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QListWidget, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QProgressBar, QHeaderView, QApplication
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import csv
import logging

from ...core.deployment.asset_uploader import AssetUploader, UploadResult
from ...core.data.deployment_store import DeploymentHistoryStore

logger = logging.getLogger(__name__)


class UploadWorker(QThread):
    """Background worker for file uploads"""

    progress = pyqtSignal(int, int, str)  # current, total, filename
    finished = pyqtSignal(list)  # List[UploadResult]
    error = pyqtSignal(str)

    def __init__(self, uploader: AssetUploader, files: List[Path],
                 bucket: str, prefix: str, region: str):
        super().__init__()
        self.uploader = uploader
        self.files = files
        self.bucket = bucket
        self.prefix = prefix
        self.region = region

    def run(self):
        """Run upload in background"""
        try:
            results = self.uploader.upload_files_batch(
                files=self.files,
                bucket=self.bucket,
                prefix=self.prefix,
                region=self.region,
                progress_callback=self.progress.emit
            )
            self.finished.emit(results)
        except Exception as e:
            logger.error(f"Upload worker error: {e}")
            self.error.emit(str(e))


class AssetUploadTab(QWidget):
    """Tab for uploading assets to cloud storage"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.deployment_store: Optional[DeploymentHistoryStore] = None
        self.current_config_path: Optional[str] = None
        self.cloud_tab = None  # Reference to Cloud Deploy tab for AWS credentials
        self.selected_files: List[Path] = []
        self.uploaded_assets: List[UploadResult] = []
        self.setup_ui()

    def setup_ui(self):
        """Setup asset upload UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Asset Upload")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)

        # Description
        description = QLabel(
            "Upload files (Excel, PDF, Word, HTML, XML) to cloud storage and get public URLs."
        )
        description.setFont(QFont("Arial", 10))
        description.setWordWrap(True)
        layout.addWidget(description)

        # Configuration section
        config_layout = QVBoxLayout()

        # Provider selection
        provider_layout = QHBoxLayout()
        provider_label = QLabel("Provider:")
        provider_label.setMinimumWidth(100)
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(["AWS S3", "Google GCS"])
        provider_layout.addWidget(provider_label)
        provider_layout.addWidget(self.provider_combo)
        provider_layout.addStretch()
        config_layout.addLayout(provider_layout)

        # Bucket name (dropdown like Cloud Deploy tab)
        bucket_layout = QHBoxLayout()
        bucket_label = QLabel("Bucket:")
        bucket_label.setMinimumWidth(100)
        self.bucket_combo = QComboBox()
        self.bucket_combo.setEditable(True)
        self.bucket_combo.setPlaceholderText("Select existing or enter new bucket name")
        self.bucket_combo.lineEdit().setPlaceholderText("Enter bucket name")
        bucket_layout.addWidget(bucket_label)
        bucket_layout.addWidget(self.bucket_combo)

        # Refresh buckets button
        self.refresh_buckets_button = QPushButton("Refresh")
        self.refresh_buckets_button.setMaximumWidth(80)
        self.refresh_buckets_button.setToolTip("Load available S3 buckets")
        self.refresh_buckets_button.clicked.connect(self.refresh_bucket_list)
        bucket_layout.addWidget(self.refresh_buckets_button)

        config_layout.addLayout(bucket_layout)

        # Prefix/path
        prefix_layout = QHBoxLayout()
        prefix_label = QLabel("Path/Prefix:")
        prefix_label.setMinimumWidth(100)
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("assets/ (optional)")
        self.prefix_input.setText("assets/")
        prefix_layout.addWidget(prefix_label)
        prefix_layout.addWidget(self.prefix_input)
        config_layout.addLayout(prefix_layout)

        # Region
        region_layout = QHBoxLayout()
        region_label = QLabel("Region:")
        region_label.setMinimumWidth(100)
        self.region_input = QLineEdit()
        self.region_input.setText("us-east-1")
        self.region_input.setPlaceholderText("us-east-1")
        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_input)
        config_layout.addLayout(region_layout)

        layout.addLayout(config_layout)

        # File selection section
        file_section_label = QLabel("Select Files:")
        file_section_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(file_section_label)

        # Browse button
        browse_button = QPushButton("Browse Files...")
        browse_button.clicked.connect(self.browse_files)
        layout.addWidget(browse_button)

        # Selected files list
        self.files_list = QListWidget()
        self.files_list.setMaximumHeight(120)
        layout.addWidget(self.files_list)

        # File actions
        file_actions_layout = QHBoxLayout()
        self.clear_files_button = QPushButton("Clear Files")
        self.clear_files_button.clicked.connect(self.clear_files)
        file_actions_layout.addWidget(self.clear_files_button)
        file_actions_layout.addStretch()
        layout.addLayout(file_actions_layout)

        # Upload section
        upload_layout = QHBoxLayout()
        self.upload_button = QPushButton("Upload Files")
        self.upload_button.clicked.connect(self.upload_files)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #2563eb;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #9ca3af;
            }
        """)
        upload_layout.addWidget(self.upload_button)
        upload_layout.addStretch()
        layout.addLayout(upload_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Results section
        results_label = QLabel("Uploaded Assets:")
        results_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(results_label)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels([
            "Filename", "Size", "Provider", "URL", "Actions"
        ])

        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        self.results_table.setAlternatingRowColors(True)
        layout.addWidget(self.results_table)

        # Export actions
        export_layout = QHBoxLayout()
        self.copy_all_button = QPushButton("Copy All URLs")
        self.copy_all_button.clicked.connect(self.copy_all_urls)
        export_layout.addWidget(self.copy_all_button)

        self.export_csv_button = QPushButton("Export to CSV")
        self.export_csv_button.clicked.connect(self.export_to_csv)
        export_layout.addWidget(self.export_csv_button)

        export_layout.addStretch()
        layout.addLayout(export_layout)

        self.setLayout(layout)

    def set_deployment_store(self, store: DeploymentHistoryStore):
        """Set deployment store reference"""
        self.deployment_store = store

    def set_cloud_tab(self, cloud_tab):
        """Set reference to Cloud Deploy tab for AWS credentials access"""
        self.cloud_tab = cloud_tab

    def set_config_path(self, config_path: str):
        """Set current config path"""
        self.current_config_path = config_path

    def browse_files(self):
        """Open file browser to select files"""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files to Upload",
            "",
            "All Files (*.*);;"
            "Excel Files (*.xlsx *.xls);;"
            "PDF Files (*.pdf);;"
            "Word Files (*.docx *.doc);;"
            "HTML Files (*.html *.htm);;"
            "XML Files (*.xml)"
        )

        if files:
            self.selected_files.extend([Path(f) for f in files])
            self.refresh_files_list()

    def clear_files(self):
        """Clear selected files"""
        self.selected_files.clear()
        self.files_list.clear()

    def refresh_files_list(self):
        """Refresh files list display"""
        self.files_list.clear()
        for file_path in self.selected_files:
            size_mb = file_path.stat().st_size / (1024 * 1024)
            self.files_list.addItem(f"{file_path.name} ({size_mb:.2f} MB)")

    def refresh_bucket_list(self):
        """Refresh list of available S3 buckets using Cloud Deploy AWS credentials"""
        provider = self.provider_combo.currentText()

        if provider != "AWS S3":
            QMessageBox.information(
                self,
                "Not Supported",
                "Bucket refresh is only supported for AWS S3.\n"
                "For Google GCS, please enter the bucket name manually."
            )
            return

        # Check if cloud_tab reference is available
        if not self.cloud_tab:
            QMessageBox.warning(
                self,
                "Configuration Required",
                "Please configure AWS credentials in the Cloud Deploy tab first."
            )
            return

        # Get selected AWS profile from Cloud Deploy tab
        profile_name = self.cloud_tab.profile_combo.currentText()
        if not profile_name or profile_name == "No profiles configured":
            QMessageBox.warning(
                self,
                "No AWS Profile",
                "Please select an AWS profile in the Cloud Deploy tab first."
            )
            return

        try:
            # Use Cloud Deploy tab's credentials manager to get AWS session
            credentials_manager = self.cloud_tab.credentials_manager

            if profile_name not in credentials_manager.profiles:
                QMessageBox.warning(
                    self,
                    "Profile Not Found",
                    f"AWS profile '{profile_name}' not found.\n"
                    f"Please configure it in the Cloud Deploy tab."
                )
                return

            # Get AWS session for the selected profile
            session = credentials_manager._get_session(profile_name)
            if not session:
                QMessageBox.warning(
                    self,
                    "Session Error",
                    f"Could not create AWS session for profile '{profile_name}'.\n"
                    f"Please verify the profile configuration in Cloud Deploy tab."
                )
                return

            # List buckets using the authenticated session
            s3_client = session.client('s3')
            response = s3_client.list_buckets()
            buckets = [b['Name'] for b in response.get('Buckets', [])]

            # Store current selection
            current_bucket = self.bucket_combo.currentText()

            # Clear and populate combo
            self.bucket_combo.clear()

            if buckets:
                for bucket_name in buckets:
                    self.bucket_combo.addItem(bucket_name)

                # Restore selection if it exists
                if current_bucket in buckets:
                    self.bucket_combo.setCurrentText(current_bucket)

                QMessageBox.information(
                    self,
                    "Buckets Loaded",
                    f"Found {len(buckets)} S3 bucket(s) using profile '{profile_name}'."
                )
            else:
                self.bucket_combo.addItem("No buckets found")
                QMessageBox.information(
                    self,
                    "No Buckets",
                    f"No S3 buckets found for profile '{profile_name}'."
                )

        except Exception as e:
            logger.error(f"Failed to refresh bucket list: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load S3 buckets:\n{str(e)}\n\n"
                f"Please verify your AWS credentials in the Cloud Deploy tab."
            )

    def upload_files(self):
        """Upload selected files to cloud storage"""
        # Validate inputs
        if not self.selected_files:
            QMessageBox.warning(self, "No Files", "Please select files to upload.")
            return

        bucket = self.bucket_combo.currentText().strip()
        if not bucket:
            QMessageBox.warning(self, "No Bucket", "Please enter a bucket name.")
            return

        provider = self.provider_combo.currentText()
        prefix = self.prefix_input.text().strip()
        region = self.region_input.text().strip() or 'us-east-1'

        # Get credentials using Cloud Deploy tab's AWS credentials manager
        if provider == "AWS S3":
            # Check if cloud_tab reference is available
            if not self.cloud_tab:
                QMessageBox.warning(
                    self,
                    "Configuration Required",
                    "Please configure AWS credentials in the Cloud Deploy tab first."
                )
                return

            # Get selected AWS profile from Cloud Deploy tab
            profile_name = self.cloud_tab.profile_combo.currentText()
            if not profile_name or profile_name == "No profiles configured":
                QMessageBox.warning(
                    self,
                    "No AWS Profile",
                    "Please select an AWS profile in the Cloud Deploy tab first."
                )
                return

            # Use Cloud Deploy tab's credentials manager to get AWS session
            credentials_manager = self.cloud_tab.credentials_manager

            if profile_name not in credentials_manager.profiles:
                QMessageBox.warning(
                    self,
                    "Profile Not Found",
                    f"AWS profile '{profile_name}' not found.\n"
                    f"Please configure it in the Cloud Deploy tab."
                )
                return

            # Get AWS session for the selected profile
            session = credentials_manager._get_session(profile_name)
            if not session:
                QMessageBox.warning(
                    self,
                    "Session Error",
                    f"Could not create AWS session for profile '{profile_name}'.\n"
                    f"Please verify the profile configuration in Cloud Deploy tab."
                )
                return

            # Pass session directly to AssetUploader (will create boto3.Session internally)
            # For now, pass profile_name and let AssetUploader handle session creation
            credentials = {'profile_name': profile_name, 'session': session}
            provider_type = 'aws_s3'

        elif provider == "Google GCS":
            # Would need GCS credentials from config
            QMessageBox.warning(
                self,
                "GCS Not Configured",
                "Google Cloud Storage support requires service account configuration.\n"
                "Please use AWS S3 for now."
            )
            return
        else:
            QMessageBox.warning(self, "Invalid Provider", f"Unknown provider: {provider}")
            return

        # Create uploader
        try:
            uploader = AssetUploader(provider_type, credentials)
        except Exception as e:
            QMessageBox.critical(self, "Upload Error", f"Failed to initialize uploader: {e}")
            return

        # Start upload worker
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, len(self.selected_files))
        self.progress_bar.setValue(0)
        self.upload_button.setEnabled(False)

        self.upload_worker = UploadWorker(
            uploader, self.selected_files, bucket, prefix, region
        )
        self.upload_worker.progress.connect(self.on_upload_progress)
        self.upload_worker.finished.connect(self.on_upload_finished)
        self.upload_worker.error.connect(self.on_upload_error)
        self.upload_worker.start()

    def on_upload_progress(self, current: int, total: int, filename: str):
        """Handle upload progress"""
        self.progress_bar.setValue(current)
        logger.info(f"Uploading ({current}/{total}): {filename}")

    def on_upload_finished(self, results: List[UploadResult]):
        """Handle upload completion"""
        self.progress_bar.setVisible(False)
        self.upload_button.setEnabled(True)

        # Add results to uploaded assets
        self.uploaded_assets.extend(results)

        # Update results table
        self.populate_results_table()

        # Save to database
        if self.deployment_store and self.current_config_path:
            for result in results:
                if result.success:
                    try:
                        self.deployment_store.save_uploaded_asset(
                            config_file_path=self.current_config_path,
                            business_name="",  # Would need from config
                            filename=result.filename,
                            file_size=result.size_bytes,
                            file_type=result.file_type,
                            provider=result.provider,
                            bucket=result.bucket,
                            remote_path=result.remote_path,
                            region=result.region,
                            public_url=result.public_url
                        )
                    except Exception as e:
                        logger.error(f"Failed to save asset to database: {e}")

        # Clear selected files
        self.clear_files()

        # Show summary
        success_count = sum(1 for r in results if r.success)
        fail_count = len(results) - success_count

        if fail_count == 0:
            QMessageBox.information(
                self,
                "Upload Complete",
                f"Successfully uploaded {success_count} file(s)!"
            )
        else:
            QMessageBox.warning(
                self,
                "Upload Complete with Errors",
                f"Uploaded: {success_count}\nFailed: {fail_count}\n\n"
                f"Check the results table for details."
            )

    def on_upload_error(self, error_msg: str):
        """Handle upload error"""
        self.progress_bar.setVisible(False)
        self.upload_button.setEnabled(True)
        QMessageBox.critical(self, "Upload Error", f"Upload failed: {error_msg}")

    def populate_results_table(self):
        """Populate results table with uploaded assets"""
        self.results_table.setRowCount(len(self.uploaded_assets))

        for row, result in enumerate(self.uploaded_assets):
            # Filename
            self.results_table.setItem(row, 0, QTableWidgetItem(result.filename))

            # Size
            size_str = AssetUploader.format_file_size(result.size_bytes)
            self.results_table.setItem(row, 1, QTableWidgetItem(size_str))

            # Provider
            self.results_table.setItem(row, 2, QTableWidgetItem(result.provider))

            # URL
            if result.success:
                self.results_table.setItem(row, 3, QTableWidgetItem(result.public_url))
            else:
                error_item = QTableWidgetItem(f"ERROR: {result.error_message}")
                error_item.setForeground(Qt.GlobalColor.red)
                self.results_table.setItem(row, 3, error_item)

            # Actions - Copy button
            copy_button = QPushButton("Copy URL")
            copy_button.clicked.connect(lambda checked, url=result.public_url: self.copy_url(url))
            copy_button.setEnabled(result.success)
            self.results_table.setCellWidget(row, 4, copy_button)

    def copy_url(self, url: str):
        """Copy URL to clipboard"""
        clipboard = QApplication.clipboard()
        clipboard.setText(url)
        self.statusBar().showMessage(f"URL copied to clipboard", 2000) if hasattr(self, 'statusBar') else None

    def copy_all_urls(self):
        """Copy all URLs to clipboard"""
        urls = [r.public_url for r in self.uploaded_assets if r.success]

        if not urls:
            QMessageBox.information(self, "No URLs", "No uploaded assets to copy.")
            return

        clipboard = QApplication.clipboard()
        clipboard.setText('\n'.join(urls))

        QMessageBox.information(
            self,
            "URLs Copied",
            f"Copied {len(urls)} URL(s) to clipboard."
        )

    def export_to_csv(self):
        """Export uploaded assets to CSV"""
        if not self.uploaded_assets:
            QMessageBox.information(self, "No Data", "No uploaded assets to export.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Assets to CSV",
            "uploaded_assets.csv",
            "CSV Files (*.csv)"
        )

        if not file_path:
            return

        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                fieldnames = [
                    'filename', 'size_bytes', 'file_type', 'provider',
                    'bucket', 'region', 'public_url', 'uploaded_at', 'success'
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()

                for asset in self.uploaded_assets:
                    writer.writerow({
                        'filename': asset.filename,
                        'size_bytes': asset.size_bytes,
                        'file_type': asset.file_type,
                        'provider': asset.provider,
                        'bucket': asset.bucket,
                        'region': asset.region,
                        'public_url': asset.public_url if asset.success else asset.error_message,
                        'uploaded_at': asset.uploaded_at.isoformat(),
                        'success': asset.success
                    })

            QMessageBox.information(
                self,
                "Export Successful",
                f"Exported {len(self.uploaded_assets)} asset(s) to:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export CSV: {e}"
            )
