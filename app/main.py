"""
FastAPI wrapper for Flask AI Trading Application
This creates a FastAPI app that serves the Flask application for deployment compatibility
"""

import sys
import os
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware
from fastapi.staticfiles import StaticFiles

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

from main import create_app

flask_app = create_app()

app = FastAPI(
    title="AI Trading Pro",
    description="AI Trading SaaS Platform with automated trading, fund management, and social media integration",
    version="1.0.0"
)

app.mount("/", WSGIMiddleware(flask_app))
