"""
Server entry point for the Library Management System.
"""

import sys
import os
import threading

# Add project root to path for direct execution
if __name__ == '__main__':
    import sys
    import os
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

# Import modules
from LibraryManagementSystem.server.network.server import Server
from LibraryManagementSystem.utils.logger import get_logger
from LibraryManagementSystem.utils.config import SERVER_HOST, SERVER_PORT, MAX_CONNECTIONS
from LibraryManagementSystem.database.db_manager import initialize_database

logger = get_logger(__name__)

def main():
    """Main entry point for the server application."""
    try:
        # Initialize the database
        initialize_database()
        
        # Create and start the server
        server = Server(SERVER_HOST, SERVER_PORT, MAX_CONNECTIONS)
        server_thread = threading.Thread(target=server.start)
        server_thread.daemon = True
        server_thread.start()
        
        logger.info(f"Server started on {SERVER_HOST}:{SERVER_PORT}")
        
        # Keep the main thread running
        try:
            while True:
                cmd = input("Enter 'quit' to stop the server: ")
                if cmd.lower() == 'quit':
                    break
        except KeyboardInterrupt:
            pass
        
        # Stop the server
        server.stop()
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Error in server main: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
