"""
Intelligent Conversational Templates
Context-aware responses that feel natural but are reliable
"""

INTELLIGENT_TEMPLATES = {
    # Work stress
    "tough day at work": "It sounds like you need to process today's work stress. Try free journaling to write it all out, and I can provide AI hints to help you explore your feelings about it.",
    "work stress": "When work is overwhelming, free journaling can help you process it. AI hints can guide you to deeper insights about what's really bothering you.",
    "job": "For work-related feelings, try free journaling to explore them deeply. AI hints will help you uncover patterns and find clarity.",
    "boss": "Relationship issues at work can be complex. Free journaling with AI hints can help you sort through the dynamics and your role in them.",
    
    # Relationship conflicts
    "argument": "After an argument, free journaling can help you process your emotions and understand your perspective better. AI hints will guide you to constructive insights.",
    "partner": "Relationship questions are perfect for guided journaling - try 'relationships' as a topic to explore your feelings and patterns.",
    "fight": "After a conflict, free journaling with AI hints can help you understand your triggers and what you really need from the relationship.",
    "relationship": "For relationship insights, try guided journaling on 'relationships' or free journaling to explore your specific situation with AI guidance.",
    
    # Anxiety and fear
    "anxious": "Anxiety often feels overwhelming, but journaling can help ground you. Try free journaling to express it all, and AI hints will help you find the underlying concerns.",
    "anxiety": "When anxiety strikes, free journaling can be a safe space to explore it. AI hints will gently guide you to the sources and coping strategies.",
    "worried": "Worrying thoughts can circle endlessly - free journaling helps break the cycle. AI hints will guide you to what's really beneath the worry.",
    "scared": "Fear is powerful but journaling helps you face it gently. Try free journaling to explore what you're afraid of, with AI hints providing support.",
    
    # Positive emotions
    "proud": "That's wonderful to hear! Guided journaling on 'accomplishments' can help you explore what made this achievement meaningful and how you can build on it.",
    "grateful": "Gratitude is beautiful to explore! Free journaling about what you're thankful for, with AI hints to deepen your appreciation, can be very fulfilling.",
    "happy": "Happy moments deserve to be savored! Free journaling about your joy, with AI hints to explore what made it so special, can help you recreate more of it.",
    "excited": "Excitement is energy waiting to be channeled! Free journaling can help you explore what you're looking forward to and how to make the most of it.",
    
    # Existential questions
    "understand myself": "Self-understanding is a beautiful journey! Try guided journaling on 'self-discovery' for structured exploration, or free journaling with AI hints for organic insights.",
    "purpose": "Questions about purpose are profound. Guided journaling on 'life purpose' can provide structured exploration, or free journaling with AI hints for personal discovery.",
    "meaning": "Searching for meaning is deeply human. Try guided journaling on 'values' or 'life purpose' to explore what truly matters to you.",
    "who am i": "Identity questions are rich exploration! Guided journaling on 'self-discovery' offers structured prompts, while free journaling with AI hints provides organic discovery.",
    
    # Journaling process
    "don't know what to write": "That's the perfect place to start! Free journaling with AI hints is designed exactly for this - the AI will analyze what you write and suggest what to explore next.",
    "stuck": "Being stuck is normal! Free journaling with AI hints can help - the AI looks at what you've written and suggests gentle directions to explore.",
    "blank mind": "A blank mind is like a fresh canvas! Start with 'I don't know what to write' in free journaling, and AI hints will help you find your words.",
    "what to write": "The beauty of free journaling is you can write anything! Start with what's present, and AI hints will help you go deeper when you're ready.",
    
    # General app guidance
    "how does this work": "PAUZ helps you journal in three ways: free writing with AI hints, structured guided prompts on topics, or mood tracking with flower visualization. What interests you?",
    "features": "You have three main tools: free journaling for open writing with AI hints, guided journaling for structured topic exploration, and your garden for mood visualization.",
    "get started": "Starting is easy! Try free journaling if you want to write openly, guided journaling if you want structured prompts, or your garden to track moods. What calls to you?",
    
    # Garden/mood specific
    "mood": "Track your moods in your garden where emotions bloom as different flowers - it's a beautiful way to see your emotional patterns over time.",
    "garden": "Your garden visualizes your emotional journey - each mood becomes a different flower, creating a living record of your inner world.",
    "feelings": "Your feelings can bloom in your garden as flowers, or you can explore them deeply through free journaling with AI hints. Which appeals to you?",
    
    # Default fallbacks
    "help": "I'm here to help! You can try free journaling with AI hints for open exploration, guided journaling for structured topics, or mood tracking in your garden.",
    "confused": "When you're confused, free journaling can help untangle your thoughts. AI hints will guide you to clarity as you write.",
    "overwhelmed": "Feeling overwhelmed calls for gentle processing. Free journaling with AI hints can help you sort through everything one piece at a time.",
}

def get_intelligent_response(user_input: str) -> str:
    """Get an intelligent, context-aware response"""
    
    input_lower = user_input.lower()
    
    # Look for exact matches first
    for key, response in INTELLIGENT_TEMPLATES.items():
        if key in input_lower:
            return response
    
    # Look for partial matches
    for key, response in INTELLIGENT_TEMPLATES.items():
        if any(word in input_lower for word in key.split()):
            return response
    
    # Default helpful response
    return "I'm here to support your journaling journey. You can explore free writing with AI hints, structured prompts, or mood tracking. What feels most helpful right now?"