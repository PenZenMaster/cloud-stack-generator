"""
Deployment History Tab - Multi-deployment management UI

Shows all deployments for the current client configuration with ability to
re-deploy, update meta tags, and delete deployments.

Phase 2 Implementation (v3.2.0)
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import List, Optional
from datetime import datetime

from src.core.config.models import DeploymentConfig, ClientConfig


class DeploymentCard(QFrame):
    """Card widget displaying a single deployment with actions"""

    # Signals
    redeploy_requested = pyqtSignal(str)  # deployment_id
    edit_requested = pyqtSignal(str)  # deployment_id
    delete_requested = pyqtSignal(str)  # deployment_id

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

        # Header: Deployment ID
        header_layout = QHBoxLayout()

        deployment_label = QLabel(f"<b>{self.deployment.deployment_id}</b>")
        deployment_label.setWordWrap(True)
        header_layout.addWidget(deployment_label)
        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Info line 1: Bucket and directory
        bucket_dir_label = QLabel(
            f"<b>Bucket:</b> {self.deployment.bucket} "
            f"<b>Directory:</b> {self.deployment.directory or '(root)'}"
        )
        layout.addWidget(bucket_dir_label)

        # Info line 2: Mode and region
        mode_text = "CloudFront + OAC" if self.deployment.mode == "cloudfront" else "S3 Only"
        mode_region_label = QLabel(
            f"<b>Mode:</b> {mode_text} | "
            f"<b>Region:</b> {self.deployment.region}"
        )
        layout.addWidget(mode_region_label)

        # Info line 3: CloudFront details (if Mode B)
        if self.deployment.mode == "cloudfront" and self.deployment.cloudfront_distribution_id:
            cf_label = QLabel(
                f"<b>Distribution:</b> {self.deployment.cloudfront_distribution_id}"
            )
            layout.addWidget(cf_label)

        # Info line 4: Last deployed
        if self.deployment.last_deployed:
            try:
                dt = datetime.fromisoformat(self.deployment.last_deployed.replace('Z', '+00:00'))
                last_deployed_str = dt.strftime("%Y-%m-%d %I:%M %p")
            except:
                last_deployed_str = self.deployment.last_deployed

            last_deployed_label = QLabel(f"<b>Last Deployed:</b> {last_deployed_str}")
            layout.addWidget(last_deployed_label)

        # Info line 5: Website URL
        website_url = self.deployment.get_website_url()
        if website_url:
            url_label = QLabel(f'<b>URL:</b> <a href="{website_url}">{website_url}</a>')
            url_label.setOpenExternalLinks(True)
            url_label.setWordWrap(True)
            layout.addWidget(url_label)

        # Info line 6: Meta tags count
        if self.deployment.meta_tags:
            meta_tags_label = QLabel(f"<b>Meta Tags:</b> {len(self.deployment.meta_tags)} configured")
            layout.addWidget(meta_tags_label)

        # Action buttons
        button_layout = QHBoxLayout()

        self.redeploy_button = QPushButton("Re-Deploy")
        self.redeploy_button.setToolTip("Deploy to this location again")
        self.redeploy_button.clicked.connect(lambda: self.redeploy_requested.emit(self.deployment.deployment_id))
        button_layout.addWidget(self.redeploy_button)

        self.edit_button = QPushButton("Update Meta Tags")
        self.edit_button.setToolTip("Edit meta tags for this deployment")
        self.edit_button.clicked.connect(lambda: self.edit_requested.emit(self.deployment.deployment_id))
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton("Delete")
        self.delete_button.setToolTip("Remove this deployment configuration")
        self.delete_button.clicked.connect(lambda: self.delete_requested.emit(self.deployment.deployment_id))
        button_layout.addWidget(self.delete_button)

        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)


class DeploymentHistoryTab(QWidget):
    """Tab showing deployment history and management"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_config: Optional[ClientConfig] = None
        self.deployment_cards: List[DeploymentCard] = []
        self.setup_ui()

    def setup_ui(self):
        """Setup deployment history UI"""
        layout = QVBoxLayout()

        # Header
        header = QLabel("<h2>Deployment History</h2>")
        layout.addWidget(header)

        # Description
        description = QLabel(
            "Manage multiple deployments for this client. Each deployment can have "
            "different meta tags, CloudFront settings, and destination directories."
        )
        description.setWordWrap(True)
        layout.addWidget(description)

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

        self.setLayout(layout)

    def set_config(self, config: ClientConfig):
        """Load deployments from config"""
        self.current_config = config
        self.refresh_deployments()

    def refresh_deployments(self):
        """Refresh deployment cards from current config"""
        # Clear existing cards
        for card in self.deployment_cards:
            card.setParent(None)
            card.deleteLater()
        self.deployment_cards.clear()

        if not self.current_config or not self.current_config.deployments:
            # Show empty state
            empty_label = QLabel(
                "<i>No deployments configured yet. Click '+ New Deployment' to create one.</i>"
            )
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_label.setStyleSheet("color: #666; padding: 40px;")
            self.deployments_layout.addWidget(empty_label)
            return

        # Create cards for each deployment
        for deployment in self.current_config.deployments:
            card = DeploymentCard(deployment)

            # Connect signals
            card.redeploy_requested.connect(self.on_redeploy)
            card.edit_requested.connect(self.on_edit_deployment)
            card.delete_requested.connect(self.on_delete_deployment)

            self.deployment_cards.append(card)
            self.deployments_layout.addWidget(card)

        # Add stretch at bottom
        self.deployments_layout.addStretch()

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
            f"Are you sure you want to delete this deployment configuration?\n\n"
            f"Deployment: {deployment_id}\n\n"
            f"Note: This will NOT delete files from S3 or CloudFront distribution. "
            f"It only removes the deployment from this configuration.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Find and remove deployment
            if self.current_config:
                self.current_config.deployments = [
                    d for d in self.current_config.deployments
                    if d.deployment_id != deployment_id
                ]
                self.refresh_deployments()

                QMessageBox.information(
                    self,
                    "Deployment Deleted",
                    f"Deployment configuration removed: {deployment_id}\n\n"
                    f"Remember to save your configuration."
                )

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
