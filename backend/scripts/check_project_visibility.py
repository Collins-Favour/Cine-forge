import requests
import json

base = 'http://127.0.0.1:5000/api'

test_users = [
    ('admin@cineforge.ai', 'Admin@123', 'admin'),
    ('director@test.com', 'Test@123', 'filmmaker'),
    ('investor@test.com', 'Test@123', 'investor'),
    ('actor@test.com', 'Test@123', 'actor'),
    ('cinematographer@test.com', 'Test@123', 'crew_member'),
    ('filmmaker@test.com', 'Test@123', 'filmmaker'),
    ('writer@test.com', 'Test@123', 'filmmaker'),
    ('producer@test.com', 'Test@123', 'filmmaker')
]

print('=== CHECKING PROJECT VISIBILITY ===\n')

for email, password, role in test_users:
    r = requests.post(f'{base}/auth/login', json={'email': email, 'password': password})
    if r.status_code == 200:
        token = r.json()['access_token']
        user_id = r.json()['user']['user_id']
        username = r.json()['user']['username']
        
        headers = {'Authorization': f'Bearer {token}'}
        projects_r = requests.get(f'{base}/projects', headers=headers)
        
        if projects_r.status_code == 200:
            projects = projects_r.json()['projects']
            print(f'{username} (ID:{user_id}, {role}): {len(projects)} project(s)')
            for p in projects:
                title = p.get('title', 'Untitled')
                pid = p.get('project_id', 'N/A')
                print(f'  - {title} (ID: {pid})')
        else:
            print(f'{username}: ERROR {projects_r.status_code}')
    print()

print('=== CHECKING DATABASE DIRECTLY ===\n')
print('Expected: Project 1 should have 4 collaborators:')
print('  - filmmaker@test.com (owner)')
print('  - writer@test.com')
print('  - producer@test.com')
print('  - cinematographer@test.com')
