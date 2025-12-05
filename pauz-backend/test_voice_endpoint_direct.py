#!/usr/bin/env python3
"""
Direct test of the voice endpoint to see the exact error
"""

import requests
import json

def test_voice_endpoint():
    """Test the voice endpoint directly"""
    print("🎤 Testing voice endpoint directly...")
    
    url = "http://localhost:8000/freejournal/text-to-voice"
    headers = {
        "Content-Type": "application/json"
    }
    
    data = {
        "text": "This is a test of the voice system.",
        "voice_profile": "hints"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Voice endpoint working!")
            return True
        else:
            print(f"❌ Voice endpoint failed: {response.status_code}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Raw error: {response.text}")
            
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return False

def test_with_auth():
    """Test with a fake auth token to see auth error"""
    print("\n🔐 Testing with authentication...")
    
    url = "http://localhost:8000/freejournal/text-to-voice"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer fake_token_for_testing"
    }
    
    data = {
        "text": "This is a test of the voice system.",
        "voice_profile": "hints"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code
        
    except Exception as e:
        print(f"❌ Request failed: {str(e)}")
        return None

if __name__ == "__main__":
    print("🎵 Voice Endpoint Debug Test")
    print("=" * 40)
    
    # Test without auth
    test_voice_endpoint()
    
    # Test with fake auth to see auth error
    test_with_auth()