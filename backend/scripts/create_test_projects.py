"""
Add projects for all test users so they all have something to see
"""
from app import create_app
from models import db, User, Project, ProjectCollaborator
from datetime import datetime

app = create_app()

with app.app_context():
    print('=== CREATING PROJECTS FOR ALL TEST USERS ===\n')
    
    # Get users
    filmmaker = User.query.filter_by(email='filmmaker@test.com').first()
    admin = User.query.filter_by(email='admin@cineforge.ai').first()
    investor = User.query.filter_by(email='investor@test.com').first()
    actor = User.query.filter_by(email='actor@test.com').first()
    
    projects_to_create = [
        {
            'owner': filmmaker,
            'title': 'Indie Film Project',
            'logline': 'A heartwarming story about finding your path',
            'genre': 'Drama',
            'stage': 'development'
        },
        {
            'owner': investor,
            'title': 'Investment Portfolio Review',
            'logline': 'Documentary series about film financing',
            'genre': 'Documentary',
            'stage': 'pre-production'
        },
        {
            'owner': actor,
            'title': 'Acting Showcase Reel',
            'logline': 'Collection of scenes for portfolio',
            'genre': 'Various',
            'stage': 'production'
        }
    ]
    
    for proj_data in projects_to_create:
        owner = proj_data['owner']
        if not owner:
            print(f'⚠️  User not found, skipping...')
            continue
            
        # Create project
        project = Project(
            title=proj_data['title'],
            logline=proj_data['logline'],
            genre=proj_data['genre'],
            production_stage=proj_data['stage'],
            created_by=owner.user_id,
            is_public=False
        )
        db.session.add(project)
        db.session.flush()
        
        # Add owner as collaborator
        collab = ProjectCollaborator(
            project_id=project.project_id,
            user_id=owner.user_id,
            role='owner',
            invited_by=owner.user_id,
            invitation_status='accepted',
            joined_at=datetime.utcnow()
        )
        db.session.add(collab)
        
        print(f'✅ Created: "{proj_data["title"]}" for {owner.email}')
    
    db.session.commit()
    
    print('\n=== PROJECTS CREATED SUCCESSFULLY ===')
    print('\nNow all test users should see at least one project!')
