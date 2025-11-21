"""Quick registration test"""
import requests
import json
from datetime import datetime

print("Testing Registration Endpoint...")
print("=" * 50)

# Create test user
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
test_user = {
    "username": f"testuser_{timestamp}",
    "email": f"test_{timestamp}@example.com",
    "password": "TestPass123",
    "first_name": "Test",
    "last_name": "User",
    "role": "filmmaker"
}

print(f"\nAttempting to register: {test_user['email']}")
print("-" * 50)

try:
    response = requests.post(
        'http://localhost:5000/api/auth/register',
        json=test_user,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 201:
        data = response.json()
        print("\n✓ SUCCESS! Registration completed")
        print(f"User ID: {data.get('user', {}).get('user_id')}")
        print(f"Username: {data.get('user', {}).get('username')}")
        print(f"Email: {data.get('user', {}).get('email')}")
        print(f"Access Token: {data.get('access_token', 'N/A')[:30]}...")
        print("\n✓ User can now login and access the dashboard")
    else:
        print(f"\n✗ FAILED")
        print(f"Response: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n✗ ERROR: Cannot connect to backend")
    print("Make sure the backend server is running:")
    print("  cd backend && python app.py")
except Exception as e:
    print(f"\n✗ ERROR: {e}")

print("\n" + "=" * 50)
