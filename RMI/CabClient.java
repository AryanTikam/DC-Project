// ===== CLIENT APPLICATION =====
// CabClient.java
import java.rmi.Naming;
import java.util.List;
import java.util.Scanner;

public class CabClient {
    private static CabService cabService;
    private static Scanner scanner;
    private static String currentUser;
    
    public static void main(String[] args) {
        try {
            // Connect to RMI service
            cabService = (CabService) Naming.lookup("//localhost/CabService");
            scanner = new Scanner(System.in);
            
            System.out.println("=== CAB MANAGEMENT CLIENT ===");
            System.out.println("Connected to server successfully!");
            
            // Main menu loop
            while (true) {
                if (currentUser == null) {
                    showLoginMenu();
                } else {
                    showMainMenu();
                }
            }
            
        } catch (Exception e) {
            System.err.println("Client error: " + e.getMessage());
            e.printStackTrace();
        }
    }
    
    private static void showLoginMenu() {
        try {
            System.out.println("\n=== LOGIN MENU ===");
            System.out.println("1. Register");
            System.out.println("2. Login");
            System.out.println("3. Exit");
            System.out.print("Choose option: ");
            
            int choice = scanner.nextInt();
            scanner.nextLine(); // consume newline
            
            switch (choice) {
                case 1:
                    registerUser();
                    break;
                case 2:
                    loginUser();
                    break;
                case 3:
                    System.out.println("Goodbye!");
                    System.exit(0);
                    break;
                default:
                    System.out.println("Invalid choice!");
            }
        } catch (Exception e) {
            System.err.println("Error in login menu: " + e.getMessage());
            scanner.nextLine(); // clear invalid input
        }
    }
    
    private static void showMainMenu() {
        try {
            System.out.println("\n=== MAIN MENU === (User: " + currentUser + ")");
            System.out.println("1. Book a Cab");
            System.out.println("2. Check Ride Status");
            System.out.println("3. Cancel Ride");
            System.out.println("4. View Available Cabs");
            System.out.println("5. Set Driver Available (Driver only)");
            System.out.println("6. System Stats");
            System.out.println("7. Logout");
            System.out.print("Choose option: ");
            
            int choice = scanner.nextInt();
            scanner.nextLine(); // consume newline
            
            switch (choice) {
                case 1:
                    bookCab();
                    break;
                case 2:
                    checkRideStatus();
                    break;
                case 3:
                    cancelRide();
                    break;
                case 4:
                    viewAvailableCabs();
                    break;
                case 5:
                    setDriverAvailable();
                    break;
                case 6:
                    showSystemStats();
                    break;
                case 7:
                    currentUser = null;
                    System.out.println("Logged out successfully!");
                    break;
                default:
                    System.out.println("Invalid choice!");
            }
        } catch (Exception e) {
            System.err.println("Error in main menu: " + e.getMessage());
            scanner.nextLine(); // clear invalid input
        }
    }
    
    private static void registerUser() {
        try {
            System.out.print("Enter username: ");
            String username = scanner.nextLine();
            System.out.print("Enter password: ");
            String password = scanner.nextLine();
            System.out.print("User type (RIDER/DRIVER): ");
            String userType = scanner.nextLine().toUpperCase();
            
            boolean success = cabService.registerUser(username, password, userType);
            if (success) {
                System.out.println("Registration successful!");
            } else {
                System.out.println("Registration failed - user already exists!");
            }
        } catch (Exception e) {
            System.err.println("Registration error: " + e.getMessage());
        }
    }
    
    private static void loginUser() {
        try {
            System.out.print("Enter username: ");
            String username = scanner.nextLine();
            System.out.print("Enter password: ");
            String password = scanner.nextLine();
            
            boolean success = cabService.authenticateUser(username, password);
            if (success) {
                currentUser = username;
                System.out.println("Login successful! Welcome " + username);
            } else {
                System.out.println("Invalid credentials!");
            }
        } catch (Exception e) {
            System.err.println("Login error: " + e.getMessage());
        }
    }
    
    private static void bookCab() {
        try {
            System.out.print("Enter pickup location: ");
            String pickup = scanner.nextLine();
            System.out.print("Enter destination: ");
            String destination = scanner.nextLine();
            
            String result = cabService.bookCab(currentUser, pickup, destination);
            if ("NO_DRIVER_AVAILABLE".equals(result)) {
                System.out.println("Sorry, no drivers available at the moment!");
            } else {
                System.out.println("Cab booked successfully! Ride ID: " + result);
            }
        } catch (Exception e) {
            System.err.println("Booking error: " + e.getMessage());
        }
    }
    
    private static void checkRideStatus() {
        try {
            System.out.print("Enter ride ID: ");
            String rideId = scanner.nextLine();
            
            String status = cabService.getRideStatus(rideId);
            System.out.println("Status: " + status);
        } catch (Exception e) {
            System.err.println("Status check error: " + e.getMessage());
        }
    }
    
    private static void cancelRide() {
        try {
            System.out.print("Enter ride ID to cancel: ");
            String rideId = scanner.nextLine();
            
            boolean success = cabService.cancelRide(rideId);
            if (success) {
                System.out.println("Ride cancelled successfully!");
            } else {
                System.out.println("Could not cancel ride - check ride ID or status!");
            }
        } catch (Exception e) {
            System.err.println("Cancellation error: " + e.getMessage());
        }
    }
    
    private static void viewAvailableCabs() {
        try {
            System.out.print("Enter your location: ");
            String location = scanner.nextLine();
            
            List<String> availableCabs = cabService.getAvailableCabs(location);
            System.out.println("\nAvailable Cabs:");
            if (availableCabs.isEmpty()) {
                System.out.println("No cabs available in your area.");
            } else {
                for (String cab : availableCabs) {
                    System.out.println("- " + cab);
                }
            }
        } catch (Exception e) {
            System.err.println("Error fetching available cabs: " + e.getMessage());
        }
    }
    
    private static void setDriverAvailable() {
        try {
            System.out.print("Enter your current location: ");
            String location = scanner.nextLine();
            
            boolean success = cabService.setDriverAvailable(currentUser, location);
            if (success) {
                System.out.println("You are now available for rides!");
            } else {
                System.out.println("Error: Only registered drivers can set availability!");
            }
        } catch (Exception e) {
            System.err.println("Error setting availability: " + e.getMessage());
        }
    }
    
    private static void showSystemStats() {
        try {
            int activeRides = cabService.getActiveRides();
            int availableDrivers = cabService.getAvailableDrivers();
            
            System.out.println("\n=== SYSTEM STATISTICS ===");
            System.out.println("Active Rides: " + activeRides);
            System.out.println("Available Drivers: " + availableDrivers);
        } catch (Exception e) {
            System.err.println("Error fetching system stats: " + e.getMessage());
        }
    }
}