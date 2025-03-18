"""
User window for the Library Management System client.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QMessageBox, QDialog, QFormLayout
)
from PyQt5.QtCore import Qt, pyqtSignal
from utils.logger import get_logger

logger = get_logger(__name__)

class UserWindow(QMainWindow):
    """User window for the Library Management System."""
    
    # Signal emitted when logout is requested
    logout_requested = pyqtSignal()
    
    def __init__(self, client, user_data):
        """
        Initialize the user window.
        
        Args:
            client: The client instance.
            user_data (dict): The user data.
        """
        super().__init__()
        
        self.client = client
        self.user_data = user_data
        
        # Initialize UI
        self.init_ui()
        
        # Load initial data
        self.load_data()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle('Library Management System - User')
        self.setMinimumWidth(800)
        self.setMinimumHeight(600)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create header
        header_layout = QHBoxLayout()
        
        # Add title
        title_label = QLabel('Library Management System')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        header_layout.addWidget(title_label)
        
        # Add spacer
        header_layout.addStretch()
        
        # Add user info
        user_label = QLabel(f'Logged in as: {self.user_data.get("username")}')
        header_layout.addWidget(user_label)
        
        # Add logout button
        logout_button = QPushButton('Logout')
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button)
        
        main_layout.addLayout(header_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_books_tab()
        self.create_my_books_tab()
        self.create_profile_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.statusBar().showMessage('Ready')
    
    def create_books_tab(self):
        """Create the books tab."""
        books_tab = QWidget()
        layout = QVBoxLayout(books_tab)
        
        # Add title
        title_label = QLabel('Book Catalog')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # Create search controls
        search_layout = QHBoxLayout()
        
        search_label = QLabel('Search:')
        self.book_search_input = QLineEdit()
        self.book_search_input.setPlaceholderText('Enter search term')
        self.book_search_input.returnPressed.connect(self.search_books)
        
        search_by_label = QLabel('Search by:')
        self.book_search_by = QComboBox()
        self.book_search_by.addItems(['Title', 'Author', 'ISBN', 'Category'])
        
        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search_books)
        
        reset_button = QPushButton('Reset')
        reset_button.clicked.connect(self.reset_book_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.book_search_input)
        search_layout.addWidget(search_by_label)
        search_layout.addWidget(self.book_search_by)
        search_layout.addWidget(search_button)
        search_layout.addWidget(reset_button)
        
        layout.addLayout(search_layout)
        
        # Create book table
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(7)
        self.book_table.setHorizontalHeaderLabels([
            'ID', 'Title', 'Author', 'ISBN', 'Publisher', 
            'Category', 'Available'
        ])
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.book_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.book_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.book_table)
        
        # Create book controls
        controls_layout = QHBoxLayout()
        
        borrow_book_button = QPushButton('Borrow Book')
        borrow_book_button.clicked.connect(self.borrow_book)
        
        view_details_button = QPushButton('View Details')
        view_details_button.clicked.connect(self.view_book_details)
        
        refresh_button = QPushButton('Refresh')
        refresh_button.clicked.connect(self.load_books)
        
        controls_layout.addWidget(borrow_book_button)
        controls_layout.addWidget(view_details_button)
        controls_layout.addStretch()
        controls_layout.addWidget(refresh_button)
        
        layout.addLayout(controls_layout)
        
        # Add to tab widget
        self.tab_widget.addTab(books_tab, 'Books')
    
    def create_my_books_tab(self):
        """Create the my books tab."""
        my_books_tab = QWidget()
        layout = QVBoxLayout(my_books_tab)
        
        # Add title
        title_label = QLabel('My Borrowed Books')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # Create filter controls
        filter_layout = QHBoxLayout()
        
        filter_label = QLabel('Filter by status:')
        self.transaction_filter = QComboBox()
        self.transaction_filter.addItems(['All', 'Borrowed', 'Returned', 'Overdue'])
        self.transaction_filter.currentIndexChanged.connect(self.filter_transactions)
        
        refresh_button = QPushButton('Refresh')
        refresh_button.clicked.connect(self.load_transactions)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.transaction_filter)
        filter_layout.addStretch()
        filter_layout.addWidget(refresh_button)
        
        layout.addLayout(filter_layout)
        
        # Create transaction table
        self.transaction_table = QTableWidget()
        self.transaction_table.setColumnCount(6)
        self.transaction_table.setHorizontalHeaderLabels([
            'ID', 'Book Title', 'Borrow Date', 'Due Date', 'Return Date', 'Status'
        ])
        self.transaction_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transaction_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transaction_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.transaction_table)
        
        # Create transaction controls
        controls_layout = QHBoxLayout()
        
        return_book_button = QPushButton('Return Book')
        return_book_button.clicked.connect(self.return_book)
        
        view_details_button = QPushButton('View Details')
        view_details_button.clicked.connect(self.view_transaction_details)
        
        controls_layout.addWidget(return_book_button)
        controls_layout.addWidget(view_details_button)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Add to tab widget
        self.tab_widget.addTab(my_books_tab, 'My Books')
    
    def create_profile_tab(self):
        """Create the profile tab."""
        profile_tab = QWidget()
        layout = QVBoxLayout(profile_tab)
        
        # Add title
        title_label = QLabel('My Profile')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # Create profile form
        form_layout = QFormLayout()
        
        # Username
        username_label = QLabel(self.user_data.get('username', ''))
        form_layout.addRow('Username:', username_label)
        
        # Full Name
        self.full_name_input = QLineEdit(self.user_data.get('full_name', ''))
        form_layout.addRow('Full Name:', self.full_name_input)
        
        # Email
        self.email_input = QLineEdit(self.user_data.get('email', ''))
        form_layout.addRow('Email:', self.email_input)
        
        # Phone
        self.phone_input = QLineEdit(self.user_data.get('phone', ''))
        form_layout.addRow('Phone:', self.phone_input)
        
        # Address
        self.address_input = QLineEdit(self.user_data.get('address', ''))
        form_layout.addRow('Address:', self.address_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('Enter new password (leave blank to keep current)')
        form_layout.addRow('New Password:', self.password_input)
        
        # Confirm Password
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input.setPlaceholderText('Confirm new password')
        form_layout.addRow('Confirm Password:', self.confirm_password_input)
        
        layout.addLayout(form_layout)
        
        # Create buttons
        buttons_layout = QHBoxLayout()
        
        save_button = QPushButton('Save Changes')
        save_button.clicked.connect(self.save_profile)
        
        reset_button = QPushButton('Reset')
        reset_button.clicked.connect(self.reset_profile)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(reset_button)
        
        layout.addLayout(buttons_layout)
        
        # Add to tab widget
        self.tab_widget.addTab(profile_tab, 'Profile')
    
    def load_data(self):
        """Load initial data."""
        self.load_books()
        self.load_transactions()
    
    def load_books(self):
        """Load books from the server."""
        self.client.send_request('book_get_all', {}, self.handle_books_response)
    
    def handle_books_response(self, response):
        """
        Handle books response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            books = response.get('data', [])
            
            # Clear the table
            self.book_table.setRowCount(0)
            
            # Add books to the table
            for book in books:
                row = self.book_table.rowCount()
                self.book_table.insertRow(row)
                
                self.book_table.setItem(row, 0, QTableWidgetItem(str(book.get('book_id'))))
                self.book_table.setItem(row, 1, QTableWidgetItem(book.get('title')))
                self.book_table.setItem(row, 2, QTableWidgetItem(book.get('author')))
                self.book_table.setItem(row, 3, QTableWidgetItem(book.get('isbn')))
                self.book_table.setItem(row, 4, QTableWidgetItem(book.get('publisher', '')))
                self.book_table.setItem(row, 5, QTableWidgetItem(book.get('category', '')))
                
                # Set availability
                available = book.get('available', 0)
                availability_text = 'Available' if available > 0 else 'Not Available'
                self.book_table.setItem(row, 6, QTableWidgetItem(availability_text))
            
            self.statusBar().showMessage(f"Loaded {len(books)} books")
        else:
            self.statusBar().showMessage(f"Error loading books: {response.get('message')}")
    
    def search_books(self):
        """Search for books."""
        query = self.book_search_input.text().strip()
        
        if not query:
            self.load_books()
            return
        
        search_by_text = self.book_search_by.currentText().lower()
        
        data = {
            'query': query,
            'search_by': search_by_text
        }
        
        self.client.send_request('book_search', data, self.handle_books_response)
    
    def reset_book_search(self):
        """Reset book search."""
        self.book_search_input.clear()
        self.load_books()
    
    def borrow_book(self):
        """Borrow a book."""
        # Get selected row
        selected_rows = self.book_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Warning', 'Please select a book to borrow.')
            return
        
        # Get book ID
        row = selected_rows[0].row()
        book_id = int(self.book_table.item(row, 0).text())
        book_title = self.book_table.item(row, 1).text()
        availability = self.book_table.item(row, 6).text()
        
        # Check if the book is available
        if availability != 'Available':
            QMessageBox.warning(self, 'Warning', 'This book is not available for borrowing.')
            return
        
        # Confirm borrowing
        reply = QMessageBox.question(
            self, 
            'Confirm Borrowing', 
            f'Do you want to borrow "{book_title}"?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Send request to server
            data = {'book_id': book_id}
            self.client.send_request('book_borrow', data, self.handle_borrow_book_response)
    
    def handle_borrow_book_response(self, response):
        """
        Handle borrow book response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            QMessageBox.information(self, 'Success', 'Book borrowed successfully.')
            self.load_books()
            self.load_transactions()
        else:
            QMessageBox.warning(self, 'Error', f"Failed to borrow book: {response.get('message')}")
    
    def view_book_details(self):
        """View book details."""
        # Get selected row
        selected_rows = self.book_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Warning', 'Please select a book to view details.')
            return
        
        # Get book ID
        row = selected_rows[0].row()
        book_id = int(self.book_table.item(row, 0).text())
        
        # Get book data
        data = {'book_id': book_id}
        self.client.send_request('book_get', data, self.handle_book_details_response)
    
    def handle_book_details_response(self, response):
        """
        Handle book details response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            book = response.get('data', {})
            
            # Create message
            message = f"Title: {book.get('title')}\n"
            message += f"Author: {book.get('author')}\n"
            message += f"ISBN: {book.get('isbn')}\n"
            message += f"Publisher: {book.get('publisher', 'N/A')}\n"
            message += f"Publication Year: {book.get('publication_year', 'N/A')}\n"
            message += f"Category: {book.get('category', 'N/A')}\n"
            message += f"Available: {book.get('available', 0)}/{book.get('quantity', 0)}\n"
            message += f"Description: {book.get('description', 'N/A')}"
            
            # Show message
            QMessageBox.information(self, 'Book Details', message)
        else:
            QMessageBox.warning(self, 'Error', f"Failed to get book details: {response.get('message')}")
    
    def load_transactions(self):
        """Load transactions from the server."""
        # Get user ID
        user_id = self.user_data.get('user_id')
        
        # Get filter
        filter_text = self.transaction_filter.currentText().lower()
        status = None if filter_text == 'all' else filter_text
        
        # Send request to server
        data = {'user_id': user_id, 'status': status}
        self.client.send_request('user_get_transactions', data, self.handle_transactions_response)
    
    def handle_transactions_response(self, response):
        """
        Handle transactions response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            transactions = response.get('data', [])
            
            # Clear the table
            self.transaction_table.setRowCount(0)
            
            # Add transactions to the table
            for transaction in transactions:
                row = self.transaction_table.rowCount()
                self.transaction_table.insertRow(row)
                
                self.transaction_table.setItem(row, 0, QTableWidgetItem(str(transaction.get('transaction_id'))))
                self.transaction_table.setItem(row, 1, QTableWidgetItem(transaction.get('book_title', 'Unknown')))
                self.transaction_table.setItem(row, 2, QTableWidgetItem(transaction.get('borrow_date', '')))
                self.transaction_table.setItem(row, 3, QTableWidgetItem(transaction.get('due_date', '')))
                self.transaction_table.setItem(row, 4, QTableWidgetItem(transaction.get('return_date', '')))
                self.transaction_table.setItem(row, 5, QTableWidgetItem(transaction.get('status', '')))
            
            self.statusBar().showMessage(f"Loaded {len(transactions)} transactions")
        else:
            self.statusBar().showMessage(f"Error loading transactions: {response.get('message')}")
    
    def filter_transactions(self):
        """Filter transactions."""
        self.load_transactions()
    
    def return_book(self):
        """Return a book."""
        # Get selected row
        selected_rows = self.transaction_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Warning', 'Please select a transaction to return the book.')
            return
        
        # Get transaction ID
        row = selected_rows[0].row()
        transaction_id = int(self.transaction_table.item(row, 0).text())
        book_title = self.transaction_table.item(row, 1).text()
        status = self.transaction_table.item(row, 5).text()
        
        # Check if the book is already returned
        if status.lower() == 'returned':
            QMessageBox.warning(self, 'Warning', 'This book has already been returned.')
            return
        
        # Confirm returning
        reply = QMessageBox.question(
            self, 
            'Confirm Return', 
            f'Do you want to return "{book_title}"?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Send request to server
            data = {'transaction_id': transaction_id}
            self.client.send_request('book_return', data, self.handle_return_book_response)
    
    def handle_return_book_response(self, response):
        """
        Handle return book response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            QMessageBox.information(self, 'Success', 'Book returned successfully.')
            self.load_transactions()
            self.load_books()
        else:
            QMessageBox.warning(self, 'Error', f"Failed to return book: {response.get('message')}")
    
    def view_transaction_details(self):
        """View transaction details."""
        # Get selected row
        selected_rows = self.transaction_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Warning', 'Please select a transaction to view details.')
            return
        
        # Get transaction ID
        row = selected_rows[0].row()
        transaction_id = int(self.transaction_table.item(row, 0).text())
        
        # Show transaction details
        message = f"Transaction ID: {transaction_id}\n"
        message += f"Book: {self.transaction_table.item(row, 1).text()}\n"
        message += f"Borrow Date: {self.transaction_table.item(row, 2).text()}\n"
        message += f"Due Date: {self.transaction_table.item(row, 3).text()}\n"
        message += f"Return Date: {self.transaction_table.item(row, 4).text() or 'Not returned yet'}\n"
        message += f"Status: {self.transaction_table.item(row, 5).text()}"
        
        QMessageBox.information(self, 'Transaction Details', message)
    
    def save_profile(self):
        """Save profile changes."""
        # Get user data
        user_id = self.user_data.get('user_id')
        full_name = self.full_name_input.text().strip()
        email = self.email_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()
        password = self.password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validate input
        if not full_name:
            QMessageBox.warning(self, 'Validation Error', 'Full name is required.')
            self.full_name_input.setFocus()
            return
        
        if not email:
            QMessageBox.warning(self, 'Validation Error', 'Email is required.')
            self.email_input.setFocus()
            return
        
        # Check if passwords match
        if password and password != confirm_password:
            QMessageBox.warning(self, 'Validation Error', 'Passwords do not match.')
            self.password_input.setFocus()
            return
        
        # Prepare data
        data = {
            'user_id': user_id,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'address': address
        }
        
        # Add password if provided
        if password:
            data['password'] = password
        
        # Send request to server
        self.client.send_request('user_update', data, self.handle_update_profile_response)
    
    def handle_update_profile_response(self, response):
        """
        Handle update profile response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            # Update user data
            self.user_data = response.get('data', {})
            
            # Clear password fields
            self.password_input.clear()
            self.confirm_password_input.clear()
            
            QMessageBox.information(self, 'Success', 'Profile updated successfully.')
        else:
            QMessageBox.warning(self, 'Error', f"Failed to update profile: {response.get('message')}")
    
    def reset_profile(self):
        """Reset profile form."""
        self.full_name_input.setText(self.user_data.get('full_name', ''))
        self.email_input.setText(self.user_data.get('email', ''))
        self.phone_input.setText(self.user_data.get('phone', ''))
        self.address_input.setText(self.user_data.get('address', ''))
        self.password_input.clear()
        self.confirm_password_input.clear()
    
    def logout(self):
        """Handle logout button click."""
        # Confirm logout
        reply = QMessageBox.question(
            self, 
            'Confirm Logout', 
            'Are you sure you want to logout?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Send logout request
            self.client.logout(self.handle_logout_response)
    
    def handle_logout_response(self, response):
        """
        Handle logout response from server.
        
        Args:
            response (dict): The response from the server.
        """
        # Emit logout signal
        self.logout_requested.emit()
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: The close event.
        """
        # Confirm exit
        reply = QMessageBox.question(
            self, 
            'Confirm Exit', 
            'Are you sure you want to exit?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Disconnect from server
            self.client.disconnect()
            
            # Accept the event
            event.accept()
        else:
            # Ignore the event
            event.ignore()
