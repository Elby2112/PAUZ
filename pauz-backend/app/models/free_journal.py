from typing import Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class FreeJournal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True) # Link to User model
    session_id: str = Field(index=True)
    content: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to User
    user: Optional["User"] = Relationship(back_populates="free_journals")