"""
Filename: src/ui/components/base_tab.py
Path: E:/projects/cloud-stack-generator/src/ui/components/base_tab.py
Description: Abstract base class for all configuration tabs with standardized interface
Enhanced with scalable layout system integration

Version: 1.1.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QTabWidget,
    QScrollArea,
    QSizePolicy,
)
from PyQt6.QtCore import pyqtSignal, QTimer, Qt
from PyQt6.QtGui import QFont
from typing import Dict, Any, List, Optional, Protocol

# Import the new layout system
from ..layouts import (
    ScalableLayout, 
    ResponsiveSection, 
    StandardFormLayout,
    ResponsiveLabel
)


class ValidationResult:
    """Standardized validation result container"""

    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.field_errors = {}  # field_name -> error_message

    def add_error(self, message: str, field_name: Optional[str] = None):
        """Add validation error"""
        self.errors.append(message)
        self.is_valid = False
        if field_name:
            self.field_errors[field_name] = message

    def add_warning(self, message: str):
        """Add validation warning"""
        self.warnings.append(message)

    def has_errors(self) -> bool:
        """Check if validation has errors"""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if validation has warnings"""
        return len(self.warnings) > 0

    def get_summary(self) -> str:
        """Get validation summary message"""
        if self.is_valid and not self.warnings:
            return "All data is valid"

        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")

        return f"Validation completed with {', '.join(parts)}"


class TabInterface(Protocol):
    """Protocol defining the interface for configuration tabs"""

    def setup_ui(self) -> None:
        """Setup the user interface for this tab"""
        ...

    def get_config_data(self) -> Dict[str, Any]:
        """Get configuration data from this tab"""
        ...

    def set_config_data(self, data: Dict[str, Any]) -> None:
        """Set configuration data for this tab"""
        ...


