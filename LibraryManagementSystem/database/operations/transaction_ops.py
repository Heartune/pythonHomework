"""
Transaction database operations for the Library Management System.
"""

import sqlite3
from datetime import datetime, timedelta
from ..db_manager import get_connection, close_connection
from ..models.transaction import Transaction
from utils.logger import get_logger

logger = get_logger(__name__)

def create_transaction(user_id, book_id, loan_period_days=14):
    """
    Create a new transaction (borrow a book).
    
    Args:
        user_id (int): The user ID.
        book_id (int): The book ID.
        loan_period_days (int, optional): The loan period in days.
        
    Returns:
        int or None: The ID of the new transaction, or None if creation failed.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if the book is available
        cursor.execute('SELECT available FROM books WHERE book_id = ?', (book_id,))
        row = cursor.fetchone()
        
        if not row or row['available'] <= 0:
            logger.warning(f"Book with ID {book_id} is not available")
            return None
        
        # Calculate the due date
        borrow_date = datetime.now().isoformat()
        due_date = (datetime.now() + timedelta(days=loan_period_days)).isoformat()
        
        # Create the transaction
        cursor.execute('''
        INSERT INTO transactions (user_id, book_id, borrow_date, due_date, status)
        VALUES (?, ?, ?, ?, ?)
        ''', (user_id, book_id, borrow_date, due_date, Transaction.STATUS_BORROWED))
        
        transaction_id = cursor.lastrowid
        
        conn.commit()
        return transaction_id
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity error creating transaction: {e}")
        conn.rollback()
        return None
    except Exception as e:
        logger.error(f"Error creating transaction: {e}")
        conn.rollback()
        return None
    finally:
        close_connection()

def get_transaction_by_id(transaction_id):
    """
    Get a transaction by ID.
    
    Args:
        transaction_id (int): The transaction ID.
        
    Returns:
        Transaction or None: The transaction, or None if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM transactions WHERE transaction_id = ?', (transaction_id,))
        row = cursor.fetchone()
        
        return Transaction.from_row(row) if row else None
    except Exception as e:
        logger.error(f"Error getting transaction by ID: {e}")
        return None
    finally:
        close_connection()

def get_transactions_by_user(user_id, status=None):
    """
    Get transactions by user ID.
    
    Args:
        user_id (int): The user ID.
        status (str, optional): The transaction status to filter by.
        
    Returns:
        list: A list of Transaction objects.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
            SELECT * FROM transactions
            WHERE user_id = ? AND status = ?
            ORDER BY borrow_date DESC
            ''', (user_id, status))
        else:
            cursor.execute('''
            SELECT * FROM transactions
            WHERE user_id = ?
            ORDER BY borrow_date DESC
            ''', (user_id,))
        
        rows = cursor.fetchall()
        
        return [Transaction.from_row(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting transactions by user: {e}")
        return []
    finally:
        close_connection()

def get_transactions_by_book(book_id, status=None):
    """
    Get transactions by book ID.
    
    Args:
        book_id (int): The book ID.
        status (str, optional): The transaction status to filter by.
        
    Returns:
        list: A list of Transaction objects.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
            SELECT * FROM transactions
            WHERE book_id = ? AND status = ?
            ORDER BY borrow_date DESC
            ''', (book_id, status))
        else:
            cursor.execute('''
            SELECT * FROM transactions
            WHERE book_id = ?
            ORDER BY borrow_date DESC
            ''', (book_id,))
        
        rows = cursor.fetchall()
        
        return [Transaction.from_row(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting transactions by book: {e}")
        return []
    finally:
        close_connection()

def get_all_transactions(status=None):
    """
    Get all transactions.
    
    Args:
        status (str, optional): The transaction status to filter by.
        
    Returns:
        list: A list of Transaction objects.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute('''
            SELECT * FROM transactions
            WHERE status = ?
            ORDER BY borrow_date DESC
            ''', (status,))
        else:
            cursor.execute('''
            SELECT * FROM transactions
            ORDER BY borrow_date DESC
            ''')
        
        rows = cursor.fetchall()
        
        return [Transaction.from_row(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting all transactions: {e}")
        return []
    finally:
        close_connection()

def return_book(transaction_id):
    """
    Return a book.
    
    Args:
        transaction_id (int): The transaction ID.
        
    Returns:
        bool: True if the return was successful, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if the transaction exists and is in 'borrowed' status
        cursor.execute('''
        SELECT * FROM transactions
        WHERE transaction_id = ?
        ''', (transaction_id,))
        
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Transaction with ID {transaction_id} not found")
            return False
        
        if row['status'] != Transaction.STATUS_BORROWED:
            logger.warning(f"Transaction with ID {transaction_id} is not in 'borrowed' status")
            return False
        
        # Update the transaction
        return_date = datetime.now().isoformat()
        
        cursor.execute('''
        UPDATE transactions
        SET return_date = ?, status = ?
        WHERE transaction_id = ?
        ''', (return_date, Transaction.STATUS_RETURNED, transaction_id))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error returning book: {e}")
        conn.rollback()
        return False
    finally:
        close_connection()

def update_overdue_transactions():
    """
    Update the status of overdue transactions.
    
    Returns:
        int: The number of transactions updated.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get current date
        current_date = datetime.now().isoformat()
        
        # Update transactions that are overdue
        cursor.execute('''
        UPDATE transactions
        SET status = ?
        WHERE status = ? AND due_date < ? AND return_date IS NULL
        ''', (Transaction.STATUS_OVERDUE, Transaction.STATUS_BORROWED, current_date))
        
        count = cursor.rowcount
        
        conn.commit()
        return count
    except Exception as e:
        logger.error(f"Error updating overdue transactions: {e}")
        conn.rollback()
        return 0
    finally:
        close_connection()

def get_transaction_details(transaction_id):
    """
    Get detailed information about a transaction, including user and book details.
    
    Args:
        transaction_id (int): The transaction ID.
        
    Returns:
        dict or None: A dictionary containing transaction, user, and book details, or None if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT t.*, u.username, u.full_name, b.title, b.author, b.isbn
        FROM transactions t
        JOIN users u ON t.user_id = u.user_id
        JOIN books b ON t.book_id = b.book_id
        WHERE t.transaction_id = ?
        ''', (transaction_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return {
            'transaction_id': row['transaction_id'],
            'user_id': row['user_id'],
            'book_id': row['book_id'],
            'borrow_date': row['borrow_date'],
            'due_date': row['due_date'],
            'return_date': row['return_date'],
            'status': row['status'],
            'username': row['username'],
            'full_name': row['full_name'],
            'book_title': row['title'],
            'book_author': row['author'],
            'book_isbn': row['isbn']
        }
    except Exception as e:
        logger.error(f"Error getting transaction details: {e}")
        return None
    finally:
        close_connection()
