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
    
    def send_request(self, action, data=None, callback=None):
        """
        Send a request to the server.
        
        Args:
            action (str): The action to perform.
            data (dict, optional): The data to send.
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        if not self.connected:
            logger.warning("Not connected to server")
            return False
        
        try:
            # Prepare the request
            request = {
                'action': action,
                'data': data or {},
                'token': self.token
            }
            
            # Generate a request ID
            request_id = str(int(time.time() * 1000))
            request['request_id'] = request_id
            
            # Register the callback
            if callback:
                self.callbacks[request_id] = callback
            
            # Encode the request
            request_json = json.dumps(request)
            request_bytes = request_json.encode('utf-8')
            
            # Send the request length first (4 bytes)
            length_bytes = len(request_bytes).to_bytes(4, byteorder='big')
            self.socket.sendall(length_bytes)
            
            # Send the request
            self.socket.sendall(request_bytes)
            
            logger.debug(f"Sent request: {action}")
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
    
    def logout(self, callback=None):
        """
        Log out from the server.
        
        Args:
            callback (callable, optional): A callback function to call when a response is received.
            
        Returns:
            bool: True if the request was sent successfully, False otherwise.
        """
        return self.send_request('logout', {}, callback)
    
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
