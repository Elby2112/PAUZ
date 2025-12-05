#!/usr/bin/env python3
"""
Check all SmartBuckets in your account
"""

import os
import base64
from dotenv import load_dotenv

load_dotenv()

def check_smartbuckets():
    """Check all available SmartBuckets and their contents"""
    
    print("🪣 SmartBucket Analysis")
    print("=" * 35)
    
    try:
        from raindrop import Raindrop
        
        api_key = os.getenv('AI_API_KEY')
        app_name = os.getenv('APPLICATION_NAME')
        
        if not api_key or not app_name:
            print("❌ Missing AI_API_KEY or APPLICATION_NAME")
            return
        
        print(f"🔑 API Key: {api_key[:20]}...")
        print(f"📱 Application: {app_name}")
        print()
        
        client = Raindrop(api_key=api_key)
        
        # Common bucket names used in your app
        bucket_candidates = [
            "journal-prompts",
            "guided-journals", 
            "pauz-guided-journals",
            "pauz-audio-files",
            "voice-recordings",
            "audio-files",
            "hints",
            "reflections",
            "garden-data",
            "user-uploads"
        ]
        
        print("🔍 Testing Bucket Access:")
        print("-" * 40)
        
        accessible_buckets = []
        test_data = base64.b64encode(b"bucket test").decode('utf-8')
        
        for bucket_name in bucket_candidates:
            try:
                # Try to put a test object
                response = client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": bucket_name,
                            "application_name": app_name
                        }
                    },
                    key="access-test",
                    content=test_data,
                    content_type="text/plain"
                )
                
                accessible_buckets.append(bucket_name)
                print(f"✅ {bucket_name} - Accessible")
                
                # Clean up test
                try:
                    client.bucket.delete(
                        bucket_location={
                            "bucket": {
                                "name": bucket_name,
                                "application_name": app_name
                            }
                        },
                        key="access-test"
                    )
                except:
                    pass  # Ignore cleanup errors
                    
            except Exception as e:
                if "not_found" in str(e):
                    print(f"❌ {bucket_name} - Not found")
                else:
                    print(f"⚠️ {bucket_name} - Error: {e}")
        
        print(f"\n📊 Summary: {len(accessible_buckets)} accessible buckets")
        
        if accessible_buckets:
            print(f"\n✅ Working Buckets: {', '.join(accessible_buckets)}")
            
            # Try to list contents of accessible buckets
            print(f"\n📋 Checking Bucket Contents:")
            print("-" * 40)
            
            for bucket_name in accessible_buckets:
                try:
                    # Try to list objects (this might not work depending on API)
                    print(f"📁 {bucket_name}:")
                    
                    # We'll try to get some info by attempting different keys
                    test_keys = [
                        "init",
                        "bucket-init", 
                        "test",
                        "hint-",
                        "prompt-",
                        "voice_recording_"
                    ]
                    
                    found_content = False
                    for key_prefix in test_keys:
                        try:
                            # This is a guess - the actual list method might be different
                            response = client.bucket.get(
                                bucket_location={
                                    "bucket": {
                                        "name": bucket_name,
                                        "application_name": app_name
                                    }
                                },
                                key=key_prefix + "test"
                            )
                            print(f"  📄 Found content with prefix: {key_prefix}")
                            found_content = True
                        except:
                            continue
                    
                    if not found_content:
                        print(f"  📭 Empty or no testable content found")
                        
                except Exception as e:
                    print(f"  ❌ Could not list contents: {e}")
        else:
            print("\n⚠️ No accessible buckets found")
            print("💡 You may need to create buckets in the Raindrop console")
        
        return accessible_buckets
        
    except Exception as e:
        print(f"❌ Error checking SmartBuckets: {e}")
        return []

def check_bucket_usage_in_code():
    """Check what buckets are referenced in your code"""
    
    print(f"\n🔍 Bucket Usage in Your Code:")
    print("-" * 40)
    
    import os
    import re
    
    # Search for bucket references in service files
    service_files = [
        'app/services/storage_service.py',
        'app/services/free_journal_service.py', 
        'app/services/guided_journal_service.py',
        'app/services/raindrop_service.py'
    ]
    
    bucket_references = {}
    
    for file_path in service_files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                # Find bucket name patterns
                bucket_matches = re.findall(r'"name":\s*"([^"]+)"', content)
                bucket_variable_matches = re.findall(r'bucket\s*=\s*"([^"]+)"', content)
                
                all_buckets = bucket_matches + bucket_variable_matches
                
                if all_buckets:
                    bucket_references[file_path] = all_buckets
                    print(f"📄 {file_path}:")
                    for bucket in all_buckets:
                        print(f"  🪣 {bucket}")
                        
            except Exception as e:
                print(f"❌ Could not read {file_path}: {e}")
    
    return bucket_references

def show_bucket_recommendations():
    """Show recommendations for bucket organization"""
    
    print(f"\n💡 SmartBucket Organization Recommendations:")
    print("-" * 50)
    
    print("🎯 Your Current Usage:")
    print("  📝 journal-prompts - For AI writing hints and prompts")
    print("  🎤 voice recordings - Currently using journal-prompts")
    print()
    
    print("🔧 Suggested Bucket Structure:")
    print("  📝 journal-prompts - AI writing hints and prompts")
    print("  🎤 voice-recordings - Audio files for transcription")
    print("  📖 guided-journals - Complete guided journal sessions")
    print("  💭 reflections - AI mood analysis and insights")
    print("  🌱 garden-data - Garden entries and flower data")
    print("  👤 user-uploads - User profile pictures and uploads")
    print()
    
    print("🎯 Benefits of Proper Organization:")
    print("  🧹 Easier cleanup and maintenance")
    print("  📊 Better analytics and monitoring")
    print("  🔒 Improved security (different access patterns)")
    print("  💾 Cost optimization (different storage tiers)")
    print("  🚀 Better performance (targeted queries)")

if __name__ == "__main__":
    print("🪣 Complete SmartBucket Analysis")
    print("=" * 50)
    
    accessible_buckets = check_smartbuckets()
    bucket_references = check_bucket_usage_in_code()
    show_bucket_recommendations()
    
    print(f"\n🎉 Analysis Complete!")
    print(f"📊 Found {len(accessible_buckets)} accessible buckets")
    print(f"📄 Found {len(bucket_references)} files using buckets")