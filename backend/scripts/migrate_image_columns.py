"""
Migration script to increase image column sizes
Run this to update the database schema for base64 image storage
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pymysql
from config import Config

def run_migration():
    connection = None
    try:
        # Parse database URL from config
        db_uri = Config.SQLALCHEMY_DATABASE_URI
        # Format: mysql+pymysql://user:password@host/database
        # Extract parts
        if 'mysql+pymysql://' in db_uri:
            db_uri = db_uri.replace('mysql+pymysql://', '')
        
        # Split user:pass@host/db
        if '@' in db_uri:
            creds, rest = db_uri.split('@')
            if ':' in creds:
                user, password = creds.split(':', 1)
            else:
                user = creds
                password = ''
            
            if '/' in rest:
                host, database = rest.split('/')
            else:
                host = rest
                database = 'cineforge_ai'
        else:
            user = 'root'
            password = ''
            host = 'localhost'
            database = 'cineforge_ai'
        
        print(f"📊 Connecting to {host}/{database}...")
        
        # Connect to database
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        
        print("📊 Connected to database")
        
        with connection.cursor() as cursor:
            # Alter users table
            print("🔧 Updating users.profile_pic_url to LONGTEXT...")
            cursor.execute("""
                ALTER TABLE users 
                MODIFY COLUMN profile_pic_url LONGTEXT
            """)
            print("✅ users.profile_pic_url updated")
            
            # Alter projects table
            print("🔧 Updating projects.thumbnail_url to LONGTEXT...")
            cursor.execute("""
                ALTER TABLE projects 
                MODIFY COLUMN thumbnail_url LONGTEXT
            """)
            print("✅ projects.thumbnail_url updated")
            
            # Commit changes
            connection.commit()
            
            # Verify changes
            print("\n📋 Verifying changes:")
            cursor.execute("""
                SELECT 
                    'users' as table_name,
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    CHARACTER_MAXIMUM_LENGTH 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = 'users' 
                AND COLUMN_NAME = 'profile_pic_url'
                UNION ALL
                SELECT 
                    'projects' as table_name,
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    CHARACTER_MAXIMUM_LENGTH 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_SCHEMA = %s
                AND TABLE_NAME = 'projects' 
                AND COLUMN_NAME = 'thumbnail_url'
            """, (database, database))
            
            results = cursor.fetchall()
            for row in results:
                print(f"  ✓ {row['table_name']}.{row['COLUMN_NAME']}: {row['DATA_TYPE']}")
            
            print("\n✅ Migration completed successfully!")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if connection:
            connection.close()
            print("🔌 Database connection closed")

if __name__ == '__main__':
    run_migration()
