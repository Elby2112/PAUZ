#!/usr/bin/env python3
"""
Script to fix Raindrop integration by using a simpler approach
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_simple_raindrop_usage():
    """Test a simpler approach to using Raindrop without pre-defined buckets"""
    print("🔧 Testing simplified Raindrop approach...")
    
    try:
        from raindrop import Raindrop
        api_key = os.getenv('AI_API_KEY')
        client = Raindrop(api_key=api_key)
        print("✅ Raindrop client initialized")
        
        # Try to use the organization level buckets
        organization_name = os.getenv('RAINDROP_ORG', 'tenapi')
        print(f"🏢 Using organization: {organization_name}")
        
        # Test if we can use a general bucket that might exist
        try:
            # Try to use 'default' bucket with the organization
            response = client.query.document_query(
                bucket_location={
                    "bucket": {
                        "name": "default",
                        "application_name": organization_name
                    }
                },
                input="Generate 3 journal prompts about mindfulness",
                object_id="test-prompt",
                request_id="test-123"
            )
            print("✅ Successfully used default bucket")
            answer = getattr(response, 'answer', str(response))
            print(f"📝 AI Response: {answer[:200]}...")
            return True
            
        except Exception as e:
            print(f"❌ Default bucket failed: {e}")
            
            # Try creating a document first in the default bucket
            try:
                print("📝 Creating test document in default bucket...")
                client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": "default",
                            "application_name": organization_name
                        }
                    },
                    key="test-prompt",
                    content="Generate 3 journal prompts about mindfulness",
                    content_type="text/plain"
                )
                print("✅ Document created, now querying...")
                
                response = client.query.document_query(
                    bucket_location={
                        "bucket": {
                            "name": "default",
                            "application_name": organization_name
                        }
                    },
                    input="Generate the prompts now",
                    object_id="test-prompt",
                    request_id="test-456"
                )
                
                answer = getattr(response, 'answer', str(response))
                print(f"✅ Success! AI Response: {answer[:200]}...")
                return True
                
            except Exception as e2:
                print(f"❌ Even creating document failed: {e2}")
                return False
    
    except Exception as e:
        print(f"❌ Raindrop client initialization failed: {e}")
        return False

def update_services_for_simple_approach():
    """Update the services to use the simplified approach"""
    print("\n🔄 Updating services for simplified approach...")
    
    # Update guided journal service
    guided_journal_file = "app/services/guided_journal_service.py"
    try:
        with open(guided_journal_file, 'r') as f:
            content = f.read()
        
        # Replace bucket names with 'default' for now
        updated_content = content.replace(
            '"journal-prompts"',
            '"default"'
        )
        
        with open(guided_journal_file, 'w') as f:
            f.write(updated_content)
        
        print("✅ Updated guided journal service")
    except Exception as e:
        print(f"❌ Failed to update guided journal service: {e}")
        return False
    
    # Update free journal service
    free_journal_file = "app/services/free_journal_service.py"
    try:
        with open(free_journal_file, 'r') as f:
            content = f.read()
        
        # Replace bucket names with 'default' for now
        updated_content = content.replace('"hints"', '"default"')
        updated_content = updated_content.replace('"journal-analysis"', '"default"')
        
        with open(free_journal_file, 'w') as f:
            f.write(updated_content)
        
        print("✅ Updated free journal service")
    except Exception as e:
        print(f"❌ Failed to update free journal service: {e}")
        return False
    
    return True

def main():
    print("🚀 Fixing Raindrop integration with simplified approach...")
    
    # Test the simple approach first
    if test_simple_raindrop_usage():
        print("✅ Simple approach works, updating services...")
        if update_services_for_simple_approach():
            print("✅ Services updated successfully")
            return True
        else:
            print("❌ Failed to update services")
            return False
    else:
        print("❌ Simple approach failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)