"""
Database utilities for persistent storage using Supabase
"""

import os
import json
from typing import Optional, List, Dict
import requests


class Database:
    """Database manager for trip data storage"""
    
    def __init__(self):
        self.supabase_url = os.environ.get('SUPABASE_URL')
        self.supabase_key = os.environ.get('SUPABASE_KEY')
        
        if not self.supabase_url or not self.supabase_key:
            print("Warning: Supabase credentials not configured. Using fallback mode.")
            self.enabled = False
        else:
            self.enabled = True
            self.headers = {
                'apikey': self.supabase_key,
                'Authorization': f'Bearer {self.supabase_key}',
                'Content-Type': 'application/json',
                'Prefer': 'return=representation'
            }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make a request to Supabase API"""
        if not self.enabled:
            return None
        
        try:
            url = f"{self.supabase_url}/rest/v1/{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, headers=self.headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=self.headers, json=data, params=params)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                return None
            
            if response.status_code in [200, 201]:
                result = response.json()
                return result if isinstance(result, list) else result
            else:
                print(f"Database error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Database request failed: {str(e)}")
            return None
    
    def save_trip(self, trip_data: Dict, expenses: List[Dict]) -> bool:
        """Save or update a trip with its expenses"""
        if not self.enabled:
            return False
        
        trip_id = trip_data['id']
        
        # Check if trip exists
        existing = self._make_request('GET', 'trips', params={'id': f'eq.{trip_id}'})
        
        data_to_save = {
            'id': trip_id,
            'name': trip_data['name'],
            'destination': trip_data['destination'],
            'start_date': trip_data['start_date'],
            'end_date': trip_data['end_date'],
            'currency': trip_data['currency'],
            'travelers': json.dumps(trip_data.get('travelers', [])),
            'expenses': json.dumps(expenses),
            'created_at': trip_data.get('created_at'),
            'updated_at': trip_data.get('updated_at')
        }
        
        if existing and len(existing) > 0:
            # Update existing trip
            result = self._make_request('PATCH', 'trips', data=data_to_save, params={'id': f'eq.{trip_id}'})
        else:
            # Insert new trip
            result = self._make_request('POST', 'trips', data=data_to_save)
        
        return result is not None
    
    def load_trip(self, trip_id: str) -> Optional[Dict]:
        """Load a trip by ID"""
        if not self.enabled:
            return None
        
        result = self._make_request('GET', 'trips', params={'id': f'eq.{trip_id}'})
        
        if result and len(result) > 0:
            trip = result[0]
            # Parse JSON fields
            trip['travelers'] = json.loads(trip.get('travelers', '[]'))
            trip['expenses'] = json.loads(trip.get('expenses', '[]'))
            return trip
        
        return None
    
    def list_trips(self) -> List[Dict]:
        """List all trips"""
        if not self.enabled:
            return []
        
        result = self._make_request('GET', 'trips', params={'order': 'created_at.desc'})
        
        if result:
            # Parse JSON fields for each trip
            for trip in result:
                trip['travelers'] = json.loads(trip.get('travelers', '[]'))
                # Don't load full expenses list for listing view
                expense_count = len(json.loads(trip.get('expenses', '[]')))
                trip['expense_count'] = expense_count
                # Remove expenses to reduce payload
                trip.pop('expenses', None)
            return result
        
        return []
    
    def delete_trip(self, trip_id: str) -> bool:
        """Delete a trip"""
        if not self.enabled:
            return False
        
        result = self._make_request('DELETE', 'trips', params={'id': f'eq.{trip_id}'})
        return result is not None
    
    def trip_exists(self, trip_id: str) -> bool:
        """Check if a trip exists"""
        if not self.enabled:
            return False
        
        result = self._make_request('GET', 'trips', params={'id': f'eq.{trip_id}', 'select': 'id'})
        return result and len(result) > 0


# Singleton instance
_db_instance = None

def get_database() -> Database:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database()
    return _db_instance
