"""
User handler for the Library Management System server.
"""

from database.operations.user_ops import (
    create_user, get_user_by_id, get_user_by_username, get_all_users,
    update_user, delete_user
)
from database.operations.transaction_ops import get_transactions_by_user
from .auth_handler import verify_authentication
from utils.logger import get_logger

logger = get_logger(__name__)

def handle_user_request(action, data, token):
    """
    Handle a user-related request.
    
    Args:
        action (str): The action to perform.
        data (dict): The request data.
        token (str): The authentication token.
        
    Returns:
        tuple: (success, message, result_data)
    """
    try:
        # Verify authentication
        authenticated, user_id, role = verify_authentication(token)
        
        if not authenticated:
            return False, "Authentication required", {}
        
        # Handle the request based on the action
        if action == 'user_create':
            # Only admins can create users
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract user data from the data field
            user_data = data.get('data', {})
            username = user_data.get('username')
            password = user_data.get('password')
            role_new = user_data.get('role', 'user')
            full_name = user_data.get('full_name')
            email = user_data.get('email')
            phone = user_data.get('phone')
            address = user_data.get('address')
            
            # Validate required fields
            if not username or not password or not full_name or not email:
                return False, "Username, password, full name, and email are required", {}
            
            # Create the user
            new_user_id = create_user(
                username, password, role_new, full_name, email, phone, address
            )
            
            if not new_user_id:
                return False, "Failed to create user", {}
            
            # Get the created user
            user = get_user_by_id(new_user_id)
            
            return True, "User created successfully", user.to_dict(include_password=False)
        
        elif action == 'user_get':
            # Extract user ID
            target_user_id = data.get('user_id')
            
            if not target_user_id:
                return False, "User ID is required", {}
            
            # Regular users can only get their own information
            if role != 'admin' and int(target_user_id) != int(user_id):
                return False, "You can only access your own information", {}
            
            # Get the user
            user = get_user_by_id(target_user_id)
            
            if not user:
                return False, "User not found", {}
            
            return True, "User retrieved successfully", user.to_dict(include_password=False)
        
        elif action == 'user_get_by_username':
            # Only admins can get users by username
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract username
            username = data.get('username')
            
            if not username:
                return False, "Username is required", {}
            
            # Get the user
            user = get_user_by_username(username)
            
            if not user:
                return False, "User not found", {}
            
            return True, "User retrieved successfully", user.to_dict(include_password=False)
        
        elif action == 'user_get_all':
            # Only admins can get all users
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Get all users
            users = get_all_users()
            
            return True, f"{len(users)} users retrieved", [user.to_dict(include_password=False) for user in users]
        
        elif action == 'user_update':
            # Extract user data
            target_user_id = data.get('user_id')
            user_data = data.get('data', {})
            user = data.get('user', {})
            
            # Try to get data from both possible sources
            username = user.get('username') or user_data.get('username')
            password = user.get('password') or user_data.get('password')
            role_new = user.get('role') or user_data.get('role')
            full_name = user.get('full_name') or user_data.get('full_name')
            email = user.get('email') or user_data.get('email')
            phone = user.get('phone') or user_data.get('phone')
            address = user.get('address') or user_data.get('address')
            
            if not target_user_id:
                return False, "User ID is required", {}
            
            # Regular users can only update their own information and cannot change their role
            if role != 'admin':
                if int(target_user_id) != int(user_id):
                    return False, "You can only update your own information", {}
                
                # Regular users cannot change their role
                if role_new and role_new != role:
                    return False, "You cannot change your role", {}
            
            # Update the user
            success = update_user(
                target_user_id, username, password, role_new, full_name, email, phone, address
            )
            
            if not success:
                return False, "Failed to update user", {}
            
            # Get the updated user
            user = get_user_by_id(target_user_id)
            
            return True, "User updated successfully", user.to_dict(include_password=False)
        
        elif action == 'user_delete':
            # Only admins can delete users
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract user ID
            target_user_id = data.get('user_id')
            
            if not target_user_id:
                return False, "User ID is required", {}
            
            # Delete the user
            success = delete_user(target_user_id)
            
            if not success:
                return False, "Failed to delete user", {}
            
            return True, "User deleted successfully", {}
        
        elif action == 'user_get_transactions':
            # Extract user ID and status
            target_user_id = data.get('user_id')
            status = data.get('status')
            
            if not target_user_id:
                return False, "User ID is required", {}
            
            # Regular users can only get their own transactions
            if role != 'admin' and int(target_user_id) != int(user_id):
                return False, "You can only access your own transactions", {}
            
            # Get transactions
            transactions = get_transactions_by_user(target_user_id, status)
            
            return True, f"{len(transactions)} transactions retrieved", [t.to_dict() for t in transactions]
        
        else:
            return False, f"Unknown action: {action}", {}
    except Exception as e:
        logger.error(f"Error handling user request: {e}")
        return False, f"Server error: {str(e)}", {}
