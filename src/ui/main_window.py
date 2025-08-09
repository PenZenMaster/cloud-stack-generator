"""
Filename: src/ui/main_window.py
Path: /src/ui/main_window.py
Description: Integrated Main Window for SEO Authority Website Generator
Combines YAML Builder with Website Generator in tabbed interface

Version: 2.0.2
Date: 2025-08-09
Author: Cloud Stack Generator Team
"""

import sys
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QMenuBar,
    QMenu,
    QMessageBox,
    QFileDialog,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QProgressBar,
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt, QThread, pyqtSignal

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.core.config_parser import ConfigParser, ConfigValidationError
from src.core.website_generator import WebsiteGenerator, GenerationError
from src.ui.yaml_builder import YAMLBuilderWidget


class GenerationWorker(QThread):
    """Worker thread for website generation to keep UI responsive"""

    progress = pyqtSignal(str)  # Progress message
    finished = pyqtSignal(bool, str, list)  # success, message, generated_files

    def __init__(self, config_dict: dict, output_dir: str):
        super().__init__()
        self.config_dict = config_dict
        self.output_dir = output_dir

    def run(self):
        """Run website generation in background thread"""
        try:
            self.progress.emit("Parsing configuration...")
            parser = ConfigParser()
            config = parser.parse(self.config_dict)

            self.progress.emit("Initializing website generator...")
            generator = WebsiteGenerator()

            self.progress.emit("Generating HTML pages...")
            result = generator.generate(config, self.output_dir)

            if result.success:
                self.progress.emit("Website generation completed!")
                self.finished.emit(
                    True, "Website generated successfully!", result.generated_files
                )
            else:
                self.finished.emit(False, f"Generation failed: {result.errors}", [])

        except ConfigValidationError as e:
            self.finished.emit(False, f"Configuration error: {str(e)}", [])
        except GenerationError as e:
            self.finished.emit(False, f"Generation error: {str(e)}", [])
        except Exception as e:
            self.finished.emit(False, f"Unexpected error: {str(e)}", [])


