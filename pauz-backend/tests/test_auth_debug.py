#!/usr/bin/env python3
"""
Debug authentication issues for Profile page
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_auth_flow():
    """Test the authentication flow"""
    
    print("🔐 Authentication Debug")
    print("=" * 30)
    
    # First, try to get the auth URL
    print("1. Getting Google Auth URL...")
    try:
        response = requests.get(f"{BASE_URL}/auth/login")
        if response.status_code == 200:
            auth_data = response.json()
            print(f"   ✅ Auth URL obtained: {auth_data.get('auth_url', 'No URL found')}")
        else:
            print(f"   ❌ Failed to get auth URL: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error getting auth URL: {e}")
    
    # Test stats endpoint without token
    print("\n2. Testing stats endpoint without token...")
    try:
        response = requests.get(f"{BASE_URL}/stats/overview")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print("   ⚠️  Unexpected response")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test stats endpoint with invalid token
    print("\n3. Testing stats endpoint with invalid token...")
    try:
        response = requests.get(
            f"{BASE_URL}/stats/overview",
            headers={"Authorization": "Bearer invalid-token-12345"}
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 401:
            print("   ✅ Correctly rejects invalid token")
        else:
            print("   ⚠️  Unexpected response")
    except Exception as e:
        print(f"   ❌ Error: {e}")

def check_frontend_auth():
    """Check what the frontend should be doing for auth"""
    
    print("\n🎨 Frontend Authentication Check")
    print("=" * 38)
    
    print("The frontend Profile.jsx should:")
    print("1. Get token from localStorage: localStorage.getItem('pauz_token')")
    print("2. Send it in Authorization header: Bearer <token>")
    print("3. Handle 401 errors appropriately")
    
    print("\n🔍 Debug steps for frontend:")
    print("1. Open browser DevTools (F12)")
    print("2. Go to Application tab > Local Storage")
    print("3. Check if 'pauz_token' exists")
    print("4. Go to Network tab")
    print("5. Try to load Profile page")
    print("6. Check the /stats/overview request")
    print("7. Check if Authorization header is present")
    
    print("\n🔧 Common auth issues:")
    print("❌ No token in localStorage")
    print("❌ Token expired")
    print("❌ Token format incorrect")
    print("❌ User not logged in")

def check_server_logs():
    """Check what server logs would show"""
    
    print("\n📋 Server Log Analysis")
    print("=" * 25)
    
    print("When you get a 500 error, check the server logs for:")
    print("1. JWT verification errors")
    print("2. Database connection issues")
    print("3. User not found in database")
    print("4. Import errors in stats routes")
    
    print("\n🧪 To check server logs:")
    print("1. Stop the current server: pkill uvicorn")
    print("2. Start with logs: uvicorn app.main:app --reload")
    print("3. Try to access Profile page")
    print("4. Watch the terminal output for errors")

def suggest_fix():
    """Suggest fixes for the auth issue"""
    
    print("\n🔨 Suggested Fix")
    print("=" * 17)
    
    print("Step 1: Check if user is logged in")
    print("- Open browser DevTools")
    print("- Check localStorage for 'pauz_token'")
    print("- If no token, login first")
    
    print("\nStep 2: If token exists but still fails")
    print("- Token might be expired")
    print("- Clear localStorage: localStorage.clear()")
    print("- Login again to get fresh token")
    
    print("\nStep 3: Check server logs")
    print("- Look for 500 errors")
    print("- Check for database issues")
    print("- Verify JWT secret is correct")
    
    print("\nStep 4: Test with fresh login")
    print("- Go to login page")
    print("- Complete Google OAuth flow")
    print("- Navigate to Profile page")

if __name__ == "__main__":
    print("🚀 Profile Auth Debug Tool")
    print("=" * 50)
    
    test_auth_flow()
    check_frontend_auth()
    check_server_logs()
    suggest_fix()
    
    print("\n✅ Auth Debug Complete!")
    print("Most likely issue: User not logged in or token expired")