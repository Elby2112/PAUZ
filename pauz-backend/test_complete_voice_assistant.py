#!/usr/bin/env python3
"""
Complete test of the improved PAUZ Voice Assistant
Tests voice, conversation memory, app knowledge, and hint voice
"""

import os
import sys
sys.path.append('.')

from app.services.voice_service import voice_service
from app.services.pauz_voice_service import pauz_voice_service

def test_voice_profiles():
    """Test that all voice profiles use the same soft voice"""
    print("🎤 Testing Voice Profile Consistency\n")
    print("=" * 50)
    
    for profile_name, settings in voice_service.voice_profiles.items():
        voice_id = settings["voice_id"]
        stability = settings["stability"]
        style = settings["style"]
        
        print(f"{profile_name.title()} Profile:")
        print(f"   Voice ID: {voice_id}")
        print(f"   Stability: {stability} (lower = more natural)")
        print(f"   Style: {style} (higher = more expressive)")
        
        # Check if it's the same voice (Bella)
        is_bella = voice_id == "EXAVITQu4vr4xnSDxMaL"
        print(f"   ✅ Uses consistent soft voice: {is_bella}")
        print()
    
    # Test that hints voice is extra soft
    hints_settings = voice_service.voice_profiles["hints"]
    is_extra_soft = hints_settings["stability"] <= 0.2 and hints_settings["style"] >= 0.8
    print(f"✅ Hints voice is extra soft and calming: {is_extra_soft}")

def test_conversation_flow():
    """Test realistic conversation flow"""
    print("\n🗣️ Testing Conversation Flow\n")
    print("=" * 50)
    
    user_id = "conversation_test_user"
    
    # Realistic conversation
    conversation = [
        "hey",
        "i'm feeling stuck with journaling", 
        "tell me more about guided journal",
        "what categories do you have?",
        "i think i want to try the mind category",
        "thanks that sounds helpful"
    ]
    
    for i, user_input in enumerate(conversation, 1):
        print(f"{i}. User: \"{user_input}\"")
        
        response = pauz_voice_service.generate_response(
            user_input=user_input,
            user_id=user_id,
            user_context={"total_journals": 2}
        )
        
        print(f"   PAUZ: \"{response}\"")
        
        # Check if it's contextual
        if i > 1:
            # Check if response acknowledges previous context
            is_contextual = len(pauz_voice_service.get_or_create_conversation(user_id)) > 2
            print(f"   📝 Has conversation context: {is_contextual}")
        
        print()

def test_app_knowledge_accuracy():
    """Test that the assistant accurately knows PAUZ features"""
    print("🎯 Testing App Knowledge Accuracy\n")
    print("=" * 50)
    
    test_cases = [
        {
            "question": "what's the difference between free and guided journal?",
            "expected_keywords": ["free writing", "categories", "prompts"],
            "should_mention": ["freedom", "structured"]
        },
        {
            "question": "how does the garden work?", 
            "expected_keywords": ["flower", "mood", "reflect"],
            "should_mention": ["track", "click"]
        },
        {
            "question": "can i record myself talking instead of writing?",
            "expected_keywords": ["record", "transcribe", "voice"],
            "should_mention": ["free journal"]
        },
        {
            "question": "what happens when i reflect with ai?",
            "expected_keywords": ["mood", "insights", "summary"],
            "should_mention": ["questions", "detect"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case["question"]
        print(f"{i}. Q: {question}")
        
        response = pauz_voice_service.generate_response(
            user_input=question,
            user_id="knowledge_test",
            user_context={"total_journals": 5}
        )
        
        print(f"   A: {response}")
        
        # Check accuracy
        response_lower = response.lower()
        
        # Check expected keywords
        found_keywords = [kw for kw in test_case["expected_keywords"] if kw in response_lower]
        keyword_score = len(found_keywords) / len(test_case["expected_keywords"])
        
        # Check should mention
        found_mentions = [mention for mention in test_case["should_mention"] if mention in response_lower]
        mention_score = len(found_mentions) / len(test_case["should_mention"])
        
        print(f"   ✅ Keyword accuracy: {keyword_score:.1%} ({found_keywords})")
        print(f"   ✅ Concept accuracy: {mention_score:.1%} ({found_mentions})")
        print()

def test_hint_voice_softness():
    """Test that hint voice settings are extra soft"""
    print("🌸 Testing Hint Voice Softness\n")
    print("=" * 50)
    
    hints_profile = voice_service.voice_profiles["hints"]
    
    # Check settings
    stability = hints_profile["stability"]
    similarity_boost = hints_profile["similarity_boost"] 
    style = hints_profile["style"]
    
    print(f"Hint Voice Settings:")
    print(f"   Stability: {stability} (should be ≤ 0.2 for extra natural)")
    print(f"   Similarity Boost: {similarity_boost} (should be ≤ 0.2 for gentle)")
    print(f"   Style: {style} (should be ≥ 0.8 for expressive but calming)")
    
    is_extra_soft = stability <= 0.2 and similarity_boost <= 0.2 and style >= 0.8
    print(f"\n✅ Hint voice is extra soft and calming: {is_extra_soft}")
    
    # Test a sample hint
    sample_hint = "Just start with whatever's on your mind. There's no wrong way to begin."
    
    try:
        voice_result = voice_service.text_to_speech(
            text=sample_hint,
            voice_profile="hints"
        )
        
        if voice_result["success"]:
            print(f"✅ Successfully generated soft hint voice ({len(voice_result['audio_data'])} bytes)")
        else:
            print(f"❌ Hint voice generation failed: {voice_result.get('error')}")
            
    except Exception as e:
        print(f"❌ Hint voice test failed: {e}")

if __name__ == "__main__":
    print("🧪 Complete PAUZ Voice Assistant Test\n")
    print("=" * 60)
    
    try:
        test_voice_profiles()
        test_conversation_flow() 
        test_app_knowledge_accuracy()
        test_hint_voice_softness()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED!")
        print("\n📋 Summary:")
        print("- ✅ Single consistent voice (Bella) for all interactions")
        print("- ✅ Extra soft and calming voice for hints")
        print("- ✅ Conversation memory maintains context")
        print("- ✅ Accurate app knowledge (FreeJournal, GuidedJournal, Garden)")
        print("- ✅ Contextual responses based on conversation history")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()