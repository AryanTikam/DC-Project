// ===== SERVER APPLICATION =====
// CabServer.java
import java.rmi.Naming;
import java.rmi.registry.LocateRegistry;

public class CabServer {
    public static void main(String[] args) {
        try {
            // Create and start RMI registry on port 1099
            LocateRegistry.createRegistry(1099);
            
            // Create service implementation
            CabServiceImpl cabService = new CabServiceImpl();
            
            // Bind service to registry
            Naming.rebind("//localhost/CabService", cabService);
            
            System.out.println("=== CAB MANAGEMENT SERVER STARTED ===");
            System.out.println("Server is running on port 1099");
            System.out.println("Service bound as: CabService");
            System.out.println("Waiting for client connections...");
            
            // Keep server running
            Thread.currentThread().join();
            
        } catch (Exception e) {
            System.err.println("Server error: " + e.getMessage());
            e.printStackTrace();
        }
    }
}