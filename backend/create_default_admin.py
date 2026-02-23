"""Quickly create an admin user with default credentials"""
from app import create_app
from models import db
from models.user import User

def create_default_admin():
    """Create admin user with default credentials"""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 70)
        print("CREATING DEFAULT ADMIN USER")
        print("=" * 70)
        print()
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@cineforge.ai').first()
        
        if admin:
            print(f"✅ Admin user already exists!")
            print(f"   Username: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Role: {admin.role}")
            print()
            print("Resetting password to 'admin123'...")
            admin.set_password('admin123')
            admin.is_active = True
            admin.is_verified = True
            admin.role = 'admin'
            db.session.commit()
            print("✅ Password reset successful!")
        else:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@cineforge.ai',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True,
                is_verified=True
            )
            admin.set_password('admin123')
            
            db.session.add(admin)
            db.session.commit()
            print("✅ Admin user created successfully!")
        
        print()
        print("=" * 70)
        print("LOGIN CREDENTIALS")
        print("=" * 70)
        print()
        print("  Email:    admin@cineforge.ai")
        print("  Password: admin123")
        print("  Role:     admin")
        print()
        print("⚠️  IMPORTANT: Change this password after first login!")
        print()

if __name__ == '__main__':
    try:
        create_default_admin()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
