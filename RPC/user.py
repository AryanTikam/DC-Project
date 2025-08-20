class User:
    def __init__(self, user_id, name, email, phone):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone = phone
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(data['user_id'], data['name'], data['email'], data['phone'])
    
    def __str__(self):
        return f"User {self.user_id}: {self.name} ({self.email})"