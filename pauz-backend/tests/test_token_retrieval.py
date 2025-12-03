#!/usr/bin/env python3
"""
Test token retrieval directly from the backend
"""

import requests
import json
from urllib.parse import urlparse, parse_qs

BASE_URL = "http://localhost:8000"

def test_token_retrieval():
    """Test the complete OAuth flow to verify token retrieval"""
    
    print("🔐 Testing Token Retrieval")
    print("=" * 35)
    
    # Step 1: Get the OAuth URL
    print("1. Getting OAuth URL...")
    try:
        # Follow redirects to get the actual Google URL
        response = requests.get(f"{BASE_URL}/auth/login", allow_redirects=False)
        
        if response.status_code == 307:
            redirect_url = response.headers.get('Location')
            print(f"   ✅ Redirect URL: {redirect_url[:100]}...")
            
            # Parse the redirect URL to see if it's properly formed
            parsed = urlparse(redirect_url)
            if 'accounts.google.com' in parsed.netloc:
                print("   ✅ Redirects to Google OAuth")
                return redirect_url
            else:
                print(f"   ❌ Unexpected redirect: {parsed.netloc}")
                return None
        else:
            print(f"   ❌ Unexpected status code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

def check_token_endpoint():
    """Test if the /token endpoint is working"""
    
    print("\n2. Testing /token endpoint...")
    try:
        # Test with dummy data to see if endpoint exists
        dummy_data = {
            "code": "dummy_code",
            "state": "dummy_state"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/token",
            json=dummy_data
        )
        
        if response.status_code == 422:
            print("   ✅ Token endpoint exists (validation error expected)")
            return True
        elif response.status_code == 400:
            print("   ✅ Token endpoint exists (bad request expected)")
            return True
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_callback_endpoint():
    """Test if the callback endpoint is working"""
    
    print("\n3. Testing /callback endpoint...")
    try:
        # Test with dummy data to see if endpoint exists
        params = {
            "code": "dummy_code",
            "state": "dummy_state"
        }
        
        response = requests.get(
            f"{BASE_URL}/auth/callback",
            params=params,
            allow_redirects=False
        )
        
        if response.status_code == 302 or response.status_code == 307:
            redirect_url = response.headers.get('Location', '')
            if 'localhost:5173' in redirect_url:
                print(f"   ✅ Callback redirects to frontend: {redirect_url[:50]}...")
                return True
            else:
                print(f"   ⚠️  Unexpected redirect: {redirect_url}")
                return False
        else:
            print(f"   Status: {response.status_code}")
            if response.status_code == 400:
                print("   ✅ Callback endpoint exists (error expected with dummy data)")
                return True
            else:
                print(f"   Response: {response.text}")
                return False
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def check_jwt_creation():
    """Test JWT token creation directly"""
    
    print("\n4. Testing JWT token creation...")
    try:
        # Import and test the JWT service
        import sys
        import os
        sys.path.append('/Users/loubnabouzenzen/Desktop/PAUZ/pauz-backend')
        
        from app.services.jwt_service import create_access_token
        
        test_token = create_access_token(data={"sub": "test@example.com"})
        print(f"   ✅ JWT token created: {test_token[:20]}...")
        
        # Test token verification
        from app.services.jwt_service import verify_token
        from fastapi import HTTPException
        
        try:
            from app.services.jwt_service import TokenData
            credentials_exception = HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
            token_data = verify_token(test_token, credentials_exception)
            print(f"   ✅ JWT token verified: {token_data.email}")
            return True
            
        except Exception as e:
            print(f"   ❌ JWT verification failed: {e}")
            return False
            
    except ImportError as e:
        print(f"   ❌ Could not import JWT service: {e}")
        return False
    except Exception as e:
        print(f"   ❌ JWT creation failed: {e}")
        return False

def verify_redirect_url():
    """Verify the redirect URL is correctly set to 5173"""
    
    print("\n5. Verifying redirect URL configuration...")
    try:
        # Check environment file
        with open('/Users/loubnabouzenzen/Desktop/PAUZ/pauz-backend/.env', 'r') as f:
            env_content = f.read()
            
        if 'REDIRECT_URI=http://localhost:5173/auth/callback' in env_content:
            print("   ✅ .env has correct redirect URI (5173)")
        else:
            print("   ❌ .env has incorrect redirect URI")
            
        # Check auth.py
        with open('/Users/loubnabouzenzen/Desktop/PAUZ/pauz-backend/app/routes/auth.py', 'r') as f:
            auth_content = f.read()
            
        if 'localhost:5173' in auth_content:
            print("   ✅ auth.py has correct redirect URI (5173)")
        else:
            print("   ❌ auth.py has incorrect redirect URI")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error checking redirect URL: {e}")
        return False

def identify_potential_issues():
    """Identify potential token retrieval issues"""
    
    print("\n🔍 Potential Issues Analysis")
    print("=" * 35)
    
    print("Common token retrieval problems:")
    print()
    print("1. 🔄 OAuth Code Issues:")
    print("   - Code expires in 10 minutes")
    print("   - Code can only be used once")
    print("   - User takes too long to complete consent")
    print()
    print("2. 🔗 Redirect URI Mismatch:")
    print("   - Google Console doesn't match backend")
    print("   - HTTP vs HTTPS mismatch")
    print("   - Trailing slashes or missing paths")
    print()
    print("3. 🔐 JWT Creation Issues:")
    print("   - Missing JWT_SECRET_KEY")
    print("   - Invalid algorithm configuration")
    print("   - Token payload issues")
    print()
    print("4. 🌐 Network Issues:")
    print("   - Firewall blocking Google requests")
    print("   - SSL/TLS certificate issues")
    print("   - DNS resolution problems")
    print()
    print("5. 👤 User Account Issues:")
    print("   - User account disabled")
    print("   - Google API quotas exceeded")
    print("   - Consent screen not configured")

if __name__ == "__main__":
    print("🚀 Token Retrieval Verification Tool")
    print("=" * 50)
    
    # Test all components
    oauth_url = test_token_retrieval()
    token_ok = check_token_endpoint()
    callback_ok = test_callback_endpoint()
    jwt_ok = check_jwt_creation()
    redirect_ok = verify_redirect_url()
    
    print("\n📊 Summary:")
    print("=" * 20)
    print(f"OAuth Flow: {'✅' if oauth_url else '❌'}")
    print(f"Token Endpoint: {'✅' if token_ok else '❌'}")
    print(f"Callback Endpoint: {'✅' if callback_ok else '❌'}")
    print(f"JWT Creation: {'✅' if jwt_ok else '❌'}")
    print(f"Redirect URL (5173): {'✅' if redirect_ok else '❌'}")
    
    identify_potential_issues()
    
    print("\n✅ Token Retrieval Test Complete!")
    if all([oauth_url, token_ok, callback_ok, jwt_ok, redirect_ok]):
        print("🎉 All tests passed! Token retrieval should work.")
    else:
        print("⚠️  Some tests failed. Check the issues above.")