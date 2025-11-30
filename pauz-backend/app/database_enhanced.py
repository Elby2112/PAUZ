"""
Enhanced Database Configuration with Migration Support
"""
import os
from sqlmodel import create_engine, Session, SQLModel
from urllib.parse import urlparse

def get_database_url():
    """Get database URL with proper defaults and validation"""
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        # Default to SQLite for development
        print("⚠️ No DATABASE_URL found, using SQLite for development")
        return "sqlite:///./database.db"
    
    # Validate database URL format
    parsed = urlparse(database_url)
    
    if parsed.scheme not in ['postgresql', 'sqlite']:
        raise ValueError(f"Unsupported database scheme: {parsed.scheme}")
    
    return database_url

def create_database_engine():
    """Create database engine with appropriate settings"""
    database_url = get_database_url()
    
    if database_url.startswith("sqlite"):
        # SQLite settings
        engine = create_engine(
            database_url,
            echo=os.getenv("SQL_DEBUG", "false").lower() == "true",
            connect_args={"check_same_thread": False}  # For SQLite
        )
        print("🗄️ Using SQLite database (development)")
    else:
        # PostgreSQL settings
        engine = create_engine(
            database_url,
            echo=os.getenv("SQL_DEBUG", "false").lower() == "true",
            pool_pre_ping=True,  # Check connection health
            pool_recycle=300,    # Recycle connections every 5 minutes
            pool_size=10,        # Connection pool size
            max_overflow=20      # Additional connections under load
        )
        print("🗄️ Using PostgreSQL database (production)")
    
    return engine

def create_db_and_tables():
    """Create database and tables - enhanced version"""
    engine = create_database_engine()
    
    # Import all models to ensure they're registered
    from app.models import User, FreeJournal, Hint, Garden, GuidedJournal, Prompt, GuidedJournalEntry
    
    try:
        SQLModel.metadata.create_all(engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️ Error creating tables: {e}")
        print("💡 Make sure your database is running and accessible")
        raise
    
    return engine

def get_session():
    """Get database session with proper error handling"""
    engine = create_database_engine()
    
    try:
        with Session(engine) as session:
            yield session
    except Exception as e:
        print(f"❌ Database session error: {e}")
        raise

# Initialize engine
engine = create_database_engine()