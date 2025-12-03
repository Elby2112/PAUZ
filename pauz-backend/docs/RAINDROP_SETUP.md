# Raindrop Integration Setup Guide

This guide explains how to set up your Pauz application to be automatically catalogued in LiquidMetal AI through Raindrop.

## Prerequisites

1. **Raindrop API Key**: You need a valid Raindrop API key with partner access
2. **Environment Setup**: All required environment variables configured

## Setup Steps

### 1. Environment Configuration

Create a `.env` file with the following required variables:

```bash
# Required for Raindrop
APPLICATION_NAME=pauz-journaling
AI_API_KEY=your_raindrop_api_key

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
REDIRECT_URI=http://localhost:8000/auth/callback

# Other required variables...
```

### 2. Register Your Application

Run the registration script to catalog your application:

```bash
python register_raindrop_app.py
```

This will:
- Register your application with Raindrop
- Create required SmartBuckets
- Enable automatic cataloguing in LiquidMetal AI

### 3. Application Structure

Your application now includes:

- `raindrop-app.json`: Application metadata for cataloguing
- `app/services/raindrop_service.py`: Raindrop integration service
- `register_raindrop_app.py`: Registration script
- Updated main app with Raindrop initialization

## How It Works

### Automatic Cataloguing

When you register your application, Raindrop:

1. **Creates Application Entry**: Adds your app to the Raindrop registry
2. **Generates Catalogue Metadata**: Uses `raindrop-app.json` for catalogue info
3. **Sets Up SmartBuckets**: Creates the data buckets your application needs
4. **Enables Discovery**: Makes your app discoverable in LiquidMetal AI

### SmartBuckets

Your application uses these SmartBuckets:

- `journal-prompts`: AI-generated prompts and hints
- `journal-analysis`: AI analysis of journal entries
- `FreeJournals`: User journal entries
- `Hints`: Writing assistance
- `Garden`: Mood tracking data

### API Integration

Your application automatically uses Raindrop for:

- AI inference through `Raindrop.query.document_query()`
- Data storage through SmartBuckets
- Application metadata management

## Verification

### Check Application Status

You can check if your application is properly registered:

```python
from app.services.raindrop_service import raindrop_service
status = raindrop_service.get_application_status()
print(status)
```

### Expected Output

```json
{
  "application_name": "pauz-journaling",
  "status": {...},
  "is_catalogued": true,
  "buckets": ["journal-prompts", "journal-analysis", "FreeJournals", "Hints", "Garden"]
}
```

## Troubleshooting

### Common Issues

1. **Missing API Key**: Ensure `AI_API_KEY` is set in your `.env`
2. **Application Not Found**: Check that `APPLICATION_NAME` is consistent
3. **Registration Failed**: Verify your Raindrop partner permissions
4. **Buckets Not Created**: Check bucket names don't conflict

### Debug Mode

Enable debug logging by setting:

```bash
RAINDROP_DEBUG=true
```

## Next Steps

After successful registration:

1. **Test Your Application**: Start your app and verify Raindrop integration
2. **Check LiquidMetal AI**: Your app should appear in the catalogue
3. **Monitor Usage**: Check Raindrop dashboard for application metrics
4. **Update Metadata**: Modify `raindrop-app.json` as needed

## Support

For Raindrop-specific issues:
- Check the Raindrop documentation
- Contact Raindrop support through your partner dashboard
- Review the application logs for error details

## Application Metadata

Your application is catalogued with:

- **Name**: Pauz - AI Journaling App
- **Category**: Productivity & Wellness
- **Tags**: journaling, ai, wellness, productivity, mood-tracking
- **Features**: Google OAuth, AI prompts, voice-to-text, PDF export

This metadata makes your application discoverable and attractive to users in the LiquidMetal AI catalogue.