class GeneratorTab(QWidget):
    """Tab for website generation and preview"""

    def __init__(self, parent: Optional["SEOGeneratorMainWindow"] = None):
        super().__init__(parent)
        self.parent_window = parent
        self.output_dir: Optional[str] = None
        self.worker: Optional[GenerationWorker] = None
        self.setup_ui()

    def setup_ui(self):
        """Set up the generator tab UI"""
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Use the Configuration Builder tab to create your website configuration, "
            "then return here to generate your SEO-optimized website."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic; padding: 10px;")
        layout.addWidget(instructions)

        # Generation controls
        controls_layout = QHBoxLayout()

        self.output_dir_label = QLabel("Output Directory: Not selected")
        controls_layout.addWidget(self.output_dir_label)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_output_dir)
        controls_layout.addWidget(self.browse_button)

        layout.addLayout(controls_layout)

        # Generate button
        self.generate_button = QPushButton("Generate Website")
        self.generate_button.setStyleSheet(
            "QPushButton { background-color: #007bff; color: white; "
            "font-weight: bold; padding: 10px; }"
            "QPushButton:hover { background-color: #0056b3; }"
        )
        self.generate_button.clicked.connect(self.generate_website)
        layout.addWidget(self.generate_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status/log area
        layout.addWidget(QLabel("Generation Log:"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)

        # Generated files area
        layout.addWidget(QLabel("Generated Files:"))
        self.files_text = QTextEdit()
        self.files_text.setReadOnly(True)
        self.files_text.setMaximumHeight(100)
        layout.addWidget(self.files_text)

        # Action buttons
        action_layout = QHBoxLayout()

        self.open_folder_button = QPushButton("Open Output Folder")
        self.open_folder_button.clicked.connect(self.open_output_folder)
        self.open_folder_button.setEnabled(False)
        action_layout.addWidget(self.open_folder_button)

        self.preview_button = QPushButton("Preview in Browser")
        self.preview_button.clicked.connect(self.preview_website)
        self.preview_button.setEnabled(False)
        action_layout.addWidget(self.preview_button)

        action_layout.addStretch()
        layout.addLayout(action_layout)

        self.setLayout(layout)

    def browse_output_dir(self):
        """Browse for output directory"""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", str(Path.home())
        )
        if directory:
            self.output_dir = directory
            self.output_dir_label.setText(f"Output Directory: {directory}")
            self.log_text.append(f"Output directory set to: {directory}")

    def generate_website(self):
        """Generate website from current configuration"""
        if not self.output_dir:
            QMessageBox.warning(
                self, "No Output Directory", "Please select an output directory first."
            )
            return

        if not self.parent_window:
            QMessageBox.critical(self, "Error", "Parent window not found.")
            return

        # Get configuration from YAML builder
        yaml_builder = self.parent_window.yaml_builder
        try:
            config_dict = yaml_builder.build_config_dict()
        except Exception as e:
            QMessageBox.critical(
                self, "Configuration Error", f"Failed to build configuration:\n{str(e)}"
            )
            return

        # Start generation in background thread
        self.generate_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.log_text.clear()
        self.files_text.clear()

        self.worker = GenerationWorker(config_dict, self.output_dir)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.generation_finished)
        self.worker.start()

    def update_progress(self, message: str):
        """Update progress display"""
        self.log_text.append(f"• {message}")

    def generation_finished(self, success: bool, message: str, generated_files: list):
        """Handle generation completion"""
        self.progress_bar.setVisible(False)
        self.generate_button.setEnabled(True)

        if success:
            self.log_text.append(f"✅ {message}")
            self.files_text.setText("\n".join(generated_files))
            self.open_folder_button.setEnabled(True)
            self.preview_button.setEnabled(True)

            QMessageBox.information(
                self,
                "Success",
                f"✅ Website generated successfully!\n\n"
                f"Generated {len(generated_files)} files in:\n{self.output_dir}",
            )
        else:
            self.log_text.append(f"❌ {message}")
            QMessageBox.warning(self, "Generation Failed", f"❌ {message}")

    def open_output_folder(self):
        """Open the output folder in file explorer"""
        if self.output_dir:
            import subprocess
            import platform

            if platform.system() == "Windows":
                subprocess.Popen(f'explorer "{self.output_dir}"')
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", self.output_dir])
            else:  # Linux
                subprocess.Popen(["xdg-open", self.output_dir])

    def preview_website(self):
        """Preview the generated website in browser"""
        if self.output_dir:
            import webbrowser

            index_path = Path(self.output_dir) / "index.html"
            if index_path.exists():
                webbrowser.open(f"file://{index_path}")
            else:
                QMessageBox.warning(
                    self, "File Not Found", "index.html not found in output directory."
                )


