import xmlrpc.client
import xmlrpc.server
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import threading

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class LoadBalancer:
    def __init__(self, server_ports):
        self.server_ports = server_ports
        self.servers = {}
        self.active_connections = {}
        for port in server_ports:
            self.servers[port] = xmlrpc.client.ServerProxy(f"http://localhost:{port}", allow_none=True)
            self.active_connections[port] = 0
        print(f"Load Balancer initialized with servers on ports: {server_ports}")

    def _dispatch(self, method, params):
        # Select server with least active connections
        if not self.servers:
            raise Exception("No servers available")
        
        port = min(self.active_connections, key=self.active_connections.get)
        self.active_connections[port] += 1
        
        try:
            server = self.servers[port]
            result = getattr(server, method)(*params)
            return result
        except Exception as e:
            print(f"Error calling method {method} on server {port}: {e}")
            # Could implement retry logic here
            raise
        finally:
            self.active_connections[port] -= 1

def main():
    # Server ports to balance between
    server_ports = [5001, 5002, 5003]
    load_balancer_port = 5000
    
    load_balancer = LoadBalancer(server_ports)
    
    server = ThreadedXMLRPCServer(("localhost", load_balancer_port), 
                                  requestHandler=SimpleXMLRPCRequestHandler, 
                                  allow_none=True)
    server.register_introspection_functions()
    server.register_instance(load_balancer)
    
    print(f"=== LOAD BALANCER STARTED ===")
    print(f"Running on localhost:{load_balancer_port}")
    print(f"Balancing between servers on ports: {server_ports}")
    print("Clients should connect to this load balancer instead of individual servers.")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nLoad balancer shutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()