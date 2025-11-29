# test_guided_journal.py
import requests

# Base URL
BASE_URL = "http://localhost:8000"


def test_generate_prompts():
    """Test ONLY the prompt generation"""
    print("🧪 Testing: Generate Prompts")

    url = f"{BASE_URL}/guided_journal/prompts"
    data = {
        "topic": "personal growth"
    }

    try:
        response = requests.post(url, json=data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            prompts = response.json()
            print(f"✅ SUCCESS: Got {len(prompts)} prompts")
            for prompt in prompts:
                print(f"  - {prompt['text']}")
        else:
            print(f"❌ FAILED: {response.text}")

    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    test_generate_prompts()