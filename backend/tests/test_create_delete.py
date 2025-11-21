import requests

base = 'http://127.0.0.1:5000/api'

print("=== TESTING CREATE & DELETE PROJECT ===\n")

# Login
r = requests.post(f'{base}/auth/login', json={'email': 'test@gmail.com', 'password': 'Test@123'})
if r.status_code != 200:
    print(f"❌ Login failed")
    exit(1)

token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print("✅ Logged in\n")

# Create project
print("Testing POST /api/projects (create)...")
new_project = {
    'title': 'Test Project - Can Be Deleted',
    'logline': 'A test project to verify create functionality',
    'synopsis': 'This is a comprehensive test of the project creation system.',
    'genre': 'Documentary',
    'target_length': 30,
    'budget_range': 'Under $100K'
}

r = requests.post(f'{base}/projects', json=new_project, headers=headers)
if r.status_code == 201:
    data = r.json()
    project_id = data['project']['project_id']
    print(f"✅ Project created successfully")
    print(f"   ID: {project_id}")
    print(f"   Title: {data['project']['title']}")
    
    # Test delete
    print(f"\nTesting DELETE /api/projects/{project_id}...")
    r = requests.delete(f'{base}/projects/{project_id}', headers=headers)
    if r.status_code == 200:
        print("✅ Project deleted successfully")
        print(f"   Message: {r.json()['message']}")
        
        # Verify it's archived
        r = requests.get(f'{base}/projects/{project_id}', headers=headers)
        if r.status_code == 200:
            project = r.json()
            print(f"   Is Archived: {project['is_archived']}")
    else:
        print(f"❌ Delete failed: {r.status_code}")
        print(f"   Error: {r.json()}")
else:
    print(f"❌ Create failed: {r.status_code}")
    print(f"   Error: {r.json()}")

print("\n✅ ALL TESTS COMPLETE")
