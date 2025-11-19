"""
Module/Script Name: Documentation Viewer Dialog
Path: src/ui/dialogs/documentation_viewer.py

Description:
Non-modal dialog for displaying documentation files with markdown rendering.

Author(s):
Rank Rocket Co (C) Copyright 2025 - All Rights Reserved

Created Date:
2025-11-19

Last Modified Date:
2025-11-19

Comments:
* v1.00 - Initial documentation viewer dialog
* v1.01 - Added markdown rendering support
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QTextBrowser,
    QPushButton,
    QLabel,
    QMessageBox,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QTextCursor

try:
    import markdown
    MARKDOWN_AVAILABLE = True
except ImportError:
    MARKDOWN_AVAILABLE = False


class DocumentationViewer(QDialog):
    """
    Non-modal dialog for viewing documentation files.

    Features:
    - Markdown rendering (.md files)
    - HTML rendering support
    - Plain text fallback
    - Scrollable view
    - Resizable window
    """

    def __init__(self, doc_path: Path, parent=None):
        """
        Initialize documentation viewer.

        Args:
            doc_path: Path to the documentation file
            parent: Parent widget
        """
        super().__init__(parent)

        self.doc_path = doc_path
        self.setWindowTitle(f"Documentation - {doc_path.name}")
        self.setMinimumSize(800, 600)

        # Make non-modal
        self.setModal(False)

        self._setup_ui()
        self._load_documentation()

    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)

        # Header with file name
        header_layout = QHBoxLayout()

        file_label = QLabel(f"<b>File:</b> {self.doc_path.name}")
        file_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        header_layout.addWidget(file_label)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Text viewer (read-only, supports HTML)
        self.text_viewer = QTextBrowser()
        self.text_viewer.setReadOnly(True)
        self.text_viewer.setOpenExternalLinks(True)  # Allow clicking links in docs

        # Use readable font size
        font = QFont("Arial", 10)
        self.text_viewer.setFont(font)

        layout.addWidget(self.text_viewer)

        # Footer with buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.close)
        close_btn.setMinimumWidth(100)
        button_layout.addWidget(close_btn)

        layout.addLayout(button_layout)

    def _load_documentation(self):
        """Load and display the documentation file with proper rendering."""
        try:
            if not self.doc_path.exists():
                self.text_viewer.setPlainText(
                    f"Error: Documentation file not found:\n{self.doc_path}"
                )
                return

            # Read file content
            with open(self.doc_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine file type and render appropriately
            file_extension = self.doc_path.suffix.lower()

            if file_extension == '.md' and MARKDOWN_AVAILABLE:
                # Render markdown as HTML
                html_content = self._render_markdown(content)
                self.text_viewer.setHtml(html_content)
            elif file_extension == '.html' or file_extension == '.htm':
                # Display HTML directly
                self.text_viewer.setHtml(content)
            else:
                # Display as plain text
                self.text_viewer.setPlainText(content)

            # Scroll to top
            cursor = self.text_viewer.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            self.text_viewer.setTextCursor(cursor)

        except Exception as e:
            error_msg = f"Error loading documentation:\n{str(e)}"
            self.text_viewer.setPlainText(error_msg)
            QMessageBox.warning(
                self,
                "Load Error",
                f"Failed to load documentation file:\n{str(e)}"
            )

    def _render_markdown(self, markdown_content: str) -> str:
        """
        Convert markdown to HTML with styling.

        Args:
            markdown_content: Raw markdown text

        Returns:
            Formatted HTML string
        """
        if not MARKDOWN_AVAILABLE:
            return f"<pre>{markdown_content}</pre>"

        # Convert markdown to HTML with extensions
        try:
            html = markdown.markdown(
                markdown_content,
                extensions=[
                    'extra',          # Tables, code blocks, etc.
                    'fenced_code',    # Fenced code blocks
                    'tables',         # Table support
                    'nl2br',          # Convert newlines to <br>
                    'sane_lists',     # Better list handling
                ]
            )
        except Exception:
            # Fallback to basic markdown if extensions fail
            html = markdown.markdown(markdown_content)

        # Wrap in styled HTML document
        styled_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    padding: 20px;
                    max-width: 900px;
                    margin: 0 auto;
                }}
                h1, h2, h3, h4, h5, h6 {{
                    color: #2c3e50;
                    margin-top: 24px;
                    margin-bottom: 16px;
                    font-weight: 600;
                    line-height: 1.25;
                }}
                h1 {{
                    font-size: 2em;
                    border-bottom: 2px solid #eaecef;
                    padding-bottom: 0.3em;
                }}
                h2 {{
                    font-size: 1.5em;
                    border-bottom: 1px solid #eaecef;
                    padding-bottom: 0.3em;
                }}
                h3 {{ font-size: 1.25em; }}
                h4 {{ font-size: 1em; }}
                p {{ margin-bottom: 16px; }}
                code {{
                    background-color: #f6f8fa;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                }}
                pre {{
                    background-color: #f6f8fa;
                    padding: 16px;
                    border-radius: 6px;
                    overflow-x: auto;
                    line-height: 1.45;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                blockquote {{
                    border-left: 4px solid #dfe2e5;
                    padding-left: 16px;
                    margin-left: 0;
                    color: #6a737d;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                    margin-bottom: 16px;
                }}
                table th, table td {{
                    border: 1px solid #dfe2e5;
                    padding: 8px 13px;
                }}
                table th {{
                    background-color: #f6f8fa;
                    font-weight: 600;
                }}
                table tr:nth-child(even) {{
                    background-color: #f6f8fa;
                }}
                ul, ol {{
                    margin-bottom: 16px;
                    padding-left: 2em;
                }}
                li {{
                    margin-bottom: 4px;
                }}
                a {{
                    color: #0366d6;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                hr {{
                    border: 0;
                    border-top: 2px solid #eaecef;
                    margin: 24px 0;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """

        return styled_html


def show_documentation(doc_path: Path, parent=None) -> Optional[DocumentationViewer]:
    """
    Convenience function to show a documentation viewer.

    Args:
        doc_path: Path to the documentation file
        parent: Parent widget

    Returns:
        DocumentationViewer instance or None if file doesn't exist
    """
    if not doc_path.exists():
        QMessageBox.warning(
            parent,
            "File Not Found",
            f"Documentation file not found:\n{doc_path}"
        )
        return None

    viewer = DocumentationViewer(doc_path, parent)
    viewer.show()
    return viewer
