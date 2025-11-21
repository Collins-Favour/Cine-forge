"""
Database Initialization Script
Creates database and tables from schema.sql
"""
import pymysql
import os
from pathlib import Path

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update this if your MySQL has a password
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def init_database():
    """Initialize database from schema.sql"""
    print("=" * 60)
    print("CINEFORGE AI - Database Initialization")
    print("=" * 60)
    
    schema_path = Path(__file__).parent / 'database' / 'schema.sql'
    
    if not schema_path.exists():
        print(f"❌ Error: schema.sql not found at {schema_path}")
        return False
    
    try:
        # Connect to MySQL server (without database)
        print("\n📡 Connecting to MySQL server...")
        connection = pymysql.connect(**DB_CONFIG)
        
        with connection.cursor() as cursor:
            # Read schema file
            print("📄 Reading schema.sql...")
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Split into individual statements and execute
            print("🔨 Creating database and tables...")
            statements = [stmt.strip() for stmt in schema_sql.split(';') if stmt.strip()]
            
            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        cursor.execute(statement)
                        if 'CREATE DATABASE' in statement.upper():
                            print(f"  ✓ Database created")
                        elif 'CREATE TABLE' in statement.upper():
                            table_name = statement.split('CREATE TABLE')[1].split('(')[0].strip()
                            print(f"  ✓ Table created: {table_name}")
                    except pymysql.Error as e:
                        # Skip if already exists
                        if 'already exists' not in str(e):
                            print(f"  ⚠ Warning executing statement {i}: {e}")
            
            connection.commit()
            print("\n✅ Database initialized successfully!")
            print("\nDatabase: cineforge_ai")
            print("Tables created: users, user_sessions, projects, project_collaborators,")
            print("               script_versions, characters, scene_characters, scenes,")
            print("               visual_styles, storyboard_panels, checklist_items,")
            print("               budget_items, cspace_messages, message_reactions,")
            print("               ai_processing_logs, usage_analytics, notifications,")
            print("               project_exports, uploaded_files, system_settings")
            
        connection.close()
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

def verify_database():
    """Verify database was created successfully"""
    print("\n" + "=" * 60)
    print("Verifying Database Setup")
    print("=" * 60)
    
    try:
        # Connect to the new database
        config = DB_CONFIG.copy()
        config['database'] = 'cineforge_ai'
        connection = pymysql.connect(**config)
        
        with connection.cursor() as cursor:
            # Check tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                print(f"\n✓ Found {len(tables)} tables in cineforge_ai")
                
                # Check users table structure
                cursor.execute("DESCRIBE users")
                print("\n✓ Users table structure verified")
                
                return True
            else:
                print("\n❌ No tables found in database")
                return False
                
        connection.close()
        
    except pymysql.Error as e:
        print(f"\n❌ Verification failed: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    
    if success:
        verify_database()
        print("\n" + "=" * 60)
        print("🎬 Database is ready for CineForge AI!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Start the backend: cd backend && python app.py")
        print("2. Start the frontend: cd frontend && npm run dev")
        print("3. Register a new user at http://localhost:3000/register")
    else:
        print("\n" + "=" * 60)
        print("❌ Database initialization failed")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Ensure MySQL server is running")
        print("2. Check MySQL credentials in this script")
        print("3. Verify you have permissions to create databases")
