from __future__ import annotations
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel

from app.models.guided_journal import GuidedJournal
from app.models.free_journal import FreeJournal
from app.models.garden import Garden
from app.models.hint import Hint

class User(SQLModel, table=True):
    __tablename__ = "users"  # Explicit table name
    id: Optional[str] = Field(default=None, primary_key=True, index=True)  # Make id a primary key
    email: str = Field(index=True, unique=True)  # Email should be unique and indexed
    name: str
    picture: Optional[str] = None

    # Relationships (use string annotations to avoid circular import)
    guided_journals: List["GuidedJournal"] = Relationship(back_populates="user")
    free_journals: List["FreeJournal"] = Relationship(back_populates="user")
    gardens: List["Garden"] = Relationship(back_populates="user")
    hints: List["Hint"] = Relationship(back_populates="user")
