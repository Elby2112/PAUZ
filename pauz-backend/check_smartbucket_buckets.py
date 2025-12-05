#!/usr/bin/env python3
"""
Check what SmartBucket buckets exist and create if needed
"""
import sys
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv()

try:
    from app.services.guided_journal_service import guided_journal_service
    
    print("🔍 Checking SmartBucket Buckets")
    print("=" * 40)
    
    if guided_journal_service.client:
        print("✅ SmartBucket client available")
        
        # Try to list buckets from main application
        try:
            print("\n📋 Checking existing buckets...")
            
            # Check if we can access hints bucket (this should work)
            try:
                hints_response = guided_journal_service.client.bucket.list(
                    bucket_location={
                        "bucket": {
                            "name": "hints",
                            "application_name": guided_journal_service.application_name
                        }
                    }
                )
                print(f"✅ Hints bucket accessible: {len(hints_response)} items")
            except Exception as e:
                print(f"⚠️  Hints bucket error: {e}")
            
            # Check if we can access audio bucket
            try:
                audio_response = guided_journal_service.client.bucket.list(
                    bucket_location={
                        "bucket": {
                            "name": "audio-files",
                            "application_name": guided_journal_service.application_name
                        }
                    }
                )
                print(f"✅ Audio bucket accessible: {len(audio_response)} items")
            except Exception as e:
                print(f"⚠️  Audio bucket error: {e}")
            
            # Try to create guided-journals bucket
            print("\n🔧 Attempting to create guided-journals bucket...")
            
            # First, try to put an item in the bucket (this creates it if it doesn't exist)
            test_data = {
                "id": "test-journal", 
                "type": "test",
                "created_at": "2024-01-01T12:00:00Z",
                "user_id": "test-user"
            }
            
            import base64
            import json
            
            guided_journal_service.client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": "guided-journals",
                        "application_name": guided_journal_service.application_name
                    }
                },
                key="test-init",
                content=base64.b64encode(json.dumps(test_data).encode()).decode(),
                content_type="application/json"
            )
            
            print("✅ Test item added to guided-journals bucket")
            
            # Now try to list the bucket
            try:
                response = guided_journal_service.client.bucket.list(
                    bucket_location={
                        "bucket": {
                            "name": "guided-journals",
                            "application_name": guided_journal_service.application_name
                        }
                    }
                )
                print(f"✅ Guided-journals bucket created and accessible: {len(response)} items")
                
                # Clean up test item
                guided_journal_service.client.bucket.delete(
                    bucket_location={
                        "bucket": {
                            "name": "guided-journals",
                            "application_name": guided_journal_service.application_name
                        }
                    },
                    key="test-init"
                )
                print("✅ Test item cleaned up")
                
            except Exception as e:
                print(f"❌ Could not list bucket after creation: {e}")
                
        except Exception as e:
            print(f"❌ Bucket setup error: {e}")
    else:
        print("❌ SmartBucket client not available")
        
    print("\n🎯 Bucket Setup Complete!")
    print("   Try saving a guided journal now.")

except Exception as e:
    print(f"❌ Script error: {e}")
    import traceback
    traceback.print_exc()