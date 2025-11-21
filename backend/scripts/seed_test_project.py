"""
Seed script to create a test project with collaboration data
Run: python seed_test_project.py
"""
from app import create_app
from models import db, User, Project, ProjectCollaborator, CSpaceMessage
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random

app = create_app()

def seed_test_project():
    with app.app_context():
        print("🌱 Starting seed process...")
        
        # Create test users if they don't exist
        users_data = [
            {
                'email': 'director@test.com',
                'username': 'sarah_director',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'filmmaker',
                'bio': 'Award-winning film director'
            },
            {
                'email': 'writer@test.com',
                'username': 'michael_writer',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'role': 'filmmaker',
                'bio': 'Screenwriter and producer'
            },
            {
                'email': 'producer@test.com',
                'username': 'emily_producer',
                'first_name': 'Emily',
                'last_name': 'Rodriguez',
                'role': 'filmmaker',
                'bio': 'Executive producer'
            },
            {
                'email': 'cinematographer@test.com',
                'username': 'david_cinematographer',
                'first_name': 'David',
                'last_name': 'Kim',
                'role': 'crew_member',
                'bio': 'Director of Photography'
            }
        ]
        
        created_users = []
        for user_data in users_data:
            user = User.query.filter_by(email=user_data['email']).first()
            if not user:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    password_hash=generate_password_hash('Test@123'),
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    role=user_data['role'],
                    bio=user_data['bio'],
                    is_verified=True
                )
                db.session.add(user)
                print(f"✅ Created user: {user_data['email']}")
            else:
                print(f"ℹ️  User exists: {user_data['email']}")
            created_users.append(user)
        
        db.session.commit()
        
        # Get the first user as project owner
        owner = created_users[0]
        
        # Create test project
        project = Project.query.filter_by(
            title='The Last Mission',
            created_by=owner.user_id
        ).first()
        
        if not project:
            project = Project(
                title='The Last Mission',
                logline='A race against time to save Earth from an asteroid collision',
                synopsis='A sci-fi thriller about a team of astronauts on a dangerous mission to save Earth from an asteroid collision. When a massive asteroid threatens to destroy the planet, a diverse crew of specialists must overcome personal conflicts and technical challenges to complete their mission.',
                genre='Science Fiction',
                production_stage='pre-production',
                created_by=owner.user_id,
                target_length=120,
                budget_range='$5M-$10M',
                is_public=False
            )
            db.session.add(project)
            db.session.commit()
            print(f"✅ Created project: {project.title}")
        else:
            print(f"ℹ️  Project exists: {project.title}")
        
        # Add project owner as owner collaborator
        owner_collab = ProjectCollaborator.query.filter_by(
            project_id=project.project_id,
            user_id=owner.user_id
        ).first()
        
        if not owner_collab:
            owner_collab = ProjectCollaborator(
                project_id=project.project_id,
                user_id=owner.user_id,
                role='owner',
                invited_by=owner.user_id,
                invitation_status='accepted',
                joined_at=datetime.utcnow()
            )
            db.session.add(owner_collab)
            db.session.commit()
            print(f"✅ Added project owner as collaborator: {owner.first_name}")
        else:
            print(f"ℹ️  Owner is already a collaborator: {owner.first_name}")
        
        # Add collaborators
        collaborators_roles = ['editor', 'writer', 'crew', 'viewer']
        for i, user in enumerate(created_users[1:], 1):
            collab = ProjectCollaborator.query.filter_by(
                project_id=project.project_id,
                user_id=user.user_id
            ).first()
            
            if not collab:
                collab = ProjectCollaborator(
                    project_id=project.project_id,
                    user_id=user.user_id,
                    role=collaborators_roles[min(i-1, len(collaborators_roles)-1)],
                    invited_by=owner.user_id
                )
                db.session.add(collab)
                print(f"✅ Added collaborator: {user.first_name} as {collab.role}")
            else:
                print(f"ℹ️  Collaborator exists: {user.first_name}")
        
        db.session.commit()
        
        # Create C-Space messages
        messages_content = [
            {
                'user': created_users[0],
                'content': "Hey team! Welcome to our C-Space for 'The Last Mission'. Let's use this to coordinate our work.",
                'channel': 'general',
                'time_offset': 120
            },
            {
                'user': created_users[1],
                'content': "Thanks Sarah! I've been working on the script revisions. Should have the new draft ready by Friday.",
                'channel': 'general',
                'time_offset': 115
            },
            {
                'user': created_users[2],
                'content': "Great! I've secured funding for the production. We're good to move forward with pre-production.",
                'channel': 'general',
                'time_offset': 110
            },
            {
                'user': created_users[3],
                'content': "I've been scouting locations. Found some amazing spots for the space station scenes.",
                'channel': 'production',
                'time_offset': 105
            },
            {
                'user': created_users[0],
                'content': "That's fantastic David! Can you share some photos in the production channel?",
                'channel': 'production',
                'time_offset': 100
            },
            {
                'user': created_users[1],
                'content': "Quick question about Act 2 - should we keep the dialogue heavy scene or make it more visual?",
                'channel': 'creative',
                'time_offset': 95
            },
            {
                'user': created_users[0],
                'content': "Let's make it more visual. The asteroid reveal should be breathtaking, not talked about.",
                'channel': 'creative',
                'time_offset': 90
            },
            {
                'user': created_users[2],
                'content': "Budget update: We need to trim $50k from post-production. Any suggestions?",
                'channel': 'budget',
                'time_offset': 85
            },
            {
                'user': created_users[0],
                'content': "We could reduce the number of VFX shots in the final sequence.",
                'channel': 'budget',
                'time_offset': 80
            },
            {
                'user': created_users[3],
                'content': "Or we could optimize the lighting setup to reduce equipment rental costs.",
                'channel': 'budget',
                'time_offset': 75
            },
            {
                'user': created_users[1],
                'content': "Just finished the character backstory for Commander Hayes. It's going to add so much depth!",
                'channel': 'creative',
                'time_offset': 70
            },
            {
                'user': created_users[2],
                'content': "Team meeting scheduled for Thursday 2pm. Let's discuss the shooting schedule.",
                'channel': 'general',
                'time_offset': 60
            },
            {
                'user': created_users[0],
                'content': "Perfect! I'll prepare the shot list. This is going to be an amazing film!",
                'channel': 'general',
                'time_offset': 55
            },
            {
                'user': created_users[1],
                'content': "Can't wait to see this story come to life! 🎬",
                'channel': 'general',
                'time_offset': 50
            }
        ]
        
        # Clear existing messages for this project to avoid duplicates
        existing_count = CSpaceMessage.query.filter_by(project_id=project.project_id).count()
        if existing_count == 0:
            for msg_data in messages_content:
                message = CSpaceMessage(
                    project_id=project.project_id,
                    user_id=msg_data['user'].user_id,
                    message_content=msg_data['content'],
                    message_type='text',
                    sent_at=datetime.utcnow() - timedelta(minutes=msg_data['time_offset'])
                )
                db.session.add(message)
            
            db.session.commit()
            print(f"✅ Created {len(messages_content)} C-Space messages")
        else:
            print(f"ℹ️  Messages already exist ({existing_count} messages)")
        
        print(f"\n🎉 Seed complete!")
        print(f"\n📋 Test Project Details:")
        print(f"   Project ID: {project.project_id}")
        print(f"   Title: {project.title}")
        print(f"   Owner: {owner.first_name} {owner.last_name} ({owner.email})")
        print(f"   Collaborators: {len(created_users)} total")
        print(f"\n🔗 Access C-Space at:")
        print(f"   http://localhost:3000/projects/{project.project_id}/c-space")
        print(f"\n🔑 Test Credentials:")
        for user in created_users:
            print(f"   {user.email} / Test@123")

if __name__ == '__main__':
    seed_test_project()
