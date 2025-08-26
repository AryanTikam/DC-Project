import asyncio
import websockets
import json
import sys

class CabClient:
    def __init__(self, server_uri="ws://localhost:8765"):
        self.server_uri = server_uri
        self.websocket = None
        self.current_user = None
        self.user_type = None
        print(f"=== CAB MANAGEMENT WEBSOCKET CLIENT ===")
    
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.server_uri)
            print(f"Connected to Cab Service at {self.server_uri}")
            return True
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            return False
    
    async def send_request(self, action, **kwargs):
        """Send request to server and get response"""
        try:
            request = {"action": action, **kwargs}
            await self.websocket.send(json.dumps(request))
            
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            print(f"Error communicating with server: {e}")
            return {"success": False, "message": "Communication error"}
    
    def show_login_menu(self):
        """Display login menu"""
        print("\n=== LOGIN MENU ===")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        print("-" * 30)
    
    def show_main_menu(self):
        """Display main menu based on user type"""
        print(f"\n=== MAIN MENU === (User: {self.current_user})")
        print("1. Book a Cab")
        print("2. Check Ride Status")
        print("3. Cancel Ride")
        print("4. View Available Cabs")
        if self.user_type == "DRIVER":
            print("5. Set Driver Available (Driver only)")
        print("6. System Stats")
        print("7. Logout")
        print("-" * 50)
    
    async def register_user(self):
        """Register a new user"""
        try:
            print("\n--- Register New User ---")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            user_type = input("User type (RIDER/DRIVER): ").strip().upper()
            
            if not username or not password or user_type not in ["RIDER", "DRIVER"]:
                print("Invalid input! Please provide valid username, password, and user type.")
                return
            
            result = await self.send_request("register_user", 
                                           username=username, 
                                           password=password, 
                                           user_type=user_type)
            
            if result["success"]:
                print("Registration successful!")
            else:
                print(f"Registration failed: {result['message']}")
                
        except Exception as e:
            print(f"Error during registration: {e}")
    
    async def login_user(self):
        """Login user"""
        try:
            print("\n--- Login ---")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            
            if not username or not password:
                print("Username and password are required!")
                return
            
            result = await self.send_request("authenticate_user",
                                           username=username,
                                           password=password)
            
            if result["success"]:
                self.current_user = username
                self.user_type = result["user_type"]
                print(f"Login successful! Welcome {username} ({self.user_type})")
            else:
                print(f"Login failed: {result['message']}")
                
        except Exception as e:
            print(f"Error during login: {e}")
    
    async def book_cab(self):
        """Book a cab"""
        try:
            print("\n--- Book a Cab ---")
            pickup = input("Enter pickup location: ").strip()
            destination = input("Enter destination: ").strip()
            
            if not pickup or not destination:
                print("Both pickup and destination are required!")
                return
            
            result = await self.send_request("book_cab",
                                           username=self.current_user,
                                           pickup=pickup,
                                           destination=destination)
            
            if result["success"]:
                print(f"Cab booked successfully!")
                print(f"Ride ID: {result['ride_id']}")
                print(f"Driver: {result['driver']}")
                print(f"Fare: ₹{result['fare']}")
            else:
                print(f"Booking failed: {result['message']}")
                
        except Exception as e:
            print(f"Error booking cab: {e}")
    
    async def check_ride_status(self):
        """Check ride status"""
        try:
            print("\n--- Check Ride Status ---")
            ride_id = input("Enter ride ID: ").strip()
            
            if not ride_id:
                print("Ride ID is required!")
                return
            
            result = await self.send_request("get_ride_status", ride_id=ride_id)
            
            if result["success"]:
                print(f"Status: {result['ride_info']}")
            else:
                print(f"Error: {result['message']}")
                
        except Exception as e:
            print(f"Error checking ride status: {e}")
    
    async def cancel_ride(self):
        """Cancel a ride"""
        try:
            print("\n--- Cancel Ride ---")
            ride_id = input("Enter ride ID to cancel: ").strip()
            
            if not ride_id:
                print("Ride ID is required!")
                return
            
            result = await self.send_request("cancel_ride", ride_id=ride_id)
            
            if result["success"]:
                print(result["message"])
            else:
                print(f"Cancellation failed: {result['message']}")
                
        except Exception as e:
            print(f"Error cancelling ride: {e}")
    
    async def view_available_cabs(self):
        """View available cabs"""
        try:
            print("\n--- Available Cabs ---")
            location = input("Enter your location: ").strip()
            
            if not location:
                print("Location is required!")
                return
            
            result = await self.send_request("get_available_cabs", location=location)
            
            if result["success"]:
                cabs = result["cabs"]
                if cabs:
                    print(f"\nAvailable Cabs ({result['count']}):")
                    for cab in cabs:
                        print(f"- {cab}")
                else:
                    print("No cabs available in your area.")
            else:
                print("Error fetching available cabs")
                
        except Exception as e:
            print(f"Error fetching available cabs: {e}")
    
    async def set_driver_available(self):
        """Set driver as available"""
        try:
            print("\n--- Set Driver Available ---")
            location = input("Enter your current location: ").strip()
            
            if not location:
                print("Location is required!")
                return
            
            result = await self.send_request("set_driver_available",
                                           driver_name=self.current_user,
                                           location=location)
            
            if result["success"]:
                print(result["message"])
            else:
                print(f"Error: {result['message']}")
                
        except Exception as e:
            print(f"Error setting driver availability: {e}")
    
    async def show_system_stats(self):
        """Show system statistics"""
        try:
            print("\n--- System Statistics ---")
            
            active_rides_result = await self.send_request("get_active_rides")
            available_drivers_result = await self.send_request("get_available_drivers")
            
            if active_rides_result["success"] and available_drivers_result["success"]:
                print(f"Active Rides: {active_rides_result['count']}")
                print(f"Available Drivers: {available_drivers_result['count']}")
            else:
                print("Error fetching system statistics")
                
        except Exception as e:
            print(f"Error fetching system stats: {e}")
    
    async def run(self):
        """Main client loop"""
        if not await self.connect():
            return
        
        try:
            while True:
                if not self.current_user:
                    self.show_login_menu()
                    choice = input("Choose option (1-3): ").strip()
                    
                    if choice == '1':
                        await self.register_user()
                    elif choice == '2':
                        await self.login_user()
                    elif choice == '3':
                        print("Goodbye!")
                        break
                    else:
                        print("Invalid choice!")
                else:
                    self.show_main_menu()
                    max_choice = 7 if self.user_type == "RIDER" else 7
                    choice = input(f"Choose option (1-{max_choice}): ").strip()
                    
                    if choice == '1':
                        await self.book_cab()
                    elif choice == '2':
                        await self.check_ride_status()
                    elif choice == '3':
                        await self.cancel_ride()
                    elif choice == '4':
                        await self.view_available_cabs()
                    elif choice == '5' and self.user_type == "DRIVER":
                        await self.set_driver_available()
                    elif choice == '6':
                        await self.show_system_stats()
                    elif choice == '7':
                        self.current_user = None
                        self.user_type = None
                        print("Logged out successfully!")
                    else:
                        print("Invalid choice!")
                        
        except KeyboardInterrupt:
            print("\nGoodbye!")
        except Exception as e:
            print(f"Unexpected error: {e}")
        finally:
            if self.websocket:
                await self.websocket.close()

async def main():
    client = CabClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())