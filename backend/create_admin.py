"""Create an admin user for CineForge AI"""
from app import create_app
from models import db
from models.user import User
import sys

def create_admin_user():
    """Create or update admin user"""
    app = create_app('development')
    
    with app.app_context():
        print("=" * 70)
        print("ADMIN USER SETUP")
        print("=" * 70)
        print()
        
        # Check if admin exists
        admin = User.query.filter_by(role='admin').first()
        
        if admin:
            print(f"⚠️  Admin user already exists:")
            print(f"   Username: {admin.username}")
            print(f"   Email: {admin.email}")
            print(f"   Role: {admin.role}")
            print()
            
            response = input("Do you want to reset the admin password? (yes/no): ")
            if response.lower() != 'yes':
                print("Cancelled.")
                return
            
            # Get new password
            new_password = input("Enter new admin password: ")
            if len(new_password) < 6:
                print("❌ Password must be at least 6 characters long!")
                return
            
            admin.set_password(new_password)
            admin.is_active = True
            admin.is_verified = True
            db.session.commit()
            
            print()
            print("✅ Admin password updated successfully!")
            print()
            print(f"Login with:")
            print(f"  Email: {admin.email}")
            print(f"  Password: {new_password}")
            print()
            
        else:
            print("No admin user found. Let's create one!")
            print()
            
            # Get admin details
            username = input("Enter admin username (default: admin): ").strip() or "admin"
            email = input("Enter admin email (default: admin@cineforge.ai): ").strip() or "admin@cineforge.ai"
            password = input("Enter admin password: ")
            
            if len(password) < 6:
                print("❌ Password must be at least 6 characters long!")
                return
            
            # Check if username/email exists
            if User.query.filter_by(username=username).first():
                print(f"❌ Username '{username}' already exists!")
                return
            
            if User.query.filter_by(email=email).first():
                print(f"❌ Email '{email}' already exists!")
                return
            
            # Create admin user
            admin = User(
                username=username,
                email=email,
                first_name="Admin",
                last_name="User",
                role='admin',
                is_active=True,
                is_verified=True
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            print()
            print("=" * 70)
            print("✅ ADMIN USER CREATED SUCCESSFULLY!")
            print("=" * 70)
            print()
            print(f"Login Credentials:")
            print(f"  Username: {username}")
            print(f"  Email: {email}")
            print(f"  Password: {password}")
            print(f"  Role: admin")
            print()
            print(f"You can now login at: http://localhost:3000")
            print()

if __name__ == '__main__':
    try:
        create_admin_user()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)
