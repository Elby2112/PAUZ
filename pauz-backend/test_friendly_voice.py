#!/usr/bin/env python3
"""
Test the improved friendly voice assistant
"""

import os
import sys
sys.path.append('.')

from app.services.casual_voice_service import casual_voice_service
from app.services.smart_memory_voice_service import smart_memory_voice_service

def test_friendly_responses():
    """Test various user inputs to ensure friendly, varied responses"""
    
    test_inputs = [
        "hi there",
        "help", 
        "I'm feeling stuck",
        "had a tough day at work",
        "feeling anxious",
        "what can I do here",
        "hello",
        "I don't know what to write",
        "feeling happy today"
    ]
    
    print("🎤 Testing Friendly Voice Assistant Responses\n")
    print("=" * 60)
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{i}. User: \"{user_input}\"")
        
        # Test casual voice service
        try:
            response1 = casual_voice_service.generate_casual_response(
                user_input=user_input,
                user_id="test_user",
                user_context=None
            )
            print(f"   Casual: \"{response1}\"")
        except Exception as e:
            print(f"   Casual: ERROR - {e}")
        
        # Test same input again to check for variety
        try:
            response2 = casual_voice_service.generate_casual_response(
                user_input=user_input,
                user_id="test_user",
                user_context=None
            )
            print(f"   Again:  \"{response2}\"")
            
            # Check if responses are different (for variety)
            if response1 != response2:
                print("   ✅ Good variety!")
            else:
                print("   ⚠️ Same response (might be cached)")
                
        except Exception as e:
            print(f"   Again:  ERROR - {e}")
    
    print("\n" + "=" * 60)
    print("\n🧠 Testing SmartMemory Service...")
    
    # Test welcome messages
    for user_type in ["new", "returning"]:
        user_context = {"is_returning_user": user_type == "returning", "total_journals": 5 if user_type == "returning" else 0}
        
        try:
            welcome = smart_memory_voice_service.generate_personalized_welcome(
                user_id="test_user",
                user_context=user_context
            )
            print(f"\n{user_type.title()} user welcome: \"{welcome}\"")
        except Exception as e:
            print(f"Welcome error: {e}")
    
    print("\n✅ Voice assistant testing complete!")

if __name__ == "__main__":
    test_friendly_responses()