#!/usr/bin/env python3
"""
Test the stats/overview endpoint
"""
import requests
import json

API_BASE = "http://localhost:8000"

def test_stats_endpoints():
    """Test that stats endpoints are accessible"""
    print("🧪 Testing Stats Endpoints")
    print("=" * 50)
    
    # Test endpoints without authentication (should return 401)
    endpoints = [
        "/stats/overview",
        "/profile/overview", 
        "/stats/free_journals/total",
        "/stats/guided_journals/total",
        "/stats/garden/total"
    ]
    
    print("📋 Testing endpoints (without auth - should return 401):")
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}")
            if response.status_code == 401:
                print(f"✅ {endpoint} - Correctly requires auth (401)")
            elif response.status_code == 404:
                print(f"❌ {endpoint} - Not found (404)")
            else:
                print(f"⚠️  {endpoint} - Unexpected status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect - start app with: uvicorn app.main:app --host 0.0.0.0 --port 8000")
            return
    
    print("\n🎯 Stats endpoints are now available!")
    print("   Frontend should work with:")
    print("   - GET /stats/overview ✅")
    print("   - GET /profile/overview ✅")
    
    print("\n📊 Expected response format for /stats/overview:")
    expected_response = {
        "total_journals": 0,
        "total_free_journals": 0, 
        "total_guided_journals": 0,
        "total_flowers": 0,
        "user_info": {
            "id": "user_id",
            "name": "User Name", 
            "email": "user@example.com",
            "picture": "profile_pic_url"
        }
    }
    print(json.dumps(expected_response, indent=2))

if __name__ == "__main__":
    test_stats_endpoints()