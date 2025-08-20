// ===== REMOTE INTERFACE =====
// CabService.java
import java.rmi.Remote;
import java.rmi.RemoteException;
import java.util.List;

public interface CabService extends Remote {
    // User management methods
    boolean registerUser(String username, String password, String userType) throws RemoteException;
    boolean authenticateUser(String username, String password) throws RemoteException;
    
    // Cab booking methods
    String bookCab(String username, String pickup, String destination) throws RemoteException;
    boolean cancelRide(String rideId) throws RemoteException;
    String getRideStatus(String rideId) throws RemoteException;
    
    // Driver methods
    boolean setDriverAvailable(String driverName, String location) throws RemoteException;
    List<String> getAvailableCabs(String location) throws RemoteException;
    
    // System monitoring
    int getActiveRides() throws RemoteException;
    int getAvailableDrivers() throws RemoteException;
}