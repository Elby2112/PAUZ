from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.services.garden_service import garden_service
from app.models.garden import Garden
from app.models.user import User
from pydantic import BaseModel
from typing import List, Optional
from app.dependencies import get_current_user
from app.database import get_session
from datetime import datetime

router = APIRouter()

class GardenCreate(BaseModel):
    mood: str
    note: Optional[str] = None
    flower_type: str

class GardenResponse(BaseModel):
    id: Optional[int]
    user_id: str
    created_at: datetime
    mood: str
    note: Optional[str] = None
    flower_type: str

    class Config:
        from_attributes = True # To allow mapping from SQLModel to Pydantic

@router.post("/", response_model=GardenResponse)
def create_garden_entry_route(
    garden_create: GardenCreate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Creates a new garden entry for the current user.
    """
    garden_entry = garden_service.create_garden_entry(
        user_id=current_user.id,
        mood=garden_create.mood,
        note=garden_create.note,
        flower_type=garden_create.flower_type,
        db=db
    )
    return garden_entry

@router.get("/", response_model=List[GardenResponse])
def get_garden_entries_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
) -> List[Garden]:
    """
    Retrieves all garden entries for the current user.
    """
    garden_entries = garden_service.get_garden_entries(current_user.id, db)
    return garden_entries