// Ride.java
import java.io.Serializable;
import java.time.LocalDateTime;

class Ride implements Serializable {
    private String rideId;
    private String riderName;
    private String driverName;
    private String pickup;
    private String destination;
    private String status; // "REQUESTED", "ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED"
    private LocalDateTime bookingTime;
    private double fare;
    
    public Ride(String rideId, String riderName, String pickup, String destination) {
        this.rideId = rideId;
        this.riderName = riderName;
        this.pickup = pickup;
        this.destination = destination;
        this.status = "REQUESTED";
        this.bookingTime = LocalDateTime.now();
    }
    
    // Getters and setters
    public String getRideId() { return rideId; }
    public String getRiderName() { return riderName; }
    public String getDriverName() { return driverName; }
    public void setDriverName(String driverName) { this.driverName = driverName; }
    public String getPickup() { return pickup; }
    public String getDestination() { return destination; }
    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }
    public LocalDateTime getBookingTime() { return bookingTime; }
    public double getFare() { return fare; }
    public void setFare(double fare) { this.fare = fare; }
}
