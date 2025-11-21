"""
Temporary migration script to add channel column to cspace_messages table
"""
from app import create_app
from models import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Add channel column
        db.session.execute(text(
            "ALTER TABLE cspace_messages ADD COLUMN channel VARCHAR(50) DEFAULT 'general' AFTER parent_message_id"
        ))
        db.session.commit()
        print("✅ Added channel column to cspace_messages")
        
        # Add index
        db.session.execute(text(
            "ALTER TABLE cspace_messages ADD INDEX idx_channel (channel)"
        ))
        db.session.commit()
        print("✅ Added index on channel column")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error: {e}")
        # Check if column already exists
        if "Duplicate column name" in str(e):
            print("ℹ️  Column already exists, skipping")
        else:
            raise
