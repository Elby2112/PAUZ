# Pauz Backend

This is the Python backend for the Pauz journaling app.

## Features

- Google login via OAuth2 with JWT-based authentication
- Guided Journal: user selects a topic, AI generates 9 prompts about the topic
- Save user responses in SmartBuckets
- Export journal as PDF
- Save PDF to Vultr Object Storage
- Free Journal with AI-powered hints and reflections
- Voice-to-text journaling with ElevenLabs (placeholder)
- Garden feature to track mood and insights

## Setup

1.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up environment variables:**

    Create a `.env` file in the root directory and add the following variables:

    ```
    GOOGLE_CLIENT_ID=your_google_client_id
    GOOGLE_CLIENT_SECRET=your_google_client_secret
    REDIRECT_URI=http://localhost:8000/auth/callback
    VULTR_ACCESS_KEY=your_vultr_access_key
    VULTR_SECRET_KEY=your_vultr_secret_key
    VULTR_REGION=your_vultr_region
    VULTR_BUCKET_NAME=your_vultr_bucket_name
    AI_API_KEY=your_ai_api_key
    SMARTBUCKET_NAME=your_smartbucket_name
    FREEJOURNALS_BUCKET_NAME=FreeJournals
    HINTS_BUCKET_NAME=Hints
    GARDEN_BUCKET_NAME=Garden
    ELEVENLABS_API_KEY=your_elevenlabs_api_key
    JWT_SECRET_KEY=a_very_secret_key # Change this to a strong, random string
    JWT_ALGORITHM=HS256
    ```

3.  **Run the application:**

    ```bash
    uvicorn app.main:app --reload
    ```

    The application will be running at `http://localhost:8000`.

## API Endpoints

### General
-   `GET /`: Welcome message.

### Authentication
-   `GET /auth/login`: Redirects to Google login.
-   `GET /auth/callback`: Handles Google OAuth2 callback and returns a JWT access token.

All other endpoints require authentication. You must include the JWT in the `Authorization` header of your requests: `Authorization: Bearer <your_jwt>`.

### Guided Journal
-   `POST /journal/prompts`: Generates journal prompts for a given topic.
-   `POST /journal/`: Creates a new journal.
-   `GET /journal/{journal_id}`: Retrieves a journal.
-   `POST /journal/{journal_id}/export`: Exports a journal to PDF and uploads it to Vultr.

### Free Journal
-   `POST /freejournal/`: Creates a new free journal session.
-   `POST /freejournal/save`: Saves user content.
-   `POST /freejournal/hints`: Gets hints for writing.
-   `POST /freejournal/voice`: Transcribes voice to text.
-   `POST /freejournal/{sessionId}/reflect`: Reflects on the journal with AI.
-   `POST /freejournal/{sessionId}/export`: Exports the free journal to PDF.

### Garden
-   `POST /garden/save`: Saves a garden entry.
-   `GET /garden/`: Retrieves all garden entries for the authenticated user.
