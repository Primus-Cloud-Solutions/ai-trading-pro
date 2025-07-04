"""
Shared Database Instance for AI Trading SaaS Platform
"""

from flask_sqlalchemy import SQLAlchemy

# Create single database instance
db = SQLAlchemy()

def init_db(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    return db

