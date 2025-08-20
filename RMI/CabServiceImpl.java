// ===== SERVER IMPLEMENTATION =====
// CabServiceImpl.java
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class CabServiceImpl extends UnicastRemoteObject implements CabService {
    private Map<String, User> users;
    private Map<String, Ride> rides;
    private Map<String, String> driverLocations; // driverName -> location
    private Map<String, Boolean> driverAvailability; // driverName -> available
    private AtomicInteger rideCounter;
    
    public CabServiceImpl() throws RemoteException {
        super();
        this.users = new ConcurrentHashMap<>();
        this.rides = new ConcurrentHashMap<>();
        this.driverLocations = new ConcurrentHashMap<>();
        this.driverAvailability = new ConcurrentHashMap<>();
        this.rideCounter = new AtomicInteger(1000);
        
        // Initialize with some sample data
        initializeSampleData();
    }
    
    private void initializeSampleData() {
        try {
            // Add sample drivers
            registerUser("driver1", "pass123", "DRIVER");
            registerUser("driver2", "pass456", "DRIVER");
            registerUser("driver3", "pass789", "DRIVER");
            
            // Set driver availability and locations
            setDriverAvailable("driver1", "Andheri");
            setDriverAvailable("driver2", "Bandra");
            setDriverAvailable("driver3", "Goregaon");
            
            System.out.println("Sample data initialized successfully");
        } catch (Exception e) {
            System.err.println("Error initializing sample data: " + e.getMessage());
        }
    }
    
    @Override
    public boolean registerUser(String username, String password, String userType) throws RemoteException {
        if (users.containsKey(username)) {
            return false; // User already exists
        }
        
        User user = new User(username, password, userType);
        users.put(username, user);
        
        if ("DRIVER".equals(userType)) {
            driverAvailability.put(username, false);
        }
        
        System.out.println("User registered: " + username + " as " + userType);
        return true;
    }
    
    @Override
    public boolean authenticateUser(String username, String password) throws RemoteException {
        User user = users.get(username);
        if (user != null && user.getPassword().equals(password)) {
            System.out.println("User authenticated: " + username);
            return true;
        }
        return false;
    }
    
    @Override
    public String bookCab(String username, String pickup, String destination) throws RemoteException {
        // Find available driver near pickup location
        String assignedDriver = findNearestDriver(pickup);
        
        if (assignedDriver == null) {
            return "NO_DRIVER_AVAILABLE";
        }
        
        // Create new ride
        String rideId = "RIDE_" + rideCounter.incrementAndGet();
        Ride ride = new Ride(rideId, username, pickup, destination);
        ride.setDriverName(assignedDriver);
        ride.setStatus("ACCEPTED");
        
        // Calculate fare (simple distance-based calculation)
        double fare = calculateFare(pickup, destination);
        ride.setFare(fare);
        
        rides.put(rideId, ride);
        driverAvailability.put(assignedDriver, false); // Mark driver as busy
        
        System.out.println("Ride booked - ID: " + rideId + ", Driver: " + assignedDriver + 
                          ", Fare: ₹" + fare);
        return rideId;
    }
    
    @Override
    public boolean cancelRide(String rideId) throws RemoteException {
        Ride ride = rides.get(rideId);
        if (ride != null && !"COMPLETED".equals(ride.getStatus())) {
            ride.setStatus("CANCELLED");
            
            // Make driver available again
            if (ride.getDriverName() != null) {
                driverAvailability.put(ride.getDriverName(), true);
            }
            
            System.out.println("Ride cancelled: " + rideId);
            return true;
        }
        return false;
    }
    
    @Override
    public String getRideStatus(String rideId) throws RemoteException {
        Ride ride = rides.get(rideId);
        if (ride != null) {
            return String.format("Ride %s: %s | Driver: %s | Pickup: %s | Destination: %s | Fare: ₹%.2f",
                    rideId, ride.getStatus(), ride.getDriverName(), 
                    ride.getPickup(), ride.getDestination(), ride.getFare());
        }
        return "RIDE_NOT_FOUND";
    }
    
    @Override
    public boolean setDriverAvailable(String driverName, String location) throws RemoteException {
        if (users.containsKey(driverName) && "DRIVER".equals(users.get(driverName).getUserType())) {
            driverAvailability.put(driverName, true);
            driverLocations.put(driverName, location);
            System.out.println("Driver " + driverName + " is now available at " + location);
            return true;
        }
        return false;
    }
    
    @Override
    public List<String> getAvailableCabs(String location) throws RemoteException {
        List<String> availableCabs = new ArrayList<>();
        
        for (Map.Entry<String, Boolean> entry : driverAvailability.entrySet()) {
            String driverName = entry.getKey();
            Boolean isAvailable = entry.getValue();
            
            if (isAvailable && driverLocations.containsKey(driverName)) {
                String driverLocation = driverLocations.get(driverName);
                availableCabs.add(driverName + " (Location: " + driverLocation + ")");
            }
        }
        
        return availableCabs;
    }
    
    @Override
    public int getActiveRides() throws RemoteException {
        return (int) rides.values().stream()
                .filter(ride -> "ACCEPTED".equals(ride.getStatus()) || "IN_PROGRESS".equals(ride.getStatus()))
                .count();
    }
    
    @Override
    public int getAvailableDrivers() throws RemoteException {
        return (int) driverAvailability.values().stream()
                .filter(available -> available)
                .count();
    }
    
    // Helper methods
    private String findNearestDriver(String pickup) {
        // Simplified logic - in real system, use geospatial algorithms
        for (Map.Entry<String, Boolean> entry : driverAvailability.entrySet()) {
            String driverName = entry.getKey();
            Boolean isAvailable = entry.getValue();
            
            if (isAvailable) {
                return driverName;
            }
        }
        return null;
    }
    
    private double calculateFare(String pickup, String destination) {
        // Simplified fare calculation - base fare + distance multiplier
        double baseFare = 50.0;
        double distanceMultiplier = 10.0; // ₹10 per "unit distance"
        
        // Mock distance calculation (in real system, use actual distance APIs)
        int mockDistance = Math.abs(pickup.hashCode() - destination.hashCode()) % 20 + 1;
        
        return baseFare + (mockDistance * distanceMultiplier);
    }
}