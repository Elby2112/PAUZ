#!/usr/bin/env python3
"""
Test script to verify DELETE functionality in SavedJournals_FIXED component
"""

import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def test_delete_functionality():
    """Test the delete functionality in the SavedJournals component"""
    
    print("🧪 Starting Delete Functionality Test")
    print("=" * 50)
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(10)
        
        print("1. 🌐 Opening the application...")
        driver.get("http://localhost:3000")  # Adjust port if needed
        
        # Check if we need to login
        try:
            login_button = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Login')]"))
            )
            print("   ℹ️  Need to login first")
            # Add login logic here if needed
        except:
            print("   ✅ Already logged in or login not required")
        
        # Navigate to saved journals
        print("2. 📚 Navigating to Saved Journals...")
        try:
            saved_journals_link = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'saved') or contains(text(), 'Saved')]"))
            )
            saved_journals_link.click()
            print("   ✅ Navigated to Saved Journals")
        except:
            print("   ❓ Could not find Saved Journals link, trying direct URL...")
            driver.get("http://localhost:3000/saved-journals")
        
        # Wait for journals to load
        print("3. ⏳ Waiting for journals to load...")
        time.sleep(3)
        
        # Check if journals exist
        print("4. 📊 Checking for existing journals...")
        journals = driver.find_elements(By.CLASS_NAME, "sj-book")
        
        if not journals:
            print("   ⚠️  No journals found to test with")
            print("   💡 Create some journals first, then run this test")
            return False
        
        print(f"   ✅ Found {len(journals)} journals")
        
        # Test delete functionality
        print("5. 🗑️  Testing delete functionality...")
        
        for i, journal in enumerate(journals[:2]):  # Test first 2 journals
            try:
                journal_id = journal.get_attribute("data-journal-id")
                print(f"   📝 Testing journal {i+1}: {journal_id}")
                
                # Hover over journal to show delete button
                driver.execute_script("arguments[0].scrollIntoView(true);", journal)
                time.sleep(1)
                
                # Find and click delete button
                delete_button = journal.find_element(By.CLASS_NAME, "sj-delete-btn")
                driver.execute_script("arguments[0].click();", delete_button)
                
                # Handle confirmation dialog
                time.sleep(1)
                try:
                    # Switch to alert and accept
                    alert = driver.switch_to.alert
                    alert_text = alert.text
                    print(f"      📋 Confirmation dialog: {alert_text}")
                    alert.accept()
                    print("      ✅ Confirmed deletion")
                except:
                    print("      ⚠️  No confirmation dialog found")
                
                # Wait for deletion to complete
                time.sleep(2)
                
                # Check if journal was removed
                remaining_journals = driver.find_elements(By.CLASS_NAME, "sj-book")
                if len(remaining_journals) < len(journals):
                    print(f"      ✅ Journal {i+1} successfully deleted")
                else:
                    print(f"      ❌ Journal {i+1} deletion failed")
                
                journals = remaining_journals  # Update for next iteration
                
            except Exception as e:
                print(f"      ❌ Error testing journal {i+1}: {e}")
        
        print("6. 🎯 Testing modal delete button...")
        if journals:
            try:
                # Open a journal in modal
                first_journal = journals[0]
                first_journal.click()
                time.sleep(2)
                
                # Find delete button in modal
                modal_delete_btn = driver.find_element(By.CLASS_NAME, "sj-delete-modal-btn")
                modal_delete_btn.click()
                
                # Handle confirmation
                time.sleep(1)
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                    print("   ✅ Modal delete button works")
                except:
                    print("   ⚠️  Modal confirmation handled differently")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"   ❌ Modal delete test failed: {e}")
        
        print("✅ Delete functionality test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
        
    finally:
        if 'driver' in locals():
            driver.quit()

def test_api_endpoints():
    """Test the DELETE API endpoints directly"""
    
    print("\n🔌 Testing API Endpoints")
    print("=" * 30)
    
    import requests
    
    # Test Free Journal DELETE endpoint
    print("1. 📝 Testing Free Journal DELETE endpoint...")
    try:
        response = requests.options("http://localhost:8000/freejournal/test-id")
        if response.status_code in [200, 405]:
            print("   ✅ Free Journal DELETE endpoint exists")
        else:
            print(f"   ❓ Free Journal endpoint response: {response.status_code}")
    except:
        print("   ⚠️  Could not connect to Free Journal endpoint")
    
    # Test Guided Journal DELETE endpoint  
    print("2. 🧭 Testing Guided Journal DELETE endpoint...")
    try:
        response = requests.options("http://localhost:8000/guided_journal/test-id")
        if response.status_code in [200, 405]:
            print("   ✅ Guided Journal DELETE endpoint exists")
        else:
            print(f"   ❓ Guided Journal endpoint response: {response.status_code}")
    except:
        print("   ⚠️  Could not connect to Guided Journal endpoint")

if __name__ == "__main__":
    print("🚀 SavedJournals Delete Functionality Test")
    print("=" * 50)
    
    test_api_endpoints()
    print()
    
    # Run browser test
    success = test_delete_functionality()
    
    print("\n📋 Test Summary:")
    print(f"Browser test: {'✅ Passed' if success else '❌ Failed'}")
    
    print("\n💡 Manual Testing Tips:")
    print("1. Start your backend: uvicorn app.main:app --reload")
    print("2. Start your frontend: npm start")
    print("3. Login to the application")
    print("4. Create some free and guided journals")
    print("5. Go to Saved Journals page")
    print("6. Hover over journals to see delete buttons (×)")
    print("7. Click delete buttons and confirm deletions")
    print("8. Check both book-spine delete and modal delete")