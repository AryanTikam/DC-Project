from datetime import datetime
import uuid

class Ride:
    def __init__(self, ride_id, rider_name, pickup, destination):
        self.ride_id = ride_id
        self.rider_name = rider_name
        self.driver_name = None
        self.pickup = pickup
        self.destination = destination
        self.status = "REQUESTED"  # "REQUESTED", "ACCEPTED", "IN_PROGRESS", "COMPLETED", "CANCELLED"
        self.booking_time = datetime.utcnow().isoformat()
        self.start_time = None
        self.end_time = None
        self.estimated_time = None
        self.estimated_distance = None
        self.fare = 0.0
        self.payment_status = "PENDING"  # "PENDING", "COMPLETED", "FAILED"
        self.rider_rating = None
        self.driver_rating = None
        self.version = 0  # For optimistic concurrency control
        self.vector_clock = {}  # For vector clock implementation
    
    def to_dict(self):
        return {
            'ride_id': self.ride_id,
            'rider_name': self.rider_name,
            'driver_name': self.driver_name,
            'pickup': self.pickup,
            'destination': self.destination,
            'status': self.status,
            'booking_time': self.booking_time,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'estimated_time': self.estimated_time,
            'estimated_distance': self.estimated_distance,
            'fare': self.fare,
            'payment_status': self.payment_status,
            'rider_rating': self.rider_rating,
            'driver_rating': self.driver_rating,
            'version': self.version,
            'vector_clock': self.vector_clock
        }
    
    @classmethod
    def from_dict(cls, data):
        ride = cls(
            data['ride_id'], 
            data['rider_name'], 
            data['pickup'], 
            data['destination']
        )
        ride.driver_name = data.get('driver_name')
        ride.status = data.get('status', 'REQUESTED')
        ride.booking_time = data.get('booking_time', datetime.utcnow().isoformat())
        ride.start_time = data.get('start_time')
        ride.end_time = data.get('end_time')
        ride.estimated_time = data.get('estimated_time')
        ride.estimated_distance = data.get('estimated_distance')
        ride.fare = data.get('fare', 0.0)
        ride.payment_status = data.get('payment_status', 'PENDING')
        ride.rider_rating = data.get('rider_rating')
        ride.driver_rating = data.get('driver_rating')
        ride.version = data.get('version', 0)
        ride.vector_clock = data.get('vector_clock', {})
        return ride
    
    def update_status(self, new_status, server_id):
        self.status = new_status
        self.version += 1
        self.vector_clock[server_id] = self.vector_clock.get(server_id, 0) + 1
        
        # Update timestamps based on status change
        now = datetime.utcnow().isoformat()
        if new_status == "ACCEPTED":
            pass
        elif new_status == "IN_PROGRESS":
            self.start_time = now
        elif new_status == "COMPLETED":
            self.end_time = now
    
    def __str__(self):
        status_str = f"({self.status})"
        driver_str = f"with {self.driver_name}" if self.driver_name else "awaiting driver"
        fare_str = f"₹{self.fare}" if self.fare > 0 else "calculating fare"
        return f"Ride {self.ride_id}: {self.rider_name} from {self.pickup} to {self.destination} - {fare_str} {status_str} {driver_str}"

    @staticmethod
    def generate_ride_id():
        return str(uuid.uuid4().hex)[:8]