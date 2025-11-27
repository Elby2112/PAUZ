from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel
from uuid import uuid4

if TYPE_CHECKING:
    from app.models.user import User


class GuidedJournal(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(foreign_key="users.id")
    topic: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    user: Optional["User"] = Relationship(back_populates="guided_journals")
    prompts: List["Prompt"] = Relationship(back_populates="guided_journal")
    entries: List["GuidedJournalEntry"] = Relationship(back_populates="guided_journal")


class Prompt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    guided_journal_id: Optional[str] = Field(default=None, foreign_key="guidedjournal.id")
    guided_journal: Optional["GuidedJournal"] = Relationship(back_populates="prompts")
    guided_journal_entry: Optional["GuidedJournalEntry"] = Relationship(back_populates="prompt")


class GuidedJournalEntry(SQLModel, table=True):
    id: Optional[str] = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    guided_journal_id: Optional[str] = Field(default=None, foreign_key="guidedjournal.id")
    prompt_id: Optional[int] = Field(default=None, foreign_key="prompt.id")
    response: str
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    guided_journal: Optional["GuidedJournal"] = Relationship(back_populates="entries")
    prompt: Optional["Prompt"] = Relationship(back_populates="guided_journal_entry")