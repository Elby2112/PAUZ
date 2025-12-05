#!/usr/bin/env python3
"""
Check the correct structure of BucketListResponse
"""
import sys
sys.path.append('.')
from dotenv import load_dotenv
load_dotenv()

try:
    from app.services.guided_journal_service import guided_journal_service
    
    print("🔍 Checking BucketListResponse Structure")
    print("=" * 45)
    
    if guided_journal_service.client:
        # Test hints bucket response structure
        print("📋 Testing hints bucket response structure...")
        try:
            response = guided_journal_service.client.bucket.list(
                bucket_location={
                    "bucket": {
                        "name": "hints",
                        "application_name": guided_journal_service.application_name
                    }
                }
            )
            
            print(f"✅ Response type: {type(response)}")
            print(f"✅ Response attributes: {dir(response)}")
            
            # Check for the correct attribute
            if hasattr(response, 'bucket_list'):
                print(f"✅ bucket_list: {len(response.bucket_list)} items")
            elif hasattr(response, 'items'):
                print(f"✅ items: {len(response.items)} items")
            elif hasattr(response, 'objects'):
                print(f"✅ objects: {len(response.objects)} items")
            else:
                print("❌ No list-like attribute found")
                # Try to iterate directly
                try:
                    items = list(response)
                    print(f"✅ Direct iteration: {len(items)} items")
                    print(f"   Sample item: {items[0] if items else 'No items'}")
                except Exception as iter_error:
                    print(f"❌ Cannot iterate: {iter_error}")
            
            # Check the actual content structure
            print(f"📄 Response content: {str(response)[:200]}...")
            
        except Exception as e:
            print(f"❌ Error checking response: {e}")
            import traceback
            traceback.print_exc()
            
    else:
        print("❌ SmartBucket client not available")
        
except Exception as e:
    print(f"❌ Script error: {e}")
    import traceback
    traceback.print_exc()