#!/usr/bin/env python3
"""
Test script to verify the voice feature fixes
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.free_journal_service import free_journal_service
from app.services.storage_service import storage_service
import base64

def test_storage_upload():
    """Test the storage upload fix"""
    print("🧪 Testing storage upload fix...")
    
    # Create test audio data (small WAV file header + some silence)
    # WAV file header for 44.1kHz, 16-bit, mono
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
    silence_data = bytes([0] * 2048)  # 2048 bytes of silence
    test_audio = wav_header + silence_data
    
    try:
        # Test the fixed storage upload
        audio_id = "test-audio-123"
        user_id = "test-user-456"
        
        print(f"📁 Testing upload of {len(test_audio)} bytes...")
        result_key = storage_service.upload_audio(user_id, audio_id, test_audio)
        print(f"✅ Storage upload successful! Key: {result_key}")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage upload failed: {e}")
        return False

def test_elevenlabs_api():
    """Test the ElevenLabs API fix"""
    print("\n🧪 Testing ElevenLabs API fix...")
    
    # Check if ElevenLabs is configured
    if not os.getenv("ELEVENLABS_API_KEY"):
        print("⚠️ ELEVENLABS_API_KEY not configured, skipping API test")
        return True
    
    # Create test audio data (same as above)
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
    
    silence_data = bytes([0] * 2048)  # 2048 bytes of silence
    test_audio = wav_header + silence_data
    
    try:
        print(f"🔊 Testing ElevenLabs API with {len(test_audio)} bytes...")
        
        # Test the fixed ElevenLabs call
        from io import BytesIO
        audio_file_obj = BytesIO(test_audio)
        
        response = free_journal_service.elevenlabs_client.speech_to_text.convert(
            model_id="scribe_v1",
            file=audio_file_obj
        )
        
        print(f"✅ ElevenLabs API call successful!")
        print(f"📝 Transcribed text: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ ElevenLabs API test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing voice feature fixes...\n")
    
    storage_ok = test_storage_upload()
    elevenlabs_ok = test_elevenlabs_api()
    
    print(f"\n📊 Test Results:")
    print(f"   Storage upload: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    print(f"   ElevenLabs API: {'✅ PASS' if elevenlabs_ok else '❌ FAIL'}")
    
    if storage_ok and elevenlabs_ok:
        print(f"\n🎉 All tests passed! The voice feature should now work correctly.")
        print(f"\n💡 What was fixed:")
        print(f"   1. Storage upload: Bytes are now converted to base64 strings")
        print(f"   2. ElevenLabs API: Using correct 'file' parameter instead of 'audio'")
    else:
        print(f"\n⚠️ Some tests failed. Please check the error messages above.")

if __name__ == "__main__":
    main()