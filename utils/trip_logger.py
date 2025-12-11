"""
Trip Logger - Log all trip activities and changes
"""

import json
import os
from datetime import datetime


class TripLogger:
    def __init__(self, log_dir='logs'):
        self.log_dir = log_dir
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        self.log_file = os.path.join(log_dir, 'trip_logger.json')
        self.activity_log = self._load_logs()
    
    def _load_logs(self):
        """Load existing logs"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_logs(self):
        """Save logs to file"""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.activity_log, f, indent=2)
        except Exception as e:
            print(f"Error saving logs: {e}")
    
    def log_trip_created(self, trip_data):
        """Log trip creation"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'trip_created',
            'trip_id': trip_data.get('id'),
            'trip_name': trip_data.get('name'),
            'destination': trip_data.get('destination'),
            'currency': trip_data.get('currency'),
            'start_date': trip_data.get('start_date'),
            'end_date': trip_data.get('end_date')
        }
        self.activity_log.append(entry)
        self._save_logs()
        self._create_trip_specific_log(trip_data['id'], 'created', trip_data)
    
    def log_trip_loaded(self, trip_id, trip_name):
        """Log trip loaded"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'trip_loaded',
            'trip_id': trip_id,
            'trip_name': trip_name
        }
        self.activity_log.append(entry)
        self._save_logs()
    
    def log_expense_added(self, trip_id, expense_data):
        """Log expense addition"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'expense_added',
            'trip_id': trip_id,
            'expense': {
                'description': expense_data.get('description'),
                'amount': expense_data.get('amount'),
                'currency': expense_data.get('currency'),
                'category': expense_data.get('category'),
                'paid_by': expense_data.get('paid_by')
            }
        }
        self.activity_log.append(entry)
        self._save_logs()
        self._create_trip_specific_log(trip_id, 'expense_added', expense_data)
    
    def log_expense_deleted(self, trip_id, expense_id):
        """Log expense deletion"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'expense_deleted',
            'trip_id': trip_id,
            'expense_id': expense_id
        }
        self.activity_log.append(entry)
        self._save_logs()
        self._create_trip_specific_log(trip_id, 'expense_deleted', {'expense_id': expense_id})
    
    def log_traveler_added(self, trip_id, traveler_data):
        """Log traveler addition"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'traveler_added',
            'trip_id': trip_id,
            'traveler': {
                'name': traveler_data.get('name'),
                'email': traveler_data.get('email')
            }
        }
        self.activity_log.append(entry)
        self._save_logs()
        self._create_trip_specific_log(trip_id, 'traveler_added', traveler_data)
    
    def log_trip_saved(self, trip_id, trip_name):
        """Log trip save"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'trip_saved',
            'trip_id': trip_id,
            'trip_name': trip_name
        }
        self.activity_log.append(entry)
        self._save_logs()
    
    def log_trip_exported(self, trip_id, export_format):
        """Log trip export"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'action': 'trip_exported',
            'trip_id': trip_id,
            'format': export_format
        }
        self.activity_log.append(entry)
        self._save_logs()
        self._create_trip_specific_log(trip_id, 'exported', {'format': export_format})
    
    def _create_trip_specific_log(self, trip_id, action, data):
        """Create trip-specific log file"""
        trip_log_file = os.path.join(self.log_dir, f'trip_{trip_id}.json')
        
        # Load existing trip logs
        trip_logs = []
        if os.path.exists(trip_log_file):
            try:
                with open(trip_log_file, 'r') as f:
                    trip_logs = json.load(f)
            except:
                trip_logs = []
        
        # Add new entry
        trip_logs.append({
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'data': data
        })
        
        # Save trip logs
        try:
            with open(trip_log_file, 'w') as f:
                json.dump(trip_logs, f, indent=2)
        except Exception as e:
            print(f"Error saving trip-specific log: {e}")
    
    def get_trip_history(self, trip_id):
        """Get all logs for a specific trip"""
        trip_log_file = os.path.join(self.log_dir, f'trip_{trip_id}.json')
        if os.path.exists(trip_log_file):
            try:
                with open(trip_log_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def get_all_trips_summary(self):
        """Get summary of all trips"""
        trips_summary = {}
        for entry in self.activity_log:
            if entry['action'] == 'trip_created':
                trip_id = entry['trip_id']
                if trip_id not in trips_summary:
                    trips_summary[trip_id] = {
                        'trip_name': entry['trip_name'],
                        'destination': entry['destination'],
                        'created': entry['timestamp'],
                        'expense_count': 0,
                        'traveler_count': 0,
                        'last_activity': entry['timestamp']
                    }
            elif entry['action'] == 'expense_added':
                trip_id = entry.get('trip_id')
                if trip_id in trips_summary:
                    trips_summary[trip_id]['expense_count'] += 1
                    trips_summary[trip_id]['last_activity'] = entry['timestamp']
            elif entry['action'] == 'traveler_added':
                trip_id = entry.get('trip_id')
                if trip_id in trips_summary:
                    trips_summary[trip_id]['traveler_count'] += 1
                    trips_summary[trip_id]['last_activity'] = entry['timestamp']
        
        return trips_summary
    
    def get_recent_activities(self, limit=20):
        """Get recent activities across all trips"""
        return self.activity_log[-limit:][::-1]  # Return most recent first
