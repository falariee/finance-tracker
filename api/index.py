from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import sys
import os

# Add parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Vercel environment flag
os.environ['VERCEL'] = '1'

# Now import the app
from app import app
