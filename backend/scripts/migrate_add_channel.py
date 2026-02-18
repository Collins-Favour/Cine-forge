#!/usr/bin/env python3
"""
Migration 003: Add channel column to cspace_messages table
This enables channel-based messaging in CSpace (general, production, creative, budget, etc.)
"""

import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from models import db
from sqlalchemy import text

def run_migration():
    """Execute the channel column migration"""
    app = create_app('development')
    
    with app.app_context():
        try:
            print("🔄 Starting migration 003: Adding channel column to cspace_messages...")
            
            # Check if column already exists
            check_query = text("""
                SELECT COUNT(*) as count
                FROM information_schema.COLUMNS 
                WHERE TABLE_SCHEMA = 'cineforge_ai' 
                AND TABLE_NAME = 'cspace_messages' 
                AND COLUMN_NAME = 'channel'
            """)
            result = db.session.execute(check_query).fetchone()
            
            if result[0] > 0:
                print("⚠️  Channel column already exists. Skipping migration.")
                return
            
            # Add channel column
            print("   → Adding 'channel' column to cspace_messages table...")
            alter_query = text("""
                ALTER TABLE cspace_messages 
                ADD COLUMN channel VARCHAR(50) DEFAULT 'general' NOT NULL 
                COMMENT 'Channel name (general, production, creative, budget, etc.)'
                AFTER message_type
            """)
            db.session.execute(alter_query)
            
            # Add index for performance
            print("   → Creating index on 'channel' column...")
            index_query = text("""
                CREATE INDEX idx_channel ON cspace_messages(channel)
            """)
            db.session.execute(index_query)
            
            # Update existing messages
            print("   → Updating existing messages to 'general' channel...")
            update_query = text("""
                UPDATE cspace_messages 
                SET channel = 'general' 
                WHERE channel IS NULL OR channel = ''
            """)
            db.session.execute(update_query)
            
            db.session.commit()
            
            print("✅ Migration 003 completed successfully!")
            print("   📊 Channel column added to cspace_messages")
            print("   📊 Index created for better query performance")
            print("   📊 Existing messages updated to 'general' channel")
            print("\n🎉 CSpace messages can now be organized by channels!")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {str(e)}")
            raise

if __name__ == '__main__':
    run_migration()
