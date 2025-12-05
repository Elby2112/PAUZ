"""
PAUZ Voice Assistant with Accurate App Knowledge
Knows the actual features: FreeJournal, GuidedJournal with categories, Garden, etc.
Maintains ongoing conversation context
"""

import os
import json
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class PauzVoiceService:
    """Voice assistant that actually understands PAUZ app features"""
    
    def __init__(self):
        # Initialize Gemini
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not self.gemini_api_key or self.gemini_api_key == 'your-gemini-api-key-here':
            raise ValueError("GEMINI_API_KEY not configured")
        
        try:
            genai.configure(api_key=self.gemini_api_key)
            # Use gemini-pro model which should be available
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ PAUZ Voice Assistant initialized with proper app knowledge")
        except Exception as e:
            print(f"⚠️ Gemini pro failed, trying 1.5-flash: {e}")
            try:
                self.model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ PAUZ Voice Assistant initialized with gemini-1.5-flash")
            except Exception as e2:
                print(f"⚠️ All Gemini models failed, using fallback only: {e2}")
                self.model = None
        
        # Store conversation history per user
        self.conversations = {}
        
    def get_pauz_app_knowledge(self) -> str:
        """Accurate description of PAUZ app features"""
        return """
        PAUZ is a journaling app with TWO main features:

        1. **FreeJournal** - Complete freedom:
           - Write freely about anything
           - Can't start? Click "Hint" for AI-generated starting ideas or continuation help
           - Afraid of writing? Record yourself talking - it transcribes automatically
           - After writing: "Reflect with AI" detects mood, insights, gives summary & follow-up questions
           - Mood detected plants a flower in your Garden (for motivation/tracking)
           - Can save journals or export as PDF

        2. **GuidedJournal** - Structured exploration:
           - Choose from 9 categories: Mind, Body, Heart, Friends, Family, Romance, Growth, Mission, Money, Joy
           - AI generates thoughtful prompts specific to that category
           - Journals are saved in-app or can export as PDF

        **Garden Feature** - Mood tracking:
           - Flowers represent moods from your journal reflections
           - Click any flower to see the journal note that created it
           - Visual way to track your emotional journey over time

        Users can view all saved journals anytime. The goal is to make journaling accessible and less intimidating.
        """
    
    def get_or_create_conversation(self, user_id: str) -> List[Dict]:
        """Get or create conversation history for user"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        return self.conversations[user_id]
    
    def add_to_conversation(self, user_id: str, role: str, content: str):
        """Add message to conversation history"""
        conversation = self.get_or_create_conversation(user_id)
        conversation.append({
            "role": role,
            "content": content,
            "timestamp": str(json.dumps({"timestamp": "now"}))  # Simple timestamp
        })
        
        # Keep only last 10 messages to avoid context overflow
        if len(conversation) > 10:
            self.conversations[user_id] = conversation[-10:]
    
    def build_conversation_context(self, user_id: str, user_input: str) -> str:
        """Build conversation context including history"""
        conversation = self.get_or_create_conversation(user_id)
        
        context = f"{self.get_pauz_app_knowledge()}\n\n"
        context += "CONVERSATION HISTORY:\n"
        
        for msg in conversation[-6:]:  # Last 6 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        context += f"\nCurrent User Message: {user_input}\n"
        context += "\nRespond as PAUZ voice assistant. Reference our conversation if relevant. Be warm and helpful. Keep responses to 1-2 sentences."
        
        return context
    
    def generate_response(self, user_input: str, user_id: str, user_context: Optional[Dict] = None) -> str:
        """
        Generate response with conversation memory and accurate app knowledge
        """
        # Add user input to conversation
        self.add_to_conversation(user_id, "user", user_input)
        
        # Build context with conversation history
        prompt = self.build_conversation_context(user_id, user_input)
        
        try:
            response = self.model.generate_content(prompt)
            
            if response.text and response.text.strip():
                assistant_response = response.text.strip()
                
                # Add assistant response to conversation
                self.add_to_conversation(user_id, "assistant", assistant_response)
                
                print(f"✅ PAUZ Response: {assistant_response[:100]}...")
                return assistant_response
            else:
                # Fallback if Gemini fails
                return self.get_contextual_fallback(user_input, user_id)
                
        except Exception as e:
            print(f"❌ Gemini failed: {e}")
            return self.get_contextual_fallback(user_input, user_id)
    
    def get_contextual_fallback(self, user_input: str, user_id: str) -> str:
        """Smart fallback that considers conversation context"""
        conversation = self.get_or_create_conversation(user_id)
        input_lower = user_input.lower()
        
        # Check if this is first message vs ongoing conversation
        is_first_message = len([msg for msg in conversation if msg["role"] == "user"]) <= 1
        
        if is_first_message:
            # First message - welcome and guide
            if any(word in input_lower for word in ["hi", "hello", "hey"]):
                return "Hi! I'm your PAUZ journaling assistant. You can ask me about FreeJournal for free writing, GuidedJournal for category-based prompts, or anything about journaling!"
            elif any(word in input_lower for word in ["help", "what", "how"]):
                return "I can help you with both journaling options! FreeJournal lets you write freely with hints and voice recording, while GuidedJournal gives you structured prompts in categories like Mind, Body, Heart, etc. What interests you?"
        
        # Ongoing conversation responses
        if any(word in input_lower for word in ["free journal", "free writing", "hints"]):
            return "FreeJournal is perfect for total freedom! You can write anything, get hints when stuck, or even record yourself talking. The 'Reflect with AI' feature is amazing for insights too!"
        
        elif any(word in input_lower for word in ["guided", "categories", "prompts"]):
            categories = "Mind, Body, Heart, Friends, Family, Romance, Growth, Mission, Money, Joy"
            return f"GuidedJournal helps you explore specific topics with thoughtful prompts. You can choose from: {categories}. Which category feels right for you today?"
        
        elif any(word in input_lower for word in ["garden", "flower", "mood"]):
            return "Your Garden shows your mood journey as flowers! Each flower represents a mood detected from your journal reflections. Click any flower to see what created it - it's a beautiful way to track your growth."
        
        elif any(word in input_lower for word in ["stuck", "don't know", "blank"]):
            return "No worries! In FreeJournal, you can use the Hint button for ideas, or try GuidedJournal for structured prompts. You can also record yourself talking if typing feels hard. What feels easier?"
        
        elif any(word in input_lower for word in ["start", "begin", "how to"]):
            return "Great question! You could start with FreeJournal to write freely, or pick a GuidedJournal category that calls to you. Both ways are valid - what feels like your style?"
        
        elif any(word in input_lower for word in ["record", "voice", "talk"]):
            return "Yes! In FreeJournal you can record yourself talking instead of writing. It transcribes automatically - perfect for when writing feels overwhelming!"
        
        else:
            # General helpful response
            if len(conversation) > 2:
                return "I'm here to help with your journaling journey! Whether you need hints, want to explore a specific category, or have questions about the Garden, I've got you. What's on your mind?"
            else:
                return "I'm your PAUZ journaling assistant! I can help you with FreeJournal (free writing with hints), GuidedJournal (category-based prompts), or explain features like the Garden. What would you like to explore?"
    
    def generate_welcome(self, user_id: str, user_context: Optional[Dict] = None) -> str:
        """Generate personalized welcome message"""
        
        # Check if user has journals
        has_journals = user_context and user_context.get("total_journals", 0) > 0
        
        if has_journals:
            welcome_variations = [
                "Welcome back! Ready to continue your journaling journey? You can pick up where you left off or try something new today.",
                "Hey again! Your journaling space is waiting. Want to continue with free writing, explore a new category, or check your Garden?",
                "Good to see you back! Your journaling practice is growing. What feels right for you today?"
            ]
        else:
            welcome_variations = [
                "Welcome to PAUZ! I'm your journaling assistant. You can try FreeJournal for free writing with hints, or GuidedJournal for structured prompts. What feels good to start?",
                "Hi! I'm excited to help you start journaling! Don't worry about writing perfectly - we have hints, voice recording, and categories to guide you. Want to explore?",
                "Hey there! Welcome to your journaling space. Whether you want to write freely, try category prompts, or just learn the ropes, I'm here to help. What's calling to you?"
            ]
        
        # Pick a random welcome
        import random
        welcome = random.choice(welcome_variations)
        
        # Add to conversation as assistant message
        self.add_to_conversation(user_id, "assistant", welcome)
        
        return welcome

# Global instance
pauz_voice_service = PauzVoiceService()