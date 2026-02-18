"""
Migration script to increase image column sizes using Flask app context
Run this to update the database schema for base64 image storage
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db

def run_migration():
    app = create_app('development')
    with app.app_context():
        try:
            print("📊 Running migration to increase image column sizes...")
            
            # Execute raw SQL to modify columns
            print("🔧 Updating users.profile_pic_url to LONGTEXT...")
            db.session.execute(db.text("""
                ALTER TABLE users 
                MODIFY COLUMN profile_pic_url LONGTEXT
            """))
            print("✅ users.profile_pic_url updated")
            
            print("🔧 Updating projects.thumbnail_url to LONGTEXT...")
            db.session.execute(db.text("""
                ALTER TABLE projects 
                MODIFY COLUMN thumbnail_url LONGTEXT
            """))
            print("✅ projects.thumbnail_url updated")
            
            # Commit changes
            db.session.commit()
            print("\n✅ Migration completed successfully!")
            print("🎉 Images can now be stored as base64-encoded data in the database")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    run_migration()
