"""
Expense Model
"""

from datetime import datetime
import uuid


class Expense:
    def __init__(self, description, amount, currency, category, paid_by, date=None, expense_id=None, split_with=None):
        self.id = expense_id or str(uuid.uuid4())
        self.description = description
        self.amount = float(amount)
        self.currency = currency
        self.category = category
        self.paid_by = paid_by
        self.date = date or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.split_with = split_with or []
    
    def to_dict(self):
        """Convert expense to dictionary"""
        return {
            "id": self.id,
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "category": self.category,
            "paid_by": self.paid_by,
            "date": self.date,
            "split_with": self.split_with
        }
    
    @classmethod
    def from_dict(cls, data):
        """Create expense from dictionary"""
        return cls(
            description=data["description"],
            amount=data["amount"],
            currency=data["currency"],
            category=data["category"],
            paid_by=data["paid_by"],
            date=data.get("date"),
            expense_id=data.get("id"),
            split_with=data.get("split_with", [])
        )
    
    def __repr__(self):
        return f"Expense('{self.description}', {self.amount} {self.currency}, {self.category})"
