#!/usr/bin/env python3
"""
Test script for Voice Hints feature
Tests the new voice endpoints and ElevenLabs integration
"""

import os
import sys
import json
import requests
import base64
from io import BytesIO

# Configuration
BASE_URL = "http://localhost:8000"  # Adjust if your backend runs on different port
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

def test_text_to_voice_endpoint():
    """Test the generic text-to-voice endpoint"""
    print("🎤 Testing text-to-voice endpoint...")
    
    test_text = "Hello! This is a test of the voice hint system. How does this sound?"
    
    url = f"{BASE_URL}/free-journal/text-to-voice"
    headers = {
        "Content-Type": "application/json",
        # You'll need to add authorization headers here if your app requires auth
    }
    
    data = {
        "text": test_text,
        "voice_profile": "hints"
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Text-to-voice endpoint working!")
            
            # Save the audio file
            if result.get("success") and result.get("audio_data"):
                audio_data = base64.b64decode(result["audio_data"])
                
                os.makedirs("test_audio_output", exist_ok=True)
                with open("test_audio_output/test_voice.mp3", "wb") as f:
                    f.write(audio_data)
                
                print("💾 Test audio saved as 'test_audio_output/test_voice.mp3'")
                print(f"📊 Audio size: {len(audio_data)} bytes")
                print(f"🎵 Content type: {result.get('content_type')}")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return False

def test_available_voices_endpoint():
    """Test the available voices endpoint"""
    print("\n🎭 Testing available voices endpoint...")
    
    url = f"{BASE_URL}/free-journal/voices/available"
    headers = {
        "Content-Type": "application/json",
        # Add auth headers if needed
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            voices = result.get("voices", [])
            
            print(f"✅ Found {len(voices)} available voices!")
            
            # Show first few voices
            for i, voice in enumerate(voices[:5]):
                print(f"  {i+1}. {voice.get('name', 'Unknown')} ({voice.get('voice_id', 'Unknown')})")
            
            return True
        else:
            print(f"❌ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error occurred: {str(e)}")
        return False

def test_voice_service_directly():
    """Test the voice service directly without API"""
    print("\n🔧 Testing voice service directly...")
    
    try:
        # Import the voice service
        sys.path.append('app')
        from services.voice_service import voice_service
        
        if not voice_service.is_available():
            print("❌ Voice service not available - check ELEVENLABS_API_KEY")
            return False
        
        print("✅ Voice service is available!")
        
        # Test text-to-speech
        test_text = "This is a direct test of the voice service. Your hints can now be read aloud!"
        
        result = voice_service.text_to_speech(test_text, voice_profile="hints")
        
        if result.get("success"):
            print("✅ Direct voice service test successful!")
            
            # Save audio
            voice_service.save_audio_to_file(result["audio_data"], "direct_test.mp3")
            
            return True
        else:
            print(f"❌ Voice service failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Direct test error: {str(e)}")
        return False

def main():
    print("🎵 Voice Hints Feature Test Suite")
    print("=" * 50)
    
    # Check if API key is set
    if not ELEVENLABS_API_KEY:
        print("⚠️  ELEVENLABS_API_KEY not set in environment variables")
        print("   Some tests may fail without a valid API key")
        response = input("Continue anyway? (y/n): ").lower().strip()
        if response != 'y':
            return
    
    # Run tests
    print("\n🧪 Running tests...")
    
    # Test 1: Direct voice service
    test1_passed = test_voice_service_directly()
    
    # Test 2: Available voices (doesn't require API key)
    test2_passed = test_available_voices_endpoint()
    
    # Test 3: Text-to-voice endpoint
    test3_passed = test_text_to_voice_endpoint()
    
    # Summary
    print("\n📊 Test Results:")
    print(f"  Direct voice service: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"  Available voices API: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"  Text-to-voice API: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    all_passed = test1_passed and test2_passed and test3_passed
    
    if all_passed:
        print("\n🎉 All tests passed! Voice hints feature is ready to use!")
        print("\n📋 Next steps:")
        print("   1. Add 'Read Aloud' buttons to your frontend hints UI")
        print("   2. Call the voice hint endpoint when users click the button")
        print("   3. Play the returned audio data in the browser")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        print("   Make sure your backend is running and API key is configured.")

if __name__ == "__main__":
    main()