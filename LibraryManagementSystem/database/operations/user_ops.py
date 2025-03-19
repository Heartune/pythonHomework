"""
User database operations for the Library Management System.
"""

import sqlite3
from ..db_manager import get_connection, close_connection
from ..models.user import User
from utils.logger import get_logger
from utils.security import hash_password

logger = get_logger(__name__)

def create_user(username, password, role, full_name, email, phone=None, address=None):
    """
    Create a new user.
    
    Args:
        username (str): The username.
        password (str): The password (will be hashed).
        role (str): The user role ('admin' or 'user').
        full_name (str): The user's full name.
        email (str): The user's email address.
        phone (str, optional): The user's phone number.
        address (str, optional): The user's address.
        
    Returns:
        int or None: The ID of the new user, or None if creation failed.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Hash the password
        hashed_password = hash_password(password)
        
        cursor.execute('''
        INSERT INTO users (username, password, role, full_name, email, phone, address)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (username, hashed_password, role, full_name, email, phone, address))
        
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity error creating user: {e}")
        conn.rollback()
        return None
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        conn.rollback()
        return None
    finally:
        close_connection()

def get_user_by_id(user_id):
    """
    Get a user by ID.
    
    Args:
        user_id (int): The user ID.
        
    Returns:
        User or None: The user, or None if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        return User.from_row(row) if row else None
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None
    finally:
        close_connection()

def get_user_by_username(username):
    """
    Get a user by username.
    
    Args:
        username (str): The username.
        
    Returns:
        User or None: The user, or None if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        row = cursor.fetchone()
        
        return User.from_row(row) if row else None
    except Exception as e:
        logger.error(f"Error getting user by username: {e}")
        return None
    finally:
        close_connection()

def get_all_users():
    """
    Get all users.
    
    Returns:
        list: A list of User objects.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users ORDER BY username')
        rows = cursor.fetchall()
        
        return [User.from_row(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting all users: {e}")
        return []
    finally:
        close_connection()

def update_user(user_id, username=None, password=None, role=None, 
                full_name=None, email=None, phone=None, address=None):
    """
    Update a user.
    
    Args:
        user_id (int): The user ID.
        username (str, optional): The username.
        password (str, optional): The password (will be hashed).
        role (str, optional): The user role ('admin' or 'user').
        full_name (str, optional): The user's full name.
        email (str, optional): The user's email address.
        phone (str, optional): The user's phone number.
        address (str, optional): The user's address.
        
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get the current user data
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"User with ID {user_id} not found")
            return False
        
        # Prepare the update data
        update_data = {}
        if username is not None:
            update_data['username'] = username
        if password is not None:
            update_data['password'] = hash_password(password)
        if role is not None:
            update_data['role'] = role
        if full_name is not None:
            update_data['full_name'] = full_name
        if email is not None:
            update_data['email'] = email
        if phone is not None:
            update_data['phone'] = phone
        if address is not None:
            update_data['address'] = address
        
        if not update_data:
            logger.warning("No data to update")
            return True
        
        # Build the SQL query
        set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(user_id)
        
        cursor.execute(f'''
        UPDATE users
        SET {set_clause}
        WHERE user_id = ?
        ''', values)
        
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity error updating user: {e}")
        conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Error updating user: {e}")
        conn.rollback()
        return False
    finally:
        close_connection()

def delete_user(user_id):
    """
    Delete a user.
    
    Args:
        user_id (int): The user ID.
        
    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if the user exists
        cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"User with ID {user_id} not found")
            return False
        
        # Check if the user has any active transactions
        cursor.execute('''
        SELECT * FROM transactions
        WHERE user_id = ? AND status = 'borrowed'
        ''', (user_id,))
        
        if cursor.fetchone():
            logger.warning(f"User with ID {user_id} has active transactions")
            return False
        
        # Delete the user
        cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error deleting user: {e}")
        conn.rollback()
        return False
    finally:
        close_connection()

def authenticate_user(username, password):
    """
    Authenticate a user.
    
    Args:
        username (str): The username.
        password (str): The password.
        
    Returns:
        User or None: The authenticated user, or None if authentication failed.
    """
    try:
        user = get_user_by_username(username)
        logger.debug(f"Authentication attempt for user '{username}': User found = {user is not None}")
        
        if user and user.verify_password(password):
            logger.debug(f"Password verification successful for user '{username}'")
            return user
        
        logger.debug(f"Password verification failed for user '{username}'")
        return None
    except Exception as e:
        logger.error(f"Error authenticating user: {e}")
        return None
