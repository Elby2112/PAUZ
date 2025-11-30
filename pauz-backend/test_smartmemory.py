#!/usr/bin/env python3
"""
Test SmartMemory functionality without app registration
"""
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def main():
    print("🧪 Testing SmartMemory functionality...")
    
    try:
        from raindrop import Raindrop
        client = Raindrop(api_key=os.getenv('AI_API_KEY'))
        print("✅ Raindrop client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Raindrop client: {e}")
        return False
    
    # Try using SmartMemory with organization level
    organization_name = os.getenv('RAINDROP_ORG', 'Loubna-HackathonApp')
    
    try:
        print("🧠 Testing SmartMemory...")
        
        # Try to put semantic memory
        client.put_semantic_memory(
            smart_memory_location={
                "smart_memory": {
                    "name": "test-memory",
                    "application_name": organization_name  # Try using org as app
                }
            },
            content="This is a test memory for PAUZ journaling app",
            session_id="test-session",
            key="test-key"
        )
        print("✅ SmartMemory creation successful")
        
        # Test query
        response = client.query.semantic_memory.search(
            needle="journal prompts",
            smart_memory_location={
                "smart_memory": {
                    "name": "test-memory",
                    "application_name": organization_name
                }
            }
        )
        print(f"✅ Semantic memory search successful: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ SmartMemory test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)