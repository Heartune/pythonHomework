"""
User dialog for the Library Management System client.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
    QLabel, QLineEdit, QComboBox, QPushButton, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from utils.logger import get_logger

logger = get_logger(__name__)

class UserDialog(QDialog):
    """Dialog for adding or editing a user."""
    
    def __init__(self, parent=None, user_data=None):
        """
        Initialize the user dialog.
        
        Args:
            parent: The parent widget.
            user_data (dict, optional): The user data for editing.
        """
        super().__init__(parent)
        
        self.user_data = user_data
        self.is_edit_mode = user_data is not None
        
        # Initialize UI
        self.init_ui()
        
        # Fill form if in edit mode
        if self.is_edit_mode:
            self.fill_form()
    
    def init_ui(self):
        """Initialize the user interface."""
        # Set window properties
        self.setWindowTitle('Add User' if not self.is_edit_mode else 'Edit User')
        self.setMinimumWidth(400)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create form layout
        form_layout = QFormLayout()
        
        # Add form fields
        # Username
        self.username_input = QLineEdit()
        form_layout.addRow('Username:', self.username_input)
        
        # Password (only for new users)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        if self.is_edit_mode:
            self.password_input.setPlaceholderText('Leave blank to keep current password')
        form_layout.addRow('Password:', self.password_input)
        
        # Full Name
        self.full_name_input = QLineEdit()
        form_layout.addRow('Full Name:', self.full_name_input)
        
        # Email
        self.email_input = QLineEdit()
        form_layout.addRow('Email:', self.email_input)
        
        # Phone
        self.phone_input = QLineEdit()
        form_layout.addRow('Phone:', self.phone_input)
        
        # Address
        self.address_input = QLineEdit()
        form_layout.addRow('Address:', self.address_input)
        
        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(['user', 'admin'])
        form_layout.addRow('Role:', self.role_combo)
        
        layout.addLayout(form_layout)
        
        # Add buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addWidget(button_box)
    
    def fill_form(self):
        """Fill the form with user data."""
        self.username_input.setText(self.user_data.get('username', ''))
        self.full_name_input.setText(self.user_data.get('full_name', ''))
        self.email_input.setText(self.user_data.get('email', ''))
        self.phone_input.setText(self.user_data.get('phone', ''))
        self.address_input.setText(self.user_data.get('address', ''))
        
        role = self.user_data.get('role', 'user')
        index = self.role_combo.findText(role)
        if index >= 0:
            self.role_combo.setCurrentIndex(index)
    
    def get_user_data(self):
        """
        Get the user data from the form.
        
        Returns:
            dict: The user data.
        """
        data = {
            'username': self.username_input.text().strip(),
            'full_name': self.full_name_input.text().strip(),
            'email': self.email_input.text().strip(),
            'phone': self.phone_input.text().strip(),
            'address': self.address_input.text().strip(),
            'role': self.role_combo.currentText().strip()
        }
        
        # Add password only if provided
        password = self.password_input.text()
        if password:
            data['password'] = password
        
        return data
