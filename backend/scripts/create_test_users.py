"""Check and create test users for all roles"""
from app import create_app
from models import db, User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print('\n=== EXISTING USERS ===')
    users = User.query.all()
    for u in users:
        print(f'{u.user_id}: {u.email:35} Role: {u.role or "MISSING":15} Active: {u.is_active}')
    
    # Fix cinematographer role
    cinematographer = User.query.filter_by(email='cinematographer@test.com').first()
    if cinematographer:
        if not cinematographer.role or cinematographer.role == '':
            cinematographer.role = 'crew_member'
            print(f'\n✅ Fixed cinematographer role to crew_member')
    
    # Fix investor role
    investor_existing = User.query.filter_by(email='investor@test.com').first()
    if investor_existing:
        if not investor_existing.role or investor_existing.role == '':
            investor_existing.role = 'investor'
            print(f'✅ Fixed investor role to investor')
    
    # Fix actor role  
    actor_existing = User.query.filter_by(email='actor@test.com').first()
    if actor_existing:
        if not actor_existing.role or actor_existing.role == '':
            actor_existing.role = 'actor'
            print(f'✅ Fixed actor role to actor')
    
    # Fix admin password
    admin_user = User.query.filter_by(email='admin@cineforge.ai').first()
    if admin_user:
        admin_user.password_hash = generate_password_hash('Admin@123')
        print(f'✅ Reset admin password')
    
    db.session.commit()
    
    # Create investor test user
    investor = User.query.filter_by(email='investor@test.com').first()
    if not investor:
        investor = User(
            username='investor_test',
            email='investor@test.com',
            password_hash=generate_password_hash('Test@123'),
            first_name='Investor',
            last_name='TestUser',
            role='investor',
            is_verified=True,
            is_active=True
        )
        db.session.add(investor)
        print(f'\n✅ Created investor test user')
    
    # Create actor test user
    actor = User.query.filter_by(email='actor@test.com').first()
    if not actor:
        actor = User(
            username='actor_test',
            email='actor@test.com',
            password_hash=generate_password_hash('Test@123'),
            first_name='Actor',
            last_name='TestUser',
            role='actor',
            is_verified=True,
            is_active=True
        )
        db.session.add(actor)
        print(f'✅ Created actor test user')
    
    db.session.commit()
    
    print('\n=== UPDATED USERS ===')
    users = User.query.all()
    for u in users:
        print(f'{u.user_id}: {u.email:35} Role: {u.role:15} Password: Test@123')
