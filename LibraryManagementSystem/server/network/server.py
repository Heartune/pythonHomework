"""
Server network module for the Library Management System.
"""

import socket
import json
import threading
import time
import ssl
from utils.logger import get_logger
from ..handlers.auth_handler import handle_login, handle_logout
from ..handlers.book_handler import handle_book_request
from ..handlers.user_handler import handle_user_request

logger = get_logger(__name__)

class ClientHandler(threading.Thread):
    """Handler for client connections."""
    
    def __init__(self, client_socket, address, server):
        """
        Initialize the client handler.
        
        Args:
            client_socket (socket.socket): The client socket.
            address (tuple): The client address (host, port).
            server (Server): The server instance.
        """
        super().__init__()
        self.socket = client_socket
        self.address = address
        self.server = server
        self.running = True
        self.user_id = None
        self.role = None
        self.token = None
    
    def run(self):
        """Handle client requests."""
        logger.info(f"Client connected from {self.address[0]}:{self.address[1]}")
        
        try:
            while self.running:
                # Receive the request length first (4 bytes)
                length_bytes = self._receive_exactly(4)
                if not length_bytes:
                    break
                
                request_length = int.from_bytes(length_bytes, byteorder='big')
                
                # Receive the request
                request_bytes = self._receive_exactly(request_length)
                if not request_bytes:
                    break
                
                # Decode the request
                request_json = request_bytes.decode('utf-8')
                request = json.loads(request_json)
                
                # Handle the request
                response = self._handle_request(request)
                
                # Encode the response
                response_json = json.dumps(response)
                response_bytes = response_json.encode('utf-8')
                
                # Send the response length first (4 bytes)
                length_bytes = len(response_bytes).to_bytes(4, byteorder='big')
                self.socket.sendall(length_bytes)
                
                # Send the response
                self.socket.sendall(response_bytes)
        except Exception as e:
            logger.error(f"Error handling client: {e}")
        finally:
            self._cleanup()
    
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
            return None
    
    def _handle_request(self, request):
        """
        Handle a client request.
        
        Args:
            request (dict): The request.
            
        Returns:
            dict: The response.
        """
        try:
            # Extract request data
            action = request.get('action')
            data = request.get('data', {})
            request_id = request.get('request_id')
            token = request.get('token')
            
            # Prepare the response
            response = {
                'action': action,
                'request_id': request_id,
                'success': False,
                'message': '',
                'data': {}
            }
            
            # Handle authentication actions
            if action == 'login':
                success, message, user_data = handle_login(data.get('username'), data.get('password'))
                response['success'] = success
                response['message'] = message
                
                if success and user_data:
                    self.user_id = user_data.get('user_id')
                    self.role = user_data.get('role')
                    self.token = user_data.get('token')
                    response['data'] = user_data
            elif action == 'logout':
                success, message = handle_logout(token)
                response['success'] = success
                response['message'] = message
                
                if success:
                    self.user_id = None
                    self.role = None
                    self.token = None
            # Handle book-related actions
            elif action.startswith('book_'):
                success, message, result_data = handle_book_request(action, data, token)
                response['success'] = success
                response['message'] = message
                response['data'] = result_data
            # Handle user-related actions
            elif action.startswith('user_'):
                success, message, result_data = handle_user_request(action, data, token)
                response['success'] = success
                response['message'] = message
                response['data'] = result_data
            else:
                response['message'] = f"Unknown action: {action}"
            
            return response
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            return {
                'action': request.get('action'),
                'request_id': request.get('request_id'),
                'success': False,
                'message': f"Server error: {str(e)}",
                'data': {}
            }
    
    def _cleanup(self):
        """Clean up resources."""
        try:
            self.running = False
            self.socket.close()
            logger.info(f"Client disconnected from {self.address[0]}:{self.address[1]}")
        except Exception as e:
            logger.error(f"Error cleaning up client handler: {e}")

class Server:
    """Server for the Library Management System."""
    
    def __init__(self, host, port, max_connections):
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
        """Start the server."""
        try:
            # Create a socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Allow reuse of the address
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Bind to the host and port
            self.socket.bind((self.host, self.port))
            
            # Listen for connections
            self.socket.listen(self.max_connections)
            
            self.running = True
            
            logger.info(f"Server started on {self.host}:{self.port}")
            
            # Accept connections
            while self.running:
                try:
                    # Accept a connection
                    client_socket, address = self.socket.accept()
                    
                    # Create a client handler
                    client_handler = ClientHandler(client_socket, address, self)
                    
                    # Add the client to the list
                    self.clients.append(client_handler)
                    
                    # Start the client handler
                    client_handler.start()
                except Exception as e:
                    if self.running:
                        logger.error(f"Error accepting connection: {e}")
                    break
        except Exception as e:
            logger.error(f"Error starting server: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the server."""
        self.running = False
        
        # Close all client connections
        for client in self.clients[:]:
            try:
                client.running = False
                client.socket.close()
                self.clients.remove(client)
            except Exception as e:
                logger.error(f"Error closing client connection: {e}")
        
        # Close the server socket
        if self.socket:
            try:
                self.socket.close()
            except Exception as e:
                logger.error(f"Error closing server socket: {e}")
            
            self.socket = None
        
        logger.info("Server stopped")
