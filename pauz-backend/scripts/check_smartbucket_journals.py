#!/usr/bin/env python3
"""
Test the updated stats endpoint to see if it counts guided journals from SmartBucket
"""
import os
import sys
sys.path.append('.')

from app.services.storage_service import storage_service
from app.database import get_session
from app.models import User
from sqlmodel import select

def check_smartbucket_journals():
    """Check what guided journals are in SmartBucket"""
    print("🔍 Checking SmartBucket guided journals...")
    print("=" * 50)
    
    try:
        db = next(get_session())
        try:
            # Get all users
            users = db.exec(select(User)).all()
            print(f"📊 Found {len(users)} users")
            
            for user in users:
                print(f"\n👤 User: {user.email} (ID: {user.id})")
                
                # Check SmartBucket for this user
                try:
                    guided_journals = storage_service.get_user_guided_journals(user.id)
                    print(f"   📝 Guided journals in SmartBucket: {len(guided_journals)}")
                    
                    if guided_journals:
                        print("   📋 Journal details:")
                        for gj in guided_journals:
                            print(f"      - ID: {gj.get('id', 'unknown')}")
                            print(f"        Topic: {gj.get('topic', 'no topic')}")
                            print(f"        Created: {gj.get('created_at', 'unknown')}")
                            print(f"        Prompts: {len(gj.get('prompts', []))}")
                            print(f"        Entries: {len(gj.get('entries', []))}")
                            print()
                except Exception as e:
                    print(f"   ❌ Error accessing SmartBucket: {e}")
                    
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_smartbucket_journals()