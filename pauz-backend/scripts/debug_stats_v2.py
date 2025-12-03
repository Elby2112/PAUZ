#!/usr/bin/env python3
"""
Test script to identify the specific issue in the stats endpoint
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_individual_endpoints():
    """Test each stats endpoint individually to find the problematic one"""
    
    print("🧪 Testing Individual Stats Endpoints")
    print("=" * 45)
    
    # We need a valid token for this test
    print("Note: This test requires a valid authentication token")
    print("If you don't have one, please login first and copy the token from localStorage")
    print()
    
    token = input("Enter your auth token (or press Enter to skip): ").strip()
    
    if not token:
        print("Skipping authenticated tests...")
        return
    
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    
    # Test endpoints in order of complexity
    endpoints = [
        ("/stats/guided_journals/total", "Guided Journals"),
        ("/stats/free_journals/total", "Free Journals"), 
        ("/stats/journals/total", "Total Journals"),
        ("/stats/garden/total", "Garden Flowers"),
        ("/stats/overview", "Overview (All)")
    ]
    
    for endpoint, name in endpoints:
        try:
            print(f"📍 Testing {name}...")
            response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {name}: {data}")
            elif response.status_code == 401:
                print(f"   ❌ {name}: Authentication failed")
                break
            elif response.status_code == 500:
                print(f"   ❌ {name}: Server Error - PROBLEM FOUND")
                print(f"   Response: {response.text}")
            else:
                print(f"   ❓ {name}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"   ❌ {name}: Exception - {e}")

def test_without_garden():
    """Test if removing Garden model fixes the issue"""
    
    print("\n🔧 Testing Without Garden Model")
    print("=" * 35)
    
    print("Creating a temporary stats endpoint without Garden queries...")
    
    # We can't modify the running server, but we can suggest the fix
    print("Suggested fix for app/routes/stats.py:")
    print("""
@router.get("/overview/test")
def get_user_overview_stats_test(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    # Get counts without Garden model
    total_guided_journals = db.scalar(
        select(func.count()).where(GuidedJournal.user_id == current_user.id)
    )
    total_free_journals = db.scalar(
        select(func.count()).where(FreeJournal.user_id == current_user.id)
    )
    
    total_journals = total_guided_journals + total_free_journals
    
    return {
        "total_journals": total_journals,
        "total_free_journals": total_free_journals,
        "total_guided_journals": total_guided_journals,
        "total_flowers": 0  # Temporarily set to 0
    }
    """)

def check_database_tables():
    """Check if Garden table exists in database"""
    
    print("\n🗄️  Checking Database Tables")
    print("=" * 30)
    
    print("To check if Garden table exists, run this in your backend:")
    print("""
import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Specifically check for Garden table
if any('garden' in table[0].lower() for table in tables):
    print("✅ Garden table exists")
else:
    print("❌ Garden table missing - this is the problem!")

conn.close()
    """)

if __name__ == "__main__":
    print("🚀 Stats Endpoint Debug Tool v2")
    print("=" * 50)
    
    test_individual_endpoints()
    test_without_garden()
    check_database_tables()
    
    print("\n🔧 Most Likely Issues:")
    print("1. Garden table doesn't exist in database")
    print("2. Garden model import is failing")
    print("3. Database relationship issue with User-Garden")
    print("\n📋 Quick Fix:")
    print("1. Temporarily remove Garden queries from stats.py")
    print("2. Test if other stats work")
    print("3. Check if database tables were created properly")