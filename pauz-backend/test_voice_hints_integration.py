#!/usr/bin/env python3
"""
Integration test for Voice Hints feature
Tests the complete flow: hint generation → voice conversion
"""

import os
import sys
import json
import base64
from pathlib import Path

# Add app to path
sys.path.append(str(Path(__file__).parent))

def test_voice_service_import():
    """Test that we can import the voice service"""
    print("🔧 Testing voice service import...")
    
    try:
        from app.services.voice_service import voice_service, VoiceService
        print("✅ Voice service imported successfully!")
        return True
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_voice_service_availability():
    """Test if voice service is properly configured"""
    print("\n🔑 Testing voice service configuration...")
    
    try:
        from app.services.voice_service import voice_service
        
        if not voice_service.is_available():
            print("⚠️  ElevenLabs API key not configured")
            print("   Set ELEVENLABS_API_KEY environment variable to test full functionality")
            return False
        
        print("✅ Voice service is properly configured!")
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def test_voice_service_direct():
    """Test voice service directly with a sample hint"""
    print("\n🎤 Testing voice service directly...")
    
    try:
        from app.services.voice_service import voice_service
        
        if not voice_service.is_available():
            print("⚠️  Skipping test - API key not configured")
            return False
        
        # Sample hint text
        sample_hint = "Take a deep breath and notice how your body feels right now. What sensations are present?"
        
        print(f"   Converting hint: '{sample_hint}'")
        
        result = voice_service.text_to_speech(sample_hint, voice_profile="hints")
        
        if result.get("success"):
            print("✅ Voice generation successful!")
            print(f"   Audio size: {result.get('file_size', 0)} bytes")
            print(f"   Voice used: {result.get('voice_id', 'Unknown')}")
            print(f"   Profile: {result.get('voice_profile', 'Unknown')}")
            
            # Save test audio
            try:
                voice_service.save_audio_to_file(result["audio_data"], "hint_test.mp3")
                print("   Test audio saved to: audio_output/hint_test.mp3")
            except Exception as e:
                print(f"   ⚠️  Could not save audio: {e}")
            
            return True
        else:
            print(f"❌ Voice generation failed: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Direct test failed: {e}")
        return False

def test_voice_profiles():
    """Test different voice profiles"""
    print("\n🎭 Testing different voice profiles...")
    
    try:
        from app.services.voice_service import voice_service
        
        if not voice_service.is_available():
            print("⚠️  Skipping test - API key not configured")
            return False
        
        test_text = "This is a test of the voice system."
        profiles = ["hints", "welcome", "guide"]
        
        success_count = 0
        
        for profile in profiles:
            print(f"   Testing profile: {profile}")
            
            result = voice_service.text_to_speech(test_text, voice_profile=profile)
            
            if result.get("success"):
                print(f"     ✅ {profile} profile working")
                success_count += 1
            else:
                print(f"     ❌ {profile} profile failed: {result.get('error')}")
        
        print(f"   Result: {success_count}/{len(profiles)} profiles working")
        return success_count == len(profiles)
        
    except Exception as e:
        print(f"❌ Profile test failed: {e}")
        return False

def test_available_voices():
    """Test fetching available voices"""
    print("\n🔊 Testing available voices fetch...")
    
    try:
        from app.services.voice_service import voice_service
        
        if not voice_service.is_available():
            print("⚠️  Skipping test - API key not configured")
            return False
        
        voices_result = voice_service.get_available_voices()
        
        if voices_result.get("success"):
            voices = voices_result.get("voices", [])
            print(f"✅ Found {len(voices)} available voices!")
            
            # Show some example voices
            for i, voice in enumerate(voices[:3]):
                name = voice.get("name", "Unknown")
                voice_id = voice.get("voice_id", "Unknown")
                gender = voice.get("gender", "Unknown")
                print(f"   {i+1}. {name} ({voice_id}) - {gender}")
            
            return True
        else:
            print(f"❌ Failed to fetch voices: {voices_result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Voices fetch test failed: {e}")
        return False

def test_api_endpoint_structure():
    """Test that the API endpoints are properly structured (without making requests)"""
    print("\n🛠️  Testing API endpoint structure...")
    
    try:
        # Import the router to check if endpoints are defined
        from app.routes.free_journal import router
        
        # Get all routes
        routes = router.routes
        voice_routes = [route for route in routes if 'voice' in route.path.lower()]
        
        print(f"✅ Found {len(voice_routes)} voice-related endpoints:")
        
        for route in voice_routes:
            methods = list(route.methods)
            print(f"   {methods} {route.path}")
        
        # Check for expected endpoints
        expected_endpoints = [
            "/text-to-voice",
            "/voices/available"
        ]
        
        found_endpoints = [route.path for route in voice_routes]
        missing_endpoints = [ep for ep in expected_endpoints if ep not in found_endpoints]
        
        if missing_endpoints:
            print(f"⚠️  Missing expected endpoints: {missing_endpoints}")
            return False
        else:
            print("✅ All expected voice endpoints are present!")
            return True
            
    except Exception as e:
        print(f"❌ Endpoint structure test failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🎵 Voice Hints Integration Test Suite")
    print("=" * 50)
    
    # Check environment
    api_key = os.getenv('ELEVENLABS_API_KEY')
    if api_key:
        print(f"🔑 API Key configured: {'*' * 10}{api_key[-4:]}")
    else:
        print("⚠️  ELEVENLABS_API_KEY not set - some tests will be skipped")
    
    # Run all tests
    tests = [
        ("Import Test", test_voice_service_import),
        ("Configuration Test", test_voice_service_availability),
        ("Direct Voice Test", test_voice_service_direct),
        ("Voice Profiles Test", test_voice_profiles),
        ("Available Voices Test", test_available_voices),
        ("API Structure Test", test_api_endpoint_structure)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Voice hints feature is ready!")
        print("\n📋 Next steps:")
        print("   1. Start your FastAPI backend")
        print("   2. Add voice buttons to your frontend")
        print("   3. Test the complete flow in your app")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
        if not api_key:
            print("💡 Try setting ELEVENLABS_API_KEY and running again")

if __name__ == "__main__":
    main()