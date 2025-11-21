import requests

base = 'http://127.0.0.1:5000/api'

print("=== TESTING COLLABORATORS DISPLAY FIX ===\n")

# Login
r = requests.post(f'{base}/auth/login', json={'email': 'test@gmail.com', 'password': 'Test@123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Get project 7 collaborators
r = requests.get(f'{base}/projects/7/collaborators', headers=headers)
if r.status_code == 200:
    collabs = r.json()['collaborators']
    print(f"✅ Found {len(collabs)} collaborator(s)\n")
    
    for collab in collabs:
        print(f"Collaborator ID: {collab['user_id']}")
        print(f"  Role: {collab['role']}")
        print(f"  User Data:")
        print(f"    - Username: {collab['user']['username']}")
        print(f"    - First Name: {collab['user']['first_name']}")
        print(f"    - Last Name: {collab['user']['last_name']}")
        
        # Show what frontend will display
        display_name = collab['user']['username'] or f"{collab['user']['first_name']} {collab['user']['last_name']}".strip()
        initial = (collab['user']['username'] or collab['user']['first_name'] or 'U')[0].upper()
        
        print(f"  Frontend Display:")
        print(f"    - Name: {display_name}")
        print(f"    - Initial: {initial}")
        print()
else:
    print(f"❌ Error: {r.status_code}")
    print(r.json())

print("✅ Test complete - frontend should now display collaborators correctly")
