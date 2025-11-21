"""
Fix filmmaker@test.com and create admin project
"""
from app import create_app
from models import db, User, Project, ProjectCollaborator
from datetime import datetime

app = create_app()

with app.app_context():
    print('=== FIXING TEST USERS ===\n')
    
    # Check filmmaker user
    filmmaker = User.query.filter_by(email='filmmaker@test.com').first()
    if filmmaker:
        print(f'Filmmaker user found: {filmmaker.email} (ID: {filmmaker.user_id})')
        # Set password
        filmmaker.set_password('Test@123')
        print('✅ Password set for filmmaker@test.com')
    else:
        print('❌ Filmmaker user not found')
    
    # Create admin project
    admin = User.query.filter_by(email='admin@cineforge.ai').first()
    if admin:
        print(f'\nAdmin user found: {admin.email} (ID: {admin.user_id})')
        
        # Create admin project
        project = Project(
            title='Platform Management Dashboard',
            logline='Admin panel for monitoring and managing the CineForge AI platform',
            genre='System',
            production_stage='production',
            created_by=admin.user_id,
            is_public=False
        )
        db.session.add(project)
        db.session.flush()
        
        # Add admin as collaborator
        collab = ProjectCollaborator(
            project_id=project.project_id,
            user_id=admin.user_id,
            role='owner',
            invited_by=admin.user_id,
            invitation_status='accepted',
            joined_at=datetime.utcnow()
        )
        db.session.add(collab)
        print('✅ Created admin project')
    
    db.session.commit()
    
    print('\n=== DONE ===')
    print('All users should now be able to login and see projects!')