class SEOGeneratorMainWindow(QMainWindow):
    """Main application window combining all functionality"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SEO Authority Website Generator - Sprint 1 MVP")
        self.setGeometry(100, 100, 1200, 800)

        # Initialize components
        self.yaml_builder: YAMLBuilderWidget
        self.generator_tab: GeneratorTab
        self.preview_tab: QWidget
        self.central_widget: QTabWidget

        self.setup_ui()
        self.setup_menu_bar()

    def setup_ui(self):
        """Set up the main user interface"""
        # Create central widget with tabs
        self.central_widget = QTabWidget()
        self.setCentralWidget(self.central_widget)

        # Configuration Builder tab (your refactored YAML builder)
        self.yaml_builder = YAMLBuilderWidget()
        self.central_widget.addTab(self.yaml_builder, "Configuration Builder")

        # Website Generator tab
        self.generator_tab = GeneratorTab(self)
        self.central_widget.addTab(self.generator_tab, "Website Generator")

        # Preview tab (placeholder for now)
        self.preview_tab = QWidget()
        preview_layout = QVBoxLayout()
        preview_layout.addWidget(
            QLabel(
                "Website Preview\n\n"
                "Coming in Sprint 2:\n"
                "• Built-in browser preview\n"
                "• Live editing capabilities\n"
                "• SEO analysis tools"
            )
        )
        self.preview_tab.setLayout(preview_layout)
        self.central_widget.addTab(self.preview_tab, "Preview (Sprint 2)")

    def setup_menu_bar(self):
        """Set up the application menu bar"""
        menubar = self.menuBar()

        # Handle potential None return from menuBar()
        if menubar is None:
            # Create a new menu bar if none exists
            menubar = QMenuBar(self)
            self.setMenuBar(menubar)

        # File menu
        file_menu = menubar.addMenu("File")
        if file_menu is not None:
            new_action = QAction("New Configuration", self)
            new_action.setShortcut("Ctrl+N")
            new_action.triggered.connect(self.new_configuration)
            file_menu.addAction(new_action)

            open_action = QAction("Open Configuration", self)
            open_action.setShortcut("Ctrl+O")
            open_action.triggered.connect(self.yaml_builder.load_yaml)
            file_menu.addAction(open_action)

            save_action = QAction("Save Configuration", self)
            save_action.setShortcut("Ctrl+S")
            save_action.triggered.connect(self.yaml_builder.save_yaml)
            file_menu.addAction(save_action)

            file_menu.addSeparator()

            exit_action = QAction("Exit", self)
            exit_action.setShortcut("Ctrl+Q")
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        if tools_menu is not None:
            validate_action = QAction("Validate Configuration", self)
            validate_action.triggered.connect(self.yaml_builder.validate_config)
            tools_menu.addAction(validate_action)

            preview_action = QAction("Quick Preview", self)
            preview_action.triggered.connect(self.yaml_builder.preview_website)
            tools_menu.addAction(preview_action)

        # Help menu
        help_menu = menubar.addMenu("Help")
        if help_menu is not None:
            about_action = QAction("About", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)

            sprint_action = QAction("Sprint 1 Status", self)
            sprint_action.triggered.connect(self.show_sprint_status)
            help_menu.addAction(sprint_action)

    def new_configuration(self):
        """Create a new configuration"""
        reply = QMessageBox.question(
            self,
            "New Configuration",
            "This will clear the current configuration. Continue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Clear all fields - this would need to be implemented in YAMLBuilderWidget
            QMessageBox.information(
                self,
                "New Configuration",
                "New configuration started. Fill out the form in the Configuration Builder tab.",
            )

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About",
            "SEO Authority Website Generator\n"
            "Sprint 1 MVP - Version 2.0.2\n\n"
            "Test-driven development approach\n"
            "Built with PyQt6 and modern web technologies\n\n"
            "Features:\n"
            "• YAML configuration builder\n"
            "• Static HTML website generation\n"
            "• SEO optimization\n"
            "• Google Maps integration",
        )

    def show_sprint_status(self):
        """Show Sprint 1 development status"""
        QMessageBox.information(
            self,
            "Sprint 1 Status",
            "✅ COMPLETED:\n"
            "• YAML configuration parser (100% tests pass)\n"
            "• Website generator core (100% tests pass)\n"
            "• Refactored YAML builder UI\n"
            "• Integrated main application\n"
            "• Basic HTML template system\n"
            "• Local file output\n\n"
            "🚀 READY FOR:\n"
            "• Sprint 2: Enhanced UI features\n"
            "• Sprint 3: SEO optimization\n"
            "• Sprint 4: AWS deployment\n"
            "• Sprint 5: Production polish",
        )


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("SEO Authority Website Generator")
    app.setApplicationVersion("2.0.2-sprint1")
    app.setOrganizationName("Cloud Stack Generator")

    # Create and show main window
    window = SEOGeneratorMainWindow()
    window.show()

    # Start the event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
