"""
Verify all journal counts are 0
"""
import os
import sys
sys.path.append('.')

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.database import DATABASE_URL

def verify_all_counts_zero():
    """Verify all journal tables are empty"""
    
    print("🔍 VERIFYING ALL JOURNAL COUNTS ARE 0")
    print("=" * 50)
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Check all relevant tables
        tables = {
            'Free Journals': 'freejournal',
            'Guided Journals': 'guidedjournal', 
            'Garden Flowers': 'garden',
            'Hints': 'hint',
            'Guided Entries': 'guidedjournalentry',
            'Prompts': 'prompt'
        }
        
        all_zero = True
        
        for name, table in tables.items():
            try:
                count = session.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
                status = "✅" if count == 0 else "❌"
                print(f"   {status} {name}: {count}")
                if count != 0:
                    all_zero = False
            except Exception as e:
                print(f"   ⚠️  {name}: Error - {e}")
        
        print()
        if all_zero:
            print("🎉 SUCCESS! All journal counts are 0!")
            print("📈 The UI should display 0 for all journal statistics.")
            print("🚀 Ready for testing the performance optimizations!")
        else:
            print("⚠️  Some tables still have data.")
        
        return all_zero
        
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False
    
    finally:
        session.close()

if __name__ == "__main__":
    verify_all_counts_zero()