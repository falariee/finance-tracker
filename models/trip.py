"""
Trip Model
"""

from datetime import datetime
import uuid


class Trip:
    def __init__(self, name, destination, start_date, end_date, currency, trip_id=None, travelers=None):
        self.id = trip_id or str(uuid.uuid4())
        self.name = name
        self.destination = destination
        self.start_date = start_date
        self.end_date = end_date
        self.currency = currency
        self.travelers = travelers or []
        self.created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def add_traveler(self, traveler):
        """Add a traveler to the trip"""
        self.travelers.append(traveler)
    
    def remove_traveler(self, traveler_name):
        """Remove a traveler from the trip"""
        self.travelers = [t for t in self.travelers if t.name != traveler_name]
    
    def to_dict(self):
        """Convert trip to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "destination": self.destination,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "currency": self.currency,
            "travelers": [t.to_dict() for t in self.travelers],
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create trip from dictionary"""
        from models.traveler import Traveler
        travelers = [Traveler.from_dict(t) for t in data.get("travelers", [])]
        return cls(
            name=data["name"],
            destination=data["destination"],
            start_date=data["start_date"],
            end_date=data["end_date"],
            currency=data["currency"],
            trip_id=data.get("id"),
            travelers=travelers
        )
    
    def __repr__(self):
        return f"Trip('{self.name}', {self.destination}, {len(self.travelers)} travelers)"
