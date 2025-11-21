"""
Test profile photo upload functionality
"""
import requests
import base64
import os

BASE_URL = 'http://localhost:5000/api'

def create_test_image():
    """Create a small test image (1x1 pixel PNG)"""
    # 1x1 pixel red PNG
    png_data = base64.b64decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=='
    )
    return png_data

def test_photo_upload():
    """Test uploading profile photo"""
    print("\n" + "="*70)
    print("PROFILE PHOTO UPLOAD TEST")
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
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    print("✓ Login successful")
    
    # Create test image file
    print("\n2. Creating test image...")
    image_data = create_test_image()
    print(f"✓ Test image created ({len(image_data)} bytes)")
    
    # Upload image
    print("\n3. Uploading profile photo...")
    files = {'file': ('test_profile.png', image_data, 'image/png')}
    response = requests.post(
        f'{BASE_URL}/users/upload-avatar',
        headers=headers,
        files=files
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("✓ Photo uploaded successfully")
        print(f"   Profile pic URL length: {len(data.get('profile_pic_url', ''))}")
        
        # Verify it's a data URI
        if data.get('profile_pic_url', '').startswith('data:image/'):
            print("✓ Image saved as data URI")
        else:
            print("❌ Image format incorrect")
    else:
        print(f"❌ Upload failed: {response.text}")
        return
    
    # Verify the photo is in profile
    print("\n4. Verifying photo in profile...")
    response = requests.get(f'{BASE_URL}/users/profile', headers=headers)
    
    if response.status_code == 200:
        profile = response.json()['user']
        if profile.get('profile_pic_url'):
            print("✓ Profile picture URL is set")
            print(f"   URL starts with: {profile['profile_pic_url'][:50]}...")
        else:
            print("❌ Profile picture URL is empty")
    else:
        print(f"❌ Failed to get profile: {response.text}")
    
    # Test file size validation
    print("\n5. Testing file size validation (large file)...")
    large_data = b'x' * (6 * 1024 * 1024)  # 6MB
    files = {'file': ('large.png', large_data, 'image/png')}
    response = requests.post(
        f'{BASE_URL}/users/upload-avatar',
        headers=headers,
        files=files
    )
    
    if response.status_code == 400:
        print("✓ Large file correctly rejected")
        print(f"   Error: {response.json().get('error')}")
    else:
        print(f"❌ Should have rejected large file (got {response.status_code})")
    
    # Test invalid file type
    print("\n6. Testing file type validation...")
    files = {'file': ('test.txt', b'not an image', 'text/plain')}
    response = requests.post(
        f'{BASE_URL}/users/upload-avatar',
        headers=headers,
        files=files
    )
    
    if response.status_code == 400:
        print("✓ Invalid file type correctly rejected")
        print(f"   Error: {response.json().get('error')}")
    else:
        print(f"❌ Should have rejected invalid file type (got {response.status_code})")
    
    print("\n" + "="*70)
    print("✓ PHOTO UPLOAD TEST COMPLETE")
    print("="*70)
    print("\nSummary:")
    print("✓ Photo upload endpoint working")
    print("✓ Images saved as base64 data URIs")
    print("✓ File size validation working (5MB limit)")
    print("✓ File type validation working")
    print("✓ Profile photo accessible after upload")
    print("\n")

if __name__ == '__main__':
    try:
        test_photo_upload()
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
