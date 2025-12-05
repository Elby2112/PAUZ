#!/usr/bin/env python3
"""
Create the voice-recordings bucket for SmartBucket
"""

import os
from dotenv import load_dotenv

load_dotenv()

def create_voice_recordings_bucket():
    """Create the voice-recordings bucket in SmartBucket"""
    
    print("🎤 Creating Voice Recordings Bucket")
    print("=" * 40)
    
    try:
        from raindrop import Raindrop
        
        # Initialize client
        api_key = os.getenv('AI_API_KEY')
        org_name = os.getenv('RAINDROP_ORG')
        app_name = os.getenv('APPLICATION_NAME')
        
        if not all([api_key, org_name, app_name]):
            print("❌ Missing required environment variables")
            return False
        
        print(f"🔑 Using API key: {api_key[:20]}...")
        print(f"🏢 Organization: {org_name}")
        print(f"📱 Application: {app_name}")
        
        client = Raindrop(api_key=api_key)
        
        # Create the voice-recordings bucket
        print("🪣 Creating voice-recordings bucket...")
        
        try:
            response = client.bucket.put(
                bucket_location={
                    "bucket": {
                        "name": "voice-recordings",
                        "application_name": app_name
                    }
                },
                key="bucket-init",
                content="bucket initialization",
                content_type="text/plain"
            )
            
            print("✅ Voice-recordings bucket created successfully!")
            print(f"   Response: {response}")
            return True
            
        except Exception as create_error:
            print(f"⚠️ Bucket creation attempt: {create_error}")
            
            # Try to put a test object to see if bucket exists
            try:
                test_response = client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": "voice-recordings", 
                            "application_name": app_name
                        }
                    },
                    key="test-voice-file",
                    content="test audio data",
                    content_type="audio/wav"
                )
                
                print("✅ Voice-recordings bucket is accessible!")
                return True
                
            except Exception as test_error:
                print(f"❌ Bucket test failed: {test_error}")
                
                # Try alternative bucket names
                alternatives = ["voice-recordings", "audio", "voice-files", "journal-audio"]
                
                for alt_name in alternatives:
                    try:
                        print(f"🔄 Trying alternative bucket: {alt_name}")
                        alt_response = client.bucket.put(
                            bucket_location={
                                "bucket": {
                                    "name": alt_name,
                                    "application_name": app_name
                                }
                            },
                            key="test",
                            content=b"test",
                            content_type="text/plain"
                        )
                        print(f"✅ Alternative bucket '{alt_name}' works!")
                        print(f"🔧 Update your code to use: {alt_name}")
                        return True
                        
                    except Exception as alt_error:
                        print(f"   ❌ {alt_name} failed: {alt_error}")
                        continue
                
                return False
        
    except ImportError:
        print("❌ Raindrop library not installed")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_existing_buckets():
    """Test what buckets already exist"""
    
    print("\n🔍 Testing Existing Buckets")
    print("=" * 35)
    
    try:
        from raindrop import Raindrop
        
        api_key = os.getenv('AI_API_KEY')
        app_name = os.getenv('APPLICATION_NAME')
        
        client = Raindrop(api_key=api_key)
        
        # Test common bucket names
        test_buckets = [
            "guided-journals",
            "journal-prompts", 
            "voice-recordings",
            "audio",
            "voice-files"
        ]
        
        for bucket_name in test_buckets:
            try:
                response = client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": bucket_name,
                            "application_name": app_name
                        }
                    },
                    key="test-key",
                    content="test content",
                    content_type="text/plain"
                )
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
                        key="test-key"
                    )
                except:
                    pass  # Ignore cleanup errors
                    
            except Exception as e:
                if "not_found" in str(e):
                    print(f"❌ {bucket_name} - Not found")
                else:
                    print(f"⚠️ {bucket_name} - Error: {e}")
        
    except Exception as e:
        print(f"❌ Bucket test failed: {e}")

if __name__ == "__main__":
    print("🎤 SmartBucket Voice Setup Tool")
    print("=" * 50)
    
    test_existing_buckets()
    success = create_voice_recordings_bucket()
    
    if success:
        print("\n🎉 Voice bucket setup complete!")
        print("📱 Try recording audio in your app now!")
    else:
        print("\n⚠️ Bucket setup failed")
        print("🔧 You may need to create the bucket manually in the Raindrop console")