#!/usr/bin/env python3
"""
Test the actual running backend's JWT functionality
"""

import requests
import os
import sys

def test_backend_health():
    """Test if the backend is responding"""
    
    print("🏥 Backend Health Check")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8000/")
        if response.status_code == 200:
            print("   ✅ Backend is responding")
            return True
        else:
            print(f"   ❌ Backend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Backend not reachable: {e}")
        return False

def test_me_endpoint_without_token():
    """Test /me endpoint without token to see auth behavior"""
    
    print("\n🔐 Testing /me endpoint without token...")
    try:
        response = requests.get("http://localhost:8000/auth/me")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
            return True
        elif response.status_code == 403:
            print("   ✅ Correctly requires authentication")
            return True
        else:
            print(f"   Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_me_endpoint_with_invalid_token():
    """Test /me endpoint with invalid token"""
    
    print("\n🔐 Testing /me endpoint with invalid token...")
    try:
        headers = {"Authorization": "Bearer invalid-token-12345"}
        response = requests.get("http://localhost:8000/auth/me", headers=headers)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly rejects invalid token")
            return True
        elif response.status_code == 403:
            print("   ✅ Correctly rejects invalid token")
            return True
        else:
            print(f"   Response: {response.text[:100]}...")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_stats_endpoint():
    """Test stats endpoint to see if it has auth issues"""
    
    print("\n📊 Testing /stats/overview endpoint...")
    try:
        response = requests.get("http://localhost:8000/stats/overview")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        elif response.status_code == 500:
            print("   ⚠️  Server error - possible token issue")
            print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   Response: {response.text[:100]}...")
            
        return response.status_code
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def check_environment_in_server():
    """Check if server has proper environment variables"""
    
    print("\n🌍 Checking server environment...")
    
    # Create a simple endpoint test
    print("   (Cannot directly check server env, but we can infer from behavior)")
    
    # If the server is running and OAuth works, env vars should be loaded
    oauth_response = requests.get("http://localhost:8000/auth/login", allow_redirects=False)
    if oauth_response.status_code == 307:
        print("   ✅ Server likely has proper environment variables")
        return True
    else:
        print("   ❌ Server may have environment issues")
        return False

def simulate_token_creation():
    """Simulate what the server does for token creation"""
    
    print("\n🔑 Simulating token creation...")
    
    # Load environment like the server would
    try:
        from dotenv import load_dotenv
        load_dotenv('/Users/loubnabouzenzen/Desktop/PAUZ/pauz-backend/.env')
        
        # Check if we can access the same variables
        jwt_secret = os.getenv("JWT_SECRET_KEY")
        jwt_algorithm = os.getenv("JWT_ALGORITHM")
        
        print(f"   JWT_SECRET_KEY: {'✅ Set' if jwt_secret else '❌ Missing'}")
        print(f"   JWT_ALGORITHM: {jwt_algorithm or '❌ Missing'}")
        
        if jwt_secret:
            try:
                from jose import jwt
                from datetime import datetime, timedelta
                
                # Create a test token like the server does
                to_encode = {"sub": "test@example.com"}
                expire = datetime.utcnow() + timedelta(hours=24)
                to_encode.update({"exp": expire})
                test_token = jwt.encode(to_encode, jwt_secret, algorithm=jwt_algorithm or "HS256")
                
                print(f"   ✅ Token created: {test_token[:20]}...")
                
                # Test decoding
                try:
                    payload = jwt.decode(test_token, jwt_secret, algorithms=[jwt_algorithm or "HS256"])
                    print(f"   ✅ Token decoded: {payload.get('sub')}")
                    return True
                except Exception as decode_error:
                    print(f"   ❌ Token decode failed: {decode_error}")
                    return False
                    
            except ImportError:
                print("   ❌ jose library not available")
                return False
            except Exception as e:
                print(f"   ❌ Token creation failed: {e}")
                return False
        else:
            return False
            
    except Exception as e:
        print(f"   ❌ Environment loading failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Backend Token Issues Diagnosis")
    print("=" * 50)
    
    # Run tests
    health_ok = test_backend_health()
    auth_no_token = test_me_endpoint_without_token()
    auth_bad_token = test_me_endpoint_with_invalid_token()
    stats_status = test_stats_endpoint()
    env_ok = check_environment_in_server()
    token_ok = simulate_token_creation()
    
    print("\n📊 Diagnosis Results:")
    print("=" * 25)
    print(f"Backend Health: {'✅' if health_ok else '❌'}")
    print(f"Auth Required: {'✅' if auth_no_token else '❌'}")
    print(f"Bad Token Rejected: {'✅' if auth_bad_token else '❌'}")
    print(f"Environment OK: {'✅' if env_ok else '❌'}")
    print(f"Token Creation: {'✅' if token_ok else '❌'}")
    
    if stats_status == 500:
        print("Stats Endpoint: ⚠️  (500 error)")
    elif stats_status == 401:
        print("Stats Endpoint: ✅ (requires auth)")
    else:
        print(f"Stats Endpoint: ⚠️  ({stats_status})")
    
    print("\n🔍 Key Findings:")
    
    if token_ok and env_ok:
        print("✅ JWT token creation should work fine")
        print("❌ The issue might be in the OAuth flow itself")
        print("   - Authorization code might be expired")
        print("   - User might be taking too long to complete consent")
        print("   - Google OAuth configuration might have issues")
    elif not token_ok:
        print("❌ JWT token creation has issues")
        print("   - Check environment variables")
        print("   - Check JWT library installation")
    else:
        print("⚠️  Mixed results - need further investigation")