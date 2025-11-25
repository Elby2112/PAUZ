from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class Prompt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    journal_id: Optional[str] = Field(default=None, foreign_key="journal.id")

    journal: Optional["Journal"] = Relationship(back_populates="prompts")

class JournalEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    prompt_id: Optional[int] = Field(default=None, foreign_key="prompt.id")
    response: str
    journal_id: Optional[str] = Field(default=None, foreign_key="journal.id")

    journal: Optional["Journal"] = Relationship(back_populates="entries")
    prompt: Optional[Prompt] = Relationship() # Assuming prompt details might be useful

class Journal(SQLModel, table=True):
    id: Optional[str] = Field(default=None, primary_key=True, index=True)
    user_id: str = Field(foreign_key="user.id", index=True) # Link to User model
    topic: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    exported_at: Optional[datetime] = None

    # Relationships
    user: Optional["User"] = Relationship(back_populates="journals")
    prompts: List[Prompt] = Relationship(back_populates="journal")
    entries: List[JournalEntry] = Relationship(back_populates="journal")