"""
Main entry point for running the Library Management System as a package.
"""

import sys
import os

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import server and client modules
from LibraryManagementSystem.server import main as server_main
from LibraryManagementSystem.client import main as client_main

if __name__ == "__main__":
    # Start the server in a separate thread
    import threading
    server_thread = threading.Thread(target=server_main.main)
    server_thread.daemon = True
    server_thread.start()
    
    # Start the client
    client_main.main()
