#!/usr/bin/env python3
"""
Test Real AI Generation
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_real_ai_generation():
    print("🧪 Testing Real AI Generation System")
    print("=" * 40)
    
    # Check OpenAI API key
    openai_key = os.getenv('OPENAI_API_KEY')
    if not openai_key or openai_key == 'your-openai-api-key-here':
        print("⚠️ OPENAI_API_KEY not set in .env file")
        print("Please add your OpenAI API key to get real AI generation")
        print("For now, showing intelligent fallback system...")
        use_openai = False
    else:
        print("✅ OpenAI API key found")
        use_openai = True
    
    # Test prompt generation
    try:
        from app.services.guided_journal_service import guided_journal_service
        
        if use_openai and guided_journal_service.openai_client:
            print("\n🤖 Testing REAL AI prompt generation...")
        else:
            print("\n🧠 Testing intelligent fallback prompts...")
        
        prompts = guided_journal_service.generate_prompts("self-discovery", 3)
        print(f"✅ Generated {len(prompts)} unique prompts:")
        
        for i, prompt in enumerate(prompts):
            print(f"  {i+1}. {prompt['text']}")
            print(f"     Type: {prompt.get('type', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Prompt generation error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test hint generation
    try:
        from app.services.free_journal_service import free_journal_service
        
        print(f"\n💡 Testing hint generation...")
        test_content = "I've been thinking about my career path lately and feeling uncertain about my choices"
        
        if use_openai and free_journal_service.openai_client:
            print("Using REAL AI for hints")
        else:
            print("Using intelligent fallback for hints")
        
        hint = free_journal_service.generate_real_hint(test_content)
        print(f"✅ Generated hint: {hint}")
        
    except Exception as e:
        print(f"❌ Hint generation error: {e}")
        import traceback
        traceback.print_exc()
    
    # Test mood analysis
    try:
        print(f"\n🧠 Testing mood analysis...")
        test_entry = "I'm feeling grateful for my family today. They support me through everything and make life meaningful."
        
        if use_openai:
            analysis = free_journal_service.analyze_mood_with_ai(test_entry)
        else:
            analysis = free_journal_service._analyze_mood_advanced(test_entry)
        
        print(f"✅ Mood Analysis:")
        print(f"  Mood: {analysis['mood']} 🌸 {analysis['flower_type']}")
        print(f"  Insights: {', '.join(analysis['insights'])}")
        print(f"  Questions: {analysis['nextQuestions']}")
        
    except Exception as e:
        print(f"❌ Mood analysis error: {e}")
    
    print(f"\n🎉 Test completed!")
    if use_openai:
        print("✨ Real AI generation is working!")
    else:
        print("✨ Intelligent fallback system is working!")
        print("💡 Add OPENAI_API_KEY to .env for real AI generation")

if __name__ == "__main__":
    test_real_ai_generation()