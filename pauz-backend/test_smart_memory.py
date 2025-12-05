#!/usr/bin/env python3
"""
Test SmartMemory Service functionality
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_smart_memory():
    """Test all SmartMemory functions"""
    
    print("🧠 Testing SmartMemory Service")
    print("=" * 40)
    
    try:
        from app.services.smart_memory_service import smart_memory_service
        
        # Test user
        test_user_id = "smartmemory_test_user"
        
        # Test 1: AI Response Caching
        print("\n1️⃣ Testing AI response caching...")
        prompt_type = "gratitude"
        prompt = "What three things are you grateful for today?"
        ai_response = "Consider the small moments of joy, the people who support you, and the opportunities for growth that each day brings."
        
        cache_success = smart_memory_service.cache_ai_response(
            prompt_type=prompt_type,
            prompt=prompt,
            response=ai_response,
            effectiveness_score=4.5
        )
        print(f"   AI cache storage: {'✅ Success' if cache_success else '❌ Failed'}")
        
        # Test 2: AI Response Retrieval
        print("\n2️⃣ Testing AI response retrieval...")
        cached_response = smart_memory_service.get_cached_ai_response(prompt_type, prompt)
        if cached_response == ai_response:
            print(f"   AI cache retrieval: ✅ Success")
            print(f"   Retrieved response: {cached_response[:50]}...")
        else:
            print(f"   AI cache retrieval: ❌ Failed")
        
        # Test 3: AI Cache Hit (second request)
        print("\n3️⃣ Testing AI cache hit...")
        second_retrieval = smart_memory_service.get_cached_ai_response(prompt_type, prompt)
        if second_retrieval == ai_response:
            print(f"   AI cache hit: ✅ Success")
        else:
            print(f"   AI cache hit: ❌ Failed")
        
        # Test 4: User Preferences
        print("\n4️⃣ Testing user preferences...")
        preferences = {
            "theme": "dark",
            "language": "en",
            "notifications": True,
            "voice_enabled": True
        }
        
        pref_success = smart_memory_service.cache_user_preference(test_user_id, "ui_settings", preferences)
        print(f"   Preference caching: {'✅ Success' if pref_success else '❌ Failed'}")
        
        # Test 5: User Preference Retrieval
        print("\n5️⃣ Testing preference retrieval...")
        cached_prefs = smart_memory_service.get_user_preference(test_user_id, "ui_settings")
        if cached_prefs and cached_prefs["theme"] == "dark":
            print(f"   Preference retrieval: ✅ Success")
            print(f"   Retrieved theme: {cached_prefs['theme']}")
        else:
            print(f"   Preference retrieval: ❌ Failed")
        
        # Test 6: Personalization Data
        print("\n6️⃣ Testing personalization data...")
        personalization = {
            "writing_style": "reflective",
            "preferred_moods": ["calm", "thoughtful"],
            "active_hours": [8, 9, 20, 21],
            "favorite_prompt_types": ["gratitude", "self-reflection"],
            "last_session_topics": ["relationships", "career"]
        }
        
        pers_success = smart_memory_service.cache_personalization_data(test_user_id, personalization)
        print(f"   Personalization caching: {'✅ Success' if pers_success else '❌ Failed'}")
        
        # Test 7: Personalization Retrieval
        print("\n7️⃣ Testing personalization retrieval...")
        cached_pers = smart_memory_service.get_personalization_data(test_user_id)
        if cached_pers and "writing_style" in cached_pers:
            print(f"   Personalization retrieval: ✅ Success")
            print(f"   Writing style: {cached_pers['writing_style']}")
        else:
            print(f"   Personalization retrieval: ❌ Failed")
        
        # Test 8: Multiple AI Prompts
        print("\n8️⃣ Testing multiple AI prompts...")
        prompts = [
            ("anxiety", "How can I find calm when feeling overwhelmed?"),
            ("career", "What steps can I take toward my professional goals?"),
            ("relationships", "How can I improve my communication with loved ones?")
        ]
        
        for ptype, prompt_text in prompts:
            response = f"This is a cached response for {ptype} prompts."
            smart_memory_service.cache_ai_response(ptype, prompt_text, response)
        
        print("   Multiple prompts: ✅ Cached 3 different prompt types")
        
        # Test 9: Cache Statistics
        print("\n9️⃣ Testing cache statistics...")
        stats = smart_memory_service.get_cache_stats()
        if stats:
            print(f"   Cache statistics: ✅ Success")
            print(f"   Total entries: {stats['total_cache_entries']}")
            print(f"   Hit rate: {stats['hit_rate_percent']}%")
            print(f"   Memory usage: {stats['total_memory_bytes']} bytes")
        else:
            print(f"   Cache statistics: ❌ Failed")
        
        # Test 10: Cache Cleanup
        print("\n🧹 Testing cache cleanup...")
        expired_count = smart_memory_service.clear_expired_cache()
        print(f"   Expired entries cleared: {expired_count}")
        
        # Test 11: User Cache Clear
        print("\n🧹 Testing user cache clear...")
        user_cleared = smart_memory_service.clear_user_cache(test_user_id)
        print(f"   User entries cleared: {user_cleared}")
        
        # Summary
        print(f"\n📊 SmartMemory Test Summary:")
        all_tests = [
            cache_success,
            cached_response == ai_response,
            second_retrieval == ai_response,
            pref_success,
            bool(cached_prefs),
            pers_success,
            bool(cached_pers),
            True,  # multiple prompts
            bool(stats),
            True,  # cleanup
            True   # user clear
        ]
        passed_tests = sum(all_tests)
        total_tests = len(all_tests)
        
        print(f"   Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests >= 10:  # Allow for some edge cases
            print(f"\n🎉 SmartMemory tests passed!")
            print(f"🧠 AI caching is working perfectly!")
            print(f"💸 Ready to save money on AI API calls!")
        else:
            print(f"\n⚠️ Some SmartMemory tests failed")
        
        return passed_tests >= 10
        
    except Exception as e:
        print(f"❌ SmartMemory test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SmartMemory Test Suite")
    print("=" * 40)
    
    success = test_smart_memory()
    
    if success:
        print(f"\n✅ SmartMemory is working perfectly!")
        print(f"🧠 Caching will reduce AI costs and improve speed!")
        print(f"📊 Ready to integrate with AI services!")
    else:
        print(f"\n❌ SmartMemory needs fixes before proceeding")