import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

# Set environment variable
os.environ['VERCEL'] = '1'

# Import Flask app
from app import app

# Vercel serverless function handler
def handler(request, response):
    return app(request, response)
