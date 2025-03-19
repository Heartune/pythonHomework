"""
Book handler for the Library Management System.
"""

# Import modules
from LibraryManagementSystem.utils.logger import get_logger
from LibraryManagementSystem.server.handlers.auth_handler import verify_auth
from LibraryManagementSystem.database.operations.book_ops import (
    add_book, get_book_by_id, get_all_books, update_book,
    delete_book, search_books
)

logger = get_logger(__name__)

def handle_book_request(action, data, token):
    """
    Handle a book-related request.
    
    Args:
        action (str): The action to perform.
        data (dict): The request data.
        token (str): The authentication token.
        
    Returns:
        tuple: (success, message, data)
    """
    try:
        # Verify authentication
        success, user_id, role = verify_auth(token)
        
        if not success:
            return False, "Authentication required", {}
        
        # Handle the action
        if action == 'book_add':
            # Verify admin role
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract book data from the data field
            book_data = data.get('data', {})
            title = book_data.get('title')
            author = book_data.get('author')
            isbn = book_data.get('isbn')
            publisher = book_data.get('publisher')
            publication_year = book_data.get('publication_year')
            category = book_data.get('category')
            description = book_data.get('description')
            quantity = book_data.get('quantity', 1)
            
            # Validate required fields
            if not title or not author or not isbn:
                return False, "Title, author, and ISBN are required", {}
            
            # Add the book
            book = add_book(
                title=title,
                author=author,
                isbn=isbn,
                publisher=publisher,
                publication_year=publication_year,
                category=category,
                description=description,
                quantity=quantity
            )
            
            if not book:
                return False, "Failed to add book", {}
            
            # Return the book data
            return True, "Book added successfully", book.to_dict()
        
        elif action == 'book_get':
            # Extract book ID
            book_id = data.get('book_id')
            
            if not book_id:
                return False, "Book ID is required", {}
            
            # Get the book
            book = get_book_by_id(book_id)
            
            if not book:
                return False, f"Book with ID {book_id} not found", {}
            
            # Return the book data
            return True, "Book retrieved successfully", book.to_dict()
        
        elif action == 'book_get_all':
            # Get all books
            books = get_all_books()
            
            # Convert books to dict format
            book_dicts = [book.to_dict() for book in books]
            
            # Log for debugging
            logger.info(f"Retrieved {len(books)} books with token {token}")
            
            return True, f"{len(books)} books retrieved", book_dicts
        
        elif action == 'book_search':
            # Extract search parameters
            search_term = data.get('search_term', '')
            
            # Search for books
            books = search_books(search_term)
            
            # Return the search results
            return True, f"{len(books)} books found", [book.to_dict() for book in books]
        
        elif action == 'book_update':
            # Verify admin role
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract book data
            book_id = data.get('book_id')
            book_data = data.get('data', {})
            book = data.get('book', {})
            
            # Log the incoming data for debugging
            logger.info(f"Book update request: book_id={book_id}, book={book}, data={book_data}")
            
            # Try to get data from both possible sources
            title = book.get('title') or book_data.get('title')
            author = book.get('author') or book_data.get('author')
            isbn = book.get('isbn') or book_data.get('isbn')
            publisher = book.get('publisher') or book_data.get('publisher')
            publication_year = book.get('publication_year') or book_data.get('publication_year')
            category = book.get('category') or book_data.get('category')
            description = book.get('description') or book_data.get('description')
            quantity = book.get('quantity') or book_data.get('quantity')
            
            if not book_id:
                return False, "Book ID is required", {}
            
            # Get the book
            existing_book = get_book_by_id(book_id)
            
            if not existing_book:
                return False, f"Book with ID {book_id} not found", {}
            
            # Update the book
            updated_book = update_book(
                book_id=book_id,
                title=title,
                author=author,
                isbn=isbn,
                publisher=publisher,
                publication_year=publication_year,
                category=category,
                description=description,
                quantity=quantity
            )
            
            if not updated_book:
                return False, "Failed to update book", {}
            
            # Return the updated book data
            return True, "Book updated successfully", updated_book.to_dict()
        
        elif action == 'book_delete':
            # Verify admin role
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract book ID
            book_id = data.get('book_id')
            
            if not book_id:
                return False, "Book ID is required", {}
            
            # Get the book
            book = get_book_by_id(book_id)
            
            if not book:
                return False, f"Book with ID {book_id} not found", {}
            
            # Delete the book
            success = delete_book(book_id)
            
            if not success:
                return False, "Failed to delete book", {}
            
            # Return success
            return True, "Book deleted successfully", {}
        
        else:
            return False, f"Unknown action: {action}", {}
    except Exception as e:
        logger.error(f"Error handling book request: {e}")
        return False, f"Error: {str(e)}", {}
