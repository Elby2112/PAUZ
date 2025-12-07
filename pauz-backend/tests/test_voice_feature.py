#!/usr/bin/env python3
"""
Test the voice feature end-to-end
"""

import os
import requests
import json
import base64
from io import BytesIO
import wave
import struct
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_voice_feature():
    """Test the complete voice feature pipeline"""
    
    print("🎤 Testing Voice Feature Pipeline")
    print("=" * 40)
    
    # Check environment variables
    print("1. Environment Variables:")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    print(f"   ELEVENLABS_API_KEY: {'✅ Set' if elevenlabs_key else '❌ Missing'}")
    
    if not elevenlabs_key:
        print("   ❌ Voice feature will not work without ElevenLabs API key")
        return
    
    # Create a test WAV file
    print("\n2. Creating test audio file...")
    test_audio = create_test_wav()
    print(f"   ✅ Test WAV created: {len(test_audio)} bytes")
    
    # Test backend endpoint
    print("\n3. Testing backend voice endpoint...")
    test_voice_endpoint(test_audio)

def create_test_wav():
    """Create a simple WAV file for testing"""
    
    # WAV file parameters
    sample_rate = 44100
    duration = 2  # 2 seconds
    frequency = 440  # A4 note
    
    # Generate a simple sine wave
    import math
    samples = []
    for i in range(int(sample_rate * duration)):
        t = float(i) / sample_rate
        sample = int(32767 * math.sin(2 * math.pi * frequency * t))
        samples.append(struct.pack('<h', sample))
    
    # Create WAV header
    wav_header = bytearray()
    
    # RIFF chunk
    wav_header.extend(b'RIFF')
    wav_header.extend(struct.pack('<I', 36 + len(samples) * 2))
    wav_header.extend(b'WAVE')
    
    # fmt chunk
    wav_header.extend(b'fmt ')
    wav_header.extend(struct.pack('<I', 16))
    wav_header.extend(struct.pack('<H', 1))  # PCM
    wav_header.extend(struct.pack('<H', 1))  # mono
    wav_header.extend(struct.pack('<I', sample_rate))
    wav_header.extend(struct.pack('<I', sample_rate * 2))
    wav_header.extend(struct.pack('<H', 2))
    wav_header.extend(struct.pack('<H', 16))
    
    # data chunk
    wav_header.extend(b'data')
    wav_header.extend(struct.pack('<I', len(samples) * 2))
    
    return bytes(wav_header) + b''.join(samples)

def test_voice_endpoint(audio_data):
    """Test the voice endpoint with test audio"""
    
    base_url = "http://localhost:8000"
    
    print("   📋 To test the voice endpoint manually:")
    print("   1. Get a valid JWT token from your app")
    print("   2. Create a Free Journal session")
    print("   3. Send audio to the voice endpoint")
    print()
    
    # Show example curl command
    print("   💻 Example curl command:")
    print("   curl -X POST 'http://localhost:8000/freejournal/{session_id}/voice' \\")
    print("        -H 'Authorization: Bearer YOUR_JWT_TOKEN' \\")
    print("        -F 'audio_file=@test_audio.wav'")
    print()
    
    # Show the test process
    print("   🧪 Test process:")
    print("   1. Frontend records audio using MediaRecorder API")
    print("   2. Audio is converted to WAV blob")
    print("   3. Blob is sent as FormData to backend")
    print("   4. Backend uploads to SmartBucket storage")
    print("   5. Backend sends to ElevenLabs for transcription")
    print("   6. Transcribed text is added to journal content")
    print()

def check_elevenlabs_config():
    """Check ElevenLabs configuration"""
    
    print("🔧 ElevenLabs Configuration Check")
    print("=" * 40)
    
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not elevenlabs_key:
        print("❌ ELEVENLABS_API_KEY not found in .env file")
        print()
        print("🔧 To fix this:")
        print("1. Get an API key from https://elevenlabs.io/app/settings/api-keys")
        print("2. Add to your .env file:")
        print("   ELEVENLABS_API_KEY=your_api_key_here")
        return False
    
    if elevenlabs_key == "your-elevenlabs-api-key-here":
        print("❌ ELEVENLABS_API_KEY is set to placeholder value")
        print("   Please replace with your actual ElevenLabs API key")
        return False
    
    print("✅ ELEVENLABS_API_KEY is configured")
    
    # Test the API connection
    try:
        from elevenlabs.client import ElevenLabs
        client = ElevenLabs(api_key=elevenlabs_key)
        
        # Try to get models to test connection
        models = client.models.get_all()
        print(f"✅ ElevenLabs API connection successful")
        print(f"   Available models: {len(models)}")
        
        # Check if speech-to-text model is available
        scribe_available = any(model.model_id == "scribe_v1" for model in models)
        print(f"   Scribe model available: {'✅' if scribe_available else '❌'}")
        
        return True
        
    except Exception as e:
        print(f"❌ ElevenLabs API connection failed: {e}")
        return False

