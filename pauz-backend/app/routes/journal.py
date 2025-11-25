from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.services.journal_service import journal_service
from app.services.storage_service import storage_service
from app.models.journal import Journal, JournalEntry, Prompt
from app.models.user import User
from app.utils import pdf_generator
from pydantic import BaseModel
from typing import List, Optional
from app.dependencies import get_current_user
from app.database import get_session


router = APIRouter()

class Topic(BaseModel):
    topic: str

class PromptCreate(BaseModel):
    text: str

class JournalCreate(BaseModel):
    topic: str
    prompts: List[PromptCreate]

class JournalEntryCreate(BaseModel):
    prompt_id: int
    response: str

@router.post("/prompts", response_model=List[Prompt])
def generate_prompts_route(topic: Topic):
    """
    Generates a list of prompts based on a given topic.
    """
    prompts_dicts = journal_service.generate_prompts(topic.topic)
    # Convert dicts to Prompt objects (without journal_id yet)
    prompts = [Prompt(text=p['text']) for p in prompts_dicts]
    return prompts

@router.post("/", response_model=Journal)
def create_journal_route(
    journal_create: JournalCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Creates a new journal for the current user.
    """
    # Convert PromptCreate to Prompt SQLModel objects
    prompts = [Prompt(text=p.text) for p in journal_create.prompts]
    
    db_journal = journal_service.create_journal(
        user_id=current_user.id, 
        topic=journal_create.topic, 
        prompts_data=prompts, # Pass SQLModel Prompt objects
        db=db
    )
    return db_journal

@router.get("/", response_model=List[Journal])
def get_user_journals_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves all journals for the current user.
    """
    journals = journal_service.get_user_journals(current_user.id, db)
    return journals

@router.get("/{journal_id}", response_model=Journal)
def get_journal_route(
    journal_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves a specific journal by its ID, ensuring it belongs to the current user.
    """
    journal = journal_service.get_journal_by_id(journal_id, db)
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    if journal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this journal")
    return journal

@router.post("/{journal_id}/entry", response_model=JournalEntry)
def add_journal_entry_route(
    journal_id: str,
    entry_create: JournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Adds a new journal entry to a specific journal.
    """
    journal = journal_service.get_journal_by_id(journal_id, db)
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    if journal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add entry to this journal")
    
    # Check if prompt_id exists within the journal's prompts
    prompt_exists = any(p.id == entry_create.prompt_id for p in journal.prompts)
    if not prompt_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid prompt_id for this journal")

    journal_entry = journal_service.add_journal_entry(
        journal_id=journal_id,
        prompt_id=entry_create.prompt_id,
        response_text=entry_create.response,
        db=db
    )
    return journal_entry


@router.post("/{journal_id}/export")
def export_journal_route(
    journal_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Exports a journal as a PDF and uploads it to storage, returning the URL.
    """
    journal = journal_service.get_journal_by_id(journal_id, db)
    if not journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    if journal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to export this journal")
        
    pdf_bytes = pdf_generator.generate_pdf(journal)
    pdf_url = storage_service.upload_pdf(journal_id, pdf_bytes)
    return {"pdf_url": pdf_url}