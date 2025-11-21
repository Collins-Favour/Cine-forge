"""
Fix user roles - Update database enum and fix empty roles
"""
from app import create_app
from models import db, User
from sqlalchemy import text

app = create_app()

with app.app_context():
    print('\n=== FIXING USER ROLES ===\n')
    
    # Step 1: Alter enum to include new roles
    print('Step 1: Updating role enum in database...')
    try:
        # For MySQL, alter the enum column
        db.session.execute(text("""
            ALTER TABLE users 
            MODIFY COLUMN role ENUM('student', 'filmmaker', 'professional', 'admin', 'investor', 'actor', 'crew_member') 
            DEFAULT 'filmmaker'
        """))
        db.session.commit()
        print('✅ Database enum updated successfully')
    except Exception as e:
        db.session.rollback()
        print(f'⚠️  Enum update: {e}')
        print('   (This is OK if enum already includes new values)')
    
    # Step 2: Fix users with empty or NULL roles
    print('\nStep 2: Fixing users with empty/missing roles...')
    
    # Map emails to their correct roles
    role_mappings = {
        'investor@test.com': 'investor',
        'actor@test.com': 'actor',
        'cinematographer@test.com': 'crew_member',
    }
    
    fixed_count = 0
    for email, correct_role in role_mappings.items():
        user = User.query.filter_by(email=email).first()
        if user:
            if not user.role or user.role == '' or user.role not in ['student', 'filmmaker', 'professional', 'admin', 'investor', 'actor', 'crew_member']:
                old_role = user.role or 'EMPTY'
                user.role = correct_role
                print(f'  ✅ {email:35} {old_role:15} → {correct_role}')
                fixed_count += 1
    
    # Fix any other users with empty roles to 'filmmaker' (default)
    users_with_empty_roles = User.query.filter(
        db.or_(
            User.role == '',
            User.role == None
        )
    ).all()
    
    for user in users_with_empty_roles:
        if user.email not in role_mappings:
            user.role = 'filmmaker'
            print(f'  ✅ {user.email:35} EMPTY           → filmmaker (default)')
            fixed_count += 1
    
    db.session.commit()
    print(f'\n✅ Fixed {fixed_count} users with incorrect roles')
    
    # Step 3: Verify all users now have valid roles
    print('\nStep 3: Verifying all users...')
    all_users = User.query.all()
    print(f'\n{"Email":<35} {"Role":<20} {"Status"}')
    print('=' * 70)
    
    for user in all_users:
        status = '✅' if user.role in ['student', 'filmmaker', 'professional', 'admin', 'investor', 'actor', 'crew_member'] else '❌ INVALID'
        print(f'{user.email:<35} {user.role:<20} {status}')
    
    print('\n=== ROLE FIX COMPLETE ===\n')
