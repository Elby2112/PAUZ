#!/usr/bin/env python3
"""
Complete SmartStorage Integration Test - Final Version
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_complete_integration():
    """Test complete SmartStorage integration"""
    
    print("🚀 Complete SmartStorage Integration Test")
    print("=" * 50)
    
    try:
        # Import all services
        from app.services.smart_storage_service import smart_storage_service
        from app.services.smart_sql_service import smart_sql_service
        from app.services.smart_memory_service import smart_memory_service
        
        print("✅ All SmartStorage services imported successfully")
        
        # Test user
        test_user_id = "integration_test_user"
        
        # === SCENARIO: User completes a journal session ===
        
        print(f"\n📝 SCENARIO: User {test_user_id} completes a journal session")
        print("-" * 55)
        
        # 1. User logs in - cache preferences
        print("\n1️⃣ User authentication...")
        user_profile = {
            "name": "Integration Test User",
            "email": "integration@example.com",
            "preferences": {
                "theme": "dark",
                "voice_enabled": True,
                "language": "en"
            }
        }
        
        # Store in SmartSQL
        sql_success = smart_sql_service.upsert_user_profile(test_user_id, user_profile)
        
        # Cache in SmartMemory
        memory_success = smart_memory_service.cache_user_preference(
            test_user_id, 
            "ui_settings", 
            user_profile["preferences"]
        )
        
        print(f"   SmartSQL profile: {'✅' if sql_success else '❌'}")
        print(f"   SmartMemory preferences: {'✅' if memory_success else '❌'}")
        
        # 2. User starts free journal with voice
        print("\n2️⃣ Voice journal session...")
        
        # Simulate voice recording
        fake_audio = b"fake_voice_data" * 500  # Simulate voice data
        
        # Store in SmartStorage
        storage_success = smart_storage_service.store_voice_recording(
            test_user_id,
            "voice_session_123",
            fake_audio
        )
        
        print(f"   SmartStorage voice: {'✅' if storage_success else '❌'}")
        
        # 3. AI transcribes and analyzes
        print("\n3️⃣ AI processing with caching...")
        
        transcribed_text = "Today I feel grateful for my family and the opportunity to work on this hackathon project."
        mood_analysis = {"mood": "grateful", "confidence": 0.85, "energy": "high"}
        
        # Check if we have cached AI response
        cached_response = smart_memory_service.get_cached_ai_response(
            "mood_analysis", 
            transcribed_text[:50]
        )
        
        if cached_response:
            ai_response = cached_response
            print(f"   Used cached AI response: ✅")
        else:
            # Simulate AI processing
            ai_response = "Your entry shows strong gratitude and positive energy."
            
            # Cache the response
            smart_memory_service.cache_ai_response(
                "mood_analysis",
                transcribed_text[:50],
                ai_response,
                effectiveness_score=4.5
            )
            print(f"   Generated and cached AI response: ✅")
        
        # 4. Store journal with AI insights
        print("\n4️⃣ Journal storage...")
        
        # Store in SmartStorage
        journal_success = smart_storage_service.store_free_journal(
            user_id=test_user_id,
            session_id="voice_session_123",
            content=transcribed_text,
            metadata={
                "has_audio": True,
                "ai_analyzed": True,
                "mood": mood_analysis["mood"],
                "ai_insights": ai_response,
                "word_count": len(transcribed_text.split())
            }
        )
        
        # Store metadata in SmartSQL
        sql_journal_success = smart_sql_service.record_journal_entry(
            user_id=test_user_id,
            entry_id="journal_456",
            journal_type="free",
            session_id="voice_session_123", 
            content=transcribed_text,
            has_audio=True,
            mood_score=mood_analysis
        )
        
        print(f"   SmartStorage journal: {'✅' if journal_success else '❌'}")
        print(f"   SmartSQL metadata: {'✅' if sql_journal_success else '❌'}")
        
        # 5. Update analytics
        print("\n5️⃣ Analytics update...")
        
        analytics_success = smart_sql_service.update_user_analytics(
            test_user_id,
            len(transcribed_text.split()),
            True,
            15,
            mood_analysis["mood"],
            len(fake_audio)
        )
        
        # Store analytics in SmartStorage
        analytics_data = {
            "voice_sessions_completed": 1,
            "total_words_today": len(transcribed_text.split()),
            "mood_trends": [mood_analysis["mood"]],
            "ai_responses_cached": 1
        }
        
        storage_analytics_success = smart_storage_service.store_user_analytics(
            test_user_id,
            analytics_data
        )
        
        print(f"   SmartSQL analytics: {'✅' if analytics_success else '❌'}")
        print(f"   SmartStorage analytics: {'✅' if storage_analytics_success else '❌'}")
        
        # 6. Personalization update
        print("\n6️⃣ Personalization learning...")
        
        personalization_data = {
            "writing_patterns": {
                "average_word_count": len(transcribed_text.split()),
                "preferred_moods": [mood_analysis["mood"]],
                "voice_usage": True
            },
            "ai_interaction": {
                "cached_responses_used": 1,
                "response_effectiveness": 4.5
            },
            "session_patterns": {
                "average_session_minutes": 15,
                "active_hours": [datetime.now().hour]
            }
        }
        
        pers_success = smart_memory_service.cache_personalization_data(
            test_user_id,
            personalization_data
        )
        
        print(f"   SmartMemory personalization: {'✅' if pers_success else '❌'}")
        
        # === VERIFICATION: Check all data is accessible ===
        
        print(f"\n🔍 VERIFICATION: Checking data integrity")
        print("-" * 45)
        
        # Test retrieval from all systems
        user_summary = smart_sql_service.get_user_summary(test_user_id)
        cached_prefs = smart_memory_service.get_user_preference(test_user_id, "ui_settings")
        cached_ai = smart_memory_service.get_cached_ai_response("mood_analysis", transcribed_text[:50])
        memory_stats = smart_memory_service.get_cache_stats()
        
        print(f"\n📊 Integration Results:")
        print(f"   SmartSQL user summary: {'✅' if user_summary else '❌'}")
        print(f"   SmartMemory preferences: {'✅' if cached_prefs else '❌'}")
        print(f"   SmartMemory AI cache: {'✅' if cached_ai else '❌'}")
        print(f"   Cache hit rate: {memory_stats['hit_rate_percent']:.1f}%")
        
        # Test results
        all_tests = [
            sql_success, memory_success, storage_success,
            sql_journal_success, journal_success, analytics_success,
            storage_analytics_success, pers_success,
            bool(user_summary), bool(cached_prefs), bool(cached_ai)
        ]
        
        passed_tests = sum(all_tests)
        total_tests = len(all_tests)
        
        print(f"\n🎉 Integration Test Results:")
        print(f"   Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print(f"\n✅ PERFECT! All SmartStorage components work together!")
            return True
        else:
            print(f"\n⚠️ Some integration issues found")
            return False
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SmartStorage Complete Integration Test")
    print("=" * 55)
    
    success = test_complete_integration()
    
    if success:
        print(f"\n🎉 SMARTSTORAGE IMPLEMENTATION COMPLETE!")
        print(f"🏆 Your PAUZ app now has enterprise-level features!")
        print(f"📱 Test it in your app - everything should work seamlessly!")
        print(f"\n💰 Benefits:")
        print(f"   🧠 AI cost savings through caching")
        print(f"   🪣 Organized storage for scalability")
        print(f"   📊 User analytics and insights")
        print(f"   🎯 Personalized user experience")
    else:
        print(f"\n⚠️ Integration needs fixes before production use")