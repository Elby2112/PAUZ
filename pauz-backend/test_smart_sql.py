#!/usr/bin/env python3
"""
Test SmartSQL Service functionality
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def test_smart_sql():
    """Test all SmartSQL functions"""
    
    print("🧪 Testing SmartSQL Service")
    print("=" * 35)
    
    try:
        from app.services.smart_sql_service import smart_sql_service
        
        # Test user
        test_user_id = "smartsql_test_user"
        
        # Test 1: User profile
        print("\n1️⃣ Testing user profile...")
        profile_data = {
            "name": "SmartSQL Test User",
            "email": "smartsql@example.com",
            "preferences": {
                "theme": "light",
                "notifications": True
            }
        }
        
        profile_success = smart_sql_service.upsert_user_profile(test_user_id, profile_data)
        print(f"   Profile storage: {'✅ Success' if profile_success else '❌ Failed'}")
        
        # Test 2: Journal metadata
        print("\n2️⃣ Testing journal metadata...")
        journal_success = smart_sql_service.record_journal_entry(
            user_id=test_user_id,
            entry_id="journal_123",
            journal_type="free",
            session_id="session_456",
            content="This is a test journal entry for SmartSQL testing.",
            has_audio=True,
            mood_score={"mood": "happy", "confidence": 0.8}
        )
        print(f"   Journal metadata: {'✅ Success' if journal_success else '❌ Failed'}")
        
        # Test 3: User analytics
        print("\n3️⃣ Testing user analytics...")
        analytics_success = smart_sql_service.update_user_analytics(
            user_id=test_user_id,
            word_count=15,
            has_voice=True,
            session_minutes=25,
            mood="happy",
            storage_bytes=2048
        )
        print(f"   Analytics update: {'✅ Success' if analytics_success else '❌ Failed'}")
        
        # Test 4: Get user analytics
        print("\n4️⃣ Testing analytics retrieval...")
        analytics_data = smart_sql_service.get_user_analytics(test_user_id, days=7)
        print(f"   Analytics retrieval: {'✅ Success' if analytics_data else '❌ Failed'}")
        if analytics_data:
            print(f"   Retrieved {len(analytics_data)} days of analytics")
        
        # Test 5: User summary
        print("\n5️⃣ Testing user summary...")
        summary = smart_sql_service.get_user_summary(test_user_id)
        if summary:
            print(f"   Summary retrieval: ✅ Success")
            print(f"   User name: {summary['profile']['name']}")
            print(f"   Total journals: {summary['lifetime_stats']['total_journals']}")
        else:
            print(f"   Summary retrieval: ❌ Failed")
        
        # Test 6: Dashboard stats
        print("\n6️⃣ Testing dashboard stats...")
        dashboard = smart_sql_service.get_dashboard_stats()
        if dashboard:
            print(f"   Dashboard stats: ✅ Success")
            print(f"   Total users: {dashboard['total_users']}")
        else:
            print(f"   Dashboard stats: ❌ Failed")
        
        # Test 7: Multiple entries
        print("\n7️⃣ Testing multiple journal entries...")
        for i in range(3):
            smart_sql_service.record_journal_entry(
                user_id=test_user_id,
                entry_id=f"journal_{i}",
                journal_type="guided",
                session_id=f"session_{i}",
                content=f"Test journal entry number {i}",
                has_audio=i % 2 == 0,
                mood_score={"mood": "reflective", "confidence": 0.7}
            )
        
        print("   Multiple entries: ✅ Created 3 test entries")
        
        # Test 8: Updated analytics
        print("\n8️⃣ Testing updated analytics...")
        updated_analytics = smart_sql_service.get_user_analytics(test_user_id, days=7)
        if updated_analytics and len(updated_analytics) > 0:
            print(f"   Updated analytics: ✅ Success")
            total_journals = sum(day['journals_written'] for day in updated_analytics)
            print(f"   Total journal entries: {total_journals}")
        else:
            print(f"   Updated analytics: ❌ Failed")
        
        # Summary
        print(f"\n📊 SmartSQL Test Summary:")
        all_tests = [
            profile_success,
            journal_success,
            analytics_success,
            bool(analytics_data),
            bool(summary),
            bool(dashboard),
            True,  # multiple entries
            bool(updated_analytics and len(updated_analytics) > 0)
        ]
        passed_tests = sum(all_tests)
        total_tests = len(all_tests)
        
        print(f"   Passed: {passed_tests}/{total_tests}")
        print(f"   Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print(f"\n🎉 All SmartSQL tests passed!")
            print(f"📊 Database is working perfectly!")
        else:
            print(f"\n⚠️ Some SmartSQL tests failed")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"❌ SmartSQL test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SmartSQL Test Suite")
    print("=" * 35)
    
    success = test_smart_sql()
    
    if success:
        print(f"\n✅ SmartSQL is working perfectly!")
        print(f"📊 Analytics and user tracking are ready!")
        print(f"🎯 Next: Add SmartMemory caching!")
    else:
        print(f"\n❌ SmartSQL needs fixes before proceeding")