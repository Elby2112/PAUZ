#!/usr/bin/env python3
"""
Test the garden API with proper format checking
"""

import json
from datetime import datetime

def test_garden_response_format():
    """Test what the garden response should look like"""
    
    # Simulate what the backend should return
    mock_response = [
        {
            "id": 1,
            "mood": "happy",
            "date": "2025-01-15",
            "note": "Had a great day with friends!",
            "flower_type": "happy",
            "created_at": "2025-01-15T14:30:00.123456"
        },
        {
            "id": 2, 
            "mood": "reflective",
            "date": "2025-01-14",
            "note": "Thinking about life goals and career path",
            "flower_type": "reflective", 
            "created_at": "2025-01-14T09:15:30.654321"
        }
    ]
    
    print("Expected Garden API Response Format:")
    print(json.dumps(mock_response, indent=2))
    
    # Test what frontend expects
    print("\nFrontend Expected Transformation:")
    for entry in mock_response:
        frontend_format = {
            "id": entry["id"],
            "mood": entry["mood"], 
            "date": entry["date"],
            "note": entry["note"]
        }
        print(json.dumps(frontend_format, indent=2))

if __name__ == "__main__":
    test_garden_response_format()