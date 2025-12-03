#!/usr/bin/env python3
"""
Test the stats endpoint with proper authentication
"""
import os
import sys
import requests
import json
from datetime import datetime

# Add the project root to the path
sys.path.append('.')

def create_test_token():
    """Create a test JWT token for authentication"""
    try:
        from app.services.jwt_service import create_access_token
        # Create a token for a test user
        token = create_access_token(data={"sub": "test@example.com"})
        return token
    except Exception as e:
        print(f"❌ Error creating test token: {e}")
        return None

def test_stats_with_auth():
    print("🔍 Testing /stats/overview with authentication...")
    print("=" * 60)
    
    # Create a test token
    token = create_test_token()
    if not token:
        print("❌ Cannot proceed without authentication token")
        return False
    
    print(f"✅ Test token created: {token[:20]}...")
    
    # Test the endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("\n📋 Testing authenticated request...")
        response = requests.get("http://localhost:8000/stats/overview", headers=headers)
        
        print(f"   Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Success! Response data:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print(f"❌ Error response:")
            try:
                error_data = response.json()
                print(json.dumps(error_data, indent=2))
            except:
                print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure the backend is running on localhost:8000")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_stats_models():
    """Test if the models are properly imported and accessible"""
    print("\n🔍 Testing model imports...")
    print("=" * 40)
    
    try:
        from app.models import User, GuidedJournal, FreeJournal, Garden
        print("✅ All models imported successfully")
        
        # Test basic model attributes
        print(f"   User table: {User.__tablename__}")
        print(f"   GuidedJournal table: {GuidedJournal.__tablename__}")
        print(f"   FreeJournal table: {FreeJournal.__tablename__}")
        print(f"   Garden table: {Garden.__tablename__}")
        
        return True
    except Exception as e:
        print(f"❌ Model import error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print(f"🕐 Starting tests at {datetime.now().strftime('%H:%M:%S')}")
    
    # Test model imports first
    models_ok = test_stats_models()
    
    if models_ok:
        # Test the authenticated endpoint
        auth_ok = test_stats_with_auth()
        
        if auth_ok:
            print("\n🎉 All tests passed! The stats endpoint is working correctly.")
        else:
            print("\n❌ Stats endpoint test failed.")
    else:
        print("\n❌ Model tests failed. Check the model definitions.")
    
    print(f"\n🕐 Tests completed at {datetime.now().strftime('%H:%M:%S')}")