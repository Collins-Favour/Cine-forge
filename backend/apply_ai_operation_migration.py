"""
Apply AI Operation Type Migration
Adds missing enum values to ai_operation type in PostgreSQL
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

def apply_migration():
    """Apply the AI operation type migration"""
    
    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL not found in environment variables")
        return False
    
    print("🔄 Applying AI operation type migration...")
    print(f"📊 Database: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'unknown'}")
    
    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("\n✅ Connected to database")
        
        # Check current enum values
        print("\n📋 Current ai_operation enum values:")
        cur.execute("SELECT unnest(enum_range(NULL::ai_operation))")
        current_values = [row[0] for row in cur.fetchall()]
        for value in current_values:
            print(f"   - {value}")
        
        # Add new enum values
        new_values = [
            'auto_script_generation',
            'storyboard_image_generation',
            'mood_board_generation'
        ]
        
        print("\n🔧 Adding new enum values...")
        
        for value in new_values:
            if value not in current_values:
                try:
                    cur.execute(f"ALTER TYPE ai_operation ADD VALUE '{value}'")
                    conn.commit()
                    print(f"   ✅ Added: {value}")
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print(f"   ℹ️  Already exists: {value}")
                    else:
                        raise
            else:
                print(f"   ℹ️  Already exists: {value}")
        
        # Verify final enum values
        print("\n📋 Final ai_operation enum values:")
        cur.execute("SELECT unnest(enum_range(NULL::ai_operation))")
        final_values = [row[0] for row in cur.fetchall()]
        for value in final_values:
            symbol = "✅" if value in new_values else "  "
            print(f"   {symbol} {value}")
        
        cur.close()
        conn.close()
        
        print("\n✅ Migration applied successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("AI OPERATION TYPE MIGRATION")
    print("="*80 + "\n")
    
    success = apply_migration()
    
    print("\n" + "="*80)
    if success:
        print("Migration Complete!")
        print("\nYou can now use these operation types:")
        print("  - auto_script_generation")
        print("  - storyboard_image_generation")
        print("  - mood_board_generation")
    else:
        print("Migration Failed!")
        print("\nPlease check the error messages above.")
    print("="*80 + "\n")
    
    sys.exit(0 if success else 1)
