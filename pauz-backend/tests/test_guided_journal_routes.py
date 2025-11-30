from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from app.main import app
from app.models import User, GuidedJournal, Prompt
from app.dependencies import get_current_user

# client = TestClient(app) # Remove global client, use client_with_db fixture

def test_generate_prompts_route(client_with_db: TestClient):
    """
    Tests the POST /guided_journal/prompts endpoint.
    """
    # 1. Mock the service method
    # The response model is Prompt, which is a SQLModel. It will have guided_journal_id.
    mock_prompts = [
        {"id": 1, "text": "What are you grateful for today?", "guided_journal_id": None},
        {"id": 2, "text": "Describe a small victory you had this week.", "guided_journal_id": None}
    ]
    with patch('app.services.guided_journal_service.guided_journal_service.generate_prompts', return_value=mock_prompts) as mock_generate_prompts:
        
        # 2. Make the HTTP request
        response = client_with_db.post("/guided_journal/prompts", json={"topic": "Gratitude"})
        
        # 3. Assert the results
        assert response.status_code == 200
        assert response.json() == mock_prompts
        mock_generate_prompts.assert_called_once_with("Gratitude")

def test_create_journal_route(client_with_db: TestClient):
    """
    Tests the POST /guided_journal/ endpoint for creating a new journal.
    """
    # 1. Mock the service method
    # The service returns a GuidedJournal object, so we mock it with a real model instance.
    mock_journal_prompts = [Prompt(id=1, text="What is a new skill you want to learn?")]
    mock_journal_obj = GuidedJournal(
        id="new-journal-id",
        user_id="test-user-id",
        topic="Growth",
        prompts=mock_journal_prompts,
        entries=[]
    )
    with patch('app.services.guided_journal_service.guided_journal_service.create_guided_journal', return_value=mock_journal_obj) as mock_create_journal:
        
        # 2. Make the HTTP request
        request_body = {
            "topic": "Growth",
            "prompts": [{"id": 1, "text": "What is a new skill you want to learn?"}]
        }
        response = client_with_db.post("/guided_journal/", json=request_body)
        
        # 3. Assert the results
        assert response.status_code == 200
        # The response JSON should match the model's dict representation
        assert response.json()['id'] == "new-journal-id"
        assert response.json()['topic'] == "Growth"
        
        mock_create_journal.assert_called_once_with(
            user_id="test-user-id",
            topic="Growth",
            prompts_data=[{"id": 1, "text": "What is a new skill you want to learn?"}]
        )

# To run this test:
# 1. Make sure you have pytest installed: `pip install pytest`
# 2. Run pytest from your project's root directory: `pytest`
