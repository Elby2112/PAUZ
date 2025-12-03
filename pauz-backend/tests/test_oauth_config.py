#!/usr/bin/env python3
"""
Test script to verify Google OAuth configuration
"""
import os
import sys
sys.path.append('.')

from app.services.auth_service import get_google_auth_url

def test_oauth_config():
    print("🔍 Testing Google OAuth Configuration...")
    print("=" * 50)
    
    try:
        # Test 1: Check environment variables
        print("📋 Test 1: Environment Variables")
        redirect_uri = os.getenv("REDIRECT_URI")
        print(f"   REDIRECT_URI: {redirect_uri}")
        
        if not redirect_uri:
            print("   ❌ REDIRECT_URI not set")
            return False
            
        # Test 2: Check client secrets file
        print("\n📋 Test 2: Client Secrets File")
        client_secrets_file = "client_secret.json"
        if os.path.exists(client_secrets_file):
            print(f"   ✅ {client_secrets_file} exists")
        else:
            print(f"   ❌ {client_secrets_file} not found")
            return False
            
        # Test 3: Generate auth URL
        print("\n📋 Test 3: Generate Authorization URL")
        auth_url, state = get_google_auth_url()
        print(f"   ✅ Auth URL generated: {auth_url[:80]}...")
        print(f"   ✅ State generated: {state}")
        
        print("\n🎉 All tests passed! OAuth configuration is correct.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_oauth_config()
    sys.exit(0 if success else 1)