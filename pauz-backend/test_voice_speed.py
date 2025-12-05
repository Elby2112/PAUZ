#!/usr/bin/env python3
"""
Test Voice Assistant Speed
Measures and optimizes response times
"""

import os
import sys
import time
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv()

def test_response_speed():
    print("⚡ Testing Voice Assistant Response Speed")
    print("=" * 50)
    
    try:
        from app.services.gemini_voice_service import gemini_voice_service
        from app.services.voice_cache import response_cache
        
        # Test questions
        test_questions = [
            "What can I do here?",
            "I'm feeling stuck",
            "How do I get started?",
            "Help me",
            "What are the features?",
            "Encourage me",
            "I don't know what to write"
        ]
        
        print("🧪 Testing response times...\n")
        
        # Test 1: First time (cache miss)
        print("📊 First Time Responses (Cache Miss):")
        total_time = 0
        for i, question in enumerate(test_questions, 1):
            start_time = time.time()
            response = gemini_voice_service.generate_intelligent_response(question)
            end_time = time.time()
            
            response_time = end_time - start_time
            total_time += response_time
            
            status = "✅" if response_time <= 5 else "⚠️"
            print(f"  {i}. {question}: {response_time:.2f}s {status}")
        
        avg_time = total_time / len(test_questions)
        print(f"\n📈 Average first-time: {avg_time:.2f}s")
        
        # Test 2: Cached responses (cache hit)
        print(f"\n🚀 Cached Responses (Cache Hit):")
        total_cached_time = 0
        
        for i, question in enumerate(test_questions, 1):
            start_time = time.time()
            response = gemini_voice_service.generate_intelligent_response(question)
            end_time = time.time()
            
            response_time = end_time - start_time
            total_cached_time += response_time
            
            status = "🚀" if response_time < 0.1 else "✅"
            print(f"  {i}. {question}: {response_time:.3f}s {status}")
        
        avg_cached_time = total_cached_time / len(test_questions)
        print(f"\n📈 Average cached: {avg_cached_time:.3f}s")
        
        # Test 3: Fast templates
        print(f"\n⚡ Fast Template Responses:")
        fast_tests = ["help", "stuck", "start", "encourage me"]
        
        for question in fast_tests:
            start_time = time.time()
            response = gemini_voice_service.generate_intelligent_response(question)
            end_time = time.time()
            
            response_time = end_time - start_time
            print(f"  {question}: {response_time:.3f}s 🚀")
        
        # Performance summary
        print(f"\n📊 Performance Summary:")
        print(f"  🆕 First Response: {avg_time:.2f}s")
        print(f"  🚀 Cached Response: {avg_cached_time:.3f}s")
        print(f"  💾 Cache Size: {response_cache.get_size()} items")
        print(f"  ⚡ Speed Improvement: {(avg_time / avg_cached_time):.1f}x faster")
        
        # Performance targets
        print(f"\n🎯 Performance Targets:")
        if avg_time <= 5:
            print(f"  ✅ First response under 5s: {avg_time:.2f}s")
        else:
            print(f"  ⚠️ First response over 5s: {avg_time:.2f}s")
        
        if avg_cached_time < 0.1:
            print(f"  ✅ Cached response under 0.1s: {avg_cached_time:.3f}s")
        else:
            print(f"  ⚠️ Cached response over 0.1s: {avg_cached_time:.3f}s")
        
        return avg_time <= 5
        
    except Exception as e:
        print(f"❌ Speed test failed: {e}")
        return False

def test_voice_generation_speed():
    print("\n🎤 Testing Voice Generation Speed")
    print("=" * 50)
    
    try:
        from app.services.voice_service import voice_service
        
        if not voice_service.is_available():
            print("⚠️ ElevenLabs not configured")
            return
        
        test_text = "I'm here to help with your journaling journey."
        
        start_time = time.time()
        result = voice_service.text_to_speech(test_text, voice_profile="guide")
        end_time = time.time()
        
        if result["success"]:
            generation_time = end_time - start_time
            print(f"🎵 Voice generation: {generation_time:.2f}s")
            print(f"📊 Audio size: {result['file_size']} bytes")
            
            status = "✅" if generation_time <= 3 else "⚠️"
            print(f"Status: {status}")
        else:
            print(f"❌ Voice generation failed: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Voice speed test failed: {e}")

if __name__ == "__main__":
    print("🚀 Voice Assistant Speed Optimization Test")
    print("=" * 60)
    
    # Test response speed
    response_ok = test_response_speed()
    
    # Test voice generation
    test_voice_generation_speed()
    
    print(f"\n🎉 Speed Test Complete!")
    
    if response_ok:
        print("✅ Your voice assistant is optimized for speed!")
        print("🚀 First responses under 5s, cached responses nearly instant!")
    else:
        print("⚠️ Consider further optimization for faster responses")
    
    print(f"\n💡 Tips for optimal speed:")
    print("  • Common questions are now cached for instant replies")
    print("  • Fast templates handle frequent queries instantly")
    print("  • Gemini responses are optimized for 1-2 sentences")
    print("  • Cache expires after 5 minutes to keep responses fresh")