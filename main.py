"""
Trip Finance Tracker - Main Application
"""

import sys
import json
from datetime import datetime
from models.trip import Trip
from models.expense import Expense
from models.traveler import Traveler
from services.expense_service import ExpenseService
from services.report_service import ReportService
from utils.currency_converter import CurrencyConverter


class TripFinanceTracker:
    def __init__(self):
        self.expense_service = ExpenseService()
        self.report_service = ReportService()
        self.current_trip = None
    
    def display_menu(self):
        """Display the main menu"""
        print("\n" + "="*50)
        print("TRIP FINANCE TRACKER")
        print("="*50)
        print("1. Create New Trip")
        print("2. Load Existing Trip")
        print("3. Add Expense")
        print("4. View All Expenses")
        print("5. Add Traveler")
        print("6. View Trip Summary")
        print("7. Generate Report")
        print("8. Export Data")
        print("9. Exit")
        print("="*50)
    
    def create_trip(self):
        """Create a new trip"""
        print("\n--- Create New Trip ---")
        name = input("Trip name: ")
        destination = input("Destination: ")
        start_date = input("Start date (YYYY-MM-DD): ")
        end_date = input("End date (YYYY-MM-DD): ")
        currency = input("Default currency (e.g., USD, EUR): ").upper()
        
        self.current_trip = Trip(name, destination, start_date, end_date, currency)
        self.expense_service.set_trip(self.current_trip)
        print(f"\n✓ Trip '{name}' created successfully!")
    
    def add_expense(self):
        """Add a new expense"""
        if not self.current_trip:
            print("\n⚠ Please create or load a trip first!")
            return
        
        print("\n--- Add Expense ---")
        description = input("Description: ")
        amount = float(input("Amount: "))
        currency = input(f"Currency [{self.current_trip.currency}]: ").upper() or self.current_trip.currency
        category = input("Category (food/transport/accommodation/activities/other): ")
        paid_by = input("Paid by (traveler name): ")
        
        expense = Expense(description, amount, currency, category, paid_by)
        self.expense_service.add_expense(expense)
        print(f"\n✓ Expense added successfully!")
    
    def view_expenses(self):
        """View all expenses"""
        if not self.current_trip:
            print("\n⚠ Please create or load a trip first!")
            return
        
        expenses = self.expense_service.get_all_expenses()
        if not expenses:
            print("\nNo expenses recorded yet.")
            return
        
        print("\n--- All Expenses ---")
        for idx, exp in enumerate(expenses, 1):
            print(f"{idx}. {exp.description} - {exp.amount} {exp.currency} ({exp.category}) - Paid by: {exp.paid_by}")
    
    def add_traveler(self):
        """Add a traveler to the trip"""
        if not self.current_trip:
            print("\n⚠ Please create or load a trip first!")
            return
        
        print("\n--- Add Traveler ---")
        name = input("Traveler name: ")
        email = input("Email (optional): ")
        
        traveler = Traveler(name, email)
        self.current_trip.add_traveler(traveler)
        print(f"\n✓ Traveler '{name}' added!")
    
    def view_summary(self):
        """View trip summary"""
        if not self.current_trip:
            print("\n⚠ Please create or load a trip first!")
            return
        
        summary = self.report_service.generate_summary(self.current_trip, self.expense_service)
        print("\n" + "="*50)
        print(f"TRIP SUMMARY: {self.current_trip.name}")
        print("="*50)
        print(summary)
    
    def generate_report(self):
        """Generate detailed report"""
        if not self.current_trip:
            print("\n⚠ Please create or load a trip first!")
            return
        
        print("\n--- Generate Report ---")
        print("1. Category Breakdown")
        print("2. Per Person Summary")
        print("3. Daily Expenses")
        choice = input("Select report type: ")
        
        if choice == "1":
            report = self.report_service.category_breakdown(self.expense_service)
            print(report)
        elif choice == "2":
            report = self.report_service.per_person_summary(self.expense_service)
            print(report)
        elif choice == "3":
            report = self.report_service.daily_expenses(self.expense_service)
            print(report)
    
    def export_data(self):
        """Export trip data"""
        if not self.current_trip:
            print("\n⚠ Please create or load a trip first!")
            return
        
        print("\n--- Export Data ---")
        filename = input("Filename (without extension): ")
        format_type = input("Format (json/csv): ").lower()
        
        if format_type == "json":
            self.expense_service.export_to_json(f"reports/{filename}.json")
        elif format_type == "csv":
            self.expense_service.export_to_csv(f"reports/{filename}.csv")
        
        print(f"\n✓ Data exported to reports/{filename}.{format_type}")
    
    def run(self):
        """Main application loop"""
        print("Welcome to Trip Finance Tracker!")
        
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-9): ")
            
            if choice == "1":
                self.create_trip()
            elif choice == "2":
                print("\n⚠ Load trip feature coming soon!")
            elif choice == "3":
                self.add_expense()
            elif choice == "4":
                self.view_expenses()
            elif choice == "5":
                self.add_traveler()
            elif choice == "6":
                self.view_summary()
            elif choice == "7":
                self.generate_report()
            elif choice == "8":
                self.export_data()
            elif choice == "9":
                print("\nThank you for using Trip Finance Tracker!")
                sys.exit(0)
            else:
                print("\n⚠ Invalid choice. Please try again.")


if __name__ == "__main__":
    app = TripFinanceTracker()
    app.run()
