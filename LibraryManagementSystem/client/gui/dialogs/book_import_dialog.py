"""
Book import dialog for the Library Management System client.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QComboBox, QPushButton, QDialogButtonBox,
    QFileDialog, QMessageBox, QProgressBar, QTextEdit, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
import os
import json
from utils.web_scraping.book_scraper import BookScraper
from utils.logger import get_logger

logger = get_logger(__name__)

class ScraperWorker(QThread):
    """Worker thread for book scraping operations."""
    
    progress_updated = pyqtSignal(str)
    operation_complete = pyqtSignal(bool, list)
    
    def __init__(self, operation, params):
        """
        Initialize the scraper worker.
        
        Args:
            operation (str): Operation to perform ('search', 'import').
            params (dict): Parameters for the operation.
        """
        super().__init__()
        self.operation = operation
        self.params = params
        self.scraper = BookScraper()
    
    def run(self):
        """Run the worker thread."""
        try:
            if self.operation == 'search':
                query = self.params.get('query')
                limit = self.params.get('limit', 10)
                sources = self.params.get('sources', ['openlibrary', 'google'])
                
                self.progress_updated.emit(f"Searching for '{query}' in {', '.join(sources)}...")
                books = self.scraper.search_books(query, limit, sources)
                
                self.progress_updated.emit(f"Found {len(books)} books.")
                self.operation_complete.emit(True, books)
            
            elif self.operation == 'import':
                file_path = self.params.get('file_path')
                file_type = self.params.get('file_type', 'json')
                
                self.progress_updated.emit(f"Importing books from {file_path}...")
                
                if file_type.lower() == 'json':
                    books = self.scraper.import_from_json(file_path)
                elif file_type.lower() == 'csv':
                    books = self.scraper.import_from_csv(file_path)
                else:
                    self.progress_updated.emit(f"Unsupported file type: {file_type}")
                    self.operation_complete.emit(False, [])
                    return
                
                self.progress_updated.emit(f"Imported {len(books)} books.")
                self.operation_complete.emit(True, books)
        
        except Exception as e:
            logger.error(f"Error in scraper worker: {e}")
            self.progress_updated.emit(f"Error: {str(e)}")
            self.operation_complete.emit(False, [])

class BookImportDialog(QDialog):
    """Dialog for importing books from external sources."""
    
    books_imported = pyqtSignal(list)
    
    def __init__(self, parent=None):
        """
        Initialize the book import dialog.
        
        Args:
            parent: The parent widget.
        """
        super().__init__(parent)
        
        self.books = []
        self.worker = None
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle('Import Books')
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create tabs layout
        self.tabs_layout = QVBoxLayout()
        
        # Create search form
        search_form = QFormLayout()
        
        # Add search query field
        self.query_input = QLineEdit()
        search_form.addRow('Search Query:', self.query_input)
        
        # Add limit field
        self.limit_combo = QComboBox()
        self.limit_combo.addItems(['5', '10', '20', '50', '100'])
        self.limit_combo.setCurrentIndex(1)  # Default to 10
        search_form.addRow('Results Limit:', self.limit_combo)
        
        # Add sources field
        sources_layout = QHBoxLayout()
        self.openlibrary_check = QCheckBox('OpenLibrary')
        self.openlibrary_check.setChecked(True)
        self.google_check = QCheckBox('Google Books')
        self.google_check.setChecked(True)
        sources_layout.addWidget(self.openlibrary_check)
        sources_layout.addWidget(self.google_check)
        search_form.addRow('Sources:', sources_layout)
        
        # Add search button
        self.search_button = QPushButton('Search')
        self.search_button.clicked.connect(self.search_books)
        search_form.addRow('', self.search_button)
        
        self.tabs_layout.addLayout(search_form)
        
        # Add separator
        separator = QLabel()
        separator.setFrameShape(QLabel.HLine)
        separator.setFrameShadow(QLabel.Sunken)
        self.tabs_layout.addWidget(separator)
        
        # Create import form
        import_form = QFormLayout()
        
        # Add file path field
        file_path_layout = QHBoxLayout()
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.browse_file)
        file_path_layout.addWidget(self.file_path_input)
        file_path_layout.addWidget(self.browse_button)
        import_form.addRow('File Path:', file_path_layout)
        
        # Add file type field
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItems(['JSON', 'CSV'])
        import_form.addRow('File Type:', self.file_type_combo)
        
        # Add import button
        self.import_button = QPushButton('Import')
        self.import_button.clicked.connect(self.import_books)
        import_form.addRow('', self.import_button)
        
        self.tabs_layout.addLayout(import_form)
        
        # Add progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        
        # Add log area
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMinimumHeight(150)
        
        # Add results count
        self.results_label = QLabel('No results')
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add all widgets to main layout
        layout.addLayout(self.tabs_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.log_area)
        layout.addWidget(self.results_label)
        layout.addWidget(button_box)
    
    def search_books(self):
        """Search for books."""
        # Get search parameters
        query = self.query_input.text().strip()
        
        if not query:
            QMessageBox.warning(self, 'Warning', 'Please enter a search query.')
            return
        
        # Get limit
        limit = int(self.limit_combo.currentText())
        
        # Get sources
        sources = []
        if self.openlibrary_check.isChecked():
            sources.append('openlibrary')
        if self.google_check.isChecked():
            sources.append('google')
        
        if not sources:
            QMessageBox.warning(self, 'Warning', 'Please select at least one source.')
            return
        
        # Disable UI elements
        self.search_button.setEnabled(False)
        self.import_button.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.show()
        
        # Clear log area
        self.log_area.clear()
        
        # Create worker thread
        self.worker = ScraperWorker('search', {
            'query': query,
            'limit': limit,
            'sources': sources
        })
        
        # Connect signals
        self.worker.progress_updated.connect(self.update_log)
        self.worker.operation_complete.connect(self.handle_search_complete)
        
        # Start worker
        self.worker.start()
    
    def import_books(self):
        """Import books from file."""
        # Get file path
        file_path = self.file_path_input.text()
        
        if not file_path or not os.path.exists(file_path):
            QMessageBox.warning(self, 'Warning', 'Please select a valid file.')
            return
        
        # Get file type
        file_type = self.file_type_combo.currentText().lower()
        
        # Disable UI elements
        self.search_button.setEnabled(False)
        self.import_button.setEnabled(False)
        
        # Show progress bar
        self.progress_bar.show()
        
        # Clear log area
        self.log_area.clear()
        
        # Create worker thread
        self.worker = ScraperWorker('import', {
            'file_path': file_path,
            'file_type': file_type
        })
        
        # Connect signals
        self.worker.progress_updated.connect(self.update_log)
        self.worker.operation_complete.connect(self.handle_import_complete)
        
        # Start worker
        self.worker.start()
    
    def browse_file(self):
        """Browse for a file."""
        file_type = self.file_type_combo.currentText().lower()
        file_filter = 'JSON Files (*.json)' if file_type == 'json' else 'CSV Files (*.csv)'
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            'Select File',
            '',
            file_filter
        )
        
        if file_path:
            self.file_path_input.setText(file_path)
    
    def update_log(self, message):
        """
        Update the log area.
        
        Args:
            message (str): Message to add to the log.
        """
        self.log_area.append(message)
    
    def handle_search_complete(self, success, books):
        """
        Handle search completion.
        
        Args:
            success (bool): Whether the search was successful.
            books (list): List of book dictionaries.
        """
        # Hide progress bar
        self.progress_bar.hide()
        
        # Enable UI elements
        self.search_button.setEnabled(True)
        self.import_button.setEnabled(True)
        
        if success:
            self.books = books
            self.results_label.setText(f"Found {len(books)} books")
            
            # Show sample of books
            if books:
                self.update_log("\nSample of books found:")
                for i, book in enumerate(books[:3]):
                    self.update_log(f"\n{i+1}. {book.get('title')} by {book.get('author')}")
                
                if len(books) > 3:
                    self.update_log(f"\n... and {len(books) - 3} more")
        else:
            self.books = []
            self.results_label.setText("Search failed")
    
    def handle_import_complete(self, success, books):
        """
        Handle import completion.
        
        Args:
            success (bool): Whether the import was successful.
            books (list): List of book dictionaries.
        """
        # Hide progress bar
        self.progress_bar.hide()
        
        # Enable UI elements
        self.search_button.setEnabled(True)
        self.import_button.setEnabled(True)
        
        if success:
            self.books = books
            self.results_label.setText(f"Imported {len(books)} books")
            
            # Show sample of books
            if books:
                self.update_log("\nSample of imported books:")
                for i, book in enumerate(books[:3]):
                    self.update_log(f"\n{i+1}. {book.get('title')} by {book.get('author')}")
                
                if len(books) > 3:
                    self.update_log(f"\n... and {len(books) - 3} more")
        else:
            self.books = []
            self.results_label.setText("Import failed")
    
    def accept(self):
        """Handle dialog acceptance."""
        if not self.books:
            QMessageBox.warning(self, 'Warning', 'No books to import.')
            return
        
        # Emit signal with books
        self.books_imported.emit(self.books)
        
        # Close dialog
        super().accept()
