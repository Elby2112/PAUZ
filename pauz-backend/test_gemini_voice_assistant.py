#!/usr/bin/env python3
"""
Test Gemini-Powered Voice Assistant
Tests the new intelligent voice responses
"""

import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def test_gemini_voice_service():
    print("🤖 Testing Gemini-Powered Voice Assistant")
    print("=" * 50)
    
    # Check environment
    gemini_key = os.getenv('GEMINI_API_KEY')
    elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
    
    if not gemini_key or gemini_key == 'your-gemini-api-key-here':
        print("❌ GEMINI_API_KEY not configured")
        return False
    
    if not elevenlabs_key:
        print("❌ ELEVENLABS_API_KEY not configured")
        return False
    
    print("✅ API keys found")
    
    try:
        # Import the services
        from app.services.gemini_voice_service import gemini_voice_service
        from app.services.voice_service import voice_service
        
        print("✅ Services imported successfully")
        
        # Test 1: Basic question
        print("\n🧪 Test 1: Basic question")
        response1 = gemini_voice_service.generate_intelligent_response("What can I do in this app?")
        print(f"User: What can I do in this app?")
        print(f"PAUZ: {response1}")
        
        # Test 2: Personal context
        print("\n🧪 Test 2: With user context")
        user_context = {
            "total_journals": 5,
            "is_returning_user": True,
            "last_journal_days_ago": 3
        }
        response2 = gemini_voice_service.generate_intelligent_response(
            "I'm feeling stuck", 
            user_context=user_context
        )
        print(f"User: I'm feeling stuck")
        print(f"PAUZ: {response2}")
        
        # Test 3: Welcome message
        print("\n🧪 Test 3: Personalized welcome")
        welcome = gemini_voice_service.generate_personalized_welcome(
            user_context=user_context
        )
        print(f"Welcome: {welcome}")
        
        # Test 4: Voice generation (if ElevenLabs is available)
        print("\n🧪 Test 4: Voice generation")
        if voice_service.is_available():
            voice_result = voice_service.text_to_speech(response1, voice_profile="guide")
            if voice_result["success"]:
                print(f"✅ Voice generated: {voice_result['file_size']} bytes")
            else:
                print(f"❌ Voice generation failed: {voice_result['error']}")
        else:
            print("⚠️ ElevenLabs not available, skipping voice test")
        
        print(f"\n🎉 Gemini Voice Assistant Test Complete!")
        print("✨ Your voice assistant is now powered by intelligent Gemini AI!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_voice_assistant_endpoints():
    """Test the actual voice assistant endpoints"""
    print("\n🌐 Testing Voice Assistant Endpoints")
    print("=" * 50)
    
    try:
        import requests
        API_BASE = "http://localhost:8000"
        
        # Test guidance endpoint
        print("🧪 Testing /voice-assistant/guidance endpoint")
        response = requests.post(
            f"{API_BASE}/voice-assistant/guidance",
            json={"question": "How do I get started with journaling?"},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Guidance response generated")
            print(f"Text: {result.get('text', 'N/A')[:100]}...")
            if result.get('audio_data'):
                print(f"✅ Audio generated: {len(result['audio_data'])} chars")
        else:
            print(f"❌ Guidance endpoint failed: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")

if __name__ == "__main__":
    success = test_gemini_voice_service()
    
    if success:
        # Test endpoints if backend is running
        try:
            test_voice_assistant_endpoints()
        except:
            print("\n⚠️ Backend not running - skip endpoint tests")
            print("💡 Start your backend with: uvicorn app.main:app --reload")
    
    print(f"\n📋 Next Steps:")
    print("1. Make sure your backend is running")
    print("2. Test the voice assistant in your frontend")
    print("3. Try different types of questions")
    print("4. Enjoy your intelligent voice assistant! 🎉")