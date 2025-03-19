"""
Book model for the Library Management System.
"""

from utils.logger import get_logger

logger = get_logger(__name__)

class Book:
    """Book model representing a library book."""
    
    def __init__(self, book_id=None, title=None, author=None, isbn=None,
                 publisher=None, publication_year=None, category=None,
                 description=None, quantity=1, available=1,
                 created_at=None, updated_at=None):
        """
        Initialize a Book object.
        
        Args:
            book_id (int, optional): The book ID.
            title (str, optional): The book title.
            author (str, optional): The book author.
            isbn (str, optional): The book ISBN.
            publisher (str, optional): The book publisher.
            publication_year (int, optional): The publication year.
            category (str, optional): The book category.
            description (str, optional): The book description.
            quantity (int, optional): The total quantity of this book.
            available (int, optional): The number of available copies.
            created_at (str, optional): The creation timestamp.
            updated_at (str, optional): The last update timestamp.
        """
        self.book_id = book_id
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.publication_year = publication_year
        self.category = category
        self.description = description
        self.quantity = quantity
        self.available = available
        self.created_at = created_at
        self.updated_at = updated_at
    
    @classmethod
    def from_row(cls, row):
        """
        Create a Book object from a database row.
        
        Args:
            row (sqlite3.Row): A database row.
            
        Returns:
            Book: A Book object.
        """
        if row is None:
            return None
        
        return cls(
            book_id=row['book_id'],
            title=row['title'],
            author=row['author'],
            isbn=row['isbn'],
            publisher=row['publisher'] if 'publisher' in row.keys() else None,
            publication_year=row['publication_year'] if 'publication_year' in row.keys() else None,
            category=row['category'] if 'category' in row.keys() else None,
            description=row['description'] if 'description' in row.keys() else None,
            quantity=row['quantity'],
            available=row['available'],
            created_at=row['created_at'],
            updated_at=row['updated_at']
        )
    
    def to_dict(self):
        """
        Convert the Book object to a dictionary.
        
        Returns:
            dict: A dictionary representation of the Book object.
        """
        return {
            'book_id': self.book_id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'publisher': self.publisher,
            'publication_year': self.publication_year,
            'category': self.category,
            'description': self.description,
            'quantity': self.quantity,
            'available': self.available,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    def is_available(self):
        """
        Check if the book is available for borrowing.
        
        Returns:
            bool: True if the book is available, False otherwise.
        """
        return self.available > 0
