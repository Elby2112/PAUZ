#!/usr/bin/env python3
"""
Test the updated stats endpoint with actual authentication
"""
import requests
import json
import os
import sys
sys.path.append('.')

def create_test_token_for_user(email):
    """Create a test token for a specific user email"""
    try:
        from app.services.jwt_service import create_access_token
        token = create_access_token(data={"sub": email})
        return token
    except Exception as e:
        print(f"❌ Error creating token for {email}: {e}")
        return None

def test_stats_for_users():
    """Test stats endpoint for different users"""
    print("🔍 Testing updated stats endpoint...")
    print("=" * 50)
    
    # Test users we know have guided journals
    test_users = [
        "loubnabouzenzen820@gmail.com",  # Has 1 guided journal in SmartBucket
        "loubna.bouzenzen2112@gmail.com",  # Has 1 guided journal in SmartBucket
    ]
    
    for email in test_users:
        print(f"\n👤 Testing stats for: {email}")
        
        # Create token
        token = create_test_token_for_user(email)
        if not token:
            continue
            
        print(f"✅ Token created: {token[:20]}...")
        
        # Test stats endpoint
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get("http://localhost:8000/stats/overview", headers=headers)
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Stats response:")
                print(f"   - Total Journals: {data.get('total_journals', 0)}")
                print(f"   - Free Journals: {data.get('total_free_journals', 0)}")
                print(f"   - Guided Journals: {data.get('total_guided_journals', 0)}")
                print(f"   - Garden Flowers: {data.get('total_flowers', 0)}")
                
                # Verify guided journal count
                guided_count = data.get('total_guided_journals', 0)
                if guided_count > 0:
                    print(f"🎉 SUCCESS: Guided journals counted correctly: {guided_count}")
                else:
                    print(f"⚠️  Expected guided journals but got 0")
            else:
                print(f"❌ Error response: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Raw: {response.text}")
                    
        except Exception as e:
            print(f"❌ Request error: {e}")

if __name__ == "__main__":
    test_stats_for_users()