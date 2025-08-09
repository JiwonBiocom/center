"""
Vercel Serverless Function handler for FastAPI backend
"""
import os
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Import FastAPI app
from main import app

# Vercel expects a function named 'handler'
handler = app