"""
Currency Converter Utility
"""

import requests
from datetime import datetime, timedelta


class CurrencyConverter:
    def __init__(self):
        self.rates = {}
        self.last_update = None
        self.base_currency = "USD"
    
    def fetch_rates(self):
        """Fetch latest exchange rates from API"""
        try:
            # Using a free API for exchange rates
            url = f"https://api.exchangerate-api.com/v4/latest/{self.base_currency}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                self.rates = data.get("rates", {})
                self.last_update = datetime.now()
                return True
            else:
                print(f"Failed to fetch rates: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error fetching exchange rates: {e}")
            return False
    
    def should_update_rates(self):
        """Check if rates need to be updated (older than 1 day)"""
        if not self.last_update:
            return True
        return datetime.now() - self.last_update > timedelta(days=1)
    
    def convert(self, amount, from_currency, to_currency):
        """Convert amount from one currency to another"""
        if from_currency == to_currency:
            return amount
        
        # Update rates if needed
        if self.should_update_rates():
            self.fetch_rates()
        
        if not self.rates:
            print("Warning: No exchange rates available. Using 1:1 conversion.")
            return amount
        
        try:
            # Convert from source currency to base currency (USD)
            if from_currency != self.base_currency:
                amount_in_base = amount / self.rates.get(from_currency, 1)
            else:
                amount_in_base = amount
            
            # Convert from base currency to target currency
            if to_currency != self.base_currency:
                result = amount_in_base * self.rates.get(to_currency, 1)
            else:
                result = amount_in_base
            
            return round(result, 2)
        except Exception as e:
            print(f"Error converting currency: {e}")
            return amount
    
    def get_rate(self, from_currency, to_currency):
        """Get exchange rate between two currencies"""
        if from_currency == to_currency:
            return 1.0
        
        if self.should_update_rates():
            self.fetch_rates()
        
        if not self.rates:
            return 1.0
        
        try:
            rate_from = self.rates.get(from_currency, 1)
            rate_to = self.rates.get(to_currency, 1)
            return round(rate_to / rate_from, 4)
        except Exception as e:
            print(f"Error getting exchange rate: {e}")
            return 1.0
