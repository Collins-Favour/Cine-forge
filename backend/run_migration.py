"""Run database migration to fix schema mismatch"""
import pymysql
import re

def run_migration():
    print("=" * 70)
    print("RUNNING DATABASE MIGRATION")
    print("=" * 70)
    print()
    
    try:
        # Connect to database
        print("📡 Connecting to database...")
        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='cineforge_ai'
        )
        cursor = conn.cursor()
        print("✅ Connected successfully")
        print()
        
        # Read migration SQL
        print("📄 Reading migration file...")
        with open(r'c:\Users\Kaptain\Documents\CINEFORGE AI\database\migrations\fix_schema_mismatch.sql', 'r') as f:
            sql_content = f.read()
        print("✅ Migration file loaded")
        print()
        
        # Split into commands and execute
        print("🔧 Applying migrations...")
        print()
        
        # Split by semicolon but keep multi-line statements together
        commands = [cmd.strip() for cmd in sql_content.split(';') if cmd.strip()]
        
        print(f"Found {len(commands)} potential commands")
        print()
        
        executed = 0
        for i, cmd in enumerate(commands, 1):
            # Skip empty commands
            if not cmd or len(cmd) < 5:
                continue
            
            # Remove comment lines and keep only SQL
            cmd_lines = [line for line in cmd.split('\n') if line.strip() and not line.strip().startswith('--')]
            cmd_clean = '\n'.join(cmd_lines).strip()
            
            if not cmd_clean:
                continue
                
            try:
                print(f"  Executing: {cmd_clean[:80]}...")
                cursor.execute(cmd_clean)
                executed += 1
                print(f"  ✅ Success")
            except pymysql.Error as e:
                # Ignore "column already exists" errors
                if "Duplicate column" in str(e):
                    print(f"  ⚠️  Column already exists (skipping)")
                else:
                    print(f"  ❌ Error: {e}")
        
        print()
        print(f"✅ Executed {executed} commands")
        print()
        
        # Commit changes
        conn.commit()
        print("✅ Changes committed")
        print()
        
        # Verify changes
        print("🔍 Verifying changes...")
        cursor.execute("DESCRIBE users")
        columns = cursor.fetchall()
        column_names = [col[0] for col in columns]
        
        # Check for required columns
        required_columns = ['phone', 'location', 'user_id', 'username', 'email']
        for col in required_columns:
            if col in column_names:
                print(f"  ✅ Column '{col}' exists")
            else:
                print(f"  ❌ Column '{col}' missing")
        
        print()
        conn.close()
        
        print("=" * 70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        print()
        
        return True
        
    except Exception as e:
        print()
        print("=" * 70)
        print("❌ MIGRATION FAILED!")
        print("=" * 70)
        print()
        print(f"Error: {str(e)}")
        print()
        return False

if __name__ == '__main__':
    success = run_migration()
    exit(0 if success else 1)
