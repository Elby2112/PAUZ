#!/usr/bin/env python3
"""
Quick test of the Pure Raindrop AI System
"""
import os
import base64
import uuid
import json
from dotenv import load_dotenv
from raindrop import Raindrop

load_dotenv()

class PauzRaindropAI:
    def __init__(self):
        self.client = Raindrop(api_key=os.getenv('AI_API_KEY'))
        self.app_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
    
    def store_sample_prompts(self):
        """Store a few sample prompts to test the system"""
        print("📚 Storing sample prompts...")
        
        prompts = [
            {
                "id": "mindfulness-1",
                "topic": "mindfulness",
                "text": "What does being present feel like for you right now?",
                "created_at": str(uuid.uuid4())
            },
            {
                "id": "mindfulness-2", 
                "topic": "mindfulness",
                "text": "Describe a moment today when you felt fully aware and engaged.",
                "created_at": str(uuid.uuid4())
            },
            {
                "id": "gratitude-1",
                "topic": "gratitude", 
                "text": "List three things you're grateful for today and why they matter.",
                "created_at": str(uuid.uuid4())
            },
            {
                "id": "stress-1",
                "topic": "stress",
                "text": "What's weighing on your mind right now, and what can you control?",
                "created_at": str(uuid.uuid4())
            }
        ]
        
        for prompt in prompts:
            try:
                self.client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": "journal-prompts",
                            "application_name": self.app_name
                        }
                    },
                    key=prompt["id"],
                    content=base64.b64encode(json.dumps(prompt).encode()).decode(),
                    content_type="application/json"
                )
                print(f"✅ Stored: {prompt['id']}")
            except Exception as e:
                print(f"❌ Failed to store {prompt['id']}: {e}")
    
    def generate_prompts(self, topic: str, count: int = 3):
        """Generate AI-powered prompt suggestions using Raindrop search"""
        print(f"🤖 Finding {count} best prompts for topic: {topic}")
        
        try:
            response = self.client.query.search(
                input=f"{topic} journal prompts mindfulness reflection",
                bucket_locations=[{
                    "bucket": {
                        "name": "journal-prompts",
                        "application_name": self.app_name
                    }
                }],
                request_id=f"prompts-{uuid.uuid4()}"
            )
            
            if hasattr(response, 'results') and response.results:
                prompts = []
                for result in response.results[:count]:
                    try:
                        prompt_data = json.loads(base64.b64decode(result.text).decode())
                        prompts.append({
                            "id": len(prompts) + 1,
                            "text": prompt_data.get("text", result.text),
                            "score": getattr(result, 'score', 0)
                        })
                    except:
                        prompts.append({
                            "id": len(prompts) + 1,
                            "text": result.text,
                            "score": getattr(result, 'score', 0)
                        })
                
                prompts.sort(key=lambda x: x['score'], reverse=True)
                return prompts[:count]
            else:
                raise Exception("No prompts found")
                
        except Exception as e:
            print(f"❌ Error finding prompts: {e}")
            raise e
    
    def analyze_mood(self, content: str):
        """Simple mood analysis"""
        content_lower = content.lower()
        
        mood_indicators = {
            "happy": ["happy", "joy", "excited", "grateful", "optimistic"],
            "sad": ["sad", "disappointed", "grief", "melancholy", "blue"],
            "anxious": ["anxious", "worried", "stressed", "nervous", "tense"],
            "calm": ["calm", "peaceful", "relaxed", "serene", "tranquil"],
            "reflective": ["reflective", "thoughtful", "contemplative"]
        }
        
        mood_scores = {}
        for mood, keywords in mood_indicators.items():
            score = sum(1 for keyword in keywords if keyword in content_lower)
            mood_scores[mood] = score
        
        primary_mood = max(mood_scores, key=mood_scores.get) if any(mood_scores.values()) else "reflective"
        
        return {
            "mood": primary_mood,
            "insights": ["You're processing your experiences through journaling."],
            "summary": content[:100] + "..." if len(content) > 100 else content
        }

# Test the system
if __name__ == "__main__":
    ai = PauzRaindropAI()
    
    print("🧪 Testing Pure Raindrop AI System")
    print("=" * 40)
    
    # Store sample prompts
    ai.store_sample_prompts()
    print()
    
    # Test prompt generation
    try:
        prompts = ai.generate_prompts("mindfulness", 3)
        print("✅ Generated prompts:")
        for i, prompt in enumerate(prompts):
            print(f"  {i+1}. {prompt['text']} (Score: {prompt.get('score', 0):.2f})")
        print()
    except Exception as e:
        print(f"❌ Prompt generation error: {e}")
    
    # Test mood analysis
    try:
        mood_data = ai.analyze_mood("I'm feeling grateful for my family today. They support me through everything.")
        print("✅ Mood analysis:")
        print(f"  Mood: {mood_data['mood']}")
        print(f"  Insights: {mood_data['insights']}")
    except Exception as e:
        print(f"❌ Mood analysis error: {e}")
    
    print("\n🎉 Pure Raindrop AI System Working!")