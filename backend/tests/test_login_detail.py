import requests
import json

base = 'http://127.0.0.1:5000/api'

# Test investor login to see full response
print('Testing investor login with full response...\n')
r = requests.post(f'{base}/auth/login', json={
    'email': 'investor@test.com',
    'password': 'Test@123'
})

print(f'Status: {r.status_code}')
print(f'\nFull Response:')
print(json.dumps(r.json(), indent=2))
