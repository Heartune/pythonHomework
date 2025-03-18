"""
User model for the Library Management System.
"""

from utils.logger import get_logger
from utils.security import hash_password, verify_password

logger = get_logger(__name__)

class User:
    """User model representing a library system user."""
    
    def __init__(self, user_id=None, username=None, password=None, role=None, 
                 full_name=None, email=None, phone=None, address=None,
                 created_at=None, updated_at=None):
        """
        Initialize a User object.
        
        Args:
            user_id (int, optional): The user ID.
            username (str, optional): The username.
            password (str, optional): The password (hashed).
            role (str, optional): The user role ('admin' or 'user').
            full_name (str, optional): The user's full name.
            email (str, optional): The user's email address.
            phone (str, optional): The user's phone number.
            address (str, optional): The user's address.
            created_at (str, optional): The creation timestamp.
            updated_at (str, optional): The last update timestamp.
        """
        self.user_id = user_id
        self.username = username
        self.password = password
        self.role = role
        self.full_name = full_name
        self.email = email
        self.phone = phone
        self.address = address
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_row(cls, row):
        """
        Create a User object from a database row.
        
        Args:
            row (sqlite3.Row): A database row.
            
        Returns:
            User: A User object.
        """
        if row is None:
            return None
        
        return cls(
            user_id=row['user_id'],
            username=row['username'],
            password=row['password'],
            role=row['role'],
            full_name=row['full_name'],
            email=row['email'],
            phone=row.get('phone'),
            address=row.get('address'),
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def to_dict(self, include_password=False):
        """
        Convert the User object to a dictionary.
        
        Args:
            include_password (bool, optional): Whether to include the password in the dictionary.
            
        Returns:
            dict: A dictionary representation of the User object.
        """
        result = {
            'user_id': self.user_id,
            'username': self.username,
            'role': self.role,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
        if include_password:
            result['password'] = self.password
        
        return result
    
    def set_password(self, password):
        """
        Set the user's password (hashed).
        
        Args:
            password (str): The password to set.
        """
        self.password = hash_password(password)
    
    def verify_password(self, password):
        """
        Verify the user's password.
        
        Args:
            password (str): The password to verify.
            
        Returns:
            bool: True if the password is correct, False otherwise.
        """
        return verify_password(password, self.password)
    
    def is_admin(self):
        """
        Check if the user is an admin.
        
        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        return self.role == 'admin'
