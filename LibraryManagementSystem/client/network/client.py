"""
Client network module for the Library Management System.
"""

import socket
import json
import threading
import time
import ssl
from utils.logger import get_logger

logger = get_logger(__name__)

class Client:
    """Client for communicating with the server."""
    
    def __init__(self, host, port):
        """
        Initialize the client.
        
        Args:
            host (str): The server host.
            port (int): The server port.
        """
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
        self.token = None
        self.receive_thread = None
        self.callbacks = {}
    
    def connect(self):
        """
        Connect to the server.
        
        Returns:
            bool: True if the connection was successful, False otherwise.
        """
        try:
            # Create a socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Set a timeout for connection attempts
            self.socket.settimeout(5)
            
            # Connect to the server
            self.socket.connect((self.host, self.port))
            
            # Reset the timeout for normal operation
            self.socket.settimeout(None)
            
            self.connected = True
            
            # Start the receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            logger.info(f"Connected to server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to server: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the server."""
        if self.connected:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing socket: {e}")
            finally:
                self.connected = False
                self.socket = None
                logger.info("Disconnected from server")
    
    def send_request(self, action_or_request, data=None, callback=None):
        """
        Send a request to the server.
        
        Args:
            action_or_request (str or dict): The action to perform or a complete request dict.
            data (dict, optional): The data to send if action_or_request is a string.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        if not self.connected:
            logger.warning("Not connected to server")
            return False
        
        try:
            # Handle the case where callback is passed as the second argument
            if callable(data) and callback is None:
                callback = data
                data = None
            
            # Prepare the request based on input type
            if isinstance(action_or_request, dict):
                # If a complete request dict was provided
                request = action_or_request.copy()
                if 'token' not in request and self.token:
                    request['token'] = self.token
            else:
                # If action and data were provided separately
                request = {
                    'action': action_or_request,
                    'data': data or {},
                    'token': self.token
                }
            
            # Generate a request ID
            request_id = str(int(time.time() * 1000))
            request['request_id'] = request_id
            
            # Register the callback
            if callback:
                self.callbacks[request_id] = callback
            
            # Encode the request (exclude callback and any function objects from serialization)
            request_data = {}
            for k, v in request.items():
                if k != 'callback' and not callable(v):
                    request_data[k] = v
            request_json = json.dumps(request_data)
            request_bytes = request_json.encode('utf-8')
            
            # Send the request length first (4 bytes)
            length_bytes = len(request_bytes).to_bytes(4, byteorder='big')
            self.socket.sendall(length_bytes)
            
            # Send the request
            self.socket.sendall(request_bytes)
            
            logger.debug(f"Sent request: {request_data.get('action')}")
            return True
        except Exception as e:
            logger.error(f"Error sending request: {e}")
            self.connected = False
            return False
    
    def login(self, username, password, callback=None):
        """
        Log in to the server.
        
        Args:
            username (str): The username.
            password (str): The password.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        data = {
            'username': username,
            'password': password
        }
        
        return self.send_request('login', data, callback)
    
    def logout(self, token=None, callback=None):
        """
        Log out from the server.
        
        Args:
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        return self.send_request('logout', {}, callback)
        
    def ping(self, callback=None):
        """
        Send a ping request to the server to check connectivity.
        
        Args:
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        return self.send_request('ping', {}, callback)
        
    def get_books(self, token=None, callback=None):
        """
        Get all books from the server.
        
        Args:
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the token explicitly in the data
        data = {'token': token}
        
        # Use the action string directly
        return self.send_request('book_get_all', data, callback)
        
    def get_users(self, token=None, callback=None):
        """
        Get all users from the server.
        
        Args:
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the token explicitly in the data
        data = {'token': token}
        
        # Use the action string directly
        return self.send_request('user_get_all', data, callback)
        
    def get_user(self, user_id, token=None, callback=None):
        """
        Get a specific user from the server.
        
        Args:
            user_id (int): The ID of the user to get.
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the user ID and token
        data = {
            'user_id': user_id,
            'token': token
        }
        
        return self.send_request('user_get', data, callback)
        
    def create_user(self, user_data, token=None, callback=None):
        """
        Create a new user on the server.
        
        Args:
            user_data (dict): The user data.
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the user data
        data = {'data': user_data}
        
        return self.send_request('user_create', data, callback)
        
    def update_user(self, user_id, user_data, token=None, callback=None):
        """
        Update a user on the server.
        
        Args:
            user_id (int): The ID of the user to update.
            user_data (dict): The updated user data.
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the user data in the 'user' field
        request = {
            'action': 'user_update',
            'token': token,
            'user_id': user_id,
            'user': user_data
        }
        
        return self.send_request(request, callback)
        
    def delete_user(self, user_id, token=None, callback=None):
        """
        Delete a user from the server.
        
        Args:
            user_id (int): The ID of the user to delete.
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the user ID
        data = {'user_id': user_id}
        
        return self.send_request('user_delete', data, callback)
        
    def get_book(self, book_id, token=None, callback=None):
        """
        Get a specific book from the server.
        
        Args:
            book_id (int): The ID of the book to get.
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the book ID and token
        data = {
            'book_id': book_id,
            'token': token
        }
        
        return self.send_request('book_get', data, callback)
        
    def create_book(self, book_data, token=None, callback=None):
        """
        Create a new book on the server.
        
        Args:
            book_data (dict): The book data.
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the book data
        data = {'data': book_data}
        
        return self.send_request('book_create', data, callback)
        
    def update_book(self, book_id, book_data, token=None, callback=None):
        """
        Update a book on the server.
        
        Args:
            book_id (int): The ID of the book to update.
            book_data (dict): The updated book data.
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the book data in the 'book' field
        request = {
            'action': 'book_update',
            'token': token,
            'book_id': book_id,
            'book': book_data
        }
        
        return self.send_request(request, callback)
        
    def delete_book(self, book_id, token=None, callback=None):
        """
        Delete a book from the server.
        
        Args:
            book_id (int): The ID of the book to delete.
            token (str, optional): The authentication token. If not provided, uses the stored token.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        # Use the stored token if none is provided
        if token is None:
            token = self.token
            
        # Create a request with the book ID
        data = {'book_id': book_id}
        
        return self.send_request('book_delete', data, callback)
    
    def _receive_loop(self):
        """Receive loop for handling server responses."""
        while self.connected:
            try:
                # Receive the response length first (4 bytes)
                length_bytes = self._receive_exactly(4)
                if not length_bytes:
                    break
                
                response_length = int.from_bytes(length_bytes, byteorder='big')
                
                # Receive the response
                response_bytes = self._receive_exactly(response_length)
                if not response_bytes:
                    break
                
                # Decode the response
                response_json = response_bytes.decode('utf-8')
                response = json.loads(response_json)
                
                # Handle the response
                self._handle_response(response)
            except Exception as e:
                logger.error(f"Error in receive loop: {e}")
                self.connected = False
                break
    
    def _receive_exactly(self, n):
        """
        Receive exactly n bytes from the socket.
        
        Args:
            n (int): The number of bytes to receive.
            
        Returns:
            bytes: The received bytes, or None if an error occurred.
        """
        try:
            data = b''
            while len(data) < n:
                chunk = self.socket.recv(n - len(data))
                if not chunk:
                    return None
                data += chunk
            return data
        except Exception as e:
            logger.error(f"Error receiving data: {e}")
            self.connected = False
            return None
    
    def _handle_response(self, response):
        """
        Handle a response from the server.
        
        Args:
            response (dict): The response.
        """
        try:
            # Extract the request ID
            request_id = response.get('request_id')
            
            # Check if we have a callback for this request
            if request_id and request_id in self.callbacks:
                callback = self.callbacks[request_id]
                del self.callbacks[request_id]
                
                # Call the callback
                callback(response)
            
            # Handle authentication responses
            if response.get('action') == 'login' and response.get('success'):
                self.token = response.get('data', {}).get('token')
                logger.info("Logged in successfully")
            elif response.get('action') == 'logout' and response.get('success'):
                self.token = None
                logger.info("Logged out successfully")
        except Exception as e:
            logger.error(f"Error handling response: {e}")
