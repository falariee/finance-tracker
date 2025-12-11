"""
Vercel Serverless Function Entry Point
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set environment variable to indicate Vercel deployment
os.environ['VERCEL'] = '1'

from app import app as application

# Export for Vercel
app = application
