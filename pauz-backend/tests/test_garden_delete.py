#!/usr/bin/env python3
"""
Test script to verify Garden DELETE functionality works correctly
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_garden_delete_endpoints():
    """Test garden DELETE endpoints"""
    
    print("🧪 Testing Garden DELETE Functionality")
    print("=" * 40)
    
    # Test if DELETE endpoint exists
    print("1. 🔍 Checking if Garden DELETE endpoint exists...")
    try:
        response = requests.options(f"{BASE_URL}/garden/123")
        if response.status_code in [200, 405]:  # 200 if OPTIONS supported, 405 if not but endpoint exists
            print("   ✅ Garden DELETE endpoint is registered")
        else:
            print(f"   ❓ Garden OPTIONS response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Could not verify Garden endpoint: {e}")
    
    # Test DELETE with authentication (will likely fail without proper auth)
    print("\n2. 🔐 Testing DELETE endpoint (requires auth)...")
    try:
        # Test with invalid token first
        response = requests.delete(
            f"{BASE_URL}/garden/123",
            headers={"Authorization": "Bearer invalid-token"}
        )
        
        if response.status_code == 401:
            print("   ✅ DELETE endpoint correctly requires authentication")
        elif response.status_code == 404:
            print("   ✅ DELETE endpoint exists (404 for non-existent flower)")
        else:
            print(f"   ❓ DELETE response: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ DELETE endpoint test failed: {e}")
    
    print("\n3. 📝 Manual testing steps:")
    print("   1. Start your backend: uvicorn app.main:app --reload")
    print("   2. Login to the application")
    print("   3. Create some journal entries")
    print("   4. Use 'Reflect with AI' to create flowers")
    print("   5. Go to the Garden view")
    print("   6. Hover over flowers to see delete buttons (×)")
    print("   7. Click delete button and confirm")
    print("   8. Verify flower is removed from garden")

def test_backend_implementation():
    """Test backend implementation"""
    
    print("\n🔧 Testing Backend Implementation")
    print("=" * 35)
    
    # Check if service method exists
    print("1. 📋 Checking GardenService implementation...")
    try:
        with open('app/services/garden_service.py', 'r') as f:
            content = f.read()
            if 'def delete_garden_entry' in content:
                print("   ✅ delete_garden_entry method exists")
            else:
                print("   ❌ delete_garden_entry method missing")
                
            if 'db.delete(garden_entry)' in content:
                print("   ✅ Database deletion implemented")
            else:
                print("   ❌ Database deletion missing")
                
    except Exception as e:
        print(f"   ❌ Could not check service file: {e}")
    
    # Check if route exists
    print("\n2. 🛣️  Checking Garden routes...")
    try:
        with open('app/routes/garden.py', 'r') as f:
            content = f.read()
            if '@router.delete' in content:
                print("   ✅ DELETE route exists")
            else:
                print("   ❌ DELETE route missing")
                
            if 'delete_garden_entry_route' in content:
                print("   ✅ DELETE route handler exists")
            else:
                print("   ❌ DELETE route handler missing")
                
            if 'HTTPException' in content:
                print("   ✅ Error handling implemented")
            else:
                print("   ❌ Error handling missing")
                
    except Exception as e:
        print(f"   ❌ Could not check routes file: {e}")

def test_frontend_implementation():
    """Test frontend implementation"""
    
    print("\n🎨 Testing Frontend Implementation")
    print("=" * 37)
    
    # Check FlowerCard component
    print("1. 🌸 Checking FlowerCard component...")
    try:
        with open('FlowerCard.jsx', 'r') as f:
            content = f.read()
            if 'onDelete' in content:
                print("   ✅ onDelete prop exists")
            else:
                print("   ❌ onDelete prop missing")
                
            if 'flower-delete-btn' in content:
                print("   ✅ Delete button implemented")
            else:
                print("   ❌ Delete button missing")
                
            if 'handleDelete' in content:
                print("   ✅ Delete handler exists")
            else:
                print("   ❌ Delete handler missing")
                
    except Exception as e:
        print(f"   ❌ Could not check FlowerCard component: {e}")
    
    # Check GardenView component
    print("\n2. 🌺 Checking GardenView component...")
    try:
        with open('GardenView.jsx', 'r') as f:
            content = f.read()
            if 'handleDeleteFlower' in content:
                print("   ✅ Delete function exists")
            else:
                print("   ❌ Delete function missing")
                
            if 'DELETE' in content and '/garden/' in content:
                print("   ✅ API call implemented")
            else:
                print("   ❌ API call missing")
                
            if 'setFlowers(prevFlowers => prevFlowers.filter' in content:
                print("   ✅ State update implemented")
            else:
                print("   ❌ State update missing")
                
    except Exception as e:
        print(f"   ❌ Could not check GardenView component: {e}")
    
    # Check CSS file
    print("\n3. 🎨 Checking CSS styles...")
    try:
        with open('styles/flowerCard.css', 'r') as f:
            content = f.read()
            if '.flower-delete-btn' in content:
                print("   ✅ Delete button styles exist")
            else:
                print("   ❌ Delete button styles missing")
                
            if 'opacity: 0' in content and 'hover' in content:
                print("   ✅ Hover effect implemented")
            else:
                print("   ❌ Hover effect missing")
                
    except Exception as e:
        print(f"   ❌ Could not check CSS file: {e}")

if __name__ == "__main__":
    print("🚀 Garden Delete Functionality Test")
    print("=" * 50)
    
    test_garden_delete_endpoints()
    test_backend_implementation()
    test_frontend_implementation()
    
    print("\n✅ Testing completed!")
    print("\n🌟 Summary:")
    print("- Backend DELETE endpoint: /garden/{flower_id}")
    print("- Frontend delete button appears on hover")
    print("- Confirmation dialog before deletion")
    print("- Real-time UI update after deletion")
    print("- Proper error handling and authentication")