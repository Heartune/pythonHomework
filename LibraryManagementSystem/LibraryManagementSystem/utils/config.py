"""
Configuration utility for the Library Management System.
"""

import os

# Server configuration
SERVER_HOST = 'localhost'
SERVER_PORT = 9000
MAX_CONNECTIONS = 5

# Database configuration
DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'database', 'library.db')

# Security configuration
PASSWORD_SALT = 'library_management_system'
TOKEN_SECRET = 'library_management_system_token'
TOKEN_EXPIRY = 24 * 60 * 60  # 24 hours

# Logging configuration
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs', 'library.log')

# Web scraping configuration
SCRAPING_INTERVAL = 24 * 60 * 60  # 24 hours
SCRAPING_SOURCES = [
    'https://www.goodreads.com/list/show/1.Best_Books_Ever',
    'https://www.goodreads.com/list/show/264.Books_That_Everyone_Should_Read_At_Least_Once'
]
