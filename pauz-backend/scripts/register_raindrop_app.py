#!/usr/bin/env python3
"""
Script to register Pauz application with Raindrop for automatic cataloguing
"""
import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.raindrop_service import raindrop_service

def main():
    """Main registration function"""
    print("🚀 Setting up Pauz application with Raindrop...")
    
    # Check environment
    if not os.getenv('AI_API_KEY'):
        print("❌ AI_API_KEY environment variable is required")
        print("Please set up your .env file with a valid Raindrop API key")
        return False
    
    if not os.getenv('APPLICATION_NAME'):
        print("⚠️ APPLICATION_NAME not set, using default: pauz-journaling")
    
    if not os.getenv('RAINDROP_ORG'):
        print("⚠️ RAINDROP_ORG not set, using default: tenapi")
    
    # Get application info
    print("\n📋 Getting application info...")
    app_info = raindrop_service.get_application_info()
    print(f"   Application Name: {app_info['application_name']}")
    print(f"   Organization: {os.getenv('RAINDROP_ORG', 'tenapi')}")
    print(f"   API Key Configured: {app_info['api_key_configured']}")
    print(f"   Client Initialized: {app_info['client_initialized']}")
    
    # Test connection
    print("\n🔗 Testing Raindrop connection...")
    test_result = raindrop_service.test_connection()
    
    if test_result.get("success"):
        print("✅ Connection successful!")
        if "note" in test_result:
            print(f"   Note: {test_result['note']}")
    else:
        # Check if it's just a bucket issue, which is expected
        error_msg = test_result.get('error', '')
        if "not found" in error_msg and "Bucket" in error_msg:
            print("✅ Connection successful! (Buckets will be created on first use)")
        else:
            print(f"❌ Connection failed: {test_result.get('error')}")
            return False
    
    # Show bucket status
    print("\n🪣 Application Buckets:")
    buckets = [
        {"name": "journal-prompts", "description": "AI-generated journal prompts and hints"},
        {"name": "journal-analysis", "description": "AI analysis of journal entries for mood and insights"},
        {"name": "FreeJournals", "description": "User's free-form journal entries"},
        {"name": "Hints", "description": "Writing hints and suggestions"},
        {"name": "Garden", "description": "Mood tracking and personal insights"}
    ]
    
    for bucket in buckets:
        print(f"   📦 {bucket['name']}: {bucket['description']}")
    
    print("\n✅ Application is ready to use with Raindrop AI!")
    print("🔄 Buckets will be automatically created on first use")
    print("🎉 Your PAUZ application is now configured and ready to use with Raindrop!")
    
    return True

if __name__ == "__main__":
    load_dotenv()
    success = main()
    sys.exit(0 if success else 1)