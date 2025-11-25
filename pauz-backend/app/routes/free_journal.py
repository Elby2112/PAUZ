from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlmodel import Session
from app.services.free_journal_service import free_journal_service
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.dependencies import get_current_user
from app.database import get_session

router = APIRouter()

class SaveContentRequest(BaseModel):
    content: str

class HintsRequest(BaseModel):
    current_content: str

class FreeJournalResponse(BaseModel):
    id: Optional[int]
    user_id: str
    session_id: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True # To allow mapping from SQLModel to Pydantic

class HintResponse(BaseModel):
    id: Optional[int]
    user_id: str
    session_id: str
    hint_text: str
    created_at: datetime

    class Config:
        orm_mode = True

@router.post("/", response_model=FreeJournalResponse)
def create_free_journal_session_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Creates a new Free Journal session for the current user.
    """
    free_journal = free_journal_service.create_free_journal_session(current_user.id, db)
    return free_journal

@router.get("/{session_id}", response_model=FreeJournalResponse)
def get_free_journal_session_route(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves a specific Free Journal session for the current user.
    """
    free_journal = free_journal_service.get_free_journal_by_session_id(session_id, current_user.id, db)
    if not free_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Free Journal session not found.")
    return free_journal

@router.post("/{session_id}/save", response_model=FreeJournalResponse)
def save_user_content_route(
    session_id: str, 
    data: SaveContentRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Saves user content to a specific Free Journal session.
    """
    try:
        free_journal = free_journal_service.save_user_content(session_id, current_user.id, data.content, db)
        return free_journal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{session_id}/hints", response_model=HintResponse)
def get_hints_route(
    session_id: str, 
    data: HintsRequest, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Generates hints for the user based on current content and saves them.
    """
    hint = free_journal_service.generate_hints(session_id, data.current_content, current_user.id, db)
    return hint

@router.get("/{session_id}/hints", response_model=List[HintResponse])
def get_session_hints_route(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves all hints for a given Free Journal session.
    """
    hints = free_journal_service.get_hints_for_session(session_id, current_user.id, db)
    return hints


@router.post("/{session_id}/voice", response_model=FreeJournalResponse)
async def transcribe_voice_route(
    session_id: str, 
    audio_file: UploadFile = File(...), 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Transcribes audio and appends it to the free journal content.
    """
    audio_bytes = await audio_file.read()
    try:
        free_journal = free_journal_service.transcribe_audio(session_id, current_user.id, audio_bytes, db)
        return free_journal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{session_id}/reflect")
def reflect_with_ai_route(
    session_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Analyzes the journal content with AI and updates the garden entry.
    """
    try:
        reflection = free_journal_service.reflect_with_ai(session_id, current_user.id, db)
        return reflection
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@router.post("/{session_id}/export")
def export_free_journal_route(
    session_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Exports a free journal to PDF.
    """
    try:
        pdf_url = free_journal_service.export_to_pdf(session_id, current_user.id, db)
        return {"pdfUrl": pdf_url}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))