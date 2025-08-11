"""
Filename: src/ui/components/business_tab.py
Path: E:/projects/cloud-stack-generator/src/ui/components/business_tab.py
Description: Business information configuration tab

Version: 1.0.1
Date: 2025-08-10
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
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont, QDesktopServices
from typing import Dict, Any, List
from .base_tab import BaseTab, ValidationResult
import re


class BusinessTab(BaseTab):
    """Tab for business information configuration"""

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
        """Setup business information UI"""
        main_layout = QVBoxLayout()

        # Business Information Section
        business_group = self._create_business_info_section()
        main_layout.addWidget(business_group)

        # Business Description Section
        description_group = self._create_description_section()
        main_layout.addWidget(description_group)

        # Help Section
        help_group = self._create_help_section()
        main_layout.addWidget(help_group)

        # Add stretch to push content to top
        main_layout.addStretch()

        self.setLayout(main_layout)

    def _create_business_info_section(self) -> QGroupBox:
        """Create the main business information section"""
        group = QGroupBox("Business Information")
        layout = QGridLayout()

        # Business Name
        layout.addWidget(QLabel("* Business Name:"), 0, 0)
        self.business_name_input = QLineEdit()
        self.business_name_input.setPlaceholderText("Enter your business name")
        layout.addWidget(self.business_name_input, 0, 1)
        layout.addWidget(self._create_error_label("business_name"), 0, 2)

        # Website Domain
        layout.addWidget(QLabel("* Website:"), 1, 0)
        self.domain_input = QLineEdit()
        self.domain_input.setPlaceholderText("https://www.yourbusiness.com")
        layout.addWidget(self.domain_input, 1, 1)
        layout.addWidget(self._create_error_label("domain"), 1, 2)

        # Industry/Category
        layout.addWidget(QLabel("* Industry:"), 2, 0)
        self.industry_input = QComboBox()
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
        layout = QVBoxLayout()

        # Description label with help text
        desc_label = QLabel("Provide a brief description of your business:")
        desc_label.setFont(QFont("Arial", 9))
        layout.addWidget(desc_label)

        # Description text area
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText(
            "Describe what your business does, your specialties, and what makes you unique. "
            "This will help generate better content for your website."
        )
        self.description_input.setMaximumHeight(100)
        layout.addWidget(self.description_input)

        # Character counter label
        self.char_counter_label = QLabel("0 characters")
        self.char_counter_label.setFont(QFont("Arial", 8))
        self.char_counter_label.setStyleSheet("color: #666;")
        layout.addWidget(self.char_counter_label)

        group.setLayout(layout)
        return group

    def _create_help_section(self) -> QGroupBox:
        """Create help and tips section"""
        group = QGroupBox("Tips & Guidelines")
        layout = QVBoxLayout()

        tips = [
            "• Use your exact business name as it appears on your website and Google Business Profile",
            "• Include 'https://' in your website URL for proper linking",
            "• Choose an industry that best matches your primary business focus",
            "• A good business description helps generate relevant website content",
        ]

        for tip in tips:
            tip_label = QLabel(tip)
            tip_label.setFont(QFont("Arial", 8))
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

        self._finish_loading()

    def clear_data(self):
        """Clear all business data"""
        self._start_loading()

        self.business_name_input.clear()
        self.domain_input.clear()
        self.industry_input.setCurrentIndex(0)
        self.description_input.clear()
        self._update_char_counter()

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
