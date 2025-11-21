"""
Test profile update functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json

BASE_URL = 'http://localhost:5000'

def login_as_user(email, password):
    """Login and get access token"""
    response = requests.post(f'{BASE_URL}/api/auth/login', json={
        'email': email,
        'password': password
    })
    
    if response.status_code == 200:
        data = response.json()
        return data.get('access_token')
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_profile_update():
    """Test updating user profile"""
    print("\n" + "="*60)
    print("Testing Profile Update Functionality")
    print("="*60)
    
    # Login as admin
    print("\n1. Logging in as admin...")
    token = login_as_user('admin@cineforge.ai', 'Admin@123')
    
    if not token:
        print("❌ Failed to login")
        return
    
    print("✓ Login successful")
    
    # Get current profile
    print("\n2. Getting current profile...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/api/users/profile', headers=headers)
    
    if response.status_code == 200:
        profile = response.json()['user']
        print(f"✓ Current profile:")
        print(f"   Name: {profile.get('first_name')} {profile.get('last_name')}")
        print(f"   Email: {profile.get('email')}")
        print(f"   Bio: {profile.get('bio', 'N/A')}")
    else:
        print(f"❌ Failed to get profile: {response.text}")
        return
    
    # Update profile
    print("\n3. Updating profile...")
    update_data = {
        'first_name': 'Super',
        'last_name': 'Admin',
        'bio': 'System Administrator - Updated ' + str(os.urandom(4).hex())
    }
    
    response = requests.put(
        f'{BASE_URL}/api/users/profile',
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        updated = response.json()['user']
        print(f"✓ Profile updated successfully:")
        print(f"   Name: {updated.get('first_name')} {updated.get('last_name')}")
        print(f"   Bio: {updated.get('bio')}")
    else:
        print(f"❌ Failed to update profile: {response.text}")
        return
    
    # Verify update
    print("\n4. Verifying update...")
    response = requests.get(f'{BASE_URL}/api/users/profile', headers=headers)
    
    if response.status_code == 200:
        profile = response.json()['user']
        if (profile.get('first_name') == update_data['first_name'] and 
            profile.get('last_name') == update_data['last_name']):
            print("✓ Profile update verified successfully")
        else:
            print("❌ Profile data mismatch after update")
    else:
        print(f"❌ Failed to verify: {response.text}")

def test_password_change():
    """Test changing password"""
    print("\n" + "="*60)
    print("Testing Password Change Functionality")
    print("="*60)
    
    # Login as investor
    print("\n1. Logging in as investor...")
    token = login_as_user('investor@cineforge.ai', 'Investor@123')
    
    if not token:
        print("❌ Failed to login")
        return
    
    print("✓ Login successful")
    
    # Test with wrong current password
    print("\n2. Testing with wrong current password...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(
        f'{BASE_URL}/api/users/change-password',
        headers=headers,
        json={
            'current_password': 'WrongPassword',
            'new_password': 'NewPassword123'
        }
    )
    
    if response.status_code == 401:
        print("✓ Correctly rejected wrong password")
    else:
        print(f"❌ Should have rejected wrong password: {response.text}")
    
    # Test with correct password (but don't actually change it)
    print("\n3. Testing password validation...")
    response = requests.post(
        f'{BASE_URL}/api/users/change-password',
        headers=headers,
        json={
            'current_password': 'Investor@123',
            'new_password': 'Investor@123'  # Same password
        }
    )
    
    if response.status_code == 200:
        print("✓ Password change endpoint is working")
    else:
        print(f"❌ Password change failed: {response.text}")

def test_admin_user_list():
    """Test admin can see all users"""
    print("\n" + "="*60)
    print("Testing Admin User List")
    print("="*60)
    
    # Login as admin
    print("\n1. Logging in as admin...")
    token = login_as_user('admin@cineforge.ai', 'Admin@123')
    
    if not token:
        print("❌ Failed to login")
        return
    
    print("✓ Login successful")
    
    # Get user list
    print("\n2. Fetching all users...")
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(f'{BASE_URL}/api/admin/users', headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        users = data.get('users', [])
        total = data.get('total', 0)
        
        print(f"✓ Retrieved {len(users)} users (Total: {total})")
        print("\n   User List:")
        for user in users:
            print(f"   - {user.get('full_name')} ({user.get('email')}) - Role: {user.get('role')}")
    else:
        print(f"❌ Failed to get users: {response.text}")

if __name__ == '__main__':
    print("\n" + "="*60)
    print("PROFILE & ADMIN PORTAL TEST SUITE")
    print("="*60)
    
    try:
        test_profile_update()
        test_password_change()
        test_admin_user_list()
        
        print("\n" + "="*60)
        print("✓ ALL TESTS COMPLETED")
        print("="*60 + "\n")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
