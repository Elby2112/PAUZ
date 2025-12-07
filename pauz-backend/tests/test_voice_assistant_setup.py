"""
Test script for voice assistant endpoints
Run this to verify your voice assistant setup is working
"""

import requests
import base64
import json

API_BASE = "http://localhost:8000"

def get_auth_token():
    """Get auth token - you'll need to update this with your actual login"""
    # First, login to get a token
    login_data = {
        "email": "test@example.com",  # Update with your test email
        "password": "testpassword"    # Update with your test password
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            print("✅ Authentication successful")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {str(e)}")
        return None

def test_welcome_endpoint(token):
    """Test the welcome endpoint"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{API_BASE}/voice-assistant/welcome-simple", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Welcome endpoint working")
            print(f"   Welcome text: {result['text'][:100]}...")
            print(f"   Audio data length: {len(result.get('audio_data', ''))}")
            return True
        else:
            print(f"❌ Welcome endpoint failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Welcome endpoint error: {str(e)}")
        return False

def test_user_context(token):
    """Test the user context endpoint"""
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(f"{API_BASE}/voice-assistant/user-context", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ User context endpoint working")
            print(f"   Total journals: {result.get('total_journals', 0)}")
            print(f"   Is returning user: {result.get('is_returning_user', False)}")
            return True
        else:
            print(f"❌ User context failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ User context error: {str(e)}")
        return False

def test_voice_to_voice_flow():
    """Test the complete voice-to-voice flow with a dummy audio file"""
    print("\n🎤 Testing voice-to-voice flow...")
    print("   (This requires actual audio data, skipping in basic test)")
    print("   To test manually:")
    print("   1. Start your frontend app")
    print("   2. Click the 🎤 Need Help? button")
    print("   3. You should hear a welcome message")
    print("   4. Then try speaking a question")

def main():
    print("🧪 Testing Voice Assistant Setup")
    print("=" * 40)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    print(f"🔑 Got auth token: {token[:20]}...")
    
    # Test endpoints
    tests = [
        ("Welcome Endpoint", lambda: test_welcome_endpoint(token)),
        ("User Context", lambda: test_user_context(token)),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        results.append(test_func())
    
    # Voice-to-voice flow test (manual)
    test_voice_to_voice_flow()
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary:")
    passed = sum(results)
    total = len(results)
    print(f"   Passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All basic tests passed! Your voice assistant should work.")
        print("\n🎉 Next steps:")
        print("   1. Make sure your ELEVENLABS_API_KEY is set")
        print("   2. Start your frontend application")
        print("   3. Click the 🎤 Need Help? button")
        print("   4. Enjoy your voice assistant!")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()