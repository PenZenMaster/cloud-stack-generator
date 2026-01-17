"""
Module/Script Name: Deployment History Tab
Path: src/ui/components/deployment_history_tab.py

Description:
Multi-deployment management UI showing all deployments for the current client
configuration with ability to delete deployments and edit friendly names inline.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-09-15

Last Modified Date:
2025-12-20

Version: v3.21

Comments:
* v3.21 - Standardized text sizing across all deployment card labels (10pt Arial)
* v3.20 - Added inline friendly name editing, removed non-functional buttons
* v3.2.0 - Phase 2 Implementation baseline
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QMessageBox, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QFont
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import csv

from src.core.config.models import DeploymentConfig, ClientConfig
from src.core.data.deployment_store import DeploymentHistoryStore
from src.core.config.parser import load_config_from_file
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DeploymentCard(QFrame):
    """Card widget displaying a single deployment with actions"""

    # Signals
    redeploy_requested = pyqtSignal(str)  # deployment_id
    edit_requested = pyqtSignal(str)  # deployment_id
    delete_requested = pyqtSignal(str)  # deployment_id
    friendly_name_changed = pyqtSignal(str, str)  # deployment_id, new_name

    def __init__(self, deployment: DeploymentConfig, parent=None):
        super().__init__(parent)
        self.deployment = deployment
        self.setup_ui()

    def setup_ui(self):
        """Setup deployment card UI"""
        self.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Raised)
        self.setLineWidth(1)

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # Header: Friendly Name (PRIMARY) - Inline Editable
        header_layout = QHBoxLayout()

        # Display friendly name as editable line edit (inline editing like Business Name)
        display_name = self.deployment.friendly_name or self.deployment.deployment_id

        from PyQt6.QtWidgets import QLineEdit
        from PyQt6.QtGui import QFont

        self.friendly_name_input = QLineEdit()
        self.friendly_name_input.setText(display_name)
        self.friendly_name_input.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.friendly_name_input.setMinimumWidth(400)
        self.friendly_name_input.setPlaceholderText("Enter deployment name...")
        self.friendly_name_input.editingFinished.connect(self.on_friendly_name_edited)
        header_layout.addWidget(self.friendly_name_input)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Technical ID (if different from friendly name)
        if self.deployment.friendly_name:
            tech_id_label = QLabel(f"<small><i>ID: {self.deployment.deployment_id}</i></small>")
            tech_id_label.setFont(QFont("Arial", 9))
            tech_id_label.setStyleSheet("color: #666;")
            layout.addWidget(tech_id_label)

        # Industry snapshot line
        if self.deployment.industry:
            industry_label = QLabel(f"<b>Industry:</b> {self.deployment.industry}")
            industry_label.setFont(QFont("Arial", 10))
            industry_label.setStyleSheet("color: #2c5282; font-weight: 500;")
            layout.addWidget(industry_label)

        # Info line 1: Bucket and directory
        bucket_dir_label = QLabel(
            f"<b>Bucket:</b> {self.deployment.bucket} "
            f"<b>Directory:</b> {self.deployment.directory or '(root)'}"
        )
        bucket_dir_label.setFont(QFont("Arial", 10))
        layout.addWidget(bucket_dir_label)

        # Info line 2: Mode and region
        mode_text = "CloudFront + OAC" if self.deployment.mode == "cloudfront" else "S3 Only"
        mode_region_label = QLabel(
            f"<b>Mode:</b> {mode_text} | "
            f"<b>Region:</b> {self.deployment.region}"
        )
        mode_region_label.setFont(QFont("Arial", 10))
        layout.addWidget(mode_region_label)

        # Info line 3: CloudFront details (if Mode B)
        if self.deployment.mode == "cloudfront" and self.deployment.cloudfront_distribution_id:
            cf_label = QLabel(
                f"<b>Distribution:</b> {self.deployment.cloudfront_distribution_id}"
            )
            cf_label.setFont(QFont("Arial", 10))
            layout.addWidget(cf_label)

        # Info line 4: Last deployed
        if self.deployment.last_deployed:
            try:
                dt = datetime.fromisoformat(self.deployment.last_deployed.replace('Z', '+00:00'))
                last_deployed_str = dt.strftime("%Y-%m-%d %I:%M %p")
            except Exception:
                last_deployed_str = self.deployment.last_deployed

            last_deployed_label = QLabel(f"<b>Last Deployed:</b> {last_deployed_str}")
            last_deployed_label.setFont(QFont("Arial", 10))
            layout.addWidget(last_deployed_label)

        # Info line 5: Website URL
        website_url = self.deployment.get_website_url()
        if website_url:
            url_label = QLabel(f'<b>URL:</b> <a href="{website_url}">{website_url}</a>')
            url_label.setFont(QFont("Arial", 10))
            url_label.setOpenExternalLinks(True)
            url_label.setWordWrap(True)
            layout.addWidget(url_label)

        # Info line 6: Meta tags count
        if self.deployment.meta_tags:
            meta_tags_label = QLabel(f"<b>Meta Tags:</b> {len(self.deployment.meta_tags)} configured")
            meta_tags_label.setFont(QFont("Arial", 10))
            layout.addWidget(meta_tags_label)

        # Action buttons
        button_layout = QHBoxLayout()

        # NOTE: Re-Deploy and Update Meta Tags buttons removed (non-functional stubs)
        # Only keep functional Delete button

        self.delete_button = QPushButton("Delete")
        self.delete_button.setToolTip("Remove this deployment configuration")
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(self.deployment.deployment_id))
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_friendly_name_edited(self):
        """Handle inline friendly name editing when user finishes editing"""
        new_name = self.friendly_name_input.text().strip()

        if new_name and new_name != self.deployment.friendly_name:
            # Update deployment
            self.deployment.friendly_name = new_name

            # Emit signal to parent to save config
            self.friendly_name_changed.emit(self.deployment.deployment_id, new_name)


class DeploymentHistoryTab(QWidget):
    """Tab showing deployment history and management"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config_path: Optional[str] = None  # Changed from current_config
        self.deployment_store = DeploymentHistoryStore()
        self.deployment_cards: List[DeploymentCard] = []
        self.setup_ui()

    def setup_ui(self):
        """Setup deployment history UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("Deployment History")
        header.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(header)

        # Description
        description = QLabel(
            "Manage multiple deployments for this client. Each deployment can have "
            "different meta tags, CloudFront settings, and destination directories."
        )
        description.setFont(QFont("Arial", 10))
        description.setWordWrap(True)
        layout.addWidget(description)

        # View toggle buttons
        view_toggle_layout = QHBoxLayout()

        self.card_view_button = QPushButton("Card View")
        self.card_view_button.clicked.connect(lambda: self.switch_view(0))
        self.card_view_button.setCheckable(True)
        self.card_view_button.setChecked(True)
        view_toggle_layout.addWidget(self.card_view_button)

        self.grid_view_button = QPushButton("Grid View")
        self.grid_view_button.clicked.connect(lambda: self.switch_view(1))
        self.grid_view_button.setCheckable(True)
        view_toggle_layout.addWidget(self.grid_view_button)

        view_toggle_layout.addStretch()
        layout.addLayout(view_toggle_layout)

        # Stacked widget for view switching
        self.view_stack = QStackedWidget()

        # Card View (Index 0 - Default)
        card_view_widget = self.create_card_view()
        self.view_stack.addWidget(card_view_widget)

        # Grid View (Index 1)
        grid_view_widget = self.create_grid_view()
        self.view_stack.addWidget(grid_view_widget)

        layout.addWidget(self.view_stack)

        self.setLayout(layout)

    def create_card_view(self) -> QWidget:
        """Create card view widget"""
        card_widget = QWidget()
        layout = QVBoxLayout()

        # Scroll area for deployment cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Container for deployment cards
        self.deployments_container = QWidget()
        self.deployments_layout = QVBoxLayout()
        self.deployments_layout.setSpacing(10)
        self.deployments_container.setLayout(self.deployments_layout)

        scroll_area.setWidget(self.deployments_container)
        layout.addWidget(scroll_area)

        # Add New Deployment button
        add_button_layout = QHBoxLayout()
        add_button_layout.addStretch()

        self.add_deployment_button = QPushButton("+ New Deployment")
        self.add_deployment_button.setToolTip("Create a new deployment configuration")
        self.add_deployment_button.clicked.connect(self.on_add_deployment)
        add_button_layout.addWidget(self.add_deployment_button)

        add_button_layout.addStretch()
        layout.addLayout(add_button_layout)

        card_widget.setLayout(layout)
        return card_widget

    def create_grid_view(self) -> QWidget:
        """Create grid view widget"""
        grid_widget = QWidget()
        layout = QVBoxLayout()

        # Toolbar
        toolbar = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search deployments...")
        self.search_input.textChanged.connect(self.filter_deployments)
        toolbar.addWidget(self.search_input)

        toolbar.addStretch()

        self.export_csv_button = QPushButton("Export to CSV")
        self.export_csv_button.clicked.connect(self.export_deployments_to_csv)
        toolbar.addWidget(self.export_csv_button)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.populate_grid)
        toolbar.addWidget(self.refresh_button)

        layout.addLayout(toolbar)

        # Table
        self.deployments_table = QTableWidget()
        self.deployments_table.setColumnCount(8)
        self.deployments_table.setHorizontalHeaderLabels([
            "Client",
            "Industry",
            "Deployed URL",
            "Deployment Mode",
            "Friendly Name",
            "Date-Time Deployed",
            "Bucket",
            "Directory"
        ])

        # Configure columns
        header = self.deployments_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # Client
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Industry
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)           # URL
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # Mode
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)           # Friendly Name
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Date
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)  # Bucket
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)  # Directory

        # Enable sorting
        self.deployments_table.setSortingEnabled(True)

        # Selection
        self.deployments_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.deployments_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        layout.addWidget(self.deployments_table)

        grid_widget.setLayout(layout)
        return grid_widget

    def switch_view(self, index: int):
        """Switch between card and grid view"""
        self.view_stack.setCurrentIndex(index)

        # Update button states
        self.card_view_button.setChecked(index == 0)
        self.grid_view_button.setChecked(index == 1)

        # Refresh grid if switching to it
        if index == 1:
            self.populate_grid()

    def set_config_path(self, config_file_path: str):
        """Load deployments from SQLite for given config file"""
        self.current_config_path = config_file_path
        self.refresh_deployments()

    def refresh_deployments(self):
        """Refresh deployment cards from SQLite database"""
        # Clear existing cards
        for card in self.deployment_cards:
            card.setParent(None)
            card.deleteLater()
        self.deployment_cards.clear()

        if not self.current_config_path:
            # Show empty state - no config loaded
            empty_label = QLabel(
                "<i>No configuration file loaded.</i>"
            )
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #666; padding: 40px;")
            self.deployments_layout.addWidget(empty_label)
            return

        # Load deployments from SQLite
        try:
            deployments = self.deployment_store.load_deployments(self.current_config_path)

            if not deployments:
                # Show empty state - no deployments yet
                empty_label = QLabel(
                    "<i>No deployments found. Create a deployment from the Cloud Deploy tab.</i>"
                )
                empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                empty_label.setStyleSheet("color: #666; padding: 40px;")
                self.deployments_layout.addWidget(empty_label)
                return

            # Create cards for each deployment
            for deployment in deployments:
                card = DeploymentCard(deployment)

                # Connect signals
                card.redeploy_requested.connect(self.on_redeploy)
                card.edit_requested.connect(self.on_edit_deployment)
                card.delete_requested.connect(self.on_delete_deployment)
                card.friendly_name_changed.connect(self.on_friendly_name_changed)

                self.deployment_cards.append(card)
                self.deployments_layout.addWidget(card)

            # Add stretch at bottom
            self.deployments_layout.addStretch()

        except Exception as e:
            logger.error(f"Error loading deployments: {e}")
            error_label = QLabel(f"<i>Error loading deployments: {str(e)}</i>")
            error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            error_label.setStyleSheet("color: #cc0000; padding: 40px;")
            self.deployments_layout.addWidget(error_label)

    def on_add_deployment(self):
        """Handle add deployment button click"""
        QMessageBox.information(
            self,
            "Coming Soon",
            "New deployment creation will be available in Phase 3.\n\n"
            "For now, deployments are created automatically when you deploy "
            "to a bucket/directory from the Cloud Deploy tab."
        )

    def on_redeploy(self, deployment_id: str):
        """Handle re-deploy request"""
        QMessageBox.information(
            self,
            "Coming Soon",
            f"Re-deployment functionality will be available in Phase 4.\n\n"
            f"Deployment: {deployment_id}"
        )

    def on_edit_deployment(self, deployment_id: str):
        """Handle edit deployment request"""
        QMessageBox.information(
            self,
            "Coming Soon",
            f"Meta tags editing will be available in Phase 5.\n\n"
            f"Deployment: {deployment_id}"
        )

    def on_delete_deployment(self, deployment_id: str):
        """Handle delete deployment request"""
        reply = QMessageBox.question(
            self,
            "Delete Deployment",
            f"Are you sure you want to delete this deployment?\n\n"
            f"Deployment: {deployment_id}\n\n"
            f"Note: This will NOT delete files from S3 or CloudFront.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if not self.current_config_path:
                return

            try:
                # Delete from SQLite
                success = self.deployment_store.delete_deployment(
                    self.current_config_path,
                    deployment_id
                )

                if success:
                    self.refresh_deployments()
                    QMessageBox.information(
                        self,
                        "Deployment Deleted",
                        f"Deployment removed: {deployment_id}"
                    )
                else:
                    QMessageBox.warning(
                        self,
                        "Delete Failed",
                        f"Could not delete deployment: {deployment_id}"
                    )

            except Exception as e:
                logger.error(f"Error deleting deployment: {e}")
                QMessageBox.critical(
                    self,
                    "Delete Error",
                    f"Error: {str(e)}"
                )

    def on_friendly_name_changed(self, deployment_id: str, new_name: str):
        """Handle friendly name change"""
        if not self.current_config_path:
            return

        try:
            # Update in SQLite
            success = self.deployment_store.update_friendly_name(
                self.current_config_path,
                deployment_id,
                new_name
            )

            if success:
                logger.info(f"Friendly name updated: {deployment_id} -> {new_name}")
            else:
                QMessageBox.warning(
                    self,
                    "Update Failed",
                    f"Could not update friendly name for: {deployment_id}"
                )

        except Exception as e:
            logger.error(f"Error updating friendly name: {e}")
            QMessageBox.critical(
                self,
                "Update Error",
                f"Error: {str(e)}"
            )

    def populate_grid(self):
        """Populate grid with deployments from current config"""
        if not self.current_config or not self.current_config.deployments:
            self.deployments_table.setRowCount(0)
            return

        # Disable sorting while populating
        self.deployments_table.setSortingEnabled(False)
        self.deployments_table.setRowCount(len(self.current_config.deployments))

        for row, deployment in enumerate(self.current_config.deployments):
            # Client (Business Name)
            business_name = self.current_config.business.business_name or "N/A"
            self.deployments_table.setItem(row, 0, QTableWidgetItem(business_name))

            # Industry (snapshotted at deployment time)
            industry = deployment.industry or "N/A"
            self.deployments_table.setItem(row, 1, QTableWidgetItem(industry))

            # Deployed URL
            url = deployment.deployment_url or deployment.get_website_url() or "N/A"
            url_item = QTableWidgetItem(url)
            url_item.setForeground(QColor("#0066cc"))  # Blue for links
            self.deployments_table.setItem(row, 2, url_item)

            # Deployment Mode
            mode = deployment.mode.upper() if deployment.mode else "N/A"
            mode_item = QTableWidgetItem(mode)
            if mode == "CLOUDFRONT":
                mode_item.setBackground(QColor("#e6f7ff"))  # Light blue background
            self.deployments_table.setItem(row, 3, mode_item)

            # Friendly Name
            friendly_name = deployment.friendly_name or deployment.deployment_id
            self.deployments_table.setItem(row, 4, QTableWidgetItem(friendly_name))

            # Date-Time Deployed (formatted)
            if deployment.last_deployed:
                # Parse ISO format: "2025-12-20T16:30:45Z"
                dt = datetime.fromisoformat(deployment.last_deployed.replace("Z", "+00:00"))
                formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
            else:
                formatted_date = "N/A"
            self.deployments_table.setItem(row, 5, QTableWidgetItem(formatted_date))

            # Bucket
            bucket = deployment.bucket or "N/A"
            self.deployments_table.setItem(row, 6, QTableWidgetItem(bucket))

            # Directory
            directory = deployment.directory or "(root)"
            self.deployments_table.setItem(row, 7, QTableWidgetItem(directory))

        # Re-enable sorting
        self.deployments_table.setSortingEnabled(True)

    def export_deployments_to_csv(self):
        """Export all deployments to CSV file"""
        if not self.current_config or not self.current_config.deployments:
            QMessageBox.information(
                self,
                "Export Deployments",
                "No deployments to export"
            )
            return

        # Generate default filename with business name and timestamp
        business_name = self.current_config.business.business_name or "client"
        safe_name = business_name.replace(" ", "_").lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"{safe_name}_deployments_{timestamp}.csv"

        # Let user choose file location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Deployment History",
            default_filename,
            "CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        try:
            with open(file_path, "w", newline="", encoding="utf-8") as file:
                fieldnames = [
                    "Client",
                    "Industry",
                    "Deployed URL",
                    "Deployment Mode",
                    "Friendly Deployment Name",
                    "Date-Time Deployed",
                    "Bucket",
                    "Directory",
                    "CloudFront Distribution ID",
                    "CloudFront Domain",
                    "Region",
                    "Deployment ID",
                    "Google Verification Code"
                ]
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()

                for deployment in self.current_config.deployments:
                    # Extract Google verification code from meta_tags
                    google_code = deployment.meta_tags.get("google-site-verification", "")

                    # Format date
                    if deployment.last_deployed:
                        dt = datetime.fromisoformat(deployment.last_deployed.replace("Z", "+00:00"))
                        formatted_date = dt.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        formatted_date = ""

                    writer.writerow({
                        "Client": self.current_config.business.business_name or "",
                        "Industry": deployment.industry or "",
                        "Deployed URL": deployment.deployment_url or deployment.get_website_url() or "",
                        "Deployment Mode": deployment.mode.upper() if deployment.mode else "",
                        "Friendly Deployment Name": deployment.friendly_name or "",
                        "Date-Time Deployed": formatted_date,
                        "Bucket": deployment.bucket or "",
                        "Directory": deployment.directory or "",
                        "CloudFront Distribution ID": deployment.cloudfront_distribution_id or "",
                        "CloudFront Domain": deployment.cloudfront_domain or "",
                        "Region": deployment.region or "",
                        "Deployment ID": deployment.deployment_id or "",
                        "Google Verification Code": google_code
                    })

            QMessageBox.information(
                self,
                "Export Success",
                f"Successfully exported {len(self.current_config.deployments)} deployments to:\n{file_path}"
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Error",
                f"Error exporting CSV:\n{str(e)}"
            )

    def filter_deployments(self, search_text: str):
        """Filter table rows based on search text"""
        search_text = search_text.lower()

        for row in range(self.deployments_table.rowCount()):
            should_show = False

            # Search in all columns
            for col in range(self.deployments_table.columnCount()):
                item = self.deployments_table.item(row, col)
                if item and search_text in item.text().lower():
                    should_show = True
                    break

            self.deployments_table.setRowHidden(row, not should_show)

    def get_config_data(self) -> dict:
        """Get deployment data for saving (compatibility with other tabs)"""
        return {}  # Deployments are managed in ClientConfig.deployments

    def set_config_data(self, data: dict):
        """Set deployment data from loaded config (compatibility with other tabs)"""
        pass  # Handled by set_config()

    def validate_data(self) -> tuple:
        """Validate deployment data (compatibility with other tabs)"""
        return True, []  # No validation needed for read-only display

    def get_required_fields(self) -> list:
        """Get required fields (compatibility with other tabs)"""
        return []  # No required fields
