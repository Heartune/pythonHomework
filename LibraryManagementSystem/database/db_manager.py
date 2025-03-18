"""
Database connection manager for the Library Management System.
"""

import sqlite3
import threading
import os
import importlib.util

# Try absolute imports first (when running as a package)
try:
    from LibraryManagementSystem.utils.logger import get_logger
    from LibraryManagementSystem.utils.config import DATABASE_PATH, DATABASE_TIMEOUT
except ImportError:
    # Fall back to relative imports (when running directly)
    try:
        from utils.logger import get_logger
        from utils.config import DATABASE_PATH, DATABASE_TIMEOUT
    except ImportError:
        import sys
        # Add project root to path
        sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from utils.logger import get_logger
        from utils.config import DATABASE_PATH, DATABASE_TIMEOUT

logger = get_logger(__name__)

# Thread-local storage for database connections
local = threading.local()

def get_connection():
    """
    Get a database connection for the current thread.
    
    Returns:
        sqlite3.Connection: A database connection.
    """
    if not hasattr(local, 'connection'):
        # Create database directory if it doesn't exist
        os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
        
        # Create a new connection for this thread
        local.connection = sqlite3.connect(DATABASE_PATH, timeout=DATABASE_TIMEOUT)
        local.connection.row_factory = sqlite3.Row  # Return rows as dictionaries
        
        # Enable foreign keys
        local.connection.execute('PRAGMA foreign_keys = ON')
        
        logger.debug(f"Created new database connection for thread {threading.current_thread().name}")
    
    return local.connection

def close_connection():
    """Close the database connection for the current thread."""
    if hasattr(local, 'connection'):
        local.connection.close()
        delattr(local, 'connection')
        logger.debug(f"Closed database connection for thread {threading.current_thread().name}")

def initialize_database():
    """Initialize the database with the required tables."""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            address TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create books table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            isbn TEXT UNIQUE NOT NULL,
            publisher TEXT,
            publication_year INTEGER,
            category TEXT,
            description TEXT,
            quantity INTEGER NOT NULL DEFAULT 1,
            available INTEGER NOT NULL DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Create transactions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            borrow_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            due_date TIMESTAMP NOT NULL,
            return_date TIMESTAMP,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (book_id) REFERENCES books (book_id)
        )
        ''')
        
        # Create a trigger to update the 'updated_at' field in users table
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_users_timestamp
        AFTER UPDATE ON users
        FOR EACH ROW
        BEGIN
            UPDATE users SET updated_at = CURRENT_TIMESTAMP WHERE user_id = OLD.user_id;
        END;
        ''')
        
        # Create a trigger to update the 'updated_at' field in books table
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_books_timestamp
        AFTER UPDATE ON books
        FOR EACH ROW
        BEGIN
            UPDATE books SET updated_at = CURRENT_TIMESTAMP WHERE book_id = OLD.book_id;
        END;
        ''')
        
        # Create a trigger to update the 'available' field in books table when a book is borrowed
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_books_available_on_borrow
        AFTER INSERT ON transactions
        FOR EACH ROW
        WHEN NEW.status = 'borrowed'
        BEGIN
            UPDATE books SET available = available - 1 WHERE book_id = NEW.book_id;
        END;
        ''')
        
        # Create a trigger to update the 'available' field in books table when a book is returned
        cursor.execute('''
        CREATE TRIGGER IF NOT EXISTS update_books_available_on_return
        AFTER UPDATE ON transactions
        FOR EACH ROW
        WHEN NEW.status = 'returned' AND OLD.status = 'borrowed'
        BEGIN
            UPDATE books SET available = available + 1 WHERE book_id = NEW.book_id;
        END;
        ''')
        
        # Insert admin user if not exists
        cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role, full_name, email)
        VALUES ('admin', '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918', 'admin', 'Administrator', 'admin@library.com')
        ''')
        
        conn.commit()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
    finally:
        close_connection()
