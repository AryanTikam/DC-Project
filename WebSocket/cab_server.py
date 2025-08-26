import asyncio
import websockets
import json
import threading
from user import User
from ride import Ride

class CabService:
    def __init__(self):
        self.users = {}
        self.rides = {}
        self.driver_locations = {}  # driverName -> location
        self.driver_availability = {}  # driverName -> available
        self.ride_counter = 1000
        self.lock = threading.Lock()
        self.connected_clients = set()
        
        # Initialize with sample data
        self.initialize_sample_data()
    
    def initialize_sample_data(self):
        """Initialize with some sample drivers"""
        try:
            # Add sample drivers
            self.register_user("driver1", "pass123", "DRIVER")
            self.register_user("driver2", "pass456", "DRIVER")
            self.register_user("driver3", "pass789", "DRIVER")
            
            # Set driver availability and locations
            self.set_driver_available("driver1", "Andheri")
            self.set_driver_available("driver2", "Bandra")
            self.set_driver_available("driver3", "Goregaon")
            
            print("Sample data initialized successfully")
        except Exception as e:
            print(f"Error initializing sample data: {e}")
    
    def register_user(self, username, password, user_type):
        """Register a new user"""
        with self.lock:
            if username in self.users:
                return {"success": False, "message": "User already exists"}
            
            user = User(username, password, user_type)
            self.users[username] = user
            
            if user_type == "DRIVER":
                self.driver_availability[username] = False
            
            print(f"User registered: {username} as {user_type}")
            return {"success": True, "message": "Registration successful"}
    
    def authenticate_user(self, username, password):
        """Authenticate user credentials"""
        user = self.users.get(username)
        if user and user.password == password:
            print(f"User authenticated: {username}")
            return {
                "success": True, 
                "user_type": user.user_type,
                "message": "Authentication successful"
            }
        return {"success": False, "message": "Invalid credentials"}
    
    def book_cab(self, username, pickup, destination):
        """Book a new ride"""
        with self.lock:
            if username not in self.users:
                return {"success": False, "message": "User not found"}
            
            # Find available driver near pickup location
            assigned_driver = self.find_nearest_driver(pickup)
            
            if not assigned_driver:
                return {"success": False, "message": "No driver available"}
            
            # Create new ride
            self.ride_counter += 1
            ride_id = f"RIDE_{self.ride_counter}"
            ride = Ride(ride_id, username, pickup, destination)
            ride.driver_name = assigned_driver
            ride.status = "ACCEPTED"
            
            # Calculate fare
            fare = self.calculate_fare(pickup, destination)
            ride.fare = fare
            
            self.rides[ride_id] = ride
            self.driver_availability[assigned_driver] = False  # Mark driver as busy
            
            print(f"Ride booked - ID: {ride_id}, Driver: {assigned_driver}, Fare: ₹{fare}")
            return {
                "success": True,
                "ride_id": ride_id,
                "driver": assigned_driver,
                "fare": fare,
                "message": f"Cab booked successfully! Ride ID: {ride_id}"
            }
    
    def cancel_ride(self, ride_id):
        """Cancel a ride"""
        with self.lock:
            ride = self.rides.get(ride_id)
            if not ride:
                return {"success": False, "message": "Ride not found"}
            
            if ride.status == "COMPLETED":
                return {"success": False, "message": "Cannot cancel completed ride"}
            
            ride.status = "CANCELLED"
            
            # Make driver available again
            if ride.driver_name:
                self.driver_availability[ride.driver_name] = True
            
            print(f"Ride cancelled: {ride_id}")
            return {"success": True, "message": f"Ride {ride_id} cancelled successfully"}
    
    def get_ride_status(self, ride_id):
        """Get ride status"""
        ride = self.rides.get(ride_id)
        if not ride:
            return {"success": False, "message": "Ride not found"}
        
        return {
            "success": True,
            "ride_info": f"Ride {ride_id}: {ride.status} | Driver: {ride.driver_name} | "
                        f"Pickup: {ride.pickup} | Destination: {ride.destination} | Fare: ₹{ride.fare:.2f}"
        }
    
    def set_driver_available(self, driver_name, location):
        """Set driver as available at a location"""
        with self.lock:
            if driver_name not in self.users:
                return {"success": False, "message": "Driver not found"}
            
            user = self.users[driver_name]
            if user.user_type != "DRIVER":
                return {"success": False, "message": "Only registered drivers can set availability"}
            
            self.driver_availability[driver_name] = True
            self.driver_locations[driver_name] = location
            user.current_location = location
            
            print(f"Driver {driver_name} is now available at {location}")
            return {"success": True, "message": f"You are now available for rides at {location}"}
    
    def get_available_cabs(self, location):
        """Get list of available cabs"""
        available_cabs = []
        
        for driver_name, is_available in self.driver_availability.items():
            if is_available and driver_name in self.driver_locations:
                driver_location = self.driver_locations[driver_name]
                available_cabs.append(f"{driver_name} (Location: {driver_location})")
        
        return {
            "success": True,
            "cabs": available_cabs,
            "count": len(available_cabs)
        }
    
    def get_active_rides(self):
        """Get count of active rides"""
        active_count = sum(1 for ride in self.rides.values() 
                          if ride.status in ["ACCEPTED", "IN_PROGRESS"])
        return {"success": True, "count": active_count}
    
    def get_available_drivers(self):
        """Get count of available drivers"""
        available_count = sum(1 for available in self.driver_availability.values() 
                             if available)
        return {"success": True, "count": available_count}
    
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

