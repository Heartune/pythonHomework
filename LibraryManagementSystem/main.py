"""
Main entry point for the Library Management System.
"""

import sys
import os
import argparse
from utils.logger import get_logger

logger = get_logger(__name__)

def start_client():
    """Start the client application."""
    try:
        from client.main import main as client_main
        client_main()
    except Exception as e:
        logger.error(f"Error starting client: {e}")
        sys.exit(1)

def start_server():
    """Start the server application."""
    try:
        from server.main import main as server_main
        server_main()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Library Management System')
    parser.add_argument('mode', choices=['client', 'server'], help='Start in client or server mode')
    
    args = parser.parse_args()
    
    if args.mode == 'client':
        start_client()
    elif args.mode == 'server':
        start_server()

if __name__ == '__main__':
    main()
