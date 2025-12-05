#!/usr/bin/env python3
"""
Test guided journal saving and PDF export functionality
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_guided_journal_save_and_export():
    """Test the complete flow: save -> export"""
    print("🧪 Testing Guided Journal Save & Export")
    print("=" * 50)
    
    # You'll need to provide a valid token for these tests
    # For now, we'll test the endpoints exist and respond correctly
    
    print("1. Testing endpoints exist (without auth):")
    
    # Test save endpoint
    try:
        response = requests.post(f"{API_BASE}/guided_journal/", 
                               json={
                                   "topic": "Test Journal",
                                   "prompts": [{"id": 1, "text": "How are you?"}],
                                   "entries": [{"prompt_id": 1, "response": "Good!"}]
                               })
        if response.status_code == 401:
            print("✅ POST /guided_journal/ - Requires auth (401)")
        elif response.status_code == 422:
            print("✅ POST /guided_journal/ - Validates input (422)")
        else:
            print(f"⚠️  POST /guided_journal/ - Unexpected: {response.status_code}")
    except Exception as e:
        print(f"❌ POST /guided_journal/ - Error: {e}")
    
    # Test prompts endpoint
    try:
        response = requests.post(f"{API_BASE}/guided_journal/prompts",
                               json={"topic": "Test Topic"})
        if response.status_code == 401:
            print("✅ POST /guided_journal/prompts - Requires auth (401)")
        elif response.status_code == 200:
            print("✅ POST /guided_journal/prompts - Works without auth")
        else:
            print(f"⚠️  POST /guided_journal/prompts - Unexpected: {response.status_code}")
    except Exception as e:
        print(f"❌ POST /guided_journal/prompts - Error: {e}")
    
    # Test export endpoint format
    try:
        response = requests.post(f"{API_BASE}/guided_journal/test-id/export")
        if response.status_code == 401:
            print("✅ POST /guided_journal/{id}/export - Requires auth (401)")
        elif response.status_code == 404:
            print("✅ POST /guided_journal/{id}/export - Returns 404 for invalid ID")
        else:
            print(f"⚠️  POST /guided_journal/{id}/export - Unexpected: {response.status_code}")
    except Exception as e:
        print(f"❌ POST /guided_journal/{id}/export - Error: {e}")
    
    print("\n2. Testing backend services:")
    
    # Test guided journal service directly
    try:
        import sys
        sys.path.append('.')
        from app.services.guided_journal_service import guided_journal_service
        print("✅ GuidedJournalService loads successfully")
        
        # Test prompt generation
        prompts = guided_journal_service.generate_prompts("test topic")
        print(f"✅ Generated {len(prompts)} prompts")
        
    except Exception as e:
        print(f"❌ GuidedJournalService error: {e}")
    
    # Test storage service
    try:
        from app.services.storage_service import storage_service
        print("✅ StorageService loads successfully")
        
    except Exception as e:
        print(f"❌ StorageService error: {e}")
    
    # Test PDF generator
    try:
        from app.utils import pdf_generator
        print("✅ PDFGenerator loads successfully")
        
    except Exception as e:
        print(f"❌ PDFGenerator error: {e}")
    
    print("\n3. Analyzing potential issues:")
    
    print("🔍 Checking common guided journal issues:")
    
    # Check if mcp_storage is available
    try:
        from mcp_storage.mcp import put_object, get_object
        print("✅ mcp_storage is available")
    except ImportError:
        print("❌ mcp_storage NOT available - this will break journal saving!")
    
    # Check if reportlab is available
    try:
        from reportlab.platypus import SimpleDocTemplate
        print("✅ reportlab is available for PDF generation")
    except ImportError:
        print("❌ reportlab NOT available - this will break PDF export!")
    
    # Check if vultr credentials are set
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    vultr_keys = ["VULTR_ACCESS_KEY", "VULTR_SECRET_KEY", "VULTR_REGION", "VULTR_BUCKET_NAME"]
    vultr_configured = all(os.getenv(key) for key in vultr_keys)
    
    if vultr_configured:
        print("✅ Vultr S3 credentials are configured")
    else:
        missing = [key for key in vultr_keys if not os.getenv(key)]
        print(f"❌ Missing Vultr credentials: {missing}")
        print("   PDF upload to S3 will fail!")

if __name__ == "__main__":
    test_guided_journal_save_and_export()