from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import threading
import time
from ride import Ride
from user import User

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass

class CabService:
    def __init__(self):
        self.users = {}
        self.rides = {}
        self.driver_locations = {}  # driverName -> location
        self.driver_availability = {}  # driverName -> available
        self.ride_counter = 1000
        self.lock = threading.Lock()
        self.lamport_clock = 0  # Lamport logical clock for server

        # Initialize with sample data
        self.initialize_sample_data()

    # --- Lamport helpers ---
    def _update_lamport_on_receive(self, client_clock):
        """Update server's Lamport clock upon receiving an event (RPC) with client's clock."""
        try:
            # If client_clock is None/absent, treat as 0
            rc = int(client_clock) if client_clock is not None else 0
        except Exception:
            rc = 0
        self.lamport_clock = max(self.lamport_clock, rc) + 1

    def _increment_internal(self):
        """Internal event on server increments lamport clock."""
        self.lamport_clock += 1

    # --- Data initialization ---
    def initialize_sample_data(self):
        """Initialize with some sample drivers"""
        try:
            # Add sample drivers (use client_clock 0 for initialization)
            self.register_user("driver1", "pass123", "DRIVER", 0)
            self.register_user("driver2", "pass456", "DRIVER", 0)
            self.register_user("driver3", "pass789", "DRIVER", 0)

            # Set driver availability and locations
            self.set_driver_available("driver1", "Andheri", 0)
            self.set_driver_available("driver2", "Bandra", 0)
            self.set_driver_available("driver3", "Goregaon", 0)

            print("Sample data initialized successfully")
        except Exception as e:
            print(f"Error initializing sample data: {e}")

    # --- RPC methods (each accepts client_clock as last param) ---
    def register_user(self, username, password, user_type, client_clock=None):
        """Register a new user (expects client_clock)"""
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
            return {"success": True, "message": "Registration successful", "server_clock": self.lamport_clock}

    def authenticate_user(self, username, password, client_clock=None):
        """Authenticate user credentials"""
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
        """Book a new ride"""
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
            self.driver_availability[assigned_driver] = False  # Mark driver as busy

            self._increment_internal()
            print(f"[Lamport {self.lamport_clock}] Ride booked - ID: {ride_id}, Driver: {assigned_driver}, Fare: ₹{fare}")
            return {
                "success": True,
                "ride_id": ride_id,
                "driver": assigned_driver,
                "fare": fare,
                "message": f"Cab booked successfully! Ride ID: {ride_id}",
                "server_clock": self.lamport_clock
            }

    def cancel_ride(self, ride_id, client_clock=None):
        """Cancel a ride"""
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
            return {"success": True, "message": f"Ride {ride_id} cancelled successfully", "server_clock": self.lamport_clock}

    def get_ride_status(self, ride_id, client_clock=None):
        """Get ride status"""
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
        """Set driver as available at a location"""
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
            return {"success": True, "message": f"You are now available for rides at {location}", "server_clock": self.lamport_clock}

    def get_available_cabs(self, location, client_clock=None):
        """Get list of available cabs"""
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
        """Get count of active rides"""
        self._update_lamport_on_receive(client_clock)
        active_count = sum(1 for ride in self.rides.values() if ride.status in ["ACCEPTED", "IN_PROGRESS"])
        self._increment_internal()
        return {"success": True, "count": active_count, "server_clock": self.lamport_clock}

    def get_available_drivers(self, client_clock=None):
        """Get count of available drivers"""
        self._update_lamport_on_receive(client_clock)
        available_count = sum(1 for available in self.driver_availability.values() if available)
        self._increment_internal()
        return {"success": True, "count": available_count, "server_clock": self.lamport_clock}

    def get_server_time(self, client_clock=None):
        """Return server's current wall-clock time (timestamp) and lamport clock"""
        self._update_lamport_on_receive(client_clock)
        self._increment_internal()
        return {"server_time": time.time(), "server_clock": self.lamport_clock}

    # Berkeley's algorithm kept (but now returns lamport info too)
    def synchronize_clocks(self, client_times, client_clock=None):
        """
        Berkeley's Algorithm:
        client_times: dict {client_name: timestamp}
        client_clock: lamport clock sent with this RPC
        Returns dict {client_name: offset_to_apply} and server lamport
        """
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

    # Helper methods
    def find_nearest_driver(self, pickup):
        """Find nearest available driver (simplified logic)"""
        for driver_name, is_available in self.driver_availability.items():
            if is_available:
                return driver_name
        return None

    def calculate_fare(self, pickup, destination):
        """Calculate fare based on distance (simplified)"""
        base_fare = 50.0
        distance_multiplier = 10.0

        # Mock distance calculation
        mock_distance = abs(hash(pickup) - hash(destination)) % 20 + 1

        return base_fare + (mock_distance * distance_multiplier)

def main():
    server = ThreadedXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()

    cab_service = CabService()
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
    main()
