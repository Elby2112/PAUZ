# PAUZ Backend API

A clean, professional backend API for the PAUZ journaling application with AI-powered features.

## 🏗️ Project Structure

```
pauz-backend/
├── backend/
│   ├── app/                    # Main application code
│   │   ├── models/            # Database models
│   │   ├── routes/            # API endpoints
│   │   ├── services/          # Business logic
│   │   └── utils/             # Utility functions
│   ├── tests/                 # Test suite
│   ├── scripts/               # Setup and utility scripts
│   ├── docs/                  # Documentation
│   ├── config/                # Configuration files
│   └── *.db                   # Database files
└── README.md
```

## 🚀 Features

### Journal Management
- **Free Journal**: Open-ended journaling with AI insights
- **Guided Journal**: Structured journaling with prompts
- **Voice Recording**: Speech-to-text transcription (ElevenLabs)
- **PDF Export**: Beautiful PDF generation of journal entries

### AI Integration
- **Gemini AI**: Free AI-powered hints and mood analysis
- **Garden System**: Visual mood tracking with flower representations
- **Smart Reflections**: AI-generated insights from journal content

### Authentication & Storage
- **OAuth Integration**: Google authentication
- **Raindrop Storage**: Cloud storage integration
- **User Management**: Secure user sessions and profiles

## 📋 API Endpoints

### Authentication
- `POST /auth/google` - Google OAuth login
- `GET /auth/me` - Get current user info

### Free Journal
- `GET /freejournal/` - List user journals
- `POST /freejournal/` - Create new session
- `POST /freejournal/{session_id}/save` - Save content
- `POST /freejournal/{session_id}/voice` - Transcribe audio
- `POST /freejournal/{session_id}/reflect` - AI reflection
- `POST /freejournal/{session_id}/export` - Export to PDF

### Guided Journal
- `GET /guided_journal/` - List guided journals
- `POST /guided_journal/` - Create guided journal
- `GET /guided_journal/{id}` - Get specific journal
- `DELETE /guided_journal/{id}` - Delete journal

### Garden
- `GET /garden/` - Get user garden
- `POST /garden/` - Create garden entry
- `DELETE /garden/{entry_id}` - Delete garden entry

### Profile & Stats
- `GET /profile/stats` - Get user statistics
- `GET /profile/garden-stats` - Get garden statistics

## 🛠️ Setup

### Prerequisites
- Python 3.11+
- PostgreSQL (or SQLite for development)
- Redis (for caching, optional)

### Installation

1. **Clone and setup environment**
```bash
git clone <repository-url>
cd pauz-backend
```

2. **Install dependencies**
```bash
cd backend
pip install -r config/requirements.txt
```

3. **Environment configuration**
```bash
cp config/.env.example config/.env
# Edit config/.env with your API keys and settings
```

4. **Database setup**
```bash
# The app will create the database automatically on first run
# or you can run migrations manually if needed
```

5. **Run the application**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 Configuration

### Required Environment Variables
```env
# Database
DATABASE_URL=sqlite:///./database.db

# Authentication
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# AI Services
GEMINI_API_KEY=your-gemini-api-key
ELEVENLABS_API_KEY=your-elevenlabs-api-key
OPENAI_API_KEY=your-openai-api-key  # Optional

# Raindrop Storage
AI_API_KEY=your-raindrop-api-key
RAINDROP_ORG=your-organization-name
APPLICATION_NAME=your-app-name
```

## 🧪 Testing

Run the test suite:
```bash
cd backend
pytest tests/ -v
```

Run specific test categories:
```bash
pytest tests/test_auth.py -v
pytest tests/test_journals.py -v
pytest tests/test_garden.py -v
```

## 📊 Database Schema

### Core Models
- **User**: User accounts and authentication
- **FreeJournal**: Open journal entries
- **GuidedJournal**: Structured journal sessions
- **Garden**: Mood tracking entries
- **Hint**: AI-generated writing hints

## 🔍 API Documentation

Once running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🚨 Error Handling

The API uses standard HTTP status codes:
- `200` - Success
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `404` - Not Found
- `500` - Internal Server Error

## 📈 Monitoring & Logs

- Application logs are written to `backend/`
- Use the scripts in `backend/scripts/` for debugging
- Check `backend/docs/` for detailed troubleshooting guides

## 🤝 Contributing

1. Follow the existing code structure
2. Write tests for new features
3. Update documentation
4. Use the provided scripts for validation

## 📝 License

[Add your license information here]

---

**Professional Backend API** - Clean, tested, and production-ready.