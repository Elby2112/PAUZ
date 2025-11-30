from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app
from app.models import Garden
import datetime

# client = TestClient(app) # Remove global client, use client_with_db fixture

def test_create_garden_entry_route(client_with_db: TestClient):
    """
    Tests POST /garden/
    """
    mock_entry = Garden(
        id=1,
        user_id="test-user-id",
        created_at=datetime.datetime.utcnow(),
        mood="happy",
        note="Good day",
        flower_type="sunflower"
    )
    with patch('app.services.garden_service.garden_service.create_garden_entry', return_value=mock_entry) as mock_create:
        response = client_with_db.post("/garden/", json={"mood": "happy", "note": "Good day", "flower_type": "sunflower"})
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["mood"] == "happy"
        assert json_response["flower_type"] == "sunflower"
        mock_create.assert_called_once()

def test_get_garden_entries_route(client_with_db: TestClient):
    """
    Tests GET /garden/
    """
    mock_entries = [
        Garden(id=1, user_id="test-user-id", created_at=datetime.datetime.utcnow(), mood="happy", note="Good day", flower_type="sunflower"),
        Garden(id=2, user_id="test-user-id", created_at=datetime.datetime.utcnow(), mood="calm", note="Relaxing", flower_type="lavender")
    ]
    with patch('app.services.garden_service.garden_service.get_garden_entries', return_value=mock_entries) as mock_get:
        response = client_with_db.get("/garden/")
        assert response.status_code == 200
        json_response = response.json()
        assert len(json_response) == 2
        assert json_response[0]["mood"] == "happy"
        assert json_response[1]["mood"] == "calm"
        mock_get.assert_called_once()
