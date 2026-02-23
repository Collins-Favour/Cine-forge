"""
Delete all admin accounts from the database
"""
from app import create_app
from models import db
from models.user import User

app = create_app('development')

with app.app_context():
    print("=" * 70)
    print("DELETE ALL ADMIN ACCOUNTS")
    print("=" * 70)
    
    # Find all admin users
    admin_users = User.query.filter_by(role='admin').all()
    
    if not admin_users:
        print("\n✅ No admin accounts found in the database.")
        print("=" * 70)
        exit()
    
    print(f"\n⚠️  Found {len(admin_users)} admin account(s):")
    for user in admin_users:
        print(f"   - {user.username} ({user.email})")
    
    print("\n⚠️  WARNING: This will permanently delete all admin accounts!")
    print("=" * 70)
    
    response = input("\nAre you sure you want to delete ALL admin accounts? (yes/no): ")
    
    if response.lower() != 'yes':
        print("❌ Deletion cancelled.")
        exit()
    
    print("\n🗑️  Deleting admin accounts...")
    
    try:
        for user in admin_users:
            print(f"   Deleting: {user.username} ({user.email})")
            db.session.delete(user)
        
        db.session.commit()
        print(f"\n✅ Successfully deleted {len(admin_users)} admin account(s)!")
        print("=" * 70)
        
    except Exception as e:
        db.session.rollback()
        print(f"\n❌ Error deleting admin accounts: {e}")
        print("=" * 70)
