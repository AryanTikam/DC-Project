class User:
    def __init__(self, username, password, user_type):
        self.username = username
        self.password = password
        self.user_type = user_type  # "RIDER" or "DRIVER"
        self.current_location = None
    
    def to_dict(self):
        return {
            'username': self.username,
            'password': self.password,
            'user_type': self.user_type,
            'current_location': self.current_location
        }
    
    @classmethod
    def from_dict(cls, data):
        user = cls(data['username'], data['password'], data['user_type'])
        user.current_location = data.get('current_location')
        return user
    
    def __str__(self):
        return f"User {self.username}: {self.user_type} at {self.current_location}"