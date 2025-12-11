"""
Flask Web Application for Trip Finance Tracker
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
import os
from datetime import datetime
from models.trip import Trip
from models.expense import Expense
from models.traveler import Traveler
from services.expense_service import ExpenseService
from services.report_service import ReportService
from utils.currency_converter import CurrencyConverter
from utils.trip_logger import TripLogger
from utils.database import get_database

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
CORS(app)

# Disable Flask session for serverless
if os.environ.get('VERCEL'):
    app.config['SESSION_TYPE'] = 'filesystem'

# Global instances
expense_service = ExpenseService()
report_service = ReportService()
currency_converter = CurrencyConverter()
trip_logger = TripLogger()
db = get_database()

# Data directory - use /tmp for Vercel serverless
DATA_DIR = '/tmp/data' if os.environ.get('VERCEL') else 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get application and database status"""
    return jsonify({
        'success': True,
        'database_enabled': db.enabled,
        'database_type': 'Supabase' if db.enabled else 'None (fallback mode)',
        'message': 'Database connected' if db.enabled else 'Running in fallback mode - data will not persist across sessions'
    })


@app.route('/api/trip', methods=['POST'])
def create_trip():
    """Create a new trip"""
    try:
        data = request.json
        trip = Trip(
            name=data['name'],
            destination=data['destination'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            currency=data['currency']
        )
        
        # Clear old trip data for fresh start
        expense_service.expenses = []
        expense_service.set_trip(trip)
        session['current_trip_id'] = trip.id
        
        # Log trip creation
        trip_logger.log_trip_created(trip.to_dict())
        
        return jsonify({
            'success': True,
            'trip': trip.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/trip', methods=['GET'])
def get_trip():
    """Get current trip"""
    if expense_service.trip:
        return jsonify({
            'success': True,
            'trip': expense_service.trip.to_dict()
        })
    return jsonify({'success': False, 'error': 'No active trip'}), 404


@app.route('/api/travelers', methods=['POST'])
def add_traveler():
    """Add a traveler to the trip"""
    try:
        # For serverless, we need to check if trip exists in memory
        if not expense_service.trip:
            return jsonify({'success': False, 'error': 'No active trip. Please create a trip first.'}), 400
        
        data = request.json
        traveler = Traveler(
            name=data['name'],
            email=data.get('email', '')
        )
        
        expense_service.trip.add_traveler(traveler)
        
        # Auto-save to database
        trip_data = expense_service.trip.to_dict()
        expenses_data = [exp.to_dict() for exp in expense_service.expenses]
        db.save_trip(trip_data, expenses_data)
        
        # Log traveler addition
        trip_logger.log_traveler_added(expense_service.trip.id, traveler.to_dict())
        
        return jsonify({
            'success': True,
            'traveler': traveler.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/travelers', methods=['GET'])
def get_travelers():
    """Get all travelers"""
    if not expense_service.trip:
        return jsonify({'success': False, 'error': 'No active trip'}), 400
    
    return jsonify({
        'success': True,
        'travelers': [t.to_dict() for t in expense_service.trip.travelers]
    })


@app.route('/api/expenses', methods=['POST'])
def add_expense():
    """Add a new expense"""
    try:
        if not expense_service.trip:
            return jsonify({'success': False, 'error': 'No active trip'}), 400
        
        data = request.json
        expense = Expense(
            description=data['description'],
            amount=float(data['amount']),
            currency=data.get('currency', expense_service.trip.currency),
            category=data['category'],
            paid_by=data['paid_by']
        )
        
        expense_service.add_expense(expense)
        
        # Auto-save to database
        trip_data = expense_service.trip.to_dict()
        expenses_data = [exp.to_dict() for exp in expense_service.expenses]
        db.save_trip(trip_data, expenses_data)
        
        # Log expense addition
        trip_logger.log_expense_added(expense_service.trip.id, expense.to_dict())
        
        return jsonify({
            'success': True,
            'expense': expense.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    """Get all expenses"""
    expenses = expense_service.get_all_expenses()
    return jsonify({
        'success': True,
        'expenses': [exp.to_dict() for exp in expenses]
    })


@app.route('/api/expenses/<expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    """Delete an expense"""
    try:
        if expense_service.trip:
            trip_logger.log_expense_deleted(expense_service.trip.id, expense_id)
        
        expense_service.expenses = [
            exp for exp in expense_service.expenses if exp.id != expense_id
        ]
        
        # Auto-save to database
        if expense_service.trip:
            trip_data = expense_service.trip.to_dict()
            expenses_data = [exp.to_dict() for exp in expense_service.expenses]
            db.save_trip(trip_data, expenses_data)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/reports/summary', methods=['GET'])
def get_summary():
    """Get trip summary"""
    if not expense_service.trip:
        return jsonify({'success': False, 'error': 'No active trip'}), 400
    
    total = expense_service.get_total_expenses()
    num_expenses = len(expense_service.get_all_expenses())
    
    # Calculate total in original currencies
    currency_totals = {}
    for expense in expense_service.get_all_expenses():
        if expense.currency not in currency_totals:
            currency_totals[expense.currency] = 0
        currency_totals[expense.currency] += expense.amount
    
    return jsonify({
        'success': True,
        'summary': {
            'total_expenses': total,
            'num_expenses': num_expenses,
            'average_expense': total / num_expenses if num_expenses > 0 else 0,
            'currency': expense_service.trip.currency,
            'currency_breakdown': currency_totals
        }
    })


@app.route('/api/reports/categories', methods=['GET'])
def get_category_report():
    """Get category breakdown"""
    category_totals = expense_service.get_category_totals()
    total = expense_service.get_total_expenses()
    
    # Get category totals by original currency
    category_currency_breakdown = {}
    for expense in expense_service.get_all_expenses():
        cat = expense.category
        curr = expense.currency
        if cat not in category_currency_breakdown:
            category_currency_breakdown[cat] = {}
        if curr not in category_currency_breakdown[cat]:
            category_currency_breakdown[cat][curr] = 0
        category_currency_breakdown[cat][curr] += expense.amount
    
    categories = []
    for category, amount in category_totals.items():
        percentage = (amount / total * 100) if total > 0 else 0
        categories.append({
            'category': category,
            'amount': amount,
            'percentage': round(percentage, 1),
            'currency_breakdown': category_currency_breakdown.get(category, {})
        })
    
    return jsonify({
        'success': True,
        'categories': sorted(categories, key=lambda x: x['amount'], reverse=True)
    })


@app.route('/api/reports/people', methods=['GET'])
def get_people_report():
    """Get per-person summary"""
    person_totals = expense_service.get_person_totals()
    total = expense_service.get_total_expenses()
    
    people = []
    for person, amount in person_totals.items():
        percentage = (amount / total * 100) if total > 0 else 0
        num_expenses = len(expense_service.get_expenses_by_person(person))
        people.append({
            'person': person,
            'amount': amount,
            'num_expenses': num_expenses,
            'percentage': round(percentage, 1)
        })
    
    return jsonify({
        'success': True,
        'people': sorted(people, key=lambda x: x['amount'], reverse=True)
    })


@app.route('/api/reports/split', methods=['GET'])
def get_split_report():
    """Get expense split calculation"""
    if not expense_service.trip:
        return jsonify({'success': False, 'error': 'No active trip'}), 400
    
    if not expense_service.trip.travelers:
        return jsonify({'success': False, 'error': 'No travelers to split expenses'}), 400
    
    person_totals = expense_service.get_person_totals()
    total = expense_service.get_total_expenses()
    num_people = len(expense_service.trip.travelers)
    per_person = total / num_people if num_people > 0 else 0
    
    balances = []
    for traveler in expense_service.trip.travelers:
        paid = person_totals.get(traveler.name, 0)
        balance = paid - per_person
        
        balances.append({
            'person': traveler.name,
            'paid': paid,
            'fair_share': per_person,
            'balance': balance,
            'status': 'owed' if balance > 0 else 'owes' if balance < 0 else 'settled'
        })
    
    return jsonify({
        'success': True,
        'balances': sorted(balances, key=lambda x: x['balance'], reverse=True)
    })


@app.route('/api/save', methods=['POST'])
def save_trip():
    """Save trip to database"""
    try:
        if not expense_service.trip:
            return jsonify({'success': False, 'error': 'No active trip'}), 400
        
        # Save to database
        trip_data = expense_service.trip.to_dict()
        expenses_data = [exp.to_dict() for exp in expense_service.expenses]
        
        success = db.save_trip(trip_data, expenses_data)
        
        if not success:
            # Fallback to file system
            filename = f"{DATA_DIR}/{expense_service.trip.id}.json"
            expense_service.export_to_json(filename)
        
        # Log trip save
        trip_logger.log_trip_saved(expense_service.trip.id, expense_service.trip.name)
        
        return jsonify({
            'success': True,
            'message': 'Trip saved successfully',
            'trip_id': expense_service.trip.id
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/load/<trip_id>', methods=['GET'])
def load_trip(trip_id):
    """Load trip from database"""
    try:
        # Try database first
        trip_data = db.load_trip(trip_id)
        
        if not trip_data:
            # Fallback to file system
            filename = f"{DATA_DIR}/{trip_id}.json"
            if not os.path.exists(filename):
                return jsonify({'success': False, 'error': 'Trip not found'}), 404
            
            expense_service.import_from_json(filename)
        else:
            # Load from database
            from models.trip import Trip
            from models.expense import Expense
            
            trip = Trip.from_dict(trip_data)
            expense_service.set_trip(trip)
            
            # Load expenses
            expense_service.expenses = []
            for exp_data in trip_data.get('expenses', []):
                expense = Expense.from_dict(exp_data)
                expense_service.expenses.append(expense)
        
        session['current_trip_id'] = trip_id
        
        # Log trip load
        trip_logger.log_trip_loaded(trip_id, expense_service.trip.name)
        
        return jsonify({
            'success': True,
            'trip': expense_service.trip.to_dict(),
            'expenses': [exp.to_dict() for exp in expense_service.expenses]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/trips', methods=['GET'])
def list_trips():
    """List all saved trips"""
    try:
        # Try database first
        trips = db.list_trips()
        
        if not trips:
            # Fallback to file system
            trips = []
            if os.path.exists(DATA_DIR):
                for filename in os.listdir(DATA_DIR):
                    if filename.endswith('.json') and filename != 'example.json':
                        filepath = os.path.join(DATA_DIR, filename)
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            if data.get('trip'):
                                trips.append(data['trip'])
        
        return jsonify({
            'success': True,
            'trips': trips
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/convert', methods=['POST'])
def convert_currency():
    """Convert currency"""
    try:
        data = request.json
        amount = float(data['amount'])
        from_currency = data['from_currency']
        to_currency = data['to_currency']
        
        converted_amount = currency_converter.convert(amount, from_currency, to_currency)
        rate = currency_converter.get_rate(from_currency, to_currency)
        
        return jsonify({
            'success': True,
            'converted_amount': converted_amount,
            'rate': rate,
            'from_currency': from_currency,
            'to_currency': to_currency
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/join/<trip_id>')
def join_trip(trip_id):
    """Join a trip via invite link"""
    # Just render the page with trip_id in URL
    # Frontend will handle loading the trip
    return render_template('index.html', trip_id=trip_id)


@app.route('/api/export/excel/<trip_id>')
def export_excel(trip_id):
    """Export trip expenses as Excel"""
    try:
        from flask import send_file
        # Create reports directory if it doesn't exist
        os.makedirs('reports', exist_ok=True)
        
        # Create a temporary expense service to export
        temp_service = ExpenseService()
        
        # Try to load from database first
        trip_data = db.load_trip(trip_id)
        
        if trip_data:
            # Load from database
            from models.trip import Trip
            from models.expense import Expense
            
            trip = Trip.from_dict(trip_data)
            temp_service.set_trip(trip)
            
            # Load expenses
            temp_service.expenses = []
            for exp_data in trip_data.get('expenses', []):
                expense = Expense.from_dict(exp_data)
                temp_service.expenses.append(expense)
        else:
            # Fallback to file system
            json_filename = f"{DATA_DIR}/{trip_id}.json"
            if not os.path.exists(json_filename):
                return jsonify({'success': False, 'error': 'Trip not found. Please save the trip first.'}), 404
            
            temp_service.import_from_json(json_filename)
        
        excel_filename = f"reports/{trip_id}_expenses.xlsx"
        temp_service.export_to_excel(excel_filename)
        
        # Log export
        trip_logger.log_trip_exported(trip_id, 'Excel')
        
        return send_file(
            excel_filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{trip_id}_expenses.xlsx'
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/export/summary/<trip_id>')
def export_summary(trip_id):
    """Get summary data for export"""
    try:
        # Try to load from database first
        trip_data = db.load_trip(trip_id)
        
        # Create a temporary expense service
        temp_service = ExpenseService()
        
        if trip_data:
            # Load from database
            from models.trip import Trip
            from models.expense import Expense
            
            trip = Trip.from_dict(trip_data)
            temp_service.set_trip(trip)
            
            # Load expenses
            temp_service.expenses = []
            for exp_data in trip_data.get('expenses', []):
                expense = Expense.from_dict(exp_data)
                temp_service.expenses.append(expense)
        else:
            # Fallback to file system
            filename = f"{DATA_DIR}/{trip_id}.json"
            if not os.path.exists(filename):
                return jsonify({'success': False, 'error': 'Trip not found. Please save the trip first.'}), 404
            
            temp_service.import_from_json(filename)
        
        # Get summary data
        total = temp_service.get_total_expenses()
        num_expenses = len(temp_service.get_all_expenses())
        category_totals = temp_service.get_category_totals()
        
        categories = []
        for category, amount in category_totals.items():
            percentage = (amount / total * 100) if total > 0 else 0
            categories.append({
                'category': category,
                'amount': amount,
                'percentage': round(percentage, 1)
            })
        
        return jsonify({
            'success': True,
            'summary': {
                'total_expenses': total,
                'num_expenses': num_expenses,
                'average_expense': total / num_expenses if num_expenses > 0 else 0
            },
            'expenses': [exp.to_dict() for exp in temp_service.expenses],
            'categories': sorted(categories, key=lambda x: x['amount'], reverse=True)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/logs/trips', methods=['GET'])
def get_all_trips_logs():
    """Get summary of all trips from logs"""
    try:
        trips_summary = trip_logger.get_all_trips_summary()
        return jsonify({
            'success': True,
            'trips': trips_summary
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/logs/trip/<trip_id>', methods=['GET'])
def get_trip_logs(trip_id):
    """Get logs for a specific trip"""
    try:
        history = trip_logger.get_trip_history(trip_id)
        return jsonify({
            'success': True,
            'history': history
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/logs/recent', methods=['GET'])
def get_recent_logs():
    """Get recent activities across all trips"""
    try:
        limit = request.args.get('limit', 20, type=int)
        activities = trip_logger.get_recent_activities(limit)
        return jsonify({
            'success': True,
            'activities': activities
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


# For Vercel serverless deployment
handler = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
