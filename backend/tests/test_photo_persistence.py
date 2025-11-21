"""
Test profile picture persistence
"""
import requests
import base64
import time

BASE_URL = 'http://localhost:5000/api'

def create_test_image():
    """Create a small test image (1x1 pixel PNG)"""
    png_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=='
    )
    return png_data

def test_persistence():
    """Test that profile picture persists across sessions"""
    print("\n" + "="*70)
    print("PROFILE PICTURE PERSISTENCE TEST")
    print("="*70)
    
    # Login
    print("\n1. Logging in as admin...")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'admin@cineforge.ai',
        'password': 'Admin@123'
    })
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return
    
    token1 = response.json()['access_token']
    headers1 = {'Authorization': f'Bearer {token1}'}
    print("✓ Login successful")
    
    # Upload photo
    print("\n2. Uploading profile photo...")
    image_data = create_test_image()
    files = {'file': ('test.png', image_data, 'image/png')}
    response = requests.post(
        f'{BASE_URL}/users/upload-avatar',
        headers=headers1,
        files=files
    )
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.text}")
        return
    
    uploaded_url = response.json()['profile_pic_url']
    print(f"✓ Photo uploaded")
    print(f"   URL: {uploaded_url[:60]}...")
    
    # Get profile immediately after upload
    print("\n3. Checking profile immediately after upload...")
    response = requests.get(f'{BASE_URL}/users/profile', headers=headers1)
    profile1 = response.json()['user']
    
    if profile1.get('profile_pic_url'):
        print(f"✓ Profile picture present")
        print(f"   URL: {profile1['profile_pic_url'][:60]}...")
        if profile1['profile_pic_url'] == uploaded_url:
            print("✓ URL matches uploaded image")
        else:
            print("❌ URL doesn't match!")
    else:
        print("❌ Profile picture not found!")
        return
    
    # Wait a moment
    print("\n4. Waiting 2 seconds...")
    time.sleep(2)
    
    # Check again with same session
    print("\n5. Checking profile with same session...")
    response = requests.get(f'{BASE_URL}/users/profile', headers=headers1)
    profile2 = response.json()['user']
    
    if profile2.get('profile_pic_url'):
        print(f"✓ Profile picture still present")
        if profile2['profile_pic_url'] == uploaded_url:
            print("✓ URL still matches")
        else:
            print("❌ URL changed!")
    else:
        print("❌ Profile picture disappeared!")
    
    # Login again (new session)
    print("\n6. Logging in again (new session)...")
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'admin@cineforge.ai',
        'password': 'Admin@123'
    })
    
    token2 = response.json()['access_token']
    headers2 = {'Authorization': f'Bearer {token2}'}
    print("✓ New session created")
    
    # Check profile with new session
    print("\n7. Checking profile with new session...")
    response = requests.get(f'{BASE_URL}/users/profile', headers=headers2)
    profile3 = response.json()['user']
    
    if profile3.get('profile_pic_url'):
        print(f"✓ Profile picture persisted across sessions")
        print(f"   URL: {profile3['profile_pic_url'][:60]}...")
        if profile3['profile_pic_url'] == uploaded_url:
            print("✓ URL matches original upload")
        else:
            print("❌ URL changed after new session!")
    else:
        print("❌ Profile picture lost after new session!")
        return
    
    # Update other profile fields
    print("\n8. Updating other profile fields...")
    response = requests.put(
        f'{BASE_URL}/users/profile',
        headers=headers2,
        json={
            'first_name': 'Test',
            'last_name': 'User',
            'bio': 'Testing profile picture persistence'
        }
    )
    
    if response.status_code == 200:
        print("✓ Profile updated")
    else:
        print(f"❌ Update failed: {response.text}")
    
    # Check if photo survived the update
    print("\n9. Checking if photo survived profile update...")
    response = requests.get(f'{BASE_URL}/users/profile', headers=headers2)
    profile4 = response.json()['user']
    
    if profile4.get('profile_pic_url'):
        print(f"✓ Profile picture survived update")
        if profile4['profile_pic_url'] == uploaded_url:
            print("✓ URL still matches")
        else:
            print("❌ URL changed after profile update!")
            print(f"   Expected: {uploaded_url[:60]}...")
            print(f"   Got: {profile4.get('profile_pic_url', 'None')[:60]}...")
    else:
        print("❌ Profile picture lost after update!")
        print("   This is the problem - profile_pic_url not included in update")
    
    print("\n" + "="*70)
    print("PERSISTENCE TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == '__main__':
    try:
        test_persistence()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
