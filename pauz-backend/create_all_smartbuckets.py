#!/usr/bin/env python3
"""
Create all 6 SmartBuckets for PAUZ Hackathon
"""

import os
import base64
from dotenv import load_dotenv

load_dotenv()

def create_all_buckets():
    """Create all required SmartBuckets"""
    
    print("🪣 Creating PAUZ SmartBuckets")
    print("=" * 35)
    
    try:
        from raindrop import Raindrop
        
        api_key = os.getenv('AI_API_KEY')
        app_name = os.getenv('APPLICATION_NAME')
        
        if not api_key or not app_name:
            print("❌ Missing required environment variables")
            return False
        
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"📱 Application: {app_name}")
        
        client = Raindrop(api_key=api_key)
        
        # Define all 6 buckets we need
        buckets_to_create = [
            {
                "name": "user-profiles",
                "description": "User profile pictures and preferences",
                "test_key": "profile_test",
                "test_content": "profile test data"
            },
            {
                "name": "free-journals", 
                "description": "Free journal text entries and voice recordings",
                "test_key": "free_journal_test",
                "test_content": "free journal test"
            },
            {
                "name": "guided-journals",
                "description": "Structured guided journaling sessions", 
                "test_key": "guided_journal_test",
                "test_content": "guided journal test"
            },
            {
                "name": "ai-prompts",
                "description": "AI writing hints and mood analysis",
                "test_key": "ai_prompts_test", 
                "test_content": "AI prompts test"
            },
            {
                "name": "garden-system",
                "description": "Garden flowers and mood visualization",
                "test_key": "garden_test",
                "test_content": "garden test data"
            },
            {
                "name": "user-analytics",
                "description": "User statistics and progress tracking",
                "test_key": "analytics_test",
                "test_content": "analytics test data"
            }
        ]
        
        successful_buckets = []
        failed_buckets = []
        
        test_data = base64.b64encode("bucket initialization test".encode()).decode('utf-8')
        
        for bucket in buckets_to_create:
            bucket_name = bucket["name"]
            description = bucket["description"]
            
            print(f"\n🪣 Creating '{bucket_name}'...")
            print(f"   📝 Purpose: {description}")
            
            try:
                # Try to create/initialize the bucket
                response = client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": bucket_name,
                            "application_name": app_name
                        }
                    },
                    key=bucket["test_key"],
                    content=test_data,
                    content_type="text/plain"
                )
                
                successful_buckets.append(bucket_name)
                print(f"   ✅ {bucket_name} - Successfully created!")
                
                # Test reading back to confirm it works
                try:
                    test_response = client.bucket.get(
                        bucket_location={
                            "bucket": {
                                "name": bucket_name,
                                "application_name": app_name
                            }
                        },
                        key=bucket["test_key"]
                    )
                    print(f"   ✅ {bucket_name} - Read test passed!")
                    
                    # Clean up test data
                    try:
                        client.bucket.delete(
                            bucket_location={
                                "bucket": {
                                    "name": bucket_name,
                                    "application_name": app_name
                                }
                            },
                            key=bucket["test_key"]
                        )
                        print(f"   🧹 {bucket_name} - Test data cleaned up")
                    except:
                        print(f"   ⚠️ {bucket_name} - Could not clean up test data (OK)")
                        
                except Exception as test_error:
                    print(f"   ⚠️ {bucket_name} - Read test failed: {test_error}")
                    
            except Exception as e:
                if "not_found" in str(e):
                    print(f"   ❌ {bucket_name} - Bucket not accessible")
                else:
                    print(f"   ❌ {bucket_name} - Error: {e}")
                failed_buckets.append(bucket_name)
        
        print(f"\n📊 Results Summary:")
        print(f"   ✅ Successful: {len(successful_buckets)}/{len(buckets_to_create)}")
        print(f"   ❌ Failed: {len(failed_buckets)}/{len(buckets_to_create)}")
        
        if successful_buckets:
            print(f"\n✅ Working Buckets:")
            for bucket in successful_buckets:
                print(f"   🪣 {bucket}")
        
        if failed_buckets:
            print(f"\n❌ Failed Buckets:")
            for bucket in failed_buckets:
                print(f"   🪣 {bucket}")
        
        return len(successful_buckets) == len(buckets_to_create)
        
    except ImportError:
        print("❌ Raindrop library not installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 PAUZ SmartBuckets Creation")
    print("=" * 40)
    
    success = create_all_buckets()
    
    if success:
        print(f"\n🎉 All SmartBuckets created successfully!")
        print(f"🚀 Ready for Phase 2: Update StorageService")
    else:
        print(f"\n⚠️ Some buckets failed - check the errors above")
        print(f"💡 You can still proceed with working buckets")