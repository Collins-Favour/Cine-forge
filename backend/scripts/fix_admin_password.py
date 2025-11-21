"""Fix admin password"""
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    admin = User.query.filter_by(email='admin@cineforge.ai').first()
    if admin:
        print(f'Admin user: {admin.email}')
        print(f'Can login with Test@123: {admin.check_password("Test@123")}')
        print(f'Can login with Admin@123: {admin.check_password("Admin@123")}')
        
        # Set password to Admin@123
        admin.password_hash = generate_password_hash('Admin@123')
        db.session.commit()
        print('\n✅ Password reset to: Admin@123')
        
        # Verify it works
        admin_check = User.query.filter_by(email='admin@cineforge.ai').first()
        print(f'✅ Verification: {admin_check.check_password("Admin@123")}')
