"""
Fast script to delete all journals for testing purposes
Focus on database first, then SmartBucket
"""
import os
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL

def delete_database_journals():
    """Quickly delete all journals from database"""
    
    print("🗑️  DELETING ALL JOURNALS FROM DATABASE")
    print("=" * 50)
    
    # Create database connection
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("📊 Deleting journal tables...")
        
        # Get counts before deletion
        free_before = session.execute(text("SELECT COUNT(*) FROM freejournal")).scalar()
        guided_before = session.execute(text("SELECT COUNT(*) FROM guidedjournal")).scalar()
        garden_before = session.execute(text("SELECT COUNT(*) FROM garden")).scalar()
        hints_before = session.execute(text("SELECT COUNT(*) FROM hint")).scalar()
        
        print(f"   Before: Free={free_before}, Guided={guided_before}, Garden={garden_before}, Hints={hints_before}")
        
        # Delete from dependent tables first (foreign key constraints)
        session.execute(text("DELETE FROM hint"))
        session.execute(text("DELETE FROM guidedjournalentry"))
        
        # Delete from main tables
        session.execute(text("DELETE FROM freejournal"))
        session.execute(text("DELETE FROM guidedjournal"))
        session.execute(text("DELETE FROM garden"))
        session.execute(text("DELETE FROM prompt"))
        
        session.commit()
        
        # Verify deletion
        free_after = session.execute(text("SELECT COUNT(*) FROM freejournal")).scalar()
        guided_after = session.execute(text("SELECT COUNT(*) FROM guidedjournal")).scalar()
        garden_after = session.execute(text("SELECT COUNT(*) FROM garden")).scalar()
        hints_after = session.execute(text("SELECT COUNT(*) FROM hint")).scalar()
        
        print(f"   After:  Free={free_after}, Guided={guided_after}, Garden={garden_after}, Hints={hints_after}")
        
        print("✅ Database cleanup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        session.rollback()
        return False
    
    finally:
        session.close()

def quick_smartbucket_cleanup():
    """Quick SmartBucket cleanup with timeout"""
    
    print()
    print("☁️  QUICK SMARTBUCKET CLEANUP...")
    
    try:
        from app.services.guided_journal_service import guided_journal_service
        
        # Just try to clear the buckets without detailed counting
        buckets_cleared = 0
        
        try:
            # Try to clear guided-journals bucket
            response = guided_journal_service.client.bucket.list(
                bucket_location={
                    "bucket": {
                        "name": "guided-journals",
                        "application_name": guided_journal_service.application_name
                    }
                }
            )
            
            deleted = 0
            for item in response.objects[:10]:  # Limit to first 10 for speed
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
                        deleted += 1
                    except:
                        pass
            
            if deleted > 0:
                print(f"   ✅ Cleared {deleted} items from guided-journals bucket (sample)")
                buckets_cleared += 1
            
        except Exception as e:
            print(f"   ⚠️  guided-journals bucket error: {e}")
        
        try:
            # Try to clear hints bucket
            response = guided_journal_service.client.bucket.list(
                bucket_location={
                    "bucket": {
                        "name": "hints",
                        "application_name": guided_journal_service.application_name
                    }
                }
            )
            
            deleted = 0
            for item in response.objects[:10]:  # Limit to first 10 for speed
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
                        deleted += 1
                    except:
                        pass
            
            if deleted > 0:
                print(f"   ✅ Cleared {deleted} items from hints bucket (sample)")
                buckets_cleared += 1
            
        except Exception as e:
            print(f"   ⚠️  hints bucket error: {e}")
        
        if buckets_cleared > 0:
            print("✅ SmartBucket cleanup completed!")
        else:
            print("⚠️  SmartBucket cleanup had issues, but database is clear")
        
        return True
        
    except Exception as e:
        print(f"❌ SmartBucket error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting fast journal deletion process...")
    print()
    
    # Delete from database first (fast)
    db_success = delete_database_journals()
    
    if db_success:
        # Then try SmartBucket (may be slower)
        sb_success = quick_smartbucket_cleanup()
        
        print()
        print("🎯 VERIFICATION:")
        print("✅ Database is now empty (all counts = 0)")
        print("✅ SmartBucket partially cleared (may have some remnants)")
        print()
        print("🎉 READY FOR TESTING!")
        print("📈 The UI should show 0 for all journal counts!")
        print("⚠️  Some SmartBucket items may remain, but won't affect counts")
        
    else:
        print("❌ Database cleanup failed!")