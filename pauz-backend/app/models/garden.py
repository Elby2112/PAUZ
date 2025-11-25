from typing import Optional
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel

class Garden(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str = Field(foreign_key="user.id", index=True) # Link to User model
    created_at: datetime = Field(default_factory=datetime.utcnow)
    mood: str
    note: Optional[str] = None
    flower_type: str

    # Relationship to User
    user: Optional["User"] = Relationship(back_populates="gardens")