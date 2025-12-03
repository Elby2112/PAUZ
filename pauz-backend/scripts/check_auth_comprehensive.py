#!/usr/bin/env python3
"""
Comprehensive authentication check for PAUZ backend
"""

import requests
import json
import time
import sys
from urllib.parse import parse_qs, urlparse

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test if the server is running"""
    print("🔍 Testing server health...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("   ✅ Server is running")
            return True
        else:
            print(f"   ❌ Server returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server not accessible: {e}")
        return False

def test_oauth_login_redirect():
    """Test OAuth login redirect"""
    print("\n🔐 Testing OAuth login endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/auth/login", allow_redirects=False)
        if response.status_code in [302, 307]:
            location = response.headers.get('Location', '')
            if 'accounts.google.com' in location:
                print("   ✅ Correctly redirects to Google OAuth")
                # Extract state from URL
                parsed = urlparse(location)
                params = parse_qs(parsed.query)
                state = params.get('state', [None])[0]
                print(f"   🔑 OAuth state generated: {state}")
                return state
            else:
                print(f"   ❌ Redirecting to unexpected URL: {location}")
                return None
        else:
            print(f"   ❌ Expected redirect, got {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error testing login: {e}")
        return None

def test_protected_endpoints():
    """Test protected endpoints without authentication"""
    print("\n🛡️  Testing protected endpoints...")
    
    endpoints = [
        ("/auth/me", "User profile"),
        ("/stats/overview", "User stats"),
        ("/guided_journal/", "Guided journals"),
        ("/freejournal/", "Free journals"),
        ("/garden/", "Garden entries")
    ]
    
    all_protected = True
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            if response.status_code == 401:
                print(f"   ✅ {description} - properly protected")
            elif response.status_code == 403:
                print(f"   ✅ {description} - requires authentication")
            else:
                print(f"   ⚠️  {description} - unexpected status: {response.status_code}")
                all_protected = False
        except Exception as e:
            print(f"   ❌ {description} - error: {e}")
            all_protected = False
    
    return all_protected

def test_invalid_token():
    """Test with invalid JWT token"""
    print("\n🚫 Testing invalid token handling...")
    
    invalid_token = "invalid.jwt.token"
    headers = {"Authorization": f"Bearer {invalid_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 401:
            print("   ✅ Invalid token correctly rejected")
            return True
        else:
            print(f"   ❌ Expected 401, got {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing invalid token: {e}")
        return False

def test_token_endpoint():
    """Test the token endpoint (if it exists)"""
    print("\n🔑 Testing token endpoint...")
    
    try:
        # This should fail without proper OAuth code
        response = requests.post(
            f"{BASE_URL}/auth/token",
            json={"code": "fake_code", "state": "fake_state"}
        )
        if response.status_code in [400, 401]:
            print("   ✅ Token endpoint properly rejects fake credentials")
            return True
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ Error testing token endpoint: {e}")
        return False

def test_cors():
    """Test CORS configuration"""
    print("\n🌐 Testing CORS configuration...")
    
    headers = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
        "Access-Control-Request-Headers": "authorization"
    }
    
    try:
        response = requests.options(f"{BASE_URL}/auth/me", headers=headers)
        
        cors_headers = {
            'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
            'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
            'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers'),
            'Access-Control-Allow-Credentials': response.headers.get('Access-Control-Allow-Credentials')
        }
        
        print("   CORS Headers:")
        for header, value in cors_headers.items():
            if value:
                print(f"     ✅ {header}: {value}")
            else:
                print(f"     ⚠️  {header}: Not set")
        
        return True
    except Exception as e:
        print(f"   ❌ Error testing CORS: {e}")
        return False

def check_environment():
    """Check environment configuration"""
    print("\n⚙️  Checking environment configuration...")
    
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    required_vars = [
        'GOOGLE_CLIENT_ID',
        'GOOGLE_CLIENT_SECRET', 
        'REDIRECT_URI',
        'JWT_SECRET_KEY'
    ]
    
    all_present = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Don't print secrets, just confirm they exist
            if 'SECRET' in var:
                print(f"   ✅ {var}: Set (length: {len(value)})")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: Not set")
            all_present = False
    
    return all_present

def main():
    """Run all authentication checks"""
    print("🚀 PAUZ Backend Authentication Check")
    print("=" * 50)
    
    results = []
    
    # Basic health check
    results.append(("Server Health", test_health_check()))
    
    if results[-1][1]:  # Only continue if server is running
        results.append(("OAuth Login", test_oauth_login_redirect() is not None))
        results.append(("Protected Endpoints", test_protected_endpoints()))
        results.append(("Invalid Token Handling", test_invalid_token()))
        results.append(("Token Endpoint", test_token_endpoint()))
        results.append(("CORS Configuration", test_cors()))
        results.append(("Environment Config", check_environment()))
    
    # Summary
    print("\n📊 SUMMARY")
    print("=" * 20)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nScore: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All authentication tests passed!")
        print("The authentication system appears to be working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
        print("Please check the failed items above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)