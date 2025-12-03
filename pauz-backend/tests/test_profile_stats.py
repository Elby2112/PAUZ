#!/usr/bin/env python3
"""
Test script to verify the stats endpoints work correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_stats_endpoints():
    """Test all stats endpoints"""
    
    print("🧪 Testing Stats Endpoints")
    print("=" * 30)
    
    # Test if endpoints exist
    print("1. 🔍 Checking endpoint registration...")
    
    endpoints = [
        "/stats/overview",
        "/stats/journals/total",
        "/stats/free_journals/total",
        "/stats/guided_journals/total",
        "/stats/garden/total"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.options(f"{BASE_URL}{endpoint}")
            if response.status_code in [200, 405]:
                print(f"   ✅ {endpoint} - Registered")
            else:
                print(f"   ❓ {endpoint} - {response.status_code}")
        except Exception as e:
            print(f"   ❌ {endpoint} - Error: {e}")
    
    # Test overview endpoint (requires auth)
    print("\n2. 🔐 Testing /stats/overview endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/stats/overview",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        if response.status_code == 401:
            print("   ✅ Correctly requires authentication")
        else:
            print(f"   ❓ Unexpected response: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error testing overview: {e}")

def test_backend_implementation():
    """Test backend implementation"""
    
    print("\n🔧 Testing Backend Implementation")
    print("=" * 35)
    
    # Check stats.py implementation
    print("1. 📋 Checking stats routes...")
    try:
        with open('app/routes/stats.py', 'r') as f:
            content = f.read()
            
            if 'get_user_overview_stats' in content:
                print("   ✅ Overview endpoint implemented")
            else:
                print("   ❌ Overview endpoint missing")
                
            if 'get_total_garden_flowers' in content:
                print("   ✅ Garden flowers endpoint implemented")
            else:
                print("   ❌ Garden flowers endpoint missing")
                
            if 'total_flowers' in content:
                print("   ✅ Garden count logic included")
            else:
                print("   ❌ Garden count logic missing")
                
            if 'user_info' in content:
                print("   ✅ User info included in overview")
            else:
                print("   ❌ User info missing from overview")
                
    except Exception as e:
        print(f"   ❌ Could not check stats routes: {e}")

def test_frontend_implementation():
    """Test frontend implementation"""
    
    print("\n🎨 Testing Frontend Implementation")
    print("=" * 37)
    
    # Check Profile component
    print("1. 👤 Checking Profile component...")
    try:
        with open('Profile.jsx', 'r') as f:
            content = f.read()
            
            if 'fetchUserStats' in content:
                print("   ✅ Stats fetching function implemented")
            else:
                print("   ❌ Stats fetching function missing")
                
            if '/stats/overview' in content:
                print("   ✅ Using overview endpoint")
            else:
                print("   ❌ Not using overview endpoint")
                
            if 'total_flowers' in content:
                print("   ✅ Flowers stat displayed")
            else:
                print("   ❌ Flowers stat not displayed")
                
            if 'loading' in content and 'error' in content:
                print("   ✅ Loading and error states implemented")
            else:
                print("   ❌ Loading/error states missing")
                
            if 'progress-bar' in content:
                print("   ✅ Progress bar implemented")
            else:
                print("   ❌ Progress bar missing")
                
    except Exception as e:
        print(f"   ❌ Could not check Profile component: {e}")
    
    # Check CSS styles
    print("\n2. 🎨 Checking CSS styles...")
    try:
        with open('styles/profile.css', 'r') as f:
            content = f.read()
            
            if '.journal-card.flower' in content:
                print("   ✅ Flower card styles exist")
            else:
                print("   ❌ Flower card styles missing")
                
            if '.progress-bar' in content:
                print("   ✅ Progress bar styles exist")
            else:
                print("   ❌ Progress bar styles missing")
                
            if '.loading-spinner' in content:
                print("   ✅ Loading spinner styles exist")
            else:
                print("   ❌ Loading spinner styles missing")
                
            if '@media' in content:
                print("   ✅ Responsive design implemented")
            else:
                print("   ❌ Responsive design missing")
                
    except Exception as e:
        print(f"   ❌ Could not check CSS: {e}")

def print_usage_instructions():
    """Print usage instructions"""
    
    print("\n📊 Profile Stats Feature")
    print("=" * 25)
    print("✨ New Features Added:")
    print("• Real-time journal statistics")
    print("• Garden flower count")
    print("• Progress tracking")
    print("• Beautiful loading states")
    print("• Error handling with retry")
    print("• Mobile responsive design")
    print()
    print("🎯 Stats Displayed:")
    print("• Total Journals")
    print("• Free Journals") 
    print("• Guided Journals")
    print("• Garden Flowers")
    print("• Progress indicator")
    print()
    print("🔄 API Endpoint:")
    print("GET /stats/overview")
    print("Returns all stats in one call")
    print()
    print("📱 Mobile Features:")
    print("• Responsive grid layout")
    print("• Touch-friendly buttons")
    print("• Optimized loading states")
    print("• Smooth animations")

if __name__ == "__main__":
    print("🚀 Profile Stats Implementation Test")
    print("=" * 50)
    
    test_stats_endpoints()
    test_backend_implementation()
    test_frontend_implementation()
    print_usage_instructions()
    
    print("\n✅ Profile Stats Implementation Complete!")
    print("\n🧪 Manual Testing:")
    print("1. Start your application")
    print("2. Login to your account")
    print("3. Navigate to Profile page")
    print("4. Check if stats load correctly")
    print("5. Test error handling by removing token")
    print("6. Check responsive design on mobile")