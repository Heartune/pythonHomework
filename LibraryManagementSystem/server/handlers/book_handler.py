"""
Book handler for the Library Management System server.
"""

from database.operations.book_ops import (
    create_book, get_book_by_id, get_book_by_isbn, get_all_books,
    search_books, update_book, delete_book
)
from database.operations.transaction_ops import (
    create_transaction, get_transactions_by_book, return_book
)
from .auth_handler import verify_authentication
from utils.logger import get_logger

logger = get_logger(__name__)

def handle_book_request(action, data, token):
    """
    Handle a book-related request.
    
    Args:
        action (str): The action to perform.
        data (dict): The request data.
        token (str): The authentication token.
        
    Returns:
        tuple: (success, message, result_data)
    """
    try:
        # Verify authentication
        authenticated, user_id, role = verify_authentication(token)
        
        if not authenticated:
            return False, "Authentication required", {}
        
        # Handle the request based on the action
        if action == 'book_create':
            # Only admins can create books
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract book data
            title = data.get('title')
            author = data.get('author')
            isbn = data.get('isbn')
            publisher = data.get('publisher')
            publication_year = data.get('publication_year')
            category = data.get('category')
            description = data.get('description')
            quantity = data.get('quantity', 1)
            
            # Validate required fields
            if not title or not author or not isbn:
                return False, "Title, author, and ISBN are required", {}
            
            # Create the book
            book_id = create_book(
                title, author, isbn, publisher, publication_year,
                category, description, quantity
            )
            
            if not book_id:
                return False, "Failed to create book", {}
            
            # Get the created book
            book = get_book_by_id(book_id)
            
            return True, "Book created successfully", book.to_dict()
        
        elif action == 'book_get':
            # Extract book ID
            book_id = data.get('book_id')
            
            if not book_id:
                return False, "Book ID is required", {}
            
            # Get the book
            book = get_book_by_id(book_id)
            
            if not book:
                return False, "Book not found", {}
            
            return True, "Book retrieved successfully", book.to_dict()
        
        elif action == 'book_get_by_isbn':
            # Extract ISBN
            isbn = data.get('isbn')
            
            if not isbn:
                return False, "ISBN is required", {}
            
            # Get the book
            book = get_book_by_isbn(isbn)
            
            if not book:
                return False, "Book not found", {}
            
            return True, "Book retrieved successfully", book.to_dict()
        
        elif action == 'book_get_all':
            # Get all books
            books = get_all_books()
            
            return True, f"{len(books)} books retrieved", [book.to_dict() for book in books]
        
        elif action == 'book_search':
            # Extract search parameters
            query = data.get('query')
            search_by = data.get('search_by', 'title')
            
            if not query:
                return False, "Search query is required", {}
            
            # Search for books
            books = search_books(query, search_by)
            
            return True, f"{len(books)} books found", [book.to_dict() for book in books]
        
        elif action == 'book_update':
            # Only admins can update books
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract book data
            book_id = data.get('book_id')
            title = data.get('title')
            author = data.get('author')
            isbn = data.get('isbn')
            publisher = data.get('publisher')
            publication_year = data.get('publication_year')
            category = data.get('category')
            description = data.get('description')
            quantity = data.get('quantity')
            
            if not book_id:
                return False, "Book ID is required", {}
            
            # Update the book
            success = update_book(
                book_id, title, author, isbn, publisher,
                publication_year, category, description, quantity
            )
            
            if not success:
                return False, "Failed to update book", {}
            
            # Get the updated book
            book = get_book_by_id(book_id)
            
            return True, "Book updated successfully", book.to_dict()
        
        elif action == 'book_delete':
            # Only admins can delete books
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract book ID
            book_id = data.get('book_id')
            
            if not book_id:
                return False, "Book ID is required", {}
            
            # Delete the book
            success = delete_book(book_id)
            
            if not success:
                return False, "Failed to delete book", {}
            
            return True, "Book deleted successfully", {}
        
        elif action == 'book_borrow':
            # Extract book ID
            book_id = data.get('book_id')
            loan_period_days = data.get('loan_period_days', 14)
            
            if not book_id:
                return False, "Book ID is required", {}
            
            # Check if the book exists and is available
            book = get_book_by_id(book_id)
            
            if not book:
                return False, "Book not found", {}
            
            if not book.is_available():
                return False, "Book is not available", {}
            
            # Create a transaction
            transaction_id = create_transaction(user_id, book_id, loan_period_days)
            
            if not transaction_id:
                return False, "Failed to borrow book", {}
            
            return True, "Book borrowed successfully", {'transaction_id': transaction_id}
        
        elif action == 'book_return':
            # Extract transaction ID
            transaction_id = data.get('transaction_id')
            
            if not transaction_id:
                return False, "Transaction ID is required", {}
            
            # Return the book
            success = return_book(transaction_id)
            
            if not success:
                return False, "Failed to return book", {}
            
            return True, "Book returned successfully", {}
        
        elif action == 'book_get_transactions':
            # Only admins can view all transactions for a book
            if role != 'admin':
                return False, "Admin privileges required", {}
            
            # Extract book ID
            book_id = data.get('book_id')
            status = data.get('status')
            
            if not book_id:
                return False, "Book ID is required", {}
            
            # Get transactions
            transactions = get_transactions_by_book(book_id, status)
            
            return True, f"{len(transactions)} transactions retrieved", [t.to_dict() for t in transactions]
        
        else:
            return False, f"Unknown action: {action}", {}
    except Exception as e:
        logger.error(f"Error handling book request: {e}")
        return False, f"Server error: {str(e)}", {}
