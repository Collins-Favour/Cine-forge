import requests
import json

base = 'http://127.0.0.1:5000/api'

# Login as director
print('Logging in as director to access project...\n')
r = requests.post(f'{base}/auth/login', json={
    'email': 'director@test.com',
    'password': 'Test@123'
})

if r.status_code == 200:
    token = r.json()['access_token']
    print('✅ Login successful\n')
    
    # Get projects
    headers = {'Authorization': f'Bearer {token}'}
    r = requests.get(f'{base}/projects', headers=headers)
    
    if r.status_code == 200:
        projects = r.json()['projects']
        print(f'Found {len(projects)} project(s):\n')
        
        for p in projects:
            print(f'  Project ID: {p["project_id"]}')
            print(f'  Title: {p["title"]}')
            print(f'  URL: http://localhost:3000/projects/{p["project_id"]}/c-space')
            print()
else:
    print('❌ Login failed')
