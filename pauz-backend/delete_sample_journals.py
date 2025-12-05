#!/usr/bin/env python3
"""
Delete sample guided journals created for frontend debugging
"""
import sys
sys.path.append('.')
from app.services.guided_journal_service import guided_journal_service

def delete_sample_journals():
    print("🗑️ Deleting Sample Guided Journals")
    print("=" * 60)

    demo_users = ["demo_user_1", "demo_user_2", "debug_user_list"]

    for user_id in demo_users:
        print(f"\n🔥 Deleting journals for user: {user_id}")
        try:
            user_journals = guided_journal_service.get_user_guided_journals(user_id)
            if not user_journals:
                print(f"   ✅ No journals found for {user_id}")
                continue

            print(f"   found {len(user_journals)} journals to delete.")
            for journal in user_journals:
                journal_id = journal.get('id')
                if journal_id:
                    try:
                        success = guided_journal_service.delete_guided_journal(user_id, journal_id)
                        if success:
                            print(f"   ✅ Deleted journal: {journal_id}")
                        else:
                            print(f"   ❌ Failed to delete journal: {journal_id}")
                    except Exception as e:
                        print(f"   ❌ Error deleting journal {journal_id}: {e}")
        except Exception as e:
            print(f"   ❌ Error retrieving journals for {user_id}: {e}")

if __name__ == "__main__":
    delete_sample_journals()