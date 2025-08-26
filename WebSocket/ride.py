from datetime import datetime

class Ride:
    def __init__(self, ride_id, rider_name, pickup, destination):
        self.ride_id = ride_id
        self.rider_name = rider_name
        self.driver_name = None
        self.pickup = pickup
        self.destination = destination
        self.status = "REQUESTED"  # "REQUESTED", "ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED"
        self.booking_time = datetime.now().isoformat()
        self.fare = 0.0
    
    def to_dict(self):
        return {
            'ride_id': self.ride_id,
            'rider_name': self.rider_name,
            'driver_name': self.driver_name,
            'pickup': self.pickup,
            'destination': self.destination,
            'status': self.status,
            'booking_time': self.booking_time,
            'fare': self.fare
        }
    
    @classmethod
    def from_dict(cls, data):
        ride = cls(data['ride_id'], data['rider_name'], 
                  data['pickup'], data['destination'])
        ride.driver_name = data.get('driver_name')
        ride.status = data['status']
        ride.booking_time = data['booking_time']
        ride.fare = data['fare']
        return ride
    
    def __str__(self):
        return f"Ride {self.ride_id}: {self.rider_name} from {self.pickup} to {self.destination} - ₹{self.fare} ({self.status})"