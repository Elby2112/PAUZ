#!/usr/bin/env python3
"""
Test script to debug the stats endpoint issue
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_endpoint_without_auth():
    """Test endpoint without authentication to see basic response"""
    
    print("🧪 Testing Stats Endpoint Without Auth")
    print("=" * 45)
    
    # Test the root endpoint first
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}")
        return
    
    # Test individual endpoints
    endpoints = [
        "/stats/guided_journals/total",
        "/stats/free_journals/total", 
        "/stats/journals/total",
        "/stats/garden/total",
        "/stats/overview"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}")
            print(f"📍 {endpoint}: {response.status_code}")
            
            if response.status_code != 401:
                print(f"   Response: {response.text}")
            else:
                print(f"   ✅ Correctly requires authentication")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_with_fake_token():
    """Test with a fake token to see if it triggers the 500 error"""
    
    print("\n🧪 Testing With Fake Token")
    print("=" * 30)
    
    fake_token = "fake.jwt.token"
    headers = {"Authorization": f"Bearer {fake_token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/stats/overview", headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 500:
            print("❌ 500 Error confirmed - backend issue")
        elif response.status_code == 401:
            print("✅ Correctly rejected fake token")
        else:
            print(f"❓ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")

def check_database_connection():
    """Check if we can connect to the database"""
    
    print("\n🗄️  Checking Database Connection")
    print("=" * 35)
    
    try:
        # Try to create a user via auth to test DB connection
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ Backend is running and responding")
        
        # Check if there are any database files
        import os
        db_files = []
        for file in os.listdir('.'):
            if file.endswith('.db'):
                db_files.append(file)
        
        if db_files:
            print(f"✅ Found database files: {db_files}")
        else:
            print("❌ No database files found")
            
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def suggest_fixes():
    """Suggest possible fixes"""
    
    print("\n🔧 Suggested Fixes")
    print("=" * 20)
    print("1. Check if backend server is running: uvicorn app.main:app --reload")
    print("2. Check if JWT_SECRET_KEY environment variable is set")
    print("3. Check if database tables exist and are properly created")
    print("4. Check Garden model imports in stats.py")
    print("5. Check if user is properly authenticated in the frontend")
    print("6. Check browser console for detailed error messages")

if __name__ == "__main__":
    print("🚀 Stats Endpoint Debug Tool")
    print("=" * 50)
    
    test_endpoint_without_auth()
    test_with_fake_token()
    check_database_connection()
    suggest_fixes()
    
    print("\n📋 Next Steps:")
    print("1. Run this script to identify the exact issue")
    print("2. Check backend logs for detailed error messages")
    print("3. Make sure user is logged in with a valid token")
    print("4. Verify database tables are created")