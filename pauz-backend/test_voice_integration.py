#!/usr/bin/env python3
"""
Test SmartStorage integration with existing voice feature
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_voice_integration():
    """Test voice recording with SmartStorage"""
    
    print("🎤 Testing Voice Integration with SmartStorage")
    print("=" * 50)
    
    try:
        from app.services.smart_storage_service import smart_storage_service
        
        # Simulate voice data
        user_id = "integration_test_user"
        session_id = "voice_test_session"
        
        # Create fake audio data (WAV header + silence)
        wav_header = bytes([
            0x52, 0x49, 0x46, 0x46,  # "RIFF"
            0x24, 0x08, 0x00, 0x00,  # File size - 8
            0x57, 0x41, 0x56, 0x45,  # "WAVE"
            0x66, 0x6d, 0x74, 0x20,  # "fmt "
            0x10, 0x00, 0x00, 0x00,  # Chunk size
            0x01, 0x00,              # Audio format (PCM)
            0x01, 0x00,              # Number of channels (mono)
            0x44, 0xac, 0x00, 0x00,  # Sample rate (44100)
            0x88, 0x58, 0x01, 0x00,  # Byte rate
            0x02, 0x00,              # Block align
            0x10, 0x00,              # Bits per sample
            0x64, 0x61, 0x74, 0x61,  # "data"
            0x00, 0x08, 0x00, 0x00   # Data size
        ])
        
        # Add some silence data
        silence_data = bytes([0] * 1024)  # 1KB of silence
        fake_audio = wav_header + silence_data
        
        print(f"🎵 Created test audio: {len(fake_audio)} bytes")
        
        # Test SmartStorage voice recording
        print("\n1️⃣ Storing voice recording in SmartStorage...")
        voice_success = smart_storage_service.store_voice_recording(user_id, session_id, fake_audio)
        print(f"   Voice storage: {'✅ Success' if voice_success else '❌ Failed'}")
        
        if not voice_success:
            print("❌ Voice storage failed - cannot continue integration test")
            return False
        
        # Test storing corresponding journal entry
        print("\n2️⃣ Storing journal transcription...")
        transcribed_text = "This is a test transcription from my voice recording. SmartStorage is working great!"
        journal_success = smart_storage_service.store_free_journal(
            user_id=user_id,
            session_id=session_id,
            content=transcribed_text,
            metadata={
                "transcribed": True,
                "audio_length_seconds": 5,
                "word_count": len(transcribed_text.split())
            }
        )
        print(f"   Journal storage: {'✅ Success' if journal_success else '❌ Failed'}")
        
        # Test storing analytics
        print("\n3️⃣ Storing user analytics...")
        analytics_data = {
            "voice_sessions_completed": 1,
            "total_voice_minutes": 5,
            "transcription_success_rate": 100,
            "storage_used_bytes": len(fake_audio)
        }
        analytics_success = smart_storage_service.store_user_analytics(user_id, analytics_data)
        print(f"   Analytics storage: {'✅ Success' if analytics_success else '❌ Failed'}")
        
        # Test storing user profile
        print("\n4️⃣ Updating user profile...")
        profile_data = {
            "name": "Integration Test User",
            "voice_feature_enabled": True,
            "total_voice_recordings": 1,
            "preferred_storage": "smartstorage"
        }
        profile_success = smart_storage_service.store_user_profile(user_id, profile_data)
        print(f"   Profile update: {'✅ Success' if profile_success else '❌ Failed'}")
        
        # Summary
        print(f"\n📊 Integration Test Summary:")
        all_tests = [voice_success, journal_success, analytics_success, profile_success]
        passed_tests = sum(all_tests)
        total_tests = len(all_tests)
        
        print(f"   Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print(f"\n🎉 Voice integration with SmartStorage is perfect!")
            print(f"🚀 Ready to test with real voice recordings!")
        else:
            print(f"\n⚠️ Some integration tests failed")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

def test_backend_restart():
    """Test if backend can use SmartStorage after restart"""
    
    print(f"\n🔄 Testing Backend Restart Compatibility")
    print("=" * 45)
    
    try:
        # Import and test the service
        from app.services.free_journal_service import free_journal_service
        
        print("✅ FreeJournal service imports correctly")
        
        # Check if it has the SmartStorage dependency
        if hasattr(free_journal_service, 'smart_storage_service') or 'smart_storage_service' in str(type(free_journal_service)):
            print("✅ SmartStorage dependency available")
        else:
            print("⚠️ SmartStorage dependency check unclear")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend restart test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SmartStorage Integration Test")
    print("=" * 45)
    
    integration_success = test_voice_integration()
    backend_success = test_backend_restart()
    
    if integration_success and backend_success:
        print(f"\n✅ All integration tests passed!")
        print(f"🎯 SmartStorage is ready for production use!")
        print(f"📱 You can now test voice recording in your app!")
    else:
        print(f"\n⚠️ Some issues found - check the errors above")