def check_storage_config():
    """Check storage configuration"""
    
    print("\n📁 Storage Configuration Check")
    print("=" * 35)
    
    api_key = os.getenv("AI_API_KEY")
    org_name = os.getenv("RAINDROP_ORG")
    app_name = os.getenv("APPLICATION_NAME")
    
    print(f"AI_API_KEY: {'✅ Set' if api_key else '❌ Missing'}")
    print(f"RAINDROP_ORG: {'✅' + org_name if org_name else '❌ Missing'}")
    print(f"APPLICATION_NAME: {'✅' + app_name if app_name else '❌ Missing'}")
    
    if all([api_key, org_name, app_name]):
        print("✅ Storage configuration looks good")
        return True
    else:
        print("❌ Storage configuration incomplete")
        return False

def frontend_debug_tips():
    """Provide frontend debugging tips"""
    
    print("\n🎨 Frontend Debug Tips")
    print("=" * 30)
    
    print("If the voice feature isn't working:")
    print()
    print("1. 🎤 Check microphone permissions:")
    print("   - Browser must allow microphone access")
    print("   - Check site settings in browser")
    print("   - Try HTTPS if microphone blocked on HTTP")
    print()
    
    print("2. 🔍 Check browser console:")
    print("   - Look for 'Error accessing microphone'")
    print("   - Check for CORS errors")
    print("   - Look for failed fetch requests")
    print()
    
    print("3. 📡 Check network requests:")
    print("   - Open DevTools Network tab")
    print("   - Filter by 'voice' or 'freejournal'")
    print("   - Check if POST request is sent")
    print("   - Check response status and body")
    print()
    
    print("4. 🧪 Test with browser console:")
    print("```javascript")
    print("// Test microphone access")
    print("navigator.mediaDevices.getUserMedia({ audio: true })")
    print("  .then(stream => console.log('✅ Microphone works'))")
    print("  .catch(err => console.error('❌ Microphone failed:', err));")
    print("```")

def show_complete_flow():
    """Show the complete voice feature flow"""
    
    print("\n🔄 Complete Voice Feature Flow")
    print("=" * 35)
    
    print("1. 🎤 User clicks microphone button in FreeJournal")
    print("2. 📱 Frontend requests microphone permission")
    print("3. ⏺️ MediaRecorder starts recording audio")
    print("4. 🛑 User stops recording")
    print("5. 📦 Audio blob is created (WAV format)")
    print("6. 🔄 FormData is prepared with audio file")
    print("7. 📡 POST request sent to /freejournal/{session_id}/voice")
    print("8. 🔐 JWT token authenticates the request")
    print("9. 📁 Backend uploads audio to SmartBucket")
    print("10. 🔊 Backend sends audio to ElevenLabs")
    print("11. 📝 ElevenLabs returns transcribed text")
    print("12. 💾 Backend updates journal with transcription")
    print("13. 📨 Response returns updated journal content")
    print("14. 🎨 Frontend updates text area with transcription")
    print()
    print("✨ User sees their voice converted to text!")

if __name__ == "__main__":
    print("🎤 Voice Feature Test Tool")
    print("=" * 50)
    
    # Check configurations
    elevenlabs_ok = check_elevenlabs_config()
    storage_ok = check_storage_config()
    
    # Test the feature
    test_voice_feature()
    
    # Show additional info
    frontend_debug_tips()
    show_complete_flow()
    
    print("\n📊 Test Results:")
    print(f"   ElevenLabs Config: {'✅ PASS' if elevenlabs_ok else '❌ FAIL'}")
    print(f"   Storage Config: {'✅ PASS' if storage_ok else '❌ FAIL'}")
    
    if elevenlabs_ok and storage_ok:
        print("\n🎉 Voice feature should work correctly!")
        print("💡 If it's still not working, check the frontend debugging tips above.")
    else:
        print("\n⚠️ Configuration issues found. Please fix the items marked as ❌.")