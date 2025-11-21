"""Create admin user for testing"""
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@cineforge.ai').first()
    
    if not admin:
        admin = User(
            username='admin',
            email='admin@cineforge.ai',
            password_hash=generate_password_hash('Admin@123'),
            first_name='Admin',
            last_name='User',
            role='admin',
            is_verified=True,
            is_active=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created')
        print(f'   Email: {admin.email}')
        print(f'   Password: Admin@123')
        print(f'   Role: {admin.role}')
    else:
        print(f'ℹ️  Admin exists: {admin.email}')
        print(f'   Role: {admin.role}')
        print(f'   User ID: {admin.user_id}')
