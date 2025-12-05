from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.services.garden_service import garden_service
from app.services.stats_service import stats_service
from app.models import Garden, User
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

    def to_dict(self):
        return {
            "id": self.id,
            "mood": self.mood,
            "date": self.created_at.strftime("%Y-%m-%d"),
            "note": self.note
        }

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
    
    # Invalidate stats cache for this user
    stats_service.invalidate_user_cache(current_user.id)
    
    return garden_entry

@router.get("/")
def get_garden_entries_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Retrieves all garden entries for the current user.
    """
    garden_entries = garden_service.get_garden_entries(current_user.id, db)
    
    # Convert to frontend-friendly format
    response_data = []
    for entry in garden_entries:
        response_data.append({
            "id": entry.id,
            "mood": entry.mood,
            "date": entry.created_at.strftime("%Y-%m-%d"),
            "note": entry.note or "No note saved.",
            "flower_type": entry.flower_type,
            "created_at": entry.created_at.isoformat()
        })
    
    # Sort by created_at descending (newest first)
    response_data.sort(key=lambda x: x["created_at"], reverse=True)
    
    return response_data

@router.delete("/{flower_id}")
def delete_garden_entry_route(
    flower_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """
    Deletes a garden entry for the current user.
    """
    success = garden_service.delete_garden_entry(flower_id, current_user.id, db)
    
    if not success:
        raise HTTPException(status_code=404, detail="Flower not found")
    
    # Invalidate stats cache for this user
    stats_service.invalidate_user_cache(current_user.id)
    
    return {"message": "Flower deleted successfully"}