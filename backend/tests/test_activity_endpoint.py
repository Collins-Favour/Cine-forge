import requests
import json

base = 'http://127.0.0.1:5000/api'

# Login as admin (has project 6)
print('Testing activity endpoint...\n')
r = requests.post(f'{base}/auth/login', json={
    'email': 'admin@cineforge.ai',
    'password': 'Admin@123'
})

if r.status_code == 200:
    token = r.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Test activity endpoint
    print('1. Testing GET /api/projects/6/activity')
    activity_r = requests.get(f'{base}/projects/6/activity', headers=headers)
    print(f'   Status: {activity_r.status_code}')
    
    if activity_r.status_code == 200:
        data = activity_r.json()
        activities = data.get('activities', [])
        print(f'   Found {len(activities)} activities')
        
        if activities:
            print('\n   Recent activities:')
            for act in activities[:3]:
                print(f'   - {act.get("activity_type")}: {act.get("activity_description")}')
        else:
            print('   (No activities yet - this is normal for new projects)')
    else:
        print(f'   Error: {activity_r.json()}')
else:
    print('Login failed')
