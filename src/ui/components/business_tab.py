"""
Filename: business_tab_fixed.py
Path: E:/projects/cloud-stack-generator/src/ui/components/business_tab_fixed.py
Description: Business information configuration tab with fixed layout issues
Simple, working layout that displays correctly in all screen modes

Version: 2.1.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

from PyQt6.QtWidgets import (
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QPushButton,
    QGroupBox,
    QSpacerItem,
    QSizePolicy,
    QScrollArea,
    QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QDesktopServices
from typing import Dict, Any, List
from .base_tab import BaseTab, ValidationResult
import re


class BusinessTab(BaseTab):
    """Tab for business information configuration with fixed layout"""

    def __init__(self, parent=None):
        # Industry suggestions for autocomplete
        self.industry_suggestions = [
            "Professional Services",
            "Healthcare",
            "Legal Services",
            "Financial Services",
            "Real Estate",
            "Construction",
            "Manufacturing",
            "Technology",
            "Retail",
            "Restaurant & Food Service",
            "Automotive",
            "Education",
            "Non-Profit",
            "Home Services",
            "Beauty & Wellness",
            "Fitness",
            "Entertainment",
            "Insurance",
            "Consulting",
            "Marketing & Advertising",
        ]

        # Initialize widget references (will be set in setup_ui)
        self.business_name_input: QLineEdit
        self.domain_input: QLineEdit
        self.industry_input: QComboBox
        self.description_input: QTextEdit
        self.char_counter_label: QLabel

        super().__init__(parent)

    def setup_ui(self):
        """Setup business information UI with working layout"""
        # Create main scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget
        content_layout = QVBoxLayout()
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(10, 10, 10, 10)

        # Business Information Section
        business_group = self._create_business_info_section()
        content_layout.addWidget(business_group)

        # Business Description Section
        description_group = self._create_description_section()
        content_layout.addWidget(description_group)

        # Help Section
        help_group = self._create_help_section()
        content_layout.addWidget(help_group)

        # Add validation button
        validation_button = QPushButton("Validate Business Information")
        validation_button.clicked.connect(self.validate_and_show_results)
        validation_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        validation_button.setMaximumWidth(300)
        content_layout.addWidget(validation_button)

        # Add stretch to push content to top
        content_layout.addStretch()

        # Create container widget
        container = QFrame()
        container.setLayout(content_layout)
        
        # Set up scroll area
        scroll_area.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
        
        self.setLayout(main_layout)

    def _create_business_info_section(self) -> QGroupBox:
        """Create the main business information section"""
        group = QGroupBox("Business Information")
        group.setMaximumHeight(150)
        layout = QGridLayout()
        layout.setSpacing(10)

        # Business Name
        layout.addWidget(QLabel("* Business Name:"), 0, 0)
        self.business_name_input = QLineEdit()
        self.business_name_input.setFont(QFont("Arial", 10))
        self.business_name_input.setMinimumHeight(30)
        self.business_name_input.setPlaceholderText("Enter your business name")
        layout.addWidget(self.business_name_input, 0, 1)
        layout.addWidget(self._create_error_label("business_name"), 0, 2)

        # Website Domain
        layout.addWidget(QLabel("* Website:"), 1, 0)
        self.domain_input = QLineEdit()
        self.domain_input.setFont(QFont("Arial", 10))
        self.domain_input.setMinimumHeight(30)
        self.domain_input.setPlaceholderText("https://www.yourbusiness.com")
        layout.addWidget(self.domain_input, 1, 1)
        layout.addWidget(self._create_error_label("domain"), 1, 2)

        # Industry/Category
        layout.addWidget(QLabel("* Industry:"), 2, 0)
        self.industry_input = QComboBox()
        self.industry_input.setFont(QFont("Arial", 10))
        self.industry_input.setMinimumHeight(30)
        self.industry_input.setEditable(True)
        self.industry_input.addItems([""] + self.industry_suggestions)
        self.industry_input.setCurrentText("")
        # Safe access to lineEdit
        line_edit = self.industry_input.lineEdit()
        if line_edit:
            line_edit.setPlaceholderText("Select or type your industry")
        layout.addWidget(self.industry_input, 2, 1)
        layout.addWidget(self._create_error_label("industry"), 2, 2)

        # Set column stretch to make inputs expand
        layout.setColumnStretch(1, 1)

        group.setLayout(layout)
        return group

    def _create_description_section(self) -> QGroupBox:
        """Create business description section"""
        group = QGroupBox("Business Description (Optional)")
        group.setMaximumHeight(180)
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Description label with help text
        desc_label = QLabel("Provide a brief description of your business:")
        desc_label.setFont(QFont("Arial", 10))
        layout.addWidget(desc_label)

        # Description text area
        self.description_input = QTextEdit()
        self.description_input.setFont(QFont("Arial", 10))
        self.description_input.setPlaceholderText(
            "Describe what your business does, your specialties, and what makes you unique. "
            "This will help generate better content for your website."
        )
        self.description_input.setMaximumHeight(100)
        self.description_input.setMinimumHeight(100)
        layout.addWidget(self.description_input)

        # Character counter label
        self.char_counter_label = QLabel("0 characters")
        self.char_counter_label.setFont(QFont("Arial", 9))
        self.char_counter_label.setStyleSheet("color: #666;")
        layout.addWidget(self.char_counter_label)

        group.setLayout(layout)
        return group

    def _create_help_section(self) -> QGroupBox:
        """Create help and tips section"""
        group = QGroupBox("Tips & Guidelines")
        group.setMaximumHeight(120)
        layout = QVBoxLayout()
        layout.setSpacing(5)

        tips = [
            "• Use your exact business name as it appears on your website and Google Business Profile",
            "• Include 'https://' in your website URL for proper linking",
            "• Choose an industry that best matches your primary business focus",
            "• A good business description helps generate relevant website content",
        ]

        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setFont(QFont("Arial", 9))
            tip_label.setStyleSheet("color: #555; margin: 2px 0;")
            tip_label.setWordWrap(True)
            layout.addWidget(tip_label)

        group.setLayout(layout)
        return group

    def connect_signals(self):
        """Connect input widgets to config_changed signal"""
        # Connect all widget signals after they're created
        self.business_name_input.textChanged.connect(self._emit_config_changed)
        self.domain_input.textChanged.connect(self._emit_config_changed)
        self.industry_input.currentTextChanged.connect(self._emit_config_changed)
        self.description_input.textChanged.connect(self._emit_config_changed)
        self.description_input.textChanged.connect(self._update_char_counter)

        # Auto-format domain URL
        self.domain_input.editingFinished.connect(self._format_domain_url)

    def get_required_fields(self) -> List[str]:
        """Get list of required field names"""
        return ["business_name", "domain", "industry"]

    def validate_data(self) -> ValidationResult:
        """Validate business data with specific business rules"""
        result = super().validate_data()

        # Get current data
        data = self.get_config_data()

        # Validate business name
        business_name = data.get("business_name", "").strip()
        if business_name and len(business_name) < 2:
            result.add_error(
                "Business name must be at least 2 characters", "business_name"
            )

        # Validate domain URL
        domain = data.get("domain", "").strip()
        if domain:
            if not self._is_valid_url(domain):
                result.add_error(
                    "Please enter a valid website URL (e.g., https://www.example.com)",
                    "domain",
                )

        # Validate industry
        industry = data.get("industry", "").strip()
        if industry and len(industry) < 3:
            result.add_error("Industry must be at least 3 characters", "industry")

        # Validate description length if provided
        description = data.get("description", "").strip()
        if description and len(description) > 500:
            result.add_warning(
                "Business description is quite long. Consider shortening for better readability."
            )

        return result

    def validate_and_show_results(self):
        """Validate data and show results to user"""
        result = self.validate_data()

        if result.is_valid:
            msg = "✅ Business information is valid!\n\n"
            data = self.get_config_data()
            
            msg += f"• Business Name: {data.get('business_name', 'Not set')}\n"
            msg += f"• Website: {data.get('domain', 'Not set')}\n"
            msg += f"• Industry: {data.get('industry', 'Not set')}\n"
            
            description = data.get('description', '')
            if description:
                msg += f"• Description: {len(description)} characters\n"

            if result.warnings:
                msg += f"• Warnings: {len(result.warnings)}\n"
                detailed_msg = msg + "\n" + "\n".join([f"⚠️ {w}" for w in result.warnings])
                msgbox = QMessageBox(self)
                msgbox.setWindowTitle("Business Validation Results")
                msgbox.setText(msg)
                msgbox.setDetailedText(detailed_msg)
                msgbox.setIcon(QMessageBox.Icon.Information)
                msgbox.exec()
            else:
                msgbox = QMessageBox(self)
                msgbox.setWindowTitle("Business Validation Success")
                msgbox.setText(msg)
                msgbox.setIcon(QMessageBox.Icon.Information)
                msgbox.exec()
        else:
            msg = f"❌ Business validation failed!\n\n"
            msg += f"• Errors: {len(result.errors)}\n"

            if result.warnings:
                msg += f"• Warnings: {len(result.warnings)}\n"

            # Show detailed errors and warnings
            details = []
            details.extend([f"❌ {e}" for e in result.errors])
            details.extend([f"⚠️ {w}" for w in result.warnings])

            detailed_msg = msg + "\n" + "\n".join(details)
            msgbox = QMessageBox(self)
            msgbox.setWindowTitle("Business Validation Results")
            msgbox.setText(msg)
            msgbox.setDetailedText(detailed_msg)
            msgbox.setIcon(QMessageBox.Icon.Critical)
            msgbox.exec()

    def get_config_data(self) -> Dict[str, Any]:
        """Get business configuration data"""
        return {
            "business_name": self.business_name_input.text().strip(),
            "domain": self.domain_input.text().strip(),
            "industry": self.industry_input.currentText().strip(),
            "description": self.description_input.toPlainText().strip(),
        }

    def set_config_data(self, data: Dict[str, Any]):
        """Set business configuration data"""
        self._start_loading()

        try:
            # Set basic fields
            self.business_name_input.setText(data.get("business_name", ""))
            self.domain_input.setText(data.get("domain", ""))

            # Set industry (handle both string and selection)
            industry = data.get("industry", "")
            if industry:
                # Try to find exact match first
                index = self.industry_input.findText(industry)
                if index >= 0:
                    self.industry_input.setCurrentIndex(index)
                else:
                    # Add custom industry and select it
                    self.industry_input.addItem(industry)
                    self.industry_input.setCurrentText(industry)
            else:
                self.industry_input.setCurrentIndex(0)  # Select empty item

            # Set description
            self.description_input.setPlainText(data.get("description", ""))

            # Update character counter
            self._update_char_counter()
        
        finally:
            self._finish_loading()

    def clear_data(self):
        """Clear all business data"""
        self._start_loading()

        try:
            self.business_name_input.clear()
            self.domain_input.clear()
            self.industry_input.setCurrentIndex(0)
            self.description_input.clear()
            self._update_char_counter()
        
        finally:
            self._finish_loading()

    def _format_domain_url(self):
        """Auto-format domain URL to include https:// if missing"""
        domain = self.domain_input.text().strip()
        if domain and not domain.startswith(("http://", "https://")):
            if not domain.startswith("www."):
                domain = "www." + domain
            domain = "https://" + domain
            self.domain_input.setText(domain)

    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid format"""
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )
        return url_pattern.match(url) is not None

    def _update_char_counter(self):
        """Update character counter for description"""
        char_count = len(self.description_input.toPlainText())
        self.char_counter_label.setText(f"{char_count} characters")

        # Change color based on length
        if char_count > 500:
            self.char_counter_label.setStyleSheet("color: #e74c3c;")  # Red for too long
        elif char_count > 400:
            self.char_counter_label.setStyleSheet(
                "color: #f39c12;"
            )  # Orange for getting long
        else:
            self.char_counter_label.setStyleSheet("color: #666;")  # Normal gray
    
    def get_tab_name(self) -> str:
        """Get tab name for title display"""
        return "Business Information"