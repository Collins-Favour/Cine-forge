"""Simple test for Supabase PostgreSQL connection"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

print("🔍 Testing Supabase connection...")
print(f"Connection string: {DATABASE_URL[:50]}...") 

try:
    # Connect to Supabase
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ Successfully connected to Supabase!")
    
    # Create a cursor and execute a simple query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()
    print(f"✅ PostgreSQL version: {db_version[0][:50]}...")
    
    # Check existing tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    print(f"✅ Found {len(tables)} table(s) in database")
    if tables:
        print(f"   Tables: {[t[0] for t in tables]}")
    else:
        print("   ⚠️  No tables found - you need to run the schema!")
    
    cursor.close()
    conn.close()
    print("\n✅ All tests passed! Connection is working.")
    
except psycopg2.OperationalError as e:
    print(f"❌ Connection failed: {e}")
    print("\n💡 Troubleshooting:")
    print("   1. Check your password in .env file")
    print("   2. Verify your project URL is correct")
    print("   3. Make sure your Supabase project is active")
except Exception as e:
    print(f"❌ Error: {e}")
