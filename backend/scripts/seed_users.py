"""
Seed Admin and Investor Users
Creates test accounts for admin and investor roles
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import db, User
from app import create_app

def seed_users():
    """Create admin and investor test accounts"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("Seeding Admin and Investor Users")
        print("=" * 60)
        
        # Check if admin exists
        admin = User.query.filter_by(email='admin@cineforge.ai').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@cineforge.ai',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True,
                is_verified=True
            )
            admin.set_password('Admin@123')
            db.session.add(admin)
            print("✓ Created admin user")
        else:
            print("⚠ Admin user already exists")
        
        # Check if investor exists
        investor = User.query.filter_by(email='investor@cineforge.ai').first()
        if not investor:
            investor = User(
                username='investor',
                email='investor@cineforge.ai',
                first_name='Investor',
                last_name='User',
                role='investor',
                is_active=True,
                is_verified=True
            )
            investor.set_password('Investor@123')
            db.session.add(investor)
            print("✓ Created investor user")
        else:
            print("⚠ Investor user already exists")
        
        db.session.commit()
        
        print("\n" + "=" * 60)
        print("Seed Complete!")
        print("=" * 60)
        print("\nLogin Credentials:")
        print("-" * 60)
        print("\nADMIN:")
        print("  Email: admin@cineforge.ai")
        print("  Password: Admin@123")
        print("\nINVESTOR:")
        print("  Email: investor@cineforge.ai")
        print("  Password: Investor@123")
        print("\n" + "=" * 60)

if __name__ == '__main__':
    seed_users()
