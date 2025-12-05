"""
SmartMemory-Powered Voice Assistant Service
Uses Raindrop's SmartMemory to remember conversations and learn user preferences
With accurate PAUZ app knowledge
"""

import os
import json
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

from app.services.smart_memory_service import smart_memory_service
from app.services.voice_cache import response_cache, FAST_RESPONSES
from app.services.casual_voice_service import casual_voice_service

class SmartMemoryVoiceService:
    """Voice assistant with memory and personalization using SmartMemory"""
    
    def __init__(self):
        # Initialize Gemini
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key or self.gemini_api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY not configured")
        
        try:
            genai.configure(api_key=self.gemini_api_key)
            # Use gemini-2.5-flash with relaxed safety settings
            self.model = genai.GenerativeModel(
                'gemini-2.5-flash',
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=150,
                    candidate_count=1,
                ),
                safety_settings=[
                    {
                        "category": "HARM_CATEGORY_HARASSMENT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_HATE_SPEECH", 
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                        "threshold": "BLOCK_NONE"
                    },
                    {
                        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                        "threshold": "BLOCK_NONE"
                    }
                ]
            )
            print("✅ SmartMemory Voice Assistant initialized (relaxed safety)")
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini: {e}")
    
    def get_app_context_description(self) -> str:
        """Get comprehensive and ACCURATE description of PAUZ app for context"""
        return PAUZ_APP_DESCRIPTION

    def _build_simple_prompt(self, user_input: str, user_context: Optional[Dict], memory_context: Optional[Dict]) -> str:
        """Build a minimal prompt that won't trigger safety filters"""
        
        # Ultra-simple prompt to avoid safety issues
        if user_context and user_context.get('is_returning_user'):
            base_prompt = "You are a helpful journaling assistant. A returning user says:"
        else:
            base_prompt = "You are a helpful journaling assistant. A user says:"
        
        prompt = f"""
        {base_prompt} "{user_input}"
        
        Respond naturally in 1-2 sentences. Be warm and helpful.
        
        Features available:
        - Free writing with AI hints
        - Structured prompts on topics  
        - Mood tracking with flowers
        
        Guide them to the right feature.
        """
        
        return prompt
        """Get comprehensive and ACCURATE description of PAUZ app for context"""
        return PAUZ_APP_DESCRIPTION
    
    def generate_intelligent_response(
        self, 
        user_input: str, 
        user_id: str,
        user_context: Optional[Dict] = None,
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Generate intelligent response using SmartMemory for personalization
        PRIORITIZES dynamic responses over repetitive templates
        """
        
        # 1. Skip cache for common conversational phrases to ensure variety
        input_lower = user_input.lower().strip()
        skip_cache_phrases = ["hi", "hello", "hey", "how are you", "what's up", "help", "stuck", "i'm", "i am"]
        should_skip_cache = any(phrase in input_lower for phrase in skip_cache_phrases)
        
        if not should_skip_cache:
            # 2. Check SmartMemory cache first for exact matches (but not for greetings)
            cached_response = response_cache.get(user_input, user_context)
            if cached_response and len(cached_response) > 15:  # Only use substantial cached responses
                self._save_conversation_to_memory(user_id, user_input, cached_response)
                return cached_response
        
        # 3. Use casual voice service for genuinely friendly responses (our main response generator)
        try:
            casual_response = casual_voice_service.generate_casual_response(
                user_input=user_input,
                user_id=user_id,
                user_context=user_context
            )
            
            # Cache the response locally (but not for common phrases)
            if not should_skip_cache:
                response_cache.set(user_input, casual_response, user_context)
            
            self._save_conversation_to_memory(user_id, user_input, casual_response)
            print(f"✅ Casual Voice Response: {casual_response[:100]}...")
            return casual_response
            
        except Exception as e:
            print(f"❌ Casual voice service failed: {e}")
            
        # 4. FALLBACK: Check SmartMemory for similar past conversations
        if not should_skip_cache:
            memory_response = self._get_memory_response(user_id, user_input, user_context)
            if memory_response:
                response_cache.set(user_input, memory_response, user_context)
                return memory_response
        
        # 5. EMERGENCY FALLBACK: Use dynamic templates with variety ONLY if everything else fails
        print("⚠️ Using emergency template as last resort")
        return self._get_dynamic_emergency_response(user_input, user_context)
    
    def _get_memory_response(self, user_id: str, user_input: str, user_context: Optional[Dict]) -> Optional[str]:
        """Get response from SmartMemory if similar conversation exists"""
        try:
            # Try to find cached AI response for similar prompt
            cached_ai = smart_memory_service.get_cached_ai_response("voice_assistant", user_input)
            if cached_ai:
                print(f"🧠 SmartMemory hit: {user_input[:30]}...")
                return cached_ai
        except Exception as e:
            print(f"❌ SmartMemory lookup failed: {e}")
        
        return None
    
    def _get_memory_context(self, user_id: str) -> Dict[str, Any]:
        """Get user's memory context from SmartMemory"""
        try:
            # Get personalization data
            personalization = smart_memory_service.get_personalization_data(user_id) or {}
            
            # Get user preferences
            communication_style = smart_memory_service.get_user_preference(user_id, "communication_style")
            topics_discussed = smart_memory_service.get_user_preference(user_id, "topics_discussed") or []
            
            return {
                "personalization": personalization,
                "communication_style": communication_style,
                "topics_discussed": topics_discussed,
                "memory_available": bool(personalization or communication_style or topics_discussed)
            }
        except Exception as e:
            print(f"❌ Memory context retrieval failed: {e}")
            return {"memory_available": False}
    
    def _build_memory_enhanced_prompt(
        self, 
        user_input: str, 
        user_id: str,
        user_context: Optional[Dict],
        memory_context: Dict[str, Any]
    ) -> str:
        """Build prompt enhanced with memory context"""
        
        base_prompt = self.get_app_context_description()
        
        # Add memory context if available
        memory_info = ""
        if memory_context.get("memory_available"):
            topics = memory_context.get("topics_discussed", [])
            if topics:
                memory_info = f"\n\n**User Memory:** You've previously discussed: {', '.join(topics[-5:])}. Reference these if relevant."
        
        # Add user context
        context_info = ""
        if user_context:
            context_info = f"\n\n**Current Context:** Returning user with {user_context.get('total_journals', 0)} journals."
        
        # Build final prompt
        full_prompt = f"""
        {base_prompt}{memory_info}{context_info}
        
        **User:** "{user_input}"
        
        Respond warmly in 1-2 sentences. Reference past conversations if helpful. Be specific about PAUZ features.
        """
        
        return full_prompt
    
    def _save_conversation_to_memory(self, user_id: str, user_input: str, response: str):
        """Save conversation to SmartMemory for learning"""
        try:
            # Cache the AI response
            smart_memory_service.cache_ai_response(
                prompt_type="voice_assistant",
                prompt=user_input,
                response=response,
                effectiveness_score=0.8  # Default score
            )
            
            # Update user's conversation topics
            topics = smart_memory_service.get_user_preference(user_id, "topics_discussed") or []
            
            # Extract simple topics from user input
            input_lower = user_input.lower()
            if any(word in input_lower for word in ["stuck", "block", "stuck"]):
                if "feeling_stuck" not in topics:
                    topics.append("feeling_stuck")
            if any(word in input_lower for word in ["help", "what", "features"]):
                if "app_guidance" not in topics:
                    topics.append("app_guidance")
            if any(word in input_lower for word in ["start", "begin", "getting"]):
                if "getting_started" not in topics:
                    topics.append("getting_started")
            if any(word in input_lower for word in ["encourage", "motivate"]):
                if "encouragement" not in topics:
                    topics.append("encouragement")
            
            # Save updated topics
            smart_memory_service.cache_user_preference(user_id, "topics_discussed", topics)
            
            # Update personalization data
            personalization = smart_memory_service.get_personalization_data(user_id) or {}
            personalization.update({
                "last_conversation": user_input,
                "conversation_count": personalization.get("conversation_count", 0) + 1,
                "preferred_response_length": "short"  # Voice responses should be concise
            })
            
            smart_memory_service.cache_personalization_data(user_id, personalization)
            
            print(f"💾 Saved conversation to memory for {user_id}")
            
        except Exception as e:
            print(f"❌ Failed to save to memory: {e}")
    
    def generate_personalized_welcome(
        self, 
        user_id: str,
        user_context: Optional[Dict] = None,
        time_based_greeting: Optional[str] = None
    ) -> str:
        """Generate intelligent, personalized welcome with memory and variety"""
        
        from datetime import datetime
        import random
        
        # Get time-based greeting
        if not time_based_greeting:
            hour = datetime.now().hour
            if 5 <= hour < 12:
                time_greeting = "Good morning"
            elif 12 <= hour < 17:
                time_greeting = "Good afternoon"  
            elif 17 <= hour < 22:
                time_greeting = "Good evening"
            else:
                time_greeting = "Hello"
        else:
            time_greeting = time_based_greeting
        
        # Get memory context
        memory_context = self._get_memory_context(user_id)
        
        # For returning users, vary the welcome messages
        if user_context and user_context.get('is_returning_user'):
            welcome_variations = [
                f"{time_greeting}! Welcome back to your journaling practice. I'm so glad you're here again.",
                f"{time_greeting}! So good to see you back. Ready to continue your writing journey?",
                f"{time_greeting}! Welcome back, friend. Your journaling space is ready when you are.",
                f"Hey there! Welcome back. I've missed our writing sessions."
            ]
            
            if memory_context.get("memory_available"):
                welcome_variations.extend([
                    f"{time_greeting}! Good to have you back. I remember our last conversation - want to continue exploring?",
                    f"{time_greeting}! Welcome back! Ready to write more about those topics we discussed before?"
                ])
            
            welcome_text = random.choice(welcome_variations)
        else:
            # For new users
            welcome_variations = [
                f"{time_greeting}! Welcome to PAUZ. I'm here to support your journey of self-discovery through writing.",
                f"{time_greeting}! Hey there! Welcome to your new journaling space. I'm excited to be your writing companion.",
                f"{time_greeting}! Welcome to PAUZ! Think of me as your friendly journaling buddy, here to help you explore your thoughts.",
                f"Hi! Welcome to PAUZ. This is your space to write freely, and I'm here to help when you need it."
            ]
            welcome_text = random.choice(welcome_variations)
        
        # Try to make it even more personal with Gemini
        try:
            personal_prompt = f"""Make this welcome message even warmer and more personal, but keep it under 2 sentences: "{welcome_text}" 
            
            Add something specific about journaling if it feels natural. Don't make it longer."""
            
            response = self.model.generate_content(personal_prompt)
            if response.text and response.text.strip():
                enhanced_welcome = response.text.strip()
                if len(enhanced_welcome) < 200:  # Keep it reasonable
                    welcome_text = enhanced_welcome
            
        except Exception as e:
            print(f"🤷 Gemini welcome enhancement failed: {e}")
        
        # Save to memory
        self._save_conversation_to_memory(user_id, "welcome_message", welcome_text)
        
        print(f"✅ SmartMemory Welcome: {welcome_text}")
        return welcome_text
    
    def _get_dynamic_emergency_response(self, user_input: str, user_context: Optional[Dict]) -> str:
        """Emergency fallback with more variety and natural language"""
        
        import random
        user_lower = user_input.lower()
        
        # Help/guidance requests
        if any(word in user_lower for word in ["what", "help", "features", "do", "how"]):
            responses = [
                "I'm here to help you explore journaling through guided prompts, free writing, or gentle hints. What feels most appealing to you right now?",
                "Hey! So you can either free write about whatever's on your mind, try some guided prompts, or get hints for inspiration. What sounds good?",
                "Great question! We've got free writing for total freedom, guided prompts for structure, or hints when you need a little push. What calls to you?"
            ]
            return random.choice(responses)
        
        # Feeling stuck
        elif any(word in user_lower for word in ["stuck", "blocked", "don't know", "blank"]):
            responses = [
                "It's okay to feel stuck. Let's start with something gentle - what's present in your awareness right now?",
                "Totally normal! Sometimes starting with 'I feel stuck because...' helps get the words flowing. Want to try?",
                "No worries! We all get stuck. Want to try a simple prompt or just write about feeling stuck?"
            ]
            return random.choice(responses)
        
        # Getting started
        elif any(word in user_lower for word in ["start", "begin", "getting"]):
            responses = [
                "I'd love to help you begin. You could try guided journaling for structure, free writing to express freely, or hints for inspiration. What calls to you?",
                "Let's get you started! Want to try free writing, a guided prompt, or just write about whatever's happening today?",
                "Starting is the hardest part! Want some structure with a prompt, or just free writing to see what comes up?"
            ]
            return random.choice(responses)
        
        # Emotional content
        elif any(word in user_lower for word in ["sad", "happy", "angry", "anxious", "excited"]):
            responses = [
                "I'm here for all your feelings. Writing them down can help you understand them better. What's coming up for you?",
                "Thank you for sharing that. Want to explore this feeling more through writing?",
                "That's a lot to hold. Want to let it all out on the page? No judgment, just space to feel."
            ]
            return random.choice(responses)
        
        # Default
        else:
            responses = [
                "I'm here to support your journaling journey. Would you like some guidance on where to begin?",
                "Hey! I'm your journaling buddy. Want to write something together, or do you have questions?",
                "I'm here to help you connect with yourself through writing. What feels most helpful right now?"
            ]
            return random.choice(responses)
    
    def _get_emergency_template_response(self, user_input: str, user_context: Optional[Dict]) -> str:
        """Emergency fallback using templates - only used when Gemini fails"""
        
        fast_key = user_input.lower().strip()
        for key, response in FAST_RESPONSES.items():
            if key in fast_key:
                return response
        
        # Ultimate fallback
        return "I'm here to help with your journaling journey. You can explore free writing with AI hints, structured prompts, or mood tracking. What interests you most?"
        """Emergency fallback if everything fails"""
        
        user_lower = user_input.lower()
        
        if any(word in user_lower for word in ["what", "help", "features", "do"]):
            return "I'm here to help you explore journaling through guided prompts, free writing, or gentle hints. What feels most appealing to you right now?"
        
        elif any(word in user_lower for word in ["stuck", "blocked", "don't know"]):
            return "It's okay to feel stuck. Let's start with something gentle - what's present in your awareness right now?"
        
        elif any(word in user_lower for word in ["start", "begin", "how"]):
            return "I'd love to help you begin. You could try guided journaling for structure, free writing to express freely, or hints for inspiration. What calls to you?"
        
        else:
            return "I'm here to support your journaling journey. Would you like some guidance on where to begin?"
    
    def _get_emergency_welcome(self, time_greeting: str, user_context: Optional[Dict]) -> str:
        """Emergency welcome fallback"""
        
        if user_context and user_context.get('is_returning_user'):
            return f"{time_greeting}! Welcome back to your journaling practice. I'm so glad you're here."
        else:
            return f"{time_greeting}! Welcome to PAUZ. I'm here to support your journey of self-discovery through writing."
    
    def get_user_memory_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user's memory statistics"""
        try:
            personalization = smart_memory_service.get_personalization_data(user_id) or {}
            topics = smart_memory_service.get_user_preference(user_id, "topics_discussed") or []
            
            return {
                "conversations": personalization.get("conversation_count", 0),
                "topics_discussed": topics,
                "last_conversation": personalization.get("last_conversation"),
                "memory_available": bool(personalization)
            }
        except Exception as e:
            print(f"❌ Failed to get memory stats: {e}")
            return {"memory_available": False}

# Global instance
smart_memory_voice_service = SmartMemoryVoiceService()