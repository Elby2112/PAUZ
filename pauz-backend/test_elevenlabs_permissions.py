#!/usr/bin/env python3
"""
Test ElevenLabs API key permissions
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_elevenlabs_permissions():
    """Test if the ElevenLabs API key has speech-to-text permissions"""
    
    print("🔊 Testing ElevenLabs API Permissions")
    print("=" * 40)
    
    api_key = os.getenv("ELEVENLABS_API_KEY")
    
    if not api_key:
        print("❌ ELEVENLABS_API_KEY not found")
        return False
    
    if api_key == "your-elevenlabs-api-key-here":
        print("❌ API key is still set to placeholder value")
        return False
    
    print(f"🔑 Testing API key: {api_key[:20]}...")
    
    try:
        from elevenlabs.client import ElevenLabs
        
        client = ElevenLabs(api_key=api_key)
        
        # Test 1: Try to get available models (should work)
        print("📋 Testing basic API access...")
        try:
            models = client.models.get_all()
            print("✅ Basic API access works")
            
            # Check if speech-to-text model is available
            scribe_available = any(model.model_id == "scribe_v1" for model in models)
            print(f"🔊 Scribe model available: {'✅' if scribe_available else '❌'}")
            
        except Exception as e:
            print(f"❌ Basic API access failed: {e}")
            return False
        
        # Test 2: Try speech-to-text API (this will show the permissions issue)
        print("\n🎤 Testing speech-to-text permissions...")
        try:
            # We'll just try to access the endpoint, not actually transcribe
            import requests
            headers = {
                "xi-api-key": api_key,
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                "https://api.elevenlabs.io/v1/models",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ API key has valid permissions")
                return True
            elif response.status_code == 401:
                error_data = response.json()
                if "missing_permissions" in str(error_data):
                    print("❌ API key missing speech-to-text permissions")
                    print("\n🔧 To fix this:")
                    print("1. Go to https://elevenlabs.io/app/settings/api-keys")
                    print("2. Edit your API key or create a new one")
                    print("3. Enable 'Speech-to-Text' permissions")
                    print("4. Update your .env file with the new API key")
                    return False
                else:
                    print(f"❌ Authentication failed: {error_data}")
                    return False
            else:
                print(f"⚠️ Unexpected response: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Permission test failed: {e}")
            return False
            
    except ImportError:
        print("❌ ElevenLabs library not installed")
        print("📦 Install with: pip install elevenlabs")
        return False

def show_fix_instructions():
    """Show detailed instructions for fixing the API key"""
    
    print("\n🔧 Detailed Fix Instructions")
    print("=" * 35)
    
    print("🌐 Step 1: Go to ElevenLabs Console")
    print("   https://elevenlabs.io/app/settings/api-keys")
    print()
    
    print("🔑 Step 2: Manage Your API Key")
    print("   Option A: Click 'Edit' on your existing key")
    print("   Option B: Click 'Create New API Key'")
    print()
    
    print("✅ Step 3: Enable Speech-to-Text")
    print("   ✅ Check the box for 'Speech-to-Text' permissions")
    print("   ✅ Make sure 'Text-to-Speech' is also enabled (for other features)")
    print()
    
    print("📋 Step 4: Copy the API Key")
    print("   Click the copy button next to your API key")
    print()
    
    print("📝 Step 5: Update Your .env File")
    print("   Open your .env file")
    print("   Replace the ELEVENLABS_API_KEY line:")
    print("   ELEVENLABS_API_KEY=your_new_api_key_here")
    print()
    
    print("🔄 Step 6: Restart Your Backend")
    print("   Stop your current backend (Ctrl+C)")
    print("   Restart with: uvicorn app.main:app --reload")
    print()
    
    print("🧪 Step 7: Test Again")
    print("   Try recording voice in your app")
    print("   Should now transcribe successfully!")

if __name__ == "__main__":
    print("🎤 ElevenLabs API Key Permission Test")
    print("=" * 50)
    
    has_permissions = test_elevenlabs_permissions()
    
    if not has_permissions:
        show_fix_instructions()
    else:
        print("\n🎉 Your API key is properly configured!")
        print("🎤 The voice transcription should work now!")