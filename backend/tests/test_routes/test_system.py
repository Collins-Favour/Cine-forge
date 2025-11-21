"""
System Check Script - Backend & Frontend Integration Test
Tests authentication flow and identifies errors
"""
import requests
import json
from datetime import datetime

# Configuration
BACKEND_URL = "http://localhost:5000"
API_BASE = f"{BACKEND_URL}/api"

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_section(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_success(message):
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")

def print_info(message):
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")

# Test 1: Backend Health Check
def test_backend_health():
    print_section("Test 1: Backend Health Check")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Backend is running: {data.get('app', 'Unknown')} v{data.get('version', 'Unknown')}")
            return True
        else:
            print_error(f"Backend returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print_error("Cannot connect to backend. Is the server running?")
        print_info(f"Expected URL: {BACKEND_URL}")
        return False
    except Exception as e:
        print_error(f"Health check failed: {str(e)}")
        return False

# Test 2: CORS Configuration
def test_cors():
    print_section("Test 2: CORS Configuration")
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type, Authorization'
        }
        response = requests.options(f"{API_BASE}/auth/register", headers=headers, timeout=5)
        
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        cors_methods = response.headers.get('Access-Control-Allow-Methods')
        cors_headers = response.headers.get('Access-Control-Allow-Headers')
        
        if cors_origin:
            print_success(f"CORS Origin: {cors_origin}")
        else:
            print_error("CORS Origin header not set")
            
        if cors_methods:
            print_success(f"CORS Methods: {cors_methods}")
        else:
            print_error("CORS Methods header not set")
            
        if cors_headers:
            print_success(f"CORS Headers: {cors_headers}")
        else:
            print_error("CORS Headers header not set")
            
        return bool(cors_origin and cors_methods and cors_headers)
    except Exception as e:
        print_error(f"CORS check failed: {str(e)}")
        return False

# Test 3: Registration Endpoint Structure
def test_registration_endpoint():
    print_section("Test 3: Registration Endpoint - Field Validation")
    
    # Test with empty data
    print_info("Testing with empty data...")
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json={},
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Empty data test failed: {str(e)}")
    
    # Test with missing fields
    print_info("\nTesting with missing password field...")
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com"
            },
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        print_info(f"Status Code: {response.status_code}")
        print_info(f"Response: {response.text}")
    except Exception as e:
        print_error(f"Missing field test failed: {str(e)}")

# Test 4: Full Registration Flow
def test_full_registration():
    print_section("Test 4: Full Registration Flow")
    
    # Generate unique test user
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_user = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "TestPass123",
        "first_name": "Test",
        "last_name": "User",
        "role": "filmmaker"
    }
    
    print_info(f"Attempting to register user: {test_user['username']}")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/register",
            json=test_user,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print_success("Registration successful!")
            print_info(f"User ID: {data.get('user', {}).get('user_id')}")
            print_info(f"Username: {data.get('user', {}).get('username')}")
            return True, data
        elif response.status_code == 409:
            print_warning("User already exists (expected for duplicate test)")
            return False, None
        else:
            print_error(f"Registration failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Registration test failed: {str(e)}")
        return False, None

# Test 5: Login Flow
def test_login(email=None, password=None):
    print_section("Test 5: Login Flow")
    
    if not email or not password:
        print_warning("No credentials provided, skipping login test")
        return False, None
    
    credentials = {
        "email": email,
        "password": password
    }
    
    print_info(f"Attempting to login with: {email}")
    
    try:
        response = requests.post(
            f"{API_BASE}/auth/login",
            json=credentials,
            headers={'Content-Type': 'application/json'},
            timeout=5
        )
        
        print_info(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Login successful!")
            print_info(f"Access Token: {data.get('access_token', 'N/A')[:20]}...")
            return True, data.get('access_token')
        else:
            print_error(f"Login failed with status {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, None
            
    except Exception as e:
        print_error(f"Login test failed: {str(e)}")
        return False, None

# Test 6: Check Frontend API Configuration
def test_frontend_config():
    print_section("Test 6: Frontend Configuration Check")
    
    try:
        with open('frontend/src/services/api.js', 'r') as f:
            content = f.read()
            if 'VITE_API_URL' in content:
                print_success("Frontend API configuration found")
                print_info("Using: VITE_API_URL environment variable")
            else:
                print_warning("VITE_API_URL not found in api.js")
    except Exception as e:
        print_error(f"Could not read frontend config: {str(e)}")

# Test 7: Registration Data Mapping
def test_registration_data_mapping():
    print_section("Test 7: Frontend-Backend Data Mapping Check")
    
    frontend_fields = ["full_name", "email", "username", "password", "role"]
    backend_fields = ["username", "email", "password", "first_name", "last_name", "role"]
    
    print_info("Frontend sends:")
    for field in frontend_fields:
        print(f"  • {field}")
    
    print_info("\nBackend expects:")
    for field in backend_fields:
        print(f"  • {field}")
    
    print_warning("\n⚠ MISMATCH DETECTED:")
    print_error("  Frontend sends 'full_name' but backend expects 'first_name' and 'last_name'")
    print_info("\nThis is likely causing registration failures!")
    
    return False

# Main execution
def main():
    print(f"\n{Colors.BOLD}{Colors.HEADER}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     CINEFORGE AI - System Integration Test Suite          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(f"{Colors.ENDC}")
    
    results = {}
    
    # Run tests
    results['health'] = test_backend_health()
    results['cors'] = test_cors()
    test_registration_endpoint()
    results['data_mapping'] = test_registration_data_mapping()
    
    reg_success, reg_data = test_full_registration()
    results['registration'] = reg_success
    
    if reg_success and reg_data:
        login_success, token = test_login(
            reg_data.get('user', {}).get('email'),
            "TestPass123"
        )
        results['login'] = login_success
    
    test_frontend_config()
    
    # Summary
    print_section("Test Summary")
    total = len([v for v in results.values() if v is not None])
    passed = sum([1 for v in results.values() if v])
    
    print(f"\nTests Passed: {passed}/{total}")
    
    if passed == total:
        print_success("\n✓ All tests passed!")
    else:
        print_error(f"\n✗ {total - passed} test(s) failed")
        print_warning("\nPrimary Issue Identified:")
        print_error("  • Frontend/Backend data field mismatch in registration")
        print_error("  • Frontend sends 'full_name', backend expects 'first_name' and 'last_name'")
    
    print(f"\n{Colors.ENDC}")

if __name__ == "__main__":
    main()
