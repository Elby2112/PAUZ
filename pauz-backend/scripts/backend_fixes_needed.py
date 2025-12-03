# ADDITIONAL BACKEND MODELS NEEDED
from pydantic import BaseModel
from typing import List, Optional

class PromptCreate(BaseModel):
    id: int
    text: str

class EntryCreate(BaseModel):
    prompt_id: int
    prompt_text: str  # Add prompt text for PDF generation
    response: str

class GuidedJournalCreate(BaseModel):
    topic: str
    prompts: List[PromptCreate]
    entries: Optional[List[EntryCreate]] = None  # Make entries optional

# ADD PUT ROUTE FOR UPDATING JOURNALS
@router.put("/{journal_id}", response_model=GuidedJournal)
def update_journal_route(
    journal_id: str,
    journal_update: GuidedJournalCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Updates an existing journal with new prompts and entries.
    """
    prompts_data = [p.model_dump() for p in journal_update.prompts]
    entries_data = [e.model_dump() for e in journal_update.entries] if journal_update.entries else []
    
    db_guided_journal = guided_journal_service.update_guided_journal(
        user_id=current_user.id,
        journal_id=journal_id,
        topic=journal_update.topic,
        prompts_data=prompts_data,
        entries_data=entries_data
    )
    return db_guided_journal