# Global service instance
cab_service = CabService()

async def handle_client(websocket):
    """Handle individual client connections"""
    try:
        cab_service.connected_clients.add(websocket)
        print(f"Client connected: {websocket.remote_address}")
        
        async for message in websocket:
            try:
                # Parse incoming JSON message
                data = json.loads(message)
                action = data.get('action')
                
                response = await process_request(action, data)
                
                # Send response back to client
                await websocket.send(json.dumps(response))
                
            except json.JSONDecodeError:
                error_response = {
                    "success": False,
                    "message": "Invalid JSON format"
                }
                await websocket.send(json.dumps(error_response))
            except Exception as e:
                error_response = {
                    "success": False,
                    "message": f"Server error: {str(e)}"
                }
                await websocket.send(json.dumps(error_response))
                print(f"Error handling message: {e}")
                
    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        cab_service.connected_clients.discard(websocket)

async def process_request(action, data):
    """Process client requests"""
    try:
        if action == "register_user":
            return cab_service.register_user(
                data.get('username'),
                data.get('password'),
                data.get('user_type')
            )
        
        elif action == "authenticate_user":
            return cab_service.authenticate_user(
                data.get('username'),
                data.get('password')
            )
        
        elif action == "book_cab":
            return cab_service.book_cab(
                data.get('username'),
                data.get('pickup'),
                data.get('destination')
            )
        
        elif action == "cancel_ride":
            return cab_service.cancel_ride(data.get('ride_id'))
        
        elif action == "get_ride_status":
            return cab_service.get_ride_status(data.get('ride_id'))
        
        elif action == "set_driver_available":
            return cab_service.set_driver_available(
                data.get('driver_name'),
                data.get('location')
            )
        
        elif action == "get_available_cabs":
            return cab_service.get_available_cabs(data.get('location'))
        
        elif action == "get_active_rides":
            return cab_service.get_active_rides()
        
        elif action == "get_available_drivers":
            return cab_service.get_available_drivers()
        
        else:
            return {"success": False, "message": "Unknown action"}
            
    except Exception as e:
        return {"success": False, "message": f"Error processing request: {str(e)}"}

async def main():
    """Start the WebSocket server"""
    print("=== CAB MANAGEMENT WEBSOCKET SERVER ===")
    print("Starting server on ws://localhost:8765")
    print("Waiting for client connections...")
    
    # Start the WebSocket server
    async with websockets.serve(handle_client, "localhost", 8765):
        print("Server is now running...")
        # Keep server running forever
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer shutting down...")