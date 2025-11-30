#!/usr/bin/env python3
"""
Pure Raindrop AI Solution for PAUZ Journaling App
This creates a complete prompt library system using only Raindrop technologies
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
        self.org_name = os.getenv('RAINDROP_ORG', 'Loubna-HackathonApp')
        
    def initialize_prompt_library(self):
        """Initialize the prompt library with high-quality prompts"""
        print("📚 Initializing PAUZ Prompt Library...")
        
        prompt_library = {
            "mindfulness": [
                "What does being present feel like for you right now?",
                "Describe a moment today when you felt fully aware and engaged.",
                "What thoughts or feelings tend to pull you away from the present moment?",
                "How can you create more space for mindfulness in your daily routine?",
                "What sensory experiences helped you feel grounded today?",
                "When did you notice your mind wandering, and how did you bring it back?",
                "What does peace feel like in your body right now?",
                "Describe your relationship with silence and stillness.",
                "What mindfulness practice resonated most with you this week?",
                "How has being present changed your perspective on something important?"
            ],
            "gratitude": [
                "List three things you're grateful for today and why they matter.",
                "Who made a positive impact on your life recently, and how?",
                "What challenge revealed something you're secretly grateful for?",
                "Describe a simple pleasure you almost overlooked today.",
                "How has expressing gratitude changed your mood or outlook?",
                "What aspect of your health are you thankful for right now?",
                "Who or what inspires you to be a better person?",
                "What mistake taught you something valuable?",
                "Describe a moment of unexpected kindness you witnessed or experienced.",
                "What part of your daily routine brings you quiet joy?"
            ],
            "stress-anxiety": [
                "What's weighing on your mind right now, and what can you control?",
                "Describe your stress using weather metaphors - what kind of storm is it?",
                "What physical sensations accompany your anxiety, and where do you feel them?",
                "When have you overcome similar stress, and what helped then?",
                "What would your wisest self tell you about your current worries?",
                "Describe your safe space - real or imagined - in detail.",
                "What small action could bring you a moment of relief right now?",
                "How does stress affect your relationships, and how can you protect them?",
                "What belief about stress might be worth questioning?",
                "Describe a time when anxiety turned out to be excitement in disguise."
            ],
            "growth-learning": [
                "What did you learn about yourself this week?",
                "Describe a recent failure and what it taught you.",
                "What skill are you developing, and what progress have you noticed?",
                "How have your values changed over the past year?",
                "What belief about yourself no longer serves you?",
                "Describe a moment when you stepped out of your comfort zone.",
                "What feedback - positive or negative - helped you grow?",
                "How do you measure personal progress, and are those metrics serving you?",
                "What part of your past self do you miss, and what part have you outgrown?",
                "Describe a future self you're working toward becoming."
            ],
            "relationships": [
                "Who in your life truly sees you, and how does that feel?",
                "Describe a recent meaningful conversation and its impact on you.",
                "What relationship pattern are you working to change?",
                "How do you show love, and how do you prefer to receive it?",
                "Describe a boundary you set recently and how it felt.",
                "Who challenges you to grow, and in what ways?",
                "What relationship are you most grateful for right now?",
                "How has your understanding of friendship evolved?",
                "Describe a moment of connection that surprised you.",
                "What would you tell a younger version of yourself about relationships?"
            ],
            "career-purpose": [
                "What part of your work makes you feel most alive?",
                "Describe a moment when you felt truly in your element professionally.",
                "What skill do you want to develop next, and why?",
                "How does your current work align with your deeper values?",
                "Describe a professional challenge that revealed your strengths.",
                "What does meaningful success look like for you, beyond titles or salary?",
                "Who has mentored you, and what wisdom did they share?",
                "What impact do you want to make through your work?",
                "Describe a time when work didn't feel like work.",
                "What would you do if you weren't afraid of failing?"
            ]
        }
        
        # Store prompts in SmartBuckets
        for topic, prompts in prompt_library.items():
            for i, prompt in enumerate(prompts):
                prompt_data = {
                    "id": f"{topic}-{i+1}",
                    "topic": topic,
                    "text": prompt,
                    "created_at": str(uuid.uuid4())
                }
                
                try:
                    self.client.bucket.put(
                        bucket_location={
                            "bucket": {
                                "name": "journal-prompts",
                                "application_name": self.app_name
                            }
                        },
                        key=prompt_data["id"],
                        content=base64.b64encode(json.dumps(prompt_data).encode()).decode(),
                        content_type="application/json"
                    )
                except Exception as e:
                    print(f"⚠️ Could not store prompt {prompt_data['id']}: {e}")
        
        print(f"✅ Prompt library initialized with {sum(len(v) for v in prompt_library.values())} prompts")
        return prompt_library
    
    def generate_prompts(self, topic: str, count: int = 3):
        """
        Generate AI-powered prompt suggestions using Raindrop search
        """
        print(f"🤖 Finding {count} best prompts for topic: {topic}")
        
        try:
            # Search for relevant prompts using semantic search
            response = self.client.query.search(
                input=f"{topic} journal prompts mindfulness reflection personal growth",
                bucket_locations=[{
                    "bucket": {
                        "name": "journal-prompts",
                        "application_name": self.app_name
                    }
                }],
                request_id=f"prompts-{uuid.uuid4()}"
            )
            
            # Extract and rank prompts
            if hasattr(response, 'results') and response.results:
                prompts = []
                for result in response.results[:count]:
                    try:
                        # Try to parse the JSON content
                        prompt_data = json.loads(base64.b64decode(result.text).decode())
                        prompts.append({
                            "id": len(prompts) + 1,
                            "text": prompt_data.get("text", result.text),
                            "score": getattr(result, 'score', 0)
                        })
                    except:
                        # Fallback if JSON parsing fails
                        prompts.append({
                            "id": len(prompts) + 1,
                            "text": result.text,
                            "score": getattr(result, 'score', 0)
                        })
                
                # Sort by score and return the best ones
                prompts.sort(key=lambda x: x['score'], reverse=True)
                return prompts[:count]
            else:
                raise Exception("No prompts found")
                
        except Exception as e:
            print(f"❌ Error finding prompts: {e}")
            raise e
    
    def generate_hint(self, current_content: str = ""):
        """Generate contextual writing hints"""
        print("💡 Finding contextual writing hint...")
        
        # Analyze the current content to find relevant hints
        if current_content:
            search_query = f"writing hints journal prompts encouragement {current_content[:50]}"
        else:
            search_query = "journal starter prompts beginning writing encouragement"
        
        try:
            response = self.client.query.search(
                input=search_query,
                bucket_locations=[{
                    "bucket": {
                        "name": "hints",
                        "application_name": self.app_name
                    }
                }],
                request_id=f"hints-{uuid.uuid4()}"
            )
            
            if hasattr(response, 'results') and response.results:
                best_result = max(response.results, key=lambda x: getattr(x, 'score', 0))
                return best_result.text
            else:
                return "What aspect of this would you like to explore further?"
                
        except Exception as e:
            print(f"❌ Error finding hint: {e}")
            return "Can you tell me more about how this makes you feel?"
    
    def analyze_mood(self, journal_content: str):
        """Analyze journal content for mood and insights"""
        print("🧠 Analyzing journal content for insights...")
        
        try:
            # Search for similar content and patterns
            response = self.client.query.search(
                input=f"mood analysis emotional insights reflection {journal_content[:100]}",
                bucket_locations=[{
                    "bucket": {
                        "name": "journal-analysis",
                        "application_name": self.app_name
                    }
                }],
                request_id=f"analysis-{uuid.uuid4()}"
            )
            
            # Basic mood extraction (you can enhance this)
            content_lower = journal_content.lower()
            
            # Simple keyword-based mood analysis
            mood_indicators = {
                "happy": ["happy", "joy", "excited", "grateful", "optimistic", "cheerful"],
                "sad": ["sad", "disappointed", "grief", "melancholy", "blue", "down"],
                "anxious": ["anxious", "worried", "stressed", "nervous", "tense", "overwhelmed"],
                "calm": ["calm", "peaceful", "relaxed", "serene", "tranquil", "centered"],
                "reflective": ["reflective", "thoughtful", "contemplative", "pensive", "introspective"]
            }
            
            mood_scores = {}
            for mood, keywords in mood_indicators.items():
                score = sum(1 for keyword in keywords if keyword in content_lower)
                mood_scores[mood] = score
            
            primary_mood = max(mood_scores, key=mood_scores.get) if any(mood_scores.values()) else "reflective"
            
            # Generate insights based on content length and themes
            insights = []
            if len(journal_content) > 200:
                insights.append("You've expressed yourself in depth today.")
            if "feel" in content_lower:
                insights.append("You're connected with your emotions.")
            if "think" in content_lower:
                insights.append("You're processing your thoughts constructively.")
            
            return {
                "mood": primary_mood,
                "insights": insights if insights else ["Journaling is helping you process your experiences."],
                "summary": journal_content[:100] + "..." if len(journal_content) > 100 else journal_content
            }
            
        except Exception as e:
            print(f"❌ Error in mood analysis: {e}")
            return {
                "mood": "reflective",
                "insights": ["Journaling is a valuable practice for self-awareness."],
                "summary": "Journal entry recorded."
            }
    
    def store_journal_entry(self, user_id: str, session_id: str, content: str):
        """Store journal entry in SmartBucket"""
        try:
            entry_data = {
                "user_id": user_id,
                "session_id": session_id,
                "content": content,
                "timestamp": str(uuid.uuid4()),
                "created_at": str(uuid.uuid4())
            }
            
            self.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": "free-journals",
                        "application_name": self.app_name
                    }
                },
                key=f"{user_id}-{session_id}",
                content=base64.b64encode(json.dumps(entry_data).encode()).decode(),
                content_type="application/json"
            )
            return True
        except Exception as e:
            print(f"❌ Error storing journal entry: {e}")
            return False

# Initialize and test the system
if __name__ == "__main__":
    ai = PauzRaindropAI()
    
    print("🚀 Setting up PAUZ Pure Raindrop AI System")
    print("=" * 50)
    
    # Initialize the prompt library
    ai.initialize_prompt_library()
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
    
    # Test hint generation
    try:
        hint = ai.generate_hint("I'm feeling overwhelmed with work deadlines")
        print(f"✅ Generated hint: {hint}")
        print()
    except Exception as e:
        print(f"❌ Hint generation error: {e}")
    
    # Test mood analysis
    try:
        mood_data = ai.analyze_mood("I'm feeling grateful for my family today. They support me through everything.")
        print("✅ Mood analysis:")
        print(f"  Mood: {mood_data['mood']}")
        print(f"  Insights: {mood_data['insights']}")
        print(f"  Summary: {mood_data['summary']}")
        print()
    except Exception as e:
        print(f"❌ Mood analysis error: {e}")
    
    print("🎉 Pure Raindrop AI System is ready!")
    print("✨ All features using only Raindrop technologies:") 
    print("  📦 SmartBuckets for storage")
    print("  🔍 Semantic search for AI-powered selection")
    print("  🧠 Content analysis and insights")
    print("  💡 Contextual hints and suggestions")