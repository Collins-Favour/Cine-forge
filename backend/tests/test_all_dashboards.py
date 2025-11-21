import requests
import json

base = 'http://127.0.0.1:5000/api'

test_users = [
    ('admin@cineforge.ai', 'Admin@123', 'admin'),
    ('filmmaker@test.com', 'Test@123', 'filmmaker'),
    ('director@test.com', 'Test@123', 'filmmaker'),
    ('investor@test.com', 'Test@123', 'investor'),
    ('actor@test.com', 'Test@123', 'actor'),
    ('cinematographer@test.com', 'Test@123', 'crew_member')
]

print('=== CHECKING DASHBOARD DATA FOR ALL ROLES ===\n')

for email, password, role in test_users:
    r = requests.post(f'{base}/auth/login', json={'email': email, 'password': password})
    if r.status_code == 200:
        token = r.json()['access_token']
        user_id = r.json()['user']['user_id']
        username = r.json()['user']['username']
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test dashboard endpoint
        dash = requests.get(f'{base}/users/dashboard', headers=headers)
        
        print(f'{username} ({role}):')
        if dash.status_code == 200:
            data = dash.json()
            print(f'  Status: ✅ {dash.status_code}')
            print(f'  Total Projects: {data.get("total_projects", "MISSING")}')
            print(f'  Active Projects: {data.get("active_projects", "MISSING")}')
            print(f'  Collaborations: {data.get("collaborations", "MISSING")}')
            print(f'  Storyboards: {data.get("total_storyboards", "MISSING")}')
            
            # Show recent projects if any
            recent = data.get('recent_projects', [])
            if recent:
                print(f'  Recent Projects: {len(recent)} found')
                for p in recent[:2]:
                    print(f'    - {p.get("title", "N/A")} (ID: {p.get("project_id", "N/A")})')
            else:
                print(f'  Recent Projects: None')
        else:
            print(f'  Status: ❌ {dash.status_code}')
            print(f'  Error: {dash.json()}')
        print()
