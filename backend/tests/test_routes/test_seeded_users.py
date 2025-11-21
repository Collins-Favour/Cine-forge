"""Test Admin and Investor Login"""
import requests
import json

print("=" * 60)
print("Testing Admin and Investor Login")
print("=" * 60)

# Test Admin Login
print("\n1. Testing ADMIN login...")
print("-" * 60)
try:
    response = requests.post(
        'http://localhost:5000/api/auth/login',
        json={
            'email': 'admin@cineforge.ai',
            'password': 'Admin@123'
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Admin login successful!")
        print(f"  User ID: {data['user']['user_id']}")
        print(f"  Username: {data['user']['username']}")
        print(f"  Role: {data['user']['role']}")
        print(f"  Token: {data['access_token'][:30]}...")
    else:
        print(f"✗ Admin login failed: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

# Test Investor Login
print("\n2. Testing INVESTOR login...")
print("-" * 60)
try:
    response = requests.post(
        'http://localhost:5000/api/auth/login',
        json={
            'email': 'investor@cineforge.ai',
            'password': 'Investor@123'
        },
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Investor login successful!")
        print(f"  User ID: {data['user']['user_id']}")
        print(f"  Username: {data['user']['username']}")
        print(f"  Role: {data['user']['role']}")
        print(f"  Token: {data['access_token'][:30]}...")
    else:
        print(f"✗ Investor login failed: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("Testing Complete!")
print("=" * 60)
print("\nYou can now login with these credentials:")
print("  Admin: admin@cineforge.ai / Admin@123")
print("  Investor: investor@cineforge.ai / Investor@123")
print("\n" + "=" * 60)
