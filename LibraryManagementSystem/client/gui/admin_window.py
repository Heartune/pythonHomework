"""
Admin window for the Library Management System client.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QLineEdit, QComboBox, QMessageBox, QGroupBox, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from utils.logger import get_logger
from .dialogs.book_dialog import BookDialog
from .dialogs.user_dialog import UserDialog

logger = get_logger(__name__)

class AdminWindow(QMainWindow):
    """Admin window for the Library Management System."""
    
    # Signal emitted when logout is requested
    logout_requested = pyqtSignal()
    
    def __init__(self, client, user_data):
        """
        Initialize the admin window.
        
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
        self.setWindowTitle('Library Management System - Admin')
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
        title_label = QLabel('Library Management System - Admin Panel')
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        header_layout.addWidget(title_label)
        
        # Add spacer
        header_layout.addStretch()
        
        # Add user info
        user_label = QLabel(f'Logged in as: {self.user_data.get("username", "Admin")}')
        header_layout.addWidget(user_label)
        
        # Add logout button
        logout_button = QPushButton('Logout')
        logout_button.clicked.connect(self.logout)
        header_layout.addWidget(logout_button)
        
        main_layout.addLayout(header_layout)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.create_dashboard_tab()
        self.create_books_tab()
        self.create_users_tab()
        self.create_reports_tab()
        
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.statusBar().showMessage('Ready')
    
    def create_dashboard_tab(self):
        """Create the dashboard tab."""
        dashboard_tab = QWidget()
        layout = QVBoxLayout(dashboard_tab)
        
        # Add title
        title_label = QLabel('Dashboard')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # Create dashboard widgets
        dashboard_layout = QHBoxLayout()
        
        # Create statistics group
        stats_group = QGroupBox('Statistics')
        stats_layout = QVBoxLayout(stats_group)
        
        self.total_books_label = QLabel('Total Books: 0')
        self.available_books_label = QLabel('Available Books: 0')
        self.total_users_label = QLabel('Total Users: 0')
        self.active_loans_label = QLabel('Active Loans: 0')
        
        stats_layout.addWidget(self.total_books_label)
        stats_layout.addWidget(self.available_books_label)
        stats_layout.addWidget(self.total_users_label)
        stats_layout.addWidget(self.active_loans_label)
        
        dashboard_layout.addWidget(stats_group)
        
        # Create charts group
        charts_group = QGroupBox('Books by Category')
        charts_layout = QVBoxLayout(charts_group)
        
        # Create a figure for the chart
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        charts_layout.addWidget(self.canvas)
        
        dashboard_layout.addWidget(charts_group)
        
        layout.addLayout(dashboard_layout)
        
        # Add to tab widget
        self.tab_widget.addTab(dashboard_tab, 'Dashboard')
    
    def create_books_tab(self):
        """Create the books tab."""
        books_tab = QWidget()
        layout = QVBoxLayout(books_tab)
        
        # Add title
        title_label = QLabel('Book Management')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # Create search controls
        search_layout = QHBoxLayout()
        
        search_label = QLabel('Search:')
        self.book_search_input = QLineEdit()
        self.book_search_input.setPlaceholderText('Enter search term')
        
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
            'ID', 'Title', 'Author', 'ISBN', 'Category', 'Quantity', 'Available'
        ])
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.book_table)
        
        # Create book controls
        controls_layout = QHBoxLayout()
        
        add_book_button = QPushButton('Add Book')
        add_book_button.clicked.connect(self.add_book)
        
        edit_book_button = QPushButton('Edit Book')
        edit_book_button.clicked.connect(self.edit_book)
        
        delete_book_button = QPushButton('Delete Book')
        delete_book_button.clicked.connect(self.delete_book)
        
        controls_layout.addWidget(add_book_button)
        controls_layout.addWidget(edit_book_button)
        controls_layout.addWidget(delete_book_button)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Add to tab widget
        self.tab_widget.addTab(books_tab, 'Books')
    
    def create_users_tab(self):
        """Create the users tab."""
        users_tab = QWidget()
        layout = QVBoxLayout(users_tab)
        
        # Add title
        title_label = QLabel('User Management')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # Create search controls
        search_layout = QHBoxLayout()
        
        search_label = QLabel('Search:')
        self.user_search_input = QLineEdit()
        self.user_search_input.setPlaceholderText('Enter username')
        
        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search_users)
        
        reset_button = QPushButton('Reset')
        reset_button.clicked.connect(self.reset_user_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.user_search_input)
        search_layout.addWidget(search_button)
        search_layout.addWidget(reset_button)
        
        layout.addLayout(search_layout)
        
        # Create user table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels([
            'ID', 'Username', 'Full Name', 'Email', 'Role'
        ])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        
        layout.addWidget(self.user_table)
        
        # Create user controls
        controls_layout = QHBoxLayout()
        
        add_user_button = QPushButton('Add User')
        add_user_button.clicked.connect(self.add_user)
        
        edit_user_button = QPushButton('Edit User')
        edit_user_button.clicked.connect(self.edit_user)
        
        delete_user_button = QPushButton('Delete User')
        delete_user_button.clicked.connect(self.delete_user)
        
        controls_layout.addWidget(add_user_button)
        controls_layout.addWidget(edit_user_button)
        controls_layout.addWidget(delete_user_button)
        controls_layout.addStretch()
        
        layout.addLayout(controls_layout)
        
        # Add to tab widget
        self.tab_widget.addTab(users_tab, 'Users')
    
    def create_reports_tab(self):
        """Create the reports tab."""
        reports_tab = QWidget()
        layout = QVBoxLayout(reports_tab)
        
        # Add title
        title_label = QLabel('Reports and Analytics')
        title_label.setStyleSheet('font-size: 16px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # Create report selection
        selection_layout = QHBoxLayout()
        
        report_label = QLabel('Select Report:')
        self.report_combo = QComboBox()
        self.report_combo.addItems([
            'Books by Category', 
            'Books by Popularity', 
            'User Activity'
        ])
        
        generate_button = QPushButton('Generate Report')
        generate_button.clicked.connect(self.generate_report)
        
        selection_layout.addWidget(report_label)
        selection_layout.addWidget(self.report_combo)
        selection_layout.addWidget(generate_button)
        selection_layout.addStretch()
        
        layout.addLayout(selection_layout)
        
        # Create report display area
        self.report_figure = Figure(figsize=(8, 6), dpi=100)
        self.report_canvas = FigureCanvas(self.report_figure)
        
        layout.addWidget(self.report_canvas)
        
        # Add to tab widget
        self.tab_widget.addTab(reports_tab, 'Reports')
    
    def logout(self):
        """Handle logout button click."""
        # Emit logout signal
        self.logout_requested.emit()
    
    def load_data(self):
        """Load initial data."""
        self.load_books()
        self.load_users()
        self.load_dashboard_data()
    
    def load_dashboard_data(self):
        """Load dashboard data."""
        # Request statistics
        self.client.send_request('book_get_all', {}, self.handle_dashboard_books_response)
        self.client.send_request('user_get_all', {}, self.handle_dashboard_users_response)
        self.client.send_request('transaction_get_all', {}, self.handle_dashboard_transactions_response)
    
    def handle_dashboard_books_response(self, response):
        """
        Handle dashboard books response.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            books = response.get('data', [])
            total_books = len(books)
            available_books = sum(1 for book in books if book.get('available', 0) > 0)
            
            self.total_books_label.setText(f'Total Books: {total_books}')
            self.available_books_label.setText(f'Available Books: {available_books}')
            
            # Update chart
            self.update_dashboard_chart(books)
        else:
            self.statusBar().showMessage(f"Error loading books: {response.get('message')}")
    
    def handle_dashboard_users_response(self, response):
        """
        Handle dashboard users response.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            users = response.get('data', [])
            total_users = len(users)
            
            self.total_users_label.setText(f'Total Users: {total_users}')
        else:
            self.statusBar().showMessage(f"Error loading users: {response.get('message')}")
    
    def handle_dashboard_transactions_response(self, response):
        """
        Handle dashboard transactions response.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            transactions = response.get('data', [])
            active_loans = sum(1 for t in transactions if t.get('status') == 'borrowed')
            
            self.active_loans_label.setText(f'Active Loans: {active_loans}')
        else:
            self.statusBar().showMessage(f"Error loading transactions: {response.get('message')}")
    
    def update_dashboard_chart(self, books):
        """
        Update the dashboard chart.
        
        Args:
            books (list): List of book dictionaries.
        """
        try:
            # Clear the figure
            self.figure.clear()
            
            # Create a new subplot
            ax = self.figure.add_subplot(111)
            
            # Count books by category
            categories = {}
            for book in books:
                category = book.get('category', 'Uncategorized')
                if category in categories:
                    categories[category] += 1
                else:
                    categories[category] = 1
            
            # Sort categories by count
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            # Limit to top 5 categories
            if len(sorted_categories) > 5:
                sorted_categories = sorted_categories[:5]
            
            # Extract data for chart
            category_names = [c[0] for c in sorted_categories]
            category_counts = [c[1] for c in sorted_categories]
            
            # Create a bar chart
            ax.bar(category_names, category_counts)
            
            # Set labels and title
            ax.set_xlabel('Category')
            ax.set_ylabel('Number of Books')
            ax.set_title('Books by Category')
            
            # Rotate x-axis labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Adjust layout
            self.figure.tight_layout()
            
            # Redraw the canvas
            self.canvas.draw()
        except Exception as e:
            logger.error(f"Error updating dashboard chart: {e}")
    
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
                self.book_table.setItem(row, 4, QTableWidgetItem(book.get('category', '')))
                self.book_table.setItem(row, 5, QTableWidgetItem(str(book.get('quantity', 0))))
                self.book_table.setItem(row, 6, QTableWidgetItem(str(book.get('available', 0))))
            
            self.statusBar().showMessage(f"Loaded {len(books)} books")
        else:
            self.statusBar().showMessage(f"Error loading books: {response.get('message')}")
    
    # Book management methods
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
    
    def add_book(self):
        """Add a new book."""
        dialog = BookDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            # Get book data
            book_data = dialog.get_book_data()
            
            # Send request to server
            self.client.send_request('book_create', book_data, self.handle_add_book_response)
    
    def handle_add_book_response(self, response):
        """
        Handle add book response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            QMessageBox.information(self, 'Success', 'Book added successfully.')
            self.load_books()
            self.load_dashboard_data()
        else:
            QMessageBox.warning(self, 'Error', f"Failed to add book: {response.get('message')}")
    
    def edit_book(self):
        """Edit a book."""
        # Get selected row
        selected_rows = self.book_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Warning', 'Please select a book to edit.')
            return
        
        # Get book ID
        row = selected_rows[0].row()
        book_id = int(self.book_table.item(row, 0).text())
        
        # Get book data
        data = {'book_id': book_id}
        self.client.send_request('book_get', data, self.handle_get_book_for_edit_response)
    
    def handle_get_book_for_edit_response(self, response):
        """
        Handle get book for edit response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            book_data = response.get('data', {})
            
            dialog = BookDialog(self, book_data)
            
            if dialog.exec_() == QDialog.Accepted:
                # Get updated book data
                updated_data = dialog.get_book_data()
                updated_data['book_id'] = book_data.get('book_id')
                
                # Send request to server
                self.client.send_request('book_update', updated_data, self.handle_edit_book_response)
        else:
            QMessageBox.warning(self, 'Error', f"Failed to get book: {response.get('message')}")
    
    def handle_edit_book_response(self, response):
        """
        Handle edit book response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            QMessageBox.information(self, 'Success', 'Book updated successfully.')
            self.load_books()
            self.load_dashboard_data()
        else:
            QMessageBox.warning(self, 'Error', f"Failed to update book: {response.get('message')}")
    
    def delete_book(self):
        """Delete a book."""
        # Get selected row
        selected_rows = self.book_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Warning', 'Please select a book to delete.')
            return
        
        # Get book ID
        row = selected_rows[0].row()
        book_id = int(self.book_table.item(row, 0).text())
        book_title = self.book_table.item(row, 1).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            'Confirm Deletion', 
            f'Are you sure you want to delete "{book_title}"?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Send request to server
            data = {'book_id': book_id}
            self.client.send_request('book_delete', data, self.handle_delete_book_response)
    
    def handle_delete_book_response(self, response):
        """
        Handle delete book response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            QMessageBox.information(self, 'Success', 'Book deleted successfully.')
            self.load_books()
            self.load_dashboard_data()
        else:
            QMessageBox.warning(self, 'Error', f"Failed to delete book: {response.get('message')}")

    
    def load_users(self):
        """Load users from the server."""
        self.client.send_request('user_get_all', {}, self.handle_users_response)
    
    def handle_users_response(self, response):
        """
        Handle users response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            users = response.get('data', [])
            
            # Clear the table
            self.user_table.setRowCount(0)
            
            # Add users to the table
            for user in users:
                row = self.user_table.rowCount()
                self.user_table.insertRow(row)
                
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user.get('user_id'))))
                self.user_table.setItem(row, 1, QTableWidgetItem(user.get('username')))
                self.user_table.setItem(row, 2, QTableWidgetItem(user.get('full_name', '')))
                self.user_table.setItem(row, 3, QTableWidgetItem(user.get('email', '')))
                self.user_table.setItem(row, 4, QTableWidgetItem(user.get('role', 'user')))
            
            self.statusBar().showMessage(f"Loaded {len(users)} users")
        else:
            self.statusBar().showMessage(f"Error loading users: {response.get('message')}")
    
    # User management methods
    def search_users(self):
        """Search for users."""
        query = self.user_search_input.text().strip()
        
        if not query:
            self.load_users()
            return
        
        # Search by username
        data = {'username': query}
        self.client.send_request('user_get_by_username', data, self.handle_user_search_response)
    
    def handle_user_search_response(self, response):
        """
        Handle user search response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            user = response.get('data', {})
            
            # Clear the table
            self.user_table.setRowCount(0)
            
            # Add user to the table
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user.get('user_id'))))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.get('username')))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.get('full_name', '')))
            self.user_table.setItem(row, 3, QTableWidgetItem(user.get('email', '')))
            self.user_table.setItem(row, 4, QTableWidgetItem(user.get('role', 'user')))
            
            self.statusBar().showMessage("User found")
        else:
            self.statusBar().showMessage(f"User not found: {response.get('message')}")
            self.user_table.setRowCount(0)
    
    def reset_user_search(self):
        """Reset user search."""
        self.user_search_input.clear()
        self.load_users()
    
    def add_user(self):
        """Add a new user."""
        dialog = UserDialog(self)
        
        if dialog.exec_() == QDialog.Accepted:
            # Get user data
            user_data = dialog.get_user_data()
            
            # Send request to server
            self.client.send_request('user_create', user_data, self.handle_add_user_response)
    
    def handle_add_user_response(self, response):
        """
        Handle add user response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            QMessageBox.information(self, 'Success', 'User added successfully.')
            self.load_users()
            self.load_dashboard_data()
        else:
            QMessageBox.warning(self, 'Error', f"Failed to add user: {response.get('message')}")
    
    def edit_user(self):
        """Edit a user."""
        # Get selected row
        selected_rows = self.user_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Warning', 'Please select a user to edit.')
            return
        
        # Get user ID
        row = selected_rows[0].row()
        user_id = int(self.user_table.item(row, 0).text())
        
        # Get user data
        data = {'user_id': user_id}
        self.client.send_request('user_get', data, self.handle_get_user_for_edit_response)
    
    def handle_get_user_for_edit_response(self, response):
        """
        Handle get user for edit response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            user_data = response.get('data', {})
            
            dialog = UserDialog(self, user_data)
            
            if dialog.exec_() == QDialog.Accepted:
                # Get updated user data
                updated_data = dialog.get_user_data()
                updated_data['user_id'] = user_data.get('user_id')
                
                # Send request to server
                self.client.send_request('user_update', updated_data, self.handle_edit_user_response)
        else:
            QMessageBox.warning(self, 'Error', f"Failed to get user: {response.get('message')}")
    
    def handle_edit_user_response(self, response):
        """
        Handle edit user response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            QMessageBox.information(self, 'Success', 'User updated successfully.')
            self.load_users()
        else:
            QMessageBox.warning(self, 'Error', f"Failed to update user: {response.get('message')}")
    
    def delete_user(self):
        """Delete a user."""
        # Get selected row
        selected_rows = self.user_table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, 'Warning', 'Please select a user to delete.')
            return
        
        # Get user ID
        row = selected_rows[0].row()
        user_id = int(self.user_table.item(row, 0).text())
        username = self.user_table.item(row, 1).text()
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, 
            'Confirm Deletion', 
            f'Are you sure you want to delete user "{username}"?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Send request to server
            data = {'user_id': user_id}
            self.client.send_request('user_delete', data, self.handle_delete_user_response)
    
    def handle_delete_user_response(self, response):
        """
        Handle delete user response from server.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            QMessageBox.information(self, 'Success', 'User deleted successfully.')
            self.load_users()
            self.load_dashboard_data()
        else:
            QMessageBox.warning(self, 'Error', f"Failed to delete user: {response.get('message')}")
    
    # Report methods
    def generate_report(self):
        """Generate a report."""
        report_type = self.report_combo.currentText()
        
        if report_type == 'Books by Category':
            self.generate_books_by_category_report()
        elif report_type == 'Books by Popularity':
            self.generate_books_by_popularity_report()
        elif report_type == 'User Activity':
            self.generate_user_activity_report()
    
    def generate_books_by_category_report(self):
        """Generate books by category report."""
        self.client.send_request('book_get_all', {}, self.handle_books_by_category_report)
    
    def handle_books_by_category_report(self, response):
        """
        Handle books by category report response.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            books = response.get('data', [])
            
            # Clear the figure
            self.report_figure.clear()
            
            # Create a new subplot
            ax = self.report_figure.add_subplot(111)
            
            # Count books by category
            categories = {}
            for book in books:
                category = book.get('category', 'Uncategorized')
                if category in categories:
                    categories[category] += 1
                else:
                    categories[category] = 1
            
            # Sort categories by count
            sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)
            
            # Extract data for chart
            category_names = [c[0] for c in sorted_categories]
            category_counts = [c[1] for c in sorted_categories]
            
            # Create a bar chart
            ax.bar(category_names, category_counts)
            
            # Set labels and title
            ax.set_xlabel('Category')
            ax.set_ylabel('Number of Books')
            ax.set_title('Books by Category')
            
            # Rotate x-axis labels
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
            
            # Adjust layout
            self.report_figure.tight_layout()
            
            # Redraw the canvas
            self.report_canvas.draw()
            
            self.statusBar().showMessage("Generated Books by Category report")
        else:
            self.statusBar().showMessage(f"Error generating report: {response.get('message')}")
    
    def generate_books_by_popularity_report(self):
        """Generate books by popularity report."""
        self.client.send_request('book_get_popularity', {}, self.handle_books_by_popularity_report)
    
    def handle_books_by_popularity_report(self, response):
        """
        Handle books by popularity report response.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            books = response.get('data', [])
            
            # Clear the figure
            self.report_figure.clear()
            
            # Create a new subplot
            ax = self.report_figure.add_subplot(111)
            
            # Sort books by borrow count
            sorted_books = sorted(books, key=lambda x: x.get('borrow_count', 0), reverse=True)
            
            # Limit to top 10 books
            if len(sorted_books) > 10:
                sorted_books = sorted_books[:10]
            
            # Extract data for chart
            book_titles = [b.get('title', 'Unknown') for b in sorted_books]
            borrow_counts = [b.get('borrow_count', 0) for b in sorted_books]
            
            # Create a horizontal bar chart
            ax.barh(book_titles, borrow_counts)
            
            # Set labels and title
            ax.set_xlabel('Number of Borrows')
            ax.set_ylabel('Book Title')
            ax.set_title('Top 10 Most Popular Books')
            
            # Adjust layout
            self.report_figure.tight_layout()
            
            # Redraw the canvas
            self.report_canvas.draw()
            
            self.statusBar().showMessage("Generated Books by Popularity report")
        else:
            self.statusBar().showMessage(f"Error generating report: {response.get('message')}")
    
    def generate_user_activity_report(self):
        """Generate user activity report."""
        self.client.send_request('user_get_activity', {}, self.handle_user_activity_report)
    
    def handle_user_activity_report(self, response):
        """
        Handle user activity report response.
        
        Args:
            response (dict): The response from the server.
        """
        if response.get('success'):
            users = response.get('data', [])
            
            # Clear the figure
            self.report_figure.clear()
            
            # Create a new subplot
            ax = self.report_figure.add_subplot(111)
            
            # Sort users by activity
            sorted_users = sorted(users, key=lambda x: x.get('transaction_count', 0), reverse=True)
            
            # Limit to top 10 users
            if len(sorted_users) > 10:
                sorted_users = sorted_users[:10]
            
            # Extract data for chart
            usernames = [u.get('username', 'Unknown') for u in sorted_users]
            transaction_counts = [u.get('transaction_count', 0) for u in sorted_users]
            
            # Create a horizontal bar chart
            ax.barh(usernames, transaction_counts)
            
            # Set labels and title
            ax.set_xlabel('Number of Transactions')
            ax.set_ylabel('Username')
            ax.set_title('Top 10 Most Active Users')
            
            # Adjust layout
            self.report_figure.tight_layout()
            
            # Redraw the canvas
            self.report_canvas.draw()
            
            self.statusBar().showMessage("Generated User Activity report")
        else:
            self.statusBar().showMessage(f"Error generating report: {response.get('message')}")
