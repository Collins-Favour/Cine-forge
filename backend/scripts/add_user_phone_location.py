"""
Add phone and location columns to users table
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from models import db
from config import Config

# Create minimal Flask app
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    try:
        # Add phone and location columns to users table using text()
        from sqlalchemy import text
        with db.engine.connect() as conn:
            # Check if columns exist first
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'phone'"))
            phone_exists = result.fetchone() is not None
            
            result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'location'"))
            location_exists = result.fetchone() is not None
            
            if not phone_exists:
                conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(20) AFTER bio"))
                print("✅ Successfully added phone column to users table")
            else:
                print("ℹ️  Column 'phone' already exists")
            
            if not location_exists:
                conn.execute(text("ALTER TABLE users ADD COLUMN location VARCHAR(255) AFTER phone"))
                print("✅ Successfully added location column to users table")
            else:
                print("ℹ️  Column 'location' already exists")
                
            conn.commit()
    except Exception as e:
        print(f"❌ Error: {e}")
        raise
