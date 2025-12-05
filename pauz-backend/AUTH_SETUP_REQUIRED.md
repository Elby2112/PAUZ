# 🚨 AUTHENTICATION SETUP REQUIRED

## Current Status
The authentication system will **NOT WORK** until you configure the environment variables with real API keys.

## 🔑 Required Setup

### 1. Google OAuth (Required for Login)
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Create OAuth 2.0 credentials
5. Add your redirect URIs (e.g., `http://localhost:8000/auth/google/callback`)
6. Update `.env` with your credentials:

```env
GOOGLE_CLIENT_ID=your-actual-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
```

### 2. JWT Secret (Required)
Generate a secure JWT secret:
```bash
openssl rand -base64 32
```
Update `.env`:
```env
JWT_SECRET_KEY=your-generated-secret-key
```

### 3. AI Services (For AI Features)
- **Gemini API**: Get key from [Google AI Studio](https://aistudio.google.com/)
- **ElevenLabs**: Get API key from [ElevenLabs Dashboard](https://elevenlabs.io/)

### 4. Raindrop Storage (For Cloud Storage)
Get API key from your Raindrop account and update:
```env
AI_API_KEY=your-raindrop-api-key
RAINDROP_ORG=your-organization-name
APPLICATION_NAME=pauz-journaling
```

## 🧪 Testing After Setup

1. Start the app: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Go to `http://localhost:8000/docs`
3. Test the `/auth/google` endpoint
4. Check if login flow works

## ⚠️ Without These Setup Steps:
- ❌ Login/authentication will fail
- ❌ AI features won't work
- ❌ Voice transcription won't work
- ❌ Cloud storage won't work

## ✅ With Proper Setup:
- ✅ Google OAuth login works
- ✅ AI journaling features work
- ✅ Voice recording and transcription
- ✅ PDF export functionality
- ✅ Garden mood tracking