"""
Client entry point for the Library Management System.
"""

import sys
import os
from utils.fix_qt_font_error import create_application  # Import the fix
import importlib.util

# Add project root to path for direct execution
if __name__ == '__main__':
    import sys
    import os
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# Try absolute imports first (when running as a package)
try:
    from LibraryManagementSystem.client.gui.login_window import LoginWindow
    from LibraryManagementSystem.client.gui.admin_window import AdminWindow
    from LibraryManagementSystem.client.gui.user_window import UserWindow
    from LibraryManagementSystem.client.network.client import Client
    from LibraryManagementSystem.utils.logger import get_logger
    from LibraryManagementSystem.utils.config import SERVER_HOST, SERVER_PORT
except ImportError:
    # Fall back to relative imports (when running directly)
    try:
        from client.gui.login_window import LoginWindow
        from client.gui.admin_window import AdminWindow
        from client.gui.user_window import UserWindow
        from client.network.client import Client
        from utils.logger import get_logger
        from utils.config import SERVER_HOST, SERVER_PORT
    except ImportError:
        # Last resort: try relative import
        from .gui.login_window import LoginWindow
        from .gui.admin_window import AdminWindow
        from .gui.user_window import UserWindow
        from .network.client import Client
        from utils.logger import get_logger
        from utils.config import SERVER_HOST, SERVER_PORT

logger = get_logger(__name__)

def main():
    """Main entry point for the client application."""
    try:
        # Create a client instance
        client = Client(SERVER_HOST, SERVER_PORT)
        
        # Create the Qt application
        app = create_application(sys.argv)  # Use the fixed application creator
        
        # Create the login window
        login_window = LoginWindow(client)
        
        # Create admin and user windows (hidden initially)
        admin_window = AdminWindow(client, {})
        user_window = UserWindow(client, {})
        
        # Connect login window signals
        def handle_login_successful(user_data):
            """Handle successful login."""
            # Hide the login window
            login_window.hide()
            
            # Show the appropriate window based on user role
            if user_data.get('role') == 'admin':
                # Update admin window with user data
                admin_window.user_data = user_data
                admin_window.show()
            else:
                # Update user window with user data
                user_window.user_data = user_data
                user_window.show()
        
        # Connect logout signals
        def handle_logout():
            """Handle logout."""
            # Hide the windows
            admin_window.hide()
            user_window.hide()
            
            # Show the login window
            login_window.show()
        
        # Connect signals
        login_window.login_successful.connect(handle_login_successful)
        admin_window.logout_requested.connect(handle_logout)
        user_window.logout_requested.connect(handle_logout)
        
        # Show the login window
        login_window.show()
        
        # Start the application event loop
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Error in client main: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
