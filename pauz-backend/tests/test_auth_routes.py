from fastapi.testclient import TestClient
from app.main import app
from app.models import User

# client = TestClient(app) # Remove global client, use client_with_db fixture

def test_read_users_me(client_with_db: TestClient):
    """
    Tests the GET /auth/me endpoint.
    This relies on the global 'override_get_current_user' fixture in conftest.py
    """
    response = client_with_db.get("/auth/me")
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["email"] == "test@example.com"
    assert json_response["name"] == "Test User"
    assert json_response["id"] == "test-user-id"
