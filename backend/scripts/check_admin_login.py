from app import create_app
from models import User

app = create_app()
with app.app_context():
    # Check for admin user
    admin = User.query.filter_by(email='admin@cineforge.ai').first()
    
    if admin:
        print(f"✅ Admin user found:")
        print(f"   Email: {admin.email}")
        print(f"   Username: {admin.username}")
        print(f"   Name: {admin.first_name} {admin.last_name}")
        print(f"   Role: {admin.role}")
        print(f"   Active: {admin.is_active}")
        
        # Try to verify password
        test_password = "Admin@123"
        if admin.check_password(test_password):
            print(f"\n✅ Password 'Admin@123' is CORRECT")
        else:
            print(f"\n❌ Password 'Admin@123' is INCORRECT")
            print(f"\nTrying to reset password to 'Admin@123'...")
            admin.set_password(test_password)
            from models import db
            db.session.commit()
            print(f"✅ Password reset successfully!")
    else:
        print("❌ Admin user not found. Creating one...")
        from models import db
        
        admin = User(
            email='admin@cineforge.ai',
            username='admin',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            is_verified=True
        )
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Admin user created!")
        print(f"   Email: admin@cineforge.ai")
        print(f"   Password: Admin@123")
