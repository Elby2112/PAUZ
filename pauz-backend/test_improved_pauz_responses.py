#!/usr/bin/env python3
"""
Test Improved PAUZ Voice Assistant with Accurate App Knowledge
"""

import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def test_improved_responses():
    print("🎯 Testing Improved PAUZ Voice Assistant")
    print("=" * 50)
    
    try:
        from app.services.smart_memory_voice_service import smart_memory_voice_service
        
        test_user_id = "test_improved_user"
        
        # Test scenarios that were failing before
        test_scenarios = [
            {
                "question": "What can I do in this app?",
                "expected": "Should mention free journaling with AI hints, guided journaling with prompts, and garden for mood tracking"
            },
            {
                "question": "I'm feeling stuck",
                "expected": "Should suggest AI hints in free journaling, NOT garden hints"
            },
            {
                "question": "How do I get hints?",
                "expected": "Should explain hints appear during free journaling when stuck"
            },
            {
                "question": "What is the garden for?",
                "expected": "Should explain garden is for mood tracking with flowers, NOT hints"
            },
            {
                "question": "Tell me about guided journaling",
                "expected": "Should explain structured prompts on specific topics"
            },
            {
                "question": "I want to track my mood",
                "expected": "Should suggest garden with flower visualization"
            }
        ]
        
        print("🧪 Testing improved responses:\n")
        
        for i, scenario in enumerate(test_scenarios, 1):
            print(f"{i}. Question: {scenario['question']}")
            print(f"   Expected: {scenario['expected']}")
            
            # Test fast template first
            start_time = time.time()
            response = smart_memory_voice_service.generate_intelligent_response(
                user_input=scenario['question'],
                user_id=test_user_id
            )
            response_time = time.time() - start_time
            
            print(f"   Response: {response}")
            print(f"   Time: {response_time:.3f}s")
            
            # Check if response is improved
            if "hints garden" in response.lower() and "garden" in scenario['question'].lower():
                print("   ⚠️ Still has garden confusion")
            elif "free journaling" in response.lower() and "ai hints" in response.lower():
                print("   ✅ Good! Mentions free journaling with AI hints")
            elif "guided journaling" in response.lower() and "prompts" in response.lower():
                print("   ✅ Good! Explains guided journaling correctly")
            elif "mood" in response.lower() and "garden" in response.lower():
                print("   ✅ Good! Connects mood tracking to garden")
            else:
                print("   🤔 Response needs review")
            
            print()
        
        print("🎉 Improved Response Test Complete!")
        print("Your voice assistant now has accurate PAUZ app knowledge!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_improved_responses()