"""
Update FreeJournal Service to use SmartStorage
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def update_free_journal_service():
    """Update FreeJournal service to use SmartStorage for voice recordings"""
    
    print("🔄 Updating FreeJournal Service for SmartStorage")
    print("=" * 50)
    
    # Read the current free journal service
    with open('app/services/free_journal_service.py', 'r') as f:
        content = f.read()
    
    # Check if it already uses SmartStorage
    if 'smart_storage_service' in content:
        print("✅ FreeJournal service already uses SmartStorage")
        return True
    
    # Add SmartStorage import
    if 'from app.services.smart_storage_service import smart_storage_service' not in content:
        # Add import after the existing imports
        import_line = "from app.services.smart_storage_service import smart_storage_service"
        # Find the last import line and add after it
        lines = content.split('\n')
        
        # Find the line with "from app" imports
        last_app_import = -1
        for i, line in enumerate(lines):
            if line.startswith('from app.') and 'import' in line:
                last_app_import = i
        
        if last_app_import != -1:
            lines.insert(last_app_import + 1, import_line)
            content = '\n'.join(lines)
    
    # Update the transcribe_audio method to use SmartStorage
    old_voice_section = '''# Upload audio to SmartBucket - NO FALLBACKS
            audio_id = str(uuid.uuid4())
            print(f"📁 Uploading audio to SmartBucket with ID: {audio_id}")

            try:
                # Convert bytes to base64 for SmartBucket storage
                import base64
                audio_base64 = base64.b64encode(audio_file).decode('utf-8')
                
                # Store in SmartBucket using existing journal-prompts bucket
                self.client.bucket.put(
                    bucket_location={
                        "bucket": {
                            "name": "journal-prompts",
                            "application_name": self.application_name
                        }
                    },
                    key=f"voice_recording_{audio_id}",
                    content=audio_base64,
                    content_type="audio/wav"
                )
                print("✅ Audio uploaded to SmartBucket successfully")'''
    
    new_voice_section = '''# Upload audio to SmartStorage - ORGANIZED STORAGE
            audio_id = str(uuid.uuid4())
            print(f"📁 Uploading audio to SmartStorage with ID: {audio_id}")

            try:
                # Store in SmartStorage with organized structure
                voice_success = smart_storage_service.store_voice_recording(
                    user_id=user_id,
                    session_id=session_id,
                    audio_data=audio_file
                )
                
                if voice_success:
                    print("✅ Audio uploaded to SmartStorage successfully")
                else:
                    print("❌ SmartStorage upload failed")
                    raise ValueError("SmartStorage upload failed")'''
    
    if old_voice_section in content:
        content = content.replace(old_voice_section, new_voice_section)
        print("✅ Updated voice recording storage to use SmartStorage")
    else:
        print("⚠️ Could not find voice recording section to update")
    
    # Save the updated file
    with open('app/services/free_journal_service.py', 'w') as f:
        f.write(content)
    
    print("✅ FreeJournal service updated successfully!")
    return True

if __name__ == "__main__":
    update_free_journal_service()