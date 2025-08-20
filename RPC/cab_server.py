from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import threading
import time
from ride import Ride
from user import User

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class CabService:
    def __init__(self):
        self.rides = {}
        self.users = {}
        self.ride_counter = 1
        self.user_counter = 1
        self.lock = threading.Lock()
    
    def register_user(self, name, email, phone):
        """Register a new user"""
        with self.lock:
            user_id = f"U{self.user_counter:03d}"
            self.user_counter += 1
            user = User(user_id, name, email, phone)
            self.users[user_id] = user
            print(f"User registered: {user}")
            return user.to_dict()
    
    def book_ride(self, user_id, pickup_location, destination):
        """Book a new ride"""
        with self.lock:
            if user_id not in self.users:
                return {"error": "User not found"}
            
            ride_id = f"R{self.ride_counter:03d}"
            self.ride_counter += 1
            
            # Calculate fare based on distance (simplified)
            fare = self._calculate_fare(pickup_location, destination)
            
            ride = Ride(ride_id, self.users[user_id].name, pickup_location, destination, fare)
            self.rides[ride_id] = ride
            
            print(f"Ride booked: {ride}")
            return ride.to_dict()
    
    def get_ride_details(self, ride_id):
        """Get details of a specific ride"""
        if ride_id in self.rides:
            return self.rides[ride_id].to_dict()
        return {"error": "Ride not found"}
    
    def cancel_ride(self, ride_id):
        """Cancel a ride"""
        with self.lock:
            if ride_id in self.rides:
                self.rides[ride_id].status = "CANCELLED"
                print(f"Ride {ride_id} cancelled")
                return {"success": f"Ride {ride_id} cancelled successfully"}
            return {"error": "Ride not found"}
    
    def get_all_rides(self, user_id=None):
        """Get all rides or rides for a specific user"""
        rides_list = []
        for ride in self.rides.values():
            if user_id is None:
                rides_list.append(ride.to_dict())
            else:
                # Check if user exists and compare names
                user = self.users.get(user_id)
                if user and user.name == ride.user_name:
                    rides_list.append(ride.to_dict())
        return rides_list
    
    def update_ride_status(self, ride_id, status):
        """Update ride status"""
        with self.lock:
            if ride_id in self.rides:
                self.rides[ride_id].status = status
                print(f"Ride {ride_id} status updated to {status}")
                return {"success": f"Ride {ride_id} status updated to {status}"}
            return {"error": "Ride not found"}
    
    def _calculate_fare(self, pickup, destination):
        """Simple fare calculation based on string length (placeholder)"""
        distance = abs(len(pickup) - len(destination)) + 5
        return round(distance * 2.5, 2)

def main():
    # Create server with allow_none=True
    server = SimpleXMLRPCServer(("localhost", 8000), requestHandler=RequestHandler, allow_none=True)
    server.register_introspection_functions()
    
    # Create and register the cab service
    cab_service = CabService()
    server.register_instance(cab_service)
    
    print("Cab Service RPC Server started on localhost:8000")
    print("Waiting for client requests...")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer shutting down...")
        server.shutdown()

if __name__ == "__main__":
    main()