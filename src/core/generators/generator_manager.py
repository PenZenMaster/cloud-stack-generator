# src/core/generators/generator_manager.py
"""
Generator Manager - Integration with Enhanced Main Window
Sprint 2 Week 2 - Days 7-8 Implementation

Manages website generation process and integrates with the UI
for progress tracking and user feedback.
"""

from typing import Optional, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from pathlib import Path
import traceback

from .page_generator import PageGenerator, GenerationResult
from ..config.models import ClientConfig


class GenerationWorker(QThread):
    """Worker thread for website generation to avoid UI blocking"""

    progress_updated = pyqtSignal(int, int, str)  # current, total, message
    generation_completed = pyqtSignal(object)  # GenerationResult

    def __init__(self, config: ClientConfig, output_dir: str = "output"):
        super().__init__()
        self.config = config
        self.output_dir = output_dir
        self.page_generator = PageGenerator(output_base_dir=output_dir)

    def run(self):
        """Run the generation process in background thread"""
        try:
            result = self.page_generator.generate_complete_website(
                self.config, progress_callback=self._emit_progress
            )
            self.generation_completed.emit(result)
        except Exception as e:
            # Create error result
            result = GenerationResult()
            result.add_error(f"Critical generation error: {str(e)}")
            result.add_error(f"Stack trace: {traceback.format_exc()}")
            self.generation_completed.emit(result)

    def _emit_progress(self, current: int, total: int, message: str):
        """Emit progress signal"""
        self.progress_updated.emit(current, total, message)


class GeneratorManager(QObject):
    """Manages website generation and UI integration"""

    # Signals for UI integration
    generation_started = pyqtSignal()
    generation_progress = pyqtSignal(int, int, str)  # current, total, message
    generation_completed = pyqtSignal(object)  # GenerationResult
    generation_error = pyqtSignal(str)  # error message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_worker = None
        self.last_result = None

    def generate_website(
        self, config: ClientConfig, output_dir: str = "output"
    ) -> bool:
        """Start website generation process"""
        # Check if generation is already in progress
        if self.current_worker and self.current_worker.isRunning():
            self.generation_error.emit("Website generation is already in progress")
            return False

        # Validate configuration
        validation_errors = self._validate_config(config)
        if validation_errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                validation_errors
            )
            self.generation_error.emit(error_msg)
            return False

        try:
            # Create and start worker thread
            self.current_worker = GenerationWorker(config, output_dir)
            self.current_worker.progress_updated.connect(self.generation_progress)
            self.current_worker.generation_completed.connect(
                self._on_generation_completed
            )

            self.generation_started.emit()
            self.current_worker.start()
            return True

        except Exception as e:
            self.generation_error.emit(f"Failed to start generation: {str(e)}")
            return False

    def cancel_generation(self):
        """Cancel current generation if running"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait(3000)  # Wait up to 3 seconds
            self.generation_error.emit("Generation cancelled by user")

    def _validate_config(self, config: ClientConfig) -> list[str]:
        """Validate configuration for website generation"""
        errors = []

        # Business information validation
        if not config.business.business_name.strip():
            errors.append("Business name is required")

        if not config.business.domain.strip():
            errors.append("Business website domain is required")

        if not config.business.industry.strip():
            errors.append("Business industry/category is required")

        # Contact information validation
        if not config.contact.phone.strip() and not config.contact.email.strip():
            errors.append("At least phone number or email is required")

        # Content validation
        if not config.services and not config.products:
            errors.append("At least one service or product should be defined")

        # Branding validation
        if not config.branding.primary_color.strip():
            errors.append("Primary brand color is required")

        return errors

    def _on_generation_completed(self, result: GenerationResult):
        """Handle generation completion"""
        self.last_result = result
        self.generation_completed.emit(result)

        # Clean up worker
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None

    def get_last_result(self) -> Optional[GenerationResult]:
        """Get the last generation result"""
        return self.last_result

    def open_generated_website(self) -> bool:
        """Open the last generated website in browser"""
        if self.last_result and self.last_result.success:
            page_generator = PageGenerator()
            return page_generator.open_generated_website(self.last_result)
        return False

    def get_generation_summary(self) -> str:
        """Get formatted summary of last generation"""
        if self.last_result:
            page_generator = PageGenerator()
            return page_generator.get_generation_summary(self.last_result)
        return "No generation has been performed yet."
