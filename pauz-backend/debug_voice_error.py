#!/usr/bin/env python3
"""
Debug script to check voice service error
"""

import os
import sys

# Check environment
print("🔍 Checking voice service configuration...")
print(f"ELEVENLABS_API_KEY exists: {bool(os.getenv('ELEVENLABS_API_KEY'))}")
print(f"API_KEY value: {os.getenv('ELEVENLABS_API_KEY', 'NOT_SET')}")

# Test voice service
try:
    sys.path.append('app')
    from services.voice_service import voice_service
    
    print(f"\nVoice service available: {voice_service.is_available()}")
    if not voice_service.is_available():
        print("❌ Voice service not available - no API key configured")
        print("\n📋 To fix this:")
        print("1. Set your ElevenLabs API key:")
        print("   export ELEVENLABS_API_KEY='your_actual_api_key_here'")
        print("2. Or create a .env file with the key")
        print("3. Restart your backend server")
    else:
        print("✅ Voice service is configured!")
        
except Exception as e:
    print(f"❌ Error importing voice service: {e}")