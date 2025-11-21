import requests
import json

base = 'http://127.0.0.1:5000/api'

print("=== TESTING PROJECT 7 FRONTEND COMPATIBILITY ===\n")

# Login
r = requests.post(f'{base}/auth/login', json={'email': 'test@gmail.com', 'password': 'Test@123'})
if r.status_code != 200:
    print(f"❌ Login failed")
    exit(1)

token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print("✅ Logged in as test@gmail.com\n")

# Test project endpoint
print("Testing GET /api/projects/7...")
r = requests.get(f'{base}/projects/7', headers=headers)
if r.status_code == 200:
    data = r.json()
    
    # Check structure
    required_fields = ['project_id', 'title', 'logline', 'synopsis', 'genre', 'production_stage', 'stats']
    missing = [f for f in required_fields if f not in data]
    
    if missing:
        print(f"❌ Missing fields: {missing}")
    else:
        print("✅ All required fields present")
        
    # Check stats structure
    if 'stats' in data:
        required_stats = ['total_scenes', 'total_characters', 'total_collaborators', 'latest_script_version']
        missing_stats = [s for s in required_stats if s not in data['stats']]
        
        if missing_stats:
            print(f"❌ Missing stats: {missing_stats}")
        else:
            print("✅ All stats fields present")
            print(f"\nProject Data:")
            print(f"  Title: {data['title']}")
            print(f"  Stats:")
            print(f"    - Scenes: {data['stats']['total_scenes']}")
            print(f"    - Characters: {data['stats']['total_characters']}")
            print(f"    - Collaborators: {data['stats']['total_collaborators']}")
            print(f"    - Script Version: {data['stats']['latest_script_version']}")
    else:
        print("❌ No stats object")
        
    # Check response structure (NOT nested in 'project' key)
    if 'project' in data:
        print("\n⚠️  WARNING: Response is nested in 'project' key (should be flat)")
    else:
        print("\n✅ Response structure is correct (flat, not nested)")
else:
    print(f"❌ Failed with status {r.status_code}")
    print(f"Error: {r.json()}")

print("\n=== Testing collaborators endpoint ===")
r = requests.get(f'{base}/projects/7/collaborators', headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    collabs = r.json().get('collaborators', [])
    print(f"✅ {len(collabs)} collaborators found")
else:
    print(f"❌ Error: {r.json() if r.status_code != 404 else '404 Not Found'}")

print("\n=== Testing activity endpoint ===")
r = requests.get(f'{base}/projects/7/activity', headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    activities = r.json().get('activities', [])
    print(f"✅ {len(activities)} activities found")
else:
    print(f"❌ Error")

print("\n✅ ALL TESTS COMPLETE")
