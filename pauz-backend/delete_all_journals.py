"""
Script to delete all journals for testing purposes
This will reset all data to 0 for verification
"""
import os
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL
from app.services.guided_journal_service import guided_journal_service
from app.services.storage_service import storage_service

def delete_all_journals():
    """Delete all journals from both database and SmartBucket"""
    
    print("🗑️  DELETING ALL JOURNALS FOR TESTING")
    print("=" * 50)
    print("⚠️  This will reset ALL journal data to 0!")
    print()
    
    # Create database connection
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("📊 DELETING FROM DATABASE...")
        
        # Delete free journals
        result = session.execute(text("DELETE FROM freejournal"))
        free_count = result.rowcount
        print(f"   ✅ Deleted {free_count} free journals")
        
        # Delete guided journals
        result = session.execute(text("DELETE FROM guidedjournal"))
        guided_count = result.rowcount
        print(f"   ✅ Deleted {guided_count} guided journals")
        
        # Delete hints
        result = session.execute(text("DELETE FROM hint"))
        hints_count = result.rowcount
        print(f"   ✅ Deleted {hints_count} hints")
        
        # Delete guided journal entries
        result = session.execute(text("DELETE FROM guidedjournalentry"))
        entries_count = result.rowcount
        print(f"   ✅ Deleted {entries_count} guided journal entries")
        
        # Delete prompts
        result = session.execute(text("DELETE FROM prompt"))
        prompts_count = result.rowcount
        print(f"   ✅ Deleted {prompts_count} prompts")
        
        # Delete garden flowers
        result = session.execute(text("DELETE FROM garden"))
        garden_count = result.rowcount
        print(f"   ✅ Deleted {garden_count} garden flowers")
        
        session.commit()
        print()
        print("✅ Database cleanup completed!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        session.rollback()
        return False
    
    finally:
        session.close()
    
    print()
    print("☁️  DELETING FROM SMARTBUCKET...")
    
    try:
        # Delete from guided-journals bucket
        try:
            response = guided_journal_service.client.bucket.list(
                bucket_location={
                    "bucket": {
                        "name": "guided-journals",
                        "application_name": guided_journal_service.application_name
                    }
                }
            )
            
            deleted_count = 0
            for item in response.objects:
                if hasattr(item, 'key') and f"journal_" in item.key:
                    try:
                        guided_journal_service.client.bucket.delete(
                            bucket_location={
                                "bucket": {
                                    "name": "guided-journals",
                                    "application_name": guided_journal_service.application_name
                                }
                            },
                            key=item.key
                        )
                        deleted_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Could not delete {item.key}: {e}")
            
            print(f"   ✅ Deleted {deleted_count} items from guided-journals bucket")
            
        except Exception as e:
            print(f"   ⚠️  guided-journals bucket error: {e}")
        
        # Delete from hints bucket
        try:
            response = guided_journal_service.client.bucket.list(
                bucket_location={
                    "bucket": {
                        "name": "hints",
                        "application_name": guided_journal_service.application_name
                    }
                }
            )
            
            deleted_count = 0
            for item in response.objects:
                if hasattr(item, 'key') and ("guided_journal_" in item.key or "hint-" in item.key):
                    try:
                        guided_journal_service.client.bucket.delete(
                            bucket_location={
                                "bucket": {
                                    "name": "hints",
                                    "application_name": guided_journal_service.application_name
                                }
                            },
                            key=item.key
                        )
                        deleted_count += 1
                    except Exception as e:
                        print(f"   ⚠️  Could not delete {item.key}: {e}")
            
            print(f"   ✅ Deleted {deleted_count} items from hints bucket")
            
        except Exception as e:
            print(f"   ⚠️  hints bucket error: {e}")
        
        print()
        print("✅ SmartBucket cleanup completed!")
        
    except Exception as e:
        print(f"❌ SmartBucket error: {e}")
        return False
    
    print()
    print("🎯 FINAL VERIFICATION...")
    
    # Verify database is empty
    session = Session()
    try:
        free_count = session.execute(text("SELECT COUNT(*) FROM freejournal")).scalar()
        guided_count = session.execute(text("SELECT COUNT(*) FROM guidedjournal")).scalar()
        garden_count = session.execute(text("SELECT COUNT(*) FROM garden")).scalar()
        
        print(f"   📊 Free journals: {free_count}")
        print(f"   📊 Guided journals: {guided_count}")
        print(f"   📊 Garden flowers: {garden_count}")
        
        if free_count == 0 and guided_count == 0 and garden_count == 0:
            print()
            print("🎉 SUCCESS! All journal data has been deleted!")
            print("📈 All counts should now show 0 in the UI!")
            return True
        else:
            print()
            print("⚠️  Some data may remain, but most has been deleted.")
            return False
            
    finally:
        session.close()

if __name__ == "__main__":
    print("Starting journal deletion process...")
    success = delete_all_journals()
    
    if success:
        print()
        print("🚀 Ready for testing! The app should show 0 for all counts.")
    else:
        print()
        print("⚠️  Some errors occurred, but most data should be deleted.")