class BaseTab(QWidget):
    """
    Base class for all configuration tabs.

    Provides standardized interface for:
    - Configuration data management
    - Validation with visual feedback
    - Change tracking and notifications
    - UI setup and teardown

    Note: Subclasses must implement setup_ui(), get_config_data(), and set_config_data()
    """

    # Signals
    config_changed = pyqtSignal()
    validation_requested = pyqtSignal()
    data_loaded = pyqtSignal()
    tab_activated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        # State tracking
        self._is_loading = False
        self._has_unsaved_changes = False
        self._last_validation_result = None

        # UI components
        self._error_widgets = {}
        self._validation_timer = QTimer()
        self._validation_timer.setSingleShot(True)
        self._validation_timer.timeout.connect(self._perform_validation)

        # Initialize UI
        self.setup_ui()
        self.connect_signals()

        # Set initial state
        self._update_ui_state()

    def setup_ui(self):
        """
        Setup the user interface for this tab.

        This method must be implemented by subclasses.
        Raises NotImplementedError if not overridden.
        """
        raise NotImplementedError("Subclasses must implement setup_ui()")

    def get_config_data(self) -> Dict[str, Any]:
        """
        Get configuration data from this tab.

        This method must be implemented by subclasses.

        Returns:
            Dict containing the configuration data for this tab

        Raises:
            NotImplementedError if not overridden by subclass
        """
        raise NotImplementedError("Subclasses must implement get_config_data()")

    def set_config_data(self, data: Dict[str, Any]):
        """
        Set configuration data for this tab.

        This method must be implemented by subclasses.

        Args:
            data: Configuration data to populate the tab

        Raises:
            NotImplementedError if not overridden by subclass
        """
        raise NotImplementedError("Subclasses must implement set_config_data()")

    def get_tab_name(self) -> str:
        """Get the display name for this tab"""
        return self.__class__.__name__.replace("Tab", "")

    def get_required_fields(self) -> List[str]:
        """Get list of required field names for validation"""
        return []

    def validate_data(self) -> ValidationResult:
        """
        Validate the data in this tab.

        Returns:
            ValidationResult with validation status and messages
        """
        result = ValidationResult()

        # Basic validation - check required fields
        config_data = self.get_config_data()
        required_fields = self.get_required_fields()

        for field in required_fields:
            value = config_data.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                result.add_error(
                    f"{field.replace('_', ' ').title()} is required", field
                )

        # Store result for UI updates
        self._last_validation_result = result

        return result

    def connect_signals(self):
        """Connect UI signals to emit config_changed"""
        # Override in subclasses to connect specific widgets
        pass

    def clear_data(self):
        """Clear all data in this tab"""
        # Override in subclasses for specific clearing logic
        pass

    def has_unsaved_changes(self) -> bool:
        """Check if tab has unsaved changes"""
        return self._has_unsaved_changes

    def mark_as_saved(self):
        """Mark tab as having no unsaved changes"""
        self._has_unsaved_changes = False
        self._update_ui_state()

    # Protected methods for subclass use

    def _emit_config_changed(self):
        """Helper method to emit config changed signal"""
        if not self._is_loading:
            self._has_unsaved_changes = True
            self._update_ui_state()
            self.config_changed.emit()

            # Trigger delayed validation
            self._validation_timer.start(500)  # 500ms delay

    def _start_loading(self):
        """Mark tab as loading data (suppresses change signals)"""
        self._is_loading = True

    def _finish_loading(self):
        """Mark tab as finished loading data"""
        self._is_loading = False
        self._has_unsaved_changes = False
        self._update_ui_state()
        self.data_loaded.emit()

    def _create_error_label(self, field_name: str) -> QLabel:
        """Create error label for field validation"""
        error_label = QLabel()
        error_label.setObjectName(f"error_label_{field_name}")
        error_label.setStyleSheet("color: red; font-size: 10px;")
        error_label.hide()
        self._error_widgets[field_name] = error_label
        return error_label

    def _show_field_error(self, field_name: str, message: str):
        """Show error message for specific field"""
        if field_name in self._error_widgets:
            error_widget = self._error_widgets[field_name]
            error_widget.setText(message)
            error_widget.show()

    def _hide_field_error(self, field_name: str):
        """Hide error message for specific field"""
        if field_name in self._error_widgets:
            self._error_widgets[field_name].hide()

    def _create_section_header(self, title: str) -> QLabel:
        """Create standardized section header"""
        header = QLabel(title)
        header.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        header.setStyleSheet("color: #2c3e50; margin: 10px 0 5px 0;")
        return header

    def _create_separator(self) -> QFrame:
        """Create horizontal separator line"""
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("color: #bdc3c7;")
        return separator

    # Private methods

    def _perform_validation(self):
        """Perform validation and update UI"""
        result = self.validate_data()
        
        # Debug logging to identify the source of tuple returns
        if isinstance(result, tuple):
            print(f"WARNING: {self.__class__.__name__}.validate_data() returned tuple instead of ValidationResult: {result}")
        
        self._update_validation_ui(result)

    def _update_validation_ui(self, result):
        """Update UI based on validation result"""
        # Hide all field errors first
        for field_name in self._error_widgets:
            self._hide_field_error(field_name)

        # Handle both ValidationResult objects and legacy tuple format
        if hasattr(result, 'field_errors'):
            # Show field-specific errors
            for field_name, error_message in result.field_errors.items():
                self._show_field_error(field_name, error_message)
        elif isinstance(result, tuple) and len(result) >= 2:
            # Handle legacy tuple format (bool, List[str])
            is_valid, errors = result
            # For tuples, we can't map errors to specific fields
            # Just log the error for debugging
            if not is_valid and errors:
                print(f"Validation errors (legacy format): {errors}")
        else:
            print(f"Unexpected validation result format: {type(result)}")

    def _update_ui_state(self):
        """Update UI state based on current tab state"""
        pass  # Can be overridden by subclasses

    # New layout system helper methods
    
    def create_scalable_layout(self) -> ScalableLayout:
        """
        Create a scalable layout for the tab content
        
        Returns:
            ScalableLayout instance with proper DPI scaling
        """
        return ScalableLayout(self)
    
    def create_responsive_section(self, title: str = "") -> ResponsiveSection:
        """
        Create a responsive section container with scroll support
        
        Args:
            title: Section title (optional)
            
        Returns:
            ResponsiveSection instance with built-in scroll area
        """
        return ResponsiveSection(title, self)
    
    def create_standard_form(self) -> StandardFormLayout:
        """
        Create a standard form layout with consistent field scaling
        
        Returns:
            StandardFormLayout instance for form fields
        """
        return StandardFormLayout(self)
    
    def create_section_header(self, title: str) -> ResponsiveLabel:
        """
        Create a responsive section header with proper scaling
        
        Args:
            title: Header text
            
        Returns:
            ResponsiveLabel configured as section header
        """
        header = ResponsiveLabel(title, self)
        font = header.font()
        font.setBold(True)
        font.setPointSize(font.pointSize() + 2)
        header.setFont(font)
        header.setStyleSheet("color: #2c3e50; margin: 15px 0 10px 0; padding: 5px 0;")
        return header
    
    def wrap_in_scroll_area(self, widget: QWidget) -> QScrollArea:
        """
        Wrap a widget in a scroll area with proper configuration
        
        Args:
            widget: Widget to wrap in scroll area
            
        Returns:
            QScrollArea containing the widget
        """
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setWidget(widget)
        
        # Ensure proper size policies
        scroll_area.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        return scroll_area
    
    def _update_tab_title(self):
        """Update tab title to show unsaved changes"""
        # Update tab title to show unsaved changes
        tab_name = self.get_tab_name()
        if self._has_unsaved_changes:
            tab_name += " *"

        # Find our tab index and update title (with proper type checking)
        parent = self.parent()
        if isinstance(parent, QTabWidget):
            try:
                index = parent.indexOf(self)
                if index >= 0:
                    parent.setTabText(index, tab_name)
            except AttributeError:
                # Fallback if indexOf/setTabText not available
                pass
    
    def get_tab_name(self) -> str:
        """Get the name of this tab - override in subclasses"""
        return "Tab"


class TabConfigurationError(Exception):
    """Exception raised when tab configuration is invalid"""

    pass
