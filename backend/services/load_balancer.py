"""
Load balancer for the Cab Booking System
Distributes client requests across multiple backend servers using least-connections algorithm
"""

import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import threading
import time
import logging
import sys
import os

# Add the parent directory to sys.path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("LoadBalancer")

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    """Threaded XML-RPC Server to handle concurrent requests"""
    pass

class LoadBalancer:
    """
    Load balancer that distributes requests across multiple backend servers
    using the least-connections algorithm.
    """
    def __init__(self, server_ports=None):
        """
        Initialize the load balancer
        
        Args:
            server_ports (list): List of server ports to balance between
        """
        if server_ports is None:
            # Use default ports from settings
            self.server_ports = [
                settings.BASE_SERVER_PORT + i for i in range(settings.SERVER_COUNT)
            ]
        else:
            self.server_ports = server_ports
            
        self.servers = {}
        self.active_connections = {}
        self.last_health_check = {}
        self.server_status = {}  # 'up' or 'down'
        self.lock = threading.RLock()
        
        # Connect to all backend servers
        for port in self.server_ports:
            self._init_server_connection(port)
        
        logger.info(f"Load Balancer initialized with servers on ports: {self.server_ports}")
        
        # Start health check thread
        self._start_health_checker()
    
    def _init_server_connection(self, port):
        """Initialize connection to a backend server"""
        with self.lock:
            server_url = f"http://{settings.SERVER_HOST}:{port}{settings.RPC_PATH}"
            self.servers[port] = xmlrpc.client.ServerProxy(server_url, allow_none=True)
            self.active_connections[port] = 0
            self.last_health_check[port] = time.time()
            self.server_status[port] = 'unknown'  # Will be updated by health check

    def _dispatch(self, method, params):
        """
        Dispatch method to a backend server
        
        This is called for every client request and implements the load balancing logic
        """
        with self.lock:
            # Filter out 'down' servers
            available_servers = [p for p, status in self.server_status.items() 
                                if status != 'down']
            
            if not available_servers:
                logger.error("No servers available")
                raise Exception("No servers available")
            
            # Select server with least active connections
            port = min(
                available_servers, 
                key=lambda p: self.active_connections.get(p, float('inf'))
            )
            
            # Increment connection count for selected server
            self.active_connections[port] += 1
        
        try:
            # Forward request to selected server
            logger.debug(f"Forwarding {method} to server on port {port}")
            server = self.servers[port]
            result = getattr(server, method)(*params)
            return result
        except Exception as e:
            logger.error(f"Error calling method {method} on server {port}: {e}")
            
            # Mark server as down if connection error
            if isinstance(e, (ConnectionError, xmlrpc.client.ProtocolError, 
                            xmlrpc.client.Fault, TimeoutError)):
                with self.lock:
                    self.server_status[port] = 'down'
                    logger.warning(f"Marked server on port {port} as DOWN")
            
            # Could implement retry logic here with another server
            raise
        finally:
            # Decrement connection count
            with self.lock:
                self.active_connections[port] = max(0, self.active_connections[port] - 1)
    
    def _health_check(self):
        """Check the health of all backend servers"""
        for port in self.server_ports:
            try:
                # Simple ping to check if server is alive
                self.servers[port].ping()
                
                with self.lock:
                    if self.server_status.get(port) == 'down':
                        logger.info(f"Server on port {port} is back UP")
                    self.server_status[port] = 'up'
                    self.last_health_check[port] = time.time()
            except Exception as e:
                logger.warning(f"Health check failed for server on port {port}: {e}")
                with self.lock:
                    self.server_status[port] = 'down'
    
    def _start_health_checker(self):
        """Start a background thread for periodic health checks"""
        def health_check_worker():
            while True:
                try:
                    self._health_check()
                except Exception as e:
                    logger.error(f"Error in health check worker: {e}")
                time.sleep(5)  # Check every 5 seconds
        
        health_thread = threading.Thread(target=health_check_worker, daemon=True)
        health_thread.start()
    
    def get_stats(self):
        """Get load balancer statistics"""
        with self.lock:
            return {
                'active_connections': dict(self.active_connections),
                'server_status': dict(self.server_status),
                'last_health_check': {
                    port: time.ctime(t) for port, t in self.last_health_check.items()
                }
            }


def main():
    """Run the load balancer server"""
    # Create directory for logs if it doesn't exist
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    
    # Server ports to balance between
    server_ports = [settings.BASE_SERVER_PORT + i for i in range(settings.SERVER_COUNT)]
    load_balancer_port = settings.LOAD_BALANCER_PORT
    
    load_balancer = LoadBalancer(server_ports)
    
    # Create server
    server = ThreadedXMLRPCServer(
        (settings.SERVER_HOST, load_balancer_port), 
        requestHandler=SimpleXMLRPCRequestHandler, 
        allow_none=True
    )
    server.register_introspection_functions()
    server.register_instance(load_balancer)
    
    logger.info(f"=== LOAD BALANCER STARTED ===")
    logger.info(f"Running on {settings.SERVER_HOST}:{load_balancer_port}")
    logger.info(f"Balancing between servers on ports: {server_ports}")
    print(f"=== LOAD BALANCER STARTED ===")
    print(f"Running on {settings.SERVER_HOST}:{load_balancer_port}")
    print(f"Balancing between servers on ports: {server_ports}")
    print("Clients should connect to this load balancer instead of individual servers.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Load balancer shutting down...")
        server.shutdown()


if __name__ == "__main__":
    main()