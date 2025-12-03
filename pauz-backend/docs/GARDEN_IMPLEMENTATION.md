# Garden Feature Implementation

## Overview
The garden feature plants flowers whenever a user creates a free journal entry and uses "Reflect with AI". Each flower represents the mood detected from the journal content.

## Backend Implementation

### Updated Mood Mapping
The backend now supports all frontend moods:
- `happy` → 🌻
- `sad` → 🔔  
- `calm` → 🪷
- `excited` → 🌺
- `reflective` → 💐
- `anxious` → 🌸
- `grateful` → 🌼

### Key Backend Changes

#### 1. Updated `free_journal_service.py`
```python
# Enhanced mood analysis with all frontend moods
mood_keywords = {
    "happy": ["happy", "joy", "excited", "grateful", ...],
    "sad": ["sad", "disappointed", "grief", ...],
    "anxious": ["anxious", "worried", "stressed", ...],
    "calm": ["calm", "peaceful", "relaxed", ...],
    "reflective": ["reflective", "thoughtful", ...],
    "excited": ["excited", "thrilled", "enthusiastic", ...],
    "grateful": ["grateful", "thankful", "appreciate", ...]
}

# Flower mapping matches frontend exactly
flower_mapping = {
    "happy": "happy",
    "sad": "sad", 
    "anxious": "anxious",
    "calm": "calm",
    "reflective": "reflective",
    "excited": "excited",
    "grateful": "grateful"
}
```

#### 2. Garden API Endpoints
- `POST /freejournal/{session_id}/reflect` - Triggers AI reflection and plants flower
- `GET /garden/` - Fetches all garden entries for user

## Frontend Implementation

### Files Created
1. **GardenView.jsx** - Main garden component
2. **FlowerCard.jsx** - Individual flower display (unchanged logic)
3. **gardenAPI.js** - API utility functions
4. **useGarden.js** - React hook for garden state
5. **FreeJournalWithGarden.jsx** - Example integration

### How It Works

#### 1. User creates a journal entry
```javascript
// User writes in free journal
// Content is saved to backend
```

#### 2. User clicks "Reflect with AI"
```javascript
const handleReflectWithAI = async () => {
  const result = await freeJournalAPI.reflectWithAI(sessionId);
  // Backend:
  // 1. Analyzes journal content with AI
  // 2. Detects mood (happy, sad, calm, etc.)
  // 3. Creates garden entry with mood + notes
  // 4. Returns analysis result
};
```

#### 3. Backend creates garden entry
```python
# In reflect_with_ai method
analysis = self.analyze_mood_with_gemini(free_journal.content)
garden_service.create_garden_entry(
    user_id=user_id,
    mood=analysis["mood"],
    note=analysis["summary"],
    flower_type=analysis["flower_type"],  # matches mood
    db=db
)
```

#### 4. Garden displays new flower
```javascript
// GardenView fetches updated entries
const entries = await gardenAPI.getGardenEntries();
// Maps to flower cards with proper mood/emoji styling
```

## Integration Steps

### 1. Update your FreeJournal component
```jsx
import { useGarden } from './useGarden';

const FreeJournal = () => {
  const { reflectWithAI } = useGarden();
  const [sessionId, setSessionId] = useState(null);

  // Add reflect button
  <button onClick={() => reflectWithAI(sessionId)}>
    🌱 Reflect with AI
  </button>
};
```

### 2. Replace GardenView with new version
The new GardenView automatically fetches from backend and handles loading/error states.

### 3. Ensure API authentication
Make sure your JWT token is included in requests:
```javascript
headers: {
  'Authorization': `Bearer ${localStorage.getItem('token')}`
}
```

## Data Flow

```
User writes journal → Save content → Click "Reflect with AI" → 
AI analyzes mood → Create garden entry → Garden shows new flower
```

## Testing

1. Create a journal entry with content
2. Click "Reflect with AI" 
3. Check that a new flower appears in garden
4. Verify flower color/emoji matches detected mood
5. Click flower to see journal notes

## Error Handling

- Network failures show retry option
- AI failures fall back to basic mood analysis
- Empty garden shows helpful message
- Loading states prevent duplicate requests

## Future Enhancements

- Flower growth animations based on journal streak
- Seasonal garden themes
- Flower sharing capabilities
- Mood trends visualization