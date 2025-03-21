"""
Logging utility for the Library Management System.
"""

import logging
import os

# Try absolute imports first (when running as a package)
try:
    from LibraryManagementSystem.utils.config import LOG_LEVEL, LOG_FILE
except ImportError:
    # Fall back to relative imports (when running directly)
    try:
        from utils.config import LOG_LEVEL, LOG_FILE
    except ImportError:
        from .config import LOG_LEVEL, LOG_FILE

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name (str): The name of the logger.
        
    Returns:
        logging.Logger: A configured logger instance.
    """
    return logging.getLogger(name)
