from fastapi import APIRouter, Depends, HTTPException, status
from app.services.guided_journal_service import guided_journal_service
from app.models import GuidedJournal, GuidedJournalEntry, Prompt, User
from app.utils import pdf_generator
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

class GuidedJournalUpdate(BaseModel):
    topic: str
    prompts: List[PromptCreate]
    entries: List[dict]

@router.post("/prompts", response_model=List[Prompt])
def generate_prompts_route(topic: Topic):
    """
    Generates a list of prompts based on a given topic.
    """
    prompts_dicts = guided_journal_service.generate_prompts(topic.topic)
    # Convert dicts to Prompt objects for response model validation
    prompts = [Prompt(**p) for p in prompts_dicts]
    return prompts

@router.post("/", response_model=dict)
def create_journal_route(
    guided_journal_create: dict, 
    current_user: User = Depends(get_current_user)
):
    """
    Creates a new journal for the current user in the SmartBucket.
    """
    # Handle both dict and object formats
    if hasattr(guided_journal_create, 'model_dump'):
        topic = guided_journal_create.topic
        prompts_data = [p.model_dump() for p in guided_journal_create.prompts]
        entries_data = []
    else:
        topic = guided_journal_create.get('topic')
        prompts_data = guided_journal_create.get('prompts', [])
        entries_data = guided_journal_create.get('entries', [])
    
    db_guided_journal = guided_journal_service.create_guided_journal_with_entries(
        user_id=current_user.id, 
        topic=topic, 
        prompts_data=prompts_data,
        entries_data=entries_data
    )
    return db_guided_journal

@router.get("/", response_model=List[dict])
def get_user_journals_route(
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves all journals for the current user from the SmartBucket.
    """
    guided_journals = guided_journal_service.get_user_guided_journals(current_user.id)
    return guided_journals

@router.get("/{journal_id}", response_model=dict)
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

@router.put("/{journal_id}", response_model=dict)
def update_journal_route(
    journal_id: str,
    journal_update: GuidedJournalUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Updates an existing journal with new prompts and entries.
    """
    prompts_data = [p.model_dump() for p in journal_update.prompts]
    entries_data = journal_update.entries
    
    # Get existing journal
    existing_journal = guided_journal_service.get_guided_journal_by_id(
        user_id=current_user.id,
        journal_id=journal_id
    )
    
    if not existing_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GuidedJournal not found")
    
    # Update journal data
    updated_journal = {
        **existing_journal,
        "topic": journal_update.topic,
        "prompts": prompts_data,
        "entries": entries_data
    }
    
    storage_service.save_guided_journal_data(current_user.id, journal_id, updated_journal)
    return updated_journal

@router.post("/{journal_id}/entry", response_model=dict)
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


@router.delete("/{journal_id}")
def delete_journal_route(
    journal_id: str, 
    current_user: User = Depends(get_current_user)
):
    """
    Deletes a specific guided journal by its ID.
    """
    success = guided_journal_service.delete_guided_journal(current_user.id, journal_id)
    if success:
        return {"message": "Guided journal deleted successfully"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Guided journal not found")


@router.post("/{journal_id}/export")
def export_journal_route(
    journal_id: str, 
    current_user: User = Depends(get_current_user)
):
    """
    Exports a journal as a PDF and uploads it to Vultr S3, returning the URL.
    """
    guided_journal = guided_journal_service.get_guided_journal_by_id(
        user_id=current_user.id, 
        journal_id=journal_id
    )
    if not guided_journal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GuidedJournal not found")
        
    pdf_bytes = pdf_generator.generate_pdf_guided_journal(guided_journal)
    
    # Upload to Vultr S3 directly - NO FALLBACKS
    import boto3
    import os
    
    vultr_access_key = os.getenv("VULTR_ACCESS_KEY")
    vultr_secret_key = os.getenv("VULTR_SECRET_KEY")
    vultr_region = os.getenv("VULTR_REGION")
    vultr_bucket_name = os.getenv("VULTR_BUCKET_NAME")
    
    if not all([vultr_access_key, vultr_secret_key, vultr_region, vultr_bucket_name]):
        raise HTTPException(status_code=500, detail="Vultr S3 credentials required for PDF export")
    
    s3 = boto3.client('s3',
                     aws_access_key_id=vultr_access_key,
                     aws_secret_access_key=vultr_secret_key,
                     region_name=vultr_region,
                     endpoint_url=f'https://{vultr_region}.vultrobjects.com')
    
    file_name = f"guided_journal_{journal_id}.pdf"
    s3.put_object(Bucket=vultr_bucket_name, Key=file_name, Body=pdf_bytes, ACL='public-read')
    
    pdf_url = f"https://{vultr_bucket_name}.{vultr_region}.vultrobjects.com/{file_name}"
    return {"pdf_url": pdf_url}