from fastapi import APIRouter, Depends, HTTPException, status
from app.services.guided_journal_service import guided_journal_service
from app.models.guided_journal import GuidedJournal, GuidedJournalEntry, Prompt
from app.models.user import User
from app.utils import pdf_generator
from app.services.storage_service import storage_service
from pydantic import BaseModel
from typing import List
from app.dependencies import get_current_user


router = APIRouter()

class Topic(BaseModel):
    topic: str

class PromptCreate(BaseModel):
    id: int
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
    # Convert dicts to Prompt objects for response model validation
    prompts = [Prompt(**p) for p in prompts_dicts]
    return prompts

@router.post("/", response_model=GuidedJournal)
def create_journal_route(
    guided_journal_create: GuidedJournalCreate, 
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new journal for the current user in the SmartBucket.
    """
    # The service now accepts dicts directly
    prompts_data = [p.model_dump() for p in guided_journal_create.prompts]
    
    db_guided_journal = guided_journal_service.create_guided_journal(
        user_id=current_user.id, 
        topic=guided_journal_create.topic, 
        prompts_data=prompts_data
    )
    return db_guided_journal

@router.get("/", response_model=List[GuidedJournal])
def get_user_journals_route(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all journals for the current user from the SmartBucket.
    """
    guided_journals = guided_journal_service.get_user_guided_journals(current_user.id)
    return guided_journals

@router.get("/{journal_id}", response_model=GuidedJournal)
def get_journal_route(
    journal_id: str, 
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a specific journal by its ID from the SmartBucket.
    """
    guided_journal = guided_journal_service.get_guided_journal_by_id(
        user_id=current_user.id, 
        journal_id=journal_id
    )
    if not guided_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GuidedJournal not found")
    return guided_journal

@router.post("/{journal_id}/entry", response_model=GuidedJournalEntry)
def add_journal_entry_route(
    journal_id: str,
    entry_create: GuidedJournalEntryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Adds a new journal entry to a specific journal in the SmartBucket.
    """
    # The service now fetches the journal and performs authorization checks implicitly
    guided_journal_entry = guided_journal_service.add_guided_journal_entry(
        user_id=current_user.id,
        journal_id=journal_id,
        prompt_id=entry_create.prompt_id,
        response_text=entry_create.response
    )
    if not guided_journal_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GuidedJournal not found or prompt ID is invalid.")
    return guided_journal_entry


@router.post("/{journal_id}/export")
def export_journal_route(
    journal_id: str, 
    current_user: User = Depends(get_current_user)
):
    """
    Exports a journal as a PDF and uploads it to storage, returning the URL.
    """
    guided_journal = guided_journal_service.get_guided_journal_by_id(
        user_id=current_user.id, 
        journal_id=journal_id
    )
    if not guided_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GuidedJournal not found")
        
    pdf_bytes = pdf_generator.generate_pdf_guided_journal(guided_journal)
    pdf_url = storage_service.upload_pdf(journal_id, pdf_bytes)
    return {"pdf_url": pdf_url}