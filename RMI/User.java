// ===== DATA MODELS =====
// User.java
import java.io.Serializable;

class User implements Serializable {
    private String username;
    private String password;
    private String userType; // "RIDER" or "DRIVER"
    private String currentLocation;
    
    public User(String username, String password, String userType) {
        this.username = username;
        this.password = password;
        this.userType = userType;
    }
    
    // Getters and setters
    public String getUsername() { return username; }
    public String getPassword() { return password; }
    public String getUserType() { return userType; }
    public String getCurrentLocation() { return currentLocation; }
    public void setCurrentLocation(String location) { this.currentLocation = location; }
}
