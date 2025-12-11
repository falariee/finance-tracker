"""
Traveler Model
"""

import uuid


class Traveler:
    def __init__(self, name, email="", traveler_id=None):
        self.id = traveler_id or str(uuid.uuid4())
        self.name = name
        self.email = email
    
    def to_dict(self):
        """Convert traveler to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create traveler from dictionary"""
        return cls(
            name=data["name"],
            email=data.get("email", ""),
            traveler_id=data.get("id")
        )
    
    def __repr__(self):
        return f"Traveler('{self.name}')"
