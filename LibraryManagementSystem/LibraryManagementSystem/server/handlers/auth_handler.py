"""
Authentication handler for the Library Management System.
"""

import time
import json

# Import modules
from LibraryManagementSystem.utils.logger import get_logger
from LibraryManagementSystem.utils.security import generate_token, verify_token
from LibraryManagementSystem.database.operations.user_ops import authenticate_user, get_user_by_id

logger = get_logger(__name__)

def handle_login(username, password):
    """
    Handle a login request.
    
    Args:
        username (str): The username.
        password (str): The password.
        
    Returns:
        tuple: (success, message, data)
    """
    try:
        # Validate input
        if not username or not password:
            return False, "Username and password are required", {}
        
        # Authenticate the user
        user = authenticate_user(username, password)
        
        if not user:
            return False, "Invalid username or password", {}
        
        # Generate a token
        token = generate_token(user.user_id, user.role)
        
        # Return the user data
        return True, "Login successful", {
            'user_id': user.user_id,
            'username': user.username,
            'role': user.role,
            'full_name': user.full_name,
            'email': user.email,
            'token': token
        }
    except Exception as e:
        logger.error(f"Error handling login: {e}")
        return False, f"Error: {str(e)}", {}

def handle_logout(token):
    """
    Handle a logout request.
    
    Args:
        token (str): The authentication token.
        
    Returns:
        tuple: (success, message)
    """
    try:
        # Validate input
        if not token:
            return False, "Token is required"
        
        # Verify the token
        payload = verify_token(token)
        
        if not payload:
            return False, "Invalid token"
        
        # Return success
        return True, "Logout successful"
    except Exception as e:
        logger.error(f"Error handling logout: {e}")
        return False, f"Error: {str(e)}"

def verify_auth(token, required_role=None):
    """
    Verify an authentication token.
    
    Args:
        token (str): The authentication token.
        required_role (str): The required role.
        
    Returns:
        tuple: (success, user_id, role)
    """
    try:
        # Validate input
        if not token:
            return False, None, None
        
        # Verify the token
        payload = verify_token(token)
        
        if not payload:
            return False, None, None
        
        user_id = payload['user_id'] if 'user_id' in payload else None
        role = payload['role'] if 'role' in payload else None
        
        # Check if the user has the required role
        if required_role and role != required_role:
            return False, None, None
        
        # Return success
        return True, user_id, role
    except Exception as e:
        logger.error(f"Error verifying authentication: {e}")
        return False, None, None
