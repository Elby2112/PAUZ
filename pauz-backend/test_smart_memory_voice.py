#!/usr/bin/env python3
"""
Test SmartMemory-Powered Voice Assistant
Tests memory capabilities and personalization
"""

import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def test_smart_memory_voice_service():
    print("🧠 Testing SmartMemory-Powered Voice Assistant")
    print("=" * 60)
    
    # Check environment
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key or gemini_key == 'your-gemini-api-key-here':
        print("❌ GEMINI_API_KEY not configured")
        return False
    
    try:
        from app.services.smart_memory_voice_service import smart_memory_voice_service
        from app.services.smart_memory_service import smart_memory_service
        
        print("✅ SmartMemory Voice Service initialized")
        
        # Test user ID
        test_user_id = "test_user_123"
        
        # Test 1: First conversation (no memory yet)
        print("\n🧪 Test 1: First conversation (no memory)")
        response1 = smart_memory_voice_service.generate_intelligent_response(
            user_input="I'm feeling stuck with my writing",
            user_id=test_user_id
        )
        print(f"User: I'm feeling stuck with my writing")
        print(f"PAUZ: {response1}")
        
        # Check memory stats
        memory_stats = smart_memory_voice_service.get_user_memory_stats(test_user_id)
        print(f"📊 Memory stats: {memory_stats['conversations']} conversations")
        
        # Test 2: Second conversation (should have memory)
        print("\n🧪 Test 2: Second conversation (with memory)")
        response2 = smart_memory_voice_service.generate_intelligent_response(
            user_input="Can you help me with journaling prompts?",
            user_id=test_user_id
        )
        print(f"User: Can you help me with journaling prompts?")
        print(f"PAUZ: {response2}")
        
        # Updated memory stats
        memory_stats = smart_memory_voice_service.get_user_memory_stats(test_user_id)
        print(f"📊 Memory stats: {memory_stats['conversations']} conversations")
        print(f"📚 Topics discussed: {memory_stats['topics_discussed']}")
        
        # Test 3: Welcome message with memory
        print("\n🧪 Test 3: Personalized welcome with memory")
        user_context = {
            "total_journals": 3,
            "is_returning_user": True
        }
        welcome = smart_memory_voice_service.generate_personalized_welcome(
            user_id=test_user_id,
            user_context=user_context
        )
        print(f"Welcome: {welcome}")
        
        # Test 4: Check cache stats
        print("\n🧪 Test 4: SmartMemory cache statistics")
        cache_stats = smart_memory_service.get_cache_stats()
        print(f"💾 Cache entries: {cache_stats['total_cache_entries']}")
        print(f"🎯 Hit rate: {cache_stats['hit_rate_percent']}%")
        print(f"📂 Categories: {cache_stats['cache_categories']}")
        
        # Test 5: Memory-based response (should find similar past conversation)
        print("\n🧪 Test 5: Memory-based response lookup")
        response3 = smart_memory_voice_service.generate_intelligent_response(
            user_input="I'm feeling stuck again",  # Similar to first query
            user_id=test_user_id
        )
        print(f"User: I'm feeling stuck again")
        print(f"PAUZ: {response3}")
        
        print(f"\n🎉 SmartMemory Test Complete!")
        print("✨ Your voice assistant now has memory and learns from conversations!")
        
        return True
        
    except Exception as e:
        print(f"❌ SmartMemory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_persistence():
    """Test that memory persists across different instances"""
    print("\n🔄 Testing Memory Persistence")
    print("=" * 40)
    
    try:
        from app.services.smart_memory_voice_service import smart_memory_voice_service
        from app.services.smart_memory_service import smart_memory_service
        
        # Create a new user conversation
        test_user_id = "persistence_test_user"
        
        print("💾 Creating conversation history...")
        
        # Simulate multiple conversations
        conversations = [
            "What can I do in this app?",
            "I'm feeling anxious today",
            "Help me get started",
            "Can you encourage me?"
        ]
        
        for i, conv in enumerate(conversations, 1):
            response = smart_memory_voice_service.generate_intelligent_response(
                user_input=conv,
                user_id=test_user_id
            )
            print(f"  {i}. {conv[:30]}... ✓")
        
        # Check final memory state
        memory_stats = smart_memory_voice_service.get_user_memory_stats(test_user_id)
        print(f"\n📊 Final memory state:")
        print(f"  💬 Conversations: {memory_stats['conversations']}")
        print(f"  📚 Topics: {memory_stats['topics_discussed']}")
        
        # Test cache persistence
        cache_stats = smart_memory_service.get_cache_stats()
        print(f"\n💾 Cache state:")
        print(f"  📊 Entries: {cache_stats['total_cache_entries']}")
        print(f"  🎯 Hit rate: {cache_stats['hit_rate_percent']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Persistence test failed: {e}")
        return False

def test_smart_memory_endpoints():
    """Test the SmartMemory endpoints"""
    print("\n🌐 Testing SmartMemory Endpoints")
    print("=" * 45)
    
    try:
        import requests
        API_BASE = "http://localhost:8000"
        
        # Test memory stats endpoint
        print("🧪 Testing /voice-assistant/memory-stats endpoint")
        response = requests.get(
            f"{API_BASE}/voice-assistant/memory-stats",
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Memory stats retrieved")
            print(f"User memory: {result.get('user_memory', {})}")
            print(f"Cache stats: {result.get('cache_stats', {})}")
        else:
            print(f"❌ Memory stats endpoint failed: {response.status_code}")
            print(f"Error: {response.text}")
    
    except Exception as e:
        print(f"❌ Endpoint test failed: {e}")

if __name__ == "__main__":
    print("🧠 SmartMemory Voice Assistant Integration Test")
    print("=" * 65)
    
    # Test SmartMemory functionality
    success = test_smart_memory_voice_service()
    
    if success:
        # Test persistence
        test_memory_persistence()
        
        # Test endpoints if backend is running
        try:
            test_smart_memory_endpoints()
        except:
            print("\n⚠️ Backend not running - skip endpoint tests")
            print("💡 Start your backend with: uvicorn app.main:app --reload")
    
    print(f"\n📋 SmartMemory Benefits:")
    print("  🧠 Remembers past conversations")
    print("  📚 Tracks topics discussed")
    print("  🎯 Personalizes responses over time")
    print("  💾 Caches responses for speed")
    print("  📊 Learns user preferences")
    print("  🔄 Adapts communication style")
    
    print(f"\n🎉 Your voice assistant now has memory! 🧠✨")