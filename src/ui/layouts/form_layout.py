"""
Filename: form_layout.py
Path: E:/projects/cloud-stack-generator/src/ui/layouts/form_layout.py
Description: Standardized form layout system with consistent field scaling and validation
Provides unified form management to prevent field visibility issues

Version: 1.0.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

from PyQt6.QtWidgets import (
    QWidget,
    QGridLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QApplication,
    QSizePolicy,
    QSpacerItem
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Optional, Dict, Tuple, List
from .responsive_widgets import ResponsiveLabel, ExpandingLineEdit, ScalableTextEdit


class StandardFormLayout(QWidget):
    """
    Standardized form layout with consistent field scaling and validation display.
    
    Features:
    - Automatic label width calculation with word wrap
    - Expandable input fields with proper size hints
    - Built-in error message display
    - Consistent spacing and alignment
    - DPI-aware font and spacing scaling
    """
    
    # Signals
    field_changed = pyqtSignal(str, str)  # field_name, value
    validation_requested = pyqtSignal(str)  # field_name
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._grid_layout = QGridLayout()
        self._fields: Dict[str, QWidget] = {}
        self._labels: Dict[str, ResponsiveLabel] = {}
        self._error_labels: Dict[str, QLabel] = {}
        self._current_row = 0
        self._setup_form()
    
    def _setup_form(self):
        """Setup form with proper spacing and policies"""
        spacing = self._scaled_value(10)
        margins = self._scaled_margins(5, 5, 5, 5)
        
        self._grid_layout.setSpacing(spacing)
        self._grid_layout.setContentsMargins(*margins)
        
        # Set column stretch factors for responsive layout
        self._grid_layout.setColumnStretch(0, 1)  # Labels column - fixed width
        self._grid_layout.setColumnStretch(1, 3)  # Input column - expandable
        self._grid_layout.setColumnStretch(2, 1)  # Error column - fixed width
        
        self.setLayout(self._grid_layout)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    
    def _scaled_value(self, base_value: int) -> int:
        """Get DPI-scaled value"""
        try:
            dpi_ratio = QApplication.primaryScreen().devicePixelRatio()
            return max(int(base_value * dpi_ratio), base_value)
        except:
            return base_value
    
    def _scaled_margins(self, left: int, top: int, right: int, bottom: int) -> Tuple[int, int, int, int]:
        """Get DPI-scaled margin values"""
        try:
            dpi_ratio = QApplication.primaryScreen().devicePixelRatio()
            return (
                max(int(left * dpi_ratio), left),
                max(int(top * dpi_ratio), top),
                max(int(right * dpi_ratio), right),
                max(int(bottom * dpi_ratio), bottom)
            )
        except:
            return (left, top, right, bottom)
    
    def _create_error_label(self, field_name: str) -> QLabel:
        """Create error label for field validation"""
        error_label = QLabel()
        error_label.setStyleSheet("color: red; font-size: 11px;")
        error_label.setWordWrap(True)
        error_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        error_label.hide()  # Hidden by default
        return error_label
    
    def addField(self, field_name: str, label_text: str, widget: QWidget, 
                placeholder: str = "", required: bool = False) -> QWidget:
        """
        Add a field to the form with proper scaling and validation setup
        
        Args:
            field_name: Unique field identifier
            label_text: Display text for label  
            widget: Input widget (LineEdit, TextEdit, ComboBox, etc.)
            placeholder: Placeholder text for input
            required: Whether field is required (adds * to label)
            
        Returns:
            The widget that was added
        """
        # Create responsive label
        display_text = f"* {label_text}" if required else label_text
        label = ResponsiveLabel(display_text)
        
        # Setup input widget
        if isinstance(widget, QLineEdit):
            if not isinstance(widget, ExpandingLineEdit):
                # Upgrade to ExpandingLineEdit for better scaling
                new_widget = ExpandingLineEdit()
                new_widget.setText(widget.text())
                if placeholder:
                    new_widget.setPlaceholderText(placeholder)
                widget = new_widget
            else:
                if placeholder:
                    widget.setPlaceholderText(placeholder)
        
        elif isinstance(widget, QTextEdit):
            if not isinstance(widget, ScalableTextEdit):
                # Upgrade to ScalableTextEdit for better scaling
                new_widget = ScalableTextEdit()
                new_widget.setPlainText(widget.toPlainText())
                if placeholder:
                    new_widget.setPlaceholderText(placeholder)
                widget = new_widget
            else:
                if placeholder:
                    widget.setPlaceholderText(placeholder)
        
        elif isinstance(widget, QComboBox):
            widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Create error label
        error_label = self._create_error_label(field_name)
        
        # Add to grid layout
        self._grid_layout.addWidget(label, self._current_row, 0, Qt.AlignmentFlag.AlignTop)
        self._grid_layout.addWidget(widget, self._current_row, 1)
        self._grid_layout.addWidget(error_label, self._current_row, 2, Qt.AlignmentFlag.AlignTop)
        
        # Store references
        self._fields[field_name] = widget
        self._labels[field_name] = label
        self._error_labels[field_name] = error_label
        
        # Connect change signals
        self._connect_field_signals(field_name, widget)
        
        self._current_row += 1
        return widget
    
    def _connect_field_signals(self, field_name: str, widget: QWidget):
        """Connect field change signals"""
        if isinstance(widget, (QLineEdit, ExpandingLineEdit)):
            widget.textChanged.connect(lambda text: self.field_changed.emit(field_name, text))
        elif isinstance(widget, (QTextEdit, ScalableTextEdit)):
            widget.textChanged.connect(lambda: self.field_changed.emit(field_name, widget.toPlainText()))
        elif isinstance(widget, QComboBox):
            widget.currentTextChanged.connect(lambda text: self.field_changed.emit(field_name, text))
    
    def addLineEdit(self, field_name: str, label_text: str, placeholder: str = "", 
                   required: bool = False) -> ExpandingLineEdit:
        """
        Add a line edit field with proper scaling
        
        Args:
            field_name: Unique field identifier
            label_text: Display text for label
            placeholder: Placeholder text
            required: Whether field is required
            
        Returns:
            The ExpandingLineEdit widget
        """
        widget = ExpandingLineEdit()
        return self.addField(field_name, label_text, widget, placeholder, required)
    
    def addTextEdit(self, field_name: str, label_text: str, placeholder: str = "", 
                   required: bool = False, min_height: int = 100) -> ScalableTextEdit:
        """
        Add a text edit field with proper scaling
        
        Args:
            field_name: Unique field identifier
            label_text: Display text for label
            placeholder: Placeholder text
            required: Whether field is required
            min_height: Minimum height for text area
            
        Returns:
            The ScalableTextEdit widget
        """
        widget = ScalableTextEdit()
        widget.setMinimumHeight(min_height)
        return self.addField(field_name, label_text, widget, placeholder, required)
    
    def addComboBox(self, field_name: str, label_text: str, items: List[str], 
                   required: bool = False) -> QComboBox:
        """
        Add a combo box field with proper scaling
        
        Args:
            field_name: Unique field identifier
            label_text: Display text for label
            items: List of items for combo box
            required: Whether field is required
            
        Returns:
            The QComboBox widget
        """
        widget = QComboBox()
        widget.addItems(items)
        return self.addField(field_name, label_text, widget, "", required)
    
    def addSectionSpacer(self, height: int = 20):
        """Add vertical spacing between form sections"""
        spacer = QSpacerItem(20, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        self._grid_layout.addItem(spacer, self._current_row, 0, 1, 3)
        self._current_row += 1
    
    def addSectionHeader(self, header_text: str):
        """Add a section header to the form"""
        header_label = QLabel(header_text)
        header_font = header_label.font()
        header_font.setBold(True)
        header_font.setPointSize(header_font.pointSize() + 1)
        header_label.setFont(header_font)
        header_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        self._grid_layout.addWidget(header_label, self._current_row, 0, 1, 3)
        self._current_row += 1
    
    def getField(self, field_name: str) -> Optional[QWidget]:
        """Get field widget by name"""
        return self._fields.get(field_name)
    
    def getFieldValue(self, field_name: str) -> str:
        """Get field value as string"""
        widget = self._fields.get(field_name)
        if not widget:
            return ""
        
        if isinstance(widget, (QLineEdit, ExpandingLineEdit)):
            return widget.text()
        elif isinstance(widget, (QTextEdit, ScalableTextEdit)):
            return widget.toPlainText()
        elif isinstance(widget, QComboBox):
            return widget.currentText()
        
        return ""
    
    def setFieldValue(self, field_name: str, value: str):
        """Set field value"""
        widget = self._fields.get(field_name)
        if not widget:
            return
        
        if isinstance(widget, (QLineEdit, ExpandingLineEdit)):
            widget.setText(value)
        elif isinstance(widget, (QTextEdit, ScalableTextEdit)):
            widget.setPlainText(value)
        elif isinstance(widget, QComboBox):
            index = widget.findText(value)
            if index >= 0:
                widget.setCurrentIndex(index)
    
    def showFieldError(self, field_name: str, error_message: str):
        """Show error message for field"""
        error_label = self._error_labels.get(field_name)
        if error_label:
            error_label.setText(error_message)
            error_label.show()
    
    def hideFieldError(self, field_name: str):
        """Hide error message for field"""
        error_label = self._error_labels.get(field_name)
        if error_label:
            error_label.hide()
    
    def clearAllErrors(self):
        """Clear all field error messages"""
        for error_label in self._error_labels.values():
            error_label.hide()
    
    def getAllFieldValues(self) -> Dict[str, str]:
        """Get all field values as dictionary"""
        return {field_name: self.getFieldValue(field_name) 
                for field_name in self._fields.keys()}
    
    def setAllFieldValues(self, values: Dict[str, str]):
        """Set multiple field values from dictionary"""
        for field_name, value in values.items():
            self.setFieldValue(field_name, value)