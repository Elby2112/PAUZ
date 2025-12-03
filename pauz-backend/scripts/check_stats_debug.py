#!/usr/bin/env python3
"""
Test script to check what data is in the database and verify the stats endpoint
"""
import os
import sys
sys.path.append('.')

from app.database import get_session
from app.models import User, GuidedJournal, FreeJournal, Garden
from sqlmodel import select

def check_database_data():
    """Check what's actually in the database"""
    print("🔍 Checking database contents...")
    print("=" * 50)
    
    try:
        db = next(get_session())
        try:
            # Get all users
            users = db.exec(select(User)).all()
            print(f"📊 Total users: {len(users)}")
            
            for user in users:
                print(f"\n👤 User: {user.email} (ID: {user.id})")
                
                # Check guided journals for this user
                guided_journals = db.exec(
                    select(GuidedJournal).where(GuidedJournal.user_id == user.id)
                ).all()
                print(f"   📝 Guided journals: {len(guided_journals)}")
                
                # Check free journals for this user
                free_journals = db.exec(
                    select(FreeJournal).where(FreeJournal.user_id == user.id)
                ).all()
                print(f"   📄 Free journals: {len(free_journals)}")
                
                # Check garden items for this user
                gardens = db.exec(
                    select(Garden).where(Garden.user_id == user.id)
                ).all()
                print(f"   🌱 Garden items: {len(gardens)}")
                
                # Show guided journal details
                if guided_journals:
                    print("   📋 Guided journal details:")
                    for gj in guided_journals:
                        print(f"      - ID: {gj.id}, Topic: {gj.topic}, Created: {gj.created_at}")
                
                # Show free journal details
                if free_journals:
                    print("   📋 Free journal details:")
                    for fj in free_journals:
                        print(f"      - ID: {fj.id}, Session: {fj.session_id}, Created: {fj.created_at}")
        finally:
            db.close()
                        
    except Exception as e:
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()

def test_stats_endpoint_logic():
    """Test the exact logic used in the stats endpoint"""
    print("\n🔍 Testing stats endpoint logic...")
    print("=" * 50)
    
    try:
        db = next(get_session())
        try:
            # Get first user for testing
            user = db.exec(select(User)).first()
            if not user:
                print("❌ No users found in database")
                return
                
            print(f"👤 Testing with user: {user.email} (ID: {user.id})")
            
            # Test guided journal count (same logic as stats endpoint)
            guided_count = db.exec(
                select(GuidedJournal).where(GuidedJournal.user_id == user.id)
            ).all()
            guided_total = len(guided_count)
            print(f"📝 Guided journals (direct query): {guided_total}")
            
            # Test with count() function (same as stats endpoint)
            from sqlmodel import func
            guided_count_func = db.scalar(
                select(func.count()).where(GuidedJournal.user_id == user.id)
            )
            print(f"📝 Guided journals (count function): {guided_count_func or 0}")
            
            # Test free journal count
            free_count_func = db.scalar(
                select(func.count()).where(FreeJournal.user_id == user.id)
            )
            print(f"📄 Free journals: {free_count_func or 0}")
            
            # Test garden count
            try:
                garden_count_func = db.scalar(
                    select(func.count()).where(Garden.user_id == user.id)
                )
                print(f"🌱 Garden items: {garden_count_func or 0}")
            except Exception as garden_error:
                print(f"🌱 Garden count error: {garden_error}")
        finally:
            db.close()
                
    except Exception as e:
        print(f"❌ Logic test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_database_data()
    test_stats_endpoint_logic()