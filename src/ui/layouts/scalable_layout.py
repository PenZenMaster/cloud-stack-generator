"""
Filename: scalable_layout.py
Path: E:/projects/cloud-stack-generator/src/ui/layouts/scalable_layout.py
Description: Core scalable layout framework with DPI awareness and proper size policies
Provides unified layout management to prevent UI scaling regressions

Version: 1.0.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

from PyQt6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox,
    QScrollArea,
    QWidget,
    QApplication,
    QSizePolicy,
    QSpacerItem
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont
from typing import Optional, Union, Tuple


class ScalableLayout(QVBoxLayout):
    """
    Core scalable layout manager with DPI awareness and proper size policies.
    
    Features:
    - Automatic DPI scaling for spacing and margins
    - Proper size policies for all added widgets
    - Built-in scroll support when needed
    - Consistent spacing ratios
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_layout()
    
    def _setup_layout(self):
        """Setup layout with DPI-aware spacing and margins"""
        spacing = self._scaled_spacing(15)
        margins = self._scaled_margins(10, 10, 10, 10)
        
        self.setSpacing(spacing)
        self.setContentsMargins(*margins)
    
    def _scaled_spacing(self, base_spacing: int) -> int:
        """Get DPI-scaled spacing value"""
        try:
            dpi_ratio = QApplication.primaryScreen().devicePixelRatio()
            return max(int(base_spacing * dpi_ratio), base_spacing)
        except:
            return base_spacing
    
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
    
    def addScalableWidget(self, widget: QWidget, stretch: int = 0):
        """
        Add widget with proper size policies for scaling
        
        Args:
            widget: Widget to add
            stretch: Stretch factor (default: 0)
        """
        # Set proper size policy for scaling
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Add to layout
        self.addWidget(widget, stretch)
    
    def addScalableSection(self, section: QWidget, title: str = "", stretch: int = 0) -> QWidget:
        """
        Add a section with proper scaling and optional scroll support
        
        Args:
            section: Section widget to add
            title: Optional title for the section
            stretch: Stretch factor
            
        Returns:
            The container widget (may be wrapped in scroll area)
        """
        if title:
            group_box = QGroupBox(title)
            layout = QVBoxLayout()
            layout.addWidget(section)
            group_box.setLayout(layout)
            container = group_box
        else:
            container = section
        
        self.addScalableWidget(container, stretch)
        return container
    
    def addStretchSpacer(self, stretch: int = 1):
        """Add stretch spacer to push content up/down"""
        spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.addItem(spacer)


class ResponsiveSection(QGroupBox):
    """
    Responsive section container with built-in scroll support and proper scaling.
    
    Features:
    - Automatic height adjustment
    - Built-in scroll area when content overflows
    - Consistent padding and margins
    - DPI-scaled fonts and spacing
    """
    
    def __init__(self, title: str = "", parent: Optional[QWidget] = None):
        super().__init__(title, parent)
        self._scroll_area: Optional[QScrollArea] = None
        self._content_widget: Optional[QWidget] = None
        self._content_layout: Optional[QVBoxLayout] = None
        self._setup_section()
    
    def _setup_section(self):
        """Setup responsive section with scroll support"""
        # Set proper size policy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Setup main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(self._scaled_value(10))
        main_layout.setContentsMargins(*self._scaled_margins(10, 10, 10, 10))
        
        # Create scroll area
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self._scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Create content widget and layout
        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setSpacing(self._scaled_value(10))
        self._content_layout.setContentsMargins(5, 5, 5, 5)
        
        self._content_widget.setLayout(self._content_layout)
        self._scroll_area.setWidget(self._content_widget)
        
        main_layout.addWidget(self._scroll_area)
        self.setLayout(main_layout)
    
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
    
    def addContentWidget(self, widget: QWidget, stretch: int = 0):
        """
        Add widget to the scrollable content area
        
        Args:
            widget: Widget to add
            stretch: Stretch factor
        """
        # Set proper size policy
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Add to content layout
        if self._content_layout:
            self._content_layout.addWidget(widget, stretch)
    
    def addContentLayout(self, layout, stretch: int = 0):
        """
        Add layout to the scrollable content area
        
        Args:
            layout: Layout to add
            stretch: Stretch factor
        """
        if self._content_layout:
            self._content_layout.addLayout(layout, stretch)
    
    def addContentStretch(self, stretch: int = 1):
        """Add stretch to push content up"""
        if self._content_layout:
            spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self._content_layout.addItem(spacer)
    
    def setScrollAreaVisible(self, visible: bool):
        """Show/hide scroll area (for sections that don't need scrolling)"""
        if self._scroll_area:
            if visible:
                self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            else:
                self._scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    
    def getContentWidget(self) -> Optional[QWidget]:
        """Get the content widget for direct manipulation"""
        return self._content_widget
    
    def getContentLayout(self) -> Optional[QVBoxLayout]:
        """Get the content layout for direct manipulation"""
        return self._content_layout


class ResponsiveGrid(QWidget):
    """
    Responsive grid container that adapts to different screen sizes
    
    Features:
    - Automatic column adjustment based on available width
    - Proper size policies for all children
    - DPI-aware spacing and margins
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._grid_layout = QGridLayout()
        self._setup_grid()
    
    def _setup_grid(self):
        """Setup responsive grid with proper spacing"""
        spacing = self._scaled_value(10)
        margins = self._scaled_margins(5, 5, 5, 5)
        
        self._grid_layout.setSpacing(spacing)
        self._grid_layout.setContentsMargins(*margins)
        
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
    
    def addWidget(self, widget: QWidget, row: int, column: int, 
                  row_span: int = 1, column_span: int = 1):
        """
        Add widget to grid with proper size policies
        
        Args:
            widget: Widget to add
            row: Grid row
            column: Grid column  
            row_span: Number of rows to span
            column_span: Number of columns to span
        """
        # Set proper size policy
        widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Add to grid
        self._grid_layout.addWidget(widget, row, column, row_span, column_span)
    
    def setColumnStretch(self, column: int, stretch: int):
        """Set column stretch factor"""
        self._grid_layout.setColumnStretch(column, stretch)
    
    def setRowStretch(self, row: int, stretch: int):
        """Set row stretch factor"""
        self._grid_layout.setRowStretch(row, stretch)