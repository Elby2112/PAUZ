#!/usr/bin/env python3
"""
Test the improved PAUZ Voice Assistant with conversation memory and app knowledge
"""

import os
import sys
sys.path.append('.')

from app.services.pauz_voice_service import pauz_voice_service

def test_conversation_memory():
    """Test that the voice assistant maintains conversation context"""
    
    print("🧠 Testing PAUZ Voice Assistant with Conversation Memory\n")
    print("=" * 70)
    
    user_id = "test_user_123"
    
    # Simulate a conversation
    conversation_flow = [
        "hi there",
        "what can I do here?", 
        "tell me about free journal",
        "what if I get stuck?",
        "thanks that helps"
    ]
    
    for i, user_input in enumerate(conversation_flow, 1):
        print(f"\n{i}. User: \"{user_input}\"")
        
        try:
            response = pauz_voice_service.generate_response(
                user_input=user_input,
                user_id=user_id,
                user_context={"total_journals": 0}
            )
            print(f"   PAUZ: \"{response}\"")
            
            # Show conversation history length
            conversation = pauz_voice_service.get_or_create_conversation(user_id)
            print(f"   📝 Conversation history: {len(conversation)} messages")
            
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 Testing App Knowledge")
    
    # Test specific app feature questions
    app_questions = [
        "what are the guided journal categories?",
        "how does the garden work?",
        "can I record myself talking?",
        "what happens when I reflect with AI?"
    ]
    
    for i, question in enumerate(app_questions, 1):
        print(f"\n{i}. Question: \"{question}\"")
        
        try:
            response = pauz_voice_service.generate_response(
                user_input=question,
                user_id="knowledge_test_user",
                user_context={"total_journals": 5}
            )
            print(f"   Response: \"{response}\"")
            
            # Check if response contains expected keywords
            if "categories" in question.lower():
                has_categories = any(cat in response.lower() for cat in ["mind", "body", "heart", "friends", "family"])
                print(f"   ✅ Mentions categories: {has_categories}")
            
            if "garden" in question.lower():
                has_garden = "flower" in response.lower() or "mood" in response.lower()
                print(f"   ✅ Explains garden: {has_garden}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("🎤 Testing Welcome Messages")
    
    # Test welcome for new vs returning user
    for user_type, user_context in [("new", {"total_journals": 0, "is_returning_user": False}), 
                                   ("returning", {"total_journals": 10, "is_returning_user": True})]:
        print(f"\n{user_type.title()} user welcome:")
        
        try:
            welcome = pauz_voice_service.generate_welcome(
                user_id=f"{user_type}_user",
                user_context=user_context
            )
            print(f"   \"{welcome}\"")
            
            # Check if welcome is appropriate
            if user_type == "returning":
                is_returning_welcome = any(word in welcome.lower() for word in ["back", "continue", "again"])
                print(f"   ✅ Recognizes returning user: {is_returning_welcome}")
            else:
                is_new_welcome = any(word in welcome.lower() for word in ["welcome", "start", "begin"])
                print(f"   ✅ Welcomes new user: {is_new_welcome}")
                
        except Exception as e:
            print(f"   ERROR: {e}")
    
    print("\n" + "=" * 70)
    print("✅ PAUZ Voice Assistant Testing Complete!")
    
    # Show final conversation state
    final_conversation = pauz_voice_service.get_or_create_conversation(user_id)
    print(f"\n📊 Final conversation stats for {user_id}:")
    print(f"   Total messages: {len(final_conversation)}")
    print(f"   User messages: {len([msg for msg in final_conversation if msg['role'] == 'user'])}")
    print(f"   Assistant messages: {len([msg for msg in final_conversation if msg['role'] == 'assistant'])}")

if __name__ == "__main__":
    test_conversation_memory()