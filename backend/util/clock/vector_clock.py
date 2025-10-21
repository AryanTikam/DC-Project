"""
Implementation of Vector Clock for distributed causality tracking
"""

class VectorClock:
    def __init__(self, node_id, node_count):
        """
        Initialize a vector clock for a node in a distributed system
        
        Args:
            node_id (str): The identifier for this node
            node_count (int): The total number of nodes in the system
        """
        self.node_id = node_id
        self.clock = {}  # Dictionary to store the vector clock
    
    def increment(self):
        """Increment the local component of the vector clock"""
        self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
        return self.get_clock()
    
    def update(self, received_clock):
        """
        Update the vector clock based on a received clock
        
        Args:
            received_clock (dict): The vector clock received from another node
        """
        # For each component in the received clock, update our clock
        # to the maximum of the two values
        if not received_clock:
            return self.get_clock()
            
        for node, time in received_clock.items():
            self.clock[node] = max(self.clock.get(node, 0), time)
        
        # Increment our own component
        self.clock[self.node_id] = self.clock.get(self.node_id, 0) + 1
        
        return self.get_clock()
    
    def get_clock(self):
        """Get the current vector clock"""
        return self.clock.copy()
    
    def happens_before(self, other_clock):
        """
        Check if this vector clock happens before another vector clock
        
        Returns:
            bool: True if this clock happens before other_clock, False otherwise
        """
        # If at least one component in this clock is less than the other,
        # and no component is greater, then this clock happens before
        less_than = False
        
        for node, time in other_clock.items():
            if self.clock.get(node, 0) > time:
                return False
            if self.clock.get(node, 0) < time:
                less_than = True
                
        return less_than
    
    def concurrent_with(self, other_clock):
        """
        Check if this vector clock is concurrent with another vector clock
        
        Returns:
            bool: True if the clocks are concurrent, False otherwise
        """
        # If there's at least one component where this clock is greater,
        # and at least one where the other is greater, they're concurrent
        this_greater = False
        other_greater = False
        
        # Check components in this clock
        for node, time in self.clock.items():
            if time > other_clock.get(node, 0):
                this_greater = True
            elif time < other_clock.get(node, 0):
                other_greater = True
        
        # Check components in other clock that might not be in this clock
        for node, time in other_clock.items():
            if node not in self.clock and time > 0:
                other_greater = True
        
        return this_greater and other_greater
    
    def __str__(self):
        return f"VectorClock(node={self.node_id}, clock={self.clock})"