from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from app.services.guided_journal_service import guided_journal_service
from app.models.guided_journal import GuidedJournal, GuidedJournalEntry, Prompt
from app.models.user import User
from app.utils import pdf_generator
from app.services.storage_service import storage_service
from pydantic import BaseModel
from typing import List
from app.dependencies import get_current_user
from app.database import get_session


router = APIRouter()

class Topic(BaseModel):
    topic: str

class PromptCreate(BaseModel):
    text: str

class GuidedJournalCreate(BaseModel):
    topic: str
    prompts: List[PromptCreate]

class GuidedJournalEntryCreate(BaseModel):
    prompt_id: int
    response: str

@router.post("/prompts", response_model=List[Prompt])
def generate_prompts_route(topic: Topic):
    """
    Generates a list of prompts based on a given topic.
    """
    prompts_dicts = guided_journal_service.generate_prompts(topic.topic)
    # Convert dicts to Prompt objects (without journal_id yet)
    prompts = [Prompt(text=p['text']) for p in prompts_dicts]
    return prompts

@router.post("/", response_model=GuidedJournal)
def create_journal_route(
    guided_journal_create: GuidedJournalCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Creates a new journal for the current user.
    """
    # Convert PromptCreate to Prompt SQLModel objects
    prompts = [Prompt(text=p.text) for p in guided_journal_create.prompts]
    
    db_guided_journal = guided_journal_service.create_guided_journal(
        user_id=current_user.id, 
        topic=guided_journal_create.topic, 
        prompts_data=prompts, # Pass SQLModel Prompt objects
        db=db
    )
    return db_guided_journal

@router.get("/", response_model=List[GuidedJournal])
def get_user_journals_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves all journals for the current user.
    """
    guided_journals = guided_journal_service.get_user_guided_journals(current_user.id, db)
    return guided_journals

@router.get("/{guided_journal_id}", response_model=GuidedJournal)
def get_journal_route(
    guided_journal_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves a specific journal by its ID, ensuring it belongs to the current user.
    """
    guided_journal = guided_journal_service.get_guided_journal_by_id(guided_journal_id, db)
    if not guided_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GuidedJournal not found")
    if guided_journal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this guided journal")
    return guided_journal

@router.post("/{guided_journal_id}/entry", response_model=GuidedJournalEntry)
def add_journal_entry_route(
    guided_journal_id: str,
    entry_create: GuidedJournalEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Adds a new journal entry to a specific journal.
    """
    guided_journal = guided_journal_service.get_guided_journal_by_id(guided_journal_id, db)
    if not guided_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GuidedJournal not found")
    if guided_journal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to add entry to this guided journal")
    
    # Check if prompt_id exists within the guided_journal's prompts
    prompt_exists = any(p.id == entry_create.prompt_id for p in guided_journal.prompts)
    if not prompt_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid prompt_id for this journal")

    guided_journal_entry = guided_journal_service.add_guided_journal_entry(
        guided_journal_id=guided_journal_id,
        prompt_id=entry_create.prompt_id,
        response_text=entry_create.response,
        db=db
    )
    return guided_journal_entry


@router.post("/{guided_journal_id}/export")
def export_journal_route(
    guided_journal_id: str, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Exports a journal as a PDF and uploads it to storage, returning the URL.
    """
    guided_journal = guided_journal_service.get_guided_journal_by_id(guided_journal_id, db)
    if not guided_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GuidedJournal not found")
    if guided_journal.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to export this guided journal")
        
    pdf_bytes = pdf_generator.generate_pdf_guided_journal(guided_journal)
    pdf_url = storage_service.upload_pdf(guided_journal_id, pdf_bytes)
    return {"pdf_url": pdf_url}