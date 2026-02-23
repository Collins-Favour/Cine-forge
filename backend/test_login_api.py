"""
Test login API endpoint
"""
import requests
import json

# API endpoint
url = "http://localhost:5000/api/auth/login"

# Login credentials
data = {
    "email": "admin@cineforge.ai",
    "password": "admin123"
}

print("=" * 70)
print("TESTING LOGIN API")
print("=" * 70)
print(f"\nEndpoint: {url}")
print(f"Email: {data['email']}")
print(f"Password: {data['password']}")
print("\n" + "=" * 70)

try:
    response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
    
    print(f"\n📡 Response Status: {response.status_code}")
    print(f"📄 Response Body:")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ LOGIN SUCCESSFUL!")
        print("=" * 70)
    else:
        print("\n❌ LOGIN FAILED!")
        print("=" * 70)
        
except requests.exceptions.ConnectionError:
    print("\n❌ CONNECTION ERROR!")
    print("   Backend server is not running or not accessible.")
    print("\n💡 Make sure the backend is running:")
    print("   cd backend")
    print("   python app.py")
    print("=" * 70)
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("=" * 70)
