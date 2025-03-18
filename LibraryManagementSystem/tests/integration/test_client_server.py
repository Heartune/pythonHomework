"""
Integration tests for client-server communication.
"""

import unittest
import os
import sys
import threading
import time
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from client.network.client import Client
from server.network.server import Server
from utils.logger import get_logger

logger = get_logger(__name__)

class TestClientServerIntegration(unittest.TestCase):
    """Test case for client-server integration."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before all tests."""
        # Server configuration
        cls.host = 'localhost'
        cls.port = 9997
        cls.max_connections = 5
        
        # Create and start server
        cls.server = Server(cls.host, cls.port, cls.max_connections)
        cls.server_thread = threading.Thread(target=cls.server.start)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        
        # Wait for server to start
        time.sleep(0.5)
    
    @classmethod
    def tearDownClass(cls):
        """Tear down test fixtures after all tests."""
        # Stop server
        cls.server.stop()
        
        # Wait for server thread to finish
        if cls.server_thread.is_alive():
            cls.server_thread.join(timeout=1)
    
    def setUp(self):
        """Set up test fixtures before each test."""
        # Create client
        self.client = Client(self.host, self.port)
        
        # Connect to server
        self.client.connect()
    
    def tearDown(self):
        """Tear down test fixtures after each test."""
        # Disconnect client
        if self.client.connected:
            self.client.disconnect()
    
    def test_ping(self):
        """Test ping request."""
        # Send ping request
        request = {
            'action': 'ping',
            'data': 'test'
        }
        
        response = self.client.send_request(request)
        
        # Verify response
        self.assertIsNotNone(response)
        self.assertIn('success', response)
        self.assertIn('message', response)
    
    def test_login_logout(self):
        """Test login and logout."""
        # Mock authentication handler
        with patch('server.handlers.auth_handler.authenticate_user') as mock_auth:
            # Set up mock
            mock_user = MagicMock()
            mock_user.user_id = 1
            mock_user.username = 'admin'
            mock_user.role = 'admin'
            mock_user.to_dict.return_value = {
                'user_id': 1,
                'username': 'admin',
                'role': 'admin'
            }
            mock_auth.return_value = mock_user
            
            # Test login
            login_response = None
            
            def login_callback(response):
                nonlocal login_response
                login_response = response
            
            # Send login request
            self.client.login('admin', 'admin123', login_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify login response
            self.assertIsNotNone(login_response)
            self.assertTrue(login_response.get('success'))
            self.assertEqual(login_response.get('message'), 'Login successful')
            self.assertIsNotNone(login_response.get('data'))
            self.assertEqual(login_response.get('data').get('username'), 'admin')
            self.assertEqual(login_response.get('data').get('role'), 'admin')
            
            # Get token
            token = login_response.get('data').get('token')
            self.assertIsNotNone(token)
            
            # Test logout
            logout_response = None
            
            def logout_callback(response):
                nonlocal logout_response
                logout_response = response
            
            # Send logout request
            self.client.logout(token, logout_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify logout response
            self.assertIsNotNone(logout_response)
            self.assertTrue(logout_response.get('success'))
            self.assertEqual(logout_response.get('message'), 'Logout successful')
    
    def test_book_operations(self):
        """Test book operations."""
        # Mock authentication and book handlers
        with patch('server.handlers.auth_handler.verify_authentication') as mock_auth, \
             patch('server.handlers.book_handler.get_all_books') as mock_get_books, \
             patch('server.handlers.book_handler.get_book_by_id') as mock_get_book, \
             patch('server.handlers.book_handler.create_book') as mock_create_book, \
             patch('server.handlers.book_handler.update_book') as mock_update_book, \
             patch('server.handlers.book_handler.delete_book') as mock_delete_book:
            
            # Set up mocks
            mock_auth.return_value = (True, 1, 'admin')
            
            mock_books = [
                {
                    'book_id': 1,
                    'title': 'Python Programming',
                    'author': 'John Smith',
                    'isbn': '1234567890',
                    'publisher': 'Tech Books',
                    'publication_year': 2020,
                    'category': 'Programming',
                    'description': 'A comprehensive guide to Python programming.',
                    'quantity': 5,
                    'available': 3
                },
                {
                    'book_id': 2,
                    'title': 'Data Science with Python',
                    'author': 'Jane Doe',
                    'isbn': '0987654321',
                    'publisher': 'Data Press',
                    'publication_year': 2021,
                    'category': 'Data Science',
                    'description': 'Learn data science using Python.',
                    'quantity': 3,
                    'available': 2
                }
            ]
            
            mock_get_books.return_value = mock_books
            
            mock_book = {
                'book_id': 1,
                'title': 'Python Programming',
                'author': 'John Smith',
                'isbn': '1234567890',
                'publisher': 'Tech Books',
                'publication_year': 2020,
                'category': 'Programming',
                'description': 'A comprehensive guide to Python programming.',
                'quantity': 5,
                'available': 3
            }
            
            mock_get_book.return_value = mock_book
            
            new_book = {
                'book_id': 3,
                'title': 'Advanced Python',
                'author': 'Robert Johnson',
                'isbn': '5566778899',
                'publisher': 'Advanced Press',
                'publication_year': 2022,
                'category': 'Programming',
                'description': 'Advanced Python programming techniques.',
                'quantity': 2,
                'available': 2
            }
            
            mock_create_book.return_value = new_book
            
            updated_book = mock_book.copy()
            updated_book['title'] = 'Updated Python Programming'
            updated_book['description'] = 'An updated guide to Python programming.'
            
            mock_update_book.return_value = updated_book
            
            mock_delete_book.return_value = True
            
            # Test get all books
            books_response = None
            
            def get_books_callback(response):
                nonlocal books_response
                books_response = response
            
            # Send get books request
            self.client.get_books('mock_token', get_books_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify get books response
            self.assertIsNotNone(books_response)
            self.assertTrue(books_response.get('success'))
            self.assertIsNotNone(books_response.get('data'))
            self.assertEqual(len(books_response.get('data')), 2)
            
            # Test get book by ID
            book_response = None
            
            def get_book_callback(response):
                nonlocal book_response
                book_response = response
            
            # Send get book request
            request = {
                'action': 'get_book',
                'token': 'mock_token',
                'book_id': 1
            }
            
            self.client.send_request(request, get_book_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify get book response
            self.assertIsNotNone(book_response)
            self.assertTrue(book_response.get('success'))
            self.assertIsNotNone(book_response.get('data'))
            self.assertEqual(book_response.get('data').get('book_id'), 1)
            self.assertEqual(book_response.get('data').get('title'), 'Python Programming')
            
            # Test create book
            create_response = None
            
            def create_book_callback(response):
                nonlocal create_response
                create_response = response
            
            # Send create book request
            request = {
                'action': 'create_book',
                'token': 'mock_token',
                'book': {
                    'title': 'Advanced Python',
                    'author': 'Robert Johnson',
                    'isbn': '5566778899',
                    'publisher': 'Advanced Press',
                    'publication_year': 2022,
                    'category': 'Programming',
                    'description': 'Advanced Python programming techniques.',
                    'quantity': 2
                }
            }
            
            self.client.send_request(request, create_book_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify create book response
            self.assertIsNotNone(create_response)
            self.assertTrue(create_response.get('success'))
            self.assertIsNotNone(create_response.get('data'))
            self.assertEqual(create_response.get('data').get('book_id'), 3)
            self.assertEqual(create_response.get('data').get('title'), 'Advanced Python')
            
            # Test update book
            update_response = None
            
            def update_book_callback(response):
                nonlocal update_response
                update_response = response
            
            # Send update book request
            request = {
                'action': 'update_book',
                'token': 'mock_token',
                'book_id': 1,
                'book': {
                    'title': 'Updated Python Programming',
                    'description': 'An updated guide to Python programming.'
                }
            }
            
            self.client.send_request(request, update_book_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify update book response
            self.assertIsNotNone(update_response)
            self.assertTrue(update_response.get('success'))
            self.assertIsNotNone(update_response.get('data'))
            self.assertEqual(update_response.get('data').get('book_id'), 1)
            self.assertEqual(update_response.get('data').get('title'), 'Updated Python Programming')
            self.assertEqual(update_response.get('data').get('description'), 'An updated guide to Python programming.')
            
            # Test delete book
            delete_response = None
            
            def delete_book_callback(response):
                nonlocal delete_response
                delete_response = response
            
            # Send delete book request
            request = {
                'action': 'delete_book',
                'token': 'mock_token',
                'book_id': 1
            }
            
            self.client.send_request(request, delete_book_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify delete book response
            self.assertIsNotNone(delete_response)
            self.assertTrue(delete_response.get('success'))
    
    def test_user_operations(self):
        """Test user operations."""
        # Mock authentication and user handlers
        with patch('server.handlers.auth_handler.verify_authentication') as mock_auth, \
             patch('server.handlers.user_handler.get_all_users') as mock_get_users, \
             patch('server.handlers.user_handler.get_user_by_id') as mock_get_user, \
             patch('server.handlers.user_handler.create_user') as mock_create_user, \
             patch('server.handlers.user_handler.update_user') as mock_update_user, \
             patch('server.handlers.user_handler.delete_user') as mock_delete_user:
            
            # Set up mocks
            mock_auth.return_value = (True, 1, 'admin')
            
            mock_users = [
                {
                    'user_id': 1,
                    'username': 'admin',
                    'full_name': 'Admin User',
                    'email': 'admin@example.com',
                    'phone': '1234567890',
                    'address': '123 Admin St',
                    'role': 'admin'
                },
                {
                    'user_id': 2,
                    'username': 'user1',
                    'full_name': 'Regular User',
                    'email': 'user@example.com',
                    'phone': '0987654321',
                    'address': '456 User Ave',
                    'role': 'user'
                }
            ]
            
            mock_get_users.return_value = mock_users
            
            mock_user = {
                'user_id': 1,
                'username': 'admin',
                'full_name': 'Admin User',
                'email': 'admin@example.com',
                'phone': '1234567890',
                'address': '123 Admin St',
                'role': 'admin'
            }
            
            mock_get_user.return_value = mock_user
            
            new_user = {
                'user_id': 3,
                'username': 'newuser',
                'full_name': 'New User',
                'email': 'new@example.com',
                'phone': '5555555555',
                'address': '789 New Rd',
                'role': 'user'
            }
            
            mock_create_user.return_value = new_user
            
            updated_user = mock_user.copy()
            updated_user['full_name'] = 'Updated Admin User'
            updated_user['email'] = 'updated@example.com'
            
            mock_update_user.return_value = updated_user
            
            mock_delete_user.return_value = True
            
            # Test get all users
            users_response = None
            
            def get_users_callback(response):
                nonlocal users_response
                users_response = response
            
            # Send get users request
            request = {
                'action': 'get_users',
                'token': 'mock_token'
            }
            
            self.client.send_request(request, get_users_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify get users response
            self.assertIsNotNone(users_response)
            self.assertTrue(users_response.get('success'))
            self.assertIsNotNone(users_response.get('data'))
            self.assertEqual(len(users_response.get('data')), 2)
            
            # Test get user by ID
            user_response = None
            
            def get_user_callback(response):
                nonlocal user_response
                user_response = response
            
            # Send get user request
            request = {
                'action': 'get_user',
                'token': 'mock_token',
                'user_id': 1
            }
            
            self.client.send_request(request, get_user_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify get user response
            self.assertIsNotNone(user_response)
            self.assertTrue(user_response.get('success'))
            self.assertIsNotNone(user_response.get('data'))
            self.assertEqual(user_response.get('data').get('user_id'), 1)
            self.assertEqual(user_response.get('data').get('username'), 'admin')
            
            # Test create user
            create_response = None
            
            def create_user_callback(response):
                nonlocal create_response
                create_response = response
            
            # Send create user request
            request = {
                'action': 'create_user',
                'token': 'mock_token',
                'user': {
                    'username': 'newuser',
                    'password': 'newpass123',
                    'full_name': 'New User',
                    'email': 'new@example.com',
                    'phone': '5555555555',
                    'address': '789 New Rd',
                    'role': 'user'
                }
            }
            
            self.client.send_request(request, create_user_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify create user response
            self.assertIsNotNone(create_response)
            self.assertTrue(create_response.get('success'))
            self.assertIsNotNone(create_response.get('data'))
            self.assertEqual(create_response.get('data').get('user_id'), 3)
            self.assertEqual(create_response.get('data').get('username'), 'newuser')
            
            # Test update user
            update_response = None
            
            def update_user_callback(response):
                nonlocal update_response
                update_response = response
            
            # Send update user request
            request = {
                'action': 'update_user',
                'token': 'mock_token',
                'user_id': 1,
                'user': {
                    'full_name': 'Updated Admin User',
                    'email': 'updated@example.com'
                }
            }
            
            self.client.send_request(request, update_user_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify update user response
            self.assertIsNotNone(update_response)
            self.assertTrue(update_response.get('success'))
            self.assertIsNotNone(update_response.get('data'))
            self.assertEqual(update_response.get('data').get('user_id'), 1)
            self.assertEqual(update_response.get('data').get('full_name'), 'Updated Admin User')
            self.assertEqual(update_response.get('data').get('email'), 'updated@example.com')
            
            # Test delete user
            delete_response = None
            
            def delete_user_callback(response):
                nonlocal delete_response
                delete_response = response
            
            # Send delete user request
            request = {
                'action': 'delete_user',
                'token': 'mock_token',
                'user_id': 1
            }
            
            self.client.send_request(request, delete_user_callback)
            
            # Wait for response
            time.sleep(0.5)
            
            # Verify delete user response
            self.assertIsNotNone(delete_response)
            self.assertTrue(delete_response.get('success'))

if __name__ == '__main__':
    unittest.main()
