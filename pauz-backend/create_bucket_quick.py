#!/usr/bin/env python3
"""
Quick test to create voice recordings bucket
"""

import os
import base64
from dotenv import load_dotenv

load_dotenv()

def create_bucket():
    try:
        from raindrop import Raindrop
        
        api_key = os.getenv('AI_API_KEY')
        app_name = os.getenv('APPLICATION_NAME')
        
        client = Raindrop(api_key=api_key)
        
        # Try to create the bucket by putting a test object
        test_data = base64.b64encode(b"bucket init").decode('utf-8')
        
        response = client.bucket.put(
            bucket_location={
                "bucket": {
                    "name": "voice-recordings",
                    "application_name": app_name
                }
            },
            key="init-test",
            content=test_data,
            content_type="text/plain"
        )
        
        print("✅ Bucket created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    create_bucket()