import xmlrpc.client
import sys
import time

class CabClient:
    def __init__(self, server_url="http://localhost:8000"):
        # Lamport logical clock
        self.lamport_clock = 0

        try:
            self.server = xmlrpc.client.ServerProxy(server_url, allow_none=True)
            self.current_user = None
            self.user_type = None
            print(f"=== CAB MANAGEMENT CLIENT ===")
            print(f"Connected to Cab Service at {server_url}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            sys.exit(1)

    # --- Lamport helpers ---
    def _lamport_before_send(self):
        """Increment Lamport clock before sending an event (RPC)."""
        self.lamport_clock += 1
        return self.lamport_clock

    def _lamport_update_on_receive(self, server_clock):
        """Update Lamport clock after receiving a response with server_clock."""
        try:
            sc = int(server_clock) if server_clock is not None else 0
        except Exception:
            sc = 0
        self.lamport_clock = max(self.lamport_clock, sc) + 1

    # --- UI helpers ---
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
        print("8. Sync Clock (Berkeley)")
        print("-" * 50)

    # --- RPC operations: always send lamport clock as last param and update on response ---
    def register_user(self):
        """Register a new user"""
        try:
            print("\n--- Register New User ---")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()
            user_type = input("User type (RIDER/DRIVER): ").strip().upper()

            if not username or not password or user_type not in ["RIDER", "DRIVER"]:
                print("Invalid input! Please provide valid username, password, and user type.")
                return

            send_clock = self._lamport_before_send()
            result = self.server.register_user(username, password, user_type, send_clock)
            # update lamport with server's clock
            self._lamport_update_on_receive(result.get("server_clock"))
            if result["success"]:
                print("Registration successful!")
            else:
                print(f"Registration failed: {result['message']}")

        except Exception as e:
            print(f"Error during registration: {e}")

    def login_user(self):
        """Login user"""
        try:
            print("\n--- Login ---")
            username = input("Enter username: ").strip()
            password = input("Enter password: ").strip()

            if not username or not password:
                print("Username and password are required!")
                return

            send_clock = self._lamport_before_send()
            result = self.server.authenticate_user(username, password, send_clock)
            self._lamport_update_on_receive(result.get("server_clock"))

            if result["success"]:
                self.current_user = username
                self.user_type = result["user_type"]
                print(f"Login successful! Welcome {username} ({self.user_type})")
            else:
                print(f"Login failed: {result['message']}")

        except Exception as e:
            print(f"Error during login: {e}")

    def book_cab(self):
        """Book a cab"""
        try:
            print("\n--- Book a Cab ---")
            pickup = input("Enter pickup location: ").strip()
            destination = input("Enter destination: ").strip()

            if not pickup or not destination:
                print("Both pickup and destination are required!")
                return

            send_clock = self._lamport_before_send()
            result = self.server.book_cab(self.current_user, pickup, destination, send_clock)
            self._lamport_update_on_receive(result.get("server_clock"))

            if result["success"]:
                print(f"Cab booked successfully!")
                print(f"Ride ID: {result['ride_id']}")
                print(f"Driver: {result['driver']}")
                print(f"Fare: ₹{result['fare']}")
            else:
                print(f"Booking failed: {result['message']}")

        except Exception as e:
            print(f"Error booking cab: {e}")

    def check_ride_status(self):
        """Check ride status"""
        try:
            print("\n--- Check Ride Status ---")
            ride_id = input("Enter ride ID: ").strip()

            if not ride_id:
                print("Ride ID is required!")
                return

            send_clock = self._lamport_before_send()
            result = self.server.get_ride_status(ride_id, send_clock)
            self._lamport_update_on_receive(result.get("server_clock"))

            if result["success"]:
                print(f"Status: {result['ride_info']}")
            else:
                print(f"Error: {result['message']}")

        except Exception as e:
            print(f"Error checking ride status: {e}")

    def cancel_ride(self):
        """Cancel a ride"""
        try:
            print("\n--- Cancel Ride ---")
            ride_id = input("Enter ride ID to cancel: ").strip()

            if not ride_id:
                print("Ride ID is required!")
                return

            send_clock = self._lamport_before_send()
            result = self.server.cancel_ride(ride_id, send_clock)
            self._lamport_update_on_receive(result.get("server_clock"))

            if result["success"]:
                print(result["message"])
            else:
                print(f"Cancellation failed: {result['message']}")

        except Exception as e:
            print(f"Error cancelling ride: {e}")

    def view_available_cabs(self):
        """View available cabs"""
        try:
            print("\n--- Available Cabs ---")
            location = input("Enter your location: ").strip()

            if not location:
                print("Location is required!")
                return

            send_clock = self._lamport_before_send()
            result = self.server.get_available_cabs(location, send_clock)
            self._lamport_update_on_receive(result.get("server_clock"))

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

    def set_driver_available(self):
        """Set driver as available"""
        try:
            print("\n--- Set Driver Available ---")
            location = input("Enter your current location: ").strip()

            if not location:
                print("Location is required!")
                return

            send_clock = self._lamport_before_send()
            result = self.server.set_driver_available(self.current_user, location, send_clock)
            self._lamport_update_on_receive(result.get("server_clock"))

            if result["success"]:
                print(result["message"])
            else:
                print(f"Error: {result['message']}")

        except Exception as e:
            print(f"Error setting driver availability: {e}")

    def show_system_stats(self):
        """Show system statistics"""
        try:
            print("\n--- System Statistics ---")

            send_clock = self._lamport_before_send()
            active_rides_result = self.server.get_active_rides(send_clock)
            self._lamport_update_on_receive(active_rides_result.get("server_clock"))

            send_clock = self._lamport_before_send()
            available_drivers_result = self.server.get_available_drivers(send_clock)
            self._lamport_update_on_receive(available_drivers_result.get("server_clock"))

            if active_rides_result["success"] and available_drivers_result["success"]:
                print(f"Active Rides: {active_rides_result['count']}")
                print(f"Available Drivers: {available_drivers_result['count']}")
            else:
                print("Error fetching system statistics")

        except Exception as e:
            print(f"Error fetching system stats: {e}")

    def get_local_time(self):
        """Return client's current time (timestamp)"""
        return time.time()

    def sync_clock_with_server(self):
        """Synchronize clock using Berkeley's algorithm (demo)"""
        try:
            print("\n--- Clock Synchronization (Berkeley) ---")
            local_time = self.get_local_time()
            # For demo, assume only one client; in real, collect from all clients
            client_times = {self.current_user: local_time}
            send_clock = self._lamport_before_send()
            result = self.server.synchronize_clocks(client_times, send_clock)
            self._lamport_update_on_receive(result.get("server_clock"))
            offsets = result.get("offsets", {})
            offset = offsets.get(self.current_user)
            print(f"Your clock offset (wall-clock): {offset} seconds")
            # Lamport clocks are logical; wall-clock adjustments would be separate.
        except Exception as e:
            print(f"Error during clock sync: {e}")

    def run(self):
        """Main client loop"""
        while True:
            try:
                if not self.current_user:
                    self.show_login_menu()
                    choice = input("Choose option (1-3): ").strip()

                    if choice == '1':
                        self.register_user()
                    elif choice == '2':
                        self.login_user()
                    elif choice == '3':
                        print("Goodbye!")
                        break
                    else:
                        print("Invalid choice!")
                else:
                    self.show_main_menu()
                    max_choice = 8
                    choice = input(f"Choose option (1-{max_choice}): ").strip()

                    if choice == '1':
                        self.book_cab()
                    elif choice == '2':
                        self.check_ride_status()
                    elif choice == '3':
                        self.cancel_ride()
                    elif choice == '4':
                        self.view_available_cabs()
                    elif choice == '5' and self.user_type == "DRIVER":
                        self.set_driver_available()
                    elif choice == '6':
                        self.show_system_stats()
                    elif choice == '7':
                        self.current_user = None
                        self.user_type = None
                        print("Logged out successfully!")
                    elif choice == '8':
                        self.sync_clock_with_server()
                    else:
                        print("Invalid choice!")

            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")

def main():
    client = CabClient()
    client.run()

if __name__ == "__main__":
    main()
