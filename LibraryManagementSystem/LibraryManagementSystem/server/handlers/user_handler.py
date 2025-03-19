"""
User handler for the Library Management System.
"""

# Import modules
from LibraryManagementSystem.utils.logger import get_logger
from LibraryManagementSystem.server.handlers.auth_handler import verify_auth
from LibraryManagementSystem.database.operations.user_ops import (
    add_user, get_user_by_id, get_all_users, update_user,
    delete_user, search_users
)

logger = get_logger(__name__)

def handle_user_request(action, data, token):
    """
    Handle a user-related request.
    
    Args:
        action (str): The action to perform.
        data (dict): The request data.
        token (str): The authentication token.
        
    Returns:
        tuple: (success, message, data)
    """
    try:
        # Verify authentication
        success, user_id, role = verify_auth(token)
        
        if not success:
            return False, "Authentication required", {}
        
        # Handle the action
        if action == 'user_add':
            # Verify admin role
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
            
            # Add the user
            user = add_user(
                username=username,
                password=password,
                role=role_new,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address
            )
            
            if not user:
                return False, "Failed to add user", {}
            
            # Return the user data
            return True, "User added successfully", user.to_dict()
        
        elif action == 'user_get':
            # Extract user ID
            target_user_id = data.get('user_id')
            
            if not target_user_id:
                return False, "User ID is required", {}
            
            # Get the user
            user = get_user_by_id(target_user_id)
            
            if not user:
                return False, f"User with ID {target_user_id} not found", {}
            
            # Check if the user has permission to view this user
            if role != 'admin' and user_id != target_user_id:
                return False, "Permission denied", {}
            
            # Return the user data
            return True, "User retrieved successfully", user.to_dict()
        
        elif action == 'user_get_all':
            # Verify admin role
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Get all users
            users = get_all_users()
            
            # Return the users data
            return True, f"{len(users)} users retrieved", [user.to_dict() for user in users]
        
        elif action == 'user_search':
            # Verify admin role
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract search parameters
            search_term = data.get('search_term', '')
            
            # Search for users
            users = search_users(search_term)
            
            # Return the search results
            return True, f"{len(users)} users found", [user.to_dict() for user in users]
        
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
            
            # Get the user
            existing_user = get_user_by_id(target_user_id)
            
            if not existing_user:
                return False, f"User with ID {target_user_id} not found", {}
            
            # Check if the user has permission to update this user
            if role != 'admin' and user_id != target_user_id:
                return False, "Permission denied", {}
            
            # If the user is trying to change the role, verify admin role
            if role_new and role_new != existing_user.role and role != 'admin':
                return False, "Admin privileges required to change role", {}
            
            # Update the user
            updated_user = update_user(
                user_id=target_user_id,
                username=username,
                password=password,
                role=role_new,
                full_name=full_name,
                email=email,
                phone=phone,
                address=address
            )
            
            if not updated_user:
                return False, "Failed to update user", {}
            
            # Return the updated user data
            return True, "User updated successfully", updated_user.to_dict()
        
        elif action == 'user_delete':
            # Verify admin role
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract user ID
            target_user_id = data.get('user_id')
            
            if not target_user_id:
                return False, "User ID is required", {}
            
            # Get the user
            user = get_user_by_id(target_user_id)
            
            if not user:
                return False, f"User with ID {target_user_id} not found", {}
            
            # Delete the user
            success = delete_user(target_user_id)
            
            if not success:
                return False, "Failed to delete user", {}
            
            # Return success
            return True, "User deleted successfully", {}
        
        else:
            return False, f"Unknown action: {action}", {}
    except Exception as e:
        logger.error(f"Error handling user request: {e}")
        return False, f"Error: {str(e)}", {}
