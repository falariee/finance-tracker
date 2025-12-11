"""
Report Service - Generate reports and summaries
"""

from collections import defaultdict
from datetime import datetime
from tabulate import tabulate


class ReportService:
    def generate_summary(self, trip, expense_service):
        """Generate a trip summary"""
        total = expense_service.get_total_expenses()
        num_expenses = len(expense_service.get_all_expenses())
        
        summary = f"""
Trip: {trip.name}
Destination: {trip.destination}
Dates: {trip.start_date} to {trip.end_date}
Travelers: {len(trip.travelers)}

Total Expenses: {total:.2f} {trip.currency}
Number of Expenses: {num_expenses}
Average per Expense: {total/num_expenses:.2f} {trip.currency if num_expenses > 0 else 0}
"""
        return summary
    
    def category_breakdown(self, expense_service):
        """Generate category breakdown report"""
        category_totals = expense_service.get_category_totals()
        total = expense_service.get_total_expenses()
        
        if not category_totals:
            return "\nNo expenses to report."
        
        # Prepare table data
        table_data = []
        for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total * 100) if total > 0 else 0
            table_data.append([category.capitalize(), f"{amount:.2f}", f"{percentage:.1f}%"])
        
        table_data.append(["TOTAL", f"{total:.2f}", "100%"])
        
        return "\n" + tabulate(
            table_data,
            headers=["Category", "Amount", "Percentage"],
            tablefmt="grid"
        )
    
    def per_person_summary(self, expense_service):
        """Generate per-person summary report"""
        person_totals = expense_service.get_person_totals()
        total = expense_service.get_total_expenses()
        
        if not person_totals:
            return "\nNo expenses to report."
        
        # Prepare table data
        table_data = []
        for person, amount in sorted(person_totals.items(), key=lambda x: x[1], reverse=True):
            percentage = (amount / total * 100) if total > 0 else 0
            num_expenses = len(expense_service.get_expenses_by_person(person))
            table_data.append([person, f"{amount:.2f}", num_expenses, f"{percentage:.1f}%"])
        
        return "\n" + tabulate(
            table_data,
            headers=["Person", "Total Paid", "# Expenses", "Percentage"],
            tablefmt="grid"
        )
    
    def daily_expenses(self, expense_service):
        """Generate daily expenses report"""
        expenses = expense_service.get_all_expenses()
        
        if not expenses:
            return "\nNo expenses to report."
        
        # Group by date
        daily = defaultdict(list)
        for exp in expenses:
            date = exp.date.split()[0]  # Get just the date part
            daily[date].append(exp)
        
        # Prepare table data
        table_data = []
        for date in sorted(daily.keys()):
            day_expenses = daily[date]
            day_total = sum(exp.amount for exp in day_expenses)
            table_data.append([date, len(day_expenses), f"{day_total:.2f}"])
        
        return "\n" + tabulate(
            table_data,
            headers=["Date", "# Expenses", "Total"],
            tablefmt="grid"
        )
    
    def split_calculator(self, expense_service, trip):
        """Calculate how to split expenses among travelers"""
        if not trip.travelers:
            return "\nNo travelers to split expenses with."
        
        person_totals = expense_service.get_person_totals()
        total = expense_service.get_total_expenses()
        num_people = len(trip.travelers)
        
        if num_people == 0:
            return "\nNo travelers to split expenses with."
        
        per_person = total / num_people
        
        # Calculate balances
        balances = {}
        for traveler in trip.travelers:
            paid = person_totals.get(traveler.name, 0)
            balances[traveler.name] = paid - per_person
        
        # Prepare table data
        table_data = []
        for person, balance in sorted(balances.items(), key=lambda x: x[1], reverse=True):
            if balance > 0:
                status = f"Owed {balance:.2f}"
            elif balance < 0:
                status = f"Owes {abs(balance):.2f}"
            else:
                status = "Settled"
            
            table_data.append([person, f"{person_totals.get(person, 0):.2f}", f"{per_person:.2f}", status])
        
        return "\n" + tabulate(
            table_data,
            headers=["Person", "Paid", "Fair Share", "Balance"],
            tablefmt="grid"
        )
