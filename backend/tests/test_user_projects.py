import requests
import json

base = 'http://127.0.0.1:5000/api'

# Login as test@gmail.com
print('Testing test@gmail.com user...\n')
r = requests.post(f'{base}/auth/login', json={
    'email': 'test@gmail.com',
    'password': 'Test@123'
})

if r.status_code == 200:
    data = r.json()
    token = data['access_token']
    user = data['user']
    
    print(f'✅ Login successful')
    print(f'User ID: {user["user_id"]}')
    print(f'Username: {user["username"]}')
    print(f'Role: {user["role"]}')
    print()
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test dashboard
    print('Testing dashboard endpoint...')
    dash = requests.get(f'{base}/users/dashboard', headers=headers)
    print(f'Status: {dash.status_code}')
    
    if dash.status_code == 200:
        stats = dash.json()
        print(json.dumps(stats, indent=2))
    else:
        print(f'Error: {dash.json()}')
        
    # Test projects endpoint
    print('\nTesting projects endpoint...')
    proj = requests.get(f'{base}/projects', headers=headers)
    print(f'Status: {proj.status_code}')
    
    if proj.status_code == 200:
        projects = proj.json()
        print(f'Total projects returned: {len(projects.get("projects", []))}')
        for p in projects.get('projects', []):
            print(f'  - {p["title"]} (ID: {p["project_id"]}, Owner: {p["created_by"]})')
else:
    print(f'Login failed: {r.status_code}')
    print(r.json())
