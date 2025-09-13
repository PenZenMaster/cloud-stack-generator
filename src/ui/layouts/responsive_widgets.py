"""
Filename: responsive_widgets.py
Path: E:/projects/cloud-stack-generator/src/ui/layouts/responsive_widgets.py
Description: Enhanced widgets with DPI awareness and proper size policies
Provides consistent widget behavior to prevent UI scaling issues

Version: 1.0.0
Date: 2025-08-15
Author: Cloud Stack Generator Team
"""

from PyQt6.QtWidgets import (
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QApplication,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPalette, QColor
from typing import Optional


class ResponsiveLabel(QLabel):
    """
    Enhanced QLabel with proper word wrapping and size policies
    
    Features:
    - Automatic word wrapping
    - Proper size hints for scaling
    - DPI-aware font sizing
    """
    
    def __init__(self, text: str = "", parent: Optional = None):
        super().__init__(text, parent)
        self._setup_label()
    
    def _setup_label(self):
        """Setup label with proper policies"""
        self.setWordWrap(True)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
    
    def sizeHint(self) -> QSize:
        """Provide proper size hint for layout calculations"""
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text())
        
        # Provide reasonable minimum width
        min_width = min(max(text_width, 100), 300)
        
        # Calculate height based on word wrap
        rect = font_metrics.boundingRect(0, 0, min_width, 0, 
                                       Qt.TextFlag.TextWordWrap, self.text())
        
        return QSize(min_width, max(rect.height(), font_metrics.height()))
    
    def minimumSizeHint(self) -> QSize:
        """Provide minimum size hint"""
        font_metrics = self.fontMetrics()
        return QSize(80, font_metrics.height())


