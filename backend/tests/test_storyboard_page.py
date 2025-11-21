import requests

base = 'http://127.0.0.1:5000/api'

print("=== TESTING STORYBOARD PAGE ENDPOINTS ===\n")

# Login
r = requests.post(f'{base}/auth/login', json={'email': 'test@gmail.com', 'password': 'Test@123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Test storyboards endpoint
print("GET /api/storyboards/project/7")
r = requests.get(f'{base}/storyboards/project/7', headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"✅ Panels: {data.get('total', 0)}")
    print(f"   Response structure: {list(data.keys())}")
else:
    print(f"❌ Error: {r.json()}")

print("\n✅ Storyboard page should now load correctly")
