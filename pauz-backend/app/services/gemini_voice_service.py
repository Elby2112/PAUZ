"""
Gemini-Powered Voice Assistant Service
Replaces rule-based responses with intelligent Gemini AI generation
Optimized for speed with caching and fast responses
"""

import os
import json
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

from app.services.voice_cache import response_cache, FAST_RESPONSES

class GeminiVoiceService:
    """Intelligent voice assistant service powered by Google Gemini"""
    
    def __init__(self):
        # Initialize Gemini
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key or self.gemini_api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY not configured. Please set up your Gemini API key.")
        
        try:
            genai.configure(api_key=self.gemini_api_key)
            # Use gemini-2.5-flash for fast, intelligent responses
            self.model = genai.GenerativeModel(
                'gemini-2.5-flash',
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=150,  # Shorter responses for voice
                    candidate_count=1,
                )
            )
            print("✅ Gemini Voice Assistant initialized (optimized for speed)")
        except Exception as e:
            raise ValueError(f"Failed to initialize Gemini: {e}")
    
    def get_app_context_description(self) -> str:
        """Get comprehensive description of PAUZ app for context"""
        return """
        You are PAUZ, a compassionate and intelligent voice assistant for a journaling app called PAUZ. 
        The app features:
        
        **Core Features:**
        - **Guided Journaling**: Structured prompts and themes for self-exploration
        - **Free Journaling**: Open, unrestricted writing space
        - **Hints Garden**: Gentle writing prompts when users need inspiration
        - **AI Reflections**: Thoughtful insights about user's journal entries
        - **Personal Statistics**: Track journaling progress and patterns
        
        **Your Role:**
        - Be warm, gentle, and softly encouraging
        - Help users navigate the app features with care
        - Provide thoughtful writing guidance and inspiration
        - Offer soft support when users feel stuck or overwhelmed
        - Celebrate their journaling journey with gentle encouragement
        
        **Your Voice:**
        - Soft, warm, and nurturing - like a gentle hug in words
        - Use "you" and "we" to create tender connection
        - Ask soft, wondering questions that invite gentle reflection
        - Validate feelings with tender compassion
        - Keep responses cozy but meaningful (2-4 sentences for voice)
        - Use words like "perhaps", "might", "gently", "softly", "inviting"
        
        **Example Interaction Style:**
        - Instead of "Here are the features..." say "I'd love to gently show you what we can explore together..."
        - Instead of "You should journal..." say "What feels softly alive for you to explore today?"
        - Instead of "Click this button" say "Let me gently guide you to..."
        """
    
    def generate_intelligent_response(
        self, 
        user_input: str, 
        user_context: Optional[Dict] = None,
        conversation_history: Optional[list] = None
    ) -> str:
        """
        Generate intelligent response using Gemini with full app context
        Optimized for speed with caching
        """
        
        # 1. Check cache first for instant responses
        cached_response = response_cache.get(user_input, user_context)
        if cached_response:
            return cached_response
        
        # 2. Check fast response templates
        fast_key = user_input.lower().strip()
        for key, response in FAST_RESPONSES.items():
            if key in fast_key:
                response_cache.set(user_input, response, user_context)
                print(f"🚀 Fast template response: {user_input[:30]}...")
                return response
        
        # 3. Generate Gemini response (optimized)
        try:
            # Build the full prompt (optimized for speed)
            full_prompt = f"""
            {self.get_app_context_description()}
            
            {"**User Context:** Returning user with progress" if user_context and user_context.get('is_returning_user') else "**User Context:** New user"}
            
            User: "{user_input}"
            
            Respond warmly and helpfully in 1-2 sentences. Be specific about PAUZ features.
            """
            
            response = self.model.generate_content(full_prompt)
            response_text = response.text.strip()
            
            # Cache the response
            response_cache.set(user_input, response_text, user_context)
            
            print(f"✅ Gemini Response: {response_text[:100]}...")
            return response_text
            
        except Exception as e:
            print(f"❌ Gemini generation failed: {e}")
            return self._get_emergency_fallback_response(user_input)
    
    def generate_personalized_welcome(
        self, 
        user_context: Optional[Dict] = None,
        time_based_greeting: Optional[str] = None
    ) -> str:
        """Generate intelligent, personalized welcome message"""
        
        from datetime import datetime
        
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
        
        context_parts = [self.get_app_context_description()]
        
        if user_context:
            context_info = f"""
            
            **User for Welcome Message:**
            - Name: {user_context.get('name', 'Friend')}
            - Total Journals: {user_context.get('total_journals', 0)}
            - Is Returning User: {user_context.get('is_returning_user', False)}
            - Last Journal: {user_context.get('last_journal_days_ago', 'Never')} days ago
            - Time of Day: {time_greeting}
            """
            context_parts.append(context_info)
        
        welcome_prompt = f"""
        {self.get_app_context_description()}
        
        **User:** {user_context.get('name', 'Friend')} - {'Returning user' if user_context.get('is_returning_user') else 'New user'}
        **Time:** {time_greeting}
        
        Generate a warm 1-2 sentence welcome that acknowledges their return status and asks how to help.
        """
        
        try:
            response = self.model.generate_content(welcome_prompt)
            welcome_text = response.text.strip()
            
            print(f"✅ Gemini Welcome: {welcome_text}")
            return welcome_text
            
        except Exception as e:
            print(f"❌ Gemini welcome failed: {e}")
            return self._get_emergency_welcome(time_greeting, user_context)
    
    def _get_emergency_fallback_response(self, user_input: str) -> str:
        """Emergency fallback if Gemini fails"""
        
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

# Global instance
gemini_voice_service = GeminiVoiceService()