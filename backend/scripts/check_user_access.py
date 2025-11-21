from models import db, Project, ProjectCollaborator, User
from app import create_app

app = create_app()
app.app_context().push()

user = User.query.get(2)
print(f'User: {user.username} (ID: {user.user_id}, Email: {user.email})')

collabs = ProjectCollaborator.query.filter_by(user_id=2, invitation_status='accepted').all()
print(f'\nProjects user has access to ({len(collabs)} total):')
for c in collabs:
    project = Project.query.get(c.project_id)
    print(f'  - Project ID: {c.project_id}, Title: "{project.title}", Role: {c.role}')

print(f'\nChecking project 6:')
p6 = Project.query.get(6)
if p6:
    print(f'  Title: {p6.title}')
    print(f'  Owner ID: {p6.created_by}')
    owner = User.query.get(p6.created_by)
    print(f'  Owner: {owner.username} ({owner.email})')
    
    # Check collaborators
    p6_collabs = ProjectCollaborator.query.filter_by(project_id=6, invitation_status='accepted').all()
    print(f'  Collaborators ({len(p6_collabs)}):')
    for c in p6_collabs:
        collab_user = User.query.get(c.user_id)
        print(f'    - {collab_user.username} (ID: {c.user_id}), Role: {c.role}')
else:
    print('  Project 6 NOT FOUND')
