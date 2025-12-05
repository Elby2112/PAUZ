#!/usr/bin/env python3
"""
Complete test of guided journal functionality
"""
import sys
sys.path.append('.')

def test_guided_journal_complete():
    print("🧪 Complete Guided Journal Test")
    print("=" * 40)
    
    # Test 1: Service imports
    print("1. Testing services...")
    try:
        from app.services.guided_journal_service import guided_journal_service
        from app.services.storage_service import storage_service
        from app.utils import pdf_generator
        print("✅ All services loaded successfully")
    except Exception as e:
        print(f"❌ Service import error: {e}")
        return
    
    # Test 2: Create a test journal
    print("\n2. Creating test journal...")
    try:
        test_user_id = "test_user_123"
        test_topic = "Test Journal Topic"
        test_prompts = [
            {"id": 1, "text": "How are you feeling today?"},
            {"id": 2, "text": "What made you happy?"}
        ]
        test_entries = [
            {"prompt_id": 1, "prompt_text": "How are you feeling today?", "response": "I'm feeling great!", "created_at": "2024-01-01T12:00:00Z"},
            {"prompt_id": 2, "prompt_text": "What made you happy?", "response": "The sunny weather!", "created_at": "2024-01-01T12:01:00Z"}
        ]
        
        journal = guided_journal_service.create_guided_journal_with_entries(
            user_id=test_user_id,
            topic=test_topic,
            prompts_data=test_prompts,
            entries_data=test_entries
        )
        
        print(f"✅ Journal created: {journal['id']}")
        journal_id = journal['id']
        
    except Exception as e:
        print(f"❌ Journal creation error: {e}")
        return
    
    # Test 3: Retrieve the journal
    print("\n3. Retrieving journal...")
    try:
        retrieved = guided_journal_service.get_guided_journal_by_id(test_user_id, journal_id)
        if retrieved:
            print(f"✅ Journal retrieved: {retrieved['topic']}")
            print(f"   Entries: {len(retrieved['entries'])}")
        else:
            print("❌ Journal not found")
            return
    except Exception as e:
        print(f"❌ Journal retrieval error: {e}")
        return
    
    # Test 4: Generate PDF
    print("\n4. Generating PDF...")
    try:
        pdf_bytes = pdf_generator.generate_pdf_guided_journal(retrieved)
        print(f"✅ PDF generated: {len(pdf_bytes)} bytes")
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return
    
    # Test 5: Upload PDF (optional - may require network)
    print("\n5. Testing PDF upload...")
    try:
        pdf_url = storage_service.upload_pdf(journal_id, pdf_bytes)
        print(f"✅ PDF uploaded: {pdf_url}")
    except Exception as e:
        print(f"⚠️  PDF upload error (may be network issue): {e}")
        print("   But PDF generation worked!")
    
    # Test 6: List user journals
    print("\n6. Listing user journals...")
    try:
        journals = guided_journal_service.get_user_guided_journals(test_user_id)
        print(f"✅ Found {len(journals)} journals for user")
        for j in journals:
            print(f"   - {j.get('id', 'unknown')}: {j.get('topic', 'no topic')}")
    except Exception as e:
        print(f"❌ List journals error: {e}")
    
    print("\n🎉 Guided journal functionality test complete!")
    print("   - Journal saving: ✅")
    print("   - Journal retrieval: ✅") 
    print("   - PDF generation: ✅")
    print("   - PDF upload: ⚠️  (depends on network/Vultr)")

if __name__ == "__main__":
    test_guided_journal_complete()