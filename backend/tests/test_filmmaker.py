import requests

base = 'http://127.0.0.1:5000/api'

# Test filmmaker@test.com
r = requests.post(f'{base}/auth/login', json={
    'email': 'filmmaker@test.com',
    'password': 'Test@123'
})

print(f'Login Status: {r.status_code}')
if r.status_code == 200:
    data = r.json()
    user_id = data.get('user', {}).get('user_id')
    username = data.get('user', {}).get('username')
    print(f'User ID: {user_id}')
    print(f'Username: {username}')
    
    token = data.get('access_token')
    headers = {'Authorization': f'Bearer {token}'}
    
    projects = requests.get(f'{base}/projects', headers=headers)
    print(f'\nProjects: {projects.status_code}')
    
    if projects.status_code == 200:
        proj_list = projects.json().get('projects', [])
        print(f'Found {len(proj_list)} project(s)')
        for p in proj_list:
            print(f'  - {p["title"]} (ID: {p["project_id"]})')
else:
    print(f'Login failed: {r.json()}')
