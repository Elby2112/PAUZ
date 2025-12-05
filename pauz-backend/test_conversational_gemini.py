#!/usr/bin/env python3
"""
Test Conversational Gemini Responses
Check if Gemini is actually responding vs using templates
"""

import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def test_conversational_responses():
    print("🗣️ Testing Conversational Gemini Responses")
    print("=" * 50)
    
    try:
        from app.services.smart_memory_voice_service import smart_memory_voice_service
        
        test_user_id = "conversational_test_user"
        
        # Test diverse, conversational questions
        conversational_tests = [
            "I had a really tough day at work today",
            "My partner and I had an argument last night", 
            "I'm feeling anxious about my future",
            "I accomplished something I'm proud of!",
            "I don't know what to write about today",
            "Can you help me understand myself better?",
            "I'm feeling grateful for my family",
            "What's the point of journaling anyway?"
        ]
        
        print("🧪 Testing if Gemini actually responds conversationally:\n")
        
        for i, question in enumerate(conversational_tests, 1):
            print(f"{i}. User: {question}")
            
            start_time = time.time()
            response = smart_memory_voice_service.generate_intelligent_response(
                user_input=question,
                user_id=test_user_id
            )
            response_time = time.time() - start_time
            
            print(f"   PAUZ: {response}")
            print(f"   Time: {response_time:.3f}s")
            
            # Check if this is a real Gemini response vs template
            template_indicators = [
                "In PAUZ, you can try",
                "I'm here to help",
                "You can explore",
                "What interests you most",
                "What feels right"
            ]
            
            is_template = any(indicator in response for indicator in template_indicators)
            
            if is_template:
                print("   ⚠️ Sounds like a template/response_cache")
            else:
                print("   ✅ Seems like a real Gemini response!")
            
            print()
        
        print("🎉 Conversational Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_conversational_responses()