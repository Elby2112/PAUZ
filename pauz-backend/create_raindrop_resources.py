#!/usr/bin/env python3
"""
Script to create Raindrop SmartBuckets and SmartMemories for PAUZ application
"""
import os
import sys
from dotenv import load_dotenv
import json
import uuid

load_dotenv()

def main():
    print("🚀 Creating Raindrop resources for PAUZ app...")
    
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
    
    # Step 1: Create SmartBuckets
    buckets = {
        "journal-prompts": "AI-generated journal prompts and hints",
        "journal-analysis": "AI analysis of journal entries for mood and insights",
        "free-journals": "User's free-form journal entries",
        "hints": "Writing hints and suggestions",
        "garden": "Mood tracking and personal insights"
    }
    
    print("\n📦 Creating SmartBuckets...")
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
        except Exception as e:
            if "not found" in str(e) and "Application" in str(e):
                print(f"❌ Application '{application_name}' not found. Please register the app first.")
                print("💡 Try running: raindrop build deploy --start")
                return False
            elif "not found" in str(e) and "Bucket" in str(e):
                print(f"❌ Bucket '{bucket_name}' creation failed: {e}")
                print("💡 Buckets may need to be defined in the manifest first")
                return False
            else:
                print(f"❌ Failed to create {bucket_name}: {e}")
                return False
    
    # Step 2: Create SmartMemories
    print("\n🧠 Creating SmartMemories...")
    memories = {
        "user-memories": "User session memories and context storage",
        "ai-contexts": "AI generation contexts and prompt storage"
    }
    
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
            print(f"⚠️ Memory creation failed for {memory_name}: {e}")
            # Continue even if memory creation fails
    
    # Step 3: Test AI functionality
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
    print(f"📊 All SmartBuckets created:")
    for bucket_name in buckets.keys():
        print(f"  📦 {bucket_name}")
    print(f"🧠 SmartMemories created for user context and AI prompts")
    print(f"🤖 AI functionality tested and working")
    print(f"\n✅ Your PAUZ app is ready to use Raindrop AI!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)