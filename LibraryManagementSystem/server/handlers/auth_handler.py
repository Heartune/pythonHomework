"""
Authentication handler for the Library Management System server.
"""

from database.operations.user_ops import authenticate_user
from utils.security import generate_token, verify_token
from utils.logger import get_logger

logger = get_logger(__name__)

# Store active tokens
active_tokens = {}

def handle_login(username, password):
    """
    Handle a login request.
    
    Args:
        username (str): The username.
        password (str): The password.
        
    Returns:
        tuple: (success, message, user_data)
    """
    try:
        if not username or not password:
            return False, "Username and password are required", None
        
        # Authenticate the user
        user = authenticate_user(username, password)
        
        if not user:
            return False, "Invalid username or password", None
        
        # Generate a token
        token = generate_token(user.user_id, user.role)
        
        # Store the token
        active_tokens[token] = {
            'user_id': user.user_id,
            'role': user.role
        }
        
        # Prepare user data
        user_data = user.to_dict(include_password=False)
        user_data['token'] = token
        
        return True, "Login successful", user_data
    except Exception as e:
        logger.error(f"Error handling login: {e}")
        return False, f"Server error: {str(e)}", None

def handle_logout(token):
    """
    Handle a logout request.
    
    Args:
        token (str): The authentication token.
        
    Returns:
        tuple: (success, message)
    """
    try:
        if not token:
            return False, "Authentication token is required"
        
        # Check if the token is active
        if token in active_tokens:
            # Remove the token
            del active_tokens[token]
            return True, "Logout successful"
        
        return False, "Invalid or expired token", None
    except Exception as e:
        logger.error(f"Error handling logout: {e}")
        return False, f"Server error: {str(e)}"

def verify_authentication(token, required_role=None):
    """
    Verify authentication.
    
    Args:
        token (str): The authentication token.
        required_role (str, optional): The required role.
        
    Returns:
        tuple: (success, user_id, role)
    """
    try:
        if not token:
            return False, None, None
        
        # Check if the token is active
        if token in active_tokens:
            user_id = active_tokens[token]['user_id']
            role = active_tokens[token]['role']
            
            # Check if the user has the required role
            if required_role and role != required_role:
                return False, user_id, role
            
            return True, user_id, role
        
        # Verify the token
        payload = verify_token(token)
        
        if not payload:
            return False, None, None
        
        user_id = payload.get('user_id')
        role = payload.get('role')
        
        # Check if the user has the required role
        if required_role and role != required_role:
            return False, user_id, role
        
        # Store the token
        active_tokens[token] = {
            'user_id': user_id,
            'role': role
        }
        
        return True, user_id, role
    except Exception as e:
        logger.error(f"Error verifying authentication: {e}")
        return False, None, None
