import requests
import json

base = 'http://127.0.0.1:5000/api'

print("=== COMPREHENSIVE PROJECT 7 TEST ===\n")

# Login
r = requests.post(f'{base}/auth/login', json={'email': 'test@gmail.com', 'password': 'Test@123'})
if r.status_code != 200:
    print(f"❌ Login failed: {r.status_code}")
    exit(1)

token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print("✅ Login successful\n")

# Test all endpoints
endpoints = [
    ('GET', '/projects', None, 'List all projects'),
    ('GET', '/projects/7', None, 'Get project details'),
    ('GET', '/scripts/project/7/versions', None, 'Get script versions'),
    ('GET', '/scenes/project/7/scenes', None, 'Get scenes'),
    ('GET', '/storyboards/project/7', None, 'Get storyboards'),
    ('GET', '/projects/7/activity', None, 'Get activity log'),
    ('GET', '/users/dashboard', None, 'Get dashboard'),
]

all_passed = True

for method, endpoint, data, description in endpoints:
    full_url = f'{base}{endpoint}'
    
    if method == 'GET':
        r = requests.get(full_url, headers=headers)
    elif method == 'POST':
        r = requests.post(full_url, json=data, headers=headers)
    
    status_icon = '✅' if r.status_code == 200 else '❌'
    print(f"{status_icon} {method} {endpoint}")
    print(f"   {description}")
    print(f"   Status: {r.status_code}")
    
    if r.status_code == 200:
        try:
            response = r.json()
            # Show key info
            if 'projects' in response:
                print(f"   Projects: {len(response['projects'])}")
            elif 'project_id' in response:
                print(f"   Project: {response.get('title', 'N/A')}")
            elif 'versions' in response:
                print(f"   Versions: {len(response['versions'])}")
            elif 'scenes' in response:
                print(f"   Scenes: {len(response['scenes'])}")
            elif 'panels' in response:
                print(f"   Panels: {len(response['panels'])}")
            elif 'activities' in response:
                print(f"   Activities: {len(response['activities'])}")
            elif 'total_projects' in response:
                print(f"   Total Projects: {response['total_projects']}")
        except:
            pass
    else:
        all_passed = False
        try:
            print(f"   Error: {r.json()}")
        except:
            print(f"   Error: {r.text[:100]}")
    
    print()

if all_passed:
    print("🎉 ALL TESTS PASSED! Project 7 is fully functional.")
else:
    print("⚠️  Some tests failed. Check errors above.")
