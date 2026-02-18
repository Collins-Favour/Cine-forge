"""
Check and clean up ProjectCollaborator records
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, Project, ProjectCollaborator, User

app = create_app()

with app.app_context():
    print("=" * 80)
    print("PROJECT COLLABORATOR AUDIT")
    print("=" * 80)
    
    # Get all collaborators
    all_collabs = ProjectCollaborator.query.all()
    print(f"\nTotal collaborator records: {len(all_collabs)}")
    
    # Group by user
    user_collabs = {}
    for collab in all_collabs:
        if collab.user_id not in user_collabs:
            user_collabs[collab.user_id] = []
        user_collabs[collab.user_id].append(collab)
    
    print(f"\nCollaborators by user:")
    print("-" * 80)
    
    for user_id, collabs in user_collabs.items():
        user = User.query.get(user_id)
        username = user.username if user else "DELETED USER"
        print(f"\nUser: {username} (ID: {user_id})")
        print(f"  Total collaborations: {len(collabs)}")
        
        for collab in collabs:
            project = Project.query.get(collab.project_id)
            project_title = project.title if project else "DELETED PROJECT"
            print(f"    - Project: {project_title} (ID: {collab.project_id})")
            print(f"      Role: {collab.role}, Status: {collab.invitation_status}")
            print(f"      Invited by: {collab.invited_by}")
    
    # Check for orphaned records (projects that don't exist)
    print("\n" + "=" * 80)
    print("ORPHANED COLLABORATOR RECORDS")
    print("=" * 80)
    
    orphaned = []
    for collab in all_collabs:
        project = Project.query.get(collab.project_id)
        if not project:
            orphaned.append(collab)
            user = User.query.get(collab.user_id)
            username = user.username if user else "DELETED USER"
            print(f"  User {username} (ID: {collab.user_id}) -> Non-existent project ID: {collab.project_id}")
    
    if orphaned:
        print(f"\n⚠️  Found {len(orphaned)} orphaned records")
        response = input("\nDelete orphaned records? (yes/no): ")
        if response.lower() == 'yes':
            for collab in orphaned:
                db.session.delete(collab)
            db.session.commit()
            print(f"✅ Deleted {len(orphaned)} orphaned records")
    else:
        print("\n✅ No orphaned records found")
    
    # Check for duplicate owner records
    print("\n" + "=" * 80)
    print("CHECKING FOR DUPLICATE OWNERS")
    print("=" * 80)
    
    projects = Project.query.all()
    for project in projects:
        owners = ProjectCollaborator.query.filter_by(
            project_id=project.project_id,
            role='owner'
        ).all()
        
        if len(owners) > 1:
            print(f"⚠️  Project '{project.title}' (ID: {project.project_id}) has {len(owners)} owners:")
            for owner in owners:
                user = User.query.get(owner.user_id)
                print(f"    - {user.username if user else 'DELETED'} (ID: {owner.user_id})")
        elif len(owners) == 0:
            print(f"⚠️  Project '{project.title}' (ID: {project.project_id}) has NO owner!")
            print(f"    Created by: {project.created_by}")
            
            response = input(f"  Add creator as owner? (yes/no): ")
            if response.lower() == 'yes':
                from datetime import datetime
                owner_collab = ProjectCollaborator(
                    project_id=project.project_id,
                    user_id=project.created_by,
                    role='owner',
                    invited_by=project.created_by,
                    invitation_status='accepted',
                    joined_at=datetime.utcnow()
                )
                db.session.add(owner_collab)
                db.session.commit()
                print(f"✅ Added creator as owner")
    
    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
