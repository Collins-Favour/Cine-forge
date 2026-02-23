"""
Verify admin account and test login
"""
from app import create_app
from models import db
from models.user import User

app = create_app('development')

with app.app_context():
    print("=" * 70)
    print("VERIFYING ADMIN ACCOUNT")
    print("=" * 70)
    
    # Check if admin exists
    admin = User.query.filter_by(email='admin@cineforge.ai').first()
    
    if not admin:
        print("\n❌ No admin account found!")
        print("   Run: python create_default_admin.py")
        exit()
    
    print(f"\n✅ Admin account found:")
    print(f"   Username: {admin.username}")
    print(f"   Email: {admin.email}")
    print(f"   Role: {admin.role}")
    print(f"   Active: {admin.is_active}")
    print(f"   Verified: {admin.is_verified}")
    
    # Test password
    print("\n🔐 Testing password 'admin123'...")
    if admin.check_password('admin123'):
        print("✅ Password verification SUCCESSFUL!")
    else:
        print("❌ Password verification FAILED!")
        print("   The password hash may be corrupted.")
        print("   Resetting password to 'admin123'...")
        admin.set_password('admin123')
        db.session.commit()
        print("✅ Password reset successful!")
    
    print("\n" + "=" * 70)
    print("LOGIN CREDENTIALS:")
    print("=" * 70)
    print(f"Email:    admin@cineforge.ai")
    print(f"Password: admin123")
    print("=" * 70)
