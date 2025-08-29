"""
Enhanced Cities Tab for managing rich city page content

This tab provides a comprehensive interface for creating and managing 
city pages with the full Chicago.html structure including:
- City information and Wikipedia content
- SEO content sections (800+ words)
- Places of interest with map embeds
- City-specific FAQ sections
- Image management with attribution

Version: 2.3.0
Author: Cloud Stack Generator Team
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QPushButton, QListWidget, QListWidgetItem, QTextEdit, QLineEdit,
    QLabel, QGroupBox, QScrollArea, QFrame, QTabWidget, QComboBox,
    QMessageBox, QDialog, QDialogButtonBox, QSplitter, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt6.QtGui import QFont

from ..components.base_tab import BaseTab
from ...core.config.models import (
    CityPageConfig, CityImageConfig, PlaceOfInterest, CityFAQItem
)
from typing import Dict, Any, List, Optional


class PlaceOfInterestDialog(QDialog):
    """Dialog for editing places of interest"""
    
    def __init__(self, place: Optional[PlaceOfInterest] = None, parent=None):
        super().__init__(parent)
        self.place = place
        self.setWindowTitle("Edit Place of Interest")
        self.setModal(True)
        self.resize(500, 300)
        self.setup_ui()
        
        if place:
            self.load_place_data(place)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Millennium Park")
        form_layout.addRow("Name*:", self.name_edit)
        
        self.embed_url_edit = QLineEdit()
        self.embed_url_edit.setPlaceholderText("https://www.google.com/maps?q=Place+Name&output=embed")
        form_layout.addRow("Map Embed URL:", self.embed_url_edit)
        
        layout.addLayout(form_layout)
        
        # Help text
        help_label = QLabel(
            "Tip: Get map embed URLs by searching on Google Maps, clicking Share → Embed a map, and copying the src URL."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 11px; margin: 10px 0;")
        layout.addWidget(help_label)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_place_data(self, place: PlaceOfInterest):
        self.name_edit.setText(place.name)
        self.embed_url_edit.setText(place.embed_url)
    
    def get_place_data(self) -> Optional[PlaceOfInterest]:
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Place name is required.")
            return None
        
        return PlaceOfInterest(
            name=self.name_edit.text().strip(),
            embed_url=self.embed_url_edit.text().strip()
        )


class CityFAQDialog(QDialog):
    """Dialog for editing city FAQ items"""
    
    def __init__(self, faq: Optional[CityFAQItem] = None, parent=None):
        super().__init__(parent)
        self.faq = faq
        self.setWindowTitle("Edit FAQ Item")
        self.setModal(True)
        self.resize(600, 400)
        self.setup_ui()
        
        if faq:
            self.load_faq_data(faq)
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Question
        layout.addWidget(QLabel("Question*:"))
        self.question_edit = QLineEdit()
        self.question_edit.setPlaceholderText("e.g., Do you provide services in this city?")
        layout.addWidget(self.question_edit)
        
        # Answer
        layout.addWidget(QLabel("Answer*:"))
        self.answer_edit = QTextEdit()
        self.answer_edit.setPlaceholderText("Provide a detailed answer to the question...")
        self.answer_edit.setMaximumHeight(200)
        layout.addWidget(self.answer_edit)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def load_faq_data(self, faq: CityFAQItem):
        self.question_edit.setText(faq.question)
        self.answer_edit.setPlainText(faq.answer)
    
    def get_faq_data(self) -> Optional[CityFAQItem]:
        if not self.question_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Question is required.")
            return None
        
        if not self.answer_edit.toPlainText().strip():
            QMessageBox.warning(self, "Validation Error", "Answer is required.")
            return None
        
        return CityFAQItem(
            question=self.question_edit.text().strip(),
            answer=self.answer_edit.toPlainText().strip()
        )


class WikipediaWorker(QObject):
    """Worker thread for Wikipedia API calls"""
    
    finished = pyqtSignal(dict)  # Signal emitted when work is done
    error = pyqtSignal(str)      # Signal emitted when error occurs
    
    def __init__(self, city_name: str):
        super().__init__()
        self.city_name = city_name
    
    def run(self):
        """Run the Wikipedia API call in background thread"""
        try:
            from ...core.utils.wikipedia_api import WikipediaAPI
            wiki_api = WikipediaAPI()
            city_info = wiki_api.get_city_image_info(self.city_name)
            self.finished.emit(city_info)
        except Exception as e:
            self.error.emit(str(e))


class EnhancedCitiesTab(BaseTab):
    """Enhanced cities tab for managing rich city page content"""
    
    def __init__(self, parent=None):
        self.city_pages: List[CityPageConfig] = []
        self.current_city_page: Optional[CityPageConfig] = None
        self.worker_thread = None
        self.wikipedia_worker = None
        super().__init__(parent)
    
    def setup_ui(self):
        """Setup the enhanced cities UI"""
        main_layout = QHBoxLayout()
        
        # Left panel - City list
        left_panel = self.create_city_list_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Right panel - City editor
        right_panel = self.create_city_editor_panel()
        main_layout.addWidget(right_panel, 3)
        
        self.setLayout(main_layout)
    
    def create_city_list_panel(self) -> QWidget:
        """Create the city list panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("City Pages")
        header_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(header_label)
        
        # City list
        self.city_list = QListWidget()
        self.city_list.itemClicked.connect(self.on_city_selected)
        layout.addWidget(self.city_list)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        self.add_city_btn = QPushButton("+ Add City")
        self.add_city_btn.clicked.connect(self.add_new_city)
        button_layout.addWidget(self.add_city_btn)
        
        self.remove_city_btn = QPushButton("Remove City")
        self.remove_city_btn.clicked.connect(self.remove_selected_city)
        self.remove_city_btn.setEnabled(False)
        button_layout.addWidget(self.remove_city_btn)
        
        self.duplicate_city_btn = QPushButton("Duplicate City")
        self.duplicate_city_btn.clicked.connect(self.duplicate_selected_city)
        self.duplicate_city_btn.setEnabled(False)
        button_layout.addWidget(self.duplicate_city_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        widget.setLayout(layout)
        widget.setMaximumWidth(250)
        return widget
    
    def create_city_editor_panel(self) -> QWidget:
        """Create the city editor panel"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        self.editor_header = QLabel("Select a city to edit")
        self.editor_header.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.editor_header)
        
        # Scroll area for editor content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Editor content
        self.editor_content = QFrame()
        self.editor_layout = QVBoxLayout()
        self.editor_content.setLayout(self.editor_layout)
        scroll_area.setWidget(self.editor_content)
        
        layout.addWidget(scroll_area)
        
        widget.setLayout(layout)
        return widget
    
    def create_city_editor_form(self, city_page: CityPageConfig):
        """Create the editor form for a city page"""
        # Clear existing layout
        while self.editor_layout.count():
            child = self.editor_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Create tabbed interface
        tab_widget = QTabWidget()
        
        # Basic Info Tab
        basic_tab = self.create_basic_info_tab(city_page)
        tab_widget.addTab(basic_tab, "Basic Info")
        
        # Content Tab
        content_tab = self.create_content_tab(city_page)
        tab_widget.addTab(content_tab, "Content")
        
        # Places Tab
        places_tab = self.create_places_tab(city_page)
        tab_widget.addTab(places_tab, "Places of Interest")
        
        # FAQ Tab
        faq_tab = self.create_faq_tab(city_page)
        tab_widget.addTab(faq_tab, "FAQ")
        
        # Image Tab
        image_tab = self.create_image_tab(city_page)
        tab_widget.addTab(image_tab, "Image")
        
        self.editor_layout.addWidget(tab_widget)
        
        # Save button
        save_btn = QPushButton("Save Changes")
        save_btn.clicked.connect(self.save_current_city)
        save_btn.setStyleSheet("font-weight: bold; padding: 8px;")
        self.editor_layout.addWidget(save_btn)
    
    def create_basic_info_tab(self, city_page: CityPageConfig) -> QWidget:
        """Create basic info tab"""
        widget = QWidget()
        layout = QFormLayout()
        
        self.city_name_edit = QLineEdit(city_page.city_name)
        layout.addRow("City Name*:", self.city_name_edit)
        
        self.state_edit = QLineEdit(city_page.state)
        layout.addRow("State:", self.state_edit)
        
        self.slug_edit = QLineEdit(city_page.slug)
        layout.addRow("URL Slug:", self.slug_edit)
        
        self.title_edit = QLineEdit(city_page.title)
        layout.addRow("Page Title:", self.title_edit)
        
        self.meta_description_edit = QTextEdit(city_page.meta_description)
        self.meta_description_edit.setMaximumHeight(80)
        layout.addRow("Meta Description:", self.meta_description_edit)
        
        self.primary_keyword_edit = QLineEdit(city_page.primary_keyword)
        layout.addRow("Primary Keyword:", self.primary_keyword_edit)
        
        self.hero_title_edit = QLineEdit(city_page.hero_title)
        layout.addRow("Hero Title:", self.hero_title_edit)
        
        self.service_area_note_edit = QLineEdit(city_page.service_area_note)
        layout.addRow("Service Area Note:", self.service_area_note_edit)
        
        widget.setLayout(layout)
        return widget
    
    def create_content_tab(self, city_page: CityPageConfig) -> QWidget:
        """Create content tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # About City
        layout.addWidget(QLabel("About City:"))
        self.about_city_edit = QTextEdit(city_page.about_city)
        self.about_city_edit.setMaximumHeight(120)
        layout.addWidget(self.about_city_edit)
        
        # SEO Content Title
        layout.addWidget(QLabel("SEO Content Title:"))
        self.seo_title_edit = QLineEdit(city_page.seo_content_title)
        layout.addWidget(self.seo_title_edit)
        
        # SEO Content Body
        layout.addWidget(QLabel("SEO Content Body (800+ words):"))
        self.seo_content_edit = QTextEdit(city_page.seo_content_body)
        self.seo_content_edit.setMinimumHeight(300)
        layout.addWidget(self.seo_content_edit)
        
        # Word count label
        self.word_count_label = QLabel()
        self.update_word_count()
        self.seo_content_edit.textChanged.connect(self.update_word_count)
        layout.addWidget(self.word_count_label)
        
        widget.setLayout(layout)
        return widget
    
    def create_places_tab(self, city_page: CityPageConfig) -> QWidget:
        """Create places of interest tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("Places of Interest:"))
        header_layout.addStretch()
        
        add_place_btn = QPushButton("+ Add Place")
        add_place_btn.clicked.connect(self.add_place_of_interest)
        header_layout.addWidget(add_place_btn)
        
        layout.addLayout(header_layout)
        
        # Places list
        self.places_list = QListWidget()
        self.places_list.itemDoubleClicked.connect(self.edit_place_of_interest)
        layout.addWidget(self.places_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        edit_place_btn = QPushButton("Edit")
        edit_place_btn.clicked.connect(self.edit_place_of_interest)
        button_layout.addWidget(edit_place_btn)
        
        remove_place_btn = QPushButton("Remove")
        remove_place_btn.clicked.connect(self.remove_place_of_interest)
        button_layout.addWidget(remove_place_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Load places
        self.load_places_of_interest(city_page.places_of_interest)
        
        widget.setLayout(layout)
        return widget
    
    def create_faq_tab(self, city_page: CityPageConfig) -> QWidget:
        """Create FAQ tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Header
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("City FAQ:"))
        header_layout.addStretch()
        
        add_faq_btn = QPushButton("+ Add FAQ")
        add_faq_btn.clicked.connect(self.add_faq_item)
        header_layout.addWidget(add_faq_btn)
        
        layout.addLayout(header_layout)
        
        # FAQ list
        self.faq_list = QListWidget()
        self.faq_list.itemDoubleClicked.connect(self.edit_faq_item)
        layout.addWidget(self.faq_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        edit_faq_btn = QPushButton("Edit")
        edit_faq_btn.clicked.connect(self.edit_faq_item)
        button_layout.addWidget(edit_faq_btn)
        
        remove_faq_btn = QPushButton("Remove")
        remove_faq_btn.clicked.connect(self.remove_faq_item)
        button_layout.addWidget(remove_faq_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Load FAQ items
        self.load_faq_items(city_page.city_faq)
        
        widget.setLayout(layout)
        return widget
    
    def create_image_tab(self, city_page: CityPageConfig) -> QWidget:
        """Create image tab with Wikipedia embed generation"""
        widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Wikipedia Embed Generation Section
        wiki_group = QGroupBox("Wikipedia Image Generation")
        wiki_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "Generate complete Wikipedia image embed code for this city. "
            "This will automatically populate the image fields below."
        )
        instructions.setFont(QFont("Arial", 10))
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        wiki_layout.addWidget(instructions)
        
        # Generate button
        generate_btn_layout = QHBoxLayout()
        self.generate_wiki_btn = QPushButton("Generate Wikipedia Embed")
        self.generate_wiki_btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.generate_wiki_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.generate_wiki_btn.clicked.connect(self._generate_wikipedia_embed_for_city)
        generate_btn_layout.addWidget(self.generate_wiki_btn)
        generate_btn_layout.addStretch()
        wiki_layout.addLayout(generate_btn_layout)
        
        # Embed code preview
        embed_label = QLabel("Generated Embed Code:")
        embed_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        wiki_layout.addWidget(embed_label)
        
        self.embed_preview = QTextEdit()
        self.embed_preview.setFont(QFont("Courier", 9))
        self.embed_preview.setMaximumHeight(100)
        self.embed_preview.setMinimumHeight(100)
        self.embed_preview.setReadOnly(True)
        self.embed_preview.setPlaceholderText("Generated embed code will appear here...")
        wiki_layout.addWidget(self.embed_preview)
        
        wiki_group.setLayout(wiki_layout)
        main_layout.addWidget(wiki_group)
        
        # Traditional Image Fields Section
        fields_group = QGroupBox("Image Details")
        layout = QFormLayout()
        
        self.image_url_edit = QLineEdit(city_page.city_image.image_url)
        layout.addRow("Image URL:", self.image_url_edit)
        
        self.image_alt_edit = QLineEdit(city_page.city_image.alt_text)
        layout.addRow("Alt Text:", self.image_alt_edit)
        
        self.image_caption_edit = QLineEdit(city_page.city_image.caption)
        layout.addRow("Caption:", self.image_caption_edit)
        
        self.image_credit_edit = QLineEdit(city_page.city_image.credit)
        layout.addRow("Credit:", self.image_credit_edit)
        
        self.image_source_edit = QLineEdit(city_page.city_image.source)
        layout.addRow("Source:", self.image_source_edit)
        
        # Add embed code field
        self.embed_code_edit = QTextEdit()
        self.embed_code_edit.setFont(QFont("Courier", 9))
        self.embed_code_edit.setMaximumHeight(120)
        self.embed_code_edit.setPlaceholderText("Complete HTML embed code...")
        # Load existing embed code if available
        if hasattr(city_page.city_image, 'embed_code'):
            self.embed_code_edit.setPlainText(city_page.city_image.embed_code)
        layout.addRow("Embed Code:", self.embed_code_edit)
        
        fields_group.setLayout(layout)
        main_layout.addWidget(fields_group)
        
        widget.setLayout(main_layout)
        return widget
    
    def _generate_wikipedia_embed_for_city(self):
        """Generate Wikipedia embed code for current city using background thread"""
        if not self.current_city_page:
            QMessageBox.warning(self, "No City Selected", "Please select a city to generate Wikipedia embed.")
            return
            
        city_name = self.current_city_page.city_name
        if not city_name:
            QMessageBox.warning(self, "No City Name", "City name is required to generate Wikipedia embed.")
            return
        
        # Disable button and show loading state
        self.generate_wiki_btn.setEnabled(False)
        self.generate_wiki_btn.setText("Generating...")
        self.embed_preview.setPlainText("Loading Wikipedia data...")
        
        # Clean up any existing worker thread
        self._cleanup_worker_thread()
        
        # Create new worker thread
        self.worker_thread = QThread()
        self.wikipedia_worker = WikipediaWorker(city_name)
        self.wikipedia_worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker_thread.started.connect(self.wikipedia_worker.run)
        self.wikipedia_worker.finished.connect(self._on_wikipedia_success)
        self.wikipedia_worker.error.connect(self._on_wikipedia_error)
        self.wikipedia_worker.finished.connect(self.worker_thread.quit)
        self.wikipedia_worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self._cleanup_worker_thread)
        
        # Start the worker thread
        self.worker_thread.start()
    
    def _on_wikipedia_success(self, city_info: dict):
        """Handle successful Wikipedia API response"""
        try:
            # Update the embed code preview
            self.embed_preview.setPlainText(city_info["embed_code"])
            
            # Auto-populate the traditional fields
            self.image_url_edit.setText(city_info["image_url"])
            self.image_alt_edit.setText(city_info["alt_text"])
            self.image_caption_edit.setText(city_info["attribution"])
            self.image_credit_edit.setText(city_info["attribution"])
            self.image_source_edit.setText(city_info["source_url"])
            
            # Set the full embed code
            if hasattr(self, 'embed_code_edit'):
                self.embed_code_edit.setPlainText(city_info["embed_code"])
            
            QMessageBox.information(
                self, "Wikipedia Embed Generated", 
                f"Successfully generated Wikipedia embed for {city_info['city_name']}.\n\n"
                f"The embed code has been generated and the image fields have been populated automatically."
            )
            
        except Exception as e:
            QMessageBox.critical(
                self, "Processing Error", 
                f"Error processing Wikipedia data: {str(e)}"
            )
        finally:
            self._reset_generate_button()
    
    def _on_wikipedia_error(self, error_message: str):
        """Handle Wikipedia API error"""
        self.embed_preview.setPlainText("Failed to load Wikipedia data.")
        QMessageBox.critical(
            self, "Wikipedia Error", 
            f"Failed to generate Wikipedia embed:\n\n{error_message}"
        )
        self._reset_generate_button()
    
    def _reset_generate_button(self):
        """Reset the generate button to normal state"""
        self.generate_wiki_btn.setEnabled(True)
        self.generate_wiki_btn.setText("Generate Wikipedia Embed")
    
    def _cleanup_worker_thread(self):
        """Clean up worker thread and worker object"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            self.worker_thread.wait()
        
        if self.wikipedia_worker:
            self.wikipedia_worker.deleteLater()
            self.wikipedia_worker = None
        
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None
    
    def update_word_count(self):
        """Update word count for SEO content"""
        text = self.seo_content_edit.toPlainText()
        word_count = len(text.split()) if text.strip() else 0
        
        color = "green" if word_count >= 800 else "orange" if word_count >= 400 else "red"
        self.word_count_label.setText(f"<span style='color: {color}'>Word count: {word_count}/800+</span>")
    
    def add_new_city(self):
        """Add a new city page"""
        from PyQt6.QtWidgets import QInputDialog
        city_name, ok = QInputDialog.getText(self, "Add New City", "Enter city name:")
        
        if ok and city_name.strip():
            # Check for duplicates
            if any(cp.city_name.lower() == city_name.lower() for cp in self.city_pages):
                QMessageBox.warning(self, "Duplicate City", f"A city page for '{city_name}' already exists.")
                return
            
            # Create new city page
            city_page = CityPageConfig(city_name=city_name.strip())
            self.city_pages.append(city_page)
            self.refresh_city_list()
            
            # Select the new city
            self.city_list.setCurrentRow(len(self.city_pages) - 1)
            self.on_city_selected()
            
            self._emit_config_changed()
    
    def remove_selected_city(self):
        """Remove the selected city"""
        current_row = self.city_list.currentRow()
        if current_row >= 0:
            city_page = self.city_pages[current_row]
            
            reply = QMessageBox.question(
                self, "Remove City",
                f"Are you sure you want to remove '{city_page.city_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                del self.city_pages[current_row]
                self.refresh_city_list()
                self.clear_editor()
                self._emit_config_changed()
    
    def duplicate_selected_city(self):
        """Duplicate the selected city"""
        current_row = self.city_list.currentRow()
        if current_row >= 0:
            original_city = self.city_pages[current_row]
            
            # Create copy with modified name
            duplicate_city = CityPageConfig(
                city_name=f"{original_city.city_name} Copy",
                state=original_city.state,
                title=f"{original_city.title} Copy",
                meta_description=original_city.meta_description,
                primary_keyword=original_city.primary_keyword,
                secondary_keywords=original_city.secondary_keywords.copy(),
                hero_title=original_city.hero_title,
                breadcrumbs=original_city.breadcrumbs.copy(),
                about_city=original_city.about_city,
                city_image=CityImageConfig(
                    image_url=original_city.city_image.image_url,
                    alt_text=original_city.city_image.alt_text,
                    caption=original_city.city_image.caption,
                    credit=original_city.city_image.credit,
                    source=original_city.city_image.source
                ),
                seo_content_title=original_city.seo_content_title,
                seo_content_body=original_city.seo_content_body,
                places_of_interest=[
                    PlaceOfInterest(name=poi.name, embed_url=poi.embed_url)
                    for poi in original_city.places_of_interest
                ],
                city_faq=[
                    CityFAQItem(question=faq.question, answer=faq.answer)
                    for faq in original_city.city_faq
                ],
                featured_products=original_city.featured_products.copy(),
                city_map_embed=original_city.city_map_embed,
                service_area_note=original_city.service_area_note
            )
            
            self.city_pages.append(duplicate_city)
            self.refresh_city_list()
            self._emit_config_changed()
    
    def on_city_selected(self):
        """Handle city selection"""
        current_row = self.city_list.currentRow()
        if current_row >= 0:
            self.current_city_page = self.city_pages[current_row]
            self.editor_header.setText(f"Editing: {self.current_city_page.city_name}")
            self.create_city_editor_form(self.current_city_page)
            
            # Enable buttons
            self.remove_city_btn.setEnabled(True)
            self.duplicate_city_btn.setEnabled(True)
        else:
            self.clear_editor()
    
    def clear_editor(self):
        """Clear the editor panel"""
        self.current_city_page = None
        self.editor_header.setText("Select a city to edit")
        
        # Clear layout
        while self.editor_layout.count():
            child = self.editor_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Disable buttons
        self.remove_city_btn.setEnabled(False)
        self.duplicate_city_btn.setEnabled(False)
    
    def save_current_city(self):
        """Save the current city page"""
        if not self.current_city_page:
            return
        
        try:
            # Update basic info
            self.current_city_page.city_name = self.city_name_edit.text().strip()
            self.current_city_page.state = self.state_edit.text().strip()
            self.current_city_page.slug = self.slug_edit.text().strip()
            self.current_city_page.title = self.title_edit.text().strip()
            self.current_city_page.meta_description = self.meta_description_edit.toPlainText().strip()
            self.current_city_page.primary_keyword = self.primary_keyword_edit.text().strip()
            self.current_city_page.hero_title = self.hero_title_edit.text().strip()
            self.current_city_page.service_area_note = self.service_area_note_edit.text().strip()
            
            # Update content
            self.current_city_page.about_city = self.about_city_edit.toPlainText().strip()
            self.current_city_page.seo_content_title = self.seo_title_edit.text().strip()
            self.current_city_page.seo_content_body = self.seo_content_edit.toPlainText().strip()
            
            # Update image
            self.current_city_page.city_image.image_url = self.image_url_edit.text().strip()
            self.current_city_page.city_image.alt_text = self.image_alt_edit.text().strip()
            self.current_city_page.city_image.caption = self.image_caption_edit.text().strip()
            self.current_city_page.city_image.credit = self.image_credit_edit.text().strip()
            self.current_city_page.city_image.source = self.image_source_edit.text().strip()
            
            # Store embed code if available
            if hasattr(self, 'embed_code_edit'):
                embed_code = self.embed_code_edit.toPlainText().strip()
                self.current_city_page.city_image.embed_code = embed_code
            
            # Refresh the list display
            self.refresh_city_list()
            self._emit_config_changed()
            
            QMessageBox.information(self, "Success", f"City page '{self.current_city_page.city_name}' saved successfully.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save city page: {str(e)}")
    
    def refresh_city_list(self):
        """Refresh the city list display"""
        self.city_list.clear()
        for city_page in self.city_pages:
            display_text = f"{city_page.city_name}"
            if city_page.state:
                display_text += f", {city_page.state}"
            
            item = QListWidgetItem(display_text)
            self.city_list.addItem(item)
    
    def load_places_of_interest(self, places: List[PlaceOfInterest]):
        """Load places of interest into the list"""
        self.places_list.clear()
        for place in places:
            item = QListWidgetItem(place.name)
            item.setData(Qt.ItemDataRole.UserRole, place)
            self.places_list.addItem(item)
    
    def load_faq_items(self, faq_items: List[CityFAQItem]):
        """Load FAQ items into the list"""
        self.faq_list.clear()
        for faq in faq_items:
            item = QListWidgetItem(faq.question)
            item.setData(Qt.ItemDataRole.UserRole, faq)
            self.faq_list.addItem(item)
    
    def add_place_of_interest(self):
        """Add a new place of interest"""
        dialog = PlaceOfInterestDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            place = dialog.get_place_data()
            if place and self.current_city_page:
                self.current_city_page.places_of_interest.append(place)
                self.load_places_of_interest(self.current_city_page.places_of_interest)
                self._emit_config_changed()
    
    def edit_place_of_interest(self):
        """Edit selected place of interest"""
        current_item = self.places_list.currentItem()
        if current_item and self.current_city_page:
            place = current_item.data(Qt.ItemDataRole.UserRole)
            dialog = PlaceOfInterestDialog(place, parent=self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_place = dialog.get_place_data()
                if updated_place:
                    # Find and update the place
                    for i, existing_place in enumerate(self.current_city_page.places_of_interest):
                        if existing_place == place:
                            self.current_city_page.places_of_interest[i] = updated_place
                            break
                    
                    self.load_places_of_interest(self.current_city_page.places_of_interest)
                    self._emit_config_changed()
    
    def remove_place_of_interest(self):
        """Remove selected place of interest"""
        current_item = self.places_list.currentItem()
        if current_item and self.current_city_page:
            place = current_item.data(Qt.ItemDataRole.UserRole)
            
            reply = QMessageBox.question(
                self, "Remove Place",
                f"Are you sure you want to remove '{place.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.current_city_page.places_of_interest.remove(place)
                self.load_places_of_interest(self.current_city_page.places_of_interest)
                self._emit_config_changed()
    
    def add_faq_item(self):
        """Add a new FAQ item"""
        dialog = CityFAQDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            faq = dialog.get_faq_data()
            if faq and self.current_city_page:
                self.current_city_page.city_faq.append(faq)
                self.load_faq_items(self.current_city_page.city_faq)
                self._emit_config_changed()
    
    def edit_faq_item(self):
        """Edit selected FAQ item"""
        current_item = self.faq_list.currentItem()
        if current_item and self.current_city_page:
            faq = current_item.data(Qt.ItemDataRole.UserRole)
            dialog = CityFAQDialog(faq, parent=self)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                updated_faq = dialog.get_faq_data()
                if updated_faq:
                    # Find and update the FAQ
                    for i, existing_faq in enumerate(self.current_city_page.city_faq):
                        if existing_faq == faq:
                            self.current_city_page.city_faq[i] = updated_faq
                            break
                    
                    self.load_faq_items(self.current_city_page.city_faq)
                    self._emit_config_changed()
    
    def remove_faq_item(self):
        """Remove selected FAQ item"""
        current_item = self.faq_list.currentItem()
        if current_item and self.current_city_page:
            faq = current_item.data(Qt.ItemDataRole.UserRole)
            
            reply = QMessageBox.question(
                self, "Remove FAQ",
                f"Are you sure you want to remove this FAQ item?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.current_city_page.city_faq.remove(faq)
                self.load_faq_items(self.current_city_page.city_faq)
                self._emit_config_changed()
    
    def get_config_data(self) -> Dict[str, Any]:
        """Get city pages configuration data - BOTH FORMATS for compatibility"""
        # Generate city_pages data (enhanced format)
        city_pages_data = [
            {
                "city_name": cp.city_name,
                "state": cp.state,
                "slug": cp.slug,
                "title": cp.title,
                "meta_description": cp.meta_description,
                "primary_keyword": cp.primary_keyword,
                "secondary_keywords": cp.secondary_keywords,
                "hero_title": cp.hero_title,
                "breadcrumbs": cp.breadcrumbs,
                "about_city": cp.about_city,
                "city_image": {
                    "image_url": cp.city_image.image_url,
                    "alt_text": cp.city_image.alt_text,
                    "caption": cp.city_image.caption,
                    "credit": cp.city_image.credit,
                    "source": cp.city_image.source,
                    "embed_code": getattr(cp.city_image, 'embed_code', ''),
                },
                "seo_content_title": cp.seo_content_title,
                "seo_content_body": cp.seo_content_body,
                "places_of_interest": [
                    {"name": poi.name, "embed_url": poi.embed_url}
                    for poi in cp.places_of_interest
                ],
                "city_faq": [
                    {"question": faq.question, "answer": faq.answer}
                    for faq in cp.city_faq
                ],
                "featured_products": cp.featured_products,
                "city_map_embed": cp.city_map_embed,
                "service_area_note": cp.service_area_note,
            }
            for cp in self.city_pages
        ]
        
        # Generate target_cities data (legacy format for backward compatibility)
        target_cities = []
        for cp in self.city_pages:
            if cp.state:
                target_cities.append(f"{cp.city_name}, {cp.state}")
            else:
                target_cities.append(cp.city_name)
        
        return {
            "city_pages": city_pages_data,    # Enhanced format for Sprint 2.5+
            "target_cities": target_cities,   # Legacy format for backward compatibility
        }
    
    def set_config_data(self, data: Dict[str, Any]):
        """Set city pages configuration data"""
        self.city_pages.clear()
        
        city_pages_data = data.get("city_pages", [])
        for cp_data in city_pages_data:
            city_page = CityPageConfig(
                city_name=cp_data.get("city_name", ""),
                state=cp_data.get("state", ""),
                slug=cp_data.get("slug", ""),
                title=cp_data.get("title", ""),
                meta_description=cp_data.get("meta_description", ""),
                primary_keyword=cp_data.get("primary_keyword", ""),
                secondary_keywords=cp_data.get("secondary_keywords", []),
                hero_title=cp_data.get("hero_title", ""),
                breadcrumbs=cp_data.get("breadcrumbs", []),
                about_city=cp_data.get("about_city", ""),
                seo_content_title=cp_data.get("seo_content_title", ""),
                seo_content_body=cp_data.get("seo_content_body", ""),
                featured_products=cp_data.get("featured_products", []),
                city_map_embed=cp_data.get("city_map_embed", ""),
                service_area_note=cp_data.get("service_area_note", ""),
            )
            
            # Load city image
            image_data = cp_data.get("city_image", {})
            city_page.city_image = CityImageConfig(
                image_url=image_data.get("image_url", ""),
                alt_text=image_data.get("alt_text", ""),
                caption=image_data.get("caption", ""),
                credit=image_data.get("credit", ""),
                source=image_data.get("source", "Wikipedia"),
                embed_code=image_data.get("embed_code", ""),
            )
            
            # Load places of interest
            for poi_data in cp_data.get("places_of_interest", []):
                city_page.places_of_interest.append(
                    PlaceOfInterest(
                        name=poi_data.get("name", ""),
                        embed_url=poi_data.get("embed_url", "")
                    )
                )
            
            # Load FAQ items
            for faq_data in cp_data.get("city_faq", []):
                city_page.city_faq.append(
                    CityFAQItem(
                        question=faq_data.get("question", ""),
                        answer=faq_data.get("answer", "")
                    )
                )
            
            self.city_pages.append(city_page)
        
        self.refresh_city_list()
    
    def validate_data(self) -> tuple[bool, list[str]]:
        """Validate city pages data"""
        errors = []
        
        for i, city_page in enumerate(self.city_pages):
            if not city_page.city_name:
                errors.append(f"City page {i+1}: City name is required")
            
            # Check for duplicate city names
            duplicate_cities = [cp for cp in self.city_pages if cp.city_name.lower() == city_page.city_name.lower()]
            if len(duplicate_cities) > 1:
                errors.append(f"Duplicate city name: '{city_page.city_name}'")
        
        return len(errors) == 0, errors
    
    def clear_data(self):
        """Clear all city pages data"""
        self.city_pages.clear()
        self.refresh_city_list()
        self.clear_editor()
    
    def __del__(self):
        """Cleanup when tab is destroyed"""
        self._cleanup_worker_thread()