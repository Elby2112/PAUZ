#!/usr/bin/env python3
"""
Test the New Casual Voice Assistant
Actually friendly, not robotic!
"""

import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def test_casual_voice():
    print("🗣️ Testing CASUAL Voice Assistant")
    print("=" * 40)
    
    try:
        from app.services.casual_voice_service import casual_voice_service
        
        test_user_id = "casual_test_user"
        
        # Test real user scenarios
        casual_tests = [
            "Ugh, work was awful today",
            "My boyfriend and I had a stupid fight", 
            "I'm feeling so anxious about everything",
            "I got a promotion! So excited!",
            "I don't know what to write about",
            "What's the point of all this journaling stuff?",
            "Feeling really grateful for my friends today",
            "I'm kinda lost in life right now"
        ]
        
        print("🧪 Testing casual, friendly responses:\n")
        
        for i, message in enumerate(casual_tests, 1):
            print(f"{i}. User: {message}")
            
            start_time = time.time()
            response = casual_voice_service.generate_casual_response(
                user_input=message,
                user_id=test_user_id
            )
            response_time = time.time() - start_time
            
            print(f"   PAUZ: {response}")
            print(f"   Time: {response_time:.3f}s")
            
            # Check if it sounds casual vs robotic
            robotic_indicators = [
                "I'm here to help",
                "PAUZ offers",
                "You can explore",
                "structured prompts",
                "What interests you most"
            ]
            
            casual_indicators = [
                "Ugh", "totally", "wanna", "gonna", "kinda", "hey", "oh", "awesome", "love that"
            ]
            
            is_robotic = any(indicator in response for indicator in robotic_indicators)
            is_casual = any(indicator in response for indicator in casual_indicators)
            
            if is_robotic:
                print("   😬 Still sounds robotic")
            elif is_casual:
                print("   ✅ Sounds casual and friendly!")
            else:
                print("   🤔 Getting warmer...")
            
            print()
        
        print("🎉 Casual Voice Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_casual_voice()