#!/usr/bin/env python3
"""
Script to create and test Raindrop SmartBuckets for PAUZ application
"""
import os
import sys
from dotenv import load_dotenv
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def create_bucket(client, bucket_name, organization_name):
    """Create a bucket by putting a test document in it"""
    try:
        print(f"📦 Creating bucket: {bucket_name}")
        client.bucket.put(
            bucket_location={
                "bucket": {
                    "name": bucket_name,
                    "application_name": organization_name
                }
            },
            key=f"init-{bucket_name}",
            content=f"Initialization document for {bucket_name} bucket",
            content_type="text/plain"
        )
        print(f"✅ Bucket '{bucket_name}' created successfully")
        return True
    except Exception as e:
        # Check if bucket already exists by trying to get it
        try:
            client.bucket.get(
                bucket_location={
                    "bucket": {
                        "name": bucket_name,
                        "application_name": organization_name
                    }
                },
                key=f"init-{bucket_name}"
            )
            print(f"✅ Bucket '{bucket_name}' already exists")
            return True
        except:
            print(f"❌ Failed to create bucket '{bucket_name}': {e}")
            return False

def test_bucket_ai(client, bucket_name, organization_name):
    """Test AI functionality with a bucket"""
    try:
        print(f"🧪 Testing AI with bucket: {bucket_name}")
        
        # Put a test document
        test_key = f"ai-test-{bucket_name}"
        client.bucket.put(
            bucket_location={
                "bucket": {
                    "name": bucket_name,
                    "application_name": organization_name
                }
            },
            key=test_key,
            content="This is a test document for AI processing.",
            content_type="text/plain"
        )
        
        # Test AI query
        response = client.query.document_query(
            bucket_location={
                "bucket": {
                    "name": bucket_name,
                    "application_name": organization_name
                }
            },
            input="Summarize this document in one sentence",
            object_id=test_key,
            request_id=f"test-{bucket_name}"
        )
        
        answer = getattr(response, 'answer', str(response))
        print(f"✅ AI test successful for '{bucket_name}': {answer[:50]}...")
        return True
        
    except Exception as e:
        print(f"❌ AI test failed for '{bucket_name}': {e}")
        return False

def main():
    print("🚀 Setting up Raindrop SmartBuckets for PAUZ...")
    
    # Check environment
    api_key = os.getenv('AI_API_KEY')
    organization_name = os.getenv('RAINDROP_ORG', 'tenapi')
    
    if not api_key:
        print("❌ AI_API_KEY not found in environment variables")
        return False
    
    try:
        from raindrop import Raindrop
        client = Raindrop(api_key=api_key)
        print(f"✅ Raindrop client initialized for org: {organization_name}")
    except Exception as e:
        print(f"❌ Failed to initialize Raindrop client: {e}")
        return False
    
    # Buckets to create
    buckets = [
        "journal-prompts",
        "journal-analysis", 
        "free-journals",
        "hints",
        "garden"
    ]
    
    # Create buckets
    print("\n📦 Creating SmartBuckets...")
    created_buckets = []
    for bucket in buckets:
        if create_bucket(client, bucket, organization_name):
            created_buckets.append(bucket)
    
    if not created_buckets:
        print("❌ No buckets were created successfully")
        return False
    
    # Test AI functionality with one bucket
    print("\n🧪 Testing AI functionality...")
    test_bucket = created_buckets[0]  # Test with the first successful bucket
    if test_bucket_ai(client, test_bucket, organization_name):
        print("✅ AI functionality test passed!")
    else:
        print("⚠️ AI functionality test failed, but buckets were created")
    
    # Test prompt generation
    print("\n🔮 Testing prompt generation...")
    try:
        from app.services.guided_journal_service import guided_journal_service
        prompts = guided_journal_service.generate_prompts('mindfulness', 3)
        print(f"✅ Prompt generation test successful! Generated {len(prompts)} prompts")
        for i, prompt in enumerate(prompts):
            print(f"  {i+1}. {prompt['text'][:60]}...")
    except Exception as e:
        print(f"❌ Prompt generation test failed: {e}")
    
    print(f"\n🎉 Setup complete! {len(created_buckets)} SmartBuckets are ready for use:")
    for bucket in created_buckets:
        print(f"  📦 {bucket}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)