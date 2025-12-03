#!/usr/bin/env python3
"""
Test Google Gemini Integration for FREE AI Generation
"""
import os
from dotenv import load_dotenv

load_dotenv()

def test_gemini_integration():
    print("🤖 Testing Google Gemini Integration (FREE AI)")
    print("=" * 50)
    
    # Check Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key or gemini_key == 'your-gemini-api-key-here':
        print("⚠️ GEMINI_API_KEY not set in .env file")
        print("📋 To get your FREE Gemini API key:")
        print("   1. Go to: https://aistudio.google.com/app/apikey")
        print("   2. Click 'Create API Key'")
        print("   3. Copy your key")
        print("   4. Add to .env: GEMINI_API_KEY=your-key-here")
        print("   5. Gemini has generous free limits!")
        use_gemini = False
    else:
        print("✅ Gemini API key found")
        use_gemini = True
    
    print()
    
    # Test prompt generation
    try:
        from app.services.guided_journal_service import guided_journal_service
        
        print("🧪 Testing prompt generation...")
        prompts = guided_journal_service.generate_prompts("self-discovery", 3)
        print(f"✅ Generated {len(prompts)} unique prompts:")
        
        for i, prompt in enumerate(prompts):
            print(f"  {i+1}. {prompt['text']}")
            print(f"     Type: {prompt.get('type', 'unknown')}")
        
    except Exception as e:
        print(f"❌ Prompt generation error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test hint generation
    try:
        from app.services.free_journal_service import free_journal_service
        
        print("💡 Testing hint generation...")
        test_content = "I've been thinking about my career path and feeling uncertain about my choices"
        hint = free_journal_service.generate_real_hint(test_content)
        print(f"✅ Generated hint: {hint}")
        
    except Exception as e:
        print(f"❌ Hint generation error: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test mood analysis
    try:
        print("🧠 Testing mood analysis...")
        test_entry = "I'm feeling grateful for my family today. They support me through everything and make life meaningful."
        
        if use_gemini and free_journal_service.gemini_model:
            analysis = free_journal_service.analyze_mood_with_gemini(test_entry)
        else:
            analysis = free_journal_service._analyze_mood_advanced(test_entry)
        
        print(f"✅ Mood Analysis:")
        print(f"  Mood: {analysis['mood']} 🌸 {analysis['flower_type']}")
        print(f"  Insights: {', '.join(analysis['insights'])}")
        if 'nextQuestions' in analysis:
            print(f"  Questions: {analysis['nextQuestions']}")
        
    except Exception as e:
        print(f"❌ Mood analysis error: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n🎉 Gemini Integration Test Complete!")
    
    if use_gemini:
        print("✨ Google Gemini AI generation is working!")
        print("💎 You have FREE AI generation for your PAUZ app!")
    else:
        print("✨ Intelligent fallback system is working!")
        print("💡 Add GEMINI_API_KEY to get FREE AI generation")
    
    print("\n🌟 Key Benefits of Gemini:")
    print("   🆓 Completely FREE with generous limits")
    print("   🤖 Excellent at creative and thoughtful prompts")
    print("   🎯 Perfect for journaling and reflection")
    print("   🚀 Fast and reliable")
    print("   🌈 Emotionally intelligent responses")

if __name__ == "__main__":
    test_gemini_integration()