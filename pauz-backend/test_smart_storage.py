#!/usr/bin/env python3
"""
Test SmartStorage Service functionality
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_smart_storage():
    """Test all SmartStorage functions"""
    
    print("🧪 Testing SmartStorage Service")
    print("=" * 40)
    
    try:
        from app.services.smart_storage_service import smart_storage_service
        
        # Test user
        test_user_id = "test_user_123"
        
        # Test 1: Store user profile
        print("\n1️⃣ Testing user profile storage...")
        profile_data = {
            "name": "Test User",
            "email": "test@example.com",
            "picture": "https://example.com/pic.jpg",
            "preferences": {
                "theme": "dark",
                "language": "en"
            }
        }
        
        profile_success = smart_storage_service.store_user_profile(test_user_id, profile_data)
        print(f"   Profile storage: {'✅ Success' if profile_success else '❌ Failed'}")
        
        # Test 2: Retrieve user profile
        print("\n2️⃣ Testing user profile retrieval...")
        retrieved_profile = smart_storage_service.get_user_profile(test_user_id)
        if retrieved_profile:
            print(f"   Profile retrieval: ✅ Success")
            print(f"   Retrieved name: {retrieved_profile.get('name')}")
        else:
            print(f"   Profile retrieval: ❌ Failed")
        
        # Test 3: Store free journal
        print("\n3️⃣ Testing free journal storage...")
        journal_content = "Today was a great day! I learned so much about SmartStorage."
        journal_metadata = {"word_count": 12, "mood": "positive"}
        
        journal_success = smart_storage_service.store_free_journal(
            test_user_id, 
            "session_456", 
            journal_content,
            journal_metadata
        )
        print(f"   Journal storage: {'✅ Success' if journal_success else '❌ Failed'}")
        
        # Test 4: Store voice recording (simulated)
        print("\n4️⃣ Testing voice recording storage...")
        audio_data = b"fake_audio_data_for_testing" * 100  # Simulated audio
        voice_success = smart_storage_service.store_voice_recording(test_user_id, "session_456", audio_data)
        print(f"   Voice storage: {'✅ Success' if voice_success else '❌ Failed'}")
        
        # Test 5: Store guided journal
        print("\n5️⃣ Testing guided journal storage...")
        guided_journal_data = {
            "topic": "Personal Growth",
            "prompts": ["What did you learn today?", "How did you feel?"],
            "responses": ["I learned about SmartStorage", "I felt excited"],
            "completion_percentage": 100
        }
        
        guided_success = smart_storage_service.store_guided_journal(
            test_user_id,
            "journal_789",
            guided_journal_data
        )
        print(f"   Guided journal storage: {'✅ Success' if guided_success else '❌ Failed'}")
        
        # Test 6: Store AI prompt
        print("\n6️⃣ Testing AI prompt storage...")
        ai_prompt_data = {
            "prompt": "What three things are you grateful for today?",
            "type": "gratitude",
            "effectiveness": "high"
        }
        
        prompt_success = smart_storage_service.store_ai_prompt(test_user_id, "gratitude", ai_prompt_data)
        print(f"   AI prompt storage: {'✅ Success' if prompt_success else '❌ Failed'}")
        
        # Test 7: Store garden data
        print("\n7️⃣ Testing garden data storage...")
        garden_data = {
            "flowers": [
                {"type": "sunflower", "position": {"x": 100, "y": 200}, "size": "large"},
                {"type": "rose", "position": {"x": 300, "y": 150}, "size": "medium"}
            ],
            "background": "sunny",
            "mood": "happy"
        }
        
        garden_success = smart_storage_service.store_garden_data(test_user_id, garden_data)
        print(f"   Garden storage: {'✅ Success' if garden_success else '❌ Failed'}")
        
        # Test 8: Store user analytics
        print("\n8️⃣ Testing user analytics storage...")
        analytics_data = {
            "journals_written": 3,
            "total_words": 156,
            "dominant_mood": "positive",
            "session_time_minutes": 45
        }
        
        analytics_success = smart_storage_service.store_user_analytics(test_user_id, analytics_data)
        print(f"   Analytics storage: {'✅ Success' if analytics_success else '❌ Failed'}")
        
        # Summary
        print(f"\n📊 Test Summary:")
        total_tests = 8
        successful_tests = sum([
            profile_success,
            bool(retrieved_profile),
            journal_success,
            voice_success,
            guided_success,
            prompt_success,
            garden_success,
            analytics_success
        ])
        
        print(f"   Passed: {successful_tests}/{total_tests}")
        print(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if successful_tests == total_tests:
            print(f"\n🎉 All SmartStorage tests passed!")
            print(f"🚀 Ready to integrate with existing services!")
        else:
            print(f"\n⚠️ Some tests failed - check the errors above")
        
        return successful_tests == total_tests
        
    except Exception as e:
        print(f"❌ SmartStorage test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SmartStorage Test Suite")
    print("=" * 40)
    
    success = test_smart_storage()
    
    if success:
        print(f"\n✅ SmartStorage is working perfectly!")
        print(f"🎯 Next: Update existing services to use SmartStorage")
    else:
        print(f"\n❌ SmartStorage needs fixes before proceeding")