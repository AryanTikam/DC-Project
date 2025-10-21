"""
Implementation of Lamport Clock for distributed timestamp ordering
"""

class LamportClock:
    def __init__(self, initial_time=0):
        self.time = initial_time
    
    def get_time(self):
        """Get the current logical time"""
        return self.time
    
    def increment(self):
        """Increment the clock when a local event occurs"""
        self.time += 1
        return self.time
    
    def update(self, received_time):
        """Update the clock based on a received message's timestamp"""
        try:
            # Handle case where received_time might be None or not a number
            rt = int(received_time) if received_time is not None else 0
        except (ValueError, TypeError):
            rt = 0
            
        # Update to the max of local time and received time, then increment
        self.time = max(self.time, rt) + 1
        return self.time
    
    def __str__(self):
        return f"LamportClock(time={self.time})"