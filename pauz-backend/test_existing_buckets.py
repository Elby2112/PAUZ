#!/usr/bin/env python3
"""
Test what buckets actually exist and their structure
"""
import sys
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv()

try:
    from app.services.guided_journal_service import guided_journal_service
    
    print("🔍 Testing Existing Bucket Structure")
    print("=" * 45)
    
    if guided_journal_service.client:
        print("✅ SmartBucket client available")
        
        # Test the hints bucket structure that we know works
        print("\n📋 Testing hints bucket structure...")
        try:
            hints_response = guided_journal_service.client.bucket.list(
                bucket_location={
                    "bucket": {
                        "name": "hints",
                        "application_name": guided_journal_service.application_name
                    }
                }
            )
            print(f"✅ Hints bucket response type: {type(hints_response)}")
            
            if hasattr(hints_response, 'bucket_list'):
                print(f"✅ Bucket list items: {len(hints_response.bucket_list)}")
                for item in hints_response.bucket_list[:3]:  # Show first 3
                    print(f"   - {item}")
            elif hasattr(hints_response, '__iter__'):
                items = list(hints_response)
                print(f"✅ Hints bucket items: {len(items)}")
                for item in items[:3]:
                    print(f"   - {item}")
            else:
                print(f"⚠️  Unexpected hints response format: {str(hints_response)[:100]}")
                
        except Exception as e:
            print(f"❌ Hints bucket error: {e}")
        
        # Try using the same bucket structure as hints
        print("\n🔧 Testing guided journals in hints bucket...")
        try:
            test_data = {
                "id": "test-guided-journal",
                "user_id": "test-user",
                "topic": "Test Topic",
                "created_at": "2024-01-01T12:00:00Z",
                "prompts": [{"id": 1, "text": "Test prompt"}],
                "entries": [{"prompt_id": 1, "response": "Test response"}],
                "type": "guided_journal"
            }
            
            import base64
            import json
            
            # Try storing guided journal in hints bucket with different key
            guided_journal_service.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": "hints",
                        "application_name": guided_journal_service.application_name
                    }
                },
                key="guided_journal_test123",
                content=base64.b64encode(json.dumps(test_data).encode()).decode(),
                content_type="application/json"
            )
            
            print("✅ Test guided journal stored in hints bucket")
            
            # Try to retrieve it
            content = guided_journal_service.client.bucket.get(
                bucket_location={
                    "bucket": {
                        "name": "hints",
                        "application_name": guided_journal_service.application_name
                    }
                },
                key="guided_journal_test123"
            )
            
            retrieved = json.loads(base64.b64decode(content['content']).decode())
            print(f"✅ Retrieved test journal: {retrieved['topic']}")
            
            # Clean up
            guided_journal_service.client.bucket.delete(
                bucket_location={
                    "bucket": {
                        "name": "hints",
                        "application_name": guided_journal_service.application_name
                    }
                },
                key="guided_journal_test123"
            )
            print("✅ Test cleaned up")
            
        except Exception as e:
            print(f"❌ Hints bucket test error: {e}")
        
    else:
        print("❌ SmartBucket client not available")

except Exception as e:
    print(f"❌ Script error: {e}")
    import traceback
    traceback.print_exc()