"""
Add action_data column to notifications table
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
        # Add action_data column to notifications table using text()
        from sqlalchemy import text
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE notifications ADD COLUMN action_data TEXT AFTER link_url"))
            conn.commit()
        print("✅ Successfully added action_data column to notifications table")
    except Exception as e:
        if 'Duplicate column name' in str(e):
            print("ℹ️  Column 'action_data' already exists")
        else:
            print(f"❌ Error: {e}")
            raise
