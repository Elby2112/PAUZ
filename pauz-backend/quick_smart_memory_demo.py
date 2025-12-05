#!/usr/bin/env python3
"""
Quick SmartMemory Test - Shows key functionality
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def quick_smart_memory_demo():
    print("🧠 SmartMemory Voice Assistant - Quick Demo")
    print("=" * 50)
    
    try:
        from app.services.smart_memory_voice_service import smart_memory_voice_service
        from app.services.smart_memory_service import smart_memory_service
        
        test_user_id = "demo_user"
        
        print("🚀 Initializing SmartMemory Voice Service...")
        
        # Demo 1: First interaction
        print("\n1️⃣ First interaction:")
        response1 = smart_memory_voice_service.generate_intelligent_response(
            user_input="I'm feeling stuck",
            user_id=test_user_id
        )
        print(f"   User: I'm feeling stuck")
        print(f"   PAUZ: {response1[:60]}...")
        
        # Check memory
        memory_stats = smart_memory_voice_service.get_user_memory_stats(test_user_id)
        print(f"   📊 Memory: {memory_stats['conversations']} conversations saved")
        
        # Demo 2: Second interaction (should learn from first)
        print("\n2️⃣ Second interaction:")
        response2 = smart_memory_voice_service.generate_intelligent_response(
            user_input="Help me start journaling",
            user_id=test_user_id
        )
        print(f"   User: Help me start journaling")
        print(f"   PAUZ: {response2[:60]}...")
        
        # Updated memory
        memory_stats = smart_memory_voice_service.get_user_memory_stats(test_user_id)
        print(f"   📊 Memory: {memory_stats['conversations']} conversations saved")
        print(f"   📚 Topics: {memory_stats['topics_discussed']}")
        
        # Demo 3: Personalized welcome
        print("\n3️⃣ Personalized welcome:")
        welcome = smart_memory_voice_service.generate_personalized_welcome(
            user_id=test_user_id,
            user_context={"total_journals": 5, "is_returning_user": True}
        )
        print(f"   🎉 Welcome: {welcome[:60]}...")
        
        # Demo 4: Cache stats
        print("\n4️⃣ SmartMemory performance:")
        cache_stats = smart_memory_service.get_cache_stats()
        print(f"   💾 Cache entries: {cache_stats['total_cache_entries']}")
        print(f"   🎯 Hit rate: {cache_stats['hit_rate_percent']:.1f}%")
        print(f"   📂 Categories: {cache_stats['cache_categories']}")
        
        print(f"\n✅ SmartMemory Demo Complete!")
        print(f"🧠 Your voice assistant now remembers and learns!")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    quick_smart_memory_demo()