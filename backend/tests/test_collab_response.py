import requests
import json

base = 'http://127.0.0.1:5000/api'

# Login as director
r = requests.post(f'{base}/auth/login', json={
    'email': 'director@test.com',
    'password': 'Test@123'
})
token = r.json()['access_token']

# Get project 2 collaborators
headers = {'Authorization': f'Bearer {token}'}
r = requests.get(f'{base}/projects/2/collaborators', headers=headers)

print('Collaborators response:')
print(json.dumps(r.json(), indent=2))
