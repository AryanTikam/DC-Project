class Ride:
    def __init__(self, ride_id, user_name, pickup_location, destination, fare):
        self.ride_id = ride_id
        self.user_name = user_name
        self.pickup_location = pickup_location
        self.destination = destination
        self.fare = fare
        self.status = "BOOKED"
    
    def to_dict(self):
        return {
            'ride_id': self.ride_id,
            'user_name': self.user_name,
            'pickup_location': self.pickup_location,
            'destination': self.destination,
            'fare': self.fare,
            'status': self.status
        }
    
    @classmethod
    def from_dict(cls, data):
        ride = cls(data['ride_id'], data['user_name'], 
                  data['pickup_location'], data['destination'], data['fare'])
        ride.status = data['status']
        return ride
    
    def __str__(self):
        return f"Ride {self.ride_id}: {self.user_name} from {self.pickup_location} to {self.destination} - ${self.fare} ({self.status})"