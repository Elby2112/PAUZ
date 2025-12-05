# Voice Hints Feature Documentation

## 🎯 Overview
The Voice Hints feature allows users to have their journaling hints read aloud using ElevenLabs text-to-speech technology. This creates a more accessible and engaging journaling experience.

## 🏗️ Architecture

### Backend Components

#### 1. Voice Service (`app/services/voice_service.py`)
- **Purpose**: Handles all ElevenLabs API interactions
- **Key Features**:
  - Multiple voice profiles (hints, welcome, guide)
  - Configurable voice settings
  - Base64 audio encoding for easy transmission
  - Error handling and fallbacks

#### 2. API Endpoints (`app/routes/free_journal.py`)
- `POST /free-journal/{session_id}/hints/{hint_id}/voice` - Convert specific hint to speech
- `POST /free-journal/text-to-voice` - Generic text-to-speech conversion
- `GET /free-journal/voices/available` - List available ElevenLabs voices

### Frontend Integration

#### 1. Voice Player Class (`voice_hints_frontend_example.js`)
- Handles audio playback
- Manages button states
- Error handling and user feedback

## 🚀 Setup Instructions

### 1. Backend Setup

1. **Install Dependencies**:
   ```bash
   # ElevenLabs library should already be in config/requirements.txt
   pip install elevenlabs
   ```

2. **Configure API Key**:
   ```bash
   export ELEVENLABS_API_KEY="your_api_key_here"
   # Or add to your .env file
   ```

3. **Test the Service**:
   ```bash
   python test_voice_hints_integration.py
   ```

### 2. Frontend Integration

1. **Include the Voice Player**:
   ```html
   <script src="voice_hints_frontend_example.js"></script>
   ```

2. **Add Voice Buttons to Hints**:
   ```javascript
   // After loading hints, add voice buttons
   addVoiceButtonsToHints();
   ```

3. **CSS Styling**:
   ```css
   /* Add to your CSS file */
   .voice-button {
       margin-left: 8px;
       padding: 4px 8px;
       background: #4CAF50;
       color: white;
       border: none;
       border-radius: 4px;
       cursor: pointer;
       font-size: 12px;
       transition: all 0.2s ease;
   }
   ```

## 🎵 Voice Profiles

### Available Profiles

1. **"hints"** (Default)
   - Voice: Rachel
   - Style: Warm, gentle, encouraging
   - Best for: Journaling hints and guidance

2. **"welcome"**
   - Voice: Domi
   - Style: Friendly, welcoming
   - Best for: App greetings and introductions

3. **"guide"**
   - Voice: Elli
   - Style: Clear, instructive
   - Best for: Instructions and explanations

### Voice Settings

Each profile has optimized settings:
- **Stability**: Controls consistency (0.0-1.0)
- **Similarity Boost**: Voice clarity (0.0-1.0)
- **Style**: Expressiveness (0.0-1.0)
- **Speaker Boost**: Enhance voice quality

## 📡 API Usage

### Convert Hint to Voice

```javascript
// Direct API call example
async function playHint(hintText) {
    const response = await fetch('/free-journal/text-to-voice', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` // if auth required
        },
        body: JSON.stringify({
            text: hintText,
            voice_profile: 'hints'
        })
    });
    
    const result = await response.json();
    
    if (result.success) {
        // Play the audio
        const audio = new Audio(`data:${result.content_type};base64,${result.audio_data}`);
        audio.play();
    }
}
```

### Get Available Voices

```javascript
async function getVoices() {
    const response = await fetch('/free-journal/voices/available');
    const result = await response.json();
    
    console.log('Available voices:', result.voices);
}
```

## 🧪 Testing

### Backend Tests

1. **Integration Test**:
   ```bash
   python test_voice_hints_integration.py
   ```

2. **API Test**:
   ```bash
   python test_voice_hints.py
   ```

### Frontend Testing

1. **Test Voice Playback**:
   - Load hints in your app
   - Click "Read Aloud" buttons
   - Verify audio plays correctly

2. **Test Different Profiles**:
   - Try different voice profiles
   - Check audio quality and style

## 🔧 Configuration

### Environment Variables

```bash
ELEVENLABS_API_KEY=your_api_key_here
```

### Voice Service Customization

You can customize voice settings in `app/services/voice_service.py`:

```python
self.voice_profiles = {
    "custom_profile": {
        "voice_id": "your_preferred_voice",
        "stability": 0.7,
        "similarity_boost": 0.6,
        "style": 0.3,
        "use_speaker_boost": True
    }
}
```

## 🎨 UI/UX Recommendations

### Button Design
- Use speaker icon (🔊) for clear indication
- Show loading state during generation
- Provide visual feedback during playback

### Audio Controls
- Add play/pause functionality
- Show remaining time
- Allow volume control

### Error Handling
- Display user-friendly error messages
- Provide retry functionality
- Fallback to text-only if voice fails

## 🚨 Troubleshooting

### Common Issues

1. **API Key Not Working**
   - Verify your ElevenLabs API key
   - Check if you have sufficient credits

2. **No Audio Playing**
   - Check browser audio permissions
   - Verify audio format support
   - Check network connection

3. **Voice Generation Fails**
   - Check API rate limits
   - Verify text length (max 5000 characters)
   - Check voice ID availability

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📈 Performance Considerations

### Audio Caching
- Cache generated audio for repeated hints
- Use browser localStorage for frequent hints

### API Rate Limits
- ElevenLabs has rate limits
- Implement client-side throttling
- Cache popular voice responses

### File Sizes
- Average hint audio: 20-50 KB
- Consider compression for longer texts
- Monitor user data usage

## 🔮 Future Enhancements

### Phase 2: Welcome Assistant
- Voice greeting on app entry
- Personalized welcome messages
- Context-aware introductions

### Phase 3: Interactive Guide
- Voice-to-voice conversations
- Natural language understanding
- Contextual help system

### Phase 4: Full Integration
- Voice navigation throughout app
- Hands-free journaling
- Advanced voice controls

## 📞 Support

For issues with:
- **ElevenLabs API**: Check their documentation
- **Backend Integration**: Review service logs
- **Frontend Issues**: Check browser console
- **Authentication**: Verify token handling

---

**Version**: 1.0  
**Last Updated**: Current Date  
**Status**: ✅ Ready for Production