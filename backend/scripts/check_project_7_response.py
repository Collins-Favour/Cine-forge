import requests

base = 'http://127.0.0.1:5000/api'

# Login
r = requests.post(f'{base}/auth/login', json={'email': 'test@gmail.com', 'password': 'Test@123'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

# Get project 7
r = requests.get(f'{base}/projects/7', headers=headers)
print("GET /api/projects/7")
print(f"Status: {r.status_code}\n")

if r.status_code == 200:
    import json
    data = r.json()
    print(json.dumps(data, indent=2))
else:
    print(f"Error: {r.json()}")
