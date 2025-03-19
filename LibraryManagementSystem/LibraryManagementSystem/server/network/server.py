"""
Server network implementation for the Library Management System.
"""

import socket
import threading
import json
import time
import traceback

# Import modules
from LibraryManagementSystem.utils.logger import get_logger
from LibraryManagementSystem.server.handlers.auth_handler import handle_login, handle_logout, verify_token
from LibraryManagementSystem.server.handlers.book_handler import handle_book_request
from LibraryManagementSystem.server.handlers.user_handler import handle_user_request

logger = get_logger(__name__)

class Server:
    """
    Server class for handling client connections and requests.
    """
    
    def __init__(self, host, port, max_connections=5):
        """
        Initialize the server.
        
        Args:
            host (str): The host to bind to.
            port (int): The port to bind to.
            max_connections (int): The maximum number of connections to accept.
        """
        self.host = host
        self.port = port
        self.max_connections = max_connections
        self.socket = None
        self.running = False
        self.clients = []
        
    def start(self):
        """
        Start the server.
        """
        try:
            # Create a socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind the socket to the host and port
            self.socket.bind((self.host, self.port))
            
            # Listen for connections
            self.socket.listen(self.max_connections)
            
            # Set the running flag
            self.running = True
            
            logger.info(f"Server started on {self.host}:{self.port}")
            
            # Accept connections
            while self.running:
                try:
                    # Accept a connection
                    client_socket, client_address = self.socket.accept()
                    
                    # Create a thread to handle the client
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, client_address)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                    # Add the client to the list
                    self.clients.append((client_socket, client_address, client_thread))
                    
                    logger.info(f"Client connected from {client_address[0]}:{client_address[1]}")
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
                    else:
                        break
        except Exception as e:
            logger.error(f"Error starting server: {e}")
            self.stop()
    
    def stop(self):
        """
        Stop the server.
        """
        try:
            # Set the running flag
            self.running = False
            
            # Close all client connections
            for client_socket, client_address, _ in self.clients:
                try:
                    client_socket.close()
                except Exception as e:
                    logger.error(f"Error closing client connection: {e}")
            
            # Clear the clients list
            self.clients = []
            
            # Close the server socket
            if self.socket:
                self.socket.close()
                self.socket = None
            
            logger.info("Server stopped")
        except Exception as e:
            logger.error(f"Error stopping server: {e}")
    
    def _handle_client(self, client_socket, client_address):
        """
        Handle a client connection.
        
        Args:
            client_socket (socket.socket): The client socket.
            client_address (tuple): The client address.
        """
        # Client state
        user_id = None
        role = None
        token = None
        
        try:
            # Receive data from the client
            while self.running:
                try:
                    # Receive data
                    data = self._receive_data(client_socket)
                    
                    # If no data, the client has disconnected
                    if not data:
                        break
                    
                    # Parse the data
                    request = json.loads(data)
                    
                    # Extract the action and data
                    action = request.get('action')
                    data = request.get('data', {})
                    token = request.get('token')
                    
                    # Prepare the response
                    response = {
                        'action': action,
                        'success': False,
                        'message': 'Unknown action',
                        'data': {}
                    }
                    
                    # Handle ping action
                    if action == 'ping':
                        response['success'] = True
                        response['message'] = 'Pong'
                    # Handle authentication actions
                    elif action == 'login':
                        success, message, user_data = handle_login(data.get('username'), data.get('password'))
                        response['success'] = success
                        response['message'] = message
                        response['data'] = user_data
                        
                        if success:
                            # Update client state
                            user_id = user_data.get('user_id')
                            role = user_data.get('role')
                            token = user_data.get('token')
                    elif action == 'logout':
                        success, message = handle_logout(token)
                        response['success'] = success
                        response['message'] = message
                        
                        if success:
                            # Update client state
                            user_id = None
                            role = None
                            token = None
                    # Handle book-related actions
                    elif action == 'book_get_all':
                        # Special case for book_get_all
                        # Include token in data for authentication
                        data['token'] = token
                        success, message, result_data = handle_book_request('book_get_all', data, token)
                        response['success'] = success
                        response['message'] = message
                        response['data'] = result_data
                        # Log the response for debugging
                        logger.info(f"Book get all response: success={success}, message={message}, data_length={len(result_data) if result_data else 0}, token={token}")
                    elif isinstance(action, str) and action.startswith('book_'):
                        success, message, result_data = handle_book_request(action, data, token)
                        response['success'] = success
                        response['message'] = message
                        response['data'] = result_data
                    # Handle user-related actions
                    elif action == 'get_users' or action == 'user_get_all':
                        # Special case for get_users
                        # Include token in data for authentication
                        data['token'] = token
                        success, message, result_data = handle_user_request('user_get_all', data, token)
                        response['success'] = success
                        response['message'] = message
                        response['data'] = result_data
                        # Log the response for debugging
                        logger.info(f"User get all response: success={success}, message={message}, data_length={len(result_data) if result_data else 0}, token={token}")
                    elif isinstance(action, str) and action.startswith('user_'):
                        success, message, result_data = handle_user_request(action, data, token)
                        response['success'] = success
                        response['message'] = message
                        response['data'] = result_data
                    
                    # Send the response
                    self._send_data(client_socket, json.dumps(response))
                except json.JSONDecodeError:
                    logger.error("Error decoding JSON")
                    break
                except Exception as e:
                    logger.error(f"Error receiving data: {e}")
                    break
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            # Close the client socket
            try:
                client_socket.close()
            except Exception as e:
                logger.error(f"Error closing client socket: {e}")
            
            # Remove the client from the list
            self.clients = [c for c in self.clients if c[0] != client_socket]
            
            logger.info(f"Client disconnected from {client_address[0]}:{client_address[1]}")
    
    def _receive_data(self, client_socket):
        """
        Receive data from a client.
        
        Args:
            client_socket (socket.socket): The client socket.
            
        Returns:
            str: The received data.
        """
        # Receive the data length
        length_data = client_socket.recv(4)
        if not length_data:
            return None
        
        # Convert the length to an integer
        length = int.from_bytes(length_data, byteorder='big')
        
        # Receive the data
        data = b''
        while len(data) < length:
            chunk = client_socket.recv(min(length - len(data), 4096))
            if not chunk:
                return None
            data += chunk
        
        # Return the data as a string
        return data.decode('utf-8')
    
    def _send_data(self, client_socket, data):
        """
        Send data to a client.
        
        Args:
            client_socket (socket.socket): The client socket.
            data (str): The data to send.
        """
        # Convert the data to bytes
        data_bytes = data.encode('utf-8')
        
        # Send the data length
        length = len(data_bytes)
        client_socket.sendall(length.to_bytes(4, byteorder='big'))
        
        # Send the data
        client_socket.sendall(data_bytes)
