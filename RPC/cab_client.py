import xmlrpc.client
import sys

class CabClient:
    def __init__(self, server_url="http://localhost:8000"):
        try:
            self.server = xmlrpc.client.ServerProxy(server_url)
            print(f"Connected to Cab Service at {server_url}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            sys.exit(1)
    
    def register_user(self, name, email, phone):
        """Register a new user"""
        try:
            result = self.server.register_user(name, email, phone)
            if "error" in result:
                print(f"Error: {result['error']}")
                return None
            print(f"User registered successfully!")
            print(f"User ID: {result['user_id']}")
            print(f"Name: {result['name']}")
            print(f"Email: {result['email']}")
            print(f"Phone: {result['phone']}")
            return result
        except Exception as e:
            print(f"Error registering user: {e}")
            return None
    
    def book_ride(self, user_id, pickup, destination):
        """Book a new ride"""
        try:
            result = self.server.book_ride(user_id, pickup, destination)
            if "error" in result:
                print(f"Error: {result['error']}")
                return None
            print(f"Ride booked successfully!")
            print(f"Ride ID: {result['ride_id']}")
            print(f"From: {result['pickup_location']} To: {result['destination']}")
            print(f"Fare: ${result['fare']}")
            print(f"Status: {result['status']}")
            return result
        except Exception as e:
            print(f"Error booking ride: {e}")
            return None
    
    def get_ride_details(self, ride_id):
        """Get ride details"""
        try:
            result = self.server.get_ride_details(ride_id)
            if "error" in result:
                print(f"Error: {result['error']}")
                return None
            print(f"Ride Details:")
            print(f"Ride ID: {result['ride_id']}")
            print(f"Passenger: {result['user_name']}")
            print(f"From: {result['pickup_location']} To: {result['destination']}")
            print(f"Fare: ${result['fare']}")
            print(f"Status: {result['status']}")
            return result
        except Exception as e:
            print(f"Error getting ride details: {e}")
            return None
    
    def cancel_ride(self, ride_id):
        """Cancel a ride"""
        try:
            result = self.server.cancel_ride(ride_id)
            if "error" in result:
                print(f"Error: {result['error']}")
            else:
                print(result['success'])
            return result
        except Exception as e:
            print(f"Error cancelling ride: {e}")
            return None
    
    def get_all_rides(self, user_id=None):
        """Get all rides"""
        try:
            rides = self.server.get_all_rides(user_id)
            if not rides:
                print("No rides found.")
                return []
            print(f"\nAll Rides:")
            print("-" * 60)
            for ride in rides:
                print(f"ID: {ride['ride_id']} | {ride['user_name']} | {ride['pickup_location']} → {ride['destination']} | ${ride['fare']} | {ride['status']}")
            return rides
        except Exception as e:
            print(f"Error getting rides: {e}")
            return []

def show_menu():
    print("\n" + "="*50)
    print("--- CAB BOOKING SYSTEM - RPC CLIENT ---")
    print("="*50)
    print("1. Register User")
    print("2. Book Ride")
    print("3. View Ride Details")
    print("4. Cancel Ride")
    print("5. View All Rides")
    print("6. View My Rides")
    print("7. Exit")
    print("-"*50)

def main():
    client = CabClient()
    current_user_id = None
    
    while True:
        show_menu()
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == '1':
            print("\n--- Register New User ---")
            name = input("Enter name: ").strip()
            email = input("Enter email: ").strip()
            phone = input("Enter phone: ").strip()
            
            if name and email and phone:
                user = client.register_user(name, email, phone)
                if user:
                    current_user_id = user['user_id']
                    print(f"You are now logged in as {name} (ID: {current_user_id})")
            else:
                print("All fields are required!")
        
        elif choice == '2':
            if not current_user_id:
                print("Please register first!")
                continue
            
            print("\n--- Book New Ride ---")
            pickup = input("Enter pickup location: ").strip()
            destination = input("Enter destination: ").strip()
            
            if pickup and destination:
                client.book_ride(current_user_id, pickup, destination)
            else:
                print("Both pickup and destination are required!")
        
        elif choice == '3':
            print("\n--- View Ride Details ---")
            ride_id = input("Enter ride ID: ").strip()
            if ride_id:
                client.get_ride_details(ride_id)
            else:
                print("Ride ID is required!")
        
        elif choice == '4':
            print("\n--- Cancel Ride ---")
            ride_id = input("Enter ride ID to cancel: ").strip()
            if ride_id:
                client.cancel_ride(ride_id)
            else:
                print("Ride ID is required!")
        
        elif choice == '5':
            print("\n--- All Rides ---")
            client.get_all_rides()
        
        elif choice == '6':
            if not current_user_id:
                print("Please register first!")
                continue
            print(f"\n--- Rides for User {current_user_id} ---")
            client.get_all_rides(current_user_id)
        
        elif choice == '7':
            print("Thank you for using Cab Booking System!")
            break
        
        else:
            print("Invalid choice! Please enter 1-7.")

if __name__ == "__main__":
    main()