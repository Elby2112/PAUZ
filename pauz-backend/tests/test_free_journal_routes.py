from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, ANY
from app.main import app
from app.models import FreeJournal, Hint
import datetime

# client = TestClient(app) # Remove global client, use client_with_db fixture

# All endpoints require authentication, which is handled by the fixture in conftest.py

def test_create_free_journal_session_route(client_with_db: TestClient):
    """
    Tests POST /freejournal/
    """
    mock_journal = FreeJournal(
        id=1,
        user_id="test-user-id",
        session_id="test-session-id",
        content="",
        created_at=datetime.datetime.utcnow()
    )
    with patch('app.services.free_journal_service.free_journal_service.create_free_journal_session', return_value=mock_journal) as mock_create:
        response = client_with_db.post("/freejournal/")
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["session_id"] == "test-session-id"
        assert json_response["user_id"] == "test-user-id"
        mock_create.assert_called_once()

def test_get_free_journal_session_route(client_with_db: TestClient):
    """
    Tests GET /freejournal/{session_id}
    """
    mock_journal = FreeJournal(id=1, user_id="test-user-id", session_id="test-session-id", content="Hello", created_at=datetime.datetime.utcnow())
    with patch('app.services.free_journal_service.free_journal_service.get_free_journal_by_session_id', return_value=mock_journal) as mock_get:
        response = client_with_db.get("/freejournal/test-session-id")
        assert response.status_code == 200
        assert response.json()["content"] == "Hello"
        mock_get.assert_called_once_with("test-session-id", "test-user-id", ANY)

def test_save_user_content_route(client_with_db: TestClient):
    """
    Tests POST /freejournal/{session_id}/save
    """
    mock_journal = FreeJournal(id=1, user_id="test-user-id", session_id="test-session-id", content="Updated content", created_at=datetime.datetime.utcnow())
    with patch('app.services.free_journal_service.free_journal_service.save_user_content', return_value=mock_journal) as mock_save:
        response = client_with_db.post("/freejournal/test-session-id/save", json={"content": "Updated content"})
        assert response.status_code == 200
        assert response.json()["content"] == "Updated content"
        mock_save.assert_called_once_with("test-session-id", "test-user-id", "Updated content", ANY)

def test_get_hints_route(client_with_db: TestClient):
    """
    Tests POST /freejournal/{session_id}/hints
    """
    mock_hint = Hint(id=1, user_id="test-user-id", session_id="test-session-id", hint_text="Tell me more.", created_at=datetime.datetime.utcnow())
    with patch('app.services.free_journal_service.free_journal_service.generate_hints', return_value=mock_hint) as mock_hint_gen:
        response = client_with_db.post("/freejournal/test-session-id/hints", json={"current_content": "I feel happy."})
        assert response.status_code == 200
        assert response.json()["hint_text"] == "Tell me more."
        mock_hint_gen.assert_called_once()

def test_transcribe_voice_route(client_with_db: TestClient):
    """
    Tests POST /freejournal/{session_id}/voice
    """
    mock_journal = FreeJournal(id=1, user_id="test-user-id", session_id="test-session-id", content="This is a test.", created_at=datetime.datetime.utcnow())
    with patch('app.services.free_journal_service.free_journal_service.transcribe_audio', return_value=mock_journal) as mock_transcribe:
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake audio data"
        response = client_with_db.post("/freejournal/test-session-id/voice", files={"audio_file": ("test.wav", b"fake audio data", "audio/wav")})
        assert response.status_code == 200
        assert response.json()["content"] == "This is a test."
        mock_transcribe.assert_called_once()

def test_reflect_with_ai_route(client_with_db: TestClient):
    """
    Tests POST /freejournal/{session_id}/reflect
    """
    mock_reflection = {"mood": "positive", "insights": "You are happy."}
    with patch('app.services.free_journal_service.free_journal_service.reflect_with_ai', return_value=mock_reflection) as mock_reflect:
        response = client_with_db.post("/freejournal/test-session-id/reflect")
        assert response.status_code == 200
        assert response.json() == mock_reflection
        mock_reflect.assert_called_once()

def test_export_free_journal_route(client_with_db: TestClient):
    """
    Tests POST /freejournal/{session_id}/export
    """
    with patch('app.services.free_journal_service.free_journal_service.export_to_pdf', return_value="https://fake.url/doc.pdf") as mock_export:
        response = client_with_db.post("/freejournal/test-session-id/export")
        assert response.status_code == 200
        assert response.json() == {"pdfUrl": "https://fake.url/doc.pdf"}
        mock_export.assert_called_once()
