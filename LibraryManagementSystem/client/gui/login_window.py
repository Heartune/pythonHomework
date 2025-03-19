"""
Login window for the Library Management System client.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from utils.logger import get_logger

logger = get_logger(__name__)

class LoginWindow(QWidget):
    """Login window for the Library Management System."""
    
    # Signal emitted when login is successful
    login_successful = pyqtSignal(dict)
    
    def __init__(self, client):
        """
        Initialize the login window.
        
        Args:
            client: The client instance.
        """
        super().__init__()
        
        self.client = client
        
        # Initialize UI
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle('Library Management System - Login')
        self.setMinimumWidth(400)
        self.setMinimumHeight(250)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Add title
        title_label = QLabel('Library Management System')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet('font-size: 18px; font-weight: bold;')
        layout.addWidget(title_label)
        
        # Add subtitle
        subtitle_label = QLabel('Please log in to continue')
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet('font-size: 12px; margin-bottom: 20px;')
        layout.addWidget(subtitle_label)
        
        # Add username field
        username_layout = QHBoxLayout()
        username_label = QLabel('Username:')
        username_label.setMinimumWidth(80)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('Enter your username')
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)
        
        # Add password field
        password_layout = QHBoxLayout()
        password_label = QLabel('Password:')
        password_label.setMinimumWidth(80)
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText('Enter your password')
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)
        
        # Add role selection
        role_layout = QHBoxLayout()
        role_label = QLabel('Role:')
        role_label.setMinimumWidth(80)
        self.role_combo = QComboBox()
        self.role_combo.addItem('User')
        self.role_combo.addItem('Admin')
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_combo)
        layout.addLayout(role_layout)
        
        # Add login button
        self.login_button = QPushButton('Login')
        self.login_button.setStyleSheet('font-weight: bold; padding: 8px;')
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)
        
        # Add register button
        self.register_button = QPushButton('Register')
        self.register_button.clicked.connect(self.register)
        layout.addWidget(self.register_button)
        
        # Set layout
        self.setLayout(layout)
        
        # Connect enter key to login
        self.username_input.returnPressed.connect(self.login)
        self.password_input.returnPressed.connect(self.login)
    
    def login(self):
        """Handle login button click."""
        # Get username and password
        username = self.username_input.text().strip()
        password = self.password_input.text()
        role = self.role_combo.currentText().lower()
        
        # Validate input
        if not username:
            QMessageBox.warning(self, 'Login Error', 'Please enter a username.')
            self.username_input.setFocus()
            return
        
        if not password:
            QMessageBox.warning(self, 'Login Error', 'Please enter a password.')
            self.password_input.setFocus()
            return
        
        # Connect to server if not connected
        if not self.client.connected:
            if not self.client.connect():
                QMessageBox.critical(self, 'Connection Error', 'Could not connect to server.')
                return
        
        # Disable login button
        self.login_button.setEnabled(False)
        self.login_button.setText('Logging in...')
        
        # Send login request
        self.client.login(username, password, self.handle_login_response)
    
    def handle_login_response(self, response):
        """
        Handle login response from server.
        
        Args:
            response (dict): The response from the server.
        """
        # Re-enable login button
        self.login_button.setEnabled(True)
        self.login_button.setText('Login')
        
        # Check if login was successful
        if response.get('success'):
            # Get user data
            user_data = response.get('data', {})
            
            # Get user role from response
            user_role = user_data.get('role', '')
            
            # No need to check selected role against actual role
            # Just log the role information
            logger.debug(f"User logged in with role: {user_role}")
            
            # Emit login successful signal
            self.login_successful.emit(user_data)
            
            # Clear password field
            self.password_input.clear()
            
            # Hide login window
            self.hide()
        else:
            # Show error message
            QMessageBox.warning(
                self, 
                'Login Error', 
                response.get('message', 'Login failed.')
            )
    
    def register(self):
        """Handle register button click."""
        # Show message box
        QMessageBox.information(
            self, 
            'Registration', 
            'Please contact the administrator to register a new account.'
        )
    
    def closeEvent(self, event):
        """
        Handle window close event.
        
        Args:
            event: The close event.
        """
        # Disconnect from server
        self.client.disconnect()
        
        # Accept the event
        event.accept()
