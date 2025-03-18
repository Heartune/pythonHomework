"""
Book dialog for the Library Management System client.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QSpinBox, QTextEdit, QComboBox,
    QPushButton, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from utils.logger import get_logger

logger = get_logger(__name__)

class BookDialog(QDialog):
    """Dialog for adding or editing a book."""
    
    def __init__(self, parent=None, book_data=None):
        """
        Initialize the book dialog.
        
        Args:
            parent: The parent widget.
            book_data (dict, optional): The book data for editing.
        """
        super().__init__(parent)
        
        self.book_data = book_data
        self.is_edit_mode = book_data is not None
        
        # Initialize UI
        self.init_ui()
        
        # Fill form if in edit mode
        if self.is_edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle('Add Book' if not self.is_edit_mode else 'Edit Book')
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Add form fields
        # Title
        self.title_input = QLineEdit()
        form_layout.addRow('Title:', self.title_input)
        
        # Author
        self.author_input = QLineEdit()
        form_layout.addRow('Author:', self.author_input)
        
        # ISBN
        self.isbn_input = QLineEdit()
        form_layout.addRow('ISBN:', self.isbn_input)
        
        # Publisher
        self.publisher_input = QLineEdit()
        form_layout.addRow('Publisher:', self.publisher_input)
        
        # Publication Year
        self.year_input = QSpinBox()
        self.year_input.setRange(1000, 2100)
        self.year_input.setValue(2023)
        form_layout.addRow('Publication Year:', self.year_input)
        
        # Category
        self.category_input = QComboBox()
        self.category_input.addItems([
            'Fiction', 'Non-Fiction', 'Science', 'Technology', 
            'History', 'Biography', 'Art', 'Philosophy', 'Other'
        ])
        self.category_input.setEditable(True)
        form_layout.addRow('Category:', self.category_input)
        
        # Quantity
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 1000)
        self.quantity_input.setValue(1)
        form_layout.addRow('Quantity:', self.quantity_input)
        
        # Description
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText('Enter book description')
        form_layout.addRow('Description:', self.description_input)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def fill_form(self):
        """Fill the form with book data."""
        self.title_input.setText(self.book_data.get('title', ''))
        self.author_input.setText(self.book_data.get('author', ''))
        self.isbn_input.setText(self.book_data.get('isbn', ''))
        self.publisher_input.setText(self.book_data.get('publisher', ''))
        
        publication_year = self.book_data.get('publication_year')
        if publication_year:
            self.year_input.setValue(int(publication_year))
        
        category = self.book_data.get('category', '')
        index = self.category_input.findText(category)
        if index >= 0:
            self.category_input.setCurrentIndex(index)
        else:
            self.category_input.setEditText(category)
        
        quantity = self.book_data.get('quantity', 1)
        self.quantity_input.setValue(int(quantity))
        
        self.description_input.setText(self.book_data.get('description', ''))
    
    def get_book_data(self):
        """
        Get the book data from the form.
        
        Returns:
            dict: The book data.
        """
        return {
            'title': self.title_input.text().strip(),
            'author': self.author_input.text().strip(),
            'isbn': self.isbn_input.text().strip(),
            'publisher': self.publisher_input.text().strip(),
            'publication_year': self.year_input.value(),
            'category': self.category_input.currentText().strip(),
            'description': self.description_input.toPlainText().strip(),
            'quantity': self.quantity_input.value()
        }