class ExpandingLineEdit(QLineEdit):
    """
    Enhanced QLineEdit with proper expansion and minimum size policies
    
    Features:
    - Proper size policies for horizontal expansion
    - DPI-aware minimum width
    - Consistent height across different DPI settings
    """
    
    def __init__(self, text: str = "", parent: Optional = None):
        super().__init__(text, parent)
        self._setup_line_edit()
    
    def _setup_line_edit(self):
        """Setup line edit with proper policies"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
    
    def sizeHint(self) -> QSize:
        """Provide proper size hint for layout calculations"""
        font_metrics = self.fontMetrics()
        
        # Base width on approximate character count
        char_width = font_metrics.averageCharWidth()
        preferred_width = char_width * 25  # ~25 characters
        
        # Height with some padding
        height = font_metrics.height() + self._scaled_value(10)
        
        return QSize(preferred_width, height)
    
    def minimumSizeHint(self) -> QSize:
        """Provide minimum size hint"""
        font_metrics = self.fontMetrics()
        
        # Minimum width for ~10 characters
        char_width = font_metrics.averageCharWidth()
        min_width = char_width * 10
        
        # Height with padding
        height = font_metrics.height() + self._scaled_value(8)
        
        return QSize(min_width, height)
    
    def _scaled_value(self, base_value: int) -> int:
        """Get DPI-scaled value"""
        try:
            dpi_ratio = QApplication.primaryScreen().devicePixelRatio()
            return max(int(base_value * dpi_ratio), base_value)
        except:
            return base_value


class ScalableTextEdit(QTextEdit):
    """
    Enhanced QTextEdit with proper scroll bars and size policies
    
    Features:
    - Always visible scroll bars when needed
    - Proper size policies for expansion
    - DPI-aware minimum dimensions
    - Custom placeholder text support
    """
    
    def __init__(self, text: str = "", parent: Optional = None):
        super().__init__(text, parent)
        self._placeholder_text = ""
        self._setup_text_edit()
    
    def _setup_text_edit(self):
        """Setup text edit with proper policies and scroll bars"""
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Ensure scroll bars are properly visible
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Set line wrap mode for better text display
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
    
    def sizeHint(self) -> QSize:
        """Provide proper size hint for layout calculations"""
        font_metrics = self.fontMetrics()
        
        # Base dimensions on character and line counts
        char_width = font_metrics.averageCharWidth()
        line_height = font_metrics.lineSpacing()
        
        # Preferred size for ~50 characters x 6 lines
        width = char_width * 50 + self._scaled_value(20)  # Extra for scroll bar
        height = line_height * 6 + self._scaled_value(20)  # Extra for padding
        
        return QSize(width, height)
    
    def minimumSizeHint(self) -> QSize:
        """Provide minimum size hint"""
        font_metrics = self.fontMetrics()
        
        # Minimum dimensions
        char_width = font_metrics.averageCharWidth()
        line_height = font_metrics.lineSpacing()
        
        # Minimum size for ~20 characters x 3 lines
        width = char_width * 20 + self._scaled_value(15)
        height = line_height * 3 + self._scaled_value(15)
        
        return QSize(width, height)
    
    def _scaled_value(self, base_value: int) -> int:
        """Get DPI-scaled value"""
        try:
            dpi_ratio = QApplication.primaryScreen().devicePixelRatio()
            return max(int(base_value * dpi_ratio), base_value)
        except:
            return base_value
    
    def setPlaceholderText(self, text: str):
        """Set placeholder text (custom implementation)"""
        self._placeholder_text = text
        if not self.toPlainText():
            self._show_placeholder()
    
    def _show_placeholder(self):
        """Show placeholder text with styling"""
        if self._placeholder_text and not self.toPlainText():
            self.setPlainText(self._placeholder_text)
            # Make text appear as placeholder
            palette = self.palette()
            palette.setColor(QPalette.ColorRole.Text, QColor(128, 128, 128))
            self.setPalette(palette)
    
    def _hide_placeholder(self):
        """Hide placeholder text and restore normal styling"""
        if self.toPlainText() == self._placeholder_text:
            self.clear()
        # Restore normal text color
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        self.setPalette(palette)
    
    def focusInEvent(self, event):
        """Handle focus in to hide placeholder"""
        self._hide_placeholder()
        super().focusInEvent(event)
    
    def focusOutEvent(self, event):
        """Handle focus out to show placeholder if empty"""
        super().focusOutEvent(event)
        if not self.toPlainText():
            self._show_placeholder()


class ColorPreviewLabel(QLabel):
    """
    Enhanced QLabel for color preview with proper size policies
    
    Features:
    - Fixed aspect ratio for color displays
    - Proper size hints for consistent appearance
    - Click signal for color picker activation
    """
    
    # Signal emitted when label is clicked
    clicked = pyqtSignal()
    
    def __init__(self, color: str = "#ffffff", parent: Optional = None):
        super().__init__(parent)
        self._color = color
        self._setup_preview()
    
    def _setup_preview(self):
        """Setup color preview with proper styling"""
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {self._color};
                border: 2px solid #ccc;
                border-radius: 4px;
            }}
            QLabel:hover {{
                border-color: #999;
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def sizeHint(self) -> QSize:
        """Provide consistent size hint"""
        size = self._scaled_value(30)
        return QSize(size, size)
    
    def minimumSizeHint(self) -> QSize:
        """Provide minimum size hint"""
        size = self._scaled_value(20)
        return QSize(size, size)
    
    def _scaled_value(self, base_value: int) -> int:
        """Get DPI-scaled value"""
        try:
            dpi_ratio = QApplication.primaryScreen().devicePixelRatio()
            return max(int(base_value * dpi_ratio), base_value)
        except:
            return base_value
    
    def setColor(self, color: str):
        """Update the color and refresh styling"""
        self._color = color
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                border: 2px solid #ccc;
                border-radius: 4px;
            }}
            QLabel:hover {{
                border-color: #999;
            }}
        """)
    
    def getColor(self) -> str:
        """Get current color value"""
        return self._color
    
    def mousePressEvent(self, event):
        """Emit clicked signal when pressed"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class ResponsiveButton(QPushButton):
    """
    Enhanced QPushButton with proper size policies and DPI scaling
    
    Features:
    - Proper minimum size hints
    - DPI-aware padding
    - Consistent appearance across different screens
    """
    
    def __init__(self, text: str = "", parent: Optional = None):
        super().__init__(text, parent)
        self._setup_button()
    
    def _setup_button(self):
        """Setup button with proper policies"""
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
    
    def sizeHint(self) -> QSize:
        """Provide proper size hint"""
        font_metrics = self.fontMetrics()
        text_width = font_metrics.horizontalAdvance(self.text())
        
        # Add padding for button appearance
        width = text_width + self._scaled_value(30)
        height = font_metrics.height() + self._scaled_value(12)
        
        return QSize(width, height)
    
    def minimumSizeHint(self) -> QSize:
        """Provide minimum size hint"""
        font_metrics = self.fontMetrics()
        
        # Minimum dimensions with padding
        width = self._scaled_value(80)
        height = font_metrics.height() + self._scaled_value(8)
        
        return QSize(width, height)
    
    def _scaled_value(self, base_value: int) -> int:
        """Get DPI-scaled value"""
        try:
            dpi_ratio = QApplication.primaryScreen().devicePixelRatio()
            return max(int(base_value * dpi_ratio), base_value)
        except:
            return base_value