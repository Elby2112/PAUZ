from fastapi.testclient import TestClient
from unittest.mock import patch

from app.main import app

# client = TestClient(app) # Remove global client, use client_with_db fixture

def test_get_inference(client_with_db: TestClient):
    """
    Tests POST /inference/
    """
    mock_response = {
        "result": "This is a mock response",
        "model": "openai/gpt-3.5-turbo",
    }
    with patch('app.services.inference_service.inference_service.get_completion_with_smart_inference', return_value=mock_response) as mock_inference:
        response = client_with_db.post("/inference/", json={"prompt": "Hello", "model": "openai/gpt-3.5-turbo"})
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["result"] == "This is a mock response"
        mock_inference.assert_called_once_with(prompt="Hello", model="openai/gpt-3.5-turbo")
