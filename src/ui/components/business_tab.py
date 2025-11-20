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
    QScrollArea,
    QFrame,
    QMessageBox,
    QTableWidget,
    QHeaderView,
    QAbstractItemView,
    QTableWidgetItem,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict, Any, List, Tuple, Optional
from .base_tab import BaseTab, ValidationResult
from ..dialogs.ai_content_preview_dialog import AIContentPreviewDialog
from ...core.services.ai_content_service import AIContentService
from ...core.generators.content.business_content_generator import BusinessContentGenerator
import re


class WhyChooseUsItem:
    """Why Choose Us data model"""

    def __init__(self, title: str = "", description: str = ""):
        self.title = title
        self.description = description

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary"""
        return {
            "title": self.title,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, str]) -> "WhyChooseUsItem":
        """Create from dictionary"""
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
        )

    def is_valid(self) -> Tuple[bool, List[str]]:
        """Validate item data"""
        errors = []
        if not self.title.strip():
            errors.append("Title is required")
        if not self.description.strip():
            errors.append("Description is required")
        return len(errors) == 0, errors


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
        
        # Enhanced content widgets
        self.tagline_input: QLineEdit
        self.hero_subtitle_input: QLineEdit
        self.years_in_business_input: QLineEdit
        self.company_overview_input: QTextEdit
        self.mission_statement_input: QTextEdit
        self.service_guarantee_input: QTextEdit
        self.service_area_description_input: QTextEdit
        # Why Choose Us table components
        self.why_choose_us_table: QTableWidget
        self.why_choose_us_items: List[WhyChooseUsItem]
        self.why_choose_us_title_input: QLineEdit
        self.why_choose_us_description_input: QTextEdit
        self.company_stats_input: QTextEdit

        super().__init__(parent)

        # Initialize why choose us items
        self.why_choose_us_items = []

        # Initialize AI services
        self.ai_service = AIContentService()
        self.business_generator = BusinessContentGenerator(self.ai_service)

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
        
        # Enhanced Business Content Section
        enhanced_group = self._create_enhanced_content_section()
        content_layout.addWidget(enhanced_group)

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
        group.setMaximumHeight(220)
        layout = QVBoxLayout()
        layout.setSpacing(10)

        # Description label with help text and AI button
        header_layout = QHBoxLayout()
        desc_label = QLabel("Provide a brief description of your business:")
        desc_label.setFont(QFont("Arial", 10))
        header_layout.addWidget(desc_label)
        header_layout.addStretch()

        # Generate with AI button
        ai_desc_button = QPushButton("✨ Generate with AI")
        ai_desc_button.setMaximumWidth(150)
        ai_desc_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        ai_desc_button.clicked.connect(self._generate_business_description)
        header_layout.addWidget(ai_desc_button)
        layout.addLayout(header_layout)

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

    def _create_enhanced_content_section(self) -> QGroupBox:
        """Create enhanced business content section for professional templates"""
        group = QGroupBox("Enhanced Business Content (Optional)")
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # Company Tag Line - Hero H1
        tagline_label = QLabel("Company Tag Line - Hero H1:")
        tagline_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(tagline_label)
        
        self.tagline_input = QLineEdit()
        self.tagline_input.setFont(QFont("Arial", 10))
        self.tagline_input.setPlaceholderText("Forging Function with Metal Mastery")
        self.tagline_input.setMinimumHeight(30)
        layout.addWidget(self.tagline_input)
        
        # Hero Subtitle
        hero_subtitle_label = QLabel("Hero Subtitle:")
        hero_subtitle_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(hero_subtitle_label)
        
        self.hero_subtitle_input = QLineEdit()
        self.hero_subtitle_input.setFont(QFont("Arial", 10))
        self.hero_subtitle_input.setPlaceholderText("Professional metal fabrication services you can trust")
        self.hero_subtitle_input.setMinimumHeight(30)
        layout.addWidget(self.hero_subtitle_input)
        
        # Years in Business
        years_label = QLabel("Years in Business:")
        years_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(years_label)
        
        self.years_in_business_input = QLineEdit()
        self.years_in_business_input.setFont(QFont("Arial", 10))
        self.years_in_business_input.setPlaceholderText("25+ Years" or "Since 1995")
        self.years_in_business_input.setMinimumHeight(30)
        layout.addWidget(self.years_in_business_input)
        
        # Company Overview
        overview_header = QHBoxLayout()
        overview_label = QLabel("Company Overview (for About section):")
        overview_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        overview_header.addWidget(overview_label)
        overview_header.addStretch()

        ai_overview_button = QPushButton("✨ Generate with AI")
        ai_overview_button.setMaximumWidth(150)
        ai_overview_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        ai_overview_button.clicked.connect(self._generate_company_overview)
        overview_header.addWidget(ai_overview_button)
        layout.addLayout(overview_header)

        self.company_overview_input = QTextEdit()
        self.company_overview_input.setFont(QFont("Arial", 10))
        self.company_overview_input.setPlaceholderText(
            "Detailed description of your company, history, and what sets you apart..."
        )
        self.company_overview_input.setMaximumHeight(80)
        layout.addWidget(self.company_overview_input)
        
        # Mission Statement
        mission_header = QHBoxLayout()
        mission_label = QLabel("Mission Statement (optional):")
        mission_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        mission_header.addWidget(mission_label)
        mission_header.addStretch()

        ai_mission_button = QPushButton("✨ Generate with AI")
        ai_mission_button.setMaximumWidth(150)
        ai_mission_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        ai_mission_button.clicked.connect(self._generate_mission_statement)
        mission_header.addWidget(ai_mission_button)
        layout.addLayout(mission_header)

        self.mission_statement_input = QTextEdit()
        self.mission_statement_input.setFont(QFont("Arial", 10))
        self.mission_statement_input.setPlaceholderText(
            "Our mission is to provide exceptional service and quality results..."
        )
        self.mission_statement_input.setMaximumHeight(60)
        layout.addWidget(self.mission_statement_input)
        
        # Service Guarantee
        guarantee_header = QHBoxLayout()
        guarantee_label = QLabel("Service Guarantee (optional):")
        guarantee_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        guarantee_header.addWidget(guarantee_label)
        guarantee_header.addStretch()

        ai_guarantee_button = QPushButton("✨ Generate with AI")
        ai_guarantee_button.setMaximumWidth(150)
        ai_guarantee_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        ai_guarantee_button.clicked.connect(self._generate_service_guarantee)
        guarantee_header.addWidget(ai_guarantee_button)
        layout.addLayout(guarantee_header)

        self.service_guarantee_input = QTextEdit()
        self.service_guarantee_input.setFont(QFont("Arial", 10))
        self.service_guarantee_input.setPlaceholderText(
            "We guarantee quality workmanship and customer satisfaction..."
        )
        self.service_guarantee_input.setMaximumHeight(60)
        layout.addWidget(self.service_guarantee_input)
        
        # Service Area Description
        service_area_header = QHBoxLayout()
        service_area_label = QLabel("Service Area Description (optional):")
        service_area_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        service_area_header.addWidget(service_area_label)
        service_area_header.addStretch()

        ai_service_area_button = QPushButton("✨ Generate with AI")
        ai_service_area_button.setMaximumWidth(150)
        ai_service_area_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        ai_service_area_button.clicked.connect(self._generate_service_area_description)
        service_area_header.addWidget(ai_service_area_button)
        layout.addLayout(service_area_header)

        self.service_area_description_input = QTextEdit()
        self.service_area_description_input.setFont(QFont("Arial", 10))
        self.service_area_description_input.setPlaceholderText(
            "We proudly serve Chicago, suburbs, and surrounding areas within 50 miles..."
        )
        self.service_area_description_input.setMaximumHeight(60)
        layout.addWidget(self.service_area_description_input)
        
        # Why Choose Us (Table-based like FAQ)
        why_choose_label = QLabel("Why Choose Us (Title & Description pairs):")
        why_choose_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(why_choose_label)
        
        # Create Why Choose Us table
        self.why_choose_us_table = QTableWidget()
        self.why_choose_us_table.setColumnCount(3)  # Title, Description, Actions
        self.why_choose_us_table.setHorizontalHeaderLabels(["Title", "Description", "Actions"])
        self.why_choose_us_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.why_choose_us_table.setAlternatingRowColors(True)
        self.why_choose_us_table.setMaximumHeight(200)
        
        # Set column widths
        header = self.why_choose_us_table.horizontalHeader()
        if header is not None:
            header.setStretchLastSection(False)
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # Title
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Description
            header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)  # Actions
        
        self.why_choose_us_table.setColumnWidth(0, 150)  # Title
        self.why_choose_us_table.setColumnWidth(2, 80)   # Actions
        
        layout.addWidget(self.why_choose_us_table)
        
        # Input section for new Why Choose Us items
        entry_layout = QHBoxLayout()
        
        self.why_choose_us_title_input = QLineEdit()
        self.why_choose_us_title_input.setPlaceholderText("Enter title (e.g., Expert Craftsmanship)")
        entry_layout.addWidget(QLabel("Title:"))
        entry_layout.addWidget(self.why_choose_us_title_input)
        
        self.why_choose_us_description_input = QTextEdit()
        self.why_choose_us_description_input.setPlaceholderText("Enter description...")
        self.why_choose_us_description_input.setMaximumHeight(60)
        entry_layout.addWidget(QLabel("Description:"))
        entry_layout.addWidget(self.why_choose_us_description_input)
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self._add_why_choose_us_item)
        entry_layout.addWidget(add_button)
        
        layout.addLayout(entry_layout)
        
        # Company Statistics (JSON format helper)
        stats_label = QLabel("Company Statistics (format: projects: 500+, years: 15+):")
        stats_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(stats_label)
        
        self.company_stats_input = QTextEdit()
        self.company_stats_input.setFont(QFont("Arial", 10))
        self.company_stats_input.setPlaceholderText(
            "projects: 500+\nyears: 15+\nlocations: 3\ncertifications: 5"
        )
        self.company_stats_input.setMaximumHeight(60)
        layout.addWidget(self.company_stats_input)
        
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
        
        # Connect enhanced content widgets
        self.tagline_input.textChanged.connect(self._emit_config_changed)
        self.hero_subtitle_input.textChanged.connect(self._emit_config_changed)
        self.years_in_business_input.textChanged.connect(self._emit_config_changed)
        self.company_overview_input.textChanged.connect(self._emit_config_changed)
        self.mission_statement_input.textChanged.connect(self._emit_config_changed)
        self.service_guarantee_input.textChanged.connect(self._emit_config_changed)
        self.service_area_description_input.textChanged.connect(self._emit_config_changed)
        # Why Choose Us input connections
        self.why_choose_us_title_input.textChanged.connect(self._emit_config_changed)
        self.why_choose_us_description_input.textChanged.connect(self._emit_config_changed)
        self.company_stats_input.textChanged.connect(self._emit_config_changed)

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
            msg = "❌ Business validation failed!\n\n"
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
        # Get why_choose_us from table items
        why_choose_us = [item.to_dict() for item in self.why_choose_us_items]
        
        # Parse company_stats from text area (key: value format)
        company_stats = {}
        stats_text = self.company_stats_input.toPlainText().strip()
        if stats_text:
            for line in stats_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    company_stats[key.strip()] = value.strip()
        
        return {
            "business_name": self.business_name_input.text().strip(),
            "domain": self.domain_input.text().strip(),
            "industry": self.industry_input.currentText().strip(),
            "description": self.description_input.toPlainText().strip(),
            "tagline": self.tagline_input.text().strip(),
            "hero_subtitle": self.hero_subtitle_input.text().strip(),
            "years_in_business": self.years_in_business_input.text().strip(),
            "company_overview": self.company_overview_input.toPlainText().strip(),
            "mission_statement": self.mission_statement_input.toPlainText().strip(),
            "service_guarantee": self.service_guarantee_input.toPlainText().strip(),
            "service_area_description": self.service_area_description_input.toPlainText().strip(),
            "why_choose_us": why_choose_us,
            "company_stats": company_stats,
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
            
            # Set enhanced content fields
            self.tagline_input.setText(data.get("tagline", ""))
            self.hero_subtitle_input.setText(data.get("hero_subtitle", ""))
            self.years_in_business_input.setText(data.get("years_in_business", ""))
            self.company_overview_input.setPlainText(data.get("company_overview", ""))
            self.mission_statement_input.setPlainText(data.get("mission_statement", ""))
            self.service_guarantee_input.setPlainText(data.get("service_guarantee", ""))
            self.service_area_description_input.setPlainText(data.get("service_area_description", ""))
            
            # Set why_choose_us (load into table)
            why_choose_us = data.get("why_choose_us", [])
            self.why_choose_us_items = []
            if isinstance(why_choose_us, list):
                for item in why_choose_us:
                    if isinstance(item, dict):
                        # New format: dict with title and description
                        self.why_choose_us_items.append(WhyChooseUsItem.from_dict(item))
                    else:
                        # Old format: convert string to title-only item
                        self.why_choose_us_items.append(WhyChooseUsItem(
                            title=str(item),
                            description=f"Our commitment to excellence in {data.get('industry', 'service').lower()} ensures outstanding results for every project."
                        ))
            self._refresh_why_choose_us_table()
            
            # Set company_stats (convert dict to text)
            company_stats = data.get("company_stats", {})
            if isinstance(company_stats, dict):
                stats_text = '\n'.join([f"{k}: {v}" for k, v in company_stats.items()])
                self.company_stats_input.setPlainText(stats_text)
            else:
                self.company_stats_input.setPlainText(str(company_stats))

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
            
            # Clear enhanced content fields
            self.tagline_input.clear()
            self.hero_subtitle_input.clear()
            self.years_in_business_input.clear()
            self.company_overview_input.clear()
            self.mission_statement_input.clear()
            self.service_guarantee_input.clear()
            self.service_area_description_input.clear()
            # Clear why choose us components
            self.why_choose_us_title_input.clear()
            self.why_choose_us_description_input.clear()
            self.why_choose_us_items = []
            self._refresh_why_choose_us_table()
            self.company_stats_input.clear()
            
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
    
    def _add_why_choose_us_item(self):
        """Add new Why Choose Us item to the table"""
        title = self.why_choose_us_title_input.text().strip()
        description = self.why_choose_us_description_input.toPlainText().strip()
        
        if not title or not description:
            QMessageBox.warning(
                self,
                "Missing Information", 
                "Please enter both title and description."
            )
            return
        
        # Create new item
        item = WhyChooseUsItem(title, description)
        self.why_choose_us_items.append(item)
        
        # Clear inputs
        self.why_choose_us_title_input.clear()
        self.why_choose_us_description_input.clear()
        
        # Refresh table
        self._refresh_why_choose_us_table()
        self._emit_config_changed()
    
    def _remove_why_choose_us_item(self, index: int):
        """Remove Why Choose Us item"""
        if 0 <= index < len(self.why_choose_us_items):
            self.why_choose_us_items.pop(index)
            self._refresh_why_choose_us_table()
            self._emit_config_changed()
    
    def _refresh_why_choose_us_table(self):
        """Refresh the Why Choose Us table"""
        self.why_choose_us_table.setRowCount(len(self.why_choose_us_items))
        
        for row, item in enumerate(self.why_choose_us_items):
            # Title
            title_item = QTableWidgetItem(item.title)
            self.why_choose_us_table.setItem(row, 0, title_item)
            
            # Description
            desc_item = QTableWidgetItem(item.description)
            self.why_choose_us_table.setItem(row, 1, desc_item)
            
            # Remove button
            remove_button = QPushButton("Remove")
            remove_button.clicked.connect(lambda checked, r=row: self._remove_why_choose_us_item(r))
            self.why_choose_us_table.setCellWidget(row, 2, remove_button)

    def get_tab_name(self) -> str:
        """Get tab name for title display"""
        return "Business Information"

    # AI Content Generation Methods

    def _generate_business_description(self):
        """Generate business description using AI"""
        if not self.ai_service.is_available():
            QMessageBox.warning(
                self,
                "AI Not Available",
                "AI content generation is not available. Please check your OpenAI API key configuration."
            )
            return

        business_name = self.business_name_input.text().strip()
        industry = self.industry_input.currentText().strip()

        if not business_name or not industry:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter Business Name and Industry before generating AI content."
            )
            return

        # Show progress message
        QMessageBox.information(
            self,
            "Generating Content",
            "Generating business description with AI... This may take a few seconds."
        )

        # Generate content
        existing_desc = self.description_input.toPlainText().strip()
        content = self.business_generator.generate_business_description(
            business_name=business_name,
            industry=industry,
            existing_description=existing_desc
        )

        if not content:
            QMessageBox.critical(
                self,
                "Generation Failed",
                "Failed to generate business description. Please try again."
            )
            return

        # Show preview dialog
        dialog = AIContentPreviewDialog(
            title="AI Generated Business Description",
            field_name="Business Description",
            content=content,
            regenerate_callback=lambda: self.business_generator.generate_business_description(
                business_name=business_name,
                industry=industry,
                existing_description=existing_desc
            ),
            parent=self
        )

        dialog.content_accepted.connect(lambda c: self.description_input.setPlainText(c))
        dialog.exec()

    def _generate_company_overview(self):
        """Generate company overview using AI"""
        if not self.ai_service.is_available():
            QMessageBox.warning(
                self,
                "AI Not Available",
                "AI content generation is not available. Please check your OpenAI API key configuration."
            )
            return

        business_name = self.business_name_input.text().strip()
        industry = self.industry_input.currentText().strip()

        if not business_name or not industry:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter Business Name and Industry before generating AI content."
            )
            return

        # Generate content
        business_desc = self.description_input.toPlainText().strip()
        years = self.years_in_business_input.text().strip()

        content = self.business_generator.generate_company_overview(
            business_name=business_name,
            industry=industry,
            business_description=business_desc,
            years_in_business=years
        )

        if not content:
            QMessageBox.critical(
                self,
                "Generation Failed",
                "Failed to generate company overview. Please try again."
            )
            return

        # Show preview dialog
        dialog = AIContentPreviewDialog(
            title="AI Generated Company Overview",
            field_name="Company Overview",
            content=content,
            regenerate_callback=lambda: self.business_generator.generate_company_overview(
                business_name=business_name,
                industry=industry,
                business_description=business_desc,
                years_in_business=years
            ),
            parent=self
        )

        dialog.content_accepted.connect(lambda c: self.company_overview_input.setPlainText(c))
        dialog.exec()

    def _generate_mission_statement(self):
        """Generate mission statement using AI"""
        if not self.ai_service.is_available():
            QMessageBox.warning(
                self,
                "AI Not Available",
                "AI content generation is not available. Please check your OpenAI API key configuration."
            )
            return

        business_name = self.business_name_input.text().strip()
        industry = self.industry_input.currentText().strip()

        if not business_name or not industry:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter Business Name and Industry before generating AI content."
            )
            return

        # Generate content
        business_desc = self.description_input.toPlainText().strip()

        content = self.business_generator.generate_mission_statement(
            business_name=business_name,
            industry=industry,
            business_description=business_desc
        )

        if not content:
            QMessageBox.critical(
                self,
                "Generation Failed",
                "Failed to generate mission statement. Please try again."
            )
            return

        # Show preview dialog
        dialog = AIContentPreviewDialog(
            title="AI Generated Mission Statement",
            field_name="Mission Statement",
            content=content,
            regenerate_callback=lambda: self.business_generator.generate_mission_statement(
                business_name=business_name,
                industry=industry,
                business_description=business_desc
            ),
            parent=self
        )

        dialog.content_accepted.connect(lambda c: self.mission_statement_input.setPlainText(c))
        dialog.exec()

    def _generate_service_guarantee(self):
        """Generate service guarantee using AI"""
        if not self.ai_service.is_available():
            QMessageBox.warning(
                self,
                "AI Not Available",
                "AI content generation is not available. Please check your OpenAI API key configuration."
            )
            return

        business_name = self.business_name_input.text().strip()
        industry = self.industry_input.currentText().strip()

        if not business_name or not industry:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter Business Name and Industry before generating AI content."
            )
            return

        # Generate content
        business_desc = self.description_input.toPlainText().strip()

        content = self.business_generator.generate_service_guarantee(
            business_name=business_name,
            industry=industry,
            business_description=business_desc
        )

        if not content:
            QMessageBox.critical(
                self,
                "Generation Failed",
                "Failed to generate service guarantee. Please try again."
            )
            return

        # Show preview dialog
        dialog = AIContentPreviewDialog(
            title="AI Generated Service Guarantee",
            field_name="Service Guarantee",
            content=content,
            regenerate_callback=lambda: self.business_generator.generate_service_guarantee(
                business_name=business_name,
                industry=industry,
                business_description=business_desc
            ),
            parent=self
        )

        dialog.content_accepted.connect(lambda c: self.service_guarantee_input.setPlainText(c))
        dialog.exec()

    def _generate_service_area_description(self):
        """Generate service area description using AI"""
        if not self.ai_service.is_available():
            QMessageBox.warning(
                self,
                "AI Not Available",
                "AI content generation is not available. Please check your OpenAI API key configuration."
            )
            return

        business_name = self.business_name_input.text().strip()
        industry = self.industry_input.currentText().strip()

        if not business_name or not industry:
            QMessageBox.warning(
                self,
                "Missing Information",
                "Please enter Business Name and Industry before generating AI content."
            )
            return

        # Generate content
        # TODO: Get actual service areas from city pages when available
        service_areas = []

        content = self.business_generator.generate_service_area_description(
            business_name=business_name,
            industry=industry,
            service_areas=service_areas
        )

        if not content:
            QMessageBox.critical(
                self,
                "Generation Failed",
                "Failed to generate service area description. Please try again."
            )
            return

        # Show preview dialog
        dialog = AIContentPreviewDialog(
            title="AI Generated Service Area Description",
            field_name="Service Area Description",
            content=content,
            regenerate_callback=lambda: self.business_generator.generate_service_area_description(
                business_name=business_name,
                industry=industry,
                service_areas=service_areas
            ),
            parent=self
        )

        dialog.content_accepted.connect(lambda c: self.service_area_description_input.setPlainText(c))
        dialog.exec()