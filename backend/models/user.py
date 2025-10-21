from datetime import datetime

class User:
    def __init__(self, username, password, user_type, name=None, email=None, phone=None):
        self.username = username
        self.password = password  # In production, this should be hashed
        self.user_type = user_type  # "RIDER" or "DRIVER"
        self.name = name
        self.email = email
        self.phone = phone
        self.current_location = None
        self.rating = 5.0
        self.created_at = datetime.utcnow().isoformat()
        self.last_active = datetime.utcnow().isoformat()
        # Driver-specific attributes
        self.vehicle_info = None if user_type != "DRIVER" else {}
        self.is_available = False if user_type == "DRIVER" else None
    
    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'user_type': self.user_type,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'current_location': self.current_location,
            'rating': self.rating,
            'created_at': self.created_at,
            'last_active': self.last_active,
            'vehicle_info': self.vehicle_info,
            'is_available': self.is_available
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(
            data['username'], 
            data['password'], 
            data['user_type'],
            data.get('name'),
            data.get('email'),
            data.get('phone')
        )
        user.current_location = data.get('current_location')
        user.rating = data.get('rating', 5.0)
        user.created_at = data.get('created_at', datetime.utcnow().isoformat())
        user.last_active = data.get('last_active', datetime.utcnow().isoformat())
        user.vehicle_info = data.get('vehicle_info')
        user.is_available = data.get('is_available')
        return user
    
    def __str__(self):
        return f"User {self.username}: {self.user_type} at {self.current_location}"