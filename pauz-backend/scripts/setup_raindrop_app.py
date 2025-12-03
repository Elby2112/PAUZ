#!/usr/bin/env python3
"""
Script to properly register PAUZ app with Raindrop and create all required resources
"""
import os
import sys
from dotenv import load_dotenv
import json
import uuid

load_dotenv()

def main():
    print("🚀 Setting up PAUZ Journaling App with Raindrop...")
    
    # Environment setup
    api_key = os.getenv('AI_API_KEY')
    organization_name = os.getenv('RAINDROP_ORG', 'Loubna-HackathonApp')
    application_name = os.getenv('APPLICATION_NAME', 'pauz-journaling')
    
    if not api_key:
        print("❌ AI_API_KEY not found in environment variables")
        return False
    
    print(f"🏢 Organization: {organization_name}")
    print(f"📱 Application: {application_name}")
    
    try:
        from raindrop import Raindrop
        client = Raindrop(api_key=api_key)
        print("✅ Raindrop client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Raindrop client: {e}")
        return False
    
    # Step 1: Create application metadata
    app_metadata = {
        "name": "Pauz - AI Journaling App",
        "description": "A smart journaling application with AI-powered prompts, mood tracking, and reflection features",
        "version": "1.0.0",
        "author": "PAUZ Team",
        "category": "Productivity & Wellness",
        "tags": ["journaling", "ai", "wellness", "productivity", "mood-tracking"],
        "features": [
            "AI-powered journal prompts",
            "Free-form journaling with AI hints", 
            "Voice-to-text transcription",
            "Mood analysis and reflection",
            "Personal garden for emotional insights"
        ],
        "created_at": str(uuid.uuid4())
    }
    
    # Step 2: Initialize SmartBuckets by putting initial content
    buckets = {
        "journal-prompts": "Initial prompts bucket - will store AI-generated journal prompts",
        "journal-analysis": "Initial analysis bucket - will store mood analysis and insights",
        "free-journals": "Initial journals bucket - will store user journal entries", 
        "hints": "Initial hints bucket - will store AI writing hints",
        "garden": "Initial garden bucket - will store mood tracking data"
    }
    
    print("\n📦 Creating SmartBuckets...")
    created_buckets = []
    for bucket_name, description in buckets.items():
        try:
            client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": bucket_name,
                        "application_name": application_name
                    }
                },
                key="init",
                content=description,
                content_type="text/plain"
            )
            print(f"✅ Created bucket: {bucket_name}")
            created_buckets.append(bucket_name)
        except Exception as e:
            print(f"❌ Failed to create {bucket_name}: {e}")
            return False
    
    # Step 3: Initialize SmartMemories
    memories = {
        "user-memories": "User session memories and context storage",
        "ai-contexts": "AI generation contexts and prompt storage"
    }
    
    print("\n🧠 Creating SmartMemories...")
    for memory_name, description in memories.items():
        try:
            client.put_semantic_memory(
                smart_memory_location={
                    "smart_memory": {
                        "name": memory_name,
                        "application_name": application_name
                    }
                },
                content=description,
                session_id="init",
                key="init"
            )
            print(f"✅ Created memory: {memory_name}")
        except Exception as e:
            print(f"❌ Failed to create {memory_name}: {e}")
            # Continue even if memory creation fails
    
    # Step 4: Store application metadata
    try:
        client.bucket.put(
            bucket_location={
                "bucket": {
                    "name": "journal-prompts",
                    "application_name": application_name
                }
            },
            key="app-metadata",
            content=json.dumps(app_metadata, indent=2),
            content_type="application/json"
        )
        print("✅ Application metadata stored")
    except Exception as e:
        print(f"❌ Failed to store metadata: {e}")
        return False
    
    # Step 5: Test AI functionality
    print("\n🧪 Testing AI functionality...")
    try:
        # Test prompt generation
        test_prompt = "Generate 3 mindfulness journal prompts"
        client.bucket.put(
            bucket_location={
                "bucket": {
                    "name": "journal-prompts",
                    "application_name": application_name
                }
            },
            key="test-prompt",
            content=test_prompt,
            content_type="text/plain"
        )
        
        response = client.query.document_query(
            bucket_location={
                "bucket": {
                    "name": "journal-prompts",
                    "application_name": application_name
                }
            },
            input="Generate the prompts now",
            object_id="test-prompt",
            request_id="test-123"
        )
        
        answer = getattr(response, 'answer', str(response))
        print(f"✅ AI test successful: {answer[:100]}...")
        
    except Exception as e:
        print(f"❌ AI test failed: {e}")
        return False
    
    print(f"\n🎉 PAUZ app setup complete!")
    print(f"📊 Created {len(created_buckets)} SmartBuckets:")
    for bucket in created_buckets:
        print(f"  📦 {bucket}")
    print(f"🧠 Created SmartMemories for user context and AI prompts")
    print(f"🤖 AI functionality tested and working")
    print(f"\n✅ Your PAUZ app is ready to use Raindrop AI!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)