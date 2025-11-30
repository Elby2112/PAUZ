import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import User, FreeJournal, GuidedJournal, Prompt
from app.dependencies import get_current_user, get_session
from sqlmodel import create_engine, Session, SQLModel
from datetime import datetime

# Create a TestClient instance
client = TestClient(app)

# Mock the get_current_user dependency to return a dummy user
@pytest.fixture(scope="session", autouse=True)
def override_get_current_user():
    """
    Fixture to override the get_current_user dependency and return a test user.
    This runs for the entire test session and applies to all tests.
    """
    app.dependency_overrides[get_current_user] = lambda: User(id="test-user-id", email="test@example.com", name="Test User", picture="https://example.com/pic.jpg")
    yield
    app.dependency_overrides = {}


# Setup for in-memory SQLite database for tests
sqlite_file_name = "test.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)

@pytest.fixture(name="db_session", autouse=True) # Make it autouse for automatic setup/teardown for each test
def db_session_fixture():
    # Make sure all models are imported so SQLModel knows about them
    import app.models.all_models
    
    SQLModel.metadata.create_all(engine) # Create tables
    with Session(engine) as session:
        # Add a test user
        test_user = User(id="test-user-id", email="test@example.com", name="Test User", picture="https://example.com/pic.jpg")
        session.add(test_user)
        session.commit()
        session.refresh(test_user)

        # Add dummy Guided Journals for the test user
        guided_journal_1 = GuidedJournal(id="guided-1", user_id="test-user-id", topic="Gratitude", created_at=datetime.utcnow())
        guided_journal_2 = GuidedJournal(id="guided-2", user_id="test-user-id", topic="Productivity", created_at=datetime.utcnow())
        session.add(guided_journal_1)
        session.add(guided_journal_2)
        session.commit()
        session.refresh(guided_journal_1)
        session.refresh(guided_journal_2)

        # Add dummy Free Journals for the test user
        free_journal_1 = FreeJournal(id=1, user_id="test-user-id", session_id="free-1", content="My first free journal.", created_at=datetime.utcnow())
        free_journal_2 = FreeJournal(id=2, user_id="test-user-id", session_id="free-2", content="My second free journal.", created_at=datetime.utcnow())
        free_journal_3 = FreeJournal(id=3, user_id="test-user-id", session_id="free-3", content="My third free journal.", created_at=datetime.utcnow())
        session.add(free_journal_1)
        session.add(free_journal_2)
        session.add(free_journal_3)
        session.commit()
        session.refresh(free_journal_1)
        session.refresh(free_journal_2)
        session.refresh(free_journal_3)
        
        yield session
    SQLModel.metadata.drop_all(engine) # Drop tables after tests

@pytest.fixture(name="client_with_db")
def client_with_db_fixture(db_session: Session): # Use the new db_session fixture
    def get_session_override():
        return db_session
    
    app.dependency_overrides[get_session] = get_session_override
    yield client # Yield the global client instance
    app.dependency_overrides.pop(get_session)
