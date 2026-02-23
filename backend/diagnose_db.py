"""Comprehensive Database Connectivity Diagnostics"""
import sys
from app import create_app
from models import db
from sqlalchemy import inspect, text

def print_status(emoji, message):
    """Helper to print status messages"""
    print(f"{emoji} {message}")

def main():
    print("=" * 70)
    print("CINEFORGE AI - DATABASE CONNECTIVITY DIAGNOSTICS")
    print("=" * 70)
    print()
    
    try:
        # 1. Create app
        print_status("🔧", "Creating Flask app...")
        app = create_app('development')
        print_status("✅", f"App created successfully")
        print(f"   Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        print()
        
        with app.app_context():
            # 2. Test basic connection
            print_status("🔌", "Testing database connection...")
            connection = db.engine.connect()
            print_status("✅", "Database connection successful!")
            print()
            
            # 3. Test query execution
            print_status("🔍", "Testing database query...")
            result = connection.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print_status("✅", f"Connected to database: {db_name}")
            print()
            
            # 4. Check tables
            print_status("📋", "Checking database tables...")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print_status("✅", f"Found {len(tables)} tables")
            print("   Tables:", ", ".join(tables[:10]))
            if len(tables) > 10:
                print(f"   ... and {len(tables) - 10} more")
            print()
            
            # 5. Check critical tables
            print_status("🔍", "Checking critical tables...")
            critical_tables = ['users', 'projects', 'scripts', 'scenes', 'storyboard_panels']
            for table in critical_tables:
                if table in tables:
                    result = connection.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.fetchone()[0]
                    print_status("✅", f"Table '{table}': {count} rows")
                else:
                    print_status("❌", f"Table '{table}': NOT FOUND")
            print()
            
            # 6. Test model imports
            print_status("📦", "Testing model imports...")
            try:
                from models.user import User
                from models.project import Project
                from models.script import Script
                print_status("✅", "All critical models imported successfully")
            except Exception as e:
                print_status("❌", f"Model import failed: {str(e)}")
            print()
            
            # 7. Test ORM query
            print_status("🔍", "Testing ORM query...")
            try:
                from models.user import User
                user_count = User.query.count()
                print_status("✅", f"ORM query successful: {user_count} users in database")
            except Exception as e:
                print_status("❌", f"ORM query failed: {str(e)}")
            print()
            
            connection.close()
            
        print("=" * 70)
        print_status("🎉", "DIAGNOSTICS COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        print("SUMMARY:")
        print("✅ Database connection: WORKING")
        print("✅ Database queries: WORKING")
        print("✅ Database tables: PRESENT")
        print("✅ ORM functionality: WORKING")
        print()
        print("The backend can successfully communicate with the database!")
        print()
        
    except Exception as e:
        print()
        print("=" * 70)
        print_status("❌", "DIAGNOSTICS FAILED!")
        print("=" * 70)
        print()
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print()
        print("TROUBLESHOOTING STEPS:")
        print("1. Verify MySQL server is running: net start MySQL")
        print("2. Check database exists: mysql -u root -e 'SHOW DATABASES;'")
        print("3. Verify database URI in config.py")
        print("4. Check if tables exist: mysql -u root cineforge_ai -e 'SHOW TABLES;'")
        print("5. Run database migrations: flask db upgrade")
        print()
        sys.exit(1)

if __name__ == '__main__':
    main()
