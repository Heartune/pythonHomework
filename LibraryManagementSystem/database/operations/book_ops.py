"""
Book database operations for the Library Management System.
"""

import sqlite3
from ..db_manager import get_connection, close_connection
from ..models.book import Book
from utils.logger import get_logger

logger = get_logger(__name__)

def create_book(title, author, isbn, publisher=None, publication_year=None,
                category=None, description=None, quantity=1):
    """
    Create a new book.
    
    Args:
        title (str): The book title.
        author (str): The book author.
        isbn (str): The book ISBN.
        publisher (str, optional): The book publisher.
        publication_year (int, optional): The publication year.
        category (str, optional): The book category.
        description (str, optional): The book description.
        quantity (int, optional): The total quantity of this book.
        
    Returns:
        int or None: The ID of the new book, or None if creation failed.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        INSERT INTO books (title, author, isbn, publisher, publication_year, category, description, quantity, available)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, author, isbn, publisher, publication_year, category, description, quantity, quantity))
        
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity error creating book: {e}")
        conn.rollback()
        return None
    except Exception as e:
        logger.error(f"Error creating book: {e}")
        conn.rollback()
        return None
    finally:
        close_connection()

def get_book_by_id(book_id):
    """
    Get a book by ID.
    
    Args:
        book_id (int): The book ID.
        
    Returns:
        Book or None: The book, or None if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
        row = cursor.fetchone()
        
        return Book.from_row(row) if row else None
    except Exception as e:
        logger.error(f"Error getting book by ID: {e}")
        return None
    finally:
        close_connection()

def get_book_by_isbn(isbn):
    """
    Get a book by ISBN.
    
    Args:
        isbn (str): The book ISBN.
        
    Returns:
        Book or None: The book, or None if not found.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM books WHERE isbn = ?', (isbn,))
        row = cursor.fetchone()
        
        return Book.from_row(row) if row else None
    except Exception as e:
        logger.error(f"Error getting book by ISBN: {e}")
        return None
    finally:
        close_connection()

def get_all_books():
    """
    Get all books.
    
    Returns:
        list: A list of Book objects.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM books ORDER BY title')
        rows = cursor.fetchall()
        
        return [Book.from_row(row) for row in rows]
    except Exception as e:
        logger.error(f"Error getting all books: {e}")
        return []
    finally:
        close_connection()

def search_books(query, search_by='title'):
    """
    Search for books.
    
    Args:
        query (str): The search query.
        search_by (str, optional): The field to search by ('title', 'author', 'isbn', 'category').
        
    Returns:
        list: A list of Book objects matching the search criteria.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Determine the field to search by
        if search_by == 'title':
            field = 'title'
        elif search_by == 'author':
            field = 'author'
        elif search_by == 'isbn':
            field = 'isbn'
        elif search_by == 'category':
            field = 'category'
        else:
            logger.warning(f"Invalid search_by value: {search_by}")
            return []
        
        # Perform the search
        cursor.execute(f'''
        SELECT * FROM books
        WHERE {field} LIKE ?
        ORDER BY title
        ''', (f'%{query}%',))
        
        rows = cursor.fetchall()
        
        return [Book.from_row(row) for row in rows]
    except Exception as e:
        logger.error(f"Error searching books: {e}")
        return []
    finally:
        close_connection()

def update_book(book_id, title=None, author=None, isbn=None, publisher=None,
                publication_year=None, category=None, description=None, quantity=None):
    """
    Update a book.
    
    Args:
        book_id (int): The book ID.
        title (str, optional): The book title.
        author (str, optional): The book author.
        isbn (str, optional): The book ISBN.
        publisher (str, optional): The book publisher.
        publication_year (int, optional): The publication year.
        category (str, optional): The book category.
        description (str, optional): The book description.
        quantity (int, optional): The total quantity of this book.
        
    Returns:
        bool: True if the update was successful, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Get the current book data
        cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Book with ID {book_id} not found")
            return False
        
        # Prepare the update data
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if author is not None:
            update_data['author'] = author
        if isbn is not None:
            update_data['isbn'] = isbn
        if publisher is not None:
            update_data['publisher'] = publisher
        if publication_year is not None:
            update_data['publication_year'] = publication_year
        if category is not None:
            update_data['category'] = category
        if description is not None:
            update_data['description'] = description
        if quantity is not None:
            # Calculate the new available count
            current_quantity = row['quantity']
            current_available = row['available']
            borrowed = current_quantity - current_available
            
            if quantity < borrowed:
                logger.warning(f"Cannot set quantity to {quantity} because {borrowed} books are borrowed")
                return False
            
            update_data['quantity'] = quantity
            update_data['available'] = quantity - borrowed
        
        if not update_data:
            logger.warning("No data to update")
            return True
        
        # Build the SQL query
        set_clause = ', '.join([f"{key} = ?" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(book_id)
        
        cursor.execute(f'''
        UPDATE books
        SET {set_clause}
        WHERE book_id = ?
        ''', values)
        
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        logger.error(f"Integrity error updating book: {e}")
        conn.rollback()
        return False
    except Exception as e:
        logger.error(f"Error updating book: {e}")
        conn.rollback()
        return False
    finally:
        close_connection()

def delete_book(book_id):
    """
    Delete a book.
    
    Args:
        book_id (int): The book ID.
        
    Returns:
        bool: True if the deletion was successful, False otherwise.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Check if the book exists
        cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
        row = cursor.fetchone()
        
        if not row:
            logger.warning(f"Book with ID {book_id} not found")
            return False
        
        # Check if the book has any active transactions
        cursor.execute('''
        SELECT * FROM transactions
        WHERE book_id = ? AND status = 'borrowed'
        ''', (book_id,))
        
        if cursor.fetchone():
            logger.warning(f"Book with ID {book_id} has active transactions")
            return False
        
        # Delete the book
        cursor.execute('DELETE FROM books WHERE book_id = ?', (book_id,))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Error deleting book: {e}")
        conn.rollback()
        return False
    finally:
        close_connection()
