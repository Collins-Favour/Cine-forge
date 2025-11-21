import requests
import json

base = 'http://127.0.0.1:5000/api'

# Login as director
print('1. Logging in as director...')
r = requests.post(f'{base}/auth/login', json={
    'email': 'director@test.com',
    'password': 'Test@123'
})
token = r.json()['access_token']
user_id = r.json()['user']['user_id']
print(f'   Logged in as user_id: {user_id}\n')

# Create new project
print('2. Creating new project...')
headers = {'Authorization': f'Bearer {token}'}
project_data = {
    'title': 'Auto-Collaborator Test Project',
    'description': 'Testing that owner is auto-added as collaborator',
    'genre': 'Drama',
    'production_stage': 'pre-production'
}
r = requests.post(f'{base}/projects', json=project_data, headers=headers)
if r.status_code == 201:
    project = r.json()['project']
    project_id = project['project_id']
    print(f'   Project created: ID {project_id}\n')
    
    # Get project collaborators
    print('3. Checking collaborators...')
    r = requests.get(f'{base}/projects/{project_id}/collaborators', headers=headers)
    if r.status_code == 200:
        collabs = r.json()['collaborators']
        print(f'   Found {len(collabs)} collaborator(s):')
        for c in collabs:
            status = c.get('invitation_status', 'N/A')
            joined = c.get('joined_at', 'N/A')
            print(f'   - User: {c["username"]} (ID: {c["user_id"]})')
            print(f'     Role: {c["role"]}')
            print(f'     Status: {status}')
            print(f'     Joined: {joined}')
    else:
        print(f'   ERROR: Status {r.status_code}')
else:
    print(f'   ERROR: Status {r.status_code}')
    print(f'   {r.json()}')
