"""
Configuration settings for the Library Management System.
"""

import os

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'database', 'library.db')
DATABASE_TIMEOUT = 30  # seconds

# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 9000
MAX_CONNECTIONS = 10
BUFFER_SIZE = 4096

# Security configuration
PASSWORD_SALT = 'library_management_system'  # In production, this should be a random string
TOKEN_EXPIRY = 3600  # seconds (1 hour)

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'library.log')

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
