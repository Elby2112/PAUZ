#!/usr/bin/env python3
"""
Debug guided journal save functionality
"""
import requests
import json
import sys
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()
API_BASE = "http://localhost:8000"

def test_guided_journal_save():
    print("🔍 Debugging Guided Journal Save")
    print("=" * 50)
    
    # Test 1: Check if endpoints are accessible
    print("1. Testing endpoint accessibility...")
    try:
        response = requests.get(f"{API_BASE}/guided_journal/")
        print(f"   GET /guided_journal/ - Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Requires authentication (expected)")
        elif response.status_code == 404:
            print("   ❌ Endpoint not found - route issue!")
            return
        else:
            print(f"   ⚠️  Unexpected: {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
        return
    
    # Test 2: Test prompts endpoint
    print("\n2. Testing prompts endpoint...")
    try:
        response = requests.post(f"{API_BASE}/guided_journal/prompts", 
                               json={"topic": "Test Topic"})
        print(f"   POST /guided_journal/prompts - Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Requires authentication (expected)")
        elif response.status_code == 200:
            prompts = response.json()
            print(f"   ✅ Got {len(prompts)} prompts")
        else:
            print(f"   ⚠️  {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test save with sample data (no auth)
    print("\n3. Testing save endpoint (no auth)...")
    sample_data = {
        "topic": "Test Journal",
        "prompts": [{"id": 1, "text": "How are you?"}],
        "entries": [{
            "prompt_id": 1, 
            "prompt_text": "How are you?", 
            "response": "Good!", 
            "created_at": "2024-01-01T12:00:00Z"
        }]
    }
    
    try:
        response = requests.post(f"{API_BASE}/guided_journal/", 
                               json=sample_data)
        print(f"   POST /guided_journal/ - Status: {response.status_code}")
        if response.status_code == 401:
            print("   ✅ Requires authentication (expected)")
        elif response.status_code == 422:
            print("   ✅ Validates input (422)")
        elif response.status_code == 500:
            print(f"   ❌ Server error: {response.text[:200]}")
        else:
            print(f"   ⚠️  {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Check backend services directly
    print("\n4. Testing backend services...")
    try:
        sys.path.append('.')
        from app.services.guided_journal_service import guided_journal_service
        print("   ✅ Guided journal service loads")
        
        # Test service initialization
        print(f"   ✅ SmartBucket client: {'Available' if guided_journal_service.client else 'NOT AVAILABLE'}")
        
    except Exception as e:
        print(f"   ❌ Service error: {e}")
    
    # Test 5: Check environment variables
    print("\n5. Checking environment variables...")
    required_vars = ['AI_API_KEY', 'RAINDROP_ORG', 'APPLICATION_NAME']
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: SET")
        else:
            print(f"   ❌ {var}: NOT SET")
    
    # Test 6: Check Raindrop bucket
    print("\n6. Testing SmartBucket access...")
    try:
        from app.services.guided_journal_service import guided_journal_service
        if guided_journal_service.client:
            # Try to access guided-journals bucket
            try:
                response = guided_journal_service.client.bucket.list(
                    bucket_location={
                        "bucket": {
                            "name": "guided-journals",
                            "application_name": guided_journal_service.application_name
                        }
                    }
                )
                print(f"   ✅ Bucket accessible: {len(response)} items")
            except Exception as bucket_error:
                print(f"   ⚠️  Bucket access error: {bucket_error}")
                print(f"   💡 This might be expected if bucket doesn't exist yet")
        else:
            print("   ❌ SmartBucket client not available")
    except Exception as e:
        print(f"   ❌ Bucket test error: {e}")
    
    print("\n🎯 Debug Summary:")
    print("   - Check browser console for specific error messages")
    print("   - Verify AI_API_KEY is set in .env")
    print("   - Make sure authentication token is valid")
    print("   - Check if SmartBucket bucket 'guided-journals' exists")

if __name__ == "__main__":
    test_guided_journal_save()