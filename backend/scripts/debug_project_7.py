from models import db, Project, ProjectCollaborator, User
from app import create_app
import requests

app = create_app()
app.app_context().push()

print("=== CHECKING PROJECT 7 ===\n")

# Check database
p7 = db.session.get(Project, 7)
if p7:
    print(f"Project 7 in database:")
    print(f"  ID: {p7.project_id}")
    print(f"  Title: {p7.title}")
    print(f"  Owner ID: {p7.created_by}")
    print(f"  Is Archived: {p7.is_archived}")
    print(f"  Is Public: {p7.is_public}")
    
    owner = db.session.get(User, p7.created_by)
    print(f"  Owner: {owner.username} ({owner.email})")
    
    collabs = ProjectCollaborator.query.filter_by(project_id=7, invitation_status='accepted').all()
    print(f"\n  Collaborators ({len(collabs)}):")
    for c in collabs:
        u = db.session.get(User, c.user_id)
        print(f"    - {u.username} (ID: {c.user_id}), Role: {c.role}, Permissions: {c.permissions}")
else:
    print("❌ Project 7 NOT FOUND in database!")

# Test API
print("\n=== TESTING API ACCESS ===\n")

base = 'http://127.0.0.1:5000/api'

# Login as test@gmail.com
r = requests.post(f'{base}/auth/login', json={'email': 'test@gmail.com', 'password': 'Test@123'})
if r.status_code == 200:
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("Testing as test@gmail.com:")
    
    # Test get project
    r1 = requests.get(f'{base}/projects/7', headers=headers)
    print(f"  GET /api/projects/7: {r1.status_code}")
    if r1.status_code != 200:
        print(f"    Error: {r1.json()}")
    else:
        data = r1.json()
        print(f"    Response keys: {list(data.keys())}")
        print(f"    Title: {data.get('title', 'MISSING')}")
    
    # Test get scripts
    r2 = requests.get(f'{base}/scripts/project/7/versions', headers=headers)
    print(f"  GET /api/scripts/project/7/versions: {r2.status_code}")
    if r2.status_code != 200:
        print(f"    Error: {r2.json()}")
    
    # Test get scenes
    r3 = requests.get(f'{base}/scenes/project/7/scenes', headers=headers)
    print(f"  GET /api/scenes/project/7/scenes: {r3.status_code}")
    if r3.status_code != 200:
        print(f"    Error: {r3.json()}")
    
    # Test get storyboards
    r4 = requests.get(f'{base}/storyboards/project/7', headers=headers)
    print(f"  GET /api/storyboards/project/7: {r4.status_code}")
    if r4.status_code != 200:
        print(f"    Error: {r4.json()}")
    
    # Test get activity
    r5 = requests.get(f'{base}/projects/7/activity', headers=headers)
    print(f"  GET /api/projects/7/activity: {r5.status_code}")
    if r5.status_code != 200:
        try:
            print(f"    Error: {r5.json()}")
        except:
            print(f"    Error (text): {r5.text[:200]}")
else:
    print(f"❌ Login failed: {r.status_code}")
