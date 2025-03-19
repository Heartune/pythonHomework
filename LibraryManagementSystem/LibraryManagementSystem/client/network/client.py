"""
Client network implementation for the Library Management System.
"""

import socket
import json
import threading
import time

# Import modules
from LibraryManagementSystem.utils.logger import get_logger

logger = get_logger(__name__)

class Client:
    """
    Client class for communicating with the server.
    """
    
    def __init__(self, host, port):
        """
        Initialize the client.
        
        Args:
            host (str): The host to connect to.
            port (int): The port to connect to.
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.token = None
        self.receive_thread = None
        self.callbacks = {}
        self.lock = threading.Lock()
    
    def connect(self):
        """
        Connect to the server.
        
        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        try:
            # Create a socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Connect to the server
            self.socket.connect((self.host, self.port))
            
            # Set the connected flag
            self.connected = True
            
            # Start the receive thread
            self.receive_thread = threading.Thread(target=self._receive_data)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            logger.info(f"Connected to server at {self.host}:{self.port}")
            
            return True
        except Exception as e:
            logger.error(f"Error connecting to server: {e}")
            self.disconnect()
            return False
    
    def disconnect(self):
        """
        Disconnect from the server.
        """
        try:
            # Set the connected flag
            self.connected = False
            
            # Close the socket
            if self.socket:
                self.socket.close()
                self.socket = None
            
            # Clear the token
            self.token = None
            
            logger.info("Disconnected from server")
        except Exception as e:
            logger.error(f"Error disconnecting from server: {e}")
    
    def send_request(self, action, data=None, callback=None):
        """
        Send a request to the server.
        
        Args:
            action (str): The action to perform.
            data (dict): The data to send.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        try:
            # Check if connected
            if not self.connected:
                if not self.connect():
                    logger.warning("Not connected to server")
                    return False
            
            # Prepare the request
            request = {
                'action': action,
                'data': data or {}
            }
            
            # Add the token if available
            if self.token:
                request['token'] = self.token
            
            # Register the callback
            if callback:
                with self.lock:
                    self.callbacks[action] = callback
            
            # Send the request
            self._send_data(json.dumps(request))
            
            return True
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            return False
    
    def login(self, username, password, callback=None):
        """
        Log in to the server.
        
        Args:
            username (str): The username.
            password (str): The password.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'username': username,
            'password': password
        }
        
        return self.send_request('login', data, callback)
    
    def logout(self, callback=None):
        """
        Log out from the server.
        
        Args:
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        return self.send_request('logout', {}, callback)
    
    def get_books(self, callback=None):
        """
        Get all books from the server.
        
        Args:
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        return self.send_request('book_get_all', {}, callback)
    
    def get_book(self, book_id, callback=None):
        """
        Get a book from the server.
        
        Args:
            book_id (int): The book ID.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'book_id': book_id
        }
        
        return self.send_request('book_get', data, callback)
    
    def add_book(self, book_data, callback=None):
        """
        Add a book to the server.
        
        Args:
            book_data (dict): The book data.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'data': book_data
        }
        
        return self.send_request('book_add', data, callback)
    
    def update_book(self, book_id, book_data, callback=None):
        """
        Update a book on the server.
        
        Args:
            book_id (int): The book ID.
            book_data (dict): The book data.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'book_id': book_id,
            'book': book_data
        }
        
        return self.send_request('book_update', data, callback)
    
    def delete_book(self, book_id, callback=None):
        """
        Delete a book from the server.
        
        Args:
            book_id (int): The book ID.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'book_id': book_id
        }
        
        return self.send_request('book_delete', data, callback)
    
    def search_books(self, search_term, callback=None):
        """
        Search for books on the server.
        
        Args:
            search_term (str): The search term.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'search_term': search_term
        }
        
        return self.send_request('book_search', data, callback)
    
    def get_users(self, callback=None):
        """
        Get all users from the server.
        
        Args:
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        return self.send_request('user_get_all', {}, callback)
    
    def get_user(self, user_id, callback=None):
        """
        Get a user from the server.
        
        Args:
            user_id (int): The user ID.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'user_id': user_id
        }
        
        return self.send_request('user_get', data, callback)
    
    def add_user(self, user_data, callback=None):
        """
        Add a user to the server.
        
        Args:
            user_data (dict): The user data.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'data': user_data
        }
        
        return self.send_request('user_add', data, callback)
    
    def update_user(self, user_id, user_data, callback=None):
        """
        Update a user on the server.
        
        Args:
            user_id (int): The user ID.
            user_data (dict): The user data.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'user_id': user_id,
            'user': user_data
        }
        
        return self.send_request('user_update', data, callback)
    
    def delete_user(self, user_id, callback=None):
        """
        Delete a user from the server.
        
        Args:
            user_id (int): The user ID.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'user_id': user_id
        }
        
        return self.send_request('user_delete', data, callback)
    
    def borrow_book(self, user_id, book_id, callback=None):
        """
        Borrow a book from the server.
        
        Args:
            user_id (int): The user ID.
            book_id (int): The book ID.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'user_id': user_id,
            'book_id': book_id
        }
        
        return self.send_request('transaction_borrow', data, callback)
    
    def return_book(self, transaction_id, callback=None):
        """
        Return a book to the server.
        
        Args:
            transaction_id (int): The transaction ID.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'transaction_id': transaction_id
        }
        
        return self.send_request('transaction_return', data, callback)
    
    def get_transactions(self, user_id=None, callback=None):
        """
        Get transactions from the server.
        
        Args:
            user_id (int): The user ID.
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {}
        
        if user_id:
            data['user_id'] = user_id
        
        return self.send_request('transaction_get_all', data, callback)
    
    def ping(self, callback=None):
        """
        Ping the server.
        
        Args:
            callback (function): A callback function to call when the response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        return self.send_request('ping', {}, callback)
    
    def _send_data(self, data):
        """
        Send data to the server.
        
        Args:
            data (str): The data to send.
        """
        # Convert the data to bytes
        data_bytes = data.encode('utf-8')
        
        # Send the data length
        length = len(data_bytes)
        self.socket.sendall(length.to_bytes(4, byteorder='big'))
        
        # Send the data
        self.socket.sendall(data_bytes)
    
    def _receive_data(self):
        """
        Receive data from the server.
        """
        try:
            while self.connected:
                try:
                    # Receive the data length
                    length_data = self.socket.recv(4)
                    if not length_data:
                        break
                    
                    # Convert the length to an integer
                    length = int.from_bytes(length_data, byteorder='big')
                    
                    # Receive the data
                    data = b''
                    while len(data) < length:
                        chunk = self.socket.recv(min(length - len(data), 4096))
                        if not chunk:
                            break
                        data += chunk
                    
                    # If no data, the server has disconnected
                    if not data:
                        break
                    
                    # Parse the data
                    response = json.loads(data.decode('utf-8'))
                    
                    # Handle the response
                    self._handle_response(response)
                except Exception as e:
                    logger.error(f"Error receiving data: {e}")
                    break
        except Exception as e:
            logger.error(f"Error in receive thread: {e}")
        finally:
            # Disconnect
            self.disconnect()
    
    def _handle_response(self, response):
        """
        Handle a response from the server.
        
        Args:
            response (dict): The response.
        """
        try:
            # Extract the action
            action = response.get('action')
            
            # Handle authentication actions
            if action == 'login' and response.get('success'):
                self.token = response.get('data', {}).get('token')
                logger.info("Logged in successfully")
            elif action == 'logout' and response.get('success'):
                self.token = None
                logger.info("Logged out successfully")
            
            # Call the callback if available
            with self.lock:
                callback = self.callbacks.get(action)
                if callback:
                    callback(response)
                    del self.callbacks[action]
        except Exception as e:
            logger.error(f"Error handling response: {e}")
