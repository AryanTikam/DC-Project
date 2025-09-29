from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
from ride import Ride
from user import User
import threading
import http.server
import urllib.request
import socket
import json
import time
import random

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def __init__(self, target_port, *args, **kwargs):
        self.target_port = target_port
        super().__init__(*args, **kwargs)

    def do_POST(self):
        target_url = f"http://localhost:{self.target_port}{self.path}"
        try:
            req = urllib.request.Request(target_url, data=self.rfile.read(int(self.headers['Content-Length'])), headers=dict(self.headers))
            with urllib.request.urlopen(req) as response:
                self.send_response(response.status)
                for header, value in response.headers.items():
                    self.send_header(header, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_error(502, f"Proxy error: {e}")

    def log_message(self, format, *args):
        pass

class CabService:
    def __init__(self, server):
        self.server = server
        self.users = {}
        self.rides = {}
        self.driver_locations = {}  
        self.driver_availability = {}  
        self.ride_counter = 1000
        self.lock = threading.Lock()
        self.lamport_clock = 0

        if self.server.is_leader:
            self.initialize_sample_data()

    def _update_lamport_on_receive(self, client_clock):
        try:
            rc = int(client_clock) if client_clock is not None else 0
        except Exception:
            rc = 0
        self.lamport_clock = max(self.lamport_clock, rc) + 1

    def _increment_internal(self):
        self.lamport_clock += 1

    def initialize_sample_data(self):
        try:
            self.register_user("driver1", "pass123", "DRIVER", 0)
            self.register_user("driver2", "pass456", "DRIVER", 0)
            self.register_user("driver3", "pass789", "DRIVER", 0)

            self.set_driver_available("driver1", "Andheri", 0)
            self.set_driver_available("driver2", "Bandra", 0)
            self.set_driver_available("driver3", "Goregaon", 0)

            print("Sample data initialized successfully")
        except Exception as e:
            print(f"Error initializing sample data: {e}")

    def register_user(self, username, password, user_type, client_clock=None):
        with self.lock:
            self._update_lamport_on_receive(client_clock)
            if username in self.users:
                return {"success": False, "message": "User already exists", "server_clock": self.lamport_clock}

            user = User(username, password, user_type)
            self.users[username] = user

            if user_type == "DRIVER":
                self.driver_availability[username] = False

            self._increment_internal()
            print(f"[Lamport {self.lamport_clock}] User registered: {username} as {user_type}")
            
            if self.server.is_leader:
                self.server.send_update('register_user', [username, password, user_type], self.lamport_clock)
            
            return {"success": True, "message": "Registration successful", "server_clock": self.lamport_clock}

    def authenticate_user(self, username, password, client_clock=None):
        self._update_lamport_on_receive(client_clock)
        user = self.users.get(username)
        if user and user.password == password:
            self._increment_internal()
            print(f"[Lamport {self.lamport_clock}] User authenticated: {username}")
            return {
                "success": True,
                "user_type": user.user_type,
                "message": "Authentication successful",
                "server_clock": self.lamport_clock
            }
        return {"success": False, "message": "Invalid credentials", "server_clock": self.lamport_clock}

    def book_cab(self, username, pickup, destination, client_clock=None):
        with self.lock:
            self._update_lamport_on_receive(client_clock)
            if username not in self.users:
                return {"success": False, "message": "User not found", "server_clock": self.lamport_clock}

            assigned_driver = self.find_nearest_driver(pickup)

            if not assigned_driver:
                return {"success": False, "message": "No driver available", "server_clock": self.lamport_clock}

            self.ride_counter += 1
            ride_id = f"RIDE_{self.ride_counter}"
            ride = Ride(ride_id, username, pickup, destination)
            ride.driver_name = assigned_driver
            ride.status = "ACCEPTED"

            fare = self.calculate_fare(pickup, destination)
            ride.fare = fare

            self.rides[ride_id] = ride
            self.driver_availability[assigned_driver] = False  

            self._increment_internal()
            print(f"[Lamport {self.lamport_clock}] Ride booked - ID: {ride_id}, Driver: {assigned_driver}, Fare: ₹{fare}")
            
            if self.server.is_leader:
                self.server.send_update('book_cab', [username, pickup, destination, fare], self.lamport_clock)
            
            return {
                "success": True,
                "ride_id": ride_id,
                "driver": assigned_driver,
                "fare": fare,
                "message": f"Cab booked successfully! Ride ID: {ride_id}",
                "server_clock": self.lamport_clock
            }

    def cancel_ride(self, ride_id, client_clock=None):
        with self.lock:
            self._update_lamport_on_receive(client_clock)
            ride = self.rides.get(ride_id)
            if not ride:
                return {"success": False, "message": "Ride not found", "server_clock": self.lamport_clock}

            if ride.status == "COMPLETED":
                return {"success": False, "message": "Cannot cancel completed ride", "server_clock": self.lamport_clock}

            ride.status = "CANCELLED"

            if ride.driver_name:
                self.driver_availability[ride.driver_name] = True

            self._increment_internal()
            print(f"[Lamport {self.lamport_clock}] Ride cancelled: {ride_id}")
            
            if self.server.is_leader:
                self.server.send_update('cancel_ride', [ride_id], self.lamport_clock)
            
            return {"success": True, "message": f"Ride {ride_id} cancelled successfully", "server_clock": self.lamport_clock}

    def get_ride_status(self, ride_id, client_clock=None):
        self._update_lamport_on_receive(client_clock)
        ride = self.rides.get(ride_id)
        if not ride:
            return {"success": False, "message": "Ride not found", "server_clock": self.lamport_clock}

        self._increment_internal()
        return {
            "success": True,
            "ride_info": f"Ride {ride_id}: {ride.status} | Driver: {ride.driver_name} | "
                         f"Pickup: {ride.pickup} | Destination: {ride.destination} | Fare: ₹{ride.fare:.2f}",
            "server_clock": self.lamport_clock
        }

    def set_driver_available(self, driver_name, location, client_clock=None):
        with self.lock:
            self._update_lamport_on_receive(client_clock)
            if driver_name not in self.users:
                return {"success": False, "message": "Driver not found", "server_clock": self.lamport_clock}

            user = self.users[driver_name]
            if user.user_type != "DRIVER":
                return {"success": False, "message": "Only registered drivers can set availability", "server_clock": self.lamport_clock}

            self.driver_availability[driver_name] = True
            self.driver_locations[driver_name] = location
            user.current_location = location

            self._increment_internal()
            print(f"[Lamport {self.lamport_clock}] Driver {driver_name} is now available at {location}")
            
            if self.server.is_leader:
                self.server.send_update('set_driver_available', [driver_name, location], self.lamport_clock)
            
            return {"success": True, "message": f"You are now available for rides at {location}", "server_clock": self.lamport_clock}

    def get_available_cabs(self, location, client_clock=None):
        self._update_lamport_on_receive(client_clock)
        available_cabs = []

        for driver_name, is_available in self.driver_availability.items():
            if is_available and driver_name in self.driver_locations:
                driver_location = self.driver_locations[driver_name]
                available_cabs.append(f"{driver_name} (Location: {driver_location})")

        self._increment_internal()
        return {
            "success": True,
            "cabs": available_cabs,
            "count": len(available_cabs),
            "server_clock": self.lamport_clock
        }

    def get_active_rides(self, client_clock=None):
        self._update_lamport_on_receive(client_clock)
        active_count = sum(1 for ride in self.rides.values() if ride.status in ["ACCEPTED", "IN_PROGRESS"])
        self._increment_internal()
        return {"success": True, "count": active_count, "server_clock": self.lamport_clock}

    def get_available_drivers(self, client_clock=None):
        self._update_lamport_on_receive(client_clock)
        available_count = sum(1 for available in self.driver_availability.values() if available)
        self._increment_internal()
        return {"success": True, "count": available_count, "server_clock": self.lamport_clock}

    def get_server_time(self, client_clock=None):
        self._update_lamport_on_receive(client_clock)
        self._increment_internal()
        return {"server_time": time.time(), "server_clock": self.lamport_clock}

    def synchronize_clocks(self, client_times, client_clock=None):
        self._update_lamport_on_receive(client_clock)
        server_time = time.time()
        all_times = [server_time] + list(client_times.values())
        avg_time = sum(all_times) / len(all_times)
        offsets = {}
        offsets["server"] = avg_time - server_time
        for client, t in client_times.items():
            offsets[client] = avg_time - t
        self._increment_internal()
        print(f"[Lamport {self.lamport_clock}] Clock sync offsets: {offsets}")
        return {"offsets": offsets, "server_clock": self.lamport_clock}

    def find_nearest_driver(self, pickup):
        for driver_name, is_available in self.driver_availability.items():
            if is_available:
                return driver_name
        return None

    def calculate_fare(self, pickup, destination):
        base_fare = 50.0
        distance_multiplier = 10.0

        mock_distance = abs(hash(pickup) - hash(destination)) % 20 + 1

        return base_fare + (mock_distance * distance_multiplier)

    def replicate_operation(self, operation, params, lamport_clock):
        with self.lock:
            self._update_lamport_on_receive(lamport_clock)
            if operation == 'register_user':
                self._register_user_internal(*params)
            elif operation == 'book_cab':
                self._book_cab_internal(*params)
            elif operation == 'cancel_ride':
                self._cancel_ride_internal(*params)
            elif operation == 'set_driver_available':
                self._set_driver_available_internal(*params)
            self._increment_internal()

    def _register_user_internal(self, username, password, user_type):
        if username in self.users:
            return
        user = User(username, password, user_type)
        self.users[username] = user
        if user_type == "DRIVER":
            self.driver_availability[username] = False
        print(f"[Lamport {self.lamport_clock}] User registered (replicated): {username} as {user_type}")

    def _book_cab_internal(self, username, pickup, destination, fare):
        if username not in self.users:
            return
        assigned_driver = self.find_nearest_driver(pickup)
        if not assigned_driver:
            return
        self.ride_counter += 1
        ride_id = f"RIDE_{self.ride_counter}"
        ride = Ride(ride_id, username, pickup, destination)
        ride.driver_name = assigned_driver
        ride.status = "ACCEPTED"
        ride.fare = fare  
        self.rides[ride_id] = ride
        self.driver_availability[assigned_driver] = False
        print(f"[Lamport {self.lamport_clock}] Ride booked (replicated) - ID: {ride_id}, Driver: {assigned_driver}, Fare: ₹{fare}")

    def _cancel_ride_internal(self, ride_id):
        ride = self.rides.get(ride_id)
        if not ride or ride.status == "COMPLETED":
            return
        ride.status = "CANCELLED"
        if ride.driver_name:
            self.driver_availability[ride.driver_name] = True
        print(f"[Lamport {self.lamport_clock}] Ride cancelled (replicated): {ride_id}")

    def _set_driver_available_internal(self, driver_name, location):
        if driver_name not in self.users:
            return
        user = self.users[driver_name]
        if user.user_type != "DRIVER":
            return
        self.driver_availability[driver_name] = True
        self.driver_locations[driver_name] = location
        user.current_location = location
        print(f"[Lamport {self.lamport_clock}] Driver {driver_name} available (replicated) at {location}")

class CabServer:
    def __init__(self, server_id, port, neighbor_port, total_servers):
        self.server_id = server_id
        self.port = port
        self.neighbor_port = neighbor_port
        self.is_leader = False
        self.active_servers = set()
        self.election_in_progress = False
        self.all_servers = list(range(1, total_servers + 1))
        self.total_servers = total_servers
        self.known_leader = 1
        self.cab_service = CabService(self)

    def send_update(self, operation, params, lamport_clock):
        for sid in self.all_servers:
            if sid != self.server_id:
                update_port = 5000 + sid + 1000
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.connect(('localhost', update_port))
                    message = {'type': 'update', 'operation': operation, 'params': params, 'lamport_clock': lamport_clock}
                    sock.send(json.dumps(message).encode())
                    sock.close()
                except Exception:
                    pass  

    def start_election(self):
        if self.election_in_progress or self.is_leader:
            return
        print(f"Server {self.server_id}: Heartbeat to leader failed. Starting election.")
        self.election_in_progress = True
        time.sleep(random.uniform(0, 2))
        if self.election_in_progress:
            initiator_port = self.port + 1000
            message = {'type': 'election', 'initiator': self.server_id, 'candidates': [self.server_id], 'initiator_port': initiator_port}
            success = self.send_to_neighbor(message)
            if not success:
                success = self.send_to_next_available_neighbor(message)
            if not success:
                if self.server_id == max(self.all_servers):
                    self.is_leader = True
                    print(f"Server {self.server_id}: Elected as leader (no neighbors available). Candidates: {message['candidates']}")
                    self.election_in_progress = False

    def handle_election(self, data):
        if data['type'] == 'election':
            initiator = data['initiator']
            candidates = data['candidates']
            initiator_port = data['initiator_port']
            if self.server_id not in candidates:
                candidates.append(self.server_id)
            print(f"Server {self.server_id}: Received election from initiator {initiator}, candidates: {candidates}")
            if initiator == self.server_id:
                leader_id = max(candidates)
                self.is_leader = (leader_id == self.server_id)
                self.known_leader = leader_id  
                print(f"Server {self.server_id}: Election complete, leader is {leader_id}, candidates: {candidates}")
                self.send_to_neighbor({'type': 'leader', 'leader_id': leader_id, 'candidates': candidates, 'initiator': self.server_id})
                self.election_in_progress = False  
            else:
                message = {'type': 'election', 'initiator': initiator, 'candidates': candidates, 'initiator_port': initiator_port}
                success = self.send_to_neighbor(message)
                if not success:
                    success = self.send_to_next_available_neighbor(message)
                if not success:
                    for attempt in range(3):
                        try:
                            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            sock.connect(('localhost', initiator_port))
                            sock.send(json.dumps(message).encode())
                            sock.close()
                            print(f"Server {self.server_id}: Sent election back to initiator {initiator}")
                            break
                        except Exception:
                            time.sleep(0.5)
                    else:
                        print(f"Server {self.server_id}: Could not send back to initiator after retries.")
        elif data['type'] == 'leader':
            leader_id = data['leader_id']
            candidates = data.get('candidates', [])
            initiator = data.get('initiator', None)
            self.known_leader = leader_id
            print(f"Server {self.server_id}: Notified of new leader {leader_id} with candidates {candidates}")
            if leader_id == self.server_id:
                self.is_leader = True
                print(f"Server {self.server_id}: Confirmed as leader. Candidates passed: {candidates}")
            else:
                self.is_leader = False
            if initiator == self.server_id:
                print(f"Server {self.server_id}: Leader notification circulated back to initiator.")
            else:
                message = {'type': 'leader', 'leader_id': leader_id, 'candidates': candidates, 'initiator': initiator}
                success = self.send_to_neighbor(message)
                if not success:
                    success = self.send_to_next_available_neighbor(message)
                if not success:
                    print(f"Server {self.server_id}: Could not forward leader message to any neighbor.")
        elif data['type'] == 'update':
            self.cab_service.replicate_operation(data['operation'], data['params'], data['lamport_clock'])
        elif data['type'] == 'heartbeat':
            pass

    def send_to_neighbor(self, message):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('localhost', self.neighbor_port + 1000))
            sock.send(json.dumps(message).encode())
            sock.close()
            return True
        except Exception:
            if message.get('type') != 'leader':
                print(f"Server {self.server_id}: Server {self.neighbor_port} down.")
            return False

    def send_to_next_available_neighbor(self, message):
        candidates = message.get('candidates', [])
        for i in range(1, self.total_servers):
            next_id = ((self.server_id + i - 1) % self.total_servers) + 1
            if next_id in candidates:
                continue
            next_port = 5000 + next_id
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect(('localhost', next_port + 1000))
                sock.send(json.dumps(message).encode())
                sock.close()
                print(f"Server {self.server_id}: Sent to next available server {next_port}")
                return True
            except Exception:
                continue
        return False

    def listen_for_election(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server_sock.bind(('localhost', self.port + 1000))
            server_sock.listen(5)
            while True:
                conn, _ = server_sock.accept()
                data = json.loads(conn.recv(1024).decode())
                self.handle_election(data)
                conn.close()
        except:
            pass
        finally:
            server_sock.close()

    def heartbeat(self):
        while True:
            time.sleep(5)
            leader_port = 5000 + self.known_leader
            for attempt in range(3):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)  
                    sock.connect(('localhost', leader_port + 1000))
                    sock.send(json.dumps({'type': 'heartbeat'}).encode())
                    sock.close()
                    break 
                except Exception as e:
                    print(f"Server {self.server_id}: Heartbeat attempt {attempt + 1} failed to leader {self.known_leader}: {e}")
                    time.sleep(1) 
            else:
                neighbor_id = (self.server_id % self.total_servers) + 1
                if neighbor_id == self.known_leader and not self.is_leader and not self.election_in_progress:
                    self.start_election()

    def run(self):
        xmlrpc_server = ThreadedXMLRPCServer(("localhost", self.port), requestHandler=RequestHandler, allow_none=True)
        xmlrpc_server.register_introspection_functions()
        xmlrpc_server.register_instance(self.cab_service)
        
        print(f"Server {self.server_id} running XML-RPC on port {self.port}")
        
        threading.Thread(target=self.listen_for_election, daemon=True).start()
        
        threading.Thread(target=self.heartbeat, daemon=True).start()
        
        if self.server_id == 1:
            self.is_leader = True
            print(f"Server {self.server_id}: Initial leader.")
        
        try:
            xmlrpc_server.serve_forever()
        except KeyboardInterrupt:
            print(f"Server {self.server_id} shutting down...")

def main():
    server = ThreadedXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()

    cab_service = CabService(None)  
    server.register_instance(cab_service)

    print("=== CAB MANAGEMENT SERVER STARTED ===")
    print("Server is running on localhost:8000")
    print("Waiting for client connections...")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        server.shutdown()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python cab_server.py <server_id> <total_servers>")
        sys.exit(1)
    server_id = int(sys.argv[1])
    total_servers = int(sys.argv[2])
    port = 5000 + server_id
    neighbor_port = 5000 + ((server_id % total_servers) + 1)
    server = CabServer(server_id, port, neighbor_port, total_servers)
    server.run()
