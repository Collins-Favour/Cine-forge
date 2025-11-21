from app import create_app
from models import db, User, Project, ProjectCollaborator
from datetime import datetime

app = create_app()

with app.app_context():
    # Get test@gmail.com user
    user = User.query.get(2)
    
    if not user:
        print('User not found')
        exit()
    
    print(f'Creating project for {user.email}...')
    
    # Create project
    project = Project(
        title='My First Film Project',
        logline='An exciting journey into filmmaking',
        synopsis='A comprehensive project to learn and master the art of filmmaking.',
        genre='Documentary',
        production_stage='pre-production',
        created_by=user.user_id,
        is_public=False
    )
    
    db.session.add(project)
    db.session.flush()
    
    # Add owner as collaborator
    collab = ProjectCollaborator(
        project_id=project.project_id,
        user_id=user.user_id,
        role='owner',
        invited_by=user.user_id,
        invitation_status='accepted',
        joined_at=datetime.utcnow()
    )
    
    db.session.add(collab)
    db.session.commit()
    
    print(f'✅ Project created: "{project.title}" (ID: {project.project_id})')
    print(f'✅ Owner added as collaborator')
