"""
Main server implementation for the Cab Booking System
Provides core functionality and handles client requests
"""

from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from socketserver import ThreadingMixIn
import threading
import logging
import time
import json
import os
import sys
import random
import uuid
import datetime
import socket
import math

# Add the parent directory to sys.path to allow relative imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.ride import Ride
from models.user import User
from util.clock.lamport_clock import LamportClock
from util.clock.vector_clock import VectorClock
from util.clock.ntp_time import NTPClient, start_time_sync
from config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler()
    ]
)

class RequestHandler(SimpleXMLRPCRequestHandler):
    """XML-RPC request handler with specific RPC path"""
    rpc_paths = (settings.RPC_PATH,)

class ThreadedXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    """Threaded XML-RPC Server to handle concurrent requests"""
    pass

class CabService:
    """
    Core cab booking service implementation with features:
    - User registration and authentication
    - Ride booking, tracking, and cancellation
    - Driver management
    - Replication for fault tolerance
    - Clock synchronization
    - Vector clock for causality tracking
    """
    def __init__(self, server_id, is_leader=False):
        """
        Initialize the cab service
        
        Args:
            server_id (int): Unique identifier for this server instance
            is_leader (bool): Whether this server is the leader for consensus
        """
        self.server_id = server_id
        self.is_leader = is_leader
        self.logger = logging.getLogger(f"CabServer-{server_id}")
        
        # Data stores
        self.users = {}  # username -> User
        self.rides = {}  # ride_id -> Ride
        self.ride_counter = 1000
        self.driver_locations = {}  # driver_name -> location
        self.driver_availability = {}  # driver_name -> bool
        
        # Synchronization
        self.lock = threading.RLock()
        
        # Clock synchronization
        self.lamport_clock = LamportClock()
        self.vector_clock = VectorClock(str(server_id), settings.SERVER_COUNT)
        self.ntp_client = NTPClient()
        
        # Start time synchronization in background
        self.ntp_client.sync_time()
        start_time_sync(settings.CLOCK_SYNC_INTERVAL)
        
        # Replication
        self.peers = {}  # port -> ServerProxy
        self.init_peers()
        
        # Start with sample data if leader
        if self.is_leader:
            self.initialize_sample_data()
        
        self.logger.info(f"CabService initialized (server_id={server_id}, is_leader={is_leader})")

    def init_peers(self):
        """Initialize connections to peer servers for replication"""
        import xmlrpc.client
        
        for i in range(settings.SERVER_COUNT):
            port = settings.BASE_SERVER_PORT + i
            if port != (settings.BASE_SERVER_PORT + self.server_id):
                server_url = f"http://{settings.SERVER_HOST}:{port}{settings.RPC_PATH}"
                try:
                    self.peers[port] = xmlrpc.client.ServerProxy(server_url, allow_none=True)
                    self.logger.debug(f"Connected to peer at {server_url}")
                except Exception as e:
                    self.logger.warning(f"Failed to connect to peer at {server_url}: {e}")
    
    def _update_lamport_on_receive(self, client_clock):
        """Update Lamport clock when receiving a message"""
        return self.lamport_clock.update(client_clock)
    
    def _increment_internal(self):
        """Increment Lamport clock for internal events"""
        return self.lamport_clock.increment()

    def initialize_sample_data(self):
        """Initialize sample data for testing"""
        # Sample users
        sample_users = [
            User("alice", "pass123", "RIDER", "Alice Johnson", "alice@example.com", "9876543210"),
            User("bob", "pass123", "RIDER", "Bob Smith", "bob@example.com", "8765432109"),
            User("driver1", "pass123", "DRIVER", "Dave Driver", "driver1@example.com", "7654321098"),
            User("driver2", "pass123", "DRIVER", "Sarah Driver", "driver2@example.com", "6543210987")
        ]
        
        for user in sample_users:
            self.users[user.username] = user
            
            if user.user_type == "DRIVER":
                # Set random locations for drivers
                locations = ["Downtown", "Airport", "Mall", "University", "Tech Park"]
                user.current_location = random.choice(locations)
                user.is_available = True
                user.vehicle_info = {
                    "type": random.choice(["Sedan", "SUV", "Hatchback"]),
                    "model": random.choice(["Swift", "City", "Innova", "Creta"]),
                    "license_plate": f"KA-{random.randint(10, 99)}-{random.choice('ABCDEFGH')}-{random.randint(1000, 9999)}"
                }
                self.driver_locations[user.username] = user.current_location
                self.driver_availability[user.username] = user.is_available
        
        self.logger.info(f"Sample data initialized with {len(sample_users)} users")

    def ping(self, client_clock=None):
        """
        Simple ping method for health checks
        
        Returns:
            dict: Response with server clock
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        return {
            "status": "ok",
            "server_id": self.server_id,
            "server_clock": server_clock,
            "utc_time": self.ntp_client.get_utc_iso()
        }

    def register_user(self, username, password, user_type, name=None, email=None, phone=None, client_clock=None):
        """
        Register a new user
        
        Args:
            username (str): Username for the new user
            password (str): Password for the new user
            user_type (str): Type of user ("RIDER" or "DRIVER")
            name (str): Full name of the user
            email (str): Email address of the user
            phone (str): Phone number of the user
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with success status
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            # Check if username already exists
            if username in self.users:
                return {
                    "success": False,
                    "message": "Username already exists",
                    "server_clock": server_clock
                }
            
            # Validate user type
            if user_type not in settings.USER_TYPES:
                return {
                    "success": False,
                    "message": f"Invalid user type. Must be one of: {settings.USER_TYPES}",
                    "server_clock": server_clock
                }
            
            # Create new user
            user = User(username, password, user_type, name, email, phone)
            self.users[username] = user
            
            # Replicate to peers
            self._replicate_operation("register_user", {
                "username": username,
                "password": password,
                "user_type": user_type,
                "name": name,
                "email": email,
                "phone": phone
            })
            
            self.logger.info(f"New user registered: {username} ({user_type})")
            
            return {
                "success": True,
                "message": "User registered successfully",
                "user_type": user_type,
                "server_clock": server_clock
            }

    def authenticate_user(self, username, password, client_clock=None):
        """
        Authenticate a user
        
        Args:
            username (str): Username to authenticate
            password (str): Password to verify
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with authentication result
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            # Check if user exists
            if username not in self.users:
                return {
                    "success": False,
                    "message": "User not found",
                    "server_clock": server_clock
                }
            
            user = self.users[username]
            
            # Check password
            if user.password != password:
                return {
                    "success": False,
                    "message": "Invalid password",
                    "server_clock": server_clock
                }
            
            # Update last active timestamp
            user.last_active = datetime.datetime.utcnow().isoformat()
            
            self.logger.info(f"User authenticated: {username}")
            
            return {
                "success": True,
                "message": "Authentication successful",
                "user_type": user.user_type,
                "user_info": {
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "rating": user.rating,
                    "current_location": user.current_location
                },
                "server_clock": server_clock
            }

    def book_cab(self, username, pickup, destination, client_clock=None):
        """
        Book a new cab ride
        
        Args:
            username (str): Username of the rider
            pickup (str): Pickup location
            destination (str): Destination location
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with booking result
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            # Check if user exists and is a rider
            if username not in self.users:
                return {
                    "success": False,
                    "message": "User not found",
                    "server_clock": server_clock
                }
            
            user = self.users[username]
            if user.user_type != "RIDER":
                return {
                    "success": False,
                    "message": "Only riders can book cabs",
                    "server_clock": server_clock
                }
            
            # Generate ride ID
            ride_id = Ride.generate_ride_id()
            
            # Calculate estimated fare
            estimated_fare = self._calculate_fare(pickup, destination)
            
            # Create new ride
            ride = Ride(ride_id, username, pickup, destination)
            ride.fare = estimated_fare
            
            # Find available driver
            available_driver = self._find_nearest_driver(pickup)
            
            if available_driver:
                ride.driver_name = available_driver
                ride.status = "ACCEPTED"
                self.driver_availability[available_driver] = False
                self.logger.info(f"Ride {ride_id} assigned to driver {available_driver}")
            else:
                self.logger.info(f"No drivers available for ride {ride_id}")
            
            # Store ride
            self.rides[ride_id] = ride
            
            # Estimate distance and time
            distance = self._estimate_distance(pickup, destination)
            duration = self._estimate_duration(distance)
            
            ride.estimated_distance = distance
            ride.estimated_time = duration
            
            # Replicate to peers
            self._replicate_operation("book_ride", {
                "ride_id": ride_id,
                "rider_name": username,
                "pickup": pickup,
                "destination": destination,
                "fare": estimated_fare,
                "driver_name": ride.driver_name,
                "status": ride.status
            })
            
            self.logger.info(f"New ride booked: {ride_id} by {username}")
            
            return {
                "success": True,
                "message": "Ride booked successfully",
                "ride_id": ride_id,
                "estimated_fare": estimated_fare,
                "driver_name": ride.driver_name,
                "status": ride.status,
                "estimated_distance": distance,
                "estimated_time": duration,
                "server_clock": server_clock
            }

    def cancel_ride(self, ride_id, client_clock=None):
        """
        Cancel a booked ride
        
        Args:
            ride_id (str): ID of the ride to cancel
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with cancellation result
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            # Check if ride exists
            if ride_id not in self.rides:
                return {
                    "success": False,
                    "message": "Ride not found",
                    "server_clock": server_clock
                }
            
            ride = self.rides[ride_id]
            
            # Check if ride can be cancelled
            if ride.status in ["COMPLETED", "CANCELLED"]:
                return {
                    "success": False,
                    "message": f"Cannot cancel a ride that is {ride.status}",
                    "server_clock": server_clock
                }
            
            # Free up the driver
            if ride.driver_name and ride.driver_name in self.driver_availability:
                self.driver_availability[ride.driver_name] = True
            
            # Update ride status
            ride.update_status("CANCELLED", self.server_id)
            
            # Replicate to peers
            self._replicate_operation("cancel_ride", {
                "ride_id": ride_id
            })
            
            self.logger.info(f"Ride {ride_id} cancelled")
            
            return {
                "success": True,
                "message": "Ride cancelled successfully",
                "server_clock": server_clock
            }

    def get_ride_status(self, ride_id, client_clock=None):
        """
        Get the status of a ride
        
        Args:
            ride_id (str): ID of the ride to check
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with ride status
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            # Check if ride exists
            if ride_id not in self.rides:
                return {
                    "success": False,
                    "message": "Ride not found",
                    "server_clock": server_clock
                }
            
            ride = self.rides[ride_id]
            
            return {
                "success": True,
                "ride_info": ride.to_dict(),
                "server_clock": server_clock
            }

    def update_ride_status(self, ride_id, new_status, client_clock=None):
        """
        Update the status of a ride
        
        Args:
            ride_id (str): ID of the ride to update
            new_status (str): New status for the ride
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with update result
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            # Check if ride exists
            if ride_id not in self.rides:
                return {
                    "success": False,
                    "message": "Ride not found",
                    "server_clock": server_clock
                }
            
            ride = self.rides[ride_id]
            
            # Validate status transition
            valid_transitions = {
                "REQUESTED": ["ACCEPTED", "CANCELLED"],
                "ACCEPTED": ["IN_PROGRESS", "CANCELLED"],
                "IN_PROGRESS": ["COMPLETED", "CANCELLED"]
            }
            
            if ride.status not in valid_transitions or new_status not in valid_transitions.get(ride.status, []):
                return {
                    "success": False,
                    "message": f"Invalid status transition from {ride.status} to {new_status}",
                    "server_clock": server_clock
                }
            
            # Update ride status
            ride.update_status(new_status, self.server_id)
            
            # Replicate to peers
            self._replicate_operation("update_ride_status", {
                "ride_id": ride_id,
                "new_status": new_status
            })
            
            self.logger.info(f"Ride {ride_id} status updated to {new_status}")
            
            return {
                "success": True,
                "message": f"Ride status updated to {new_status}",
                "server_clock": server_clock
            }

    def set_driver_available(self, driver_name, location, is_available=True, client_clock=None):
        """
        Set a driver's availability and location
        
        Args:
            driver_name (str): Username of the driver
            location (str): Current location of the driver
            is_available (bool): Whether the driver is available for rides
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with update result
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            # Check if user exists and is a driver
            if driver_name not in self.users:
                return {
                    "success": False,
                    "message": "Driver not found",
                    "server_clock": server_clock
                }
            
            user = self.users[driver_name]
            if user.user_type != "DRIVER":
                return {
                    "success": False,
                    "message": "User is not a driver",
                    "server_clock": server_clock
                }
            
            # Update driver's location and availability
            user.current_location = location
            user.is_available = is_available
            self.driver_locations[driver_name] = location
            self.driver_availability[driver_name] = is_available
            
            # Replicate to peers
            self._replicate_operation("set_driver_available", {
                "driver_name": driver_name,
                "location": location,
                "is_available": is_available
            })
            
            self.logger.info(f"Driver {driver_name} set to {'available' if is_available else 'unavailable'} at {location}")
            
            return {
                "success": True,
                "message": f"Driver status updated",
                "server_clock": server_clock
            }

    def get_available_cabs(self, location, client_clock=None):
        """
        Get a list of available drivers near a location
        
        Args:
            location (str): Location to search near
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with list of available drivers
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            available_drivers = []
            
            for username, user in self.users.items():
                if (user.user_type == "DRIVER" and 
                    username in self.driver_availability and 
                    self.driver_availability[username]):
                    
                    # Check if driver is near the location
                    driver_location = self.driver_locations.get(username)
                    if driver_location:
                        # In a real system, we would calculate actual distance
                        # Here we're simplifying by considering all drivers available
                        available_drivers.append({
                            "username": username,
                            "name": user.name,
                            "location": driver_location,
                            "rating": user.rating,
                            "vehicle_info": user.vehicle_info
                        })
            
            return {
                "success": True,
                "available_drivers": available_drivers,
                "server_clock": server_clock
            }

    def get_active_rides(self, client_clock=None):
        """
        Get a list of all active rides
        
        Args:
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with list of active rides
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            active_rides = []
            
            for ride_id, ride in self.rides.items():
                if ride.status not in ["COMPLETED", "CANCELLED"]:
                    active_rides.append(ride.to_dict())
            
            return {
                "success": True,
                "active_rides": active_rides,
                "server_clock": server_clock
            }

    def get_user_rides(self, username, client_clock=None):
        """
        Get all rides for a specific user
        
        Args:
            username (str): Username to get rides for
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with list of user's rides
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            user_rides = []
            
            for ride_id, ride in self.rides.items():
                if ride.rider_name == username or ride.driver_name == username:
                    user_rides.append(ride.to_dict())
            
            return {
                "success": True,
                "rides": user_rides,
                "server_clock": server_clock
            }

    def get_server_time(self, client_clock=None):
        """
        Get the current server time
        
        Args:
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with server time info
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        return {
            "success": True,
            "utc_time": self.ntp_client.get_utc_iso(),
            "lamport_time": server_clock,
            "vector_clock": self.vector_clock.get_clock(),
            "server_clock": server_clock
        }

    def synchronize_clocks(self, client_time, client_clock=None):
        """
        Synchronize client clock with server
        
        Args:
            client_time (float): Client's current time
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with synchronization info
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        try:
            # Simple one-way synchronization
            server_time = self.ntp_client.get_time()
            time_diff = server_time - float(client_time)
            
            return {
                "success": True,
                "server_time": server_time,
                "time_diff": time_diff,
                "server_clock": server_clock
            }
        except Exception as e:
            self.logger.error(f"Error in clock synchronization: {e}")
            return {
                "success": False,
                "message": f"Clock synchronization failed: {str(e)}",
                "server_clock": server_clock
            }

    def _find_nearest_driver(self, pickup):
        """
        Find the nearest available driver to a pickup location
        
        Args:
            pickup (str): Pickup location
            
        Returns:
            str or None: Username of nearest driver, or None if no drivers available
        """
        available_drivers = []
        
        for driver, is_available in self.driver_availability.items():
            if is_available and driver in self.driver_locations:
                available_drivers.append(driver)
        
        if not available_drivers:
            return None
        
        # In a real system, we would calculate actual distances
        # For now, just pick a random available driver
        return random.choice(available_drivers)

    def _calculate_fare(self, pickup, destination):
        """
        Calculate the fare for a ride
        
        Args:
            pickup (str): Pickup location
            destination (str): Destination location
            
        Returns:
            float: Estimated fare
        """
        # Calculate estimated distance
        distance = self._estimate_distance(pickup, destination)
        
        # Calculate fare based on distance
        base_fare = settings.BASE_FARE
        per_km_rate = settings.PER_KM_RATE
        surge_factor = settings.SURGE_FACTOR
        
        fare = base_fare + (distance * per_km_rate)
        fare *= surge_factor
        
        return round(fare, 2)

    def _estimate_distance(self, pickup, destination):
        """
        Estimate the distance between two locations
        
        In a real system, this would use a mapping service.
        Here we're using a simple heuristic.
        
        Args:
            pickup (str): Pickup location
            destination (str): Destination location
            
        Returns:
            float: Estimated distance in kilometers
        """
        # For demo purposes, generate a random but consistent distance
        # based on the location strings
        def hash_location(loc):
            return sum(ord(c) for c in loc)
        
        pickup_hash = hash_location(pickup)
        dest_hash = hash_location(destination)
        
        # Generate a distance between 1 and 30 km
        distance = 1 + (abs(pickup_hash - dest_hash) % 29)
        
        return round(distance, 1)

    def _estimate_duration(self, distance):
        """
        Estimate the duration of a ride based on distance
        
        Args:
            distance (float): Distance in kilometers
            
        Returns:
            int: Estimated duration in minutes
        """
        # Assume average speed of 30 km/h
        avg_speed = 30
        
        # Convert distance to minutes
        duration = (distance / avg_speed) * 60
        
        # Add 5 minutes for pickup
        duration += 5
        
        return int(round(duration))

    def _replicate_operation(self, operation, params):
        """
        Replicate an operation to peer servers
        
        Args:
            operation (str): Name of the operation to replicate
            params (dict): Parameters for the operation
        """
        # Only replicate if replication is enabled
        if settings.REPLICATION_MODE == "none":
            return
        
        # Update vector clock
        self.vector_clock.increment()
        params["vector_clock"] = self.vector_clock.get_clock()
        
        # Synchronous replication waits for all peers to acknowledge
        if settings.REPLICATION_MODE == "synchronous":
            for port, peer in self.peers.items():
                try:
                    getattr(peer, f"_replicate_{operation}")(params, self.lamport_clock.get_time())
                except Exception as e:
                    self.logger.error(f"Failed to replicate {operation} to peer at port {port}: {e}")
                    # In a production system, we might want to retry or handle this differently
        
        # Asynchronous replication happens in the background
        elif settings.REPLICATION_MODE == "asynchronous":
            def replicate_async():
                for port, peer in self.peers.items():
                    try:
                        getattr(peer, f"_replicate_{operation}")(params, self.lamport_clock.get_time())
                    except Exception as e:
                        self.logger.error(f"Failed to replicate {operation} to peer at port {port}: {e}")
            
            threading.Thread(target=replicate_async, daemon=True).start()

    # Replication endpoint methods
    def _replicate_register_user(self, params, client_clock=None):
        """Replicate user registration"""
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            username = params["username"]
            password = params["password"]
            user_type = params["user_type"]
            name = params.get("name")
            email = params.get("email")
            phone = params.get("phone")
            
            # Create new user if it doesn't exist
            if username not in self.users:
                user = User(username, password, user_type, name, email, phone)
                self.users[username] = user
                self.logger.info(f"Replicated new user: {username}")
            
            # Update vector clock if provided
            vector_clock = params.get("vector_clock")
            if vector_clock:
                self.vector_clock.update(vector_clock)
                
            return {"success": True, "server_clock": server_clock}

    def _replicate_book_ride(self, params, client_clock=None):
        """Replicate ride booking"""
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            ride_id = params["ride_id"]
            rider_name = params["rider_name"]
            pickup = params["pickup"]
            destination = params["destination"]
            fare = params["fare"]
            driver_name = params.get("driver_name")
            status = params.get("status", "REQUESTED")
            
            # Create new ride if it doesn't exist
            if ride_id not in self.rides:
                ride = Ride(ride_id, rider_name, pickup, destination)
                ride.fare = fare
                ride.driver_name = driver_name
                ride.status = status
                self.rides[ride_id] = ride
                self.logger.info(f"Replicated new ride: {ride_id}")
                
                # Update driver availability
                if driver_name and driver_name in self.driver_availability:
                    self.driver_availability[driver_name] = False
            
            # Update vector clock if provided
            vector_clock = params.get("vector_clock")
            if vector_clock:
                self.vector_clock.update(vector_clock)
                
            return {"success": True, "server_clock": server_clock}

    def _replicate_cancel_ride(self, params, client_clock=None):
        """Replicate ride cancellation"""
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            ride_id = params["ride_id"]
            
            if ride_id in self.rides:
                ride = self.rides[ride_id]
                ride.update_status("CANCELLED", self.server_id)
                
                # Free up the driver
                if ride.driver_name and ride.driver_name in self.driver_availability:
                    self.driver_availability[ride.driver_name] = True
                    
                self.logger.info(f"Replicated ride cancellation: {ride_id}")
            
            # Update vector clock if provided
            vector_clock = params.get("vector_clock")
            if vector_clock:
                self.vector_clock.update(vector_clock)
                
            return {"success": True, "server_clock": server_clock}

    def _replicate_update_ride_status(self, params, client_clock=None):
        """Replicate ride status update"""
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            ride_id = params["ride_id"]
            new_status = params["new_status"]
            
            if ride_id in self.rides:
                ride = self.rides[ride_id]
                ride.update_status(new_status, self.server_id)
                self.logger.info(f"Replicated ride status update: {ride_id} -> {new_status}")
            
            # Update vector clock if provided
            vector_clock = params.get("vector_clock")
            if vector_clock:
                self.vector_clock.update(vector_clock)
                
            return {"success": True, "server_clock": server_clock}

    def _replicate_set_driver_available(self, params, client_clock=None):
        """Replicate driver availability update"""
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            driver_name = params["driver_name"]
            location = params["location"]
            is_available = params["is_available"]
            
            if driver_name in self.users:
                user = self.users[driver_name]
                user.current_location = location
                user.is_available = is_available
                self.driver_locations[driver_name] = location
                self.driver_availability[driver_name] = is_available
                self.logger.info(f"Replicated driver availability: {driver_name} -> {is_available}")
            
            # Update vector clock if provided
            vector_clock = params.get("vector_clock")
            if vector_clock:
                self.vector_clock.update(vector_clock)
                
            return {"success": True, "server_clock": server_clock}

    def get_server_stats(self, client_clock=None):
        """
        Get server statistics
        
        Args:
            client_clock (int): Client's Lamport clock value
            
        Returns:
            dict: Response with server statistics
        """
        server_clock = self._update_lamport_on_receive(client_clock)
        
        with self.lock:
            active_rides = len([r for r in self.rides.values() if r.status not in ["COMPLETED", "CANCELLED"]])
            completed_rides = len([r for r in self.rides.values() if r.status == "COMPLETED"])
            cancelled_rides = len([r for r in self.rides.values() if r.status == "CANCELLED"])
            
            rider_count = len([u for u in self.users.values() if u.user_type == "RIDER"])
            driver_count = len([u for u in self.users.values() if u.user_type == "DRIVER"])
            
            available_drivers = len([d for d, available in self.driver_availability.items() if available])
            
            stats = {
                "server_id": self.server_id,
                "is_leader": self.is_leader,
                "lamport_clock": self.lamport_clock.get_time(),
                "vector_clock": self.vector_clock.get_clock(),
                "system_time": self.ntp_client.get_utc_iso(),
                "users": {
                    "total": len(self.users),
                    "riders": rider_count,
                    "drivers": driver_count,
                },
                "rides": {
                    "total": len(self.rides),
                    "active": active_rides,
                    "completed": completed_rides,
                    "cancelled": cancelled_rides,
                },
                "drivers": {
                    "total": driver_count,
                    "available": available_drivers,
                }
            }
            
            return {
                "success": True,
                "stats": stats,
                "server_clock": server_clock
            }


class CabServer:
    """
    Main server class that initializes the XML-RPC server and cab service
    """
    def __init__(self, server_id=0):
        """
        Initialize the cab server
        
        Args:
            server_id (int): Unique identifier for this server instance
        """
        self.server_id = server_id
        self.is_leader = (server_id == 0)  # First server is the leader by default
        self.port = settings.BASE_SERVER_PORT + server_id
        
        # Create directory for logs if it doesn't exist
        os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
        
        self.logger = logging.getLogger(f"CabServer-{server_id}")
        
        # Initialize the XML-RPC server
        self.server = ThreadedXMLRPCServer(
            (settings.SERVER_HOST, self.port),
            requestHandler=RequestHandler,
            allow_none=True
        )
        
        # Initialize the cab service
        self.cab_service = CabService(server_id, self.is_leader)
        
        # Register the cab service with the server
        self.server.register_introspection_functions()
        self.server.register_instance(self.cab_service)
    
    def run(self):
        """Start the server and run indefinitely"""
        self.logger.info(f"=== CAB SERVER {self.server_id} STARTED ===")
        self.logger.info(f"Running on {settings.SERVER_HOST}:{self.port}")
        self.logger.info(f"Is leader: {self.is_leader}")
        
        print(f"=== CAB SERVER {self.server_id} STARTED ===")
        print(f"Running on {settings.SERVER_HOST}:{self.port}")
        print(f"Is leader: {self.is_leader}")
        print("Waiting for client connections...")
        
        try:
            self.server.serve_forever()
        except KeyboardInterrupt:
            self.logger.info("Server shutting down...")
            print("Server shutting down...")
            self.server.shutdown()


def main():
    """Run the cab server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Cab Server')
    parser.add_argument('--id', type=int, default=0, help='Server ID')
    args = parser.parse_args()
    
    server = CabServer(args.id)
    server.run()


if __name__ == "__main__":
    main()