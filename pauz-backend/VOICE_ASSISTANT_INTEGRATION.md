# Voice Assistant Integration Guide

## 🎯 Overview

The Voice Assistant provides a conversational interface for your journaling app with:
- **Personalized welcome greetings** based on time and user history
- **Interactive guidance** for app features and journaling help
- **Voice-first interaction** with typing fallback
- **Context-aware responses** about journaling options

## 📁 Files Created

### Backend Components
- `app/routes/voice_assistant.py` - Voice Assistant API endpoints
- Updated `app/main.py` - Added voice assistant router

### Frontend Components
- `VoiceAssistant.jsx` - Main voice assistant component
- `voiceAssistant.css` - Complete styling for the assistant
- `VoiceAssistantIntegration.jsx` - Integration examples
- `test_voice_assistant.html` - Test page for all features

## 🚀 Quick Start

### 1. Test the Backend
Open `test_voice_assistant.html` in your browser to test all voice assistant features:
- Welcome messages
- User context
- Guidance responses
- Quick actions

### 2. Add to Your Main App
Copy these integration steps into your main app:

#### Step 1: Import Components
```jsx
import VoiceAssistant from './VoiceAssistant';
import './voiceAssistant.css';
```

#### Step 2: Add State Management
```jsx
const [showAssistant, setShowAssistant] = useState(false);
const [autoPlayWelcome, setAutoPlayWelcome] = useState(false);
```

#### Step 3: Add the Component
```jsx
<VoiceAssistant
  isVisible={showAssistant}
  onClose={() => setShowAssistant(false)}
  autoPlayWelcome={autoPlayWelcome}
/>
```

#### Step 4: Add Trigger Button
```jsx
<button 
  onClick={() => {
    setShowAssistant(true);
    setAutoPlayWelcome(true);
  }}
>
  🎵 Voice Assistant
</button>
```

## 🎵 Voice Profiles

### Welcome Voice (Domi)
- **Purpose**: Personalized greetings and welcome messages
- **Style**: Warm, friendly, inviting
- **Use Cases**: First-time visitors, returning users

### Guide Voice (Elli)
- **Purpose**: Help and guidance responses
- **Style**: Clear, helpful, instructional
- **Use Cases**: Explaining features, answering questions

## 🔧 API Endpoints

### POST /voice-assistant/welcome
Generates personalized welcome greeting.
```javascript
const response = await fetch('/voice-assistant/welcome', {
  method: 'POST',
  headers: getAuthHeaders(),
  body: JSON.stringify({
    user_context: { /* user statistics */ },
    time_of_day: 14 // Current hour
  })
});
```

### POST /voice-assistant/guidance
Answers user questions about the app.
```javascript
const response = await fetch('/voice-assistant/guidance', {
  method: 'POST',
  headers: getAuthHeaders(),
  body: JSON.stringify({
    question: "What can I do here?",
    context: "journaling_help"
  })
});
```

### GET /voice-assistant/user-context
Gets user statistics for personalization.
```javascript
const response = await fetch('/voice-assistant/user-context', {
  headers: getAuthHeaders()
});
```

## 🎯 Integration Strategies

### Strategy 1: First-Time Welcome
```jsx
useEffect(() => {
  const hasVisited = localStorage.getItem('pauz_has_visited');
  if (!hasVisited) {
    setShowAssistant(true);
    setAutoPlayWelcome(true);
    localStorage.setItem('pauz_has_visited', 'true');
  }
}, []);
```

### Strategy 2: Help Button
```jsx
<button 
  className="help-button"
  onClick={() => {
    setShowAssistant(true);
    setAutoPlayWelcome(false);
  }}
>
  🎵 Need Help?
</button>
```

### Strategy 3: Smart Assistance
```jsx
// Detect if user seems stuck
const checkIfStuck = () => {
  const lastActivity = localStorage.getItem('last_activity');
  const inactiveTime = Date.now() - parseInt(lastActivity || 0);
  
  if (inactiveTime > 120000) { // 2 minutes
    setShowAssistant(true);
    setAutoPlayWelcome(false);
  }
};
```

