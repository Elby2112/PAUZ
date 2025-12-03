#!/usr/bin/env python3
"""
Test script to verify the stats endpoint works correctly
"""
import requests
import json

def test_stats_endpoint():
    print("🔍 Testing /stats/overview endpoint...")
    print("=" * 50)
    
    # Test without authentication
    print("📋 Test 1: Without authentication")
    try:
        response = requests.get("http://localhost:8000/stats/overview")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n📋 Test 2: Check endpoint exists")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"   Backend status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Backend is running")
        else:
            print("   ❌ Backend is not responding correctly")
    except Exception as e:
        print(f"   ❌ Backend connection error: {e}")
    
    print("\n📋 Test 3: Check available routes")
    try:
        response = requests.get("http://localhost:8000/docs")
        print(f"   Docs endpoint: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ FastAPI docs available")
        else:
            print("   ❌ FastAPI docs not available")
    except Exception as e:
        print(f"   ❌ Docs endpoint error: {e}")

if __name__ == "__main__":
    test_stats_endpoint()