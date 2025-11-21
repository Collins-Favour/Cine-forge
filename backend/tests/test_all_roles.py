import requests
import json

base = 'http://127.0.0.1:5000/api'

test_users = [
    ('admin@cineforge.ai', 'Admin@123', 'admin'),
    ('director@test.com', 'Test@123', 'filmmaker'),
    ('investor@test.com', 'Test@123', 'investor'),
    ('actor@test.com', 'Test@123', 'actor'),
    ('cinematographer@test.com', 'Test@123', 'crew_member')
]

print('=== TESTING ALL ROLES ===\n')
for email, password, expected_role in test_users:
    print(f'Testing {expected_role.upper()}: {email}')
    
    # Login
    r = requests.post(f'{base}/auth/login', json={'email': email, 'password': password})
    if r.status_code == 200:
        data = r.json()
        token = data.get('access_token')
        role = data.get('role', 'MISSING')
        user_id = data.get('user_id')
        print(f'  Login: SUCCESS - Role: {role} (user_id: {user_id})')
        
        # Test dashboard
        headers = {'Authorization': f'Bearer {token}'}
        dash = requests.get(f'{base}/users/dashboard', headers=headers)
        if dash.status_code == 200:
            stats = dash.json()
            projects = stats.get('total_projects', 0)
            active = stats.get('active_projects', 0)
            collabs = stats.get('collaborations', 0)
            print(f'  Dashboard: SUCCESS - {projects} total projects, {active} active, {collabs} collaborations')
        else:
            print(f'  Dashboard: FAILED - Status {dash.status_code}')
            
        # Test admin access (should only work for admin)
        admin = requests.get(f'{base}/admin/dashboard', headers=headers)
        if admin.status_code == 200:
            print(f'  Admin Access: GRANTED')
        elif admin.status_code == 403:
            print(f'  Admin Access: DENIED (expected for non-admin)')
        else:
            print(f'  Admin Access: ERROR {admin.status_code}')
    else:
        print(f'  Login: FAILED - Status {r.status_code}')
    print()

print('=== TEST COMPLETE ===')
