"""
Transaction model for the Library Management System.
"""

from datetime import datetime, timedelta
from utils.logger import get_logger

logger = get_logger(__name__)

class Transaction:
    """Transaction model representing a book borrowing/returning transaction."""
    
    # Transaction status constants
    STATUS_BORROWED = 'borrowed'
    STATUS_RETURNED = 'returned'
    STATUS_OVERDUE = 'overdue'
    
    def __init__(self, transaction_id=None, user_id=None, book_id=None,
                 borrow_date=None, due_date=None, return_date=None,
                 status=None):
        """
        Initialize a Transaction object.
        
        Args:
            transaction_id (int, optional): The transaction ID.
            user_id (int, optional): The user ID.
            book_id (int, optional): The book ID.
            borrow_date (str, optional): The borrow date.
            due_date (str, optional): The due date.
            return_date (str, optional): The return date.
            status (str, optional): The transaction status.
        """
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.book_id = book_id
        self.borrow_date = borrow_date
        self.due_date = due_date
        self.return_date = return_date
        self.status = status
    
    @classmethod
    def from_row(cls, row):
        """
        Create a Transaction object from a database row.
        
        Args:
            row (sqlite3.Row): A database row.
            
        Returns:
            Transaction: A Transaction object.
        """
        if row is None:
            return None
        
        return cls(
            transaction_id=row['transaction_id'],
            user_id=row['user_id'],
            book_id=row['book_id'],
            borrow_date=row['borrow_date'],
            due_date=row['due_date'],
            return_date=row.get('return_date'),
            status=row['status']
        )
    
    def to_dict(self):
        """
        Convert the Transaction object to a dictionary.
        
        Returns:
            dict: A dictionary representation of the Transaction object.
        """
        return {
            'transaction_id': self.transaction_id,
            'user_id': self.user_id,
            'book_id': self.book_id,
            'borrow_date': self.borrow_date,
            'due_date': self.due_date,
            'return_date': self.return_date,
            'status': self.status
        }
    
    @staticmethod
    def calculate_due_date(borrow_date, loan_period_days=14):
        """
        Calculate the due date based on the borrow date and loan period.
        
        Args:
            borrow_date (str or datetime): The borrow date.
            loan_period_days (int, optional): The loan period in days.
            
        Returns:
            str: The due date in ISO format.
        """
        if isinstance(borrow_date, str):
            borrow_date = datetime.fromisoformat(borrow_date.replace('Z', '+00:00'))
        
        due_date = borrow_date + timedelta(days=loan_period_days)
        return due_date.isoformat()
    
    def is_overdue(self, current_date=None):
        """
        Check if the transaction is overdue.
        
        Args:
            current_date (str or datetime, optional): The current date.
            
        Returns:
            bool: True if the transaction is overdue, False otherwise.
        """
        if self.status == self.STATUS_RETURNED:
            return False
        
        if current_date is None:
            current_date = datetime.now()
        elif isinstance(current_date, str):
            current_date = datetime.fromisoformat(current_date.replace('Z', '+00:00'))
        
        due_date = datetime.fromisoformat(self.due_date.replace('Z', '+00:00'))
        return current_date > due_date