## 💬 Sample Interactions

### Common Questions
- **"What can I do here?"** - Explains all app features
- **"How do I get started?"** - Provides beginner guidance
- **"I'm feeling stuck"** - Offers writing prompts and encouragement
- **"What should I write about?"** - Suggests journaling topics
- **"Encourage me"** - Provides motivational support

### Smart Responses
The assistant recognizes patterns and provides contextual help:
- Time-based greetings ("Good morning", "Good evening")
- Personalized statistics ("You've written 5 journals")
- Activity-based suggestions ("It's been a while since your last journal")

## 🎨 Customization

### Voice Settings
Modify voice profiles in `app/services/voice_service.py`:
```python
self.voice_profiles = {
    "welcome": {
        "voice_id": "29vD33N1CtxCmqQRPOwJ",  # Change voice
        "stability": 0.6,
        "similarity_boost": 0.7,
        "style": 0.4,
        "use_speaker_boost": True
    }
}
```

### Greeting Logic
Update welcome messages in `app/routes/voice_assistant.py`:
```python
def get_personalized_welcome(user: User, user_context: Optional[Dict] = None) -> str:
    # Customize your welcome messages here
    greeting = get_time_based_greeting()
    return f"{greeting}! Welcome back to your journaling space."
```

### Guidance Responses
Add new question patterns in `get_guidance_response()`:
```python
if "meditation" in question_lower:
    return "Try our mindfulness journaling prompts..."
```

## 🔊 Browser Support

### Speech Recognition
The assistant uses the Web Speech API for voice input:
- **Chrome**: Full support
- **Firefox**: Limited support
- **Safari**: Limited support
- **Mobile**: Varies by device

### Fallback Options
If speech recognition isn't available:
1. Users can type their questions
2. All voice responses have text display
3. Mute option for text-only interaction

## 📱 Mobile Optimization

The voice assistant is fully responsive:
- Adapts to smaller screens
- Touch-optimized controls
- Larger buttons for mobile use
- Optimized conversation display

## 🚨 Troubleshooting

### Voice Not Playing
1. Check ElevenLabs API key
2. Verify browser audio permissions
3. Test with different voice profiles

### Authentication Issues
1. Ensure user is logged in
2. Check token format in localStorage
3. Verify backend CORS settings

### Speech Recognition Not Working
1. Check browser compatibility
2. Verify microphone permissions
3. Fallback to typing input

### Performance Issues
1. Cache voice responses
2. Optimize conversation history
3. Use audio compression

## 📈 Analytics & Tracking

Track voice assistant usage:
```javascript
// Log voice assistant interactions
const logAssistantEvent = (action, details) => {
  analytics.track('voice_assistant', {
    action, // 'welcome', 'question', 'close'
    user_id: currentUser.id,
    timestamp: Date.now(),
    ...details
  });
};
```

## 🔮 Future Enhancements

### Phase 3 Ideas
- **Proactive suggestions** based on user patterns
- **Mood detection** in voice input
- **Multilingual support** for different languages
- **Custom voice training** for consistent brand voice

### Advanced Features
- **Voice commands** for app navigation
- **Conversation memory** across sessions
- **Integration with calendar** for time-based suggestions
- **Emotion analysis** of user input

## 🎉 Success Metrics

Track these metrics to measure success:
- **Welcome message completion rate**
- **Questions asked per session**
- **User satisfaction scores**
- **Feature adoption rate**
- **Session duration impact**

## 📞 Support

For issues:
1. Check browser console for errors
2. Verify backend is running
3. Test with `test_voice_assistant.html`
4. Check authentication status

---

**Phase 2 Complete!** 🎉 Your app now has a fully functional voice assistant that welcomes users and provides helpful guidance!