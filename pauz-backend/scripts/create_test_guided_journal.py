#!/usr/bin/env python3
"""
Create a test guided journal to verify the stats endpoint works
"""
import os
import sys
sys.path.append('.')

from app.database import get_session
from app.models import User, GuidedJournal, Prompt, GuidedJournalEntry
from sqlmodel import select
from uuid import uuid4
from datetime import datetime

def create_test_guided_journal():
    """Create a test guided journal entry"""
    print("🔍 Creating test guided journal...")
    print("=" * 50)
    
    try:
        db = next(get_session())
        try:
            # Get first user
            user = db.exec(select(User)).first()
            if not user:
                print("❌ No users found")
                return
                
            print(f"👤 Creating guided journal for: {user.email}")
            
            # Create guided journal
            guided_journal = GuidedJournal(
                id=str(uuid4()),
                user_id=user.id,
                topic="Test Topic - Gratitude and Growth"
            )
            db.add(guided_journal)
            db.commit()
            db.refresh(guided_journal)
            
            print(f"✅ Created guided journal: {guided_journal.id}")
            
            # Create some test prompts
            prompts_data = [
                "What are you grateful for today?",
                "Describe something you learned recently.",
                "What made you smile this week?"
            ]
            
            for i, prompt_text in enumerate(prompts_data):
                prompt = Prompt(
                    text=prompt_text,
                    guided_journal_id=guided_journal.id
                )
                db.add(prompt)
                
                # Create corresponding entry
                entry = GuidedJournalEntry(
                    id=str(uuid4()),
                    guided_journal_id=guided_journal.id,
                    prompt_id=prompt.id,  # Will be set after commit
                    response=f"This is my response to prompt {i+1}."
                )
                db.add(entry)
            
            db.commit()
            print("✅ Created 3 prompts and 3 entries")
            
            # Verify the count
            guided_journals = db.exec(
                select(GuidedJournal).where(GuidedJournal.user_id == user.id)
            ).all()
            total_guided = len(guided_journals)
            print(f"📊 Total guided journals for user: {total_guided}")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_test_guided_journal()