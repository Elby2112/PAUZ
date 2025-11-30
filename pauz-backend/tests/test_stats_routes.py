from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.models import FreeJournal, GuidedJournal

# client = TestClient(app) # Removed global client, use client_with_db fixture

def test_get_total_guided_journals(client_with_db: TestClient):
    """
    Tests GET /stats/guided_journals/total
    """
    response = client_with_db.get("/stats/guided_journals/total")
    assert response.status_code == 200
    assert response.json() == {"total_guided_journals": 2} # Expect 2 guided journals from conftest.py

def test_get_total_free_journals(client_with_db: TestClient):
    """
    Tests GET /stats/free_journals/total
    """
    response = client_with_db.get("/stats/free_journals/total")
    assert response.status_code == 200
    assert response.json() == {"total_free_journals": 3} # Expect 3 free journals from conftest.py

def test_get_total_journals(client_with_db: TestClient):
    """
    Tests GET /stats/journals/total
    """
    response = client_with_db.get("/stats/journals/total")
    assert response.status_code == 200
    assert response.json() == {"total_journals": 5} # Expect 2 guided + 3 free journals
