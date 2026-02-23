"""Test database connection"""
from app import create_app
from models import db

app = create_app('development')

with app.app_context():
    try:
        # Try to connect to database
        connection = db.engine.connect()
        print("✅ Database connection successful!")
        
        # Try to execute a simple query
        result = connection.execute(db.text("SELECT 1"))
        print("✅ Database query successful!")
        
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"✅ Found {len(tables)} tables: {tables[:5]}{'...' if len(tables) > 5 else ''}")
        
        connection.close()
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print(f"Error type: {type(e).__name__}")
