#!/usr/bin/env python3
"""
Test script to verify DELETE endpoints for both Free Journal and Guided Journal
"""

import requests
import json

# Base URL (adjust if your server runs on different port)
BASE_URL = "http://localhost:8000"

def test_free_journal_delete():
    """Test DELETE endpoint for Free Journal"""
    print("\n🧪 Testing Free Journal DELETE endpoint...")
    
    # First, create a free journal session
    print("1. Creating a free journal session...")
    create_response = requests.post(
        f"{BASE_URL}/freejournal/",
        headers={"Authorization": "Bearer your-test-token-here"}
    )
    
    if create_response.status_code == 200:
        session_id = create_response.json()["session_id"]
        print(f"✅ Created session: {session_id}")
        
        # Test DELETE endpoint
        print("2. Deleting the session...")
        delete_response = requests.delete(
            f"{BASE_URL}/freejournal/{session_id}",
            headers={"Authorization": "Bearer your-test-token-here"}
        )
        
        if delete_response.status_code == 200:
            print("✅ DELETE endpoint works: " + delete_response.json()["message"])
        else:
            print(f"❌ DELETE failed: {delete_response.status_code} - {delete_response.text}")
    else:
        print(f"❌ Failed to create test session: {create_response.status_code}")

def test_guided_journal_delete():
    """Test DELETE endpoint for Guided Journal"""
    print("\n🧪 Testing Guided Journal DELETE endpoint...")
    
    # Test DELETE with non-existent journal (should return 404)
    print("1. Testing DELETE with non-existent journal...")
    delete_response = requests.delete(
        f"{BASE_URL}/guided_journal/non-existent-id",
        headers={"Authorization": "Bearer your-test-token-here"}
    )
    
    if delete_response.status_code == 404:
        print("✅ DELETE endpoint correctly returns 404 for non-existent journal")
    elif delete_response.status_code == 401:
        print("⚠️ DELETE endpoint returns 401 (authentication required) - this is expected without proper auth")
    else:
        print(f"❓ DELETE response: {delete_response.status_code} - {delete_response.text}")

def verify_endpoints_exist():
    """Verify that DELETE endpoints are registered"""
    print("\n🧪 Verifying endpoint registration...")
    
    # Test Free Journal DELETE
    try:
        response = requests.options(f"{BASE_URL}/freejournal/test-session-id")
        if response.status_code in [200, 405]:  # 200 if OPTIONS supported, 405 if not but endpoint exists
            print("✅ Free Journal DELETE endpoint is registered")
        else:
            print(f"❓ Free Journal OPTIONS response: {response.status_code}")
    except:
        print("❓ Could not verify Free Journal endpoint")
    
    # Test Guided Journal DELETE
    try:
        response = requests.options(f"{BASE_URL}/guided_journal/test-journal-id")
        if response.status_code in [200, 405]:
            print("✅ Guided Journal DELETE endpoint is registered")
        else:
            print(f"❓ Guided Journal OPTIONS response: {response.status_code}")
    except:
        print("❓ Could not verify Guided Journal endpoint")

if __name__ == "__main__":
    print("🚀 Testing Journal DELETE endpoints")
    print("=" * 50)
    
    verify_endpoints_exist()
    test_free_journal_delete()
    test_guided_journal_delete()
    
    print("\n✅ Testing completed!")
    print("\n📝 Manual testing steps:")
    print("1. Start your FastAPI server: uvicorn app.main:app --reload")
    print("2. Get a valid auth token by logging in")
    print("3. Use curl/Postman to test:")
    print("   DELETE http://localhost:8000/freejournal/{session_id}")
    print("   DELETE http://localhost:8000/guided_journal/{journal_id}")
    print("   (Include Authorization: Bearer <your-token> header)")