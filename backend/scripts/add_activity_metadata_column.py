"""
Add activity_metadata column to activity_log table
"""
from models import db
from app import create_app

app = create_app()

with app.app_context():
    try:
        # Check if column exists
        result = db.session.execute(db.text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE()
            AND TABLE_NAME = 'activity_log' 
            AND COLUMN_NAME = 'activity_metadata'
        """))
        
        if result.fetchone():
            print("✅ Column 'activity_metadata' already exists")
        else:
            print("Adding 'activity_metadata' column to activity_log table...")
            
            db.session.execute(db.text("""
                ALTER TABLE activity_log 
                ADD COLUMN activity_metadata JSON AFTER entity_id
            """))
            
            db.session.commit()
            print("✅ Column 'activity_metadata' added successfully")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.session.rollback()
