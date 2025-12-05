"""
Casual Friendly Voice Assistant
Actually conversational - like talking to a friend who knows the app
"""

import os
import json
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

from app.services.smart_memory_service import smart_memory_service
from app.services.voice_cache import response_cache

class CasualVoiceService:
    """Voice assistant that sounds like a friend, not a robot"""
    
    def __init__(self):
        # Initialize Gemini with minimal restrictions
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key or self.gemini_api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY not configured")
        
        try:
            genai.configure(api_key=self.gemini_api_key)
            # Use gemini-1.5-flash which is available
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            print("✅ Casual Voice Assistant initialized")
        except Exception as e:
            print(f"⚠️ Gemini failed, using fallback mode: {e}")
            self.model = None
    
    def generate_casual_response(
        self, 
        user_input: str, 
        user_id: str,
        user_context: Optional[Dict] = None
    ) -> str:
        """
        Generate actually conversational response like a friend would
        MORE VARIETY - less caching, more dynamic responses
        """
        
        # Skip cache for common conversational phrases to ensure variety
        input_lower = user_input.lower().strip()
        skip_cache_phrases = ["hi", "hello", "hey", "how are you", "what's up", "help", "stuck"]
        should_skip_cache = any(phrase in input_lower for phrase in skip_cache_phrases)
        
        # Only check cache for specific, non-conversational queries
        if not should_skip_cache:
            cached = response_cache.get(user_input, user_context)
            if cached and len(cached) > 20:  # Only use substantial cached responses
                return cached
        
        # 2. Try Gemini with a super casual prompt - add variety
        if self.model:
            try:
                casual_response = self._ask_gemini_casually(user_input, user_context, user_id)
                if casual_response and len(casual_response) > 10:
                    # Only cache longer, meaningful responses
                    if not should_skip_cache:
                        response_cache.set(user_input, casual_response, user_context)
                    self._save_to_memory(user_id, user_input, casual_response)
                    return casual_response
            except Exception as e:
                print(f"🤷 Gemini being difficult: {e}")
        
        # 3. Fallback to genuinely friendly responses with more variety
        friendly_response = self._get_friendly_fallback(user_input, user_context)
        if not should_skip_cache:
            response_cache.set(user_input, friendly_response, user_context)
        self._save_to_memory(user_id, user_input, friendly_response)
        return friendly_response
    
    def _ask_gemini_casually(self, user_input: str, user_context: Optional[Dict], user_id: str) -> Optional[str]:
        """Ask Gemini to be genuinely casual and friendly"""
        
        # Add variety to prompts based on user input
        import random
        
        prompt_variations = [
            f"""You're PAUZ, a warm and friendly journaling buddy. Someone just said: "{user_input}"

Respond like a real friend - casual, supportive, maybe even a little playful. Use contractions (you're, wanna, kinda). Keep it to 1-2 sentences max.

If they seem stressed: "Ugh, that sounds rough. Wanna write about it?"
If they're happy: "OMG that's amazing! You should totally capture this feeling!"
If they need help: "Hey! So you can free write, do some prompts, or track your mood. What feels good?"

Be natural and warm, not like an AI assistant.""",
            
            f"""Imagine you're texting with a friend who's using a journaling app. They just wrote: "{user_input}"

Respond in a super casual, supportive way - like you would text a good friend. Use emojis if it feels natural. One sentence is perfect!

Match their energy: if they're excited, be excited! If they're down, be gentle.
Always guide them toward journaling in a natural way.""",
            
            f"""You're a chill journaling buddy named PAUZ. Your friend just told you: "{user_input}"

Respond like you would to a close friend - super casual, maybe a little fun, always supportive. Don't sound like a therapist or an AI.

Keep it short and sweet (1-2 sentences). If they ask for help, mention the options: free writing, guided prompts, or mood tracking."""
        ]
        
        simple_prompt = random.choice(prompt_variations)
        
        try:
            response = self.model.generate_content(simple_prompt)
            
            # Handle the response properly
            if response.text and response.text.strip():
                return response.text.strip()
            else:
                return None
                
        except Exception as e:
            print(f"😅 Gemini trip: {e}")
            return None
    
    def _get_friendly_fallback(self, user_input: str, user_context: Optional[Dict]) -> str:
        """Actually friendly fallback responses - super casual with VARIETY"""
        
        import random
        input_lower = user_input.lower()
        
        # Stress/work stuff - multiple options
        if any(word in input_lower for word in ["tough day", "bad day", "work stress", "stressful", "overwhelmed"]):
            responses = [
                "Ugh, sounds rough. Wanna just vent about it? Free writing can help get it all out of your head.",
                "Oh no, tough days are the worst. Sometimes just writing it all out helps you breathe again.",
                "That sounds really stressful. Want to just brain dump? No pressure to make it pretty.",
                "Ugh, I hate those days. Wanna let it all out? Sometimes typing fast and messy actually helps."
            ]
            return random.choice(responses)
        
        # Relationship stuff
        if any(word in input_lower for word in ["argument", "fight", "partner", "relationship", "broke up"]):
            responses = [
                "Oh no, relationship stuff is the worst. Writing it down sometimes helps you see it clearer. Want to try?",
                "Ugh, I'm sorry. Relationships can be so complicated. Want to write through what happened?",
                "That sounds really hard. Sometimes getting thoughts out of your head and onto paper helps. Want to try?",
                "Oof, my heart. Want to write it out? Sometimes seeing the words helps sort the feelings."
            ]
            return random.choice(responses)
        
        # Anxiety/worry
        if any(word in input_lower for word in ["anxious", "worried", "scared", "nervous", "panic"]):
            responses = [
                "Anxiety is awful, but you've got this. Sometimes just writing the spinning thoughts helps them slow down.",
                "Ugh, that anxious feeling is the worst. Want to try writing whatever's bouncing around in your head?",
                "I'm sorry you're feeling this way. Sometimes just writing the worries helps shrink them a bit.",
                "Anxiety is so exhausting. Want to let it all out? No need to make it pretty, just write."
            ]
            return random.choice(responses)
        
        # Happy/excited
        if any(word in input_lower for word in ["excited", "happy", "proud", "accomplished", "great"]):
            responses = [
                "OMG that's amazing! You should totally write about this while the feeling is fresh - capture that good stuff!",
                "Yesss! I love that for you! Want to save this feeling? Writing it down helps you remember it later.",
                "That's so awesome! Want to document this moment? Future you will love reading about it.",
                "Woohoo! That's incredible! Want to write it down so you never forget this feeling?"
            ]
            return random.choice(responses)
        
        # Gratitude
        if any(word in input_lower for word in ["grateful", "thankful", "blessed"]):
            responses = [
                "I love that energy! Writing down what you're grateful for is like sunshine for your brain. Want to free write about it?",
                "That's such a beautiful mindset! Want to list out what you're grateful for? It's like collecting happy moments.",
                "I love this for you! Gratitude journaling is basically magic. Want to write about what's feeling good?",
                "What a wonderful way to think! Want to explore that feeling? Writing about gratitude makes it grow."
            ]
            return random.choice(responses)
        
        # Stuck/confused
        if any(word in input_lower for word in ["stuck", "don't know", "blank", "confused", "lost"]):
            responses = [
                "Totally happens to everyone! Sometimes I just start with 'blah I have no idea what to write but...' and then it flows.",
                "Ugh, blank page syndrome is real! Want to try just writing 'I don't know what to write' over and over until something comes?",
                "That's so normal! Want me to give you a prompt? Or we can just write about feeling stuck - that counts too!",
                "No worries! Sometimes the best writing comes from 'I have no idea what to say here.' Want to try that?"
            ]
            return random.choice(responses)
        
        # General questions
        if any(word in input_lower for word in ["what can i do", "help", "how does", "features"]):
            responses = [
                "Oh! So you can either free write about whatever's on your mind, do some guided prompts if you want structure, or track your mood. What feels good?",
                "Hey! So we've got free writing for whatever's happening, guided prompts when you want direction, or mood tracking. What's calling to you?",
                "Great question! You can vent freely with no structure, try some thoughtful prompts, or track how you're feeling. What sounds helpful?",
                "So your options are: free writing (total freedom), guided prompts (when you want help), or mood tracking. What feels right?"
            ]
            return random.choice(responses)
        
        # Greetings - be more varied
        if any(word in input_lower for word in ["hi", "hello", "hey", "what's up"]):
            responses = [
                "Hey! I'm your journaling buddy - what's on your mind?",
                "Hi there! Ready to write something or just chat?",
                "Hey! Want to do some journaling or just hang out for a bit?",
                "Hello! What's going on in your world today?"
            ]
            return random.choice(responses)
        
        # Existential stuff
        if any(word in input_lower for word in ["meaning", "purpose", "who am i", "understand myself"]):
            responses = [
                "Whoa, deep questions! I love it. You could either free write and see what comes up, or try some self-discovery prompts. What's your vibe?",
                "Ooh, the big stuff! Want to free write and see what emerges, or try some prompts that explore identity?",
                "I'm here for these questions! Want to just write whatever comes to mind, or try some structured self-discovery prompts?",
                "Deep thoughts! Want to free write about it, or try some prompts that explore meaning and purpose?"
            ]
            return random.choice(responses)
        
        # Default - super casual with variety
        responses = [
            "Hey! I'm your journaling buddy - you can free write, do some prompts, or just rant. Whatever you need!",
            "Hey there! Want to write something? We can do free writing, prompts, or just talk it out.",
            "Hi! Ready to get some thoughts out of your head? We've got options - whatever feels right!",
            "Hey! What's going on? Want to write it down, try a prompt, or just vent?"
        ]
        return random.choice(responses)
    
    def _save_to_memory(self, user_id: str, user_input: str, response: str):
        """Save conversation to SmartMemory"""
        try:
            smart_memory_service.cache_ai_response(
                prompt_type="casual_voice",
                prompt=user_input,
                response=response,
                effectiveness_score=0.9
            )
            
            # Track conversation topics
            topics = smart_memory_service.get_user_preference(user_id, "topics_discussed") or []
            
            input_lower = user_input.lower()
            if "work" in input_lower or "job" in input_lower:
                if "work_stress" not in topics:
                    topics.append("work_stress")
            if "partner" in input_lower or "relationship" in input_lower:
                if "relationship" not in topics:
                    topics.append("relationship")
            if "anxious" in input_lower or "worry" in input_lower:
                if "anxiety" not in topics:
                    topics.append("anxiety")
            
            smart_memory_service.cache_user_preference(user_id, "topics_discussed", topics)
            
        except Exception as e:
            print(f"⚠️ Memory save failed: {e}")

# Global instance
casual_voice_service = CasualVoiceService()