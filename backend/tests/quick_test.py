"""
Quick test for profile updates and admin portal
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

# Test 1: Admin login
print("\n" + "="*60)
print("TEST 1: Admin Login")
print("="*60)
response = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'admin@cineforge.ai',
    'password': 'Admin@123'
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    admin_token = response.json()['access_token']
    print("✓ Admin login successful")
else:
    print(f"✗ Login failed: {response.text}")
    exit(1)

# Test 2: Update profile
print("\n" + "="*60)
print("TEST 2: Update Profile")
print("="*60)
headers = {'Authorization': f'Bearer {admin_token}'}
response = requests.put(f'{BASE_URL}/users/profile', headers=headers, json={
    'first_name': 'System',
    'last_name': 'Administrator',
    'bio': 'Platform Admin - Testing'
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✓ Profile updated")
    print(f"   Name: {response.json()['user']['first_name']} {response.json()['user']['last_name']}")
else:
    print(f"✗ Update failed: {response.text}")

# Test 3: Change password (with correct current password)
print("\n" + "="*60)
print("TEST 3: Change Password")
print("="*60)
response = requests.post(f'{BASE_URL}/users/change-password', headers=headers, json={
    'current_password': 'Admin@123',
    'new_password': 'Admin@123'  # Keep same for testing
})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("✓ Password change endpoint working")
else:
    print(f"✗ Password change failed: {response.text}")

# Test 4: Admin get all users
print("\n" + "="*60)
print("TEST 4: Admin Get All Users")
print("="*60)
response = requests.get(f'{BASE_URL}/admin/users', headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    users = data.get('users', [])
    print(f"✓ Retrieved {len(users)} users (Total: {data.get('total', 0)})")
    for user in users[:5]:  # Show first 5
        print(f"   - {user['full_name']} ({user['email']}) - {user['role']}")
else:
    print(f"✗ Failed to get users: {response.text}")

# Test 5: Investor login
print("\n" + "="*60)
print("TEST 5: Investor Login and Profile Update")
print("="*60)
response = requests.post(f'{BASE_URL}/auth/login', json={
    'email': 'investor@cineforge.ai',
    'password': 'Investor@123'
})
print(f"Login Status: {response.status_code}")
if response.status_code == 200:
    investor_token = response.json()['access_token']
    print("✓ Investor login successful")
    
    # Update investor profile
    headers2 = {'Authorization': f'Bearer {investor_token}'}
    response = requests.put(f'{BASE_URL}/users/profile', headers=headers2, json={
        'first_name': 'Jane',
        'last_name': 'Investor',
        'bio': 'Film Investor - Portfolio Manager'
    })
    print(f"Update Status: {response.status_code}")
    if response.status_code == 200:
        print("✓ Investor profile updated")
    else:
        print(f"✗ Update failed: {response.text}")
else:
    print(f"✗ Login failed: {response.text}")

print("\n" + "="*60)
print("ALL TESTS COMPLETED")
print("="*60 + "\n")
