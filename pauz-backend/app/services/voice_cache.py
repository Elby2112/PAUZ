"""
Fast Response Cache for Voice Assistant
Caches common responses to make the assistant feel faster
"""

import time
from typing import Dict, Optional
import hashlib

class VoiceResponseCache:
    """Fast cache for voice responses to improve perceived speed"""
    
    def __init__(self, max_size: int = 100, ttl_seconds: int = 300):
        self.cache: Dict[str, Dict] = {}
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.access_times: Dict[str, float] = {}
    
    def _get_key(self, user_input: str, user_context: Optional[Dict] = None) -> str:
        """Generate cache key from input and context"""
        # Simplify context for caching (only essential parts)
        context_key = ""
        if user_context:
            context_key = f"ret:{user_context.get('is_returning_user', False)}"
        
        # Create a simple hash
        full_key = f"{user_input.lower().strip()}_{context_key}"
        return hashlib.md5(full_key.encode()).hexdigest()[:16]
    
    def get(self, user_input: str, user_context: Optional[Dict] = None) -> Optional[str]:
        """Get cached response if available and not expired"""
        key = self._get_key(user_input, user_context)
        
        if key not in self.cache:
            return None
        
        # Check if expired
        if time.time() - self.cache[key]['timestamp'] > self.ttl_seconds:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return None
        
        # Update access time for LRU
        self.access_times[key] = time.time()
        
        print(f"🚀 Cache hit: {user_input[:30]}...")
        return self.cache[key]['response']
    
    def set(self, user_input: str, response: str, user_context: Optional[Dict] = None):
        """Cache a response"""
        key = self._get_key(user_input, user_context)
        
        # Remove oldest if at max size
        if len(self.cache) >= self.max_size:
            oldest_key = min(self.access_times.keys(), key=lambda k: self.access_times[k])
            del self.cache[oldest_key]
            del self.access_times[oldest_key]
        
        self.cache[key] = {
            'response': response,
            'timestamp': time.time()
        }
        self.access_times[key] = time.time()
        
        print(f"💾 Cached: {user_input[:30]}...")
    
    def get_size(self) -> int:
        """Get current cache size"""
        return len(self.cache)

# Fast response templates for instant replies
FAST_RESPONSES = {
    # General help
    "what can i do": "In PAUZ, you can try free journaling to write freely with AI hints, guided journaling to explore topics with prompts, or track your mood in your garden. What interests you most?",
    "help": "I'm here to help! PAUZ offers free journaling with AI hints, guided journaling on specific topics, and mood tracking in your garden. What would you like to explore?",
    "features": "PAUZ has free journaling with contextual AI hints, guided journaling with structured prompts on any topic, and a mood garden for tracking emotional patterns.",
    
    # Getting started
    "start": "Let's begin! You can try free journaling to write freely and get AI hints when stuck, or guided journaling to explore a specific topic with structured prompts. What feels right?",
    "begin": "I'm excited to help you start! Try free journaling for open expression with AI support, or guided journaling for structured topic exploration. What calls to you?",
    "how do i start": "Starting is easy! Choose free journaling to write freely with hints, or guided journaling to explore specific topics with prompts. Both are beautiful ways to begin.",
    
    # Feeling stuck
    "stuck": "When you're stuck in free journaling, AI hints analyze your writing and suggest what to explore next. Would you like to try free journaling with hints?",
    "blocked": "Feeling blocked is normal! In free journaling, you can get AI hints that analyze what you've written and provide contextual suggestions to continue.",
    "don't know": "Not knowing is perfect! In free journaling, AI hints can help by analyzing your writing and suggesting what to explore next. Want to try?",
    
    # Encouragement
    "encourage": "You're already doing something beautiful by showing up to journal. Your willingness to reflect matters deeply, whether you choose free writing or structured exploration.",
    "motivate": "Your commitment to self-reflection is inspiring. Every moment you spend journaling contributes to your growth and understanding.",
    "inspire": "You are your own best teacher. Trust what emerges as you write - your inner wisdom is speaking through the journaling process.",
    
    # Hints (IMPORTANT: Correct the confusion)
    "hints": "AI hints appear during free journaling! Start a free journal session, and if you get stuck, the AI analyzes your writing and provides contextual suggestions.",
    "hint garden": "The garden is for mood tracking with flowers, not hints. For writing hints, use free journaling and ask for AI hints when you're stuck.",
    "garden hints": "The garden tracks your mood with different flowers - it's a beautiful visual way to see emotional patterns over time!",
    
    # Free journaling
    "free journaling": "Free journaling lets you write anything freely, with AI hints that analyze your writing and suggest what to explore next when you're stuck.",
    "free journal": "Start a free journal session to write openly. AI hints will help if you get stuck by analyzing what you've written and providing contextual suggestions.",
    
    # Guided journaling
    "guided journaling": "Guided journaling gives you structured prompts on any topic - just choose a theme and AI generates thoughtful questions to explore.",
    "guided journal": "Pick a topic for guided journaling and AI will create 3-5 specific prompts to help you explore that theme deeply.",
    
    # Garden/mood tracking
    "garden": "Your garden visualizes your mood with different flowers - it's a beautiful way to track emotional patterns over time and see how you're feeling.",
    "mood": "Track your mood in the garden where different emotions bloom as different flowers - rose for love, sunflower for happiness, etc.",
}

# Global cache instance
response_cache = VoiceResponseCache()