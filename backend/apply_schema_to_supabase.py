"""
Apply PostgreSQL schema to Supabase
This script reads the schema_postgresql.sql file and applies it to your Supabase database.
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
SCHEMA_FILE = '../database/schema_postgresql.sql'

print("=" * 70)
print("CINEFORGE AI - Supabase Schema Migration")
print("=" * 70)
print("\nThis will:")
print("  1. Drop existing public schema (if exists)")
print("  2. Create all tables with migrations included")
print("  3. Set up indexes and constraints")
print("  4. Insert default system settings")
print("\n⚠️  WARNING: This will delete all existing data!")
print("=" * 70)

response = input("\nAre you sure you want to continue? (yes/no): ")
if response.lower() != 'yes':
    print("❌ Migration cancelled.")
    exit()

print("\n🔄 Starting migration...")

try:
    # Read schema file
    print("\n📖 Reading schema file...")
    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    
    print(f"✅ Loaded {len(schema_sql)} characters from schema file")
    
    # Connect to database
    print("\n🔌 Connecting to Supabase...")
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = False  # Use transaction
    cursor = conn.cursor()
    
    print("✅ Connected successfully")
    
    # Execute schema
    print("\n🚀 Applying schema...")
    print("   (This may take 10-20 seconds...)")
    
    cursor.execute(schema_sql)
    
    # Commit transaction
    conn.commit()
    print("✅ Schema applied successfully!")
    
    # Verify tables
    print("\n🔍 Verifying installation...")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    
    print(f"\n✅ Successfully created {len(tables)} tables:")
    for table in tables:
        print(f"   ✓ {table[0]}")
    
    # Check system settings
    cursor.execute("SELECT COUNT(*) FROM system_settings;")
    settings_count = cursor.fetchone()[0]
    print(f"\n✅ System settings initialized: {settings_count} settings")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 70)
    print("🎉 MIGRATION COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("\nYour database includes all migrations:")
    print("  ✓ Extended user roles (investor, actor, crew_member)")
    print("  ✓ Phone and location fields for users")
    print("  ✓ Base64 image support (profile pics, thumbnails)")
    print("  ✓ Channel support for C-Space messages")
    print("  ✓ Action data for notifications")
    print("\nNext steps:")
    print("  1. Create admin user: python create_default_admin.py")
    print("  2. Start your app: python app.py")
    print("  3. Test the connection")
    print("=" * 70)
    
except FileNotFoundError:
    print(f"❌ Error: Could not find schema file at {SCHEMA_FILE}")
    print("   Make sure you're running this from the backend folder")
except psycopg2.Error as e:
    print(f"❌ Database error: {e}")
    print(f"   Error code: {e.pgcode}")
    if conn:
        conn.rollback()
        print("   Changes rolled back - database unchanged")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
finally:
    if 'cursor' in locals() and cursor:
        cursor.close()
    if 'conn' in locals() and conn:
        conn.close()
